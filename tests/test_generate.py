from app.generate import BLANK, build_study_set, term_pattern

NOTES = """
A hash table stores key-value pairs in an array of buckets. A hash function maps each key to a bucket index.
Collisions happen when two keys map to the same bucket. Chaining handles collisions by storing a list in each
bucket. The load factor is the number of entries divided by the number of buckets. When the load factor gets
too high, the hash table resizes and rehashes every key. A good hash function spreads keys evenly.
"""


def test_term_pattern_matches_plurals_and_case():
    pattern = term_pattern("Hash Table")
    assert pattern.search("Two hash tables were merged.")
    assert pattern.search("HASH TABLE")
    assert not pattern.search("hashtable")


def test_term_pattern_skips_hyphenated_words():
    assert not term_pattern("Key").search("It stores key-value pairs.")


def test_summary_uses_sentences_from_the_notes():
    study = build_study_set(NOTES)
    assert study["summary"]
    for sentence in study["summary"].split(". "):
        assert sentence.rstrip(".") in NOTES.replace("\n", " ")


def test_cards_blank_out_the_answer():
    for card in build_study_set(NOTES)["flashcards"]:
        assert BLANK in card["front"]
        assert not term_pattern(card["back"]).search(card["front"])


def test_each_sentence_used_once():
    fronts = [card["front"] for card in build_study_set(NOTES)["flashcards"]]
    assert len(fronts) == len(set(fronts))
    assert len(fronts) >= 3


def test_empty_notes():
    study = build_study_set("")
    assert study == {"summary": "", "concepts": [], "flashcards": [], "quiz": []}


def test_quiz_has_four_options_with_one_answer():
    quiz = build_study_set(NOTES)["quiz"]
    assert quiz
    for question in quiz:
        assert len(question["options"]) == 4
        assert len(set(question["options"])) == 4
        assert question["options"][question["answer"]] == question["concept"]
        assert BLANK in question["question"]


def test_quiz_is_stable_between_runs():
    assert build_study_set(NOTES)["quiz"] == build_study_set(NOTES)["quiz"]


def test_no_quiz_without_enough_concepts():
    assert build_study_set("Stacks push and pop items. Stacks push items on top.")["quiz"] == []
