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

Discovery is the primary portfolio objective. At least half of concurrent
research lanes should normally run prospectively frozen transformation trials;
proof extraction may use the remaining lanes when it is near a meaningful
closure or produces a reusable invariant identity. A long proof ladder is not
a substitute for testing new separating transformations.

The first frozen portfolio round is complete. It produced bounded holds for
WOWII 198a, 145/146, 291, 314, 160, and 34, with zero crossings. The 314 lane
also stopped on prior art. The 145/146 trial exposed a strong theorem signal,
`tree(G) >= 2 * ecc(B(G))`, but historical status and existing upstream work
make theorem extraction there secondary to novel-disproof work. These are
published zeroes, not successes and not held-out-corpus claims.

The next round concentrates on the genuinely live-looking core after the
historical-priority gate:

1. **WOWII 19:** odd-cycle block trees, nonuniform blow-ups, and bounded edge
   surgery designed to separate induced-bipartite size from the eccentricity
   and local-independence wall;
2. **WOWII 40:** nonuniform bipartite block trees, block substitutions, and ear
   surgery designed to separate induced-forest rank from path-cover and
   induced-bipartite coordinates;
3. **WOWII 61:** two independent lanes over graphical degree sequences and
   nonisomorphic realizations, targeting the exact residual-overshoot
   obstruction rather than repeating the earlier 2-switch sample;
4. **WOWII 133:** two independent C4-free lanes, one based on alternate-handle
   surgery and one on cages, covers, lifts, and C4-safe switches.

WOWII 200 receives only a source/status audit because the historical page
already records a refutation by others; confirmation closes it as prior art
before any development-family row. Likewise, proof work on already resolved
141 and already-disproved 59 is stopped while release discovery is the active
priority.

Every lane writes its contract before evaluating its development family and
uses an append-only ledger, the database-sanity and independent-recomputation
gates, and the same 60-second process cap. These targets have been studied by
the project before, so the round is prospective only with respect to its newly
frozen transformations; it is not a held-out-corpus experiment.

That live-core round produced no release candidate. Its sharp conclusions are
retained rather than retuned: diameter-two and graph-square moves are blocked
for #19; four distinct #40 wall moves failed for explicit Hamiltonicity,
forest-growth, cloning, or co-depression reasons; all one-switch descents from
the order-eight #61 realization cliffs are absent and ordinary two-lifts move
far from equality; and two independent #133 lanes found explicit source-sized
paths in every frozen candidate. Continuing those exact moves would violate
the method's stop discipline.

The first cross-corpus equality round started from new equality data in the
current `formal-conjectures` corpus:

- Reed's finite-graph bound on odd `C5[K_m]`, using two independently frozen
  separating transformations;
- Erdős 23 on the exactly tight triangle-free complement carrier, using
  nonuniform independent-part blow-ups and triangle-free surgery;
- the newly observed order-twelve WOWII 61 realization cliff, which is outside
  the completed order-eight switch bracket;
- the residual-one Heawood wall for WOWII 133;
- a #40 cross-petal incompatibility move motivated by, but distinct from, the
  failed bouquet construction; and
- one independently ranked equality wall elsewhere in the concretely
  applicable current manifest.

The Reed and Erdős lanes concern major human conjectures and therefore receive
an especially conservative source and novelty gate. They are prospective
stress tests of the equality-navigation heuristic, not predictions that those
conjectures are false.

That round is complete with no release candidate. Its durable outcomes are:

- Reed complete joins confirmed the frozen coordinate prediction exactly on
  all 48 outputs; a second Reed lane stopped because every surgery remained in
  the proved claw-free class;
- the Erdős 23 carrier family satisfies the exact identity
  `beta_edge = min_i |A_i||A_(i+1)|`, making balance uniquely extremal among
  all 574 tested nonuniform blow-ups;
- the order-twelve #61 wall contains three neutral descendants, but its
  literal-contract switch frontier closes at depth three without increasing
  diameter; an earlier global-seen implementation is preserved separately as
  `INCONCLUSIVE_PROTOCOL_DEVIATION`;
- the #133 contraction preserves the local floor but collapses radius, while
  the #40 cross-petal construction suppresses forest growth but restores
  Hamiltonicity; and
- the frozen cyclic `Z3` lift for #141 is infeasible, independently in the
  integer model and an exact finite-field CSP.

#### Post-v0.8 audited round

The next committed round remained within current finite-graph declarations
represented in `google-deepmind/formal-conjectures`. After excluding the
original Erdős 23 v1 `PROTOCOL_DEVIATION`, it contains six protocol-valid
outcome rows and zero crossings:

| Target | Scorekeeping classification | Durable conclusion |
|---|---|---|
| Dean `k=5` two-switches | `HOLD_BOUNDED` | 7,081 depth-indexed rows, 6,951 distinct labelled graphs, and 20 isomorphism classes all contain 5- and 10-cycles; Dirac closes the whole order-ten 5-regular operation class |
| Erdős 128 canonical Hajós join | `PREMISE_FALSE_STRICT` | a certified nine-vertex, two-edge set falsifies the order-19 graph's strict density premise; the derived low-separator Lean theorem is a general witness mechanism, not a claim about every Hajós join |
| independent-domination private-leaf transfer | `HOLD_BOUNDED` | the premise survives, but `(n,D,i)=(30,10,20)` has safe slack 240; the private-leaf formula and the transformed arithmetic have separate warning-clean Lean interfaces |
| Erdős 23 Andrásfai successor | v1 `PROTOCOL_DEVIATION` excluded; v2 `HOLD_BOUNDED` | the separately frozen parameter-41 `A14[bar K5]` row has exact slack 456 and passed independent audit; the low-parameter v1 rows remain post-deviation calibration |
| Erdős 742 part transfer | `KNOWN_PROOF_DOMAIN` | the order-ten proposal lies inside Fan's proved range, so it contributes zero candidate evaluations, holds, or crossings; the `K4,6` row is excluded post-stop calibration |
| WOWII 19 equality-seed line graphs | `INCONCLUSIVE` | 39 of 49 in-scope isomorphism classes were solved exactly with no crossing and five equalities; ten exact optimizations remain unresolved, so the lane is not a hold |

