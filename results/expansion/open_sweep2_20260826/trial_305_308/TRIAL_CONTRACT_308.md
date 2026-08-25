# TRIAL CONTRACT — WOWII 308 wall-navigation trial (open_sweep2, 2026-08-26)

**Frozen before any development-family member is constructed or evaluated.**
Method: METHOD.md v1.0 phases 0A–7 + METHOD_V1_7.md R1 (step-aware sign check).
Status: `DEVELOPMENT` (WOWII corpus is this campaign's development set).
Shared apparatus with the WOWII 305 contract in this directory; readings,
tie-break discipline, and stop rules below are 308-specific where noted.

## 1. Target and source reading

- **Target:** WOWII **308** — page marker `O` (open), note dated Mar. 1, 2007;
  transcription in `data/wowii-conjectures.json` id 308:
  > If G is a simple connected graph such that n(G) > 2, then
  > γ_t(G) ≤ (1/2)·[maxine(G) + minimum of |N_bar(G)(e)|]
- **Hypotheses (frozen):** G simple, connected, n(G) > 2.
- **Residual (exact):** per reading,
  `R(G) = ½[maxine(G) + min_e |N̄(e)|] − γ_t(G)` in exact `Fraction`s.
  Hold ⟺ R ≥ 0; witness has R < 0.
- **Neighborhood reading table:** identical four readings as the 305 contract
  §1 (RDG-B PRIMARY "comp-edge incl" 309-locked: e ∈ E(bar G), open union in
  bar G incl endpoints, |N̄(e)| = n − codeg_G(u,v); RDG-A excl variant;
  RDG-C e ∈ E(G) with N in bar G; RDG-D N_G(nonedge)), except 308 takes the
  **MINIMUM** over e. Undefined-term rule as in 305 (complete graphs
  NOT_APPLICABLE under RDG-A/B/D).
- **maxine semantics (FROZEN):** maxine(G) = |S| where S is built by: while the
  current graph contains an edge, select a vertex of maximum current degree,
  add it to S, and delete it together with all its neighbors; when the current
  graph is discrete (edgeless), add all remaining vertices to S. This is the
  only parse of DeLaViña's definition ("order of the largest independent set
  that one gets from the greedy algorithm that proceeds by removing a vertex of
  maximum degree until the subgraph is discrete") that always yields an
  independent set.
- **TIE-BREAK DISCIPLINE (mandatory, survey-flagged risk).** maxine is NOT an
  isomorphism invariant: it depends on which maximum-degree vertex is chosen.
  Therefore for every graph row we compute `maxmin(G)` = smallest and
  `maxmax(G)` = largest value reachable by ANY deterministic tie-break rule
  (exhaustive branching over distinct closed-neighborhood deletions, memoized),
  and the full reachable value set. Verdicts per reading:
  - HOLD requires R ≥ 0 with maxine = `maxmin` (holds under EVERY rule);
  - VIOLATION requires R < 0 with maxine = `maxmax` (robust to every rule);
  - otherwise the row is `AMBIGUOUS_TIEBREAK` and is reported, never scored as
    hold or kill. Every reported row states which tie-break quantifier was used.

## 2. Resolution card (Phase 0A)

```json
{
  "logical_class": "FINITE_UNIVERSAL",
  "target_negation": "there exists one finite connected graph on > 2 vertices with R < 0 under a fixed tie-break resolution of maxine",
  "negation_certificate": "labelled adjacency + exact gamma_t witness + exact min_e |N_bar(e)| certificate edge + reachable-maxine-set enumeration proving the tie-break quantifier",
  "finite_witness_suffices": true,
  "exact_residual": "R = (1/2)*(maxine + min_e |N_bar(e)|) - gamma_t",
  "answer_placeholder": false,
  "eventual_quantifier": false,
  "global_constant_quantifier": false,
  "unbounded_auxiliary_search": false
}
```

## 3. Baselines, theorem shadows, pre-stated predictions (Phases 3–4, frozen)

- **Sibling disambiguation:** as in the 305 contract §3 — proved sibling 306
  shares the min-of-|N̄(e)| term and survives small controls ONLY under RDG-B,
  which is therefore PRIMARY here too; RDG-A/C/D are executed for the record.
- **Pre-stated orientation prediction (recorded BEFORE any evaluation):** hand
  arithmetic gives diamond K₄−e: γ_t = 2, maxine = 1 (tie-invariant: every run
  leaves exactly one vertex), min_e|N̄(e)| = 0/0/2/2 under RDG-A/B-excl?/C/D —
  precisely: RDG-B min term = 2 over the single complement edge {1,2} ⇒
  R = ½(1+2) − 2 = −½ < 0; RDG-A/C give min 0 ⇒ R = −3/2; RDG-D gives 2 ⇒
  R = −½. PREDICTION: every reading is violated by an n = 4 atlas control and
  the entry-level outcome will be STOP_CORRUPT_READING. This prediction is
  falsifiable by the gate; if instead some reading survives, the trial proceeds
  to families normally.
- **Shadow S1 (shared with 305):** verified γ_t ≤ ⅔n on the gate set ⇒ diam ≥ 3
  regime shadowed (min term can be as low as 2 but γ_t grows); live region
  diam 2 with γ_t ≤ 4 pinned against maxine ≤ α ≤ n−... (no sharp pin known:
  recorded honestly).
- **Obstruction identity candidate (testable if gate survives):** on C₅-blow-ups
  B(w): maxine reaches α = 2 (greedy on twin-dense graphs removes whole blobs);
  min_e|N̄(e)|_RDG-B = n − codeg_max where codeg_max = max blob size among
  middle blobs of nonedge pairs = max(wᵢ) ⇒ RHS = ½(2 + n − w_max) vs γ_t = 3:
  crossing needs ½(n − w_max) ∈ {½, 1} at γ_t = 3 ⇒ n − w_max ≤ 2 impossible for
  5 positive weights. Blow-up axis cannot cross.

## 4. Sign-potential table (frozen prediction, conditional on gate survival)

| quantity | predicted motion | reason |
|---|---|---|
| maxine | tracks α from below; grows only when greedy gets trapped | hereditary-flavored greedy quantity |
| min_e\|N̄(e)\| | pinned ≥ c_min-related density floor; jumps to ~n when a distance-≥3 pair appears | complement-neighborhood of sparsest nonedge |
| net R | increase along subdivision/metric knobs; flat/equality inside dense region | both sides move together |

Frozen prediction: NO crossing on the designed grid IF any reading survives the
gate; primary expected outcome remains STOP_CORRUPT_READING (§3 prediction).

## 5. Development family (FROZEN grid — identical to 305's, shared rows)

Same F1–F6 arms as TRIAL_CONTRACT_305.md §5 (unequal C₅ blow-ups wᵢ ∈ {1,2,3};
T(k) k=5..9; CP(k) k=2..7; ten complete multipartites; exhaustive connected
n = 8 extension; subdivided-C₅ control arm ℓ ∈ {1,2,3}). Rows are computed for
every reading that survives the 308 gate, with maxmin/maxmax/reachable-set
columns. Nothing else may be added without a new contract.

## 6. Bounds, budgets, stop rules

- Per-member cap **60 s CPU** signal-enforced; F5 aggregate cap 900 s CPU.
  maxine reachable-set enumeration memoized; a state space exceeding the cap
  ⇒ bracket + incomplete marker for that member.
- All arithmetic exact (`Fraction`); no spectral quantities (guard vacuous).
- **γ_t two independent engines** (ascending-k enumeration + ILP) as in 305;
  **maxime two independent implementations** (iterative memoized DFS and a
  recursive formulation) cross-checked on every scored row.
- **Step-aware sign check (v1.7 R1):** the residual has rounding operators on
  BOTH sides' absence — ½[·] introduces half-integer steps: runs must span
  parity changes of (maxine + min term). F1 covers n − w_max contiguous ≥ 4
  values; F2/F3 provide fixed-term controls. Constant-residual neighbours alone
  are never a stop.
- **Stop rules:**
  1. Exact R < 0 (with maxmax) on a gate-surviving reading after two-engine
     replay ⇒ `KILL_CANDIDATE` review or discard.
  2. All members hold (with maxmin) after full step-sampled run ⇒
     `HOLD_BOUNDED`.
  3. A reading violated by ANY applicable gate control ⇒ READING rejected as
     mis-transcription (witness recorded, move on). ALL readings dead ⇒ entry
     verdict `STOP_CORRUPT_READING`.
  4. Budget exhausted ⇒ partial `HOLD_BOUNDED`, reported as such.

## 7. Database-sanity gate

Identical to 305 §7: all connected Graph Atlas graphs n ≤ 7 plus C₅–C₉, P₇,
Petersen, K₃,₃, K₇, stars K_{1,n} n=3..8, K_{n,n} n=2..6.

## 8. What counts as CROSS

Exact Fraction R < 0 under a gate-surviving reading with maxine = maxmax
(tie-break-robust), connected n > 2, reproduced by two independent code paths,
gate replayed, labelled adjacency saved. Ties never kill. AMBIGUOUS_TIEBREAK
rows are disclosed and never promoted.

## 9. Pre-freeze disclosure

As in 305 §9: selection/slacks/precedent predate this contract; orientation
hand-arithmetic (diamond prediction, C₅-blow-up identity) predates it and is
disclosed as analysis; zero development-family constructions or evaluations
occurred before this freeze.
