# Method v1.3 prospective benchmark (proposed)

**Status:** successor scaffold in PRE_P0 development; no v1.3 P0, S0,
production registry, C0, C1, entropy, selection, or target-semantic inspection
has occurred
**Purpose:** rerun the original twelve-cluster DeepMind comparison with the
identical v1.2 scientific design after correcting one fail-closed
`git_user_delta` corpus-binding validator defect

Method v1.3 is a new prospective experiment. It does not reopen, extend, or
reinterpret Method v1.2. The v1.2 terminal result remains
`PROTOCOL_INVALID`.

## Sole change from v1.2

V1.3 inherits v1.2's sampling frame, five fixed strata, 3/3/2/2/2 quotas,
three arms, budgets, priors, transformation library, scoring, stopping rules,
source boundary, and non-circular publication protocol without scientific
change. Its only correction is in the contamination replay validator:
ordinary Git histories bind `corpus_sha256` to
`git_object_metadata_sha256`, while normalized `git_user_delta` sources bind
it to `user_commit_set_sha256`; both bindings also include the exact worktree
overlay inventory digest. Missing, mismatched, or unsupported binding inputs
fail closed.

No eligibility rule, target population, classifier, quota, search budget,
forecast, transformation, scoring threshold, or retry policy changes in v1.3.
Any further change requires a later benchmark version.

The machine-readable inheritance statement is frozen separately in
[`results/benchmark/v1.3-protocol/inheritance-manifest.json`](results/benchmark/v1.3-protocol/inheritance-manifest.json)
and is a required P0 component.

## Invariants carried forward unchanged

The sampling unit remains a question cluster. Sibling statements, equivalent
encodings, and logical negations are one unit. Identity ambiguity still means
exclusion.

An actual v1.3 selection contains exactly twelve uncontaminated clusters from
one pinned `google-deepmind/formal-conjectures` commit and tree, with these
fixed quotas:

- three `GRAPH_SCALAR_INEQUALITY` clusters;
- three `GRAPH_STRUCTURAL_PROPERTY` clusters;
- two `FINITE_ALGEBRA_EQUATIONAL` clusters;
- two `AUTOMATA_GAME_PROCESS` clusters;
- two `FINITE_COMBINATORIAL` clusters.

There is no cross-stratum backfill, quota relaxation, replacement after C0,
or manual substitution. A selected cluster remains in the denominator after
source-status, certificate-shape, prior-art, formalization, or identity stops.

Every runnable cluster receives the same three isolated discovery arms:
`CATALOGUE`, `GENERIC`, and `WALL_NAVIGATION`. Each arm retains eight process
trees, a 60-second wall cap per process tree, and at most 480 CPU-seconds.
Shared analysis remains at most 600 CPU-seconds and independent verification
remains two additional 60-second process trees. Seeds, grids, executable
contracts, the one wall transformation, and `no_adaptation: true` are frozen
before any discovery arm starts. No result is shared between arms before all
three terminate.

The outcome space, exact probability vectors, terminal precedence, theorem
yield, support thresholds, hard process isolation, append-only hash-chained
ledgers, and the rule against stopping after a crossing remain those of v1.2
unless a v1.3 freeze artifact explicitly restates an equivalent rule. New
solvers, target families, bounds, or backup transformations belong to a later
benchmark version.

## Two meanings of contact

V1.2 distinguishes two observably different kinds of identity contact. V1.3
preserves both, but only one is semantic
contamination.

`MACHINE_REGISTRY_CONTACT` means that a content-addressed, allowlisted program
handled registry material without presenting target semantics to a human or a
language model. Permitted operations are limited to:

- reading a pinned Git tree;
- locating open-category markers, paths, declaration kinds and names;
- computing content and statement-header digests;
- computing allowlisted syntax flags and fixed strata;
- conservative machine grouping, alias generation, provenance matching,
  eligibility intersection, quota counts, and later random selection; and
- emitting schema-bounded rows, aggregate counts, hashes, and replay evidence
  with no statement text, residual, mathematical interpretation, candidate,
  proof route, or target-specific result.

