# Method v0.4 Lane P1: the closed-neighborhood transversal rung is false

Date: **2026-08-13**. Status: **the repaired auxiliary rung is refuted by an
infinite exact family; WOWII 183 remains open in this lane**.

This note continues `method_v04_183_unique_layer.md`.  It tests only the
proposed implication

```text
G connected, nonbipartite and claw-free,
L3(x)={z}, with no vertex farther from x, and gamma_c(G)>=5
  ==>
some t in N[x] makes G-t bipartite.
```

The implication is false.  The counterexamples below are given by a direct
family construction and proved structurally; no graph search or graph
generation was used.  The already-frozen Atlas/order-eight audit in the
preceding note remains correct: the smallest member of this family has nine
vertices, just beyond that audit.

## The pendant-clique family

For an integer `m>=4`, let `H_m` have vertices

```text
Q = {q0,q1,...,q_(m-1)},
R = {r0,r1,...,r_(m-1)},
and z.
```

Make `Q` a clique.  For every `i`, add the edge `qi-ri`, and add the one
additional edge `r1-z`.  There are no other edges.  Thus every clique vertex
has one pendant neighbor, except that the pendant edge at `q1` is extended to
the path

```text
q1-r1-z.
```

Take the distinguished centre to be

```text
x=q0.
```

Equivalently, `H_m` is the line graph of the tree consisting of `m` two-edge
arms at a common centre, with one arm extended by one edge.  The direct
description above is used throughout the proof.

## Verification of the live hypotheses

The graph is connected.  It is nonbipartite because `Q` contains a triangle
when `m>=4`.

It is claw-free.  For each `qi`, its neighborhood is the union of the clique
`Q-{qi}` and the singleton `{ri}`.  Hence that neighborhood has independence
number at most two.  Every `ri` with `i!=1` has degree one, `r1` has the two
neighbors `q1,z`, and `z` has degree one.  No vertex can therefore be the
centre of an induced claw.

The distance layers from `x=q0` are exactly

```text
L0 = {q0},
L1 = (Q-{q0}) union {r0},
L2 = R-{r0},
L3 = {z}.
```

Indeed, every other `qi` is adjacent to `q0`, each `ri` with `i!=0` is reached
through `qi`, and `z` is reached by `q0-q1-r1-z`.  The stated absence of other
edges also proves that these distances cannot be shortened.  Thus `z` is the
unique vertex at distance three and no vertex is farther from `x`.

## Exact connected domination number

> **Proposition.** `gamma_c(H_m)=m+1`.

The set

```text
Q union {r1}
```

is connected and dominates every vertex, so `gamma_c(H_m)<=m+1`.

For the reverse inequality, let `D` be a connected dominating set.  No single
vertex dominates `H_m`, so `|D|>1`.  For each `i!=1`, the vertex `ri` is a
leaf.  Dominating it requires `ri in D` or `qi in D`; if `ri in D`,
connectivity of a non-singleton `D` also requires its only neighbor `qi` to
belong to `D`.  Consequently

```text
qi in D for every i!=1.
```

Similarly, domination of the leaf `z` requires `z in D` or `r1 in D`.  If
`z in D`, connectivity requires `r1 in D` as well, so in all cases
`r1 in D`.  Since `m>=4`, the set `D` also contains clique vertices distinct
from `q1`; connecting `r1` to them requires its only non-`z` neighbor `q1` to
belong to `D`.  Hence

```text
Q union {r1} subset D,
```

and `|D|>=m+1`.  This proves the proposition.  In particular,
`gamma_c(H_m)>=5` for every `m>=4`.

## Exact induced-bipartite number

> **Proposition.** `b(H_m)=m+3`.

Any induced bipartite vertex set contains at most two vertices of the clique
`Q`; three clique vertices would induce a triangle.  It can contain at most
all `m+1` vertices of `R union {z}`.  Therefore

```text
b(H_m) <= 2+(m+1)=m+3.
```

Conversely, take all of `R union {z}` and any two vertices of `Q`.  The
induced graph consists of one edge between the selected clique vertices,
some pendant edges, and possibly the tail `q1-r1-z`.  It is a forest, hence
bipartite, and it has `m+3` vertices.  Thus equality holds.

This family is not a counterexample to WOWII 183.  It attains the desired
bound exactly:

```text
b(H_m)=m+3=gamma_c(H_m)+2.
```

## Failure of every one-vertex transversal

Deleting any one vertex outside `Q` leaves the full clique `K_m`.  Deleting
one vertex of `Q` leaves the clique `K_(m-1)`.  Since `m>=4`, both remaining
cliques contain a triangle.  Therefore

```text
H_m-t is nonbipartite for every vertex t of H_m.
```

In particular, no `t in N[x]` makes `H_m-t` bipartite.  More precisely, the
odd-cycle transversal number is

```text
tau_odd(H_m)=m-2,
```

because one must delete all but at most two vertices of `Q`, and doing so is
sufficient.  This also follows from

```text
|V(H_m)|-b(H_m)=(2m+1)-(m+3)=m-2.
```

The smallest case `H_4` has order nine, `gamma_c=5`, `b=7`, and
`tau_odd=2`.  This explains exactly why the repaired rung survived every
qualifying graph in the frozen catalogues through order eight.

## What the family says about the proof route

The endpoint-return obstruction from the odd-cycle family was not the only
way the one-vertex-transversal strategy could fail.  In `H_m`, the unique
distance-three vertex lies on the single extended pendant arm, while all odd
cycles lie in a dense clique entirely within `N[x]`.  The unique third layer
therefore controls the remote arm but does not bound the odd-cycle
transversal number of the first layer.

At the same time, the family is exact for the target because the same clique
coordinates force both sides to grow together:

```text
each additional clique arm raises gamma_c by one,
and raises b by one,
while preserving b-gamma_c=2.
```

Thus replacing `t=x` by `t in N[x]` repairs the order-eight countermodel but
does not supply a valid general rung.  A continuation must compare the size
of the near-centre odd-cycle obstruction with the connected-domination cost,
rather than trying to collapse all odd cycles with one deletion.  The exact
family above should remain a compulsory equality test for any such proposed
lemma.

## Honest stop point

The closed-neighborhood transversal rung is conclusively false, even in an
infinite family satisfying every live hypothesis with `gamma_c` arbitrarily
large.  The family satisfies WOWII 183 at equality, so this is an auxiliary
counterexample only.  No replacement theorem is claimed here, and no public
counterexample, release, or full proof of WOWII 183 follows from this note.
