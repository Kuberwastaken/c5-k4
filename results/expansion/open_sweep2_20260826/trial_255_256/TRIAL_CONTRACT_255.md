# TRIAL CONTRACT 255 — WOWII 255 wall-navigation trial (open_sweep2_20260826)

**Frozen before any development-family member is constructed or evaluated.**
Method: METHOD.md v1.0 phases 0A–7 + METHOD_V1_7.md R1 (step-aware sign check).
Status: `DEVELOPMENT` (WOWII corpus is this campaign's development set).
Rank-2 target pair member of SURVEY.md; sibling contract `TRIAL_CONTRACT_256.md`
freezes the same protocol for the paired entry (shared denominator mechanics,
different numerator). This contract is complete standalone for 255.

> **AMENDMENT 1 (2026-08-26, STEP 1 — semantic microfixture calibration,
> BEFORE any development-family construction/evaluation):** the hand-frozen
> fixture pass exposed two hand-arithmetic errors in §3/§4 predictions, which
> are corrected here and in TRIAL_LOG.md: (i) γ_t(C6) = 4 (not 3) — any
> 3-subset of C6 contains an isolated-in-D vertex or leaves a vertex
> undominated; C6 is therefore NOT an ETD equality point (n/Δ = 3 < 4) and its
> RD-A residual is **1**, not 0; (ii) |C(C7)| = 7 (not 1) — C7 is
> vertex-transitive, hence self-centered, so every vertex is a center; its RD-A
> residual is **1/2** for BOTH entries (regular collapse OI-5). All downstream
> §4 rows touching C6/C7 derivatives are restated below; everything else in
> this freeze stands. No family row existed at amendment time.

> **AMENDMENT 2 (2026-08-26, STEP 4 — prediction correction, no construction
> change):** the §4 value "Q3+chord = 0" was mis-derived. The frozen chord
> (0,7) IS the true antipodal pair (verified dist(0,7)=3), but shortcutting
> ONE antipodal pair leaves the other three at distance 3 ⇒ diam stays 3,
> ecc(0)=ecc(7)=2, others 3 ⇒ |C| = {0,7} = **2**, not 8. OI-1 then gives
> R = γ_t − 2|C|/n = 2 − 4/8 = **3/2** (γ_t drops to 2 via the TD pair
> {0,7}, maxN = n = 8). Corrected predicted value: **3/2**; machine row
> (both engines) confirms. The "lands on a new zero" claim is RETRACTED;
> the member remains diagnostic (γ_t halved while R stayed positive — the
> wall protects through |C| collapse).

## 1. Target and source reading

- **Target:** WOWII **255** — page marker `O` (open), page note Feb. 23, 2007,
  section "Lower bounds for Total Domination"; transcription
  `data/wowii-conjectures.json` id 255, verbatim:
  > If G is a simple connected graph, then γ_t(G) ≥ 2·|C|/[maximum of
  > {N(e): e an edge of G}], where C is the set of vertices that are centers
  > of G.
- **Invariant resolutions (INVARIANT-GLOSSARY.md, frozen before evaluation):**
  - `γ_t(G)` = total domination number (smallest D ⊆ V with every vertex
    adjacent to some member of D);
  - `C` = center = set of ALL vertices of minimum eccentricity; `|C|` its
    cardinality;
  - `N(e)` for edge e = {u,v}: per glossary verbatim def, "the set of vertices
    of V adjacent to at least one of u or v". The glossary compute hint
    (`|N(u) ∪ N(v) \ {u,v}|`) diverges from the verbatim def by the endpoints
    u, v (each endpoint IS adjacent to the other, hence belongs to the union).
    Both parses are plausible transcriptions of Graffiti.pc intent ⇒ tabled as
    two separate readings below. An intersection parse (common neighbors) is
    REJECTED: directly contradicts "at least one of u or v".
- **Reading table (every plausible reading = its own row):**
  - **RD-A ("union-incl", source-faithful primary):**
    `maxN(e) := max over edges e={u,v} of |N({u,v})|` with N(·) the glossary
    open neighborhood of a vertex SET. Robustness note: since u~v, the open
    union already contains both endpoints, so RD-A coincides with the
    closed-neighborhood union parse `|N[u] ∪ N[v]|` — two conventions, one
    value.
  - **RD-B ("hint-excl", secondary):**
    `maxN(e) := max over edges e={u,v} of |(N(u) ∪ N(v)) \ {u,v}|`.
    Known risk flagged in SURVEY.md: a sibling excl-parse was gate-dead.
  - Numerator: single source-faithful reading `|C|` (center cardinality). No
    alternative parse exists (the statement names the set C explicitly).
- **Domain:** simple connected graphs with at least 2 vertices. (n = 1 has no
  edges ⇒ `max of {}` undefined, and γ_t(K1) does not exist; WOWII practice
  throughout the sweep treats the implicit domain as edge-bearing connected
  graphs.)
- **Residual (exact, Fractions):** `R(G) = γ_t(G) − 2·|C(G)| / maxN(G)`.
  Hold ⟺ R ≥ 0 (rational comparison, no rounding operators anywhere in the
  statement). A counterexample witness has R < 0. Ties (R = 0) never kill.

## 2. Resolution card (Phase 0A)

```json
{
  "logical_class": "FINITE_UNIVERSAL",
  "target_negation": "there exists one finite connected graph on >= 2 vertices with R < 0",
  "negation_certificate": "labelled adjacency + exact gamma_t, |C|, maxN(e)",
  "finite_witness_suffices": true,
  "exact_residual": "R = gamma_t - 2*abs(C)/maxN   (Fraction)",
  "answer_placeholder": false,
  "eventual_quantifier": false,
  "global_constant_quantifier": false,
  "unbounded_auxiliary_search": false,
  "rounding_operators_in_statement": false
}
```

## 3. Baselines and obstruction identities (Phases 3–4, frozen, testable)

- **OI-1 (γ_t = 2 protection).** If γ_t(G) = 2 then some EDGE {u,v} totally
  dominates G, whence N({u,v}) = V and maxN = n ≥ |C|, so
  R = 2 − 2|C|/n ≥ 0. Equality iff |C| = n. *No γ_t=2 graph can ever cross.*
- **OI-2 (regular vertex-transitive wall identity).** If G is triangle-free,
  k-regular, vertex-transitive (n vertices): every edge has
  |N({u,v})| = 2k (endpoints + 2(k−1) distinct others, no triangles) so
  maxN = 2k, and vertex-transitivity + regularity give rad = diam ⇒ |C| = n.
  Hence RHS = 2n/2k = n/k ≤ γ_t (each dominator covers ≤ k vertices:
  n ≤ k·γ_t). **Residual ≥ 0 always; zero exactly at efficient-open-
  domination members (γ_t = n/k).** Predicted exact-zero landings (corrected
  per Amendment 1; originally hand-derived pre-evaluation): K_n (n ≥ 2),
  K_{n,n}, C4, triangular prism C3□K2 (γ_t = 2 = 6/3), C6□K2
  (γ_t = 4 = 12/3). NOT a zero: C6 itself — γ_t(C6) = 4 > 3 = n/Δ ⇒ R = 1.
- **OI-3 (blow-up scale invariance).** On lexicographic blow-ups C5[K_m]
  (m ≥ 1, uniform or nonuniform weights w_i > 0): diameter 2 ⇒ |C| = n = Σw_i;
  maxN = max over cross-blob edges of (n − b_min-side) ≤ n − min_i w_i with
  equality for uniform weights (maxN = 4m); γ_t = 3 for every positive weight
  vector (2 vertices always miss one blob; the frozen 3-set {two in blob i,
  one in blob i+2} works). Therefore
  R = 3 − 2Σw/(Σw − min w) ∈ [1/2, 1), maximized exactly at uniform weights
  (R = 1/2). **Blob-size knobs move maxN but can never push RHS above 5/2 < 3.**
- **OI-4 (small-center protection).** If |C| ≤ 2 then RHS ≤ 4/maxN ≤ 2 (any
  edge sees ≥ 2 vertices) ≤ γ_t. All trees satisfy |C| ∈ {1,2} ⇒ trees never
  cross 255.
- **Live region (from OI-1..4):** a crossing requires γ_t ∈ {3,4},
  |C|/n large, AND maxN < 2|C|/γ_t — i.e. dense-enough-to-be-3-total-dominated
  yet edge-neighborhoods far below twice the center count, outside OI-2's
  regular-transitive shelter. The frozen families below probe exactly this
  region plus the equality walls where asymmetric motion would show first.

## 4. Sign-potential table (frozen predictions, hand-derived pre-evaluation)

Knobs chosen (with justification): (i) **wall-perturbation ops** on wall/
near-wall members (K3,3 exact-zero; cube R = 4/3 and C6 R = 1 near-wall) —
discrete sign lottery at small |R|, the only
places asymmetric dR can be read off at unit resolution; (ii) **prism/
circulant orders n** — sweeps the OI-2 wall family through its ETD zeros
(predicted zeros at n ∈ {3,6}); (iii) **blob-weight vectors** — tests OI-3's
predicted R = 3 − 2Σw/(Σw − min w) ≥ 1/2; (iv) **line-graph orders** —
different (edge-vs-vertex) geometry for C and N(e), RHS grows like t(t−1)/(3(t−2))
while γ_t(L(K_t)) grows linearly ⇒ safety margin widens. G²-knobs are NOT used:
Δ(G²)/rad(G²) appear nowhere in 255 (justification recorded per protocol).

| arm | predicted motion of R | predicted values |
|---|---|---|
| W cube ops | del-edge/subdiv/pendant leave wall UPWARD (γ_t↑, \|C\|↓); antipodal chord LANDS ON new zero (γ_t→2, OI-1) | Q3: 4/3; Q3−e, Q3+sub, Q3+pend > 0; Q3+chord = 0 |
| W C6 ops (corrected per Amendment 1) | base sits at R = 1 (γ_t=4, maxN=4, \|C\|=6); chord: γ_t→2 but \|C\|→{0,3} = 2 ⇒ R255 = 2 − 4/6 = **4/3**; del-edge (=P6): γ_t = 4, \|C\| = 2, maxN = 4 ⇒ **3**; subdiv (=C7): \|C\| = 7 ⇒ **1/2**; pendant > 0 | C6: 1; C6+chord: 4/3; C6−e: 3; C6-sub: 1/2 |
| W K33 ops | small perturbations stay positive; within-part edge adds triangle, γ_t stays 2, maxN = 6 = n | K33: 0; +part-edge: 2 − 12/6 = 0 |
| P prisms n=3..8 | OI-2 zeros at n=3,6; positive elsewhere | 0, 4/3, 2/3, 0, ≥0, 4/3 (γ_t(P5-prism)=4?, γ_t(P7-prism)≥⌈14/3⌉) |
| C circulants | vertex-transitive; C_n(1,2) has triangles ⇒ OI-2 shelter only partial; predict R > 0 throughout, γ_t ≈ n/2 vs RHS ≈ n/3 | all > 0 expected |
| B blobs | R = 3 − 2Σw/(Σw − min w) exactly (OI-3), γ_t = 3 | (3,1,1,1,1): 2/3; (4,1,1,1,1): 5/7; (3,2,1,1,1): 5/7; (5,1,2,1,1): 7/9; (2,3,2,3,2): 3/5; (6,1,1,1,1): 7/9 |
| L line graphs | RHS = t(t−1)/(3(t−2)) vs γ_t(L(K_t)) grows linearly ⇒ margin widens in t | all > 0 expected |

Any deviation from a predicted value is recorded as a calibration event, not
silently accepted.

## 5. Development family (FROZEN grid — 34 members, deterministic)

All constructions deterministic; no post-hoc member may be added without a new
contract. Max n = 21. Anchors C5, C5[K2], K3,3, C6, C7 come from the gate/
arsenal tables (referenced, not duplicated).

- **Arm W (wall perturbations, 12 members).** Ops applied to base B with the
  LEXICOGRAPHICALLY FIRST edge/node in sorted order (frozen):
  - Cube Q3 (nx.hypercube_graph(3), relabelled 0..7): Q3−e (delete first
    edge); Q3-sub (subdivide first edge); Q3+pend (pendant at node 0);
    Q3+chord (add edge between node 0 and its bitwise-complement antipode).
  - C6: C6−e (=P6); C6-sub (=C7); C6+pend (pendant at 0); C6+chord (add 0–3).
  - K3,3 (parts {a0,a1,a2},{b0,b1,b2}): K33−e (delete a0–b0); K33-sub
    (subdivide a0–b0); K33+pend (pendant at a0); K33+pe (add edge a0–a1).
- **Arm P (prisms + circulants, 11 members).** Prisms C_n□K_2 for
  n ∈ {3,4,5,6,7,8}; circulants C_n(1,2) for n ∈ {9,10,11,12}; plus the lift
  control C_10(1,3).
- **Arm B (unequal blob blow-ups, 6 members).** C5[B(w0..w4)] with weight
  vectors (3,1,1,1,1), (4,1,1,1,1), (3,2,1,1,1), (5,1,2,1,1), (2,3,2,3,2),
  (6,1,1,1,1) — blobs are cliques of sizes w_i, complete joins between
  consecutive blobs mod 5.
- **Arm L (line graphs, 5 members).** L(K_t) for t ∈ {5,6,7}; L(Q3);
  L(Petersen).

Total: 34 constructed members per reading row.

## 6. Bounds, budgets, stop rules

- Construction + full evaluation cap per member: **60 s CPU** (measured,
  recorded per row).
- Exact arithmetic throughout: residuals as `fractions.Fraction`; no spectral
  quantities are used anywhere in 255 (the spectral guard 1e-6 is vacuously
  satisfied; recorded for completeness). Ties (R = 0) never kills.
- **Engines:** engine A = ILP (pulp/CBC: minimize Σx_v s.t. Σ_{u∈N(v)} x_u ≥ 1
  per vertex). Engine B = differently-coded pure-python branch-and-bound
  (undominated-vertex branching over its neighbors, greedy upper bound to
  seed pruning). Both engines must return IDENTICAL γ_t on EVERY row;
  |C|, maxN recomputed by two independent code paths (networkx BFS eccentricity
  vs hand BFS). Any hit R < 0 must additionally survive a third ad-hoc
  recomputation (independent brute-force subset check at feasible n) before it
  may be called KILL_CANDIDATE.
- **Step-aware sign check (v1.7 R1):** residuals evaluated over FULL contiguous
  runs — RUN-P (prism n = 3..8), RUN-C (circulant n = 9..12), RUN-W-base
  ({base, −e, sub, +pend, +op} per base), RUN-B (weight vectors ordered by
  frozen knob κ = Σw: 7→8→8→10→12), RUN-L (t = 5,6,7) — BEFORE any sign-zero
  conclusion; a constant residual across ADJACENT members alone is NOT a stop.
  Rational jumps occur exactly when maxN, |C| change value; runs are designed
  to cross those discontinuities.
- **Stop rules:**
  1. Any member with exact R < 0 (both engines + third check + gate replay):
     freeze witness + labelled adjacency → `KILL_CANDIDATE` or discard.
  2. All members hold after full step-sampled runs → `HOLD_BOUNDED`.
  3. Reading violated by any DB-gate control → `STOP_CORRUPT_READING` for that
     reading-row (record violating controls, move remaining evaluation to the
     surviving reading).
  4. Budget exhausted mid-grid → `HOLD_BOUNDED` over completed rows only,
     reported as such.

## 7. Database-sanity gate (before family evaluation)

Per reading-row, over ALL controls: every connected Graph Atlas graph with
2 ≤ n ≤ 7 (`nx.graph_atlas_g()`, disconnected filtered), plus C5–C9, P7,
Petersen, K3,3, K7, stars K_{1,n} n = 3..8, K_{n,n} n = 2..6.
A single violated control kills THAT READING (record violations, verdict
`STOP_CORRUPT_READING` for the reading-row, continue with surviving readings).
Division-by-zero (maxN = 0, possible only under RD-B at K2) counts as reading
corruption, recorded as `UNDEFINED`.

## 8. What counts as CROSS

Exact Fraction R < 0 on a connected graph with n ≥ 2 under a gate-surviving
reading, reproduced identically by BOTH engines (plus third check), gate
replayed clean, labelled adjacency saved to disk. Ties never kills.

## 9. Tightness map (Phase 5, frozen list)

Campaign arsenal under surviving reading(s): C5[K_m] m = 2..8, T(7), T(8),
T(9), comp(C5[K4]), C7[K3], C9[K3], Petersen. Predictions (hand-derived,
pre-evaluation): C5[K_m]: R = 1/2 exactly (m-invariant, OI-3); Petersen:
R = 2/3; T(t): R = γ_t(T(t)) − t(t−1)/(3(t−2)); comp(C5[K4]): RHS = 5/2;
C7[K3]: RHS = 7/2; C9[K3]: RHS = 9/2 (γ_t terms computed exactly).

## 10. Pre-freeze disclosure

Rank-2 selection, slack-0.5 note, and the gate-dead sibling excl-parse warning
were fixed in SURVEY.md before this contract. No development-family member has
been constructed or evaluated as of this freeze. Hand-derived predictions in
§4 were derived from the glossary definitions + published γ_t formulas only;
all of them are machine-checkable and will be scored in TRIAL_LOG.md.
