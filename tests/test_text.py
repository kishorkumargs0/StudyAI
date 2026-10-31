from app.text import split_sentences


def test_splits_on_periods():
    text = "Gradient descent lowers the loss. The learning rate sets the step size."
    assert split_sentences(text) == [
        "Gradient descent lowers the loss.",
        "The learning rate sets the step size.",
    ]


def test_question_and_exclamation_marks():
    text = "Why does the loss go up? The learning rate is too large! Lower it and try again."
    assert len(split_sentences(text)) == 3


def test_keeps_abbreviations_together():
    text = "Some activations, e.g. ReLU, are cheap to compute. Others like tanh are slower."
    assert split_sentences(text)[0] == "Some activations, e.g. ReLU, are cheap to compute."


def test_keeps_decimals_together():
    text = "A learning rate of 0.01 is a common starting point. Larger values can diverge quickly."
    assert split_sentences(text)[0] == "A learning rate of 0.01 is a common starting point."


def test_joins_wrapped_lines():
    text = "Backpropagation uses the chain\nrule to compute gradients for every weight."
    assert split_sentences(text) == ["Backpropagation uses the chain rule to compute gradients for every weight."]


def test_rejoins_hyphenated_words():
    text = "Regulari-\nzation keeps the weights small during training."
    assert split_sentences(text) == ["Regularization keeps the weights small during training."]


def test_bullets_become_sentences():
    text = "- Hash tables map keys to buckets\n- Collisions happen when two keys share a bucket\n* Rehashing grows the table"
    assert split_sentences(text) == [
        "Hash tables map keys to buckets",
        "Collisions happen when two keys share a bucket",
        "Rehashing grows the table",
    ]


def test_bullet_continuation_and_end():
    text = "- Chaining stores a list\n  in each bucket\nOpen addressing probes for the next free slot."
    assert split_sentences(text) == [
        "Chaining stores a list in each bucket",
        "Open addressing probes for the next free slot.",
    ]


def test_numbered_list_and_headings():
    text = "# Week 3\n1. Load factor is entries divided by buckets\n2) Chaining stores a list in each bucket"
    assert split_sentences(text) == [
        "Load factor is entries divided by buckets",
        "Chaining stores a list in each bucket",
    ]


def test_drops_short_fragments():
    assert split_sentences("Overview.\n\nA hash function maps keys to indexes.") == [
        "A hash function maps keys to indexes."
    ]


def test_empty_text():
    assert split_sentences("") == []
    assert split_sentences("   \n\n  ") == []
