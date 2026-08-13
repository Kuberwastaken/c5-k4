# Method v0.6 prospective selector: no eligible held-out WOWII target

Date: **2026-08-13 UTC**

Current local upstream checkout: `google-deepmind/formal-conjectures`
`9a1636c4030039f70cf78b866c216d8b6c5f35b0`

Selector disposition: **FROZEN, NOT EVALUATED**

Frozen outcome: **`NO_ELIGIBLE_TARGET`**

This is a selection audit only. It constructs and evaluates no graph, computes
no new invariant, authorizes no search, and changes no previously frozen trial.
The requested combination “genuinely held-out” plus “exclude every target
already evaluated in this repository” leaves an empty eligible set. Selecting
exactly one target or family would therefore falsify the provenance record.

## 1. Scope lock

The admissible corpus is restricted to WOWII statements actually represented
by a declaration tagged `@[category research open]` in the current local
`google-deepmind/formal-conjectures` checkout. The Graphify map was used only
to navigate to the deterministic manifest and prior trial records. Eligibility
was then checked directly against the current Lean files and the local source
transcription; the graph map is not a coverage authority.

The following are excluded categorically:

- Written on the Wall I, Graph Brain, TxGraffiti/Optimist, AutoGraphiX, and all
  other corpora not represented by the current WOWII directory;
- released, merged, solved, retro, corrupt, or externally claimed statements;
- every target already evaluated, discussed, ranked, searched, or placed in a
  proof lane anywhere in this repository;
- every graph family, parameter grid, surgery, or transformation already
  constructed or evaluated here.

The last exclusion implements the programme's held-out rule literally:
previous exposure cannot be converted retrospectively into held-out evidence
by choosing a new parameter range.

## 2. Current-manifest audit

At upstream commit `9a1636c4`, the current WOWII directory contains exactly
these 14 open research modules:

```text
19, 40, 59, 61, 100, 133, 141, 145, 146, 160, 198a, 200, 291, 314
```

This is the same WOWII open set recorded in
`results/expansion/formal_conjectures.md`; the newer checkout changes neither
its membership nor the decisive exposure fact. That report's completion audit
states that all 14 were already evaluated source-faithfully in the campaign's
complete 522-entry WOWII sweep and gives their arsenal verdicts. Direct file
search confirms corresponding rows in `results/open_sweep/` and additional
mentions or work products throughout the repository.

The exact current Lean declarations were re-read from the 14 files under
`FormalConjectures/WrittenOnTheWallII/`, rather than inferred from Graphify.
Their target cluster and exclusion are:

| WOWII | current formal target | decisive exclusion |
|---:|---|---|
| 19 | open connected-graph invariant inequality | already evaluated; active status/proof work |
| 40 | induced-forest lower bound using path cover and `b(G)` | already evaluated in the full sweep and later structured ledgers |
| 59 | induced-forest lower bound `ceil(sqrt(residue(G)b(G)))` | already evaluated in the full sweep and forest-family records |
| 61 | induced-forest bound `residue(G)+ceil(diam(G)/3)` | already evaluated; bounded search and active formal proof lane |
| 100 | independence bound using maximum local independence and a complement term | already evaluated; interpretation and upstream-resolution history recorded |
| 133 | induced-path/radius/local-independence bound | already evaluated; bounded search and active formal proof lane |
| 141 | induced-tree/girth/local-independence bound | already evaluated and currently claimed/resolution-tracked |
| 145 | induced-tree/boundary-eccentricity/complement-local-independence bound | already evaluated and currently claimed/resolution-tracked |
| 146 | induced-tree/boundary-eccentricity/square-radius bound | already evaluated and currently claimed/resolution-tracked |
| 160 | spanning-tree-leaf/local-triangle/C4-free bound | already evaluated and currently claimed/resolution-tracked |
| 198a | open connected-graph invariant inequality | already evaluated and currently claimed/resolution-tracked |
| 200 | conditional graph statement | already evaluated; the fixed arsenal was recorded not applicable |
| 291 | open connected-graph invariant inequality | already evaluated and currently claimed/resolution-tracked |
| 314 | triangle-free, induced-path, well-total-domination statement | already evaluated; fixed arsenal result recorded as vacuous hold |

