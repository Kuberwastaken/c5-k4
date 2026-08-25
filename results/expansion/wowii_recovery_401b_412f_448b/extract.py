import re, html as H

def decode(s):
    s = re.sub(r"<[^>]+>", "", s)
    s = H.unescape(s)
    return re.sub(r"\s+", " ", s).strip()

def extract(html):
    """Return {id_lower: [(marker, statement_text), ...]}"""
    out = {}
    # find every bolded conjecture number like <b>412f.</b> or <B>31.&nbsp;</b>
    for m in re.finditer(r"<[bB]>\s*(\d{1,3}[a-zA-Z]?)\s*\.(?:\s*&nbsp;)?\s*</[bB]>", html):
        cid = m.group(1).lower()
        back = html[max(0, m.start()-800):m.start()]
        tds = re.findall(r"<td[^>]*>(.*?)</td>", back, re.S | re.I)
        marker = ""
        for td in reversed(tds):
            txt = re.sub(r"<[^>]+>", "", td).strip()
            if txt:
                marker = txt
                break
        fwd = html[m.end():]
        em = re.search(r"</tr>", fwd, re.I)
        chunk = fwd[:em.start()] if em else fwd[:4000]
        out.setdefault(cid, []).append((marker, decode(chunk)))
    return out

if __name__ == "__main__":
    import sys
    targets = sys.argv[1].split(",")
    for ts in ["20080905162657", "20100812025246", "20161011143644"]:
        html = open(f"/tmp/opencode/wowii_snaps/all_{ts}.html", encoding="utf-8", errors="replace").read()
        rows = extract(html)
        print(f"##### {ts}  ({len(rows)} unique ids)")
        for t in targets:
            hits = rows.get(t.lower()) or []
            if not hits:
                print(f"--- {t}: NOT PRESENT")
            for mk, st in hits:
                print(f"[{ts} | {t} | marker={mk}]")
                print(f"    {st}")
        print()
