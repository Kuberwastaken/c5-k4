# Overarching research plan

**Frozen scope date:** 2026-08-13 UTC  
**Status:** active development programme  
**Detailed protocol:** [`METHOD.md`](METHOD.md)  
**Publication protocol:** [`UPSTREAM_PROTOCOL.md`](UPSTREAM_PROTOCOL.md)

## Objective

Turn the `C5[K4]` campaign from a catalogue of unusually productive witnesses
into a traceable method for navigating equality walls in machine-generated
graph conjectures:

```text
source-faithful statement
  -> exact residual and database gate
  -> tight/equality family
  -> theorem-baseline subtraction
  -> explicit obstruction identity
  -> prospectively chosen separating transformation
  -> bounded complete trial
  -> exact and formal certification, or an honest zero/theorem signal
```

The immediate research claim is deliberately narrower than a general
counterexample engine:

> Equality and near-equality structure can prospectively guide the design of
> counterexamples—and the extraction of theorem lemmas—for published
> machine-generated graph conjectures.

## Scope boundary

Development targets must be existing graph statements from collections already
represented in `google-deepmind/formal-conjectures`. In this campaign the main
historical collection is **Written on the Wall II**. DeepMind's repository does
not cover Written on the Wall I; WoW I and Graph Brain results therefore do not
enter this programme's target queue or its methodological success count.

`formal-conjectures` is read-only for new discovery publication. Existing
campaign pull requests may receive CI or review maintenance, but new results
are published, when eligible, as one-problem releases in this repository. The
method does not generate new conjectures and does not introduce a new upstream
corpus.

## Standing operating rules

1. Freeze the statement, readings, family, bounds, and stop rules before
   evaluating a prospective family.
2. Run the complete database-sanity gate before any development-family row.
3. Use exact arithmetic and explicit witnesses. Every solver, scratch search,
   and child process has a hard wall-clock cap of 60 seconds.
4. Append results incrementally under `results/expansion/`; a timeout is an
   unknown bracket, never evidence for a hold or crossing.
5. Give every durable selection, implementation, ledger, correction, proof
   bridge, and publication checkpoint its own sequential git commit and push.
6. Preserve failed lemmas and smallest countermodels. Retract errors visibly;
   do not silently rewrite the research trail.
7. Count correlated formulas as one structural cluster. Separate direct
   carrier kills, spawned families, retro-witnesses, theorem results, corrupt
   statements, and interpretation-dependent results.
8. Do not publish a counterexample until source recovery, all plausible
   readings, independent recomputation, novelty review, a warning-clean
   no-`sorry` Lean certificate, and the release lock all pass.

## Active workstreams

### A. Prospective wall crossings

Run one frozen cluster at a time. The current non-metric trial is WOWII 179,
selected in `results/expansion/method_v04_nonmetric_selection.md`. Its database
gate and fixed private-neighborhood split-clique grid may be evaluated exactly
as written; its family and bounds may not be adapted after observing results.

Every completed trial ends in one durable outcome from `METHOD.md`, including
the zeroes. A negative residual starts verification; it does not itself start
publication. A bounded hold may seed a proof lane only after an exact lemma
ladder is written.

### B. Proof extraction and formalization

Maximize reusable no-`sorry` proof components, not merely top-level theorem
counts. Active proof extraction is restricted to WOWII declarations present
in the current `formal-conjectures` checkout. Current theorem lanes are:

- **WOWII 19:** the maximum-star, endpoint-tail, mixed star--geodesic, and
  whole-graph/one-deletion certificates are formal. They cover every connected
  Graph Atlas control through order seven. In general, `b>=n-tau_odd` reduces
  the conjecture to the precise transversal charge
  `tau_odd+diameter+localMax<=n+1`; 5,516 deterministic order-8--10 controls
  satisfy that charge. The maximum-star complement proves the universal
  partial charge `tau_odd+localMax+1<=n`, hence all diameter-at-most-two
  graphs. For trees, the charge is reduced to the classical finite connected
  count `diameter+maximumDegree<=n+1`. A path-index argument proves the needed
  two/three-neighbor bound, closes that count, and proves the exact conjecture
  for every finite connected bipartite graph. A portable odd-unicyclic core
  certificate also closes its class. A conventional tree-plus-one-edge model
  now supplies the unique fundamental path and cycle carrier, and actual
  diametral/max-degree equality is classified exactly. The remaining bridge is
  the unicyclic incidence exclusion of those saturated configurations.
- **WOWII 40:** the exact deficiency coordinates and arbitrary disjoint-path
  family transfer are formal. A 17-vertex four-petal cactus refutes the
  tempting one-long-path lemma; feedback-sized short-path families and the
  full even-cycle-flower petal certificate replace it. The surviving theorem
  is block-level extraction of total linear-forest rank at least `2tau+1`.
  One shared cut vertex can now be allocated away formally and the construction
  is instantiated on a shared-center flower. Inserting a disjoint leaf-block
  path now formally advances the rank budget from `2k+1` to `2(k+1)+1`;
  feedback deletion advances exactly when restoring the selected vertex does
  not grow the maximum induced forest. These combine into a complete one-step
  transfer. Include/exclude cut states are now attained and recover the global
  optimum by `max`. For a one-vertex separation, both state formulas are now
  exact: exclude states add, while include states add with one shared cut
  vertex counted once.
