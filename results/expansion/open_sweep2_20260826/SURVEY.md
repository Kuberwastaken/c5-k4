# Open WOWII survivor survey — open_sweep2, 2026-08-26

Purpose: rank the OPEN *Written on the Wall II* entries that remain un-killed,
un-stopped, and exactly-tight (or nearly so) on the campaign arsenal, after the
complete sweeps (`results/open_sweep/` batches 0–5, `results/family_domination.md`,
`results/expansion/prospective_*` ledgers). One prospective navigation trial is
launched from rank 1 (see `TRIAL_CONTRACT.md` in this directory).

## Inclusion criteria

(i) holds on the entire known arsenal (carrier, C₅[K_m] m∈{2..8}, C₇[K₂..₄],
C₉[K₃], nonuniform B(4,4,3,4,3)/B(4,2,4,2,4)/B(4,1,4,1,4), comp(C₅[K₄]), T(7..9));
(ii) not in the stopped/closed set **{19, 40, 61, 133, 200, 141, 59}**
(WOWII 19/40/61/133 moves FAILED and CLOSED; 200 closes as prior art; 141/59
proof work stopped);
(iii) exact-tightness data near the arsenal: zero or tiny slack on some arsenal
member (equality-wall candidates).

## Exclusions applied before ranking

| exclusion | entries | reason |
|---|---|---|
| killed by campaign | 63, 64, 85, 309, 172, 176, 181, 430a | gate-surviving disproofs already published/upstream |
| corrupt as published | 401b, 412f, 448b | violated inside Graffiti.pc's own database; original wording needed |
| stopped set | 19, 40, 61, 133, 200, 141, 59 | OVERARCHING_PLAN stop discipline |
| theorem-shadowed | 438b | attempted separation yielded a stronger arbitrary-subset theorem *proving* it |
| operation class closed | 382e, 422b, 430c, 434c, 169/174/180/182, 184/185-tier barbell moves for 176 | published HOLD_BOUNDED trials closed their frozen transformations (method_v02_382e: 212,502 substitutions + 20,000 weight samples; method_v01_422b: quotient-level no-crossing proof) |

## Ranked survivors

Slack source: `results/family_profiles/*.verdicts.json` (13-graph arsenal),
`results/open_sweep/batch*.jsonl` (carrier), and analytic identities for the
L_s+b cluster (below). Ranking: (a) slack at the wall (smaller better);
(b) natural integer transformation knobs; (c) hereditary induced invariant
(f/b/tree/path/α) on the wall — the pin-flat-vs-metric-growth mechanism;
(d) whether the coordinate is genuinely untried.

