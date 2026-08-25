# SUMMARY — erdos2_20260826 ErdosProblems lane (first pass)

Method: METHOD_V1_6 §A1 yield bands, §A6 four-coordinate status; upstream pinned `2411d22e`.
Scope: 364 untouched ErdosProblems declarations triaged (§A4); 15 audited in depth below.

| Target | Class | One-line result | Gates passed |
|---|---|---|---|
| EP 647 | retro / prior-art stop | ⨆-parse defect hypothesis rejected with typecheck evidence (faithful max-form); exact search empty for n ∈ (24, 5·10⁶]; superseded by kernel-checked issue #5021 (10⁸) + literature (9.17·10¹⁸) | source recovery, all-readings, 3 independent computations, DB-sanity ({24} recovered), duplicate check |
| EP 931 | HOLD_BOUNDED | solution censuses exact and plateauing: (3,3) → 16 sols (last n₂=58562), (4,4) → 5 sols, inside numbers ≤ 1.5·10⁶; no infinite family visible; finiteness survives | source recovery, faithfulness vs prose, sieve+sympy independent paths agreeing exactly, DB-sanity (AlphaProof witness (10,3,0,13) reproduced), duplicate clean |
| EP 288 | HOLD_BOUNDED (data) | \|I₂\|=1 variant: exactly six sporadic solutions ≤ 400 incl. the source's own [3,6]+{20}=1 example; single-interval sanity matches Kürschák | source recovery (erdosproblems.com/288 fetched), exact Fractions, faithfulness, duplicate clean |
| EP 1212 | STOP_PRIOR_ART_DOMAIN | diagonal-jog automaton route to an explicit ray sketched but stopped: pinned file already carries 2026 cores naming a "no-periodic-certificate theorem" | local theorem-domain audit (v0.9), source recovery, duplicate search |
| EP 944 | STATUS_NOTE | Skottová–Steiner 2508.08703 settles k ≥ 5 (∀ r); open core is k = 4 (Dirac 1970); declaration correctly still open; ∅-critical-set non-vacuity checked | literature recovery, degeneracy check, duplicate clean |
| EP 723 | AUDIT_CLEAN | prime-power conjecture faithful; order-1 degenerate plane excluded by Mathlib `one_lt_order` | definition-level audit at pinned mathlib rev, duplicate clean |
| EP 108 | AUDIT_CLEAN | subgraph reading makes clique obstructions void; asymptotic ∃f — not bounded-evaluable | statement read, duplicate clean |
| EP 141 | STOP_LOW_YIELD_BRACKET | k=11 consecutive-prime AP beyond meaningful bracket at our budget | statement read, duplicate clean |
| EP 193 | AUDIT_CLEAN | ℤ³ collinear-triple universal over infinite walks; degenerate loops guarded by range-infinite hypothesis | statement read incl. formalization note, duplicate clean |
| EP 398 | STOP_LOW_YIELD_BRACKET | Brocard set-equality faithful; further solutions excluded only ≥ 10⁹ in literature | statement read, duplicate clean |
| EP 506 | STOP_NOT_FALSIFIABLE | value placeholder (`IsLeast … answer(sorry)`), no closed-form claim to contradict | statement read |
| EP 61 | AUDIT_CLEAN | Erdős–Hajnal faithful (induced-free formulation matches source); solved variants present in-file | statement read |
| EP 70 | AUDIT_CLEAN | continuum-level Ramsey (𝔠 → (β,n)³₂): set-theoretic, not finite | statement read |
| EP 74/75 | GROUP AUDIT_CLEAN | EHS82 bipartite edge-distance / ℵ₁-chromatic graphs: cardinal/asymptotic quantification | statements skimmed with API tests |

Headline: **0 crossings, 0 repairable defects found; 2 prior-art stops; 3 honest brackets recorded.**
Negative results are recorded as such; no timeout was converted into a hold anywhere.

Artifacts: LEDGER.md, EP647.md, EP931.md, EP288.md, EP1212.md, EP944.md, EP723.md, COMPACT_AUDITS.md (this dir).
Solver scripts preserved under solvers/ (all numeric claims reproducible within the 60 s caps stated).
