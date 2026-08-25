#!/usr/bin/env python3
"""Fetch OEIS source pages (gate a: primary source recovery)."""
import os
import sys
import time
import urllib.request

UA = "OpenAI File Downloader, XaiImageApiFetch/1.0"
OUT = "/Users/kuber.mehta/Personal-Projects/c5-k4/results/expansion/oeis2_20260826/oeis_pages"
os.makedirs(OUT, exist_ok=True)


def fetch(a):
    url = f"https://oeis.org/A{a}/internal"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


for a in sys.argv[1:]:
    dest = os.path.join(OUT, f"A{a}.html")
    if os.path.exists(dest):
        continue
    try:
        html = fetch(a)
        with open(dest, "w") as f:
            f.write(html)
        print(f"fetched A{a} ({len(html)} bytes)")
    except Exception as exc:
        print(f"FAIL A{a}: {exc}")
    time.sleep(1.0)
