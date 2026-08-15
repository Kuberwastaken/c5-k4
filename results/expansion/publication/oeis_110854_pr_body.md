## Summary

`OeisA110854.conjecture` was `research open` and stated

```lean
∀ d > 0, (∃ p1 p2 : ℕ, p1.Prime ∧ p2.Prime ∧ d = (p1 - p2 : ℤ).natAbs) →
  ∃ n > 0, d = (a n).natAbs
```

That statement is false, and it is not the question A110854 asks. The only
comment on [A110854](https://oeis.org/A110854) is "Do the absolute values cover
A004275?", and [A004275](https://oeis.org/A004275) is "1 together with the
nonnegative even numbers", not the set of prime differences. The formalized
hypothesis is strictly weaker than `d ∈ A004275`, so the declaration was
strictly stronger than its source.

Counterexample `d = 3 = |5 - 2|`: `a 1 = 7 - 5 - 3 + 2 = 1`, and for `n ≥ 2` the
four primes `prime(2n-1), …, prime(2n+2)` are all odd, so `a n` is even. Hence
`(a n).natAbs ∈ {1} ∪ 2ℕ` for every `n > 0` and `3` is never attained. The same
argument refutes every `d = p - 2` with `p` an odd prime greater than `3`.

**This refutes the formalized statement only. The OEIS question — whether the
absolute values cover A004275 — is untouched and remains open.**

This PR therefore does three things:

1. marks `conjecture` as `answer(False)` with a complete in-repo proof;
2. corrects the docstring, which asserted "A004275 is the set of all differences
   between two prime numbers" (it is not; that error is the likely origin of the
   broadened hypothesis);
3. adds the source-faithful question as `conjecture.variants.oeis_question`,
   tagged `research open`, so the actual OEIS question stays in the file.

If reviewers would rather keep this PR to the disproof alone, item 3 is easy to
drop.

Fixes #4982.

## Follow-up discovery pattern

This came from the statement-audit lane of the C₅[K₄] campaign, which compares
declarations against their cited sources and then searches for witnesses where
the two diverge. It is a formalization counterexample of the same family as the
mismatches collected in #4896 and #4923, not a mathematical advance on A110854.

Source audit and exact witness derivation:
https://github.com/Kuberwastaken/c5-k4/blob/e4e95c3e3adda9dd91cd3e077ec30b0fccb543f9/results/expansion/live-search-2026-08-15/oeis-hunt-part1.md#L203-L272

## Formal proof

The proof is complete and in-repo; nothing is cited externally and no
`formal_proof` link is used. Three `category API` lemmas carry it:

- `odd_nth_prime` — `Nat.nth Nat.Prime k` is odd for `k ≠ 0`, via
  `Nat.nth_mem_of_infinite` and strict monotonicity of `Nat.nth` off
  `Nat.nth_prime_zero_eq_two`;
- `a_add_two` — the defining formula with the truncated-subtraction index
  arithmetic carried out, valid for `n ≥ 2`;
- `even_a` — `Even (a (m + 2))`, from the four odd primes.

`conjecture` then instantiates the hypothesis at `d = 3` with `p1 = 5, p2 = 2`,
splits on `n = 1` versus `n ≥ 2`, and closes the second branch with
`Int.natAbs_even`.

A standalone copy of the same proof, importing only Mathlib, is recorded at:
https://github.com/Kuberwastaken/c5-k4/blob/e4e95c3e3adda9dd91cd3e077ec30b0fccb543f9/lean/OeisA110854Disproof.lean#L1-L163

## Source/status note

- A110854 (OFFSET 1,4) defines
  `a(n) = A155750(n) - A155067(n) = prime(2n+2) - prime(2n+1) - prime(2n) + prime(2n-1)`,
  DATA `1, 0, 0, 4, 0, -4, 4, -4, 2, 2, 0, -2, …`; its single comment is the
  A004275 question.
- The new `conjecture.variants.oeis_question` encodes A004275 as
  `d = 1 ∨ Even d`. It is not vacuous or trivially false at small values:
  `a 1 = 1` supplies `d = 1` and `a 2 = 0` supplies `d = 0`.
- The definition of `a` and the statement of `conjecture` are unchanged; only
  the `answer`/category, the docstring, and the added lemmas are new.

## Verification

- `#print axioms` reports exactly `[propext, Classical.choice, Quot.sound]` for
  `conjecture`, `even_a`, `a_add_two` and `odd_nth_prime`. No `sorryAx`, no
  `native_decide`, no `decide +native`.
- The file's new content elaborates warning-clean under
  `lean -DwarningAsError=true` (Lean 4.27.0, Mathlib `v4.27.0`).
- An independent sieve-based recomputation (primes to `4·10⁶`) reproduces the
  published DATA exactly, finds `n = 1` to be the only `n > 0` with `a n` odd,
  and finds no `n` with `|a n| = 3`:
  https://github.com/Kuberwastaken/c5-k4/blob/e4e95c3e3adda9dd91cd3e077ec30b0fccb543f9/results/expansion/live-search-2026-08-15/scripts/part1/c110854.py#L1-L24
- The two remaining `sorry` tokens in the file are the `answer(sorry)` and proof
  body of the new open `conjecture.variants.oeis_question`.

## AI assistance disclosure

Claude Code and delegated coding agents assisted with the source audit, the
search for the witness, the Lean proof, the independent verification, and the
preparation of this pull request. The submitter reviewed the mathematical
statement, the counterexample, and the Lean artifact, and takes responsibility
for the submission.
