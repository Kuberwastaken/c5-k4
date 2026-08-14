# Method v1.5 future-cohort benchmark (pre-P1 protocol)

**Status:** pre-P1 implementation and validation. The deterministic builders,
bounded schemas, authenticated P1 component closure, exact CAPTURE DAG,
custody and noninterference verifiers, private identity join,
aggregate/replay certificates, public-chain verifier, fail-closed checkpoint
runner, target-blind scheduler and controlled-harness verifier, classifier
closure/runtime gate, and production target-free Linux isolation adapter exist
and have contract tests. They are not an operational benchmark yet: no live
listener, production WORM/KMS/signing infrastructure, or accepted operational
receipts exist. No P1 freeze, U1 capture, future-cohort observation, entropy,
selection, or target-semantic inspection has occurred.

**Purpose:** run the unchanged twelve-cluster, three-arm DeepMind experiment on
a genuinely prospective population: question clusters first introduced on
`google-deepmind/formal-conjectures` strictly after a public Method v1.5 freeze.

Method v1.5 succeeds immutable Method v1.4; it does not reinterpret or erase
that experiment. V1.4 correctly terminated `NO_ELIGIBLE_BENCHMARK_PRE_C0` for
its frozen rules. Its 728-cluster population is development history, not a
confirmatory population for v1.5.

## Why a future cohort

The v1.4 audit established that the accumulated local corpus cannot provide
twelve uncontaminated clusters under its frozen exclusion policy. Relaxing
that policy after seeing the zero count would turn a confirmatory experiment
into a post-hoc one. V1.5 instead moves the chronology boundary forward. A
cluster that does not yet exist at public P1 cannot have influenced the method
before P1.

This design tests the same scientific claim as v1.4 without laundering prior
contact. It deliberately trades speed for a clean temporal holdout.

The prospective claim is deliberately participant-relative. Before C1, the
only experimental participants are P1-frozen machine executables inside one
`ai-vps-controlled-harness`; there are no human participants and no model
endpoints. “Uncontaminated” therefore means that future-target semantics did
not reach, and were not produced for, one of those frozen participants. It
does not claim that every researcher or public channel was unaware of the
target. Mac applications, humans, stock Codex or Claude, interactive VPS
sessions, tmux, agent-sync, and the local LLM relay are outside the experiment
only while frozen isolation controls prove they have no causal ingress into
the harness.

## P1, scheduled checkpoints, and the fixed observation horizon

P1 has two public commits. `P1A` freezes the complete executable protocol,
schemas, source boundary, provenance rules, checkpoint invocation, and exact
component digests. Native v1.5 roles come from a closed role map; unchanged
scientific roles are selected by name and derived from the authenticated v1.4
P0A/P0T closure rather than copied from caller input. Runtime components are
resolved through exact `{closure, role}` selectors in the P1-bound checkpoint
component manifest. `P1T` must be the sole-parent child of `P1A` and change
only its one attestation artifact. Neither commit may contain candidate
identities, statement text, target rankings, or target analysis.

After the public remote is proven to contain `P1T`, the chronology capture
records the then-current upstream `main` tip as `U1`. Publication of `P1T`
must precede the observation of `U1`. The exact `P1T`, public receipt, `U1`
commit and tree, command transcript, and UTC times are content-addressed.

After U1, a public GitHub Actions schedule starts one machine-only checkpoint
at **00:17 UTC every day**. The hosted job is a target-blind scheduler and
bounded publisher, not a target-bearing participant: the dedicated controlled
harness must authenticate its request, capture canonical upstream `main`,
construct the private future pool, and return only the signed bounded
publication. A hosted runner may not decode candidate statements or receive
private registry inputs. Manual dispatch and rerun results are not cohort
checkpoints. A scheduled run that does not start before 06:00 UTC cannot be
recreated; the first detectable expired unpublished tick produces only the
bounded chronology-failure terminal bundle. Target identities remain private
until a passing pool is frozen in the separate pre-entropy phase.

The public checkpoint history is a Git-authenticated chain, not a mutable
directory convention. Its genesis must be a sole-parent child of exact `P1T`
that adds only the U1 receipt. Each checkpoint must be a sole-parent,
add-only commit from the verified public tip and add exactly
`publication-manifest.json`, `quota-certificate.json`, and `receipt.json`
under its scheduled-tick path. The verifier derives the prior receipt from
ancestry; a caller-supplied predecessor is not authoritative. Publication is
an atomic normal fast-forward push, with overwrite and force-push forbidden.

The cohort closes at the first scheduled checkpoint whose frozen aggregate
counts meet all five quotas. This is a target-blind stopping time: neither
statement semantics nor outcomes are inspected, and the operator cannot wait
for a preferred passing tip. That checkpoint is U2. The terminal population is
computed from `U1..U2`; later commits cannot enter it.

