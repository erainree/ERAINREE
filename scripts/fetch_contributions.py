"""
fetch_contributions.py

Fetches your real GitHub contribution calendar with no token needed.
GitHub serves it as public HTML at:
    https://github.com/users/<username>/contributions

This is the same fragment the profile page itself uses. We parse the
day cells with BeautifulSoup and write data/contributions.json with
raw days plus derived stats (current streak, longest streak, best day,
totals).

Usage:
    python3 fetch_contributions.py
Output:
    ../data/contributions.json
"""

import datetime
import json
import os
import re

import requests
from bs4 import BeautifulSoup

USERNAME = "erainree"

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(HERE, "..", "data", "contributions.json")

URL = f"https://github.com/users/{USERNAME}/contributions"


def fetch_html():
    headers = {"User-Agent": "Mozilla/5.0 (profile-readme-bot)"}
    resp = requests.get(URL, headers=headers, timeout=20)
    resp.raise_for_status()
    return resp.text


def parse_days(html):
    soup = BeautifulSoup(html, "html.parser")
    days = []

    # Each day is a <td data-date="..." id="contribution-day-...">.
    # The actual contribution count lives in a separate <tool-tip for="...">
    # element (linked to the td's id), not on the td itself — GitHub only
    # puts a coarse data-level (0-4) on the td.
    tooltip_by_target = {}
    for tip in soup.select("tool-tip[for]"):
        target_id = tip.get("for")
        text = tip.get_text(strip=True)
        tooltip_by_target[target_id] = text

    cells = soup.select("td.ContributionCalendar-day[data-date]")
    for cell in cells:
        date = cell.get("data-date")
        if not date:
            continue

        cell_id = cell.get("id")
        tooltip_text = tooltip_by_target.get(cell_id, "")

        if "No contributions" in tooltip_text:
            count = 0
        else:
            m = re.search(r"(\d+)\s+contribution", tooltip_text)
            if m:
                count = int(m.group(1))
            else:
                # Fall back to the coarse data-level if no tooltip matched
                count = int(cell.get("data-level", 0))

        days.append({"date": date, "count": count})

    days.sort(key=lambda d: d["date"])
    return days


def compute_stats(days):
    total = sum(d["count"] for d in days)

    best_day = max(days, key=lambda d: d["count"]) if days else {"date": None, "count": 0}

    # streaks
    current_streak = 0
    longest_streak = 0
    running = 0
    for d in days:
        if d["count"] > 0:
            running += 1
            longest_streak = max(longest_streak, running)
        else:
            running = 0

    # current streak counts backward from the most recent day with data
    for d in reversed(days):
        if d["count"] > 0:
            current_streak += 1
        else:
            break

    date_range = {
        "start": days[0]["date"] if days else None,
        "end": days[-1]["date"] if days else None,
    }

    return {
        "total_contributions": total,
        "best_day": best_day,
        "current_streak": {"length": current_streak},
        "longest_streak": {"length": longest_streak},
        "range": date_range,
    }


def main():
    html = fetch_html()
    days = parse_days(html)

    if not days:
        raise RuntimeError(
            "No contribution cells found — GitHub's markup may have changed, "
            "or the username/contributions endpoint is unreachable."
        )

    stats = compute_stats(days)
    data = {"days": days, **stats}

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(data, f, indent=2)

    print(f"wrote {OUT_PATH} ({len(days)} days, {stats['total_contributions']} total contributions)")


if __name__ == "__main__":
    main()
