import os

from dotenv import load_dotenv

from app.generate import term_pattern

load_dotenv()

MODELS = os.environ.get("GEMINI_MODELS", "gemini-flash-latest,gemini-flash-lite-latest,gemini-2.5-flash")
TIMEOUT_MS = 30_000
MAX_SENTENCES = 6
PROMPT = """You are helping a student review their own lecture notes.
Explain "{concept}" in 2 or 3 short sentences, in plain language, using only the notes below.
If the notes don't explain it, say that the notes don't cover it.

Notes:
{notes}"""


class ExplainError(Exception):
    pass


def api_key():
    return os.environ.get("GEMINI_API_KEY", "").strip()


def available():
    return bool(api_key())


def relevant_sentences(concept, sentences, limit=MAX_SENTENCES):
    pattern = term_pattern(concept)
    return [sentence for sentence in sentences if pattern.search(sentence)][:limit]


def build_prompt(concept, sentences):
    notes = "\n".join(f"- {sentence}" for sentence in relevant_sentences(concept, sentences))
    return PROMPT.format(concept=concept, notes=notes)


def explain(concept, sentences):
    if not available():
        raise ExplainError("Add a GEMINI_API_KEY to use explanations.")
    if not relevant_sentences(concept, sentences):
        raise ExplainError("Your notes don't say enough about this to explain it.")
    from google import genai
    from google.genai import errors, types

    client = genai.Client(api_key=api_key(), http_options=types.HttpOptions(timeout=TIMEOUT_MS))
    prompt = build_prompt(concept, sentences)
    message = "Gemini didn't respond. Try again in a minute."
    for model in [name.strip() for name in MODELS.split(",") if name.strip()]:
        try:
            response = client.models.generate_content(model=model, contents=prompt)
        except errors.ServerError:
            message = "Gemini is busy right now. Try again in a minute."
            continue
        except errors.ClientError as exc:
            if exc.code == 429:
                message = "Gemini is rate limiting requests. Wait a minute and try again."
            elif exc.code in (400, 401, 403):
                raise ExplainError("Gemini rejected the API key. Check GEMINI_API_KEY in your .env.") from exc
            continue
        except Exception:
            continue
        text = (response.text or "").strip()
        if text:
            return text
    raise ExplainError(message)
