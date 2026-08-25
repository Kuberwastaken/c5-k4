#!/usr/bin/env python3
"""Fetch OEIS declaration files from google-deepmind/formal-conjectures at pinned commit 2411d22e."""
import json
import os
import sys
import time
import urllib.request

COMMIT = "2411d22e"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "upstream_cache")
INVENTORY = "/Users/kuber.mehta/Personal-Projects/c5-k4/results/expansion/open_targets_oeis_erdos_20260815.json"
UA = "OpenAI File Downloader, XaiImageApiFetch/1.0"


def fetch(path):
    url = f"https://raw.githubusercontent.com/google-deepmind/formal-conjectures/{COMMIT}/{path}"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def main():
    ids = sys.argv[1:]
    with open(INVENTORY) as f:
        data = json.load(f)
    paths = {e["id"]: e["path"] for e in data if e["corpus"] == "OEIS"}
    ok = 0
    for i in ids:
        dest = os.path.join(OUT, f"{i}.lean")
        if os.path.exists(dest) and os.path.getsize(dest) > 0:
            ok += 1
            continue
        try:
            blob = fetch(paths[i])
            with open(dest, "wb") as f:
                f.write(blob)
            ok += 1
            print(f"fetched {i} ({len(blob)} bytes)")
        except Exception as exc:
            print(f"FAIL {i}: {exc}")
        time.sleep(0.2)
    print(f"done {ok}/{len(ids)}")


if __name__ == "__main__":
    main()
