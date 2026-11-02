from datetime import date

from app.priority import priority_score, rank_priorities, review_need, weakness

TODAY = date(2026, 11, 2)

STUDY = {
    "concepts": [
        {"term": "Hash Table", "score": 4.0},
        {"term": "Load Factor", "score": 3.0},
        {"term": "Collision", "score": 2.0},
    ],
    "flashcards": [
        {"concept": "Hash Table"},
        {"concept": "Load Factor"},
        {"concept": "Collision"},
    ],
}


def test_weakness_from_quiz_accuracy():
    assert weakness(4, 1) == 0.75
    assert weakness(2, 2) == 0
    assert weakness(0, 0) == 0.5


def test_review_need_grows_when_overdue():
    assert review_need(None, TODAY) == 0.5
    assert review_need({"due": "2026-11-09"}, TODAY) == 0
    assert review_need({"due": "2026-11-02"}, TODAY) == 0.5
    assert review_need({"due": "2026-10-26"}, TODAY) == 1.0
    assert review_need({"due": "2026-09-01"}, TODAY) == 1.0


def test_score_range():
    assert priority_score(0, 0, 0) == 0
    assert priority_score(1, 1, 1) == 100


def test_missed_concept_ranks_first():
    stats = {"Collision": (3, 0), "Hash Table": (3, 3)}
    states = {0: {"due": "2026-11-20"}, 1: {"due": "2026-11-20"}, 2: {"due": "2026-11-20"}}
    ranked = rank_priorities(STUDY, stats, states, TODAY)
    assert ranked[0]["concept"] == "Collision"
    assert "missed 3 of 3" in ranked[0]["reasons"]


def test_overdue_card_beats_scheduled_card():
    stats = {"Hash Table": (2, 2), "Load Factor": (2, 2), "Collision": (2, 2)}
    states = {0: {"due": "2026-11-20"}, 1: {"due": "2026-10-30"}, 2: {"due": "2026-11-20"}}
    ranked = rank_priorities(STUDY, stats, states, TODAY)
    assert ranked[0]["concept"] == "Load Factor"
    assert "card overdue 3 days" in ranked[0]["reasons"]


def test_sorted_and_empty():
    scores = [row["score"] for row in rank_priorities(STUDY, {}, {}, TODAY)]
    assert scores == sorted(scores, reverse=True)
    assert rank_priorities({"concepts": [], "flashcards": []}, {}, {}, TODAY) == []
