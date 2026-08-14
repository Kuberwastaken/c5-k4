# Bondy longest-cycles frozen DEVELOPMENT contract v2

**State:** superseding v2 guard hash sealed, disabled by default, never dispatched

**Evidence class:** contaminated `DEVELOPMENT`, never held out

**Target:** `Arxiv.«2606.03696».bondy_conjecture`

**Only slice:** `k=4`, source parameter `t=4`, `n=24`

This v2 contract supersedes the prepared v1 seal while preserving its reports
as historical records. It freezes the same small balanced delete/add port-
rewiring arm around the source sharpness graph `S(4,4)`. This seal alone does not authorize execution,
publication, a release, an issue, or a pull request.
The workflow remains disabled by default. A target process can start only when
an explicit dispatch supplies all of: `enable_target=true`, a campaign commit
equal to the checked-out `HEAD`, a clean tree, and a guard whose SHA-256 is
exactly `d061571de2bf737ce447b77ebe0e6c2d995d98ab3061f000d1db25fe161e69dc`.
Only the hash is tracked; the guard preimage is deliberately absent from code,
the manifest, and documentation. `HEAD` is checked at runtime rather than
embedded in its own tracked contents, avoiding a self-referential Git hash.
The immutable v2 content registry independently binds every executable and
contract file. Before any target row, the runner also requires the full v2
live-gate schema, the exact 16-check PASS set, equal bracket snapshots, exact
identity/file bindings, and zero open-PR target-path matches; a minimal or
forged `PASS` object is insufficient. Exact nonzero counts, key sets, PR-number
order, sorted changed paths, per-PR path digests, and the complete checks,
bracket, file-binding, and full-record digests are recomputed against the
sealed compact v2 attestation before target evaluation.
Workflow dispatch strings are mapped through step environment variables and
expanded only as double-quoted arguments; no `${{ inputs.* }}` expression is
interpolated into shell source, so quotes and newlines cannot create commands.

## Immutable source and formal shape

The upstream lock is
`google-deepmind/formal-conjectures@b5acb0ff13e38084105b7fe020ba0d59c1925bc5`,
tree `4f6c9bd17fdfdc264f54b26862ce768743da5d63`, file
`FormalConjectures/Arxiv/2606.03696/BondyLongestCycles.lean`, blob
`c4c5cb1983936860d5a4a7208b3f04bd201290d4`, raw SHA-256
`562fbbb0ec47041a61017bb85ec0c7e9aa6fc98cf132be3022268a7dc60e9004`.
The primary source is arXiv:2606.03696v1, PDF SHA-256
`56213cd6384cc2111864d67150c41e1426608c59b1b009c6752acab9be3487fb`.

The exact declaration is `answer(sorry) ↔ RHS`. The repository default
`google.answer = always_true` makes the proof target definitionally
`True ↔ RHS`, not a bare `RHS`. A candidate disproves `RHS` and answers the
intended question `False`; it does not literally falsify an opaque wrapper.
A later formal correction must replace the placeholder with `answer(False)`
and discharge the outer equivalence (for example via `true_iff`/`false_iff`
after selecting the answer). No result may blur this answer-wrapper caveat.

The live gate rechecks current `main`, commit/tree/blob/content hashes, exact
open status, all open-PR changed-file lists, exact-name/path/paper-ID issue and
PR searches, standalone repositories, local project history, and the paper
hash. Any drift is `GATE_FAIL`; there is no repin inside this trial.

Authenticated REST collection uses bounded 24-worker pools. The gate first
captures a complete canonical bracket snapshot of main, exact searches,
standalone repositories, and all open-PR identities (number, title, draft,
updated time, and head/base SHA/ref/repository). It then fetches each frozen
identity's fully paginated changed-file list exactly once, sorts and digest-
binds the list to that identity, and finally repeats the complete identity
snapshot. The before/after snapshots and open-PR number sets must be equal.
Thus head/base/file-affecting updates and new/closed PRs fail closed without a
second file scan. Any worker or pagination error also fails closed; scheduling
cannot affect canonical order or hashes.
Live records use schema
`bondy_source_status_duplicate_gate_bracketed_single_scan_v2` and explicitly
require the file-binding identities to equal the complete before identity set.