The six protocol-valid rows comprise three bounded holds, one strict
premise-false stop, one known-proof-domain stop, and one inconclusive bracket.
The original Erdős 23 deviation is preserved but is not prospective evidence.
The theorem and Lean closures derived from these rows are not additional
trials: Dean Hamiltonian divisibility, the Erdős 128 low-separator
obstruction, the private-leaf independent-domination formula and arithmetic,
the Erdős 23 uniform-blow-up scaling API, and the WOWII 19 endpoint-clique
bound all have explicit honest adapter boundaries.

Two earlier v0.8 operation classes also received committed formal closure.
For WOWII 40, if `G(H)` is `K_{2,c}` with arbitrary internal right-side graph
`H`, Lean proves
`c+1 <= b(G(H)) -> c <= f(G(H))`; equivalently, the omitted right vertices
form a subsingleton vertex cover, forcing `H` to be a star plus isolates. For
WOWII 141, Lean replaces the seven-row voltage table with a Boolean parity
theorem forcing an even one among five base four-cycles. Its gauge and graph-
cover transport remain an explicit adapter boundary, so this is not described
as a complete graph-level Lean theorem.

No WoW I, Graph Brain, AutoGraphiX, TxGraffiti, uncommitted live lane, theorem
closure, or post-stop calibration enters this scorecard's denominator. Any
next transformation must receive a separate frozen contract before its first
development row.

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
  the unicyclic incidence exclusion of those saturated configurations. A
  separately frozen line-graph trial is inconclusive rather than a hold: 39
  of 49 in-scope isomorphism classes are exact and safe, while ten retain
  timeout brackets. Its reusable coordinate conclusion is nevertheless
  sharp: line-graph neighborhood independence is at most two, and an induced
  bipartite selected-edge set has seed degree at most two. Both necessities
  are warning-clean in Lean; the even-cycle converse remains outside that
  extraction.
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
  vertex counted once. The internal-surgery wall is now theorem-closed: for
  `G(H)=K_{2,c}` with arbitrary internal right-side graph `H`, the full
  invariant adapter proves `c+1<=b(G(H)) -> c<=f(G(H))`. The proof extracts a
  subsingleton vertex cover of `H`, so `H` is a star plus isolates. Further
  work must leave this internal-edge operation class.
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
  remaining substantive cycle-peak condition. Separately, the completed
  `K3,3-e` two-lift zero now has a Boolean parity theorem: every voltage triple
  makes at least one of five base four-cycles even. The labelled-base, gauge,
  and lift-to-simple-cycle adapters remain explicit, so this is an algebraic
  obstruction rather than a claimed graph-level Lean closure.
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
obligations. The post-v0.8 round adds calibration rather than a fifth crossing
case study: six protocol-valid outcomes, zero crossings, and five reusable
formal explanations spanning Hamiltonicity, low separators, private-leaf
domination, uniform blow-up scaling, and line-graph coordinates. WOWII 40's
internal-edge cone is now theorem-closed, while WOWII 141's two-lift parity
obstruction is formal at the voltage-algebra level.

## Near-term execution order

1. Preserve all protocol stops and brackets. The original Erdős 23 v1 rows
   remain excluded; Erdős 742 is stopped in a known proof domain; the ten
   unresolved WOWII 19 line-graph rows stay unknown unless a new frozen
   solver contract is justified. Preserve the independent WOWII 179 timeout
   bracket as well.
2. Do not deepen the Dean order-ten two-switch family: Dirac closes every
   5-regular graph at that order. Any new Dean trial must leave order ten and
   retain `minDegree>=5` without automatic `minDegree>=n/2` Hamiltonicity.
3. Treat low-separator composition as adverse to the Erdős 128 strict
   premise unless a new frozen operation proves an eligible-set density
   budget in advance. Do not generalize the single Hajós row to all joins.
4. Do not repeat the independent-domination single-leaf concentration move.
   Its exact formula explains the safe displacement; any continuation must
   specify how it avoids lowering `i` while changing the parity/degree side.
5. For WOWII 19 line graphs, the next operation must be newly frozen and must
   aim to raise the floor of average edge eccentricity without matching growth
   in even-linear edge rank. The five equality rows identify a wall but do not
   select a unique transformation.
6. Treat WOWII 40's internal-edge cone as closed. For WOWII 141, either
   discharge the labelled-base/gauge/lift adapters or choose a transformation
   outside ordinary two-lifts; do not count the algebraic parity theorem as a
   second prospective decision.
7. For any future negative residual, stop family adaptation and execute the
   statement, database, independent-recompute, novelty, and Lean gates in that
   order. Keep all current WOWII modules excluded from any held-out success
   count; new transformations can yield discoveries, but not retrospective
   held-out evidence.

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
