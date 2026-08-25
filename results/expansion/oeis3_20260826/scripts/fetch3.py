#!/usr/bin/env python3
"""Round 3 fetch: pinned upstream files + OEIS pages + b-files."""
import json
import os
import sys
import time
import urllib.request

COMMIT = "2411d22e"
BASE = "/Users/kuber.mehta/Personal-Projects/c5-k4/results/expansion/oeis3_20260826"
INVENTORY = "/Users/kuber.mehta/Personal-Projects/c5-k4/results/expansion/open_targets_oeis_erdos_20260815.json"
UA = "OpenAI File Downloader, XaiImageApiFetch/1.0"


def get(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def main():
    mode = sys.argv[1]
    ids = sys.argv[2:]
    with open(INVENTORY) as f:
        data = json.load(f)
    paths = {e["id"]: e["path"] for e in data if e["corpus"] == "OEIS"}
    for i in ids:
        try:
            if mode == "lean":
                dest = os.path.join(BASE, "upstream_cache", f"{i}.lean")
                if os.path.exists(dest) and os.path.getsize(dest) > 0:
                    continue
                blob = get(f"https://raw.githubusercontent.com/google-deepmind/formal-conjectures/{COMMIT}/{paths[i]}")
            elif mode == "page":
                dest = os.path.join(BASE, "oeis_pages", f"A{i}.html")
                if os.path.exists(dest):
                    continue
                blob = get(f"https://oeis.org/A{i}/internal").decode("utf-8", "replace").encode()
            else:  # bfile
                dest = os.path.join(BASE, "bfiles", f"bA{i}.txt")
                if os.path.exists(dest):
                    continue
                try:
                    blob = get(f"https://oeis.org/A{i}/bA{i}.txt")
                except Exception as exc:
                    print(f"NO-BFILE A{i}: {exc}")
                    continue
            with open(dest, "wb") as f:
                f.write(blob)
            print(f"fetched {mode} A{i} ({len(blob)} bytes)")
        except Exception as exc:
            print(f"FAIL {mode} A{i}: {exc}")
        time.sleep(0.4)


if __name__ == "__main__":
    main()
