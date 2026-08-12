# Conjecture Corpora Acquisition Report

Date: 2026-08-12. All JSON files share the shape:
`{"id", "statement_text", "invariants": [tags], "hypotheses", "status", "status_detail", "source_url", "transcription_confidence"}`
(`status_detail` is a deliberate extension carrying attribution/evidence text; `list`/`sublist` extra keys appear only in the WoW II file.)

Raw sources, parsers, and intermediate text are under `raw/`.

---

## Corpus 1 — Graffiti / "Written on the Wall" (WoW I) — `graffiti_wow.json` (587 entries)

**Canonical source found:** Fajtlowicz's own July-2004 edition of *Written on the Wall*
(216 pp., TeX `conj.dvi` → PS/PDF). Provenance chain:
- Craig Larson's UH page `math.uh.edu/~clarson/graffiti.html` (dead; 2004 Wayback capture in `raw/graffiti_2004.html`) hosted `wow-pre-840.ps`, `wow-post-840.ps` and `wow-july2004.ps` — "the list of Conjectures of Graffiti".
- A verbatim PDF of the July-2004 file survives in `github.com/RoucairolMilo/refutation-COCOON2022` (`wow-july2004.pdf`, 907 KB) — downloaded to `raw/`.
- The PDF uses Type-3 bitmap fonts (no text layer); text was recovered by OCR (`ocrmypdf`/tesseract → `raw/wow-ocr.txt`, 355 KB). OCR quality is good for prose, imperfect for math symbols → **transcription_confidence = medium** for nearly all entries.

