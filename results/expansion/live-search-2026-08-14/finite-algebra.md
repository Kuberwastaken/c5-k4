# Live finite-algebra/equational search — 2026-08-14

## Scope and terminal outcome

**Lane outcome: `ZERO_BOUNDED`; no candidate and no novelty claim.** This lane
searched the currently open Latin-square finite-algebra cluster represented by
the literal declarations
`LatinSquare.latinSquareOrder11Transversal`,
`LatinSquare.oddOrderLatinSquareTransversal`, and
`LatinSquare.latinSquareNearTransversal`. The previously completed finite
`Equation 677 -> Equation 255` SAT lane was excluded: it already has a closed
order-5--8 contract and report, so rerunning it would violate the instruction
to select unresolved/unclaimed search work.

The shared object space was order-11 Latin operation tables. A table with no
full transversal would cross both the order-11 declaration and the general
odd-order declaration. Such a table would cross the near-transversal
declaration only if an independent exact search also found no partial
transversal of size 10. No no-transversal table was found, so the
candidate-specific database replay, independent-candidate verification, and
novelty-claim stages were never activated; the general control gate was still
run before interpreting the bounded zero.

## Literal-statement and live-status gates

The current upstream `main` response was audited through the GitHub API before
search. It resolved to
[`b33d8678a28118c95d8d4f60b11faaf39ccff1e6`](https://github.com/google-deepmind/formal-conjectures/commit/b33d8678a28118c95d8d4f60b11faaf39ccff1e6),
committed at `2026-08-13T23:56:30Z`. The raw file at that commit still marks all
three declarations above `category research open` and contains `sorry` bodies.

The matching repository issue
[#2271](https://github.com/google-deepmind/formal-conjectures/issues/2271) is
closed only because the statement-formalization PR
[#3516](https://github.com/google-deepmind/formal-conjectures/pull/3516) merged
on 2026-03-19. The PR is titled `feat(Paper): Add latin square conjectures`;
it did not solve the declarations. A current all-state repository issue/PR
search found later Latin-square changes #4128/#4129 (the already solved even
cyclic-table fact), #4186 (statement restriction to odd order), #4449 (MOLS
formalization), and open module-migration PR #4688, but no claimed proof or
counterexample for the three searched declarations.

The exact finite predicates used in the search were:

- `valid_latin(L)`: every row and column is exactly `{0,...,n-1}`;
- `full(L)`: there is a permutation of columns whose selected symbols are all
  distinct;
- `near(L)`: there are `n-1` cells in distinct rows, columns, and symbols.

Thus the crossing gates were literally `valid_latin(L) and not full(L)` for
the order-11/odd-order pair, followed by `not near(L)` for the near-transversal
sibling. There was no alternate reading or numerical tolerance.

## Frozen arms and budgets

Every launched search or verification process was wrapped in an external
`timeout 60s`. The generic and wall arms used seeds `0,...,7` in eight
single-threaded processes. Their requested internal search horizon was 30
seconds per process (240 process-seconds per arm); a final exact transversal
evaluation was allowed to finish inside the hard 60-second process cap. The
catalogue exhausted naturally in one process rather than idling seven copies
of the same deterministic list.

| arm | frozen construction | budget and realized work | exact outcome |
|---|---|---|---|
| `CATALOGUE` | All 100 affine order-11 quasigroup tables `L(r,c)=a*r+b*c mod 11`, `a,b in {1,...,10}`. These fixed parameter representatives cover the affine/cyclic catalogue; arbitrary row, column, and symbol relabellings were symmetry-pruned because they preserve transversal existence. | One process, hard cap 60 s; natural exhaustion in 0.059015 s; 100 tables checked. | Every table had a full transversal. `ZERO_COMPLETE` for this catalogue. |
| `GENERIC` | Independently generated Latin tables. The first row is fixed by row/symbol symmetry; each later row is a seeded randomized perfect matching in the unused column-symbol bipartite graph, with restart if the forced last row is not a permutation. No target score guides generation. | Eight processes x 30 s requested, each below the 60 s hard cap; maximum realized wall time 30.016474 s. 57,675 generated tables checked (`7,554, 6,972, 7,604, 7,307, 7,214, 6,862, 7,294, 6,868` by seed). | Exact backtracking found a full transversal in every table. Zero crossings. Each full witness also yields a size-10 near transversal by deleting one selected cell. `HOLD_BOUNDED`. |
| `WALL_NAVIGATION` | Start from a generated order-11 table, compute the cycle decomposition of the relative permutation of a chosen row pair, and swap the two rows on one proper cycle. This is a Latin trade that preserves every row and column symbol set. Accept moves that do not increase the exact/capped transversal score, with a frozen 0.03 uphill probability. No backup transformation was used. | Eight processes x 30 s requested, each below the 60 s hard cap; realized wall times 30.095095--35.232683 s. Across the processes: 17 fresh starting tables, 29 defined cycle-trade proposals, and 40 scored states. | The minimum full-transversal count was **3,404**. Counts below the 4,096 enumeration cap are exact, so this minimum is exact and strictly positive. Zero crossings; all scored tables also satisfy the near-transversal statement. `HOLD_BOUNDED`. |

Products were not activated because a nontrivial direct product changes the
literal order 11. Quotients and proper subalgebras were not activated because
they produce a smaller table and no frozen lifting theorem would turn their
transversal behavior into a counterexample to the order-11 universal. The
applicable algebraic symmetry reduction and table-surgery operations were the
canonical first-row normalization and the row-pair cycle trades above.

## Database-sanity and exact-verification gates

Before interpreting any zero, two independent finite paths checked cyclic
Latin controls of orders 3 through 9. The primary recursive exact matcher and
a separate literal permutation enumerator agreed:

| order | full transversal | size-`n-1` near transversal | expected control |
|---:|---|---|---|
| 3 | yes | yes | odd cyclic full |
| 4 | no | yes | even cyclic obstruction, but near |
| 5 | yes | yes | odd cyclic full |
| 6 | no | yes | even cyclic obstruction, but near |
| 7 | yes | yes | odd cyclic full |
| 8 | no | yes | even cyclic obstruction, but near |
| 9 | yes | yes | odd cyclic full |

This gate confirms that the evaluator detects the standard even cyclic
no-transversal obstruction without falsely converting it into a failure of
the near-transversal statement. A second verifier then generated 64 fresh
order-11 tables with seed `8675309`: all 64 passed the Latin row/column test,
all 64 had independently reconstructed full witnesses, and every witness had
11 distinct rows, columns, and symbols. There were zero invalid tables, zero
missing witnesses, and zero malformed witnesses.

No candidate survived discovery, so there is no candidate table for the two
additional 60-second independent-verification processes. In particular, this
report does not promote absence from 57,775 catalogue/generic objects plus 40
wall-scored states (57,815 total evaluations) to a proof of any universal
declaration.

## Receipts and method observations

The search implementation SHA-256 was
`450827c007fbc5c90658c54ac0311514b6f3504d0ce5b421b18182eaab03c55`;
the independent verifier SHA-256 was
`f711be669a35f54d486bdf3edef7eaa6ff719974397bc96ecdbc49f65e896cb4`.
The aggregate verification record SHA-256 was
`955039333ca6bb666799714c3ace2cf4535fa1f5deab6a97f0747984d5f8371a`.
These scripts and raw per-seed JSON records were deliberately kept outside the
repository under `/tmp`; this report is the sole requested durable output.

The main improvement observation is a real cost separation. Exact existence
search is cheap enough to screen tens of thousands of order-11 tables in four
CPU-minutes, while exact transversal counting reduces wall-arm throughput to
40 states in the same nominal budget. The wall arm did locate a low-count
table with exactly 3,404 transversals, but without an equally counted generic
baseline this is a wall coordinate, not evidence of an arm win. A better next
wall contract should use a cheaper certified lower-bound score for most moves
and reserve exact counting for checkpoints. It should also retain the best
positive table, not only a zero candidate, so a second verifier can replay the
reported minimum.

The row-pair cycle move also exposes a structural stop: affine order-11 tables
have a single 11-cycle between each row pair, hence no proper row-pair cycle
trade. Wall navigation needs non-affine generated seeds before this surgery is
available. Enlarging the affine catalogue or merely relabelling its rows,
columns, or symbols cannot change transversal existence.
