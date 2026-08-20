"""PDF text extraction using PyMuPDF."""

from pathlib import Path
from typing import Any

import fitz


def extract_pdf_text(file_path: Path) -> str:
    """Extract text from a PDF file."""
    document: Any = fitz.open(str(file_path))

    try:
        return "\n".join(page.get_text() for page in document)
    finally:
        document.close()
