# StudyAI

Turns lecture notes into study guides, flashcards, and practice quizzes.

The study material is generated from your notes with plain Python. Gemini is optional and only used to explain the few concepts you're weakest on.

## What it does

- Paste notes or upload a PDF, TXT, or Markdown file
- Splits the notes into sentences and ranks the key concepts
- Builds a short summary from the most important sentences
- Makes fill-in-the-blank flashcards and a multiple choice quiz
- Saves quiz answers and tracks accuracy per concept
- Schedules flashcard reviews with SM-2 (the algorithm Anki is based on)
- Ranks what to study next using quiz accuracy, due cards, and how central each concept is
- Searches all your notes with BM25 and stemming
- Explains your top weak concepts with Gemini, using only your notes (optional)

## Run

```
uv sync
uv run uvicorn app.main:app --port 8765
```

Then open http://127.0.0.1:8765

For Gemini explanations, add your key to a `.env` file in this folder:

```
GEMINI_API_KEY=your-key
```

## Tests

```
uv run pytest
uv run ruff check .
```

## Search eval

40 labeled questions over 4 lectures (16 use the lecture's wording, 24 are reworded):

```
uv run python -m eval.evaluate
```

| Method | Hit@1 reworded | Hit@1 all | Hit@3 all | MRR |
| --- | --- | --- | --- | --- |
| Keyword count | 38% | 55% | 70% | 0.63 |
| BM25 | 46% | 62% | 78% | 0.71 |
| BM25 + stemming | 50% | 62% | 82% | 0.72 |
| BM25 + stemming + stopwords | 46% | 60% | 70% | 0.66 |
