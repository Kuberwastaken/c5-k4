import subprocess
UA = "OpenAI File Downloader, XaiImageApiFetch/1.0"
out = "/tmp/opencode/wowii_snaps/all_20260723161837_clean.html"
url = "https://web.archive.org/web/20260723161837id_/http://cms.dt.uh.edu/faculty/delavinae/research/wowII/all.html"
subprocess.run(["curl", "-s", "--compressed", "-A", UA, "--max-time", "180", "-o", out, url])
d = open(out, "rb").read()
t = d.decode("utf-8", "replace")
print("bytes", len(d), "magic", d[:8], "| 412f:", "412f" in t, "| 448b:", "448b" in t, "| 401b:", "401b" in t)
