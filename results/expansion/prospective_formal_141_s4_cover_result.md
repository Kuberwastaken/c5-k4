# WOWII #141 four-sheet `S4` permutation-lift result

Date: 2026-08-13 UTC
Verdict: `NO_APPLICABLE_CANDIDATES`

Frozen contract SHA-256:
`7c52fc5ac4c792ef81734aa628a3c3a4e08affe8913f1af4653053c671e59b55`

## Result

The exact frozen `S4` constraint system is infeasible.  No four-sheet lift of
`complement(C5[K3])` simultaneously makes every base 4-/5-cycle monodromy
fixed-point-free, so no candidate reached the cover/local-`lambda`/girth or
induced-tree decision gates.

This is stronger than another reduction to the earlier cyclic class.  In
`S4`, every cotree variable initially retained all nine derangements: six
4-cycles and three double transpositions.  Those choices include explicit
noncommuting pairs.  Nevertheless, the complete coupled 423-cycle system has
no assignment at all, even before the additional noncommutativity and
transitive-sheet-action applicability requirements matter.

## Database gate

The exact parent gate ran first and passed all 1,057 controls with zero
failures or timeouts.  Every row retained exact girth, all local-neighborhood
independence values, exact maximum induced-tree order, and a replayed witness.
The residual-one seed was reproduced as

```text
n=15, m=45, girth=4, lambda_max=6,
target=7, tree=8, R141=1.
```

## Exact CSP outcome

The deterministic BFS gauge has 14 tree edges and 31 cotree variables.  Every
cotree variable is isolated by at least one short fundamental-cycle
constraint, but unlike `S3` that singleton constraint permits nine rather than
two values.  The exhaustive GAC/branching solver reported:

```text
status = infeasible
branch states = 34
short-cycle constraints = 423
memoized domain states = 3,241
local assignments examined = 7,368,276
cycle-feasible leaves = 0
elapsed = 6.4 seconds
```

A second deterministic run reproduced the status and every structural count.
An independent table audit verified all 24 permutations, composition and
inverse tables, the nine derangements, the 423-cycle enumeration, and full
singleton-cycle coverage of the 31 variables.

## Interpretation

Four sheets genuinely escape the algebraic `S3 -> A3 ~= Z3` collapse, but not
the seed's combinatorial obstruction.  The dense five-part geometry makes the
complete demand “every 4-/5-cycle has no fixed sheet” inconsistent even over
all of `S4`.  Increasing the group from three to four sheets therefore does
not supply a candidate for #141.  Per the frozen protocol, this lane stops
without another cover retuning.

Artifacts:

- frozen contract:
  `results/expansion/prospective_formal_141_s4_cover_contract.md`;
- append-only ledger:
  `results/expansion/prospective_formal_141_s4_cover_ledger.jsonl`;
- exact runner:
  `scripts/prospective_formal_141_s4_cover.py`.

No commit, push, release, issue, PR, or other public action was performed.
