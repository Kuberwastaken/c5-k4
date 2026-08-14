# OEIS A108211 preflight: strict stop before evaluation

**Disposition:** `STRICT_STOP_BEFORE_EVALUATION` for the next prospective
counterexample-search lane; retain only as a possible `THEOREM_SIGNAL` /
proof-extraction target.

**Audit time:** 2026-08-14T11:57:59Z

This is a read-only Phase-0/Phase-5 preflight. It is not a frozen trial and
does not authorize one. **No target evaluation was run, no bounded result was
obtained, and no release is permitted by this report.** The earlier literal
boundary checks recorded elsewhere in this repository are calibration only
and are not promoted here. Written on the Wall I is outside this audit and was
not inspected or used.

## Exact target and immutable identities

At audit time, `google-deepmind/formal-conjectures` `main` resolved to:

- commit:
  `942fb149e782a56c2719c543ab58e093f733acb4`;
- tree: `cf09732f4a5a246540e577e2b5bc76bf5ea09d9a`;
- commit URL:
  <https://github.com/google-deepmind/formal-conjectures/commit/942fb149e782a56c2719c543ab58e093f733acb4>;
- declaration path: `FormalConjectures/OEIS/108211.lean`;
- declaration blob SHA-1:
  `42a056ffbf30a778f71b04ac69c735f8b3788966`;
- declaration SHA-256:
  `10a1a0c6caf0bc442446201ee5bdedd27c7b15545e82eecb45aeb7d428fafeec`;
- immutable blob URL:
  <https://github.com/google-deepmind/formal-conjectures/blob/942fb149e782a56c2719c543ab58e093f733acb4/FormalConjectures/OEIS/108211.lean>;
- immutable raw URL:
  <https://raw.githubusercontent.com/google-deepmind/formal-conjectures/942fb149e782a56c2719c543ab58e093f733acb4/FormalConjectures/OEIS/108211.lean>.

The declaration remained exactly `@[category research open, AMS 11]`. In
ordinary notation it asserts, for every positive natural number `n`,

```text
16 n^2 + 1 = floor(1 / D_n),

D_n = 1/(4n) - log(2) + sum_{k=n+1}^{2n} 1/k.
```

Its literal negation has the right finite certificate shape: one explicit
positive `n` for which the two displayed integers differ. The OEIS offset is
`1,1`, and the source formula and Lean quantifier both begin at positive `n`,
so no index-shift reading was found.

The local protocol snapshot inspected for this decision was repository commit
`1a165f20771c8b17064c94c2bc39e4a6b1f082a7`, tree
`948fdc552f6169ca7953d7f8036316ed83d59c22`, with `METHOD.md` SHA-256
`c41cfc7b43f3da3ad6a55525a71b8ac2a6d1a56299efd19d056155fd868d0322`.

## Primary-source and database status

