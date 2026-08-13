# Graph pebbling product declaration — Phase 0 source/status contract

Frozen: **2026-08-13 UTC**
Scope: **Phase 0 only; no development-family or pebbling-state evaluation**

## Exact current source

- Repository: `google-deepmind/formal-conjectures`.
- Refreshed commit: `d16e05aded22b8c467a0a27c14b2311f53185006`.
- File: `FormalConjectures/Wikipedia/PebblingNumberConjecture.lean`.
- Blob: `200b127f9d93460d9a82e85c0036b931a0442d84`.
- Declaration: `PebblingNumberConjecture.pebbling_number_conjecture`.
- Category: `@[category research open, AMS 5]`.
- Immutable source URL:
  `https://github.com/google-deepmind/formal-conjectures/blob/d16e05aded22b8c467a0a27c14b2311f53185006/FormalConjectures/Wikipedia/PebblingNumberConjecture.lean`.

The literal statement is: for finite connected simple graphs `G` and `H` on
possibly different finite vertex types,

```text
PebblingNumber (G □ H) <= PebblingNumber G * PebblingNumber H.
```

Here `□` is mathlib's Cartesian/box product. `PebblingNumber G` is the least
natural `n` such that every distribution with **exactly** `n` pebbles and
every root has a reachable distribution placing at least one pebble on that
root. A move removes two pebbles at one vertex and adds one at an adjacent
vertex; reachability is the reflexive transitive closure of these moves.

## Reading classification

Classification: **`UNAMBIGUOUS`** for the current Lean declaration.

The exact-`n` formulation agrees with the ordinary finite connected pebbling
number: solvability is monotone under adding unused pebbles, so an
at-least-`n` distribution contains an exactly-`n` subdistribution whose move
sequence remains legal. Zero moves are allowed by reflexivity. The two factor
types are now independent and both connectedness hypotheses are explicit.

Closed issue #4516 records why those last two details matter: an earlier
formal declaration used one shared vertex type and omitted connectedness.
The current source has the corrected domain, so the obsolete reading is not
retained as a competing target.

## Local-repository coverage gate

The project previously listed this declaration in the 77-declaration source
sweep and ranked the graph-pebbling cluster third in a later current-target
audit. Both records explicitly excluded it from fixed-arsenal evaluation.
There is no local pebbling evaluator, product trial, theorem, counterexample,
or prior development-family row. The source module itself proves only

```text
PebblingNumber (completeGraph V) = |V|.
```

That is a factor calibration, not a proof of the product declaration.

## Live issue, PR, and literature gate

Exact GitHub searches on 2026-08-13 found:

- issue #4516, **closed** on 2026-07-22 after the factor-domain correction;
- zero open PRs matching `pebbling` or `pebbling_number_conjecture`;
- zero closed PR search hits under those exact terms;
- no issue or PR claiming a proof or counterexample to the current theorem.

Primary-source status remains open. Asplund--Hurlbert--Kenter (arXiv:1801.07808)
prove the universal bounds

```text
pi(G □ H) <= (pi(G) + |G|) * pi(H) <= 2*pi(G)*pi(H),
```

not Graham's conjectured factor-one bound. Kenter--Skipper--Wilson
(arXiv:1905.08683) still describe the Lemke square as a potential
counterexample and report only `64 <= pi(L □ L) <= 85`.

The later Pulaj--Wood--Yerger paper (arXiv:2411.19314, 2024) proves that all
products of eight-vertex Lemke graphs obey the 64-pebble bound **when the
configuration support has size at most four**. It does not determine the
ordinary pebbling number. The authors explicitly identify large-support
bounds as a future direction. The frozen states below have support 63, so
they are disjoint from that proved support-restricted domain.

## Known proof-domain exclusions

A future trial must stop before state evaluation if its factor pair falls in
a proved class. The primary literature records the conjecture for products of
paths, cycles, trees, fans, and wheels, and for specified pairings involving
the 2-pebbling property. More precisely, the 2019 survey/computation records:

- if one factor has the 2-pebbling property, the other may be an even cycle,
  tree, complete graph, or complete bipartite graph in the cited theorems;
- products of two odd cycles are covered;
- `L □ K_n` and `L □ T` are proved for the original Lemke graph `L`;
- exact results are also recorded for the three minimal eight-vertex Lemke
  graphs paired with `K8`, `K12`, `K4,4`, or `K6,6`.
- every product of eight-vertex Lemke graphs is covered only for pebbling
  configurations of support at most four.

The frozen seed below is not in these classes: both factors are `L`, which is
specifically a smallest graph without the 2-pebbling property.

## Exact near-wall seed

Use the labelled original Lemke graph from Figure 1 of arXiv:1905.08683, with
roles `v1,...,v8` and edge list

```text
(v1,v2), (v1,v3),
(v2,v4),
(v3,v5), (v3,v6), (v3,v7),
(v4,v5), (v4,v6), (v4,v7), (v4,v8),
(v5,v8),
(v6,v8),
(v7,v8).
```

This is a full labelled record; the vertex names are the role map. The source
states `|V(L)|=8`, `|E(L)|=13`, `pi(L)=8`, and failure of the 2-pebbling
property. Therefore

```text
|V(L □ L)| = 64,
|E(L □ L)| = 208,
pi(L) * pi(L) = 64,
64 <= pi(L □ L) <= 85.
```

For the residual

```text
R(G,H) = pi(G)*pi(H) - pi(G □ H),
```

the conjecture is `R>=0`, while the seed has the certified bracket
`-21 <= R(L,L) <= 0`. The obstruction identity is exact: because both factors
are Class 0, the conjectured upper bound equals the unavoidable vertex-count
lower bound. Thus Graham's inequality on this pair is equivalent to closure
of Class 0 under this Cartesian square. Failure of the 2-pebbling property
removes the standard product-proof discount.

## One frozen bounded state-space transformation

No graph transformation is authorized. Keep the labelled graph `L □ L`
fixed on vertices `(vi,vj)` in lexicographic order.

For each root `r` and each distinct vertex `x`, begin with the canonical
immobile lower-bound distribution having one pebble on every nonroot vertex
and zero on `r`, then perform exactly one transformation: add one extra pebble
at `x`. Equivalently,

```text
D(r,x)(u) = 0 if u=r,
            2 if u=x,
            1 otherwise.
```

Every state has exactly 64 pebbles. The complete future state space is exactly

```text
64 roots * 63 extra-pebble locations = 4,032 labelled states.
```

Each state has support exactly 63. This deliberately begins at the opposite
end of the state space from the 2024 support-at-most-four theorem and follows
that paper's stated large-support direction without extending the graph menu.

This is the smallest shell above the universal unsolvable 63-pebble
configuration and directly tests whether the missing 2-pebbling discount can
leave a threshold configuration unsolvable. Every state must retain `r`, `x`,
the full labelled factor edge list, and the Cartesian role map. Exact
reachability must return a move sequence or an exact infeasibility
certificate. A timeout is unresolved.

The family is terminal: no second extra pebble, redistribution, root pruning,
factor substitution, edge surgery, random state, or post-result extension may
be added. Any future activation requires a separate evaluation contract,
database/calibration gate, independent reachability semantics, and per-process
limits of at most 60 seconds.

## Phase 0 disposition

**`PHASE0_FROZEN_NOT_EVALUATED`**. The declaration, reading, proof-domain
exclusions, exact near-wall seed, and one bounded transformation survive
selection. This document authorizes no state construction or reachability
evaluation and makes no mathematical claim about any of the 4,032 states.

No commit, push, issue, PR, release, or other public action is authorized.
