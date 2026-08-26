# RESULT — WOWII 255 + 256 prospective wall-navigation trials
(open_sweep2_20260826 / trial_255_256; contracts frozen before any
development-family evaluation; method: METHOD.md v1.0 phases 0A–7 +
METHOD_V1_7 R1; retry agent — prior agent died pre-work, zero artifacts
inherited)

## Verdicts (per entry per reading)

| entry | reading | verdict |
|---|---|---|
| **WOWII 255** | RD-A (union-incl; `maxN(e)=max_{uv∈E}|N({u,v})|`) | **HOLD_BOUNDED** |
| **WOWII 255** | RD-B (hint-excl; `\|(N(u)∪N(v))\{u,v}\|`) | **STOP_CORRUPT_READING** |
| **WOWII 256** | RD-A | **HOLD_BOUNDED** |
| **WOWII 256** | RD-B | **STOP_CORRUPT_READING** |

Primary outcome: **both entries HOLD under the only gate-viable reading.**
Published zeros. No KILL_CANDIDATE arose; no novelty audit or Lean certificate
is owed.

## What was run

- **Contracts frozen first** (`TRIAL_CONTRACT_255.md`, `TRIAL_CONTRACT_256.md`):
  source-verbatim statements from `data/wowii-conjectures.json`; every
  plausible denominator parse tabled as its own reading-row (RD-A verbatim-def
  open-union — provably identical to the closed-union convention since u~v;
  RD-B glossary-compute-hint variant with endpoints excluded; intersection
  parse rejected as contradicting the verbatim text); exact Fraction residuals
  `R = γ_t − 2·num/maxN`; gate plan; frozen 34-member grid (arms W/P/B/L,
  n ≤ 21); obstruction identities OI-1..OI-6; stop rules.
- **Database-sanity gate:** 1,015 controls (995 connected Atlas graphs n≤7;
  C5–C9, P7, Petersen, K3,3, K7, stars K_{1,3}–K_{1,8}, K_{n,n} n=2..6).
  RD-A: **0 violations** on both entries. RD-B: violated by 272 controls
  against 255 and 118 against 256 — including K3, C7 (exactly the survey's
  warning), every cycle C5–C9, Petersen, K7, all K_{n,n} — plus division-by-
  zero at K2. RD-B is corrupt as a transcription of Graffiti.pc intent for
  BOTH entries; recorded, evaluation continued under RD-A only.
- **Tightness map (arsenal):** all 14 members hold; min slack exactly **1/2**
  (shared by C5[K_m] m=2..8 — m-invariant per OI-3 — comp(C5[K4]), C7[K3],
  C9[K3]); Petersen 2/3; T(7)/T(8)/T(9) = 6/5, 17/9, 18/7 (γ_t(T(t)) = t−3,
  margin widens as predicted).
- **Frozen family:** 37 rows constructed and evaluated (34 planned + 3 base
  rows, disclosed), both independent engines (pulp/CBC ILP vs pure-python
  branch-and-bound) agreeing on EVERY coordinate of EVERY row, max 0.064 s vs
  the 60 s cap. **No negative residual anywhere** under either entry.
- **Step-aware sign check (R1):** all six frozen runs evaluated in full before
  any sign conclusion; runs advance/oscillate through SIX exact equality-wall
  zeros without going negative; no dR=0 stall anywhere.

## Durable conclusions

1. **The wall is an attracting manifold, and its mechanism is now identified.**
   Every observed zero is an instance of OI-1/OI-2: γ_t = 2 forces maxN = n
   (the TD edge sees everything) so RHS ≤ 2 with equality iff |C| = n (or
   |N(A)| = n for 256); triangle-free vertex-transitive graphs give
   RHS = n/Δ ≤ γ_t with equality exactly at efficient-open-domination members.
   Chord additions that create TD pairs halve γ_t but simultaneously collapse
   |C| or pin |N(A)| = V — the residual cannot go negative through this door.
2. **The pair separates structurally, not numerically:** Q3+antipodal-chord and
   C6+chord are exact zeros for 256 while positive (3/2, 4/3) for 255 — 256's
   numerator |N(A)| pins to V under chord surgery where |C| collapses. Any
   future differential attack on the pair should start from chord/TD-pair
   surgery on near-wall regulars.
3. **Nonuniform blow-ups are provably harmless here:** OI-3's closed form
   R = 3 − 2Σw/(Σw − min w) ∈ [1/2, 1) was confirmed EXACTLY on all six weight
   vectors — blob knobs move maxN but can never push RHS past 5/2 < γ_t = 3.
   This closes the survey's "nonuniform blobs change |C| and maxN(e)"
   exploitability note: they change both, in the safe direction.
4. **Survey correction (recorded):** the excl-parse is gate-dead for BOTH
   entries (survey phrased it via 256/C7); and C6 is NOT exact-tight for this
   pair (R = 1: γ_t(C6) = 4 ≠ 3 = n/Δ).

## Calibration disclosures

Three hand-derived predictions were machine-caught wrong and amended
(timestamped Amendment blocks in both contracts, BEFORE any family row was
evaluated): γ_t(C6) = 4 not 3; |C(C7)| = 7 not 1 (vertex-transitive ⇒
self-centered); Q3+chord lands at 3/2 not 0 (diam stays 3 ⇒ |C| = 2). The
first fixture pass FAILED on two rows and was re-frozen; fixtures then passed
13/13. All hand-predictions that survived (B-arm formula, prism zeros at
n ∈ {3,6}, Petersen 2/3, arsenal 1/2-walls, T(t) widening) are flagged in
TRIAL_LOG.md.

## Artifacts

`TRIAL_CONTRACT_255.md`, `TRIAL_CONTRACT_256.md`, `TRIAL_LOG.md`,
`trial_255_256.py`, `fixtures.json`, `gate_rows.json`, `arsenal_rows.json`,
`family_rows.json`. Venv: `/Users/kuber.mehta/Personal-Projects/c5-k4/.venv/bin/python`
(networkx 3.6.1, pulp 3.3.2). All arithmetic exact Fractions/integers; no
spectral quantities used (1e-6 guard vacuous; ties never kills). No process
exceeded its cap. No git operations performed.