If no checkpoint passes, the last allowed checkpoint starts at 00:17 UTC on
**2027-08-15** and must start before **2027-08-15T06:00:00Z**. This deadline
was chosen in the pre-P1 scaffold, before future targets or counts existed. A
quota deficit there terminates `INSUFFICIENT_FUTURE_COHORT_PRE_C0`; a missed
last checkpoint terminates `INVALID_CHRONOLOGY_CAPTURE`. The deadline cannot
be extended or replaced. Every U2 candidate must descend from U1; no alternate
ref, manual run, rerun, or hand-picked tip may be substituted.

## Deterministic future-cohort membership

The sampling unit remains the frozen conservative question cluster used by
the inherited machine grouping rule. V1.5 claims only the identities and
relations that this exact executable rule can establish; it does not claim a
universal decision procedure for mathematical equivalence. A cluster belongs
to the future cohort only if all of the following hold:

1. it has an unambiguous first-introduction commit in `U1..U2` under the
   frozen grouping and history-walk algorithm;
2. neither it nor any identity trace or relation detected by the frozen
   grouping/history rules is present at `U1` or in the immutable v1.4
   728-cluster population;
3. its first-introduction membership is determined from Git ancestry and
   content, not author or committer timestamps;
4. it satisfies the same open-status, finite-object, classifier, identity,
   and executable applicability rules frozen at P1; and
5. no semantic or unknown exposure is found from P1 through the pre-selection
   source cutoff.

Machine-detectable rename, move, delete-and-readd, namespace reuse, coupled
formal add/delete, or reopening does not make an old cluster new. A
transformation whose continuity cannot be established by the frozen rules is
excluded as ambiguous/unknown; the protocol does not assert that every
possible reformalization is logically recognized. Membership is generated
without mathematical interpretation, target ranking, or outcome inspection.

The v1.4 population is an explicit negative-control exclusion set. No one of
those 728 clusters may enter v1.5 confirmatory selection, even if a later
upstream edit would otherwise make it appear newly introduced.

## Provenance, authenticated delivery, and private identity joining

V1.5 distinguishes content custody from semantic contact. Merely storing an
immutable upstream blob or a verified schema-bounded enumeration is not
evidence that a human or language model understood a target. Conversely, no
source is exempt merely because a program copied it.

Every evidence unit receives exactly one frozen provenance class:

- `SEMANTIC_EXPOSURE`: target meaning, status, residual, family, proof route,
  candidate, or target-specific result was delivered to a human or language
  model. This excludes the whole cluster.
- `MACHINE_REGISTRY_CONTACT`: an allowlisted, content-addressed executable
  performed only frozen identity/syntax/history operations and emitted a
  bounded schema with no target semantics. This is recorded but does not
  exclude.
- `IMMUTABLE_SOURCE_CUSTODY`: exact upstream/vendor bytes were retained but
  there is no evidence that they were presented semantically. Only frozen
  machine lanes may decode these bytes before C1. This is recorded but does
  not exclude.
- `UNKNOWN`: provenance, completeness, producer, output schema, or contact
  level cannot be proved. This excludes the whole cluster.

The ontology is prospective only. It may not reclassify v1.4 evidence or
recover a member of the 728-cluster exclusion set. Natural-language research,
manual target inspection, model prompts, code comments, and target-specific
compute remain semantic when they reach or control a frozen experimental
participant. Public existence, or independent delivery to a proved
nonparticipant, is not experimental delivery. The source boundary does not
claim complete surveillance of GitHub, every local file, every browser, Mac,
or general interactive sessions. It freezes a causal boundary around the
controlled harness instead. Any possible unregistered filesystem, socket,
process-memory, credential, environment, network, model-context, or
control-input ingress into that boundary invalidates the protocol; it cannot
be downgraded to cluster-level `UNKNOWN` because no alias later matches. A
captured but unclassifiable unit is `UNKNOWN` and excludes every cluster to
which the frozen exact join binds it.

The implemented custody contracts specify signed per-host hash/sequence
chains, five-minute heartbeat bounds, content-addressed payload verification,
restart and gap handling, private coverage certificates, and a public sealed
binding that cannot disclose private record metadata. The broker,
remote-authoritative WORM bridge, custody compiler, private-input assembler,
participant ledger, and noninterference key/receipt contracts exercise durable
`PREPARE -> START -> DELIVER/ABORT` transitions, Ed25519 receipt chaining, a
240-second heartbeat, sticky invalidation, crash recovery, and wrapped
subprocess standard streams. They are deliberately fixed to
`PRE_P1_NOT_OPERATIONAL`: there is no live production daemon, immutable remote
store, accepted host key, or operational proof of noninterference from stock
Codex, Claude, Mac, tmux, the local relay, or general VPS delivery paths.

