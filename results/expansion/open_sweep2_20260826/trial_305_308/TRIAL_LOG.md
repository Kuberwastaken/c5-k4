# TRIAL LOG — WOWII 305 + 308 (open_sweep2_20260826, trial_305_308)

Append-only. One entry per completed step. Contracts frozen before any
development-family construction or evaluation; see TRIAL_CONTRACT_305.md and
TRIAL_CONTRACT_308.md in this directory.

## 2026-08-26 — STEP 0: contracts frozen

Both contracts written and frozen. Targets: WOWII **305** (survey rank 5) and
**308** (survey rank 4). Reading tables freeze FOUR parses of the shared token
`N_bar(G)(e)` (RDG-A/B/C/D), with **RDG-B ("comp-edge incl", the campaign's
locked 309 precedent: e ∈ E(bar G), literal open-neighborhood union in bar(G),
endpoints included)** primary for both entries on sibling-consistency grounds
(proved sibling 306 shares the min-term and, by pre-freeze hand arithmetic,
survives small controls ONLY under RDG-B). 308 additionally freezes maxine
semantics (closed-neighborhood greedy) and mandatory tie-break discipline:
rows are evaluated at maxmin/maxmax reachable maxine over ALL deterministic
tie-break rules, with HOLD requiring maxmin and VIOLATION requiring maxmax.

Pre-freeze orientation predictions recorded in both contracts §3:
- 305/RDG-B: C₅ is an EXACT equality point (R = 0) — sharper than the
  survey's quoted slack-1, which traces to reading RDG-C/NbarA-excl rows in
  the old profile JSONs (both of those readings are predicted gate-dead);
- 308: the diamond K₄−e (γ_t = 2, maxine = 1 tie-invariant, min-term ≤ 2
  under every reading) is predicted to violate ALL FOUR readings ⇒ expected
  entry outcome STOP_CORRUPT_READING.

No development-family member has been constructed or evaluated as of this
freeze. Survey-data correction to be confirmed at the gate step.

## 2026-08-26 — STEP 0a: implementation defect caught before any scored row

Engine-B ILP initially encoded `x[u] + Σ_{w∈N(u)} x_w ≥ 1` (plain domination,
not total domination); the frozen K₃ microfixture caught it (ILP returned 1,
enumeration 2). Fixed to `Σ_{w∈N(u)} x_w ≥ 1` BEFORE any gate or family row
was produced; disclosed here per the trial-log discipline of the 183 exemplar.

## 2026-08-26 — STEP 1: semantic microfixtures PASS (both engines)

Hand-frozen fixtures, exact Fractions, engines A (enumeration certificate) and
B (ILP) in agreement on every row:

| fixture | γ_t(A) | γ_t(B) | maxmin=maxmax | 305 R_B | 305 R_A | 305 R_C | 305 R_D | 308 R_B(min/maxine) |
|---|---|---|---|---|---|---|---|---|
| K3 | 2 | 2 | 1 | N/A (complete) | N/A | **−2** ✗ | N/A | N/A |
| C5 | 3 | 3 | 2 | **0** (equality) | **−1** ✗ | **−1** ✗ | **−1** ✗ | **0** (equality) |
| diamond K4−e | 2 | 2 | 1 (tie-invariant) | 0 | **−2** ✗ | **−1** ✗ | 0 | **−1/2** ✗ |
| K1,3 | 2 | 2 | 1 | 0 | **−1** ✗ | 0 | **−1** ✗ | 0 |
| P4 | 2 | 2 | 2 | 1 | 0 | 0 | 0 | 1/2 |
| C5[K2] | 3 | 3 | 2 | 3 | 1 | 1 | 3 | 2 |

Pre-freeze predictions CONFIRMED at fixture level:
- 305/RDG-B: **C₅ is an exact equality wall** (survey's "slack 1" belongs to
  the RDG-C/NbarA-excl profile rows, not to the defensible primary reading);
- readings A/C/D already violate named controls;
- 308/RDG-B is violated by the diamond with a TIE-INVARIANT maxine
  (maxmin = maxmax = 1), i.e. robust under every deterministic tie-break rule.

Formal gate verdicts deferred to STEP 2 (full atlas + named control set).

## 2026-08-26 — STEP 2: database-sanity gate — VERDICTS PER READING

Controls: **1,013** (995 connected Graph Atlas graphs n=3..7 filtered
applicable per reading, plus C5–C9, P7, Petersen, K3,3, K7, stars K_{1,3..8},
K_{n,n} n=2..6). Engine A throughout; ILP spot agreement 7/7 sampled rows;
every violation witness below replayed through engine B before its reading was
declared dead. Full machine-readable rows: `gate_rows.json`.

