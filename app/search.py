import math
import re
from collections import Counter

K1 = 1.5
B = 0.75
WORD = re.compile(r"[a-z0-9]+")


def tokenize(text):
    return WORD.findall(text.lower())


class BM25:
    def __init__(self, documents):
        self.documents = documents
        self.tokens = [tokenize(document["text"]) for document in documents]
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
        words = set(tokenize(query))
        if not words:
            return []
        scored = [(self.score(words, index), index) for index in range(len(self.documents))]
        ranked = sorted((pair for pair in scored if pair[0] > 0), key=lambda pair: (-pair[0], pair[1]))
        return [dict(self.documents[index], score=round(score, 3)) for score, index in ranked[:limit]]


def highlight(text, query):
    words = set(tokenize(query))
    parts = []
    for piece in re.split(r"([A-Za-z0-9]+)", text):
        if piece:
            parts.append((piece, piece.lower() in words))
    return parts
