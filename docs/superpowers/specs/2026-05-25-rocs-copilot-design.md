# rocs-copilot — Design Spec

**Date:** 2026-05-25
**Status:** APPROVED (design lock); ready for implementation-plan authoring
**Author / approver:** Project owner (FedEx; MVP proxy for ROCS planners)
**Source brainstorming sessions:** UUIDs `fcebe39f-4a69-4dc0-be36-38a98c7b0ae0` (initial) + `849a452d-6b6a-421e-9314-b7e73953167a` (this turn — Sections 3–5 closed and locked)

---

## 1. Executive summary

rocs-copilot is a single-user, laptop-hosted chatbot copilot for **ROCS** — FedEx's internal routing/optimization web app for ground-operations planners. It provides:

- **Q&A over ROCS documentation** (5–20 PDF/Word manuals supplied by the user).
- **Error and discrepancy troubleshooting guidance** sourced from the same corpus.

The system is a classic Retrieval-Augmented Generation (RAG) pipeline: a Flask + LangChain backend retrieves relevant document chunks from a local Chroma vector store, then streams an LLM-generated answer back to a Vite/React/TypeScript frontend over Server-Sent Events. Answers are cited; the user can see which document chunks informed each response.

This spec is the **single source of truth** for the design. The implementation plan (next artifact) will translate it into an ordered, dependency-aware build sequence.

---

## 2. Goals and non-goals

### 2.1 Goals (MVP)

- Single user, single laptop runtime. No multi-tenancy, no cloud deploy in MVP.
- Ingest 5–20 PDF/DOCX manuals into a persistent local Chroma vector store via an out-of-band CLI.
- Serve a streaming chat UI over Flask SSE: planner asks a question, gets a token-streamed answer with citations.
- Provider-agnostic LLM access: dev uses Groq + OpenAI via a thin abstraction; prod target is FedEx GCP (provider TBD, abstraction is mandatory so the swap is one config change).
- FedEx brand styling (Digital Blue primary, purple→orange gradient signature, gray surface system).
- Solid test coverage of risky paths (chains, SSE parsing, error paths) without coverage-gate ceremony.

### 2.2 Non-goals (deliberate, out of MVP scope)

- No authentication, no user accounts.
- No database; no chat history persistence (refresh = blank slate).
- No multi-user concurrency or session isolation.
- No production deployment (the binary will run; the deployment story is deferred).
- No real-time ROCS data integration. Source of truth is the doc corpus, not live ROCS state.
- No agent / tool use. Pure RAG; the LLM doesn't call functions or browse.
- No rate limiting or throttling on `/api/chat` (single-user laptop).
- No conversation persistence, autosave, or recovery flows.
- No cross-provider automatic failover (if Groq is down, the user sees the error; provider swap is a config + restart, not runtime).
- No server-side retry on LLM errors. The UI surfaces the error and offers a manual Retry button.
- No Playwright / browser E2E tests; no load tests; no accessibility tests; no visual regression tests.

---

## 3. Audience and runtime context

| Aspect | Value |
|---|---|
| Primary user | FedEx ground-operations **planners** (non-technical). |
| MVP user (this build) | Project owner, acting as planner proxy. |
| Runtime host | Single user's laptop (Windows). |
| Concurrency | One user, one chat session at a time. |
| Persistence | Chroma vector store on local disk; no other state. |
| Network requirements | Outbound HTTPS to LLM provider (Groq or OpenAI) and embeddings provider (OpenAI). No inbound. |

---

## 4. Constraints

| Constraint | Implication |
|---|---|
| FedEx GCP target has no programmatic LLM today (only Gemini chat UI) | Provider abstraction (`providers/llm.py`) is **load-bearing**, not optional. Prod LLM is TBD. |
| Windows dev environment (per global `~/.claude/CLAUDE.md`) | Forward-slash paths only; `.exe` invocations via PowerShell; project venv at `.venv/Scripts/python.exe` (preauthorized in `.claude/settings.local.json`). |
| Wide sibling-project denylist in `.claude/settings.local.json` | All file writes must stay inside `C:/Users/3626416/Projects/rocs-copilot/`. |
| No git repo yet | Defer `git init` until first source code lands. CI is set up day-1 once `git init` happens. |
| Brand kit included but logo is a marketing photo, not a wordmark | Use a typographic placeholder in `frontend/src/assets/brand/` until a clean SVG/PNG is supplied. |
| Single LLM provider available per dev environment | No automatic cross-provider failover; provider swap is via env var + restart. |

