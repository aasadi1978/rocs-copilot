"""Document loaders for PDF and DOCX. Returns a uniform list of (text, metadata) pairs."""
from __future__ import annotations

from pathlib import Path
from typing import Iterator

from langchain_community.document_loaders import Docx2txtLoader, PyPDFLoader


class LoaderError(Exception):
    """Raised when a single file fails to load. The CLI catches + logs + skips."""


def load_file(path: Path) -> list[tuple[str, dict]]:
    """Load a single file. Returns list of (page_text, metadata) tuples.

    Metadata contains: source (filename), page (1-indexed for PDFs, 1 for DOCX).
    Raises LoaderError on parse failure; caller decides whether to skip.
    """
    suffix = path.suffix.lower()
    try:
        if suffix == ".pdf":
            docs = PyPDFLoader(str(path)).load()
            return [
                (
                    d.page_content,
                    {"source": path.name, "page": d.metadata.get("page", 0) + 1},
                )
                for d in docs
            ]
        if suffix == ".docx":
            docs = Docx2txtLoader(str(path)).load()
            # Docx2txt yields one Document for the whole file.
            return [(d.page_content, {"source": path.name, "page": 1}) for d in docs]
        raise LoaderError(f"unsupported extension: {suffix}")
    except LoaderError:
        raise
    except Exception as e:
        raise LoaderError(f"{path.name}: {e}") from e


def iter_corpus(corpus_dir: Path) -> Iterator[Path]:
    """Yield .pdf and .docx files under corpus_dir (non-recursive)."""
    for path in sorted(corpus_dir.iterdir()):
        if path.is_file() and path.suffix.lower() in (".pdf", ".docx"):
            yield path
