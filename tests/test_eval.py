from eval.evaluate import METHODS, evaluate, load, rank_of


def test_every_answer_is_in_its_lecture():
    lectures, questions = load()
    assert len(questions) == 40
    for question in questions:
        assert any(question["answer"].lower() in sentence.lower() for sentence in lectures[question["lecture"]])


def test_rank_of():
    assert rank_of(["a cat", "the dog barks"], "dog") == 2
    assert rank_of(["a cat"], "dog") is None


def test_scores_are_between_zero_and_one():
    results, _ = evaluate()
    assert set(results) == set(METHODS)
    for groups in results.values():
        for scores in groups.values():
            assert 0 <= scores["hit1"] <= scores["hit3"] <= 1
