# TRIAL LOG — WOWII 255 + 256 (open_sweep2_20260826 / trial_255_256)

Append-only. One entry per completed step. Retry agent (prior agent died
pre-work; no prior artifacts existed in this directory).

## 2026-08-26 — STEP 0: orientation + contracts frozen

- Orientation: SURVEY.md (rank-2 pair, slack 0.5 incl-endpoints, excl-parse
  gate-dead warning), exemplar contract/log/result of the 183 trial,
  `data/wowii-conjectures.json` ids 255/256 verbatim,
  `data/INVARIANT-GLOSSARY.md` (C, A, N(S), N(e), γ_t resolved precisely).
- Key resolution: glossary verbatim N(e) def ("adjacent to at least one of u or
  v") vs compute hint (`|N(u)∪N(v)\{u,v}|`) diverge by the endpoints ⇒ two
  tabled denominator readings RD-A (union-incl; provably equals the
  closed-union parse since u~v) and RD-B (hint-excl). Intersection parse
  rejected (contradicts verbatim text). Numerators single-reading.
- **`TRIAL_CONTRACT_255.md` and `TRIAL_CONTRACT_256.md` written and frozen
  BEFORE any development-family construction or evaluation.** Contents:
  source-faithful statements, reading tables, exact Fraction residuals,
  obstruction identities OI-1..OI-6 (γ_t=2 protection; regular-transitive wall
  n/Δ ≤ γ_t; blow-up scale invariance; small-center protection; 255≡256
  collapse on regular graphs), frozen 34-member grid (arms W/P/B/L, max n=21),
  hand-derived falsifiable predictions (including predicted EXACT ZEROS at
  Q3+chord, C6+chord, triangular prism, C6□K2 under RD-A), gate plan, R1 runs,
  stop rules.
- No family member constructed/evaluated yet. Next: fixtures → gate → arsenal
  map → family → R1 → verdicts.

## 2026-08-26 — STEP 1: semantic microfixtures PASS (after disclosed calibration)

Hand-frozen fixtures, both engines, exact integers/Fractions, RD-A values:

| fixture | γ_t | \|C\| | \|N(A)\| | maxN_incl | R255_A | R256_A | frozen expected |
|---|---|---|---|---|---|---|---|
| K2 | 2 | 2 | 2 | 2 | 0 | 0 | 0, 0 |
| K3 | 2 | 3 | 3 | 3 | 0 | 0 | 0, 0 |
| K4 | 2 | 4 | 4 | 4 | 0 | 0 | 0, 0 |
| C4 | 2 | 4 | 4 | 4 | 0 | 0 | 0, 0 |
| C5 | 3 | 5 | 5 | 4 | 1/2 | 1/2 | 1/2, 1/2 |
| C6 | 4 | 6 | 6 | 4 | **1** | **1** | corrected: 1, 1 (was 0,0) |
| C7 | 4 | **7** | 7 | 4 | 1/2 | 1/2 | corrected: 1/2, 1/2 (|C| was 1) |
| P7 | 4 | 1 | 2 | 4 | 7/2 | 3 | 7/2, 3 |
| K1,3 | 2 | 1 | 1 | 4 | 3/2 | 3/2 | 3/2, 3/2 |
| K1,4 | 2 | 1 | 1 | 5 | 8/5 | 8/5 | 8/5, 8/5 |
| K3,3 | 2 | 6 | 6 | 6 | 0 | 0 | 0, 0 |
| Q3 | 4 | 8 | 8 | 6 | 4/3 | 4/3 | 4/3, 4/3 |
| Petersen | 4 | 10 | 10 | 6 | 2/3 | 2/3 | 2/3, 2/3 |

First pass FAILED on C6/C7 → two hand-arithmetic errors identified and fixed:
γ_t(C6) = 4 (not 3; no 3-subset works), and C7 is vertex-transitive hence
self-centered ⇒ |C| = n = 7. Contracts amended (Amendment 1, both files,
timestamped BEFORE any family construction); fixtures re-frozen; second pass
ALL 13 PASS (`fixtures.json`, exit 0). Engine A (ILP) ≡ engine B (B&B) on every
coordinate of every fixture.

## 2026-08-26 — STEP 2: database-sanity gate — RD-A survives, RD-B CORRUPT

`trial_255_256.py gate` — 1,015 controls (995 connected Atlas graphs n≤7 +
C5–C9, P7, Petersen, K3,3, K7, K1,3..K1,8, K2,2..K6,6), both engines agreeing
on every coordinate of every row (disagreements: 0), no row over cap:

| reading-row | violations | undefined | verdict |
|---|---|---|---|
| 255 / RD-A (union-incl) | **0** | 0 | survives |
| 255 / RD-B (hint-excl) | **272** (+K2 UNDEFINED: maxN=0 division-by-zero) | 1 | **STOP_CORRUPT_READING** |
| 256 / RD-A (union-incl) | **0** | 0 | survives |
| 256 / RD-B (hint-excl) | **118** (+K2 UNDEFINED) | 1 | **STOP_CORRUPT_READING** |

Concrete confirmations: K3 (atlas:2) violates RD-B for BOTH entries
(γ_t=2, maxN_excl=1 ⇒ RHS=6); **C7 violates RD-B for BOTH entries exactly as
SURVEY.md warned** ("fails on C7 itself": γ_t=4, maxN_excl=2, numerator 7 ⇒
R = −3); named-control violations include every cycle C5–C9, Petersen, K3,3,
K7, and all K_{n,n}. RD-A min slack on gate: exact zeros at K2, K3, K4, C4,
K_n-family members, K_{n,n} (all γ_t=2 OI-1/OI-2 equality points).
Rows persisted to `gate_rows.json`. All further evaluation proceeds under
RD-A only.

## 2026-08-26 — STEP 3: arsenal tightness map — all hold, min slack 1/2

14 arsenal members under RD-A, both engines agreeing, max time 6.5 s (cap 60 s).
R255_RD-A ≡ R256_RD-A on every row (all regular ⇒ OI-5 collapse):

| member | n | γ_t | R |
|---|---|---|---|
| C5[K_m] m=2..8 | 10..40 | 3 | **1/2** each (m-invariant, OI-3 confirmed empirically) |
| comp(C5[K4]) | 20 | 3 | **1/2** (RHS = 5/2 as predicted) |
| C7[K3] | 21 | 4 | **1/2** (RHS = 7/2 as predicted) |
| C9[K3] | 27 | 5 | **1/2** (RHS = 9/2 as predicted) |
| Petersen | 10 | 4 | **2/3** (as predicted) |
| T(7) | 21 | 4 | **6/5** |
| T(8) | 28 | 5 | **17/9** |
| T(9) | 36 | 6 | **18/7** |

Survey's "min slack 0.5 uniformly" CONFIRMED and sharpened: the 1/2-wall is
shared by the entire C₅-blow-up class + comp(C5[K4]) + C7[K3] + C9[K3];
T(t) margins widen with t exactly as the §4 sign table predicted
(RHS ~ t(t−1)/(3(t−2)) grows slower than γ_t(T(t)) = t−3). Rows persisted to
`arsenal_rows.json`.

## 2026-08-26 — STEP 4: frozen family evaluation — NO CROSSING under RD-A

37 rows evaluated (34 planned members + 3 base rows; disclosure below). Both
engines agreed on every coordinate of every row (0 disagreements); max time
0.064 s vs 60 s cap. Full table in `family_rows.json`.

**Disclosure (row count):** contract §5 counted 12 W-members (ops only, bases
as anchors) but Q3 was not in the anchor list, so `W_Q3_base` was constructed
explicitly; `W_C6_base`/`W_K33_base` duplicate gate rows exactly (values match
gate — internal cross-check PASS). Total constructed = 37. No other deviation.

**Disclosure (calibration event → Amendment 2):** first family pass exposed a
third hand-error: predicted "Q3+chord = 0" required |C| = 8, but shortcutting
ONE antipodal pair leaves three at distance 3 ⇒ diam 3, |C| = {0,7} = 2 ⇒
R255 = 2 − 4/8 = **3/2** (machine value). Construction verified faithful to
the frozen text (dist(0,7)=3 pre-chord). Prediction retracted in Amendment 2;
the same member gives R256 = **0** exactly (|N(A)| = V), an asymmetry witness:
one graph, two entries, R255 = 3/2 > 0 = R256.

Exact-zero (RD-A) equality-wall points found — all explained by OI-1/OI-2:

| member | R255 | R256 | mechanism |
|---|---|---|---|
| W_K33_base | 0 | 0 | γ_t=2=n/k ETD (OI-2) |
| W_K33_partedge_a0a1 | 0 | 0 | γ_t→2, \|C\|=n, maxN=n (OI-1 equality) |
| P_prism_C3xK2 | 0 | 0 | γ_t=2, TD edge sees all (OI-1) |
| P_prism_C6xK2 | 0 | 0 | γ_t=4=12/3 ETD (OI-2) |
| W_Q3_chord_antipodal | 3/2 | **0** | 256-only: \|N(A)\|=V=maxN pins RHS at γ_t |
| W_C6_chord_03 | 4/3 | **0** | same mechanism |

Hand-prediction scorecard (RD-A): B-arm 6/6 EXACT (OI-3 formula confirmed on
every weight vector); prisms n=3..8: values 0, 4/3, 2/3, 0, 1/3, 2/3 — zeros at
n ∈ {3,6} as predicted (γ_t(C8□K2)=6 independently justified by the counting
bound ⌈n/Δ⌉ = ⌈16/3⌉); C-arm all positive as predicted; L-arm all positive.
Wrong predictions (all machine-caught, all amended): C6-base zero claim,
C7 |C|, Q3+chord zero claim.

**No negative residual exists anywhere in the family under either entry.**

## 2026-08-26 — STEP 5: step-aware sign check (METHOD v1.7 R1) — PASS

Full contiguous runs evaluated BEFORE any sign conclusion (adjacent dR=0 alone
treated as non-evidence):

- RUN-P (prisms n=3..8): 0, 4/3, 2/3, 0, 1/3, 2/3 — advances/oscillates through
  TWO exact zeros without ever going negative; no stall.
- RUN-C (circulants n=9..12): 3/7, 8/7, 6/7, 4/7 — advancing, positive.
- RUN-W-cube: 4/3, 4/3, 1, 2, 3/2 — opens with an adjacent tie (base→delete),
  run as a whole varies ⇒ R1 satisfied, sign genuinely non-negative.
- RUN-W-C6: 1, 3, 1/2, 2, 4/3; RUN-W-K33: 0, 2/3, 2/3, 6/7, 0 — varied, ≥ 0.
- RUN-B (frozen κ-order): 2/3, 5/7, 5/7, 7/9, 3/5, 7/9 — one adjacent tie,
  overall tracks the closed-form OI-3 curve R = 3 − 2Σw/(Σw − min w) exactly.
- RUN-L (t=5,6,7): 7/9, 3/2, 6/5 — non-monotone but strictly positive.

No rounding operators exist in either statement; rational jumps occur exactly
at maxN/\|C\|/\|N(A)\| value changes and every run crosses them. R1 verdict:
sign readings are genuine, not under-sampling artifacts.

## 2026-08-26 — STEP 6: VERDICTS

- **255 / RD-A: HOLD_BOUNDED** — 0 crossings over 37 family rows + 1,015 gate
  rows + 14 arsenal rows; equality-wall zeros fully explained by OI-1/OI-2.
- **256 / RD-A: HOLD_BOUNDED** — same; plus two 256-only exact zeros
  (Q3+chord, C6+chord) documented as structural asymmetry witnesses.
- **255 / RD-B: STOP_CORRUPT_READING** — 272 gate violations + K2 division-by-zero.
- **256 / RD-B: STOP_CORRUPT_READING** — 118 gate violations + K2 division-by-zero.

Full statements in `RESULT.md`. Campaign ledger: both rank-2 entries remain
OPEN with their only viable reading now bounded-held across the designed
coordinate set; the excl-parse transcription question is closed as corrupt.

## 2026-08-26 — STEP 6a: artifact hygiene disclosure

The DISCARDED first family pass (buggy hit-detector scanning gate-dead RD-B
tags) had emitted `HITS.json` + 20 `witness_*.adjlist` files mislabelling
positive-residual rows as candidates. Deleted after the corrected re-run;
`family_rows.json` is the single authoritative family table. No genuine hit
ever existed under RD-A, so no witness file was owed.
