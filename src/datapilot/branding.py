"""White-label the Streamlit shell: browser title and favicon are DataPilot from the first byte (no flash).

Run before the server starts:  python -m datapilot.branding   (run.ps1 and the Dockerfile do this).
Idempotent and safe: a failure only logs a warning, the app still works.
"""
from __future__ import annotations

import logging
import re
from pathlib import Path

TITLE = "DataPilot"
log = logging.getLogger("datapilot.branding")


def make_icon(path: Path, size: int = 192) -> None:
    """Gradient rounded square with a white compass needle."""
    from PIL import Image, ImageDraw

    scale = 4
    s = size * scale
    grad = Image.new("RGB", (s, s))
    px = grad.load()
    stops = [(14, 116, 144), (8, 145, 178), (249, 115, 22)]
    for y in range(s):
        for x in range(s):
            t = (x + y) / (2 * s)
            a, b, u = (stops[0], stops[1], t * 2) if t < .5 else (stops[1], stops[2], (t - .5) * 2)
            px[x, y] = tuple(int(a[i] + (b[i] - a[i]) * u) for i in range(3))
    mask = Image.new("L", (s, s), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, s, s), radius=int(s * .25), fill=255)
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    img.paste(grad, (0, 0), mask)
    d = ImageDraw.Draw(img)
    c = s / 2
    d.polygon([(c, s * .16), (c + s * .15, c + s * .04), (c, c - s * .02), (c - s * .15, c + s * .04)], fill="white")
    d.polygon([(c, s * .84), (c + s * .15, c - s * .04), (c, c + s * .02), (c - s * .15, c - s * .04)], fill=(255, 255, 255, 150))
    img.resize((size, size), Image.LANCZOS).save(path)


ICON_NAME = "datapilot-favicon.png"  # NEW file name on purpose: Streamlit serves static files as "immutable, max-age=1 year",
ICON_VERSION = "2"                    # so a browser that cached the old favicon.png would never re-check it.
ICON_LINKS = (f'<link rel="icon" type="image/png" href="./{ICON_NAME}?v={ICON_VERSION}" />\n'
              f'    <link rel="shortcut icon" href="./{ICON_NAME}?v={ICON_VERSION}" />')


def apply() -> bool:
    try:
        import streamlit

        static = Path(streamlit.__file__).parent / "static"
        index = static / "index.html"
        html = index.read_text(encoding="utf-8")
        new = re.sub(r"<title>.*?</title>", f"<title>{TITLE}</title>", html, count=1, flags=re.S)
        if ICON_NAME not in new:  # swap Streamlit's favicon link for ours (idempotent)
            new = re.sub(r'<link rel="shortcut icon"[^>]*>', ICON_LINKS, new, count=1)
        if new != html:
            index.write_text(new, encoding="utf-8")
        icon = static / ICON_NAME
        if not icon.exists():
            make_icon(icon)
        make_icon(static / "favicon.png") if not (static / ".datapilot_icon_v2").exists() else None
        (static / ".datapilot_icon_v2").write_text("1")
        return True
    except Exception as exc:  # read-only site-packages etc.
        log.warning("Could not apply branding: %s", exc)
        return False


def page_icon():
    """Same icon for st.set_page_config, so the tab icon does not change when Streamlit finishes loading."""
    from PIL import Image

    path = Path(__file__).resolve().parents[2] / "assets" / ICON_NAME
    if not path.exists():
        path.parent.mkdir(exist_ok=True)
        make_icon(path)
    return Image.open(path)


if __name__ == "__main__":
    print("branding applied" if apply() else "branding skipped")
