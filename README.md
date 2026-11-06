# StudyAI

Turns lecture notes into study guides, flashcards, and practice quizzes.

The study material is generated from your notes with plain Python. Gemini is optional and only used to explain the few concepts you're weakest on.

## Download

No coding needed. Go to the [latest release](https://github.com/kishorkumargs0/StudyAI/releases/latest) and download the file for your computer.

**Mac (Apple Silicon)**: download `StudyAI-mac.zip`, double-click it, and drag StudyAI into Applications. The first time you open it, macOS will say it can't verify the developer. Open System Settings, go to Privacy & Security, scroll down, and click Open Anyway.

**Windows**: download `StudyAI-windows.zip`, unzip it, and double-click `StudyAI.exe`. If Windows shows "Windows protected your PC", click More info, then Run anyway.

Older Intel Macs and Linux aren't supported by the download yet. Use "Run from source" below instead.

Your notes stay on your computer, in `~/Library/Application Support/StudyAI` on Mac and `%LOCALAPPDATA%\StudyAI` on Windows. Gemini explanations are optional and you can add a key in Settings.

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

## Run from source

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then:

```
uv sync
uv run uvicorn app.main:app --port 8765
```

Then open http://127.0.0.1:8765

Or open it in its own window:

```
uv run --group desktop python -m app.desktop
```

For Gemini explanations, add your key in Settings, or put it in a `.env` file in this folder:

```
GEMINI_API_KEY=your-key
```

## Build the app

GitHub Actions builds the Mac and Windows downloads whenever a release is published. To build locally:

```
uv run --group desktop pyinstaller --noconfirm --name StudyAI --windowed --paths . --add-data app/templates:app/templates --add-data app/static:app/static --collect-submodules uvicorn app/desktop.py
```

## Tests

```
uv run --group desktop pytest
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
