# rocs-copilot — 2026-05-26 — no git

## Resuming this session

Session UUID: 849a452d-6b6a-421e-9314-b7e73953167a

    claude --resume 849a452d-6b6a-421e-9314-b7e73953167a
    /resume 849a452d-6b6a-421e-9314-b7e73953167a

## Goal

Complete the `enhanced-brainstorming` flow for rocs-copilot — close the design walkthrough (Sections 3–5), author the design spec, author the implementation plan, run Phase-3 gate-readiness checks, re-snapshot, and prepare the Phase-5 hand-off to a fresh Sonnet 4.6 (1M) execution session. No source code is written in this session by design.

## Current state

Design spec + implementation plan written and gate-checked; ready for hand-off to a fresh Sonnet 4.6 (1M) session to execute the plan task-by-task. Source code build has not started.

    branch: no git
    working tree: STATUS.md modified (this snapshot); docs/superpowers/specs/ + docs/superpowers/plans/ both new this session; key-notes.md added/modified by user via manual paste

## Files in play

- `C:/Users/3626416/Projects/rocs-copilot/STATUS.md` — modified: this snapshot (rewritten now; previous version from earlier in this session overwritten in place).
- `C:/Users/3626416/Projects/rocs-copilot/docs/superpowers/specs/2026-05-25-rocs-copilot-design.md` — new: approved design spec; 13 sections; single source of truth for the build.
- `C:/Users/3626416/Projects/rocs-copilot/docs/superpowers/plans/2026-05-25-rocs-copilot-implementation.md` — new: 28-task / 7-phase implementation plan with pragmatic TDD; consumed by `superpowers:executing-plans` or `superpowers:subagent-driven-development`.
- `C:/Users/3626416/Projects/rocs-copilot/CLAUDE.md` — read-only-context: project scaffold; defers path/shell/venv conventions to global `~/.claude/CLAUDE.md`.
- `C:/Users/3626416/Projects/rocs-copilot/key-notes.md` — read-only-context: user-managed notes; contains the "Retrieval-miss threshold" explanation pasted this session (Claude drafted text; user pasted because plan mode blocked direct write).
- `C:/Users/3626416/Projects/rocs-copilot/brand/` — read-only-context: FedEx brand kit (color formulas PDF, PPT templates, mastheads, marketing-photo "logo" that is NOT a UI wordmark — see spec §11).
- `C:/Users/3626416/Projects/rocs-copilot/.claude/settings.local.json` — read-only-context: preauthorizes `.venv/Scripts/{python,pip,pytest}.exe`; wide sibling-project denylist.

## What has changed

- Closed **Section 3 (Data flow)**: SSE ordering = tokens stream first then a single `source` event before `done`; retriever = history-aware (`create_history_aware_retriever` rewrites follow-ups before Chroma search) (uncommitted, no git).
- Closed **Section 4 (Error handling)**: three-surface model (ingestion CLI / Flask backend / React UI); structured SSE error codes (`no_corpus`, `llm_unavailable`, `internal`); retrieval-miss threshold tunable via `RETRIEVAL_MIN_SCORE=0.3`; canned helpful no-docs answer with no `source` event; [Retry] button on transient-error bubbles; explicitly NOT doing server-side retry / persistence / rate limiting / cross-provider failover (uncommitted, no git).
- Closed **Section 5 (Testing)**: pytest backend + Vitest frontend with mocking rules; no hard coverage gate; CI day-1 once `git init` happens; tiny synthetic PDF/DOCX fixtures committed to `tests/fixtures/corpus/`; explicitly NOT doing Playwright E2E / load / a11y / visual regression (uncommitted, no git).
- Wrote `C:/Users/3626416/Projects/rocs-copilot/docs/superpowers/specs/2026-05-25-rocs-copilot-design.md` — 13-section design spec consolidating the full approved design including all locked decisions and explicit non-goals (uncommitted, no git).
- Wrote `C:/Users/3626416/Projects/rocs-copilot/docs/superpowers/plans/2026-05-25-rocs-copilot-implementation.md` — 28-task / 7-phase implementation plan with full code in every step; pragmatic TDD; conventional-commit cadence; explicit Windows/PowerShell conventions; phased structure (Bootstrap → Ingestion → Backend serving → Frontend bootstrap → Frontend chat → CI → DoD walkthrough) (uncommitted, no git).
- Re-wrote `STATUS.md` mid-session after exiting plan mode, then re-wrote it again here.
- Deleted the stale plan-mode scratchpad at `C:/Users/3626416/.claude/plans/laod-status-md-and-tell-cuddly-wand.md` (created earlier in this session as a workaround when plan mode blocked direct `STATUS.md` writes; obsolete now that STATUS.md is authoritative).
- User created and populated `C:/Users/3626416/Projects/rocs-copilot/key-notes.md` with the Claude-drafted "Retrieval-miss threshold" explanation (manual paste because plan mode blocked direct write).
- Ran spec self-review (placeholders, internal consistency, scope, ambiguity) — clean.
- Ran plan self-review (spec coverage, placeholder scan, type/signature consistency across Python↔TS boundary) — clean.
- Ran `enhanced-brainstorming` Phase-3 gate-readiness checks against the plan — all five gates pass (acceptance criteria, no open arch decisions, risk flags, out-of-scope section, definition of done).