| rank | entry | statement (residual form) | min slack on arsenal | knobs | hereditary term | prior trials | exploitability notes |
|---:|---|---|---|---|---|---|---|
| 1 | **183** | `R = L_s + b − Δ(G²) − 2·rad(G²)` | **0** (exact, entire C₅[K_m] and nonuniform-B arsenal; analytic: G²=K_n, L_s=n−γ_c=5m−3, b=4 ⇒ 5m+1=5m+1) | subdivision length ℓ of a rim join, blob vector (w₀..w₄), bridge widths | **yes — b** (induced bipartite number), the exact invariant the cliff paper proves pins flat under blow-up while metrics grow | theory lane only (theorem signal, pendant-clique lemma ladder); **no frozen separating-family navigation trial ever run** | untried navigationally; diameter-2 region theorem-shadowed by the proved n+1 baseline, which tells the trial exactly where to leave diameter 2; cluster-mates 184/185 share the same wall and count as consequences of one trial |
| 2 | **255 / 256** | `γ_t ≥ 2|C|/max N(e)` (resp. 2|N(A)|/max N(e)) | **0.5** under the only gate-viable reading (incl-endpoints), uniformly on every arsenal member (fractional RHS — real crossing potential) | blow-up m (RHS ratio is m-invariant: 2·5m/4m = 2.5), nonuniform blobs change \|C\| and max N(e) | no — center-set/edge-neighborhood metrics only | none | excl-endpoints reading is gate-dead (fails on C7 itself) so reading fragility is high; no hereditary pin mechanism; γ_t NP-hard but small-n exact |
| 3 | **232 / 233** | `γ_t ≥ ½(rad + ecc(B))`; `γ_t ≥ ⅔(1+ecc(B))` | 1 (3 vs 2 on C₅[K_m]) | subdivision length grows rad/ecc(B) linearly while γ_t may lag | no | none | metric-vs-metric walls; γ_t tends to track radius, weak mechanism |
| 4 | **308** | `γ_t ≤ ½(maxine + min|N̄(e)|)` | 0 on C₅[K₂] | blob sizes, complement surgery | maxine is greedy-independent (α-adjacent) but tie-order-dependent | rejected once at selection (tie-order-dependent Maxine term) | upper-bound wall needs γ_t to JUMP while RHS pins; reading-risk flagged |
| 5 | **305** | `γ_t ≤ ceil[⅔·max |N̄(e)|]` | 1 (3 vs 4 on C₅[K₂]) | complement-edge neighborhoods via blob geometry | no | v0.5 trial EXCLUDED (protocol deviation) — **never validly scored**, fresh contract legal | clean slate but weak mechanism; ceiling step function (R1 caveat applies) |
| 6 | **247** | `γ_t ≥ 2p(G)` (regular) | 1 | regular blow-up families; p = path-cover number | p is path-cover-adjacent (hereditary flavor) | none | regularity hypothesis restricts knobs to regular families |
| 7 | **268 / 271** | `γ_t ≥ floor(1+dist_avg(C))`; `γ_t ≥ ceil(sqrt(2 dist_max(M)))` | 1 | metric growth via subdivision | no | none | rounding-operator walls (R1 step-aware check mandatory); slow-growing RHS makes crossing hard |
| 8 | **402** | `γ₂ ≤ 2(isolates(A_δ) + \|{v: \|N(v)∩A_Δ\|=1}\| + γ_t)` | 1 (comp(C₅[K₄])) | degree-layer surgery on complements | partial (isolates/degree layers) | none | many moving parts on the RHS; hard to predict signs |
| 9 | **310** | `γ_t ≤ ceil(1 + Tdist_min(v)/3)` | 3 | dense-small-transmission + large-γ_t tension | no | none | large slack; listed for completeness |

## Why rank 1 is 183

1. **Zero slack, whole arsenal, analytic.** On every C₅-blow-up (uniform or
   nonuniform, any positive weights) the graph has diameter 2, so G² = K_n and
   the residual collapses to `(n − γ_c) + b − (n+1) = b − γ_c − 1 = 4 − 3 − 1
   = 0`. The window proofs in `results/family_domination.md` pin both sides.
2. **The mechanism fits.** The wall term carries `b`, the hereditary induced
   invariant the project's discretization-cliff paper proves stays flat
   (= 2r on C_{2r+1}[K_m]) while square-metrics grow — precisely the
   pin-flat-vs-grow mechanism the navigation method is designed to attack.
3. **Untried coordinate.** Prior 183 work is theorem-side (Wave A theory lane,
   pendant-wall lemma ladder, Lean tiers γ_c ≥ 3/4). No frozen separating
   transformation has ever been evaluated against it.
4. **Clean algebraic target.** With `L_s = n − γ_c` (Duchet–Meurisse), the
   residual is exactly
   `R = (b − γ_c) + (n − Δ(G²)) − 2·rad(G²)`,
   giving a frozen crossing inequality `γ_c − b > (n − Δ(G²)) − 2·rad(G²)`
   and a signed prediction per transformation knob.

Cluster note: 184 (`dist_avg(B(G²),V(G²))` variant) and 185 (`dist_avg(G²)`
variant) sit at the same equality point (21 = 21 on the carrier) and share the
entire LHS; any 183 consequence evaluates them jointly. They are recorded as
cluster consequences of the single rank-1 trial, not separate targets.

## Honest liabilities

- 183's diameter-2 regime is **theorem-shadowed**: the proved baseline
  `L_s + b ≥ n+1` (used to close 176/182–185 attacks) is exactly the 183
  inequality when G² = K_n. The trial must therefore operate outside diameter
  2, where the proved tier results (γ_c ≥ 3/4 cases formalized in Lean)
  further constrain the live region. This is stated up front: the plausible
  outcomes include a THEOREM_SHADOW stop, and a HOLD here is a published zero.
- Slack values for ranks 2–9 come from float slacks in the profile JSONs
  (readings double-checked in the sweeps); rank 1's zero slack is exact/integer
  arithmetic.