## Source control and theorem subtraction

For

```text
S(k,t) = K_k join ((k+1) disjoint K_t),
n = k + (k+1)t,
delta = k+t-1,
```

the scaled premise residual is

```text
(k+1)delta - n - k(k-1) = -1.
```

The frozen source control proves exactly `(k,t,n,delta)=(4,4,24,7)`, threshold
`ceil(36/5)=8`, and residual `-1`. It is a control, never a candidate.

The source proves `k<=3`; Ma--Ning--Zhao prove `n>=5k^2+7k`; Zhang proves the
claw-free domain. Every retained row therefore has `k=4`, `n=24<108`, exact
minimum degree eight, and a serialized induced `K_1,3`. A claw-free row is
`KNOWN_PROOF_DOMAIN` before target evaluation.

Pure edge addition is a strict stop. One cross edge between two source
peripheral cliques joins two clique Hamilton paths, leaving a spanning cover
by at most four paths and hence a Hamilton cycle in the join. The frozen arm
must delete ten declared internal matching edges and add a declared loopless
cross-block 2-factor. No-op, monotone, matching-only, and any cross factor
with at most four components are rejected before target evaluation.

## Frozen balanced grammar

Peripheral vertices are labelled `4*i+j`, with block `i in Z/5Z` and port
`j in {0,1,2,3}`. Each block deletes exactly one of the three ordered perfect
matchings

```text
01|23, 02|13, 03|12.
```

The added 2-factor comes from the complete four-entry ordered quotient-cycle
catalogue and three ordered global port permutations embedded verbatim in
`manifest.json` and `prospective_bondy_construct.py`. Occurrence number in a
quotient cycle selects the port before permutation. Every catalogue row has
five four-cycles, covers every port once, has no within-block edge, and gives
every port cross-degree two. Thus every retained `H` is exactly 4-regular and
`K_4 join H` has minimum degree eight.

The immutable row order is lexicographic in the five matching choices, then
quotient index, then port-permutation index. The prefix contains exactly 96
parameter rows. Labelled edge digests reject repeats first; frozen
Weisfeiler--Lehman buckets followed by exact NetworkX isomorphism reject
ordinary-isomorphic repeats. No quotient, permutation, matching, orientation,
row, or row-limit extension is permitted after any target residual is seen.

Target-free gates replay the complete labelled edge list and role map, all
declared edits, order, theorem range, every vertex degree, threshold equality,
all 2,325 deletion sets of size below four with a surviving universal hub,
an explicit induced claw, neutral-family subtraction, source-seed rejection,
and both duplicate layers. Constructor tests may not import or call proposed
candidate circumference, path-cover, or `q_4` evaluation.

## Exact target and certificate

Define

```text
q_4(H) = max |U| such that H[U] is coverable by at most four
         pairwise vertex-disjoint nonempty paths.
```

The discovery encoding is a deterministic endpoint subset DP. With values
capped at five, `p[S]` is the minimum path-cover count of `H[S]` and `d[S,v]`
is the same minimum with `v` an endpoint of a distinguished path:

```text
p[empty]=0,
d[S,v]=min(p[S-v]+1, min_{u in (S-v) cap N(v)} d[S-v,u]),
p[S]=min_{v in S} d[S,v].
```

This is exactly the linear-forest encoding (maximum degree two, acyclic,
`|V(F)|-|E(F)|<=4`) without an external solver. The discovery code records
SHA-256 digests of its one-byte `p` table and endpoint table. A separately
written C++ implementation regenerates the recurrence and the complete
1,048,576-byte `p` table; candidate acceptance requires identical table
digests. A candidate requires all of:

1. a simple four-vertex path `Q` in the induced off-cycle graph `H[Q]`
   (chords among its support are allowed by the formal target);
2. an explicit at-most-four-path cover of `H-Q`, proving `q_4(H)>=16`;
3. an explicit stitched cycle using every hub and exactly `H-Q`;
4. an independent exact proof `q_4(H)<=16`, equivalently
   `pc(H-X)>4` for every one of the 1,351 sets `X` with `|X|<4`; and
