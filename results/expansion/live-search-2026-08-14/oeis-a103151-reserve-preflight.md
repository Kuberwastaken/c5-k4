# OEIS A103151 reserve preflight

**Audit date:** 2026-08-14 UTC

**Classification:** `DEFER`

**Rank:** best remaining current-main direct finite-universal reserve

**Evidence split:** contaminated `DEVELOPMENT`, not held out

**Evaluation:** none

This is a source/status, novelty, and method-shape preflight after the completed
joint A109908/A109909 bounded zero. It does not freeze or authorize a search,
evaluate an A103151 target value, claim a bounded mathematical result, or
authorize a release, issue, pull request, or other public action. Catch-Up
`N=24` is a separate frozen lane and is not part of this ranking.

Written on the Wall I is not represented in
`google-deepmind/formal-conjectures` and is outside the scope fixed by
`METHOD.md`. The method's graph-corpus scope includes Written on the Wall II,
not Written on the Wall I or Graph Brain. No WoW I target was inspected, ranked,
or used here.

## Immutable source and status pins

The live formal-conjectures tip resolved to
[`19066fe4bb66314a2e20f5054bbf02b05ae34064`](https://github.com/google-deepmind/formal-conjectures/commit/19066fe4bb66314a2e20f5054bbf02b05ae34064),
tree `4c9fbdb57c9a1a9af2af68ff32fab8266d03dd13`, committed
`2026-08-14T18:33:21Z`.

The exact declaration is
[`OeisA103151.conjecture`](https://github.com/google-deepmind/formal-conjectures/blob/19066fe4bb66314a2e20f5054bbf02b05ae34064/FormalConjectures/OEIS/103151.lean)
in `FormalConjectures/OEIS/103151.lean`:

- Git blob SHA-1: `fec2d6b527fd1c6338aeddc4503bcd96d70ccc6d`;
- raw-file SHA-256:
  `f7f236f5e627853d16212fbc23d873ab2a3ca04591f7ce8c1f36733732e54db4`;
- category: `@[category research open, AMS 11]`;
- body: `sorry`;
- literal statement: for every natural `n >= 4`, the representation count
  `a n` is at least one.

The file entered through merged formal-conjectures
[#4450](https://github.com/google-deepmind/formal-conjectures/pull/4450),
merge commit `d7032450c559849f2a345f80582688c76b25ffcb`. Exact all-state issue and
pull-request searches for `A103151`, `OeisA103151`, `103151.lean`, and
`2n+1 2p+q` returned no resolving item. Exact-path Git history contains only
the ingestion commit. Public GitHub code searches located the upstream
statement, implementations of the sequence, and this project's ranking and
boundary artifacts, but no proof or counterexample certificate.

The authoritative OEIS snapshot was
[`oeis/oeisdata@8872fa543438401edd424a57b67ad5e0737bebfb`](https://github.com/oeis/oeisdata/commit/8872fa543438401edd424a57b67ad5e0737bebfb).
The [A103151 record](https://oeis.org/A103151) has header revision
`#10 Sep 11 2025 18:39:07`; its `.seq` file has SHA-256
`eadc25f02e069f2b9d9bee859616f08a34afe368d6b063a7669f8dece53ab2e5`.
The live b-file contains 10,777 rows, ending in `10777 518`, and has SHA-256
`3da2af0438db1c0e1094c2ebb2c5353a531f78f660cf437fb09fe271fa9b9ec7`.
The OEIS record continues to label positivity for every `n >= 4` a conjecture.

## Historical and computational prior boundary

A103151 is the classical Lemoine--Levy conjecture in the odd-prime form:
every odd integer at least nine is `2p+q` for odd primes `p,q`. It is not a
newly isolated OEIS phenomenon. Farkas and Juhasz, *A generalization of
Goldbach's conjecture* (2017), identify Lemoine's 1894 conjecture and report
three independent computational checks of their coefficient-pair framework
through `10^9`; the pair `(1,2)` contains the A103151 statement:

- [primary paper](https://ac.inf.elte.hu/Vol_046_2017/039_46.pdf);
- downloaded PDF SHA-256:
  `2e62613fb386f91cda991b702f58ce6f83d5b6658eef33a991e2219481bbd8ad`.

Therefore every proposed `n <= 10^9` is historical calibration, never a
novelty candidate. Negative novelty searches cannot establish global absence
of private, unindexed, or unpublished work, so the same checks must run again
immediately before any later dispatch.

## Local exposure and contamination

A103151 is already exposed in the repository's benchmark inventories and
contamination records. It was classified in the finite-combinatorial stratum,
appears in the question-cluster pool, and is marked `EXPOSED` after
contamination application. The live-search boundary audit also evaluated the
published controls `n=4,5,6`, obtaining `a(n)=1,1,2`, and multiple committed
rotation reports discussed and ranked the target and its residue-cover idea.

This contact is enough to exclude A103151 from future held-out evidence even
though no target-specific frozen search, candidate, proof, release, or claimed
result exists. Any authorized lane would be explicitly adaptive
`DEVELOPMENT` evidence.

## Literal negation and exact residue wall

For `n >= 4`, let

```text
a(n) = #{odd primes p <= n : q = 2n + 1 - 2p is prime}.
```

The exact residual wall is `a(n)=1`, and the crossing is `a(n)=0`. A literal
counterexample certificate contains one explicit `n`, the complete set of
eligible odd primes `p`, and for every corresponding
`q = 2n+1-2p` an exact proper divisor. The endpoint, odd-prime, positivity,
and natural-subtraction conventions must match the Lean definition.

For a frozen odd prime divisor `r`, with `2^-1` interpreted modulo `r`,

```text
r divides (2n + 1 - 2p)  <->  p = n + 2^-1 (mod r).
```

For a frozen divisor family `D`, define `U_D(n)` to be the least eligible odd
prime `p <= n` for which the assigned classes in `D` do not provide a proper
divisor of `q`. Values with `q <= 1` or assigned divisor `r=q` are explicit
exceptions, not composite certificates. The finite-prefix cover crosses only
if `U_D(n)>n` and every assigned divisor is proper.

## Why this is not yet a sharp method wall

The congruence is an exact construction coordinate, but no committed family
currently pins `U_D(n)` near `n`, gives a closed form for the source's
`a(n)=1` rows, or supplies a frozen sign-potential predicting a crossing.
Moreover, a finite `D` cannot cover all primes globally. For each `r in D`,
one may choose a nonzero residue distinct from the single assigned class;
CRT leaves reduced residue classes avoiding every assignment, and primes occur
in such classes. A finite divisor family can therefore attempt only a bounded
prefix whose first escape happens after `n`, not an infinite covering system.

That bounded construction may still be useful, but without a justified
least-escape geometry it is substantially closer to extending a heavily
studied Lemoine computation than to the method's
`tight carrier -> obstruction identity -> separating transformation` pattern.
A flat `n` scan, a longer sieve prefix, or an adaptively enlarged divisor set
would be brute-force calibration and must not be counted as wall-navigation
evidence.

## Barker comparison and strict stop

The only newly added current-main declaration with a literal finite
counterexample object is
[`Arxiv.2104.00502.barker_conjecture`](https://github.com/google-deepmind/formal-conjectures/blob/19066fe4bb66314a2e20f5054bbf02b05ae34064/FormalConjectures/Arxiv/2104.00502/BarkerSequence.lean),
introduced by merged
[#4793](https://github.com/google-deepmind/formal-conjectures/pull/4793). Its
file SHA-256 is
`084b802cc01efb2cfc09e7866e348c754f32d88fdcec99671ec3ed035bb45e68`,
and it remains `research open` with `sorry`.

It does not displace A103151. Willms's source states that odd lengths above 13
are theorem-closed and that even Barker sequences are already excluded for
`4 < n <= 4*10^33`:

- [arXiv:2104.00502](https://arxiv.org/abs/2104.00502);
- downloaded PDF SHA-256:
  `838955d6e8c48b7a8e4fc0db0897c628aab3c7db2483a9dc45de93787e51b266`.

Thus a GitHub-CI-sized enumeration of short lengths is entirely preempted.
Barker is `PRIOR_RANGE_STRICT_STOP` unless a new theorem-derived
symmetry/pruning operation reaches a previously unexcluded even length; an
ordinary bounded zero there would be method calibration, not discovery
evidence.

## Classification and conditional frozen shape

**Classification: `DEFER`.** A103151 is the best remaining current-main direct
finite-universal reserve after subtracting completed lanes, theorem shadows,
formalization defects, and the A109908/A109909 bounded zero. It is not ready
for `GO`: the direct certificate is finite and the public status is open, but
the proposed residue family lacks a sharp pre-evaluation wall and has a large
certificate burden.

A later authorization should freeze a search only after a separate analytic
or solver preflight demonstrates credible least-escape pressure in a fixed
universe. The conditional shape is:

1. **`CATALOGUE_CONTROL`:** content-lock both upstream files and replay all
   10,777 OEIS rows with two independent prime enumerators. These rows cannot
   emit novelty candidates.
2. **`RESIDUE_COVER_SYNTHESIS`:** before target evaluation, freeze `D`, every
   allowed `n mod r` profile, CRT representative ordering, deterministic seed,
   candidate interval strictly above `10^9`, maximum bit length, shard map,
   and the exact definition and tie order of `U_D`.
3. **`EXCEPTION_FACTOR_REPLAY`:** accept a candidate only after a complete
   segmented-prime replay of every eligible `p`, explicit handling of `q=r`
   and boundary cases, and exact proper factors for every remaining `q`.
   Independent replay must reconstruct the interval and factors rather than
   trust a sieve bitmap or solver model.
4. **Caps:** each shard constructs through 48 seconds, stops launching child
   work and finalizes durable output by 54 seconds, and runs inside a
   60-second external process-group cap. Every factorization and primality
   child has its own shorter cap.
5. **Terminal discipline:** use `NO_COMPLETE_FINITE_PREFIX_COVER`,
   `CAP_PREFIX`, `DOMAIN_EXHAUSTED`, `SANITY_GATE_FAILED`, or a fully verified
   candidate. Do not add divisors, enlarge the interval, change the solver, or
   fall back to a flat Goldbach scan after observing the result.

No target instance was evaluated during this preflight. No workflow, commit,
push, release, issue, or pull request is authorized by this document.
