# OEIS A231201 v2.1 contaminated DEVELOPMENT freeze

This is the smallest operational supersession of the immutable v2 freeze at
commit `83ef494`.  Run
[`31809864013`](https://github.com/Kuberwastaken/c5-k4/actions/runs/31809864013)
proved that the v2 constructor cannot execute on its declared Python 3.9.23
runner: all 18 round-zero constructor jobs reached
`int.bit_count()` and failed before emitting an assignment.  That run is an
operational failure and carries no mathematical result.

## Frozen change

V2.1 changes only the constructor entry point and its pre-dispatch tests:

- `scripts/construct_oeis_a231201_v21.py` replaces the three uses of
  `int.bit_count()` with an explicit nonnegative-integer population-count
  helper implemented as `bin(value).count("1")`;
- `scripts/test_oeis_a231201_v21_constructor_paths.py` executes synthetic
  deterministic-greedy, compressed-set-cover, and small-basis-growth paths;
  the CP-SAT boundary is mocked, so the tests instantiate no real target model
  and evaluate no frozen target seed/domain, exact target adversary, candidate
  certification, or search.  The greedy smoke does construct a 55-coordinate
  target-format assignment against only three synthetic rows;
- `.github/workflows/oeis-a231201-v21-development.yml` runs those tests under
  Python 3.9.23 before any gate or search job and uses distinct v2.1 artifact
  names.

The v2 manifest, arithmetic universe, source locks, database-sanity gate,
evidence schemas, predecessor validation, adversary, independent verifier,
three arms, six cells, three rounds, and deterministic settings are reused
without alteration.  Every construction, adversary, gate, and independent
verification execution remains bounded by 54 internal seconds and the same
external `timeout --signal=TERM --kill-after=6s 60s` cap.

## Execution rule

Only an exact 40-hex commit containing this complete freeze may be supplied to
the v2.1 workflow.  The harness must verify the immutable v1 and v2 freezes,
then this v2.1 registry, compile every A231201 v2/v2.1 Python file, and pass the
v2.1 constructor-path tests under Python 3.9.  Any prerequisite, checksum,
predecessor, artifact-verifier, or freeze failure remains fail-closed.

This lane is still `CONTAMINATED_DEVELOPMENT`; it is not a held-out trial.
Do not publish a candidate or release from constructor output.  Only the exact
adversary plus the independent final verifier may promote a candidate, followed
by source/status/novelty review under the repository protocol.
