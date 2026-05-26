# rocs-copilot Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Run on **Sonnet 4.6 (1M context)** per the global plan/execution boundary in `~/.claude/CLAUDE.md` — switch with `/model sonnet` before executing.

**Goal:** Build the rocs-copilot MVP per the approved design spec — a single-user, laptop-hosted Flask + React/TS chatbot copilot with LangChain RAG over Chroma for FedEx ROCS planner docs.

**Architecture:** Two surfaces (out-of-band ingestion CLI + Flask serving), LangChain LCEL backend with history-aware retriever, Chroma local vector store, Vite/React/TS frontend with CSS Modules + typed theme tokens, vanilla `useChatStream` SSE hook. See spec §5 + §6 for component trees.

**Tech Stack:** Python 3.11+, Flask, LangChain (`langchain`, `langchain-openai`, `langchain-groq`, `langchain-community`, `langchain-chroma`), Chroma (`chromadb`), `pydantic-settings`, `tenacity`, `pytest`. Vite + React 18 + TypeScript, Vitest, React Testing Library. CI: GitHub Actions.

---

## Reference (READ FIRST before starting)

- **Design spec (single source of truth):** `C:/Users/3626416/Projects/rocs-copilot/docs/superpowers/specs/2026-05-25-rocs-copilot-design.md`
- **Session snapshot:** `C:/Users/3626416/Projects/rocs-copilot/STATUS.md`
- **User glossary:** `C:/Users/3626416/Projects/rocs-copilot/key-notes.md`
- **Project scaffold conventions:** `C:/Users/3626416/Projects/rocs-copilot/CLAUDE.md` → defers to global `C:/Users/3626416/.claude/CLAUDE.md`
- **Brand kit:** `C:/Users/3626416/Projects/rocs-copilot/brand/` (FedEx color formulas FY26 PDF — used in Phase 4 for theme tokens)

## Conventions for the executing session

- **Host:** Windows. Forward-slash paths everywhere. `.exe` invocations use the **PowerShell** tool; simple Unix-like commands (`ls`, `grep`, `cat`, `git`) use **Bash**. Never use bare `python` — always the venv path.
- **Project venv:** `C:/Users/3626416/Projects/rocs-copilot/.venv/Scripts/python.exe` (does NOT exist until Phase 1 Task 1.3 creates it; preauthorized in `.claude/settings.local.json`).
- **Commit cadence:** commit after each passing TDD task. Conventional commits (`feat:`, `test:`, `chore:`, `ci:`, `docs:`).
- **TDD style — PRAGMATIC:** test-first for risky/load-bearing logic (chunker, store idempotency, provider factory, RAG chain composition + history rewrite, SSE event ordering, all §8 error paths, `useChatStream` parser, error-bubble Retry). Write-then-smoke for trivial wiring (Flask app factory, route registration, theme CSS variables, `App.tsx` layout shell, Vite config).
- **Scope discipline:** if you find yourself wanting to add a feature not in the spec (auth, persistence, multi-user, real LLM provider integration tests, Playwright E2E), STOP. The spec §2.2 lists explicit non-goals. Re-read it.
- **External lookups:** for library API questions (LangChain, Flask, Vite, React, Chroma, Vitest), prefer `context7` MCP — `mcp__plugin_context7_context7__resolve-library-id` then `mcp__plugin_context7_context7__query-docs` — over WebSearch.
- **GCP prod LLM gap:** FedEx prod has no programmatic LLM today (spec §4). Provider abstraction in `providers/llm.py` is load-bearing. Don't shortcut it.
- **Brand logo gap:** `brand/logo-with-fred-smith.png` is a marketing photo, NOT a UI wordmark (spec §11). Phase 4 uses a typographic placeholder.

---

# Phase 1 — Project bootstrap

Goal: directory skeleton, dependency manifest, virtualenv, git history, test fixtures.

## Task 1.1: Directory skeleton + `.gitignore` + `pyproject.toml` + `.env.example`

**Files:**
- Create: `C:/Users/3626416/Projects/rocs-copilot/pyproject.toml`
- Create: `C:/Users/3626416/Projects/rocs-copilot/.gitignore`
- Create: `C:/Users/3626416/Projects/rocs-copilot/.env.example`
- Create: `C:/Users/3626416/Projects/rocs-copilot/src/rocs_copilot_backend/__init__.py`
- Create: `C:/Users/3626416/Projects/rocs-copilot/src/rocs_copilot_backend/routes/__init__.py`
- Create: `C:/Users/3626416/Projects/rocs-copilot/src/rocs_copilot_backend/chains/__init__.py`
- Create: `C:/Users/3626416/Projects/rocs-copilot/src/rocs_copilot_backend/providers/__init__.py`
- Create: `C:/Users/3626416/Projects/rocs-copilot/src/rocs_copilot_backend/ingest/__init__.py`
- Create: `C:/Users/3626416/Projects/rocs-copilot/scripts/__init__.py` (empty marker; the CLI module lives here)
- Create: `C:/Users/3626416/Projects/rocs-copilot/tests/__init__.py`
- Create: `C:/Users/3626416/Projects/rocs-copilot/tests/fixtures/__init__.py`
- Create: `C:/Users/3626416/Projects/rocs-copilot/tests/conftest.py`

- [ ] **Step 1: Create directory tree**

Run (PowerShell):
```powershell
New-Item -ItemType Directory -Force -Path src/rocs_copilot_backend/routes, src/rocs_copilot_backend/chains, src/rocs_copilot_backend/providers, src/rocs_copilot_backend/ingest, scripts, tests/fixtures/corpus, data/corpus, data/chroma | Out-Null
```

Verify:
```powershell
Get-ChildItem -Recurse -Directory | Select-Object FullName
```
Expected: `src/`, `src/rocs_copilot_backend/`, `src/rocs_copilot_backend/{routes,chains,providers,ingest}/`, `scripts/`, `tests/`, `tests/fixtures/corpus/`, `data/corpus/`, `data/chroma/`, plus pre-existing `brand/`, `docs/`, `.claude/`.

- [ ] **Step 2: Create empty `__init__.py` files**

Run (PowerShell):
```powershell
$inits = @(
  'src/rocs_copilot_backend/__init__.py',
  'src/rocs_copilot_backend/routes/__init__.py',
  'src/rocs_copilot_backend/chains/__init__.py',
  'src/rocs_copilot_backend/providers/__init__.py',
  'src/rocs_copilot_backend/ingest/__init__.py',
  'scripts/__init__.py',
  'tests/__init__.py',
  'tests/fixtures/__init__.py'
)
foreach ($p in $inits) { if (-not (Test-Path $p)) { New-Item -ItemType File $p | Out-Null } }
```

- [ ] **Step 3: Write `pyproject.toml`**

Create `C:/Users/3626416/Projects/rocs-copilot/pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "rocs-copilot"
version = "0.1.0"
description = "FedEx ROCS chatbot copilot — RAG over operations manuals for ground-ops planners."
requires-python = ">=3.11"
readme = "README.md"
authors = [{ name = "rocs-copilot maintainers" }]
dependencies = [
  "flask>=3.0,<4.0",
  "pydantic>=2.6,<3.0",
  "pydantic-settings>=2.2,<3.0",
  "python-dotenv>=1.0,<2.0",
  "tenacity>=8.2,<9.0",
  "langchain>=0.3,<0.4",
  "langchain-openai>=0.2,<0.3",
  "langchain-groq>=0.2,<0.3",
  "langchain-community>=0.3,<0.4",
  "langchain-chroma>=0.1,<0.2",
  "chromadb>=0.5,<0.6",
  "pypdf>=4.0,<5.0",
  "docx2txt>=0.8,<0.9"
]

[project.optional-dependencies]
dev = [
  "pytest>=8.0,<9.0",
  "pytest-cov>=5.0,<6.0",
  "reportlab>=4.0,<5.0",
  "python-docx>=1.1,<2.0"
]

[project.scripts]
rocs-ingest = "scripts.ingest:main"

[tool.setuptools.packages.find]
where = ["src", "."]
include = ["rocs_copilot_backend*", "scripts*"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-ra --strict-markers"
pythonpath = ["src", "."]
```

> **Note on version pinning:** majors locked, minors floating within a major. The fresh executor should `pip install -e .[dev]` and accept whatever minor pip resolves. If install fails, use `context7` MCP to check the latest valid major for the offending package.

- [ ] **Step 4: Write `.gitignore`**

Create `C:/Users/3626416/Projects/rocs-copilot/.gitignore`:

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.venv/
.pytest_cache/
.coverage
htmlcov/
*.egg-info/
build/
dist/

