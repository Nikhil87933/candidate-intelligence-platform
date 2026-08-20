"""OCR text extraction for scanned/image-based documents using Tesseract."""

from io import BytesIO
from pathlib import Path
from typing import Any

import fitz
import pytesseract
from PIL import Image

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".tiff", ".bmp"}


def extract_ocr_text(file_path: Path) -> str:
    """Extract text from a scanned PDF or image file using OCR.

    PDFs are rasterized page-by-page with PyMuPDF and each page image is
    passed through Tesseract. Plain image files are OCR'd directly.
    """
    suffix = file_path.suffix.lower()

    if suffix == ".pdf":
        return _extract_pdf_via_ocr(file_path)

    if suffix in IMAGE_SUFFIXES:
        with Image.open(file_path) as image:
            return str(pytesseract.image_to_string(image))

    raise ValueError(f"Unsupported file type for OCR extraction: {suffix}")


def _extract_pdf_via_ocr(file_path: Path) -> str:
    """Rasterize each PDF page and run OCR on it."""
    document: Any = fitz.open(str(file_path))

    try:
        page_texts = []
        for page in document:
            pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            with Image.open(BytesIO(pixmap.tobytes("png"))) as image:
                page_texts.append(str(pytesseract.image_to_string(image)))
        return "\n".join(page_texts)
    finally:
        document.close()
