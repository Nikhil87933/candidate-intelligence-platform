"""DOCX text extraction using python-docx."""

from pathlib import Path

from docx import Document


def extract_docx_text(file_path: Path) -> str:
    """Extract text from a DOCX file."""
    document = Document(str(file_path))

    return "\n".join(
        paragraph.text for paragraph in document.paragraphs if paragraph.text
    )
