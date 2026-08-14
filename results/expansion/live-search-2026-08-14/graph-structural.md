# Live search: finite graph structural/property targets

Started: 2026-08-14 UTC  
Completed: 2026-08-14T06:22:33Z  
Disposition: **NO CANDIDATE; one bounded zero and one status-preempted calibration**

This is a live development lane, not part of the uncontaminated Method v1.5
benchmark.  It uses current upstream
`google-deepmind/formal-conjectures@b33d8678a28118c95d8d4f60b11faaf39ccff1e6`
(tree `b3507366468669ac7a599254f59c5bc05f8409cb`).  The remote tip was
rechecked at completion.  Every search or exact-control subprocess was under
an external `timeout` with a 60-second wall cap.  Discovery arms used one
process and 30 seconds each except where an exhaustive catalogue terminated
naturally; there was no cross-arm adaptation or result sharing during a
triplet.

## Selection and statement gate

I regenerated the live syntax classification from the current upstream tree
and subtracted target-specific work already present in this repository.  Most
otherwise untouched `GRAPH_STRUCTURAL_PROPERTY` rows are not finite
counterexample targets: Erdős 1175, 567, 595, 600, 80, and 82 are
infinite/asymptotic; Erdős 593 and 596 depend on infinite obligatory/escape
predicates or an opaque `answer(sorry)` characterization.  Extending a finite
prefix cannot resolve those declarations.  The two initially runnable rows
were:

1. `FormalConjectures/Paper/ClaudesCycles.lean`,
   `cube_hamiltonian_arc_decomposition_even`: for every even `m > 2`, the
   three outgoing arcs at every vertex of `(ZMod m)^3` can be partitioned into
   three directed Hamiltonian cycles.  The first instance is `m=4`.
2. `FormalConjectures/ErdosProblems/835.lean`, `erdos_835` / the Johnson
   variant: does some `k>2` admit a `(k+1)`-colouring of the `k`-sets of a
   `2k`-set in which every `(k+1)`-set sees all colours?  Equivalently,
   `chi(J(2k,k))=k+1`.  Upstream and Ma--Tang rule out the composite-`k+1`
   cases and explicitly cover `3 <= k <= 9`; `k=10` (`k+1=11` prime) is the
   first remaining bounded witness search.

The search evaluated the right-hand mathematical predicates, not the truth
value hidden by `answer(sorry)`.  A witness would support a positive answer;
failure to find one is neither a disproof nor evidence for the opposite value.

## Attempt 1: Claude's Cycles, `m=4`

### Frozen encoding and arms

A state assigns the three coordinate-bump arcs at each of the 64 vertices to
three colours.  Every state admitted to scoring was checked to give each
colour exactly one incoming and one outgoing arc at every vertex.  The
objective was

`sum_c (number of directed cycles in colour c - 1)`.

Thus objective zero is literally a `HasHamiltonianArcDecomposition 4`
witness; no proxy inequality was used.

| arm | 30-second outcome | best literal cycle counts | verdict |
|---|---:|---:|---|
| `CATALOGUE` | 436,329 raw evaluations of the fixed affine direction-colouring catalogue (repeated complete passes over the tiny parameter set); 16,161 valid factorizations | `[16,16,16]`, residual 45; state SHA-256 `fa54277c5450e8455831670d5e94e473fb44fad776685d67c13c2cb016f0cb80` | `HOLD_BOUNDED` for the catalogue only |
| `GENERIC` | 182,675 random alternating-factor switches, 73,586 accepted, 366 restarts | `[1,2,1]`, residual 1; state SHA-256 `69aefa27b7c605cea96bc44e543b660a00b9894f7b101a01e5c19e6ed4390ac3` | `NO_CANDIDATE`, one cycle above the goal |
| `WALL_NAVIGATION` | 32,000 target-specific alternating-cycle splice evaluations, 996 accepted, 65 restarts | `[2,1,1]`, residual 1; state SHA-256 `aea8410a16b027973cc9a612e99267d25189591d42a194296035da67601aa6f3` | `NO_CANDIDATE`, one cycle above the goal |

### Literal and database sanity

The ordinary connected-Atlas gate is ill-typed for this directed torus
decomposition predicate, so I used the source-native controls instead.

- Exhaustive `m=2`: all `6^8 = 1,679,616` local arc-colour assignments were
  checked; 576 are three perfect matchings and zero are three Hamilton cycles.
  This independently reproduces the stated Aubert--Schneider impossibility.
- Known-positive odd `m=3`: both the generic and wall engines reached residual
  zero almost immediately, with independently different state hashes
  `66e118a58d7fe85e422b0a68a8d4c1196a81de42ccd857cd6f4509e7264ce769`
  and `3fb94a7ad7cf6d2236dd0a6d3a6afda7ed94f447fda6bfa02bba929c05fdd242`.
- Every reported `m=4` state passed the incoming/outgoing bijection and local
  three-distinct-directions checks.  There was no candidate to send through
  independent witness replay.

### Upstream/source gate: status preempted

