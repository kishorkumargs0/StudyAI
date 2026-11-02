from datetime import date, datetime
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException

from app import db
from app.generate import build_study_set
from app.priority import rank_priorities
from app.samples import LECTURES, find
from app.search import BM25, highlight
from app.sm2 import GRADES, new_card, review
from app.text import split_sentences
from app.uploads import MAX_BYTES, UploadError, read_upload

BASE = Path(__file__).parent

app = FastAPI(title="StudyAI")
app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")
templates = Jinja2Templates(directory=BASE / "templates")
db.init()

MIN_WORDS = 30
WEAK_ACCURACY = 0.75
STUDY_NEXT = 5


def greeting():
    hour = datetime.now().hour
    if hour < 12:
        return "Good morning"
    if hour < 18:
        return "Good afternoon"
    return "Good evening"


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse(
        request, "dashboard.html", {"active": "dashboard", "greeting": greeting(), "lectures": LECTURES}
    )


@app.get("/library", response_class=HTMLResponse)
def library(request: Request):
    context = {"active": "library", "lectures": LECTURES, "saved": db.list_lectures()}
    return templates.TemplateResponse(request, "library.html", context)


@app.get("/insights", response_class=HTMLResponse)
def insights(request: Request):
    concepts = db.concept_accuracy()
    attempts = sum(row["attempts"] for row in concepts)
    correct = sum(row["correct"] for row in concepts)
    due = []
    priorities = []
    for lecture in db.list_lectures():
        study = build_study_set(lecture["notes"])
        cards = len(due_cards(lecture["id"], len(study["flashcards"]))[0])
        if cards:
            due.append({"lecture": lecture, "cards": cards})
        for row in lecture_priorities(lecture["id"], study):
            priorities.append(dict(row, lecture=lecture))
    priorities.sort(key=lambda row: -row["score"])
    weak = [row for row in concepts if row["accuracy"] < WEAK_ACCURACY]
    weak.sort(key=lambda row: (row["accuracy"], -row["attempts"]))
    context = {
        "active": "insights",
        "attempts": attempts,
        "accuracy": round(100 * correct / attempts) if attempts else None,
        "reviews": db.review_count(),
        "due": due,
        "due_total": sum(row["cards"] for row in due),
        "weak": weak,
        "priorities": priorities[:STUDY_NEXT],
        "concepts": sorted(concepts, key=lambda row: (row["title"], -row["accuracy"])),
    }
    return templates.TemplateResponse(request, "insights.html", context)


@app.get("/search", response_class=HTMLResponse)
def search(request: Request, q: str = ""):
    q = q.strip()[:200]
    results = []
    if q:
        documents = []
        for lecture in db.list_lectures():
            for sentence in split_sentences(lecture["notes"]):
                documents.append({"text": sentence, "lecture": lecture})
        results = BM25(documents).search(q)
        for result in results:
            result["parts"] = highlight(result["text"], q)
    context = {"active": "search", "q": q, "results": results}
    if request.headers.get("HX-Request"):
        return templates.TemplateResponse(request, "search_results.html", context)
    return templates.TemplateResponse(request, "search.html", context)


@app.get("/lectures/new", response_class=HTMLResponse)
def new_lecture(request: Request, mode: str = "file"):
    mode = "text" if mode == "text" else "file"
    return templates.TemplateResponse(request, "new_lecture.html", {"active": "library", "mode": mode})


@app.post("/lectures")
async def save_lecture(
    request: Request,
    title: str = Form(""),
    course: str = Form(""),
    notes: str = Form(""),
    mode: str = Form("text"),
    file: Annotated[UploadFile | None, File()] = None,
):
    title, course, notes = title.strip(), course.strip(), notes.strip()
    mode = "file" if mode == "file" else "text"
    source = "pasted notes"
    error = None
    if not title or not course:
        error = "Add a title and a course."
    elif mode == "file":
        if file is None or not file.filename:
            error = "Choose a file to upload."
        else:
            try:
                notes = read_upload(file.filename, await file.read(MAX_BYTES + 1))
                source = file.filename
            except UploadError as exc:
                error = str(exc)
    if not error and len(notes.split()) < MIN_WORDS:
        error = f"The notes need at least {MIN_WORDS} words."
    if error:
        form = {"title": title, "course": course, "notes": notes if mode == "text" else ""}
        context = {"active": "library", "mode": mode, "error": error, "form": form}
        return templates.TemplateResponse(request, "new_lecture.html", context, status_code=400)
    lecture_id = db.add_lecture(title, course, notes, source)
    return RedirectResponse(f"/notes/{lecture_id}", status_code=303)