---

## 5. Architecture (Section 1, locked)

Two surfaces, separated:

1. **Ingestion CLI** (`scripts/ingest.py`) — out-of-band, dev-time. Walks `data/corpus/`, parses PDFs/DOCX, chunks, embeds, upserts into Chroma with content-hash idempotency. NOT part of the Flask process.
2. **Flask serving** — long-running web process exposing two routes: `POST /api/chat` (SSE streaming) and `GET /api/health` (smoke). Reads from Chroma; never writes. Streams LLM responses to the React UI.

Orchestration uses **LangChain LCEL** (loaders, splitters, retrievers, chains). Vector store is **Chroma** (embedded, persistent SQLite under `data/chroma/`). LLM providers are accessed via a thin factory (`providers/llm.py`) so dev (Groq / OpenAI) and prod (TBD GCP) are swap-by-env.

Frontend is **Vite + React + TypeScript** with **CSS Modules** + typed theme tokens (`theme/tokens.ts`) and CSS custom properties (`theme/theme.css`). No Tailwind, no chat-UI library, no Vercel AI SDK. SSE consumed via a small (~80 LOC) `useChatStream` hook built on `fetch` + `ReadableStream`.

```
                    ┌──────────────────────────┐
                    │ scripts/ingest.py (CLI)  │
                    │  PDF/DOCX → chunk →      │
                    │  embed → Chroma upsert   │
                    └────────────┬─────────────┘
                                 │ (writes)
                                 ▼
                         ┌───────────────┐
                         │  Chroma       │  data/chroma/  (persistent SQLite)
                         │  vector store │
                         └───────┬───────┘
                                 │ (reads)
┌────────────┐   HTTP/SSE   ┌────┴────────────────────────┐
│ React UI   │ ◀───────────▶│ Flask /api/chat (SSE)       │
│  Vite + TS │              │  LCEL: history_aware_       │
│  CSS Modules│              │  retriever | prompt | LLM   │
└────────────┘              └─────────────────────────────┘
                                          │
                                          ▼
                                   ┌────────────┐
                                   │ LLM        │  Groq or OpenAI (dev)
                                   │ provider   │  GCP-TBD (prod)
                                   └────────────┘
```

---

## 6. Components (Section 2, locked)

### 6.1 Backend (Python — planned tree; nothing on disk yet)

```
src/rocs_copilot_backend/
  app.py                    # Flask app factory; CORS for Vite dev (5173); wires routes
  config.py                 # pydantic settings (env-driven); validates LLM_PROVIDER, API keys,
                            # RETRIEVAL_MIN_SCORE, CHROMA_DIR, CORPUS_DIR; fails app startup
                            # on missing required vars
  routes/
    chat.py                 # POST /api/chat — SSE streaming response generator;
                            # ordering: tokens first, then `source` event before `done`
    health.py               # GET /api/health — returns {"status": "ok"} (smoke)
  chains/
    rag_chain.py            # LCEL: history_aware_retriever | prompt | chat_model | parser
                            # History rewrite runs BEFORE Chroma retrieval
  providers/
    llm.py                  # get_chat_model() and get_embeddings() factories;
                            # branches on LLM_PROVIDER env var (groq | openai)
  ingest/
    loader.py               # PyPDFLoader + Docx2txtLoader, attaches metadata
                            # (filename, page, content hash)
    chunker.py              # RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    store.py                # Chroma upsert with content-hash idempotency; tenacity backoff
                            # on embeddings API (3 attempts: 1s/4s/16s)
scripts/
  ingest.py                 # CLI entry point: walks data/corpus/, calls ingest/* in order,
                            # prints "Indexed: N / Skipped: M" summary, exits non-zero on
                            # missing API keys or Chroma write errors; per-file parse failure
                            # logged + skipped + continues
data/
  corpus/                   # user-supplied PDFs/DOCX (gitignored)
  chroma/                   # Chroma persistent SQLite dir (gitignored)
tests/
  fixtures/corpus/          # tiny synthetic PDFs/DOCX committed for real loader exercise
  test_chunker.py
  test_store.py
  test_provider_factory.py
  test_rag_chain.py
  test_routes_chat.py       # Flask test client + mocked LLM
  test_routes_health.py
```

### 6.2 Frontend (TypeScript — planned tree; nothing on disk yet)

