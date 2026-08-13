# Invariant-Wall Navigation: Development Method v0.8

Programme-level execution order and maturity criteria are maintained in
[`OVERARCHING_PLAN.md`](OVERARCHING_PLAN.md). This file is the detailed,
versioned protocol that governs that plan.

**Status:** committed development protocol, 2026-08-13

**Scope:** existing published finite-graph conjectures from collections already
represented in
[`google-deepmind/formal-conjectures`](https://github.com/google-deepmind/formal-conjectures).
For this campaign that includes Written on the Wall II, but **not** Written on
the Wall I or Graph Brain. This does not include generating new conjectures or
introducing a new upstream corpus.

**Not yet:** a preregistered held-out evaluation or a general-purpose discovery engine

## Research claim under development

This project tests a narrow, falsifiable claim:

> Exact equality and near-equality data can be used prospectively to design
> counterexample families for machine-generated graph-invariant conjectures.

The method is not "try many graphs." It treats a tight graph as a local map of
an inequality, identifies the invariant relation preventing a crossing, and
chooses a graph transformation predicted to break that relation while
preserving the rest of the extremal structure.

The current evidence is developmental, not held out:

1. `C5[K_m]` exposed a rounding cliff behind WOWII 63/64/85 and a correlated
   historical failure cluster.
2. Its `L_s+b` equality geometry exposed the obstruction `alpha=lambda_max`;
   triangular graphs separated those quantities and crossed the formalized
   square-degree reading of WOWII 181.
3. Subtracting the proved WOWII 173 baseline showed that a diameter-two attack
   on 176/182--185 was impossible; leaving diameter two with the barbell family
   `D_L` crossed WOWII 176 and adjacent 172.
4. In a different invariant cluster, a nonuniform `P7` clique blow-up separated
   center geometry from the Caro--Wei correction and crossed WOWII 430a.
5. Graph Brain upper-081 transferred from the carrier to elementary windmill
   families, demonstrating that the useful geometry is not confined to one
   historical WoW page.

These examples justify developing a reproducible heuristic. They do not yet
establish a calibrated success rate. Targets discussed or ranked before this
document are a **development set** and can refine the method, but cannot later
be counted as held-out evidence.

## Unit of analysis: the residual wall

Write every admissible inequality in a signed residual form

```text
R(G) = LHS(G) - RHS(G),
```

or reverse the sign once and record the convention. A conjecture holds when
`R(G) >= 0`; a counterexample has `R(G) < 0`.

For a candidate family `F(theta)`, the working record must contain:

- the exact hypotheses and source reading;
- `R(F(theta))`, exactly where feasible;
- the zero-slack and least-positive-slack parameter values;
- every known theorem that lower-bounds `R` or a component of it;
- invariant identities holding throughout the family;
- a predicted transformation that can decrease `R`;
- a hard search and optimization budget;
- every tested result, including holds, timeouts, corrupt readings, and old
  counterexamples.

This turns "tightness" into a concrete object rather than a visual analogy.

## Method v0.3

### Phase 0 — Freeze the target and its provenance

Before construction work:

1. Record the upstream repository commit, file, declaration, source URL, and
   current `category`.
2. Confirm no existing issue, PR, formal proof, accepted resolution, project
   commit, tag, or release already covers the target.
3. Recover the historical statement when the formalization is not itself the
   sole target.
4. Enumerate every plausible reading before evaluating any preferred witness.
5. Mark the target as one of:
   - `UNAMBIGUOUS`;
   - `FORMALIZED_READING` (the Lean statement is clear but historical intent is
     unsettled);
   - `MULTI_READING`;
   - `UNUSABLE_SOURCE`.
6. If any hypothesis is strict, quantified over subsets, or defined by an
   extremum, freeze the exact witness semantics for both truth and failure.
   A scalar minimum or Boolean flag is insufficient: a premise-false stop must
   carry a replayable subset/vertex/edge witness, its eligibility calculation,
   the induced quantity, and the literal strict comparison.

No reading may be changed after a candidate is found without preserving the
old result and explaining the change in the log.

### Phase 1 — Database-sanity gate

Every reading must first survive the historical-control set:

- all connected Graph Atlas graphs on at most seven vertices;
- `C5`--`C9`, `P7`, Petersen, `K3,3`, `K7`, stars, and complete bipartite
  controls;
- any named sharpness or refutation graphs stated near the source conjecture.

A reading contradicted by an applicable control that the conjecturer could
reasonably have known is presumed corrupt or mistranscribed, not newly false.
It is logged and rejected unless primary-source evidence resolves the conflict.

For a statement with conditional clauses, each clause is gated separately on
the controls satisfying that clause. A passing default branch cannot rescue a
corrupt exceptional branch, as the source-faithful leaf clause of WOWII 434c
demonstrates.

All arithmetic is exact where possible. Spectral comparisons use the existing
`1e-6` guard and are never promoted from a smaller numerical gap. Every ILP or
CBC call is capped at 60 seconds; timeout bounds are recorded, not guessed.

### Phase 2 — Find and classify walls

Evaluate the fixed development arsenal and structured family table. Rank a
target only when at least one of these signals exists:

1. exact equality on several nonisomorphic graphs or family parameters;
2. a one-unit or one-rounding-step margin;
3. a residual whose terms have known closed forms on a structured family;
4. a neighboring conjecture sharing all but one controlling invariant;
5. a known theorem explaining most, but not all, of the residual.

Correlated statements sharing the same residual wall are one **cluster**, not
independent methodological successes.

### Phase 3 — Subtract theorem baselines

Before searching harder, write

```text
R(G) = T(G) + C(G),
```

where `T(G) >= 0` is a known theorem when possible. Then classify:

- `THEOREM_SHADOW`: the proposed wall reduces to an established theorem in the
  declared regime;
- `THEOREM_SIGNAL`: computation and reduction isolate a plausible missing
  lemma, but no proof is known;
- `FREE_RESIDUAL`: no baseline blocks the observed direction.

The WOWII 173 episode is the model: diameter-two 176/182--185 collapse to the
proved `L_s+b >= n+1` baseline. The correct action was to prune that search
space, then examine the residual terms outside diameter two.

### Phase 4 — Identify the obstruction identity

For each tight family, state why the current parameter cannot cross. Examples:

- `alpha=lambda_max` on a carrier family;
- diameter two forces `G^2=K_n` and collapses several corrections;
- regularity makes the center or maximum-degree set equal to all vertices;
- uniform blow-up weights make two correction terms scale together;
- a floor or ceiling remains on the safe side of an integer threshold.

An obstruction must be an equation, inequality, implication, or monotonicity
statement that is testable on the whole family. "This family did not work" is
not an obstruction.

### Phase 5 — Choose a separating transformation

Use a transformation-effect catalogue rather than unconstrained graph search:

| transformation | intended invariant effect | demonstrated development example |
|---|---|---|
| uniform clique blow-up | grow density/distance terms while pinning hereditary induced invariants | `C5[K_m]` cliff |
| nonuniform clique blow-up | separate center/eccentricity and weighted-degree corrections | `P7` blow-up for 430a |
| line graph | create small clique independence with larger ordinary independence | `T(n)=L(K_n)` for 181/191 |
| complement | exchange dense regular geometry for sparse or triangle-free structure | WoW I 889 |
| subdivision / barbell | grow metric separation while preserving small cyclic cores | `D_L` for 176/172 |
| windmill / shared-clique sum | separate independence from connectivity gaps | Graph Brain upper-081 |
| bounded edge surgery | move one residual term while measuring damage to neighboring walls | development target |

Before running a transformation, record a directional prediction for every
term in `R`: increase, decrease, pinned, or unknown. A successful family counts
as **prospectively designed** only when the predicted controlling separation
was written before the violating instance was evaluated.

The prediction itself is an auditable outcome. If every tested coordinate
matches a frozen closed form, record `PREDICTION_CONFIRMED` even when the family
moves safely away from the wall. If the prescribed construction is exactly
infeasible, record `NO_APPLICABLE_CANDIDATES`; do not substitute another group,
sheet count, gadget, or parameter in the same trial. A transformation that
enters a class where the target is already proved stops as
`KNOWN_PROOF_DOMAIN` before expensive invariant evaluation.

### Phase 6 — Bounded construction search

Search the smallest parameter region capable of testing the prediction:

- quotient graphs before expanded blow-ups;
- orbit representatives before labelled edge edits;
- exact rational feasibility before integer scaling;
- incremental outputs after every 15--20 targets or every completed family;
- one target cluster per report;
- stop at the declared family/parameter/CPU limit.

Every exploratory subprocess, including scratch one-liners used to test a
lemma, must be launched under an explicit wall-clock timeout. A parent agent's
turn boundary is not a timeout: before checkpointing or delegating, inspect for
live child processes and terminate any process outside the declared bound. No
output from an over-cap process may enter the evidence ledger.

The objective is not the smallest graph at this phase. It is a transparent
structural witness. Minimality is a separate bounded follow-up.

Before optimizing transformation parameters, derive any quotient-level or
family-level necessary condition for a negative residual. If that condition is
never negative on the declared quotient universe, stop: larger weights cannot
help. The complete 422b trial is the model—all quotient/set residuals were
nonnegative, so no positive clique weights of any expanded order could cross.

When a bounded local surgery repeatedly reaches equality but never crosses,
record which parameter is pinned by the construction. Do not silently add more
edge edits. The barbell Wave 1 trial showed that endpoint clique size and two
local edge toggles are pinning coordinates for 169/174/180/182; a further trial
must change the quotient or core geometry.

Every completed frozen family is closed. A follow-up may use its learned
identity only through a separately committed addendum or contract naming a
genuinely different transformation. Post-result parameter extension, solver
replacement that changes semantics, or an added mutation is retuning and may
not be folded into the original verdict.

Implementation semantics are independently audited against the literal
contract. If they differ, preserve the original rows and classify them
`PROTOCOL_DEVIATION`; then run a separately identified literal replay if still
within the frozen budget. A no-crossing result does not cure a protocol error.

### Phase 6A — Serialize labelled structure, not merely an abstract graph

Graph6 identifies a graph serialization; it does not certify that designated
vertex numbers still denote the frozen roots, ports, fibers, bipartition
sides, or witness coordinates. Whenever a construction depends on labelled
roles, every row must therefore store:

- the full labelled edge list (or an equivalent adjacency table);
- an explicit role map for roots, ports, fibers, parts, and attachments;
- graph6 as an abstract-graph checksum, not the sole labelled record;
- every witness in the same labelled coordinate system; and
- a digest of the combined labelled record.

Replay must either reconstruct the exact labelled graph, or exhibit an
explicit isomorphism and transport every role and witness through it before
checking the claim. Abstract isomorphism alone cannot validate a labelled
distance or attachment statement. The WOWII 61 cube-chain audit is the model:
its conditional mathematics survived, but a graph6/root-port mismatch
overrode the apparent hold with `PROTOCOL_DEVIATION`.

### Phase 7 — Candidate verification

No apparent crossing is a result until it passes all gates:

1. **Hypotheses:** replay every graph hypothesis exactly. Strict or extremal
   premises require a concrete satisfying or falsifying witness; equality at a
   strict boundary is premise failure, not a hold.
2. **All readings:** compute a verdict table for every frozen interpretation.
3. **Database sanity:** rerun the accepted reading on all controls.
4. **Independent recomputation:** use a second implementation or a structural
   proof, not the discovery helper.
5. **Exact witness:** save adjacency/graph6, parameters, and term-by-term values.
6. **Family explanation:** derive closed forms or prove enough inequalities to
   explain why the witness is not an isolated numerical accident.
7. **Novelty:** search the statement, conjecture number, witness family, known
   refutations, upstream issues, and PRs.
8. **Status:** distinguish new, retro, erratum, metadata defect, ambiguous, and
   already resolved.

### Phase 7A — Proof extraction after a bounded hold

A bounded hold becomes a theorem lane only when the completed trial isolates a
precise statement strictly narrower than the original conjecture. Before any
new computation, write a **lemma ladder**:

1. the already-proved baseline;
2. the exact residual identity;
3. the smallest remaining structural proposition;
4. the source hypotheses actually used;
5. a proof route and the first step at which it can fail.

The lane then alternates paper proof and countermodel checks against each
lemma, not against the original conjecture wholesale. A failed lemma is saved
with its smallest exact counterexample and replaced explicitly. A surviving
lemma receives a bounded independent audit only after its proof idea is
written. No search bound may be enlarged merely because a proof attempt is
hard.

The 438b result is the model: a proposed low-degree-layer crossing was replaced
by an edge-partition lemma valid for every vertex subset, and the stronger
theorem was then proved in Lean. The output is a theorem, not a negative-search
statistic.

### Phase 8 — Formal certification and project release

All public writes follow [`UPSTREAM_PROTOCOL.md`](UPSTREAM_PROTOCOL.md). Despite
the historical filename, it now governs releases in this repository: do not
create a tag or release until its committed preflight and release-lock records
pass. New `formal-conjectures` issues and PRs are out of scope; that repository
is read-only for selection and duplicate checks. Existing campaign PRs may be
repaired only in response to CI or review.

For each gate-surviving new disproof:

1. Commit the source audit and exact verifier to this repository.
2. Write a no-`sorry` Lean certificate here and compile with warnings as errors.
3. Audit `#print axioms`; reject `sorryAx` and project-specific axioms.
4. Commit a release checklist recording novelty searches, full artifact SHAs,
   verifier/build results, trust assumptions, and the proposed tag/title.
5. Lock an annotated tag to the audited preflight snapshot and publish one
   non-draft project release for one problem, without generated binary assets.
6. Read back the tag, release body, target, and every immutable link.
7. Keep priority caveats and AI-assistance disclosure in the release body.
8. Never describe a formalized-reading disproof as settling ambiguous
   historical intent.

Every durable stage receives a sequential commit. Empty commits may retrigger a
confirmed transient CI failure, but they are never evidence of mathematical
progress.

## Outcome ledger

Every attempted target receives exactly one primary outcome:

| outcome | meaning |
|---|---|
| `GATE_FAIL` | a frozen calibration, fixture, control, or constructor assertion failed; the family remains locked |
| `NEW_UNAMBIGUOUS_DISPROOF` | all source readings agree and novelty survives |
| `NEW_FORMALIZED_READING_DISPROOF` | the Lean/gate-preferred reading is false; historical intent remains caveated |
| `RETRO_COUNTEREXAMPLE` | witness is new to this campaign but the conjecture was already false |
| `THEOREM_SHADOW` | a known theorem makes the apparent wall uncrossable in the tested regime |
| `THEOREM_SIGNAL` | a sharply reduced possible theorem with negative computational evidence |
| `PREDICTION_CONFIRMED` | every tested coordinate matches a frozen closed-form prediction |
| `NO_APPLICABLE_CANDIDATES` | the exact prescribed transformation has no admissible output |
| `NO_TARGET_RAISING_CANDIDATES` | admissible outputs exist, but none moves the preregistered target coordinate |
| `KNOWN_PROOF_DOMAIN` | every admissible output lies in a class where the target is already proved |
| `NEUTRAL_CORRIDOR` | exact transformations produce new tight objects but the frozen frontier closes |
| `PROTOCOL_DEVIATION` | implementation and frozen contract differ; rows are preserved but excluded |
| `PREMISE_FALSE_STRICT` | an exact witness falsifies a strict premise, so the conjectured conclusion is not evaluated |
| `HOLD_BOUNDED` | all declared tests hold; no truth claim beyond the bounds |
| `TIMEOUT_BRACKET` | exact optimization did not finish; certified bounds retained |
| `CORRUPT_OR_ERRATUM` | source/database gate rejects the printed statement |
| `AMBIGUOUS` | readings produce materially different status |
| `NOT_APPLICABLE` | the fixed family does not satisfy the hypotheses |
| `NEW_PROOF` | the source conjecture is proved, with a checkable argument |
| `STRONGER_THEOREM` | a proved statement strictly subsumes the source conjecture |

Counts in public summaries are separated into direct carrier kills, spawned
families, retro-witnesses, theorem shadows/signals, and interpretation-dependent
results. Several formulas crossed by one family are reported as one method
trial with multiple consequences.

## Development-set program: formal-conjectures only

Until a future protocol is frozen and tagged for a held-out corpus, work stays
inside already-published statements from collections already represented in
`formal-conjectures`. Source recovery does not by itself make an unrelated
corpus eligible. WoW I and Graph Brain results remain internal to `c5-k4` and
must not be submitted upstream. This keeps the public research trail legible
while Method v0.8 is refined.

### Wave A — known tight walls

1. **Independent-domination cluster:** start with WOWII 422b, then 430c and
   434c. Reuse the quotient-weight view that produced 430a; record why each
   correction term can or cannot be separated.
2. **Barbell neighborhood:** bounded two-edge orbit surgery and endpoint clique
   substitutions around 169/174/180/182. Treat shared consequences as one
   cluster and stop at the declared orbit/parameter limits.
3. **WOWII 183 theory lane:** seek the remaining extremal lemma after subtracting
   173. This lane may end in a theorem signal or proof rather than a disproof.

### Wave B — current upstream graph declarations

Refresh the exact `@[category research open]` finite-graph manifest from the
current upstream commit. Rank only concretely falsifiable universal statements
whose invariants intersect the transformation catalogue. Preserve the prior
77-declaration sweep as a baseline, including its zeroes.

### Iteration rule

After each completed cluster, append a method changelog entry containing:

- prediction;
- search bounds and compute;
- outcome;
- failed assumptions;
- transformation-table update;
- whether the change was learned before or after seeing the result.

Changes may improve the development method, but the eventual held-out protocol
must be frozen in advance and cannot inherit post-result choices silently.

## Future held-out evaluation (not started)

The eventual evaluation will commit, before any search:

- an untouched machine-generated conjecture manifest;
- eligibility and stratification rules;
- fixed transformation library and ranking score;
- equal compute budgets for arsenal-only, generic-search, and wall-navigation
  baselines;
- metrics including clusters crossed, counterexamples per CPU-hour, residual
  improvement, rejected readings, theorem shadows, ambiguities, timeouts, and
  formalization cost;
- complete publication of successes and zeroes.

No target already inspected, discussed, ranked, or searched in this repository
will be counted as held out.

## Method changelog

### v0.8 — 2026-08-13

- Records the first post-v0.7 round as **zero crossings across nine frozen
  decisions**: five clean bounded holds and four strict stops. The holds are
  the WOWII 40 internal matching and shared-endpoint star families, the WOWII
  141 Whitney switch, and the Reed hard-claw and singleton-edge-deletion
  trials. The stops are the WOWII 61 sparse-bead coordinate mismatch, the
  WOWII 61 cube-chain labelled-protocol deviation, the WOWII 141 two-lift
  family with no target-raising output, and the Erdős 128 Mycielski graph with
  an explicitly false strict premise. Conditional cube-chain rows are not
  counted as a hold, and analytic corollaries are not counted as extra trials.
- Separates applicability outcomes that earlier summaries could blur:
  `NO_APPLICABLE_CANDIDATES`, `NO_TARGET_RAISING_CANDIDATES`,
  `PREMISE_FALSE_STRICT`, and `PROTOCOL_DEVIATION` are distinct from
  `HOLD_BOUNDED`. A protocol defect overrides a numerically safe downstream
  table; a false strict premise stops before the conclusion.
- Promotes **radius-one exhaustion followed by theorem-shadow closure** to a
  preferred stopping pattern. For the 18-vertex Reed graph, all 89 singleton
  edge deletions were exactly eight-colorable. Colorability monotonicity then
  proves that every nonempty edge-deletion set is eight-colorable, closing the
  whole pruning operation class without adaptively testing larger deletion
  menus. The general implication is certified in
  `lean/ReedEdgeDeletionClosure.lean`.
- Requires role-preserving labelled serialization. Graph6 alone is an
  abstract-graph artifact and cannot certify a root-port distance, fiber,
  bipartition, or sparse-labelled witness. Store the labelled edge list and
  role map; otherwise transport all roles and witnesses through an explicit
  isomorphism. The cube-chain mismatch is retained as
  `INCONCLUSIVE_PROTOCOL_DEVIATION` even though its actual labelled family was
  independently safe.
- Requires explicit falsifying witnesses for strict premises. In the Erdős
  128 Mycielski lane, the shadow set is eligible and independent, so its zero
  induced-edge count falsifies the strict density premise. Lean generalizes
  that witness to every classical Mycielski graph; this closes the
  transformation direction without saying anything about the conjecture's
  truth on graphs satisfying the premise.
- Treats transformation-family closure as a mathematical product, not a
  license to retune. The WOWII 40 internal-edge cone is theorem-shadowed, every
  two-lift of `K3,3-e` retains a 4-cycle by an exact voltage-parity obstruction,
  every nonempty pruning of the Reed seed loses the ninth color, and every
  classical Mycielski graph fails the selected strict premise. A new trial must
  leave the closed operation class and freeze a new coordinate law.
- Reaffirms that a computed crossing is only a **candidate** until source,
  status, duplicate/priority, exact-replay, and full novelty gates pass, then a
  local no-`sorry`, warnings-as-errors Lean certificate and axiom audit pass.
  Only that complete record can enter the one-problem release preflight. This
  round produced no release candidate and authorized no public action.

### v0.7 — 2026-08-13

- Promotes preregistered coordinate prediction to a first-class outcome. The
  Reed complete-join trial predicted and then verified exact slack `2m` on all
  48 outputs.
- Adds `NO_APPLICABLE_CANDIDATES` and `KNOWN_PROOF_DOMAIN` stops. The WOWII 141
  cyclic, `S3`, and `S4` cover systems were exactly infeasible; two Reed gadget
  lanes stopped inside proved claw-free classes before transformed profiling.
- Adds `NEUTRAL_CORRIDOR`: the order-twelve WOWII 61 switch lane found three
  new tight realizations, then exhausted its literal frontier without raising
  diameter.
- Requires literal-contract replay after any implementation mismatch. The
  initial #61 corridor implementation used global-seen rather than
  retained-only deduplication and remains separately classified
  `PROTOCOL_DEVIATION` even though it found no crossing.
- Makes every frozen family terminal. A next trial needs a separately committed
  contract and a genuinely new separating operation; it cannot extend the old
  grid after seeing the result.
- Requires a theorem-domain audit before expensive profiling on major human
  conjectures. This prevented claw-free Reed gadgets from being misrepresented
  as open-domain evidence.
- Adds policy scanning for `native_decide` alongside `sorry`, `admit`, and
  custom axioms. The #133 contraction certificate was corrected to kernel
  `decide` and rebuilt warning-clean under its 60-second cap.

### v0.6 — 2026-08-13

- Requires each prospective trial to compile a canonical machine-readable
  contract before evaluation. Source identity, normalized statement,
  applicability, residual sign, controls, fixtures, solvers, caps, family,
  grid, and stop rules are hashed together.
- Adds hand-derived semantic microfixtures and 40-second feasibility sentinels
  before the full gate. Two implementations agreeing is insufficient if both
  contradict a frozen calibration or cannot execute the declared controls with
  headroom below the 55/60-second caps.
- Requires an exact pre-grid obstruction check and an independently audited,
  chronological unlock attestation. Grid constructors remain unavailable
  until every calibration, witness, baseline, gate row, and replay passes.
- Preserves protocol-violating rows append-only but excludes them from every
  mathematical outcome. See
  [`method_v06_gate_contract.md`](results/expansion/method_v06_gate_contract.md).
- Records that all 14 current open WOWII modules in `formal-conjectures` were
  already evaluated, so the genuinely held-out queue is empty until a future
  upstream-manifest addition.

### v0.5 — 2026-08-13

- Added the prospective WOWII 305 trial and then stopped it when post-run audit
  found its endpoint-excluding calibration contradicted the frozen
  endpoint-inclusive reading. The accidentally unlocked grid is classified
  `EXCLUDED_PROTOCOL_VIOLATION`, not `HOLD_BOUNDED`.
- Advanced proof extraction: closed the corrected cubic C4-free specialization
  of WOWII 133 in Lean, formalized the `gamma_c>=3` and `gamma_c>=4`
  distance-three tiers behind WOWII 183, and carried explicit graphical
  realizability into the WOWII 61 residue-transfer lane.

### v0.4 — 2026-08-12

- Replaced new upstream issues/PRs with one-problem versioned releases in
  `Kuberwastaken/c5-k4`.
- Expanded duplicate detection to this project's own commits, tags, and
  releases after WOWII 64 exposed that an upstream-filename-only check can
  duplicate already completed campaign work.
- Required annotated tags locked to audited commits, GitHub readback, and
  HTTP-200 verification of every immutable artifact link.
- Existing upstream PRs are maintenance-only; `formal-conjectures` remains the
  read-only development corpus.
- Extended the 60-second discipline to scratch/exploratory subprocesses after
  an orphaned exponential residue-lemma loop ran past its bound; its output was
  discarded and the process terminated.

### v0.3 — 2026-08-12

- Added a proof-extraction phase after bounded holds. A theorem signal must now
  be converted into a precise lemma ladder before further computation.
- Required proof lanes to seek countermodels to each proposed intermediate
  lemma, preventing a plausible but false reduction from becoming narrative.
- Added `NEW_PROOF` and `STRONGER_THEOREM` outcomes after WOWII 438b was proved
  by an arbitrary-subset inequality stronger than the source statement.
- Prohibited silent search-bound expansion in theorem lanes; proof failure is
  recorded at the first broken step.
- Retained the scope correction: only collections already represented in
  `formal-conjectures` are eligible for upstream work.

### v0.2 — 2026-08-12

- Required conditional clauses to pass the database gate independently after
  WOWII 434c's source-faithful leaf exception failed on `P4`.
- Added quotient-level necessary-condition pruning after the exhaustive 422b
  trial proved that no positive clique weights over quotients through order
  nine can cross its residual wall.
- Classified persistent unit slack plus structural reduction as theorem
  evidence, not permission for an unbounded search; WOWII 183 is reduced to a
  precise diameter-three core with local independence at most three.
- Recorded pinning coordinates for failed local surgery. The barbell cluster
  can reach equality but needs a quotient-level change to cross.
- Scope correction: upstream submissions are limited to collections already
  represented in `formal-conjectures`. WoW I and Graph Brain are explicitly
  excluded even when source-recovered and formally certified. No new
  conjecture generation or new upstream corpus is admitted.

### v0.1 — 2026-08-12

- Converted the campaign's verification discipline into an eight-phase
  discovery-to-submission workflow.
- Defined the residual wall, theorem subtraction, obstruction identity, and
  transformation-effect prediction as required artifacts.
- Separated development evidence from a future preregistered evaluation.
- Restricted the immediate program to existing `formal-conjectures` targets.
- Defined conservative cluster-level counting and interpretation-dependent
  outcome labels.
