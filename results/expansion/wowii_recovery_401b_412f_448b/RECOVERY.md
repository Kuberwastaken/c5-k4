# WOWII Recovery — original wording of 401b, 412f, 448b from Wayback

Campaign: c5-k4. Date: 2026-08-26. Agent: recovery sweep (Wayback).
Corpus: `data/wowii-conjectures.json`. Question: did DeLaViña's page ever carry
different (non-corrupt) wording for these three entries than what was transcribed?

## Verdict up front

**No differing wording exists.** Every available Wayback snapshot of
`cms.dt.uh.edu/faculty/delavinae/research/wowII/all.html` carries the three
entries byte-identical (modulo cosmetic `printDefinitions(...)` link ids) to the
live-page/corpus wording. The corrupt wording **is** the original published
wording — DeLaViña's own typo/bug, stable since first capture:

| id | dated on page | first capture containing it | wording changed since? |
|----|---------------|------------------------------|------------------------|
| 401b | Jan 2010 | **2010-08-12** (`all.html`) | **NO** (identical raw HTML 2010→2016→2026) |
| 412f | Jun 2010 | **2010-08-12** (`all.html`) | **NO** (identical raw HTML 2010→2016→2026) |
| 448b | Jan 2012 | **2016-10-11** (`all.html`) | **NO** (identical raw HTML 2016→2026) |

Consequence: there is no "repaired original" to hunt. What remains huntable is
only *plausible readings* of the published wording — evaluated per reading in
`EVALUATION.md`.

## Method

1. CDX enumeration (POST-free GET):
   `http://web.archive.org/cdx/search/cdx?url=cms.dt.uh.edu/faculty/delavinae/research/wowII*&output=json&collapse=digest&fl=timestamp,original,statuscode,digest,length`
   → 170 captures (2004–2026). Content pages of interest: `all.html` captures at
   2004-03-28, 2004-05-14, 2004-12-16, 2006-09-05, 2007-08-20, 2008-09-05,
   **2010-08-12**, **2016-10-11**, 2026-07-23 (+2026-07-26); plus early `open.html`
   / `resolved.htm` / dir-index captures.
2. Raw fetches via `https://web.archive.org/web/{ts}id_/...` with UA
   `OpenAI File Downloader, XaiImageApiFetch/1.0`; the 2026 capture needed
   `curl --compressed` (body stored gzip'd). Files cached under
   `/tmp/opencode/wowii_snaps/`.
3. Row extraction: regex over `<td>` marker + `<b>{id}.</b>` + statement cell;
   Symbol-font spans mapped glyph-wise (£→≤ etc.), overline spans reconstructed
   as `bar(X)`; decoded and compared against corpus `statement_text` for **every
   shared id**, per snapshot.

## Snapshots used (URLs)

- `https://web.archive.org/web/20100812025246/http://cms.dt.uh.edu/faculty/delavinae/research/wowII/all.html`
- `https://web.archive.org/web/20161011143644/http://cms.dt.uh.edu/faculty/delavinae/research/wowII/all.html`
- `https://web.archive.org/web/20260723161837/http://cms.dt.uh.edu/faculty/delavinae/research/wowII/all.html`
- (context only) `…/web/20080905162657/…/all.html` — pre-dates all three entries.

## Quoted text per snapshot (decoded; Symbol font restored)

### 401b — identical in 2010-08-12, 2016-10-11, 2026-07-23 (marker O each time)

> Let G be a connected graph on n > 2 vertices. Then γ₂ ≤ FLOOR[3\*Tdist_max /
> freq[T_max(v)]].

Raw (2010): `&#947;<sub>2</sub> ≤ &nbsp;FLOOR[3*Tdist<sub>max </sub>/ freq[T<sub>max</sub>(v)]].`
Sibling 401a (context): `γ₂ ≤ 1+ FLOOR[Tdist_max/disp_avg]` — also stable.

### 412f — identical in 2010-08-12, 2016-10-11, 2026-07-23 (marker O)

> Let G be a connected graph on n > 2 vertices, P the set of pendant vertices
> and H the union of all maximum critical independent sets of G. Then |H| ≥
> μ(G[V−N(P)]), and if G is also bipartite then, then |H| ≥ number of components
> of G[V−N(P] + μ(G[V−N(P)]).

The doubled "then, then" and unbalanced `G[V-N(P]` are on the page in **all**
snapshots — DeLaViña's own typos, not transcription damage.

### 448b — identical in 2016-10-11, 2026-07-23 (marker O); absent from 2010-08-12 ✓ (dated Jan 2012)

> Let G be a connected graph on n > 3 vertices. Then α₂(G) ≤ |V−A| +
> |E(G[N(S)])| + ρ(G), where A is the set of vertices of minimum degree and S is
> the set of support vertices in G.

Raw has Symbol-font `a` (α), `£` (≤), `r` (ρ) exactly as transcribed.

## Diffs vs published corpus

- Cross-snapshot raw-HTML comparison: **zero content differences** for the five
  rows checked (401a, 401b, 412d, 412f, 448b). Only variance: the trailing
  `javascript:printDefinitions(...)` argument (e.g. `1006…` vs `940…`), which is
  page chrome, not statement.
- Whole-corpus scan (423 shared ids @2010, 499 @2016, 499 @2026 vs JSON): after
  proper symbol/overline decoding, **zero genuine statement disagreements**.
  All residual low-similarity flags were extraction artifacts, verified as such:
  - split-anchor rows (`<b>1</b></a><b>31.</b>` = conj **131**) mislabeled by the
    quick extractor — matches `transcription_audit.md` §(a);
  - stripped `<span style="text-decoration: overline">G</span>` complements
    (corpus's `bar(G)` is correct);
  - mojibake around Symbol `£` in some 4xx rows (my decoder, not the page);
  - trailing "definitions"/"reference" link words.
- Opportunistic invariant-name audit requested by orchestrator: **no entry found
  where snapshot wording disagrees with `wowii-conjectures.json`** beyond the
  above artifacts. The corpus's Greek-letter restorations (λ, μ, γ_t, Δ, χ_…)
  are confirmed faithful in all three eras.

## Interpretation

HANDOFF's hypothesis — that stars/K₃/C₄ violating these entries means the
published wording cannot be what Graffiti.pc tested — can no longer be explained
by later corruption of the page. The wording was born corrupt (or Graffiti.pc's
internal semantics for one of these symbols differed from the definitions page —
unknowable from public artifacts; see EVALUATION.md reading analysis).

Per-reading evaluation continues in `EVALUATION.md`.
