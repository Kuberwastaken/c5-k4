# New upstream targets after the committed inventory

Date: 2026-08-14 UTC

Status: **HONEST ZERO — NO NEW <=60S FINITE COUNTEREXAMPLE LANE**

This is a source/status scout only. It performed **zero target evaluations**.

## Pins and comparison boundary

The latest committed full target inventory is
[`results/benchmark/c0/open-inventory.json`](../../benchmark/c0/open-inventory.json),
whose manifest pins
`google-deepmind/formal-conjectures@7a38c469ec329d0c97c068e03c58834f61628e7e`
(tree `daa36d0d9e82133dfd83488d89594d92b4940fb7`).

At `2026-08-14T19:15Z`, upstream `main` was exactly
`6c0950bec7743f5098c0196c6aee7b22c1ec8005`
(tree `5af0d2a3a319ee2458f8cd061db7c49aeba1b35e`). This is also the
source pin already committed by the completed A108569 campaign. GitHub's
compare endpoint reports `21` commits between the inventory and that tip;
comparison from the A108569 pin to live `main` is `identical` (`ahead_by = 0`).

Thus this report is exhaustive for theorem-bearing modules added or changed
after the committed full inventory, while also recording that **nothing newer
than the A108569 source pin exists to scout**.

## Added open modules

All category checks below are against the exact upstream tip. A merged
formalization PR establishes presence in the corpus, not a mathematical
resolution.

| Added module | Open declaration(s) | Exact file SHA-256 | Source/status disposition |
|---|---|---|---|
| `Arxiv/2104.00502/BarkerSequence.lean` | `barker_conjecture` | `084b802cc01efb2cfc09e7866e348c754f32d88fdcec99671ec3ed035bb45e68` | `research open`; added by merged PR #4793. A counterexample is a finite list, but the source states that odd lengths above 13 are already excluded and the unresolved case is even length above 4. Short bounded enumeration would revisit heavily studied negative territory, not expose a fresh certificate geometry. |
| `Arxiv/2604.08040/Conjecture5_5.lean` | `solvable_of_cyc_lt` | `26669f9461c5c65d8bd69469825057a2210eebee05f2e3a0ff3fedcfb57fc28a` | `research open`; merged PR #4865. Already consumed locally: 65 exact nonsolvable profiles and the complete 63-descriptor wall schedule produced a bounded zero. Excluded as completed development, not reopened. |
| `Books/BugeaudDistributionModuloOne/Problem10_9.lean` | `problem_10_9` | `1f9003a73391a77f81bc8ac762502dc2143d71dcbceaabff7bfdbaa9da8f2d4c` | `research open`; merged PR #4204. It is exactly `type_of% Mahler32.mahler_conjecture`, so it duplicates an inventory target rather than adding a mathematical question. A witness must satisfy infinitely many real inequalities, so it is not a finite certificate lane. |
| `GreensOpenProblems/53.lean` | `green_53` | `de5a19984a32e542ec7643e0d7ed55b4bfa6e066154e794c654c1fb35767176a` | `research open`; merged PR #4392. The statement is answer-wrapped and quantifies over all dimensions with an existential global codimension function. No single finite partition refutes it. |
| `GreensOpenProblems/64.lean` | `green_64`, `green_64.variants.p_sub_one` | `3b846e75e27198a3ac4738bd738ae4c0b7f196e173dc34108c553da5f743279c` | both `research open`; merged PR #4364. Infinitude assertions behind `answer(sorry)` cannot be refuted by a finite prime certificate. |
| `Kourovka/1_40.lean` | `kourovka.«1.40»` | `f80e590093957af6836eaf3bee0df48efa16d21c6bda7279afa0b075916522dd` | `research open`; merged PR #4639. Answer-wrapped and quantifies over arbitrary groups. A finite-group catalogue is not a credible crossing lane: the finite setting lies in the classical nilpotent/Engel regime motivating the problem. |
| `Kourovka/1_74.lean` | `kourovka.«1.74»` | `d7ddaea54da3243a8b60d68ea99d127ad29e6a79a8a2b5d763832628b6951c8a` | `research open`; merged PR #4638. The desired witness is explicitly an infinite Tarski monster with a non-discrete Hausdorff group topology, so no finite certificate arm applies. |
| `Wikipedia/PowerfulNumbersDensity.lean` | `error_term_improvement` | `4e3cc7695d04c06bcf953c28c01d5044c2ff2568c2442ba95e10968a97c208b6` | `research open`; merged PR #4422. Answer-wrapped asymptotic big-O statement; finite computation cannot certify its negation. |

