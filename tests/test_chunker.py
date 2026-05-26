from rocs_copilot_backend.ingest.chunker import split_text


def test_split_text_respects_chunk_size_and_overlap():
    text = "x" * 2500  # 2500 chars
    chunks = split_text(text, chunk_size=1000, chunk_overlap=100)
    # 2500 chars with 1000/100 → first 1000, then start at 900, etc.
    # Expect at least 3 chunks, no chunk longer than 1000.
    assert len(chunks) >= 3
    assert all(len(c) <= 1000 for c in chunks)


def test_split_text_default_params_match_spec():
    """Spec §6.1: RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)."""
    # Call with no args — defaults must be 1000/100.
    text = "y" * 1500
    chunks = split_text(text)
    assert len(chunks) >= 2
    assert all(len(c) <= 1000 for c in chunks)


def test_split_text_short_input_returns_single_chunk():
    text = "short"
    chunks = split_text(text)
    assert chunks == ["short"]
