# Method v0.2 Trial G: WOWII 438b

Status: **THEOREM_SHADOW (stronger elementary theorem)**
Target frozen in: `method_v02_wave2_manifest.md`
Source record: `data/wowii-conjectures.json`, entry `438b`
Historical marker: open (`O`), January 2012
Database gate: `VIABLE`, 997 applicable controls, zero violations

## Frozen statement and reading

For every connected graph `G` of order greater than three,

```text
alpha_2(G) <= alpha(G) + alpha(G[V - H_2]) + |E(G[H_2])|,
```

where `H_2 = {v : degree_G(v) <= 2}` and `alpha_2` is the maximum
cardinality of a vertex set inducing maximum degree at most one.

The transcription is unambiguous for this trial. The source occurrence is
listed under the matching-number sublist, but the statement itself and its
duplicate both concern `alpha_2` and `alpha`; this metadata mismatch does not
alter the formula.

Use the signed residual

```text
R(G) = alpha(G) + alpha(G[V - H_2]) + |E(G[H_2])| - alpha_2(G).
```

The conjecture asserts `R(G) >= 0`.

## Baseline and compensation identity

The frozen baseline was `alpha_2(G) <= 2 alpha(G)`, because every graph of
maximum degree at most one is bipartite. Splitting the matching edges of an
optimal 2-independent set across `H_2` gives the exact compensation that the
baseline alone misses.

In fact, let `H` be **any** subset of the vertices of a finite simple graph
`G`, and put `B = V(G) - H`. Choose a maximum 2-independent set `S`. The
induced graph `G[S]` is a disjoint union of isolated vertices and edges. If
`m = |E(G[S])|`, then

```text
alpha(G[S]) = |S| - m,
```

so `|S| <= alpha(G) + m`.

Partition the `m` matching edges into:

- `m_H`, the edges with both endpoints in `H`; and
- `m_B`, the edges with at least one endpoint in `B`.

Clearly `m_H <= |E(G[H])|`. From every edge counted by `m_B`, select one
endpoint in `B` (the unique `B` endpoint for a crossing edge, and either
endpoint for a `B`--`B` edge). These selected endpoints are independent: two
endpoints selected from different edges cannot be adjacent, since every
vertex of `G[S]` already has degree at most one. Therefore

```text
m_B <= alpha(G[B]).
```

Combining the three inequalities gives the stronger arbitrary-subset theorem

```text
alpha_2(G) <= alpha(G) + alpha(G[V - H]) + |E(G[H])|.
```

Taking `H = H_2` proves WOWII 438b. Connectivity, the order bound, and the
degree definition of `H_2` are not needed.

Equivalently, the frozen low-degree-layer prediction is compensated edge by
edge: a matching edge wholly inside the layer pays one unit through
`|E(G[H_2])|`, while every other matching edge injects one independent vertex
into the high-degree core.

## Bounded-search disposition

The Wave 2 manifest explicitly makes a proof that the correction compensates
the construction a terminating outcome for this subfamily. The argument above
proves compensation for every graph and every vertex subset, so no dense-core,
attachment-orbit, layer-size, or expanded-order search was run. In particular,
there were zero ILP calls and zero timeouts; the 60-second per-solve cap was
vacuous.

This is stronger evidence than a bounded hold, but it is not a counterexample.
The primary outcome is `THEOREM_SHADOW`: the apparent tight wall is the shadow
of a simple matching-edge partition lemma.

## Independent exact check

`scripts/method_v02_438b_verify.py` independently enumerates the definitions
with bit masks. It checks:

1. the stronger arbitrary-subset inequality for every graph in the NetworkX
   Graph Atlas and every subset `H`;
2. the source specialization `H = H_2` on every applicable connected Atlas
   graph;
3. the named control graphs and the frozen structured dense-core / low-degree
   false-twin constructions.

The verifier does not use the proof's edge-selection construction to compute
either side.

Observed output (Python 3.9.25, approximately 3.0 seconds wall time):

```text
PASS arbitrary-H atlas checks: 144923
PASS source H_2 atlas checks: 992
PASS named H_2 checks: 10
PASS structured compressed-exact H_2 checks: 66
PASS WOWII 438b stronger arbitrary-subset theorem
```

## Method consequence

The intended shared-neighborhood false-twin transformation cannot cross #438b:
the correction is not merely empirically compensating that construction. It
compensates every possible maximum-degree-one induced subgraph. Future
iterations should classify bounds of the form

```text
alpha_2 <= alpha + alpha(complementary induced part) + induced-edge cost
```

as theorem shadows before assigning construction budget.

No novelty claim or upstream status change is made in this trial report. A
separate source/novelty audit would be required before presenting the argument
as a new resolution of the historically open entry.
