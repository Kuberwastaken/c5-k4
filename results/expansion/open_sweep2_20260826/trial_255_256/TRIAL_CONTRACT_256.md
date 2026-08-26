# TRIAL CONTRACT 256 — WOWII 256 wall-navigation trial (open_sweep2_20260826)

**Frozen before any development-family member is constructed or evaluated.**
Method: METHOD.md v1.0 phases 0A–7 + METHOD_V1_7.md R1 (step-aware sign check).
Status: `DEVELOPMENT`. Paired rank-2 target with 255 (SURVEY.md); sibling
contract `TRIAL_CONTRACT_255.md` freezes the shared denominator/protocol
detail. This contract is complete standalone for 256.

> **AMENDMENT 1 (2026-08-26, STEP 1 — semantic microfixture calibration,
> BEFORE any development-family construction/evaluation):** fixture pass
> exposed two hand errors shared with the sibling freeze: γ_t(C6) = 4 (not 3)
> and |C(C7)| = 7 (not 1) — C7 is vertex-transitive ⇒ self-centered ⇒ every
> vertex is a center, and by OI-5 its residual is **1/2** here too. The
> regular-arm prediction row is corrected accordingly (C6 base row = **1**,
> not 0; C6+chord R256 = 0 STANDS — A = deg-2 vertices have N(A) = V). No
> family row existed at amendment time.

> **AMENDMENT 2 (2026-08-26, STEP 4):** sibling Amendment 2 applies: Q3+chord
> has |C| = 2 (diam stays 3), γ_t = 2, and here |N(A)| = 8 = V (A = six
> deg-3 vertices, all adjacent to a chord endpoint or each other) ⇒
> R256 = 2 − 16/8 = **0** — an exact zero for 256 ONLY (asymmetric pair
> witness: same member separates the two entries). Corrected from the
> sibling's shared-value assumption.

## 1. Target and source reading

- **Target:** WOWII **256** — page marker `O` (open), page note Feb. 23, 2007,
  section "Lower bounds for Total Domination"; transcription
  `data/wowii-conjectures.json` id 256, verbatim:
  > If G is a simple connected graph, then γ_t(G) ≥ 2·|N(A)|/[maximum of
  > {N(e): e an edge of G}], where A is the set of vertices of minimum degree.
- **Invariant resolutions (INVARIANT-GLOSSARY.md, frozen before evaluation):**
  - `γ_t(G)` = total domination number;
  - `A` = set of ALL vertices of minimum degree (page convention, glossary §
    "Named vertex sets": A = vertices of minimum degree);
  - `N(A)` = glossary open neighborhood of the SET A: "the set of vertices that
    are adjacent to at least one vertex of S". Members of A adjacent to other
    members of A therefore COUNT in N(A) (no exclusion rule exists in the
    definition). The closed-neighborhood symbol N[A] is separately defined in
    the same glossary; substituting it would contradict the source text ⇒ the
    closed parse is REJECTED as not a plausible transcription. Single
    numerator reading exists.
  - `N(e)` denominator: identical ambiguity to 255 ⇒ same two tabled readings.
    Intersection parse rejected (contradicts "at least one of u or v").
- **Reading table:**
  - **RD-A ("union-incl", primary):** `maxN(e) := max over edges {u,v} of
    |N({u,v})|` (equals the closed-union parse; see sibling contract §1).
  - **RD-B ("hint-excl", secondary):** `maxN(e) := max over edges {u,v} of
    |(N(u) ∪ N(v)) \ {u,v}|`.
- **Domain:** simple connected graphs with ≥ 2 vertices (n = 1: max over empty
  edge set undefined; γ_t(K1) undefined).
- **Residual (exact, Fractions):**
  `R(G) = γ_t(G) − 2·|N(A(G))| / maxN(G)`. Hold ⟺ R ≥ 0. Witness: R < 0.
  Ties never kill.

## 2. Resolution card (Phase 0A)

```json
{
  "logical_class": "FINITE_UNIVERSAL",
  "target_negation": "there exists one finite connected graph on >= 2 vertices with R < 0",
  "negation_certificate": "labelled adjacency + exact gamma_t, |N(A)|, maxN(e)",
  "finite_witness_suffices": true,
  "exact_residual": "R = gamma_t - 2*abs(N(A))/maxN   (Fraction)",
  "answer_placeholder": false,
  "eventual_quantifier": false,
  "global_constant_quantifier": false,
  "unbounded_auxiliary_search": false,
  "rounding_operators_in_statement": false
}
```

## 3. Baselines and obstruction identities (frozen, testable)

Shared with 255 (sibling contract §3): OI-1 (γ_t = 2 protection), OI-2
(triangle-free vertex-transitive wall: RHS = n/Δ ≤ γ_t, zeros exactly at ETD
members), OI-4 (small-center/small-N(A) protection).

