# Method v0.4 Lane P1: multi-vertex augmentation closes the `gamma_c=4` tier

Date: **2026-08-13**. Status: **paper proof complete for the
`gamma_c=4` tier; the full WOWII 183 core is not proved**.

This note continues `method_v04_183_extension_lemma.md`.  The 13-vertex
counterexample there shows why one cannot always enlarge a fixed
distance-three geodesic by a *single adjacent* vertex while preserving
bipartiteness.  Its three vertices anticomplete to the geodesic suggest the
right replacement: allow two vertices anticomplete to the geodesic at once.

The resulting argument is stronger and simpler than the failed lemma.  It
uses neither 2-connectivity, claw-freeness, nor uniqueness of the vertex at
distance three.

## The multi-vertex augmentation theorem

Write `b(G)` for the maximum order of an induced bipartite subgraph and
`gamma_c(G)` for the connected domination number.

> **Theorem.** Let `G` be a connected graph containing vertices `x,z` with
> `dist(x,z)=3`.  If `gamma_c(G)>=4`, then `b(G)>=6`.

In particular, every graph in the live 2-connected WOWII 183 core with
`gamma_c(G)=4` satisfies

```text
b(G) >= 6 = gamma_c(G)+2.
```

### Proof

Fix a shortest path

```text
P = x-a-b-z.
```

It is induced.  Suppose for a contradiction that `b(G)<=5`.

Call a vertex `y` outside `P` **compatible** when `G[P union {y}]` is
bipartite.  First observe that no compatible vertex can have a neighbor on
`P`.  Indeed, if such a `y` existed, then `B=P union {y}` would be a
maximum-cardinality induced bipartite set: it has five vertices and the
assumption gives `b(G)<=5`.  In a bipartition of `G[B]`, let `A` be the
two-vertex path-parity class not containing `y`.  Thus

```text
A = {x,b}  or  A = {a,z}.
```

Every vertex outside a maximum induced bipartite set has a neighbor in each
color class; otherwise it could be added to the opposite class.  Hence every
vertex outside `B` has a neighbor in `A`.  The two vertices of `A` have a
common neighbor on `P` (`a` in the first case and `b` in the second).  Adding
that common neighbor to `A` gives a connected three-vertex set which dominates
`B` and every vertex outside `B`.  This would give `gamma_c(G)<=3`, contrary
to the hypothesis.

Now partition the vertices outside `P` as follows:

```text
R = {r outside P : r has no neighbor on P},
Y = V(G) - (V(P) union R).
```

Every vertex of `Y` is adjacent to `a` or `b`.  To see this, take `y in Y`.
It meets `P`, and it is not compatible by the preceding paragraph.  If it
were adjacent to neither `a` nor `b`, its nonempty neighborhood on `P` would
be contained in `{x,z}`.  It cannot contain both endpoints, because that
would give `dist(x,z)<=2`.  It would therefore meet exactly one endpoint,
making `G[P union {y}]` a path with one extra leaf and hence bipartite, a
contradiction.

There are now three exhaustive cases.

1. If `|R|>=2`, choose distinct `r,s in R`.  The induced graph on
   `P union {r,s}` is the disjoint union of `P4` and the graph induced by two
   vertices (either `K2` or two isolated vertices).  It is bipartite and has
   six vertices, contradicting `b(G)<=5`.
2. If `R` is empty, the edge `{a,b}` is a connected dominating set: it
   dominates `P`, and every vertex outside `P` lies in `Y` and meets
   `{a,b}`.  Thus `gamma_c(G)<=2`, a contradiction.
3. If `R={r}`, connectedness supplies a neighbor `y` of `r`.  Since `r` is
   anticomplete to `P` and is the only member of `R`, this neighbor lies in
   `Y`; hence it is adjacent to `a` or `b`.  The set `{a,b,y}` is connected.
   It dominates `P`, all of `Y` through `{a,b}`, and `r` through `y`.
   Therefore `gamma_c(G)<=3`, again a contradiction.

All cases contradict the assumptions, so `b(G)>=6`.  QED.

## How the failed one-vertex rung led to the proof

The counterexample `LhrMXotKwQ?c?c` from the preceding note has three
vertices `r1,r2,r3` anticomplete to `P`.  No vertex touching `P` is a
compatible one-vertex extension, but any two of the `ri` enlarge `P` to an
induced bipartite graph of order six.  The proof above shows that this is not
an accidental repair:

- two anticomplete vertices give the required bipartite augmentation;
- zero anticomplete vertices expose a connected dominating edge;
- one anticomplete vertex exposes a connected dominating triple.

Thus the exact obstruction to the failed adjacent-extension lemma supplies
the missing alternative rather than requiring a wider graph search.

## Fixed-catalogue audit

As an independent falsification check, the stronger theorem was evaluated on
the already-fixed catalogues only.  No graphs were generated.  The command
was externally capped at 60 seconds and completed in 8.98 seconds.

| catalogue | connected graphs | graphs with diameter at least 3 | cases with `gamma_c>=4` and `b=6` | failures of `b>=6` |
|---|---:|---:|---:|---:|
| Graph Atlas, orders at most 7 | 995 | 538 | 14 | 0 |
| McKay connected order 8 | 11,117 | 6,962 | 89 | 0 |

The equality column is included only to show that the conclusion is sharp in
both fixed catalogues.  The theorem rests on the proof above, not on this
bounded audit.

## Consequence and remaining obligation

The two distance-three tiers are now rigorous in forms stronger than the live
core assumptions:

```text
gamma_c(G)>=3  ==>  b(G)>=5,
gamma_c(G)>=4  ==>  b(G)>=6.
```

The first was proved in `method_v04_183_tier_proof.md`; the second is proved
here.  This closes the exact `gamma_c=4` obligation isolated by the
2-connected lane.

It does **not** prove WOWII 183.  The outstanding 2-connected obligation is
to prove that the live core has `gamma_c<=4`, or to extend the tier argument
to larger connected domination number.  The cut-vertex branch identified in
`method_v04_183_proof.md` also remains separate.  No full-conjecture or public
release claim is made here.
