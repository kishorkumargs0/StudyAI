import pytest
from google.genai import errors

from app import explain

NOTES = [
    "The load factor is the number of entries divided by the number of buckets.",
    "When the load factor gets too high, the table resizes.",
    "Chaining stores a list in each bucket.",
]


class FakeResponse:
    def __init__(self, text):
        self.text = text


class FakeClient:
    prompts = []

    def __init__(self, api_key, http_options=None):
        self.models = self

    def generate_content(self, model, contents):
        FakeClient.prompts.append(contents)
        return FakeResponse("  The load factor tells you how full the table is.  ")


class BrokenClient(FakeClient):
    def generate_content(self, model, contents):
        raise RuntimeError("503 overloaded")


@pytest.fixture
def key(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")


def test_only_sends_sentences_about_the_concept():
    prompt = explain.build_prompt("Load Factor", NOTES)
    assert "number of entries divided" in prompt
    assert "Chaining" not in prompt
    assert '"Load Factor"' in prompt


def test_unavailable_without_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    assert not explain.available()
    with pytest.raises(explain.ExplainError, match="GEMINI_API_KEY"):
        explain.explain("Load Factor", NOTES)


def test_explains_with_gemini(key, monkeypatch):
    monkeypatch.setattr("google.genai.Client", FakeClient)
    assert explain.explain("Load Factor", NOTES) == "The load factor tells you how full the table is."
    assert "Load Factor" in FakeClient.prompts[-1]


def test_concept_missing_from_notes(key, monkeypatch):
    monkeypatch.setattr("google.genai.Client", FakeClient)
    with pytest.raises(explain.ExplainError, match="don't say enough"):
        explain.explain("Open Addressing", NOTES)


def test_api_failure_becomes_friendly_error(key, monkeypatch):
    monkeypatch.setattr("google.genai.Client", BrokenClient)
    with pytest.raises(explain.ExplainError, match="didn't respond"):
        explain.explain("Load Factor", NOTES)


class FailingClient(FakeClient):
    failures = {}
    calls = []

    def generate_content(self, model, contents):
        FailingClient.calls.append(model)
        code = self.failures.get(model)
        if code:
            kind = errors.ServerError if code >= 500 else errors.ClientError
            raise kind(code, {"error": {"code": code, "message": "nope", "status": "ERROR"}})
        return FakeResponse("Explained.")


def use_failures(monkeypatch, failures):
    FailingClient.failures = failures
    FailingClient.calls = []
    monkeypatch.setattr("google.genai.Client", FailingClient)
    monkeypatch.setattr(explain, "MODELS", "first,second")


def test_busy_model_falls_back_to_next(key, monkeypatch):
    use_failures(monkeypatch, {"first": 503})
    assert explain.explain("Load Factor", NOTES) == "Explained."
    assert FailingClient.calls == ["first", "second"]


def test_unknown_model_falls_back_to_next(key, monkeypatch):
    use_failures(monkeypatch, {"first": 404})
    assert explain.explain("Load Factor", NOTES) == "Explained."


def test_all_models_busy(key, monkeypatch):
    use_failures(monkeypatch, {"first": 503, "second": 503})
    with pytest.raises(explain.ExplainError, match="busy"):
        explain.explain("Load Factor", NOTES)


def test_rate_limited(key, monkeypatch):
    use_failures(monkeypatch, {"first": 429, "second": 429})
    with pytest.raises(explain.ExplainError, match="rate limiting"):
        explain.explain("Load Factor", NOTES)


def test_bad_key_stops_right_away(key, monkeypatch):
    use_failures(monkeypatch, {"first": 400})
    with pytest.raises(explain.ExplainError, match="API key"):
        explain.explain("Load Factor", NOTES)
    assert FailingClient.calls == ["first"]
