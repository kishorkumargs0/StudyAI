from datetime import date

WEAKNESS_WEIGHT = 0.5
REVIEW_WEIGHT = 0.3
IMPORTANCE_WEIGHT = 0.2
UNKNOWN = 0.5


def weakness(attempts, correct):
    return 1 - correct / attempts if attempts else UNKNOWN


def days_overdue(state, today):
    return (today - date.fromisoformat(state["due"])).days


def review_need(state, today):
    if state is None:
        return UNKNOWN
    overdue = days_overdue(state, today)
    if overdue < 0:
        return 0.0
    return min(1.0, UNKNOWN + overdue / 14)


def priority_score(weak, need, importance):
    return round(100 * (WEAKNESS_WEIGHT * weak + REVIEW_WEIGHT * need + IMPORTANCE_WEIGHT * importance))


def card_reason(state, today):
    if state is None:
        return "card not reviewed yet"
    overdue = days_overdue(state, today)
    if overdue > 0:
        return f"card overdue {overdue} day{'s' if overdue != 1 else ''}"
    if overdue == 0:
        return "card due today"
    return None


def rank_priorities(study, stats, states, today=None):
    today = today or date.today()
    concepts = study["concepts"]
    if not concepts:
        return []
    top = concepts[0]["score"]
    cards = {card["concept"]: index for index, card in enumerate(study["flashcards"])}
    ranked = []
    for concept in concepts:
        term = concept["term"]
        attempts, correct = stats.get(term, (0, 0))
        importance = concept["score"] / top
        reasons = []
        if attempts and correct < attempts:
            reasons.append(f"missed {attempts - correct} of {attempts}")
        need = 0.0
        if term in cards:
            state = states.get(cards[term])
            need = review_need(state, today)
            if card_reason(state, today):
                reasons.append(card_reason(state, today))
        if importance == 1:
            reasons.append("top concept")
        score = priority_score(weakness(attempts, correct), need, importance)
        ranked.append({"concept": term, "score": score, "reasons": reasons})
    ranked.sort(key=lambda row: -row["score"])
    return ranked
