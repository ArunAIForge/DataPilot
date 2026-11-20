# CLAUDE.md: DataPilot

Context for AI coding assistants working on this repo.

## What this is
AutoGen (AgentChat 0.7) + Streamlit app: user uploads a sales CSV and asks a question → Planner, Coder, Executor, Reviewer
loop (self-correcting) → plain-English answer, charts, `analysis.py`; human approves or asks a follow-up.
Brief: the use-case definitions PDF, use case 03. Full spec: `PRPs/datapilot_agents.md`.

## Commands
- Run: `powershell -ExecutionPolicy Bypass -File run.ps1` (or `streamlit run app.py`)
- Test: `python -m pytest -q` (offline, mock LLM, real sandbox)
- Env lives outside the repo: `%USERPROFILE%\venvs\datapilot` (Python 3.12)

## Architecture rules (do not break)
1. **Numbers come from executed code, never from the LLM.** Reviewer may only quote numbers the Executor printed.
2. **Code runs only in the sandbox** (`runs/<id>/` or Docker). Keep `sandbox.BLOCKED` guard on via `approval_func`.
3. **Always stop**: `FunctionalTermination(reviewer_approved) | MaxMessageTermination(settings.max_messages)` (default 20, env MAX_MESSAGES).
4. **Loop logic lives in `team.next_speaker`** (deterministic): Executor error → Coder; Reviewer not approved → Coder.
5. **Vendor isolation:** only `llm.py` builds model clients. Providers: openrouter, groq, openai (+ offline `mock`).
6. **Mock mode works with no keys**, runs real code, and is labelled MOCK. Tests stay offline.
7. The team runs in a worker thread (`runner.py`); the UI only reads `Progress`. Never call Streamlit from the thread.
8. Secrets only in `.env` (git-ignored). Never hard-code keys.
9. UI styling lives in `ui_style.py` (gradients, shadows, hover); HTML fragments in `views.py`. Keep logic out of both.
10. Charts need title, axis labels and units; `analysis.py` must re-run to identical output.

## Style
Python 3.11+, type hints, small modules (<150 lines), no global state outside Streamlit `session_state`.