# Project data (user-supplied corpus + Chroma store)
data/corpus/*
!data/corpus/.gitkeep
data/chroma/*
!data/chroma/.gitkeep

# Env
.env
.env.local

# Frontend
frontend/node_modules/
frontend/dist/
frontend/.vite/

# OS / editor
.DS_Store
Thumbs.db
*.swp
.idea/
.vscode/
```

Also create empty marker files so the dirs are tracked:
```powershell
New-Item -ItemType File data/corpus/.gitkeep | Out-Null
New-Item -ItemType File data/chroma/.gitkeep | Out-Null
```

- [ ] **Step 5: Write `.env.example`**

Create `C:/Users/3626416/Projects/rocs-copilot/.env.example`:

```bash
# Required: which LLM provider to use for chat completion (groq | openai)
LLM_PROVIDER=openai

# Required if LLM_PROVIDER=openai OR for embeddings (always used in MVP)
OPENAI_API_KEY=sk-...

# Required if LLM_PROVIDER=groq
GROQ_API_KEY=gsk_...

# Optional overrides (defaults shown)
OPENAI_CHAT_MODEL=gpt-4o-mini
GROQ_CHAT_MODEL=llama-3.3-70b-versatile
EMBEDDING_MODEL=text-embedding-3-small
CHROMA_DIR=data/chroma
CORPUS_DIR=data/corpus
RETRIEVAL_MIN_SCORE=0.3
RETRIEVAL_TOP_K=4
HISTORY_TURN_CAP=8
```

- [ ] **Step 6: Write minimal `tests/conftest.py`**

Create `C:/Users/3626416/Projects/rocs-copilot/tests/conftest.py`:

```python
"""Shared pytest fixtures. Per-test fixtures live in their own test modules."""
import os
import pytest


@pytest.fixture(autouse=True)
def _clear_env(monkeypatch):
    """Each test starts with a clean env so config.py validation is deterministic."""
    for var in (
        "LLM_PROVIDER", "OPENAI_API_KEY", "GROQ_API_KEY",
        "OPENAI_CHAT_MODEL", "GROQ_CHAT_MODEL", "EMBEDDING_MODEL",
        "CHROMA_DIR", "CORPUS_DIR",
        "RETRIEVAL_MIN_SCORE", "RETRIEVAL_TOP_K", "HISTORY_TURN_CAP",
    ):
        monkeypatch.delenv(var, raising=False)
```

- [ ] **Step 7: Verify file presence**

Run (PowerShell):
```powershell
Get-ChildItem pyproject.toml, .gitignore, .env.example | Format-Table Name, Length
```
Expected: three rows, each with non-zero Length.

(No commit yet — git not initialized; Task 1.2 does that.)

## Task 1.2: `git init` + initial commit

**Files:** none new; commits the artifacts created in Task 1.1.

- [ ] **Step 1: Initialize git repo**

Run (Bash):
```bash
git init -b main
git config user.name "rocs-copilot bootstrap"
git config user.email "rocs-copilot@example.invalid"
```

> Replace `user.name` / `user.email` with your real values if the project will grow beyond the MVP, or rely on global git config. Local config keeps the bootstrap deterministic.

- [ ] **Step 2: Stage and inspect**

Run (Bash):
```bash
git add pyproject.toml .gitignore .env.example src/ scripts/ tests/ data/corpus/.gitkeep data/chroma/.gitkeep
git status
```
Expected: all listed files staged as new. No tracked files in `data/corpus/` other than `.gitkeep`.

- [ ] **Step 3: Initial commit**

Run (Bash):
```bash
git commit -m "chore: bootstrap project skeleton (pyproject, gitignore, package layout)"
```
Expected: one commit with ~12 files.

## Task 1.3: Create virtualenv + install dependencies

**Files:** none new.

- [ ] **Step 1: Create `.venv`**

Run (PowerShell):
```powershell
py -3.11 -m venv .venv
```
Expected: `.venv/Scripts/python.exe` exists.

Verify (PowerShell):
```powershell
.venv/Scripts/python.exe --version
```
Expected: `Python 3.11.x` (or higher patch).

- [ ] **Step 2: Upgrade pip + install project in editable mode with dev extras**

Run (PowerShell):
```powershell
.venv/Scripts/python.exe -m pip install --upgrade pip
.venv/Scripts/python.exe -m pip install -e ".[dev]"
```
Expected: long install log; final line `Successfully installed ...`. If any pin in `pyproject.toml` fails to resolve, use `context7` MCP to check the package's current major version, update `pyproject.toml`, retry.

- [ ] **Step 3: Smoke-test the install**

Run (PowerShell):
```powershell
.venv/Scripts/python.exe -c "import flask, langchain, chromadb, pydantic_settings, tenacity, pypdf, docx2txt; print('ok')"
.venv/Scripts/pytest.exe --version
```
Expected: `ok` printed; `pytest 8.x.x`.

- [ ] **Step 4: Commit nothing (no new files)**

`.venv/` is gitignored. Skip commit.

## Task 1.4: Generate fixture corpus

Two tiny synthetic documents (one PDF, one DOCX) live in `tests/fixtures/corpus/`. A one-off generator script creates them, then the binary outputs are committed (per spec §9.5).

**Files:**
- Create: `tests/fixtures/generate_corpus.py`
- Create (via generator): `tests/fixtures/corpus/sample-rocs-module.pdf`
- Create (via generator): `tests/fixtures/corpus/sample-error-catalog.docx`

- [ ] **Step 1: Write the generator script**

Create `C:/Users/3626416/Projects/rocs-copilot/tests/fixtures/generate_corpus.py`:

```python
"""One-off generator for synthetic test fixtures.

Run once (outputs are committed); rerun only if you change the fixture content.

Usage:
    .venv/Scripts/python.exe tests/fixtures/generate_corpus.py
"""
from pathlib import Path

from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

OUT = Path(__file__).parent / "corpus"
OUT.mkdir(parents=True, exist_ok=True)


def make_pdf() -> None:
    path = OUT / "sample-rocs-module.pdf"
    c = canvas.Canvas(str(path), pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, 720, "Sample ROCS Module — Fictional Test Fixture")
    c.setFont("Helvetica", 11)
    body = [
        "This is a synthetic test fixture, not a real FedEx document.",
        "",
        "The Sample Routing Module governs how the Sample Engine assigns",
        "fictional stops to fictional vehicles. It uses heuristic SAMPLE-A",
        "by default and falls back to SAMPLE-B when stop windows conflict.",
        "",
        "Error code SAMPLE-001 indicates the engine could not reconcile",
        "stop windows for a given vehicle. To resolve, planners should",
        "verify the stop manifest in the Sample Manifest screen and rerun",
        "the routing step. Error code SAMPLE-002 indicates a missing",
        "vehicle capacity profile; planners must populate the profile in",
        "the Sample Fleet screen.",
        "",
        "This document exists solely to exercise PyPDFLoader in tests.",
    ]
    y = 690
    for line in body:
        c.drawString(72, y, line)
        y -= 16
    c.showPage()
    c.save()
    print(f"wrote {path}")


def make_docx() -> None:
    path = OUT / "sample-error-catalog.docx"
    doc = Document()
    doc.add_heading("Sample Error Catalog — Fictional Test Fixture", level=1)
    doc.add_paragraph(
        "This is a synthetic test fixture, not a real FedEx document."
    )
    doc.add_heading("Error SAMPLE-100", level=2)
    doc.add_paragraph(
        "Triggered when the Sample Discrepancy Resolver finds a mismatch "
        "between planned and actual stop counts. Recommended action: "
        "open the Sample Reconciliation panel and accept or override the "
        "discrepancy line item."
    )
    doc.add_heading("Error SAMPLE-200", level=2)
    doc.add_paragraph(
        "Indicates the Sample Heuristic timed out. Recommended action: "
        "reduce the planning horizon to a single shift and rerun."
    )
    doc.save(str(path))
    print(f"wrote {path}")


def main() -> None:
    make_pdf()
    make_docx()


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run the generator**

Run (PowerShell):
```powershell
.venv/Scripts/python.exe tests/fixtures/generate_corpus.py
```
Expected: two lines `wrote .../sample-rocs-module.pdf` and `wrote .../sample-error-catalog.docx`.

Verify:
```powershell
Get-ChildItem tests/fixtures/corpus | Format-Table Name, Length
```
Expected: two files, both with non-zero Length (PDF ~3 KB, DOCX ~7 KB).

- [ ] **Step 3: Commit generator + fixtures**

Run (Bash):
```bash
git add tests/fixtures/generate_corpus.py tests/fixtures/corpus/sample-rocs-module.pdf tests/fixtures/corpus/sample-error-catalog.docx
git commit -m "test: add synthetic fixture corpus generator + outputs"
```

## Task 1.5: Smoke — pytest discovery

**Files:**
- Create: `tests/test_smoke.py`

- [ ] **Step 1: Write a trivial passing test**

Create `C:/Users/3626416/Projects/rocs-copilot/tests/test_smoke.py`:

```python
def test_pytest_runs():
    assert 1 + 1 == 2
```

- [ ] **Step 2: Run pytest**

Run (PowerShell):
```powershell
.venv/Scripts/pytest.exe -v
```
Expected: `tests/test_smoke.py::test_pytest_runs PASSED`; exit 0.

- [ ] **Step 3: Commit**

Run (Bash):
```bash
git add tests/test_smoke.py
git commit -m "test: smoke test that pytest discovers and runs"
```

---

# Phase 2 — Ingestion

Goal: text splitter, provider factory, Chroma store with idempotency, document loader, CLI orchestrator. Test-first for chunker, store, provider factory; smoke for loader and CLI.

## Task 2.1: `chunker.py` — text splitter wrapper (TDD)

**Files:**
- Create: `tests/test_chunker.py`
- Create: `src/rocs_copilot_backend/ingest/chunker.py`

- [ ] **Step 1: Write the failing test**

Create `C:/Users/3626416/Projects/rocs-copilot/tests/test_chunker.py`:

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run (PowerShell):
```powershell
.venv/Scripts/pytest.exe tests/test_chunker.py -v
```
Expected: `ImportError` / `ModuleNotFoundError` because `chunker.py` doesn't exist yet.

- [ ] **Step 3: Write minimal implementation**

Create `C:/Users/3626416/Projects/rocs-copilot/src/rocs_copilot_backend/ingest/chunker.py`:

```python
"""Text splitter wrapper. Defaults locked by spec §6.1: chunk_size=1000, chunk_overlap=100."""
from __future__ import annotations

from langchain_text_splitters import RecursiveCharacterTextSplitter

DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 100


def split_text(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    return splitter.split_text(text)
```

> `langchain-text-splitters` is a transitive dep of `langchain`. If the import fails, add it explicitly to `pyproject.toml` deps as `langchain-text-splitters>=0.3,<0.4` and reinstall.

- [ ] **Step 4: Run tests to verify they pass**

Run (PowerShell):
```powershell
.venv/Scripts/pytest.exe tests/test_chunker.py -v
```
Expected: 3 PASSED.

- [ ] **Step 5: Commit**

Run (Bash):
```bash
git add tests/test_chunker.py src/rocs_copilot_backend/ingest/chunker.py
git commit -m "feat(ingest): chunker with 1000/100 defaults from spec"
```

## Task 2.2: `providers/llm.py` — embeddings + chat-model factories (TDD)

The factory branches on `LLM_PROVIDER` env var. We test the branching + failure modes with mocked SDKs.

**Files:**
- Create: `tests/test_provider_factory.py`
- Create: `src/rocs_copilot_backend/providers/llm.py`

- [ ] **Step 1: Write the failing tests**

Create `C:/Users/3626416/Projects/rocs-copilot/tests/test_provider_factory.py`:

```python
import pytest

from rocs_copilot_backend.providers import llm as factory


def test_get_chat_model_openai(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-fake")
    model = factory.get_chat_model()
    # Class name check is enough to confirm we got the OpenAI branch.
    assert model.__class__.__name__ == "ChatOpenAI"


def test_get_chat_model_groq(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "groq")
    monkeypatch.setenv("GROQ_API_KEY", "gsk-fake")
    model = factory.get_chat_model()
    assert model.__class__.__name__ == "ChatGroq"


def test_get_chat_model_unknown_provider_raises(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-fake")
    with pytest.raises(ValueError, match="Unknown LLM_PROVIDER"):
        factory.get_chat_model()


def test_get_chat_model_missing_provider_raises(monkeypatch):
    # LLM_PROVIDER not set
    with pytest.raises(ValueError, match="LLM_PROVIDER is required"):
        factory.get_chat_model()


def test_get_chat_model_openai_missing_api_key_raises(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    # OPENAI_API_KEY not set
    with pytest.raises(ValueError, match="OPENAI_API_KEY is required"):
        factory.get_chat_model()


def test_get_chat_model_groq_missing_api_key_raises(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "groq")
    # GROQ_API_KEY not set
    with pytest.raises(ValueError, match="GROQ_API_KEY is required"):
        factory.get_chat_model()


def test_get_embeddings_always_openai(monkeypatch):
    """Spec §10: embeddings always use OpenAI in MVP regardless of LLM_PROVIDER."""
    monkeypatch.setenv("LLM_PROVIDER", "groq")
    monkeypatch.setenv("GROQ_API_KEY", "gsk-fake")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-fake")  # still required for embeddings
    emb = factory.get_embeddings()
    assert emb.__class__.__name__ == "OpenAIEmbeddings"


def test_get_embeddings_missing_openai_key_raises(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "groq")
    monkeypatch.setenv("GROQ_API_KEY", "gsk-fake")
    # OPENAI_API_KEY not set
    with pytest.raises(ValueError, match="OPENAI_API_KEY is required"):
        factory.get_embeddings()
```

- [ ] **Step 2: Run tests to verify failure**

Run (PowerShell):
```powershell
.venv/Scripts/pytest.exe tests/test_provider_factory.py -v
```
Expected: all 8 tests fail with `ImportError`.

- [ ] **Step 3: Write implementation**

Create `C:/Users/3626416/Projects/rocs-copilot/src/rocs_copilot_backend/providers/llm.py`:

```python
"""LLM + embeddings provider factory. Branches on LLM_PROVIDER env var.

Per spec §4 + §6.1: provider abstraction is load-bearing because FedEx prod GCP
has no programmatic LLM today. Dev supports openai + groq; embeddings always
OpenAI in MVP.
"""
from __future__ import annotations

import os
from typing import Any


def _require_env(name: str) -> str:
    val = os.getenv(name)
    if not val:
        raise ValueError(f"{name} is required in environment")
    return val


def get_chat_model() -> Any:
    """Return a LangChain chat model instance based on LLM_PROVIDER."""
    provider = os.getenv("LLM_PROVIDER")
    if not provider:
        raise ValueError("LLM_PROVIDER is required in environment (groq | openai)")

    if provider == "openai":
        from langchain_openai import ChatOpenAI

        api_key = _require_env("OPENAI_API_KEY")
        model = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")
        return ChatOpenAI(model=model, api_key=api_key, streaming=True)

    if provider == "groq":
        from langchain_groq import ChatGroq

        api_key = _require_env("GROQ_API_KEY")
        model = os.getenv("GROQ_CHAT_MODEL", "llama-3.3-70b-versatile")
        return ChatGroq(model=model, api_key=api_key, streaming=True)

    raise ValueError(
        f"Unknown LLM_PROVIDER={provider!r}. Supported: groq, openai."
    )


def get_embeddings() -> Any:
    """Return a LangChain embeddings instance.

    Per spec §10: embeddings always use OpenAI in MVP, regardless of LLM_PROVIDER.
    """
    from langchain_openai import OpenAIEmbeddings

    api_key = _require_env("OPENAI_API_KEY")
    model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    return OpenAIEmbeddings(model=model, api_key=api_key)
```

- [ ] **Step 4: Run tests to verify pass**

Run (PowerShell):
```powershell
.venv/Scripts/pytest.exe tests/test_provider_factory.py -v
```
Expected: 8 PASSED.

- [ ] **Step 5: Commit**

Run (Bash):
```bash
git add tests/test_provider_factory.py src/rocs_copilot_backend/providers/llm.py
git commit -m "feat(providers): LLM + embeddings factory branching on LLM_PROVIDER"
```

## Task 2.3: `ingest/store.py` — Chroma upsert with content-hash idempotency (TDD)

The store wraps Chroma. Embeddings are passed in (DI) so tests can use a fake. Content-hash idempotency means re-ingesting the same file twice produces zero new vectors.

**Files:**
- Create: `tests/test_store.py`
- Create: `src/rocs_copilot_backend/ingest/store.py`

- [ ] **Step 1: Write the failing tests**

Create `C:/Users/3626416/Projects/rocs-copilot/tests/test_store.py`:

```python
"""Tests for the Chroma store wrapper. Uses tmp_path + fake embeddings."""
from __future__ import annotations

import hashlib

import pytest

from rocs_copilot_backend.ingest.store import (
    ChromaStore,
    compute_content_hash,
)


class FakeEmbeddings:
    """Deterministic embedding: 1536-dim vector of hash-derived floats."""

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._vec(t) for t in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._vec(text)

    def _vec(self, text: str) -> list[float]:
        h = hashlib.sha256(text.encode()).digest()
        # Repeat to 1536 dims; values in [-1, 1].
        return [((b / 255.0) * 2.0) - 1.0 for b in (h * 48)[:1536]]


@pytest.fixture
def store(tmp_path):
    return ChromaStore(
        persist_dir=str(tmp_path / "chroma"),
        embeddings=FakeEmbeddings(),
    )


def test_compute_content_hash_is_deterministic():
    h1 = compute_content_hash("hello world")
    h2 = compute_content_hash("hello world")
    h3 = compute_content_hash("hello world!")
    assert h1 == h2
    assert h1 != h3
    assert len(h1) == 64  # sha256 hex


def test_upsert_then_retrieve(store):
    store.upsert_chunks(
        source="manual.pdf",
        page=1,
        chunks=["Sample text about routing.", "Another chunk about errors."],
    )
    results = store.similarity_search("routing", k=2)
    assert len(results) == 2
    # Both chunks should be retrieved; ordering depends on similarity.
    texts = {r["text"] for r in results}
    assert texts == {"Sample text about routing.", "Another chunk about errors."}


def test_upsert_is_idempotent(store):
    """Spec §6.1: content-hash idempotency. Re-ingesting same source+content adds no duplicates."""
    chunks = ["Sample text about routing.", "Another chunk about errors."]
    store.upsert_chunks(source="manual.pdf", page=1, chunks=chunks)
    store.upsert_chunks(source="manual.pdf", page=1, chunks=chunks)  # re-run
    results = store.similarity_search("routing", k=10)
    assert len(results) == 2  # not 4


def test_similarity_search_returns_metadata(store):
    store.upsert_chunks(source="manual.pdf", page=7, chunks=["Routing details."])
    results = store.similarity_search("routing", k=1)
    assert results[0]["source"] == "manual.pdf"
    assert results[0]["page"] == 7
    assert "score" in results[0]
    assert "text" in results[0]


def test_count_returns_zero_for_empty_store(store):
    assert store.count() == 0


def test_count_returns_total_chunks(store):
    store.upsert_chunks(source="a.pdf", page=1, chunks=["one", "two"])
    store.upsert_chunks(source="b.pdf", page=1, chunks=["three"])
    assert store.count() == 3
```

- [ ] **Step 2: Run tests to verify failure**

Run (PowerShell):
```powershell
.venv/Scripts/pytest.exe tests/test_store.py -v
```
Expected: `ImportError` / `ModuleNotFoundError`.

- [ ] **Step 3: Write implementation**

Create `C:/Users/3626416/Projects/rocs-copilot/src/rocs_copilot_backend/ingest/store.py`:

```python
"""Chroma store wrapper with content-hash idempotency.

Per spec §6.1: re-running ingest on the same source file produces no duplicates.
Embeddings are injected (DI) so the call site decides which provider to use and
tests can substitute a fake.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from langchain_chroma import Chroma

COLLECTION_NAME = "rocs_copilot"


def compute_content_hash(text: str) -> str:
    """Stable sha256 hex of the chunk text. Used as the Chroma document ID."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class ChromaStore:
    """Thin wrapper around langchain_chroma.Chroma with idempotent upserts."""

    def __init__(self, persist_dir: str, embeddings: Any) -> None:
        Path(persist_dir).mkdir(parents=True, exist_ok=True)
        self._client = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=embeddings,
            persist_directory=persist_dir,
        )

    def upsert_chunks(
        self,
        source: str,
        page: int,
        chunks: list[str],
    ) -> None:
        """Upsert chunks with content-hash IDs. Re-upserting same text is a no-op."""
        if not chunks:
            return
        ids = [compute_content_hash(c) for c in chunks]
        metadatas = [{"source": source, "page": page} for _ in chunks]
        # Chroma's add_texts upserts when IDs match.
        self._client.add_texts(texts=chunks, metadatas=metadatas, ids=ids)

    def similarity_search(self, query: str, k: int = 4) -> list[dict]:
        """Return top-k hits with text + metadata + cosine similarity score (0..1)."""
        # similarity_search_with_relevance_scores returns a relevance score in [0,1]
        # (1 = identical, 0 = unrelated) — what we want for §8.2 threshold checks.
        hits = self._client.similarity_search_with_relevance_scores(query, k=k)
        return [
            {
                "text": doc.page_content,
                "source": doc.metadata.get("source", ""),
                "page": doc.metadata.get("page", 0),
                "score": float(score),
            }
            for doc, score in hits
        ]

    def count(self) -> int:
        """Total number of vectors in the collection."""
        return self._client._collection.count()
```

- [ ] **Step 4: Run tests**

Run (PowerShell):
```powershell
.venv/Scripts/pytest.exe tests/test_store.py -v
```
Expected: 6 PASSED. (If Chroma emits telemetry warnings, those are not failures.)

- [ ] **Step 5: Commit**

Run (Bash):
```bash
git add tests/test_store.py src/rocs_copilot_backend/ingest/store.py
git commit -m "feat(ingest): Chroma store wrapper with content-hash idempotency"
```

## Task 2.4: `ingest/loader.py` — PyPDF + Docx2txt loaders (smoke test)

Loaders are thin wrappers around LangChain community loaders. We smoke-test against the fixture corpus rather than full TDD.

**Files:**
- Create: `tests/test_loader.py`
- Create: `src/rocs_copilot_backend/ingest/loader.py`

- [ ] **Step 1: Write the implementation first (smoke style)**

Create `C:/Users/3626416/Projects/rocs-copilot/src/rocs_copilot_backend/ingest/loader.py`:

```python
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
```

- [ ] **Step 2: Write a smoke test against the fixtures**

Create `C:/Users/3626416/Projects/rocs-copilot/tests/test_loader.py`:

```python
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
```

- [ ] **Step 3: Run tests**

Run (PowerShell):
```powershell
.venv/Scripts/pytest.exe tests/test_loader.py -v
```
Expected: 5 PASSED.

- [ ] **Step 4: Commit**

Run (Bash):
```bash
git add tests/test_loader.py src/rocs_copilot_backend/ingest/loader.py
git commit -m "feat(ingest): PDF + DOCX loaders with uniform metadata shape"
```

## Task 2.5: `scripts/ingest.py` — CLI orchestrator

Walks `data/corpus/`, loads → chunks → embeds → upserts. Logs per-file progress. Exits non-zero on hard failures (missing API key, Chroma error). Logs + skips + continues on per-file parse failures. Wraps the embeddings call in `tenacity` backoff (3 attempts: 1s/4s/16s) per spec §8.1.

**Files:**
- Create: `tests/test_cli_ingest.py`
- Create: `scripts/ingest.py`

- [ ] **Step 1: Write the CLI implementation**

Create `C:/Users/3626416/Projects/rocs-copilot/scripts/ingest.py`:

```python
"""Ingestion CLI.

Walks CORPUS_DIR, parses PDFs/DOCX, chunks, embeds, upserts into Chroma.
- Per-file parse failures: log + skip + continue (spec §8.1).
- Missing API keys / Chroma errors: fail loud, non-zero exit (spec §8.1).
- Embeddings API failures: tenacity backoff 3 attempts at 1s / 4s / 16s.

Usage:
    .venv/Scripts/python.exe scripts/ingest.py
    .venv/Scripts/python.exe -m scripts.ingest
"""
from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from rocs_copilot_backend.ingest.chunker import split_text
from rocs_copilot_backend.ingest.loader import LoaderError, iter_corpus, load_file
from rocs_copilot_backend.ingest.store import ChromaStore
from rocs_copilot_backend.providers.llm import get_embeddings

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(message)s",
)
log = logging.getLogger("ingest")


# Embeddings call wrapped with tenacity: 3 attempts at ~1s, 4s, 16s.
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=16),
    retry=retry_if_exception_type(Exception),
    reraise=True,
)
def _upsert_with_retry(store: ChromaStore, source: str, page: int, chunks: list[str]) -> None:
    store.upsert_chunks(source=source, page=page, chunks=chunks)


def _resolve_corpus_dir() -> Path:
    raw = os.getenv("CORPUS_DIR", "data/corpus")
    return Path(raw).resolve()


def _resolve_chroma_dir() -> Path:
    raw = os.getenv("CHROMA_DIR", "data/chroma")
    return Path(raw).resolve()


def main() -> int:
    load_dotenv()  # picks up .env if present

    corpus_dir = _resolve_corpus_dir()
    if not corpus_dir.exists() or not any(corpus_dir.iterdir()):
        log.error(
            "No documents found in %s. Drop PDFs/DOCX there and rerun.",
            corpus_dir,
        )
        return 1

    try:
        embeddings = get_embeddings()  # raises ValueError on missing API key (fail loud)
    except ValueError as e:
        log.error("Provider misconfig: %s", e)
        return 2

    try:
        store = ChromaStore(persist_dir=str(_resolve_chroma_dir()), embeddings=embeddings)
    except Exception as e:
        log.error("Failed to open Chroma store: %s", e)
        return 3

    indexed = 0
    skipped = 0
    for path in iter_corpus(corpus_dir):
        try:
            pages = load_file(path)
        except LoaderError as e:
            log.warning("skipped %s: %s", path.name, e)
            skipped += 1
            continue

        for text, meta in pages:
            chunks = split_text(text)
            if not chunks:
                continue
            try:
                _upsert_with_retry(
                    store, source=meta["source"], page=meta["page"], chunks=chunks
                )
            except Exception as e:
                log.error(
                    "Failed to upsert %s page %s after retries: %s",
                    meta["source"], meta["page"], e,
                )
                return 4
        indexed += 1
        log.info("indexed %s", path.name)

    log.info("Indexed: %d / Skipped: %d", indexed, skipped)
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Write CLI tests (smoke-style with mocked embeddings)**

Create `C:/Users/3626416/Projects/rocs-copilot/tests/test_cli_ingest.py`:

```python
"""Smoke tests for the ingestion CLI. Uses fake embeddings + tmp Chroma dir."""
from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from rocs_copilot_backend.ingest.store import ChromaStore
from tests.test_store import FakeEmbeddings  # reuse the deterministic fake

import scripts.ingest as ingest_cli


@pytest.fixture
def patched_dirs(tmp_path, monkeypatch):
    corpus = tmp_path / "corpus"
    chroma = tmp_path / "chroma"
    corpus.mkdir()
    chroma.mkdir()
    monkeypatch.setenv("CORPUS_DIR", str(corpus))
    monkeypatch.setenv("CHROMA_DIR", str(chroma))
    # Copy the fixture corpus into the tmp corpus dir.
    fixtures = Path(__file__).parent / "fixtures" / "corpus"
    for f in fixtures.iterdir():
        shutil.copy(f, corpus / f.name)
    return corpus, chroma


@pytest.fixture
def fake_embeddings(monkeypatch):
    """Replace the real embeddings factory with a deterministic fake."""
    monkeypatch.setattr(ingest_cli, "get_embeddings", lambda: FakeEmbeddings())


def test_main_indexes_fixtures(patched_dirs, fake_embeddings, caplog):
    caplog.set_level("INFO")
    rc = ingest_cli.main()
    assert rc == 0
    assert "Indexed: 2 / Skipped: 0" in caplog.text


def test_main_empty_corpus_returns_1(tmp_path, monkeypatch, fake_embeddings, caplog):
    empty_corpus = tmp_path / "empty"
    empty_corpus.mkdir()
    monkeypatch.setenv("CORPUS_DIR", str(empty_corpus))
    monkeypatch.setenv("CHROMA_DIR", str(tmp_path / "chroma"))
    caplog.set_level("ERROR")
    rc = ingest_cli.main()
    assert rc == 1
    assert "No documents found" in caplog.text


def test_main_missing_api_key_returns_2(patched_dirs, monkeypatch, caplog):
    # Real factory is in play (no fake_embeddings fixture). No OPENAI_API_KEY set.
    caplog.set_level("ERROR")
    rc = ingest_cli.main()
    assert rc == 2
    assert "Provider misconfig" in caplog.text
```

- [ ] **Step 3: Run tests**

Run (PowerShell):
```powershell
.venv/Scripts/pytest.exe tests/test_cli_ingest.py -v
```
Expected: 3 PASSED.

- [ ] **Step 4: Commit**

Run (Bash):
```bash
git add tests/test_cli_ingest.py scripts/ingest.py
git commit -m "feat(ingest): CLI orchestrator with tenacity backoff + skip-and-continue"
```

---

# Phase 3 — Backend serving

Goal: config validation at startup, RAG chain (history-aware retriever + LLM + parser), health route, chat SSE route, Flask app factory. TDD for chain + chat route; smoke for config, health, app factory.

## Task 3.1: `config.py` — pydantic settings (TDD-light: validation behavior)

**Files:**
- Create: `tests/test_config.py`
- Create: `src/rocs_copilot_backend/config.py`

- [ ] **Step 1: Write tests for validation behavior**

Create `C:/Users/3626416/Projects/rocs-copilot/tests/test_config.py`:

```python
import pytest
from pydantic import ValidationError

from rocs_copilot_backend.config import Settings


def test_settings_loads_with_defaults(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-fake")
    s = Settings()
    assert s.llm_provider == "openai"
    assert s.retrieval_min_score == 0.3
    assert s.retrieval_top_k == 4
    assert s.history_turn_cap == 8
    assert s.chroma_dir == "data/chroma"
    assert s.corpus_dir == "data/corpus"
    assert s.embedding_model == "text-embedding-3-small"


def test_settings_requires_llm_provider(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-fake")
    with pytest.raises(ValidationError):
        Settings()


def test_settings_rejects_unknown_provider(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-fake")
    with pytest.raises(ValidationError):
        Settings()


def test_settings_overrides_via_env(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "groq")
    monkeypatch.setenv("GROQ_API_KEY", "gsk-fake")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-fake")
    monkeypatch.setenv("RETRIEVAL_MIN_SCORE", "0.5")
    monkeypatch.setenv("RETRIEVAL_TOP_K", "8")
    s = Settings()
    assert s.retrieval_min_score == 0.5
    assert s.retrieval_top_k == 8
```

- [ ] **Step 2: Verify failure**

Run (PowerShell):
```powershell
.venv/Scripts/pytest.exe tests/test_config.py -v
```
Expected: `ImportError`.

- [ ] **Step 3: Write implementation**

Create `C:/Users/3626416/Projects/rocs-copilot/src/rocs_copilot_backend/config.py`:

```python
"""Application settings.

Per spec §10: env-driven via pydantic-settings; validation runs at app startup
(failing Flask boot rather than per-request). Per §8.2 missing-API-key handling
happens in providers/llm.py, not here, because the right key depends on which
provider is selected at request time. Settings just validates LLM_PROVIDER itself.
"""
from __future__ import annotations

from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    llm_provider: Literal["groq", "openai"] = Field(...)
    openai_api_key: str | None = None
    groq_api_key: str | None = None

    openai_chat_model: str = "gpt-4o-mini"
    groq_chat_model: str = "llama-3.3-70b-versatile"
    embedding_model: str = "text-embedding-3-small"

    chroma_dir: str = "data/chroma"
    corpus_dir: str = "data/corpus"

    retrieval_min_score: float = 0.3
    retrieval_top_k: int = 4
    history_turn_cap: int = 8
```

- [ ] **Step 4: Run tests**

Run (PowerShell):
```powershell
.venv/Scripts/pytest.exe tests/test_config.py -v
```
Expected: 4 PASSED.

- [ ] **Step 5: Commit**

Run (Bash):
```bash
git add tests/test_config.py src/rocs_copilot_backend/config.py
git commit -m "feat(config): pydantic settings with startup validation"
```

## Task 3.2: `chains/rag_chain.py` — LCEL with history-aware retriever (TDD)

The chain composes a history-aware retriever (rewrites follow-ups using prior turns BEFORE Chroma search) and the chat model. We test composition + that the rewrite step is invoked.

**Files:**
- Create: `tests/test_rag_chain.py`
- Create: `src/rocs_copilot_backend/chains/rag_chain.py`

- [ ] **Step 1: Write the failing tests**

Create `C:/Users/3626416/Projects/rocs-copilot/tests/test_rag_chain.py`:

```python
"""Tests for the RAG chain. Mocks the LLM and the store; verifies orchestration."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from rocs_copilot_backend.chains.rag_chain import build_chain, rewrite_question


class FakeChatModel:
    """Records calls and returns a canned response. Mimics LangChain's BaseChatModel surface enough for our chain."""

    def __init__(self, response: str = "REWRITTEN") -> None:
        self.calls: list[str] = []
        self._response = response

    def invoke(self, messages, **_):
        # `messages` is a list of (role, content) tuples or BaseMessage. Capture content.
        captured = "\n".join(getattr(m, "content", str(m)) for m in messages)
        self.calls.append(captured)
        from langchain_core.messages import AIMessage
        return AIMessage(content=self._response)


def test_rewrite_question_no_history_returns_input():
    """No prior turns → standalone query == original question."""
    llm = FakeChatModel(response="ignored")
    out = rewrite_question(llm, question="What is error SAMPLE-001?", history=[])
    assert out == "What is error SAMPLE-001?"
    assert llm.calls == []  # short-circuit: no LLM call when history is empty


def test_rewrite_question_with_history_invokes_llm():
    """Prior turns → LLM is asked to rewrite into a standalone query."""
    llm = FakeChatModel(response="What is error SAMPLE-001?")
    history = [
        {"role": "user", "content": "Tell me about routing errors."},
        {"role": "assistant", "content": "There are several. SAMPLE-001 is..."},
    ]
    out = rewrite_question(llm, question="Tell me more about that one.", history=history)
    assert out == "What is error SAMPLE-001?"
    assert len(llm.calls) == 1


def test_build_chain_returns_callable():
    """Composition smoke: chain is callable with (question, history)."""
    llm = FakeChatModel(response="Sample answer about SAMPLE-001.")

    class FakeStore:
        def similarity_search(self, query, k):
            return [
                {"text": "SAMPLE-001 means routing failed.", "source": "manual.pdf",
                 "page": 1, "score": 0.8},
            ]

    chain = build_chain(llm=llm, store=FakeStore(), min_score=0.3, top_k=4)
    assert callable(chain.stream)


def test_chain_stream_yields_answer_then_sources():
    """Spec §7.2: emits answer tokens, then a 'sources' marker, then done."""
    llm = MagicMock()
    # llm.stream yields BaseMessageChunks with .content
    from langchain_core.messages import AIMessageChunk

    llm.stream = MagicMock(return_value=iter([
        AIMessageChunk(content="Based "),
        AIMessageChunk(content="on the manual, "),
        AIMessageChunk(content="SAMPLE-001 means..."),
    ]))
    llm.invoke = MagicMock(return_value=AIMessageChunk(content="standalone"))

    class FakeStore:
        def similarity_search(self, query, k):
            return [
                {"text": "...", "source": "manual.pdf", "page": 1, "score": 0.8},
            ]

    chain = build_chain(llm=llm, store=FakeStore(), min_score=0.3, top_k=4)
    events = list(chain.stream(question="What is SAMPLE-001?", history=[]))

    # Expect: 3 token events, 1 source event, 1 done event.
    kinds = [e["kind"] for e in events]
    assert kinds.count("token") == 3
    assert kinds.count("source") == 1
    assert kinds.count("done") == 1
    # Order: all tokens before source, source before done (spec §7.2).
    assert kinds.index("source") > max(i for i, k in enumerate(kinds) if k == "token")
    assert kinds.index("done") == len(kinds) - 1


def test_chain_stream_retrieval_miss_yields_canned_answer_no_source():
    """Spec §8.2: best score < min_score → canned response, no LLM call, no source event."""
    llm = MagicMock()
    llm.stream = MagicMock(side_effect=AssertionError("LLM should NOT be called on retrieval miss"))

    class FakeStore:
        def similarity_search(self, query, k):
            return [{"text": "irrelevant", "source": "x.pdf", "page": 1, "score": 0.1}]

    chain = build_chain(llm=llm, store=FakeStore(), min_score=0.3, top_k=4)
    events = list(chain.stream(question="totally off-topic", history=[]))

    kinds = [e["kind"] for e in events]
    assert "source" not in kinds  # no source event on miss
    assert kinds[-1] == "done"
    full_text = "".join(e["text"] for e in events if e["kind"] == "token")
    assert "I don't have documentation covering that" in full_text


def test_chain_stream_no_hits_yields_canned_answer():
    """Empty retrieval → same canned response as score-below-threshold."""
    llm = MagicMock()
    llm.stream = MagicMock(side_effect=AssertionError("LLM should NOT be called"))

    class FakeStore:
        def similarity_search(self, query, k):
            return []

    chain = build_chain(llm=llm, store=FakeStore(), min_score=0.3, top_k=4)
    events = list(chain.stream(question="anything", history=[]))
    full_text = "".join(e["text"] for e in events if e["kind"] == "token")
    assert "I don't have documentation covering that" in full_text
```

- [ ] **Step 2: Verify failure**

Run (PowerShell):
```powershell
.venv/Scripts/pytest.exe tests/test_rag_chain.py -v
```
Expected: `ImportError`.

- [ ] **Step 3: Write implementation**

Create `C:/Users/3626416/Projects/rocs-copilot/src/rocs_copilot_backend/chains/rag_chain.py`:

```python
"""RAG chain: history-aware retriever → LLM → token stream.

Per spec §7.3:
  1. If history non-empty, LLM rewrites the question into a standalone query.
  2. Standalone query → Chroma similarity_search (top_k).
  3. If best score < min_score (or zero hits): yield canned no-docs answer; skip LLM.
  4. Otherwise: stream LLM answer tokens, then emit one source event, then done.

Per spec §7.2: ordering is TOKENS → SOURCE → DONE.
"""
from __future__ import annotations

from typing import Any, Iterator

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

NO_DOCS_MESSAGE = (
    "I don't have documentation covering that. "
    "Try asking about specific error codes, ROCS modules, or operational procedures."
)


REWRITE_SYSTEM = (
    "You are a query rewriter. Given a chat history and a new user question, "
    "rewrite the new question as a fully standalone query that captures the user's "
    "intent without needing the prior turns to interpret. If the new question is "
    "already standalone, return it unchanged. Output ONLY the rewritten question."
)

ANSWER_SYSTEM = (
    "You are a helpful assistant for FedEx ROCS planners. Answer the user's question "
    "using ONLY the provided context. If the context is insufficient, say so. Cite the "
    "source documents inline using their filenames when helpful."
)


def rewrite_question(llm: Any, question: str, history: list[dict]) -> str:
    """Rewrite a follow-up question into a standalone retrieval query.

    Short-circuits when history is empty (saves a round-trip).
    """
    if not history:
        return question
    history_text = "\n".join(f"{turn['role']}: {turn['content']}" for turn in history)
    messages = [
        SystemMessage(content=REWRITE_SYSTEM),
        HumanMessage(content=f"Chat history:\n{history_text}\n\nNew question: {question}"),
    ]
    result = llm.invoke(messages)
    return result.content.strip()


def _format_context(hits: list[dict]) -> str:
    return "\n\n".join(
        f"[{h['source']} p.{h['page']}] {h['text']}" for h in hits
    )


def _format_history_messages(history: list[dict]) -> list[Any]:
    out: list[Any] = []
    for turn in history:
        if turn["role"] == "user":
            out.append(HumanMessage(content=turn["content"]))
        else:
            out.append(AIMessage(content=turn["content"]))
    return out


class RagChain:
    def __init__(self, llm: Any, store: Any, min_score: float, top_k: int) -> None:
        self._llm = llm
        self._store = store
        self._min_score = min_score
        self._top_k = top_k

    def stream(self, question: str, history: list[dict]) -> Iterator[dict]:
        # Step 1: rewrite for retrieval
        query = rewrite_question(self._llm, question, history)

        # Step 2: retrieve
        hits = self._store.similarity_search(query, k=self._top_k)

        # Step 3: retrieval-miss → canned answer, NO LLM call, NO source event
        if not hits or hits[0]["score"] < self._min_score:
            for word in NO_DOCS_MESSAGE.split(" "):
                yield {"kind": "token", "text": word + " "}
            yield {"kind": "done"}
            return

        # Step 4: stream LLM answer, then emit source event, then done
        context = _format_context(hits)
        messages = [
            SystemMessage(content=ANSWER_SYSTEM),
            *_format_history_messages(history),
            HumanMessage(content=f"Context:\n{context}\n\nQuestion: {question}"),
        ]
        for chunk in self._llm.stream(messages):
            text = getattr(chunk, "content", "") or ""
            if text:
                yield {"kind": "token", "text": text}

        yield {
            "kind": "source",
            "chunks": [
                {
                    "id": f"{h['source']}:p{h['page']}",
                    "filename": h["source"],
                    "page": h["page"],
                    "score": round(h["score"], 4),
                    "snippet": h["text"][:200],
                }
                for h in hits
            ],
        }
        yield {"kind": "done"}


def build_chain(llm: Any, store: Any, min_score: float, top_k: int) -> RagChain:
    return RagChain(llm=llm, store=store, min_score=min_score, top_k=top_k)
```

- [ ] **Step 4: Run tests**

Run (PowerShell):
```powershell
.venv/Scripts/pytest.exe tests/test_rag_chain.py -v
```
Expected: 6 PASSED.

- [ ] **Step 5: Commit**

Run (Bash):
```bash
git add tests/test_rag_chain.py src/rocs_copilot_backend/chains/rag_chain.py
git commit -m "feat(chains): RAG chain with history-aware retriever + tokens-then-source ordering"
```

## Task 3.3: `routes/health.py` — smoke

**Files:**
- Create: `tests/test_routes_health.py`
- Create: `src/rocs_copilot_backend/routes/health.py`

- [ ] **Step 1: Write implementation**

Create `C:/Users/3626416/Projects/rocs-copilot/src/rocs_copilot_backend/routes/health.py`:

```python
"""GET /api/health — smoke endpoint."""
from flask import Blueprint, jsonify

bp = Blueprint("health", __name__, url_prefix="/api")


@bp.get("/health")
def health():
    return jsonify({"status": "ok"})
```

- [ ] **Step 2: Write smoke test** (depends on Task 3.5 `app.py`; place test now, run after 3.5)

Create `C:/Users/3626416/Projects/rocs-copilot/tests/test_routes_health.py`:

```python
import pytest

from rocs_copilot_backend.app import create_app


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-fake")
    app = create_app()
    return app.test_client()


def test_health_returns_ok(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok"}
```

> Don't run this test yet — `app.py` doesn't exist until Task 3.5. Tests run together at the end of Phase 3.

- [ ] **Step 3: Commit**

Run (Bash):
```bash
git add tests/test_routes_health.py src/rocs_copilot_backend/routes/health.py
git commit -m "feat(routes): /api/health smoke endpoint"
```

## Task 3.4: `routes/chat.py` — SSE streaming endpoint (TDD)

Wraps the RAG chain output as Server-Sent Events: `token`, `source`, `done`, `error`. Handles all error paths from spec §8.2.

**Files:**
- Create: `tests/test_routes_chat.py`
- Create: `src/rocs_copilot_backend/routes/chat.py`

- [ ] **Step 1: Write the failing tests**

Create `C:/Users/3626416/Projects/rocs-copilot/tests/test_routes_chat.py`:

```python
"""Tests for POST /api/chat. Mocks the chain and store."""
from __future__ import annotations

import json
from unittest.mock import patch

import pytest

from rocs_copilot_backend.app import create_app


def _parse_sse(body: bytes) -> list[tuple[str, dict]]:
    """Parse SSE response body into (event_name, data_dict) pairs."""
    events: list[tuple[str, dict]] = []
    cur_event = None
    for line in body.decode().splitlines():
        if line.startswith("event:"):
            cur_event = line.removeprefix("event:").strip()
        elif line.startswith("data:"):
            payload = json.loads(line.removeprefix("data:").strip())
            assert cur_event is not None
            events.append((cur_event, payload))
            cur_event = None
    return events


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-fake")
    app = create_app()
    return app.test_client()


def test_chat_happy_path_streams_tokens_then_source_then_done(client):
    """Spec §7.2: tokens first, then source, then done."""
    fake_events = [
        {"kind": "token", "text": "Hello "},
        {"kind": "token", "text": "world."},
        {"kind": "source", "chunks": [{"id": "m.pdf:p1", "filename": "m.pdf",
                                       "page": 1, "score": 0.8, "snippet": "..."}]},
        {"kind": "done"},
    ]

    def fake_stream(self, question, history):
        yield from fake_events

    from rocs_copilot_backend.chains import rag_chain
    with patch.object(rag_chain.RagChain, "stream", fake_stream):
        resp = client.post("/api/chat", json={"question": "hi", "history": []})

    assert resp.status_code == 200
    assert resp.headers["Content-Type"].startswith("text/event-stream")
    events = _parse_sse(resp.data)
    kinds = [name for name, _ in events]
    # Order assertions per spec §7.2: all tokens before source, source before done.
    assert kinds == ["token", "token", "source", "done"]


def test_chat_no_corpus_emits_error_event(client):
    """Spec §8.2: empty Chroma store → error code 'no_corpus'."""
    def fake_count():
        return 0

    from rocs_copilot_backend.ingest.store import ChromaStore
    with patch.object(ChromaStore, "count", fake_count):
        resp = client.post("/api/chat", json={"question": "hi", "history": []})

    events = _parse_sse(resp.data)
    assert events[0][0] == "error"
    assert events[0][1]["code"] == "no_corpus"
    assert events[-1][0] == "done"


def test_chat_retrieval_miss_streams_canned_no_source(client):
    """Spec §8.2: retrieval miss → canned answer tokens, NO source event."""
    fake_events = [
        {"kind": "token", "text": "I don't have documentation covering that. "},
        {"kind": "token", "text": "Try asking about specific error codes..."},
        {"kind": "done"},
    ]

    def fake_stream(self, question, history):
        yield from fake_events

    from rocs_copilot_backend.chains import rag_chain
    with patch.object(rag_chain.RagChain, "stream", fake_stream):
        resp = client.post("/api/chat", json={"question": "off-topic", "history": []})

    events = _parse_sse(resp.data)
    kinds = [name for name, _ in events]
    assert "source" not in kinds
    assert kinds[-1] == "done"


def test_chat_llm_unavailable_emits_error_event(client):
    """Spec §8.2: LLM provider error mid-stream → error code 'llm_unavailable'."""
    def fake_stream(self, question, history):
        yield {"kind": "token", "text": "Start "}
        raise RuntimeError("rate limited")

    from rocs_copilot_backend.chains import rag_chain
    with patch.object(rag_chain.RagChain, "stream", fake_stream):
        resp = client.post("/api/chat", json={"question": "hi", "history": []})

    events = _parse_sse(resp.data)
    error_events = [e for e in events if e[0] == "error"]
    assert len(error_events) == 1
    assert error_events[0][1]["code"] == "llm_unavailable"
    assert error_events[0][1]["retryable"] is True


def test_chat_invalid_body_returns_400(client):
    """Missing 'question' → 400 (not SSE; this is a client error)."""
    resp = client.post("/api/chat", json={"history": []})
    assert resp.status_code == 400
```

- [ ] **Step 2: Verify failure**

Run (PowerShell):
```powershell
.venv/Scripts/pytest.exe tests/test_routes_chat.py -v
```
Expected: `ImportError` because `app.py` and `routes/chat.py` don't exist yet.

- [ ] **Step 3: Write implementation**

Create `C:/Users/3626416/Projects/rocs-copilot/src/rocs_copilot_backend/routes/chat.py`:

```python
"""POST /api/chat — SSE streaming. Wraps the RAG chain output.

Spec references:
  - §7.1 request shape: {"question": str, "history": [{"role","content"}]}
  - §7.2 ordering: tokens → source → done
  - §8.2 error codes: no_corpus, llm_unavailable, internal (all 'retryable' bool)
"""
from __future__ import annotations

import json
import logging
from typing import Iterator

from flask import Blueprint, Response, current_app, request

log = logging.getLogger(__name__)

bp = Blueprint("chat", __name__, url_prefix="/api")


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


def _generate(
    question: str,
    history: list[dict],
) -> Iterator[str]:
    chain = current_app.extensions["rag_chain"]
    store = current_app.extensions["chroma_store"]

    # §8.2: empty corpus check
    try:
        if store.count() == 0:
            yield _sse("error", {
                "code": "no_corpus",
                "message": "No documents indexed yet. Run scripts/ingest.py first.",
                "retryable": False,
            })
            yield _sse("done", {})
            return
    except Exception as e:
        log.exception("corpus count failed")
        yield _sse("error", {
            "code": "internal",
            "message": "Something went wrong on our end.",
            "retryable": True,
        })
        yield _sse("done", {})
        return

    try:
        for event in chain.stream(question=question, history=history):
            kind = event["kind"]
            if kind == "token":
                yield _sse("token", {"text": event["text"]})
            elif kind == "source":
                yield _sse("source", {"chunks": event["chunks"]})
            elif kind == "done":
                yield _sse("done", {})
    except GeneratorExit:
        log.info("client disconnected")
        raise
    except Exception:
        log.exception("LLM provider error")
        yield _sse("error", {
            "code": "llm_unavailable",
            "message": "The assistant is temporarily unavailable. Please try again in a moment.",
            "retryable": True,
        })
        yield _sse("done", {})


@bp.post("/chat")
def chat():
    body = request.get_json(silent=True) or {}
    question = body.get("question")
    history = body.get("history", [])
    if not question or not isinstance(question, str):
        return ({"error": "missing or invalid 'question'"}, 400)

    return Response(
        _generate(question, history),
        mimetype="text/event-stream",
        headers={"X-Accel-Buffering": "no", "Cache-Control": "no-cache"},
    )
```

> Note: tests for chat run together with health tests after Task 3.5 builds `app.py`.

- [ ] **Step 4: Commit (tests fail until 3.5 — that's fine)**

Run (Bash):
```bash
git add tests/test_routes_chat.py src/rocs_copilot_backend/routes/chat.py
git commit -m "feat(routes): /api/chat SSE endpoint with all spec §8.2 error paths"
```

## Task 3.5: `app.py` — Flask factory wiring + run all backend tests

**Files:**
- Create: `src/rocs_copilot_backend/app.py`

- [ ] **Step 1: Write the app factory**

Create `C:/Users/3626416/Projects/rocs-copilot/src/rocs_copilot_backend/app.py`:

```python
"""Flask app factory. Validates settings at boot; wires routes; injects
chain + store into `app.extensions` so routes can pull them out.

Per spec §8.2: provider misconfig should fail at app startup. We instantiate
the embeddings client and chat model here so a missing API key raises
immediately (Flask refuses to boot).
"""
from __future__ import annotations

import logging

from flask import Flask

from rocs_copilot_backend.chains.rag_chain import build_chain
from rocs_copilot_backend.config import Settings
from rocs_copilot_backend.ingest.store import ChromaStore
from rocs_copilot_backend.providers.llm import get_chat_model, get_embeddings
from rocs_copilot_backend.routes import chat, health

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")


def create_app(settings: Settings | None = None) -> Flask:
    settings = settings or Settings()  # raises ValidationError on bad config

    app = Flask(__name__)
    app.config["SETTINGS"] = settings

    # Eager provider construction — fail fast on missing API keys per §8.2.
    embeddings = get_embeddings()
    chat_model = get_chat_model()

    store = ChromaStore(persist_dir=settings.chroma_dir, embeddings=embeddings)
    rag_chain = build_chain(
        llm=chat_model,
        store=store,
        min_score=settings.retrieval_min_score,
        top_k=settings.retrieval_top_k,
    )

    app.extensions["chroma_store"] = store
    app.extensions["rag_chain"] = rag_chain

    app.register_blueprint(health.bp)
    app.register_blueprint(chat.bp)

    # Dev-only CORS for the Vite dev server (5173). Same-origin in prod.
    @app.after_request
    def _cors(resp):
        resp.headers["Access-Control-Allow-Origin"] = "http://localhost:5173"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
        resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        return resp

    return app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=5000, debug=False, threaded=True)
```

- [ ] **Step 2: Run ALL backend tests**

Run (PowerShell):
```powershell
.venv/Scripts/pytest.exe -v
```
Expected: all tests PASS. (Smoke tests for routes pull `OPENAI_API_KEY=sk-fake` from monkeypatch in their fixtures.)

If chat tests fail because `Settings` doesn't pull from `app.config`, double-check Task 3.1's `Settings` defaults — `Literal["groq","openai"]` enforces the provider check at Settings init, which the fixtures handle by setting `LLM_PROVIDER=openai` + `OPENAI_API_KEY=sk-fake`.

- [ ] **Step 3: Smoke — boot the app manually**

Run (PowerShell):
```powershell
$env:LLM_PROVIDER="openai"; $env:OPENAI_API_KEY="sk-fake-bootcheck"
.venv/Scripts/python.exe -m rocs_copilot_backend.app
```
Expected: Flask logs `Running on http://127.0.0.1:5000`. Curl from another shell:
```powershell
Invoke-RestMethod http://127.0.0.1:5000/api/health
```
Expected: `status : ok`. Stop the server with Ctrl+C.

- [ ] **Step 4: Commit**

Run (Bash):
```bash
git add src/rocs_copilot_backend/app.py
git commit -m "feat(app): Flask app factory with eager provider validation + CORS"
```

---

# Phase 4 — Frontend bootstrap

Goal: Vite + React + TS scaffold, dev proxy, brand theme, placeholder wordmark. Mostly smoke; no TDD here (the interesting frontend logic lives in Phase 5).

## Task 4.1: Scaffold Vite + React + TS

**Files:**
- Create (via Vite scaffold): `frontend/` tree (`package.json`, `tsconfig.json`, `vite.config.ts`, `index.html`, `src/`, etc.)

- [ ] **Step 1: Verify Node + npm available**

Run (PowerShell):
```powershell
node --version
npm --version
```
Expected: Node ≥ 20, npm ≥ 10. If absent, install Node LTS from https://nodejs.org before proceeding.

- [ ] **Step 2: Scaffold Vite project**

Run (PowerShell):
```powershell
npm create vite@latest frontend -- --template react-ts
```
When prompted to confirm, answer `y`. Expected: `frontend/` directory created.

- [ ] **Step 3: Install scaffold deps**

Run (PowerShell):
```powershell
Set-Location frontend
npm install
Set-Location ..
```

- [ ] **Step 4: Install test + extra deps**

Run (PowerShell):
```powershell
Set-Location frontend
npm install --save-dev vitest @vitest/ui jsdom @testing-library/react @testing-library/jest-dom @testing-library/user-event
npm install --save react-markdown
Set-Location ..
```

- [ ] **Step 5: Add vitest script + jsdom env to `frontend/package.json`**

Open `frontend/package.json` and modify the `scripts` section so it includes:
```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "preview": "vite preview",
    "test": "vitest run",
    "test:watch": "vitest"
  }
}
```

- [ ] **Step 6: Smoke build**

Run (PowerShell):
```powershell
Set-Location frontend
npm run build
Set-Location ..
```
Expected: `dist/` built without TypeScript errors.

- [ ] **Step 7: Commit**

Run (Bash):
```bash
git add frontend/
git commit -m "chore(frontend): Vite + React + TypeScript scaffold with Vitest"
```

## Task 4.2: `vite.config.ts` — proxy `/api/*` to Flask `:5000`

**Files:**
- Modify: `frontend/vite.config.ts`
- Create: `frontend/vitest.config.ts`

- [ ] **Step 1: Replace `vite.config.ts`**

Overwrite `C:/Users/3626416/Projects/rocs-copilot/frontend/vite.config.ts`:

```ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://127.0.0.1:5000",
        changeOrigin: true,
      },
    },
  },
});
```

- [ ] **Step 2: Add a Vitest config**

Create `C:/Users/3626416/Projects/rocs-copilot/frontend/vitest.config.ts`:

```ts
import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./src/test-setup.ts"],
  },
});
```

Create `C:/Users/3626416/Projects/rocs-copilot/frontend/src/test-setup.ts`:

```ts
import "@testing-library/jest-dom/vitest";
```

- [ ] **Step 3: Smoke — run vitest**

Run (PowerShell):
```powershell
Set-Location frontend
npm run test
Set-Location ..
```
Expected: vitest reports `No test files found` (or runs zero tests). Zero failures.

- [ ] **Step 4: Commit**

Run (Bash):
```bash
git add frontend/vite.config.ts frontend/vitest.config.ts frontend/src/test-setup.ts
git commit -m "chore(frontend): Vite dev proxy /api/* → :5000 + Vitest config"
```

## Task 4.3: `theme/tokens.ts` + `theme/theme.css` — FedEx brand tokens

Maps the locked semantic tokens from spec §6.3 to typed TS constants and CSS custom properties.

**Files:**
- Create: `frontend/src/theme/tokens.ts`
- Create: `frontend/src/theme/theme.css`

- [ ] **Step 1: Write `tokens.ts`**

Create `C:/Users/3626416/Projects/rocs-copilot/frontend/src/theme/tokens.ts`:

```ts
/**
 * Typed brand tokens. Mirror of theme.css custom properties.
 * Spec §6.3: semantic mapping of FedEx palette.
 */
