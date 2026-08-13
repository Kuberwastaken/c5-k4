# WOWII 40 proof ladder: source baseline, exact residual, and the first formal rung

**Date:** 2026-08-13

**Outcome:** proof-extraction note only; no new candidate family, Lean file, or truth claim

**Project snapshot:** `c5-k4` `6b16e1d5c4c0288cd68a5e88c5a95015d3dd7e94`

**Read-only upstream snapshot:** `formal-conjectures` `9a1636c4030039f70cf78b866c216d8b6c5f35b0`

## 1. Frozen statement and provenance

The exact upstream declaration is
`FormalConjectures/WrittenOnTheWallII/GraphConjecture40.lean`:

```lean
namespace WrittenOnTheWallII.GraphConjecture40

open SimpleGraph

variable {α : Type*} [Fintype α] [DecidableEq α] [Nontrivial α]
    (G : SimpleGraph α)

@[category research open, AMS 5]
theorem conjecture40 (h_conn : G.Connected)
    (h_nontrivial : 1 < Fintype.card α) :
    ⌈(((pathCoverNumber G : ℝ) + b G + 1) / 2)⌉ ≤
      G.largestInducedForestSize := by
  sorry
```

The local source record `data/wowii-conjectures.json`, record 40, gives the
same high-confidence reading:

> If `G` is a simple connected graph on more than one vertex, then
> `f(G) >= CEIL[(p(G)+b(G)+1)/2]`.

It is marked open and is in the source section “Lower bounds on the forest
number of simple connected graphs, `f(G)`.” The record also preserves the
author's 2004 note:

> For a connected graph on more than one vertex it is easily shown that
> `f(G) >= b(G)/2 + 1`. Thus, in the special case that path covering is one,
> the result follows.

This note is the source-faithful baseline below. The glossary fixes all three
invariants unambiguously:

- `f(G)` is the order of a largest induced forest;
- `b(G)` is the order of a largest induced bipartite subgraph;
- `p(G)` is the minimum number of pairwise vertex-disjoint paths covering all
  vertices, not the order of a largest induced path.

The upstream status ledger `results/race_sweep.md` recorded issue `#4702` as
an open partial reduction with verification through order 11 and no PR. The
local literature ledger summarizes that reduction as the deficiency form
`ℓ + o >= 2τ + 1`, with the bipartite case reduced to two open lemmas. This
note does not refresh that external status because the present task forbids
browsing.

Classification: **UNAMBIGUOUS, research open at the inspected upstream
snapshot**.

## 2. Exact normalization

Write, as natural numbers,

```text
n = |V(G)|
f = largestInducedForestSize(G)
B = largestInducedBipartiteSubgraphSize(G)
p = pathCoverNumber(G).
```

The upstream real-valued abbreviation `b G` is exactly `(B : ℝ)`. Since all
terms before division by two are integral, the ceiling statement is
equivalent to

```text
p + B + 1 <= 2f.                                      (40-int)
```

Use the signed integer residual

```text
R40(G) = 2f - (p + B + 1).
```

Thus WOWII 40 is exactly `R40(G) >= 0`; no rounding ambiguity remains.

There is a second exact normalization. Define

```text
τ = n - f   (minimum feedback-vertex deletion number),
o = n - B   (minimum odd-cycle deletion number),
ℓ = n - p   (maximum edge count of a spanning linear forest).
```

The last identity uses the standard bijection: a cover by `p` vertex-disjoint
paths has `n-p` edges, and the components of a spanning linear forest are a
path cover. Substitution gives

```text
R40(G) = ℓ + o - 2τ - 1,
```

so the conjecture is exactly

```text
ℓ + o >= 2τ + 1.                                     (40-def)
```

This agrees with the independently recorded partial-reduction form in
`results/literature.md`.

## 3. Subtracting the known basic wall

For a connected nontrivial graph, a largest induced bipartite subgraph has a
two-colouring with a colour class of size at least `ceil(B/2)`. That colour
class is independent. Adding one vertex outside it produces an induced star
plus isolated vertices, hence an induced forest. Connectedness and
nontriviality ensure that such a vertex exists. Therefore

```text
f >= ceil(B/2) + 1,
2f >= B + 2.                                         (source baseline)
```

This is precisely the inequality quoted in the source note. Put

```text
Sbasic(G) = 2f - (B + 2) >= 0.
```