```
frontend/
  src/
    App.tsx                  # Layout shell; renders Chat
    components/
      Chat.tsx               # message list + textarea input; owns AbortController
                             # for cancelling in-flight streams when user submits new
                             # question
      MessageBubble.tsx      # renders markdown + inline citations; variants for user /
                             # assistant / error; error variant includes [Retry] button
      SourcePanel.tsx        # collapsible sources list for the latest answer; shows
                             # filename + page + similarity score
    hooks/
      useChatStream.ts       # fetch + ReadableStream SSE parser (~80 LOC);
                             # emits parsed events (token, source, done, error);
                             # supports AbortController cancellation
    theme/
      tokens.ts              # typed TS constants for FedEx colors + gradient
      theme.css              # CSS custom properties on :root; consumed by CSS Modules
    assets/
      brand/                 # typographic placeholder wordmark + gradient class;
                             # swap for real asset when supplied
    types/
      api.ts                 # ChatRequest, ChatStreamEvent discriminated union contracts
    __tests__/               # Vitest
      useChatStream.test.ts
      MessageBubble.test.tsx
      SourcePanel.test.tsx
      Chat.test.tsx          # integration; mocks useChatStream
  vite.config.ts             # proxy /api/* to Flask :5000 in dev
  package.json
  tsconfig.json
```

### 6.3 Brand tokens (semantic mapping)

| Token (semantic) | FedEx value | Usage |
|---|---|---|
| `--color-primary` | `#007AB7` (Digital Blue) | Primary action buttons, links, focused input border |
| `--color-accent-purple` | `#4D148C` (brand purple) | Header gradient start, accent badges |
| `--color-accent-orange` | `#FF6200` (brand orange) | Header gradient end, accent badges |
| `--gradient-signature` | `linear-gradient(90deg,#4D148C 0%,#7D22C3 33%,#FF6200 100%)` | Header band, "signature" hero moments |
| `--text-strong` / `--text-default` / `--text-muted` | Gray 90 / 80 / 70 | Text hierarchy |
| `--surface-1` / `--surface-2` / `--surface-3` | Gray 30 / 20 / 10 | Layered backgrounds |
| `--color-error` | TBD red tint (FedEx accent palette) | Error bubble background tint, error icons |

---

## 7. Data flow (Section 3, locked)

### 7.1 Request contract

```http
POST /api/chat
Content-Type: application/json

{
  "question": "What does error code XYZ mean?",
  "history": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ]
}
```

`history` is sent by the frontend on every request (stateless backend). The history array is bounded by the frontend to recent turns (exact cap TBD in implementation plan; suggest last 8 turns).

### 7.2 Response: SSE event stream

The response is `text/event-stream`. Events emitted in **this strict order**:

1. **Zero or more `token` events** — the LLM-generated answer, delta-streamed token by token:
   ```
   event: token
   data: {"text": "Based "}

   event: token
   data: {"text": "on "}
   ```
2. **Exactly one `source` event** — the list of retrieved chunks that informed the answer, emitted **after all tokens** and before `done`:
   ```
   event: source
   data: {"chunks": [
     {"id": "...", "filename": "OPS-Manual-v4.pdf", "page": 12, "score": 0.78, "snippet": "..."},
     ...
   ]}
   ```
3. **Exactly one `done` event** — terminal marker; frontend uses this to re-enable input:
   ```
   event: done
   data: {}
   ```

**Rationale for tokens-then-source ordering:** the answer feels snappier when text starts streaming immediately; sources frame the finished conclusion at the end. Same final UI either way, but this ordering puts perceived latency on the answer (which the user is reading) and not on the citations (which they consult after).

### 7.3 History-aware retrieval

The chain uses LangChain's `create_history_aware_retriever` pattern: **before** Chroma retrieval, an LLM call rewrites the new question using prior turns so follow-ups like "and that one?" or "tell me more about error 42" get standalone-meaningful retrieval queries.

Pipeline:

```
question + history
   │
   ▼  (LLM call: rewrite question using history into a standalone query)
standalone_query
   │
   ▼  (Chroma similarity search with standalone_query)
chunks (top k)
   │
   ▼  (LLM call: answer using chunks + history + original question; streamed)
answer tokens  ─▶  source event  ─▶  done
```

This costs one extra LLM call per turn (~200–400ms latency, small token cost) but makes the chat actually conversational instead of forcing the user to repeat full context every turn.

---

## 8. Error handling (Section 4, locked)

Three surfaces, each with distinct audiences and tolerances.

### 8.1 Ingestion errors (CLI surface — out of band, audience: developer at terminal)

