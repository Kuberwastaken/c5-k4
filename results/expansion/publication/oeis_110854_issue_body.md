## Summary

`OeisA110854.conjecture` in `FormalConjectures/OEIS/110854.lean` is tagged
`@[category research open]` and states

```lean
theorem conjecture :
  ∀ d > 0, (∃ p1 p2 : ℕ, p1.Prime ∧ p2.Prime ∧ d = (p1 - p2 : ℤ).natAbs) →
  ∃ n > 0, d = (a n).natAbs
```

with `a n = prime(2n+2) - prime(2n+1) - prime(2n) + prime(2n-1)`.

This statement is false, and it is also not the question that A110854 asks.

The only comment on [A110854](https://oeis.org/A110854) is *"Do the absolute
values cover A004275?"*, and [A004275](https://oeis.org/A004275) is **"1
together with the nonnegative even numbers"** (`0, 1, 2, 4, 6, 8, 10, …`) — it
is not the set of differences of two primes. The formalized hypothesis
"`d` is an absolute difference of two primes" is strictly weaker than
`d ∈ A004275`, because every `d = p - 2` with `p` an odd prime is an absolute
prime difference and is odd and `> 1`, hence not in A004275. The declaration is
therefore strictly stronger than its source, and exactly that extra strength
fails.

**The OEIS question itself is untouched and remains open.** What is refuted is
the formalized statement, not the coverage of A004275.

The file's docstring also states "A004275 is the set of all differences between
two prime numbers", which is incorrect and is presumably where the broadened
hypothesis came from.

## Counterexample

`d = 3`.

The hypothesis holds: `3 > 0`, and `p1 = 5`, `p2 = 2` are prime with
`(5 - 2 : ℤ).natAbs = 3`.

The conclusion fails for **every** `n > 0`:

- `n = 1`: `a 1 = prime(4) - prime(3) - prime(2) + prime(1) = 7 - 5 - 3 + 2 = 1`,
  so `(a 1).natAbs = 1 ≠ 3`.
- `n ≥ 2`: the four indices `2n-1, 2n, 2n+1, 2n+2` are all `≥ 3`, so each of
  `prime(2n-1), prime(2n), prime(2n+1), prime(2n+2)` is an odd prime, and
  `odd - odd - odd + odd` is even. Hence `a n` is even and `(a n).natAbs ≠ 3`.

Therefore `{(a n).natAbs : n > 0} ⊆ {1} ∪ 2ℕ`, and `3` is in neither part. This
is a proof for all `n`, not a bounded check.

The same argument refutes every `d = p - 2` with `p` an odd prime greater
than `3`, i.e. `d = 5, 9, 11, 15, 17, 21, 27, 29, 35, …`.

## Relationship to the C₅[K₄] campaign

This came out of the campaign's statement-audit lane, which compares
`formal-conjectures` declarations against their cited sources and then looks for
witnesses where the two diverge. It is a formalization counterexample of the
same kind as the source/statement mismatches collected in #4896 and #4923, not a
mathematical advance on A110854.

The source audit, the exact witness derivation, and the duplicate search are
recorded immutably at:

https://github.com/Kuberwastaken/c5-k4/blob/e4e95c3e3adda9dd91cd3e077ec30b0fccb543f9/results/expansion/live-search-2026-08-15/oeis-hunt-part1.md#L203-L272

The result ledger entry is at:

https://github.com/Kuberwastaken/c5-k4/blob/e4e95c3e3adda9dd91cd3e077ec30b0fccb543f9/results/expansion/live-search-2026-08-15/CONFIRMED_LEDGER.md#L29

## Independent verifier

An independent sieve-based recomputation (primes to `4·10⁶`, replaying the Lean
definition of `a` including the truncated-subtraction indexing) reproduces the
published DATA `1, 0, 0, 4, 0, -4, 4, -4, 2, 2, 0, -2` exactly, finds `n = 1` to
be the only `n > 0` with `a n` odd, and finds no `n` with `|a n| = 3`:

https://github.com/Kuberwastaken/c5-k4/blob/e4e95c3e3adda9dd91cd3e077ec30b0fccb543f9/results/expansion/live-search-2026-08-15/scripts/part1/c110854.py#L1-L24

The bounded scan only agrees with the parity argument; the parity argument is
what settles the `∀`.

## Complete formal certificate

A no-`sorry` Lean 4 certificate that proves `False ↔ <the declaration above>`,
using the upstream definition of `a` verbatim:

https://github.com/Kuberwastaken/c5-k4/blob/e4e95c3e3adda9dd91cd3e077ec30b0fccb543f9/lean/OeisA110854Disproof.lean#L1-L163

Lean 4.27.0 with Mathlib `v4.27.0`. It elaborates warning-clean under
`-DwarningAsError=true`, and `#print axioms` reports exactly
`[propext, Classical.choice, Quot.sound]` for `conjecture`, `even_a`,
`a_add_two` and `odd_nth_prime`. There is no `sorryAx`, no `native_decide` and
no project-specific axiom.

## Source/status note

- A110854 (OFFSET 1,4) defines
  `a(n) = A155750(n) - A155067(n) = prime(2n+2) - prime(2n+1) - prime(2n) + prime(2n-1)`,
  DATA `1, 0, 0, 4, 0, -4, 4, -4, 2, 2, 0, -2, 0, 0, 0, -2, …`. Its single
  comment is "Do the absolute values cover A004275?".
- A004275 is "1 together with the nonnegative even numbers".
- Because `a 2 = 0` and `a 1 = 1`, the source question is not trivially false at
  its own small values; the parity obstruction above is specific to the odd
  `d > 1` that the broadened hypothesis lets in.
- Suggested resolution: mark `conjecture` as `answer(False)` with the proof
  above, correct the docstring's description of A004275, and keep the
  source-faithful question as a separate `research open` statement.

## AI assistance disclosure

Claude Code and delegated coding agents assisted with the source audit, the
search for the witness, the Lean proof, the independent verification, and the
preparation of this report. The submitter reviewed the mathematical statement,
the counterexample, and the Lean artifact, and takes responsibility for the
submission.
