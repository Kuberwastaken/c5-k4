## Summary

Adds a solved formalization of WOWII Conjecture 309 under the source-faithful
reading

`gamma_t(G) <= (1/2) * (max_v(dist_even(v) - even_horizontal(v)) + min_{e in E(complement G)} |N_{complement G}(e)|)`.

Jonas J. Gebendorfer disproved the conjecture with the family `C5[K_k]` for
every `k >= 3`. The linked complete Lean certificate uses `C5[K4]`:

- `gamma_t = 3`;
- `dist_even(v) - even_horizontal(v) = 9 - 28 = -19` for every vertex;
- every complement edge has complement-neighborhood union of order 16.

The proposed bound is therefore `3 <= (-19 + 16)/2 = -3/2`.

Closes #4931.

## Prior result and follow-up discovery pattern

This is a formal-certification follow-up to the `C5[K4]` carrier pattern
exposed by the earlier WOWII 63/85 disproofs. Gebendorfer identified
Conjecture 309 as another application of that carrier and proved the stronger
infinite-family result. This PR adds the source-faithful declaration and an
external no-`sorry` certificate; it does not claim a new mathematical
disproof or first-resolution priority.

Source/status/priority audit:
https://github.com/Kuberwastaken/c5-k4/blob/05c3546ca8aa64ecb0a3b8ba456b56b07ba61b12/results/expansion/wowii_309_status_audit.md

Independent exact verifier:
https://github.com/Kuberwastaken/c5-k4/blob/57f2826673b2b5b5d3695947900537f9b959b3de/scripts/verify_wowii_309.py

## Formal proof

The complete no-`sorry` Lean 4 certificate is linked immutably from the
declaration:

https://github.com/Kuberwastaken/c5-k4/blob/c9daf0f594d6d5b264c6cd54dc9eec488cb64741/lean/GraphConjecture309.lean

Its trust assumptions are `propext`, `Classical.choice`,
`Lean.ofReduceBool`, `Lean.trustCompiler`, and `Quot.sound`; it has no
`sorryAx` or project-specific axiom.

## Source/status note

The live WOWII page still marks entry 309 `O`, but Gebendorfer's disproof was
published on 25 July 2026:
https://doi.org/10.5281/zenodo.21553295

Primary WOWII list:
http://cms.uhd.edu/faculty/delavinae/research/wowII/all.html

The declaration follows the complete-list wording: `e` ranges over edges of
the complement and `N_{complement G}(e)` is the union of the two complement
neighborhoods, including both endpoints. The minimum is represented by an
`Option` because a complete graph has no complement edge; the universal
statement is vacuous in that undefined case. This totalization does not affect
the counterexample, whose complement has 80 edges.

## Verification

- The independent exact verifier passes under its 60-second cap, checks six
  nearby readings, and reports zero violations among 989 applicable connected
  Atlas controls.
- The external certificate passes `lake env lean -DwarningAsError=true` against
  upstream commit `a3d35a75bfa56dbc49c1a0be4d3ce628491d7536`.
- `lake --wfail build FormalConjectures.WrittenOnTheWallII.GraphConjecture309`
  passes on a clean GitHub Actions runner.
- The full upstream warning-as-error corpus build is recorded at:
  https://github.com/Kuberwastaken/c5-k4/actions/runs/31710725372

## AI assistance disclosure

OpenAI Codex and delegated coding agents assisted with source interpretation,
priority research, proof development, independent verification, workflow
development, and submission preparation. The submitter reviewed the
mathematical statement, attribution, counterexample, formalization, and Lean
artifact and takes responsibility for the submission.
