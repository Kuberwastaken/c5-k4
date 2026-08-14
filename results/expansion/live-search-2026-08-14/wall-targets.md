# Live wall-target search — 2026-08-14

Scope: current `google-deepmind/formal-conjectures` research-open targets,
ranked by **observed** wall quality after subtracting prior c5-k4 evaluations.
This is a development search, not a prospective benchmark result. No row is a
candidate crossing.

## Current-source and database sanity

The GitHub API resolved upstream `main` to
`b33d8678a28118c95d8d4f60b11faaf39ccff1e6` (committer timestamp
`2026-08-13T23:56:30Z`). Direct content reads at that SHA confirmed that the
following exact declarations remain tagged `research open`:

- `CernyConjecture.cerny_conjecture`, blob
  `f1ba46e9b04edbe9a52e1bdc4e9a5c0f24c26b77`;
- `CatchUp.value_of_even_mul_succ_self_div_two`, module blob
  `ce8251a228ea79a6b2f8414e9eb6b5291a640677`;
- `EquationalTheories_677_255.Finite.Equation677_implies_Equation255`, module
  blob `f5641e3da7b811dca952f00b6fddc3ed3700d0a4`;
- `LatinTableau.SimpleGraph.LatinTableauConjecture`, blob
  `7d5ff013ae3cf5472ee57fbc5250628f07466dda`;
- `OeisA108081.count_words_in_x_is_a_shifted`, blob
  `e8ea8ead2b463cf4fc30dd68047ed595568897bd`;
- the pebbling product, Erdős 628, graceful labeling, Sidorenko, and Erdős 184
  modules, respectively blobs `200b127f...`, `3aa4c369...`, `0de8bcd4...`,
  `872b7fc2...`, and `374dbab4...`, still contain their general research-open
  declarations.

