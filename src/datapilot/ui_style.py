"""CSS for the Streamlit app: one palette (CSS variables), gradients, soft shadows, hover lift and glow. No logic here.

Palette: deep teal / ocean for structure, warm orange for the single main action, and
green / amber / red kept strictly for status so colour always means something.
"""

CSS = """
<style>
:root {
  --ink: #0c2430; --muted: #5b7380;
  --bg1: #f0fdfa; --bg2: #ecfeff; --bg3: #fff7ed;
  --primary: #0e7490; --primary2: #0891b2; --sky: #0ea5e9; --teal: #0d9488;
  --accent: #f97316; --accent2: #f59e0b;
  --side1: #042f2e; --side2: #0c4a6e;
  --ok: #16a34a; --warn: #f59e0b; --err: #dc2626;
  --line: #bae6fd; --card: rgba(255,255,255,.92);
  --shadow: rgba(8,145,178,.45);
}

/* hide Streamlit chrome: menu, deploy, footer, running man, decoration bar */
#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDeployButton"], [data-testid="stDecoration"],
[data-testid="stStatusWidget"], [data-testid="stAppDeployButton"] { display: none !important; visibility: hidden !important; }
header[data-testid="stHeader"] { background: transparent; height: 2.2rem; }
.block-container { padding: 1.2rem 1.25rem 1.5rem 1.25rem !important; max-width: 100% !important; }
[data-testid="stMainBlockContainer"] { padding-left: 1.25rem !important; padding-right: 1.25rem !important; }
.hero, .stepper, .tiles, .agents { width: 100%; box-sizing: border-box; }

.stApp { background: linear-gradient(135deg, var(--bg1) 0%, var(--bg2) 55%, var(--bg3) 100%); color: var(--ink); }
[data-testid="stSidebar"] { background: linear-gradient(180deg, var(--side1) 0%, var(--side2) 100%); }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] { color: #d1faf5; }
[data-testid="stSidebar"] [data-testid="stAlert"] [data-testid="stMarkdownContainer"] { color: inherit; }
[data-testid="stSidebar"] > div:first-child { padding-top: .5rem; }

/* ---------- hero ---------- */
.hero {
  display: flex; align-items: center; justify-content: space-between; gap: 18px; flex-wrap: wrap;
  background: linear-gradient(120deg, #134e4a 0%, #0f766e 30%, #0891b2 62%, #0ea5e9 85%, #f59e0b 130%);
  background-size: 250% 250%; animation: shift 14s ease infinite;
  color: #fff; padding: 22px 28px; border-radius: 22px; margin-bottom: 14px;
  box-shadow: 0 20px 44px -14px rgba(8,145,178,.65); transition: transform .3s, box-shadow .3s;
}
.hero:hover { transform: translateY(-2px); box-shadow: 0 28px 54px -14px rgba(8,145,178,.8); }
.hero h1 { margin: 0; font-size: 2rem; color: #fff; padding: 0; line-height: 1.15; }
.hero p { margin: 6px 0 0; opacity: .95; font-size: 1rem; max-width: 640px; }
.hero .hr { display: flex; flex-direction: column; align-items: flex-end; gap: 10px; }
.hero .pills { display: flex; gap: 8px; flex-wrap: wrap; justify-content: flex-end; }
.hero .pills span { padding: 4px 12px; border-radius: 999px; font-size: .76rem; font-weight: 600;
  background: rgba(255,255,255,.14); border: 1px solid rgba(255,255,255,.28); transition: transform .15s, background .15s; }
.hero .pills span:hover { transform: translateY(-2px); background: rgba(255,255,255,.28); }
.badge { display:inline-block; padding:5px 15px; border-radius:999px; font-size:.8rem; font-weight:700;
  background: rgba(255,255,255,.22); border: 1px solid rgba(255,255,255,.4); backdrop-filter: blur(4px); }
@keyframes shift { 0%{background-position:0% 50%} 50%{background-position:100% 50%} 100%{background-position:0% 50%} }

/* ---------- cards / containers ---------- */
div[data-testid="stVerticalBlockBorderWrapper"] { background: var(--card); border: 1px solid var(--line) !important;
  border-radius: 20px !important; box-shadow: 0 12px 30px -14px var(--shadow); transition: box-shadow .25s; }
div[data-testid="stVerticalBlockBorderWrapper"]:hover { box-shadow: 0 22px 44px -16px var(--shadow); }
div[data-testid="stVerticalBlockBorderWrapper"] h5 { margin: 0 0 8px; color: var(--primary); }
.stTextInput input, .stTextArea textarea { border-radius: 12px !important; transition: box-shadow .2s, border-color .2s; }
.stTextInput input:hover, .stTextArea textarea:hover { border-color: var(--sky) !important; }
.stTextInput input:focus, .stTextArea textarea:focus { box-shadow: 0 0 0 3px rgba(14,165,233,.4) !important; }

/* ---------- buttons: outlined teal = secondary, orange = the real action ---------- */
.stButton > button, .stDownloadButton > button, [data-testid="stFormSubmitButton"] > button {
  background: #fff; color: var(--primary); border: 1.5px solid #67e8f9; border-radius: 12px; padding: .55rem 1.2rem; font-weight: 700;
  box-shadow: 0 4px 12px -8px var(--shadow); transition: transform .18s ease, box-shadow .18s ease, background .18s, border-color .18s;
}
.stButton > button:hover, .stDownloadButton > button:hover {
  transform: translateY(-2px); background: #ecfeff; border-color: var(--primary2); color: var(--primary); box-shadow: 0 10px 20px -10px var(--shadow);
}
.stButton > button[kind="primary"], .stDownloadButton > button[kind="primary"], [data-testid="stFormSubmitButton"] > button {
  background: linear-gradient(90deg, #ea580c, #f97316, #f59e0b); background-size: 200% 100%; color: #fff; border: 0;
  padding: .65rem 1.4rem; box-shadow: 0 10px 20px -8px rgba(234,88,12,.6); font-size: 1rem;
  transition: transform .18s ease, box-shadow .18s ease, background-position .4s ease;
}
.stButton > button[kind="primary"]:hover, .stDownloadButton > button[kind="primary"]:hover {
  transform: translateY(-3px) scale(1.02); background-position: 100% 0; color: #fff; box-shadow: 0 16px 26px -8px rgba(234,88,12,.7);
}
.stButton > button:active { transform: translateY(0) scale(.98); }
.stButton > button:disabled { background: #e2e8f0 !important; color: #94a3b8 !important; border: 0; box-shadow: none; transform: none; }
[data-testid="stSidebar"] .stButton > button:not([kind="primary"]) { background: rgba(255,255,255,.1); color: #fff; border: 1px solid rgba(255,255,255,.3); }
[data-testid="stSidebar"] .stButton > button:not([kind="primary"]):hover { background: rgba(255,255,255,.22); }

/* ---------- stepper ---------- */
.stepper { display:flex; gap:10px; margin: 0 0 16px; flex-wrap: wrap; }
.step { flex:1; min-width:130px; display:flex; align-items:center; gap:10px; padding:10px 14px; border-radius:14px; background:#fff;
  border:1px solid #e2e8f0; color: var(--muted); font-weight:600; box-shadow:0 4px 12px -8px rgba(0,0,0,.3); transition: transform .18s, box-shadow .18s; }
.step:hover { transform: translateY(-3px); box-shadow: 0 12px 20px -10px var(--shadow); }
.step .num { width:26px; height:26px; border-radius:50%; display:grid; place-items:center; background:#e2e8f0; color:#334155; font-size:.8rem; }
.step.done { color:#166534; border-color:#86efac; background: linear-gradient(90deg,#f0fdf4,#fff); }
.step.done .num { background: var(--ok); color:#fff; }
.step.now { color:#fff; border:0; background: linear-gradient(90deg, var(--primary), var(--primary2), var(--sky)); box-shadow:0 10px 22px -8px var(--shadow); }
.step.now .num { background: rgba(255,255,255,.3); color:#fff; }

/* ---------- tiles ---------- */
.tiles { display:grid; grid-template-columns: repeat(3,1fr); gap:14px; margin: 6px 0 14px; }
.tile { display:flex; align-items:center; gap:14px; padding:14px 18px; border-radius:16px; background: linear-gradient(135deg,#fff,var(--bg2));
  border:1px solid var(--line); border-left: 5px solid var(--accent); box-shadow:0 8px 20px -12px var(--shadow); transition: transform .2s, box-shadow .2s; }
.tile:hover { transform: translateY(-4px); box-shadow: 0 18px 28px -12px var(--shadow); }
.tile .ti { font-size:1.7rem; } .tile .tv { font-size:1.35rem; font-weight:800; color: var(--primary); } .tile .tl { font-size:.78rem; color: var(--muted); }

/* ---------- agent cards ---------- */
.agents { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin: 8px 0 18px; }
@media (max-width: 800px) { .agents, .tiles { grid-template-columns: repeat(2, 1fr); } }
.agent { background: #fff; border-radius: 16px; padding: 16px; border: 1px solid #e2e8f0; text-align: center;
  box-shadow: 0 6px 16px -8px rgba(0,0,0,.25); transition: transform .2s, box-shadow .2s, border-color .2s; }
.agent:hover { transform: translateY(-6px) scale(1.02); box-shadow: 0 20px 32px -10px var(--shadow); border-color: var(--sky); }
.agent .ico { font-size: 1.9rem; } .agent .name { font-weight: 700; margin-top: 4px; color: var(--ink); }
.agent .state { font-size: .8rem; color: var(--muted); margin-top: 2px; }
.agent.working { background: linear-gradient(135deg, #fef3c7, #fde68a); border-color: var(--warn); animation: pulse 1.4s infinite; }
.agent.done { background: linear-gradient(135deg, #dcfce7, #bbf7d0); border-color: var(--ok); }
.agent.fixed { background: linear-gradient(135deg, #fee2e2, #fecaca); border-color: var(--err); }
@keyframes pulse { 0%,100%{box-shadow:0 0 0 0 rgba(245,158,11,.55)} 50%{box-shadow:0 0 0 14px rgba(245,158,11,0)} }

/* ---------- conversation ---------- */
.msg { border-radius: 14px; padding: 12px 16px; margin: 10px 0; border-left: 6px solid var(--primary2); background:#fff;
  box-shadow: 0 6px 16px -8px rgba(0,0,0,.25); transition: transform .18s, box-shadow .18s; animation: pop .35s ease; }
.msg:hover { transform: translateX(5px); box-shadow: 0 14px 26px -10px var(--shadow); }
.msg .who { font-weight: 700; font-size: .85rem; letter-spacing: .03em; margin-bottom: 4px; color: var(--ink); }
.msg pre { white-space: pre-wrap; margin: 0; font-size: .86rem; max-height: 280px; overflow: auto; }
.msg.Planner { border-color: var(--sky); background: linear-gradient(90deg,#e0f2fe,#fff); }
.msg.Coder { border-color: var(--teal); background: linear-gradient(90deg,#ccfbf1,#fff); }
.msg.Executor { border-color: var(--ok); background: linear-gradient(90deg,#dcfce7,#fff); }
.msg.Executor.err { border-color: var(--err); background: linear-gradient(90deg,#fee2e2,#fff); }
.msg.Reviewer { border-color: var(--warn); background: linear-gradient(90deg,#fef3c7,#fff); }
.msg.user { border-color: var(--accent); background: linear-gradient(90deg,#ffedd5,#fff); }
@keyframes pop { from{opacity:0; transform: translateY(8px)} to{opacity:1; transform:none} }

/* ---------- answer ---------- */
.answer { background: linear-gradient(135deg,#f0fdfa,#ecfeff 55%,#fff7ed); border: 1px solid #99f6e4; border-radius: 20px;
  padding: 22px 26px; box-shadow: 0 16px 36px -14px rgba(13,148,136,.5); transition: transform .25s, box-shadow .25s; }
.answer:hover { transform: translateY(-3px); box-shadow: 0 24px 46px -14px rgba(13,148,136,.65); }
.answer h4 { margin: 0 0 6px; color: var(--primary); letter-spacing:.08em; font-size:.82rem; }
.answer p { margin: 0 0 12px; white-space: pre-wrap; color: var(--ink); }
.chips { display:flex; gap:8px; flex-wrap:wrap; margin:6px 0; }
.chip { padding:5px 13px; border-radius:999px; background:linear-gradient(90deg,#cffafe,#ccfbf1); color: var(--primary); font-size:.8rem; font-weight:700;
  box-shadow:0 3px 8px -3px var(--shadow); transition: transform .15s, box-shadow .15s; }
.chip:hover { transform: translateY(-2px) scale(1.05); box-shadow:0 8px 14px -4px var(--shadow); }
[data-testid="stImage"] img { border-radius: 14px; box-shadow: 0 10px 24px -10px rgba(0,0,0,.35); transition: transform .25s, box-shadow .25s; }
[data-testid="stImage"] img:hover { transform: scale(1.03); box-shadow: 0 20px 34px -10px var(--shadow); }

/* ---------- sidebar ---------- */
[data-testid="stSidebar"] [data-baseweb="select"] > div { border-radius: 12px; }
.brand { display:flex; align-items:center; gap:12px; padding:14px; margin-bottom:18px; border-radius:16px;
  background: linear-gradient(135deg, rgba(255,255,255,.16), rgba(255,255,255,.05)); border:1px solid rgba(255,255,255,.18);
  box-shadow: 0 10px 24px -12px rgba(0,0,0,.6); }
.brand .logo { width:44px; height:44px; border-radius:12px; display:grid; place-items:center; font-size:1.5rem;
  background: linear-gradient(135deg, var(--primary), var(--primary2), var(--accent)); box-shadow: 0 8px 16px -6px rgba(249,115,22,.55); }
.brand .bn { font-weight:800; font-size:1.15rem; color:#fff; line-height:1.1; } .brand .bt { font-size:.72rem; opacity:.75; margin-top:2px; }
.sec { font-size:.68rem; letter-spacing:.14em; font-weight:700; opacity:.7; margin: 18px 2px 8px; }
.warnbox { margin:8px 0; padding:10px 12px; border-radius:12px; font-size:.8rem; background:rgba(251,191,36,.18); border:1px solid rgba(251,191,36,.5); }
.warnbox code { background: rgba(0,0,0,.3); padding:1px 5px; border-radius:5px; }
.kv { display:flex; justify-content:space-between; padding:8px 4px; font-size:.82rem; border-bottom:1px dashed rgba(255,255,255,.18); }
.kv span { opacity:.75; } .kv b { color:#fff; }

/* provider cards (buttons): active = teal glow, others = glass */
.st-key-providers button { justify-content: flex-start !important; text-align: left !important; padding: 12px 14px !important;
  border-radius: 14px !important; background: rgba(255,255,255,.07) !important; border: 1px solid rgba(255,255,255,.16) !important;
  box-shadow: none !important; transform: none; transition: transform .18s, background .18s, box-shadow .18s !important; }
.st-key-providers button p { text-align: left; font-size: .85rem; line-height: 1.45; margin: 0; color: #d1faf5; }
.st-key-providers button:hover { transform: translateX(5px) !important; background: rgba(255,255,255,.18) !important;
  box-shadow: 0 10px 20px -10px rgba(0,0,0,.6) !important; filter: none !important; }
.st-key-providers button[kind="primary"] { background: linear-gradient(90deg, rgba(14,165,233,.5), rgba(13,148,136,.45)) !important;
  border: 1px solid #5eead4 !important; box-shadow: 0 0 0 2px rgba(94,234,212,.35), 0 12px 22px -10px rgba(0,0,0,.65) !important; }
.st-key-providers button[kind="primary"] p { color: #fff; }
.st-key-providers [data-testid="stElementContainer"] { margin-bottom: 8px; }

/* ---------- workspace card ---------- */
.st-key-workspace { padding: 6px 10px 10px; }
.st-key-workspace > [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:first-child { border-right: 1px solid var(--line); padding-right: 1.6rem; }
.ph { display:flex; align-items:center; gap:12px; margin-bottom: 10px; }
.ph .pn { width:32px; height:32px; border-radius:50%; display:grid; place-items:center; flex:none; font-weight:800; color:#fff;
  background: linear-gradient(135deg, var(--primary), var(--sky)); box-shadow: 0 6px 14px -6px var(--shadow); }
.ph b { display:block; font-size:1.05rem; color: var(--ink); line-height:1.2; }
.ph small { display:block; color: var(--muted); font-size:.78rem; }
[data-testid="stFileUploaderDropzone"] { border: 2px dashed #38bdf8; border-radius: 16px; padding: 22px 18px;
  background: linear-gradient(135deg, #f0f9ff, #f0fdfa); transition: border-color .2s, box-shadow .2s, transform .2s; }
[data-testid="stFileUploaderDropzone"]:hover { border-color: var(--primary2); box-shadow: 0 10px 24px -12px var(--shadow); transform: translateY(-2px); }
[data-testid="stFileUploaderDropzone"] button { border-radius: 10px; }
.hint { margin-top: 4px; padding: 10px 14px; border-radius: 12px; font-size: .84rem; color: var(--primary);
  background: linear-gradient(90deg, #ecfeff, #fff); border: 1px dashed #67e8f9; }
.hint.warn { color: #92400e; background: #fffbeb; border-color: #fcd34d; }
.st-key-examples button { padding: .3rem .6rem; font-size: .74rem; font-weight: 600; border-radius: 999px;
  background: linear-gradient(90deg, #ecfeff, #f0fdfa); border: 1px solid #99f6e4; box-shadow: none; min-height: 0; }
.st-key-examples button:hover { background: #ccfbf1; transform: translateY(-2px); }
.sech { font-size: .72rem; letter-spacing: .14em; font-weight: 800; color: var(--muted); margin: 4px 2px 2px; text-transform: uppercase; }

.legend { font-size: .7rem; opacity: .75; margin: -2px 2px 10px; }
.works { font-size: .74rem; color: var(--muted); margin: 12px 2px 4px; font-weight: 600; }
.st-key-providers button > div, .st-key-providers button [data-testid="stMarkdownContainer"] { width: 100%; text-align: left !important; justify-content: flex-start !important; }
.st-key-providers button p { white-space: normal; }
.st-key-examples button p { white-space: nowrap; }
[data-testid="stSidebar"] > div:first-child { padding-top: 0; }

.msg .mbody { white-space: pre-wrap; word-break: break-word; font-size: .86rem; line-height: 1.5; max-height: 300px; overflow: auto; }
.msg .mbody.code { font-family: Consolas, "Cascadia Mono", monospace; font-size: .78rem; line-height: 1.45; background: rgba(12,36,48,.05);
  border-radius: 8px; padding: 8px 10px; }
.msg pre { line-height: 1.5; }
.answer p { line-height: 1.55; font-size: .96rem; }
.answer { margin-bottom: 14px; }
.tile { padding: 10px 16px; }
.hero.compact { padding: 12px 22px; margin-bottom: 10px; border-radius: 18px; }
.hero.compact h1 { font-size: 1.35rem; }
.rb-stats { display:flex; gap:8px; flex-wrap:wrap; margin-left:auto; }
.stat { display:inline-flex; align-items:center; gap:6px; padding:6px 13px; border-radius:12px; font-size:.78rem; font-weight:600;
  background:#ecfeff; border:1px solid #99f6e4; color: var(--primary); }
.stat b { font-size:1rem; } .stat i { font-style:normal; }
.stat.ok { background:#dcfce7; border-color:#86efac; color:#166534; }
.stat.run { background:#fef3c7; border-color:#fcd34d; color:#92400e; animation: pulse 1.4s infinite; }
.stat.bad { background:#fee2e2; border-color:#fca5a5; color:#991b1b; }
.errbox { display:flex; flex-direction:column; gap:4px; padding:14px 16px; margin: 6px 0; border-radius:14px; background: linear-gradient(90deg,#fee2e2,#fff);
  border:1px solid #fca5a5; border-left:6px solid var(--err); box-shadow:0 8px 18px -12px rgba(220,38,38,.5); }
.errbox b { color:#991b1b; } .errbox span { color:#7f1d1d; font-size:.9rem; line-height:1.45; }
.runbar { display:flex; align-items:center; gap:22px; flex-wrap:wrap; padding:12px 18px; margin-bottom: 14px; border-radius:16px;
  background: linear-gradient(90deg, #fff, var(--bg2)); border:1px solid var(--line); box-shadow: 0 8px 20px -14px var(--shadow);
  transition: box-shadow .2s, transform .2s; }
.runbar:hover { transform: translateY(-2px); box-shadow: 0 14px 26px -14px var(--shadow); }
.runbar .rb-data { display:flex; align-items:center; gap:10px; padding-right:22px; border-right:1px solid var(--line); }
.runbar .rb-ic { font-size:1.5rem; } .runbar b { display:block; color: var(--ink); font-size:.95rem; line-height:1.2; }
.runbar small { color: var(--muted); font-size:.72rem; display:block; letter-spacing:.04em; }
.runbar .rb-q { flex:1; min-width:240px; } .runbar .rb-q span { display:block; color: var(--ink); font-weight:600; font-size:.95rem; }
.agents.compact .agent { padding: 9px 12px; border-radius: 14px; display:flex; align-items:center; gap:10px; text-align:left; }
.agents.compact .agent .ico { font-size: 1.35rem; } .agents.compact .agent .name { margin: 0; font-size:.92rem; }
.agents.compact .agent .state { margin: 0; font-size:.72rem; } .agents.compact .agent:hover { transform: translateY(-3px); }

a.dl { display:block; text-align:center; padding:.6rem 1.2rem; border-radius:12px; background:#fff; border:1.5px solid #67e8f9; font-weight:700;
  color: var(--primary) !important; text-decoration:none !important; box-shadow:0 4px 12px -8px var(--shadow);
  transition: transform .18s ease, box-shadow .18s ease, background .18s, border-color .18s; }
a.dl:hover { transform: translateY(-2px); background:#ecfeff; border-color: var(--primary2); box-shadow:0 10px 20px -10px var(--shadow); }
</style>
"""
