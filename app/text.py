import re

ABBREVIATIONS = {"e.g", "i.e", "etc", "vs", "dr", "mr", "mrs", "ms", "prof", "fig", "eq", "approx", "no", "st"}
BULLET = re.compile(r"^(?:[•●○▪■◦‣·\x7f\uf0b7]\s*|[-*]\s+|\d+[.)]\s+)")
SENTENCE_END = re.compile(r"[.!?]+[\"')\]]*\s+(?=[\"'(\[]?[A-Z0-9])")
MIN_WORDS = 4
SHORT_LINE = 8


def is_short_line(line):
    return 0 < len(line.split()) <= SHORT_LINE and not BULLET.match(line) and line[-1] not in ".!?:;,"


def is_heading(lines, index):
    following = [line for line in lines[index + 1 :] if line]
    if not is_short_line(lines[index]) or not following:
        return False
    return bool(BULLET.match(following[0])) or is_heading(lines, lines.index(following[0], index + 1))


def paragraphs(text):
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)
    raw_lines = text.split("\n")
    lines = [raw.strip() for raw in raw_lines]
    chunks = []
    current = []
    in_bullet = False
    for index, raw in enumerate(raw_lines):
        line = lines[index]
        is_bullet = bool(BULLET.match(line))
        ends_bullet = in_bullet and line and not raw[:1].isspace()
        following = lines[index + 1] if index + 1 < len(lines) else ""
        standalone = not in_bullet and is_short_line(line) and not following[:1].islower()
        if not line or line.startswith("#") or is_bullet or ends_bullet or standalone:
            if current:
                chunks.append(" ".join(current))
            current = []
            in_bullet = is_bullet
            if line.startswith("#") or (standalone and is_heading(lines, index)):
                continue
            line = BULLET.sub("", line)
        if line:
            current.append(line)
        if standalone:
            chunks.append(" ".join(current))
            current = []
    if current:
        chunks.append(" ".join(current))
    return chunks


def split_paragraph(paragraph):
    pieces = []
    start = 0
    for match in SENTENCE_END.finditer(paragraph):
        before = paragraph[start : match.start()].split()
        last = before[-1].lower() if before else ""
        if last in ABBREVIATIONS or (len(last) == 1 and last.isalpha()):
            continue
        pieces.append(paragraph[start : match.end()].strip())
        start = match.end()
    pieces.append(paragraph[start:].strip())
    return pieces


def split_sentences(text):
    sentences = []
    for paragraph in paragraphs(text):
        for sentence in split_paragraph(paragraph):
            if len(sentence.split()) >= MIN_WORDS:
                sentences.append(sentence)
    return sentences
