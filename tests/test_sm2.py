from datetime import date

import pytest

from app.sm2 import MIN_EASE, new_card, review

TODAY = date(2026, 11, 2)


def test_first_reviews_use_one_then_six_days():
    first = review(new_card(), "good", TODAY)
    assert first["interval"] == 1
    assert first["due"] == "2026-11-03"
    second = review(first, "good", TODAY)
    assert second["interval"] == 6
    assert second["due"] == "2026-11-08"


def test_later_reviews_multiply_by_ease():
    card = {"repetitions": 2, "interval": 6, "ease": 2.5}
    assert review(card, "good", TODAY)["interval"] == 15


def test_again_resets_the_card():
    card = {"repetitions": 4, "interval": 40, "ease": 2.5}
    result = review(card, "again", TODAY)
    assert result["repetitions"] == 0
    assert result["interval"] == 1


@pytest.mark.parametrize(("grade", "change"), [("easy", 0.1), ("good", 0.0), ("hard", -0.14), ("again", -0.8)])
def test_ease_changes_with_grade(grade, change):
    assert review(new_card(), grade, TODAY)["ease"] == pytest.approx(2.5 + change)


def test_ease_never_drops_below_minimum():
    card = new_card()
    for _ in range(10):
        card = review(card, "again", TODAY)
    assert card["ease"] == MIN_EASE
