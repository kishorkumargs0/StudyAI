import math
import re
import zlib

from app.concepts import rank_concepts
from app.text import split_sentences

BLANK = "_____"
SUMMARY_SIZE = 4
MIN_CARD_WORDS = 6
QUIZ_OPTIONS = 4


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


def distractors(concept, concepts, count, seed):
    others = [other["term"] for other in concepts if other["term"] != concept["term"]]
    shift = seed % len(others)
    others = others[shift:] + others[:shift]
    size = len(concept["term"].split())
    others.sort(key=lambda term: len(term.split()) != size)
    return others[:count]


def quiz_questions(sentences, concepts, cards):
    card_sentences = {card["front"] for card in cards}
    used = set()
    questions = []
    if len(concepts) < QUIZ_OPTIONS:
        return questions
    for concept in concepts:
        pattern = term_pattern(concept["term"])
        options = []
        for index, sentence in enumerate(sentences):
            match = pattern.search(sentence)
            if not match or len(sentence.split()) < MIN_CARD_WORDS:
                continue
            blanked = with_period(pattern.sub(BLANK, sentence))
            reused = index in used or blanked in card_sentences
            options.append((reused, match.start() / len(sentence), index, blanked))
        if not options:
            continue
        _, _, index, blanked = min(options)
        used.add(index)
        seed = zlib.crc32(blanked.encode())
        choices = distractors(concept, concepts, QUIZ_OPTIONS - 1, seed)
        answer = seed % QUIZ_OPTIONS
        choices.insert(answer, concept["term"])
        questions.append(
            {
                "question": f"Which term fills the blank? {blanked}",
                "options": choices,
                "answer": answer,
                "explanation": with_period(sentences[index]),
                "concept": concept["term"],
            }
        )
    return questions


def build_study_set(text):
    sentences = split_sentences(text)
    concepts = rank_concepts(text)
    cards = cloze_cards(sentences, concepts)
    return {
        "summary": summarize(sentences, concepts),
        "concepts": concepts,
        "flashcards": cards,
        "quiz": quiz_questions(sentences, concepts, cards),
    }