5. direct replay that the off-cycle path has four support vertices, hence
   `P.support.length+1=5>4`.

Every candidate serializes the complete canonical edge lists of both `H` and
`G=K_4 join H`; the verifier reconstructs the join independently and requires
byte-equivalent ordered `edges_g`. It also binds the Python and NetworkX
versions, named Python/C++ DP algorithm versions, source and executable
digests, exact 48/54/60 caps, discovery/replay timings, exit status, and the
independent verifier's compiler/flags/build digest. The runtime provenance is
frozen exactly to CPython `3.11.9`, NetworkX `3.3`, discovery algorithm
`python_endpoint_path_cover_dp_v1`, and replay algorithm
`cpp_endpoint_path_cover_dp_v1`; the verifier rejects any mismatch.

If any deletion set `X` with `|X|<4` instead has `pc(H-X)<=4`, the row is an
ordinary exact noncandidate, `Q4_UPPER_BOUND_REJECTED`. Its ledger row must
contain the canonical removed set and masks plus an explicit at-most-four-path
cover of every vertex of `H-X`; the terminal verifier replays that cover.
An independent-replay deadline alone may produce `CAP_PREFIX`. Any nonzero
logical rejection, malformed output, table disagreement, or internal replay
failure is `GATE_FAIL`, never a timeout prefix.

For every row with global optimum 16, the discovery path enumerates all
`C(20,4)=4,845` four-sets in lexicographic order, finds the least simple
four-vertex path ordering when one exists, and exactly tests a spanning
at-most-four-path cover of its complement. `DOMAIN_EXHAUSTED` is unavailable
until this complete frozen `Q` catalogue has finished for every such row.

The independent C++ verifier enumerates those deletion sets with its own
endpoint-table implementation. It imports no discovery helper.
Together the witnessed lower and independently replayed upper bounds prove
`q_4(H)=16`, so every cycle in `K_4 join H` has length at most `4+16=20`
and the stitched cycle is globally longest. Merely proving non-Hamiltonicity,
`pc(H)>4`, or one nonspanning cycle is explicitly insufficient.

## Caps, atomic evidence, and terminals

The target process has an exact 48-second search horizon, 54-second internal
finalization boundary, and external process-group command
`timeout --signal=TERM --kill-after=6s 60s`. Independent candidate or terminal
verification is separately capped at 60 seconds. The discovery DP is entirely
in-process and checks its monotonic deadline while filling the frozen table;
the independent C++ replay is a separately capped process. An incomplete DP,
deadline, or nonzero replay exit fails closed.

Every constructor/evaluation row is canonical JSONL, fsynced immediately, and
bound into a SHA-256 chain. Candidate and terminal files use fsync plus atomic
rename. A durable candidate seals the ledger; no later append is allowed.

Target-free calibration on the declared VPS completed all 96 constructor rows
in 2.36 seconds. A synthetic `C20` endpoint-DP fixture, explicitly not a
proposed candidate, completed one full table in 6.889 seconds and produced
`pc`-table SHA-256
`fbb482ddcf2737fcb30159a44c7b9faec8e06911e1ae4a74dfe8f6bcc345b58f`.
This predicts that the immutable target run may honestly end `CAP_PREFIX`
after only a small number of applicable rows. It does not authorize target
evaluation or reduce the exact 48/54/60 caps.

The sole terminals are:

- `CANDIDATE_FOUND` (only after the full replayable compact certificate);
- `DOMAIN_EXHAUSTED` (all 96 frozen rows completed);
- `CAP_PREFIX` (an exact prefix finalized, never a bounded zero);
- `NO_APPLICABLE_CANDIDATES`;
- `NO_TARGET_RAISING_CANDIDATES`; and
- `GATE_FAIL`.

No timeout, computation error, missing artifact, hash drift, replay failure, or
process-audit ambiguity can become a hold. No terminal proves the universal
conjecture. Any later change in family, `k`, `t`, order, catalogue, cap, algorithm,
or certificate semantics is a new contract.