| Failure | Behavior |
|---|---|
| `data/corpus/` empty or missing | Exit early with explicit message: `"No documents found in data/corpus/. Drop PDFs/DOCX there and rerun."` Exit code non-zero. |
| Single PDF/DOCX fails to parse (corrupt, password-protected, image-only) | Log `WARN: skipped <filename>: <reason>`, continue with remaining files. Final summary line: `"Indexed: 14 / Skipped: 2"`. |
| Embeddings API failure (rate limit, network) | Retry with exponential backoff via `tenacity`: 3 attempts at 1s / 4s / 16s. If all fail, exit non-zero with provider error surfaced. |
| Chroma upsert failure | Fail loudly — exit non-zero with traceback. Indicates disk / permissions problem; no point continuing. |
| Missing required env var (e.g. `OPENAI_API_KEY`) | Fail at script startup before reading any files: `"Missing OPENAI_API_KEY in environment"`. |

### 8.2 Backend serving errors (Flask `/api/chat` — audience: React frontend via SSE)

Every failure becomes a structured SSE `error` event. No raw 500s, no stack traces into the chat box.

| Failure | SSE event payload |
|---|---|
| Vector store empty (no corpus ingested yet) | `event: error\ndata: {"code": "no_corpus", "message": "No documents indexed yet. Run scripts/ingest.py first.", "retryable": false}` then `done`. |
| Retrieval returns no chunks OR best chunk score < `RETRIEVAL_MIN_SCORE` (default `0.3`, env-tunable) | **Skip the LLM call entirely.** Stream the canned answer as normal tokens: `"I don't have documentation covering that. Try asking about specific error codes, ROCS modules, or operational procedures."` Emit `done` (no `source` event — there are no good sources to cite). |
| LLM provider error (rate limit, timeout, 5xx) | `event: error\ndata: {"code": "llm_unavailable", "message": "The assistant is temporarily unavailable. Please try again in a moment.", "retryable": true}` then `done`. **No server-side retry.** |
| Provider misconfig (missing API key, bad model name) | Fail at **app startup** (pydantic settings validation); Flask refuses to boot. Never happens per-request. |
| Client disconnects mid-stream | Generator catches `GeneratorExit`, closes LLM stream cleanly, logs `INFO: client disconnected`. No orphan LLM calls. |
| Unexpected exception (bug) | `event: error\ndata: {"code": "internal", "message": "Something went wrong on our end.", "retryable": true}`; log full stack trace server-side. |

### 8.3 Frontend errors (React — audience: planner)

| Failure | Behavior |
|---|---|
| Receives SSE `error` event mid-stream | Render error bubble (red-tinted background, FedEx accent border), preserve any partial answer already streamed above it, re-enable input, focus the textarea. If `retryable: true`, show **[Retry]** button on the bubble that resends the same question (no re-typing). |
| Network failure before stream opens | Inline notification: `"Couldn't reach the assistant. Check your connection and try again."` plus inline Retry button. |
| Stream connection drops mid-tokens | Same handling as `event: error` — show "Connection lost" bubble, preserve partial answer, re-enable input. |
| User submits new question while one is streaming | `AbortController.abort()` on the prior fetch; backend sees disconnect and cleans up; UI immediately starts rendering the new question's bubble. |
| Malformed SSE event (stray bytes) | Log to browser console; ignore that event; keep stream alive. Never crash. |

### 8.4 Explicit NOT-doing

- No server-side retry on LLM errors (retries inflate perceived latency on real outages).
- No conversation persistence — refresh discards everything (by design).
- No rate limiting / throttling on `/api/chat` (single-user laptop runtime).
- No automatic cross-provider failover (provider swap is config + restart).

---

## 9. Testing strategy (Section 5, locked)

### 9.1 Backend (pytest)

| Test | Approach |
|---|---|
| `test_chunker.py` | Pure unit. Synthetic text strings → verify expected chunk count, sizes, overlap with `RecursiveCharacterTextSplitter(1000, 100)`. |
| `test_store.py` | Real Chroma in `tmp_path` fixture; mocked embeddings function. Verify upsert + retrieval + content-hash idempotency (re-running ingest on same input file produces no duplicate vectors). |
| `test_provider_factory.py` | Mock `openai` and `groq` SDKs. Parametrize over `LLM_PROVIDER=groq` vs `openai`. Verify correct class + config returned; assert fail-loud on missing API key. |
| `test_rag_chain.py` | Mock the LLM. Assert chain composes as `history_aware_retriever | prompt | llm | parser`; assert history rewrite step actually invoked before retrieval; assert chain returns expected stream shape. |
| `test_routes_chat.py` | Flask test client + mocked LLM + real Chroma in `tmp_path`. Cover: happy path SSE ordering (tokens-then-source-then-done); `no_corpus` error; `llm_unavailable` error; retrieval-miss canned response (no LLM call, no `source` event); client disconnect cleanup. |
| `test_routes_health.py` | Smoke: returns 200 + `{"status": "ok"}`. |

