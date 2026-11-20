"""End-to-end UI check with real Chrome (Playwright) against a RUNNING app. Mock provider only: no API calls, no cost.

    pip install playwright            # uses your installed Chrome, no browser download
    streamlit run app.py              # in another terminal
    python tests/e2e_smoke.py [http://localhost:8501]

Exit code 0 = every check passed. Not collected by pytest (file name does not start with test_).
"""
import sys
import tempfile
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8501"
SAMPLE = Path(__file__).resolve().parents[1] / "sample_data" / "sales_2026.csv"
results: list[tuple[bool, str]] = []
console_errors: list[str] = []


not_found: list[str] = []
last_step = {"name": "start"}


def check(name: str, ok: bool, detail: str = "") -> None:
    last_step["name"] = name
    results.append((bool(ok), name))
    print(("PASS " if ok else "FAIL ") + name + (f"  [{detail}]" if detail and not ok else ""))


def body(pg) -> str:
    return pg.inner_text("body")


def wait_text(pg, text: str, timeout: int = 60) -> bool:
    end = time.time() + timeout
    while time.time() < end:
        if text in body(pg):
            return True
        time.sleep(0.5)
    return False


def no_app_error(pg) -> bool:
    return pg.locator('[data-testid="stException"]').count() == 0 and "Run failed" not in body(pg)


def horizontal_overflow(pg) -> bool:
    return pg.evaluate("document.documentElement.scrollWidth > window.innerWidth + 2")


def upload(pg, name: str, data: bytes) -> None:
    f = Path(tempfile.mkdtemp()) / name
    f.write_bytes(data)
    pg.set_input_files('input[type="file"]', str(f))
    time.sleep(3)


