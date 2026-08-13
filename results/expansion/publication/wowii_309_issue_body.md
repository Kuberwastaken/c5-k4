## Summary

WOWII Conjecture 309 is still marked `O` on the primary source page. Under the
source-faithful reading

`gamma_t(G) <= (1/2) * (max_v(dist_even(v) - even_horizontal(v)) + min_{e in E(complement G)} |N_{complement G}(e)|)`,

the conjecture is false. This issue tracks a Lean formalization of the
already-published disproof. Jonas J. Gebendorfer recorded the resolution and
the infinite counterexample family `C5[K_k]`, `k >= 3`, on 25 July 2026.

## Counterexample

For `C5[K4]`, the complete certificate proves:

- `gamma_t = 3`;
- `dist_even(v) = 9` for every vertex;
- `even_horizontal(v) = 28` for every vertex;
- `min_{e in E(complement G)} |N_{complement G}(e)| = 16`.

The proposed right-hand side is therefore

`(1/2) * ((9 - 28) + 16) = -3/2`,

contradicting `3 <= -3/2`.

An independent exact verifier reconstructs the graph, certifies total
domination number three, evaluates every vertex and complement edge, checks six
nearby readings, and runs the statement on 994 connected Atlas controls. The
chosen source reading has zero Atlas violations and fails on the witness.

## Relationship to the C5[K4] campaign

This is a formal-certification follow-up to the carrier pattern exposed by the
earlier WOWII 63/85 disproofs. Gebendorfer identified Conjecture 309 as another
application of that carrier and proved the stronger family result. This
submission adds a complete Lean certificate and exact source-reading audit; it
does not claim a new mathematical disproof or first-resolution priority.

The source/status/priority audit and exact verifier are recorded immutably at:

https://github.com/Kuberwastaken/c5-k4/blob/05c3546ca8aa64ecb0a3b8ba456b56b07ba61b12/results/expansion/wowii_309_status_audit.md

https://github.com/Kuberwastaken/c5-k4/blob/57f2826673b2b5b5d3695947900537f9b959b3de/scripts/verify_wowii_309.py

The versioned wall-navigation method is:

https://github.com/Kuberwastaken/c5-k4/blob/460c505162adebfd91ca9864f05166a165ca4cab/METHOD.md

## Complete formal certificate

The complete no-`sorry` Lean 4 certificate is available at:

https://github.com/Kuberwastaken/c5-k4/blob/c9daf0f594d6d5b264c6cd54dc9eec488cb64741/lean/GraphConjecture309.lean

It compiles warning-clean against current `formal-conjectures`. Its trust
assumptions are `propext`, `Classical.choice`, `Lean.ofReduceBool`,
`Lean.trustCompiler`, and `Quot.sound`; there is no `sorryAx` or
project-specific axiom.

## Source/status note

The live WOWII page still marks entry 309 `O`, but the mathematical status is
false by Gebendorfer's dated publication:

https://doi.org/10.5281/zenodo.21553295

The formalization follows the complete-list wording: `e` ranges over edges of
the complement and `N_{complement G}(e)` is the union of the two complement
neighborhoods, including the endpoints. The minimum is represented by an
`Option` because a complete graph has no complement edge; the statement is
vacuous in that undefined case. This totalization does not affect the
counterexample, whose complement has 80 edges.

## AI assistance disclosure

OpenAI Codex and delegated coding agents assisted with source interpretation,
priority research, proof development, independent verification, and
submission preparation. The submitter reviewed the mathematical statement,
attribution, counterexample, and Lean artifact and takes responsibility for
the submission.
