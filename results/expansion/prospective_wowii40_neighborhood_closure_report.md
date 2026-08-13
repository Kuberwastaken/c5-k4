# Prospective WOWII #40 neighborhood-closure report

Date: 2026-08-13
Status: `HOLD_BOUNDED`; no exact crossing

## Exact wall identity

The ten equality rows in the committed #40 checkpoint do not merely have
residual `R` equal to one or two.  With

```text
epsilon = (p + b + 1) mod 2,
R = (n-p) + (n-b) - 2*(n-f),
```

all ten satisfy the single parity-sensitive identity

```text
2*f = p + b + 1 + epsilon,
R - epsilon = 1.
```

Eight rows lie on the odd wall `(epsilon,R)=(1,2)` and two on the even wall
`(epsilon,R)=(0,1)`:

| checkpoint row | n | f | b | p | epsilon | R |
|---|---:|---:|---:|---:|---:|---:|
| `ears_(2,2)_twin0` | 4 | 3 | 3 | 1 | 1 | 2 |
| `subst_1_3_1_clique_complete` | 5 | 3 | 3 | 1 | 1 | 2 |
| `subst_1_3_1_clique_matching` | 5 | 4 | 4 | 2 | 1 | 2 |
| `subst_1_3_1_indep_complete` | 5 | 4 | 5 | 1 | 1 | 2 |
| `subst_2_3_2_indep_complete` | 7 | 5 | 7 | 1 | 1 | 2 |
| `subst_1_3_3_1_indep_complete` | 8 | 5 | 8 | 1 | 0 | 1 |
| `subst_2_4_2_indep_complete` | 8 | 5 | 8 | 1 | 0 | 1 |
| `subst_2_2_4_2_indep_complete` | 10 | 7 | 10 | 2 | 1 | 2 |
| `subst_2_3_2_3_indep_complete` | 10 | 7 | 10 | 2 | 1 | 2 |
| `subst_2_2_4_2_2_indep_complete` | 12 | 9 | 12 | 4 | 1 | 2 |

The frozen derivation is recorded in
[`prospective_wowii40_neighborhood_closure_contract.md`](prospective_wowii40_neighborhood_closure_contract.md).

## Independently frozen separator

For every seed vertex `v`, the trial completed the open neighborhood `N(v)`
to a clique.  This local many-edge operation preserves order and connectivity
but can create overlapping cycles at once.  It is distinct from the earlier
ear, block-substitution, bipartite-block-tree, one/two-edge, and line-graph
lanes.

The prospective coordinate calculation was frozen before evaluation.  If
`a`, `c`, and `d` are respectively the changes in `tau_F`, `tau_B`, and `p`,
then

```text
R' = R - d + c - 2*a.
```

The intended crossing required the doubled forest-deletion burden to outrun
the bipartite and path-cover safeguards.

## Gate and exact result

The database sanity gate ran first.  Exact evaluation of 1,031 controls—every
connected Graph Atlas graph of orders three through seven, paths, cycles and
complete graphs through order nine, Petersen, and `K(a,b)` for
`2 <= a <= b <= 6`—found zero crossings.

The ten seed values and the parity identity were then recomputed exactly.
Their 66 nontrivial vertex closures reduced to 20 isomorphism-distinct graphs
of orders four through twelve.  Every graph completed within the 60-second
limits:

| outcome | count |
|---|---:|
| strict crossings | 0 |
| exact equality | 3 |
| positive slack | 17 |
| timeouts | 0 |

The minimum slack was zero.  The three surviving equality graphs were `K4`,
`K5`, and the five-vertex graph6 witness `D~[`.  All 20 forest, bipartite, and
path-cover witnesses passed a separate structural validation.

## Interpretation

Pure neighborhood densification does increase feedback burden, but in this
bounded wall sample it decreases the maximum induced-bipartite order (and
often the path-cover number) enough to compensate.  It therefore does not
separate the #40 coordinates.  A next separator should preserve a large
induced bipartite witness and avoid improving path cover while increasing
overlapping-cycle burden; repeating local clique closure is not supported by
this trial.

The append-only evidence is in
[`prospective_wowii40_neighborhood_closure_ledger.jsonl`](prospective_wowii40_neighborhood_closure_ledger.jsonl),
and the reproducible runner is
[`scripts/prospective_wowii40_neighborhood_closure.py`](../../scripts/prospective_wowii40_neighborhood_closure.py).

No commit, push, release, issue, PR, or other public action was performed.
