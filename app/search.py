import math
import re
from collections import Counter

K1 = 1.5
B = 0.75
WORD = re.compile(r"[a-z0-9]+")
STOPWORDS = set(
    """
    a about after all also an and any are as at be because been being but by can could did do does doing
    for from had has have how i if in into is it its just me my of on or our so some than that the their
    them then there these they this those to too was we were what when where which while who why will with
    would you your explain define mean means meant
    """.split()
)


def tokenize(text):
    return WORD.findall(text.lower())


def stem(word):
    if len(word) <= 3:
        return word
    if word.endswith("ies") and len(word) > 4:
        word = word[:-3] + "y"
    elif word.endswith("sses"):
        word = word[:-2]
    elif word.endswith("s") and not word.endswith(("ss", "us", "is")):
        word = word[:-1]
    for suffix in ("ing", "ed", "ly"):
        base = word[: -len(suffix)]
        if word.endswith(suffix) and len(base) >= 3 and re.search(r"[aeiouy]", base):
            word = base
            if len(word) > 3 and word[-1] == word[-2] and word[-1] not in "lsz":
                word = word[:-1]
            break
    if word.endswith("e") and len(word) > 4:
        word = word[:-1]
    if word.endswith("ll") and len(word) > 4:
        word = word[:-1]
    return word


def analyze(text):
    return [stem(word) for word in tokenize(text)]


class BM25:
    def __init__(self, documents, analyzer=analyze):
        self.documents = documents
        self.analyzer = analyzer
        self.tokens = [analyzer(document["text"]) for document in documents]
        self.counts = [Counter(tokens) for tokens in self.tokens]
        self.average = sum(len(tokens) for tokens in self.tokens) / len(self.tokens) if self.tokens else 0
        df = Counter(word for counts in self.counts for word in counts)
        total = len(documents)
        self.idf = {word: math.log((total - n + 0.5) / (n + 0.5) + 1) for word, n in df.items()}

    def score(self, query_words, index):
        counts = self.counts[index]
        length = len(self.tokens[index])
        total = 0.0
        for word in query_words:
            tf = counts.get(word, 0)
            if not tf:
                continue
            norm = tf + K1 * (1 - B + B * length / self.average)
            total += self.idf[word] * tf * (K1 + 1) / norm
        return total

    def search(self, query, limit=10):
        words = set(self.analyzer(query))
        if not words:
            return []
        scored = [(self.score(words, index), index) for index in range(len(self.documents))]
        ranked = sorted((pair for pair in scored if pair[0] > 0), key=lambda pair: (-pair[0], pair[1]))
        return [dict(self.documents[index], score=round(score, 3)) for score, index in ranked[:limit]]


def highlight(text, query):
    words = set(analyze(query))
    parts = []
    for piece in re.split(r"([A-Za-z0-9]+)", text):
        if piece:
            parts.append((piece, piece.lower() not in STOPWORDS and stem(piece.lower()) in words))
    return parts
