## Summary

`FormalConjectures/OEIS/108864.lean` defined its membership predicate as
`0 < n ∧ |σ₁(n) − 2n| ≤ 10`, while the file's own docstring — and
[A108864](https://oeis.org/A108864)'s NAME — say *"the perfect deficiency of `n` is `≤ 10`"*.
The perfect deficiency is [A109883](https://oeis.org/A109883), a greedy divisor-subtraction
quantity, not the deviation from perfection.

The two sets are provably different from published data alone. `24` is the twentieth term of
A108864's DATA and its perfect deficiency is `0` (`24 − 1 − 2 − 3 − 4 − 6 − 8 = 0`), but
`σ₁(24) = 60` and `|60 − 48| = 12 > 10`, so the old predicate rejected a term the source lists.
Conversely `56 ∉ A108864` (perfect deficiency `20`) yet `σ₁(56) = 2 · 56`, so the old predicate
accepted it.

The drift also decided the open statement. Under `|σ₁(n) − 2n| ≤ 10` the sequence has
`a 67 = 8925`, which is odd with `67 > 58`, so `∀ n > 58, Even (a n)` was false and the
`answer` hole on a `research open` declaration was already forced to `False`. Further odd terms
appear at `a 74 = 32445` and `a 94 = 442365`.

This PR replaces the predicate with the perfect deficiency itself and leaves the conjecture
open. It does not resolve A108864's question, which was never in danger: `8925` has perfect
deficiency `2969` and is not a term of A108864 at all, and the real sequence has no odd term
after `1155` up to `3 · 10⁵`.

Fixes #4984

## Follow-up discovery pattern

The bound in the statement is what exposed the drift. `∀ n > 58, Even (a n)` encodes *"1155 is
the last odd term"*, and `1155` sits at 0-indexed position **58** in the published A108864 — but
at position **52** in the set the old predicate defined. The index arithmetic had been
calibrated against the real sequence while the predicate defined a different one, so comparing
a declaration's numeric constants against the sequence its predicate actually generates is a
cheap and general detector for this class of mis-encoding.

## Formal content

No proof is added and none is claimed. `conjecture` keeps `answer(sorry)` and
`@[category research open]`; its statement text is unchanged. What changed is the set it is
about.

- `perfectDeficiency` is new:
  ```lean
  def perfectDeficiency (n : ℕ) : ℕ :=
    ((List.range (n + 1)).filter (· ∣ n)).foldl (fun r d => if r < d then r else r - d) n
  ```
  `(List.range (n + 1)).filter (· ∣ n)` lists the divisors of `n` in increasing order. The
  single guard `if r < d` captures both stopping rules of A109883's description: once the
  remainder is below one divisor it is below every later one, so the fold is constant
  thereafter; and for `n > 1` the divisor `n` is never subtracted, because the remainder is
  already `< n` after `1` has been. For `n = 1` the only divisor `1` is subtracted, giving `0`,
  the value A109883 records. `perfectDeficiency 0 = 0`, and `A`'s `0 < n` guard keeps that junk
  value out of the sequence.

  Divisors are listed by filtering a range rather than by sorting `Nat.divisors` because the
  fold needs them in increasing order and the filtered range reduces in the kernel;
  `Finset.sort` does not reduce under `decide`, which made the `test` theorems fail.
- `mem_divisorList_iff` (new, `category API`) proves the filtered range is exactly
  `Nat.divisors n` for `0 < n`, so the definition is not silently folding over the wrong list.
- `perfectDeficiency_values` (new, `category test`) pins A109883's first ten published terms.
- `a_19 : a 19 = 24` (new, `category test`) pins the term that separates the two readings — it
  is exactly the value the old predicate got wrong.
- `a_0`…`a_4` are unchanged and still pass; `1, 2, 3, 4, 5` lie in both sets.
- The module docstring now names A109883, states the distinction, and cites both sequences.

## Source/status note

- A108864 (OFFSET `1,2`): *"Numbers n such that the perfect deficiency of n (A109883) is
  <= 10"*. Sole comment: *"Is 1155 the last odd number in this sequence?"* — the statement
  `conjecture` formalizes. Status: **open**, before and after this PR.
- A109883: *"Start subtracting from n its divisors beginning from 1 until one reaches a number
  smaller than the last divisor subtracted or reaches the last nontrivial divisor < n. Define
  this to be the perfect deficiency of n."*
- The file entered the repository in #4450 (`Add the first 64 files from AutoOeis`), the only
  commit that has ever touched it. The mismatch looks like an automated reading of "perfect
  deficiency" as the abundance/deficiency `|σ₁(n) − 2n|`.
- Alternative repair considered and rejected: keep `|σ₁(n) − 2n| ≤ 10` and close the
  declaration with `answer(False)` and the `n = 67` certificate. That is sound as Lean, but it
  would record a refutation of a conjecture that has not been refuted and would leave the
  docstring, the A108864 reference and the `58` describing a sequence the file no longer
  defines. AGENTS.md (*"Each statement must say what its source says"*) and the shape of #4933
  point the other way. Issue #4984 states the trade-off; if you prefer the `answer(False)`
  form, the `n = 67` witness there is exactly what it would certify and the switch is
  mechanical.

## Verification

`lake --wfail build 'FormalConjectures.OEIS.«108864»'` — passes, warning-clean, exit 0
(Lean `v4.27.0`, repo-pinned Mathlib).

`#print axioms`:

```
'OeisA108864.perfectDeficiency_values' depends on axioms: [propext]
'OeisA108864.mem_divisorList_iff'      depends on axioms: [propext, Classical.choice, Quot.sound]
'OeisA108864.a_0'                      depends on axioms: [propext, Classical.choice, Quot.sound]
'OeisA108864.a_19'                     depends on axioms: [propext, Classical.choice, Quot.sound]
'OeisA108864.conjecture'               depends on axioms: [propext, sorryAx, Classical.choice, Quot.sound]
```

No `decide +native`, no `native_decide`, no `Lean.ofReduceBool` / `Lean.trustCompiler`.
`conjecture` carries `sorryAx` by design.

Evaluated from the new definition and matching the published data:

| Check | Result |
|---|---|
| A109883's first **79** published terms | reproduced exactly |
| A108864's **61** published DATA terms, from `perfectDeficiency n ≤ 10` | reproduced exactly |
| 0-indexed position of `1155` | **58**, matching the `> 58` in `conjecture` |
| `perfectDeficiency` at `8925` / `24` / `56` | `2969` / `0` / `20` |

Reproduced independently in Python from A109883's NAME (two separately written stopping-rule
formulations), and the counterexample enumeration was recomputed both by a numpy divisor-sum
sieve to `10⁷` and by plain trial division with no sieve. Record:

https://github.com/Kuberwastaken/c5-k4/blob/125be1d2ad3da8ade60615d1f6d7d3b1722a098a/results/expansion/publication/oeis_108864_submission.md

**Limitations.** Only the changed module was built; the full project was not. `a 58 = 1155` is
not asserted as a Lean `test` theorem — `decide` on `Nat.count A 1155 = 58` would need the
kernel to reduce `perfectDeficiency` on every `n < 1155`. It is verified by `#eval` and by the
independent recomputations above, not by the kernel.

## AI assistance disclosure

Claude Code and delegated coding agents assisted with the source audit, the search for the
witness, the Lean repair, the independent verification and the preparation of this pull
request. The submitter reviewed the mathematical statement, the counterexample and the Lean
artifact, and takes responsibility for the submission.
