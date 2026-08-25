# RESULT — WOWII 305 + 308 prospective wall-navigation trials
(open_sweep2_20260826 / trial_305_308; contracts frozen before any
development-family evaluation; method: METHOD.md v1.0 + METHOD_V1_7 R1)

## WOWII 305 — `γ_t(G) ≤ ceil[(2/3)·max_e |N̄(e)|]`

**Verdict: HOLD_BOUNDED** under the sole gate-surviving reading **RDG-B**
("comp-edge incl", the campaign's locked 309 precedent: e ∈ E(bar G), literal
open-neighborhood union in bar(G), endpoints included, |N̄(e)| = n − codeg_G(u,v)).

- Gate: RDG-B survives all 1,013 controls with zero violations. Readings
  RDG-A (45 violations), RDG-C (17), RDG-D (32) are rejected at the gate as
  mis-transcriptions — consistent with proved sibling 306 being viable only
  under RDG-B.
- Shadow S1 verified empirically (γ_t ≤ ⅔n on every control): diameter ≥ 3 is
  THEOREM_SHADOWED (a distance-≥3 nonedge pair forces M = n ⇒ R ≥ ceil(⅔n) − γ_t).
- Obstruction identity (testable, confirmed on every family row): crossings can
  only be diameter-2 graphs with γ_t ∈ {3,4} and M = n − c_min ≤ 5; on
  C₅-blow-ups M = n − w_min and γ_t = 3 for ALL positive weights ⇒ R =
  ceil[⅔(n−w_min)] − 3 ≥ 0 with equality iff C₅ itself.
- Families: F1 (243 unequal blow-ups) closed-form EXACT on all members;
  F2 T(k) c_min pinned at 4 (quadratic-RHS safety); F3 CP(k) pin-flat equality
  wall R ≡ 0; F4 multipartites hold with M = p_max; F6 control arm leaves the
  wall upward and found a NEW equality point at **C₆** (γ_t=4=ceil[⅔·6]).
- F5: ALL 11,117 connected graphs on n = 8 evaluated exhaustively — zero
  violations, 16 exact equalities, empty (γ_t≥4 ∧ M≤5) population.
- Survey correction: the survey's "slack 1 (3 vs 4) on C₅[K₂]" belonged to
  profile rows of now-rejected readings; under RDG-B, **C₅ is an exact
  equality point** (R = 0), so 305's wall is tighter than surveyed but sits on
  small dense controls, not on the big arsenal (arsenal min slack 3).

Primary outcome: **HOLD_BOUNDED** (with PREDICTION_CONFIRMED arms). A published
zero over 12,392 exact rows. No KILL_CANDIDATE arose; no novelty audit or Lean
certificate owed.

## WOWII 308 — `γ_t(G) ≤ ½[maxine(G) + min_e |N̄(e)|]`

**Verdict: STOP_CORRUPT_READING.**

All four plausible readings of |N̄(e)| are violated by applicable database
controls (first witness P₃, n=3: γ_t=2 > ½[1+2] = 3/2):

| reading | tie-break-robust control violations |
|---|---|
| RDG-B (primary, 309-locked) | 23 |
| RDG-A | 390 |
| RDG-C (source of the survey's "slack 0" datum) | 324 |
| RDG-D | 232 |

Tie-break discipline (contract §1): every RDG-B violation holds at BOTH maxmin
and maxmax of the exhaustively enumerated reachable-maxine set — i.e. under
EVERY deterministic tie-break rule of the greedy; maxine is not load-bearing
for the failure. The pre-stated §3 prediction (diamond refutes all readings)
is CONFIRMED and strengthened (P₃ already suffices). Since proved sibling 306
shares the min-term and survives controls ONLY under RDG-B, the printed 308 —
which dies even under RDG-B — cannot be the statement DeLaViña's page carried;
as transcribed it is corrupt/mis-transcribed. Per stop rule 3 the entry stops
before family evaluation; no truth claim is made about any repaired variant.

## Artifacts

| file | content |
|---|---|
| TRIAL_CONTRACT_305.md / TRIAL_CONTRACT_308.md | frozen contracts |
| TRIAL_LOG.md | append-only step log (STEPs 0–7) |
| trial_common.py | shared exact apparatus (2 engines for γ_t; reachable-maxine enumerator; 4 readings) |
| step1_fixtures.py … step5_f5.py | per-step runners |
| gate_rows.json | 1,013-control gate rows, violation witnesses, slack histograms |
| arsenal_rows.json | 16-member arsenal tightness map (both engines agree everywhere) |
| family_rows.json | F1–F4, F6 rows |
| f5_rows.json | exhaustive n=8 summary |

Budgets: every construction/evaluation inside its 60 s cap; F5 total 18.9 s
against a 900 s aggregate cap; largest single-member engine time < 30 s.
Arithmetic exact throughout (Fractions/integers); no spectral quantities used.
No git commands were run by this trial.