## Tried & failed (do not retry)

- Tried writing to `key-notes.md` directly mid-conversation → failed because plan mode blocked edits outside its scratchpad → use manual paste workflow (Claude prints text in chat, user pastes).
- Tried calling `ExitPlanMode` to unblock spec write before snapshotting → failed because user rejected and asked for `/snapshot` first → write snapshot to plan-mode scratchpad as an interim, then exit plan mode, then copy into the project's `STATUS.md` and clean up the scratchpad.
- Tried writing snapshot to the canonical `STATUS.md` path while plan mode was active → failed because plan mode confined writes to a single harness scratchpad → use plan-mode scratchpad as interim and copy to `STATUS.md` after exiting plan mode.
- Tried (prior session) Approach A (minimal hand-rolled, raw provider SDKs, no framework) → failed because user preferred Approach B for familiarity with LangChain → use LangChain (loaders, splitters, retrievers, LCEL chains).
- Tried (prior session) assuming an internal LLM gateway / Azure OpenAI / Anthropic-direct for prod → failed because FedEx GCP target has no programmatic LLM today (only Gemini chat UI) → design provider-agnostic; dev on Groq + OpenAI; prod TBD.
- Tried (prior session) treating `brand/logo-with-fred-smith.png` as a usable UI logo → failed because it is a marketing photo, not a wordmark → use a typographic placeholder in `frontend/src/assets/brand/` (codified in plan Task 4.4) until a clean SVG/PNG is supplied.
- Tried (prior session) accessing FedEx team-repo URLs via WebFetch → failed because private FedEx GitHub pages require SSO → use `gh api orgs/FedEx/teams/<slug>/repos` (gh authenticated as `alireza-asadi_fedex`, scopes `repo`+`read:org`).

## What to do next

1. Exit this Claude Code session.
2. Start a fresh Claude Code session in `C:/Users/3626416/Projects/rocs-copilot/`.
3. In the fresh session, run `/model sonnet` to switch to **Sonnet 4.6 (1M context)** per the global `~/.claude/CLAUDE.md` plan/execution boundary.
4. Paste the resume prompt below into the fresh session.
5. The fresh session reads `C:/Users/3626416/Projects/rocs-copilot/STATUS.md`, then the spec at `docs/superpowers/specs/2026-05-25-rocs-copilot-design.md`, then the plan at `docs/superpowers/plans/2026-05-25-rocs-copilot-implementation.md`.
6. The fresh session invokes `superpowers:executing-plans` (single-context) OR `superpowers:subagent-driven-development` (fresh subagent per task, recommended for plans this size).
7. The fresh session walks Phase 1 → Phase 7 of the implementation plan task-by-task: bootstrap → ingestion → backend serving → frontend bootstrap → frontend chat → CI → end-to-end DoD walkthrough.
8. The fresh session re-snapshots `STATUS.md` after each phase, or at minimum at MVP completion (Phase 7 done, `v0.1.0` tagged).

## How to verify

- `Test-Path C:/Users/3626416/Projects/rocs-copilot/docs/superpowers/specs/2026-05-25-rocs-copilot-design.md` → `True`.
- `Test-Path C:/Users/3626416/Projects/rocs-copilot/docs/superpowers/plans/2026-05-25-rocs-copilot-implementation.md` → `True`.
- `Test-Path C:/Users/3626416/.claude/plans/laod-status-md-and-tell-cuddly-wand.md` → `False` (cleaned up).
- `Get-ChildItem C:/Users/3626416/Projects/rocs-copilot -Name` → expect `CLAUDE.md`, `STATUS.md`, `brand`, `docs`, `key-notes.md` (and the hidden `.claude` dir). No `src/`, `frontend/`, `tests/`, `.venv/`, `.git/` yet — by design; the implementation plan creates them.
- `gh auth status` → confirms `alireza-asadi_fedex` (active) with `repo`+`read:org` on github.com.

## Known quirks / constraints

