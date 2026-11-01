# StudyAI

Turns lecture notes into study guides, flashcards, and practice quizzes.

Everything is generated from your notes with plain Python, no AI API needed.

## What it does

- Paste notes or upload a PDF, TXT, or Markdown file
- Splits the notes into sentences and ranks the key concepts
- Builds a short summary from the most important sentences
- Makes fill-in-the-blank flashcards
- Makes a multiple choice quiz and saves your answers

## Run

```
uv sync
uv run uvicorn app.main:app --port 8765
```

Then open http://127.0.0.1:8765

## Tests

```
uv run pytest
uv run ruff check .
```