export const colors = {
  primary: "#007AB7",         // Digital Blue — primary action
  accentPurple: "#4D148C",
  accentOrange: "#FF6200",
  textStrong: "#1A1A1A",      // Gray 90
  textDefault: "#333333",     // Gray 80
  textMuted: "#666666",       // Gray 70
  surface1: "#F5F5F5",        // Gray 30 (deeper background)
  surface2: "#FAFAFA",        // Gray 20
  surface3: "#FFFFFF",        // Gray 10 (top surface)
  error: "#C8102E",           // FedEx red accent — TBD precise hex from brand kit
} as const;

export const gradients = {
  /** Spec §6.3 signature gradient: purple → mid → orange. */
  signature:
    "linear-gradient(90deg,#4D148C 0%,#7D22C3 33%,#FF6200 100%)",
} as const;

export const typography = {
  body: '"Segoe UI", system-ui, -apple-system, BlinkMacSystemFont, sans-serif',
  mono: 'ui-monospace, "Cascadia Mono", "Source Code Pro", monospace',
} as const;
```

> The `error` red is the FedEx red used on cargo livery; if the brand kit specifies a different palette red for digital UI, update both `tokens.ts` and `theme.css` together (spec §11 brand-logo / color gap).

- [ ] **Step 2: Write `theme.css`**

Create `C:/Users/3626416/Projects/rocs-copilot/frontend/src/theme/theme.css`:

```css
/* CSS custom properties mirroring src/theme/tokens.ts. */
:root {
  --color-primary: #007ab7;
  --color-accent-purple: #4d148c;
  --color-accent-orange: #ff6200;

  --text-strong: #1a1a1a;
  --text-default: #333333;
  --text-muted: #666666;

  --surface-1: #f5f5f5;
  --surface-2: #fafafa;
  --surface-3: #ffffff;

  --color-error: #c8102e;

  --gradient-signature: linear-gradient(
    90deg,
    #4d148c 0%,
    #7d22c3 33%,
    #ff6200 100%
  );

  --font-body: "Segoe UI", system-ui, -apple-system, BlinkMacSystemFont,
    sans-serif;
  --font-mono: ui-monospace, "Cascadia Mono", "Source Code Pro", monospace;

  font-family: var(--font-body);
  color: var(--text-default);
  background: var(--surface-2);
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  min-height: 100vh;
}
```

- [ ] **Step 3: Wire `theme.css` into `main.tsx`**

Open `frontend/src/main.tsx` and replace the import for `./index.css` with `./theme/theme.css`:

```ts
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./theme/theme.css";
import App from "./App.tsx";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>
);
```

Delete the now-unused `frontend/src/index.css` and `frontend/src/App.css` if they exist:

```powershell
if (Test-Path frontend/src/index.css) { Remove-Item frontend/src/index.css }
if (Test-Path frontend/src/App.css) { Remove-Item frontend/src/App.css }
```

- [ ] **Step 4: Smoke build**

Run (PowerShell):
```powershell
Set-Location frontend
npm run build
Set-Location ..
```
Expected: build succeeds.

- [ ] **Step 5: Commit**

Run (Bash):
```bash
git add frontend/src/theme/ frontend/src/main.tsx
git rm --cached frontend/src/index.css frontend/src/App.css 2>/dev/null || true
git commit -m "feat(frontend): FedEx brand tokens (typed + CSS custom properties)"
```

## Task 4.4: `assets/brand/` — placeholder wordmark

Spec §11: marketing-photo logo is not a UI wordmark. Phase 4 ships a typographic placeholder.

**Files:**
- Create: `frontend/src/assets/brand/Wordmark.tsx`
- Create: `frontend/src/assets/brand/wordmark.module.css`

- [ ] **Step 1: Write the React component**

Create `C:/Users/3626416/Projects/rocs-copilot/frontend/src/assets/brand/Wordmark.tsx`:

```tsx
import styles from "./wordmark.module.css";

