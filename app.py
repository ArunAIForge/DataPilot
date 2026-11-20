"""DataPilot: Streamlit UI over an AutoGen team (Planner, Coder, Executor, Reviewer + human approval)."""
import html
import logging
import re
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent / "src"))

import importlib  # noqa: E402

from datapilot import branding, ui_style, views  # noqa: E402
from datapilot.answer import best_effort, count_fixes, final_answer, output_files, strip_files  # noqa: E402
from datapilot.config import PROVIDERS, SAMPLE_CSV, UI_PROVIDERS, load_settings  # noqa: E402
from datapilot.mock_script import build_mock_script  # noqa: E402
from datapilot.sandbox import new_session_dir, purge_old_runs  # noqa: E402
from datapilot.validation import validate_csv  # noqa: E402

st.set_page_config(page_title="DataPilot", page_icon=branding.page_icon(), layout="wide", initial_sidebar_state="expanded")


@st.cache_resource
def _bootstrap() -> bool:
    """Once per server process: logging, branding, old-session cleanup."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    branding.apply()
    purge_old_runs(24)
    return True


_bootstrap()
for _m in (ui_style, views):  # always pick up the latest styles/fragments (no stale module after edits)
    importlib.reload(_m)
st.markdown(ui_style.CSS, unsafe_allow_html=True)

S = st.session_state
for k, v in dict(workdir=None, progress=None, history=[], question="", approved_flag=False, upname=None,
                 settled=None, upload_error="", upkey=None, up_n=0).items():
    S.setdefault(k, v)

# ---------------- sidebar: model providers ----------------
with st.sidebar:
    st.markdown('<div class="brand"><div class="logo">🧭</div><div><div class="bn">DataPilot</div>'
                '<div class="bt">Self-correcting data analyst</div></div></div>', unsafe_allow_html=True)
    default = load_settings()
    options = UI_PROVIDERS + ["mock"]
    idx = options.index(default.provider) if default.provider in options else 0
    ready = {o: o == "mock" or bool(load_settings(o).api_key) for o in options}
    label = {"groq": "Groq", "openrouter": "OpenRouter", "openai": "OpenAI", "mock": "Mock (offline demo)"}

    S.setdefault("provider", options[idx])
    provider = S.provider if S.provider in options else options[idx]
    settings = load_settings(provider)

    st.markdown('<div class="sec">MODEL PROVIDERS</div><div class="legend">Click a card to activate · 🟢 key found · ⚪ no key</div>',
                unsafe_allow_html=True)
    with st.container(key="providers"):
        for o in options:
            model_name = PROVIDERS[o][0].split("/")[-1] if o in PROVIDERS else "scripted replies"
            active = "  ✔ ACTIVE" if o == provider else ""
            if st.button(f"{'🟢' if ready[o] else '⚪'} **{label[o]}**{active}  \n{model_name}",
                         key=f"prov_{o}", type="primary" if o == provider else "secondary", use_container_width=True):
                S.provider = o
                st.rerun()
    if not settings.ready:
        st.markdown(f'<div class="warnbox">Add <b>{PROVIDERS[provider][2]}</b> to <code>.env</code> and refresh.</div>',
                    unsafe_allow_html=True)

    st.markdown('<div class="sec">SAFETY LIMITS</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="kv"><span>Max messages</span><b>{settings.max_messages}</b></div>'
        f'<div class="kv"><span>Sandbox</span><b>{settings.executor}</b></div>'
        f'<div class="kv"><span>Run timeout</span><b>{settings.exec_timeout}s / step</b></div>'
        f'<div class="kv"><span>Stops on</span><b>APPROVED</b></div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 New session", use_container_width=True):
        for k in ("workdir", "progress", "upname", "settled", "upkey"):
            S[k] = None
        S.history, S.question, S.upload_error = [], "", ""
        S.up_n += 1  # new uploader widget so a previously uploaded file does not silently reload
        st.rerun()

# ---------------- hero + stepper ----------------
badge = "MOCK MODE" if settings.is_mock else f"{label[provider]} · {(settings.model or PROVIDERS[provider][0]).split(chr(47))[-1]}"
if S.progress is not None:  # a run exists: slim header, the answer is the focus
    st.markdown(f'<div class="hero compact"><h1>🧭 DataPilot</h1><span class="badge">● {badge}</span></div>', unsafe_allow_html=True)
else:
    st.markdown(
        '<div class="hero"><div class="hl"><h1>🧭 DataPilot</h1>'
        '<p>Ask a business question in plain English. AI agents write and run the Python, fix their own errors, '
        'and answer with charts.</p></div>'
        f'<div class="hr"><span class="badge">● {badge}</span>'
        '<div class="pills"><span>🤖 4 agents</span><span>🔒 Sandboxed code</span><span>♻️ Self-correcting</span></div></div></div>',
        unsafe_allow_html=True)

p = S.progress
step = 1 if S.workdir is None else 2 if p is None else 3 if p.status == "running" else 4
st.markdown(views.stepper(step), unsafe_allow_html=True)


def launch(question: str):
    from datapilot.runner import start_run  # lazy: autogen import is slow, keep first paint fast

    S.question = question
    script = build_mock_script(S.workdir / "data.csv") if settings.is_mock else None
    S.progress = start_run(settings, S.workdir, question, S.history, script)
    S.approved_flag, S.settled = False, None


DEFAULT_Q = "Which category had the biggest revenue drop in September vs August, and which region caused most of it?"
EXAMPLES = {"🏆 Top products": "Which 5 products earned the most revenue?",
            "📈 Monthly trend": "How did total revenue change month by month?",
            "🏷️ Discounts": "Which region gives the highest average discount?"}
S.setdefault("q_text", S.question or DEFAULT_Q)


def _use_example(text: str):
    S.q_text = text


# ---------------- workspace: one card, two balanced halves ----------------
go = False
if S.progress is None:
    with st.container(border=True, key="workspace"):
        left, right = st.columns([1, 1.1], gap="large")
        with left:
            st.markdown('<div class="ph"><span class="pn">1</span><div><b>Your data</b>'
                        '<small>A sales CSV with dates, categories and numbers</small></div></div>', unsafe_allow_html=True)
            up = st.file_uploader("Upload a sales CSV", type="csv", label_visibility="collapsed", key=f"uploader_{S.up_n}")
            if up is None:
                S.upkey = None
            elif S.upkey != (up.name, up.size):
                S.upkey = (up.name, up.size)  # remembered even when rejected: validated once, not on every rerun
                check = validate_csv(up.getvalue())
                if check.ok:
                    S.workdir = new_session_dir(up.getvalue()); S.upname = up.name; S.history = []; S.progress = None
                    S.upload_error = ""
                else:
                    S.upload_error = check.message
                st.rerun()
            if st.button("📊 Or use the sample data (sales_2026.csv)", use_container_width=True):
                S.workdir = new_session_dir(SAMPLE_CSV.read_bytes()); S.upname = None; S.history = []; S.progress = None
                S.upload_error = ""
                st.rerun()
            if S.upload_error:
                st.error(S.upload_error)
            if S.workdir is not None:
                df = pd.read_csv(S.workdir / "data.csv", nrows=50000)
                st.markdown(views.chips([f"✓ {len(df):,} rows", f"{df.shape[1]} columns", "ready"]), unsafe_allow_html=True)
                with st.expander("Preview data"):
                    st.dataframe(df.head(6), use_container_width=True, hide_index=True, height=190)
            elif not S.upload_error:
                st.markdown('<div class="hint">👆 Upload a CSV or load the sample to unlock the next step.</div>'
                            '<div class="works">Works best with columns like</div>'
                            + views.chips(["order_date", "region", "category", "units", "unit_price", "…"]),
                            unsafe_allow_html=True)
        with right:
            st.markdown('<div class="ph"><span class="pn">2</span><div><b>Your question</b>'
                        '<small>Plain English. No SQL or Python needed.</small></div></div>', unsafe_allow_html=True)
            q = st.text_area("Question", key="q_text", height=105, label_visibility="collapsed", max_chars=500)
            with st.container(key="examples"):
                cols = st.columns(len(EXAMPLES))
                for col, (name, text) in zip(cols, EXAMPLES.items()):
                    col.button(name, key=f"ex_{name}", help=text, on_click=_use_example, args=(text,), use_container_width=True)
            can_run = S.workdir is not None and settings.ready and bool(q.strip())
            go = st.button("🚀 Run analysis", type="primary", disabled=not can_run, use_container_width=True)
            st.markdown('<div class="works" style="margin-top:12px">💡 Tip: name the months, region or product you care about for a sharper answer.</div>',
                        unsafe_allow_html=True)
            if not settings.ready:
                st.markdown(f'<div class="hint warn">Add {PROVIDERS[provider][2]} to .env or pick Mock in the sidebar.</div>', unsafe_allow_html=True)

if go:
    launch(q.strip())
    st.rerun()

# ---------------- idle: meet the team (fills the page with something useful) ----------------
if S.progress is None:
    st.markdown('<div class="sech">Meet your analyst team</div>', unsafe_allow_html=True)
    st.markdown(views.agent_cards("", []), unsafe_allow_html=True)


# ---------------- results (a fragment: refreshes itself, the rest of the page is not re-run) ----------------
@st.cache_data(show_spinner=False)
def _data_meta(path: str):
    df = pd.read_csv(path, nrows=50000)
    return len(df), df.shape[1]


def render_results():
    try:
        _render_results()
    except Exception:  # never leave a silent blank panel
        logging.getLogger("datapilot.ui").exception("render failed")
        st.error("Something went wrong while showing the results. Check the server log, then run the question again.")


def _render_results():
    p = S.progress
    if p.status != "running" and S.settled is not p:
        S.settled = p
        st.rerun()  # once, when the run ends: step bar updates, polling stops; nothing is drawn twice (no stale download links)
    events = p.snapshot()
    approved_text, approved = final_answer(events) if p.status == "done" else ("", False)
    status = {"running": "Running", "error": "Failed"}.get(p.status, "Approved" if approved else "Limit reached")
    rows, ncols = _data_meta(str(S.workdir / "data.csv"))
    tone = {"Running": "run", "Failed": "bad", "Approved": "ok"}.get(status, "bad")
    st.markdown(views.run_bar(S.upname or "sales_2026.csv (sample)", rows, ncols, S.question,
                              [("💬", len(events), "messages", ""), ("🛠️", count_fixes(events), "self-fixes", ""),
                               ("●", status, "", tone)]), unsafe_allow_html=True)
    st.markdown(views.agent_cards(p.active, events, compact=True), unsafe_allow_html=True)

    result, feed = st.columns([1.15, 1], gap="large")  # the answer comes first
    with feed:
        with st.container(border=True, height=900):
            st.markdown("##### 🤖 Agent conversation")
            if p.status == "running":
                st.info("Agents are working... errors and fixes appear as they happen.")
            st.markdown("".join(views.message_card(e) for e in events), unsafe_allow_html=True)
            if p.status == "error":
                st.markdown(f'<div class="errbox"><b>⚠️ The analysis could not finish</b><span>{html.escape(p.error)}</span></div>',
                            unsafe_allow_html=True)
    with result:
        with st.container(border=True):
            st.markdown("##### ✅ Answer")
            if p.status == "running":
                st.caption("The answer appears here once the Reviewer approves.")
            elif p.status == "error":
                st.markdown('<div class="hint warn">No answer was produced. Pick another provider in the sidebar, click '
                            '<b>New session</b>, then run the question again.</div>', unsafe_allow_html=True)
            elif p.status == "done" and not approved:
                st.warning(f"The {settings.max_messages}-message limit was reached before the Reviewer approved. "
                           "Showing the last successful (unreviewed) output; rephrasing the question may help.")
                partial = best_effort(events)
                if partial:
                    st.code(partial[:3000], language="text")
                files = output_files(S.workdir)
                if files["charts"]:
                    cols = st.columns(min(len(files["charts"]), 2))
                    for i, img in enumerate(files["charts"]):
                        cols[i % len(cols)].image(str(img), caption=img.name, use_container_width=True)
                if files["script"]:
                    st.markdown(views.download_link(files["script"], "analysis.py", "⬇️ Download analysis.py"), unsafe_allow_html=True)
            elif approved:
                st.markdown(views.answer_card(strip_files(approved_text)), unsafe_allow_html=True)
                files = output_files(S.workdir)
                if files["charts"]:
                    cols = st.columns(len(files["charts"]))
                    for col, img in zip(cols, files["charts"]):
                        col.image(str(img), caption=img.name, use_container_width=True)
                m = re.search(r"SUGGESTED NEXT QUESTION\s*\n(.+)", approved_text)
                st.markdown('<div class="sech" style="margin-top:6px">Your call</div>', unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                with c1:
                    if files["script"]:
                        st.markdown(views.download_link(files["script"], "analysis.py", "⬇️ Download analysis.py"), unsafe_allow_html=True)
                with c2:
                    if S.approved_flag:
                        st.success("Approved ✓")
                    elif st.button("👍 Approve answer", type="primary", use_container_width=True):
                        S.approved_flag = True
                        S.history.append((S.question, approved_text.split("\n\n")[0][:300]))
                        st.rerun(scope="fragment")
                follow = st.text_input("Ask a follow-up (same session, same data)", value=m.group(1).strip() if m else "",
                                       placeholder="Ask a follow-up question", max_chars=500)
                if st.button("➡️ Ask follow-up", type="primary", use_container_width=True) and follow.strip():
                    if not S.approved_flag:
                        S.history.append((S.question, approved_text.split("\n\n")[0][:300]))
                    launch(follow.strip())
                    st.rerun()  # full rerun: step bar + polling restart


if S.progress is not None:
    running = S.progress.status == "running"
    st.fragment(run_every=1.0 if running else None)(render_results)()
