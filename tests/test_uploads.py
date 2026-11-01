import pytest

from app.uploads import MAX_BYTES, UploadError, clean_markdown, read_upload


def test_reads_text_files():
    assert read_upload("notes.txt", b"Stacks are last in, first out.") == "Stacks are last in, first out."


def test_handles_utf8_bom_and_latin1():
    assert read_upload("a.txt", "﻿Café notes".encode()) == "Café notes"
    assert read_upload("b.txt", "Café notes".encode("latin-1")) == "Café notes"


def test_cleans_markdown():
    text = "**Queues** are FIFO. See [the docs](http://example.com) and `deque`.\n> quoted line"
    assert clean_markdown(text) == "Queues are FIFO. See the docs and deque.\nquoted line"


@pytest.mark.parametrize(
    ("name", "raw", "message"),
    [
        ("notes.docx", b"hello", "Upload a PDF"),
        ("notes.txt", b"", "empty"),
        ("notes.txt", b"a" * (MAX_BYTES + 1), "10 MB"),
        ("notes.txt", bytes(range(256)) * 4, "readable"),
        ("notes.pdf", b"not really a pdf", "Could not read"),
    ],
)
def test_rejects_bad_uploads(name, raw, message):
    with pytest.raises(UploadError, match=message):
        read_upload(name, raw)


def test_rejects_pdf_without_text():
    from io import BytesIO

    from pypdf import PdfWriter

    writer = PdfWriter()
    writer.add_blank_page(612, 792)
    buffer = BytesIO()
    writer.write(buffer)
    with pytest.raises(UploadError, match="scanned"):
        read_upload("scan.pdf", buffer.getvalue())
