#!/usr/bin/env python3
"""
Reads assets/contributions.json and draws it as an animated grid SVG,
columns (weeks) wiping in one after another, colored with a custom ramp
instead of GitHub's default green.
"""
import json
import os
from datetime import datetime
from collections import defaultdict

DATA_PATH = os.environ.get("DATA_PATH", "assets/contributions.json")
OUT_PATH = os.environ.get("OUT_PATH", "graph.svg")

# index 0 = no activity -> index 4 = top activity tier
LEVELS = ["#1a1a2e", "#16537e", "#1c7ed6", "#4dabf7", "#a5d8ff"]
BG = "#0d1117"
TEXT = "#8b949e"
ACCENT = "#4dabf7"

CELL = 11
GAP = 3
LEFT_PAD = 30
TOP_PAD = 34


def load_data():
    with open(DATA_PATH) as f:
        return json.load(f)


def to_weeks(days):
    """Group day list into columns (weeks), Sun-Sat, like GitHub's calendar."""
    weeks = []
    week = [None] * 7
    if not days:
        return weeks

    first_date = datetime.strptime(days[0]["date"], "%Y-%m-%d")
    # pad the first week so days line up under the correct weekday column
    lead_pad = (first_date.weekday() + 1) % 7  # weekday(): Mon=0 -> want Sun=0
    for i in range(lead_pad):
        week[i] = None

    col = lead_pad
    for d in days:
        dt = datetime.strptime(d["date"], "%Y-%m-%d")
        wd = (dt.weekday() + 1) % 7  # Sun=0 ... Sat=6
        week[wd] = d
        if wd == 6:
            weeks.append(week)
            week = [None] * 7
    if any(x is not None for x in week):
        weeks.append(week)
    return weeks


def month_labels(weeks):
    labels = []
    last_month = None
    for i, week in enumerate(weeks):
        first_real = next((c for c in week if c), None)
        if not first_real:
            continue
        m = datetime.strptime(first_real["date"], "%Y-%m-%d").strftime("%b")
        if m != last_month:
            labels.append((i, m))
            last_month = m
    return labels


def build_svg(data):
    weeks = to_weeks(data.get("days", []))
    n_weeks = len(weeks)
    width = LEFT_PAD + n_weeks * (CELL + GAP) + 20
    height = TOP_PAD + 7 * (CELL + GAP) + 60

    parts = []
    parts.append(
        f'<svg viewBox="0 0 {width} {height}" width="{width}" height="{height}" '
        f'xmlns="http://www.w3.org/2000/svg" font-family="Consolas, Menlo, monospace">'
    )
    parts.append(f'<rect width="100%" height="100%" rx="10" fill="{BG}"/>')

    # month labels
    for col, label in month_labels(weeks):
        x = LEFT_PAD + col * (CELL + GAP)
        parts.append(f'<text x="{x}" y="18" font-size="10" fill="{TEXT}">{label}</text>')

    # weekday labels (Mon, Wed, Fri only, like GitHub)
    weekday_names = {1: "Mon", 3: "Wed", 5: "Fri"}
    for wd, name in weekday_names.items():
        y = TOP_PAD + wd * (CELL + GAP) + CELL - 2
        parts.append(f'<text x="0" y="{y}" font-size="9" fill="{TEXT}">{name}</text>')

    # cells, animated column by column
    total_cols = max(n_weeks, 1)
    for ci, week in enumerate(weeks):
        col_delay = (ci / total_cols) * 1.1  # spread the wave across ~1.1s
        for ri, cell in enumerate(week):
            x = LEFT_PAD + ci * (CELL + GAP)
            y = TOP_PAD + ri * (CELL + GAP)
            level = cell["level"] if cell else 0
            color = LEVELS[min(level, 4)]
            delay = col_delay + ri * 0.02
            parts.append(
                f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" '
                f'fill="{color}" opacity="0">'
                f'<animate attributeName="opacity" from="0" to="1" '
                f'begin="{delay:.2f}s" dur="0.35s" fill="freeze"/>'
                f'</rect>'
            )

    # legend
    legend_y = height - 34
    parts.append(f'<text x="{LEFT_PAD}" y="{legend_y+9}" font-size="9" fill="{TEXT}">Less</text>')
    lx = LEFT_PAD + 30
    for lvl, color in enumerate(LEVELS):
        parts.append(f'<rect x="{lx}" y="{legend_y}" width="{CELL}" height="{CELL}" rx="2" fill="{color}"/>')
        lx += CELL + GAP
    parts.append(f'<text x="{lx+4}" y="{legend_y+9}" font-size="9" fill="{TEXT}">More</text>')

    # stats line
    total = data.get("total", 0)
    streak = data.get("current_streak", 0)
    longest = data.get("longest_streak", 0)
    busiest = data.get("busiest_weekday", "-")
    dot = "\u00b7"
    stats = f"{total} contributions {dot} current streak {streak} {dot} longest {longest} {dot} busiest day {busiest}"
    parts.append(
        f'<text x="{LEFT_PAD}" y="{height-8}" font-size="10" fill="{ACCENT}">{stats}</text>'
    )

    parts.append('</svg>')
    return "\n".join(parts)


def main():
    data = load_data()
    svg = build_svg(data)
    with open(OUT_PATH, "w") as f:
        f.write(svg)
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
