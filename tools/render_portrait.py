#!/usr/bin/env python3
"""
Downscales assets/photo-ready.png to a character grid, maps brightness to a
glyph ramp, and animates each row drawing in left-to-right via a clipping
rectangle whose width goes 0 -> full, staggered ~40ms per row.

Usage:
    python tools/render_portrait.py
    # writes portrait.svg
"""
import os
from PIL import Image

SRC_PATH = os.environ.get("SRC_PATH", "assets/photo-ready.png")
OUT_PATH = os.environ.get("OUT_PATH", "portrait.svg")

# left = light/empty, right = dense/dark - softer than the usual @%# ramp
GLYPHS = " '.,:;~+*xXO#"

COLS = 70          # character grid width
CHAR_W = 7.2
CHAR_H = 12
ACCENT = "#4dabf7"
BG = "#0d1117"
ROW_STAGGER = 0.04  # seconds between each row starting its draw-in


def load_grid():
    img = Image.open(SRC_PATH).convert("L")
    w, h = img.size
    aspect = h / w
    cols = COLS
    # character cells are taller than wide, correct for that so the portrait
    # doesn't look squashed
    rows = max(1, round(cols * aspect * (CHAR_W / CHAR_H)))
    small = img.resize((cols, rows))
    pixels = list(small.getdata())
    grid = [pixels[r * cols:(r + 1) * cols] for r in range(rows)]
    return grid, cols, rows


def brightness_to_glyph(v):
    # v: 0 (black) .. 255 (white). White background -> should map to empty/light glyph.
    idx = int((255 - v) / 255 * (len(GLYPHS) - 1))
    return GLYPHS[max(0, min(len(GLYPHS) - 1, idx))]


def esc(ch):
    return {"&": "&amp;", "<": "&lt;", ">": "&gt;"}.get(ch, ch)


def build_svg(grid, cols, rows):
    width = cols * CHAR_W + 20
    height = rows * CHAR_H + 20

    parts = []
    parts.append(
        f'<svg viewBox="0 0 {width:.0f} {height:.0f}" width="{width:.0f}" height="{height:.0f}" '
        f'xmlns="http://www.w3.org/2000/svg" font-family="Consolas, Menlo, monospace">'
    )
    parts.append(f'<rect width="100%" height="100%" rx="10" fill="{BG}"/>')

    for r, row in enumerate(grid):
        line = "".join(esc(brightness_to_glyph(v)) for v in row)
        y = 16 + r * CHAR_H
        row_w = cols * CHAR_W
        delay = r * ROW_STAGGER
        clip_id = f"clip{r}"
        # clip rect animates width 0 -> full so the row appears to type/draw in
        parts.append(
            f'<clipPath id="{clip_id}">'
            f'<rect x="10" y="{y-CHAR_H+3:.1f}" height="{CHAR_H}" width="0">'
            f'<animate attributeName="width" from="0" to="{row_w:.1f}" '
            f'begin="{delay:.2f}s" dur="0.5s" fill="freeze" calcMode="spline" '
            f'keySplines="0.3 0 0.2 1"/>'
            f'</rect></clipPath>'
        )
        parts.append(
            f'<text x="10" y="{y:.1f}" font-size="{CHAR_H-2}" fill="{ACCENT}" '
            f'clip-path="url(#{clip_id})" xml:space="preserve">{line}</text>'
        )

    parts.append('</svg>')
    return "\n".join(parts)


def main():
    if not os.path.exists(SRC_PATH):
        print(f"[render_portrait] {SRC_PATH} not found - run clean_photo.py first", file=None)
        raise SystemExit(1)
    grid, cols, rows = load_grid()
    svg = build_svg(grid, cols, rows)
    with open(OUT_PATH, "w") as f:
        f.write(svg)
    print(f"Wrote {OUT_PATH} ({cols}x{rows} chars)")


if __name__ == "__main__":
    main()
