# 🧭 DataPilot: Self-Correcting Data Analyst

Ask a business question in plain English. A team of **Microsoft AutoGen** agents plans, writes Python (pandas + matplotlib),
runs it in a sandbox, **fixes its own errors**, and returns the answer with charts and the re-runnable `analysis.py`.

Brief: the use-case definitions PDF, use case 03 (Track 3, Agentic AI, AutoGen).
Full spec: [`PRPs/datapilot_agents.md`](PRPs/datapilot_agents.md).

## Run locally (Windows)

**Prerequisite:** Python 3.12 installed (the launcher uses `py -3.12`).

### Option A: one command (recommended)
```powershell
cd <path-to>\DataPilot
powershell -ExecutionPolicy Bypass -File run.ps1
```
First run creates `%USERPROFILE%\venvs\datapilot`, installs requirements, creates `.env` and sample data, then starts
Streamlit at http://localhost:8501.

### Option B: manual
```powershell
cd <path-to>\DataPilot
py -3.12 -m venv $env:USERPROFILE\venvs\datapilot          # first time only
& "$env:USERPROFILE\venvs\datapilot\Scripts\python.exe" -m pip install -r requirements.txt   # first time only
copy .env.example .env                                      # first time only
& "$env:USERPROFILE\venvs\datapilot\Scripts\python.exe" -m streamlit run app.py
```

### Add your API key
Edit `.env`: set the provider and ONE key, then restart the app.
```
LLM_PROVIDER=groq            # or openrouter | openai
GROQ_API_KEY=your_key_here   # or OPENROUTER_API_KEY / OPENAI_API_KEY
```
You can also click a provider card in the sidebar: 🟢 means a key was found, ⚪ means no key, and the active card shows ACTIVE.
No key? Click the **Mock (offline demo)** card in the sidebar: scripted agent replies, real code execution.

### Use the app
1. Click **Use sample data** (or upload a CSV with columns like `order_date, region, category, product, units, unit_price, discount`).
2. Keep the default question or type your own.
3. Click **Run analysis** and watch the agents plan, code, hit errors and fix them.
4. Read the answer and charts, download `analysis.py`, click **Approve**, or ask a follow-up.

Uploads are validated first: CSV only, up to 25 MB and 500,000 rows, at least 2 columns, and at least one numeric column.
Anything else shows a readable error instead of starting a run.

### Troubleshooting
- `py -3.12` not found: install Python 3.12 from python.org.
- Port busy: add `--server.port 8502` to the streamlit command.
- Sidebar shows "Add ..._API_KEY to .env": the key is missing or the provider doesn't match the key.
- Regenerate sample data: `python sample_data\make_sample.py`.

## Models: OpenRouter, Groq, OpenAI
Put ONE key in `.env` (git-ignored) and set `LLM_PROVIDER`:

| Provider | Key variable | Default model |
|---|---|---|
| `groq` | `GROQ_API_KEY` | `openai/gpt-oss-120b` |
| `openrouter` | `OPENROUTER_API_KEY` | `meta-llama/llama-3.3-70b-instruct` |
| `openai` | `OPENAI_API_KEY` | `gpt-4o-mini` |

Override with `LLM_MODEL` or the sidebar box. `mock` (offline, scripted replies, **real** code execution) needs no key and
is used by the tests.

## The agents
| Agent | AutoGen class | Job |
|---|---|---|
| Planner | `AssistantAgent` | Short analysis plan from question + columns |
| Coder | `AssistantAgent` | Writes `analysis.py`; rewrites on error/feedback |
| Executor | `CodeExecutorAgent` + local/Docker executor | Runs code in the sandbox folder |
| Reviewer | `AssistantAgent` | Checks answer, numbers, chart labels; replies `APPROVED` |
| You | Streamlit buttons | Approve the answer or ask a follow-up (same session) |

Team: `SelectorGroupChat` with a deterministic `selector_func`: error → Coder, not approved → Coder, else onward.
Stops on `APPROVED` **or** `MAX_MESSAGES` (default 20; set 12 for the brief's strict limit) via `FunctionalTermination | MaxMessageTermination`.

## Sample
`sample_data/sales_2026.csv` (≈12.4k rows). Question: *Which category had the biggest revenue drop in September vs August,
and which region caused most of it?* → Electronics, South region, with `category_trend.png`, `region_breakdown.png`, `analysis.py`.

## Safety
Code runs only in `runs/<session>/` (or Docker with `EXECUTOR=docker`). A pre-run guard blocks `subprocess`, `os.system`,
`shutil`, sockets, `requests`, `eval/exec`. Timeout 60 s per run.

## Tests
```powershell
# app running in another terminal, then (real Chrome, mock provider, no API calls):
& $env:USERPROFILE\venvs\datapilot\Scripts\python.exe tests\e2e_smoke.py
```
```powershell
& $env:USERPROFILE\venvs\datapilot\Scripts\python.exe -m pytest -q   # offline, no keys
& $env:USERPROFILE\venvs\datapilot\Scripts\python.exe -m pyflakes app.py src tests   # static check
```
GitHub Actions (`.github/workflows/ci.yml`) runs the offline tests on each push.

## Docs
`CLAUDE.md` · `docs/ARCHITECTURE.md` · `docs/TESTING_CHECKLIST.md` · `PRPs/INITIAL.md` · `PRPs/datapilot_agents.md`
