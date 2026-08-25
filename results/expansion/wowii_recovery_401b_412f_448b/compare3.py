"""Decoder v3 + canonicalized full-corpus comparison."""
import re, json, html as H
from difflib import SequenceMatcher

SYM = {"a":"α","b":"β","g":"γ","d":"δ","e":"ε","l":"λ","m":"μ","n":"ν","p":"π",
       "r":"ρ","s":"σ","t":"τ","f":"φ","c":"χ","w":"ω","k":"κ","q":"θ","u":"υ",
       "i":"ι","h":"η","x":"ξ","y":"ψ","z":"ζ",
       "A":"Α","B":"Β","C":"Χ","D":"Δ","E":"Ε","F":"Φ","G":"Γ","H":"Η","I":"Ι",
       "J":"ϑ","K":"Κ","L":"Λ","M":"Μ","N":"Ν","O":"Ο","P":"Π","Q":"Θ","R":"Ρ",
       "S":"Σ","T":"Τ","U":"Υ","V":"ς","W":"Ω","X":"Ξ","Y":"Ψ","Z":"Ζ",
       "£":"≤","³":"≥","Ç":"∩","í":"⊆","Î":"⊆","¹":"≠","+":"±","¥":"×","Ö":"÷",
       "®":"°","Á":"Ø","\u00a3":"≤","\u00b3":"≥","\u00c7":"∩","\u00ed":"⊆"}

def fix_mojibake(s):
    for bad, good in [("\u00c2\u00a3","£"),("\u00c2\u00b3","³"),("\u00c3\u0087","Ç"),("\u00c3\u00ad","í")]:
        s = s.replace(bad, good)
    return s

def decode_v3(raw):
    s = fix_mojibake(raw)
    s = re.sub(r'<font[^>]*face\s*=\s*"?Symbol"?>*(.*?)</font>', lambda m: "".join(SYM.get(ch,ch) for ch in m.group(1)), s, flags=re.I|re.S)
    s = re.sub(r'<span[^>]*text-decoration:\s*overline[^>]*>(.*?)</span>', r' bar(\1) ', s, flags=re.I|re.S)
    s = re.sub(r"<sub>(.*?)</sub>", r"\1", s, flags=re.I|re.S)
    s = re.sub(r"<sup>(.*?)</sup>", r"^\1", s, flags=re.I|re.S)
    s = re.sub(r"<[^>]+>", "", s)
    s = H.unescape(s).replace("\xa0"," ")
    return re.sub(r"\s+"," ",s).strip()

def canon(s):
    s = s.replace(" definitions","").replace(" reference","")
    s = re.sub(r"\b(definitions|reference)\b","",s)
    s = s.replace("_","").replace(" ","").replace("\u2009","")
    return s

def rows_raw(html):
    out={}
    for m in re.finditer(r"<[bB]>\s*(\d{1,3}[a-zA-Z]?)\s*\.(?:\s*&nbsp;)?\s*</[bB]>",html):
        cid=m.group(1).lower()
        fwd=html[m.end():]; em=re.search(r"</tr>",fwd,re.I)
        out.setdefault(cid, fwd[:em.start()] if em else fwd[:4000])
    return out

SNAPS={"2010":"/tmp/opencode/wowii_snaps/all_20100812025246.html",
       "2016":"/tmp/opencode/wowii_snaps/all_20161011143644.html",
       "2026":"/tmp/opencode/wowii_snaps/all_20260723161837_clean.html"}
corpus={str(e["id"]).lower():e for e in json.load(open("/Users/kuber.mehta/Personal-Projects/c5-k4/data/wowii-conjectures.json"))}

for label,path in SNAPS.items():
    html=open(path,encoding="utf-8",errors="replace").read()
    rr=rows_raw(html); n=0; flags=[]
    for cid,raw in rr.items():
        c=corpus.get(cid)
        if not c: continue
        n+=1
        s1=canon(decode_v3(raw)); s2=canon(c["statement_text"])
        r=SequenceMatcher(None,s1,s2).ratio()
        if r<0.97: flags.append((cid,r,s1,s2))
    print(f"{label}: shared={n} flagged={len(flags)}")
    for cid,r,s1,s2 in flags:
        print(f"  [{cid} sim={r:.3f}]")
        print(f"    SNAP: {s1}")
        print(f"    CORP: {s2}")
    print()