The descriptions above summarize the current formal targets only far enough to
identify the audited declaration. They are not new interpretations and do not
authorize evaluation.

## 3. Residual-wall ranking

The eligible ranked queue is empty:

```text
ranked_eligible_targets = []
```

No residual, equality graph, or transformation score is computed for an
ineligible target. In particular, 59, 61, and 133 might superficially offer
tractable signed residuals, but ranking any of them as a held-out candidate
would ignore their existing sweep, family-search, or proof-lane exposure.
Likewise, attaching a previously unused family to one of the 14 would not make
the target genuinely held out.

Therefore there is no selected target, no selected bounded parameterized
family, no parameter grid, no directional prediction table, and no numerical
calibration under Method v0.6:

```text
selected_target = null
selected_family = null
parameter_bounds = null
grid_authorized = false
```

This is not `HOLD_BOUNDED`, `THEOREM_SHADOW`, or `NOT_APPLICABLE`: none of
those is a selection-stage outcome, and no v0.6 graph was evaluated.

## 4. Frozen execution prerequisites for a future eligible manifest addition

If a later **current** formal-conjectures manifest adds an untouched open WOWII
statement, a new selection document—not an amendment to this one—must freeze
exactly one target and one bounded parameterized family before construction.
That document must include all of the following.

### Database and controls

1. Every connected Graph Atlas graph satisfying the exact hypotheses through
   order seven.
2. `P3`--`P12`, `C3`--`C12`, stars `K1,r` for `2<=r<=10`, complete bipartite
   graphs `K(a,b)` for `1<=a<=b<=6`, complete graphs `K3`--`K10`, Petersen,
   `K3,3`, `K7`, `T(7)`, the carrier, `C5[Ks]` for `1<=s<=8`, and all source-
   named sharpness, theorem, and project controls applicable to that statement.
3. Explicit `NOT_APPLICABLE_HYPOTHESES` or operator-domain records instead of
   invented numerical conventions.
4. At least one hand-derived, statement-specific numerical calibration whose
   convention is replayed literally; endpoint inclusion, complements,
   rounding, and graph powers must be asserted in code rather than narrative
   only.

### Independent exact replay

The primary implementation and independent implementation must differ in
representation and optimization route. Every claimed optimum receives an
explicit witness, direct witness replay, and independent minimality or
maximality certification. Exact graph encoding and every invariant entering
the residual must agree. A disagreement, failed witness, failed calibration,
unexpected control crossing, theorem-baseline violation, or timeout stops the
trial.

### Supervision and durable output

- one graph per fresh externally supervised process;
- internal cancellation at 55 seconds and external hard stop at 60 seconds;
- one JSONL record appended, flushed, and `fsync`ed per graph;
- timeouts recorded only as `TIMEOUT_BRACKET`, never as holds;
- canonical family deduplication while preserving all frozen parameter aliases;
- stop at the first negative residual, followed by independent reproduction of
  the graph encoding, witnesses, controlling terms, and signed residual;
- no adaptive family, bounds, reading, or calibration after any result is seen.

### Mandatory unlock assertions

Before the first prospective-family constructor is callable, the coordinator
must assert programmatically—not infer from a completion marker—that:

```text
manifest SHA and target identity match the selection contract
AND every expected gate index has exactly one admissible final row
AND every applicable hypothesis and operator domain was replayed
AND all witnesses and exact invariants passed independent comparison
AND every theorem baseline is nonnegative
AND every frozen numerical calibration equals its literal expected tuple
AND no gate timeout, error, disagreement, or unexplained crossing exists
AND the independent-gate-complete record precedes every grid record
```

The verifier must independently audit this chronology. A stale completion
marker, matching implementations sharing one mistaken convention, or a
calibration checked only after grid execution cannot unlock a family.

## 5. Frozen outcome

```text
FROZEN_OUTCOME = NO_ELIGIBLE_TARGET
```

The exact rationale is exhaustion by prior exposure: all 14 current open
formal-conjectures WOWII targets were already evaluated in this repository,
and the programme forbids retrospectively calling any inspected target held
out. Method v0.6 therefore freezes no target and no family. The selector may be
reopened only by a later manifest addition that is both open and demonstrably
untouched before its own selection contract is committed.

No graph was constructed or evaluated; no browsing, upstream action, commit,
push, README edit, or existing-file edit was performed.
