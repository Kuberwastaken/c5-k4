# TRIAL LOG — WOWII 183 (open_sweep2_20260826)

Append-only. One entry per completed step.

## 2026-08-26 — STEP 0: contract frozen

`TRIAL_CONTRACT.md` written and frozen before any development-family
construction or evaluation. Target: WOWII 183 (rank 1 of SURVEY.md).
Reading, residual, crossing inequality, 16-member family grid, bounds,
stop rules all as in the contract.

## 2026-08-26 — STEP 0a: pre-evaluation grid amendment (disclosed)

Grid tightened to 13 members, n ≤ 16, BEFORE any construction/evaluation, so
both frozen exact engines finish inside the 60 s caps. Amendment recorded in
the contract with a timestamped note. No family row has been computed.

## 2026-08-26 — STEP 1: semantic microfixtures PASS

Hand-frozen fixtures, both engines, exact integers:

| fixture | L_s | b | Δ(G²) | rad(G²) | R_A | R_B | frozen expected |
|---|---|---|---|---|---|---|---|
| K2 | 2 | 2 | 1 | 1 | 1 | 1 | 1 |
| K3 | 2 | 2 | 2 | 1 | 0 | 0 | 0 |
| C5 | 2 | 4 | 4 | 1 | 0 | 0 | 0 |
| P7 | 2 | 7 | 4 | 2 | 1 | 1 | 1 |
| K1,4 | 4 | 5 | 4 | 1 | 3 | 3 | 3 |
| K7 | 6 | 2 | 6 | 1 | 0 | 0 | 0 |

All six OK (`trial_183.py fixtures`, exit 0). Note K3, C5, K7 are already
exact-tight under 183 — consistent with the diameter-two theorem shadow
(proved baseline equality).

## 2026-08-26 — STEP 2: database-sanity gate PASS

`trial_183.py gate` — engine A (exact enumeration/certificates; T(7) routed
through the König line-colouring characterization `b(L(K_n)): chi'(K[S])<=2`,
verified by deletion-enumeration over edge sets):

- Graph Atlas: 1,253 graphs, filtered to **995 connected, n≥2** — all R ≥ 0.
- Named controls: C5(0) C6(0) **C7(0)** C8(2) C9(2) P7(1) Petersen(2)
  K3,3(3) K7(0) **T(7)(9)** K1,1..K1,6(1..5) K2,2(1) K3,3(3) K4,4(5).
- **Violations: 0. Incomplete rows: 0.** Gate verdict: reading survives.

Observations recorded pre-family: the equality wall includes C5, C6, C7, K3,
K7 (all R=0) — i.e. the proved diameter-two baseline shadow plus small
diameter-three cycles sit exactly on 183. T(7) is far off the wall (R=9),
consistent with the α=λ_max geometry being a different mechanism entirely.

Rows persisted to `gate_rows.json`.

## 2026-08-26 — STEP 3: frozen family evaluation — NO CROSSING

Both exact engines, all integers, every member under 0.7 s (cap 60 s):

| member | ℓ | w | n | γ_c | L_s | b | Δ(G²) | rad(G²) | **R** |
|---|---|---|---|---|---|---|---|---|---|
| A1_l1 | 1 | (2,2,2,2,2) | 10 | 3 | 7 | 4 | 9 | 1 | **0** |
| A1_l2 | 2 | ″ | 12 | 4 | 8 | 6 | 9 | 2 | **1** |
| A1_l3 | 3 | ″ | 14 | 5 | 9 | 6 | 9 | 2 | **2** |
| A1_l4 | 4 | ″ | 16 | 6 | 10 | 8 | 9 | 2 | **5** |
| A2_l1 | 1 | (2,1,2,1,1) | 7 | 3 | 4 | 4 | 6 | 1 | **0** |
| A2_l2 | 2 | ″ | 8 | 4 | 4 | 6 | 6 | 2 | **0** |
| A2_l3 | 3 | ″ | 9 | 5 | 4 | 6 | 6 | 2 | **0** |
| A2_l4 | 4 | ″ | 10 | 6 | 4 | 8 | 6 | 2 | **2** |
| A2_l5 | 5 | ″ | 11 | 7 | 4 | 8 | 6 | 2 | **2** |
| A3_l2 (=C6) | 2 | (1,×5) | 6 | 4 | 2 | 6 | 4 | 2 | **0** |
| A3_l3 (=C7) | 3 | ″ | 7 | 5 | 2 | 6 | 4 | 2 | **0** |
| A3_l4 (=C8) | 4 | ″ | 8 | 6 | 2 | 8 | 4 | 2 | **2** |
| A3_l5 (=C9) | 5 | ″ | 9 | 7 | 2 | 8 | 4 | 2 | **2** |

Engine agreement: 13/13 on every coordinate (γ_c, τ_odd, Δ(G²), rad(G²), R).
A3 rows independently reproduce the gate's C6/C7/C8/C9 controls exactly.

**Disclosure (calibration events):** the first family pass ran engine B with
two defects — (i) it computed *domination* (no connectivity), returning γ ≤ γ_c;
(ii) v2 rejected dominating-but-disconnected prefixes instead of extending them
to connected sets. Engine A (primary enumeration path) was unaffected and
returned identical values on every pass; rows from defective passes were
discarded and re-evaluated with corrected engine B (connected-set-growth
IDDFS). Final table above is from the corrected pass. Fixtures re-passed
before the final run.

## 2026-08-26 — STEP 4: step-aware sign check (METHOD v1.7 R1)

Residuals along the contiguous ℓ-runs are NOT constant — they advance
(A1: 0→1→2→5; A2: 0→0→0→2→2; A3: 0→0→2→2) — so the sampling rule is satisfied
and the sign reading is genuinely positive past the tight plateau, not an
under-sampled dR=0 artifact. No rounding-operator argument stalls anywhere
(all quantities integer-exact).

## 2026-08-26 — STEP 5: VERDICT — HOLD_BOUNDED

- **No negative residual exists on the frozen grid.** Zero crossings over
  13 designed members + 1,013 database-sanity rows.
- **Frozen prediction REFUTED (recorded):** subdividing a rim join does NOT
  separate the terms. Measured mechanism: per subdivision level,
  dγ_c/dℓ = +1 while db/dℓ alternates 0/+2 (each new bridge level donates an
  induced-path pair to the bipartite side), so b − γ_c is non-decreasing;
  meanwhile rad(G²) **saturates at 2** (bridge vertices keep both cores within
  square-distance 2) and the Δ(G²)-defect stays flat — the RHS sheds nothing
  further. The wall term moves WITH the hereditary term, against the frozen
  sign-potential table.
- Obstruction identity (testable, holds on the whole family):
  `dR/dℓ = [Δb − Δγ_c] − [Δ(n − Δ(G²)) − 2Δrad] ≥ 0` with both brackets ≥ 0;
  equality rows are exactly the ℓ ≤ 3 plateau (rad still 1 or b lagging).
- Consequence for the cluster: this closes the *subdivided-join* coordinate
  for 183. It says nothing about other coordinates (blob-count asymmetry at
  fixed diameter, complement surgery, line-graph moves), and it does not
  touch cluster-mates 184/185 (their dist_avg RHS terms were outside the
  frozen scope).

Primary outcome: **HOLD_BOUNDED** — a published zero, not a failure to hide.
No KILL_CANDIDATE arose, so no novelty audit or Lean certificate is owed.
The theorem-signal sharpened by this trial: any counterexample to 183 must
make b grow strictly slower than γ_c while keeping G² nearly complete —
the opposite of what induced-path-donating subdivisions do.