A file path, declaration name, identity-only row, aggregate count, registry
clone, generated inventory, CI log, or tool result is therefore not by itself
proof that a target was considered semantically. Exact identities in such an
output still record machine contact and may be non-excluding only when its
provenance record proves that it was
produced by an allowlisted executable digest under a frozen invocation
contract and that its output validates against the bounded registry-contact
schema. There are no ad hoc hash exemptions. A mixed unit, an unverifiable
unit, or a unit whose producer or schema is not frozen is `UNKNOWN`, which
fails closed.

`SEMANTIC_EXPOSURE` means that a human or language model received or discussed
the statement, its mathematical meaning, residual, family, status, proof or
disproof route, theorem signal, transformation, or candidate. It also includes
target-specific compute and any machine output that contains such information.
Supplying a statement to a model is exposure even if the model returns no
answer. Hand-authored research prose, code, comments, commit messages, and
natural-language session turns are semantic sources. A semantic source cannot
be relabeled as registry contact merely because it was stored or copied by a
program.

Each scanned source unit receives exactly one provenance class:
`SEMANTIC_SOURCE`, `MACHINE_REGISTRY_CONTACT`, or `UNKNOWN`. Identity evidence
in a semantic or unknown unit excludes the whole conservative question
cluster. Identity evidence confined to proved registry-contact units is
recorded in the audit inventory but does not exclude it. Any direct semantic
evidence, incomplete source, unresolved cross-module sibling relation, or
provenance ambiguity excludes it. Absence of an alias hit alone never cures a
gap in source discovery.

The registry-contact exception changes the evidentiary classification of
machine provenance; it does not excuse prior semantic work. In particular, a
cluster semantically exposed before v1.3 remains excluded.

## Pre-C0 quota-feasibility gate

The five-strata classifier, grouping rule, provenance policy, source-discovery
boundary, exact upstream-ref rule, quotas, schemas, linter, selector, budgets,
forecasts, transformation library, scoring rule, and stopping rule must first
be committed and publicly available in a protocol artifact commit `P0A`.
Because `P0A` cannot contain its own object ID, a protocol attestation commit
`P0T` records the already-public `P0A` ID and publication time without changing
the protocol artifacts. `P0A` contains no final eligible-pool rows, selected
targets, target ranking, statement text, or semantic target analysis. It may
retain explicitly marked `PRE_P0_NOT_FREEZE` syntax-only prototype registry
artifacts from protocol development; those artifacts have no authority in the
formal build, eligibility replay, or selection. `P0T` is fixed
before the one allowed v1.3 registry build and deterministically fixes the one
upstream commit that build may resolve.

After `P0T`, the operator acquires immutable snapshots of all semantic sources
through a recorded cutoff `S0`. No human or language model may inspect v1.3
candidate statements between `S0` and C1. Registry work after `S0` must occur
only through the frozen machine-contact lane. Any natural-language research
turn after `S0` and before C1 is added to a supplemental semantic snapshot
before C0; it is not silently ignored. Any target-semantic access after C0 and
before C1 is a protocol violation because the frozen pool can no longer be
repaired.

### Semantics-blind source discovery and S0 acquisition

The executable source-boundary builder is
[`scripts/build_benchmark_v13_source_snapshot.py`](scripts/build_benchmark_v13_source_snapshot.py).
Its path-purpose policy is
[`results/benchmark/v1.3-protocol/source-path-purpose-policy.json`](results/benchmark/v1.3-protocol/source-path-purpose-policy.json).
The policy becomes authoritative only when its exact bytes are committed in `P0A`; changing
even JSON whitespace changes its digest. Repository inclusion is decided only
from a path relative to the frozen discovery root. An unclassified repository,
overlapping allow/deny rules, an unsupported or unmerged worktree object, or a
required source that is absent makes the source configuration incomplete.

Discovery does not decode or emit Git blobs, commit messages, transcript turns,
release bodies, or candidate statements. Except for hashing current-tree
overlay bytes, it records only exact local Git tips, remotes, HEAD, and a
SHA-256 of sorted reachable Git object IDs, types, and sizes. This pins history
without copying it. Release metadata is supplied as a separately
preserved JSON export and pinned by byte count and SHA-256. The exact
`ai-chats` commit is pinned separately. Each required local Codex and Claude
JSONL tree must be an exact path-and-Git-object subset of its configured
subtree at that commit. The local seven-day retention window may omit older
archived sessions, but a retained path with different bytes fails closed. The
complete pinned ai-chats subtree is scanned later. Hashing those bytes is
permitted machine acquisition; the tool neither parses nor emits their turns.

