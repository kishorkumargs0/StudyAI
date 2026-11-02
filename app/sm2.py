from datetime import date, timedelta

GRADES = {"again": 0, "hard": 3, "good": 4, "easy": 5}
START_EASE = 2.5
MIN_EASE = 1.3


def new_card():
    return {"repetitions": 0, "interval": 0, "ease": START_EASE}


def review(card, grade, today=None):
    today = today or date.today()
    quality = GRADES[grade]
    repetitions, interval, ease = card["repetitions"], card["interval"], card["ease"]
    if quality < 3:
        repetitions, interval = 0, 1
    else:
        if repetitions == 0:
            interval = 1
        elif repetitions == 1:
            interval = 6
        else:
            interval = round(interval * ease)
        repetitions += 1
    ease = max(MIN_EASE, ease + 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    return {
        "repetitions": repetitions,
        "interval": interval,
        "ease": round(ease, 2),
        "due": (today + timedelta(days=interval)).isoformat(),
    }
