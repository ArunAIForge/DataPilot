"""Thread-safe progress object: the worker thread writes, the Streamlit UI only reads."""
from __future__ import annotations

import threading
from dataclasses import dataclass, field


@dataclass
class Progress:
    events: list = field(default_factory=list)  # dicts: {source, text, error}
    status: str = "running"  # running | done | error
    stop_reason: str = ""
    error: str = ""
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def add(self, source: str, text: str, error: bool = False) -> None:
        with self._lock:
            self.events.append({"source": source, "text": text, "error": error})

    def snapshot(self) -> list:
        with self._lock:
            return list(self.events)

    @property
    def active(self) -> str:
        """Agent expected to speak next (the one after the last speaker)."""
        ev = self.snapshot()
        if self.status != "running":
            return ""
        if not ev:
            return "Planner"
        last = ev[-1]
        nxt = {"user": "Planner", "Planner": "Coder", "Coder": "Executor", "Reviewer": "Coder"}
        if last["source"] == "Executor":
            return "Coder" if last["error"] else "Reviewer"
        return nxt.get(last["source"], "")