An included research repository need not have a clean worktree. Discovery
content-addresses its complete delta from HEAD: staged index values, unstaged
tracked values, deletions, and untracked nonignored files. Every overlay row
records a normalized relative path, index or worktree layer, presence state,
mode, object type, byte count, SHA-256, and an immutable Git-blob or replayable
filesystem selector. A path with different staged and unstaged values has two
rows. File contents are hashed but never emitted. The overlay digest is bound
with the reachable-history object digest into the source corpus digest. S0 and
the contamination builder both reconstruct every row and fail on any path,
mode, layer, byte, or hash drift before scanning those exact units.

Without a P0 attestation, `discover` can emit only a
`c5k4-semantic-sources-config-1.3-prototype` object with
`prototype_only: true`. `acquire` categorically refuses that object. Production
discovery validates exact `P0A`/`P0T` ancestry, the policy hash, the P0-frozen
digest of the complete discovery invocation (projects root, session roots and
subtrees, ai-chats repository, and release exports), and that `P0T`
is advertised by the preregistered public remote using read-only `git
ls-remote`. The P0T artifact does not self-name its commit or remote: those are
explicit acquisition arguments. The tool verifies its exact committed bytes,
sole-parent P0A ancestry, one-path change rule, then reads the authenticated
committed P0A to verify both component hashes. S0 then replays every tip,
history and current-tree corpus hash,
session-mirror comparison, and release-export hash. It records the supplied
whole-second UTC acquisition time on every source and emits an internally
content-addressed manifest. Source repositories and histories are never
modified or copied.

After public `P0T`, the operator must first sync every local Codex and Claude
session into `ai-chats`, commit and publish that repository, and preserve the
frozen GitHub release-metadata JSON export. Then `discover` is run with every
required session mirror and release snapshot plus the P0 attestation, followed
immediately by `acquire` with a recorded UTC timestamp. The config, exports,
and S0 manifest are preserved before the registry build. No production
discovery or S0 acquisition was run while preparing this prototype.

The deterministic builder then makes the open inventory, conservative cluster
pool, provenance inventory, and contamination-applied eligible pool for one
exact upstream commit and tree determined by the rule preregistered at `P0T`.
It emits a quota-
feasibility certificate containing:

- the `P0A`/`P0T`, upstream commit/tree, source-snapshot, classifier, provenance-
  policy, contamination-inventory, and eligible-pool digests;
- the fixed quota and exact eligible count for every stratum;
- the deficit `max(0, quota - eligible_count)` for every stratum;
- `entropy_used: false`, an empty selected-cluster list, and no ordering or
  ranking derived from randomness; and
- a canonical certificate digest reproducible from the frozen pool.

The gate passes if and only if every eligible count meets its frozen quota.
The linter must recompute the counts from every pool row, recompute the
eligibility intersection, and agree exactly with the certificate. Aggregate
counts written by the builder are not sufficient evidence.

If the gate fails, v1.3 terminates immediately as
`NO_ELIGIBLE_BENCHMARK_PRE_C0`. A failure artifact commit `F0A` publishes the
pool and failure certificate with a null self-reference; a failure attestation
commit `F0T` records the already-public `F0A` object ID and publication time
without changing those artifacts. It has no C0, C1, selected clusters,
randomness round or value, evaluation timestamp, contracts, or ledgers, and
cannot be scored as a twelve-cluster benchmark. The selector and drand fetcher
must refuse this phase. There is no wait for public randomness and no attempt
to repair a deficit. Trying another upstream pin, classifier, source boundary,
or provenance rule requires a later protocol version.

Only a passing certificate permits C0. Thus v1.3 can start the decisive
experiment only when the frozen population really contains the required
uncontaminated 3/3/2/2/2 pool; the gate prevents another avoidable wait but
does not manufacture eligibility.

## C0 and future public randomness

On a passing gate, the C0 artifact commit contains the exact upstream pin,
inventories, applied pool, passing feasibility certificate, all protocol
artifacts and priors, and one future League of Entropy drand round. The round
must close after C0 is publicly available. Its value and all C1 fields are
null at C0.

