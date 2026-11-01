from app.concepts import rank_concepts

NEURAL = """
A neural network is made of layers of neurons connected by weights. Each neuron computes a weighted sum
of its inputs and passes it through an activation function. Activation functions like ReLU let the network
model nonlinear relationships. Without an activation function, stacked layers behave like one linear model.
Training uses gradient descent to reduce a loss function. Gradient descent updates every weight in the
direction that lowers the loss. The learning rate controls the size of each update. A learning rate that is
too large can overshoot, while a small learning rate makes training slow.
"""

HASHING = """
- A hash table stores key-value pairs in an array of buckets
- A hash function maps each key to a bucket index
- Collisions happen when two keys map to the same bucket
- Chaining handles collisions by storing a linked list in each bucket
- The load factor is the number of entries divided by the number of buckets
- When the load factor gets too high, the hash table resizes
- A good hash function spreads keys evenly across buckets
"""


def terms(text):
    return [concept["term"] for concept in rank_concepts(text)]


def test_finds_two_word_concepts():
    found = terms(NEURAL)
    assert "Activation Function" in found
    assert "Learning Rate" in found
    assert "Gradient Descent" in found


def test_bigram_absorbs_its_words():
    found = [term.lower() for term in terms(NEURAL)]
    assert "learning" not in found
    assert "rate" not in found
    assert "activation" not in found


def test_plurals_count_as_one_concept():
    found = [term.lower() for term in terms(HASHING)]
    assert "bucket" in found
    assert "buckets" not in found
    assert found.count("key") + found.count("keys") == 1


def test_skips_verbs_after_a_noun():
    found = [term.lower() for term in terms(HASHING)]
    assert "maps" not in found
    assert "handles" not in found


def test_ranked_by_score():
    scores = [concept["score"] for concept in rank_concepts(HASHING)]
    assert scores == sorted(scores, reverse=True)


def test_limit_and_empty_text():
    assert len(rank_concepts(NEURAL, limit=3)) == 3
    assert rank_concepts("") == []
