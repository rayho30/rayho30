#!/usr/bin/env python3
"""
Pulls the public contribution calendar HTML fragment GitHub serves at
https://github.com/users/<username>/contributions
and turns it into a small JSON summary: per-day counts, current streak,
longest streak, and busiest weekday.

No auth/token needed - this is the same public fragment the profile page uses.
"""
import json
import os
import sys
from datetime import datetime, date
from collections import defaultdict

import httpx
from lxml import html

USERNAME = os.environ.get("GH_USERNAME", "rayho30")
OUT_PATH = os.environ.get("OUT_PATH", "assets/contributions.json")


def fetch_contributions(username: str):
    url = f"https://github.com/users/{username}/contributions"
    headers = {"User-Agent": "Mozilla/5.0 (profile-readme-bot)"}
    with httpx.Client(timeout=20, follow_redirects=True) as client:
        resp = client.get(url, headers=headers)
        resp.raise_for_status()
        return resp.text


def parse_days(fragment_html: str):
    tree = html.fromstring(fragment_html)
    days = []

    # Newer GitHub markup uses <td> or <rect> depending on rollout; handle both.
    cells = tree.xpath('//td[@data-date]') or tree.xpath('//rect[@data-date]') or tree.xpath('//*[@data-date]')

    for cell in cells:
        d = cell.get("data-date")
        if not d:
            continue
        level = cell.get("data-level")
        count_attr = cell.get("data-count")
        if count_attr is not None:
            count = int(count_attr)
        elif level is not None:
            # data-level (0-4) is a fallback when raw count isn't exposed
            count = int(level)
        else:
            # try to parse from tooltip text like "3 contributions on ..."
            tip_id = cell.get("id")
            count = 0
        days.append({"date": d, "count": count, "level": int(level) if level is not None else None})

    days.sort(key=lambda x: x["date"])
    return days


def summarize(days):
    if not days:
        return {"days": [], "current_streak": 0, "longest_streak": 0,
                 "busiest_weekday": None, "total": 0}

    total = sum(d["count"] for d in days)

    # streaks
    longest = cur = 0
    for d in days:
        if d["count"] > 0:
            cur += 1
            longest = max(longest, cur)
        else:
            cur = 0

    current_streak = 0
    for d in reversed(days):
        if d["count"] > 0:
            current_streak += 1
        else:
            break

    weekday_totals = defaultdict(int)
    for d in days:
        wd = datetime.strptime(d["date"], "%Y-%m-%d").strftime("%A")
        weekday_totals[wd] += d["count"]
    busiest = max(weekday_totals, key=weekday_totals.get) if weekday_totals else None

    # normalize levels 0-4 for rendering even if GitHub didn't give data-level
    max_count = max((d["count"] for d in days), default=0) or 1
    for d in days:
        if d["level"] is None:
            if d["count"] == 0:
                d["level"] = 0
            else:
                ratio = d["count"] / max_count
                d["level"] = min(4, max(1, round(ratio * 4)))

    return {
        "days": days,
        "total": total,
        "current_streak": current_streak,
        "longest_streak": longest,
        "busiest_weekday": busiest,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "username": USERNAME,
    }


def main():
    try:
        raw = fetch_contributions(USERNAME)
        days = parse_days(raw)
        if not days:
            raise ValueError("No day cells parsed - GitHub markup may have changed")
        data = summarize(days)
    except Exception as e:
        print(f"[pull_contributions] fetch/parse failed: {e}", file=sys.stderr)
        # Fall back to previous file if it exists, so the workflow doesn't break the graph
        if os.path.exists(OUT_PATH):
            print("[pull_contributions] keeping previous contributions.json", file=sys.stderr)
            return
        data = summarize([])

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Wrote {OUT_PATH}: {data['total']} contributions, "
          f"streak {data['current_streak']} (longest {data['longest_streak']})")


if __name__ == "__main__":
    main()