- **OI-5 (regularity collapse).** If G is regular then A = V and N(A) = V (no
  isolates), so |N(A)| = n and **256's residual coincides exactly with 255's**
  on every regular graph. All Arm-P prism/circulant rows, all arsenal regular
  rows, Petersen, T(t), L(Q3), L(Petersen) are NUMERICALLY SHARED between the
  two entries; only W-arm and B-arm irregular rows can differentiate the pair.
  Recorded as a consequence, not a defect.
- **OI-6 (min-degree concentration).** |N(A)| ≤ Σ_{a∈A} deg(a) = δ·|A| and
  every neighbor of A lies within distance 1 of the δ-core. Dense cores push
  maxN up at least as fast as |N(A)|: if some a ∈ A lies on/near an edge with
  large coverage the ratio stays pinned. No crossing mechanism was found by
  pre-freeze analysis in this direction — recorded honestly as a NEGATIVE
  result of the Phase-3/4 analysis (the trial still probes it empirically via
  W/B arms).
- **Live region:** γ_t ∈ {3,4}, |N(A)| large relative to n, maxN small.
  Hand-checkable sub-case: on trees, A ⊇ leaves so N(A) = support set and
  RHS = 2·(#supports)/maxN which grows like n/4 vs γ_t ≈ n/2 (paths) ⇒ safe;
  stars: N(A) = 1 ⇒ RHS tiny.

## 4. Sign-potential table (frozen predictions, hand-derived pre-evaluation)

Same family grid as 255 (justification: the pair shares denominator mechanics;
identical grids make the numerator comparison clean). Predictions:

| arm | prediction |
|---|---|
| regular arms (P, C, L, plus K33/Q3 bases) | numerically IDENTICAL to 255's rows (OI-5): prisms 0, 4/3, 2/3, 0, …; Q3+chord = 0. C6 base = 1 (Amendment 1) |
| W C6+chord | γ_t→2 (TD pair {0,3}); A = deg-2 vertices {1,2,4,5}, N(A) = V = 6 → R = 2 − 12/6 = **0** (OI-1 zero stands) |
| W C6+pend | A = leaves {new pendant}: N(A) = {old attach vertex} = 1 → R = γ_t − 2/maxN > 0 |
| W C6−e (=P6) | A = {endpoints}, N(A) = 2, maxN = 4 → R = γ_t(P6) − 1 = 4 − 1 = 3 |
| W K33+pe | triangle side degrees rise; A = deg-3 side incl. a2; N(A) = V → R = γ_t − 12/6 = 0 (γ_t=2, OI-1) |
| W Q3 ops | del-edge/subdiv/pendant: \|N(A)\| tracks the low-degree core, RHS stays ≤ 2n/maxN-scale; all > 0 predicted |
| B blobs | nonuniform weights are IRREGULAR: A = ALL min-degree blobs' vertices; predict R ∈ [1/2, 1] similar to 255 |

Any deviation recorded as calibration event.

## 5. Development family (FROZEN grid — identical to sibling contract §5)

34 deterministic members: Arms W (12), P (11), B (6), L (5), constructions
exactly as specified in `TRIAL_CONTRACT_255.md` §5 (incorporated herein by
reference to the frozen text; the file is part of this freeze).

## 6. Bounds, budgets, stop rules

Identical machinery to sibling contract §6: 60 s CPU cap per member; Fractions
everywhere; engine A = pulp ILP, engine B = differently-coded branch-and-bound;
both engines must agree on every coordinate of every row; third independent
check required before any KILL_CANDIDATE; step-aware R1 runs RUN-P, RUN-C,
RUN-W-base×3, RUN-B, RUN-L evaluated in full before any sign conclusion (dR = 0
over adjacent members alone is NOT a stop); stop rules 1–4 as in sibling §6
with `STOP_CORRUPT_READING` applying per reading-row.

## 7. Database-sanity gate

Identical control list to sibling §7: all connected Atlas graphs 2 ≤ n ≤ 7,
plus C5–C9, P7, Petersen, K3,3, K7, stars K_{1,n} n = 3..8, K_{n,n} n = 2..6.
Per-reading verdicts; one violated control kills that reading-row
(`STOP_CORRUPT_READING`); RD-B division-by-zero at K2 counts as corruption
(`UNDEFINED`). Survey warning on record: the excl-parse was already flagged
gate-dead for this pair ("fails on C7 itself") — the gate will confirm or
refute that claim empirically.

## 8. What counts as CROSS

As sibling §8: exact Fraction R < 0 under a gate-surviving reading, both
engines + third check agreeing, gate replayed clean, labelled adjacency saved.

## 9. Tightness map (Phase 5, frozen list)

Same arsenal list as sibling §9. Under OI-5 all regular arsenal rows coincide
with 255's; predictions: C5[K_m]: 1/2; Petersen: 2/3; T(t)/comp(C5[K4])/
C7[K3]/C9[K3]: shared values, γ_t computed exactly.

## 10. Pre-freeze disclosure

Rank-2 selection and excl-parse warning fixed in SURVEY.md before freeze. No
development-family member constructed or evaluated as of this freeze. The
OI-5 collapse means roughly half the family rows cannot distinguish 255 from
256 — disclosed now, accepted deliberately (the differentiating W/B rows are
the informative ones).
