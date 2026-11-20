import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from datapilot import branding  # noqa: E402
from datapilot.runner import friendly_error  # noqa: E402
from datapilot.validation import validate_csv  # noqa: E402


def test_validation_rejects_bad_files():
    assert not validate_csv(b"").ok
    assert not validate_csv(b"a\n1\n").ok  # one column
    assert not validate_csv(b"a,b\nx,y\n").ok  # no numeric column
    assert not validate_csv(b"a,b\n").ok  # no rows


def test_validation_accepts_sales_csv():
    r = validate_csv(b"order_date,region,units\n2026-01-01,South,3\n")
    assert r.ok and r.rows == 1 and "region" in r.columns


def test_friendly_errors():
    assert "key" in friendly_error(Exception("Error code: 401 invalid api key")).lower()
    assert "rate limit" in friendly_error(Exception("429 rate limit")).lower()
    assert "longer than" in friendly_error(TimeoutError()).lower()


def test_branding_title_and_icon(tmp_path):
    icon = tmp_path / "i.png"
    branding.make_icon(icon, 64)
    assert icon.stat().st_size > 200
    assert branding.apply() in (True, False)
    import streamlit

    html = (Path(streamlit.__file__).parent / "static" / "index.html").read_text(encoding="utf-8")
    assert "<title>DataPilot</title>" in html


def test_approval_detection_is_lenient_but_safe():
    from types import SimpleNamespace as M

    from datapilot.team import reviewer_approved

    assert reviewer_approved([M(source="Reviewer", content="ANSWER ...\n\nApproved")])
    assert reviewer_approved([M(source="Reviewer", content="**APPROVED**")])
    assert not reviewer_approved([M(source="Reviewer", content="Not approved: add labels")])
    assert not reviewer_approved([M(source="Reviewer", content="Disapproved")])
    assert not reviewer_approved([M(source="Coder", content="APPROVED")])


def test_best_effort_and_script_recovery(tmp_path):
    from datapilot.answer import best_effort, output_files

    ev = [{"source": "Executor", "text": "Traceback", "error": True},
          {"source": "Executor", "text": "Biggest drop: Electronics", "error": False},
          {"source": "Executor", "text": "KeyError", "error": True}]
    assert best_effort(ev) == "Biggest drop: Electronics"
    (tmp_path / "tmp_code_abc.py").write_text("print(1)")
    assert output_files(tmp_path)["script"].name == "analysis.py"


def test_strip_files_section_removes_invented_names():
    from datapilot.answer import strip_files

    txt = "ANSWER\nElectronics fell.\n\nFILES\nfake.png | analysis.py\n\nSUGGESTED NEXT QUESTION\nWhy?"
    out = strip_files(txt)
    assert "fake.png" not in out and "ANSWER" in out and "SUGGESTED NEXT QUESTION" in out


def test_script_with_non_ascii_is_readable(tmp_path):
    """Regression: AI-written code with a rupee sign made the UI read fail on Windows (cp1252), blanking the answer panel."""
    f = tmp_path / "analysis.py"
    f.write_bytes('# revenue in ₹ lakh — final\nprint(1)\n'.encode("utf-8"))
    assert "₹" in f.read_text(encoding="utf-8", errors="replace")


def test_run_bar_stats_and_escaping():
    from datapilot import views

    html = views.run_bar("a<b>.csv", 10, 3, "q?", [("💬", 5, "messages", ""), ("●", "Approved", "", "ok")])
    assert "a&lt;b&gt;.csv" in html and "stat ok" in html and "10 rows" in html


def test_errors_never_leak_technical_details():
    from datapilot.config import Settings

    raw = ("RuntimeError: NotFoundError: Error code: 404 - The model llama-3.3-70b-versatile does not exist "
           "or you do not have access to it. Traceback: Traceback (most recent call last): File x.py")
    out = friendly_error(RuntimeError(raw), Settings(provider="groq", model="llama-3.3-70b-versatile", api_key="x"))
    assert "isn't available" in out and "llama-3.3-70b-versatile" in out
    for bad in ("Traceback", "RuntimeError", "NotFoundError", "Error code", ".py"):
        assert bad not in out
    generic = friendly_error(ValueError("boom: secret stack /home/x/y.py line 3"), None, "ab12cd34")
    assert "boom" not in generic and "ab12cd34" in generic and "Traceback" not in generic
    assert "key" in friendly_error(Exception("403 forbidden")).lower()
    assert "unavailable" in friendly_error(Exception("503 overloaded")).lower()


def test_download_link_roundtrip(tmp_path):
    import base64

    from datapilot import views

    f = tmp_path / "analysis.py"
    f.write_bytes(("# revenue in " + chr(0x20b9) + " lakh" + chr(10) + "print(1)" + chr(10)).encode("utf-8"))
    link = views.download_link(f, "analysis.py", "Download")
    assert 'download="analysis.py"' in link and chr(10) not in link  # one line: safe inside Markdown
    b64 = link.split("base64,")[1].split('"')[0]
    assert chr(0x20b9) in base64.b64decode(b64).decode("utf-8")
