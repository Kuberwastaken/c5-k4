# Method v0.1 development log: WOWII 430c / 434c

Date opened: **2026-08-12**. Cluster: independent-domination upper bounds.
Status at opening: **PHASES 0--1 IN PROGRESS; NO SEARCH EVALUATED**.

This is an incremental development log. Predictions and bounds below were
written before evaluating the bounded construction search. A later candidate
does not erase a rejected reading, a database-gate failure, a timeout, or a
zero.

## Phase 0: frozen targets and provenance

Campaign commit at freeze time:
`0287c2eb53eaa29cc2e11aabfc9ba58f5e5ae12e`. Upstream
`google-deepmind/formal-conjectures` `main` was
`547f309edcc2069c1f61c2465729031c10385540`. Neither target yet has a Lean
file/declaration, issue, or PR upstream; this Wave-A task is therefore a
development target for a possible new one-problem formalization, not an
already-present declaration. The live author page is
`http://cms.uhd.edu/faculty/delavinae/research/wowII/open.html`, fetched on
2026-08-12; both rows carry marker `O` and date `Dec. 8 2010`.

### WOWII 430c

The live HTML prints:

```text
Let G be a connected graph on n > 3 vertices and C the center of G. Then
i(G) <= lambda_max(G) * residue(G^2) + Delta(G[M]).
```

The site-wide definitions give `i` as independent domination, `lambda(v)` as
the independence number of `G[N(v)]`, `residue` as the Havel--Hakimi residue,
`G^2` as adjacency at distance at most two, and `M(G)` as the maximum-degree
vertices. The row itself introduces `C` but never defines `M`; this is a real
source defect, not a transcription choice.

Frozen readings:

1. **430c-MAXDEG (gate-preferred):** `M=M(G)`, following the site's global
   convention; `lambda_max` is maximum local independence.
2. **430c-CENTER:** `M=C`, treating the unexplained `M` as a possible copy
   error from the hypothesis.
3. **430c-SPECTRAL (robustness only):** adjacency spectral radius in place of
   local independence. This is not supported by the site's definition of
   `lambda(v)` and cannot establish a source-faithful result.

For readings 1--2, with `Delta_H(S)` the maximum internal degree of `H[S]`,

```text
R_430c(G;S) = lambda_local_max(G) residue(G^2) + Delta_G(S) - i(G).
```

The conjecture holds when `R_430c >= 0`.

### WOWII 434c

The live HTML prints:

```text
Let G be a connected graph on n > 3 vertices and M the set of maximum degree
vertices of G. Then
  i(G) <= delta(G[V-M]) + 1 + SW(G^c).
If delta(G)=1, then
  i(G) <= delta(G[V-M]) + SW(G^c).
```

The live definition of `SW(H)` is "the maximum of minimum degrees over all
subgraphs of H", i.e. degeneracy (without an added one). `delta(G[V-M])` is
the internal minimum degree of the induced subgraph. The source does not state
what happens when `V-M` is empty.

Frozen readings:

1. **434c-ZEROEMPTY (gate-preferred):** `delta(empty)=0`, matching the total
   natural-valued convention used by finite implementations.
2. **434c-NONEMPTY:** the statement is inapplicable when `V-M` is empty.
3. **434c-SWPLUSONE (robustness only):** `SW=degeneracy+1`; this conflicts
   with the source definition but records a common chromatic-bound convention.

Both the general clause and the stronger `delta(G)=1` clause are evaluated.
The source-faithful residuals are

```text
R_434c_general(G) = delta(G[V-M]) + 1 + degeneracy(G^c) - i(G),
R_434c_leaf(G)    = delta(G[V-M])     + degeneracy(G^c) - i(G).
```

## Phase 1: declared database-sanity gate

Before construction search, every frozen source reading will be checked on:

- all 992 connected Graph Atlas graphs of orders 4--7;
- `C5`--`C9`, `P7`, Petersen, `K3,3`, `K7`;
- stars `K1,r` for `2<=r<=7`;
- complete bipartite `Ka,b` for `2<=a<=4` and `a<=b<=5`;
- the 430a witness `P7[K_(1,4,12,19,12,4,1)]` as a cluster control.

