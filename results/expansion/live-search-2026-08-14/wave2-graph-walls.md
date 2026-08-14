# Wave-two live graph-scalar wall navigation — 2026-08-14

## Frozen selection and live preflight

This cohort uses only the empirical first-wave outcomes in `graph-scalar.md`
as its selection signal.  WOWII 40, 61, and 133 are the complete eligible set:
each is a finite simple connected-graph declaration, each first-wave minimum
was equality, and each wall arm made a best one-unit improvement which stopped
at equality.  No target whose first wave stayed farther than one unit from the
wall was admitted.

The live upstream `main` ref was resolved independently with `git ls-remote`
and the GitHub commits API as
`b33d8678a28118c95d8d4f60b11faaf39ccff1e6`.  The exact files at that commit
still mark all three theorems `@[category research open]` with `sorry`.
An open-and-closed GitHub issue/PR search found no proof, disproof, or competing
claim for any selected target.  WOWII 40 issue 4702 remains an open status
note (equivalent deficiency form and finite checking through order 11), WOWII
61 appears only in the unrelated open module-reorganization PR 4688, and the
only target-specific WOWII 133 result is closed statement-correction PR 4282.
Thus none was done, closed, or preempted at freeze time.

## Necessary baseline ingestion before mutation

The mutation coordinates were frozen only after recomputing the exact equality
seeds and loading the necessary lower-bound baselines:

| target | exact residual | ingested necessary baseline / equality coordinate |
|---|---|---|
| WOWII 40 | `R40 = f-ceil((p+b+1)/2)` | proved `b+2 <= 2f`; equivalently the still-unpaid coordinate is `p-1 <= 2f-(b+2)`.  The first-wave generic equality `IL~~~r{}w` was recomputed as `(f,b,p)=(4,5,1)`. |
| WOWII 61 | `R61 = f-residue-ceil(diameter/3)` | degree-preserving switches hold the Havel--Hakimi residue fixed; mutations were admitted only after recomputing equality seed `G}u@?_` as `(f,residue,diameter)=(6,4,4)`. |
| WOWII 133 | `R133 = path-radius-(hasC4 ? 1 : floor(avg local-alpha))` | on the C4-present branch the geodesic theorem gives `path >= radius+1`; equality seed `GjnL~g` was recomputed as `(path,radius,correction)=(3,2,1)`. |

Every arm below has one process per target, an identical external hard cap of
60 seconds, and no adaptive transfer of time between targets or arms.  A
negative residual is only a provisional candidate until independent exact
recomputation, database sanity, and a repeated live status audit all pass.

## Incremental attempt ledger

| target | arm | hard budget | completed evaluations | outcome | closest observation |
|---|---|---:|---:|---|---|
| WOWII 40 | `DIRECT_WALL_REPLAY` | 60 s | 45 in 1.577 s | `HOLD_BOUNDED`; 0 crossings, 0 timeouts | residual histogram `{0:38, 1:7}`; minimum 0 at `Il~~~r{}w`, `(f,b,p)=(4,5,1)` |
| WOWII 40 | `NEUTRAL_CORRIDOR` | 60 s | 240 in 5.363 s | `HOLD_BOUNDED`; 0 crossings, 0 timeouts | two-step equality/unit beam, histogram `{0:211, 1:29}`; minimum 0 |
| WOWII 40 | `EQUALITY_RAYS` | 60 s | 66 in 3.147 s | `HOLD_BOUNDED`; 0 crossings, 0 timeouts | false/true twins, edge subdivisions, and leaves; histogram `{0:15, 1:51}`; minimum 0 at `JL~~~r{}{~_`, `(n,f,b,p)=(11,4,5,1)` |
| WOWII 61 | `DIRECT_WALL_REPLAY` | 60 s | 11 in 0.042 s | `HOLD_BOUNDED`; 0 crossings, 0 timeouts | all distinct legal degree-preserving two-switch outputs, histogram `{0:8, 1:3}`; minimum 0 at `Gnu@C?`, `(f,residue,diameter)=(6,4,4)` |
| WOWII 61 | `NEUTRAL_CORRIDOR` | 60 s | 47 in 0.165 s | `HOLD_BOUNDED`; 0 crossings, 0 timeouts | two-switch equality/unit beam, histogram `{0:29, 1:18}`; minimum 0 |
| WOWII 61 | `EQUALITY_RAYS` | 60 s | 32 in 0.221 s | `HOLD_BOUNDED`; 0 crossings, 0 timeouts | false/true twins, edge subdivisions, and leaves; histogram `{0:9, 1:23}`; minimum 0 at `H}u@?b{`, `(n,f,residue,diameter)=(9,6,4,4)` |
| WOWII 133 | `DIRECT_WALL_REPLAY` | 60 s | 28 in 0.313 s | `HOLD_BOUNDED`; 0 crossings, 0 timeouts | all direct one-edge toggles, histogram `{0:4, 1:24}`; minimum 0 at `GjlL~g`, `(path,radius,C4-correction)=(3,2,1)` |
| WOWII 133 | `NEUTRAL_CORRIDOR` | 60 s | 240 in 1.539 s | `HOLD_BOUNDED`; 0 crossings, 0 timeouts | two-step equality/unit beam, histogram `{0:26, 1:199, 2:15}`; minimum 0 |
| WOWII 133 | `EQUALITY_RAYS` | 60 s | 40 in 0.384 s | `HOLD_BOUNDED`; 0 crossings, 0 timeouts | false/true twins, edge subdivisions, and leaves; histogram `{0:12, 1:28}`; minimum 0 at `HjnL~hN`, `(n,path,radius,C4-correction)=(9,3,2,1)` |

