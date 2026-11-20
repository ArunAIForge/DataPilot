"""Runs the AutoGen team in a worker thread with its own event loop; streams messages into Progress."""
from __future__ import annotations

import asyncio
import logging
import os
import threading
import uuid
from pathlib import Path

import pandas as pd
from autogen_agentchat.base import TaskResult

from .config import PROVIDERS, Settings
from .progress import Progress
from .team import build_team, is_error

log = logging.getLogger("datapilot.runner")
RUN_TIMEOUT = int(os.getenv("RUN_TIMEOUT", "300"))  # hard wall-clock cap per run (seconds)


def describe_data(csv: Path) -> str:
    df = pd.read_csv(csv)
    return (f"Dataset: data.csv, {len(df)} rows.\nColumns/dtypes:\n{df.dtypes.to_string()}\n"
            f"First rows:\n{df.head(3).to_string()}")


def build_task(question: str, data_desc: str, history: list) -> str:
    prev = "".join(f"\nEarlier question: {q}\nEarlier answer: {a}\n" for q, a in history[-3:])
    return f"{data_desc}\n{prev}\nQuestion: {question}"


def friendly_error(exc: BaseException, settings: Settings | None = None, error_id: str = "") -> str:
    """One short, human sentence with a fix hint. Never a type name, status dump or traceback (those go to the log)."""
    name, msg = type(exc).__name__, str(exc)
    low = f"{name} {msg}".lower()
    prov = settings.provider.capitalize() if settings and not settings.is_mock else "the provider"
    model = (settings.model or PROVIDERS.get(settings.provider, ("",))[0]) if settings and not settings.is_mock else ""

    def has(*needles) -> bool:
        return any(n in low for n in needles)

    if has("404", "notfounderror", "does not exist", "model_not_found", "no endpoints found", "not a valid model"):
        shown = f"'{model.split('/')[-1]}'" if model else "selected model"
        return (f"The model {shown} isn't available for your {prov} account. Pick another provider in the sidebar, "
                "or set LLM_MODEL in .env to a model you can use.")
    if has("401", "403", "invalid api key", "incorrect api key", "authentication", "unauthorized", "permission"):
        return f"{prov} rejected the API key. Check the key for this provider in .env."
    if has("429", "rate limit", "ratelimit", "quota", "insufficient", "credit", "402"):
        return f"{prov} rate limit or credits reached. Wait a minute, add credits, or switch provider."
    if isinstance(exc, (asyncio.TimeoutError, TimeoutError)) or has("timed out", "timeout"):
        return f"The run took longer than {RUN_TIMEOUT}s and was stopped. Try a simpler question."
    if has("connection", "connecterror", "network", "name resolution", "ssl"):
        return "Could not reach the model provider. Check your internet connection and try again."
    if has("context length", "context_length", "too many tokens", "maximum context", "400", "badrequest"):
        return "The provider rejected the request (input too long or invalid). Try a shorter question or smaller dataset."
    if has("500", "502", "503", "504", "overloaded", "unavailable", "bad gateway", "internal server"):
        return f"{prov} is temporarily unavailable. Please try again in a moment."
    ref = f" (reference {error_id})" if error_id else ""
    return f"Something went wrong while running the agents{ref}. Please try again, or switch provider."


async def _stream(settings, workdir, task, progress, mock_script):
    team = build_team(settings, workdir, mock_script)
    async for msg in team.run_stream(task=task):
        if isinstance(msg, TaskResult):
            progress.stop_reason = msg.stop_reason or ""
            continue
        text = getattr(msg, "content", None)
        if isinstance(text, str):
            progress.add(msg.source, text, error=msg.source == "Executor" and is_error(text))


def start_run(settings: Settings, workdir: Path, question: str, history=None, mock_script=None) -> Progress:
    progress = Progress()
    task = build_task(question, describe_data(workdir / "data.csv"), history or [])
    log.info("run start provider=%s session=%s", settings.provider, workdir.name)

    def work():
        try:
            asyncio.run(asyncio.wait_for(_stream(settings, workdir, task, progress, mock_script), RUN_TIMEOUT))
            progress.status = "done"
            log.info("run done session=%s messages=%d", workdir.name, len(progress.snapshot()))
        except Exception as exc:  # surface a readable message to the UI, never die silently
            error_id = uuid.uuid4().hex[:8]
            log.exception("run failed session=%s ref=%s", workdir.name, error_id)  # full details stay in the server log
            progress.error = friendly_error(exc, settings, error_id)
            progress.status = "error"

    threading.Thread(target=work, daemon=True, name=f"run-{workdir.name}").start()
    return progress