Any source-faithful reading contradicted here is rejected as corrupt/erratum,
not promoted as a new disproof. Exact integer arithmetic is used except for the
explicitly non-source spectral robustness reading.

## Preregistered residual prediction

For a positive clique blow-up `Q[s]`:

- `i(Q[s])=i(Q)` is **pinned**;
- maximum local independence is **pinned** by `Q`;
- `residue((Q[s])^2)` is predicted **decreaseable** by making the square's
  weighted degree sequence highly nonuniform;
- `Delta(G[M])` is predicted **decreaseable** to zero if the weighted
  closed-neighborhood sums have a unique maximizer whose blob has weight one;
- `delta(G[V-M])` is predicted **decreaseable** by leaving an isolated
  nonmaximum blob after deleting all maximum-degree blobs;
- `SW(G^c)` is predicted **hard to decrease**, because clique blow-ups become
  independent blobs in the complement. This is the anticipated obstruction
  for 434c.

Thus the prospective 430c crossing condition is a quotient with
`i(Q)>lambda_local_max(Q)`, together with weights forcing square residue one
and `Delta(G[M])=0`. The prospective 434c condition is a quotient with large
`i(Q)` but complement degeneracy at most `i(Q)-2` (or `i(Q)-1` in the leaf
clause), while making `delta(G[V-M])=0`.

The 430a weight vector is only a development seed. No success is predicted
from reusing it unchanged: its large center blob should make
`Delta(G[M])` expensive for 430c, and its complement should make the SW term
expensive for 434c.

## Declared bounded search

1. Gate first; do not search a rejected primary reading.
2. Connected quotient graphs `Q` of order at most 9.
3. Exact positive integer weights, expanded order at most 100.
4. Start with atlas quotients (orders 2--7), then structured/random connected
   quotients of orders 8--9; deduplicate by graph6.
5. Weight trials: uniform weights, the 430a vector where dimension permits,
   coordinate weights `1..8`, random positive compositions, and constraint-led
   candidates for a unique degree-maximizing singleton blob.
6. Every ILP/CBC call has a 60-second wall cap. A timeout records its incumbent
   and bound; it is not a verdict.
7. Stop after 250,000 exact `(Q,s)` evaluations per target or 60 CPU-minutes,
   whichever occurs first.
8. Any apparent hit must be recomputed by an independent expanded-graph
   implementation, with graph6, adjacency, all readings, and an exact term
   table saved here before any novelty claim.

## Incremental outcomes

### Phase 1 completed: database gate

The reusable verifier checked 992 applicable connected Atlas graphs and 25
named/cluster controls.

| reading/clause | minimum residual | gate violations | decision |
|---|---:|---:|---|
| 430c-MAXDEG | 0 | 0 | accepted for bounded search |
| 430c-CENTER | 1 | 0 | retained as ambiguity reading |
| 434c general, source `SW=degeneracy` | 0 | 0 | passes alone |
| 434c `delta(G)=1`, source `SW=degeneracy` | -1 | 14 | **rejected before search** |

The smallest 434c failure is `P4` (`graph6=Ck`):

```text
i(P4)=2,
M = the two internal vertices,
delta(P4[V-M])=0,
SW(P4^c)=degeneracy(P4^c)=1,
so the leaf clause prints 2 <= 1.
```

Its decoded adjacency is
`0:{1,3}, 1:{0,2}, 2:{1}, 3:{0}`. All fourteen rejected-control rows are
preserved by graph6 below; each has `delta(G[V-M])=0`, and each misses by one:

```text
Ck  Db[  E@dW  E]_O  EYOw  En}?  F~`__
FxqgG  FPzs?  F^MGO  FlMgG  FrXwO  F^NI?  Fz~{?
```

All fourteen failures become equality if `SW` is changed to
`degeneracy+1`. That change is not source-faithful: the live definition says
maximum of subgraph minimum degrees, and DeLaVina--Pepper--Waller,
*Graffiti.pc on the Independent-Domination Number of a Graph* (2011), likewise
defines degeneracy as that maximum. The paper was recovered as a text-based
nine-page PDF with no unreadable pages; it discusses the same late-2010
independent-domination query but does not resolve 434c. The `V-M` nonempty
reading does not repair `P4`. Under Method v0.1, 434c is therefore
`CORRUPT_OR_ERRATUM` for the printed leaf clause and its construction search
was pruned. The general clause by itself is not refuted by the gate.

No ILP/CBC call was needed, so there was no optimizer timeout to report.

### Phases 2--6 completed: 430c residual search

The obstruction lower bound

```text
R_430c >= lambda_local_max(Q) - i(Q)
```

shows that a positive clique blow-up can cross only when
`i(Q)>lambda_local_max(Q)`. Of 2,589 generated connected quotients, only 37
survived this exact weight-independent filter:

```text
order 6: 1; order 7: 8; order 8: 8; order 9: 20.
```

Seed `430434` then evaluated 9,997 distinct exact positive weight vectors,
each with expanded order at most 100. The quotient pool contained every
connected Atlas graph through order 7, structured path/cycle/star/complete/
wheel quotients on 8--9 vertices, and 1,200 seeded random connected candidates
at each of orders 8 and 9 before graph6 deduplication. Weight trials contained
uniform, coordinate `2/4/8`, the 430a vector when dimension matched, and exact
positive compositions with totals at most 100.

Outcome: **no 430c crossing under either admitted `M` reading**. The minimum
residual was `+1` for both 430c-MAXDEG and 430c-CENTER. The non-source spectral
robustness convention was not admitted as a historical reading and was not
used to rank candidates.
Representative tight rows were:

| quotient graph6 | weights | i | lambda_max | residue(G^2) | Delta(G[M]) | residual |
|---|---|---:|---:|---:|---:|---:|
| `FhCK?` | `(1,1,1,1,1,2,1)` | 3 | 2 | 2 | 0 | 1 |
| `FhCK?` | `(1,4,1,2,2,1,2)` | 3 | 2 | 2 | 0 | 1 |
| `FhoGG` | `(1,1,2,1,1,1,1)` | 3 | 2 | 2 | 0 | 1 |

The prediction was half successful: weights repeatedly removed the
`Delta(G[M])` correction exactly as intended, but on every best row the square
residue stayed at 2 rather than the required 1. This isolates the next
obstruction as:

```text
i(Q)>lambda_max(Q) and Delta(G[M])=0  ==>  observed residue(G^2)>=2.
```

This is a **THEOREM_SIGNAL**, not a theorem: the implication is only an
observed invariant wall inside the declared bounded construction class.

The unchanged 430a seed behaves as predicted and is not a 430c witness; its
large maximum-degree induced blob contributes a positive correction. No
candidate triggered novelty search or Lean work.

### Phase 7 validation

The discovery formulas were cross-checked on 500 separately expanded random
clique blow-ups. Expanded enumeration independently recomputed `i`, maximum
local independence, the square graph and Havel--Hakimi residue, the
maximum-degree set and its internal degree, and graph6 round trips. All 500
checks passed. `python3 -m py_compile` also passes.

Primary outcomes:

- **430c: `HOLD_BOUNDED`**, minimum residual `+1` over the declared 9,997
  eligible weighted evaluations under both `M=M(G)` and `M=C`; the source
  ambiguity remains recorded.
- **434c: `CORRUPT_OR_ERRATUM`** for the printed minimum-degree-one clause,
  exposed already by `P4`; no construction search was permitted.

Method update learned from this cluster: the database gate must cover each
conditional clause independently, and an exact necessary-condition filter
should precede weight enumeration. The post-result candidate for a future
development iteration is to test or prove the square-residue obstruction;
this suggestion is not part of the preregistered search above.

Reproduction commands:

```bash
python3 scripts/search_wowii_430c_434c.py gate
python3 scripts/search_wowii_430c_434c.py search --limit 250000 --seed 430434
PYTHONDONTWRITEBYTECODE=1 \
  python3 scripts/search_wowii_430c_434c.py selftest --seed 430434
```
