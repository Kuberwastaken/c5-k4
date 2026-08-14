# OEIS A231201 held-out preflight: strict stop

**Audit date:** 2026-08-14 UTC
**Held-out disposition:** `STRICT_STOP_NOT_HELD_OUT_EXISTING_TARGET_SPECIFIC_EXPOSURE`
**Development disposition:** `FREEZE_ELIGIBLE_CONTAMINATED_NOT_AUTHORIZED`
**Target evaluated in this preflight:** no
**Search authorized or dispatched:** no

This report preflights DeepMind Formal Conjectures' OEIS A231201 declaration
as a possible held-out prospective lane. It is not a result, contract launch,
claim, release, or upstream action. The held-out lane must not run: the target
and the proposed covering-congruence mechanism both have prior, public,
target-specific computational exposure.

Contamination does not make the mathematics or certificate shape unsuitable
for the separately labelled DEVELOPMENT loop. The finite residue-cover design
below is sound enough to freeze as a contaminated development continuation;
it is not authorized for execution by this preflight.

## Current upstream statement and status

The live `google-deepmind/formal-conjectures` `main` tip at audit time was
[`4010c1f1b811be0b0f95c9cf8bc084d72cea2a88`](https://github.com/google-deepmind/formal-conjectures/commit/4010c1f1b811be0b0f95c9cf8bc084d72cea2a88)
(2026-08-14 10:40:05 UTC). At that commit:

- path: `FormalConjectures/OEIS/231201.lean`;
- Git blob SHA-1: `2fc0d6bf46e910481242688c713985eb4d26e972`;
- module SHA-256:
  `3cfc75e1613477cd4087e6fe9406658e27981abc2c0834958a311e9551bc8fa1`;
- declaration: `OeisA231201.conjecture`;
- category: `@[category research open, AMS 11]`;
- statement:

```lean
def A (n : ℕ) : Prop :=
  ∃ x y : ℕ, 0 < x ∧ 0 < y ∧ n = x + y ∧ (2^x + y).Prime

theorem conjecture (n : ℕ) (hn : 1 < n) : A n := by
  sorry
```

The source file is byte-identical to the version previously pinned locally in
July 2026. The current [OEIS entry](https://oeis.org/A231201) still calls
`a(n)>0` for every `n>1` a conjecture and reports verification through
`10^7`. Its downloadable `n=1..10000` b-file had 10,000 rows (plus its blank
first line) and SHA-256
`5e4e34c5132b40f4666ed04000615b4d652a6af46c9a2ad5022c725d293e5ace`
at this audit. The OEIS page links Han--Yu's May 2026
[positive-density theorem](https://arxiv.org/abs/2605.15758); that theorem
proves density at least `0.0734`, not the universal assertion.

### Repository item and commit search

Exact searches over open and closed issues, open/closed/merged pull requests,
and commits found only the ingestion chain:

- closed issue [#1486](https://github.com/google-deepmind/formal-conjectures/issues/1486);
- merged PR [#1580](https://github.com/google-deepmind/formal-conjectures/pull/1580);
- ingestion commit
  [`4c8a3bc21c8a4fb00f7280b153fd6fed7825905e`](https://github.com/google-deepmind/formal-conjectures/commit/4c8a3bc21c8a4fb00f7280b153fd6fed7825905e).

No upstream item claims a proof or counterexample to the exact declaration.
The `FC100SolvedSet1` import is not such a claim: it selects the proved test
declaration `OeisA231201.a_8`, not `OeisA231201.conjecture`. A public `fc100`
copy under a directory named `FC100Solved` also leaves the conjecture as
`sorry` and is not a solution.

## Resolution card and the registry ambiguity

For fixed `n`, positivity and `n=x+y` force `1 <= x < n` and `y=n-x`.
Therefore the literal negation is the finite proposition

```text
∃ n > 1, ∀ x in {1,...,n-1}, 2^x + n - x is composite.
```

An explicit `n`, together with one proper factor for each of its `n-1`
values, is a finite exact disproof certificate. The Phase-0 resolution card is
therefore:

```json
{
  "logical_class": "FINITE_UNIVERSAL",
  "target_negation": "there exists n>1 such that every 1<=x<n makes 2^x+n-x composite",
  "negation_certificate": "n plus a proper-divisor table covering x=1..n-1, or a finite periodic divisor cover implying that table",
  "finite_witness_suffices": true,
  "exact_residual": "r(n)=#{x:1<=x<n and Prime(2^x+n-x)}; failure means r(n)=0",
  "answer_placeholder": false,
  "eventual_quantifier": false,
  "global_constant_quantifier": false,
  "unbounded_auxiliary_search": false
}
```

This resolves the scout's *logical-shape* ambiguity: the v1.4 syntactic
classifier recorded `UNCLASSIFIED_WITHOUT_FINITE_SIGNAL`, then conservatively
promoted that to cluster status `AMBIGUOUS_EXCLUDE`. It failed to infer the
bounds on the nested existentials. A human Phase-0 card may classify this
declaration as finite-combinatorial for a **development** counterexample lane.
It must not retroactively mutate the immutable v1.4 registry or make the
target held out.

That classification issue is separate from contamination, and the
contamination record is decisive.

## Decisive prior target exposure

The production contamination inventory correctly records A231201 as
`EXPOSED`, with `SEMANTIC_SOURCE` evidence rather than mere registry contact.
Two public histories independently defeat a held-out interpretation.

### This user's prior exact A231201 experiment

`Kuberwastaken/breakthroughmaxxing` commit
[`62c190b23cdc8c03e6fd65f11c7ae28a5d8258d5`](https://github.com/Kuberwastaken/breakthroughmaxxing/commit/62c190b23cdc8c03e6fd65f11c7ae28a5d8258d5)
(2026-07-24) contains the target-specific lane
[`06-bigger/oeis231201-first-over64`](https://github.com/Kuberwastaken/breakthroughmaxxing/tree/62c190b23cdc8c03e6fd65f11c7ae28a5d8258d5/06-bigger/oeis231201-first-over64).
It evaluated the exact predicate, exhaustively established

```text
max {L(n): 2<=n<=326} = L(220)=59,
L(327)=72,
```

and independently certified the prime at the sharp case. The committed
certificate SHA-256 is
`8d1e10af9c9abe39261678bd03c623af62ceecd92af8f79e3f753cca605a08a6`.
This did not extend the OEIS `10^7` existence boundary, but it is still direct
semantic and computational exposure to the exact target.

### The proposed construction was already tried publicly

`txmy/ultra-mathematician` contains an explicit
[`solve-a231201-covering`](https://github.com/txmy/ultra-mathematician/tree/d52f81ad64dfc77e9a89dee8ae97db983ac6d5f7/runs/run-2026-07-26-002/tasks/solve-a231201-covering)
lane dated 2026-07-26. It derives the same coordinate

```text
n mod q = x - 2^x mod q
```

and uses CP-SAT to choose one residue of `n` for each prime. Its committed
results exactly exhausted prime bounds `7`, `11`, and `13`, returning
`INFEASIBLE` for combined periods `420`, `4620`, and `60060` respectively.
Thus the residue-cover attack is not a fresh held-out mechanism; increasing
the frozen prime bound would be continuation of an exposed development lane.

The correct registry resolution is consequently:

```text
logical shape:       finite-counterexample eligible after human Phase 0
semantic exposure:   yes
unknown exposure:    immaterial once semantic exposure is established
held-out eligibility:no
development use:     possible only if explicitly relabelled contaminated
```

## Corrected exact design (development-only, not authorized)

The following freezes the scout's suggested extension precisely enough to
avoid a post-result change of universe. It is recorded only as a
**contaminated DEVELOPMENT continuation**. This preflight does not authorize
implementing or running it.

### Frozen residue universe

Let `P` be exactly the 55 primes at most 257:

```text
2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,
73,79,83,89,97,101,103,107,109,113,127,131,137,139,149,151,
157,163,167,173,179,181,191,193,197,199,211,223,227,229,233,
239,241,251,257
```

For `q in P`, define `o_q=ord_q(2)` (`o_2=1`) and
`m_q=q*o_q`. For each `a in {0,...,q-1}`, define the exact covered classes

```text
C(q,a) = {r in Z/m_q Z : r - 2^r = a (mod q)}.
```

The only construction variables are `a_q in Z/qZ`, one per prime. A model is
acceptable exactly when

```text
for every integer x, some q in P has x mod m_q in C(q,a_q).
```

The combined period is the exact 357-bit integer

```text
249728679334046128590697275594786190851950664265138725258656853072581268625525551538208526056090039506543200.
```

Direct enumeration of this 108-digit period, as the scout's informal "one
finite SAT/set-cover" wording might suggest, cannot satisfy a 60-second cap.
The implementation must use counterexample-guided residue constraints plus an
exact generalized-CRT coverage verifier; replacing this with period scanning,
flat `n` scanning, random residues, or a larger prime bound changes the frozen
experiment.

### Frozen search and independent verifier

1. Recompute primality of `P`, each `o_q`, `m_q`, and the combined period with
   plain integer arithmetic. Any mismatch is `PREPARATION_FAILED`.
2. Use Python 3.9 and `ortools==9.15.6755`, one CP-SAT worker and random seed
   zero. The master has exactly-one constraints for every `a_q`. It begins
   with exponent representatives `x=0,...,4095` and lexicographically adds
   one uncovered generalized-CRT class returned by the verifier per
   iteration. Variable order is ascending `(q,a)`; no objective is used.
3. For a proposed assignment, the independent verifier does not import the
   model builder. It refines congruence classes in ascending `q` order. A
   state `(r,M)` is split into all residues modulo `lcm(M,m_q)` compatible
   with `r mod M`, discarding exactly those in `C(q,a_q)`. Empty final state
   proves complete coverage; the least surviving `(r,M)` is the next master
   counterexample.
4. A complete cover yields CRT congruences `n=a_q (mod q)`. Let
   `Q=product(q in P)` and choose the least positive member `n=n_0+kQ`
   strictly above `10^7`. Because `2^x-x>=1` for `x>=1` and `n>257`, every
   assigned divisor satisfies `1<q<2^x+n-x`.
5. Independent replay must rebuild the CRT solution, coverage tree, every
   modular exponent, and the proper-divisor inequalities. A solver model or
   probable-prime output is not a certificate.

No candidate `n`, residue assignment, or coverage outcome was computed in
this preflight.

### Source/database sanity gate

Before any construction process launches, a separately capped gate must:

- match current upstream commit, path, blob, module hash, declaration header,
  exact statement, and `research open` category to a committed manifest;
- retrieve and hash the live OEIS statement and b-file, match offset `1,5`,
  the definition of `a(n)`, and the prior boundary `10^7`;
- independently reproduce all 10,000 b-file counts by enumerating
  `x=1,...,n-1`, using proof-producing deterministic primality checks;
- replay the Lean controls `n=2,3,4,5,8,53`, plus the OEIS examples `53` and
  `64`, checking positivity, `x+y=n`, and primality;
- verify the earlier public `L(327)=72` certificate as a contamination
  control, never as new evidence; and
- bind the external covering results at bounds `7`, `11`, and `13` as prior
  development controls. Reproducing them is calibration, not a success.

Any source drift, count mismatch, incomplete deterministic prime proof,
missing contamination control, or cap expiry terminates
`SANITY_GATE_INCOMPLETE`. No construction arm may launch after that status.

### Incremental output and caps

- The gate, master, CRT adversary, and final verifier are distinct process
  trees. Each has a 54-second internal deadline inside a 60-second external
  process-group cap; the external wrapper sends `TERM` at 60 seconds and
  `KILL` six seconds later.
- Append and `fsync` one canonical JSONL row after every gate chunk, master
  model, adversary refinement level, returned uncovered class, and terminal
  event. Rows form a SHA-256 hash chain. A checkpoint binds the ordered state
  queue and solver response after every CEGAR iteration.
- Terminal receipts bind the upstream/source hashes, dependency versions,
  frozen prime list, order table, combined period, last row hash, ledger hash,
  counters, elapsed time, and exit/signal status.
- `COVER_FOUND_PENDING_VERIFY` is not a result. Only independent replay can
  promote it to `VERIFIED_COUNTEREXAMPLE`.
- A deadline is `DEADLINE_PREFIX`, never `NO_COMPLETE_COVER`. Solver
  `INFEASIBLE` is `SOLVER_INFEASIBLE_UNVERIFIED` unless a separate exact
  exhaustive certificate is replayed. `NO_COMPLETE_COVER` is allowed only
  after such replay.

## Terminal decision

- Exact upstream declaration: still open.
- Duplicate upstream solution/claim: none found.
- Human resolution-shape ambiguity: resolved; a finite disproof certificate
  suffices.
- Prior target-specific evaluation: present and public.
- Prior residue-cover construction: present and public.
- Held-out prospective lane: **ineligible**.
- Contaminated DEVELOPMENT freeze: **eligible on the exact design above, but
  not authorized or dispatched here**.
- Search contract, candidate evaluation, Actions dispatch, README edit,
  commit, push, release, issue, PR, or other outward action: **none**.

A231201 may be revisited only as an explicitly contaminated DEVELOPMENT
continuation. It must not be counted as a new held-out lane or as independent
evidence for prospective method efficacy.
