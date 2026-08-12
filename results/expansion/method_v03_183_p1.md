# Method v0.3 Lane P1: WOWII 183 proof extraction

Date: **2026-08-12**. Status: **strictly narrowed theorem signal; no complete
proof claimed**.

This report executes Lane P1 of the frozen v0.3 manifest. It uses only the
previously fixed connected Graph Atlas and McKay order-8 catalogues. No graph
generation, larger-order catalogue, random search, or enlarged bound is used.

## Source correction: the `mu=3` branch is already proved

The primary-source formula in DeLaViña and Waller, *Spanning Trees with Many
Leaves and Average Distance*, Theorem 5, is

```text
L_s(G) >= n - b(G) + ceil(mu(G)/2).
```

Since `L_s(G)=n-gamma_c(G)`, this is exactly

```text
b(G) >= gamma_c(G) + ceil(mu(G)/2).
```

The earlier v0.1 report and the frozen v0.3 manifest transcribed the ceiling as
`floor(mu/2)`. That transcription is too weak. In particular, **every `mu=3`
core already has `b>=gamma_c+2`**. The only live local-independence branch is

```text
mu(G) <= 2,
```

which is precisely the claw-free branch. This is a source audit, not a new
conjectural lemma.

Primary source: Theorem 5 on page 12 of
<https://www.combinatorics.org/ojs/index.php/eljc/article/download/v15i1r33/pdf>.

## Exact remaining implication

The reductions in `method_v01_183_theory.md` remain valid. Put `H=G^2`,
`r=rad(H)`, and `q=n-1-Delta(H)`. The geodesic bound `q>=2r-3` and WOWII 173
settle every case except `q=2r-3`. Safe deletion of the forced singleton tail
leaves a graph of radius three with a centre `x` having a unique vertex `z` at
distance three.

After the corrected Theorem 5 reading, it is enough to prove:

> **Live claw-free core.** If `G` is connected, nonbipartite and claw-free,
> `rad(G)=3`, and some centre `x` has exactly one vertex at distance three,
> then `b(G)>=gamma_c(G)+2`.

The radius condition is retained here because it is what the square-extremal
reduction actually supplies. Dropping it would make the intermediate statement
stronger than needed.

## Failed minimum-CDS proof devices

The fixed-catalogue checker is
[`scripts/method_v03_183_lemma_check.py`](../../scripts/method_v03_183_lemma_check.py).
It independently enumerates all minimum connected dominating sets and maximum
induced bipartite orders.

### Failure 1: avoid both extremal endpoints

The proposed route

```text
choose a minimum connected dominating set D with x,z not in D
```

is false. The smallest exact countermodel is

```text
graph6 = FhoG_
edges  = 01 04 12 14 23 36 45
gamma_c = 4, b = 6, mu = 2
```

Its unique minimum connected dominating set is `{1,2,3,4}`. For the extremal
pairs `(x,z)=(1,6)` and `(2,5)`, the centre belongs to that set. Thus adding the
two named endpoints supplies at most one new vertex, not the two vertices the
argument needs. The target inequality itself is tight and true on this graph.

### Failure 2: enlarge a minimum CDS by two vertices

The more flexible statement

```text
some minimum connected dominating set D and u,v outside D have
G[D union {u,v}] bipartite
```

is also false. Its smallest fixed-catalogue countermodel is

```text
graph6 = G?`aeG
edges  = 04 07 15 16 17 25 36 57
gamma_c = 5, b = 7, mu = 2
unique minimum CDS = {0,1,5,6,7}
```

That minimum set already contains the triangle `1-5-7-1`, so no superset of it
is bipartite. A proof must construct the large induced bipartite set and the
connected dominating set separately, as in the DeLaViña--Waller greedy
argument; it cannot assume the latter sits inside the former.

### Failure 3: bound `gamma_c` by four

The radius-three geodesic gives `b(G)>=2 rad(G)=6`. It therefore proves the live
core whenever `gamma_c<=4`. But `gamma_c<=4` is false in general: the same
order-8 graph `G?`aeG` has `gamma_c=5`.

## Sharpened surviving lemma

Write `tau_odd(G)=n-b(G)` for the minimum odd-cycle-transversal order. The
following strictly narrower dichotomy survives every fixed critical graph:

> **Candidate dichotomy.** In the live claw-free core, either
> `gamma_c(G)<=4` or `tau_odd(G)<=1`.

Either outcome proves the required inequality:

1. If `gamma_c<=4`, an induced radius geodesic has six vertices, so
   `b>=6>=gamma_c+2`.
2. If `tau_odd<=1`, nonbipartiteness gives `b=n-1`. A connected graph has
   `gamma_c=n-2` only when its maximum-leaf spanning trees have two leaves,
   equivalently when it is a path or a cycle. The live core is nonbipartite and
   has a centre with one (not two) distance-three vertices, so it is neither.
   Hence `gamma_c<=n-3` and again `b>=gamma_c+2`.

This candidate is not presented as proved. Its value is that it replaces the
full invariant inequality by a concrete structural assertion: a claw-free
radius-three core with no one-vertex odd-cycle transversal must have a
connected dominating set of order at most four.

## Fixed-catalogue audit

The checker gives the following exact split.

| catalogue | nonbipartite critical | `mu=3` (already proved) | claw-free | candidate-dichotomy failures |
|---|---:|---:|---:|---:|
| Graph Atlas, orders 2--7 | 7 | 0 | 7 | 0 |
| McKay connected order 8 | 140 | 91 | 49 | 0 |

Reproduction:

```bash
timeout 60s python3 scripts/method_v03_183_lemma_check.py
timeout 60s python3 scripts/method_v03_183_lemma_check.py \
  --graph6 /path/to/the/fixed/graph8c.g6
```

All subset optimization is exhaustive and exact. The zero in the final column
is only a bounded audit, not evidence of a proof beyond the frozen catalogues.

## Honest stop point

Lane P1 has advanced in two rigorous ways: the `mu=3` branch is closed by the
correct primary-source theorem, and three tempting connected-dominating-set
lemmas have exact smallest countermodels. The remaining paper obligation is
the candidate dichotomy above (or another lemma implying it). No Lean file is
appropriate yet: the full paper implication has not been proved.
