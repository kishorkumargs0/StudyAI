from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException

from app import db
from app.samples import LECTURES, find
from app.text import split_sentences

BASE = Path(__file__).parent

app = FastAPI(title="StudyAI")
app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")
templates = Jinja2Templates(directory=BASE / "templates")
db.init()

MIN_WORDS = 30


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


@app.get("/lectures/new", response_class=HTMLResponse)
def new_lecture(request: Request, mode: str = "file"):
    mode = "text" if mode == "text" else "file"
    return templates.TemplateResponse(request, "new_lecture.html", {"active": "library", "mode": mode})


@app.post("/lectures")
def save_lecture(request: Request, title: str = Form(""), course: str = Form(""), notes: str = Form("")):
    title, course, notes = title.strip(), course.strip(), notes.strip()
    error = None
    if not title or not course:
        error = "Add a title and a course."
    elif len(notes.split()) < MIN_WORDS:
        error = f"Paste at least {MIN_WORDS} words of notes."
    if error:
        form = {"title": title, "course": course, "notes": notes}
        context = {"active": "library", "mode": "text", "error": error, "form": form}
        return templates.TemplateResponse(request, "new_lecture.html", context, status_code=400)
    lecture_id = db.add_lecture(title, course, notes)
    return RedirectResponse(f"/notes/{lecture_id}", status_code=303)


@app.get("/notes/{lecture_id}", response_class=HTMLResponse)
def saved_notes(request: Request, lecture_id: int):
    lecture = db.get_lecture(lecture_id)
    if lecture is None:
        raise HTTPException(status_code=404)
    context = {"active": "library", "lecture": lecture, "sentences": split_sentences(lecture["notes"])}
    return templates.TemplateResponse(request, "notes.html", context)


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
