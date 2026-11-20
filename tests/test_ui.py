import sys
import time
from pathlib import Path

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from datapilot import views  # noqa: E402


def test_views_escape_and_states():
    ev = {"source": "Executor", "text": "<b>KeyError</b>", "error": True}
    assert "&lt;b&gt;" in views.message_card(ev) and "err" in views.message_card(ev)
    assert "working" in views.agent_cards("Coder", [])
    assert "ANSWER" in views.answer_card("ANSWER\nx")


def test_app_full_flow_mock():
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=60).run()
    assert not at.exception
    next(b for b in at.button if "Mock" in b.label).click().run()
    next(b for b in at.button if "sample" in b.label).click().run()
    next(b for b in at.button if "Run analysis" in b.label).click().run()
    t = time.time()
    while time.time() - t < 90 and not any("Approve" in b.label for b in at.button):
        time.sleep(1)
        at.run()
    assert not at.exception, at.exception
    assert any("Approve" in b.label for b in at.button)
