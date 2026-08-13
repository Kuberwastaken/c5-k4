# Method v0.6: executable gate contracts

Date: **2026-08-13 UTC**

Status: **methodology proposal; no graph evaluation performed**

Scope: existing published graph statements from collections already represented
in `google-deepmind/formal-conjectures`. This report changes the execution
protocol only. It does not select a target, authorize a trial, or alter any
earlier outcome.

## Central failure mode

The WOWII 179 and WOWII 305 incidents reveal one common failure mode: **the
mandatory gate was frozen before the gate itself had been shown to be
internally consistent and executable under its declared resources**.

- For WOWII 179, the contract required a complete database gate, but the
  selected exact formulations could not finish `T(7)` in the primary run or
  `C5[K5]` in the independent replay under the immutable 55-second internal
  deadline. Meanwhile, a pre-grid family identity proved the entire frozen
  family nonnegative. The trial therefore spent most of its budget on a gate
  that could not close before using an exact obstruction that could have pruned
  the grid.
- For WOWII 305, the prose contract explicitly included the endpoints of a
  complement edge in the union of their open neighborhoods, but its frozen
  `C5[K2]` calibration used the endpoint-excluding value. Both implementations
  correctly agreed on the endpoint-including value. The coordinator initially
  treated implementation agreement as sufficient and unlocked the grid because
  the exact frozen calibration assertion was absent from the executable unlock
  predicate.

The lesson is not merely to add one assertion or choose a faster solver. Method
v0.6 must compile every selection contract into executable assertions and must
make successful compilation, semantic calibration, computational feasibility,
and independent replay prerequisites for an atomic grid-unlock attestation.

## 1. Machine-readable contract compilation

Every prospective selection report must have a canonical machine-readable
companion contract before a trial implementation can be considered frozen. A
JSON representation is sufficient if it is serialized with sorted keys,
UTF-8, and no non-semantic formatting variance.

The contract must contain at least:

```text
schema_version
target_id
source_repository
source_commit
source_file_or_record
normalized_statement_ast
reading_id
applicability_rules
residual_definition
residual_sign
baseline_theorem
baseline_identity
semantic_fixtures
gate_control_keys
feasibility_sentinels
primary_solver_id
replay_solver_id
internal_timeout_seconds
external_timeout_seconds
family_constructor_id
parameter_domain
grid_keys
stop_rules
```

Contract compilation must fail unless all of the following assertions hold:

```text
assert schema_version == METHOD_V06_SCHEMA
assert sha256(canonical_contract_json) == frozen_contract_sha
assert source_commit == frozen_source_commit
assert normalize(source_statement) == normalized_statement_ast
assert residual_sign == "negative_is_crossing"
assert gate_control_keys == expected_gate_control_keys
assert len(gate_control_keys) == len(set(gate_control_keys))
assert grid_keys == canonical_deduplicated_declared_grid_keys
assert len(grid_keys) == len(set(grid_keys))
assert internal_timeout_seconds == 55
assert external_timeout_seconds == 60
```

The compiled artifact must record the selection commit or immutable content
hash. Trial code must refuse contracts whose source, statement normalization,
control manifest, family constructor, parameter domain, or stop rules differ
from that frozen artifact.

## 2. Semantic microfixtures

Before the full database gate, both implementations must evaluate a small set
of hand-derivable semantic fixtures. These fixtures test definitions and
conventions, not search performance. Each fixture contains an exact graph,
applicability result, invariant tuple, residual, and any relevant multiset or
extremizing witness.

The executable requirement is:

```text
for fixture in contract.semantic_fixtures:
    assert primary(fixture.graph) == fixture.expected_tuple
    assert replay(fixture.graph) == fixture.expected_tuple
    assert verify_witnesses(primary(fixture.graph))
    assert verify_witnesses(replay(fixture.graph))
```

Fixtures must cover every convention capable of changing the verdict, such as
open versus closed neighborhoods, inclusion or exclusion of edge endpoints,
empty optimization domains, integer division, floor/ceiling placement, and
exceptional hypotheses.

For the endpoint-inclusive reading used in the WOWII 305 contract, the
required calibration would have been:

```text
assert C5K2.complement_edge_neighborhood_multiset == [8] * 20
assert (m, M, gamma_t, T306, R305) == (8, 8, 3, 5, 3)
assert every complement edge uv satisfies:
       u in N(u) union N(v)
       v in N(u) union N(v)
```

The former frozen tuple `(gamma_t,M,R305)=(3,6,1)` must therefore fail contract
compilation rather than survive until the end of a 1,079-row gate.

When a prospective family has a previously evaluated boundary, constructor
equivalence is also a semantic fixture. For the WOWII 305 family it would be:

```text
for s in 1..8:
    assert canonical_g6(G(s,s)) == canonical_g6(C5[Ks])
```

For a WOWII 179-style trial, the complete-graph and star equalities must be
literal expected tuples, including the `K2` convention, rather than properties
checked only after all controls have run.

## 3. Forty-second feasibility sentinels

The fixed 55-second internal and 60-second external caps remain unchanged.
Before a solver/control manifest can be frozen, however, both proposed exact
implementations must complete a declared sentinel set within **40 seconds per
graph** on the campaign environment. This reserves fifteen seconds of headroom
below the internal deadline for ordinary runtime variation and serialization.

The sentinel set must include:

- every named control known or expected to be optimizer-hard;
- the largest or densest controls for each exact formulation;
- representatives exercising every materially different solver model;
- size-matched neutral controls for the largest prospective row, without
  evaluating a held-back prospective family member.

The executable requirement is:

```text
for solver in [primary, replay]:
    for graph in feasibility_sentinels:
        result = timed_exact_run(solver, graph)
        assert result.status == "OK"
        assert result.elapsed_seconds <= 40
        assert verify_witnesses(result)
```