- **WOWII 59:** the statement is already externally disproved. Around the only
  low-residue corner `(residue,b,f)=(3,6,4)`, Lean now proves mixed-color
  attachment, core exchange, and the exact dense `2+2/2+3/3+2/3+3`
  classification. All 32 one-outside, all 544 two-outside, and all 3,188
  three-outside rows retaining `b=6,f=4` have residue two. The three attachment
  rows obey a formal aligned-or-rotating-complement dichotomy in each color.
  Four dense rows on one color side force repetition or an aligned triple;
  each side has four types and the product has 16, so 17 vertices formally
  force a repeated full row. The sharp five-distinct-type bi-alignment theorem
  is now formal via symbolic normalization and a shallow kernel certificate;
  four explicit types prove sharpness. The aligned-five boundary, compatible
  seven-vertex extension, exact selection/complete-cover alternative, and the
  one-edge six-vertex plateau are formal. The path branch is reduced to the
  extension vertex hitting at least two outside-path vertices. Deletion-
  critical bipartite five-cards yield explicit rectangles, and the coordinate
  classifier leaves only `K3,3` and `K3,3-e`; explicit `Fin 3` transport is the
  remaining interface. A residue audit proves degree-only closure impossible.
- **WOWII 61:** exact Havel--Hakimi trajectory accounting, padded excess
  profiles, one-step residual loss, and cumulative residual coupling are
  formal. Ordinary successor prefix dominance and pointwise recursive loss
  order are both formally false at order four. The exact remaining theorem is
  that initial weak graphical dominance supplies nonnegative cumulative
  credit. The credit has an exact local update and solvency rule, and local
  funding is equivalent to `2*targetHead<=credit+2*sourceHead`, with no failure
  among 105,582,418 audited pairs through order ten. Cumulative loss is exactly
  twice cumulative eliminated-head sum, reducing the theorem to monotonicity
  of those head prefixes under graphical weak majorization. The proposed
  original-graph incident-edge extremal formula is false already on `P5`, so
  further work must use a degree-sequence-intrinsic prefix functional. The
  second head is sharply between `e-1` and `e`, with its exact endpoint
  determined by survival of a maximum beyond the decrement boundary. Prefix-
  sum saturation and descending localization close the equal-top-two case.
  Arbitrary-depth funded-trajectory induction now allows multi-unit reversals.
  The exact remaining statement is the no-residual-overshoot bridge: initial
  graphical weak prefix dominance must prevent the signed residual degree-sum
  gap from exceeding its initial value.
- **WOWII 100:** the exact current Lean `degreeL2Norm Gᶜ` declaration is proved
  for every finite nontrivial connected graph, with a direct theorem matching
  the upstream signature. Complement connectedness is unnecessary. The
  upstream prose uses a different complement-diameter reading and remains
  separated from this completed formal statement.
- **WOWII 133:** the exact C4-free reduction and low-degree classes are formal.
  In the four-regular branch, long handle contacts and the complete depth-two
  choice are discharged; depth-three contact rows are classified exactly.
  Shared-parent triangle/C4 constraints initially left 20 abstract row
  matrices. A same-row two-edge detour eliminates every multi-contact row,
  leaving ten injective singleton triples. Further progress must compare the
  patterns across alternative clean-vertex choices or use endpoint degrees.
  Choice accounting exposes nine disjoint depth-two vertices but leaves all
  ten abstract triples, locating the next constraint in the third layer.
  Third-layer capacity and shared-blocker coexistence are formal. Endpoint
  geometry removes target zero from the blocker budget; the four remaining
  targets hold at most eight thirds, while one branch supplies nine distinct
  thirds. The blocker injection and all aggregate profile eliminations are
  formal. Only the graph-level clean-handle-failure to internal-blocker splice
  remains.
- **WOWII 141:** the exact conjecture is formal unconditionally for every
  connected graph of girth at most nine. The radius-two forest contradiction,
  distance-three witness, local five-cycle chord exclusion, and complete
  second-leaf assembly close girth eight/nine beyond the earlier girth-seven
  theorem. Girth ten/eleven is the next scalable tail length.
  The third-leaf assembly, exact `maxLocal+4` arithmetic, and chordless
  distance-four prefix for that range are now formal. Global radius-three BFS
  acyclicity is reduced to a cycle-peak theorem. Canonical root-path splicing,
  closing-edge exclusion, and independence of all BFS layers through radius
  three are formal. Unique parenthood between consecutive layers is the
  remaining substantive cycle-peak condition.
