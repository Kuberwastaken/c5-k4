# RESULT — open_sweep2 (2026-08-26): WOWII 183 wall-navigation trial

**Primary outcome: `HOLD_BOUNDED`.** No crossing. Published zero.

- Target: WOWII 183, `L_s + b ≥ Δ(G²) + 2·rad(G²)` (open, page marker O,
  2005). Rank 1 of the survivor survey (`SURVEY.md`).
- Contract frozen before any family evaluation (`TRIAL_CONTRACT.md`), with a
  disclosed pre-evaluation grid tightening (13 members, n ≤ 16).
- Database-sanity gate: **1,013 rows, 0 violations, 0 incomplete** (995
  connected Atlas graphs n≤7; C5–C9, P7, Petersen, K3,3, K7, K1,n, Kn,n,
  T(7) via the exact König line-colouring route). C5/C6/C7/K3/K7 are
  themselves exact-tight — the proved diameter-two baseline shadow.
- Trial: both independent engines agreed on all 13/13 family rows;
  min R = 0, no negative residual anywhere. Full table in `TRIAL_LOG.md`.
- Step-aware sign check (v1.7 R1): residuals advance along every ℓ-run
  (no under-sampled dR=0 stop); sign genuinely positive past the plateau.
- Frozen prediction refuted and recorded: subdivision does not separate the
  terms — db/dℓ ∈ {0,+2} tracks dγ_c/dℓ = +1 while rad(G²) saturates at 2,
  so R is non-decreasing on the whole transformation class.

Durable conclusions:

1. The subdivided-join coordinate for 183 is CLOSED by bounded evidence plus
   the measured monotone identity. Any future 183 lane must change the
   quotient geometry, not subdivide further.
2. Sharpened theorem signal: a counterexample needs b to grow strictly slower
   than γ_c while G² stays nearly complete — induced-path-donating
   transformations are provably the wrong direction.
3. Cluster-mates 184/185 were not evaluated (outside frozen scope); they
   remain same-wall cluster candidates with their own RHS terms untested.

Artifacts: `SURVEY.md`, `TRIAL_CONTRACT.md`, `TRIAL_LOG.md`,
`trial_183.py`, `gate_rows.json`, `family_rows.json`.
Venv used: `/Users/kuber.mehta/Personal-Projects/c5-k4/.venv/bin/python`
(networkx 3.6.1). All arithmetic integer-exact; no process exceeded its cap
(max 0.66 s vs 60 s budget). No git operations performed.
