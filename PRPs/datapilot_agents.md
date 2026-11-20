# PRP: DataPilot, Self-Correcting Data Analyst

Source: the use-case definitions PDF, use case 03 (Track 3, Agentic AI, AutoGen).

## 1. Goal
A Streamlit chat app where a business owner uploads a sales CSV, asks a question in plain English, and an AutoGen team
returns an answer calculated by real code, with charts and `analysis.py`, after self-correcting any errors.

## 2. Why
Owners cannot write Python/SQL and wait days for analysts; normal chatbots guess numbers. Agents that write, run, and
check code give verifiable answers in minutes.

## 3. What (success criteria)
- [x] Upload any CSV + question; sample data included
- [x] Agents: Planner, Coder, Executor, Reviewer (+ human approval via UI)
- [x] Agent conversation visible live, including errors and fixes
- [x] Outputs: short written answer, charts as PNG, final `analysis.py`
- [x] Executor runs code only in sandbox folder (or Docker)
- [x] Stops on APPROVED or after MAX_MESSAGES (default 20; brief says 12), never loops forever
- [x] Re-running `analysis.py` reproduces the same numbers
- [x] Every chart has title, axis labels, units
- [x] Human approval works; follow-up continues the same session
- [x] Providers: OpenRouter, Groq, OpenAI via `.env`; offline mock for tests
- [x] Interactive UI: gradient hero, shadowed cards, hover lift/glow, pulsing active agent, colour-coded message cards

## 4. Context
| Brief item | Implementation |
|---|---|
| AssistantAgent (Planner, Coder, Reviewer) | `autogen_agentchat.agents.AssistantAgent(name, model_client, system_message)` |
| CodeExecutorAgent | `CodeExecutorAgent(name, code_executor, approval_func=...)`; `LocalCommandLineCodeExecutor(work_dir, timeout, cleanup_temp_files=False)` or `DockerCommandLineCodeExecutor` |
| Team | `SelectorGroupChat(participants, model_client, selector_func=..., termination_condition=...)` (deterministic router; stretch = LLM picks) |
| Termination | `FunctionalTermination(reviewer_approved) \| MaxMessageTermination(MAX_MESSAGES)` (case-insensitive APPROVED, Reviewer only) |
| Human-in-the-loop | Streamlit Approve / follow-up (Streamlit can't block on `UserProxyAgent` input) |
| Models | `OpenAIChatCompletionClient`; Groq/OpenRouter via `base_url` + explicit `ModelInfo` |

Gotchas
- Executor deletes the script after run by default → `cleanup_temp_files=False`.
- Coder must begin its block with `# filename: analysis.py` so the file is saved.
- Matplotlib needs `Agg` backend (no GUI); never `plt.show()`.
- `run_stream` is async → run in a thread with its own event loop; UI polls `Progress`.
- Executor errors surface as text (`Traceback`, `Error`); `team.is_error` routes to the Coder.

## 5. Implementation blueprint
1. `config.py`, `llm.py`: settings and client factory (groq, openrouter, openai, mock).
2. `prompts.py`: one job per agent; Reviewer's APPROVED format.
3. `sandbox.py`: session folder, executor, safety guard.
4. `team.py`: agents + `next_speaker` + termination.
5. `runner.py` + `progress.py`: thread, streaming, history-aware task text.
6. `answer.py`: final answer, fix count, outputs.
7. `mock_script.py`: scripted run with a real bug→fix→feedback→APPROVED path.
8. `validation.py`: reject bad CSVs (size, rows, columns, no numeric column) before a run.
9. `ui_style.py`, `views.py`, `app.py`: UI. `branding.py`: tab title and icon.
10. Tests, README, docs.

## 6. Validation loop
- `python -m pytest -q` → all pass (offline)
- `run.ps1` → sample question → Electronics / South, 2 PNGs, `analysis.py` downloadable
- Re-run `analysis.py` twice → identical stdout
- Real provider run with each of Groq, OpenRouter, OpenAI keys

## 7. Anti-patterns
- Letting the LLM state numbers it did not see in Executor output
- Running generated code outside the sandbox folder
- Unbounded loops (no termination cap)
- Hard-coded API keys; calling Streamlit from the worker thread
- Hard-coding the sample question's columns in prompts (must work on any sales CSV)
