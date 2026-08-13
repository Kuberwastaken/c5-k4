# Method v0.4 Lane P1: what the unique third layer does not force

Date: **2026-08-13**. Status: **one exact uniqueness-based proof rung is
refuted; a weaker transversal rung is isolated and survives the fixed
catalogues, but is not proved**.

This note continues `method_v04_183_general_distance3.md`.  It considers only
the live implication

```text
G connected, nonbipartite and claw-free,
L3(x)={z}, and no vertex is farther than z
  ==>  b(G) >= gamma_c(G)+2.
```

No graphs were generated.  The only computational checks used the already
fixed connected Graph Atlas and McKay order-eight catalogues.  Every command
was externally capped at 60 seconds.

## A rigorous reduction to a one-vertex odd-cycle transversal

Write

```text
tau_odd(G) = n-b(G).
```

The two earlier distance-three arguments prove the target through
`gamma_c<=4`.  Indeed, an induced geodesic `P4` handles `gamma_c<=2`, while
`method_v04_183_tier_proof.md` and `method_v04_183_multiext.md` prove

```text
gamma_c>=3 ==> b>=5,
gamma_c>=4 ==> b>=6.
```

For the remaining tier there is a short rigorous implication.

> **Transversal reduction.**  Under the displayed live hypotheses, if
> `tau_odd(G)<=1`, then `b(G)>=gamma_c(G)+2`.

Proof.  First, `gamma_c(G)<=n-3`.  If every vertex had degree at most two,
connectedness would make `G` a path or a cycle.  A path is bipartite.  Among
nonbipartite cycles, `C3` and `C5` have eccentricity less than three, every
vertex of `C7` has two vertices at distance three, and every longer odd cycle
has a vertex farther than distance three.  Thus none satisfies the unique
third-layer hypothesis.  Consequently `G` has a vertex of degree at least
three.

Choose three edges incident with such a vertex.  This three-edge star is a
forest and therefore extends to a spanning tree of `G`.  The spanning tree
has a vertex of degree at least three, so it has at least three leaves.  Its
nonleaves form a connected dominating set, proving `gamma_c(G)<=n-3`.

Now `tau_odd<=1` gives `b>=n-1`, and hence

```text
b >= n-1 >= gamma_c+2.
```

This proves the reduction.  QED.

Thus, after the two absolute tiers, the only unresolved numerical regime is

```text
gamma_c>=5 and tau_odd>=2.
```

A proof that this regime is impossible would close the live claw-free core.

## Failed rung: the distinguished centre need not hit every odd cycle

The seven-cycle obstruction in `method_v04_183_general_distance3.md` suggests
that uniqueness might block the two endpoint-returning arcs by forcing the
distinguished centre `x` itself to hit every odd cycle.  The precise proposed
rung was:

> **False centre-transversal lemma.**  If the live hypotheses hold and
> `gamma_c(G)>=5`, then `G-x` is bipartite.

This is false in the fixed order-eight catalogue.  The exact countermodel is

```text
graph6 = GCQ`e_
V = {0,1,2,3,4,5,6,7}
E = {03,05,07,14,17,25,26,36,37}.
```

Take `x=7` and `z=2`.  The distance layers are

```text
L0 = {7},
L1 = {0,1,3},
L2 = {4,5,6},
L3 = {2}.
```

So `z` is the unique distance-three vertex and there is no farther vertex.
The graph is nonbipartite because `{0,3,7}` is a triangle.  It is claw-free
by the following complete neighborhood check:

```text
N(0)={3,5,7}, with 3-7 present;   N(1)={4,7};
N(2)={5,6};                       N(3)={0,6,7}, with 0-7 present;
N(4)={1};                         N(5)={0,2};
N(6)={2,3};                       N(7)={0,1,3}, with 0-3 present.
```

No displayed neighborhood contains an independent triple.  Nevertheless,
`G-x` contains the induced odd cycle

```text
0-3-6-2-5-0,
```

so the distinguished centre is not an odd-cycle transversal.  This is
exactly an endpoint-return obstruction surviving the unique-third-layer
condition: the extra path `7-1-4` and the attachments through `0,3` keep all
vertices except `2` within distance two of `7`, while the `C5` remains after
`7` is deleted.

For completeness, this graph satisfies the desired WOWII 183 core inequality
tightly rather than refuting it.  Every connected dominating set contains
`1` to dominate the leaf `4`, and then contains `7` to connect `1` to the
rest of the graph.  If only two vertices of the `C5` were added, connectivity
to `7` leaves only the adjacent pairs `{0,3}`, `{3,6}`, or `{0,5}`.  These
respectively fail to dominate `2`, `5`, or `6`.  Hence at least three cycle
vertices are necessary.  Conversely,

```text
{0,1,2,5,7}
```

is connected and dominating, so `gamma_c(G)=5`.  Deleting `0` leaves the
seven-vertex path

```text
4-1-7-3-6-2-5,
```

and deleting `3` leaves the seven-vertex path

```text
4-1-7-0-5-2-6.
```

Thus `b(G)=7` and `b=gamma_c+2`.  In particular, the failed lemma prescribed
the wrong transversal vertex; it did not expose a failure of the target.

## The repaired rung

The countermodel suggests the strictly weaker statement

> **Closed-neighborhood transversal rung.**  Under the live hypotheses and
> `gamma_c(G)>=5`, there is a vertex `t in N[x]` such that `G-t` is
> bipartite.

This would prove the remaining tier immediately by the transversal reduction.
It is genuinely weaker than the refuted rung: for ``GCQ`e_``, the only
one-vertex odd-cycle transversals are `0` and `3`, both in `N(x)` but neither
equal to `x`.

An exact fixed-catalogue audit gives:

| catalogue | qualifying graphs with `gamma_c>=5` | qualifying `(x,z)` pairs | failures of `G-x` bipartite | failures of the closed-neighborhood rung |
|---|---:|---:|---:|---:|
| Graph Atlas, orders at most 7 | 0 | 0 | 0 | 0 |
| McKay connected order 8 | 5 | 9 | 1 | 0 |

The sole failure of the stronger centre-transversal statement is the
orientation `(x,z)=(7,2)` in ``GCQ`e_`` proved above.  The repaired rung is only
a theorem signal: bounded survival is not a proof.

## Honest stop point

Uniqueness does not itself eliminate endpoint-returning odd cycles, and a
proof must not assert that the distinguished centre meets every odd cycle.
The durable narrowing is instead:

1. the full live core is already proved through `gamma_c<=4`;
2. a one-vertex odd-cycle transversal proves every remaining tier;
3. the natural claim that the transversal is `x` has the exact smallest
   fixed-catalogue countermodel ``GCQ`e_``;
4. allowing the transversal anywhere in `N[x]` repairs that countermodel and
   has no failure in the fixed catalogues, but remains unproved.

No claim beyond this reduction, countermodel, and bounded repaired rung is
made here.