/**
 * Typographic placeholder wordmark for rocs-copilot.
 * Spec §11: replace with a clean SVG/PNG once supplied.
 */
export function Wordmark() {
  return (
    <span className={styles.wordmark}>
      <span className={styles.rocs}>ROCS</span>
      <span className={styles.copilot}>copilot</span>
    </span>
  );
}
```

- [ ] **Step 2: Write the CSS module**

Create `C:/Users/3626416/Projects/rocs-copilot/frontend/src/assets/brand/wordmark.module.css`:

```css
.wordmark {
  display: inline-flex;
  align-items: baseline;
  gap: 0.4rem;
  font-family: var(--font-body);
  letter-spacing: -0.01em;
  line-height: 1;
}

.rocs {
  font-weight: 800;
  font-size: 1.5rem;
  background: var(--gradient-signature);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.copilot {
  font-weight: 400;
  font-size: 1.1rem;
  color: var(--text-muted);
}
```

- [ ] **Step 3: Commit**

Run (Bash):
```bash
git add frontend/src/assets/
git commit -m "feat(frontend): typographic placeholder Wordmark (spec §11 brand logo gap)"
```

---

# Phase 5 — Frontend chat

Goal: SSE event types, streaming hook (TDD), source panel, message bubble with error variant + Retry, Chat integration, App shell.

## Task 5.1: `types/api.ts` — chat-stream event union

**Files:**
- Create: `frontend/src/types/api.ts`

- [ ] **Step 1: Write the types**

Create `C:/Users/3626416/Projects/rocs-copilot/frontend/src/types/api.ts`:

```ts
/** Mirrors backend SSE contract from spec §7.2 + §8.2. */

export interface ChatRequest {
  question: string;
  history: ChatTurn[];
}

export interface ChatTurn {
  role: "user" | "assistant";
  content: string;
}

export interface SourceChunk {
  id: string;
  filename: string;
  page: number;
  score: number;
  snippet: string;
}

export type ChatStreamEvent =
  | { kind: "token"; text: string }
  | { kind: "source"; chunks: SourceChunk[] }
  | { kind: "done" }
  | {
      kind: "error";
      code: "no_corpus" | "llm_unavailable" | "internal";
      message: string;
      retryable: boolean;
    };
```

- [ ] **Step 2: Commit**

Run (Bash):
```bash
git add frontend/src/types/api.ts
git commit -m "feat(frontend): SSE event union types mirroring backend contract"
```

## Task 5.2: `hooks/useChatStream.ts` — SSE parser (TDD)

**Files:**
- Create: `frontend/src/hooks/__tests__/useChatStream.test.ts`
- Create: `frontend/src/hooks/useChatStream.ts`

- [ ] **Step 1: Write failing tests**

Create `C:/Users/3626416/Projects/rocs-copilot/frontend/src/hooks/__tests__/useChatStream.test.ts`:

```ts
import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, act, waitFor } from "@testing-library/react";