After C1, target semantics may enter only fresh isolated arm and independent-
verification processes or model contexts. No arm inherits a prior chat,
memory, cache, session, writable state, or another arm's result. Humans remain
outside the scored execution path until sealed arm and verification records
exist.

The temporal holdout also requires upstream nonintervention. Before P1T, the
experimenter identities and abstention rule must be frozen. Those identities
may not author, edit, review, request changes to, lobby for, or otherwise
influence a future-cohort `formal-conjectures` cluster during `P1T..U2`.
Machine-detectable experimenter contact excludes the conflicted cluster;
unreported or unattributable intervention invalidates the protocol.

At a checkpoint, provenance ledgers and their content pack stay private. The
private identity-join builder reopens digest-verified bytes only for excluding
`SEMANTIC_EXPOSURE` and `UNKNOWN` units and compares the machine-generated
cluster aliases with a frozen exact, boundary-delimited rule. It emits neither
source text nor matched alias values. The future-cohort builder consumes this
private hit ledger to exclude affected clusters; the public checkpoint exposes
only sealed bindings and aggregates. This is an exact frozen alias join, not a
claim that semantic paraphrases or all logical equivalents can be detected.

## Unchanged confirmatory experiment

An actual v1.5 selection still contains exactly twelve clusters with fixed
quotas:

- three `GRAPH_SCALAR_INEQUALITY`;
- three `GRAPH_STRUCTURAL_PROPERTY`;
- two `FINITE_ALGEBRA_EQUATIONAL`;
- two `AUTOMATA_GAME_PROCESS`; and
- two `FINITE_COMBINATORIAL`.

There is no cross-stratum backfill, quota relaxation, manual substitution,
replacement, or complete-case denominator. If any stratum is short at the
fixed horizon, v1.5 terminates `INSUFFICIENT_FUTURE_COHORT_PRE_C0` with no
entropy and no selection.

Every selected cluster receives the unchanged isolated `CATALOGUE`, `GENERIC`,
and `WALL_NAVIGATION` arms. Each arm has eight process trees, a 60-second wall
cap per tree, and at most 480 CPU-seconds. Shared analysis remains capped at
600 CPU-seconds and independent verification at two additional 60-second
process trees. All twelve selected clusters remain in the denominator.

V1.5 inherits v1.4's fixed baselines, wall transformation, no-adaptation rule,
process isolation, append-only ledgers, outcome space, scoring, stopping,
forecasting, verification, and non-circular publication rules. P1 must bind
the exact inherited bytes and executable digests; this scaffold alone is not
an executable freeze.

## Gate, selection, and terminal outcomes

Each scheduled registry checkpoint keeps schema-bounded identities private and
emits only bounded aggregate evidence until the quota gate passes. The
certificate builder authenticates P1A/P1T, resolves grouping, classification,
registry, provenance, and schemas through the exact P1 component selectors,
binds the chronology receipt and private runtime inputs, recomputes counts and
deficits from records, and seals the private-registry digest. The replay step
must independently reconstruct the private registry in an isolated repository
and produce byte-identical output before a checkpoint receipt can finalize.
The public-chain verifier then proves that every earlier scheduled checkpoint
failed the quota gate and that U2 is the first pass.

If all five quotas are met, a public pre-entropy commit freezes the complete
eligible pool. Selection then uses the same future drand rule and exact
3/3/2/2/2 sampler as v1.4, followed by the same C0/C1 separation. There is no
target-semantic inspection before C1.

The allowed high-level terminal outcomes are:

- `INSUFFICIENT_FUTURE_COHORT_PRE_C0`: a fixed stratum quota is short at the
  horizon;
- `INVALID_CHRONOLOGY_CAPTURE`: P1/U1/U2 ancestry, timing, receipt, or replay
  does not validate;
- `PROTOCOL_INVALID`: another frozen invariant fails; or
- a completed twelve-cluster score report under the unchanged v1.4 scientific
  rules.

No terminal outcome authorizes rerunning the same cohort with new rules. A
scientific change requires a new version and a new genuinely future boundary.

## Implemented contracts and remaining activation work

The repository currently contains and tests:

- future-cohort, chronology, provenance, source-boundary, path-purpose, and
  checkpoint-invocation contracts;
- strict schemas for registries, source/provenance/custody evidence, aggregate
  certificates, replay attestations, public-chain proofs, component manifests,
  and P1A/P1T;
- builders/verifiers for authenticated vendor bases, Git provenance
  partitioning, source snapshots, provenance classification, the private
  identity join, future-cohort construction, aggregate extraction and exact
  replay, private custody chains, the public checkpoint chain, generated
  registry artifacts, and P1 assembly;
