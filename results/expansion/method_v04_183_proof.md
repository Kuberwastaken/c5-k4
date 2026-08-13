# Method v0.4 Lane P1: WOWII 183 claw-free core

Date: **2026-08-12**. Status: **paper-proof attempt; no complete proof**.

This note continues the corrected full-core lane in
`method_v03_183_p1.md`. The live proposition is:

> If `G` is connected, nonbipartite and claw-free, and some vertex `x` has
> exactly one vertex `z` at distance three and no vertex farther from `x`, then
> `b(G) >= gamma_c(G)+2`.

Only the previously fixed connected Graph Atlas and McKay order-8 catalogues
are used as falsification gates. Every reported computation was externally
capped at 60 seconds. No new graphs were generated.

## Normalization

Let

```text
tau_odd(G) = n-b(G)
```

be the minimum number of vertices whose deletion makes `G` bipartite. Since
`L_s(G)=n-gamma_c(G)`, the desired inequality is equivalently

```text
L_s(G) >= tau_odd(G)+2.
```

The corrected primary-source Theorem 5 proves this whenever `mu(G)>=3`.
Hence this note considers only `mu<=2`, equivalently claw-free graphs.

## A sound sufficient construction

The following lemma is valid, but its existence hypothesis is not automatic.

> **Deletion lemma.** Let `x,z` satisfy `dist(x,z)=3`. Suppose `B` is an
> inclusion-maximal connected induced bipartite vertex set containing `x,z`,
> and `G[B-{x,z}]` is connected and dominates `x,z`. Then `B-{x,z}` is a
> connected dominating set of `G`. Consequently
> `gamma_c(G)<=|B|-2<=b(G)-2`.

Proof. Let `D=B-{x,z}`. It is connected and dominates `x,z` by hypothesis.
Every vertex outside `B` has neighbors in both color classes of `G[B]`;
otherwise it could be added while preserving connectedness and bipartiteness,
contrary to maximality. If an outside vertex had no neighbor in `D`, both such
neighbors would lie in `{x,z}`. It would therefore be adjacent to both `x` and
`z`, contradicting `dist(x,z)=3`. Thus `D` dominates every vertex. Its size is
`|B|-2<=b-2`. QED.

This isolates a concrete route to the target, but the required `B` need not
exist. One smallest-order exact failure in the full Atlas core is `EYWO` for the
qualifying pair `(x,z)=(2,5)`:

```text
graph6 = EYWO
edges  = 02 12 13 14 24 35
```

Thus the deletion lemma is only a sufficient branch, not the core proof.

## Failed invariant shortcuts

### Odd-cycle transversal versus maximum degree

Every connected graph has a spanning tree with at least `Delta(G)` leaves, so

```text
tau_odd(G) <= Delta(G)-2
```

would prove the target. This proposed lemma is false. Its smallest full-core
countermodel is

```text
graph6 = EhNG
n=6, m=8, Delta=3, tau_odd=2
edges = 01 05 12 15 23 24 34 45
```

Here `tau_odd=Delta-1`, although the target itself still holds.

### Maximum connected bipartite set

It is also false that a maximum induced bipartite subgraph can always be
chosen connected. The smallest full-core countermodel is

```text
graph6 = EtoO
n=6, m=7, b=5
edges = 01 02 03 04 14 23 35
```

Its unique maximum induced bipartite set is disconnected. Hence connectivity
cannot simply be imposed on a `b`-set.

## Structural split suggested by the fixed core

Claw-freeness gives one useful exact fact: deleting any cut vertex creates at
most two components. Otherwise choosing one neighbor in each of three
components produces an induced claw centered at the cut vertex. Equivalently,
every **cut-vertex node** in the block-cut tree has degree at most two. This
does not make the whole block-cut tree a path: a block node may still have
degree greater than two.

The fixed catalogues support, but do not prove, the following two-branch route:

1. every 2-connected live-core graph has `gamma_c<=4`;
2. every live-core graph with a cut vertex and `gamma_c>4` has
   `tau_odd<=1`.

Exact bounded counts:

| catalogue | 2-connected live core | failures of `gamma_c<=4` | cut-vertex live core | failures of (`gamma_c<=4` or `tau_odd<=1`) |
|---|---:|---:|---:|---:|
| Graph Atlas, orders 2--7 | 32 | 0 | 68 | 0 |
| McKay connected order 8 | 176 | 0 | 210 | 0 |

If proved, the second branch finishes immediately: `tau_odd<=1` gives
`b>=n-1`, while `gamma_c<=n-3` because the live nonbipartite graph is neither a
path nor a cycle. The first branch requires an additional lower bound `b>=6`;
that does not follow merely from `ecc(x)=3`, so `gamma_c<=4` alone is not yet a
complete proof route.

The five order-8 live-core graphs with `gamma_c=5` all lie in the cut-vertex
branch and all have `tau_odd=1`:

```text
G?`aeG  G?b@dG  G?qacg  G?qadO  GCQ`e_
```

This observation is developmental evidence only.

## Honest stop point

No complete proof of the claw-free core has been obtained. The durable
progress is:

1. a proved maximal-bipartite deletion lemma, with its existence clause
   sharply separated;
2. smallest exact countermodels to three natural strengthenings;
3. a cut-vertex component bound suggesting a 2-connected/cut-vertex proof
   split, without the stronger and generally false claim that the block-cut
   tree must be a path.

The next paper step is to prove a usable induced-bipartite lower bound in the
2-connected branch and an odd-cycle-transversal statement for the cut-vertex
branch. Neither claim is promoted from bounded data here.