Because a commit cannot contain its own object ID, C0 uses the same two-commit
attestation pattern as v1.2:

1. publish the immutable artifact commit `C0A`, with a null self-reference;
2. publish `C0T`, which records the already-public `C0A` object ID and its
   publication time without changing any content-addressed C0 artifact; and
3. require the drand round to close after the recorded publication time.

`C0T` is an attestation to `C0A`, not a second opportunity to change the pool,
round, eligibility, quotas, priors, library, or rules. Git ancestry and file
digests must prove that only the allowed chronology fields changed.

At C1, two frozen relays must agree on the exact round and the existing BLS and
randomness-hash checks must pass. Selection uses the v1.3 domain-separated
unbiased Fisher--Yates algorithm over the complete eligible ranking in each
stratum. The first fixed quota in each shuffled stratum is selected. The
selector replays the passing feasibility certificate before consuming entropy
and rejects any pool, inventory, classifier, provenance policy, or upstream
digest mismatch. A C1 artifact commit `C1A` freezes the relay and selection
evidence without naming itself; a C1 attestation commit `C1T` records the
already-public `C1A` ID and may populate the phase and chronology fields, but
may not change the selection or any C0 artifact.

The selected manifest has exactly twelve clusters. There is no post-C0
shortage branch because C0 itself is forbidden unless the exact frozen pool is
quota-feasible. A digest mismatch is `PROTOCOL_INVALID`, never an invitation
to rebuild or backfill.

## Post-C1 evaluation and full denominator

The selection forecast for each of the twelve clusters is frozen in `C1A`
using only the permitted registry metadata and frozen development priors.
Manual source recovery and semantic review begin only after `C1T`. Each
cluster then receives a resolution card, source/status audit, and
database/calibration ledger. The intervention forecast and, where runnable,
all three arm contracts are frozen before evaluation. Phase-0 facts may stop a
cluster, but may not remove or replace it.

All headline aggregates report `selected_n = 12`. Forecast Brier scores,
terminal outcomes, theorem yield, crossing classes, timeout and protocol-
invalid rates use all twelve selected clusters. For an arm-ineligible Phase-0
stop, all three arms receive a preregistered structural-zero gain and the two
wall-versus-baseline comparisons are ties; no CPU-normalized value is imputed.
Consequently mean arm gain and paired wins/losses/ties also have denominator
twelve rather than a favorable complete-case subset. Reports additionally
show `runnable_n`, completed-arm counts, consumed CPU, and the reason for every
structural zero.

Controlling-term sign results report correct, incorrect, and non-evaluable
counts out of twelve. The support gate may not discard non-evaluable selected
clusters; its exact treatment must be fixed in the v1.3 scoring artifact at
C0. This prevents presearch stops or missing wall evaluations from improving
the headline intervention claim by shrinking its denominator.

There is no early stop after a counterexample. All twelve selected clusters
must reach one frozen terminal state. A single certified crossing can satisfy
the crossing component of `DISCOVERY_SUPPORT`, including when other clusters
produce theorem signals, but wall navigation must still beat both baselines
under the full-denominator rules and satisfy every other frozen support gate.
The final results use the same non-circular pattern: a result artifact commit
`R0A` freezes all terminal evidence, ledgers, and derived scores without naming
itself, and a result attestation commit `R0T` records the already-public `R0A`
ID and completion time without altering scientific evidence or scores.

## Required schema changes

Add `benchmark-v1.3.schema.json` rather than editing the v1.2 schema. The new
schema must at minimum add or change:

- phase values for `PROTOCOL_DESIGN`, `PRE_C0_FEASIBILITY`,
  `NO_ELIGIBLE_BENCHMARK_PRE_C0`, `C0_FROZEN`, `C1_SELECTED`, `EVALUATING`,
  `COMPLETE`, and `PROTOCOL_INVALID`;
- a content-addressed `protocol` object for `P0A`/`P0T`, the provenance policy,
  registry-contact input/output schemas, and allowlisted producer and
  invocation-contract digests;
- a `source_snapshots` object containing `S0`, every supplemental snapshot,
  acquisition times, corpus digests, completeness flags, and immutable refs;