- a fail-closed checkpoint runner that authenticates its prospective
  P1/component and public-chain inputs, constrains publication to three
  schema-bounded public files, and refuses CAPTURE while the invocation and
  operational-evidence gates remain PRE-P1;
- a dedicated-VPS controlled-delivery prototype and adversarial tests for
  signed receipt sequencing, content-before-delivery custody, crash ambiguity,
  store failure, heartbeat expiry, and stdin/stdout/stderr capture;
- a PRE-P1 S3 Object Lock adapter contract that verifies COMPLIANCE retention,
  an exact KMS key and bucket-policy digest, deletion denial, a single
  version/no-delete-marker inventory, and version-pinned bytes, plus a
  remote-authoritative broker bridge whose local CAS is only a cache;
- an inert, target-blind CloudFormation plan for the future private store. Its
  static verifier closes the five-resource S3 Object Lock/KMS/single-writer
  IAM set, exact policy commitments, universal destructive/out-of-prefix
  denies, retention on replacement/deletion, and zero public outputs. It makes
  no AWS call and is not live acceptance;
- a signed broker-to-custody compiler with an authenticated single-service
  epoch, and an inert private-input assembler that accepts only version-pinned
  WORM locators, replays the registry against two distinct acquisitions, and
  writes its private manifest atomically last;
- an exact fourteen-stage CAPTURE orchestrator, authenticated P1 role
  resolution, and target-blind controlled-harness request verifier with
  durable replay reservation and a bounded three-file response;
- a machine-only participant ledger plus signed noninterference receipt and
  public-key commitment contracts; raw verification-key bytes remain private
  WORM input and are not repository roles;
- a target-free classifier closure receipt and runtime gate that authenticate
  the exact classifier, syntax-pool builder, schemas, and executing verifier
  before any future-registry row may be read;
- a target-free three-arm capability matrix and execution-envelope validator
  that deny wall data to both baselines, enforce the all-PENDING/equal-budget
  barrier, and embargo every arm result until the complete triplet terminates;
- a test-only sealed triplet-launch skeleton that exercises one-shot claiming,
  deterministic balanced scheduling of all 24 trees, capability-minimal
  inputs, and combined-only result records;
- a descriptor-pinned Linux isolation path and production 24-tree adapter with
  six namespaces, read-only capability mounts, disjoint private writable
  roots, no network, one CPU, and a 60-second process-tree cap. Target-free
  acceptance passes on a supported Linux host, but the adapter remains
  nonactivated and has consumed no target;
- an inert Amazon Linux 2023 deployment scaffold and read-only host verifier,
  plus a future operational-unit generator that binds root-owned P1/service
  bytes, offline-verified TLS certificate/key identity, systemd credential
  delivery, the exact scheduled-workflow OIDC identity, pinned endpoint
  resolution, WORM/noninterference/destructive-gap acceptances, and required
  namespace capabilities. Generated units remain uninstalled, inactive, and
  unauthorized for activation;
- an offline validation workflow; and
- a target-blind scheduled checkpoint workflow and bounded publisher in an
  intentionally inert state. Its invocation contract remains
  `PRE_P1_SCAFFOLD_NOT_EXECUTABLE`, with null workflow and runner digests, so
  scheduled jobs must refuse to capture.

The hosted scheduled workflow is not yet connected to a deployed dedicated
harness. The production endpoint, listener, TLS/OIDC deployment, and
operational receipts remain unset. The hosted side must remain target-blind:
finding a private input in hosted `RUNNER_TEMP` is not custody or delivery
proof.

The following are operational blockers, not completed artifacts:

1. provision and live-accept the private Object Lock bucket, KMS key, deletion
   policy, least-privilege role, host signing key, TLS/OIDC endpoint, and
   continuously supervised single-writer service;
2. produce and verify operational custody, participant, and noninterference
   evidence for the machine-only `ai-vps-controlled-harness`, including zero
   ingress from Mac, humans, stock Codex/Claude, tmux, general sessions,
   agent-sync, and the local relay, and bind its exact filesystem, process,
   network, environment, secret, and control-input isolation;
3. run the complete target-free CAPTURE and 24-tree triplet path on the chosen
   production host, accept its real kernel/WORM/broker evidence, and freeze the
   exact workflow, runner, custody, source, isolation, schema, and executable
   digests in the closed P1 component set;
4. freeze experimenter identities, upstream abstention, and deterministic
   conflict exclusion, then change the invocation contract to executable only
   after every activation requirement passes;
5. create and publish the sole-purpose `P1A` and immediate one-path `P1T`
   commits and verify the public P1T receipt; and
6. only then perform the one-shot U1 capture and create the public checkpoint
   branch genesis.

No P1A, P1T, operational custody/noninterference receipt, U1/U2 receipt,
operational private store, future registry, entropy value, selection, target
identity publication, or benchmark outcome exists today.
