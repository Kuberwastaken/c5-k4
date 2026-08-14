# OEIS A231201 v3 observed-design scout

Date: 2026-08-14 UTC

Input run: [`31812806288`](https://github.com/Kuberwastaken/c5-k4/actions/runs/31812806288)

Immutable campaign commit: `74f904b66edcb191f2172eaf04c303b438648b74`

Classification: contaminated DEVELOPMENT design work, not a search result

## Scope and non-claims

This report uses the completed v2.2 execution to choose a different next
iteration. It does not modify the v2.2 result, run a target search, certify a
cover, produce a candidate `n`, resolve A231201, or support a release. The six
target assignments below are used only as bounded design diagnostics.

Any v3 execution must retain the unchanged source/DB sanity gate, exact
least-positive semantics, immutable campaign commit, hash-chained receipts,
independent final replay, and the standing 60-second external cap. Construction,
adversary, and final verification must each reserve finalization time inside
that cap.

## What v2.2 actually taught us

Only `SMALL_BASIS_CEGAR` round zero emitted assignments. Each covered 192
low-discrepancy active rows. All six exact adversaries completed the same
`q=17` level with 368,640 live CRT states of modulus 2,042,040, then reached an
honest deadline while processing `q=19`:

| cell | assignment SHA-256 | q19 inputs processed | partial q19 states |
|---|---|---:|---:|
| `0_0` | `dc437cdec85bcd3469cfbbe46c3540765ba4887a9627b8656353ab8cdf9b794d` | 253,820 | 13,706,282 |
| `0_1` | `267a91722999291aba9c22464c5b60e8e940bf11be2829dc31f30a652a42a569` | 249,455 | 13,470,619 |
| `0_2` | `ec269746aa44d3890ced4871e00e8390ae995511292353ace1249679a42be66f` | 249,315 | 13,463,061 |
| `1_0` | `5dd3efe67b33ac4032312dd6f0c1789ff2276bcdcc3953fdcd6385a91b25e9d3` | 334,789 | 18,078,619 |
| `1_1` | `b6172fb28b99d49bc442f2fc2cc51fe81a0add3c6d61bfbe31079c2227397bed` | 242,711 | 13,106,410 |
| `1_2` | `b080f5b91b7ccc1ecb12b4713390f998e069a326a4e6a404e2750dd4d63421b8` | 253,901 | 13,710,669 |

The partial ratio is 54 surviving states per processed q19 input in every
cell, up to the one in-progress split recorded by the deadline cursor. A full
explicit q19 level would therefore contain exactly
`368,640 * 54 = 19,906,560` states. More wall time would only materialize this
known explosion.

Round one repeated the same 192-row assignments because the adversary returned
deadlines, not replayable uncovered exponents. Round two expanded the basis to
320 rows and emitted no assignment. The other two construction arms emitted no
assignment in any round. Thus v2.2 produced zero candidates and no mathematical
result.

## Bounded diagnostic: the basis missed the local wall

A single hard-capped diagnostic scanned only `x=1..4096`, in increasing order,
against each of the six already-emitted assignments. It used the frozen
`direct_value(q,x)` predicate and stopped at the first exponent missed by all
55 assigned residues. Invocation was enclosed by
`timeout --signal=TERM --kill-after=6s 60s`; all six checks together took
0.064238 seconds.

| cell | least missed `x` in `1..4096` |
|---|---:|
| `0_0` | 3 |
| `0_1` | 5 |
| `0_2` | 29 |
| `1_0` | 6 |
| `1_1` | 6 |
| `1_2` | 22 |

These are design observations, not conjecture witnesses. They explain why the
low-discrepancy basis was a poor first wall: it spread 192 constraints over the
whole seed interval instead of first closing its short contiguous prefix. For
example, the `0_0` final basis begins
`1, 2049, 3073, 513, 1537, 3585, ...`; it does not contain `3`.

The v3 master should therefore optimize the least missed exponent first. A
wide-distribution basis remains useful only after a contiguous prefix has been
closed.

## Static ordering calculation

At the completed q17 modulus `M=2,042,040`, processing a prime `q` expands each
state by

`lcm(M, q*ord_q(2))/M`

splits. When `ord_q(2)` already divides `M`, exactly one of the `q` split
classes has `x-2^x = a_q (mod q)`, so precisely `q-1` survive. This gives the
following exact one-step counts without evaluating another target frontier:

| next prime | survivors/input | resulting states | reduction from q19 |
|---:|---:|---:|---:|
| 19 | 54 | 19,906,560 | baseline |
| 23 | 22 | 8,110,080 | 59.26% |
| 29 | 28 | 10,321,920 | 48.15% |
| 31 | 30 | 11,059,200 | 44.44% |

Using the prior v2.1 observation of roughly 1.8 GiB for 67 million explicit
states only as a normalized storage proxy, these queues correspond to about
0.535, 0.218, 0.277, and 0.297 GiB respectively. Those are not Python peak-RSS
guarantees.

Dynamic ordering is justified as a pressure reducer, but not as a solution:
after the same set of primes has been processed, the exact uncovered set is
order-independent. Ordering changes intermediate width and when a useful
counterexample is exposed; it does not remove the eventual explicit-product
blow-up.

## Proposed v3 arms

### Arm 1: `LEXICOGRAPHIC_ESCAPE_CEGAR` — primary

1. Begin each `(a2,a3)` cell with active exponents in increasing order, not the
   bit-reversal order.
2. Require a complete assignment to cover a frozen contiguous prefix first.
   Start with 256 active rows and grow by the next 128 active rows after each
   adversary miss.
3. Before any CRT frontier work, scan the entire frozen seed `1..4096` exactly
   and return the least missed exponent. Append that exponent as a mandatory
   master clause and warm-start from the previous assignment.
4. Preserve a secondary low-discrepancy sample only as a tie-break/regularizer
   after the contiguous prefix objective.
5. Deduplicate by `(assignment SHA-256, least-missed-x)` and persist each
   assignment before its adversary call.

Expected improvement: on the six v2.2 assignments, this arm would have produced
an exact useful clause in at most 29 direct exponent checks rather than spending
48 seconds at q19. The diagnostic is retrospective and does not predict that a
repaired master will find another assignment within its cap.

### Arm 2: `SYMBOLIC_MIN_ESCAPE` — exact complement backend

Do not represent the complement as millions of explicit CRT residue pairs.
Factor the combined periods into shared prime-power coordinates and encode, for
each selected prime `q`, the exact forbidden relation
`x mod q = a_q + 2^(x mod ord_q(2)) mod q`. Use a reduced decision diagram,
SAT/SMT encoding, or exact bucket-elimination table over those shared
coordinates, with the objective of finding the least positive avoiding `x`.

The output is either:

- a concrete least missed `x`, independently checked against all 55 frozen
  periodic predicates and fed back to the master; or
- a proof-trace-supported exhaustion of the bounded interval actually needed
  by a proposed candidate.

The important change is **bounded minimum escape**, not unbounded periodic
coverage. A design invariant worth proving before dispatch is that primes can
be introduced in ascending order while their own `x mod q` coordinate is still
fresh; this appears to construct an unbounded avoiding residue class cheaply.
If independently proved, that would rule out complete periodic coverage by
this finite 55-prime mechanism, but it would not rule out covering only
`1 <= x < n`. This report does not elevate that invariant to a mathematical
claim.

Resource freeze: cap the symbolic node/learned-clause store at 500,000 entries
and emit `SYMBOLIC_RESOURCE_CAP` with a replayable prefix when reached. At a
conservative 64 bytes per node this is about 30.5 MiB, over an order of
magnitude below the normalized q19 explicit queue estimate.

### Arm 3: `DYNAMIC_ORDER_STREAM` — bounded fallback

Retain the exact streaming adversary only as a fallback and choose the next
prime deterministically by the tuple

`(predicted surviving states, lcm-growth factor, q)`.

Recompute the score from the current modulus after every completed level and
record the complete chosen order and score table in the hash chain. Maintain a
fixed max-heap of the 4,096 least positive uncovered representatives while
streaming. On a deadline, persist those representatives, their predicate
checks, the exact cursor, and the prefix digest; feed the verified
representatives back as master clauses. Never persist or reconstruct a
multi-million-state partial queue merely to continue it.

The q23 calculation shows a 59.26% immediate width reduction at the observed
wall. The 4,096-representative heap is below 1 MiB for compact integer/hash
records, versus 13.1–18.1 million partial states in v2.2. Because ordering
cannot change final set size, this arm must stop after one useful clause batch
or a bounded symbolic handoff; it must not become a longer explicit search.

## Recommended freeze and stop rules

Freeze only Arms 1–3. Arm 1 should run first because the observed assignments
fail locally. Arm 2 is the substantive representation change. Arm 3 is an
instrumented source of exact clauses, not the main solver.

Every stage must distinguish:

- `LEAST_ESCAPE_FOUND`: verified exponent and assignment binding;
- `SYMBOLIC_RESOURCE_CAP`: bounded exact prefix, no coverage claim;
- `ADVERSARY_DEADLINE`: bounded exact stream prefix, no coverage claim;
- `BOUNDED_INTERVAL_EXHAUSTED_PENDING_FINAL`: never a result until independent
  replay passes;
- `NOT_RUN` and `PREREQUISITE_NOT_RUN`: explicit absent-stage terminals.

Stop the A231201 residue-assignment lane after one frozen v3 execution if it
again fails to move the least missed exponent materially beyond the contiguous
seed, or if the ascending-coordinate invariant is independently proved and the
bounded-minimum backend cannot compare its escape with a candidate `n` inside
60 seconds. In either case, more explicit frontier width is not evidence for
the repository's discovery method and should not consume another iteration.

## Checks performed

- Read-only GitHub artifact inventory: 163 immutable artifacts for run
  `31812806288`.
- Downloaded only the six round-zero `SMALL_BASIS_CEGAR` construction and six
  paired adversary artifacts; no workflow was dispatched.
- Verified artifact-reported assignment SHA-256 bindings and extracted the q17
  completed rows and q19 deadline rows.
- Recomputed the static q19/q23/q29/q31 lcm multipliers from the frozen
  `order_two` table.
- Ran the one bounded `x=1..4096` diagnostic under the external 60-second cap;
  no full adversary, target solver, candidate check, or final verifier ran.
- README, v2.2 `result.md`/`result.json`, workflows, scripts, releases, and git
  history were not modified by this scout.