import { useChatStream } from "../useChatStream";

function mockSSEResponse(eventLines: string[]): Response {
  const body = eventLines.join("\n") + "\n";
  const encoder = new TextEncoder();
  const stream = new ReadableStream<Uint8Array>({
    start(controller) {
      controller.enqueue(encoder.encode(body));
      controller.close();
    },
  });
  return new Response(stream, {
    status: 200,
    headers: { "Content-Type": "text/event-stream" },
  });
}

describe("useChatStream", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("parses token events into a streaming answer", async () => {
    vi.spyOn(global, "fetch").mockResolvedValue(
      mockSSEResponse([
        "event: token",
        'data: {"text": "Hello "}',
        "",
        "event: token",
        'data: {"text": "world."}',
        "",
        "event: done",
        "data: {}",
      ])
    );

    const { result } = renderHook(() => useChatStream());

    await act(async () => {
      await result.current.send("hi", []);
    });

    await waitFor(() => {
      expect(result.current.answer).toBe("Hello world.");
      expect(result.current.streaming).toBe(false);
    });
  });

  it("captures source chunks after done", async () => {
    vi.spyOn(global, "fetch").mockResolvedValue(
      mockSSEResponse([
        "event: token",
        'data: {"text": "Answer."}',
        "",
        "event: source",
        'data: {"chunks": [{"id":"m.pdf:p1","filename":"m.pdf","page":1,"score":0.8,"snippet":"..."}]}',
        "",
        "event: done",
        "data: {}",
      ])
    );

    const { result } = renderHook(() => useChatStream());

    await act(async () => {
      await result.current.send("q", []);
    });

    await waitFor(() => {
      expect(result.current.sources).toHaveLength(1);
      expect(result.current.sources[0].filename).toBe("m.pdf");
    });
  });

  it("captures error events with retryable flag", async () => {
    vi.spyOn(global, "fetch").mockResolvedValue(
      mockSSEResponse([
        "event: error",
        'data: {"code":"llm_unavailable","message":"down","retryable":true}',
        "",
        "event: done",
        "data: {}",
      ])
    );

    const { result } = renderHook(() => useChatStream());

    await act(async () => {
      await result.current.send("q", []);
    });

    await waitFor(() => {
      expect(result.current.error).toEqual({
        code: "llm_unavailable",
        message: "down",
        retryable: true,
      });
    });
  });

  it("supports abort via the returned controller", async () => {
    const neverResolves = new Promise<Response>(() => {});
    vi.spyOn(global, "fetch").mockReturnValue(neverResolves as Promise<Response>);

    const { result } = renderHook(() => useChatStream());

    act(() => {
      void result.current.send("q", []);
    });

    expect(result.current.streaming).toBe(true);

    act(() => {
      result.current.abort();
    });

    await waitFor(() => {
      expect(result.current.streaming).toBe(false);
    });
  });
});
```

- [ ] **Step 2: Verify failure**

Run (PowerShell):
```powershell
Set-Location frontend
npm run test
Set-Location ..
```
Expected: import error / not found.

- [ ] **Step 3: Write the hook**

Create `C:/Users/3626416/Projects/rocs-copilot/frontend/src/hooks/useChatStream.ts`:

```ts
import { useCallback, useRef, useState } from "react";
import type {
  ChatStreamEvent,
  ChatTurn,
  SourceChunk,
} from "../types/api";