Then the exact residual decomposition is

```text
R40(G) = Sbasic(G) - (p - 1).                        (residual wall)
```

Consequently the traceable case `p=1` is fully absorbed by the source
baseline. The whole unresolved content is:

```text
p - 1 <= Sbasic(G).
```

Other elementary bounds do not close this gap. In particular, Gallai--Milgram
gives `p <= α`, while an independent set plus one vertex gives `f >= α+1`;
these bounds control `p` and `f` separately but do not pay the simultaneous
`B` term in `(40-int)`.

## 4. What the frozen ledgers say

The earlier sweep did not isolate a counterexample direction:

- `results/open_sweep/batch0.jsonl` records the carrier `C5[K4]` with
  `(f,p,B)=(4,1,4)`, hence ceiling slack 1 and integer residual
  `R40=2`.
- `results/family_forest.md` records zero violations on all 30 frozen family
  members. Every complete or independent cycle blow-up in that ledger is
  traceable, so it lies entirely in the already-explained `p=1` slice.
- Its closest listed non-traceable controls also hold: `Kneser(6,2)` has
  `(f,p,B)=(7,3,9)` and ceiling slack 1; Heawood has `(10,7,14)` and slack 2;
  Möbius--Kantor has `(11,8,16)` and slack 2.
- `results/race_sweep.md` and `results/literature.md` already warn that this is
  an active partial-proof lane, not an unclaimed candidate-search target.

This is a `THEOREM_SIGNAL` only. A bounded hold is not evidence of a proof.

## 5. Source-faithful lemma ladder

### Rung 0 — expose witnesses for the three optimization definitions

The present proof APIs are definition-heavy:

- `PathCover.lean` defines `IsPathCover` and `pathCoverNumber` by an `sInf`, but
  provides no attainment or comparison lemmas;
- `Induced.lean` defines `largestInducedForestSize` and
  `largestInducedBipartiteSubgraphSize` by `sSup`;
- only the bipartite invariant currently has a computable-equality theorem;
  there is no corresponding forest witness theorem and no theorem connecting
  path covers to spanning linear forests.

Before attacking the residual, a Lean development will need finite-attainment
lemmas of the following forms:

```text
IsPathCover G P              -> pathCoverNumber G <= P.card
(G.induce s).IsAcyclic       -> s.card <= largestInducedForestSize G
(G.induce s).IsBipartite     -> s.card <= largestInducedBipartiteSubgraphSize G
```

and converses supplying optimizing witnesses. These are finite-order API
bridges, not new graph theory.

### Rung 1 — formalize the source baseline

This is the first campaign-worthy, Lean-formalizable, true rung. Its exact
proposed signature is:

```lean
lemma largestInducedBipartiteSubgraphSize_add_two_le_two_mul_forestSize
    {α : Type*} [Fintype α] [DecidableEq α] [Nontrivial α]
    (G : SimpleGraph α) (h_conn : G.Connected)
    (h_nontrivial : 1 < Fintype.card α) :
    G.largestInducedBipartiteSubgraphSize + 2 ≤
      2 * G.largestInducedForestSize := by
  -- extract a maximum bipartite witness;
  -- take its larger colour class I;
  -- choose v outside I using connectedness/nontriviality;
  -- prove G.induce (I ∪ {v}) acyclic;
  -- compare cardinalities and discharge Nat arithmetic.
```

No stronger existing theorem was found in the inspected local APIs. This rung
should be proved before introducing deficiency parameters: it certifies the
source note and removes the complete `p=1` branch.

### Rung 2 — isolate the colour-imbalance easy regime

Let a maximum induced bipartite witness have colour classes `X,Y`, with
`|X| >= |Y|`, and set `d=|X|-|Y|`. The same source construction gives the
forest `X ∪ {v}` of size at least `|X|+1`. Hence

```text
p <= d + 1  ->  p + B + 1 <= 2f.
```

Thus a counterexample, or the remaining proof case, must satisfy

```text
d <= p - 2
```

for every maximum bipartite witness, after ordering its two colour classes by
size. Informally: only nearly balanced maximum bipartite cores with a
genuinely nontrivial path-cover deficiency survive the source argument.

### Rung 3 — certify the optimization dualities

Introduce report-local definitions of feedback deletion `τ`, odd-cycle
deletion `o`, and maximum spanning-linear-forest size `ℓ`, then prove:

```text
f = n - τ,
B = n - o,
p = n - ℓ.
```

The first two are direct complements of induced witnesses. The third requires
the path-cover/linear-forest bijection and is the only one not represented by
an upstream invariant today. These equalities should culminate in a theorem
that rewrites `(40-int)` to `(40-def)` without real casts or ceilings.

### Rung 4 — solve the bipartite core

When `G` is connected, nontrivial, and bipartite, `o=0`; the exact remaining
claim is

```text
ℓ >= 2τ + 1.                                         (BIP)
```

This is the correct structural base case, not merely another numerical lower
bound for `f`. It is also the portion that the local literature ledger says
has only been reduced to open lemmas. A proof should work with a minimum
feedback set and build a spanning linear forest with at least `2τ+1` edges.
For later use on `H=G-O`, which need not be connected, the componentwise form
should be proved at the same time:

```text
ℓ(H) >= 2τ(H) + c+(H),
```

where `c+(H)` is the number of components containing an edge. Additivity
reduces this to `(BIP)` on each nontrivial component; isolated vertices
contribute zero to both `ℓ` and `τ`. A maximum induced bipartite subgraph of a
connected nontrivial graph contains an edge, so its `c+` is at least one.

### Rung 5 — transfer from a maximum bipartite core

Let `O` be a minimum odd-cycle deletion set and `H=G-O`; equivalently, `H` is
a maximum induced bipartite core. Starting from a linear forest in `H`, insert
the vertices of `O` while
tracking the potential

```text
Φ = ℓ - 2τ.
```

The required amortized statement is that the `|O|` insertions lose at most
`|O|` units of this potential, including any surplus supplied by `(BIP)`:

```text
Φ(G) >= 1 - |O|,
```

which is `(40-def)`. The proof must be amortized over the whole core; the
apparently natural pointwise insertion lemma below is false.

### First failure point — do not use pointwise feedback-sensitive insertion

The tempting assertion

```text
τ(J) = τ(J-v)+1  ->  ℓ(J) >= ℓ(J-v)+1
```

fails on frozen control `atlas:99`, graph6 `EQKo`. It is the graph with edges

```text
02, 13, 24, 25, 34, 35
```

(a 4-cycle on `2,4,3,5` with a pendant at each of the opposite vertices
`2,3`). Deleting `4` or `5` leaves a tree. In either case

```text
τ(J)=1,  τ(J-v)=0,  ℓ(J)=4,  ℓ(J-v)=4.
```

The bipartite-core surplus is what saves WOWII 40 on this graph; a proof that
charges every feedback-number drop to a new linear-forest edge discards that
surplus and cannot work. Rung 5 therefore needs a slack-aware exchange or a
block-level augmentation argument.

## 6. Bounded audit of the intermediate rungs

One read-only exact audit was run under `timeout 60s`; it finished in 6.885 s.
It used only the already-frozen controls: all distinct connected Graph Atlas
graphs on 2--7 vertices plus the existing named cycles, `P7`, Petersen,
`K3,3`, `K7`, stars, and complete-bipartite controls. No graph family was
generated or searched.

Exact subset/DP computations gave:

```text
distinct frozen controls                         1008
controls satisfying the bipartite base premise    82
vertex-deletion checks                           6867
violations of ℓ+o >= 2τ+1                           0
violations of (BIP)                                 0
violations of pointwise insertion                   9
```

The first pointwise-insertion failure was `atlas:99` above. These checks
support the normalization and reject one proof route; they do not establish
`(BIP)`, Rung 5, or WOWII 40.

## 7. Recommended next formal step

Create no conjecture-40 proof file until Rung 1's support API has been chosen.
The next implementation unit should contain only:

1. generic upper/lower witness lemmas for the `sSup` induced invariants;
2. an independent-set-plus-one-vertex acyclicity lemma;
3. the exact Rung 1 theorem above;
4. a cast/ceiling arithmetic corollary closing the upstream theorem under
   `pathCoverNumber G = 1`.

That unit would be a genuine, source-certified advance: it formalizes the
author's stated baseline, closes the traceable slice, and leaves the residual
`p-1 <= Sbasic(G)` explicit. The next paper-proof question is then `(BIP)` plus
a slack-aware core-transfer lemma; the failed pointwise insertion must not be
reintroduced under a different name.
