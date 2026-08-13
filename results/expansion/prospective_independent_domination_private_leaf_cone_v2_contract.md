# Frozen v2 analytic trial: private-leaf cone for Conjecture 1.6

Frozen: **2026-08-13 UTC, after a fresh semantic gate and before evaluation**

This is a new trial identity, not a repair of the terminally failed v1 lane.

## Passed semantic gate

The executable v2 gate fetched current `upstream/main`, checked the live
`research open` declarations `independentDominationEven` and
`independentDominationOdd`, and matched both formulas and the isolate-free
premise. It inspected the primary arXiv TeX semantically through the labeled
conjecture environment `con:idset-general`, rather than relying on a rendered
title. The paper proves `D<=4` and reports omitted checks for `D=5,6,7,8`.
Issue #227 and merged PR #1373 only added the open declarations; the exact
search found no resolving issue or PR.

## Exact quotient coordinates

For a clique of `q>=2` centers with positive private-leaf vector `p`, put

```text
M=max p_j, S=sum p_j, T=S-M.
D=q-1+M, i=1+T, n=q+M+T.
```

The proved private-leaf formula supplies `i`. Direct algebra reduces the
formal right-minus-left residuals to

```text
even D: D(D^2-4T),
odd D:  D(D^2-1-4T).
```

## Frozen bounded domain and stop rule

Evaluate exactly every realizable quotient triple with

```text
2 <= q <= 32, 1 <= M <= 32,
q-1 <= T <= (q-1)M, D=q-1+M >= 9.
```

The canonical vector has first entry `M`, all remaining entries initially one,
then distributes `T-(q-1)` greedily by increasing index. Evaluate triples in
lexicographic `(D,q,M,T)` order. Stop at the first negative residual and move
to independent graph/novelty verification. If none is negative, report all
bounded equality data and extract a theorem for the full positive-vector cone.
No adaptive extension is authorized.

Every process is capped at 60 seconds. The ledger is append-only. No commit,
push, release, issue, PR, or public action is authorized.
