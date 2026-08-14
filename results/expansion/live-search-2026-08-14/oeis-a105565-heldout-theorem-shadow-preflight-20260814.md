# OEIS A105565 held-out/theorem-shadow preflight

**Audit time:** 2026-08-14 12:49 UTC
**Disposition:** `STRICT_STOP_THEOREM_SHADOW_AND_HELDOUT_INELIGIBLE`
**Target evaluation:** none
**Upstream/public action:** none

This is a source, status, duplication, and resolution-shape preflight. It did
not select or freeze A105565, evaluate a target candidate, extend the OEIS
table, run a continued-fraction candidate list, edit the project README, or
make any upstream action. Its conclusion is that A105565 is not an admissible
held-out lane and should not receive a counterexample search. If pursued at
all, it should be a separately authorized proof-extraction/formalization task.

## Current upstream lock

At the audit time, `refs/heads/main` of
[`google-deepmind/formal-conjectures`](https://github.com/google-deepmind/formal-conjectures)
resolved independently by `git ls-remote` and the GitHub commits API to:

```text
main commit: 4010c1f1b811be0b0f95c9cf8bc084d72cea2a88
main tree:   068a3702caca4310f8ae3eea88d6042c9b069925
commit time: 2026-08-14T10:40:05Z
```

The exact current file is
[`FormalConjectures/OEIS/105565.lean`](https://github.com/google-deepmind/formal-conjectures/blob/4010c1f1b811be0b0f95c9cf8bc084d72cea2a88/FormalConjectures/OEIS/105565.lean):

```text
Git blob SHA-1: d5bbbea9b76cb2506548569310cffb321c269b3f
file SHA-256:   11851b1203bd8721ab2301e24b6b08f77364bbe57e2dab860f0168d405495fe5
size:           3052 bytes
```

The declaration remains literally:

```lean
@[category research open, AMS 11]
theorem conjecture (n : ℕ) (hn : 1 ≤ n) :
    betaConst - 2 < s n - alphaConst * (n : Real) ∧
      s n - alphaConst * (n : Real) < betaConst - 1 := by
  sorry
```

There is no `formal_proof` annotation, solved category, or answer field. The
formal sequence counts Fibonacci **indices** `k` in `range (5*n+10)`, so the
two occurrences of `fib = 1` are counted separately; `a(1)=0` is explicitly
proved, and the universal statement begins at `n=1`.

## Duplicate and claim audit

The exact-path history on current `main` contains one commit only:

- merged ingestion commit
  [`d7032450c559849f2a345f80582688c76b25ffcb`](https://github.com/google-deepmind/formal-conjectures/commit/d7032450c559849f2a345f80582688c76b25ffcb),
  “Add the first 64 files from AutoOeis to formal-conjectures (#4450),” on
  2026-08-13;
- merged PR
  [#4450](https://github.com/google-deepmind/formal-conjectures/pull/4450)
  added the file with the same blob that is current today. Its review threads
  contain no A105565-specific mathematical claim, proof, disproof, or status
  change.

The following all-state checks were run at the audit time:

- GitHub issue/PR search for `A105565`, `105565`, `OeisA105565`,
  `Fibonacci digit-count`, and `Fibonacci numbers with n digits`: zero
  target-specific results. PR #4450 is found by exact changed-file history,
  not text search, because its batch title and body do not name A105565.
- GitHub commit search for `A105565`, `105565`, and `OeisA105565`: zero
  message hits; the exact path-history API supplies the ingestion commit above.
- Default-branch code search for `105565`: exactly the current Lean module.
- Every one of the 284 open PRs was inspected through its changed-file list:
  none touches `FormalConjectures/OEIS/105565.lean`.
- The 100 most recently updated closed-unmerged PRs were similarly inspected:
  none touches the file. This window covers the period after the file's
  2026-08-13 introduction. Merged-file history is complete through the
  exact-path commits endpoint.

Accordingly, no open claim or merged resolution duplicates this work in the
upstream repository. This is a point-in-time result: GitHub search can lag and
cannot expose unpushed/private branches.

The authoritative [OEIS A105565](https://oeis.org/A105565) page likewise
still prints the inequality as a conjecture and links the 10,000-row
[`b105565.txt`](https://oeis.org/A105565/b105565.txt) table. The b-file was
retrieved only as a source receipt, not evaluated:

```text
rows plus comment: 10001 lines (n=1..10000)
SHA-256: e0253183e03e6c80e95f01e041b8f70a36723f83fc1751f331ac5cef196cf6e5
```

The [OEIS revision history](https://oeis.org/history?seq=A105565&start=10)
shows that Hans J. H. Tuenter added/corrected the rotation formula in July and
September 2025 and added the partial-sum conjecture on 2025-09-05. Web searches
for the exact inequality, the sequence identifier with `proof`, `theorem`, or
`solved`, and the exact rotation formula found no separate claimed solution.
Absence from web search is not itself a novelty proof; the exact structural
reduction below is the reason to stop.

## Held-out eligibility stop

A105565 is already semantically exposed inside this repository:

- `wave2-oeis-boundary.md` records a source-boundary check at `n=1..30`;
- `next-current-development-target-scout.md` identifies the rotation wall,
  continued fractions, semiconvergents, and a theorem-shadow stop;
- the target entered public upstream before this preflight and its source
  formula and table have been inspected.

It therefore cannot be called a genuinely held-out prospective target under
the project's future-cohort benchmark discipline. At most it was a
DEVELOPMENT reserve. This audit now closes even that search reserve.

## Exact collapse of the digit-count wall

Use the shifted constants in the source and Lean declaration:

```text
α = log(10)/log(φ) - 4
β = log(5)/(2 log(φ)) - 1
```

The current OEIS formula states, for `k>1`,

```text
a(k) = [ {kα+β} < α ].
```

Here `0<α<1`; also `1<α+β<2`. Put
`F_k = floor(kα+β)`. The indicator is not merely rotation-like: it is
the exact floor difference

```text
[ {kα+β} < α ] = F_k - F_(k-1).
```

Indeed, adding `α` to `{(k-1)α+β}` makes the fractional part land
below `α` exactly when it crosses an integer. Since `a(1)=0` and
`floor(α+β)=1`, this telescopes for every `n≥1` to

```text
S(n) = floor(nα+β) - 1,
S(n)-nα = β - 1 - {nα+β}.
```

Consequently the scout's two residuals are exactly

```text
R_upper(n) = {nα+β},
R_lower(n) = 1 - {nα+β}.
```

The lower inequality is immediate from `{x}<1`. The upper inequality only
asks that `nα+β` never be an integer.

Suppose `nα+β=m` for integers `n≥1` and `m`. Substitution and
multiplication by `2 log(φ)` give

```text
2n log(10) + log(5) = 2(m+4n+1) log(φ),
5 * 10^(2n) = φ^(2(m+4n+1)).
```

The logarithms show `K=m+4n+1>0`. But

```text
φ^(2K) = Fib(2K) * φ + Fib(2K-1)
```

is irrational, whereas `5*10^(2n)` is an integer. This contradiction makes
`R_upper(n)>0`. Thus, once the OEIS rotation formula is bridged to the exact
Lean `a`, the conjectural strip is forced for every `n`; no untested numerical
premise remains in the wall argument.

This report is a preflight theorem-shadow diagnosis, not a claim that the
Lean theorem has been proved. The proof-extraction obligations are:

1. prove the safe cutoff `range (5*n+10)` includes every Fibonacci index with
   `n` digits;
2. prove the OEIS rotation formula for the formal definition, treating
   `n=1` and duplicate `fib 1 = fib 2 = 1` exactly;
3. certify `0<α<1` and `1<α+β<2` without floating point;
4. formalize the floor telescope and the irrationality contradiction above.

These are theorem obligations, not search coordinates.

## Continued-fraction wall and terminal decision

Continued fractions do explain near equality, but they do not supply a
separating move. A small upper residual is an inhomogeneous approximation

```text
||nα+β|| near 0,
```

so ordinary convergents of `α` are not by themselves the right candidate
set; one would need inhomogeneous best approximants/Ostrowski states for the
offset `-β`. Small lower residuals similarly approach fractional part `1`.
Either computation would catalogue close approaches to the two exact walls.
The telescope and irrationality argument show that neither list can cross or
touch a wall.

Therefore there is no genuinely structural **search** design to freeze. A
continued-fraction depth, semiconvergent list, adaptive precision rule, or
larger exact Fibonacci digit scan would only measure proximity inside a strip
already forced by the source identity. The strict terminal rule is:

```text
STOP_THEOREM_SHADOW
NO_TARGET_SELECTION
NO_CANDIDATE_EVALUATION
NO_CONTINUED_FRACTION_RUN
NO_PREFIX_EXTENSION
```

Any future work must be explicitly re-scoped as proof extraction for the four
obligations above. It must not be reported as a held-out arm, a bounded search
result, a counterexample hunt, or evidence for search-arm efficacy.

## Terminal record

- Exact current upstream declaration/status: locked and still research-open.
- Relevant merged item: ingestion PR #4450 only.
- Relevant open PR or issue: none found.
- Relevant later merged commit: none; exact path has one historical commit.
- Existing solved/claimed work found: none.
- Held-out eligibility: rejected due prior local semantic/evaluation exposure.
- Theorem-shadow risk: decisive, not merely high.
- Structural exact candidate search: rejected as logically non-separating.
- Target candidate evaluated: no.
- Mathematical proof claimed: no; a proof skeleton and its bridge obligations
  are recorded.
- README edit, commit, push, Actions dispatch, release, issue, PR, or other
  public/upstream action: none.
