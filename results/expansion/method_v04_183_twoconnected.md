# Method v0.4 Lane P1: the 2-connected live core

Date: **2026-08-13**. Status: **bounded lemma search; no complete proof**.

This note isolates one obligation from `method_v04_183_proof.md`.  Let `G` be
2-connected, nonbipartite and claw-free, and suppose that some vertex `x` has
exactly one vertex `z` at distance three and no vertex farther away.  Write
`b=b(G)` and `gamma=gamma_c(G)`.  The desired conclusion is

```text
b >= gamma+2.
```

Only the fixed connected Graph Atlas graphs of orders at most 7 and the frozen
McKay connected order-8 file `/tmp/graph8c.g6` were used as countermodel gates.
No graphs were generated.  Each audit command was externally capped at 60
seconds.

## Lemma ladder

### Rung 1: a universal lower bound

The distance hypothesis itself gives

> **Lemma.** `b(G)>=4`.

Indeed, a shortest `x`--`z` path has four vertices and is induced.  Its induced
subgraph is `P4`, hence bipartite.  Consequently the target is already proved
whenever `gamma<=2`.

### Rung 2: the proposed uniform `b>=6` bound is false

Combining `gamma<=4` with the uniform bound `b>=6` would finish this branch.
That bound fails at order 6.  A smallest-order, minimum-edge countermodel in
the Atlas live core is

```text
graph6 = EZEG
n=6, m=7, gamma=3, b=5
edges = 02 05 12 13 23 34 45
qualifying ordered pairs (x,z) = (1,5), (5,1)
```

Thus a proof cannot discard the value of `gamma`.  The same order contains an
even stronger numerical counterexample:

```text
graph6 = EhNG
n=6, m=8, gamma=2, b=4
edges = 01 05 12 15 23 24 34 45
```

Both graphs are 2-connected, claw-free and in the stated distance core.  They
still satisfy the target exactly.

### Rung 3: the exact tiered obligation

After Rung 1, `gamma<=4` reduces the entire 2-connected branch to two precise
induced-bipartite statements:

```text
gamma=3  ==>  b>=5,
gamma=4  ==>  b>=6.
```

Equivalently, the sufficient bound is `b>=gamma+2` only on the two remaining
levels `gamma in {3,4}`.  The fixed-catalogue distributions are:

| catalogue | `(gamma,b)` counts |
|---|---|
| Atlas, orders at most 7 | `(2,4):12`, `(2,5):7`, `(3,5):8`, `(3,6):3`, `(4,6):2` |
| McKay connected order 8 | `(2,4):37`, `(2,5):47`, `(2,6):4`, `(3,5):34`, `(3,6):36`, `(4,6):17`, `(4,7):1` |

Hence there are no fixed-catalogue countermodels to either tier: 32 Atlas and
176 order-8 live-core graphs were checked.

### Rung 4: an explicit sufficient witness

A non-tautological construction that would prove both remaining tiers is:

> **Path-extension proposition.** There is a minimum connected dominating set
> `D` such that `G[D]` is an induced path, and there are distinct vertices
> `p,q` outside `D` for which `G[D union {p,q}]` is bipartite.

If this proposition holds, its displayed induced bipartite graph has
`gamma+2` vertices, proving the target.  It passes all 32 Atlas and all 176
order-8 gates.  This is evidence, not a proof.  Its two assertions must be
proved together: merely finding a path-like minimum connected dominating set
does not identify a usable pair `p,q`.

The weaker existential statement, with no requirement that `G[D]` be a path,
also passes all 208 gates.  Several natural strengthenings do not.

## Smallest countermodels to tempting strengthenings

### The distance-three endpoints need not be the added pair

It is false that one can choose a minimum connected dominating set `D`
disjoint from the qualifying endpoints and use `p=x`, `q=z`.  `EZEG` is again
a smallest countermodel, for both qualifying orientations.  Thus the two
additional vertices in the path-extension proposition must remain free.

### Not every minimum connected dominating set extends

It is also false that every minimum connected dominating set has a suitable
two-vertex extension.  In `EZEG`, the minimum sets are

```text
{0,2,3}, {0,2,5}, {2,3,4}, {3,4,5}.
```

The first and third admit no two-vertex bipartite extension, whereas the
second and fourth do.  The correct quantifier in Rung 4 is therefore
existential.

### Long induced cycles do not supply the tiers

The required bipartite set cannot always be obtained as one induced cycle.
For the `gamma=3` tier, the smallest Atlas example having no induced cycle of
length at least 5 is

```text
graph6 = Fhxgg
n=7, m=11, gamma=3, b=5, longest induced cycle=4
edges = 01 04 12 14 15 23 24 25 36 45 56
```

For the `gamma=4` tier, the order-8 graph

```text
graph6 = GCdedc
n=8, m=12, gamma=4, b=6, longest induced cycle=5
edges = 03 04 06 07 15 16 25 27 34 36 37 67
```

has no induced cycle of length 6.  In both cases a maximum induced bipartite
subgraph exists but is not a single long hole.

## Honest stop point

The attractive uniform lower bound `b>=6` is refuted.  What survives is a
sharper proof programme:

1. the induced `P4` closes `gamma<=2` rigorously;
2. prove only `b>=5` at `gamma=3` and `b>=6` at `gamma=4`;
3. a single path-extension proposition would prove both tiers and has no
   countermodel in either fixed catalogue;
4. its endpoints cannot be prescribed, and its minimum connected dominating
   set cannot be arbitrary.

No claim beyond the fixed catalogues is made for Rungs 3 or 4, and this note
does not prove the full WOWII 183 conjecture.
