import json
from pathlib import Path

from app.search import BM25, STOPWORDS, stem, tokenize
from app.text import split_sentences

ROOT = Path(__file__).parent
DEPTH = 5


def keyword_count(sentences, query):
    words = [word for word in tokenize(query) if word not in STOPWORDS]
    scored = []
    for sentence in sentences:
        hits = sum(sentence.lower().count(word) for word in words)
        if hits:
            scored.append((-hits, len(sentence), sentence))
    return [sentence for _, _, sentence in sorted(scored)]


def bm25(analyzer=None):
    def run(sentences, query):
        documents = [{"text": sentence} for sentence in sentences]
        index = BM25(documents, analyzer=analyzer) if analyzer else BM25(documents)
        return [result["text"] for result in index.search(query, limit=DEPTH)]

    return run


def stemmed(text):
    return [stem(word) for word in tokenize(text)]


METHODS = {
    "Keyword count": keyword_count,
    "BM25": bm25(tokenize),
    "BM25 + stemming": bm25(stemmed),
    "BM25 + stemming + stopwords": bm25(),
}


def load():
    data = json.loads((ROOT / "questions.json").read_text())
    lectures = {lecture["id"]: split_sentences((ROOT / lecture["file"]).read_text()) for lecture in data["lectures"]}
    return lectures, data["questions"]


def rank_of(ranked, answer):
    for rank, sentence in enumerate(ranked[:DEPTH], start=1):
        if answer.lower() in sentence.lower():
            return rank
    return None


def evaluate():
    lectures, questions = load()
    for question in questions:
        if not any(question["answer"].lower() in sentence.lower() for sentence in lectures[question["lecture"]]):
            raise ValueError(f"No sentence contains the answer for: {question['question']}")
    results = {}
    for name, method in METHODS.items():
        ranks = [
            (question["type"], rank_of(method(lectures[question["lecture"]], question["question"]), question["answer"]))
            for question in questions
        ]
        results[name] = {
            group: summarize([rank for kind, rank in ranks if group in ("all", kind)])
            for group in ("exact", "reworded", "all")
        }
    return results, questions


def summarize(ranks):
    total = len(ranks)
    return {
        "hit1": sum(rank == 1 for rank in ranks) / total,
        "hit3": sum(rank is not None and rank <= 3 for rank in ranks) / total,
        "mrr": sum(1 / rank for rank in ranks if rank) / total,
        "count": total,
    }


def main():
    results, questions = evaluate()
    counts = {kind: sum(question["type"] == kind for question in questions) for kind in ("exact", "reworded")}
    print(
        f"{len(questions)} questions: {counts['exact']} use the lecture's wording, {counts['reworded']} are reworded\n"
    )
    print(f"{'Method':<30}{'Hit@1 reworded':>16}{'Hit@1 exact':>13}{'Hit@1 all':>11}{'Hit@3 all':>11}{'MRR all':>9}")
    for name, groups in results.items():
        print(
            f"{name:<30}{groups['reworded']['hit1']:>16.0%}{groups['exact']['hit1']:>13.0%}"
            f"{groups['all']['hit1']:>11.0%}{groups['all']['hit3']:>11.0%}{groups['all']['mrr']:>9.2f}"
        )


if __name__ == "__main__":
    main()
