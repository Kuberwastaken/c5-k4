"""Decoder v2: Symbol-font spans + overline complements handled before tag strip."""
import re, html as H

SYM = {"a":"α","b":"β","g":"γ","d":"δ","e":"ε","l":"λ","m":"μ","n":"ν","p":"π",
       "r":"ρ","s":"σ","t":"τ","f":"φ","c":"χ","w":"ω","k":"κ","q":"θ","u":"υ",
       "i":"ι","h":"η","x":"ξ","y":"ψ","z":"ζ","A":"α","B":"β","G":"γ","D":"δ",
       "E":"ε","L":"λ","M":"μ","P":"π","R":"ρ","S":"σ","T":"τ","F":"φ","C":"χ",
       "W":"ω","Q":"θ","K":"κ","£":"≤","³":"≥","Ç":"∩","í":"⊆","Î":"⊆",
       "¹":"≠","»":"⇔","+":"±","¥":"×","Ö":"÷","®":"°","Á":"Ø","Å":"σ",
       "\u00a3":"≤","\u00b3":"≥","\u00c7":"∩","\u00ed":"⊆"}

def fix_mojibake(s):
    for bad, good in [("\u00c2\u00a3", "£"), ("\u00c2\u00b3", "³"), ("\u00c3\u0087", "Ç"), ("\u00c3\u00ad", "í")]:
        s = s.replace(bad, good)
    return s

def _sym_span(m):
    return "".join(SYM.get(ch, ch) for ch in m.group(1))

def decode_v2(raw):
    s = fix_mojibake(raw)
    # symbol font spans (face attribute any case/quote)
    s = re.sub(r'<font[^>]*face\s*=\s*"?Symbol"?>*(.*?)</font>', _sym_span, s, flags=re.I | re.S)
    # overline complements -> bar(X)
    s = re.sub(r'<span[^>]*text-decoration:\s*overline[^>]*>(.*?)</span>', r' bar(\1) ', s, flags=re.I | re.S)
    # sub/superscripts: keep content
    s = re.sub(r"<sub>(.*?)</sub>", r"\1", s, flags=re.I | re.S)
    s = re.sub(r"<sup>(.*?)</sup>", r"^\1", s, flags=re.I | re.S)
    s = re.sub(r"<[^>]+>", "", s)
    s = H.unescape(s)
    s = s.replace("\xa0", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s

if __name__ == "__main__":
    import json
    from difflib import SequenceMatcher
    SNAPS = {
        "20100812025246": "/tmp/opencode/wowii_snaps/all_20100812025246.html",
        "20161011143644": "/tmp/opencode/wowii_snaps/all_20161011143644.html",
        "20260723161837": "/tmp/opencode/wowii_snaps/all_20260723161837_clean.html",
    }
    def rows_raw(html):
        out = {}
        for m in re.finditer(r"<[bB]>\s*(\d{1,3}[a-zA-Z]?)\s*\.(?:\s*&nbsp;)?\s*</[bB]>", html):
            cid = m.group(1).lower()
            fwd = html[m.end():]
            em = re.search(r"</tr>", fwd, re.I)
            chunk = fwd[:em.start()] if em else fwd[:4000]
            out.setdefault(cid, chunk)
        return out

    corpus = {str(e["id"]).lower(): e for e in json.load(open("/Users/kuber.mehta/Personal-Projects/c5-k4/data/wowii-conjectures.json"))}

    flagged_total = 0
    for ts, path in SNAPS.items():
        html = open(path, encoding="utf-8", errors="replace").read()
        rr = rows_raw(html)
        n_shared, flags = 0, []
        for cid, raw in rr.items():
            c = corpus.get(cid)
            if not c:
                continue
            n_shared += 1
            snap_txt = decode_v2(raw)
            snap_txt = snap_txt.replace(" definitions", "").strip()
            corp_txt = re.sub(r"\s+", " ", c["statement_text"]).strip()
            r = SequenceMatcher(None, snap_txt.lower(), corp_txt.lower()).ratio()
            if r < 0.97:
                flags.append((cid, r, snap_txt, corp_txt))
        print(f"{ts}: shared={n_shared} flagged={len(flags)}")
        for cid, r, s1, s2 in flags:
            print(f"  [{cid} sim={r:.3f}]")
            print(f"    SNAP: {s1}")
            print(f"    CORP: {s2}")
        flagged_total += len(flags)
        print()
    print("TOTAL FLAGGED:", flagged_total)
