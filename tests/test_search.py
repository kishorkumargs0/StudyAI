from app.search import BM25, highlight, tokenize

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
    assert index.idf["hash"] > index.idf["the"]


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
    assert len(BM25(DOCS).search("the", limit=2)) == 2


def test_empty_index():
    assert BM25([]).search("anything") == []


def test_highlight_marks_query_words():
    parts = highlight("The learning rate.", "Rate")
    assert ("rate", True) in [(text.lower(), hit) for text, hit in parts]
    assert "".join(text for text, _ in parts) == "The learning rate."
