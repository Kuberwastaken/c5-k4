# Wave-two finite targets — 2026-08-14

## Outcome

**`ZERO_BOUNDED`; no literal counterexample candidate.** Three structural
second-wave arms were run under equal external hard caps of 60 seconds. This
was not a longer replay of either excluded wall: Equation `677 -> 255` at
order 8 and Catch-Up `N=24` were not run.

The selected moves came directly from the first-wave reports:

1. replace expensive exact Latin-square counting during navigation by a cheap
   randomized full-transversal witness score, retaining exact counting only at
   record checkpoints;
2. repair the proved one-way two-cycle obstruction for Černý automata by adding
   a third, independently placed rank-12 defect letter;
3. test the proposed Latin Tableau one-defect exchange mechanism on the four
   exposed order-15 profile redistributions and then on further matching
   profile walls, rather than performing another undirected order sweep.

No candidate existed to notify or replay. Candidate hooks were frozen in the
search: a Latin zero would have been replayed after reversing the row order,
and a Černý length above 144 after reversing letter enumeration. Neither hook
activated. The retained noncandidate extrema were nevertheless replayed by
independently encoded exact evaluators.

## Live source and claim-status gate

The GitHub API resolved upstream `main` to
`b33d8678a28118c95d8d4f60b11faaf39ccff1e6`, committed
`2026-08-13T23:56:30Z`. Direct raw reads at that commit found all searched
declarations still tagged `@[category research open]`.

| target | source SHA-256 | live issue/PR audit |
|---|---|---|
| `LatinSquare.latinSquareOrder11Transversal` (and the stronger general odd-order declaration) | `16305fddbd8e1545a75caf8c8f7efa6f368d5c96a01a7892d5fbc6eaa8929195` | statement PR #3516 is merged; repository-wide search found only the solved even-cyclic-table PR #4129 and no resolving transversal claim |
| `CernyConjecture.cerny_conjecture` | `a370ccc0e20edf6c2d7af7aa8638a224a47dfdbe28125fbdf8f78ab3deb0cd12` | statement PR #3906 is merged; exact-name search found no proof/disproof PR |
| `LatinTableau.SimpleGraph.LatinTableauConjecture` | `b5313175ebe43aad389eefca4f34e085366dd7e1cf3ccd5291aa645f3b188271` | statement PR #1385 and later semantic bugfix PR #4554 are merged; the current post-fix declaration remains open and no resolving PR was found |

The predicates were literal: a valid order-11 Latin table with no full
transversal; a synchronizing 13-state DFA whose exact shortest reset word is
greater than 144; and the current post-#4554 CDS-coloring/profile objects for
Latin Tableau. The third arm probes the exposed induction structure; absence
of an exchange certificate is not itself a counterexample to the declaration.

## Equal hard-60-second arms

Each subprocess used GNU `timeout --signal=TERM --kill-after=1s 60s` and
flushed JSON progress after controls, record improvements, and periodic
checkpoints. The two discovery loops used a 58-second internal horizon so
their final exact checkpoint could serialize within the common external cap.

### Arm 1 — order-11 Latin-square cheap-score navigation

The first-wave exact-count wall evaluated only 40 states. This arm instead
scored a table by 48 seeded randomized greedy transversal attempts. It moved
among valid Latin tables using proper-cycle trades between row pairs, accepted
non-increasing scores (plus a frozen 0.02 escape probability), and performed
exact capped backtracking only when the proxy reached a new minimum. Seed:
`11082026`.

Exact controls correctly found no transversal in the cyclic order-8 table and
a transversal in cyclic order 7. In 58.92 seconds the arm proposed **30,715**
cycle trades and accepted **12,406**. The proxy reached zero after 13 proposals,
but the exact checkpoint already found at least 256 transversals, demonstrating
that this particular 48-trial proxy is too noisy to order the deep positive
wall. The retained valid table had **3,533** transversals exactly, below the
first wave's retained minimum of 3,404 only in quality, not in value.

