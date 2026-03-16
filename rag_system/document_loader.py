from __future__ import annotations

from pathlib import Path

from docx import Document
from pypdf import PdfReader

from backend.config import ALLOWED_DOCUMENT_EXTENSIONS


def load_documents(root: Path) -> list[tuple[Path, str]]:
    documents: list[tuple[Path, str]] = []
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.suffix.lower() in ALLOWED_DOCUMENT_EXTENSIONS:
            text = load_document_text(path)
            if text.strip():
                documents.append((path, text))
    return documents


def load_document_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".txt", ".md"}:
        return path.read_text(encoding="utf-8")
    if suffix == ".pdf":
        reader = PdfReader(str(path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    if suffix == ".docx":
        document = Document(str(path))
        return "\n".join(paragraph.text for paragraph in document.paragraphs)
    return ""
