# Formal-conjectures one-off result: WOWII #141

Date: 2026-08-13 UTC

Frozen contract SHA-256:
`32f26e75f9773e7dc3340eaf9e7fe571e7fa496779b1205f9c96421c8f3d1dda`

## Gate-classified result

`NO_APPLICABLE_CANDIDATES`

The sole frozen transformation is infeasible.  There is no connected cyclic
three-sheet voltage lift of `complement(C5[K3])` in the frozen gauge whose
circulation is nonzero on every simple base cycle of length four and five.
Consequently this transformation cannot raise the seed girth from four to at
least six while preserving its covering/local-neighborhood coordinate.

No counterexample candidate was produced, so no status/novelty audit or public
action was triggered.

## Selection result

The selection/rejection table is frozen in
`prospective_formal_oneoff_141_contract.md`.  It uses only the existing
formal-conjectures equality map and excludes Reed, Erdős 23, and exhausted
WOWII 19/40/61/133 as instructed.

WOWII #141 was the sole selection because the map records residual one on
`complement(C5[K3])`, while a cover gives an exact separable coordinate:
degrees and empty neighborhood graphs are preserved, hence
`lambda_max = 6` remains fixed, while cycle voltages can in principle change
girth.

The exact seed row was reproduced:

```text
n = 15, m = 45, girth = 4, lambda_max = 6,
target = 4//2 - 1 + 6 = 7,
largest induced tree = 8, residual = 1.
```

## Database and certificate gate

The exact pre-transformation gate passed all 1,057 controls with no timeout or
certificate mismatch.  It included every connected Graph Atlas graph of order
2--7, all frozen cycles, paths, stars, complete and complete-bipartite graphs,
Petersen, and the residual-one seed.

For every row, the evaluator retained exact girth, all local neighborhood
independence values, an exact maximum induced-tree order, and a replayed
induced-tree witness.  There were zero negative residuals.

## Frozen transformation outcome

The lexicographic BFS gauge has 14 tree edges and 31 cotree voltage variables.
The seed contains 423 simple cycles of lengths four and five.  Each frozen
constraint requires the signed voltage sum around one such cycle to lie in
`{1,2}` modulo three.

The bounded integer linear program returned infeasible in 0.046 seconds.  A
separate exact finite-domain checker then replayed all 423 modular constraints
directly over `{0,1,2}`.  Generalized arc consistency plus branching closed the
search in three states and independently confirmed that no assignment exists.

This is stronger than a failed heuristic search: within the frozen
transformation class, infeasibility is exact.

## Reusable obstruction

The desired invariant separation is blocked at the construction level.  The
dense `K3,3`-type interfaces in the five-part seed create a coupled system of
short-cycle circulation demands.  Individual short cycles can be lifted to
longer cycles, but all 423 length-four/five demands cannot be made nonzero
simultaneously in a cyclic three-cover.

Therefore a future #141 cover lane should not repeat cyclic `Z3` voltage
lifts of this seed.  To move girth while retaining local independence, it
would need either:

- a noncyclic/nonregular covering group with more independent voltage
  coordinates;
- a different residual-one seed without the coupled complete-bipartite block
  structure; or
- a transformation outside graph covers.

This one-off supplies no evidence against #141 itself.  It instead identifies
an exact obstruction to the most direct equality-wall move.

## Artifacts

- Frozen selection and trial contract:
  `results/expansion/prospective_formal_oneoff_141_contract.md`
- Append-only 1,063-line ledger:
  `results/expansion/prospective_formal_oneoff_141_ledger.jsonl`
- Exact evaluator, MILP, and independent modular audit:
  `scripts/prospective_formal_oneoff_141.py`

No commit, push, release, issue, PR, or other public action was made by this
lane.
