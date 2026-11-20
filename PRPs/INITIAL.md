# INITIAL: DataPilot feature request

## FEATURE
DataPilot, a self-correcting data analyst. User uploads a sales CSV and asks a business question in plain English.
AutoGen agents (Planner, Coder, Executor, Reviewer + human approval) plan, write pandas/matplotlib code, run it in a
sandbox, fix their own errors, and return a plain-English answer, labelled charts (PNG) and a re-runnable `analysis.py`.

## EXAMPLES
- `sample_data/sales_2026.csv` (columns: order_date, region, category, product, units, unit_price, discount)
- Question: "Which category had the biggest revenue drop in September vs August, and which region caused most of it?"
- Expected conversation: Planner plan → Coder → Executor `KeyError: 'revenue'` → Coder fix → OK → Reviewer "chart 2 has no
  axis labels" → Coder → OK → Reviewer APPROVED.
- Expected answer shape: ANSWER / WHERE IT CAME FROM / FILES / SUGGESTED NEXT QUESTION (see brief §3.6).

## DOCUMENTATION
- Brief: the use-case definitions PDF (use case 03)
- AutoGen AgentChat: https://microsoft.github.io/autogen/stable/ (AssistantAgent, CodeExecutorAgent, SelectorGroupChat, termination)
- Sibling conventions: `../CompetitorResearchCrew` (CLAUDE.md, PRPs, run.ps1, ui_style.py)

## OTHER CONSIDERATIONS
- LLM providers: OpenRouter, Groq, OpenAI only (+ offline mock for tests); keys in `.env`.
- Numbers must come from executed code. Code runs only in the sandbox. Hard stop at MAX_MESSAGES (default 20; 12 per the brief).
- UI must feel interactive: gradients, shadows, hover lift/glow, pulsing active-agent card, live conversation feed.
- Stretch: SelectorGroupChat with LLM-chosen speaker, multi-sheet Excel, one-page PDF export.
