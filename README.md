# ROCS Copilot

A single-user, laptop-hosted AI chatbot for **FedEx ROCS** (Routing and Optimization for Courier Services) planners. It answers questions and troubleshoots errors from your ROCS documentation using Retrieval-Augmented Generation (RAG) — no internet search, no hallucinated facts, only answers grounded in the documents you feed it.

---

## How it works

```
Your PDFs/DOCX
      │
      ▼  scripts/ingest.py
 ┌─────────────┐
 │  Chroma     │  ← local vector store on disk
 │  vector DB  │
 └──────┬──────┘
        │ similarity search
        ▼
 ┌──────────────────────────┐       ┌─────────────┐
 │  Flask backend (:5000)   │──────▶│  OpenAI /   │
 │  LangChain RAG chain     │       │  Groq LLM   │
 └──────────────────────────┘       └─────────────┘
        │ Server-Sent Events
        ▼
 ┌──────────────────────────┐
 │  React frontend (:5173)  │
 │  Vite dev server         │
 └──────────────────────────┘
```

Documents are ingested once via a CLI script. The backend serves streaming answers over SSE. The frontend streams tokens as they arrive and shows which document pages were used.

---

## Prerequisites

| Tool | Minimum version | Notes |
|------|----------------|-------|
| Python | 3.11+ | 3.12 recommended |
| Node.js | 18+ | 20 LTS recommended |
| npm | 9+ | Comes with Node |
| An OpenAI API key | — | Always required — used for embeddings and (optionally) chat |
| A Groq API key | — | Optional — only needed if `LLM_PROVIDER=groq` |

---

## Repository locations

The source code lives in two private GitHub repositories (mirrors of each other):

| Account | Repository URL | Access method |
|---------|---------------|---------------|
| Personal (`aasadi1978`) | `https://github.com/aasadi1978/rocs-copilot` | SSH via `github-aasadi` alias |
| FedEx (`alireza-asadi_fedex`) | `https://github.com/alireza-asadi_fedex/rocs-copilot` | HTTPS |

Both remotes are configured in this repo:

```bash
git remote -v
# origin_private  git@github-aasadi:aasadi1978/rocs-copilot.git
# origin_fdx      https://github.com/alireza-asadi_fedex/rocs-copilot.git
```

To push changes to both at once:

```bash
git push origin_private main
git push origin_fdx main
```

---

## Setup

### 1. Clone the repo

```bash
# Via personal SSH alias
git clone git@github-aasadi:aasadi1978/rocs-copilot.git

# Or via FedEx HTTPS
git clone https://github.com/alireza-asadi_fedex/rocs-copilot.git
```

### 2. Create the Python virtual environment

```powershell
# Windows (PowerShell)
py -3.12 -m venv .venv
```

```bash
# macOS / Linux
python3.12 -m venv .venv
```

### 3. Install Python dependencies

```powershell
# Windows
.venv/Scripts/python.exe -m pip install --upgrade pip
.venv/Scripts/python.exe -m pip install -e ".[dev]"
```

```bash
# macOS / Linux
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e ".[dev]"
```

This installs Flask, LangChain, Chroma, and all other backend dependencies listed in `pyproject.toml`.

### 4. Install frontend dependencies

```powershell
Set-Location frontend
npm install
Set-Location ..
```

### 5. Create your `.env` file

Copy the example and fill in your API key(s):

```powershell
Copy-Item .env.example .env
```

Then open `.env` and set your values:

```env
# Required — selects the chat LLM (openai or groq)
LLM_PROVIDER=openai

# Required for embeddings AND if LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...

# Required only if LLM_PROVIDER=groq
GROQ_API_KEY=gsk_...

# Optional — these defaults work for most setups
OPENAI_CHAT_MODEL=gpt-4o-mini
GROQ_CHAT_MODEL=llama-3.3-70b-versatile
EMBEDDING_MODEL=text-embedding-3-small
CHROMA_DIR=data/chroma
CORPUS_DIR=data/corpus
RETRIEVAL_MIN_SCORE=0.3
RETRIEVAL_TOP_K=4
HISTORY_TURN_CAP=8
```

