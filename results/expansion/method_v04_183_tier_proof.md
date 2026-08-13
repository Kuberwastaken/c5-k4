# Method v0.4 Lane P1: the two distance-core tiers

Date: **2026-08-13**. Status: **the `gamma_c=3` tier is proved; the
`gamma_c=4` tier is reduced to one explicit structural lemma**.

This note continues `method_v04_183_twoconnected.md`.  Let

```text
P = x-a-b-z
```

be a shortest path, where `dist(x,z)=3`.  Thus `P` is induced and bipartite.
The ambient live-core assumptions are that `G` is 2-connected,
nonbipartite and claw-free, that `z` is the unique vertex at distance three
from `x`, and that no vertex is farther from `x`.  The first proof below in
fact needs only the displayed distance condition.

Only the fixed connected Graph Atlas and frozen McKay order-8 catalogues were
used to falsify auxiliary lemmas.  No graphs were generated.  Every audit
command was externally capped at 60 seconds.

## A necessary correction to the preceding note

The deletion lemma in `method_v04_183_proof.md` is false with
"inclusion-maximal connected induced bipartite" as its hypothesis.  Such a
set need not dominate the graph: a vertex at distance two from the set cannot
be added while preserving connectedness, but can remain undominated by the
proposed deletion.

The fixed Atlas graph `EYWO` already supplies an exact countermodel.  For the
qualifying pair `(x,z)=(4,5)`, take

```text
B = {1,3,4,5},       D = B-{x,z} = {1,3}.
edges = 02 12 13 14 24 35.
```

Here `G[B]` is an inclusion-maximal connected induced bipartite graph;
`G[D]` is connected and dominates `x,z`; but vertex `0` has no neighbor in
`D`.  Hence `D` is not a connected dominating set.

The following stronger premise is sound and is what the tier argument uses.

> **Maximum-set color lemma.**  Let `B` be a maximum-cardinality induced
> bipartite vertex set, with color classes `A,C`.  Every vertex outside `B`
> has a neighbor in each of `A` and `C`.

Indeed, if an outside vertex had neighbors in at most one color class, it
could be placed in the other color class (and if it had no neighbor in `B`,
in either class), producing an induced bipartite set larger than `B`.

This distinction between *maximal connected* and *maximum-cardinality* is
essential.

## Complete proof of the `gamma_c=3` tier

> **Proposition.**  If a connected graph contains vertices `x,z` at distance
> three and `gamma_c(G)>=3`, then `b(G)>=5`.  In particular, the live
> 2-connected claw-free core with `gamma_c=3` satisfies `b>=5`.

Proof.  Suppose instead that `b<=4`.  The four vertices of the induced path
`P=x-a-b-z` form an induced bipartite set, so `b=4` and `V(P)` is a maximum
induced bipartite set.  Give it color classes

```text
A={x,b},       C={a,z}.
```

By the maximum-set color lemma, every vertex outside `P` has a neighbor in
both `A` and `C`.  An outside vertex with no neighbor in `{a,b}` would
therefore have to be adjacent to both `x` and `z`, contradicting
`dist(x,z)=3`.  Consequently `{a,b}` dominates every outside vertex.  It also
dominates `x,z`, and it is connected.  Thus it is a connected dominating set
of order two, contrary to `gamma_c>=3`.  Therefore `b>=5`.  QED.

This closes the first surviving tier without the path-extension proposition,
2-connectivity, claw-freeness, or uniqueness of the distance-three vertex.

## The `gamma_c=4` tier: one surviving lemma

The same color argument proves the second tier once the geodesic can be
extended by one adjacent vertex.

> **Conditional proposition.**  Suppose `gamma_c(G)>=4` and some vertex
> `y` outside `P` has a neighbor in `P` and makes `G[P union {y}]`
> bipartite.  Then `b(G)>=6`.

Proof.  Assume `b<=5`.  The preceding proposition gives `b>=5`, hence `b=5`
and `B=P union {y}` is a maximum induced bipartite set.  In its bipartition,
one color class is exactly one of the two path-parity pairs

```text
{x,b}  or  {a,z};
```

call this two-vertex class `A`.  The other class contains `y`.  Because `y`
has a neighbor in `P`, every vertex in the other class has a neighbor in
`A`.  The two vertices of `A` have a common neighbor on `P`: `a` for
`A={x,b}`, and `b` for `A={a,z}`.  Adding that common neighbor to `A` gives a
connected three-vertex set `D` which dominates all of `B`.

By the maximum-set color lemma, every vertex outside `B` has a neighbor in
`A`, so `D` dominates all of `G`.  This gives `gamma_c<=3`, contradicting
`gamma_c>=4`.  Therefore `b>=6`.  QED.

Thus the only unproved step needed for the `gamma_c=4` tier is:

> **Adjacent geodesic-extension lemma.**  Under the live 2-connected,
> claw-free, unique-distance-three hypotheses, the geodesic
> `P=x-a-b-z` has a vertex `y` outside `P` which is adjacent to `P` and for
> which `G[P union {y}]` is bipartite.

Equivalently, some vertex meeting `P` has all its neighbors on `P` in one
path-parity class.  This lemma passed every qualifying geodesic in the fixed
catalogues:

| catalogue | qualifying `gamma_c=4` geodesics | failures |
|---|---:|---:|
| Graph Atlas, orders at most 7 | 24 | 0 |
| McKay connected order 8 | 206 | 0 |

These are path counts, not graph counts.  The audit checked every qualifying
orientation and every shortest induced `x`--`z` path.  This bounded survival
is not a proof.

The lemma has a plausible 2-connectivity route: if no such `y` exists, every
extra neighbor of `x` must also meet `a`, and symmetrically every extra
neighbor of `z` must also meet `b`.  An internally disjoint alternate
`x`--`z` path of length three would then combine with `P` into an induced
bipartite set of order six (the forced extra edges respect the six-cycle
bipartition).  What remains unresolved is the case where 2-connectivity only
supplies ears returning to an internal vertex of `P`; no complete argument
was found that converts all such ears into the required adjacent extension.

## Honest stop point

The tier split has produced one theorem and one sharply isolated lemma:

1. `gamma_c=3 ==> b>=5` is proved, in a stronger distance-three-only form;
2. `gamma_c=4 ==> b>=6` follows immediately from the adjacent
   geodesic-extension lemma;
3. that lemma survives all 230 fixed-catalogue geodesics but remains
   unproved;
4. the earlier maximal-connected deletion lemma must not be used without
   replacing maximality by maximum cardinality (or separately proving
   domination).

No complete proof of the full 2-connected branch, and therefore no proof of
WOWII 183, is claimed here.