These eight modules contribute nine open declarations, but only Barker has a
literal finite counterexample object. Its certificate checker would be cheap
for a supplied list; the missing piece is a scientifically credible short
search domain, not certificate verification.

## Other changed theorem modules

The same upstream delta modified, but did not add, these target-bearing
modules:

- `ErdosProblems/1063.lean` corrects an `lcm` coercion and documents necessary
  hypotheses; its open upper-bound question was already inventoried.
- `ErdosProblems/92.lean` changes both formerly open variants to
  `research solved`/`answer(False)`.
- `ErdosProblems/940.lean` corrects the `large_integers` range from `r >= 2`
  to `r >= 3`; its remaining open asymptotic questions are not finite-witness
  targets.
- `OEIS/945.lean` renames `conjecture` to `every_prime_occurs`; it does not add
  a target, and failure of an every-prime-occurs assertion has no finite
  non-occurrence certificate.
- `Wikipedia/Mahler32.lean` removes an unnecessary `x != 0` hypothesis. The
  target was already inventoried and remains infinite rather than finitely
  falsifiable.
- `Wikipedia/PompeiuProblem.lean` moves the conjecture and hard direction from
  open to solved false.
- `WrittenOnTheWallII/GraphConjecture100.lean` replaces the incorrect
  complement-diameter reading by the source `degreeL2Norm` reading. This exact
  corrected declaration is already proved locally through
  `lean/GraphConjecture100UpstreamBridge.lean`, so it is excluded as completed.
- `WrittenOnTheWallII/GraphConjecture145.lean` moves from open to solved.
- `WrittenOnTheWallII/GraphConjecture200.lean` moves from open to solved false
  with the already known 11-vertex witness `J??FFBRq}N_`.

The remaining changed files are corpus metadata or README files and create no
declarations.

## Eligibility result

Applying the required subtraction in order gives:

1. remove solved-at-tip declarations;
2. remove aliases/renames of already inventoried targets;
3. remove locally completed, prior-art, and bounded-zero lanes;
4. remove `answer(sorry)` questions whose truth value is not contradicted by
   one finite object;
5. remove infinitude, arbitrary-infinite-group, real-asymptotic, and other
   non-finite-certificate statements;
6. require a motivated search domain whose complete shard fits the 60-second
   cap.

**Survivors: 0.** No GitHub workflow should be created from this delta merely
to make the runner busy.

## Decisive next action

**Recommended next target:** none from this upstream delta. It supplies no
new executable target after the source/status and prior-art gates.

**Equation `677 -> 255`: PRIOR_ART_STRICT_STOP.** The subsequently verified
public record in
[`teorth/equational_theories` issue #1464](https://github.com/teorth/equational_theories/issues/1464)
already contains the same column reduction and reports a DRAT exclusion
through order 10. This invalidates it as a novel prospective run; do not
freeze, dispatch, or present that lane as a new method trial.

**Runner-up:** Barker sequences, but only as a separately labelled
method-calibration negative lane after deriving a symmetry/pruning wall that
reaches a previously unexhausted even length. Do not launch flat enumeration
of small lengths and do not count a bounded zero there as discovery evidence.

**Explicit exclusions:** do not reopen `solvable_of_cyc_lt`; do not duplicate
Mahler through Problem 10.9; do not treat Green/Kourovka/Powerful
`answer(sorry)` declarations as affirmative universal conjectures; and do not
re-search WOWII 100, 145, or 200.
