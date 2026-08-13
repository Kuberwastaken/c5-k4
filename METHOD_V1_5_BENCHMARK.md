# Method v1.5 future-cohort benchmark (pre-P1 protocol)

**Status:** protocol scaffold only. No P1 freeze, future-cohort observation,
registry build, entropy, selection, or target-semantic inspection has occurred.

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

## P1, scheduled checkpoints, and the fixed observation horizon

P1 has two public commits. `P1A` freezes the complete executable protocol,
schemas, source boundary, provenance rules, inherited component digests, and
the one allowed chronology-capture invocation. `P1T` attests the already
public `P1A` object and changes only the attestation artifact. Neither commit
may contain candidate identities, statement text, target rankings, or target
analysis.

After the public remote is proven to contain `P1T`, the chronology capture
records the then-current upstream `main` tip as `U1`. Publication of `P1T`
must precede the observation of `U1`. The exact `P1T`, public receipt, `U1`
commit and tree, command transcript, and UTC times are content-addressed.

After U1, a public GitHub Actions schedule starts one machine-only checkpoint
at **00:17 UTC every day**. Manual dispatch and rerun results are not cohort
checkpoints. A scheduled run that does not start before 06:00 UTC is recorded
as missed and cannot be recreated. Each valid checkpoint atomically captures
canonical upstream `main`, constructs the identity-only future pool, and
publishes only receipts, hashes, aggregate stratum counts, and the quota
certificate to an append-only checkpoint branch.

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

The sampling unit remains a conservative question cluster: sibling
statements, equivalent encodings, and logical negations are one unit. A
cluster belongs to the future cohort only if all of the following hold:

1. it has an unambiguous first-introduction commit in `U1..U2` under the
   frozen grouping and history-walk algorithm;
2. neither it nor any known sibling/equivalent/negated encoding is present at
   `U1` or in the immutable v1.4 728-cluster population;
3. its first-introduction membership is determined from Git ancestry and
   content, not author or committer timestamps;
4. it satisfies the same open-status, finite-object, classifier, identity,
   and executable applicability rules frozen at P1; and
5. no semantic or unknown exposure is found from P1 through the pre-selection
   source cutoff.

Rename, move, delete-and-readd, namespace change, reformalization, or reopening
does not make an old cluster new. Ambiguous ancestry or grouping fails closed.
Membership is generated without mathematical interpretation, target ranking,
or outcome inspection.

The v1.4 population is an explicit negative-control exclusion set. No one of
those 728 clusters may enter v1.5 confirmatory selection, even if a later
upstream edit would otherwise make it appear newly introduced.

## Provenance without storage-as-exposure

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
manual target inspection, model prompts, code comments, commits, issues,
releases, and target-specific compute remain semantic sources. Mixed units
and unverifiable generated artifacts are `UNKNOWN`.

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

Each scheduled registry checkpoint emits only schema-bounded identity and
aggregate evidence until the quota gate passes. Before any entropy request, a
machine linter recomputes first-introduction membership, the v1.4 exclusion,
provenance, eligibility, exact per-stratum counts, and proof that U2 is the
first passing checkpoint.

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

## Scaffold artifacts

The present checkpoint adds only these non-executable high-level contracts:

- `results/benchmark/v1.5-protocol/future-cohort-rule.json`;
- `results/benchmark/v1.5-protocol/provenance-ontology.json`; and
- `results/benchmark/v1.5-protocol/chronology-rule.json`.

Production builders, schemas, source snapshots, P1 components, receipts,
entropy, selections, target identities, and outcomes intentionally do not
exist yet.
