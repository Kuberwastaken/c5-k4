# Method v0.3 Lane P1: WOWII 183 proof extraction

Date: **2026-08-12**. Status: **strictly narrowed theorem signal; no complete
proof claimed**.

This report advances Lane P1 of the frozen v0.3 manifest. It uses only the
previously fixed connected Graph Atlas and McKay order-8 catalogues. No graph
generation, larger-order catalogue, random search, or enlarged bound is used.

## Source correction: every `mu>=3` branch is already proved

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
`floor(mu/2)`. That transcription is too weak. In particular, **every
`mu>=3` core already has `b>=gamma_c+2`**. The only live
local-independence branch is

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
leaves a graph having a vertex `x` with a unique vertex `z` at distance three
and no vertex farther from `x`.

After the corrected Theorem 5 reading, it is enough to prove:

> **Live claw-free core.** If `G` is connected, nonbipartite and claw-free,
> and some vertex `x` has exactly one vertex at distance three and no farther
> vertex, then `b(G)>=gamma_c(G)+2`.

No assertion about `rad(G)` follows from this hypothesis: `x` has eccentricity
three, but another vertex may have eccentricity two. The full-core audit below
therefore filters on the stated eccentricity-layer condition, not on radius or
the pre-pruning square equality.

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

is false. The smallest full-core fixed-catalogue countermodel is

```text
graph6 = EJe?
edges  = 04 05 12 13 23 34
gamma_c = 3, b = 5, mu = 2
```

Its unique minimum connected dominating set is `{0,3,4}`. For the qualifying
pair `(x,z)=(3,5)`, `x` belongs to that set. Thus adding the two named endpoints
supplies at most one new vertex, not the two vertices the argument needs. The
target inequality itself is tight and true on this graph.

### Failure 2: enlarge a minimum CDS by two vertices

The more flexible statement

```text
some minimum connected dominating set D and u,v outside D have
G[D union {u,v}] bipartite
```

is also false. Its smallest full-core fixed-catalogue countermodel is

```text
graph6 = Fg?hg
edges  = 01 12 25 26 36 45 56
gamma_c = 4, b = 6, mu = 2
unique minimum CDS = {1,2,5,6}
```

That minimum set contains the triangle `2-5-6-2`, so no superset of it is
bipartite. A proof must construct the large induced bipartite set and the
connected dominating set separately; it cannot assume the latter sits inside
the former. The order-8 claw-free graph `G?`aeG` is another exact countermodel
and additionally has `gamma_c=5`.

### Failure 3: bound `gamma_c` by four

The auxiliary assertion `gamma_c<=4` is false on the full claw-free core. The
smallest fixed-catalogue countermodels have order eight; one is
`G?`aeG`, with `gamma_c=5`, `b=7`, and `mu=2`. No residual dichotomy is promoted
from the narrower square-critical audit.

## Fixed-catalogue audit

The checker gives the following exact split. The **full core** column is exactly
the frozen post-pruning proposition. The **square-critical subset** additionally
requires `q=2 rad(G^2)-3` and restricts `x` to maximum-degree vertices of
`G^2`; it is retained only to compare with the earlier verifier.

| catalogue | full core | full core `mu>=3` (Theorem 5) | full core claw-free | target failures | square-critical subset | square-critical claw-free |
|---|---:|---:|---:|---:|---:|---:|
| Graph Atlas, orders 2--7 | 441 | 341 | 100 | 0 | 7 | 7 |
| McKay connected order 8 | 6,326 | 5,940 | 386 | 0 | 140 | 49 |

The failed-lemma counts on the full core are:

| catalogue | endpoint-avoidance failing `(x,z)` pairs | minimum-CDS-plus-two failing graphs | `gamma_c<=4` failing claw-free graphs |
|---|---:|---:|---:|
| Graph Atlas, orders 2--7 | 96 | 2 | 0 |
| McKay connected order 8 | 1,200 | 39 | 5 |

Reproduction:

```bash
timeout 60s python3 scripts/method_v03_183_lemma_check.py
timeout 60s python3 scripts/method_v03_183_lemma_check.py \
  --graph6 /path/to/the/fixed/graph8c.g6
```

All subset optimization is exhaustive and exact. The target's zero failures
are only a bounded audit, not evidence of a proof beyond the frozen catalogues.

## Honest stop point

Lane P1 has advanced in two rigorous ways: every `mu>=3` branch is closed by
the corrected primary-source theorem, and three tempting
connected-dominating-set lemmas have exact countermodels. The full frozen core
still has 100 Atlas and 386 order-8 claw-free instances, all holding but not
proved in general. No Lean file is appropriate yet: the full paper implication
has not been proved.