PR #3906 (Černý statement) and PR #1325 (Catch-Up statement) are merged; their
statement issues are closed. Catch-Up API issue #4834 is open and does not
claim a resolution. Searches for the exact target names found no open
resolution PR for Černý, Catch-Up, or the finite Equation 677 implication.
The Equation 677 search did find several closed, **unmerged** solution PRs
(#2733, #3024, #3255); their titles concern other directions or broad mutual
non-implication claims, while the current file still marks the finite
`677 -> 255` implication open. Thus none preempts the literal finite target.

Literal negation sanity used the existing resolution cards rather than a
proxy:

- Černý: a synchronizing finite DFA with shortest reset word greater than
  `(n-1)^2`; non-synchronizing automata fail the premise and are not candidates.
- Catch-Up: an even-triangular-sum `N` whose exact minimax value is nonzero.
- finite Equation 677: a complete finite magma satisfying Equation 677 but
  failing Equation 255. The exact SAT residual is Boolean; SAT is a candidate,
  UNSAT is a bounded hold, and interrupted search is a timeout.

Existing source/database controls were also rechecked before selection:
`cerny13_two_cycle_resolution_card.json`,
`catchup_n23_n24_resolution_card.json`, and
`equation677_255_resolution_card.json` record the current informal and formal
status coordinates, certificate shapes, and literal declaration hashes. No
apparent candidate was produced, so no downstream novelty/database claim was
activated.

## Ranking by observed wall quality

Scores are `0..3` for exact tight seed (`T`), signed/literal residual (`R`),
bounded verifier (`V`), and open-domain safety (`O`). They reflect completed
local evidence, not plausibility of the conjecture.

| rank | current open cluster | T | R | V | O | total | observed wall |
|---:|---|---:|---:|---:|---:|---:|---|
| 1 | finite Equation `677 -> 255` | 3 | 3 | 3 | 3 | 12 | Exact UNSAT through orders 5--7; order 8 is the first solver wall. The premise yields permutation left translations, a sound target-specific strengthening. |
| 2 | Catch-Up | 3 | 3 | 2 | 3 | 11 | Exact draws through the calibrated range and at `N=23`; `N=24` is the immediate even-sum minimax wall. |
| 3 | Černý | 3 | 3 | 3 | 2 | 11 | `C_n` has exact equality `(n-1)^2`. Prior two-cycle surgery destroyed the residual; rank-preserving surgery was still an unresolved structural branch before this run. |
| 4 | Latin Tableau | 2 | 2 | 3 | 3 | 10 | All 176 order-15 diagrams were colorable, but four bottom-corner deletions have non-basis profile redistribution: a narrow exchange wall, not a scalar crossing wall. |
| 5 | OEIS A108081 | 3 | 3 | 1 | 3 | 10 | Exact equality through length 14; length 15 is the literal next row but state growth makes a 60-second process unlikely to finish without a representation improvement. |
| 6 | graph pebbling product | 2 | 2 | 2 | 2 | 8 | The support-63 shell on `L square L` is exactly tight below threshold, but all 4,032 one-extra states have an immediate path relay. A useful wall exists only outside this closed shell. |
| 7 | Erdős 628 (Tihany) | 2 | 3 | 2 | 1 | 8 | The 25-vertex open-domain seed survives an internal-edge deletion, but 115/116 edge complements explicitly retain the required 5-chromatic side; the tested move has poor crossing pressure. |
| 8 | graceful/Kotzig/Ringel | 3 | 1 | 2 | 0 | 6 | Exact difference-set certificates are attractive, but the frozen subdivision lane stays among paths, and all trees through 35 vertices are already in a reported computationally proved domain. |
| 9 | Sidorenko | 1 | 3 | 3 | 0 | 7 | Integer residual is excellent, but no nondegenerate exact finite-host equality wall is available for the certified open pattern; obvious equality seeds are theorem-closed or degenerate. |
| 10 | Erdős 184 | 1 | 1 | 1 | 0 | 3 | The bounded covering variant is theorem-closed (Pyber); the live edge-disjoint statement is asymptotic and cannot be crossed by a bounded finite grid. |

The ordering deliberately favors wall **quality** over raw totals when prior
proof-domain exposure makes a trial non-diagnostic. It also rotates away from
the already saturated WOWII scalar-pattern families.

## Live wall-navigation runs

### 1. Finite Equation `677 -> 255`, order 8

Transformation: extend the exact finite-table search from the completed UNSAT
prefix `n=5,6,7` to `n=8`, retaining the derived wall constraint that every
left translation is a permutation. This strengthening is a theorem of finite
Equation 677 models, not an extra premise. Failure of Equation 255 was fixed at
element `0`, without loss by relabeling.

Command and budget:

```text
timeout --signal=TERM --kill-after=1s 60s \
  python3 scripts/prospective_equation677_255_sat.py \
  --n 8 --cap-seconds 58 --solver cadical195
```

Exact encoding: 512 variables, 36,544 clauses, CNF SHA-256
`1168924d7cf6682c3e7bb947ba51ff935fc0ffbead4fa4a4f15723f3648cd99c`.
Outcome: external exit `124`, no SAT/UNSAT result, wall `60.03s`, user CPU
`56.13s`, system CPU `0.27s`, maximum RSS `65,856 KiB`.

Disposition: `TIMEOUT_BRACKET`; zero candidate tables. The wall is solver
search, not CNF construction or memory.

### 2. Catch-Up, `N=24`

Transformation: extend the normalized exact game from the completed `N=23`
draw to the next contracted even-triangular-sum row `N=24`, preserving the
literal state `(remaining_mask,current_deficit)` and ascending move order.

Build: `g++ -std=c++20 -O3 -Wall -Wextra -Werror`; source SHA-256
`6815d216f88a31ac2e629cfde4dc6b48d929764fb14db555a53fb3bde8066ffd`;
temporary binary SHA-256
`9f0fe8b9dd0e259342edf4959653261ccd246587ed5da9badfb8cd8220f33f32`.

Command and budget:

```text
timeout --signal=TERM --kill-after=1s 60s /tmp/c5k4-catchup-live --n 24
```

Outcome: external exit `124`, no minimax value, wall `60.34s`, user CPU
`55.02s`, system CPU `1.12s`, maximum RSS `1,805,528 KiB`. The last complete
progress checkpoint was 67,000,000 memo states and 562,082,020 recursive calls;
the table had rehashed from 67,108,864 to 134,217,728 slots at 46,976,205
states.

Disposition: `TIMEOUT_BRACKET`; no strategy DAG and no candidate non-draw.
The live run advances much farther than a superficial size sweep and confirms
that hash-table growth, not literal ambiguity, is the active wall.

### 3. Černý `C13`, rank-preserving two-cycle surgery

Transformation: in the standard `C13`, swap the successor images `a(d)` and
`a(12)` for `d=1..6`, splitting the permutation letter into cycles of lengths
`(d+1,12-d)`, while **retaining** the standard defect-one letter
`b(12)=0` and `b(i)=i` otherwise. This is the natural wall-directed repair of
the prior trial, whose extra merge lowered `rank(b)` from 12 to 11 and made
reset words very short.

Budget: one externally capped 60-second Python process; exact BFS over the
8,191 nonempty subsets for every row, using the existing literal transition
and image routines.

| `d` | cycle lengths | `rank(b)` | exact outcome |
|---:|---:|---:|---|
| 1 | 2,11 | 12 | non-synchronizing |
| 2 | 3,10 | 12 | non-synchronizing |
| 3 | 4,9 | 12 | non-synchronizing |
| 4 | 5,8 | 12 | non-synchronizing |
| 5 | 6,7 | 12 | non-synchronizing |
| 6 | 7,6 | 12 | non-synchronizing |

Outcome: all six complete in `0.056890s` internal wall (`0.18s` process wall),
exit `0`, maximum RSS `14,620 KiB`; zero candidate DFAs.

The exact obstruction is structural. The permutation letter preserves two
cycles. The sole defect maps state 12 from one cycle into the other, so it can
drain that source cycle, but on the destination cycle both letters are
injective. Its `d+1 >= 2` states can never be merged. Hence every row fails the
synchronizing premise. This is stronger than another bounded hold: the entire
two-cycle-permutation plus one one-way defect template is the wrong search
geometry unless the destination cycle is a singleton.

## Actionable method changes

1. **Equation 677:** spend the next 60-second process on symmetry reduction,
   not another SAT backend replay. Canonically fix one left translation and
   quotient remaining simultaneous relabelings before clause generation; keep
   the current CNF as the equivalence control. The live memory footprint is
   small enough that search-tree symmetry is the credible bottleneck.
2. **Catch-Up:** replace the oversized flat hash table with a compact
   layer/remaining-mask representation or a disk/checkpoint-capable table
   before rerunning `N=24`. A backend-only retry wastes the observed
   1.8-GiB/67-million-state frontier and cannot produce a replayable result
   inside the same cap.
3. **Černý:** exclude every future two-cycle proposal whose only
   non-permutation letter is a single one-way rank-`n-1` defect and whose
   destination cycle has size at least two. To retain synchronization and the
   defect-one wall, use either a third letter, a non-permutation primary letter,
   or a transformation with an independently proved route that contracts the
   destination cycle.
4. **Selector:** promote literal finite targets with an observed solver wall
   (Equation 677, Catch-Up) above visually tight but theorem-closed equality
   seeds. Require a nondegenerate open-domain equality/near-wall object before
   spending discovery budget on Sidorenko-like density targets.
5. **Outcome discipline:** premise failures from the Černý lane are
   `PREMISE_FALSE_STRICT`, not `HOLD_BOUNDED`; the two 60-second interrupted
   searches are `TIMEOUT_BRACKET`, not evidence for their conjectures.

No candidate, counterexample, proof, issue, PR, release, or other public action
is authorized by these runs.
