#!/usr/bin/env python3
"""
Renders a small terminal-style "sysinfo" panel: a header bar plus a few
labeled rows, each typing itself in with a short fade/slide delay.
Set PREVIEW=1 to disable the animation for previewing in a plain image viewer.
"""
import os

ROWS = [
    ("role", "CSE Undergrad @ BAIUST"),
    ("focus", "Backend + Cloud-Native Systems"),
    ("stack", "Node.js \u00b7 TypeScript \u00b7 Kubernetes \u00b7 AWS"),
    ("now", "Building a microservice ecommerce platform"),
]

BG = "#0d1117"
BORDER = "#30363d"
HEADER_BG = "#161b22"
LABEL_COLOR = "#4dabf7"
VALUE_COLOR = "#c9d1d9"
DOT_COLORS = ["#ff5f56", "#ffbd2e", "#27c93f"]

WIDTH = 460
ROW_H = 34
HEADER_H = 32
TOP_PAD = 14
PREVIEW = os.environ.get("PREVIEW") == "1"


def esc(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;").replace("\u00b7", "\u00b7"))


def build_svg():
    height = HEADER_H + TOP_PAD + len(ROWS) * ROW_H + 20

    parts = []
    parts.append(
        f'<svg viewBox="0 0 {WIDTH} {height}" width="{WIDTH}" height="{height}" '
        f'xmlns="http://www.w3.org/2000/svg" font-family="Consolas, Menlo, monospace">'
    )
    parts.append(
        f'<rect x="0.5" y="0.5" width="{WIDTH-1}" height="{height-1}" rx="10" '
        f'fill="{BG}" stroke="{BORDER}"/>'
    )
    # header bar with traffic-light dots
    parts.append(f'<rect x="0.5" y="0.5" width="{WIDTH-1}" height="{HEADER_H}" rx="10" fill="{HEADER_BG}"/>')
    parts.append(f'<rect x="0.5" y="{HEADER_H-9}" width="{WIDTH-1}" height="9" fill="{HEADER_BG}"/>')
    for i, c in enumerate(DOT_COLORS):
        parts.append(f'<circle cx="{20 + i*16}" cy="{HEADER_H/2}" r="5" fill="{c}"/>')
    parts.append(
        f'<text x="{WIDTH/2}" y="{HEADER_H/2 + 4}" font-size="11" fill="{VALUE_COLOR}" '
        f'text-anchor="middle">whoami --verbose</text>'
    )

    for i, (label, value) in enumerate(ROWS):
        y = HEADER_H + TOP_PAD + i * ROW_H + 18
        group_attrs = ""
        anim = ""
        if not PREVIEW:
            delay = i * 0.35
            group_attrs = 'opacity="0"'
            anim = (
                f'<animate attributeName="opacity" from="0" to="1" '
                f'begin="{delay:.2f}s" dur="0.4s" fill="freeze"/>'
                f'<animateTransform attributeName="transform" type="translate" '
                f'from="-8 0" to="0 0" begin="{delay:.2f}s" dur="0.4s" fill="freeze"/>'
            )
        parts.append(f'<g {group_attrs}>{anim}'
                      f'<text x="24" y="{y}" font-size="13" fill="{LABEL_COLOR}">{esc(label)}</text>'
                      f'<text x="110" y="{y}" font-size="13" fill="{VALUE_COLOR}">{esc(value)}</text>'
                      f'</g>')

    # blinking cursor at the end
    cursor_y = HEADER_H + TOP_PAD + len(ROWS) * ROW_H + 12
    cursor_delay = len(ROWS) * 0.35 + 0.2
    parts.append(
        f'<text x="24" y="{cursor_y}" font-size="13" fill="{VALUE_COLOR}" opacity="0">'
        f'<animate attributeName="opacity" from="0" to="1" begin="{cursor_delay:.2f}s" dur="0.2s" fill="freeze"/>$ _'
        f'<animate attributeName="opacity" values="1;0;1" dur="1s" begin="{cursor_delay+0.2:.2f}s" repeatCount="indefinite"/>'
        f'</text>'
    )

    parts.append('</svg>')
    return "\n".join(parts)


def main():
    svg = build_svg()
    with open("sysinfo.svg", "w") as f:
        f.write(svg)
    print("Wrote sysinfo.svg" + (" (preview/static mode)" if PREVIEW else ""))


if __name__ == "__main__":
    main()
