# Erdős 373 maximal factorial-product solution: DEVELOPMENT preflight

**Audit date:** 2026-08-14 UTC

**Disposition:** `GO_FOR_FREEZE_AFTER_SOURCE_BOUND_GATE`

**Evaluation state:** `NOT_EVALUATED`

**Authorization:** none

This is a source, status, semantics, and crossing-reachability preflight. It
does not freeze or run a target search. No `n >= 17` target instance was
evaluated, no candidate or bounded result exists, and no workflow, dispatch,
release, issue, pull request, or other public action is authorized by this
document.

## Immutable target identity

The GitHub commits API resolved `google-deepmind/formal-conjectures` `main` to

```text
commit  2411d22e1bd550d050d0eac6c1fb379a76a3e7c5
tree    f6b52f1d3f63b365d6f8c405623d5f7a4e674efc
date    2026-08-14T19:16:38Z
```

at the audit time. The selected object at that exact tree is:

```text
path       FormalConjectures/ErdosProblems/373.lean
mode       100644
blob       e4d534288b0e5eade9169f8b5d23fb22b1d3b286
bytes      3342
SHA-256    032d4e1e4f9ae9ecd3281873ebd75ecac9c200f4476aa2214d18624d24a36204
declaration Erdos373.erdos_373.variants.maximal_solution
header SHA-256 91d0b1e3d95e1ed3426f9562dbbded27407ae83fbb3d3a743c539ff53eab9986
```

