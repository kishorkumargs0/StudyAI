import re

ABBREVIATIONS = {"e.g", "i.e", "etc", "vs", "dr", "mr", "mrs", "ms", "prof", "fig", "eq", "approx", "no", "st"}
BULLET = re.compile(r"^(?:[-*•]|\d+[.)])\s+")
SENTENCE_END = re.compile(r"[.!?]+[\"')\]]*\s+(?=[\"'(\[]?[A-Z0-9])")
MIN_WORDS = 4


def paragraphs(text):
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)
    chunks = []
    current = []
    in_bullet = False
    for raw in text.split("\n"):
        line = raw.strip()
        is_bullet = bool(BULLET.match(line))
        ends_bullet = in_bullet and line and not raw[:1].isspace()
        if not line or line.startswith("#") or is_bullet or ends_bullet:
            if current:
                chunks.append(" ".join(current))
            current = []
            in_bullet = is_bullet
            if line.startswith("#"):
                continue
            line = BULLET.sub("", line)
        if line:
            current.append(line)
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
