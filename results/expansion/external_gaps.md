# External corpus and archive gap audit

Audit date: **2026-08-12**.  This lane looked beyond the four corpora already
covered by the campaign.  It used primary author pages, archived author pages,
author-project repositories/issues, and primary papers only.

The campaign's normal four gates apply here: source fidelity and DB sanity,
all plausible readings, independent recomputation for any surviving violation,
and a novelty search before any claim.  Spectral comparisons use the existing
`1e-6` guard.  No ILP run in this lane exceeded the 60-second cap.

## Wayback recovery: WoW II 401b, 412f, and 448b

The Wayback CDX index was queried on 2026-08-12 for both historical hostnames,
`cms.dt.uh.edu` and `cms.uhd.edu`.  I compared the earliest capture containing
each conjecture with the 2016 capture already used by the campaign and the
2026 archived/live page.  HTML presentation changed in a few places, but the
normalized statement text did not.

| id | earliest capture containing it | comparison captures | result |
|---|---|---|---|
| 401b | [2010-07-17 `all.html`](https://web.archive.org/web/20100717162629id_/http://cms.uhd.edu/faculty/delavinae/research/wowII/all.html) | [2016-10-11](https://web.archive.org/web/20161011143644id_/http://cms.dt.uh.edu/faculty/delavinae/research/wowII/all.html), [2026-07-26](https://web.archive.org/web/20260726061534id_/http://cms.dt.uh.edu/faculty/delavinae/research/wowII/all.html) | Identical wording from the first post-publication capture onward. |
| 412f | [2010-07-17 `all.html`](https://web.archive.org/web/20100717162629id_/http://cms.uhd.edu/faculty/delavinae/research/wowII/all.html) | [2016-10-11](https://web.archive.org/web/20161011143644id_/http://cms.dt.uh.edu/faculty/delavinae/research/wowII/all.html), [2026-07-26](https://web.archive.org/web/20260726061534id_/http://cms.dt.uh.edu/faculty/delavinae/research/wowII/all.html) | The doubled “then” and unbalanced `G[V-N(P]` are already present in the earliest capture. |
| 448b | [2016-10-11 `all.html`](https://web.archive.org/web/20161011143644id_/http://cms.dt.uh.edu/faculty/delavinae/research/wowII/all.html) (first available capture after its Jan. 2012 posting) | [2026-07-26](https://web.archive.org/web/20260726061534id_/http://cms.dt.uh.edu/faculty/delavinae/research/wowII/all.html) | Identical mathematical wording; `£` is the page's Symbol-font encoding of `≤`, not a later transcription change. |

The archive therefore does **not** recover a cleaner machine output for any of
the three entries:

- **401b remains unusable.**  Its literal `freq[T_max(v)]` and the plausible
  `freq[Tdist_max(v)]` repair fail the DB-sanity gate on connected atlas graphs.
  The first archived wording is exactly the wording already evaluated, so the
  intended denominator cannot be reconstructed from page history.
- **412f remains unusable.**  The first inequality is readable, but on the
  author's empty-set convention it is already refuted by `K3`; the alternative
  repair `G[N(P)]` is atlas-clean and holds on `C5[K4]`.  The archive preserves
  rather than resolves the page error.
- **448b remains unusable.**  The literal page is already refuted by `C4`; the
  atlas-clean `A -> S` repair is only a hypothesis about the lost machine
  output and holds on `C5[K4]`.  No earlier captured wording exists to choose
  between repairs.

Verdict for all three: **`SKIP_SOURCE_CORRUPT`**.  The Wayback follow-up is now
exhausted unless an uncaptured original export or private manuscript surfaces.

## Graph Brain / CONJECTURING source recovery

The 2017 Graph Brain paper does contain an explicit open set.  Its Figure 14
points to [the author-project issue #421](https://github.com/math1um/objects-invariants-properties/issues/421),
“A complete list of open alpha conjectures.”  The issue was opened on
2017-09-07 and remains open; the lower-list body was last updated in 2018.  An
author comment on the same issue supplies the upper-list continuation.

The GitHub API is a clean machine-readable primary source.  I preserved all
**228 exact lines** (89 lower bounds and 139 upper bounds) in
`corpora/graphbrain_open_alpha.json`, with source URL, author-post timestamp,
retrieval date, and a deliberately cautious `open-as-posted` status.  “Issue is
still open” is not treated as proof that every line remains mathematically open.

The primary paper is Bushaw–Larson–Van Cleemput et al.,
[“Automated Conjecturing VII: The Graph Brain Project & Big Mathematics”](https://arxiv.org/abs/1801.01814),
arXiv:1801.01814v1 (2017-12-28).  Its PDF has a clean text layer: 31 pages,
no pages needing OCR, and no encoding warning under `pdf-inspector`.

### Evaluation ledger

Evaluations are appended below one statement at a time.  The first bounded set
is the nine compact lower bounds displayed in Figure 14 plus the paper's second
worked conjecture, the average-distance upper bound.  This avoids pretending
that all 228 syntactically generated expressions have already been audited.

#### Figure 14 / lower-001 — `HOLD_ARSENAL`

`alpha >= min(girth, floor(theta))`.  On `C5[K4]`, `alpha=2`, `girth=3`,
and Lovasz theta is `sqrt(5)=2.236067977...`, so the right side is `2`:
equality.  The primary paper reports exhaustive verification on every
connected graph through order 10 and random testing through order 100.  No
violation appeared on the campaign's named arsenal.

#### Figure 14 / lower-003 — `HOLD_ARSENAL`

`alpha >= min(diameter, theta)`.  On `C5[K4]`, `diameter=2` and
`theta=sqrt(5)`, hence the right side is `2=alpha`.  The named arsenal yielded
no violation; the paper's connected-order-at-most-10 verification covers its
original database.

#### Figure 14 / lower-006 — `HOLD_ARSENAL`

`alpha >= max(residue, theta/2)`.  Havel-Hakimi leaves residue `2` for the
constant degree sequence `(11^20)`, while `theta/2=sqrt(5)/2`; the right side
is therefore `2=alpha(C5[K4])`.  Independent degree-sequence reduction and the
closed-form theta value agree.  No named-arsenal violation was found.

#### Figure 14 / lower-008 — `HOLD_ARSENAL`

`alpha >= 2*floor(arccosh(theta))`, with real `arccosh`.  For
`theta(C5[K4])=sqrt(5)`, the right side is `2*floor(1.4436...)=2`, again
equality.  The value is far outside the `1e-6` boundary guard, and the named
arsenal produced no violation.

#### Figure 14 / lower-009 — `HOLD_ARSENAL`

`alpha >= floor(arccosh(theta))^2`.  On `C5[K4]` the right side is
`floor(1.4436...)^2=1`, below `alpha=2`.  This is also outside the numerical
guard band.  No named-arsenal violation was found.

#### Figure 14 / lower-013 — `HOLD_ARSENAL`

`alpha >= ceil(theta)-radius`.  On `C5[K4]`, this is
`2 >= ceil(sqrt(5))-2 = 1`.  The closed form avoids spectral rounding, and no
named-arsenal violation was found.

#### Figure 14 / lower-014 — `HOLD_ARSENAL`

`alpha >= ceil(theta)-girth`.  On `C5[K4]`, the right side is
`ceil(sqrt(5))-3=0`, so the inequality has slack `2`.  No named-arsenal
violation was found.