**Parsing:** numbered blocks (`0.`, `1.`, … `894.`) selected via longest-nondecreasing-subsequence over candidate line starts (WoW numbering is monotone; this rejects Fajtlowicz's dated-comment artifacts like "9. 96."). Each block = statement + Fajtlowicz's follow-up commentary. Status extracted from commentary keywords (proved/refuted/counterexample/open), with two cross-references merged in:
- **A&H 2010 survey Table 6** (Aouchiche–Hansen, LAA 432:2293–2322): per-number status (O/P/R) for 192 spectral WoW conjectures.
- **Roucairol–Cazenave 2024** (arXiv:2409.18626): WoW #197 refuted (open until 2024); notes that #28/#209 refutation sources are lost, #140's refutation could not be located, and 12 of 13 previously-refuted spectral WoW conjectures were re-refuted by search.

**Coverage:** 581 distinct numbers in range 0–894 (~580 of ~900; the file itself states it contains "more than half of Graffiti's conjectures from the original version" — the missing numbers, e.g. 3–27 partially, 117–119, are absent in the source, not lost in parsing; #117–119 are noted by Fajtlowicz as not Graffiti's). Conjectures ≥840 are the Fullerene series. Status tally: 126 refuted / 90 open / 52 proved / 319 unannotated (bare statements with no status note; for spectral ones the survey status was merged where available).

**Gaps:** (i) OCR-garbled math in some statements (marked low/medium); (ii) the pre-1998 "original version" conjectures Fajtlowicz dropped are not recoverable from this file; (iii) DeLaVina's bibliography `wowref` (raw/wowrefintro.htm) maps papers→conjecture numbers but its JS data file wasn't parsed; (iv) `fajtlowicz.pdf` in TxGraffiti_APP (7-page scan, needs OCR) not transcribed.

## Corpus 1b (bonus) — Graffiti.pc / "Written on the Wall II" — `graffiti_pc_wow2.json` (519 entries)

DeLaVina's WoW II site is **live and current** (`cms.uhd.edu/faculty/delavinae/research/wowII/`, last update **2026-08-06**; menu reports 488 Dalmatian + 52 Sophie conjectures; 204 open / 284 resolved). Scraped `all.html`, `open.html`, `resolved.htm`. Status letters: T=theorem/proved (149), F=false/refuted, O=open, R/E=resolved variants (letter kept raw in `status_detail`; exact E/R semantics not documented on-site). Parsed 519 rows (388 distinct numbers 1–459; the same conjecture can appear under several invariant lists — duplicates keep `(2)` suffixes). 218 open, 138 refuted, 163 proved-ish. Confidence high (native HTML). **wow2-309 is present and open** (a γ_t upper bound in terms of even-distance counts). Gap: ~100 of the 540 menu-count conjectures use markup variants my row-pattern missed; `sublist` attribution is approximate.

## Corpus 2 — TxGraffiti / Optimist / CONJECTURING / Graph Brain — `txgraffiti.json` (26 entries)

**Sources acquired:**
- arXiv:2507.17780 (Davila 2025, "Ten Years…"): 4 flagship conjectures labeled "TxGraffiti – Open Since 2016/2017/2020/2023".
- arXiv:2409.19379 ("Automated Conjecturing with TxGraffiti", 2024): 4 open conjectures + 8 proved former conjectures (theorem envs).
- arXiv:2306.12917 ("A Framework for Conjecturing", 2023): 6 conjecture envs + theorems.
- arXiv:2411.09158 ("The Optimist", 2024): conjecture content is session output inside code listings (base64 payloads decoded); only 3 unique generated statements (mostly rediscoveries, tagged `generated`).
- Repos checked (`RandyRDavila/*`: TxGraffiti, TxGraffiti2, TxGraffiti_APP, Linear_TxGraffiti, GraffitiAI, The-Optimist, Pickle_Graffiti, Christy.jl, Conjecturing.jl): they contain **invariant datasets and generator code, no exported conjecture JSON/CSV** — the web app generates conjectures on the fly.
- CONJECTURING project (Larson–Van Cleemput): the Sage database `math1um/objects-invariants-properties` stores invariants/properties/theorems, again no open-conjecture export. The AIJ 2016 paper is paywalled (not on arXiv).
- Graph Brain Project: arXiv:1801.01814 acquired (`raw/graphbrain.md`) — it is a program-manifesto (independence-number case study), not a conjecture list.

13 open / 10 proved / 3 generated; confidence high (LaTeXML HTML; math slightly doubled by unicode+TeX duplication but readable). Invariant vocabulary: alpha, zero_forcing, total_domination, independent domination, matching, residue, annihilation, Randić/harmonic index, cubic/claw-free hypotheses.

**Gaps:** TxGraffiti's full historical conjecture stream (hundreds shown in the web app over the years) is not persisted anywhere public; only the paper-published subset is machine-readable. Davila–Henning proof papers (arXiv 2017–2022) would add ~15 more proved-status entries.

## Corpus 3 — AutoGraphiX (AGX) — `autographix.json` (259 entries)

**Primary source:** Aouchiche & Hansen, *A survey of automated conjectures in spectral graph theory*, LAA 432 (2010) 2293–2322. ScienceDirect blocks datacenter IPs (Cloudflare), GERAD cahier G-2009-18 is login-gated, and the old AGX site's `~agx/file/conjectures.pdf` + `phd.pdf` (Aouchiche thesis) were **never captured** by Wayback — the PDF was finally obtained via **scholar.archive.org's preserved CORE/Elsevier copy** (`raw/agx_survey.pdf`, clean text layer).

**Contents:**
- 18 numbered `Conjecture` environments from the survey (the other numbered statements are Theorems), extracted from `pdftotext -layout` with correct ⩽/⩾ glyphs; statuses from survey text plus post-2010 literature overrides.
- 235 rows from survey **Tables 4–5** = the AGX "Form 1" automated comparison of λ₁ vs. every invariant (from Aouchiche's 2006 thesis / VNS-20 paper): each row carries lower/upper bound, extremal graphs, and status letter (O open / P proved / K known / T trivial / R refuted / N none). Table text is column-wrapped → confidence medium; formulas partially garbled but expression + status are reliable.
- 6 literature-tracked AGX/thesis conjectures with 2021–2023 refutations: λ₁+μ ≥ √(n−1)+1 (Wagner 2021), π+∂_{⌊2D/3⌋}>0 (A&H 2016; refuted), λ₁·π ≤ n−1, a·π ≥ f(n), λ₁−α ≥ √(n−1)−n+1, R+α ≤ n−1+√(n−1) (all refuted by Vito–Stefanus AMCS, arXiv:2306.07956).

70 open / 12 refuted / 54 proved / 98 trivial / 10 known / 14 no-result / 1 partially refuted.

**Gaps:** (i) Aouchiche's thesis annex list (A.1–A.xxx) itself is unrecoverable online (`phd.pdf` never archived) — Tables 4–5 cover its λ₁ chapter only; comparisons for other invariant pairs (energy, distance invariants vs. each other) exist in the VNS paper series (EUDML/GERAD, per-paper, not acquired); (ii) the EJCO 2013 "Open problems on graph eigenvalues studied with AutoGraphiX" update is paywalled (Springer/RG blocked); (iii) `raw/liora_laplacian.pdf` + `raw/duhamel_spectral.pdf` (lamsade, 2025) acquired but not yet folded in as status updates.

---

## Source-quality summary

| corpus | entries | open | confidence | source class |
|---|---|---|---|---|
| graffiti_wow (WoW I, July 2004) | 587 | 90 (+319 unannotated) | medium (OCR) | author's canonical file, mirrored PDF |
| graffiti_pc_wow2 (WoW II) | 519 | 218 | high | live author site, updated 2026-08-06 |
| txgraffiti | 26 | 13 | high | arXiv LaTeXML HTML |
| autographix | 259 | 70 | medium/high | preserved publisher PDF + arXiv |

## Access notes (for reproducibility)
- web.archive.org and export.arxiv.org rate-limit this VPS IP aggressively; Wayback/scholar.archive.org fetches were routed through the Mac (`ssh mac curl ...`).
- ScienceDirect/Springer/ResearchGate Cloudflare-block both the VPS and plain curl from the Mac; scholar.archive.org's CORE Elsevier dump was the only working path to the A&H survey.
