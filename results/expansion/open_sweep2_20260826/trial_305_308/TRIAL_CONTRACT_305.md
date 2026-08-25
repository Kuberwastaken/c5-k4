# TRIAL CONTRACT — WOWII 305 wall-navigation trial (open_sweep2, 2026-08-26)

**Frozen before any development-family member is constructed or evaluated.**
Method: METHOD.md v1.0 phases 0A–7 + METHOD_V1_7.md R1 (step-aware sign check).
Status: `DEVELOPMENT` (WOWII corpus is this campaign's development set).
Shared apparatus with the WOWII 308 contract in this directory; the two
entries are evaluated under separately frozen readings and stop rules.

## 1. Target and source reading

- **Target:** WOWII **305** — page marker `O` (open), note dated Mar. 1, 2007;
  transcription in `data/wowii-conjectures.json` id 305:
  > If G is a simple connected graph such that n(G) > 2, then
  > γ_t(G) ≤ CEIL[(2/3)·maximum of |N_bar(G)(e)|]
  Section: "Upper bounds for Total Domination γ_t".
- **Hypotheses (frozen):** G simple, connected, n(G) > 2. Rows with n ≤ 2 or
  disconnected are NOT_APPLICABLE and never scored.
- **Residual (exact):** for each reading below,
  `R(G) = CEIL[(2/3)·max_e |N̄(e)|] − γ_t(G)` computed in exact `Fraction`
  arithmetic. Hold ⟺ R ≥ 0; a counterexample witness has R < 0.
- **Reading table (ALL plausible parses; every reading gets gate + family rows).**
  The token `N_bar(G)(e)` is ambiguous between quantifier domain (edges of G vs
  edges of bar G) and endpoint convention. The campaign's locked precedent for
  this exact token is `scripts/verify_wowii_309.py` (same page section, same
  note date, same min/max-of-|N̄(e)| machinery): there the SOURCE reading is
  the literal union of open neighborhoods in bar(G) over complement edges,
  endpoints included. That precedent plus a sibling-consistency argument
  (see §3) fixes the primary reading; the others remain tabulated:
  - **RDG-B (PRIMARY, "comp-edge incl", 309-locked):** e ranges over E(bar G);
    |N̄(e)| = |N̄_bar(u) ∪ N̄_bar(v)| (open neighborhoods in the complement,
    endpoints included — u and v are adjacent in bar G). Identity:
    |N̄(e)| = n − codeg_G(u,v) for nonedge uv.
  - **RDG-A ("comp-edge excl"):** e ∈ E(bar G); same union minus {u,v}.
    Identity: n − 2 − codeg_G(u,v).
  - **RDG-C ("G-edge in bar", survey-slack source):** e ∈ E(G); open union in
    bar G. For a G-edge uv the endpoints are non-adjacent in bar G, so the
    include/exclude conventions coincide: n − 2 − codeg_G(u,v), max over E(G).
  - **RDG-D ("N_G(nonedge)", 309-tabulated alternate):** e ranges over nonedges
    of G; |N̄(e)| = |N_G(u) ∪ N_G(v)| (open union in G; endpoints never count).
- **Undefined-term rule:** graphs with no complement edge (complete graphs)
  make RDG-A/B undefined; graphs with no nonedge make RDG-D undefined; those
  rows are recorded NOT_APPLICABLE per the 309 Atlas-gate precedent, never
  counted as holds or violations.
- **γ_t:** total domination number (every vertex, including set members, has a
  neighbor in the set); exact by two independent implementations (§6).
- **maxine:** not used by 305.

## 2. Resolution card (Phase 0A)

```json
{
  "logical_class": "FINITE_UNIVERSAL",
  "target_negation": "there exists one finite connected graph on > 2 vertices with R < 0 under the reading",
  "negation_certificate": "labelled adjacency + exact gamma_t witness set + exact max_e |N_bar(e)| certificate edge",
  "finite_witness_suffices": true,
  "exact_residual": "R = ceil((2/3)*max_e |N_bar(e)|) - gamma_t",
  "answer_placeholder": false,
  "eventual_quantifier": false,
  "global_constant_quantifier": false,
  "unbounded_auxiliary_search": false
}
```

## 3. Baselines, theorem shadows, sibling consistency (Phases 3–4, frozen)

- **Sibling disambiguation:** WOWII **306** (`γ_t ≤ 2·floor[½·min|N̄(e)|]`) is
  page-marker `T` (PROVED). Hand orientation arithmetic shows RDG-C violates
  306 on K₃ itself (term = 0 ⇒ RHS 0 < 2) and RDG-A on the diamond K₄−e
  (min term 0 over its single complement edge), RDG-D on K₁,₃ (term 1 ⇒ RHS 0).
  Only RDG-B keeps proved-306 alive on small controls. RDG-B is therefore
  PRIMARY for 305; the other readings are executed for the record and expected
  to die at the gate.
- **Candidate shadow S1 (to be verified computationally before use):** the
  classical bound γ_t(G) ≤ ⅔·n(G) for connected n ≥ 3 (P₆-type equality).
  If verified on the whole gate set it becomes a shadow: any graph with diam ≥ 3
  has a nonedge pair at distance ≥ 3, hence codeg = 0 available, hence under
  RDG-B max_e|N̄(e)| = n and R = ceil(⅔n) − γ_t ≥ 0: **the diameter ≥ 3 regime
  is THEOREM_SHADOWED** and the live region is diam(G) = 2.
- **Diameter-two squeeze (obstruction identity, testable):** if diam(G) = 2 then
  γ(G) ≤ 2 (any vertex v plus a neighbor of anything at distance 2 dominates),
  so γ_t ≤ 2γ ≤ 4. Crossing under RDG-B needs ceil(⅔M) < γ_t with
  M := max(n − codeg) over nonedges, i.e. M < (3/2)γ_t ≤ 6, i.e. **M ≤ 5**, and
  M = n − c_min where c_min = min codeg over nonedges. So every crossing must be
  a diameter-2 graph with γ_t ∈ {3,4}, n − c_min ≤ 5, i.e. twin-dense: every
  nonedge pair shares ≥ n − 5 common neighbors. This identity bounds the entire
  live region and is checked on every family row.
- **Arsenal obstruction identity (C₅ blow-ups):** on B(w₀..w₄) (all wᵢ ≥ 1),
  nonedges are exactly blob pairs at cyclic distance 2–3 with middle blob the
  common neighborhood, so M = n − min(wᵢ) ≥ 4 while γ_t = 3 for ALL positive
  weights: R = ceil(⅔(n − w_min)) − 3 ≥ ceil(8/3) − 3 = 0, equality iff
  n − w_min = 4 (in particular C₅ itself: R = 0). Blow-up weights can NEVER
  cross; only leaving the C₅-blow-up class can move M/(γ_t).

## 4. Sign-potential table (frozen prediction)

Transformation axis: density/twin structure of diameter-2 graphs (knob k =
c_min-raising twin surgery) vs metric growth (subdivision, which exits the live
region entirely).

| quantity | predicted motion | reason |
|---|---|---|
| M = max_e|N̄(e)| | pinned ≤ n; grows to n when diam ≥ 3 | distance-≥3 pair donates codeg 0 |
| γ_t | ≤ 4 pinned inside diam 2; grows slowly outside | γ_t ≤ 2γ, γ ≤ 2 at diam 2 |
| net R | **increase** along subdivision (shadow side); flat-at-equality or positive inside diam 2 | RHS floor ceil(⅔M) tracks n while γ_t caps at 4 |

Frozen prediction: NO crossing exists on the designed grid; the trial's value
is the exact mapping of the equality walls (C₅, stars K₁,₃, C₄-type points) and
the obstruction identity. If any row returns R < 0 the prediction was wrong and
the stop rules take over.

## 5. Development family (FROZEN grid)

Nothing may be added without a new contract.

- **F1 unequal C₅-blow-ups B(w₀..w₄)**, wᵢ ∈ {1,2,3} all 243 weight vectors,
  n ∈ [5,15]: tests §3 arsenal identity at the C₅ equality point; closed-form
  prediction R = ceil(⅔(n − w_min)) − 3.
- **F2 line graphs T(k) = L(K_k)**, k ∈ {5,...,9}: edge-maximal neighbourhood
  growth structure; nonedges = disjoint edge pairs, codeg = 4 (k ≥ 4), so
  M = C(k,2) − 4 pinned while γ_t(L(K_k)) measured exactly (predicted ~k−1);
  documents quadratic-RHS safety.
- **F3 cocktail party CP(k) = K_{2k} minus perfect matching**, k ∈ {2..7}:
  maximal twin-density; M = 2 pinned, γ_t = 2 predicted ⇒ R ≡ 0 equality wall
  along the whole knob (pin-flat BOTH sides).
- **F4 complete multipartite K(p)**, p ∈ {(2,1,1),(2,2,1),(3,1,1),(2,2,2),
  (3,2,1),(3,3,1),(4,2,1),(3,3,2),(4,3,1),(5,2,1)}: comp = disjoint cliques ⇒
  M_RDG-B = p_max; γ_t = 2 predicted; crossing needs p_max ≤ 2 ⇒ equality-only.
- **F5 exhaustive small-region extension:** EVERY connected graph on n = 8
  vertices, generated as connected atlas-7 graphs plus one attached vertex,
  deduplicated up to isomorphism (canonical adjacency-string bucketing +
  isomorphism check), full exact evaluation. Together with the atlas gate this
  makes the n ≤ 8 region EXHAUSTIVE, covering the only γ_t = 3 crossing shapes
  allowed by §3 (M ≤ 3 forces n ≤ 8 unless c_min ≥ n−3 twin-density appears).
- **F6 control arm (metric growth, shadow-side):** subdivided C₅[D(w)] single
  rim-edge subdivisions ℓ ∈ {1,2,3}: predicted diam ≥ 3 ⇒ R = ceil(⅔n) − γ_t > 0,
  confirming the S1 shadow boundary empirically.

## 6. Bounds, budgets, stop rules

- Construction + full evaluation cap per member: **60 s CPU** (signal-enforced).
  F5 runs as one arm with a stated aggregate cap of 900 s CPU; any member that
  cannot certify exactly inside its cap is recorded as a bracket, marked
  incomplete.
- All arithmetic exact (`Fraction`); no spectral quantities are used anywhere
  in this trial (the campaign 1e-6 spectral guard is therefore vacuously
  satisfied; noted for completeness).
- **γ_t two independent implementations** (ascending-k subset enumeration with
  witness certificate AND ILP via pulp/CBC); every scored row requires engine
  agreement; disagreement ⇒ row quarantined, recomputed, disclosed.
- **Step-aware sign check (v1.7 R1):** the ceiling argument (⅔)M advances by 1
  whenever M advances by 2; F1 rows cover M = 4..10 contiguous, F2 covers
  growing M at fixed c_min = 4. No sign-zero conclusion may be drawn from
  constant-residual neighbours alone; the run must span ≥ 2 rounding steps of
  every rounding operator in the residual, which F1+F2 jointly provide.
- **Stop rules:**
  1. Any member with exact R < 0 under a gate-surviving reading: freeze witness
     (labelled adjacency + γ_t set + argmax edge), rerun both engines, replay
     DB gate ⇒ verdict `KILL_CANDIDATE` or discard.
  2. All members hold after the full step-sampled run ⇒ `HOLD_BOUNDED`.
  3. A reading violated by ANY applicable gate control ⇒ that READING is
     rejected as mis-transcription (record first-violation witness, move on).
     If all four readings die ⇒ entry-level `STOP_CORRUPT_READING`.
  4. Budget exhausted mid-grid ⇒ `HOLD_BOUNDED` over completed rows, reported
     as such.

## 7. Database-sanity gate (before family evaluation)

Every applicable control must satisfy R ≥ 0 under each reading scored:
all connected Graph Atlas graphs n ≤ 7 (`nx.graph_atlas_g()`, disconnected
filtered out), plus C₅–C₉, P₇, Petersen, K₃,₃, K₇, stars K_{1,n} n=3..8, and
K_{n,n} n=2..6.

## 8. What counts as CROSS

An exact Fraction R < 0 under a gate-surviving reading on a connected graph
with n > 2, reproduced by two independent code paths (enumeration certificates
+ ILP), surviving the §7 gate replay, with labelled adjacency saved. Ties
(R = 0) are never kills.

## 9. Pre-freeze disclosure

The rank-4/#308 / rank-5/#305 selection, the survey slack figures, and the
309 reading precedent were fixed in SURVEY.md and prior sweeps before this
contract. Orientation hand-arithmetic done BEFORE this freeze (reading
consistency analysis, diamond/K₃ predictions, C₅-blow-up closed forms) is
analysis only; no development-family member was constructed or evaluated
pre-freeze. Arsenal tightness data quoted from family profile JSONs was
re-derived independently inside this trial's own gate run.
