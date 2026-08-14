# OEIS A108569 odd-core DEVELOPMENT freeze

**State:** frozen harness, not evaluated, not dispatched

**Target:** `OeisA108569.conjecture` at
`google-deepmind/formal-conjectures@8d3eaa0412f65db0c983b006dd3a44075c0d7965`

This is a development-set trial under `METHOD.md`. It is not held out. The
complete source gate, profile catalogues, ownership, ordering, shards, evidence
transaction, verifier, and 48/54/60-second caps are frozen before any target
coordinate is constructed or any equality is evaluated.

The local pre-freeze history boundary is
`c5-k4@ccc510285d57dc51cc32ff9074c476fd89dc113a`; the eventual freeze commit
must be its direct non-merge child. The boundary includes the completed
A067720 result and contains no A108569 target evaluation or claim.

## Literal certificate and enumeration bridge

Let `A(k) := 0 < k ∧ phi(k)=phi(k+phi(k))` and `a(n):=n.nth A`. A
mathematical crossing is an odd `k>1` with `A(k)`. A literal theorem
counterexample additionally binds `i := Nat.count A k`: `Nat.nth_count`
gives `a(i)=k`, while `A(1)`, `1<k`, and `Nat.count_strict_mono` give
`i>0`. A certificate
therefore contains complete ordered factorizations of `k` and
`m=k+phi(k)`, exact totient products, equality, oddness, and that symbolic
count/nth bridge. Equality without the bridge is
`SEMANTIC_CANDIDATE_ONLY`, never a promotable result.

The target-free generic bridge in `lean/Oeis108569EnumerationBridge.lean`
(SHA-256 `f04975ea522a36681a2a467ec0e8c0d65d41689f8b96699654b41aa07ba0a2bd`)
was compiled with warnings as errors. It proves the count/nth/parity reduction
for any decidable predicate without evaluating a target coordinate. A future
candidate still requires a concrete no-`sorry` instantiation discharging
`A 1`, `A k`, `1<k`, and oddness.
The workflow independently checks out Mathlib at
`a3a10db0e9d66acbebf76c5e6a135066525ac900`, installs its exact Lean
toolchain, retrieves the two pinned import caches with retries, recompiles
the frozen bridge with `-DwarningAsError=true`, prints both theorem axiom
sets, and rejects `sorryAx` under explicit 240/180-second caps.

## Source, status, race, duplicate, and database gate

The gate binds the pinned Lean blob (SHA-256
`0e62b2d15f41a2b2dbcc568a63abd3644e8429fa7befdec7cc2d0e96cc6244f8`),
literal `@[category research open]` and `sorry`, OEIS source revision
`#14 Sep 08 2022 08:45:19`, offset `1,2`, and the exact 384-row b-file
through `(384,997694)`. It completely factors both endpoints for every row,
recomputes both totients, replays the recorded even and divisor lift
identities, and independently checks frozen Sophie-Germain controls
`p=5,11,23,29,41` producing `k=110,506,2162,3422,6806`. Those rows are
controls and exclusions.

The final source refresh moved upstream main to `8d3eaa0412...` (tree
`4e397bf82a...`) via two unrelated commits adding
`GreensOpenProblems/53.lean` and `64.lean`;
the A108569 blob and status are byte-identical to the preflight snapshot.

A fresh authenticated audit must match live upstream head/tree, exact search
queries and completeness, exact merged ingestion PR #4450 identity, every page
of open-PR changed files including `previous_filename`, exact target content
for any touch, and every page of local releases. Any new target path touch,
claim, incomplete/truncated response, source/hash/status drift, or #4450
identity drift is `GATE_FAIL` before construction. The freeze expects exactly
280 open PRs at the final 2026-08-14T18:31:12Z replay and exact full-file pagination receipts for
`3422,4004,4198,4356,4417,4428,4496,4576,4688`; any count, membership, or page-size
drift stops the lane.

## Frozen profile construction

Use the first 128 odd primes (ending 727), `k<=2,000,000,000`, and
`m<4,000,000,000`. Canonical order is support cardinality, increasing
one-based prime ranks, then the listed exponent tuple.

- support one uses exponents 1..12;
- support two uses `(1,1),(1,2),(2,1),(2,2),(1,3),(3,1)`;
- support three uses `(1,1,1),(2,1,1),(1,2,1),(1,1,2)`;
- the endpoint catalogue uses the identical supports and exponents.

`ODD_CORE_PROFILES` owns support one and two (34,066 profiles).
`ODD_COLLISION_WALL` owns support three (745,665 profiles). Each target arm
has 24 shards by canonical arm ordinal modulo 24.
`CATALOGUE_LIFT_CONTROL` owns exactly the 384 source controls and is not a
target arm.

For support sets S and T, `rho(x)=phi(x)/x`. If reduced
`rho(k)=A/B`, equality requires `rho(m)=A/(A+B)`, equivalently
`B*prod(T^f)=(A+B)*prod(S^e)`. The wall arm indexes endpoint profiles by
reduced rho, then enforces the exact translation `m=k+phi(k)`; a ratio
collision without that assembly is diagnostic only. Both target arms require
the exact reduced-rho identity, the exponent-lattice identity, and the
endpoint-catalogue translation before residual evaluation. No arbitrary
factorization and no flat integer scan are permitted.

The target-free pre-freeze benchmark constructed and hashed only these profile
catalogues. It did not compute phi, construct `m`, match translations or
ratios, evaluate equality, or access a target coordinate. It pinned 482,
33,584, and 745,665 core profiles; 880,891 unique endpoint entries; stream
hashes in `manifest.json`; 13.56 seconds wall time; and 313,876 KiB peak RSS,
inside the 48-second cap.

## Evidence and caps

Workers have a 48-second in-process horizon, stop launching work and finalize
under a 54-second external cap, and use a separately implemented verifier under
60 seconds. Each ledger is create-new, canonical JSONL, hash chained and
fsynced. A checkpoint occurs after every completed actual source/endpoint
support pair (including a diagnostic pair that fails translation or lattice)
and no later than 16 completed exponent coordinates since the previous
checkpoint, never midway through a coordinate. Candidate
write is an fsync-and-rename state commit; no ledger append follows it. The
terminal binds the exact prefix, counts, chain tail, ledger byte hash, gate,
arm, shard, and campaign commit. A deadline is `CAP_PREFIX`, never
`DOMAIN_EXHAUSTED`; any missing/malformed terminal remains incomplete.

The independent verifier reconstructs catalogues without importing discovery
code, replays ownership and the exact prefix, validates the source controls,
and recomputes candidate factors, primality, totients, translation, equality,
oddness, source exclusion, and the exact symbolic count/nth bridge schema plus
its numeric preconditions. Python does not prove the Lean bridge: public
eligibility additionally requires a compiled, no-`sorry` Lean lemma.

This freeze authorizes no target evaluation, dispatch, issue, pull request,
release, README edit, tag, or publication.
