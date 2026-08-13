# Method v0.50: WOWII 61 sparse high-feedback bead gate

## Outcome

The frozen trial stops at the bead-coordinate gate as **`INCONCLUSIVE`**. No
development graph was constructed or evaluated.

Five of the six preregistered rooted beads match their predicted order, root
eccentricity, and exact maximum induced-forest order. The frozen `Cube3`
prediction does not: the 3-cube has maximum induced forest five, not six.
The contract explicitly states that any bead-coordinate mismatch stops the
trial rather than repairing or replacing the menu, so the planned 468-graph
family remains unevaluated.

No commit, push, issue, PR, release, or other public action was taken by this
trial.

Artifacts:

- `results/expansion/prospective_wowii61_sparse_feedback_bead_contract.md`;
- `results/expansion/prospective_wowii61_sparse_feedback_bead_ledger.jsonl`;
- `scripts/prospective_wowii61_sparse_feedback_bead.py`.

## Gates

The database sanity gate ran first and reproduced all 1,030 established
controls with no negative residual or timeout:

| residual | 0 | 1 | 2 | 3 | 4 | 5 |
|---:|---:|---:|---:|---:|---:|---:|
| graphs | 159 | 574 | 281 | 10 | 5 | 1 |

The subsequent exact bead gate used decreasing-cardinality exhaustive subset
enumeration and all-source shortest paths:

| bead | predicted `(n,rho,forest)` | measured `(n,rho,forest)` | status |
|---|---|---|---|
| `Prism3` | `(6,2,4)` | `(6,2,4)` | pass |
| `K3,3` | `(6,2,4)` | `(6,2,4)` | pass |
| `Cube3` | `(8,3,6)` | `(8,3,5)` | **mismatch** |
| `Petersen` | `(10,2,7)` | `(10,2,7)` | pass |
| `PetersenSub` | `(11,3,8)` | `(11,3,8)` | pass |
| `Heawood` | `(14,3,10)` | `(14,3,10)` | pass |

For `Cube3`, vertices `{0,1,2,4,5}` form an induced forest of order five.
Exhaustive rejection of every subset of orders six, seven, and eight supplies
the upper certificate. Equivalently, every feedback vertex set of the cube has
at least three vertices.

## Interpretation

The failed prediction is mathematically useful: the cube is a stronger sparse
feedback block than assumed. Under a corrected coordinate it would contribute
five forest vertices for feedback loss three, potentially improving the
intended threshold geometry. But using that fact now would be retrospective
retuning of this frozen family. A future trial may preregister a corrected menu
as a new experiment; this one remains stopped and its development outcome is
unknown.