### 9.2 Frontend (Vitest)

| Test | Approach |
|---|---|
| `useChatStream.test.ts` | Mock `Response` with a controllable `ReadableStream`. Verify the hook parses `source` / `token` / `done` / `error` events correctly, assembles the full answer from token deltas, and that `AbortController.abort()` cleanly terminates the stream. |
| `MessageBubble.test.tsx` | RTL assertions. Markdown renders; inline citations link to source IDs; error variant shows red-tinted bubble with [Retry] button; Retry click invokes the supplied handler. |
| `SourcePanel.test.tsx` | RTL. Collapsed and expanded states; renders source list with filename, page, score. |
| `Chat.test.tsx` | Integration with `useChatStream` mocked. Submit question → message appears → mock streams tokens → bubble fills in → source panel appears → input re-enables. Error path: error bubble shows, Retry resends. |

### 9.3 Mocking discipline

| Always mock | Never mock | Use real |
|---|---|---|
| LLM SDKs (`openai`, `groq`) — too slow, costs money, flaky | `RecursiveCharacterTextSplitter` — deterministic, fast | Chroma in `tmp_path` — local SQLite, fast, more honest than mocking |
| Embeddings API calls — same reasons | SSE parser logic — that IS the thing being tested | Flask test client — that's the integration boundary |

### 9.4 Coverage and CI

- **No hard coverage gate.** Tests target risky paths (chains, SSE parsing, error branches). No `--cov-fail-under` threshold; coverage incentives produce noise tests.
- **CI day-1.** Once `git init` happens, the first commit includes `.github/workflows/test.yml` that runs `pytest` (backend) and `vitest run` (frontend) on every push.

### 9.5 Test corpus

A small set of synthetic PDFs and DOCX files committed to `tests/fixtures/corpus/`. Each ~1 page, fake content about a fictional "sample ROCS module" (so it's clear they're fixtures, not real FedEx docs). Integration tests ingest these end-to-end through the real `PyPDFLoader` and `Docx2txtLoader` so a loader regression is caught.

### 9.6 Explicit NOT-testing

- No Playwright / browser E2E. Manual smoke is sufficient at MVP scale.
- No load tests. Single-user laptop runtime.
- No real LLM provider integration tests. Flaky + expensive; mocks are sufficient.
- No accessibility (a11y) tests. Acknowledged gap; defer until real planner usage.
- No visual regression tests. UI surface is small; eyeball is enough at this scale.

---

## 10. Configuration surface

Environment variables (consumed by `config.py` via pydantic settings; missing required ones fail at app startup):

| Variable | Required? | Default | Purpose |
|---|---|---|---|
| `LLM_PROVIDER` | yes | none | `groq` or `openai`; selects chat model factory branch |
| `OPENAI_API_KEY` | conditional | none | Required if `LLM_PROVIDER=openai` OR for embeddings (always uses OpenAI in MVP) |
| `GROQ_API_KEY` | conditional | none | Required if `LLM_PROVIDER=groq` |
| `OPENAI_CHAT_MODEL` | no | `gpt-4o-mini` (TBD in impl) | OpenAI chat model name |
| `GROQ_CHAT_MODEL` | no | TBD in impl plan | Groq chat model name |
| `EMBEDDING_MODEL` | no | `text-embedding-3-small` | OpenAI embedding model |
| `CHROMA_DIR` | no | `data/chroma` | Chroma persistent directory (relative to repo root) |
| `CORPUS_DIR` | no | `data/corpus` | Where the ingest CLI looks for source documents |
| `RETRIEVAL_MIN_SCORE` | no | `0.3` | Cosine-similarity floor; below this, retrieval is treated as a miss and the canned no-docs answer is streamed (see §8.2) |
| `RETRIEVAL_TOP_K` | no | `4` (TBD) | Number of chunks retrieved per query |
| `HISTORY_TURN_CAP` | no | `8` (TBD) | Max prior turns the frontend sends in `history` |