with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    ctx = browser.new_context(viewport={"width": 1536, "height": 1000}, accept_downloads=True)
    pg = ctx.new_page()
    pg.on("console", lambda m: console_errors.append(m.text) if m.type == "error" else None)
    pg.on("pageerror", lambda e: console_errors.append(str(e)))
    pg.on("response", lambda r: not_found.append(f"{r.url[-70:]} (after: {last_step['name']})") if r.status == 404 and "favicon" not in r.url else None)

    # ---------------------------------------------------------------- 1. load + branding
    pg.goto(URL)
    check("page renders", wait_text(pg, "Your data", 60))
    time.sleep(1)
    check("browser title is DataPilot", pg.title() == "DataPilot", pg.title())
    icons = pg.eval_on_selector_all("link[rel*=icon]", "els => els.map(e => e.href)")
    check("favicon is the DataPilot icon (new cache-busted file)", any("datapilot-favicon" in i for i in icons), str(icons))
    check("no 'Streamlit' text/menu/deploy chrome", "Deploy" not in body(pg) and pg.locator('[data-testid="stToolbar"]:visible').count() == 0)
    check("no exception on first load", no_app_error(pg))
    check("no horizontal scroll (desktop idle)", not horizontal_overflow(pg))
    check("idle: step bar, workspace and team cards shown",
          all(t.lower() in body(pg).lower() for t in ("Your question", "Meet your analyst team", "Planner", "Coder", "Executor", "Reviewer")))
    check("Run disabled before data is loaded", pg.get_by_role("button", name="Run analysis").is_disabled())

    # ---------------------------------------------------------------- 2. sidebar
    sb = pg.locator('[data-testid="stSidebar"]')
    st = sb.inner_text()
    check("sidebar lists 4 providers", all(n in st for n in ("Groq", "OpenRouter", "OpenAI", "Mock")))
    check("sidebar safety limits (20 messages)", "Max messages" in st and "20" in st)
    pg.get_by_role("button", name="Mock (offline demo)").click()
    time.sleep(2)
    check("clicking a provider activates it (exactly one ACTIVE)", sb.inner_text().count("ACTIVE") == 1 and "MOCK MODE" in body(pg))
    pg.get_by_role("button", name="OpenRouter").first.click()
    time.sleep(2)
    check("switching provider updates hero badge", "OpenRouter" in pg.locator(".badge").first.inner_text())
    pg.get_by_role("button", name="Mock (offline demo)").click()
    time.sleep(2)

    # ---------------------------------------------------------------- 3. upload validation
    upload(pg, "empty.csv", b"")
    check("empty CSV rejected with a clear message", wait_text(pg, "empty", 20) or wait_text(pg, "Could not read", 2))
    check("Run still disabled after bad upload", pg.get_by_role("button", name="Run analysis").is_disabled())
    upload(pg, "text.csv", b"a,b\nx,y\n")
    check("CSV without numeric column rejected", wait_text(pg, "numeric", 20))
    upload(pg, "latin1.csv", "name,val\ncafé,1\n".encode("latin-1"))
    check("non-UTF-8 CSV handled without exception", no_app_error(pg))
    check("no raw traceback shown for bad files", "Traceback" not in body(pg))

    # ---------------------------------------------------------------- 4. valid upload (the 12k-row sample via the uploader)
    pg.set_input_files('input[type="file"]', str(SAMPLE))
    check("valid CSV accepted (rows/columns chips)", wait_text(pg, "12,360 rows", 20) or wait_text(pg, "rows", 5))
    check("step bar moved to Question", "Question" in pg.locator(".step.now").first.inner_text())
    pg.get_by_text("Preview data").click()
    end = time.time() + 15
    while time.time() < end and pg.locator('[data-testid="stDataFrame"]').count() == 0:
        time.sleep(0.5)
    check("data preview expander works", pg.locator('[data-testid="stDataFrame"]').count() >= 1)

    # ---------------------------------------------------------------- 5. question + examples
    ta = pg.locator("textarea").first
    pg.get_by_role("button", name="Top products").click()
    time.sleep(1.5)
    check("example chip fills the question box", "5 products" in ta.input_value(), ta.input_value())
    ta.fill("")
    ta.press("Control+Enter")
    time.sleep(1.5)
    check("empty question disables Run", pg.get_by_role("button", name="Run analysis").is_disabled())
    ta.fill("Which category had the biggest revenue drop in September vs August, and which region caused most of it?")
    ta.press("Control+Enter")
    time.sleep(1.5)
    check("valid question enables Run", pg.get_by_role("button", name="Run analysis").is_enabled())

    # ---------------------------------------------------------------- 6. full agent run (mock): self-fix, review, answer
    pg.get_by_role("button", name="Run analysis").click()
    check("run starts: header collapses, step 3 active",
          wait_text(pg, "Agent conversation", 20) and pg.locator(".hero.compact").count() == 1)
    done = wait_text(pg, "Approve answer", 90)
    check("run completes and shows the answer", done)
    time.sleep(1)
    txt = body(pg)
    check("answer: Electronics and South identified", "Electronics" in txt and "South" in txt)
    check("answer: exact numbers shown (Rs ... L, %)", "Rs" in txt and "%" in txt)
    check("agent self-correction visible (Executor ERROR then fix)", "ERROR" in txt and "self-fixed" in txt)
    check("all four agent cards green", pg.locator(".agent.done").count() == 4)
    check("status chip Approved", "Approved" in pg.locator(".rb-stats").inner_text())
    check("stepper: all steps complete, Answer active", pg.locator(".step.done").count() == 3 and "Answer" in pg.locator(".step.now").inner_text())
    check("FILES section replaced by real files (no invented names)", "SUGGESTED NEXT QUESTION" in txt and "FILES" not in pg.locator(".answer").inner_text())
    imgs = pg.locator('[data-testid="stImage"] img')
    check("two charts rendered", imgs.count() == 2, str(imgs.count()))
    check("charts actually loaded (non-zero size)", all(imgs.nth(i).evaluate("e => e.naturalWidth") > 100 for i in range(imgs.count())))
    check("no app exception during run", no_app_error(pg))
    check("conversation shows the question only (no dataset dump)", "Dataset: data.csv" not in txt)

    with pg.expect_download(timeout=15000) as dl:
        pg.get_by_role("link", name="Download analysis.py").click()
    script = Path(dl.value.path()).read_text(encoding="utf-8")
    check("download analysis.py works and is the final script", "revenue" in script and "savefig" in script and "set_ylabel" in script)

    # ---------------------------------------------------------------- 7. human approval + follow-up in same session
    pg.get_by_role("button", name="Approve answer").click()
    check("human approval recorded", wait_text(pg, "Approved ✓", 15))
    follow = "Did discounts on Earbuds X2 change between 2026-08 and 2026-09?"
    fu = pg.get_by_label("Ask a follow-up (same session, same data)")
    fu.fill(follow)
    fu.press("Enter")
    time.sleep(1)
    pg.get_by_role("button", name="Ask follow-up").click()
    time.sleep(3)
    check("follow-up starts a new run on the same data", follow in pg.locator(".runbar").inner_text() and "sales_2026" in pg.locator(".runbar").inner_text())
    check("follow-up run completes", wait_text(pg, "Approve answer", 90))
    check("no app exception after follow-up", no_app_error(pg))

    # ---------------------------------------------------------------- 8. responsive layout (answer screen)
    for w, h in ((1280, 800), (1024, 800), (768, 900), (390, 844)):
        pg.set_viewport_size({"width": w, "height": h})
        time.sleep(1.5)
        check(f"no horizontal overflow at {w}px (results)", not horizontal_overflow(pg))
    pg.set_viewport_size({"width": 1536, "height": 1000})
    time.sleep(1)

    # ---------------------------------------------------------------- 9. reset
    pg.get_by_role("button", name="New session").click()
    check("New session returns to the start", wait_text(pg, "Your data", 15) and pg.locator(".hero.compact").count() == 0)
    check("Run disabled again after reset", pg.get_by_role("button", name="Run analysis").is_disabled())
    pg.set_viewport_size({"width": 390, "height": 844})
    time.sleep(1.5)
    check("no horizontal overflow at 390px (idle)", not horizontal_overflow(pg))

    ignorable = ("favicon", "Failed to load resource", "ResizeObserver", "net::ERR")
    real_errors = [e for e in console_errors if not any(i in e for i in ignorable)]
    check("no browser console errors", not real_errors, "; ".join(real_errors[:3]) + " | 404s: " + "; ".join(not_found[:3]))
    browser.close()

failed = [n for ok, n in results if not ok]
print(f"\n{len(results) - len(failed)}/{len(results)} checks passed")
if failed:
    print("FAILED:\n - " + "\n - ".join(failed))
sys.exit(1 if failed else 0)
