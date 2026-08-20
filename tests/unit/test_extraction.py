"""Tests for document text extraction."""

from pathlib import Path

import fitz
from docx import Document

from candidate_intelligence.extraction.docx_extractor import extract_docx_text
from candidate_intelligence.extraction.pdf_extractor import extract_pdf_text


def test_extract_pdf_text(tmp_path: Path) -> None:
    """Verify text can be extracted from a PDF."""
    file_path = tmp_path / "resume.pdf"

    document = fitz.open()
    page = document.new_page()
    page.insert_text((72, 72), "Nikhil Python Developer")
    document.save(file_path)
    document.close()

    text = extract_pdf_text(file_path)

    assert "Nikhil Python Developer" in text


def test_extract_docx_text(tmp_path: Path) -> None:
    """Verify text can be extracted from a DOCX document."""
    file_path = tmp_path / "resume.docx"

    document = Document()
    document.add_paragraph("Nikhil Data Engineer")
    document.save(file_path)

    text = extract_docx_text(file_path)

    assert "Nikhil Data Engineer" in text
