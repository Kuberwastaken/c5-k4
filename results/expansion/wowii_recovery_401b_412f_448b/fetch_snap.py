import subprocess, time, sys, os

UA = "OpenAI File Downloader, XaiImageApiFetch/1.0"
snaps = [
    ("20100812025246", "http://cms.dt.uh.edu/faculty/delavinae/research/wowII/all.html"),
    ("20161011143644", "http://cms.dt.uh.edu/faculty/delavinae/research/wowII/all.html"),
    ("20260723161837", "http://cms.dt.uh.edu/faculty/delavinae/research/wowII/all.html"),
    ("20080905162657", "http://cms.dt.uh.edu/faculty/delavinae/research/wowII/all.html"),
]
for ts, url in snaps:
    out = f"/tmp/opencode/wowii_snaps/all_{ts}.html"
    if os.path.exists(out) and os.path.getsize(out) > 5000:
        print(f"{ts}: cached ({os.path.getsize(out)} bytes)", flush=True); continue
    wurl = f"https://web.archive.org/web/{ts}id_/{url}"
    for attempt in range(5):
        r = subprocess.run(["curl", "-s", "-A", UA, "-w", "%{http_code}", "--max-time", "180",
                            "-o", out, wurl], capture_output=True, text=True)
        code = r.stdout.strip()
        size = os.path.getsize(out) if os.path.exists(out) else 0
        if code == "200" and size > 3000:
            print(f"{ts}: OK {size} bytes", flush=True); break
        print(f"{ts}: attempt {attempt+1} code={code} size={size}; backing off", flush=True)
        if os.path.exists(out): os.remove(out)
        time.sleep(20 * (attempt + 1))
    else:
        print(f"{ts}: FAILED", flush=True)
    time.sleep(5)
