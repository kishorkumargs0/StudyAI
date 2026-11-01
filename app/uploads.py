import re
from io import BytesIO
from pathlib import Path

from pypdf import PdfReader

ALLOWED = {".txt", ".md", ".pdf"}
MAX_BYTES = 10 * 1024 * 1024
MIN_PDF_WORDS = 30


class UploadError(ValueError):
    pass


def decode(raw):
    try:
        return raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        return raw.decode("latin-1")


def clean_markdown(text):
    text = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"(\*\*|__|`)", "", text)
    return re.sub(r"^\s*>\s?", "", text, flags=re.MULTILINE)


def read_pdf(raw):
    try:
        reader = PdfReader(BytesIO(raw))
        pages = [page.extract_text() or "" for page in reader.pages]
    except Exception as exc:
        raise UploadError("Could not read that PDF. Try exporting it again or paste the text instead.") from exc
    text = "\n\n".join(pages)
    if len(text.split()) < MIN_PDF_WORDS:
        raise UploadError("That PDF has almost no text. It might be a scanned image, so paste the notes instead.")
    return text


def read_upload(filename, raw):
    suffix = Path(filename or "").suffix.lower()
    if suffix not in ALLOWED:
        raise UploadError("Upload a PDF, TXT, or Markdown file.")
    if not raw:
        raise UploadError("That file is empty.")
    if len(raw) > MAX_BYTES:
        raise UploadError("Files can be up to 10 MB.")
    if suffix == ".pdf":
        return read_pdf(raw).strip()
    text = decode(raw)
    unreadable = sum(1 for char in text if not char.isprintable() and not char.isspace())
    if unreadable > len(text) // 10:
        raise UploadError("That file isn't readable text.")
    if suffix == ".md":
        text = clean_markdown(text)
    return text.strip()