- provenance records with the three unit classes, producer/input/output
  digests, mixed-unit rejection, evidence totals, and the rule that semantic
  or unknown identity evidence excludes while registry-only evidence does not;
- a required `quota_feasibility` object with pool and policy digests, exact
  quotas, eligible counts, deficits, `PASS` or `FAIL`, `entropy_used: false`,
  and an empty selection;
- a phase-dependent randomness union: absent/unarmed with null round and value
  for pre-C0 failure, and a complete future-round contract with null value at
  C0 and verified value/evidence after unlock;
- chronology fields for `p0_artifact_commit`, `p0_attestation_commit`,
  `p0_published_at_utc`,
  `s0_acquired_at_utc`, `feasibility_checked_at_utc`, `c0_artifact_commit`,
  `c0_attestation_commit`, `c0_published_at_utc`, randomness retrieval, C1,
  evaluation, the `R0A`/`R0T` completion, and the `F0A`/`F0T` pre-C0
  termination; and
- explicit `selected_n: 12`, `aggregate_denominator: ALL_SELECTED`, structural-
  zero records, `runnable_n`, and the unchanged three-arm budget signature.

The v1.2 schema, terminal artifacts, and validator remain immutable and
independently replayable.

## Required linter and executable changes

Implement versioned v1.3 builders, selector, linter, scorer, and tests. The
v1.3 linter must fail closed unless it can prove all of the following:

1. `P0T` predates `S0`; `S0` and all supplemental snapshots predate C0; C0 is
   absent on a failed gate; and C0 publication predates the drand close.
2. The upstream commit/tree, source snapshots, classifier, provenance policy,
   inventory, eligible pool, feasibility certificate, priors, transformation
   library, scoring rule, and stopping rule all match their recorded digests.
3. Every source completed; every unit has one provenance class; every machine-
   contact unit validates against its bounded schema and frozen producer
   contract; mixed, unknown, or unexplained units fail closed.
4. Eligible rows are exactly the intersection of unambiguous machine
   classification, complete identity grouping, and absence of semantic or
   unknown exposure. Registry-contact evidence remains visible but is never
   silently placed in the exclusion set.
5. Feasibility counts and deficits are recomputed from rows. `PASS` is
   equivalent to satisfying 3/3/2/2/2; `FAIL` is equivalent to at least one
   positive deficit. Both branches have zero entropy consumption and no
   selection.
6. Only `PASS` can enter C0. Only C0 can arm a future round. The pre-C0 terminal
   branch contains no round, beacon artifact, C1, selected cluster, or
   evaluation evidence.
7. The `P0A`/`P0T`, `F0A`/`F0T`, `C0A`/`C0T`, `C1A`/`C1T`, and `R0A`/`R0T`
   artifact and attestation pairs are non-circular, ancestry is correct, and
   every attestation changes only phase and allowlisted chronology fields.
8. C1 selection is an exact replay from the content-addressed passing pool and
   verified future value, produces exactly twelve unique clusters at the fixed
   quotas, and performs no backfill or exclusion relaxation.
9. Every selected declaration stays within the pinned
   `FormalConjectures/` tree and matches its source digest. No cluster can be
   deleted, replaced, or marked outside the denominator after C1.
10. All runnable clusters have three content-addressed contracts with identical
    8 x 60-second, 480-CPU-second budgets, fixed seeds and grids, and
    `no_adaptation: true`; contract and ledger chronology precedes execution.
11. Append-only ledger chains, terminal evidence, theorem evidence,
    independent crossing verification, and all resource caps validate.
12. The scorer derives every aggregate from ledgers, emits no hand-authored
    aggregate, uses `selected_n = 12` for every headline comparison, and
    applies structural-zero/tie rules exactly once to each nonrunnable unit.

CI must include positive fixtures for both a feasible C1/complete path and an
early pre-C0 failure, plus negative fixtures for provenance laundering, mixed
units, missing source snapshots, false feasibility counts, a beacon attached
to a failed gate, C0 before a passing gate, a non-future round, selection replay
drift, quota/backfill drift, post-C1 replacement, unequal arm budgets,
pre-freeze evaluation, broken ledger chains, and denominator shrinkage.

No v1.3 C0 freeze is permitted until these checks are executable in CI and the
one preregistered feasibility build passes them.
