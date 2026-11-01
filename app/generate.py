import math
import re

from app.concepts import rank_concepts
from app.text import split_sentences

BLANK = "_____"
SUMMARY_SIZE = 4
MIN_CARD_WORDS = 6


def term_pattern(term):
    words = [re.escape(word) + r"(?:s|es)?" for word in term.lower().split()]
    return re.compile(r"(?<![\w-])" + r"\s+".join(words) + r"(?![\w-])", re.IGNORECASE)


def with_period(sentence):
    return sentence if sentence[-1] in ".!?" else sentence + "."


def summarize(sentences, concepts, size=SUMMARY_SIZE):
    patterns = [(term_pattern(concept["term"]), concept["score"]) for concept in concepts]
    scored = []
    for index, sentence in enumerate(sentences):
        hits = sum(score for pattern, score in patterns if pattern.search(sentence))
        if hits:
            scored.append((hits / math.sqrt(len(sentence.split())), index))
    best = sorted(index for _, index in sorted(scored, reverse=True)[:size])
    return " ".join(with_period(sentences[index]) for index in best)


def cloze_cards(sentences, concepts):
    cards = []
    used = set()
    for concept in concepts:
        pattern = term_pattern(concept["term"])
        options = []
        for index, sentence in enumerate(sentences):
            match = pattern.search(sentence)
            if index in used or not match or len(sentence.split()) < MIN_CARD_WORDS:
                continue
            options.append((match.start() / len(sentence) + len(sentence.split()) / 40, index))
        if not options:
            continue
        index = min(options)[1]
        used.add(index)
        front = with_period(pattern.sub(BLANK, sentences[index]))
        cards.append({"front": front, "back": concept["term"], "concept": concept["term"]})
    return cards


def build_study_set(text):
    sentences = split_sentences(text)
    concepts = rank_concepts(text)
    return {
        "summary": summarize(sentences, concepts),
        "concepts": concepts,
        "flashcards": cloze_cards(sentences, concepts),
    }
