from pathlib import Path

import pytest

from rocs_copilot_backend.ingest.loader import LoaderError, iter_corpus, load_file

FIXTURE_CORPUS = Path(__file__).parent / "fixtures" / "corpus"


def test_iter_corpus_finds_pdf_and_docx():
    files = sorted(p.name for p in iter_corpus(FIXTURE_CORPUS))
    assert files == ["sample-error-catalog.docx", "sample-rocs-module.pdf"]


def test_load_pdf_returns_pages_with_metadata():
    pages = load_file(FIXTURE_CORPUS / "sample-rocs-module.pdf")
    assert len(pages) >= 1
    text, meta = pages[0]
    assert "Sample ROCS Module" in text
    assert meta["source"] == "sample-rocs-module.pdf"
    assert meta["page"] == 1


def test_load_docx_returns_single_page():
    pages = load_file(FIXTURE_CORPUS / "sample-error-catalog.docx")
    assert len(pages) == 1
    text, meta = pages[0]
    assert "Sample Error Catalog" in text
    assert meta["source"] == "sample-error-catalog.docx"
    assert meta["page"] == 1


def test_load_unsupported_extension_raises(tmp_path):
    p = tmp_path / "ignored.txt"
    p.write_text("hello")
    with pytest.raises(LoaderError, match="unsupported extension"):
        load_file(p)


def test_load_missing_file_raises(tmp_path):
    with pytest.raises(LoaderError):
        load_file(tmp_path / "does-not-exist.pdf")
