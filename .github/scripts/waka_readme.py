#!/usr/bin/env python3
"""Update the WakaTime section of README.md using only the WakaTime API.

Needs WAKATIME_API_KEY and the workflow built-in GITHUB_TOKEN (git push).
"""
import json
import os
import re
import subprocess
import urllib.error
import urllib.request
from datetime import datetime, timezone

README = "README.md"
START = "<!--START_SECTION:waka-->"
END = "<!--END_SECTION:waka-->"
TIMEZONE_LABEL = "Asia/Hong_Kong"
API = "https://wakatime.com/api/v1/users/current/stats/last_7_days"
BAR_WIDTH = 25
FULL = chr(0x2588)
LIGHT = chr(0x2591)


def fetch_stats():
    key = os.environ.get("WAKATIME_API_KEY", "")
    print("key_len=%d" % len(key))
    url = API + "?api_key=" + key
    req = urllib.request.Request(url, headers={"User-Agent": "waka-readme-script"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.load(resp)["data"]
    except urllib.error.HTTPError as exc:
        print("HTTP %s: %s" % (exc.code, exc.read()[:400].decode("utf-8", "replace")))
        raise


def duration(total_seconds):
    seconds = int(total_seconds or 0)
    hours, minutes = seconds // 3600, (seconds % 3600) // 60
    if hours:
        return "%d hrs %d mins" % (hours, minutes)
    if minutes:
        return "%d mins" % minutes
    return "%d secs" % seconds


def bar(percent):
    filled = round(max(0.0, min(100.0, float(percent or 0))) / 100 * BAR_WIDTH)
    return FULL * filled + LIGHT * (BAR_WIDTH - filled)


def rows(items):
    lines = []
    for item in (items or [])[:8]:
        name = (item.get("name") or "Other")[:25]
        pct = float(item.get("percent") or 0)
        lines.append("%-25s %-19s %s   %6.2f %% " % (name, duration(item.get("total_seconds")), bar(pct), pct))
    return lines


def render(data):
    langs = rows(data.get("languages"))
    editors = rows(data.get("editors"))
    oses = rows(data.get("operating_systems"))
    now = datetime.now(timezone.utc).strftime("%m/%d/%Y %H:%M:%S UTC")
    if not langs:
        return "No coding activity recorded in the last 7 days."
    clock = chr(0x1F551) + chr(0xFE0E)
    speech = chr(0x1F4AC)
    fire = chr(0x1F525)
    computer = chr(0x1F4BB)
    chart = chr(0x1F4CA)
    fence = chr(96) * 3
    parts = [chart + " **This Week I Spent My Time On**", "", fence + "text"]
    parts.append(clock + " Time Zone: " + TIMEZONE_LABEL)
    parts.append("")
    if langs:
        parts.append(speech + " Programming Languages: ")
        parts.extend(langs)
        parts.append("")
    if editors:
        parts.append(fire + " Editors: ")
        parts.extend(editors)
        parts.append("")
    if oses:
        parts.append(computer + " Operating System: ")
        parts.extend(oses)
    parts.append(fence)
    parts.append("")
    parts.append(" Last Updated on " + now)
    return "\n".join(parts)


def main():
    text = render(fetch_stats())
    with open(README, encoding="utf-8") as fh:
        content = fh.read()
    if START not in content or END not in content:
        raise SystemExit("README markers not found")
    pattern = re.escape(START) + r".*?" + re.escape(END)
    new = re.sub(pattern, START + "\n" + text + "\n" + END, content, flags=re.S)
    if new == content:
        print("README already up to date")
        return
    with open(README, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(new)
    subprocess.run(["git", "config", "user.name", "github-actions[bot]"], check=True)
    subprocess.run(["git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com"], check=True)
    subprocess.run(["git", "add", README], check=True)
    subprocess.run(["git", "commit", "-m", "Update waka metrics"], check=True)
    subprocess.run(["git", "push"], check=True)


if __name__ == "__main__":
    main()