interface UseChatStream {
  answer: string;
  sources: SourceChunk[];
  error: { code: string; message: string; retryable: boolean } | null;
  streaming: boolean;
  send: (question: string, history: ChatTurn[]) => Promise<void>;
  abort: () => void;
  reset: () => void;
}

/**
 * SSE consumer for POST /api/chat. Parses event / data line pairs into the
 * ChatStreamEvent union (spec §7.2). Supports AbortController cancellation.
 */
export function useChatStream(): UseChatStream {
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState<SourceChunk[]>([]);
  const [error, setError] = useState<UseChatStream["error"]>(null);
  const [streaming, setStreaming] = useState(false);
  const controllerRef = useRef<AbortController | null>(null);

  const reset = useCallback(() => {
    setAnswer("");
    setSources([]);
    setError(null);
  }, []);

  const abort = useCallback(() => {
    controllerRef.current?.abort();
    controllerRef.current = null;
    setStreaming(false);
  }, []);

  const send = useCallback(
    async (question: string, history: ChatTurn[]) => {
      reset();
      controllerRef.current?.abort();
      const controller = new AbortController();
      controllerRef.current = controller;
      setStreaming(true);

      try {
        const resp = await fetch("/api/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ question, history }),
          signal: controller.signal,
        });
        if (!resp.ok || !resp.body) {
          setError({
            code: "internal",
            message: `Request failed: ${resp.status}`,
            retryable: true,
          });
          return;
        }
        const reader = resp.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";
        while (true) {
          const { value, done } = await reader.read();
          if (done) break;
          buffer += decoder.decode(value, { stream: true });
          let idx;
          while ((idx = buffer.indexOf("\n\n")) !== -1) {
            const raw = buffer.slice(0, idx);
            buffer = buffer.slice(idx + 2);
            const evt = parseEvent(raw);
            if (evt) applyEvent(evt);
          }
          // Handle non-blank single-trailing newline events (server may use \n).
          let nl;
          while ((nl = buffer.indexOf("\n")) !== -1) {
            const line = buffer.slice(0, nl);
            if (line === "") {
              buffer = buffer.slice(nl + 1);
              continue;
            }
            break;
          }
        }
        // Drain residual buffer
        if (buffer.trim()) {
          const evt = parseEvent(buffer);
          if (evt) applyEvent(evt);
        }
      } catch (e) {
        if ((e as Error).name === "AbortError") {
          // user cancelled — silent
        } else {
          setError({
            code: "internal",
            message: (e as Error).message,
            retryable: true,
          });
        }
      } finally {
        setStreaming(false);
        controllerRef.current = null;
      }

      function applyEvent(evt: ChatStreamEvent) {
        switch (evt.kind) {
          case "token":
            setAnswer((prev) => prev + evt.text);
            break;
          case "source":
            setSources(evt.chunks);
            break;
          case "error":
            setError({
              code: evt.code,
              message: evt.message,
              retryable: evt.retryable,
            });
            break;
          case "done":
            // terminal marker; nothing to do beyond letting the loop exit
            break;
        }
      }
    },
    [reset]
  );

  return { answer, sources, error, streaming, send, abort, reset };
}

