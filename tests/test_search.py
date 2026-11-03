from app.search import BM25, analyze, highlight, stem, tokenize

DOCS = [
    {"text": "The learning rate controls the size of each update."},
    {"text": "Gradient descent updates the weights to lower the loss."},
    {"text": "A hash table stores keys in buckets."},
    {"text": "The the the the the the learning."},
    {"text": "Overfitting happens when the model memorizes the training data and does badly on new data later."},
]


def test_tokenize():
    assert tokenize("Hash-tables, O(1) lookups!") == ["hash", "tables", "o", "1", "lookups"]


def test_finds_matching_sentence():
    results = BM25(DOCS).search("hash table")
    assert results[0]["text"] == DOCS[2]["text"]


def test_rare_words_count_more():
    index = BM25(DOCS)
    assert index.idf["hash"] > index.idf["learn"]


def test_repeats_have_diminishing_returns():
    index = BM25([{"text": "loss"}, {"text": "loss loss loss loss"}, {"text": "other words"}])
    once, many = index.score({"loss"}, 0), index.score({"loss"}, 1)
    assert many > once
    assert many < 4 * once


def test_long_sentences_are_penalized():
    index = BM25([{"text": "data loss"}, {"text": "data loss in a much longer sentence about other things"}])
    assert index.score({"loss"}, 0) > index.score({"loss"}, 1)


def test_no_results_for_empty_or_unknown_query():
    index = BM25(DOCS)
    assert index.search("") == []
    assert index.search("quantum") == []


def test_limit():
    assert len(BM25(DOCS).search("learning", limit=1)) == 1


def test_empty_index():
    assert BM25([]).search("anything") == []


def test_highlight_marks_query_words():
    parts = highlight("The learning rate.", "Rate")
    assert ("rate", True) in [(text.lower(), hit) for text, hit in parts]
    assert "".join(text for text, _ in parts) == "The learning rate."


def test_stem_word_variants():
    assert stem("learning") == stem("learned") == stem("learns") == stem("learn")
    assert stem("controls") == stem("controlled") == stem("control")
    assert stem("updates") == stem("updated") == stem("update")
    assert stem("studies") == stem("study")
    assert stem("class") == "class"
    assert stem("string") == "string"


def test_analyze_stems_every_word():
    assert analyze("What does the learning rate control?") == ["what", "doe", "the", "learn", "rate", "control"]


def test_common_words_barely_count():
    index = BM25(DOCS)
    assert index.idf["the"] < index.idf["learn"] < index.idf["hash"]


def test_stemming_finds_reworded_question():
    results = BM25(DOCS).search("what is the learning rate controlling")
    assert results[0]["text"] == DOCS[0]["text"]


def test_content_words_beat_filler_words():
    results = BM25(DOCS).search("what is the hash table")
    assert results[0]["text"] == DOCS[2]["text"]


def test_plain_tokens_still_supported():
    index = BM25(DOCS, analyzer=tokenize)
    assert index.search("controlling") == []
    assert BM25(DOCS).search("controlling")


def test_highlight_uses_stems():
    parts = highlight("The learning rate controls updates.", "control the rate")
    marked = [text for text, hit in parts if hit]
    assert marked == ["rate", "controls"]