**Shadow S1 verified:** γ_t(G) ≤ (2/3)·n(G) holds on ALL 1,013 controls
(zero violations) — the candidate baseline is empirically grounded on the gate;
diameter ≥ 3 regime of both entries is THEOREM_SHADOWED under RDG-B
(a distance-≥3 pair donates a codeg-0 nonedge ⇒ max term = n ⇒ R ≥ ceil(2n/3) − γ_t ≥ 0).

| reading | 305 violations | 308 tie-robust (maxmax) | 308 any-rule (maxmin) | first witness |
|---|---|---|---|---|
| RDG-A | **45** ✗ | 390 ✗ | 438 | atlas0:3 (P3): R305 = −2 |
| **RDG-B (primary)** | **0 — SURVIVES** | **23 ✗** | 27 | atlas0:3 (P3): R308 = −1/2, maxine = 1 tie-invariant |
| RDG-C | **17** ✗ | 324 ✗ | 348 | atlas0:3 (P3): R305 = −1 |
| RDG-D | **32** ✗ | 232 ✗ | 267 | atlas0:3 (P3): R305 = −1 |

Consequences per frozen stop rule 3:
- **WOWII 305:** readings A/C/D rejected as mis-transcription (recorded,
  moved on). **RDG-B carries the entry forward** — consistent with proved
  sibling 306 being non-viable under any other parse.
- **WOWII 308: ALL FOUR readings are violated by applicable controls ⇒**
  entry-level outcome **STOP_CORRUPT_READING**. The pre-stated §3 prediction
  is CONFIRMED and sharpened: the refuting controls start at P3 itself
  (n=3: γ_t=2 > ½[1+2]), not only the diamond; all 23 RDG-B violations are
  TIE-BREAK-ROBUST (R < 0 at maxmax, i.e. under EVERY deterministic
  tie-break rule), so the survey's flagged maxine ambiguity is NOT load-bearing
  for the failure. As printed, 308 cannot be the statement DeLaViña's page
  carried alongside PROVED sibling 306.
- Survey correction recorded: the survey's "slack 1" (305) / "slack 0" (308)
  on C5[K2] correspond to profile rows of readings NbarA-excl / NbarB — both
  gate-dead here. Under the defensible reading RDG-B, C5 sits at EXACT
  EQUALITY for 305 (slack 0), making 305 a stronger wall than surveyed.

## 2026-08-26 — STEP 3: arsenal tightness map (305 / RDG-B) — ALL HOLD

Implementation note: the cycle-blowup builder was initially hardcoded to five
blobs (C7[Kk] came out disconnected); caught by an applicability assert before
any row was scored, fixed to `cycle_blowup`, builder regression added. Rows
below are from the corrected run. Both engines (A: enumeration certificate,
B: ILP/CBC Optimal) agree on every member; every row inside caps (total 4.3 s).

| member | n | γ_t (A=B) | max_e\|N̄\|_B | **R_B** | closed-form check |
|---|---|---|---|---|---|
| C5[K2] | 10 | 3 | 8 | **3** | ceil(2/3·4m)−3 ✓ |
| C5[K3] | 15 | 3 | 12 | **5** | ✓ |
| C5[K4] carrier | 20 | 3 | 16 | **8** | ✓ |
| C5[K5] | 25 | 3 | 20 | **11** | ✓ |
| C5[K6] | 30 | 3 | 24 | **13** | ✓ |
| C5[K7] | 35 | 3 | 28 | **16** | ✓ |
| C5[K8] | 40 | 3 | 32 | **19** | ✓ |
| C7[K2] | 14 | 4 | 14=n | **6** | shadow regime (diam 3): M=n ✓ |
| C7[K3] | 21 | 4 | 21=n | **10** | ✓ |
| C7[K4] | 28 | 4 | 28=n | **15** | ✓ |
| C9[K3] | 27 | 5 | 27=n | **13** | ✓ |
| B(4,4,3,4,3) | 18 | 3 | 15=n−w_min | **7** | ✓ |
| B(4,2,4,2,4) | 16 | 3 | 14=n−w_min | **7** | ✓ |
| B(4,1,4,1,4) | 14 | 3 | 13=n−w_min | **6** | ✓ |
| comp(C5[K4]) | 20 | 3 | 16 | **8** | — |
| T(7) | 21 | 4 | 17 | **8** | c_min=4 pinned |
| T(8) | 28 | 5 | 24 | **11** | ✓ |
| T(9) | 36 | 6 | 32 | **16** | ✓ |