An independent memoized `(row, used-columns, used-symbols)` counter replayed
the retained table and also obtained exactly 3,533 transversals after 169,648
states. Thus this arm produced zero no-transversal tables and no crossing.

### Arm 2 — Černý third-letter rescue

For each first-wave two-cycle permutation obtained by swapping the standard
13-cycle outputs at `d` and 12 (`d=1,...,6`), the standard one-way defect
`b(12)=0` was retained and a third identity-except-one-merge letter
`c(src)=dst` was varied. Exact BFS ran on the complete 8,191-state nonempty
subset automaton. This is a new three-letter encoding of the structural repair,
not a timeout extension of the failed two-letter family.

The exact control reproduced the standard `C13` reset length **144**. In
58.09 seconds the arm evaluated **3,143** rows; **987** synchronized. The
maximum exact reset length was only **50**, at `(d,src,dst)=(4,3,5)`, leaving
a signed residual of `144-50=94`. No row exceeded the conjectured bound.

A separate replay precomputed each letter's image for every subset and used
set-valued BFS layers rather than the discovery queue. It again returned reset
length 50 and reached 8,179 subsets. The added defect repairs synchronization
in many rows but creates strong shortcuts; it does not preserve the slow
Černý geometry.

### Arm 3 — Latin Tableau one-defect exchange wall

The arm computed every profile coordinate as an exact capacitated bipartite
max flow, searched child CDS colorings by MRV backtracking, and tested whether
the two relevant color matchings contained a connected component with the
one-unit imbalance needed by the proposed Kempe exchange, while the insertion
color avoided the new corner's column. It first evaluated the four order-15
exceptions and then streamed only bottom-corner shapes of orders 16--22 with
profile delta `e_a-e_b+e_c`.

The calibration shape `(3,2,1)` had exact profile `(3,2,1)`. The four exposed
deltas were reproduced exactly:

```text
(7,3,3,1,1)     0,1,-1,1,0,0,0
(5,5,2,1,1,1)   0,0,0,1,-1,1
(4,4,4,2,1)     0,0,1,-1,1
(4,4,4,1,1,1)   0,0,1,-1,0,1
```

The corrected arm reached the hard cap at exactly 60.00 seconds (exit 124,
57.99 user seconds, 16,568 KiB peak RSS). It completed and serialized **15**
one-defect shapes, including all four order-15 exceptions. A valid child CDS
coloring was found for every completed row, but the single returned coloring
in each row exposed no qualifying bichromatic component. The next backtracking
row was interrupted before serialization.

Disposition: **`TIMEOUT_BRACKET`**, not an exhaustive absence result. It shows
that “take the first CDS coloring” is insufficient even on all four motivating
walls. A useful next encoding must make component imbalance part of the
coloring search constraints, rather than coloring first and inspecting one
solution afterward.

## Verification, receipts, and interpretation

The final search script SHA-256 was
`f7fbaad02a5b0788e39a6cc577aa9defab534d8d13b5bfd95ad6df4f920f184b`.
Incremental-log SHA-256 values were
`ed9e57d61e64b3baf353999e86fcc08ffa701a9d5736d3566d48edac36bf1889`
(Černý),
`a6f880c2ebfd1d43db0bbfaaee0bd232a3710460613cb25b493697fc3a83bf89`
(Latin square), and
`814e1b847b3cf68acadd9d126424209a67c5e361776b7592b14b6d6957b5c9c3`
(corrected Latin Tableau arm). Temporary scripts and raw logs were kept under
`/tmp`; this report is the sole durable artifact from this lane.

The first-wave recommendations were directionally useful but now separate
cleanly. Cheap Latin witness sampling improves throughput by roughly three
orders of magnitude, yet its zero score did not correlate with the exact deep
wall; a better certified lower-bound proxy is still needed. A third Černý
letter restores synchronization but destroys reset distance. The Latin
Tableau exchange idea remains the most structurally faithful next move, but it
must be encoded jointly with coloring feasibility. None of these bounded
results supports a proof, disproof, issue, PR, or publication claim.
