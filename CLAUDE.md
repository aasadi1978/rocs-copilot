# rocs-copilot

Fresh project scaffold. No source code, manifest, README, or git history yet —
only `.claude/` settings are populated. Update this file as the project takes
shape.

## Status

- **Language (intended):** Python — inferred from `.claude/settings.local.json`
  allowlists for `.venv/Scripts/python.exe`, `pip.exe`, and `pytest.exe`.
- **Source layout:** none yet.
- **Manifest:** none yet (no `pyproject.toml`, `requirements.txt`, `setup.py`).
- **Git:** not initialized.

## Environment

- **Project venv:** `C:/Users/3626416/Projects/rocs-copilot/.venv/`
  - Python: `.venv/Scripts/python.exe`
  - pip: `.venv/Scripts/pip.exe`
  - pytest: `.venv/Scripts/pytest.exe`
- Use the project venv for anything that depends on project packages. The
  global `~/.claude/.venv` is fine for one-off scripts that only need
  pandas / plotly / pyarrow / rich.

## Commands

The venv exists by convention but no project dependencies are pinned yet.

| Task          | Command                                                                             |
| ------------- | ----------------------------------------------------------------------------------- |
| Install a dep | `C:/Users/3626416/Projects/rocs-copilot/.venv/Scripts/python.exe -m pip install …`  |
| Run tests     | `C:/Users/3626416/Projects/rocs-copilot/.venv/Scripts/pytest.exe`                   |
| Run a script  | `C:/Users/3626416/Projects/rocs-copilot/.venv/Scripts/python.exe path/to/script.py` |

Add a real `Run` / `Build` row here once an entry point exists.

## Conventions

- All path rules, shell-selection rules (PowerShell vs Bash), Python-venv
  rules, and git/commit conventions live in the user's global
  `~/.claude/CLAUDE.md`. Don't duplicate them here — just follow them.
- Project-specific rules go below as the project grows.

## TODO (kill these as they get answered)

- [ ] What is rocs-copilot? Add a one-line purpose.
- [ ] Create `pyproject.toml` (or `requirements.txt`) and pin deps.
- [ ] Decide source layout (`src/rocs_copilot/…` vs flat) and document it.
- [ ] Define entry point(s) and add the real `Run` command above.
- [ ] `git init` and set the default branch.
