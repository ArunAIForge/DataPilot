# Testing checklist (maps to the brief's Done checklist)

Automated:
- `python -m pytest -q` (offline unit + engine + UI tests)
- `python tests/e2e_smoke.py` with the app running: 49 real-browser checks (uploads, run, answer, download, approve, follow-up, reset, responsive widths, console errors). Mock provider, no API cost.
- `python -m pyflakes app.py src tests` static check

| # | Requirement | How verified |
|---|---|---|
| 1 | A run shows agents fixing a code error on their own | `test_self_correction_visible` (real `KeyError: 'revenue'` then Coder fix); UI shows red Executor card |
| 2 | Code runs only inside sandbox folder or Docker | `runs/<id>/` workdir; `test_sandbox_blocks_dangerous_code` |
| 3 | Stops on APPROVED or after MAX_MESSAGES (default 20) | `test_message_cap_respected`; termination in `team.py` |
| 4 | Re-running `analysis.py` gives identical numbers | `test_files_and_rerun_is_deterministic` |
| 5 | Every chart has title, axis labels, units | Reviewer prompt + mock flow (feedback on unlabeled chart); eyeball PNGs |
| 6 | Human approval works; follow-up continues session | `test_app_full_flow_mock` reaches Approve; manual: click Approve, ask follow-up |

## Manual run (real LLM)
- [ ] `.env` has one of `GROQ_API_KEY` / `OPENROUTER_API_KEY` / `OPENAI_API_KEY`; sidebar shows "Ready"
- [ ] Sample question returns Electronics / South with numbers matching a pandas check
- [ ] Upload a different CSV and ask a different question without code changes
- [ ] Hover effects: hero, agent cards, message cards, buttons, charts
- [ ] Bad API key shows a readable error, not a crash
- [ ] No keys in git (`git status` shows `.env` ignored)