function parseEvent(raw: string): ChatStreamEvent | null {
  let eventName = "";
  let dataLine = "";
  for (const line of raw.split("\n")) {
    if (line.startsWith("event:")) eventName = line.slice("event:".length).trim();
    else if (line.startsWith("data:")) dataLine += line.slice("data:".length).trim();
  }
  if (!eventName || !dataLine) return null;
  try {
    const payload = JSON.parse(dataLine);
    switch (eventName) {
      case "token":
        return { kind: "token", text: payload.text };
      case "source":
        return { kind: "source", chunks: payload.chunks };
      case "done":
        return { kind: "done" };
      case "error":
        return {
          kind: "error",
          code: payload.code,
          message: payload.message,
          retryable: payload.retryable,
        };
      default:
        return null;
    }
  } catch {
    return null;
  }
}
```

- [ ] **Step 4: Run tests**

Run (PowerShell):
```powershell
Set-Location frontend
npm run test
Set-Location ..
```
Expected: 4 PASSED in `useChatStream.test.ts`.

- [ ] **Step 5: Commit**

Run (Bash):
```bash
git add frontend/src/hooks/
git commit -m "feat(frontend): useChatStream SSE parser hook with AbortController"
```

## Task 5.3: `components/SourcePanel.tsx` (TDD)

**Files:**
- Create: `frontend/src/components/__tests__/SourcePanel.test.tsx`
- Create: `frontend/src/components/SourcePanel.tsx`
- Create: `frontend/src/components/sourcePanel.module.css`

- [ ] **Step 1: Write failing tests**

Create `C:/Users/3626416/Projects/rocs-copilot/frontend/src/components/__tests__/SourcePanel.test.tsx`:

```tsx
import { describe, it, expect } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";

import { SourcePanel } from "../SourcePanel";
import type { SourceChunk } from "../../types/api";

const chunks: SourceChunk[] = [
  { id: "m.pdf:p1", filename: "m.pdf", page: 1, score: 0.82, snippet: "Routing details" },
  { id: "m.pdf:p3", filename: "m.pdf", page: 3, score: 0.71, snippet: "Error codes" },
];