Findings: (i) the frozen §3 identity `M = n − w_min, γ_t = 3` on C₅-blow-ups
is CONFIRMED at every positive weight tested — blow-up weights can never cross;
(ii) diameter ≥ 3 members sit exactly at `M = n` (shadow boundary empirical);
(iii) under the defensible reading, NO arsenal member sits on the wall —
arsenal min slack = 3 (C5[K2]); the true RDG-B equality points are small dense
controls (C5, K1,3, diamond, P3-class), which the frozen families below probe.
308 has no family rows here: its entry stopped at the gate (STEP 2), per
contract §5 ("rows computed for every reading that survives the 308 gate").

## 2026-08-26 — STEP 4: frozen families F1–F4 + F6 (305 / RDG-B) — ALL HOLD

Engine A on every member; ILP spot agreement 10/10 sampled F1 members;
zero violations; `family_rows.json`.

- **F1 (243 unequal C5-blow-ups, w_i∈{1,2,3}^5):** γ_t = 3 pinned on ALL
  members; closed form `R = ceil[(2/3)(n − w_min)] − 3` matches EXACTLY on all
  243 (PREDICTION CONFIRMED arm-wide). R range 0..5; the single R=0 member is
  w=(1,1,1,1,1) = C5 itself.
- **F2 (T(5), T(6)):** γ_t = 3, 4; M = 6, 11; R = 1, 4 (joins T(7..9) from
  STEP 3: c_min pinned at 4, RHS grows quadratically — mechanism documented).
- **F3 (CP(k), k=2..7):** perfect PIN-FLAT equality wall — γ_t = 2 AND M = 2,
  R ≡ 0 along the whole knob. Both sides move together; no separation possible
  in maximal twin-density structures.
- **F4 (10 complete multipartites):** all hold; M = p_max as predicted;
  equality iff p_max ≤ 3 (γ_t pinned at 2).
- **F6 (control arm ℓ=1,2,3 = C5, C6, C7):** R = 0, 0, 1 — metric growth leaves
  the wall upward; NEW equality point discovered at **C6** (γ_t=4 = ceil[⅔·6]),
  alongside C5.

## 2026-08-26 — STEP 5: F5 exhaustive connected-n=8 extension — ALL HOLD

Generation: connected atlas-7 graph + one attached vertex over every nonempty
neighborhood subset (108,331 raw candidates), WL-hash bucketing + explicit
isomorphism dedupe ⇒ **11,117 unique connected graphs on 8 vertices** — exactly
the known count of connected order-8 graphs, validating the generator.
K8 itself: RDG-B term undefined ⇒ NOT_APPLICABLE (1 row). All others scored
exactly (engine A):

- violations: **0**
- exact equality walls (R = 0): **16** graphs
- minimum positive slack: **1**
- population with the only possible crossing shape (γ_t ≥ 4 ∧ M ≤ 5): **0**

With the STEP 2 gate this makes n ≤ 8 EXHAUSTIVE and clean under 305/RDG-B;
for n ≥ 9 the frozen §3 obstruction identity requires a diameter-2 graph with
γ_t ∈ {3,4} and twin-density c_min ≥ n − 5, a regime the families show pins
γ_t ≤ 2–3 instead. Budgets: F5 total 18.9 s against its 900 s aggregate cap.

## 2026-08-26 — STEP 6: step-aware sign check (METHOD v1.7 R1) — SATISFIED

- The residual's only rounding operator is ceil[(2/3)·M]. Across F1 the
  argument M = n − w_min assumes EVERY integer value 4..14, so the run crosses
  repeated rounding discontinuities (R advances 0→1→2→3→4→5 through M=4..14);
  the C5[K_m] arsenal run continues M = 4m to 32. No sign-zero conclusion rests
  on adjacent-member constancy anywhere.
- CP(k)'s constant R ≡ 0 wall (M pinned at 2) is explicitly NOT treated as a
  stop: per v1.7 R1 it is an under-sampled-looking constant that the widened
  runs (F1, F2, F6, arsenal) show to be a genuine pin, not a sampling artifact.

## 2026-08-26 — STEP 7: VERDICTS

See RESULT.md (same directory). Summary:
- **WOWII 305: HOLD_BOUNDED (reading RDG-B)** with PREDICTION_CONFIRMED closed
  forms on F1/arsenal; readings A/C/D rejected at gate as mis-transcriptions;
  survey slack figure corrected (C5 is an exact equality point under RDG-B).
  Zero crossings over 1,013 controls + 243 + 13 + 10 + 6 + 11,117 designed/
  exhausted members. No KILL_CANDIDATE arose ⇒ no novelty audit or Lean
  certificate owed.
- **WOWII 308: STOP_CORRUPT_READING** — all four plausible readings of
  |N̄(e)| are violated by applicable atlas controls (RDG-B: 23 tie-break-robust
  violations starting at P3 itself); the printed statement cannot be what the
  page carried alongside proved sibling 306.
