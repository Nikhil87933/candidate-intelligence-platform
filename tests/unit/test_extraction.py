"""Tests for document text extraction."""

from pathlib import Path

import fitz
import pytest
from docx import Document
from PIL import Image, ImageDraw

from candidate_intelligence.extraction.docx_extractor import extract_docx_text
from candidate_intelligence.extraction.ocr_extractor import extract_ocr_text
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


def test_extract_ocr_text_from_image(tmp_path: Path) -> None:
    """Verify text can be extracted from an image via OCR."""
    file_path = tmp_path / "resume.png"

    image = Image.new("RGB", (400, 100), color="white")
    draw = ImageDraw.Draw(image)
    draw.text((10, 40), "Nikhil OCR Engineer", fill="black")
    image.save(file_path)

    text = extract_ocr_text(file_path)

    assert "Nikhil" in text


def test_extract_ocr_text_from_pdf(tmp_path: Path) -> None:
    """Verify text can be extracted from a scanned PDF via OCR."""
    file_path = tmp_path / "scanned_resume.pdf"

    image = Image.new("RGB", (400, 100), color="white")
    draw = ImageDraw.Draw(image)
    draw.text((10, 40), "Nikhil OCR Scanner", fill="black")
    image_path = tmp_path / "page.png"
    image.save(image_path)

    document = fitz.open()
    page = document.new_page()
    rect = fitz.Rect(0, 0, 400, 100)
    page.insert_image(rect, filename=str(image_path))
    document.save(file_path)
    document.close()

    text = extract_ocr_text(file_path)

    assert "Nikhil" in text


def test_extract_ocr_text_unsupported_file_type(tmp_path: Path) -> None:
    """Verify unsupported file types raise a clear error."""
    file_path = tmp_path / "resume.txt"
    file_path.write_text("plain text file")

    with pytest.raises(ValueError, match="Unsupported file type"):
        extract_ocr_text(file_path)