Final default values for the TBD entries are set in the implementation plan, not here.

---

## 11. Known risks and open questions (carry into post-MVP)

| Risk / open question | Mitigation / plan |
|---|---|
| **GCP prod LLM gap** — FedEx GCP has no programmatic LLM today (only Gemini chat UI). Prod path is unknown. | Provider abstraction (`providers/llm.py`) is load-bearing. When GCP provides a programmatic surface (Vertex AI, an internal gateway, etc.), add a new branch to the factory and flip `LLM_PROVIDER`. No other code change. |
| **Brand logo gap** — `brand/logo-with-fred-smith.png` is a marketing photo, not a usable UI wordmark. | Ship MVP with a typographic placeholder in `frontend/src/assets/brand/`. Swap when a clean SVG/PNG is supplied. |
| **Retrieval threshold needs tuning** — `RETRIEVAL_MIN_SCORE=0.3` is a guess. Real values depend on corpus quality and embedding-model behavior. | Tunable via env var; expect to retune after the first 10–20 real planner questions. Too high → bot says "I don't know" too often. Too low → bot hallucinates from loose context. |
| **First-use UX is bad** — if the user runs the app before ingesting, every question returns the `no_corpus` error. | The error message points to `scripts/ingest.py`. Consider a future "first-run wizard" or a startup-time check in the UI shell. Out of MVP scope. |
| **History rewrite may rewrite badly** on ambiguous follow-ups. | Document the pattern; observe in real use; tune the rewrite prompt in `chains/rag_chain.py` once we see real follow-up patterns. |
| **Single embeddings provider (OpenAI)** — if OpenAI is unavailable, ingestion can't run. | Acknowledged; out of MVP scope to add a second embeddings provider. The factory pattern (`get_embeddings()`) leaves the door open. |
| **No corpus management UX** — user must drop files into `data/corpus/` and re-run the CLI manually. | Out of MVP scope. Future: admin UI for upload + re-index. |

---

## 12. Definition of done (MVP)

The MVP is complete when, on a fresh laptop:

1. Developer creates `.venv`, installs deps (`pip install -e .` plus `frontend/` `npm install`).
2. Developer sets `LLM_PROVIDER`, `OPENAI_API_KEY`, and (if needed) `GROQ_API_KEY` in environment.
3. Developer drops 5–20 ROCS PDFs/DOCX into `data/corpus/`.
4. Developer runs `scripts/ingest.py`; sees per-file progress + final `Indexed: N / Skipped: M` summary; Chroma directory populated.
5. Developer starts Flask backend on `:5000` and Vite dev server on `:5173`.
6. Opens browser to `localhost:5173`; sees branded chat shell with FedEx gradient header and typographic wordmark.
7. Types a question grounded in the corpus; sees tokens stream in immediately, then a source panel appears with filenames + pages + scores, then input re-enables.
8. Asks a follow-up like "and what about that error?"; history-aware rewrite kicks in and the answer is grounded in relevant chunks.
9. Asks a question NOT in the corpus; gets the canned helpful answer with no source panel.
10. Disconnects mid-stream (closes tab / new question); no orphan LLM calls in backend logs.
11. Triggers an LLM error (set `OPENAI_API_KEY` to garbage and restart); sees red error bubble with [Retry] button; click resends the same question.
12. `pytest` passes; `vitest run` passes; CI green on push.

---

## 13. References

- Source brainstorming snapshot: `C:/Users/3626416/Projects/rocs-copilot/STATUS.md` (session UUID `849a452d-...`, dated 2026-05-26).
- Prior-session snapshot: same path, earlier version (overwritten 2026-05-26); session UUID `fcebe39f-...`.
- User notes / glossary: `C:/Users/3626416/Projects/rocs-copilot/key-notes.md` (includes "Retrieval-miss threshold" explanation appended in this session).
- Brand kit: `C:/Users/3626416/Projects/rocs-copilot/brand/` (FedEx color formulas FY26 PDF, PPT templates, mastheads, marketing-photo "logo" — see §11 brand logo gap).
- Project scaffold + Windows/path/venv conventions: `C:/Users/3626416/Projects/rocs-copilot/CLAUDE.md` plus global `C:/Users/3626416/.claude/CLAUDE.md`.

---

**Next artifact:** implementation plan at `C:/Users/3626416/Projects/rocs-copilot/docs/superpowers/plans/2026-05-25-rocs-copilot-implementation.md`, authored via `superpowers:writing-plans` consuming this spec as input.