The primary source is [OEIS A108211](https://oeis.org/A108211). The source
record retrieved at audit time was revision 62, last changed
2025-06-06T11:14:45-04:00. It still labels Clark Kimberling's formula
"Conjecture" and gives the same summation endpoints as the Lean declaration.
The exact retrieval locators and observed content hashes were:

- OEIS JSON:
  <https://oeis.org/search?q=id:A108211&fmt=json>, SHA-256
  `e59a2380b34b13d4fd52df058a120703a2f90294cdc649fc1ee002cbc23e8c65`;
- OEIS b-file:
  <https://oeis.org/A108211/b108211.txt>, SHA-256
  `65e60b62d8153ea20575509300f4374e8731fdd4cf359155d9d4a9439915ebac`.

The b-file has 10,000 ordered rows, from `1 17` through
`10000 1600000001`. It certifies only the elementary sequence definition
`a(n) = 16n^2 + 1`. **It is not evidence for the conjectural floor identity.**
Any future database-sanity gate must independently evaluate and certify the
right-hand side; matching the b-file alone must fail closed.

## Status and cheap duplicate audit

The following checks were completed before this stop:

- exact GitHub issue search for `A108211` in
  `google-deepmind/formal-conjectures`, open and closed: zero matches;
- exact GitHub pull-request search for `A108211` in the same repository, open,
  closed, and merged through the closed set: zero matches;
- complete local commit, tag, release-record, Lean-file, and publication-record
  text search for `A108211` / `108211`: no covering proof or disproof, apart
  from inventory and earlier boundary-audit mentions;
- exact web searches for the sequence identifier and displayed floor formula:
  no proof or disproof located;
- the current OEIS record itself still calls the identity a conjecture.

These are cheap preflight checks, not a claim that the entire mathematical
literature has been exhaustively reviewed. They establish only that no obvious
existing resolution or duplicate campaign artifact was found at the audit
time.

## The theorem signal

The expression has a structural interpretation that makes a blind
counterexample scan poorly motivated. Let `f(x)=1/x`. The composite
trapezoidal approximation to `integral_n^(2n) f(x) dx` with unit-width
subintervals is

```text
(f(n)+f(2n))/2 + sum_{k=n+1}^{2n-1} f(k)
  = 1/(4n) + sum_{k=n+1}^{2n} 1/k.
```

Since the integral is `log 2`, `D_n` is exactly this trapezoidal-rule error.
For the interval from `k` to `k+1`, put `t_k = 1/(2k+1)`. Its error is

```text
e_k
  = (1/2)(1/k + 1/(k+1)) - log((k+1)/k)
  = 2 t_k/(1-t_k^2) - 2 atanh(t_k)
  = 2 sum_{j>=1} (2j/(2j+1)) t_k^(2j+1)
  > 0.
```

Thus `D_n = sum_{k=n}^{2n-1} e_k` has a positive rational-power expansion
with a geometrically controllable tail. Standard expansion of that exact
representation gives the prospective wall law

```text
1 / D_n = 16 n^2 + 2 - 3/(4 n^2) + O(n^-4).
```

The reciprocal therefore approaches the *upper* adjacent integer from the
safe side. This does not prove the conjecture, but it supplies a much more
specific theorem signal than a finite scan would: seek the all-`n` bounds

```text
1/(16n^2 + 2) < D_n <= 1/(16n^2 + 1).
```

Those inequalities would immediately force
`floor(1/D_n) = 16n^2+1`. The positive `atanh` expansion suggests a rational
tail-bound route to them and exposes the exact lemma that may fail.

## Why the counterexample lane stops at METHOD Phase 5

The target passes the elementary certificate-shape test, but it does not pass
the separating-transformation requirement:

1. The only candidate coordinate is the original integer `n`; there is no
   carrier, construction, quotient, local surgery, or second invariant to
   separate.
2. The preflight found no symbolic range, feasible negative objective, or
   negative local derivative predicting a crossing.
3. The structural expansion predicts movement toward the boundary from the
   safe side rather than through it.
4. Splitting a large interval of `n` across catalogue, generic, and
   "wall-navigation" workers would change scheduling, not mathematical
   geometry. It would be generic brute force mislabeled as the method.
5. The current `METHOD.md` top-level scope is finite-graph conjectures. A
   separate, explicit arithmetic-development addendum would be required even
   for a non-method calibration run.

Accordingly this target is not genuinely suitable as the prospective search
lane following A105720. The strict stop is a methodological result, not a
bounded hold and not evidence that the conjecture is true.

## Requirements if the stop is deliberately superseded

If a later committed protocol explicitly admits this as an arithmetic
calibration or proof lane, it must still freeze the following before any
evaluation:

- source retrievals and all hashes above;
- distinct checks for the polynomial b-file and conjectural floor expression;
- exact rational interval arithmetic for `log 2`, with a fail-closed precision
  loop and independent implementation;
- disjoint, immutable index sets and 60-second subprocess caps;
- a certificate proving the denominator sign and locating the reciprocal
  between consecutive integers;
- a Lean proof using an adaptive rational enclosure and `Int.floor_eq_iff`,
  followed by the normal warnings-as-errors and axiom audit.

Mathlib's fixed `Real.log_two_near_10` estimate is not a general large-`n`
certificate: the relevant distance to the upper floor boundary shrinks like
`n^-2`, while the corresponding denominator enclosure must become much
tighter. Precision must therefore be part of the replayable certificate, not
an undocumented floating-point setting.

## Terminal record

- Target evaluation: **not run**.
- Bounded mathematical result: **none**.
- Counterexample: **none claimed**.
- Proof: **none claimed**.
- Release: **not authorized and not created**.
- Upstream issue or PR: **not authorized and not created**.
- WoW I: **excluded**.
- Recommended disposition: **strict stop for counterexample search; optional
  theorem-signal proof extraction under a separately committed scope**.
