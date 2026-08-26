# ARSENAL.md — extended SRG / explicit arsenal for the 2026-08-26 sweep

## What this arsenal is

The old campaign's separating families capped out at `T(9)` (n=36). This
sweep extends the cap to **n = 120** with certified extended-SRG and explicit
structured graphs. The lever: metric/spectral terms (diam, ecc_avg, dist
stats, spectral radius, transmissions) grow **linearly** in n across these
families, while hereditary induced invariants (α, f, b, tree, path) grow like
~n/2 or slower. Open WOWII/AGX inequalities mixing a hereditary LHS with a
metric/spectral RHS must crack somewhere between T(9) and T(16) if they are
false at all.

## Families (all built by `scripts/build_arsenal.py`; cache/arsenal.gpickle)

| Family | Members | n range | Notes |
|---|---|---|---|
| `T(n)` = L(K_n) | n = 10..16 | 45..120 | SRG (v=C(n,2), k=2(n-2)); α = ⌊n/2⌋ exactly |
| `KG(n,2)` = comp(T(n)) | n = 10..16 | 45..120 | complement spectrum; α = n−1 |
| `Paley(q)` | q ∈ {13,17,29,37,41,53,61,73,89,97,101} | 13..101 | self-complementary SRG; closed-form spectra (−1±√q)/2 |
| `CP(m)` = K_{2,…,2} | m = 2..8 | 4..16 | complete multipartite; α=2, ω=m |
| `CMP(m)` = K_{2,…,2,1} | m = 2..8 | 3..15 | non-regular control family |
| `comp(C5[K_m])` | m = 2..8 | 10..40 | the campaign's namesake carrier family, blown up further |
| `C7[K3]`, `C9[K3]` | — | 21, 27 | odd-cycle blow-ups |
| `K(3,3)`, `K(3,3,3)` | — | 6, 9 | multipartite calibration |

50 graphs total. Vertex-transitivity is **certified** for every graph except
the CMP(m) family: explicit automorphism generators are constructed per
family and verified to preserve edges, and the orbit of vertex 0 is verified
to cover V (`arsenal_meta.json: vt.orbit_full/perms_valid`). This licenses
the O(1) λ(v) evaluation on VT graphs (constant local independence).

## Verification performed before trusting the cache (Gate 1)

`scripts/verify_cache.py` — independent recomputation, deliberately written
against different algorithms than `invlib.py`:

1. **Meta consistency** over all 50 graphs (n, m, δ, Δ vs pickle).
2. **Closed-form structure + exact spectra** over every family member:
   - `T(k)`: v=C(k,2), k-regular of degree 2(k−2); spectrum {2(k−2)¹,
     (k−4)^{k−1}, (−2)^{C(k,2)−k}} — multiplicities verified numerically.
   - `KG(k,2)`: degree C(k,2)−1−2(k−2); spectrum {top¹, (−(k−3))^{k−1},
     (+1)^{C(k,2)−k}}.
   - `Paley(q)`: degree (q−1)/2; eigenvalue (q−1)/2 once and each root of
     (−1±√q)/2 with multiplicity (q−1)/2.
   - `CP(m)`: spectrum formula check.
   All 50/50 PASS.
3. **Deep spot-checks** on T(12), comp(C5[K3]), CP(3), KG(13,2): fresh
   recomputation of n, m, degrees, deg_avg, residue (fresh Havel–Hakimi),
   diam/rad (networkx eccentricity), triangles (matrix trace), matching,
   connectivity, plus **independent ILP recomputation of α and γ_t** on the
   small graphs (pulp/CBC, fresh formulation). All PASS.

Verdict: **cache certified trustworthy** as of 2026-08-26.

## Certification battery (per graph; `certify.py`, resumable)

Poly side: degree stats, modes/medians/quartiles, residue, HH-steps,
annihilation, Caro–Wei, maxine, Welsh–Powell(bar), degeneracy G & bar,
length², eccentricities, dist_even/odd, transmissions, horizontal edge
counts, radial circles, triangle/K4-per-vertex sequences, disparity,
edge-neighborhood sizes, named-set cards, dp/2-B pairs, C4-free indicator,
proximity/remoteness/avg-distance (exact numerator+denominator), Randić.

NP-hard side (exact or BRACKET — never guessed):
α (Tomita bitset BnB), ω (BnB), λ(v)-battery (per-vertex BnB),
γ, γ_t, γ_2, i (ILP/CBC 60 s), α′ critical independence (two-stage ILP),
α₂ dissociation (BnB), f/tree (induced-forest BnB), b (2-coloring BnB),
induced path (DFS BnB), path cover p(G) (Hamiltonian-path witness ⇒ 1),
L_s (directed-flow spanning-tree ILP). Each carries
`{"value", "certified": bool}`; timeouts keep the incumbent tagged
uncertified → readings go BRACKET, never VIO off an unproved number.

Spectra are stored numerically for screening but every violation touching a
spectral term must be re-derived from the family closed forms above (exact).

## Process notes

- The interrupted predecessor job's `certify.py` process was found **still
  running** on resume (PID had completed T(14), KG(14,2)); it was left to
  finish the remaining arsenal graphs serially rather than duplicated.
- Two latent bugs were found and fixed in `xctx.py` before sweeping:
  (a) `lambda_per_vertex` passed the time-cap where the vertex argument
  belongs (would silently return λ(v₀) for all v); (b) a dead
  `BracketTimeout` handler let *uncertified* incumbents flow into readings
  as exact values. Both paths now raise Undef → BRACKET unless exactly
  proved, and exploit the certified vertex-transitivity to compute one
  representative value where legal.

## Sweep outcomes (same day)

- WOWII: all 220 open entries evaluated against all 50 certified graphs
  (~30k reading-graph decisions; 3,191+ holds at 23 contexts pre-final,
  final tallies in VERDICTS.md). Six entries flagged VIOLATED_CANDIDATE;
  every flag resolved by gates: two were prior kills re-witnessed
  (#63/#64 on new families), four failed the DB-sanity gate as
  mis-transcriptions (#111 readings A/C/D, #235, #255, #256).
- AGX: 70 open entries screened; 12 survey conjectures fully evaluated
  (holds/brackets), 2 candidates gate-discarded, 56 Form-1 OCR rows
  recorded UNPARSEABLE_SOURCE rather than guessed.
- BRACKET policy: f/tree/b/path/L_s on T(14..16), KG(14..16,2) and large
  Paley graphs exceeded exact-solve caps and are recorded as uncertified
  incumbents; no verdict anywhere relies on a guessed value.

## Verdict-file map

- `VERDICTS.md` — consolidated running table (WOWII + AGX).
- `SWEEP_LEDGER.md` — append-only batch log incl. correction pass.
- `candidates_verdicts.json`, `corrected_verdicts.json`,
  `candidates_agx.json`, `candidates_report.json` — machine-readable.
- `scripts/` — verify_cache.py (gate 1), certify.py/certify_sanity.py,
  spectra_exact.py (exact closed-form spectra), sweep.py + agx_sweep.py
  (drivers), sanity_gate.py in gate/ (DB-sanity gate),
  recompute_independent.py (independent recomputation),
  collect_candidates.py / process_candidates.py (triage).
