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

#### Figure 14 / lower-071 — `RETRO_KILL`

`alpha >= floor(2*tan(matching_number)-2)`, with real-radian `tan`.
Every graph of order at most 10 has matching number at most 5; direct evaluation
for the six integer inputs `0,...,5` gives a right side at most `1`, so the
entire stated small-graph database passes.  `K28` has `alpha=1`, `mu=14`, while
`floor(2*tan(14)-2)=floor(12.489213...)=12`.  The arsenal witness `C7[K4]`
also has `mu=14` (pair within every `K4` fiber) and `alpha=3<12`.  Both are far
outside the `1e-6` guard.  Independent library evaluation and structural
matching/independence proofs agree; see the executable certificate.  This is a
stale retro-kill of a still-open-as-posted line, not a novelty claim.

#### Figure 14 / lower-082 — `RETRO_KILL`

`alpha >= floor(log(tan(order)^2)/log(10))`, using the program's ordinary
real-radian `tan` and natural `log` (the quotient makes the logarithm base
irrelevant).  Direct evaluation for every order `2,...,10` gives a right side
at most `1`, so every nonempty connected graph in the stated database passes.
At order 11, however, `K11` has `alpha=1` but right side
`floor(4.708027945...)=4`.  The carrier-family witness `C5[K11]` has order 55,
`alpha=2`, and right side `floor(3.309951816...)=3`.  Both evaluations are far
outside the `1e-6` integer-boundary guard and independently reproduce.  This
is a stale retro-kill of a still-open-as-posted line, not a novelty claim; see
the executable certificate.

#### Paper worked conjecture 2 — `HOLD_ARSENAL`

The paper separately states `alpha <= average_distance^degree_sum`, defining
degree sum as the sum of all vertex degrees.  For `C5[K4]`, average distance
over unordered distinct pairs is exactly `(110 + 2*80)/190 = 27/19`, and the
degree sum is `20*11=220`.  Thus the right side is `(27/19)^220`, vastly above
`alpha=2`.  Computing in the logarithmic domain independently confirms the
comparison.  No named-arsenal violation was found.

### Bounded-set summary

All **9/9** compact conjectures printed in Figure 14 and the paper's second
worked conjecture have now been evaluated: **7 `HOLD_ARSENAL`, 2
`RETRO_KILL`**, and the worked upper bound `HOLD_ARSENAL` (10 explicit
statements total).  The two kills are lower-071 and lower-082 above.  The
remaining 219 exact issue lines are retained in the corpus for subsequent
mechanical evaluation; missing or nonstandard invariant semantics must be
reported as `SKIP_UNDEFINED`, not guessed.

## Graph Brain Hamiltonicity paper

The author-hosted primary PDF [*New Conditions for Graph Hamiltonicity*](https://math1um.github.io/Research/r31.pdf)
has a clean nine-page text layer (no OCR gaps or encoding warnings).  It gives
Conjectures 7--12 explicitly.  I transcribed the six rows into
`corpora/graphbrain_hamiltonicity.json`; Conjecture 8 is marked proved because
the same paper proves it as Theorem 20.

#### Hamiltonicity 7 — `HOLD_ARSENAL`

Every connected bipartite distance-regular graph is conjectured Hamiltonian.
Applicable named controls such as `K3,3`, cubes, and the Heawood graph have
Hamilton cycles.  `C5[K4]` and its complement do not satisfy the full
hypothesis.  No counterexample was found.
