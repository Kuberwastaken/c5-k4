# Prospective WOWII #133 alternate-geometry trial contract

Frozen: 2026-08-13 UTC, before candidate evaluation

Status at freeze: prospective, no candidate evaluated

## Target and reading

Target: current DeepMind `FormalConjectures/WrittenOnTheWallII/GraphConjecture133.lean`.

For every finite nontrivial connected simple graph `G`, define

```text
R133(G) = path(G) - radius(G) - floor(l(G))^cC4(G),
```

where:

- `path(G)` is the maximum number of vertices in an induced path;
- `radius(G)` is the natural graph radius;
- `l(G)` is the average, over vertices `v`, of the independence number of
  the open neighborhood `N(v)`;
- `cC4(G)=1` when `G` has no not-necessarily-induced four-cycle, and zero
  otherwise.

A crossing is exactly `R133(G) < 0`.  The search lane accepts only connected
simple C4-free graphs, so its tested inequality is

```text
path(G) >= radius(G) + floor(l(G)).
```

## Frozen prediction

The proof ladder's shifted-endpoint/clean-handle geometry suggests testing
C4-free bases under local surgeries which increase metric depth while
retaining dense or locally independent neighborhoods.  The intended
separation is:

```text
radius increases faster than maximum induced-path order,
while floor(l) stays pinned or increases.
```

This prediction is directional and may fail.  All holds and failures are
logged.

## Frozen construction strata

Only the following strata may be evaluated in this trial.

1. `cage_base`: named C4-free cages and symmetric sparse controls available
   in NetworkX: Petersen, Heawood, Möbius--Kantor, Pappus, Desargues,
   Dodecahedron, Tutte--Coxeter, and Hoffman--Singleton.
2. `incidence_base`: exact Levi incidence graphs of projective planes of
   prime order `q in {2,3}` and complete-graph subdivision incidence graphs
   `S(K_n)` for `5 <= n <= 9`.
3. `clean_edge_substitution`: replace one edge of a triangle-free base by a
   path with `2 <= length <= 4`, adding at most three vertices.  Up to eight
   edge-orbit representatives are chosen deterministically by endpoint
   degree, triangle count, distance profile, then labels.
4. `sparse_shifted_attachment`: from a base or one clean-edge substitution,
   attach one pendant path of length `1 <= h <= 3` at an original endpoint
   or a new subdivision vertex.  At most six vertices may be added relative
   to the frozen base.  Up to eight deterministic attachment sites are used.

No random graph generation, unrestricted atlas expansion, degree switch, or
post-hoc new family is allowed.  Isomorphic duplicates are removed within
each base lineage by Weisfeiler--Lehman hash followed by exact isomorphism.

## Exact gates and witnesses

Every evaluated graph must pass, in order:

1. simple, nontrivial, connected;
2. exact C4-free test: every unordered vertex pair has at most one common
   neighbor;
3. exact radius by all-source BFS, retaining a center/eccentricity witness;
4. exact local neighborhood independence numbers by subset enumeration,
   retaining every local value and the exact rational average;
5. exact longest induced path by endpoint-extension enumeration, retaining
   a maximum path witness.

Each invariant is recomputed independently for every crossing or equality
candidate by descending vertex-subset enumeration of induced paths.  A
solver timeout is `UNRESOLVED_TIMEOUT`, never a hold or crossing.

## Database-sanity gate

Before construction search, the evaluator must reproduce nonnegative
residual on:

- every connected Graph Atlas graph on orders two through seven;
- cycles `C5` through `C9`, `P7`, Petersen, `K3,3`, `K7`;
- stars `K1,n` for `2 <= n <= 7`;
- `K2,3`, `K2,4`, `K3,4`, and `K4,4`.

This gate includes C4-present controls and uses the full exponent reading.
Any negative row or invariant mismatch stops the lane as `GATE_FAIL`.

## Resource and logging discipline

- Every operating-system process is capped at 60 seconds.
- Every exact induced-path solve has an internal cap of at most 55 seconds.
- Candidate order is capped at 56.
- The search stops after 1,500 nonisomorphic construction candidates or on
  the first independently verified crossing.
- Every row is appended immediately to
  `results/expansion/prospective_wowii133_alt_geometry_ledger.jsonl`.
- Phase summaries include candidate, C4 rejection, isomorph rejection,
  timeout, equality, minimum-residual, and crossing counts.

## Verdict classes

- `GATE_FAIL`: database sanity or independent invariant verification fails.
- `CROSSING_VERIFIED`: a negative residual passes the independent verifier.
- `HOLD_BOUNDED`: all completed candidates are nonnegative, with no timeout.
- `HOLD_WITH_TIMEOUTS`: no verified crossing, but at least one exact solve
  timed out.
- `NO_APPLICABLE_CANDIDATES`: all constructions fail the predeclared gates.

## Source, status, and novelty audit

Only after a verified crossing:

1. re-read the current upstream Lean declaration and repository source JSON;
2. search current DeepMind issues/PRs and the local release/status reports;
3. search the web for the exact graph/formula pairing and known resolutions;
4. classify `NEW`, `ALREADY_KNOWN`, `SOURCE_ERRATUM`, `READING_DEPENDENT`, or
   `STATUS_UNCLEAR` with URLs and dates.

No crossing may be called new before this audit.  A noncrossing trial uses
the already recorded source/status context and does not initiate public
action.

## Public-action rule

This lane may write only local script, ledger, and report artifacts.  It may
not commit, push, open an issue, open a PR, or modify an upstream repository.
