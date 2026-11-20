"""Offline tests: real AutoGen team + real sandbox execution, scripted (mock) LLM replies."""
import subprocess
import sys
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from datapilot.answer import count_fixes, final_answer, output_files  # noqa: E402
from datapilot.config import SAMPLE_CSV, Settings  # noqa: E402
from datapilot.mock_script import build_mock_script  # noqa: E402
from datapilot.runner import start_run  # noqa: E402
from datapilot.sandbox import cleanup, is_safe, new_session_dir  # noqa: E402
from datapilot.team import is_error  # noqa: E402


def wait(p, timeout=120):
    t = time.time()
    while p.status == "running" and time.time() - t < timeout:
        time.sleep(0.3)
    return p


@pytest.fixture(scope="module")
def run():
    d = new_session_dir(SAMPLE_CSV.read_bytes())
    p = start_run(Settings(provider="mock"), d, "Which category had the biggest revenue drop?",
                  mock_script=build_mock_script(d / "data.csv"))
    yield d, wait(p)
    cleanup(d)


def test_completes_and_approved(run):
    d, p = run
    assert p.status == "done", p.error
    text, approved = final_answer(p.snapshot())
    assert approved and "Electronics" in text and "Rs" in text


def test_self_correction_visible(run):
    _, p = run
    ev = p.snapshot()
    assert count_fixes(ev) >= 1
    assert any(e["error"] and "revenue" in e["text"] for e in ev)


def test_message_cap_respected(run):
    _, p = run
    assert len(p.snapshot()) <= Settings().max_messages + 1


def test_files_and_rerun_is_deterministic(run):
    d, _ = run
    files = output_files(d)
    assert len(files["charts"]) == 2 and files["script"]
    outs = [subprocess.run([sys.executable, "analysis.py"], cwd=d, capture_output=True, text=True).stdout for _ in range(2)]
    assert outs[0] == outs[1] and "Biggest drop" in outs[0]


def test_sandbox_blocks_dangerous_code():
    assert not is_safe("import subprocess")[0]
    assert not is_safe("import os; os.system('x')")[0]
    assert is_safe("import pandas as pd\ndf = pd.read_csv('data.csv')")[0]


def test_error_detection():
    assert is_error("Traceback (most recent call last): KeyError: 'revenue'")
    assert not is_error("Months compared: 2026-08 vs 2026-09")
