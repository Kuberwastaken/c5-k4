# Next DEVELOPMENT rotation after Equation 677

**Audit time:** 2026-08-14 UTC  
**Disposition:** `RANKED_NOT_FROZEN_NOT_EVALUATED`  
**Recommended next target:** the joint OEIS A109908/A109909 quadratic-prime
cluster  
**Runner-up:** Fernandes' even direct-product permutation-group conjecture  
**Third:** OEIS A103151

This is a source/status and method-selection report only. It does not evaluate
any target instance, freeze a search, claim a bounded result, or authorize a
release or upstream action. Written on the Wall I is outside
`google-deepmind/formal-conjectures` and was excluded without being ranked.

## Current pin and subtraction

Two independent `git ls-remote` reads resolved current upstream `main` to
[`google-deepmind/formal-conjectures@6c0950bec7743f5098c0196c6aee7b22c1ec8005`](https://github.com/google-deepmind/formal-conjectures/commit/6c0950bec7743f5098c0196c6aee7b22c1ec8005).
Every declaration ranked below is still literally tagged
`@[category research open]` with a `sorry` body at that commit.

The selection subtracts every terminal project lane, including the completed
graph, finite-combinatorial, finite-algebra, automata/game, OEIS boundary,
answer-wrapped, A063880, A105720, A105565, A108081, A231201, A056777,
A067720, and A108569 work. It also subtracts known controls, released findings,
formalization defects, theorem shadows, strict stops, and public prior art.
The small A109908/A109909 boundary checks and the A103151 checks at
`n=4,5,6` are calibration only; neither cluster has received a frozen
structural search. The only local contact with Fernandes is registry metadata,
not mathematical evaluation.

Equation `677 -> 255` is a **public-overlap strict stop** for this rotation.
Open Equational Theories
[#1464](https://github.com/teorth/equational_theories/issues/1464), created
2026-07-22, reports a Lean orbit lemma and DRAT-checked UNSAT for all 45
canonical order-10 orbit cases. The report is still unreviewed and does not
resolve the implication, but it already dominates the proposed order-eight
finite-table direction and claims the same structural territory. Its order-11
follow-up also records a certified local Hamming-ball exclusion. No Equation
677 compute should launch unless that overlap is first resolved and a genuinely
nonoverlapping method is preregistered.

## Public status and identity audit

| rank | exact declaration(s) | current files | source/status result |
|---:|---|---|---|
| 1 | `OeisA109908.conjecture`; `OeisA109909.conjecture` | `OEIS/109908.lean`, blob `79f24ed3...`, SHA-256 `518c786a...`; `OEIS/109909.lean`, blob `f4328ad6...`, SHA-256 `bb91d62d...` | Both entered in merged PR #4450. Exact all-state upstream searches for either sequence ID returned no issue or PR. Both OEIS records still print the conjecture and say it was verified through `10^9`. |
| 2 | `Arxiv.2605.12342.conjecture_1` | `Arxiv/2605.12342/Conjecture1.lean`, blob `f73b5388...`, SHA-256 `801f7278...` | Issue #4815 and merged PR #4836 only introduced the statement. The May 2026 source still labels Conjecture 1 open and lists computed positive and negative controls; no later resolving item was found. |
| 3 | `OeisA103151.conjecture` | `OEIS/103151.lean`, blob `fec2d6b5...`, SHA-256 `f7f236f5...` | Entered in merged PR #4450. Exact all-state search for `OeisA103151` returned no issue or PR. OEIS still prints the stronger-than-Goldbach conjecture. |

The current authoritative b-files contain 10,000 A109908 rows, 93 A109909
rows, and 10,777 A103151 rows. A109908 and A109909 are one correlated target:
their zero/nonzero predicates are extensionally the same even though one
stores the greatest prime and the other counts distinct prime values.

## 1. A109908/A109909 — quadratic-prime finite-prefix covering

### Literal negation and exact certificate

For `n>3`, put

```text
f_n(k) = k(n-k)-1.
```

The two declarations assert that at least one value is prime. A single shared
counterexample is therefore one explicit `n>3` such that every relevant
`f_n(k)` is nonprime. For A109908 the formal range is
`1 <= k <= floor(n/2)`; A109909 uses `1 <= k < n`, but
`f_n(k)=f_n(n-k)` reduces it to the same half-range. A replayable certificate
contains `n` and, for every symmetry representative, either the exact
boundary value `<=1` or a proper divisor `1<d<f_n(k)`.

### Wall and separating coordinate

For a proposed divisor `q` with invertible `k mod q`,

```text
q | f_n(k)  <->  n = k + k^(-1) (mod q).
```

Thus the useful coordinate is not another flat prefix in `n`; the source has
already checked through `10^9`. It is the **least uncovered symmetry
representative** after assigning quadratic residue classes to exact divisors:

```text
U(n,D) = least 1 <= k <= floor(n/2)
         not certified composite by the frozen divisor family D.
```

The crossing wall is `U(n,D)>floor(n/2)`. Complete periodic coverage of all
integers is not available: with finitely many independent prime moduli, CRT
constructs an avoiding residue. The prospective move is therefore a finite
prefix cover whose first CRT escape lies beyond the literal half-interval,
not a false claim of an infinite covering system. This explicitly subtracts
the periodic-cover obstruction learned in the A231201 lane.

### Database-sanity gate

Before construction, a frozen gate must:

1. hash and replay every current b-file row for both sequences;
2. independently reconstruct the two formal ranges and prove their reduction
   to the same half-range by `k <-> n-k` symmetry;
3. reproduce the exact values at `n=1..20`, including the zero boundary
   through `n=3` and positivity from `n=4`;
4. use direct primality/factorization and a separate divisor replay on all
   controls; and
5. treat every `n<=10^9` as historical calibration, never novelty.

Any range mismatch, `Nat`-subtraction mismatch, probable-prime-only row, or
improper divisor fails closed.

### Exact stop rule

Freeze one divisor universe, one CRT/residue-profile universe, one interval
bound for candidate representatives above `10^9`, deterministic ordering, and
shard map before evaluating `U`. Give construction 48 seconds, stop launching
factor work by 54 seconds, and enforce a 60-second process-group cap. Stop at
the frozen profile universe or cap. `CAP_PREFIX` is not exhaustion. A profile
whose first escape remains inside the half-range is a wall diagnostic; a
profile with an uncovered or incompletely factored value is never a candidate.
Do not add moduli, enlarge the interval, or switch to a flat `n` scan after
seeing the result.

This ranks first because one exact certificate attacks two current
machine-generated declarations, the literal negation is finite, and the wall
is an algebraic finite-prefix escape problem rather than another magma,
graph-invariant, or totient-profile search.

## 2. Fernandes — separate the parity-product obstruction

### Literal negation and exact certificate

For an admissible pair `m>=n>=2`, define

```text
Gamma_(m+n) = {(sigma,tau) in S_m x S_n : sign(sigma)=sign(tau)}.
```

The formal conclusion is that two elements generate this finite group. Its
literal negation at one admissible `(m,n)` is

```text
for every g1,g2 in Gamma_(m+n), closure({g1,g2}) != Gamma_(m+n).
```

A finite certificate may be an exhaustive orbit-reduced pair ledger with
independently replayed closures, or preferably a maximal-subgroup cover that
places every ordered pair in a proper subgroup. The latter is compact enough
to bridge to Lean. Merely failing to find generators is not a certificate.

### Wall and separating coordinate

The source controls are exact: `(2,2)` has rank one; `(3,3)`, `(4,3)`, and
`(4,4)` have rank three; tested pairs including `(5,5)`, `(6,6)`, `(7,7)`,
`(8,8)`, `(9,3)`, and `(9,4)` have rank two. The wall is therefore the
transition from the three exceptional common-quotient geometries to the first
uncovered parity-synchronised direct products. The separating coordinate is
the common quotient/subdirect-product obstruction from Goursat geometry, not
group order alone: determine whether every proposed generator pair has
projections that generate both symmetric factors but remains trapped in a
proper parity-compatible subdirect product.

### Database-sanity gate

The gate must independently:

1. enumerate `Gamma_(m+n)` and verify cardinality `m! n! / 2`;
2. reproduce rank one at `(2,2)` and non-2-generation at all three rank-three
   exceptions;
3. replay explicit two-generator certificates for every positive source
   control listed above;
4. verify projection, sign, multiplication, closure, and conjugacy-orbit
   conventions with a second implementation; and
5. subtract every pair already covered by a theorem or explicit construction
   in the source paper before any search.

### Exact stop rule

Freeze a finite grid of source-uncovered pairs, the conjugacy/orbit reduction,
GAP version, ordering, and per-pair certificate form. Each pair receives a
48/54/60-second cap. Stop a row immediately as `KNOWN_PROOF_DOMAIN` if source
subtraction supplies generators. Stop at the fixed grid; do not enlarge `m`
or `n` after observing holds. Promote non-generation only after an independent
maximal-subgroup or complete-pair certificate replay. This is the runner-up
because it is a genuinely different finite-group method, but source theorem
subtraction may close much of the attractive small grid before computation.

## 3. A103151 — a finite strengthened-Goldbach miss

### Literal negation and exact certificate

For `n>=4`, the declaration asks for an odd prime `p<=n` such that

```text
q = 2n+1-2p
```

is prime. A counterexample is one explicit `n` together with the complete list
of eligible odd primes `p` and a proper factor of every resulting `q`. This is
a direct finite refutation of the Lean theorem, without an `answer(sorry)` or
`Nat.nth` bridge.

### Wall and separating coordinate

The residual is the representation count `a(n)`. The wall is `a(n)=1`, and
the crossing is `a(n)=0`. For a frozen small prime divisor `r`, compositeness
of `q` is forced on the affine class

```text
p = n + 2^(-1) (mod r).
```

The separating coordinate is therefore coverage of the **eligible prime
residue classes**, not coverage of every integer or a longer Goldbach prefix.
The construction should synthesize `n` so the surviving prime `p` classes are
assigned exact proper divisors of `q`, then independently sieve the finite
uncovered set.

### Database-sanity gate

Hash and replay all 10,777 b-file rows; reproduce the formal zeros at
`n=1,2,3`, the first positive rows, odd-prime and strict-positivity semantics,
and the `Finset.range (n+1)` endpoint. Cross-check every control with a second
prime enumerator. Record every stronger-Goldbach computation or theorem found
in the source links as a prior boundary. A sieve miss without a proper factor
for every eligible `q` is not a certificate.

### Exact stop rule

Freeze one modulus/divisor family, one CRT candidate family, one maximum
candidate size, and one segmented-prime verifier before evaluating any
representation count. Apply 48/54/60-second caps per shard and stop at the
frozen family. Do not turn a failed residue cover into an enlarged flat
Goldbach scan. Every candidate must serialize `n`, all eligible `p`, all `q`,
and exact proper divisors, followed by independent replay.

It ranks third because its certificate is literal and finite, but it currently
has a weaker equality geometry and potentially much larger certificate than
either the shared quadratic-prime cluster or a small finite-group obstruction.

## Recommendation

Freeze **only the joint A109908/A109909 finite-prefix-cover lane** after one
fresh live race check. Preserve Fernandes as the next method-diverse rotation
if source theorem subtraction leaves a nonempty small grid. Keep A103151 as
the arithmetic reserve. Do not return to Equation 677 from this branch: public
issue #1464 makes the proposed finite-table continuation overlapping work,
even though its claims remain subject to review.
