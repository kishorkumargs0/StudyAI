import re
from collections import Counter, defaultdict

from app.text import split_sentences

STOPWORDS = set(
    """
    a about above after again against all also am an and any are as at be because been before being below
    between both but by can could did do does doing down during each either else even every few for from
    further get gets got had has have having he her here hers him his how however i if in into is it its
    itself just let like many may me might more most much must my no nor not now of off often on once only
    or other our ours out over own per rather same she should since so some such than that the their theirs
    them then there these they this those through thus to too under until up upon us use used uses using
    very via was we well were what when where whether which while who whom whose why will with within
    without would yet you your yours one two three first second new make makes made way ways
    example examples lecture notes today across along around among good bad high low large small next
    different certain several various important number set
    """.split()
)
WORD = re.compile(r"[A-Za-z][A-Za-z0-9'-]*")
BIGRAM_WEIGHT = 1.6
SUBJECT_BONUS = 0.5
MIN_SCORE = 2
TOP_N = 8


def tokens(sentence):
    return [match.group().strip("'-") for match in WORD.finditer(sentence)]


def is_candidate(word):
    return len(word) > 2 and word.lower() not in STOPWORDS


def singular(word):
    word = word.lower()
    if len(word) > 3 and word.endswith("s") and not word.endswith(("ss", "us", "is")):
        return word[:-1]
    return word


def modifier(word):
    return singular(word) == word.lower()


def candidates(sentence):
    words = tokens(sentence)
    found = []
    leading = True
    for i, word in enumerate(words):
        after_noun = i > 0 and is_candidate(words[i - 1]) and modifier(words[i - 1])
        if is_candidate(word):
            if not (after_noun and not modifier(word)):
                found.append((singular(word), word, leading))
            if i + 1 < len(words) and modifier(word) and is_candidate(words[i + 1]):
                second = words[i + 1]
                found.append((f"{singular(word)} {singular(second)}", f"{word} {second}", leading))
            leading = False
    return found


def rank_concepts(text, limit=TOP_N):
    sentences = split_sentences(text)
    counts = Counter()
    bonus = Counter()
    spellings = defaultdict(Counter)
    for sentence in sentences:
        seen = set()
        for key, original, leading in candidates(sentence):
            spellings[key][original] += 1
            if key in seen:
                continue
            seen.add(key)
            counts[key] += 1
            if leading:
                bonus[key] += SUBJECT_BONUS

    scores = {}
    for key, count in counts.items():
        is_bigram = " " in key
        if is_bigram and count < 2:
            continue
        scores[key] = count * (BIGRAM_WEIGHT if is_bigram else 1) + bonus[key]

    inside = Counter()
    for key in scores:
        if " " in key:
            for part in key.split():
                inside[part] += counts[key]
    for part, count in inside.items():
        if part in scores and counts[part] - count < 2:
            del scores[part]

    ranked = sorted((key for key in scores if scores[key] >= MIN_SCORE), key=lambda key: (-scores[key], key))
    return [{"term": display(key, spellings[key]), "score": round(scores[key], 2)} for key in ranked[:limit]]


def display(key, spellings):
    best = spellings.most_common(1)[0][0]
    best = " ".join(word if modifier(word) else word[:-1] for word in best.split())
    if best.islower():
        return best.title() if " " in key else best.capitalize()
    return best