describe("SourcePanel", () => {
  it("renders nothing when chunks is empty", () => {
    const { container } = render(<SourcePanel chunks={[]} />);
    expect(container.firstChild).toBeNull();
  });

  it("renders a summary count when collapsed", () => {
    render(<SourcePanel chunks={chunks} />);
    expect(screen.getByText(/2 sources/i)).toBeInTheDocument();
  });

  it("expands to show filenames, pages, and scores on click", () => {
    render(<SourcePanel chunks={chunks} />);
    fireEvent.click(screen.getByRole("button", { name: /sources/i }));
    expect(screen.getByText(/m\.pdf/i)).toBeInTheDocument();
    expect(screen.getByText(/p\.1/i)).toBeInTheDocument();
    expect(screen.getByText(/0\.82/)).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Verify failure**

Run (PowerShell):
```powershell
Set-Location frontend; npm run test; Set-Location ..
```
Expected: import not found.

- [ ] **Step 3: Write component**

Create `C:/Users/3626416/Projects/rocs-copilot/frontend/src/components/SourcePanel.tsx`:

```tsx
import { useState } from "react";
import type { SourceChunk } from "../types/api";
import styles from "./sourcePanel.module.css";

interface Props {
  chunks: SourceChunk[];
}

export function SourcePanel({ chunks }: Props) {
  const [open, setOpen] = useState(false);
  if (chunks.length === 0) return null;
  return (
    <div className={styles.panel}>
      <button
        type="button"
        className={styles.toggle}
        onClick={() => setOpen((v) => !v)}
      >
        {chunks.length} sources {open ? "▴" : "▾"}
      </button>
      {open && (
        <ul className={styles.list}>
          {chunks.map((c) => (
            <li key={c.id} className={styles.item}>
              <span className={styles.filename}>{c.filename}</span>
              <span className={styles.page}> · p.{c.page}</span>
              <span className={styles.score}> · {c.score.toFixed(2)}</span>
              <p className={styles.snippet}>{c.snippet}</p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
```

- [ ] **Step 4: Write CSS module**

Create `C:/Users/3626416/Projects/rocs-copilot/frontend/src/components/sourcePanel.module.css`:

```css
.panel {
  margin-top: 0.5rem;
  font-size: 0.875rem;
  color: var(--text-muted);
}

.toggle {
  background: transparent;
  border: 1px solid var(--surface-1);
  border-radius: 999px;
  padding: 0.2rem 0.6rem;
  color: var(--text-default);
  cursor: pointer;
  font: inherit;
}

.toggle:hover {
  background: var(--surface-1);
}

.list {
  list-style: none;
  padding: 0.5rem 0 0;
  margin: 0;
}

.item {
  padding: 0.4rem 0;
  border-top: 1px solid var(--surface-1);
}

.filename {
  font-weight: 600;
  color: var(--text-strong);
}

.page,
.score {
  color: var(--text-muted);
}

.snippet {
  margin: 0.2rem 0 0;
  color: var(--text-default);
}
```

- [ ] **Step 5: Run tests**

Run (PowerShell):
```powershell
Set-Location frontend; npm run test; Set-Location ..
```
Expected: 3 PASSED in `SourcePanel.test.tsx`.

- [ ] **Step 6: Commit**

Run (Bash):
```bash
git add frontend/src/components/SourcePanel.tsx frontend/src/components/sourcePanel.module.css frontend/src/components/__tests__/SourcePanel.test.tsx
git commit -m "feat(frontend): SourcePanel — collapsible citation list"
```

## Task 5.4: `components/MessageBubble.tsx` (TDD)

Renders markdown for normal bubbles; error variant shows red-tinted background and `[Retry]` button if `retryable`.

**Files:**
- Create: `frontend/src/components/__tests__/MessageBubble.test.tsx`
- Create: `frontend/src/components/MessageBubble.tsx`
- Create: `frontend/src/components/messageBubble.module.css`

- [ ] **Step 1: Write failing tests**

Create `C:/Users/3626416/Projects/rocs-copilot/frontend/src/components/__tests__/MessageBubble.test.tsx`:

```tsx
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";

import { MessageBubble } from "../MessageBubble";

describe("MessageBubble", () => {
  it("renders user variant", () => {
    render(<MessageBubble variant="user" content="What is SAMPLE-001?" />);
    expect(screen.getByText("What is SAMPLE-001?")).toBeInTheDocument();
  });

  it("renders markdown in assistant variant", () => {
    render(<MessageBubble variant="assistant" content="**Bold** and `code`." />);
    expect(screen.getByText("Bold").tagName).toBe("STRONG");
    expect(screen.getByText("code").tagName).toBe("CODE");
  });

  it("renders an error variant with retry button when retryable", () => {
    const onRetry = vi.fn();
    render(
      <MessageBubble
        variant="error"
        content="The assistant is temporarily unavailable."
        retryable
        onRetry={onRetry}
      />
    );
    const btn = screen.getByRole("button", { name: /retry/i });
    fireEvent.click(btn);
    expect(onRetry).toHaveBeenCalledTimes(1);
  });

  it("hides retry button when not retryable", () => {
    render(
      <MessageBubble
        variant="error"
        content="No documents indexed yet."
        retryable={false}
      />
    );
    expect(screen.queryByRole("button", { name: /retry/i })).toBeNull();
  });
});
```

- [ ] **Step 2: Verify failure**

Run: `Set-Location frontend; npm run test; Set-Location ..` — expect not-found.

- [ ] **Step 3: Write component**

Create `C:/Users/3626416/Projects/rocs-copilot/frontend/src/components/MessageBubble.tsx`:

```tsx
import ReactMarkdown from "react-markdown";
import styles from "./messageBubble.module.css";

type Variant = "user" | "assistant" | "error";

interface Props {
  variant: Variant;
  content: string;
  retryable?: boolean;
  onRetry?: () => void;
}

export function MessageBubble({ variant, content, retryable, onRetry }: Props) {
  return (
    <div className={`${styles.bubble} ${styles[variant]}`}>
      {variant === "user" ? (
        <p className={styles.text}>{content}</p>
      ) : (
        <div className={styles.text}>
          <ReactMarkdown>{content}</ReactMarkdown>
        </div>
      )}
      {variant === "error" && retryable && (
        <button type="button" className={styles.retry} onClick={onRetry}>
          Retry
        </button>
      )}
    </div>
  );
}
```

- [ ] **Step 4: Write CSS module**

Create `C:/Users/3626416/Projects/rocs-copilot/frontend/src/components/messageBubble.module.css`:

```css
.bubble {
  max-width: 80%;
  padding: 0.8rem 1rem;
  border-radius: 12px;
  margin-bottom: 0.75rem;
}

.bubble .text :first-child {
  margin-top: 0;
}
.bubble .text :last-child {
  margin-bottom: 0;
}

.user {
  align-self: flex-end;
  background: var(--color-primary);
  color: white;
}

.assistant {
  align-self: flex-start;
  background: var(--surface-3);
  color: var(--text-default);
  border: 1px solid var(--surface-1);
}

.error {
  align-self: flex-start;
  background: #fff2f2;
  color: var(--text-strong);
  border: 1px solid var(--color-error);
}

.retry {
  margin-top: 0.5rem;
  background: var(--color-error);
  color: white;
  border: none;
  border-radius: 6px;
  padding: 0.3rem 0.8rem;
  cursor: pointer;
  font: inherit;
}

.retry:hover {
  filter: brightness(1.1);
}
```

- [ ] **Step 5: Run tests**

Run (PowerShell):
```powershell
Set-Location frontend; npm run test; Set-Location ..
```
Expected: 4 PASSED in `MessageBubble.test.tsx`.

- [ ] **Step 6: Commit**

Run (Bash):
```bash
git add frontend/src/components/MessageBubble.tsx frontend/src/components/messageBubble.module.css frontend/src/components/__tests__/MessageBubble.test.tsx
git commit -m "feat(frontend): MessageBubble — user/assistant/error variants with Retry"
```

## Task 5.5: `components/Chat.tsx` + `App.tsx` integration (TDD)

Wires `useChatStream` into a chat surface with message list + input + SourcePanel + error bubble + Retry.

**Files:**
- Create: `frontend/src/components/__tests__/Chat.test.tsx`
- Create: `frontend/src/components/Chat.tsx`
- Create: `frontend/src/components/chat.module.css`
- Modify: `frontend/src/App.tsx`
- Create: `frontend/src/app.module.css`

- [ ] **Step 1: Write failing integration test**

Create `C:/Users/3626416/Projects/rocs-copilot/frontend/src/components/__tests__/Chat.test.tsx`:

```tsx
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor, act } from "@testing-library/react";

import { Chat } from "../Chat";
import * as hookModule from "../../hooks/useChatStream";

function mockHook(overrides: Partial<ReturnType<typeof hookModule.useChatStream>>) {
  const send = vi.fn();
  const abort = vi.fn();
  const reset = vi.fn();
  vi.spyOn(hookModule, "useChatStream").mockReturnValue({
    answer: "",
    sources: [],
    error: null,
    streaming: false,
    send,
    abort,
    reset,
    ...overrides,
  });
  return { send, abort, reset };
}

describe("Chat", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("submits a question and renders the user bubble", async () => {
    const { send } = mockHook({});
    render(<Chat />);
    const input = screen.getByPlaceholderText(/ask about ROCS/i);
    fireEvent.change(input, { target: { value: "What is SAMPLE-001?" } });
    fireEvent.click(screen.getByRole("button", { name: /send/i }));
    await waitFor(() => {
      expect(send).toHaveBeenCalledWith("What is SAMPLE-001?", []);
      expect(screen.getByText("What is SAMPLE-001?")).toBeInTheDocument();
    });
  });

  it("renders an error bubble with retry on llm_unavailable", async () => {
    const { send } = mockHook({
      error: { code: "llm_unavailable", message: "down", retryable: true },
      streaming: false,
    });
    render(<Chat />);
    // To trigger the error path we need the user to have asked something first;
    // simulate by submitting then re-rendering with error.
    fireEvent.change(screen.getByPlaceholderText(/ask about ROCS/i), {
      target: { value: "hi" },
    });
    fireEvent.click(screen.getByRole("button", { name: /send/i }));
    await waitFor(() => {
      expect(screen.getByText(/down/i)).toBeInTheDocument();
      expect(screen.getByRole("button", { name: /retry/i })).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole("button", { name: /retry/i }));
    expect(send).toHaveBeenCalledTimes(2);
  });
});
```

- [ ] **Step 2: Verify failure**

Run: `Set-Location frontend; npm run test; Set-Location ..` — expect not-found.

- [ ] **Step 3: Write `Chat.tsx`**

Create `C:/Users/3626416/Projects/rocs-copilot/frontend/src/components/Chat.tsx`:

```tsx
import { useCallback, useEffect, useState } from "react";
import { useChatStream } from "../hooks/useChatStream";
import type { ChatTurn } from "../types/api";
import { MessageBubble } from "./MessageBubble";
import { SourcePanel } from "./SourcePanel";
import styles from "./chat.module.css";

export function Chat() {
  const [draft, setDraft] = useState("");
  const [turns, setTurns] = useState<ChatTurn[]>([]);
  const [lastQuestion, setLastQuestion] = useState<string>("");
  const { answer, sources, error, streaming, send } = useChatStream();

  const submit = useCallback(
    (question: string) => {
      setTurns((prev) => [...prev, { role: "user", content: question }]);
      setLastQuestion(question);
      void send(question, turns);
    },
    [send, turns]
  );

  // When the stream finishes successfully, archive the answer to the turns list.
  useEffect(() => {
    if (!streaming && answer && !error) {
      setTurns((prev) => {
        // avoid double-archive: last turn must be user before we append assistant
        if (prev.length === 0 || prev[prev.length - 1].role !== "user") return prev;
        return [...prev, { role: "assistant", content: answer }];
      });
    }
    // We only react to streaming completion.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [streaming]);

  const onSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!draft.trim() || streaming) return;
    const q = draft.trim();
    setDraft("");
    submit(q);
  };

  const onRetry = () => {
    if (lastQuestion) submit(lastQuestion);
  };

  return (
    <div className={styles.chat}>
      <div className={styles.messages}>
        {turns.map((t, i) => (
          <MessageBubble
            key={i}
            variant={t.role === "user" ? "user" : "assistant"}
            content={t.content}
          />
        ))}
        {streaming && answer && (
          <MessageBubble variant="assistant" content={answer + "▌"} />
        )}
        {!streaming && answer && error === null && (
          <SourcePanel chunks={sources} />
        )}
        {error && (
          <MessageBubble
            variant="error"
            content={error.message}
            retryable={error.retryable}
            onRetry={onRetry}
          />
        )}
      </div>
      <form className={styles.form} onSubmit={onSubmit}>
        <textarea
          className={styles.input}
          placeholder="Ask about ROCS error codes, modules, or procedures…"
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              onSubmit(e as unknown as React.FormEvent);
            }
          }}
          disabled={streaming}
        />
        <button
          type="submit"
          className={styles.send}
          disabled={streaming || !draft.trim()}
        >
          Send
        </button>
      </form>
    </div>
  );
}
```

- [ ] **Step 4: Write `chat.module.css`**

Create `C:/Users/3626416/Projects/rocs-copilot/frontend/src/components/chat.module.css`:

```css
.chat {
  display: flex;
  flex-direction: column;
  height: 100%;
  max-width: 800px;
  margin: 0 auto;
  padding: 1rem;
}

.messages {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  padding-bottom: 1rem;
}

.form {
  display: flex;
  gap: 0.5rem;
  border-top: 1px solid var(--surface-1);
  padding-top: 0.75rem;
}

.input {
  flex: 1;
  min-height: 60px;
  resize: vertical;
  border: 1px solid var(--surface-1);
  border-radius: 8px;
  padding: 0.6rem;
  font: inherit;
}

.input:focus {
  outline: 2px solid var(--color-primary);
  outline-offset: 1px;
}

.send {
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 0 1.2rem;
  cursor: pointer;
  font: inherit;
  font-weight: 600;
}

.send:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
```

- [ ] **Step 5: Rewrite `App.tsx` as the layout shell**

Overwrite `C:/Users/3626416/Projects/rocs-copilot/frontend/src/App.tsx`:

```tsx
import { Chat } from "./components/Chat";
import { Wordmark } from "./assets/brand/Wordmark";
import styles from "./app.module.css";

export default function App() {
  return (
    <div className={styles.shell}>
      <header className={styles.header}>
        <Wordmark />
      </header>
      <main className={styles.main}>
        <Chat />
      </main>
    </div>
  );
}
```

Create `C:/Users/3626416/Projects/rocs-copilot/frontend/src/app.module.css`:

```css
.shell {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: var(--surface-2);
}

.header {
  background: var(--gradient-signature);
  padding: 0.75rem 1.5rem;
  display: flex;
  align-items: center;
}

.main {
  flex: 1;
  display: flex;
}
```

- [ ] **Step 6: Run all frontend tests**

Run (PowerShell):
```powershell
Set-Location frontend
npm run test
Set-Location ..
```
Expected: all suites PASS (`useChatStream`, `SourcePanel`, `MessageBubble`, `Chat`).

- [ ] **Step 7: Smoke build**

Run (PowerShell):
```powershell
Set-Location frontend
npm run build
Set-Location ..
```
Expected: build succeeds with no TS errors.

- [ ] **Step 8: Commit**

Run (Bash):
```bash
git add frontend/src/components/Chat.tsx frontend/src/components/chat.module.css frontend/src/components/__tests__/Chat.test.tsx frontend/src/App.tsx frontend/src/app.module.css
git commit -m "feat(frontend): Chat integration with streaming, sources, error+retry"
```

---

# Phase 6 — CI

Goal: run pytest + vitest on every push.

## Task 6.1: `.github/workflows/test.yml`

**Files:**
- Create: `.github/workflows/test.yml`

- [ ] **Step 1: Write the workflow**

Create `C:/Users/3626416/Projects/rocs-copilot/.github/workflows/test.yml`:

```yaml
name: test

on:
  push:
  pull_request:

jobs:
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: pip
      - name: Install
        run: |
          python -m pip install --upgrade pip
          python -m pip install -e ".[dev]"
      - name: Pytest
        run: pytest -v

  frontend:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: frontend
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: npm
          cache-dependency-path: frontend/package-lock.json
      - name: Install
        run: npm ci
      - name: Vitest
        run: npm run test
      - name: Build
        run: npm run build
```

- [ ] **Step 2: Commit**

Run (Bash):
```bash
git add .github/workflows/test.yml
git commit -m "ci: pytest + vitest + frontend build on push"
```

## Task 6.2: Push to remote, verify CI green

> Skip this task if a remote isn't set up yet. If skipped, document in commit log that CI is locally configured but not yet exercised.

- [ ] **Step 1: Configure remote (one-time, if not set)**

Run (Bash):
```bash
git remote -v
```
If empty, add your remote (replace URL):
```bash
git remote add origin git@github.com:<owner>/<repo>.git
```

- [ ] **Step 2: Push**

Run (Bash):
```bash
git push -u origin main
```

- [ ] **Step 3: Verify CI green**

Run (Bash):
```bash
gh run watch
```
Expected: both `backend` and `frontend` jobs pass.

If a check fails, fix it inline and push again — DO NOT mark this task complete with red CI.

---

# Phase 7 — End-to-end smoke (Definition of Done walkthrough)

Walk through spec §12 with real keys + real corpus.

## Task 7.1: Ingest the fixture corpus

- [ ] **Step 1: Copy fixtures into the live corpus dir for an end-to-end run**

Run (PowerShell):
```powershell
Copy-Item tests/fixtures/corpus/*.* data/corpus/
```

- [ ] **Step 2: Set up env vars for a real provider**

Create `C:/Users/3626416/Projects/rocs-copilot/.env`:
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=<paste a real key>
```

- [ ] **Step 3: Run ingest**

Run (PowerShell):
```powershell
.venv/Scripts/python.exe scripts/ingest.py
```
Expected: log lines `indexed sample-error-catalog.docx`, `indexed sample-rocs-module.pdf`, and final `Indexed: 2 / Skipped: 0`.

Verify Chroma:
```powershell
Get-ChildItem data/chroma -Recurse | Measure-Object | Select-Object -ExpandProperty Count
```
Expected: non-zero (Chroma writes SQLite files).

## Task 7.2: Manual DoD walkthrough

- [ ] **Step 1: Start backend (terminal A)**

Run (PowerShell, in a dedicated window):
```powershell
.venv/Scripts/python.exe -m rocs_copilot_backend.app
```

- [ ] **Step 2: Start frontend (terminal B)**

Run (PowerShell, in a separate window):
```powershell
Set-Location frontend
npm run dev
```

- [ ] **Step 3: Walk through spec §12 DoD steps 6–11**

Open `http://localhost:5173` in a browser. For each step, manually verify and tick:
- [ ] Branded chat shell renders with FedEx gradient header and typographic wordmark.
- [ ] Asking "What is error SAMPLE-001?" streams tokens, then a source panel appears with `sample-rocs-module.pdf` p.1, then input re-enables.
- [ ] Follow-up "and what about SAMPLE-002?" gets answered with a rephrased standalone query under the hood.
- [ ] Asking something OFF-topic (e.g. "What's the weather?") returns the canned helpful answer with NO source panel.
- [ ] While streaming, sending a NEW question aborts the in-flight one (no double answer in DOM, backend log shows `client disconnected`).
- [ ] Set `OPENAI_API_KEY=garbage` and restart backend → ask anything → red error bubble with [Retry]; click Retry resends.

- [ ] **Step 4: Tag v0.1.0**

Run (Bash):
```bash
git tag -a v0.1.0 -m "rocs-copilot MVP: DoD walkthrough green"
git push origin v0.1.0
```

---

## Done

All §12 DoD criteria met. Hand back to the user.

Optional follow-ups (NOT part of this plan; spec §11 risks):
- Pin a real FedEx red for `--color-error` from the brand kit.
- Replace the typographic Wordmark with a clean SVG/PNG when supplied.
- Add a startup hint in the UI when Chroma is empty ("Run scripts/ingest.py first").
- Retune `RETRIEVAL_MIN_SCORE` after the first 10–20 real planner questions.
