# OEIS A109908/A109909 finite-prefix-cover DEVELOPMENT freeze

**State:** target unevaluated; exact committed-SHA unlock required

**Targets:** `OeisA109908.conjecture` and `OeisA109909.conjecture` at
`google-deepmind/formal-conjectures@7eb70784eab1a3c6f4c3d99f8920b970cd7f68c4`.
They form one correlated cluster: both are positive exactly when some value
`f_n(k)=k(n-k)-1` is prime. Symmetry `f_n(k)=f_n(n-k)` reduces both literal
negations to the representatives `1 <= k <= floor(n/2)`.

This is a development-set trial under `METHOD.md`, not held out. No target
profile or candidate `n` was evaluated while preparing this freeze. Execution
is disabled until the workflow checks out an exact 40-hex campaign commit and
the script verifies that `HEAD` is that commit.

## Literal certificate

A shared disproof is one `n>3` with selected moduli, one residue for `n` per
modulus, the paired root classes for `k`, and an exact digest proving their
union covers every `1 <= k <= floor(n/2)`. A residue-profile hit, a
probable-prime test, a covered construction prefix, or an incomplete interval
replay is not a candidate. The independent verifier reconstructs both formal
ranges, checks the symmetry reduction, and recomputes the interval digest
without importing discovery code. This compact certificate replaces an
unnecessary half-billion-row divisor table.

The `Nat`-safe range bridge is explicit. If `1<=k<n`, put
`j=min(k,n-k)`. Then `1<=j<=n/2`; when `k>n/2`, natural subtraction gives
`n-(n-k)=k`, and commutativity yields `f_n(j)=f_n(k)`. Conversely every half
range representative is already in `1<=k<n`. Thus the two finite sets of
distinct prime values are equal, including odd `n` and the `Nat` subtraction
boundary.

## Source and database-sanity gate

The manifest pins both Lean blobs, their `research open` declarations, the
current formal-conjectures and OEIS repository heads/trees, OEIS source files,
and complete b-files (10,000 rows for A109908 and 93 for A109909). Before
construction, the gate recomputes each b-file row from the
literal quadratic definition with an exact sieve, reproduces `n=1..20` by a
separate trial-division implementation, checks the zero boundary and positive
controls, and verifies that both half/full ranges have the same distinct prime
set. The live workflow also requires the pinned upstream head/tree,
byte-identical target files, and a fresh issue/PR/path race check. Any drift,
new target touch, or mismatch fails before search.

OEIS links Niu and Zhang's 2024 *On Two Conjectures of A. Murthy*. Its claimed
proof was audited and rejected: the `mu=0` stationary branch is feasible with
`f=-l/4`, so it cannot be the asserted global maximum and the claimed positive
minimum does not follow. The attestation records
`PUBLIC_PROOF_CLAIM_AUDITED_INVALID`; current OEIS and formal status remains
conjecture / `research open`.

Every `n<=10^9` is historical calibration and is excluded from novelty.

## Frozen finite-prefix construction

For `q>1` with `gcd(k,q)=1`,

```text
q | k(n-k)-1  <->  n = k + k^(-1) (mod q).
```

For each prime `q`, one residue for `n` is selected and its root classes are
paired by inversion. Every recorded divisor also satisfies `1<q<f_n(k)`;
the frozen range has `q<n-2`, which suffices because `f_n(k)>=n-2` on the
half range.

The construction uses exactly the 14 primes `2..43` listed in `manifest.json`.
At each prime it chooses one residue for `n`; this choice covers exactly the
prefix positions whose `k+k^-1` residue agrees. For `q=2`, the sole unit root
is `k=1` and its prescribed residue is `n=0 mod 2`, so this single frozen
trial deliberately selects the tighter even-`n` arm and certifies every odd
representative immediately. Odd `n` is outside this trial rather than being
added later as a second adaptive arm. A deterministic beam of width 256 is
ordered by depth, descending least-uncovered position, descending covered
count, CRT residue, and residue tuple. Frozen profiles start at depth 10, the
first depth whose selected-profile modulus exceeds half of every `n` in the
candidate interval. Their CRT representatives are enumerated only in
`1,000,000,001..1,500,000,000`, never by scanning consecutive `n`, and are
owned by canonical profile ordinal modulo 16.

The complete 14-prime universe has lcm `Q=13,082,761,331,670,030`. More
importantly, every emitted profile is checked using its own selected-product
modulus: since `k=Q_profile` is uncovered by every selected modulus (each gives
`f_n(Q_profile)=-1 mod q`), a trial is eligible only when
`Q_profile>n/2`. Starting at depth 10 makes the stronger frozen condition
`Q_profile>candidate_n_maximum/2` hold before any representative is emitted.
The 262,144-position mask is a construction score, not a proof boundary.
After the committed-SHA unlock, a trial is checked from `k=1` onward under the
48-second internal deadline. The first uncovered representative is a wall
diagnostic. Only exact segmented coverage through `floor(n/2)` may atomically
publish a compact `candidate.json` containing the moduli, residues,
inverse-paired root classes, interval metadata, and coverage digest. The first
uncovered `k` is stored with `f_n(k)` and an exact complete factorization.
Thus `PREFIX_OPEN`, `CAP_PREFIX`, an unfactored escape, and an incomplete
interval digest are never candidates.

Finite independent prime moduli cannot cover every integer residue: this lane
does not claim an infinite covering system and does not repeat the invalid
periodic-cover direction rejected in the A231201 work.

## Evidence, caps, and stop rules

Construction stops internally at 48 seconds, under a 54-second process cap;
independent replay has a 60-second cap. Canonical JSONL is hash-chained,
fsynced after every 16 completed profile trials, and closed by a terminal that
binds the campaign commit, shard, exact visited prefix, counts, chain tail,
ledger hash, and candidate/coverage hashes. A deadline is `CAP_PREFIX`,
not exhaustion. Missing or malformed terminal evidence fails closed.

The profile universe, divisor universe, interval, beam width, shards, and caps
are immutable for this trial. No post-result modulus, interval, flat scan, or
generic factor-search extension is permitted. This contract authorizes no
dispatch, README edit, release, tag, issue, pull request, or public claim.
