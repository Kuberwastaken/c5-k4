import subprocess, time, os
UA = "OpenAI File Downloader, XaiImageApiFetch/1.0"
for ts in ["20100812025516", "20070820172529", "20220121015437"]:
    out = f"/tmp/opencode/wowii_snaps/defs_{ts}.js"
    if os.path.exists(out) and os.path.getsize(out) > 3000:
        print(ts, "cached"); continue
    url = f"https://web.archive.org/web/{ts}id_/http://cms.dt.uh.edu/faculty/delavinae/research/wowII/wowIIdefs.js"
    for a in range(4):
        r = subprocess.run(["curl","-s","--compressed","-A",UA,"--max-time","120","-o",out,"-w","%{http_code}",url],capture_output=True,text=True)
        sz = os.path.getsize(out) if os.path.exists(out) else 0
        if r.stdout.strip()=="200" and sz>3000:
            print(ts,"OK",sz); break
        time.sleep(15*(a+1))
    else:
        print(ts,"FAILED")
    time.sleep(3)