Pinned source:
[`373.lean`](https://github.com/google-deepmind/formal-conjectures/blob/2411d22e1bd550d050d0eac6c1fb379a76a3e7c5/FormalConjectures/ErdosProblems/373.lean).
The declaration is still literally tagged `@[category research open]` and has
a `sorry` body at this pin.

The module defines

```text
S = {(n,l) |
       n! = product (map factorial l),
       l is pairwise nonincreasing,
       l.headI < n-1,
       and every a in l satisfies 1<a}.
```

The selected theorem is exactly

```text
(16,[14,5,2]) in S  and  every s in S has s.fst <= 16.
```

Consequently its literal negation is

```text
(16,[14,5,2]) notin S
or
there exists (n,l) in S with 16<n.
```

The first disjunct is a source control, not a discovery direction. The proposed
lane targets only the second disjunct. A literal counterexample must therefore
serialize one natural `n >= 17` and one finite list `l` such that all four
defining conditions of `S` replay exactly. Merely finding a numerical near
equality, a probable factorization, or a solution with `l.headI = n-1` is not a
counterexample.

## Public status and duplicate audit

Exact GitHub issue and pull-request searches were run in both open and closed
states for `erdos_373`, `Erdos373`, `14!5!2!`, `Suranyi-Hickerson`, and
`Hickerson`, restricted to `google-deepmind/formal-conjectures`.

- There were zero open issues and zero open pull requests for every term.
- `Erdos373`, `14!5!2!`, `Suranyi-Hickerson`, and `Hickerson` returned zero
  closed issues and zero closed pull requests.
- `erdos_373` returned four closed pull requests: #2746, #2755, #3267, and
  #3276. All four concern only the already `research solved` conditional
  declarations `erdos_373.variants.of_limit` and
  `erdos_373.variants.of_lower_bound`. None claims, edits, proves, or disproves
  `variants.maximal_solution`.
- Exact-path history contains no later resolution. The most recent path commit,
  `c252a41054125b5fd9c8356e2137cd9b55337657`, only changed the shared utility
  import during repository refactoring.

The same exact identities were searched locally outside frozen benchmark
inventories. There was no result, report, candidate, script, workflow,
publication record, commit message, tag, pull request, or release for Erdős
373, Surányi--Hickerson, or the factorial-product wall before this preflight.

This is a point-in-time textual and path audit, not knowledge of private work.
A later freeze must repeat it and must additionally enumerate every then-open
upstream PR's changed files. Any open PR touching the target path, any status
change, or any resolving public artifact is a race-gate strict stop.

## Source status and historical-bound gate

The current independent source check is
[`arXiv:2602.23838v1`](https://arxiv.org/abs/2602.23838), *Products of
factorials which are products of factorials*. Its downloaded PDF has SHA-256

```text
c89fc2ebc9b86d4f85ef14daef187ecd8676a4a37ee78322e02eea948b4b755d
```

and was classified as text-based with eight readable pages, no OCR gaps, and
no encoding warning. The arXiv source archive retrieved during this audit has
SHA-256

```text
6a475a1b63adc5244f1b1a1d1dabd42c9a20f0ab3220c36f9722ddd7a70c4867
```

Its introduction explicitly calls

```text
16! = 14! 5! 2!
```

the Surányi--Hickerson prediction for the largest nontrivial solution. It says
that Nair and Shorey obtain the complete displayed list only **under Baker's
explicit abc conjecture**:

```text
7!3!3!2! = 9!,  7!6! = 10!,  7!5!3! = 10!,
14!5!2! = 16!,  15!(2!)^4 = 16!.
```

The last displayed identity is a useful semantics boundary, not a member of
the formal set `S`: its largest factor is `15`, while the Lean predicate at
`n=16` requires `l.headI < n-1 = 15`. The database gate must reproduce the
integer identity and then reject it from `S`. This prevents the source's
broader equation list from being silently substituted for the stricter Lean
domain.

Thus the source does not turn the selected unconditional declaration into a
theorem shadow. It also does not supply, in the inspected passage, an
unconditional exhaustive numerical cutoff beyond which a new bounded search
could claim priority. The older cited 1976 scan could not be extracted by the
local PDF parser and therefore was not guessed from.

This missing historical cutoff is a mandatory **database-sanity gate**, not
permission to call the first rediscovered row new. Before a freeze, retrieve
and hash the relevant Hickerson, Nair--Shorey, Luca--Saradha--Shorey, Takeda,
and Erdős--Graham records; record every unconditional enumerated `n` range and
every published solution. If the proposed band is already exhausted in public
work, either label it wholly `CATALOGUE_CONTROL` or stop. No row inside an
unresolved historical range may become a novelty claim.

## DEVELOPMENT classification and contamination

The committed `c0` registry classified the module as
`MACHINE_ELIGIBLE_PENDING_CONTAMINATION`, `FINITE_COMBINATORIAL`, and
`UNEXPOSED`, with cluster identity

```text
dd8d0a0872c6dde1ed6c006c0481032fd6f65b6fd1fe84b823807e5fc278a7a9.
```

That label is correct only for the frozen `c0` snapshot: its complete identity
scan found no prior campaign contact. This preflight has now read the exact
statement, source discussion, wall seed, and proposed construction. The target
is therefore exposed in the broader session and must be labelled
**DEVELOPMENT**, never held-out, uncontaminated, or prospective-benchmark
evidence. A successful later frozen construction may still be prospective
within DEVELOPMENT, but it cannot retroactively restore `c0` independence.

## Equality wall and separating coordinate

The source control is exact:

```text
16! = 14! * 5! * 2!.
```

The list `[14,5,2]` is nonincreasing, each entry exceeds one, and
`14 < 16-1`. Hence `(16,[14,5,2]) in S`. The asserted maximum sits exactly at
`n=16`; the first crossing slice is the one-unit move `n=17`.

Flat bigint equality search is the wrong coordinate. For every prime `p`, set

```text
V_p(m) = v_p(m!),
T(n)   = (V_p(n)) over primes p<=n.
```

Then a list is a solution exactly when

```text
T(n) = sum_{a in l} T(a),    2<=a<=n-2,
```

with the `a` values in nonincreasing order. This changes the wall from one
enormous integer equation to a nonnegative vector decomposition. The useful
separating coordinate is the largest prime whose target valuation has not yet
been paid. If that prime is `q`, the next factorial must have index at least
`q`; for `q>n/2`, its target exponent is one, so exactly one selected factorial
may contain `q`. If `n` or `n-1` itself is prime, no allowed factorial can pay
that coordinate and the slice stops immediately.

## Target-free crossing-reachability gate

No target residual for `n>=17` may be computed until a separately committed
freeze passes all of the following without reading a target result:

1. Recompute factorials and prime-valuation vectors independently for
   `0<=m<=16`; compare Legendre's formula with repeated exact division.
2. Reproduce the published controls above, including both order-16 lists
   `[14,5,2]` and `[15,2,2,2,2]`, using valuation sums and independent bigint
   products. Accept the first as a member of `S`; reject the second at the
   strict `headI < n-1` premise despite its valid factorial identity.
3. Generate planted synthetic targets solely by choosing fixed lists first and
   summing their factorial-valuation vectors. The constructor must recover a
   canonical nonincreasing list or certify an equivalent one. These are not
   Erdős 373 target instances.
4. Feed malformed controls to the independent verifier: a wrong exponent, an
   entry `0` or `1`, an increasing pair, an `a=n-1` boundary, a truncated
   vector, and a product differing by one. Every mutation must fail closed.
5. Materialize the complete proposed task schedule, shard ownership, prime
   lists, and estimated state-memory bounds without constructing `T(n)` for
   any scheduled `n>=17`.
6. Pass the source/database, open-PR changed-file, target-blob, declaration,
   and local-race checks immediately before activation.

Failure of any item is `SANITY_GATE_FAILED`. It cannot be repaired after
observing target output without a new sequentially committed preflight and
freeze.

## Proposed fixed search grammar

The first freeze should use exactly the integer band

```text
17 <= n <= 256
```

and exactly sixteen shards, with owner `n mod 16`. This band is proposed here
so it cannot be enlarged after seeing a nearest miss. The source-bound gate may
retire all or part of it as historical control, but may not silently replace
it with a larger band.

For each owned `n`, define the fixed alphabet

```text
A_n = {2,3,...,n-2}
```

and recurse on states `(R,u)`, where `R` is the exact remaining valuation
vector and `u` is the greatest permitted next index. The grammar is:

1. If every coordinate of `R` is zero, emit the current nonincreasing list.
2. Let `q` be the largest prime with `R_q>0`.
3. Consider only `a` with `q<=a<=u`, in descending order, for which
   `T(a)` is coordinatewise at most `R`.
4. Recurse on `(R-T(a),a)`. Memoize the complete canonical serialization of
   `(R,a)`; no lossy hash may determine mathematical equality.
5. Reject immediately when an unpaid coordinate has no admissible `a`, when a
   coordinate overshoots, or when the prime-coordinate lower bound exceeds
   `u`.

The only permitted theorem filters are consequences checked independently:
Legendre valuations, the missing-prime rejection for prime `n` or `n-1`,
coordinatewise domination, and the `q>n/2` unique-payer rule. Solver changes,
meet-in-the-middle variants, added indices, reordered branches, and enlarged
bands require a new committed version before evaluation.

## Caps, exact verification, and durable output

Each shard receives a 48-second construction horizon. It must stop launching
new recursion nodes at 48 seconds, serialize and `fsync` its current prefix by
54 seconds, and run inside an external process-group cap of 60 seconds. A
deadline terminal is `CAP_PREFIX`, never `DOMAIN_EXHAUSTED`. The full band is
exhausted only when all sixteen shards independently report every owned `n`
complete.

Append-only output must be written incrementally after every completed `n`,
candidate-shaped hit, periodic checkpoint, error, and terminal. Each row binds
the campaign commit, source commit/tree/blob/SHA-256, manifest hash, shard,
`n`, deterministic ordinal, previous-row hash, and evaluator version. A final
summary is derived from these rows; it is never the only durable artifact.

A candidate-shaped list must be replayed by a separate implementation that
does not import the discovery code. It must check:

- `17<=n<=256` and every `a` is a natural with `2<=a<=n-2`;
- the list is pairwise nonincreasing and therefore satisfies the literal
  `Pairwise` and `headI` conditions;
- prime factorizations and Legendre valuations are complete;
- coordinate sums equal `T(n)` exactly; and
- an independently computed arbitrary-precision integer product satisfies
  `factorial(n) = product(factorial(a) for a in l)`.

Only after that replay may a separate novelty/status audit begin. A discovery
worker never writes release text and never contacts upstream.

## Strict stops

Stop without target evaluation or promotion if any of the following occurs:

- the upstream commit/tree/path/blob/declaration/category changes;
- an open PR touches the path or any issue, PR, commit, paper, database, local
  artifact, tag, or release already resolves the declaration or contains the
  same candidate;
- the historical-bound audit cannot distinguish controls from potentially new
  territory;
- the conditional explicit-abc classification is mistakenly treated as an
  unconditional theorem or as computational priority;
- the target-free gate fails, a planted witness is missed, or a malformed
  witness passes;
- any target coordinate is evaluated before the frozen manifest and code
  hashes are committed;
- a worker times out, leaves an incomplete memo state, loses its ledger tail,
  or cannot prove complete factorization;
- a result depends on probable primality, floating point, a partial valuation
  vector, a lossy memo key, or unchecked bigint arithmetic;
- the fixed band, alphabet, shard map, branch order, cap, or verifier is
  changed after target output is visible; or
- a candidate lacks independent replay and a repeated live source/status/
  duplicate audit.

## Terminal preflight decision

This target has the required direct finite negation, exact equality wall,
one-unit first crossing, compact certificates, and a structurally justified
sub-54-second valuation arm in a factorial/Diophantine cluster distinct from
the campaign's graph, tuple, residue-cover, and automata lanes.

The decision is **`GO_FOR_FREEZE_AFTER_SOURCE_BOUND_GATE`**, not permission to
run it. This file records zero target evaluations, zero candidates, zero
results, and zero release or dispatch authorization.