> **Note:** `.env` is gitignored and never committed.

---

## Ingesting documents

The chatbot can only answer questions about documents that have been ingested into its local vector database. This step must be done before you run the app, and repeated any time you add or update documents.

### Step 1 — Add your documents

Drop your ROCS PDF and Word files into the `data/corpus/` folder:

```
data/
  corpus/
    ROCS-User-Guide-v4.pdf
    ROCS-Error-Catalog-2024.pdf
    Routing-Module-Reference.docx
    ...
```

Supported formats: **PDF** (`.pdf`) and **Word** (`.docx`). Other file types are skipped with a warning.

### Step 2 — Run the ingestion script

```powershell
# Windows
.venv/Scripts/python.exe scripts/ingest.py
```

```bash
# macOS / Linux
.venv/bin/python scripts/ingest.py
```

**What it does:**

1. Walks every `.pdf` and `.docx` in `data/corpus/`
2. Extracts text page by page
3. Splits text into 1,000-character chunks (100-character overlap)
4. Sends chunks to OpenAI's embedding API (`text-embedding-3-small`)
5. Stores the resulting vectors in a local Chroma database at `data/chroma/`

**Expected output:**

```
INFO indexed ROCS-User-Guide-v4.pdf
INFO indexed ROCS-Error-Catalog-2024.pdf
INFO indexed Routing-Module-Reference.docx
INFO Indexed: 3 / Skipped: 0
```

**Re-ingesting is safe.** Each chunk is identified by a hash of its text content, so running the script twice on the same files adds no duplicate vectors.

**If a file fails** (password-protected PDF, image-only scan, corrupt file), it is logged and skipped — other files continue processing. Only a missing API key or a disk error will abort the whole run.

### Step 3 — Re-ingest when documents change

Any time you add, remove, or update documents in `data/corpus/`, re-run the script. The Chroma database is persistent and accumulates new vectors automatically; removed files are not pruned (full re-index: delete `data/chroma/` and re-run).

---

## Running the application

You need two terminals running simultaneously.

### Terminal A — Flask backend

```powershell
# Windows
.venv/Scripts/python.exe -m rocs_copilot_backend.app
```

```bash
# macOS / Linux
.venv/bin/python -m rocs_copilot_backend.app
```

The backend starts on `http://127.0.0.1:5000`. You should see:

```
INFO  * Running on http://127.0.0.1:5000
```

### Terminal B — Vite frontend

```powershell
Set-Location frontend
npm run dev
```

Open **`http://localhost:5173`** in your browser. The Vite dev server automatically proxies all `/api/*` requests to the Flask backend on port 5000.

---

## Configuration reference

All settings are read from the `.env` file at startup. The backend will refuse to start if required settings are missing.

| Variable | Required | Default | Description |
|---|---|---|---|
| `LLM_PROVIDER` | ✅ | — | `openai` or `groq` — selects the chat model |
| `OPENAI_API_KEY` | ✅ | — | Required for embeddings and if `LLM_PROVIDER=openai` |
| `GROQ_API_KEY` | ✅ if Groq | — | Required only if `LLM_PROVIDER=groq` |
| `OPENAI_CHAT_MODEL` | No | `gpt-4o-mini` | OpenAI model name for chat |
| `GROQ_CHAT_MODEL` | No | `llama-3.3-70b-versatile` | Groq model name for chat |
| `EMBEDDING_MODEL` | No | `text-embedding-3-small` | OpenAI model used for embeddings |
| `CHROMA_DIR` | No | `data/chroma` | Where the vector database is stored on disk |
| `CORPUS_DIR` | No | `data/corpus` | Where the ingestion script looks for documents |
| `RETRIEVAL_MIN_SCORE` | No | `0.3` | Minimum similarity score to use a retrieved chunk. Lower = more permissive; higher = stricter. Tune this after seeing real planner questions. |
| `RETRIEVAL_TOP_K` | No | `4` | Number of document chunks retrieved per question |
| `HISTORY_TURN_CAP` | No | `8` | Maximum prior conversation turns sent to the LLM |

### Switching between OpenAI and Groq

Update `.env` and restart the backend:

```env
# Use Groq instead of OpenAI for chat (embeddings always use OpenAI)
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_...
OPENAI_API_KEY=sk-...   # still required for embeddings
```

---

## Project structure

```
rocs-copilot/
│
├── src/rocs_copilot_backend/   # Flask + LangChain backend
│   ├── app.py                  # Flask app factory (entry point)
│   ├── config.py               # Pydantic settings (env-driven)
│   ├── chains/
│   │   └── rag_chain.py        # History-aware RAG chain (LangChain LCEL)
│   ├── providers/
│   │   └── llm.py              # LLM + embeddings factory (OpenAI / Groq)
│   ├── ingest/
│   │   ├── chunker.py          # Text splitter (1000 chars / 100 overlap)
│   │   ├── loader.py           # PDF + DOCX loaders
│   │   └── store.py            # Chroma wrapper (idempotent upserts)
│   └── routes/
│       ├── chat.py             # POST /api/chat  — SSE streaming endpoint
│       └── health.py           # GET  /api/health — smoke check
│
├── scripts/
│   └── ingest.py               # Document ingestion CLI
│
├── frontend/                   # Vite + React + TypeScript UI
│   └── src/
│       ├── App.tsx             # App shell (sidebar + top bar layout)
│       ├── components/
│       │   ├── Chat.tsx        # Chat surface (messages + input)
│       │   ├── MessageBubble.tsx
│       │   └── SourcePanel.tsx # Collapsible citations
│       ├── hooks/
│       │   └── useChatStream.ts  # SSE parser hook
│       ├── types/
│       │   └── api.ts          # Shared TypeScript contracts
│       └── theme/
│           ├── tokens.ts       # Typed FedEx colour constants
│           └── theme.css       # CSS custom properties (:root)
│
├── data/
│   ├── corpus/                 # ← drop your PDFs/DOCX here (gitignored)
│   └── chroma/                 # ← generated vector DB (gitignored)
│
├── tests/                      # pytest test suite (42 tests)
├── .env.example                # Template — copy to .env and fill in keys
├── pyproject.toml              # Python package manifest + dependencies
└── .github/workflows/test.yml  # CI: pytest + vitest + build on every push
```

---

## Running tests

```powershell
# Backend (Python)
.venv/Scripts/pytest.exe -v

# Frontend (TypeScript)
Set-Location frontend
npm run test
```

---

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/chat` | Stream a chat response as Server-Sent Events |
| `GET` | `/api/health` | Returns `{"status": "ok"}` — smoke check |

### Chat request body

```json
{
  "question": "What does error SAMPLE-001 mean?",
  "history": [
    { "role": "user",      "content": "Tell me about routing errors." },
    { "role": "assistant", "content": "There are several..." }
  ]
}
```

### SSE event stream (response)

Events arrive in this exact order:

```
event: token
data: {"text": "Based "}

event: token
data: {"text": "on the manual..."}

event: source
data: {"chunks": [{"filename": "ROCS-Guide.pdf", "page": 12, "score": 0.78, "snippet": "..."}]}

event: done
data: {}
```

---

## Troubleshooting

**"No documents found in data/corpus/"**  
→ Drop at least one `.pdf` or `.docx` into `data/corpus/` and re-run `scripts/ingest.py`.

**"No documents indexed yet. Run scripts/ingest.py first."** (in the chat UI)  
→ The vector database is empty. Run the ingestion script (see above).

**"I don't have documentation covering that."** (in the chat UI)  
→ The question didn't match any document chunk above the similarity threshold. Try rephrasing using terms from your ROCS manuals. If this happens too often for valid questions, lower `RETRIEVAL_MIN_SCORE` in `.env` (e.g. `0.2`).

**Red error bubble in the UI**  
→ The LLM provider is unavailable or the API key is wrong. Check your `.env`, then click **Retry**.

**Backend won't start — ValidationError**  
→ A required environment variable is missing. Check that `.env` exists in the project root and contains `LLM_PROVIDER` and `OPENAI_API_KEY`.

**PDF pages are blank / empty after ingestion**  
→ The PDF may be image-based (scanned). `pypdf` extracts text only — scanned PDFs require an OCR pre-processing step outside this tool.