- **WOWII 183:** the false singleton rooted-trunk interface has been repaired.
  Attachment selection, connected domination, component folding, aggregate
  accounting, and singleton branches are formal. Bipartite and tree components
  receive full-support witnesses automatically. Deleting a non-root leaf is a
  certified exact trunk for tree components, and a degree-sum proof now finds
  such a leaf away from every prescribed root. An explicit nested-subtype graph
  homomorphism proves ambient connectivity, so nontrivial tree components now
  integrate unconditionally. One-deletion nonbipartite trunks fail the budget
  by exactly one; the corrected two-deletion threshold and local interface are
  formal. A root-sensitive adjacent pair is explicit on every cycle of order
  at least five, and its complement is formally identified with a connected
  bipartite path. The separate triangle selector also satisfies the ordinary
  package and budget exactly; the earlier `C3` budget-obstruction diagnosis is
  retracted.
- **WOWII 438b:** maintain the completed stronger arbitrary-subset proof and
  existing upstream review lane; do not recast it as a counterexample.

Proof work is independently useful even if no new counterexample appears: it
tests whether repeated equality walls are shadows of genuine invariant
relations.

### C. Verification and releases

The release backlog is audited before selecting new public work. As of
`results/expansion/release_backlog_audit_2026-08-13.md`, it is empty: completed
unreleased disproofs are already claimed, already released, retro, corrupt,
ambiguous, or incomplete.

For a genuinely new candidate, proceed in separate commits:

1. source/status audit and exact verifier;
2. independent recomputation and saved witness;
3. no-`sorry` Lean certificate and `#print axioms` audit;
4. novelty and immutable-artifact preflight;
5. annotated locked tag and one-problem GitHub release;
6. release/tag/link readback.

No public issue or pull request is opened for a new result under the current
policy.

### D. Method iteration

After each cluster, update `METHOD.md` only with lessons supported by the
completed ledger. Record whether each lesson was known prospectively or learned
after the result. In particular, update:

- the transformation-effect catalogue;
- theorem-shadow and theorem-signal criteria;
- quotient/family pruning rules;
- formalization cost and recurring API bridges;
- failure modes in source parsing, process supervision, or novelty checks.

The README should explain the method through a few strong case studies and its
published zeroes, not optimize for a raw kill count.

## Evidence already established

The development set currently contains four qualitatively useful outcomes:

1. `C5[K_m]` exposed the rounding cliff behind WOWII 63/64/85 and a correlated
   historical failure cluster.
2. Separating `alpha=lambda_max` with triangular graphs crossed the formalized
   square-degree reading of WOWII 181.
3. Leaving the diameter-two theorem wall with barbell graphs crossed WOWII 176
   and adjacent 172.
4. Nonuniform `P7` clique blow-ups separated center geometry from the
   Caro--Wei correction and crossed WOWII 430a in another invariant cluster.

The zeroes and theorem lanes are part of the evidence: 422b was pruned at the
quotient level, 184/185 held on their frozen grid, 438b became a stronger
theorem, and 133/183 have produced successively narrower formal or structural
obligations.

## Near-term execution order

1. Preserve the strict `TIMEOUT_BRACKET` stop on WOWII 179; do not reopen its
   unevaluated grid without a newly frozen protocol.
2. Finish WOWII 19's center and consecutive-endpoint residues after the
   distance-two off-path route elimination.
3. Extend WOWII 40's exclude-dominant recursive leaf theorem through the
   include-dominant branch and then a block-tree induction; do not revive the
   refuted one-long-path strategy.
4. Close WOWII 133's final clean-handle-failure to internal-blocker splice.
5. Prove WOWII 141's unique-parent condition and feed it into cycle peak.
6. Feed WOWII 183's now-closed odd-cycle package, including the corrected
   triangle selector, into the component assembly.
7. Prove WOWII 61's no-residual-overshoot bridge via cumulative credit, never
   through ordinary successor prefix dominance or pointwise loss order, both
   formally false.
8. Keep Method v0.6's prospective queue empty until a genuinely new open
   WOWII module enters `formal-conjectures`; all 14 current modules were
   already evaluated and cannot be retrospectively relabeled held out.

Long computation and narrow proof experiments should be delegated to bounded
agents. The primary lane validates artifacts, catches scope or trust errors,
and integrates one logical checkpoint at a time.

## Maturity milestone

The development method becomes ready for a genuinely held-out experiment only
after it has:

- a stable target-ranking rule and transformation library;
- multiple prospective successes in distinct invariant clusters;
- complete ledgers for failures, ambiguities, theorem shadows, and compute;
- repeatable exact-verification and Lean-certificate templates; and
- no unresolved publication or provenance ambiguity in its case studies.

Only then may a new untouched manifest and equal baseline budgets be frozen.
Nothing already discussed, ranked, or searched in this repository can be
retrospectively labelled held out.

## Completion condition

This programme is not complete when a headline counterexample is found. It is
complete only when the method, full developmental evidence, formal artifacts,
negative results, and a prospectively frozen held-out evaluation can be audited
from the git history without relying on private context.
