# TxGraffiti status follow-up: the harmonic-index conjecture is resolved

Audit date: **2026-08-12**. This corrects the status, but not the arithmetic,
in `txgraffiti.md` for C-D / `txg-2507.17780-Conjecture4`:

> If `G` is a nontrivial connected graph, then `mu*(G) <= H(G)`, where
> `mu*` is the minimum cardinality of a maximal matching and `H` is the
> harmonic index.

The arsenal verdict remains correct: every graph evaluated there satisfies the
inequality, and `C5[K4]` is strict (`9 < 10`). The conjecture's **open status
was stale**, however. It was already refuted by Türker Bıyıkoğlu, *A Note on
the TxGraffiti Conjecture about Harmonic Index and Minimum Maximal Matching
Number*, MATCH Commun. Math. Comput. Chem. 96 (2026), 1097--1099,
[doi:10.46793/match.96-3.28425](https://doi.org/10.46793/match.96-3.28425)
(received 2025-10-29).

Chakshu Gupta's later
[*Sharp bounds between the saturation number and the harmonic index*](https://arxiv.org/abs/2606.15761)
gives exact small examples, extremal bounds, and exhaustive minimality results.
In particular, the friendship graph `F4` (four triangles sharing one hub) is a
smallest counterexample, of order nine:

```text
mu*(F4) = 4 > 18/5 = H(F4).
```

Gupta reports an exhaustive exact-arithmetic check of all 12,112 connected
graphs of orders 2 through 8 and finds no counterexample; at order nine there
are eight, with `F4` having the smallest harmonic index among them.

## Why this is the requested invariant-separation move

The failed carrier search used only regular graphs. For every `r`-regular
graph of order `n`, each edge has harmonic weight `1/r`, so

```text
H(G) = (nr/2)/r = n/2,
```

while every matching has at most `floor(n/2)` edges. Thus **regularity itself
is the obstructing invariant**: no regular carrier, triangular graph, or
strongly regular graph can refute C-D.

The friendship family separates exactly that invariant. Let `Fk` consist of
`k` triangles sharing one hub. The `k` pairwise-disjoint rim edges form a
maximal matching, and every maximal matching must meet every rim pair, hence
`mu*(Fk)=k`. But the hub has degree `2k` while every rim vertex has degree 2,
which lowers the harmonic weights:

```text
H(Fk) = 2k/(k+1) + k/2.
```

Consequently `F3` is exactly tight (`mu*=H=3`) and `F4` crosses the wall
(`4 > 18/5`). This is precisely

```text
tight family -> identify regularity as obstruction
             -> introduce hub/rim degree heterogeneity while pinning mu*
             -> counterexample family.
```

It is a strong independent example of the proposed discovery pattern in a
different corpus, but it is **not a new discovery of this campaign**. The
priority and resolution belong to the papers above.

Bıyıkoğlu's more general construction joins `k` disjoint edges to an
independent set of `m` hubs. It keeps `mu*=k` while making `mu*/H` unbounded;
Gupta derives the exact limiting ratio `m+1`.

## Independent verification and database gate

[`scripts/verify_txgraffiti_cd.py`](../../scripts/verify_txgraffiti_cd.py)
uses exact `Fraction` arithmetic and computes `mu*` in two independent ways:

1. bottom-up enumeration of maximal matchings as edge subsets;
2. maximum independent unmatched sets whose deletion leaves a perfect
   matching.

The two computations agree on every test graph. Reproduction output:

```text
atlas gate: 995 connected graphs on 2..7 vertices, all hold
named gate: 24 graphs, all hold
F4: mu*=4 > H=18/5 (gap=2/5)
two independent saturation-number computations agree throughout
```

The named gate contains `C5`--`C9`, `P7`, Petersen, `K3,3`, `K7`, stars, and
complete bipartite controls. No solver or floating-point comparison is used.

## Verdict

`RESOLVED_EXTERNALLY_FALSE`, not a campaign kill. The negative arsenal result
was sound; only the literature/status conclusion was wrong.
