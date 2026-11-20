"""HTML fragments for the UI (no Streamlit calls here, so they are testable)."""
from __future__ import annotations

import base64
import html

from .team import AGENTS

ICONS = {"Planner": "🧭", "Coder": "💻", "Executor": "⚙️", "Reviewer": "🔍"}
BLURB = {"Planner": "Plans the steps", "Coder": "Writes & fixes code", "Executor": "Runs it safely", "Reviewer": "Checks the result"}


def agent_cards(active: str, events: list, compact: bool = False) -> str:
    """Idle: blurbs. Running: the active agent pulses; an Executor error shows red only until the Coder fixes it.
    Finished (active == ''): everything that spoke is green, Executor notes how many errors were self-fixed."""
    spoken = {e["source"] for e in events}
    running = bool(active)
    last_exec = next((e for e in reversed(events) if e["source"] == "Executor"), None)
    fixes = sum(1 for e in events if e["source"] == "Executor" and e["error"])
    out = []
    for name in AGENTS:
        cls, state = "", BLURB[name]
        if name == active:
            cls, state = "working", "working..."
        elif name == "Executor" and running and last_exec and last_exec["error"]:
            cls, state = "fixed", "hit an error, Coder fixing"
        elif name in spoken:
            cls, state = "done", "done"
            if name == "Executor" and fixes:
                state = f"done, self-fixed {fixes} error{'s' if fixes > 1 else ''}"
        out.append(f'<div class="agent {cls}"><div class="ico">{ICONS[name]}</div><div class="name">{name}</div>'
                   f'<div class="state">{state}</div></div>')
    return f'<div class="agents{" compact" if compact else ""}">{"".join(out)}</div>'


def run_bar(data_name: str, rows: int, cols: int, question: str, stats: list | None = None) -> str:
    chips_html = "".join(
        f'<span class="stat {tone}"><i>{icon}</i><b>{html.escape(str(val))}</b>{html.escape(lbl)}</span>'
        for icon, val, lbl, tone in (stats or []))
    return (f'<div class="runbar"><div class="rb-data"><span class="rb-ic">📁</span><div><b>{html.escape(data_name)}</b>'
            f'<small>{rows:,} rows · {cols} columns</small></div></div>'
            f'<div class="rb-q"><small>QUESTION</small><span>{html.escape(question)}</span></div>'
            f'<div class="rb-stats">{chips_html}</div></div>')


def message_card(ev: dict) -> str:
    src = ev["source"]
    cls = f"{src}{' err' if ev['error'] else ''}"
    who = "You" if src == "user" else src
    tag = " ❌ ERROR" if ev["error"] else ""
    text = ev["text"]
    if src == "user" and "Question:" in text:  # show the question, not the dataset dump sent to the agents
        text = text.split("Question:")[-1].strip()
    if ev["error"] and src == "Executor":  # tracebacks: keep only the useful tail
        text = "\n".join(text.strip().split("\n")[-8:])
    if len(text) > 4000:
        text = text[:4000] + "\n... (trimmed)"
    # newlines as &#10; keep the whole card on ONE line, so Markdown never sees blank lines, code fences or '#' headings
    body = html.escape(text).replace("\r", "").replace("\n", "&#10;")
    mono = " code" if src in ("Coder", "Executor") else ""
    # a <div> (not <pre>): Streamlit's sanitizer strips <pre>, which would collapse every newline
    return f'<div class="msg {cls}"><div class="who">{who}{tag}</div><div class="mbody{mono}">{body}</div></div>'


def answer_card(text: str) -> str:
    blocks = []
    for part in text.split("\n\n"):
        head, _, body = part.partition("\n")
        if head.isupper() and body:
            blocks.append(f"<h4>{html.escape(head)}</h4><p>{html.escape(body).replace(chr(10), '&#10;')}</p>")
        else:
            blocks.append(f"<p>{html.escape(part).replace(chr(10), '&#10;')}</p>")
    return f'<div class="answer">{"".join(blocks)}</div>'


STEPS = ["Data", "Question", "Agents work", "Answer"]


def stepper(current: int) -> str:
    out = []
    for i, name in enumerate(STEPS, 1):
        cls = "done" if i < current else "now" if i == current else ""
        out.append(f'<div class="step {cls}"><span class="num">{"✓" if i < current else i}</span>{name}</div>')
    return f'<div class="stepper">{"".join(out)}</div>'


def tiles(items: list) -> str:
    return '<div class="tiles">' + "".join(
        f'<div class="tile"><div class="ti">{i}</div><div><div class="tv">{html.escape(str(v))}</div>'
        f'<div class="tl">{l}</div></div></div>' for i, v, l in items) + "</div>"


def chips(items: list) -> str:
    return '<div class="chips">' + "".join(f'<span class="chip">{html.escape(i)}</span>' for i in items) + "</div>"


def download_link(path, filename: str, label: str) -> str:
    """A self-contained download link (file embedded as a data URI): no server-side media file, so it can never 404."""
    data = path.read_bytes() if hasattr(path, "read_bytes") else str(path).encode("utf-8")
    if len(data) > 2_000_000:  # generated scripts are tiny; refuse silly sizes rather than bloat the page
        return ""
    b64 = base64.b64encode(data).decode("ascii")
    return (f'<a class="dl" download="{html.escape(filename)}" href="data:text/x-python;base64,{b64}">'
            f'{html.escape(label)}</a>')