The direct arm exhausts the legal first-step neighborhood of the recomputed
seed (one-edge toggles for 40/133, two-switches for 61).  The corridor arm
retains only equality/unit first-step rows and explores their next legal wall
move, capped deterministically at 240 exact rows.  The ray arm applies each
false-twin, true-twin, edge-subdivision, and pendant extension once.  These
choices are consequences of the first-wave observation only: direct wall
moves reached equality but did not cross, so wave two tests neutral traversal
and minimal one-vertex continuations from that equality face.

## Database sanity and independent exact replay

A fresh implementation, sharing no discovery evaluator, exhaustively checked
all 995 connected Graph Atlas graphs on 2--7 vertices plus named controls.  It
used descending vertex-subset enumeration for induced forests, induced
bipartite graphs, neighbourhood independence, and induced paths; an independent
ordinary-path subset DP for path cover; and a separately coded full-zero-suffix
Havel--Hakimi reduction.

| target | Atlas result | named-control result | independent replay of arm extrema |
|---|---|---|---|
| WOWII 40 | 995 rows, minimum 0, 175 equalities, 0 crossings (3.896 s including replay) | 28 rows, minimum 0, 0 crossings | `Il~~~r{}w`: `(n,m,f,b,p,R)=(10,38,4,5,1,0)`; `JL~~~r{}{~_`: `(11,45,4,5,1,0)` |
| WOWII 61 | 995 rows, minimum 0, 151 equalities, 0 crossings (2.215 s including replay) | 60 rows, minimum 0, 0 crossings | `Gnu@C?`: `(n,m,f,residue,diameter,R)=(8,11,6,4,4,0)`; `H}u@?b{`: `(9,17,6,4,4,0)` |
| WOWII 133 | 995 rows, minimum 0, 44 equalities, 0 crossings (3.737 s including replay) | 19 rows, minimum 0, 0 crossings | `GjlL~g`: `(n,m,path,radius,hasC4,floor_l,R)=(8,19,3,2,true,2,0)`; `HjnL~hN`: `(9,25,3,2,true,2,0)` |

The independent replay confirms that every reported closest row is equality,
not a negative candidate.  In particular, WOWII 40 again uses ordinary paths
in its path cover; no induced-path reinterpretation entered this cohort.

## Repeated live issue/PR/commit audit

After all computation and independent replay, the GitHub commits API still
resolved `main` to `b33d8678a28118c95d8d4f60b11faaf39ccff1e6`
(committer timestamp `2026-08-13T23:56:30Z`), matching `git ls-remote`.
Fresh open-and-closed searches and direct object reads showed:

- WOWII 40: issue 4702 is still `OPEN`, last updated
  `2026-08-03T19:20:10Z`; it contains status/finite-verification work, not a
  proof or disproof claim.
- WOWII 61: no target-specific proof/disproof issue or PR exists.  PR 4688 is
  still `OPEN` and unmerged (`mergeStateStatus: DIRTY`), titled only
  `chore: modulize FormalConjectures/`; it does not preempt the target.
- WOWII 133: PR 4282 remains the merged statement correction from 2026-06-17,
  not a resolution.  No later target-specific proof/disproof item was found.

The exact current source files remained `research open` throughout both live
audits.  No done, closed, or preempted target entered an arm.

## Terminal result

`ZERO_COMPLETE_WITHIN_BUDGET`: **3 targets, 9 equal-budget arm processes, 749
mutated exact graph evaluations, 0 crossings, and 0 timeouts.**  Including the
9 mandatory pre-mutation seed recomputations, 3,092 independent database rows,
and 6 independent extremal replays, the cohort made 3,856 exact evaluations.

The empirical result sharpens the first-wave wall observation without crossing
it.  Direct replay, a neutral second step, and four minimal equality rays all
produced additional equality rows, but every apparent improvement again
stopped at residual zero.  Therefore there is no candidate, no novelty claim,
and nothing to promote outward.

No file other than this report was created or edited by this cohort.  No git
add, commit, push, issue, pull request, comment, release, or other outward
action was performed.
