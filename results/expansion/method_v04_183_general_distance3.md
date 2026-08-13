# Method v0.4 Lane P1: the general distance-three inequality is false

Date: **2026-08-13**. Status: **stronger auxiliary theorem refuted; the
original WOWII 183 core is unaffected**.

The two proved tiers in `method_v04_183_tier_proof.md` and
`method_v04_183_multiext.md` invite the stronger statement

```text
if G is connected and has a distance-three pair, then
b(G) >= gamma_c(G)+2.
```

This statement is false.  The smallest fixed-catalogue countermodel is the
seven-cycle.  The failure also identifies exactly why the multi-vertex
augmentation proof cannot be iterated beyond its two absolute tiers.

No graphs were generated in this investigation.  The only computational
inputs were the already-fixed NetworkX Graph Atlas and McKay connected
order-eight catalogue `/tmp/graph8c.g6`.  Every subprocess was externally
capped at 60 seconds.

## Exact counterexample

Let `G=C_7`, with cyclic edges

```text
01 12 23 34 45 56 60.
```

In the fixed Graph Atlas its graph6 encoding is

```text
FhCKG.
```

The vertices `0` and `3` are at distance three.  Nevertheless

```text
b(C_7)=6,
gamma_c(C_7)=5,
```

and hence

```text
b(C_7)=gamma_c(C_7)+1 < gamma_c(C_7)+2.
```

Both invariant values have short structural proofs.  An induced bipartite
subgraph of an odd cycle must omit at least one vertex, while deleting any
one vertex from `C_7` leaves an induced path, so `b(C_7)=6`.  Every proper
connected induced vertex set in a cycle is a consecutive block.  Such a
block dominates the cycle only if its complementary block has at most two
vertices.  Thus every connected dominating set of `C_7` has at least five
vertices, and any five consecutive vertices attain the bound.

In fact this is an infinite obstruction, not an isolated catalogue accident.
For every odd cycle `C_(2k+1)` with `k>=3`,

```text
diam(C_(2k+1)) = k >= 3,
b(C_(2k+1)) = 2k,
gamma_c(C_(2k+1)) = 2k-1.
```

Thus every such cycle has a distance-three pair and misses the proposed
inequality by one.  This family conclusion is a direct proof from the single
cycle structure; it is not the output of a widened graph search.

## Exact failure of the `R` argument

Fix the geodesic

```text
P = 0-1-2-3
```

in `C_7`, and use the partition from the multi-extension proof:

```text
R = {vertices outside P anticomplete to P} = {5},
Y = V(G) - (V(P) union R) = {4,6}.
```

The graph induced by `R` has one isolated component.  Both vertices in `Y`
are compatible one-vertex extensions of `P`:

```text
N(4) intersect P = {3},
N(6) intersect P = {0},
```

so both `G[P union {4}]` and `G[P union {6}]` are bipartite.

The proof of the already-established theorem

```text
gamma_c(G)>=4  ==>  b(G)>=6
```

assumes `b<=5`.  Under that numerical assumption, a compatible five-vertex
extension `P union {y}` is *maximum-cardinality*.  The maximum-set color lemma
then produces a connected dominating triple, contradicting `gamma_c>=4`.
Consequently that proof may rule out all compatible vertices meeting `P`,
deduce that every vertex of `Y` meets `{1,2}`, and finish from the three cases
`|R|=0`, `|R|=1`, and `|R|>=2`.

For the proposed relative inequality, the contrary assumption is only

```text
b <= gamma_c+1.
```

When `gamma_c>=5`, this does **not** make a five-vertex compatible extension
maximum.  In `C_7`, such an extension has order five while `b=6`.  The
maximum-set color lemma is therefore unavailable.  Compatible vertices `4`
and `6` survive, neither meets the internal edge `{1,2}`, and the conclusion
that `{1,2}` dominates `Y` is false.  This is the first failed step; the later
`R` case split never starts.

Replacing the five-vertex extension by a genuinely maximum bipartite set does
not repair the proof.  A maximum bipartite set in `C_7` is a six-vertex path.
Its omitted vertex attaches to both path color classes, exactly as the
maximum-set color lemma requires, but no four-vertex connected dominating set
exists.  Thus there is no general operation deleting two vertices from such a
maximum set and retaining connected domination.

The component structure of `R` alone is correspondingly too weak: here `R`
has only one isolated vertex, yet `gamma_c=5`.  The two arcs in `Y` that return
to opposite endpoints of `P` can make connected domination large without
making `R` large.  Any successful relative theorem needs an additional
hypothesis controlling those endpoint-returning arcs, not merely the number
or bipartite structure of components in `R`.

## Fixed-catalogue audit

An independent exact subset enumeration recomputed `b` and `gamma_c` for
every connected fixed-catalogue graph of diameter at least three.  A subset
was counted for `gamma_c` only after direct connectivity and domination
checks, and for `b` only after a direct bipartiteness check.

| catalogue | connected graphs of diameter at least 3 | failures of `b>=gamma_c+2` | smallest / only failure |
|---|---:|---:|---|
| Graph Atlas, orders at most 7 | 538 | 1 | `FhCKG` (`C_7`), `(gamma_c,b)=(5,6)` |
| McKay connected order 8 | 6,962 | 1 | ``GCp`eO``, `(gamma_c,b)=(5,6)` |

The order-eight failure has 10 edges,

```text
03 04 07 14 15 17 25 26 36 47,
```

and vertices `4` and `7` are adjacent true twins.  Deleting either one gives
an induced `C_7`.  It is therefore the same obstruction under a true-twin
extension, rather than evidence for a distinct mechanism.

The audit is only a falsification check.  The counterexample and infinite odd-
cycle family rest on the structural proofs above.

## What remains valid

Combining the induced `P4` bound with the two prior proofs gives the sharp
general statement currently justified by this lane:

```text
if G is connected and has a distance-three pair, then
  gamma_c(G)<=2  ==> b(G)>=gamma_c(G)+2,
  gamma_c(G)=3   ==> b(G)>=5=gamma_c(G)+2,
  gamma_c(G)=4   ==> b(G)>=6=gamma_c(G)+2,
  gamma_c(G)>=4  ==> b(G)>=6.
```

Equivalently, the proved uniform summary is

```text
b(G) >= min(gamma_c(G)+2, 6).
```

The seven-cycle shows that the relative `+2` term cannot continue past
`gamma_c=4` under the distance-three hypothesis alone.

This does not refute WOWII 183 or its post-pruning core.  For every vertex of
`C_7`, there are **two** vertices at distance three, whereas the unresolved
core requires a centre with a **unique** distance-three vertex and none
farther away.  The failed strengthening therefore confirms that this
uniqueness condition is mathematically substantive and cannot simply be
dropped.
