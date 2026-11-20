# Architecture

```
Streamlit app.py ──start_run()──▶ worker thread (asyncio) ──▶ SelectorGroupChat
      ▲                                                          │
      └── polls Progress (thread-safe event list) ◀──────────────┤
                                                                 ▼
  Planner ─▶ Coder ─▶ Executor ─▶ Reviewer
               ▲         │ error      │ not approved
               └─────────┴────────────┘          APPROVED or 20 msgs ─▶ stop
```

## Modules (`src/datapilot/`)
| File | Responsibility |
|---|---|
| `config.py` | `.env` → `Settings`; providers table (groq, openrouter, openai) |
| `llm.py` | Only place that builds model clients (`OpenAIChatCompletionClient` with base_url + model_info for Groq/OpenRouter; replay client for mock) |
| `prompts.py` | System messages, one job per agent |
| `team.py` | Agents, `next_speaker` loop logic, termination conditions |
| `sandbox.py` | Per-session folder, local/Docker executor, `BLOCKED` safety guard |
| `runner.py` | Thread + event loop, builds task text (schema + history + question) |
| `progress.py` | Thread-safe event log read by the UI |
| `answer.py` | Extract final answer, count self-fixes, list outputs |
| `mock_script.py` | Offline scripted replies (includes a real KeyError → fix → label feedback → APPROVED) |
| `validation.py` | Checks uploaded CSVs before the agents see them (≤25 MB, ≤500k rows, ≥2 columns, ≥1 numeric column) |
| `branding.py` | Sets the browser tab title and icon to DataPilot before Streamlit starts (`python -m datapilot.branding`, run by `run.ps1` and the Dockerfile) |
| `ui_style.py`, `views.py` | CSS (gradients/shadows/hover) and HTML fragments |

## Key decisions
- **SelectorGroupChat + `selector_func`** instead of plain RoundRobin: a round-robin would call the Planner again every
  cycle; the function routes by outcome with zero LLM cost. (An LLM-picked speaker is the brief's stretch goal: drop `selector_func`.)
- **Human = UI buttons**, not a blocking `UserProxyAgent`: Streamlit cannot block on stdin. Approve/follow-up is equivalent
  and a follow-up passes earlier Q&A into the next task, with the same data folder (same session).
- **Termination restricted to `Reviewer`** mentioning APPROVED so the Coder echoing the word cannot end the run.
- **Sandbox**: `LocalCommandLineCodeExecutor` in `runs/<id>/` with `cleanup_temp_files=False` so `analysis.py` is kept; Docker optional.