- **Not a git repo yet.** Implementation plan Phase 1 Task 1.2 runs `git init`. No commits possible until then.
- **Windows / git-bash path rules** (per global `~/.claude/CLAUDE.md`): forward slashes only; `.exe` invocations via PowerShell; never bare `python`; project venv path will be `C:/Users/3626416/Projects/rocs-copilot/.venv/Scripts/python.exe` (preauthorized in `.claude/settings.local.json`) but `.venv` does not exist on disk yet — plan Phase 1 Task 1.3 creates it with `py -3.11 -m venv .venv`.
- **`.claude/settings.local.json`** blocks Write/Edit to 30+ sibling project dirs under `C:/Users/3626416/Projects/` — all writes must stay inside `C:/Users/3626416/Projects/rocs-copilot/`.
- **FedEx team-repo URLs are out of reach** without an explicit `gh` clone — keep treating the project as greenfield unless the user names specific repos to pull.
- **Brand logo gap:** `brand/logo-with-fred-smith.png` is a marketing photo (Fred Smith + FedEx logo), not a UI wordmark. Plan Task 4.4 ships a typographic placeholder; swap when a clean asset is supplied.
- **GCP prod LLM gap:** FedEx GCP has no programmatic LLM today (only Gemini chat UI). The provider abstraction in `providers/llm.py` (plan Task 2.2) is load-bearing, not optional.
- **Model boundary** (per global `~/.claude/CLAUDE.md`): planning/spec/plan-writing runs on **Opus 4.7** (current session); implementation execution runs on **Sonnet 4.6 (1M context)** in a fresh session. The fresh session MUST `/model sonnet` before invoking `superpowers:executing-plans` or `superpowers:subagent-driven-development`.
- **Library docs lookup** (per global `~/.claude/CLAUDE.md`): use `context7` MCP (`mcp__plugin_context7_context7__resolve-library-id` then `mcp__plugin_context7_context7__query-docs`) for LangChain, Flask, Vite, React, Chroma, Vitest — not WebSearch.
- **Brainstorming flow:** this session completed enhanced-brainstorming Phases 1–4 (brainstorm, spec, plan, gate-checks). Phase 5 (execution) is the fresh session's job. Do NOT re-invoke `enhanced-brainstorming` or `superpowers:brainstorming` in the execution session.

## Architecture reference

See the design spec for full architecture detail; do not duplicate here. Key entry points the execution session needs:

- **Spec:** `C:/Users/3626416/Projects/rocs-copilot/docs/superpowers/specs/2026-05-25-rocs-copilot-design.md` — §5 architecture, §6 component trees, §7 data flow, §8 error handling, §9 testing, §10 config, §11 risks, §12 DoD.
- **Plan:** `C:/Users/3626416/Projects/rocs-copilot/docs/superpowers/plans/2026-05-25-rocs-copilot-implementation.md` — 7 phases × 28 tasks; pragmatic TDD; conventional commits.
- **Locked stack:** Python 3.11+ / Flask / LangChain (LCEL) / Chroma / Groq + OpenAI providers (prod TBD on GCP) / Vite + React 18 + TypeScript / CSS Modules + typed theme tokens / vanilla `useChatStream` SSE hook / pytest + Vitest / GitHub Actions CI.

## Resume prompt