For a 179-like gate, `T(7)`, `C5[K5]`, and `C5[K8]` must be sentinels because
the actual incident showed that different formulations fail on different
members of that set.

If a sentinel fails, the selection cannot freeze that solver/control
combination. The allowed responses are to supply a structural certificate,
use a faster exact formulation, or prospectively declare a smaller control
manifest with a written coverage justification. Increasing the cap after the
failure remains forbidden.

## 4. Row-level gate assertions

Implementation agreement is necessary but not sufficient. Every completed
control must independently satisfy the contract:

```text
for row in completed_gate_rows:
    assert replay_hypotheses(row.graph) == row.hypotheses
    assert replay_applicability(row.graph) == row.applicability
    assert row.residual == row.lhs - row.rhs
    assert row.residual == evaluate(contract.residual_definition, row)
    assert evaluate(contract.baseline_identity, row)
    assert row.baseline_slack >= 0
    assert verify_all_serialized_witnesses(row)
    assert every_reported_optimum_has_matching_certificate(row)
    assert primary_tuple(row.key) == replay_tuple(row.key)
```

Gate completion additionally requires the exact expected control-key set, no
duplicate keys, no missing rows, no unexpected status, no timeout, no failed
fixture, no negative proved baseline, and no unexplained source-statement
crossing.

## 5. Pre-grid obstruction check

Before expensive invariant optimization, the trial must attempt an exact
family- or quotient-level feasibility check for a negative residual on the
entire frozen parameter domain.

The check returns exactly one of:

```text
SAT      an exact parameter tuple can make the residual negative
UNSAT    the frozen domain is proved nonnegative
UNKNOWN  no complete exact reduction is available
```

The protocol is:

```text
status = exact_negative_feasibility(
    family_constructor,
    parameter_domain,
    residual_definition,
    baseline_identity,
)
assert status in {"SAT", "UNSAT", "UNKNOWN"}

if status == "UNSAT":
    assert count(grid_rows) == 0
    stop as PREGRID_THEOREM_SHADOW
```

`UNSAT` may be certified by exact symbolic algebra, exhaustive arithmetic over
the declared parameter tuples, a proof assistant, or a separately verified
finite quotient argument. It is not inferred from sampled graph evaluations.

For WOWII 179, the pre-grid checker would verify on every frozen parameter
tuple:

```text
R179(H(p;a)) = 2 * (A - M - (s - 1))
assert R179(H(p;a)) >= 0
```

That exact identity makes the frozen negative-residual feasibility problem
`UNSAT`; the grid should have been pruned without waiting for the database gate
to close. A pre-grid theorem shadow is a valid methodological result, but it
does not prove the source conjecture beyond the certified family.

## 6. Cryptographic and chronological unlock attestation

Grid construction and grid evaluation must be separate from gate execution.
The grid constructor may run only after an atomic attestation binds the exact
contract to the exact primary and replay ledgers.

Define:

```text
gate_ok =
    contract_integrity_ok
    and semantic_fixtures_ok
    and feasibility_sentinels_ok
    and primary_gate_complete
    and replay_gate_complete
    and exact_rowwise_agreement
    and all_row_level_assertions_ok
    and no_timeout
    and no_error
    and no_failed_calibration
    and no_unexplained_crossing
```

Before issuing an unlock token, assert chronological integrity:

```text
assert gate_ok
assert count(existing_grid_rows) == 0
assert last_primary_event == "gate_complete"
assert last_replay_event == "gate_verify_complete"
assert no ledger event after either completion mutates a gate row
```

The attestation is then:

```text
unlock_token = sha256(
    frozen_contract_sha
    || primary_ledger_merkle_root
    || replay_ledger_merkle_root
    || semantic_fixture_report_sha
    || feasibility_report_sha
    || gate_completion_timestamp
)
```

Every grid worker must receive the token, recompute it from immutable inputs,
and reject execution if it differs. The first grid row must record the token.
Any later gate correction invalidates the token and permanently excludes rows
produced under the superseded attestation.

This would have prevented the WOWII 305 grid from being constructed: the
failed calibration makes `gate_ok` false even though the two implementations
agree with each other.

## 7. Required Method v0.6 chronology

The enforced order is:

```text
source/readings freeze
  -> canonical contract compilation
  -> semantic microfixtures
  -> 40-second feasibility sentinels
  -> pre-grid obstruction feasibility
  -> full primary database gate, unless pre-grid UNSAT stops the trial
  -> complete independent replay
  -> row-level and manifest-level audit
  -> cryptographic/chronological unlock attestation
  -> construction of the first grid row
```

No stage may infer the success of an earlier stage from the absence of an
error. Each stage emits a named, hashed, positive completion record consumed
by the next stage.

## 8. Held-out status

No genuinely held-out target can be nominated from the currently inspected
repository material. The 77-declaration cross-sweep classified every
declaration in its manifest, and the subsequent refresh inspected the Dean
`k=5` addition, producing 79 inspected declarations. Items excluded from
single-arsenal falsification were still read and categorized; they cannot be
retrospectively relabeled held out.

A future held-out evaluation therefore requires a new upstream-manifest delta
after the locked `547f309e` baseline. That delta must be frozen before
statement-level ranking, wall analysis, transformation selection, or graph
evaluation. Method v0.6 nominates **no current WOWII or formal-conjectures
target as held out**.

## Disposition

Method v0.6 should treat a trial contract as executable evidence, not prose
that an implementation approximates. The #179 timeout and #305 calibration
disagreement are both prevented by the same change: prove that the gate is
semantically correct, computationally feasible, and cryptographically closed
before allowing the prospective grid to exist.
