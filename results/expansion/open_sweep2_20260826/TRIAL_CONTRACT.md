# TRIAL CONTRACT — WOWII 183 wall-navigation trial (open_sweep2, 2026-08-26)

**Frozen before any development-family member is constructed or evaluated.**
Method: METHOD.md v1.0 phases 0A–7 + METHOD_V1_7.md R1 (step-aware sign check).
Status: `DEVELOPMENT` (WOWII corpus is this campaign's development set).

## 1. Target and source reading

- **Target:** WOWII **183** — page marker `O` (open), note dated Aug 8, 2005;
  transcription in `data/wowii-conjectures.json` id 183:
  > If G is a simple connected graph on at least 2 vertices, then
  > L_s(G) + b(G) ≥ Δ(G²) + 2·rad(G²).
- **Reading (single, source-faithful, frozen):** all derived quantities of G²
  are taken on the second power graph G² wholesale (vertices adjacent iff
  distance ≤ 2 in G), Graffiti.pc-style, per the open-sweep reading audit.
  - `L_s(G)` = maximum leaf count over spanning trees;
  - `b(G)` = order of a largest induced bipartite subgraph (= n − τ_odd);
  - `Δ(G²)`, `rad(G²)` = max degree and radius of G².
  Reading class: `UNAMBIGUOUS` (the sweep audited the mixed-G alternative and
  rejected it as not a plausible parse; no second reading exists to table).
- **Residual (exact):** `R(G) = L_s(G) + b(G) − Δ(G²) − 2·rad(G²)`.
  Hold ⟺ R ≥ 0. A counterexample witness has R < 0.

## 2. Resolution card (Phase 0A)

```json
{
  "logical_class": "FINITE_UNIVERSAL",
  "target_negation": "there exists one finite connected graph on >= 2 vertices with R < 0",
  "negation_certificate": "labelled adjacency + exact L_s, b, Delta(G^2), rad(G^2)",
  "finite_witness_suffices": true,
  "exact_residual": "R = L_s + b - Delta(G^2) - 2*rad(G^2)",
  "answer_placeholder": false,
  "eventual_quantifier": false,
  "global_constant_quantifier": false,
  "unbounded_auxiliary_search": false
}
```

## 3. Baselines and theorem shadows (Phases 3–4, frozen)

- **Identity:** for connected G with n ≥ 3, `L_s(G) = n − γ_c(G)`
  (Duchet–Meurisse; γ_c = connected domination). Hence exactly
  `R = (b − γ_c) + (n − Δ(G²)) − 2·rad(G²)`.
  **Frozen crossing inequality:** `γ_c − b > (n − Δ(G²)) − 2·rad(G²)`.
- **Diameter-two theorem shadow:** if diam(G)=2 then G²=K_n and 183 reduces to
  `L_s + b ≥ n+1` — the proved baseline that closed the 176/182–185 attacks.
  The diameter-2 regime is therefore THEOREM_SHADOWED and the trial operates
  with diam ≥ 3 (equivalently G² ≠ K_n).
- **Obstruction identity on the arsenal (Phase 4 statement, testable):** every
  C₅-blow-up has α = 2 ⇒ b = 4 pinned, γ_c = 3, G² = K_n ⇒ Δ+2rad = n+1, so
  `R ≡ 0`. Blow-up weights cannot separate the terms; only leaving diameter 2
  can move `(n − Δ(G²)) − 2rad(G²)` away from −1.
- **Known proved tiers** (Lean, prior lanes): 183 holds when γ_c ≤ 4 within the
  studied claw-free/distance-three core. Any crossing witness must respect
  these tiers; they are recorded as constraints, not stops outside their
  hypotheses.

## 4. Sign-potential table (frozen prediction)

Transformation: replace one rim join of a C₅-blow-up by a bridge chain of ℓ
cliques ("subdivided join"), keeping everything else complete.

| quantity | predicted motion | reason |
|---|---|---|
| γ_c | increase slowly (+~⌈ℓ/2⌉−1) | dominators must traverse the bridge |
| b | near-pinned while bridge blobs ≥ 2 (triangles persist); may gain ~ℓ via bridge paths when bridge widths are 1 | hereditary pin vs induced-path growth — the measured separation |
| Δ(G²) | decrease by ≈ min(w₃,w₄)+… per far pair | square loses completeness across the split |
| rad(G²) | increase toward ⌈(ℓ+1)/2⌉+1 | metric growth |
| net R | **decrease**, candidate crossing at moderate ℓ with asymmetric weights | RHS sheds 2/rad-step + Δ-defect faster than LHS gains |

## 5. Development family (FROZEN grid)

Family F(ℓ; w₀..w₄; c₁..c_{ℓ−1}): cliques W₀..W₄ (|W_i| = w_i ≥ 1) at cycle
positions 0–4 with complete joins W_i–W_{i+1} (mod 5) EXCEPT the join W₃–W₄,
which is replaced by a chain W₃–B₁–…–B_{ℓ−1}–W₄ of cliques |B_j| = c_j ≥ 1,
consecutive complete joins. ℓ = 1 recovers the plain blow-up.

Arms (all members listed now; nothing else may be added without a new contract):
- **A1 uniform:** ℓ ∈ {1,2,3,4}, w = (2,2,2,2,2), c = (2,…,2) → 4 members
  (n = 10, 12, 14, 16).
- **A2 asymmetric weights:** ℓ ∈ {1,2,3,4,5}, w = (2,1,2,1,1), c = (1,…,1)
  → 5 members (n = 7, 8, 9, 10, 11).
- **A3 bare control:** ℓ ∈ {2,3,4,5}, w = (1,1,1,1,1), c = (1,…,1)
  (subdivided C₅, no blow-up) → 4 members (n = 6, 7, 8, 9).

Total 13 members, n ≤ 16 throughout.

> **Pre-evaluation amendment (2026-08-26, before any member was constructed):**
> the original draft grid (m ∈ {2,3}, heavier weights, n ≤ 26) was tightened to
> the above so that *both* frozen independent exact engines (combinatorial
> certificate enumeration and branch-and-bound) terminate inside the 60 s cap
> on every member. The step-aware sign check ranges (§6) are unchanged. No
> member has been evaluated prior to this amendment.

## 6. Bounds, budgets, stop rules

- Construction + full evaluation cap per member: **60 s CPU**.
- All arithmetic exact integers (no spectral quantities; Fractions trivially
  satisfied). γ_c and τ_odd computed by two independent implementations
  (ascending-k certificate enumeration AND an ILP/second code path); any
  coordinate that cannot be certified exactly inside the cap is recorded as a
  bracket for that member and the member's row marked incomplete.
- **Step-aware sign check (v1.7 R1):** the residual is evaluated over the full
  contiguous ℓ-run {1..4} (arm A1), {1..5} (A2), and {2..5} (A3) before any
  sign-zero conclusion; a constant residual across adjacent members alone is
  NOT a stop.
- **Stop rules:**
  1. Any member with exact R < 0: freeze witness, rerun both independent
     implementations, replay DB gate → verdict `KILL_CANDIDATE` or discard.
  2. All members hold after the full step-sampled run → `HOLD_BOUNDED`.
  3. Reading violated by any DB-gate control → `STOP_CORRUPT_READING`.
  4. Budget exhausted mid-grid → `HOLD_BOUNDED` only over completed rows,
     reported as such.

## 7. Database-sanity gate (before family evaluation)

Every applicable control must satisfy R ≥ 0 under the frozen reading:
all connected Graph Atlas graphs n ≤ 7 (`nx.graph_atlas_g()`, disconnected
filtered out), plus C₅–C₉, P₇, Petersen, K₃,₃, K₇, stars K_{1,n} (n=1..6),
K_{n,n} (n=2,3,4), and T(7)=L(K₇).

## 8. What counts as CROSS

An exact integer R < 0 on a connected graph with n ≥ 2, reproduced by two
independent code paths (enumeration certificates + ILP), surviving the §7
gate, with labelled adjacency saved. Ties (R = 0) are never kills.

## 9. Pre-freeze disclosure

The rank-1 selection and the analytic arsenal equality R≡0 were fixed in
SURVEY.md before this contract. No development-family member has been
constructed or evaluated as of this freeze. Arsenal rows used for the survey
are the documented sweep data plus closed-form identities only.