```text
You are starting a fresh execution session for the rocs-copilot project. The brainstorming + spec + implementation-plan phases are DONE. Your job is to execute the implementation plan.

Project: full-stack chatbot copilot for ROCS (FedEx's internal routing/optimization web app for ground-operations planners). Repo path: C:/Users/3626416/Projects/rocs-copilot. NOT a git repo yet (Plan Phase 1 Task 1.2 runs `git init`). No source code yet — only CLAUDE.md, STATUS.md, brand/, docs/, key-notes.md, .claude/.

FIRST ACTIONS (in order):
  1. Run `/model sonnet` to switch to Sonnet 4.6 (1M context) per the global plan/execution boundary in ~/.claude/CLAUDE.md.
  2. Read C:/Users/3626416/Projects/rocs-copilot/STATUS.md (this snapshot — has full state and constraints).
  3. Read C:/Users/3626416/Projects/rocs-copilot/docs/superpowers/specs/2026-05-25-rocs-copilot-design.md (design spec — single source of truth).
  4. Read C:/Users/3626416/Projects/rocs-copilot/docs/superpowers/plans/2026-05-25-rocs-copilot-implementation.md (28-task implementation plan).
  5. Invoke `superpowers:subagent-driven-development` (recommended for a plan this size — fresh subagent per task, two-stage review) OR `superpowers:executing-plans` (single-context with checkpoints).
  6. Walk Phase 1 → Phase 7 of the plan task-by-task. Each task has explicit "Expected" outputs and a commit step.

PLAN PHASES (high-level):
  Phase 1: Project bootstrap (directory skeleton, pyproject.toml, .gitignore, .env.example, git init, venv, install deps, generate fixture corpus, pytest smoke).
  Phase 2: Ingestion (chunker, providers/llm factory, Chroma store with content-hash idempotency, PDF/DOCX loader, scripts/ingest.py CLI with tenacity backoff).
  Phase 3: Backend serving (config.py pydantic settings, chains/rag_chain.py with history-aware retriever, routes/health.py, routes/chat.py SSE endpoint with all §8.2 error paths, app.py Flask factory).
  Phase 4: Frontend bootstrap (Vite + React + TS scaffold, Vitest, vite proxy /api/* → :5000, theme tokens + CSS, typographic Wordmark placeholder).
  Phase 5: Frontend chat (types/api.ts SSE event union, useChatStream hook with AbortController, SourcePanel, MessageBubble with error+Retry variant, Chat integration, App shell with branded header).
  Phase 6: CI (.github/workflows/test.yml runs pytest + vitest + frontend build on push; push to remote; verify CI green).
  Phase 7: End-to-end DoD walkthrough (ingest fixture corpus with real OpenAI key, boot backend + frontend, walk spec §12 DoD steps 6-11 in a browser, tag v0.1.0).

LOCKED DECISIONS (do not re-litigate — spec is the source):
  - Job: Q&A over ROCS docs + error/discrepancy troubleshooting.
  - Audience: planners (user is MVP proxy).
  - LLM dev: Groq + OpenAI via provider abstraction. Prod GCP: no programmatic LLM today; abstraction is load-bearing.
  - Embeddings: OpenAI text-embedding-3-small.
  - Runtime: single user, laptop, stateless, no auth, no DB, no chat-history persistence.
  - Stack: LangChain (LCEL) + Chroma + Flask + Vite/React/TS + CSS Modules + typed theme tokens (no Tailwind, no chat-UI lib, no Vercel AI SDK).
  - SSE ordering: TOKENS first, then ONE `source` event, then `done` (spec §7.2).
  - Retriever: history-aware (`create_history_aware_retriever`).
  - Retrieval-miss threshold: tunable via `RETRIEVAL_MIN_SCORE=0.3` env var; on miss, SKIP LLM call entirely and stream the canned helpful answer with no `source` event.
  - Frontend error bubble: red-tinted, FedEx accent, [Retry] button on transient errors; input always re-enables; AbortController on user resubmit.
  - Brand: Digital Blue #007AB7 primary; purple #4D148C + orange #FF6200 accents; gradient `linear-gradient(90deg,#4D148C 0%,#7D22C3 33%,#FF6200 100%)` for signature moments; Gray 90/80/70 text; Gray 30/20/10 surfaces.

CONSTRAINTS / GOTCHAS:
  - Windows / git-bash: forward slashes only; .exe via PowerShell; never bare `python`. Project venv path is C:/Users/3626416/Projects/rocs-copilot/.venv/Scripts/python.exe (preauthorized) — created in Phase 1 Task 1.3 with PowerShell `py -3.11 -m venv .venv`.
  - .claude/settings.local.json blocks edits to 30+ sibling project dirs — stay inside C:/Users/3626416/Projects/rocs-copilot/.
  - Not a git repo until Phase 1 Task 1.2. No commits possible before that.
  - For library API questions (LangChain, Flask, Vite, React, Chroma, Vitest) use the context7 MCP (mcp__plugin_context7_context7__resolve-library-id then __query-docs), NOT WebSearch.
  - Brand logo: brand/logo-with-fred-smith.png is a marketing photo, NOT a UI wordmark. Plan Task 4.4 ships a typographic placeholder.
  - GCP prod LLM gap: no programmatic LLM available. The provider abstraction (Task 2.2) is mandatory; do not shortcut it.
  - Do NOT add features outside the spec (auth, persistence, multi-user, real LLM provider integration tests, Playwright E2E, load tests, a11y tests, visual regression). Spec §2.2 lists explicit non-goals. Plan conventions header reinforces.
  - Do NOT re-invoke enhanced-brainstorming or superpowers:brainstorming. Brainstorming is done. Execute the plan.

TRIED & FAILED (do not retry):
  - Approach A (minimal hand-rolled, no framework) → user picked Approach B (LangChain) → use LangChain.
  - Azure / internal LLM gateway for prod → no programmatic LLM on FedEx GCP today → provider abstraction load-bearing.
  - brand/logo-with-fred-smith.png as UI logo → marketing photo, not wordmark → typographic Wordmark placeholder per Plan Task 4.4.
  - WebFetch on FedEx team-repo URLs → SSO-blocked → use `gh api orgs/FedEx/teams/<slug>/repos` (gh authenticated as alireza-asadi_fedex).

FULL CONTEXT: read C:/Users/3626416/Projects/rocs-copilot/STATUS.md, then the spec, then the plan, then start executing.
```
