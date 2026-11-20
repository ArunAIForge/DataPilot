"""Sandboxed code execution: a per-session folder (local) or a Docker container."""
from __future__ import annotations

import re
import shutil
import sys
import uuid
import venv
from pathlib import Path

from .config import RUNS_DIR, Settings

# Code that could escape the sandbox folder or touch the network is refused before it runs.
BLOCKED = re.compile(
    r"\b(subprocess|os\.system|os\.remove|os\.rmdir|os\.popen|shutil|socket|requests|urllib|http\.client|"
    r"importlib|ctypes)\b|__import__|\beval\(|\bexec\("
)


def new_session_dir(csv_bytes: bytes) -> Path:
    d = RUNS_DIR / uuid.uuid4().hex[:8]
    d.mkdir(parents=True, exist_ok=True)
    (d / "data.csv").write_bytes(csv_bytes)
    return d


def is_safe(code: str) -> tuple[bool, str]:
    m = BLOCKED.search(code)
    return (False, f"blocked pattern: {m.group(0)}") if m else (True, "")


def approval(request):
    from autogen_agentchat.agents import ApprovalResponse

    ok, why = is_safe(request.code)
    return ApprovalResponse(approved=ok, reason=why or "ok")


def build_executor(workdir: Path, settings: Settings):
    if settings.executor == "docker":
        from autogen_ext.code_executors.docker import DockerCommandLineCodeExecutor

        return DockerCommandLineCodeExecutor(work_dir=workdir, timeout=settings.exec_timeout, image="python:3.12-slim")
    from autogen_ext.code_executors.local import LocalCommandLineCodeExecutor

    try:
        ctx = venv.EnvBuilder().ensure_directories(sys.prefix)  # run code with this env's python (pandas, matplotlib)
    except Exception:
        ctx = None
    return LocalCommandLineCodeExecutor(timeout=settings.exec_timeout, work_dir=workdir, virtual_env_context=ctx,
                                       cleanup_temp_files=False)  # keep analysis.py for download/re-run


def purge_old_runs(max_age_hours: float = 24) -> int:
    """Delete session folders older than max_age_hours (uploaded data should not pile up)."""
    import time

    n = 0
    for d in RUNS_DIR.glob("*"):
        if d.is_dir() and time.time() - d.stat().st_mtime > max_age_hours * 3600:
            shutil.rmtree(d, ignore_errors=True)
            n += 1
    return n


def cleanup(workdir: Path) -> None:
    shutil.rmtree(workdir, ignore_errors=True)
