"""Turn the finished conversation into answer text + files."""
from __future__ import annotations

import re
import shutil
from pathlib import Path

from .team import APPROVED_RE


def final_answer(events: list) -> tuple[str, bool]:
    """Return (answer_text, approved). Approved only if the Reviewer's last message contains APPROVED."""
    for ev in reversed(events):
        if ev["source"] == "Reviewer":
            if APPROVED_RE.search(ev["text"]):
                return re.sub(r"[\s*_`]*APPROVED[\s*_`.!]*$", "", ev["text"], flags=re.I).strip(), True
            break
    return "", False


def strip_files(text: str) -> str:
    """Drop the model's FILES section: it lists invented names; the UI shows the real charts and script itself."""
    parts = [p for p in text.split("\n\n") if not p.strip().upper().startswith("FILES")]
    return "\n\n".join(parts).strip()


def count_fixes(events: list) -> int:
    """How many times the Coder repaired itself right after an Executor error."""
    return sum(1 for a, b in zip(events, events[1:]) if a["source"] == "Executor" and a["error"] and b["source"] == "Coder")


def best_effort(events: list) -> str:
    """When the run hit the limit: the last successful (unreviewed) Executor output, so the user still gets something."""
    for ev in reversed(events):
        if ev["source"] == "Executor" and not ev["error"] and ev["text"].strip():
            return ev["text"].strip()
    return ""


def output_files(workdir: Path) -> dict:
    script = workdir / "analysis.py"
    if not script.exists():  # Coder forgot '# filename: analysis.py' -> recover the newest generated script
        tmp = sorted(workdir.glob("tmp_code_*.py"), key=lambda f: f.stat().st_mtime)
        if tmp:
            shutil.copy(tmp[-1], script)
    return {"charts": sorted(workdir.glob("*.png")), "script": script if script.exists() else None}