@app.get("/notes/{lecture_id}", response_class=HTMLResponse)
def saved_notes(request: Request, lecture_id: int, q: int = -1, pick: int = -1):
    lecture = db.get_lecture(lecture_id)
    if lecture is None:
        raise HTTPException(status_code=404)
    study = build_study_set(lecture["notes"])
    context = {
        "active": "library",
        "lecture": lecture,
        "sentences": split_sentences(lecture["notes"]),
        "study": study,
        "progress": db.quiz_progress(lecture_id),
        "due": len(due_cards(lecture_id, len(study["flashcards"]))[0]),
        "priorities": lecture_priorities(lecture_id, study)[:3],
        "answered": q,
        "pick": pick,
    }
    return templates.TemplateResponse(request, "notes.html", context)


@app.post("/notes/{lecture_id}/quiz/{index}")
def answer_question(request: Request, lecture_id: int, index: int, picked: int = Form(-1)):
    lecture = db.get_lecture(lecture_id)
    if lecture is None:
        raise HTTPException(status_code=404)
    quiz = build_study_set(lecture["notes"])["quiz"]
    if not 0 <= index < len(quiz) or not 0 <= picked < len(quiz[index]["options"]):
        raise HTTPException(status_code=400)
    question = quiz[index]
    db.add_attempt(lecture_id, index, question["concept"], picked, picked == question["answer"])
    if request.headers.get("HX-Request"):
        context = {"lecture": lecture, "question": question, "index": index, "pick": picked}
        return templates.TemplateResponse(request, "quiz_question.html", context)
    return RedirectResponse(f"/notes/{lecture_id}?q={index}&pick={picked}#q{index}", status_code=303)


def lecture_priorities(lecture_id, study):
    return rank_priorities(study, db.concept_stats(lecture_id), db.card_states(lecture_id))


def due_cards(lecture_id, count):
    states = db.card_states(lecture_id)
    today = date.today().isoformat()
    due = [card for card in range(count) if card not in states or states[card]["due"] <= today]
    return due, states


@app.get("/notes/{lecture_id}/review", response_class=HTMLResponse)
def review_cards(request: Request, lecture_id: int, side: str = "front"):
    lecture = db.get_lecture(lecture_id)
    if lecture is None:
        raise HTTPException(status_code=404)
    cards = build_study_set(lecture["notes"])["flashcards"]
    due, states = due_cards(lecture_id, len(cards))
    context = {
        "active": "library",
        "lecture": lecture,
        "due": len(due),
        "index": due[0] if due else None,
        "card": cards[due[0]] if due else None,
        "side": "back" if side == "back" else "front",
        "next_due": min((state["due"] for state in states.values()), default=None),
    }
    return templates.TemplateResponse(request, "review.html", context)


@app.post("/notes/{lecture_id}/review/{index}")
def grade_card(lecture_id: int, index: int, grade: str = Form("")):
    lecture = db.get_lecture(lecture_id)
    if lecture is None:
        raise HTTPException(status_code=404)
    cards = build_study_set(lecture["notes"])["flashcards"]
    if not 0 <= index < len(cards) or grade not in GRADES:
        raise HTTPException(status_code=400)
    state = db.card_states(lecture_id).get(index) or new_card()
    db.save_review(lecture_id, index, cards[index]["concept"], review(state, grade))
    return RedirectResponse(f"/notes/{lecture_id}/review", status_code=303)


@app.get("/lectures/{lecture_id}", response_class=HTMLResponse)
def lecture_page(
    request: Request,
    lecture_id: int,
    tab: str = "guide",
    card: int = 0,
    side: str = "front",
    q: int = 0,
    pick: int = -1,
):
    lecture = find(lecture_id)
    if lecture is None:
        raise HTTPException(status_code=404)
    if tab not in ("guide", "flashcards", "quiz"):
        tab = "guide"
    cards = lecture["flashcards"]
    quiz = lecture["quiz"]
    context = {
        "active": "library",
        "lecture": lecture,
        "tab": tab,
        "card_index": card % len(cards),
        "side": "back" if side == "back" else "front",
        "q_index": q % len(quiz),
        "pick": pick if 0 <= pick < 4 else -1,
    }
    return templates.TemplateResponse(request, "lecture.html", context)


@app.exception_handler(HTTPException)
def http_error(request: Request, exc: HTTPException):
    context = {"active": "", "code": exc.status_code}
    return templates.TemplateResponse(request, "error.html", context, status_code=exc.status_code)


@app.exception_handler(RequestValidationError)
def bad_request(request: Request, exc: RequestValidationError):
    return templates.TemplateResponse(request, "error.html", {"active": "", "code": 404}, status_code=404)
