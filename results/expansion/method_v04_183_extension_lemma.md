# Method v0.4 Lane P1: counterexample to the adjacent extension lemma

Date: **2026-08-13**. Status: **the auxiliary lemma is false; WOWII 183
remains open in this lane**.

> **Follow-up (2026-08-13).** The failed lemma exposed the correct
> multi-vertex dichotomy. `method_v04_183_multiext.md` proves that every
> connected graph with a distance-three pair and `gamma_c>=4` has `b>=6`, so
> the exact `gamma_c=4` tier is now closed without the auxiliary lemma.

This note tests only the adjacent geodesic-extension lemma isolated in
`method_v04_183_tier_proof.md`.  It does not widen the catalogue search and
does not claim a counterexample to WOWII 183.

## The quantified lemma being tested

Fix a shortest path

```text
P = x-a-b-z.
```

The proposed lemma says that if `G` is 2-connected and claw-free, `z` is the
unique vertex at distance three from `x`, no vertex is farther from `x`, and
`gamma_c(G)=4`, then there is a vertex `y` outside `P` such that

1. `y` has a neighbor on `P`; and
2. `G[P union {y}]` is bipartite.

For the path bipartition

```text
A = {x,b},       C = {a,z},
```

condition 2 is equivalent to `N(y) intersect P` being contained in `A` or in
`C`.  The counterexample below refutes the statement for the displayed fixed
geodesic `P`.

## A 13-vertex counterexample

Take

```text
V(G) = {x,a,b,z}
       union {u1,u2,u3}
       union {w1,w2,w3}
       union {r1,r2,r3}.
```

Start with the path `x-a-b-z`.  Make `U={u1,u2,u3}` and
`W={w1,w2,w3}` cliques.  For each `i in {1,2,3}`, add

```text
x-ui, a-ui, b-wi, z-wi, ui-wi, ui-ri, wi-ri.
```

There are no other edges.  With the vertex order

```text
x,a,b,z,u1,u2,u3,w1,w2,w3,r1,r2,r3
```

an exact graph6 encoding is

```text
LhrMXotKwQ?c?c
```

The graph has 13 vertices and 30 edges.

## Verification of every hypothesis

The graph is nonbipartite: `{x,a,u1}` induces a triangle.

It is 2-connected because it contains the spanning cycle

```text
x-a-b-z-w1-r1-u1-u2-r2-w2-w3-r3-u3-x.
```

It is claw-free.  This follows directly by inspecting neighborhoods:

- `N(x)={a} union U` and `N(z)={b} union W` are cliques;
- `N(a)` is the union of the clique `{x} union U` and the singleton `{b}`;
- `N(b)` is the union of the clique `{z} union W` and the singleton `{a}`;
- `N(ui)` is the disjoint union of the cliques
  `{x,a} union (U-{ui})` and `{wi,ri}`;
- `N(wi)` is the disjoint union of the cliques
  `{b,z} union (W-{wi})` and `{ui,ri}`;
- `N(ri)={ui,wi}` is a clique.

Thus no vertex neighborhood contains an independent set of order three.

The distance layers from `x` are exact:

```text
L0 = {x},
L1 = {a,u1,u2,u3},
L2 = {b,w1,w2,w3,r1,r2,r3},
L3 = {z}.
```

In particular, `z` is the unique vertex at distance three and no vertex is
farther away.

Finally, `gamma_c(G)=4`.  The set

```text
D = {u1,u2,u3,w1}
```

is connected and dominating, so `gamma_c<=4`.  For the reverse inequality,
observe that

```text
N[ri] = {ui,wi,ri}
```

for each `i`.  These three closed neighborhoods are pairwise disjoint, so a
dominating set of order three would have to choose exactly one vertex from
each triple `{ui,wi,ri}` and no other vertex.  To dominate `x` it must choose
some `ui`, and to dominate `z` it must choose some `wi`.  If it chooses an
`ri`, that vertex is isolated inside the chosen set because the other two
vertices of its triple were not chosen.  If it chooses only `u`- and
`w`-vertices, the chosen `u`-vertices and chosen `w`-vertices have no edge
between them: the only `U`--`W` edges are the matched edges `ui-wi`, while
only one member of each indexed triple was chosen.  Either way the chosen set
is disconnected.  Hence no connected dominating set has order three, and
`gamma_c=4`.

## Failure of the extension conclusion

Every vertex outside `P` has one of the following neighborhoods on `P`:

```text
N(ui) intersect P = {x,a},
N(wi) intersect P = {b,z},
N(ri) intersect P = empty.
```

The first two sets meet both parity classes `A` and `C`, so adding the vertex
creates a triangle on the five induced vertices.  The vertices `ri` do not
meet `P` at all.  Therefore there is no admissible `y`, and the adjacent
geodesic-extension lemma is false even with `gamma_c=4` and every live
2-connected hypothesis.

As a sanity check that this is only an auxiliary-lemma counterexample,

```text
P union {r1,r2,r3}
```

is an induced bipartite set of order seven.  Hence this graph satisfies the
desired tier bound `b(G)>=6`; it does not refute WOWII 183.

## Independent exact check

A separate exhaustive subset check, externally capped at 60 seconds,
recomputed `node_connectivity=2`, claw-freeness, the displayed distance
layers, absence of an admissible extension, and `gamma_c=4`.  It also found
`b(G)=7`.  The structural arguments above do not depend on that computation.

## Consequence for the proof lane

The `gamma_c=3` theorem proved in `method_v04_183_tier_proof.md` survives.
The conditional implication from an adjacent extension to `b>=6` also
survives.  What fails is the claim that the live hypotheses always supply
such an extension.  Any continuation of the `gamma_c=4` tier must allow a
larger bipartite augmentation (the three vertices `r1,r2,r3` do so here) or
use a different argument; the one-vertex extension route is closed.
