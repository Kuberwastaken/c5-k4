# Next DeepMind rotation after A056777

**Audit time:** 2026-08-14 UTC

**Disposition:** `RANKED_NOT_FROZEN_NOT_EVALUATED`

**Recommended next target:** OEIS A067720

**Ordered reserve:** OEIS A108569

**Best direct-universal challenger:** OEIS A103151

This is a source/status and target-selection report only. It does not freeze a
contract, evaluate a target instance, extend a search domain, claim a bounded
result, or authorize a release, issue, pull request, or publication. Written
on the Wall I is not represented in `google-deepmind/formal-conjectures`; it
was excluded without being ranked or used.

## Immutable audit pins

The live upstream was refreshed independently with `git fetch upstream main`
and the GitHub commits API. Both resolved
[`google-deepmind/formal-conjectures@05ea0345d09375efac830fac93bf083b654e317e`](https://github.com/google-deepmind/formal-conjectures/commit/05ea0345d09375efac830fac93bf083b654e317e),
tree `002d0d472115157683c0ecf7f2290f2383bea58f`, committed
`2026-08-14T13:42:35Z`. The tip change marks the unrelated Pompeiu conjecture
disproved; it does not touch any ranked file.

The source snapshot is
[`oeis/oeisdata@8872fa543438401edd424a57b67ad5e0737bebfb`](https://github.com/oeis/oeisdata/commit/8872fa543438401edd424a57b67ad5e0737bebfb),
committed `2026-08-14T07:05:01Z`. Live OEIS b-files were retrieved separately
and hashed below.

The committed local policy/evidence snapshot used for subtraction is
`c5-k4@191a4a7e7123a66e9256bc8804c956610ad8293e`; `METHOD.md` has SHA-256
`c41cfc7b43f3da3ad6a55525a71b8ac2a6d1a56299efd19d056155fd868d0322`
and `README.md` has SHA-256
`56bd88c1c6bf93287b1f6bc2f99c4f6b7bc8e6b02b2306e933415b8a010f6001`.
Only committed evidence is used in this ranking.

All three ranked declarations remain literally marked
`@[category research open]` and contain `sorry` at the upstream pin.

| rank | declaration | upstream identity | OEIS identity | status result |
|---:|---|---|---|---|
| 1 | `OeisA67720.prime_add_one_of_a` | `FormalConjectures/OEIS/67720.lean`; blob `c43381687cfcf605679ad268fefcab70ae01bc64`; SHA-256 `af8ae5ba8ebed4d7252b9cee3d6cb7e304f7971282db7f8954ce2f0da99d249e` | `seq/A067/A067720.seq` SHA-256 `13c478e7850f14ecf1f3ed5a78a28ffee42ef6429539943b87a068fe3c761aa4`; 10,000-row b-file through value `1548870`, SHA-256 `c50d6120a72dfda1f6bf82642407007ea68604c76788a8e98c2f43cfeb9bb928` | current and unclaimed |
| 2 | `OeisA108569.conjecture` | `FormalConjectures/OEIS/108569.lean`; blob `daf4427246c28b56a429646958a2c38ca4cf04fa`; SHA-256 `0e62b2d15f41a2b2dbcc568a63abd3644e8429fa7befdec7cc2d0e96cc6244f8` | `seq/A108/A108569.seq` SHA-256 `66a98eb6032c98c12f6bf8250c30356775c434fae4ca4cc2b8ed98eb04d83d9f`; 384-row b-file through value `997694`, SHA-256 `a84aa7eb3295768365d07e081bcaf7b4f0b6d412b6e0615128d615148c238544` | current and unclaimed |
| 3 | `OeisA103151.conjecture` | `FormalConjectures/OEIS/103151.lean`; blob `fec2d6b527fd1c6338aeddc4503bcd96d70ccc6d`; SHA-256 `f7f236f5e627853d16212fbc23d873ab2a3ca04591f7ce8c1f36733732e54db4` | `seq/A103/A103151.seq` SHA-256 `eadc25f02e069f2b9d9bee859616f08a34afe368d6b063a7669f8dece53ab2e5`; 10,777-row b-file, SHA-256 `3da2af0438db1c0e1094c2ebb2c5353a531f78f660cf437fb09fe271fa9b9ec7` | current and unclaimed, but weaker method fit |

## Completed-work and theorem subtraction

This ranking does not recycle a target merely because its full conjecture is
still open. The committed A056777 run exhausted all three frozen tuple domains:
2,599,809 constructed states, 72 independently replayed workers, and zero
equation hits. Its common-block continuation is theorem-blocked, so the
existing repeated-power, squarefree-three-block, pure-power, and common-block
directions are locally closed. A new A056777 block-surgery contract would be a
new trial, not the next rotation.

The following are also subtracted:

- A063880: all three frozen MITM domains exhausted, 147,554 durable ledger
  rows and zero eligible candidates;
- A105720: all 216,000 frozen rows exhausted with zero extra squares;
- A105565: strict stop at a telescoping/theorem shadow before evaluation;
- A108081: exact development through length 14 and a recorded state-growth
  wall at 15;
- A231201: three versions culminated in 54 capped v3 constructor cells and no
  full-seed proposal; its complete-periodic-cover direction is theorem-blocked;
- A108211 and A115257: committed Phase-0/Phase-5 strict stops;
- A000041, A104320, A108129, A108866, A001157, and the other Wave 2/3 targets:
  already received committed bounded evaluation or a terminal status gate;
- A109074 and A111291: formalization/source errata rather than mathematical
  counterexample lanes;
- A113019 and other locally resolved or released targets: already claimed
  campaign results, not rotations.

The automatic finite-stratum classifier previously marked A067720 ambiguous.
Manual literal-negation audit overrides that syntax-only false negative: the
theorem is a direct implication with an implicit natural parameter, and one
explicit `k` refutes it. No answer placeholder, asymptotic quantifier, or
infinite nonexistence certificate is involved.

## Duplicate and priority audit

The audit searched the live upstream across exact sequence IDs, namespaces,
declaration names, issue/PR text in all states, exact-path Git history, and the
changed-file lists of all 280 open pull requests. No open PR touches any of the
three ranked files, and no open issue or PR claims any ranked result.

- A067720 has one relevant merged item: ingestion PR
  [#1878](https://github.com/google-deepmind/formal-conjectures/pull/1878),
  merged as `2e7ff5eeba593908427463753fb363fe61af4863`. It introduced the
  statement and proves only the forward prime construction. The later batch
  rewrite in merged PR [#4450](https://github.com/google-deepmind/formal-conjectures/pull/4450)
  left the reverse implication open. Search also returns issue #1456 because
  its text contains the sequence identifier, but that issue is a different
  `math.CO/0409509` item and is not a resolving claim.
- A108569 and A103151 entered through batch PR #4450, merged as
  `d7032450c559849f2a345f80582688c76b25ffcb`. Their exact path histories have
  no later commit, and exact issue/PR searches return no mathematical claim.
- The local `Kuberwastaken/c5-k4` issue/PR search returns zero items for all
  three IDs. Local commit-message, tag, release-name, publication-record, and
  result-text checks find only the earlier ranking/source-boundary mentions of
  A067720 and A108569, not a target result. A103151 likewise has no local
  evaluation or claim.

This is a point-in-time public audit. It cannot observe private or unpushed
work, so the exact checks must be repeated immediately before any dispatch.

## 1. A067720 — composite-successor escape from the exceptional seed

### Literal counterexample and exact wall

Define

```text
A(k) := phi(k^2 + 1) = k * phi(k + 1),
R(k) := phi(k^2 + 1) - k * phi(k + 1).
```

The theorem says `A(k)` and `k != 8` imply `Prime(k+1)`. A literal
counterexample is therefore one integer `k != 8` with:

1. complete prime factorizations of `k+1` and `k^2+1`;
2. exact multiplicative totient products proving `R(k)=0`; and
3. an explicit proper factor of `k+1`.

This is the cleanest remaining certificate in the current corpus: it is
finite, direct, small, and independent of an enumerating `Nat.nth` wrapper.

### Theorem baseline and separating coordinate

The module already proves that if both `k+1` and `k^2+1` are prime, then
`A(k)`. Subtract that entire prime-prime family. The source identifies exactly
one observed point on the equality wall with composite successor:

```text
k = 8,
k+1 = 9 = 3^2,
k^2+1 = 65 = 5*13,
phi(65) = 48 = 8*phi(9).
```

Consequently numerical size and another flat prefix are not separating
coordinates. The prospective coordinate is the ordered exponent profile of
`k+1`, together with the factor profile induced on `k^2+1`. Every known
nonexceptional table row belongs to the subtracted prime-successor side; the
exception changes the successor profile from prime to a square and splits the
other endpoint into two primes.

### Proposed constructive arms

All universes, prime lists, exponent lists, interval bands, ordering, and
shard maps must be frozen in a separate contract before the first target
residual is evaluated.

1. **`CATALOGUE_CONTROL`:** replay all 10,000 source rows, prove `R=0`, verify
   that `k=8` is the only row with composite `k+1`, and independently replay
   the two endpoint factorizations. It validates semantics and cannot emit a
   novelty candidate.
2. **`SUCCESSOR_PROFILE_SURGERY`:** construct `k+1` from frozen composite
   profiles `q^e` and `q^e r^f`, beginning with but not duplicating the
   `3^2` control. Compute `k`, completely factor `k^2+1`, and evaluate the
   exact signed residual only after both factorizations close. This directly
   varies the coordinate that distinguishes the exception.
3. **`TOTIENT_RATIO_WALL`:** meet in the middle on frozen reduced Euler-factor
   products for `k+1` and `k^2+1`, with the product relation
   `phi(k^2+1)=k*phi(k+1)` checked as an exact integer identity. Candidate
   assembly must also satisfy the rigid translation `k^2+1`; ratio matches
   without a complete translated endpoint are diagnostic rows only.

### 48/54/60 stop discipline

Each arm gets an in-process construction horizon of 48 seconds, must stop
launching factor children and finalize its append-only ledger by 54 seconds,
and runs inside a 60-second external process-group cap. Factorization and
primality children receive shorter explicit subcaps. A deadline prefix is
`CAP_PREFIX`, not `DOMAIN_EXHAUSTED`.

Stop at the frozen profile universe or cap. Do not add a prime, exponent,
profile, factor backend, interval, or ratio bucket after seeing a residual.
Probable primes, incomplete cofactors, and ratio-only matches are
`INCOMPLETE_FACTOR_CERTIFICATE`, never candidates. Any hit at `k=8`, in the
source table, or with prime `k+1` is a control/theorem-shadow hit and cannot be
promoted.

## 2. A108569 — remove the even-lift coordinate

### Literal counterexample and certificate burden

Let

```text
A(k) := 0 < k and phi(k) = phi(k + phi(k)),
R(k) := phi(k + phi(k)) - phi(k).
```

Mathematically, any odd `k>1` with `R(k)=0` crosses the source conjecture. The
literal Lean theorem is stated through `a(n)=n.nth A`, however, so a formal
counterexample must also bind

```text
i = Nat.count A k,
a(i) = k,
i > 0.
```

Complete factorizations of `k` and `k+phi(k)` certify the equality, but they do
not by themselves certify the enumeration index. This is why A108569 remains
behind A067720 despite its clean parity wall.

### Theorem subtraction and arms

The OEIS source proves an even lift: an even member produces `2^m*k` members,
and it records a more general divisor lift. Subtract every such even lift.
The separating coordinate is the odd prime-exponent core itself.

Use three separately frozen arms:

1. **`CATALOGUE_LIFT_CONTROL`:** replay all 384 source rows, the index offset,
   the source lift identities, and every complete factorization.
2. **`ODD_CORE_PROFILES`:** enumerate frozen odd prime-power and mixed-power
   cores; compute `phi(k)`, factor `k+phi(k)` completely, and retain only exact
   `R=0` rows.
3. **`ODD_COLLISION_WALL`:** meet in the middle on frozen odd Euler-factor
   profiles for the two endpoints, then enforce the exact translation by
   `phi(k)`. Profile collisions that do not assemble to the same `k` are wall
   diagnostics, not candidates.

Use the same 48-second search, 54-second finalization, and 60-second external
caps. Stop at the odd-core universe or cap. A mathematical odd member without
a complete `Nat.count`/`Nat.nth` replay is `SEMANTIC_CANDIDATE_ONLY`. No even
lift, table row, partially factored endpoint, or post-result profile extension
may be promoted.

## 3. A103151 — direct finite miss, but no sharp equality wall

For `n>=4`, the declaration asserts that there is an odd prime `p` for which

```text
q = 2*n + 1 - 2*p
```

is prime. A literal counterexample is an explicit `n` and, for every eligible
odd prime `p<=n`, a nontrivial factor of `q`. This is direct and finite, with no
answer wrapper or enumeration rank, and the current 10,777 source rows provide
a sizeable calibration prefix.

The obstruction is certificate scale: unlike A067720 and A108569, the target
has no currently justified equality/tightness identity that collapses the
candidate family. Its natural structural attempt is a residue cover of the
eligible `p` classes, with explicit treatment of the exceptional cases where
an assigned divisor equals `q`.

If this fallback is ever frozen, use `CATALOGUE_CONTROL`, a fixed
`RESIDUE_COVER_SYNTHESIS` universe, and an independent
`EXCEPTION_FACTOR_REPLAY` arm. Apply the same 48/54/60 caps. Stop immediately
if the frozen modular family leaves any eligible prime class uncovered; do not
fall back to an enlarged flat Goldbach search. A sieve miss without a complete
factor for every `q` is not a counterexample certificate.

It ranks third because its literal resolution shape is better than the
answer-wrapped alternatives, but its separating coordinate is materially less
developed than either reserve.

## Challengers that do not displace the reserves

- **A108864:** an odd number after 1155 with perfect deficiency at most 10 is a
  compact intended-source witness, and parity splits the wall into equations
  `sigma(k)-2k=d` for `-10<=d<=10`. The formal theorem is answer-wrapped and
  uses `Nat.nth`, so it inherits both answer semantics and a rank certificate;
  it is not cleaner than A108569.
- **A109905:** another zero would have a finite compositeness certificate, but
  the source reports none through `10^9`, and certificate length grows with
  `n/2`. No compact cover identity currently offsets that cost.
- **A113609:** a second pair of composite prime powers at distance two would be
  a tiny positive certificate, but the theorem is answer-wrapped and the
  proposed exponential-Diophantine search has no better prospective wall than
  the direct A067720 totient equality.
- **A103662, A105210, A110566, and asymptotic OEIS declarations:** their
  negations require eventual, infinite, or nonexistence evidence rather than a
  finite counterexample certificate.
- **A034693 and similar large interval assertions:** formally finite but not
  GitHub-CI-friendly; the certificate must settle an enormous interval, and
  the relevant periodic-cover direction has the same escape obstruction
  already exposed by A231201.

## Selection

Freeze **A067720 only** as the next DeepMind development rotation, after one
last live recheck of upstream `main`, all open PR changed-file lists, exact
issue/PR terms, the OEIS record, and local releases. Retain A108569 as the
ordered reserve. A bounded zero on A067720 is useful only as prospective
method evidence about composite-successor profile surgery; it is not evidence
that the universal conjecture is true and does not authorize an adaptive
extension.
