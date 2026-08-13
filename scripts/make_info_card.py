"""
make_info_card.py

Builds a neofetch-style info card SVG: a terminal window frame with
key/value rows (Now, Prev, Stack, Highlights) that fade + slide in
line by line, matching the look of the ASCII portrait's terminal card.

Usage:
    python3 make_info_card.py            # writes info-card.svg
    STATIC=1 python3 make_info_card.py   # writes a frozen frame (no animation)
"""

import html
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "info-card.svg")

WIDTH = 630
PAD = 20
TITLEBAR_H = 30
ROW_H = 34
LABEL_W = 118

BG = "#0d1117"
BG2 = "#111722"
FRAME = "#30363d"
TITLE_TEXT = "#7d8590"
LABEL_COLOR = "#7d8590"
VALUE_COLOR = "#c9d1d9"
ACCENT = "#39d353"

STATIC = bool(os.environ.get("STATIC"))

# ---- Content -------------------------------------------------------

ROWS = [
    ("Now", "Post-bacc coursework @ SMC + job hunting"),
    ("Prev", "B.S. Mathematics, UC Santa Cruz \u201925"),
    ("Stack", "Python \u00b7 Flask \u00b7 Node.js \u00b7 OpenCV \u00b7 C/C++"),
    ("Highlights", [
        "Paris Metro Pathfinder (Flask / Dijkstra & A*)",
        "Rocket Propulsion Simulator (Python)",
        "World Cup 2026 Predictor (Elo / Node.js)",
    ]),
]

# ---- Layout ----------------------------------------------------------

def build_rows():
    """Flatten ROWS into (label, value, is_continuation) lines."""
    lines = []
    for label, value in ROWS:
        if isinstance(value, list):
            lines.append((label, value[0], False))
            for extra in value[1:]:
                lines.append(("", extra, True))
        else:
            lines.append((label, value, False))
    return lines


lines = build_rows()
HEIGHT = TITLEBAR_H + PAD + len(lines) * ROW_H + PAD

STAGGER = 0.18
FADE_DUR = 0.45

parts = []
parts.append(
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" '
    f'viewBox="0 0 {WIDTH} {HEIGHT}" font-family="ui-monospace, SFMono-Regular, '
    f'Menlo, Consolas, monospace">'
)
parts.append(
    '<defs><linearGradient id="bg2" x1="0" y1="0" x2="0" y2="1">'
    f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/>'
    '</linearGradient></defs>'
)
parts.append(f'<rect width="{WIDTH}" height="{HEIGHT}" rx="12" fill="url(#bg2)"/>')
parts.append(
    f'<rect x="0.5" y="0.5" width="{WIDTH-1}" height="{HEIGHT-1}" rx="12" '
    f'fill="none" stroke="{FRAME}" stroke-width="1"/>'
)
parts.append(f'<line x1="0" y1="{TITLEBAR_H}" x2="{WIDTH}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>')
for i, dotcol in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
    parts.append(f'<circle cx="{PAD + i*16}" cy="{TITLEBAR_H/2}" r="5" fill="{dotcol}"/>')
parts.append(
    f'<text x="{WIDTH/2}" y="{TITLEBAR_H/2 + 4}" fill="{TITLE_TEXT}" font-size="12" '
    f'text-anchor="middle">elaine@github: ~$ neofetch</text>'
)

for i, (label, value, is_cont) in enumerate(lines):
    y = TITLEBAR_H + PAD + i * ROW_H + ROW_H * 0.65
    delay = i * STAGGER
    safe_label = html.escape(label)
    safe_value = html.escape(value)

    label_span = ""
    if not is_cont:
        label_span = (
            f'<tspan fill="{ACCENT}" font-weight="600">{safe_label}</tspan>'
            f'<tspan fill="{LABEL_COLOR}">{"." * max(1, 13 - len(label))} </tspan>'
        )
    else:
        label_span = f'<tspan fill="{LABEL_COLOR}">{"".ljust(14)}</tspan>'

    row_group_open = "<g>" if STATIC else (
        f'<g opacity="0">'
        f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.2f}s" '
        f'dur="{FADE_DUR:.2f}s" fill="freeze"/>'
    )
    parts.append(row_group_open)
    parts.append(
        f'<text x="{PAD}" y="{y:.1f}" font-size="14">'
        f'{label_span}<tspan fill="{VALUE_COLOR}">{safe_value}</tspan></text>'
    )
    parts.append('</g>')

parts.append('</svg>')

svg = "".join(parts)
with open(OUT, "w") as f:
    f.write(svg)
print(f"wrote {OUT} ({WIDTH}x{HEIGHT}), {len(lines)} rows")
