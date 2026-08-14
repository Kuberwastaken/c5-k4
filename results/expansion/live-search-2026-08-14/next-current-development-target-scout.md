# Next current-main DEVELOPMENT target scout

**Audit date:** 2026-08-14 UTC  
**Disposition:** `RANKED_NOT_SELECTED_NOT_EVALUATED`

This is a read-only selection and status audit for the next DEVELOPMENT target
after the live OEIS A105720 lane. It does not freeze or authorize a search.
No target instance was evaluated, no bounded mathematical result was obtained,
and no proof, disproof, release, issue, pull request, or other upstream action is
claimed or authorized by this report. Written on the Wall I is outside this
audit and was not inspected or used.

## Current-main and scope lock

The audited upstream is
[`google-deepmind/formal-conjectures@942fb149e782a56c2719c543ab58e093f733acb4`](https://github.com/google-deepmind/formal-conjectures/commit/942fb149e782a56c2719c543ab58e093f733acb4),
the current `main` tip at audit time. Each ranked declaration remains marked
`@[category research open]` at that commit.

The ranking subtracts completed or overexposed development lanes rather than
recycling them. In particular:

- A108211 and A115257 now have committed Phase-5 strict-stop reports;
- A104320, A001157/A1157, A108866, and A108081 have already received
  substantial bounded evaluation;
- no current finite-graph declaration survives the existing project coverage
  subtraction as a cleaner next target than the arithmetic candidates below;
- these are DEVELOPMENT candidates, not held-out benchmark targets. Existing
  source and registry exposure means that even a prospectively frozen arm must
  not be described as uncontaminated evidence.

The current `METHOD.md` is graph-oriented. Any selected arithmetic target must
therefore receive an explicit arithmetic DEVELOPMENT scope card, resolution
card, source lock, and frozen contract before evaluation.

## Ranking

### 1. OEIS A063880: an alternative primitive divisor-sum core

#### Exact identity and status

- File: `FormalConjectures/OEIS/63880.lean`.
- Declarations:
  - `OeisA63880.mod_216_of_a`, category line 81;
  - `OeisA63880.unique_primitive_108`, category line 91.
- Git blob SHA-1:
  `0aa326a3062c646f0347506ea3979f8892e430c7`.
- Module SHA-256:
  `b50d00e13735613cbe37bd3a25c19130874e8f036ca2a0e3c1aceb177a33c683`.
- Statement-header SHA-256 values:
  - `212f1990afad2593d598e39044982901976356041f0ac91603ee3d33f47be188`;
  - `fde760497125f048a6ecc0c5f67ddc9d087c6a02f0e9eda387c4fbc796af4784`.
- Registry classification:
  `MACHINE_ELIGIBLE_PENDING_PROVENANCE` in `FINITE_COMBINATORIAL`.

Both exact declarations remain research-open. The all-state GitHub audit found
only the ingestion issue/PR and three closed, unmerged attempts concerning the
different theorem `exists_primitive_of_a`:

- issue [#1455](https://github.com/google-deepmind/formal-conjectures/issues/1455)
  and merged PR
  [#1877](https://github.com/google-deepmind/formal-conjectures/pull/1877)
  ingested A063880;
- closed PRs
  [#2568](https://github.com/google-deepmind/formal-conjectures/pull/2568),
  [#3028](https://github.com/google-deepmind/formal-conjectures/pull/3028),
  and
  [#3092](https://github.com/google-deepmind/formal-conjectures/pull/3092)
  did not merge and did not resolve either ranked declaration.

The current [OEIS A063880](https://oeis.org/A063880) page says that all known
members are `108 mod 216`, confirmed through `10^7`, and that `108` is the only
primitive term below `10^18`. The local project contains only initial source
checks at `108`, `540`, and `756`; it contains no target-specific frozen lane,
candidate, Lean certificate, tag, publication record, or release.

#### Residual wall and separating coordinate

For

```text
n = product_i p_i ^ e_i,
```

multiplicativity gives the exact wall

```text
sigma(n) / usigma(n)
  = product_i (1 + p_i + ... + p_i ^ e_i) / (1 + p_i ^ e_i)
  = 2.
```

Every squarefree prime factor (`e_i=1`) contributes exactly `1`. The meaningful
coordinates are therefore the powerful prime-power core, not the numerical
size of `n`. The known primitive seed has the exact factor geometry

```text
108 = 2^2 * 3^3,
(1 + 2 + 2^2)/(1 + 2^2) = 7/5,
(1 + 3 + 3^2 + 3^3)/(1 + 3^3) = 10/7,
(7/5) * (10/7) = 2.
```

This supplies a literal local-surgery point: replace one or both reduced Euler
factors while retaining exact product `2`, then test whether the resulting
core is primitive and whether it escapes the `108 mod 216` class.

#### Literal negation and certificate

A counterexample to `mod_216_of_a` is an explicit positive `n` with:

1. a complete prime factorization;
2. an exact coefficient/product proof that `sigma(n) = 2 * usigma(n)`; and
3. `n % 216 != 108`.

A counterexample to `unique_primitive_108` additionally needs:

1. `n != 108`;
2. the same exact membership proof; and
3. a complete proper-divisor replay proving that no proper divisor belongs to
   A063880.

The candidate record must include every prime-power Euler factor in reduced
form, their exact rational product, the labelled factorization, and the
proper-divisor witnesses in the same coordinates.

#### Database-sanity gate

Before construction, a frozen gate must:

- retrieve and hash the authoritative A063880 source table;
- reproduce every frozen table row from independent prime factorization;
- independently compute `sigma` and `usigma`, once by divisor enumeration and
  once by their prime-power formulas;
- verify `108`, `540`, and `756`, the primitive status of `108`, and the source
  congruence fixtures;
- strip squarefree factors and check that doing so leaves the rational wall
  unchanged; and
- classify every candidate at or below the source's `10^18` primitive-search
  boundary as historically covered, never as a new discovery.

Any missing row, factorization disagreement, table mismatch, or incomplete
proper-divisor replay is `SANITY_GATE_FAILED`, not a target result.

#### Frozen construction recommendation

Use three disjoint, preregistered arms:

1. **Catalogue/control:** reconstruct source cores and the complete frozen
   historical range; these rows can validate the implementation but cannot
   create a novelty claim.
2. **Generic factor-core:** fixed-seed enumeration of bounded powerful cores
   above `10^18`, with the prime list, exponent range, maximum core size, and
   tie order frozen before any wall evaluation.
3. **Wall navigation:** meet-in-the-middle multiplication of reduced
   prime-power Euler factors, seeded by exact replacements of `7/5` and
   `10/7`; evaluate `n` only after the rational product is exactly `2`.

Every worker receives a 54-second internal budget and 60-second external
process-group cap. Every exact-factorization subprocess is independently
capped. Rows and terminal bindings must be hash-chained and durably written.

#### Theorem-shadow risk and strict stop

Risk is medium. The proved/source-backed decomposition into a primitive core
times a coprime squarefree factor is a strong theorem baseline, but it does not
prove that `108` is the unique primitive core.

The frozen prime list, exponent range, core size, and rational-factor universe
are terminal. Stop with a bounded zero when that universe is exhausted or the
cap expires. Reject a row when it is nonprimitive, at most `10^18`, congruent
and relevant only to the other declaration, already present in a source, or
not independently replayable. Do not add a prime, exponent, factor, solver, or
post-result mutation without a separately committed addendum.

**Recommendation:** this is the best next freeze. It has an exact equality
wall, a closed-form obstruction, an auditable separating surgery, and compact
certificates.

### 2. OEIS A231201: a residue-cover attack on Sun's `2^x + y` conjecture

#### Exact identity and status

- File: `FormalConjectures/OEIS/231201.lean`.
- Declaration: `OeisA231201.conjecture`, category line 66.
- Git blob SHA-1:
  `2fc0d6bf46e910481242688c713985eb4d26e972`.
- Module SHA-256:
  `3cfc75e1613477cd4087e6fe9406658e27981abc2c0834958a311e9551bc8fa1`.
- Statement-header SHA-256:
  `adeb838fbf819a8c4961d2e74c0d3266867c7a3dd20bd66f8be971010ed26768`.
- Registry classification: `AMBIGUOUS_EXCLUDE` because the conservative
  classifier did not certify the nested existential's resolution shape.

The exact declaration remains research-open. Closed issue
[#1486](https://github.com/google-deepmind/formal-conjectures/issues/1486)
and merged PR
[#1580](https://github.com/google-deepmind/formal-conjectures/pull/1580)
only ingested the statement. No open, closed, or merged target-specific
solution item was found. The current [OEIS A231201](https://oeis.org/A231201)
page still labels the all-`n` assertion a conjecture and reports verification
through `10^7`. It also links the 2026 positive-density result, which does not
prove the universal statement.

There is no local target evaluation, candidate, proof, tag, or release. Generic
registry contact is not mathematical evaluation, but the target cannot enter a
run until a new Phase-0 card resolves its `AMBIGUOUS_EXCLUDE` classification.

#### Literal negation and separating coordinate

The declaration states that for each `n > 1` there are positive `x,y` with

```text
n = x + y
```

and `2^x + y` prime. Since `y=n-x`, its literal negation at a fixed `n` is the
finite proposition

```text
for every x with 1 <= x < n, 2^x + n - x is composite.
```

The proposed wall is the representation count `r(n)=0`. The separating move is
not a flat extension beyond `10^7`; it is a finite covering system. For a prime
`q`, the condition

```text
q divides 2^x + n - x
```

depends periodically on `x` through `ord_q(2)` and linearly on `n mod q`.
Choose one residue for `n` modulo each frozen prime, cover every exponent class,
then use CRT to construct an `n` whose whole representation interval has a
certified composite divisor.

#### Literal counterexample certificate

A certificate contains:

1. an explicit `n > 1` outside the source-verified range;
2. a finite periodic covering table with exact moduli, residue classes, and
   assigned prime divisors;
3. an exact CRT reconstruction of `n`;
4. proof that every `1 <= x < n` belongs to a covered class; and
5. for its assigned prime `q_x`, exact checks
   `1 < q_x < 2^x + n - x` and
   `q_x | 2^x + n - x`.

Independent replay must rebuild the periods and CRT solution, not trust a
solver's model. The compact periodic cover is the mathematical certificate;
an unverified list of probable-composite values is not sufficient.

#### Database-sanity gate

Before construction, the gate must:

- retrieve and hash the current A231201 table and source statement;
- reproduce the frozen source rows and the formal examples at
  `n=2,3,4,5,8,53`;
- verify every claimed prime with proof-producing deterministic certificates,
  not a probable-prime flag;
- confirm the `x+y=n`, positivity, and OEIS offset conventions; and
- record `10^7` as the source-reported prior verification boundary.

If the exact frozen source replay cannot complete under the declared caps, the
terminal status is `SANITY_GATE_INCOMPLETE` and no construction arm launches.

#### Frozen construction recommendation

Run one finite SAT/set-cover geometry, for example a source-locked prime
universe through `257`, with `ord_q(2)`, every allowed `n mod q` choice, the
combined exponent period, variable order, and solver version frozen first.
Only after a complete periodic cover exists may the workflow form its CRT
candidate. Catalogue rows at or below `10^7` are controls only. A generic flat
arm is forbidden because it merely repeats the source search.

All SAT, order, primality, and CRT subprocesses receive individual caps, with
54-second worker and 60-second external caps and fail-closed terminal records.

#### Theorem-shadow risk and strict stop

Theorem-shadow risk is low-to-medium: positive density does not settle all
integers, but the source's prize and large prior verification make an ordinary
counterexample unlikely. The central risk is that no complete cover exists in
the frozen residue universe.

If the exact cover misses even one exponent class, stop as
`NO_COMPLETE_COVER`; do not add primes or switch to flat search. Reject CRT
candidates at most `10^7`, with an equality case `2^x+n-x=q_x`, or without a
complete independent factor replay. Any larger prime universe is a separately
frozen trial.

This is the cleanest locally unevaluated prospective construction, but it is
ranked second because the Phase-0 registry ambiguity must be resolved first.

### 3. OEIS A105565: the Fibonacci digit-count discrepancy wall

#### Exact identity and status

- File: `FormalConjectures/OEIS/105565.lean`.
- Declaration: `OeisA105565.conjecture`, category line 91.
- Git blob SHA-1:
  `d5bbbea9b76cb2506548569310cffb321c269b3f`.
- Module SHA-256:
  `11851b1203bd8721ab2301e24b6b08f77364bbe57e2dab860f0168d405495fe5`.
- Statement-header SHA-256:
  `8bb6104726fb82cc1792b2a2aa08fccb3f434de0adf9fdd3f4f237597c36df47`.
- Registry classification:
  `MACHINE_ELIGIBLE_PENDING_PROVENANCE` in `FINITE_COMBINATORIAL`.

The declaration remains research-open. No target-specific issue, PR, proof,
tag, publication record, or release was found; PR #4450 only ingested the
module. The current [OEIS A105565](https://oeis.org/A105565) page still prints
the conjecture and provides a 10,000-row table. Local mathematical exposure is
limited to the committed `n=1..30` source-boundary check.

#### Residual wall and separating coordinate

Let

```text
alpha = log(10)/log(phi) - 4,
beta  = log(5)/(2*log(phi)) - 1,
S(n)  = sum_{k=1}^n a(k).
```

Write the two strict residuals as

```text
R_lower(n) = S(n) - alpha*n - (beta - 2),
R_upper(n) = (beta - 1) - (S(n) - alpha*n).
```

The conjecture requires both residuals to be positive. The source formula for
the number of Fibonacci numbers having `n` digits turns `a(n)` into an
irrational-rotation indicator. Consequently, continued-fraction denominators,
semiconvergents, and their Ostrowski states are the natural coordinates for
approaching either strict endpoint. Consecutive large `n` are not a separating
move.

#### Literal counterexample certificate

A certificate contains:

1. an explicit `n >= 1`;
2. the exact integer `S(n)` and an independently reconstructed indicator
   prefix;
3. rigorous rational lower and upper enclosures for `log(phi)`, `log(5)`, and
   `log(10)`; and
4. exact interval arithmetic proving `R_lower(n) <= 0` or
   `R_upper(n) <= 0`.

The verifier must prove the failed strict inequality without MPFR rounding and
must independently validate the formal `5*n+10` Fibonacci-index cutoff.

#### Database-sanity gate

Before construction, the gate must:

- retrieve and hash the 10,000-row A105565 source table and relevant A050815
  digit-count formula;
- independently count the Fibonacci numbers in every frozen digit block;
- match every source bit and the formal sequence offset;
- prove the `5*n+10` cutoff includes every relevant Fibonacci index; and
- enclose both conjectural residuals for all source-control rows with directed
  exact interval arithmetic.

Any table disagreement, inconclusive strict comparison, or inadequately tight
logarithm enclosure fails closed.

#### Frozen construction recommendation

Phase 3 comes before search: derive the exact rotation/floor expression and
attempt to write the discrepancy as a telescoping coboundary. If it does not
force the conjectured strip, freeze a finite list of continued-fraction
convergents and semiconvergents whose denominators lie beyond the source
cutoff, plus their deterministic endpoint neighborhoods. Evaluate only that
list with adaptive rational enclosures and fixed tie order.

Every enclosure refinement and recurrence computation is capped separately;
workers receive 54 seconds internally and 60 seconds externally. An interval
overlapping a wall is `INCONCLUSIVE_INTERVAL`, never a crossing.

#### Theorem-shadow risk and strict stop

Risk is high. The rotation indicator may make the stated width-one strip an
exact bounded-remainder theorem. If the symbolic reduction forces both bounds,
stop before search and classify the target `THEOREM_SHADOW`; any continuation
belongs in proof extraction. Otherwise exhaust only the frozen convergent set
and stop. Do not extend to a flat prefix or increase continued-fraction depth
after seeing the outcome.

This is ranked third because it may mature the method by finding a theorem
shadow rather than a counterexample.

## Deliberate exclusions

- **A108211:** committed Phase-5 strict stop; its trapezoidal-error expansion
  predicts safe-side behavior and supplies no separating coordinate.
- **A115257:** committed Phase-5 strict stop; ordinary polynomial
  factorization by increasing `n` is not invariant-wall navigation.
- **A104320:** already evaluated through a complete prefix to `5000` and
  additional generic/wall arms.
- **A001157/A1157:** already checked exactly for `2 <= k <= 12` and
  `1 <= n <= 20000`.
- **A108866:** already checked through `n=20000`.
- **A108081:** already has target-specific exact development through length
  `14` and a recorded state-growth obstruction at `15`.
- **A237271 Carmichael observation:** the formal premise quantifies over every
  nonzero residue rather than every unit. For a composite modulus, nonzero
  zero divisors make that premise appear inconsistent; this is a
  source/formalization adjudication target, not a finite-counterexample lane.
- **A067720:** its exact totient equality and the exceptional seed `k=8` are
  attractive, but the registry marks it `AMBIGUOUS_EXCLUDE` and it belongs to
  the same multiplicative-totient cluster as the stronger A063880 wall. It is
  a reserve, not an independent methodological replication.
- **A103151:** its finite representation-count negation is clear, but it lacks
  a comparably sharp separating identity and is substantially closer to a
  volume-only strengthened-Goldbach search.
- **Written on the Wall I:** excluded from the repository method scope and
  from this audit.

## Terminal record

- Target selected: **no**.
- Frozen contract: **no**.
- Target instance evaluated: **no**.
- Bounded result: **none**.
- Counterexample: **none claimed**.
- Proof or theorem shadow established: **none claimed**.
- Release: **not authorized and not created**.
- Upstream issue or pull request: **not authorized and not created**.
- Written on the Wall I: **not inspected or used**.
- Recommended next action: freeze A063880 only after a fresh live source and
  duplicate recheck; retain A231201 and A105565 as ordered reserves subject to
  their stated Phase-0 and theorem-shadow stops.