Live main still marks the declaration `research open`, but the required PR and
commit audit found open PR
[#4935](https://github.com/google-deepmind/formal-conjectures/pull/4935),
created 2026-08-13, CI-green and mergeable.  It records that Knuth's note was
revised on 2026-04-14: the added page 6 settles the even case, and the PR
author independently verified explicit decompositions at `m=4` and `m=6`.
The original statement entered through merged PR
[#3428](https://github.com/google-deepmind/formal-conjectures/pull/3428) /
commit `c9387bb1d9c0`, before that revision.  Issue #3427 is closed.  Therefore
this arm triplet is **STATUS_PREEMPTED**, not an open-target zero and never a
novelty candidate.

The residual-one states are still a useful calibration: single alternating
factor switches readily merge all but one component, but the chosen greedy
wall neighbourhood stalls before the final simultaneous splice.  Since the
source has a construction, this is direct evidence that the wall catalogue is
missing a multi-factor/global switch rather than evidence of nonexistence.

## Attempt 2: Erdős 835, `k=10`

### Frozen encoding and arms

There are `C(20,10)=184,756` colour variables and `C(20,11)=167,960`
rainbow constraints.  For each 11-set the code enumerated its eleven 10-set
deletions exactly.  The residual is the sum, over constraints, of
`11 - number_of_distinct_colours`; residual zero is exactly `Property 10`.

| arm | 30-second outcome | best result | verdict |
|---|---:|---:|---|
| `CATALOGUE` | 802 complete evaluations from three frozen polynomial/rank hash families | duplicate residual 437,580; 512/167,960 constraints rainbow | `NO_CANDIDATE` |
| `GENERIC` | 6,462 full-CSP min-conflict moves, 5,628 accepted | duplicate residual 632,238; 41 constraints rainbow | `NO_CANDIDATE` |
| `WALL_NAVIGATION` | 6,318 quotient min-conflict moves, 5,453 accepted | duplicate residual 619,869; 47 constraints rainbow | `NO_CANDIDATE` |

The final wall arm imposed the current Hoffman-equality theorem signal: in any
remaining `(k+1)`-colouring with even `k` and prime `k+1`, every `k`-set must
have the same colour as its complement.  It therefore searched 92,378 paired
variables instead of 184,756 independent variables.  Under the same 30-second
budget it beat the generic arm's residual by 12,369 but did not approach a
witness.  A preliminary quadratic-edge-weight wall family, run before the
source discussion exposed complement closure, was worse (residual 645,170,
29 rainbow constraints); it is retained as an explicit failed arm design, not
substituted into the comparison table.

### Literal and database sanity

Again, the ordinary graph-Atlas gate is not the relevant historical database:
the objects are colourings of one fixed Johnson graph.  Native controls passed.

- Positive boundary `k=2`: the three perfect matchings of `K4` colour its six
  edges; direct replay checked that all four 3-sets see all three colours.
- Negative known case `k=3`: a complete DSATUR backtrack of `J(6,3)` explored
  209 search nodes and proved that no four-colouring exists, reproducing the
  upstream known-case direction.
- The `k=10` evaluator built every variable and every constraint and never
  treated a partial or sampled constraint table as a candidate.  No candidate
  existed, so independent candidate verification was not unlocked.

### Upstream, issue, commit, and source status

At the pinned current main the three relevant declarations remain
`research open`.  Merged PR
[#1428](https://github.com/google-deepmind/formal-conjectures/pull/1428) /
commit `f169c53d2a7f` introduced the module.  Closed, unmerged PRs #2548 and
#3073 concern only known Johnson-bound/finite-case variants; repository search
returned no open solution PR for the existential problem.  Formalization issue
#967 is closed because the statement was added, not because the mathematics
was resolved.  The live Erdős Problems entry remains **VERIFIABLE/open** and
states that Ma--Tang exclude `k+1` composite.  Its current discussion further
identifies a solution with a large set of Steiner systems and records the
complement-closure consequence used by the final wall arm.  Nothing from this
search is called novel.

## Zeroes and theorem signals

- **Claimable crossings/candidates:** zero.
- **Complete zero:** the exhaustive Claude `m=2` control, already a known
  theorem; it is calibration only.
- **Bounded zero:** no `Property 10` witness in any of the three 30-second
  Erdős 835 arms.  This is not a nonexistence result.
- **Status-preempted zero:** no `m=4` Claude witness in these arms, despite the
  revised source's known construction.  It is excluded from the open-target
  denominator.
- **Theorem signals:** (i) Claude residual-one states isolate the missing move
  as a global/multi-factor cycle splice; (ii) Erdős 835 complement closure
  produces a literal half-size quotient and improves the generic residual;
  (iii) each colour class in a putative solution must meet every 11-set's
  deletion clique exactly once, so the next exact wall is a large-set/Steiner
  exact-cover formulation, not another unconstrained colour hash.

## Method improvements from the lane

1. **Source revision and open-PR checks belong before arm spend, not merely
   before a novelty claim.** Main's `research open` tag lagged the cited source,
   and #4935 had already documented the correction.  The triplet would have
   been skipped had the open-PR/source gate preceded execution.
2. **Do not equate the machine stratum with bounded resolvability.** Most live
   structural/property rows have infinite or asymptotic outer shape.  They
   require a finite-obstruction theorem before a catalogue/generic/wall
   experiment is meaningful.
3. **The wall arm must ingest known necessary equalities.** Complement pairing
   was more useful than a superficially target-shaped quadratic hash family.
   Future Erdős 835 work should freeze a complement-quotiented large-Steiner-
   system exact-cover/SAT model and compare all arms on the same prime case.
4. **Residual definitions must remain literal and auditable.** Both searches
   counted exact unsatisfied structure (extra directed cycles; missing colours
   per deletion clique), while state hashes and native positive/negative
   controls prevented a low proxy score from being mistaken for a candidate.

No file under `lean/` was modified; in particular,
`lean/SnakeInTheBoxNine191.lean` was not touched.  No issue, PR, comment,
commit, push, release, or other outward action was performed.
