# Generic arm — results

Arm 2 of the preregistered three-arm test ([`PREREGISTRATION.md`](PREREGISTRATION.md), tag `prereg-three-arm-v1`), run blind to the other two arms.

**Written incrementally; last update 2026-08-16T15:13:01Z.**

## Method

Search without structural insight. Four mechanical generators, run as a fixed deterministic sequence of work units so that a staged run reproduces a single long run exactly:

| unit | what it does |
|---|---|
| `FAM` | standard random families over a wide order and density range: `G(n,p)` for `p = 0.08..0.92`, random `d`-regular, random bipartite, uniform random trees (Prüfer), Barabási–Albert preferential attachment, random geometric. Orders `9..n_max`. |
| `SWEEP` | near-exhaustive sweep beyond `D`: every connected graph on 9 vertices has a non-cut vertex, so extending every `n = 8` member of `D` by one vertex over all 255 non-empty neighbourhoods covers `n = 9` exhaustively up to isomorphism. Bases are visited in increasing order of their slack. |
| `GROW` | beam search: keep the lowest-slack graphs found at each order and extend them by one vertex over sampled neighbourhoods. |
| `ANNEAL` | simulated annealing minimising the target's slack, moves = single edge flips plus degree-preserving double-edge swaps, restarted from many seeds across the order range. |

`n_max` per target is set by a probe: the largest order in `10..40` at which one exact evaluation of that target costs ≤ 80 ms. Tightness/slack data from `population.json` is used only as a numeric objective and as a seed ordering; no equality member is analysed structurally and no purpose-built family is constructed.

**Budget.** 1 CPU-hour per target (`time.process_time` of that target's own process), the preregistered cap. `HELD` means the cap was spent without a crossing; `BRACKET` means the run stopped before the cap.

## Evaluator and gates

`scripts/exp/generic/ginv.py` is an independent implementation of the 42 invariants the 30 targets use, written from the `invariant_definitions` shipped in `population.json`; it shares no code with `scripts/gen/invariants.py`. Exact `int`/`Fraction` arithmetic throughout.

* invariant cross-check against `scripts/gen/invariants.py` on 1255 graphs of `D`, against **both** gen backends (exhaustive `2^n` and branch-and-bound), over all 42 invariants the population uses: **0 mismatches**
* invariant cross-check against the `scripts/gen` branch-and-bound backend on 68 graphs with `n = 9..24` outside `D` (random `G(n,p)` at four densities, paths, cycles, complete graphs): **0 mismatches**
* spectral audit: `floor(lambda_1)` is identical under both conventions on all 12,112 members of `D`. `ceil(lambda_1)` differs on **19** of them: `scripts/gen/invariants._spectral_bracket` returns `ceil = floor` whenever `det(floor*I - A) = 0`, i.e. whenever `floor(lambda_1)` happens to be *some* eigenvalue, not necessarily the largest. On all 19 the arm's value is the one that matches the actual spectral radius (e.g. `Dh_`, lambda_1 = sqrt(3) = 1.7320508…: the arm gives `ceil = 2`, the generator gives `ceil = 1`).
* all 30 frozen targets re-evaluated over all 12,112 members of `D` through this arm's own evaluator: **0 counterexamples under both conventions**. Under the generator's convention every recorded equality count, min slack and max slack reproduces exactly (0 mismatches). Under the definition-faithful convention the equality count of FP-008 differs, because that target's right-hand side depends on `ceil(lambda_1)`.

Every candidate crossing must pass both of the required gates, and this arm adds a third check of its own:

* **(a) second code path** — the witness is recomputed by `scripts/gen/invariants.py` (backend `scal`, plus the exhaustive `2^n` backend `brute` when `n ≤ 20`) and re-evaluated by `scripts/gen/expressions.py`; LHS, RHS and slack must agree exactly and the slack must be negative;
* **(b) database-sanity gate** — the same reading is re-evaluated over all 12,112 members of `D` (rebuilt from `scripts/gen/`); it must produce zero counterexamples there and reproduce the recorded equality count. A reading that also refutes members of `D` is a bug and is discarded.

* **(c) third code path** (not required by the protocol; added here) — every crossing is recomputed a third time from different algorithms again: `networkx` primitives for the polynomial invariants and the matching number, `networkx.max_weight_clique` for `alpha`/`omega`/`lambda(v)`, the chromatic number as an exact minimum cover of `V` by independent sets, and the four domination numbers by naive `itertools` enumeration over all vertex subsets in increasing size (`scripts/exp/generic/audit_crossings.py`).

Two protocol notes, recorded because they affect how this arm should be read:

* A first pass of this arm was run and DISCARDED before any verdict was recorded, because profiling showed the arm's exact spectral test was slow enough to cap the searchable order at n=9 for the two targets that use floor(lambda_1) (FP-019, FP-026). The evaluator was rewritten (fraction-free integer Sylvester test) and the whole arm restarted from unit 0 with the final code, so every target was searched by one and the same instrument. No verdict from the discarded pass was carried over.
* While fixing that, the arm found that scripts/gen/invariants._spectral_bracket returns ceil(lambda_1) = floor(lambda_1) whenever floor(lambda_1) is an eigenvalue, even when it is not the largest one; that is wrong on 19 of the 12,112 members of D. It affects exactly one target, FP-008, whose right-hand side is floor(A / ceil(lambda_1)). The arm searches under the definition-faithful convention, which is the harder one for this target (a larger ceil makes the right-hand side smaller and the '>=' easier to satisfy), and every crossing is required to be a crossing under BOTH conventions.

Witnesses are then reduced mechanically (greedy vertex deletion while connected and slack < 0), which is why several are much smaller than the graph the search first hit.

## Counts

| verdict | targets |
|---|---|
| CROSSED | 14 |
| HELD | 16 |
| **total** | **30** |

## Per-target results

| id | statement | verdict | witness (graph6) | n | LHS | RHS | found by | CPU s | gate (a) | gate (b) | gate (c) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| FP-001 | `alpha <= ceil((Tdist_max - dist_even_min)/2) + 1` | **HELD** | — | — | — | — | — | 3600.01 | n/a (no candidate) | n/a (no candidate) | n/a (no candidate) |
| FP-002 | `alpha >= dist_even_max - chi` | **CROSSED** | ``L`cAwH@CxsVySP`` | 13 | 5 | 6 | FAM | 0.04 | PASS | PASS | PASS |
| FP-003 | `alpha >= lambda_max - cutv` | **HELD** | — | — | — | — | — | 3600.01 | n/a (no candidate) | n/a (no candidate) | n/a (no candidate) |
| FP-004 | `A >= floor((disp_min)/2) + dist_avg` | **HELD** | — | — | — | — | — | 3600.0 | n/a (no candidate) | n/a (no candidate) | n/a (no candidate) |
| FP-005 | `A >= floor((n)/(gamma_t))` | **HELD** | — | — | — | — | — | 3600.07 | n/a (no candidate) | n/a (no candidate) | n/a (no candidate) |
| FP-006 | `chi >= ceil((omega - chi_regular)/2) + 1` | **HELD** | — | — | — | — | — | 3600.05 | n/a (no candidate) | n/a (no candidate) | n/a (no candidate) |
| FP-007 | `diam <= disp_max + gamma_2` | **CROSSED** | `HAgcACO` | 9 | 8 | 7 | FAM | 8.46 | PASS | PASS | PASS |
| FP-008 | `diam >= floor((A)/(ceil(lambda_1)))` | **CROSSED** | `L???????????~~` | 13 | 2 | 3 | FAM | 0.65 | PASS | PASS | PASS |
| FP-009 | `gamma <= floor((lambda_avg)/2) + res` | **CROSSED** | `N?I@?CAOCc?C?C?Gg??` | 15 | 7 | 6 | FAM | 0.19 | PASS | PASS | PASS |
| FP-010 | `gamma <= gamma_2 - chi_C4free` | **HELD** | — | — | — | — | — | 3600.4 | n/a (no candidate) | n/a (no candidate) | n/a (no candidate) |
| FP-011 | `gamma >= ceil((Tdist_min)/(m))` | **HELD** | — | — | — | — | — | 3600.03 | n/a (no candidate) | n/a (no candidate) | n/a (no candidate) |
| FP-012 | `gamma_2 <= dist_even_max - chi_regular + 2` | **CROSSED** | `IkQ?K@?G?` | 10 | 8 | 7 | FAM | 0.2 | PASS | PASS | PASS |
| FP-013 | `gamma_2 >= ceil((Delta)/(Sigma_2))` | **HELD** | — | — | — | — | — | 3600.26 | n/a (no candidate) | n/a (no candidate) | n/a (no candidate) |
| FP-014 | `gamma_2 >= floor((dist_even_min + disp_min)/2)` | **CROSSED** | `Q??????k|{Y[ao~w^gD~?[wBm??` | 18 | 5 | 6 | FAM | 0.42 | PASS | PASS | PASS |
| FP-015 | `gamma_i <= diam + mu - 1` | **CROSSED** | `UqP?GP?GC?G?C?C?C??G?O?A??A???O?A???G???` | 22 | 11 | 10 | FAM | 0.22 | PASS | PASS | PASS |
| FP-016 | `gamma_i <= floor((alpha)/2) + gamma` | **CROSSED** | `I_A_L?SVO` | 10 | 5 | 4 | ANNEAL | 103.23 | PASS | PASS | PASS |
| FP-017 | `gamma_t >= floor((cutv + chi_tree)/2) + 1` | **HELD** | — | — | — | — | — | 3600.0 | n/a (no candidate) | n/a (no candidate) | n/a (no candidate) |
| FP-018 | `gamma_t >= floor((gamma)/(disp_min))` | **HELD** | — | — | — | — | — | 3600.79 | n/a (no candidate) | n/a (no candidate) | n/a (no candidate) |
| FP-019 | `kappa <= floor((t)/2) + floor(lambda_1)` | **HELD** | — | — | — | — | — | 3600.86 | n/a (no candidate) | n/a (no candidate) | n/a (no candidate) |
| FP-020 | `kappa >= floor((disp_avg - ecc_avg)/2) + 1` | **CROSSED** | `OwbWmk_vomazb?fvaRMYc` | 16 | 1 | 2 | FAM | 0.34 | PASS | PASS | PASS |
| FP-021 | `kappa >= floor((lambda_avg - disp_max)/2) + 1` | **CROSSED** | `M?~vfbokF_]?G?w??` | 14 | 1 | 2 | FAM | 30.15 | PASS | PASS | PASS |
| FP-022 | `lambda_max >= floor((dd - f_1)/2)` | **CROSSED** | `LZ~Rzv~}v^^~^~` | 13 | 2 | 3 | FAM | 0.01 | PASS | PASS | PASS |
| FP-023 | `lambda_max >= floor((gamma_2 - chi)/2) + 1` | **CROSSED** | `K_Q@@OO?gC@?` | 12 | 3 | 4 | FAM | 0.29 | PASS | PASS | PASS |
| FP-024 | `mu <= ceil((n - chi_tree)/2)` | **HELD** | — | — | — | — | — | 3600.22 | n/a (no candidate) | n/a (no candidate) | n/a (no candidate) |
| FP-025 | `mu >= floor((delta + lambda_min)/2)` | **HELD** | — | — | — | — | — | 3600.26 | n/a (no candidate) | n/a (no candidate) | n/a (no candidate) |
| FP-026 | `rad >= floor((disp_max)/(floor(lambda_1)))` | **HELD** | — | — | — | — | — | 3600.05 | n/a (no candidate) | n/a (no candidate) | n/a (no candidate) |
| FP-027 | `rad >= floor((ecc_avg)/2) + chi_bipartite` | **HELD** | — | — | — | — | — | 3600.01 | n/a (no candidate) | n/a (no candidate) | n/a (no candidate) |
| FP-028 | `res <= alpha + CW - 1` | **HELD** | — | — | — | — | — | 3600.01 | n/a (no candidate) | n/a (no candidate) | n/a (no candidate) |
| FP-029 | `res >= A - deg_avg` | **CROSSED** | `L?GOB@CcCC?OA?` | 13 | 5 | 67/13 | FAM | 0.0 | PASS | PASS | PASS |
| FP-030 | `res >= floor((dd)/(gamma_t))` | **CROSSED** | `H~Fwtnv` | 9 | 2 | 3 | FAM | 0.08 | PASS | PASS | PASS |

## Crossings in detail

### FP-002 — `alpha >= dist_even_max - chi`

* refuting graph (graph6, `n = 13`): ``L`cAwH@CxsVySP``
* at the witness: **LHS = 5**, **RHS = 6**, slack = -1
* found by: `FAM`; first hit at `n = 37` (``daXBGTD?siq?{PoT@C?ZWfrf?jJw@tiw[POeBLJAyFy?BnA{dCdOd^C?K{gGf@hxWTEqBJzTY}dx{oPzWmcFkM`GfHCY{\DjdBZ|Be|EGEoLPWgb``), then reduced to `n = 13`
* search cost: 0.04 CPU s (cap 3600 s); verification 8.36 CPU s
* gate (a) second code path: **PASS** — `scripts/gen` brute: LHS 5 / RHS 6, scal: LHS 5 / RHS 6
* gate (b) database sanity: **PASS** — 0 counterexamples over all 12,112 members of `D` through this arm's evaluator, 0 through the `scripts/gen` path on a 1500-graph sample; equality count 249 vs 249 recorded
* gate (c) third code path: **PASS** — LHS 5, RHS 6, slack -1
* invariants at the witness (third path): `alpha = 5`, `chi = 4`, `dist_even_max = 10`
* seeds: base `20276653`; BASE_SEED(20260815) + 7919 * int(id suffix); FAM unit k -> base+1000+k, ANNEAL unit k -> base+500000+k, GROW unit k -> base+900000+k, probe -> base XOR 0x5EED

### FP-007 — `diam <= disp_max + gamma_2`

* refuting graph (graph6, `n = 9`): `HAgcACO`
* at the witness: **LHS = 8**, **RHS = 7**, slack = -1
* found by: `FAM`; first hit at `n = 18` (`QC?@?PGBA??_?@?CA???CGAAA??`), then reduced to `n = 9`
* search cost: 8.46 CPU s (cap 3600 s); verification 10.50 CPU s
* gate (a) second code path: **PASS** — `scripts/gen` brute: LHS 8 / RHS 7, scal: LHS 8 / RHS 7
* gate (b) database sanity: **PASS** — 0 counterexamples over all 12,112 members of `D` through this arm's evaluator, 0 through the `scripts/gen` path on a 1500-graph sample; equality count 6 vs 6 recorded
* gate (c) third code path: **PASS** — LHS 8, RHS 7, slack -1
* invariants at the witness (third path): `diam = 8`, `disp_max = 2`, `gamma_2 = 5`
* seeds: base `20316248`; BASE_SEED(20260815) + 7919 * int(id suffix); FAM unit k -> base+1000+k, ANNEAL unit k -> base+500000+k, GROW unit k -> base+900000+k, probe -> base XOR 0x5EED

### FP-008 — `diam >= floor((A)/(ceil(lambda_1)))`

* refuting graph (graph6, `n = 13`): `L???????????~~`
* at the witness: **LHS = 2**, **RHS = 3**, slack = -1
* found by: `FAM`; first hit at `n = 14` (`M?????????????~~_`), then reduced to `n = 13`
* search cost: 0.65 CPU s (cap 3600 s); verification 9.62 CPU s
* gate (a) second code path: **PASS** — `scripts/gen` brute: LHS 2 / RHS 3, scal: LHS 2 / RHS 3
* gate (b) database sanity: **PASS** — 0 counterexamples over all 12,112 members of `D` through this arm's evaluator, 0 through the `scripts/gen` path on a 1500-graph sample; equality count 6 vs 7 recorded
* gate (c) third code path: **PASS** — LHS 2, RHS 3, slack -1
* invariants at the witness (third path): `annih = 12`, `diam = 2`, `spec_ceil = 4`
* seeds: base `20324167`; BASE_SEED(20260815) + 7919 * int(id suffix); FAM unit k -> base+1000+k, ANNEAL unit k -> base+500000+k, GROW unit k -> base+900000+k, probe -> base XOR 0x5EED

### FP-009 — `gamma <= floor((lambda_avg)/2) + res`

* refuting graph (graph6, `n = 15`): `N?I@?CAOCc?C?C?Gg??`
* at the witness: **LHS = 7**, **RHS = 6**, slack = -1
* found by: `FAM`; first hit at `n = 15` (`N?I@?CAOCc?C?C?Gg??`), then reduced to `n = 15`
* search cost: 0.19 CPU s (cap 3600 s); verification 8.87 CPU s
* gate (a) second code path: **PASS** — `scripts/gen` brute: LHS 7 / RHS 6, scal: LHS 7 / RHS 6
* gate (b) database sanity: **PASS** — 0 counterexamples over all 12,112 members of `D` through this arm's evaluator, 0 through the `scripts/gen` path on a 1500-graph sample; equality count 704 vs 704 recorded
* gate (c) third code path: **PASS** — LHS 7, RHS 6, slack -1
* invariants at the witness (third path): `gamma = 7`, `lam_avg = 28/15`, `res = 6`
* seeds: base `20332086`; BASE_SEED(20260815) + 7919 * int(id suffix); FAM unit k -> base+1000+k, ANNEAL unit k -> base+500000+k, GROW unit k -> base+900000+k, probe -> base XOR 0x5EED

### FP-012 — `gamma_2 <= dist_even_max - chi_regular + 2`

* refuting graph (graph6, `n = 10`): `IkQ?K@?G?`
* at the witness: **LHS = 8**, **RHS = 7**, slack = -1
* found by: `FAM`; first hit at `n = 13` (`LkQAC?@_A??@A?`), then reduced to `n = 10`
* search cost: 0.20 CPU s (cap 3600 s); verification 9.88 CPU s
* gate (a) second code path: **PASS** — `scripts/gen` brute: LHS 8 / RHS 7, scal: LHS 8 / RHS 7
* gate (b) database sanity: **PASS** — 0 counterexamples over all 12,112 members of `D` through this arm's evaluator, 0 through the `scripts/gen` path on a 1500-graph sample; equality count 17 vs 17 recorded
* gate (c) third code path: **PASS** — LHS 8, RHS 7, slack -1
* invariants at the witness (third path): `chi_reg = 0`, `dist_even_max = 5`, `gamma_2 = 8`
* seeds: base `20355843`; BASE_SEED(20260815) + 7919 * int(id suffix); FAM unit k -> base+1000+k, ANNEAL unit k -> base+500000+k, GROW unit k -> base+900000+k, probe -> base XOR 0x5EED

### FP-014 — `gamma_2 >= floor((dist_even_min + disp_min)/2)`

* refuting graph (graph6, `n = 18`): `Q??????k|{Y[ao~w^gD~?[wBm??`
* at the witness: **LHS = 5**, **RHS = 6**, slack = -1
* found by: `FAM`; first hit at `n = 27` (`Z?????????????????F}gnKxV]BH{D}fATJ?j~w@|]?]~g?~^w?k{w?]to??`), then reduced to `n = 18`
* search cost: 0.42 CPU s (cap 3600 s); verification 15.05 CPU s
* gate (a) second code path: **PASS** — `scripts/gen` brute: LHS 5 / RHS 6, scal: LHS 5 / RHS 6
* gate (b) database sanity: **PASS** — 0 counterexamples over all 12,112 members of `D` through this arm's evaluator, 0 through the `scripts/gen` path on a 1500-graph sample; equality count 85 vs 85 recorded
* gate (c) third code path: **PASS** — LHS 5, RHS 6, slack -1
* invariants at the witness (third path): `disp_min = 3`, `dist_even_min = 9`, `gamma_2 = 5`
* seeds: base `20371681`; BASE_SEED(20260815) + 7919 * int(id suffix); FAM unit k -> base+1000+k, ANNEAL unit k -> base+500000+k, GROW unit k -> base+900000+k, probe -> base XOR 0x5EED

### FP-015 — `gamma_i <= diam + mu - 1`

* refuting graph (graph6, `n = 22`): `UqP?GP?GC?G?C?C?C??G?O?A??A???O?A???G???`
* at the witness: **LHS = 11**, **RHS = 10**, slack = -1
* found by: `FAM`; first hit at `n = 39` (``fpa?OO__@?O?A?A?C?@????C??`???O????G?G?C??????OG????A???@???O????G?????O?@?????????a?????G???????G????C???????A?_?????@??????``), then reduced to `n = 22`
* search cost: 0.22 CPU s (cap 3600 s); verification 14.08 CPU s
* gate (a) second code path: **PASS** — `scripts/gen` scal: LHS 11 / RHS 10
* gate (b) database sanity: **PASS** — 0 counterexamples over all 12,112 members of `D` through this arm's evaluator, 0 through the `scripts/gen` path on a 1500-graph sample; equality count 3 vs 3 recorded
* gate (c) third code path: **PASS** — LHS 11, RHS 10, slack -1
* invariants at the witness (third path): `diam = 5`, `gamma_i = 11`, `mu = 6`
* seeds: base `20379600`; BASE_SEED(20260815) + 7919 * int(id suffix); FAM unit k -> base+1000+k, ANNEAL unit k -> base+500000+k, GROW unit k -> base+900000+k, probe -> base XOR 0x5EED

### FP-016 — `gamma_i <= floor((alpha)/2) + gamma`

* refuting graph (graph6, `n = 10`): `I_A_L?SVO`
* at the witness: **LHS = 5**, **RHS = 4**, slack = -1
* found by: `ANNEAL`; first hit at `n = 14` (`M[Gd_BgOKO[vXg\z?`), then reduced to `n = 10`
* search cost: 103.23 CPU s (cap 3600 s); verification 9.18 CPU s
* gate (a) second code path: **PASS** — `scripts/gen` brute: LHS 5 / RHS 4, scal: LHS 5 / RHS 4
* gate (b) database sanity: **PASS** — 0 counterexamples over all 12,112 members of `D` through this arm's evaluator, 0 through the `scripts/gen` path on a 1500-graph sample; equality count 290 vs 290 recorded
* gate (c) third code path: **PASS** — LHS 5, RHS 4, slack -1
* invariants at the witness (third path): `alpha = 5`, `gamma = 2`, `gamma_i = 5`
* seeds: base `20387519`; BASE_SEED(20260815) + 7919 * int(id suffix); FAM unit k -> base+1000+k, ANNEAL unit k -> base+500000+k, GROW unit k -> base+900000+k, probe -> base XOR 0x5EED

### FP-020 — `kappa >= floor((disp_avg - ecc_avg)/2) + 1`

* refuting graph (graph6, `n = 16`): `OwbWmk_vomazb?fvaRMYc`
* at the witness: **LHS = 1**, **RHS = 2**, slack = -1
* found by: `FAM`; first hit at `n = 40` (``gBM????S@qFB]DB?IBr_C]Dk?_?BAGB?KB??n?QA_doD@GQ?DG?@?O??H?w`qY?h`???Ak@?TPoYOgjoDoO?wL?Sun?QDDloAOgl_K?wC??Q@pK@JAOd\m__GQgeGAW@DdC``), then reduced to `n = 16`
* search cost: 0.34 CPU s (cap 3600 s); verification 15.85 CPU s
* gate (a) second code path: **PASS** — `scripts/gen` brute: LHS 1 / RHS 2, scal: LHS 1 / RHS 2
* gate (b) database sanity: **PASS** — 0 counterexamples over all 12,112 members of `D` through this arm's evaluator, 0 through the `scripts/gen` path on a 1500-graph sample; equality count 1284 vs 1284 recorded
* gate (c) third code path: **PASS** — LHS 1, RHS 2, slack -1
* invariants at the witness (third path): `disp_avg = 85/16`, `ecc_avg = 13/4`, `kappa = 1`
* seeds: base `20419195`; BASE_SEED(20260815) + 7919 * int(id suffix); FAM unit k -> base+1000+k, ANNEAL unit k -> base+500000+k, GROW unit k -> base+900000+k, probe -> base XOR 0x5EED

### FP-021 — `kappa >= floor((lambda_avg - disp_max)/2) + 1`

* refuting graph (graph6, `n = 14`): `M?~vfbokF_]?G?w??`
* at the witness: **LHS = 1**, **RHS = 2**, slack = -1
* found by: `FAM`; first hit at `n = 23` (`V?B{rpguFo^?m?i?\?Fo?]?AW?Fo?Fo??O??s??DO???`), then reduced to `n = 14`
* search cost: 30.15 CPU s (cap 3600 s); verification 14.42 CPU s
* gate (a) second code path: **PASS** — `scripts/gen` brute: LHS 1 / RHS 2, scal: LHS 1 / RHS 2
* gate (b) database sanity: **PASS** — 0 counterexamples over all 12,112 members of `D` through this arm's evaluator, 0 through the `scripts/gen` path on a 1500-graph sample; equality count 335 vs 335 recorded
* gate (c) third code path: **PASS** — LHS 1, RHS 2, slack -1
* invariants at the witness (third path): `disp_max = 3`, `kappa = 1`, `lam_avg = 5`
* seeds: base `20427114`; BASE_SEED(20260815) + 7919 * int(id suffix); FAM unit k -> base+1000+k, ANNEAL unit k -> base+500000+k, GROW unit k -> base+900000+k, probe -> base XOR 0x5EED

### FP-022 — `lambda_max >= floor((dd - f_1)/2)`

* refuting graph (graph6, `n = 13`): `LZ~Rzv~}v^^~^~`
* at the witness: **LHS = 2**, **RHS = 3**, slack = -1
* found by: `FAM`; first hit at `n = 25` (`X~~qv~~}~~~v^l~~~^~Vz~~|~v~}~~~zy|~~tz~l~~~v^v~^n~~`), then reduced to `n = 13`
* search cost: 0.01 CPU s (cap 3600 s); verification 8.08 CPU s
* gate (a) second code path: **PASS** — `scripts/gen` brute: LHS 2 / RHS 3, scal: LHS 2 / RHS 3
* gate (b) database sanity: **PASS** — 0 counterexamples over all 12,112 members of `D` through this arm's evaluator, 0 through the `scripts/gen` path on a 1500-graph sample; equality count 380 vs 380 recorded
* gate (c) third code path: **PASS** — LHS 2, RHS 3, slack -1
* invariants at the witness (third path): `dd = 6`, `f1 = 0`, `lam_max = 2`
* seeds: base `20435033`; BASE_SEED(20260815) + 7919 * int(id suffix); FAM unit k -> base+1000+k, ANNEAL unit k -> base+500000+k, GROW unit k -> base+900000+k, probe -> base XOR 0x5EED

### FP-023 — `lambda_max >= floor((gamma_2 - chi)/2) + 1`

* refuting graph (graph6, `n = 12`): `K_Q@@OO?gC@?`
* at the witness: **LHS = 3**, **RHS = 4**, slack = -1
* found by: `FAM`; first hit at `n = 15` (`N_OA?A?CPc?_?D?C?O?`), then reduced to `n = 12`
* search cost: 0.29 CPU s (cap 3600 s); verification 11.42 CPU s
* gate (a) second code path: **PASS** — `scripts/gen` brute: LHS 3 / RHS 4, scal: LHS 3 / RHS 4
* gate (b) database sanity: **PASS** — 0 counterexamples over all 12,112 members of `D` through this arm's evaluator, 0 through the `scripts/gen` path on a 1500-graph sample; equality count 30 vs 30 recorded
* gate (c) third code path: **PASS** — LHS 3, RHS 4, slack -1
* invariants at the witness (third path): `chi = 2`, `gamma_2 = 8`, `lam_max = 3`
* seeds: base `20442952`; BASE_SEED(20260815) + 7919 * int(id suffix); FAM unit k -> base+1000+k, ANNEAL unit k -> base+500000+k, GROW unit k -> base+900000+k, probe -> base XOR 0x5EED

### FP-029 — `res >= A - deg_avg`

* refuting graph (graph6, `n = 13`): `L?GOB@CcCC?OA?`
* at the witness: **LHS = 5**, **RHS = 67/13**, slack = -2/13
* found by: `FAM`; first hit at `n = 35` (`b???@A?@?C???@??O??O????S??????????_??OG????C?OCA?????aGO_???G????OO?G?@?A??O??AC???_???O??AA???__???`), then reduced to `n = 13`
* search cost: 0.00 CPU s (cap 3600 s); verification 6.99 CPU s
* gate (a) second code path: **PASS** — `scripts/gen` brute: LHS 5 / RHS 67/13, scal: LHS 5 / RHS 67/13
* gate (b) database sanity: **PASS** — 0 counterexamples over all 12,112 members of `D` through this arm's evaluator, 0 through the `scripts/gen` path on a 1500-graph sample; equality count 32 vs 32 recorded
* gate (c) third code path: **PASS** — LHS 5, RHS 67/13, slack -2/13
* invariants at the witness (third path): `annih = 7`, `deg_avg = 24/13`, `res = 5`
* seeds: base `20490466`; BASE_SEED(20260815) + 7919 * int(id suffix); FAM unit k -> base+1000+k, ANNEAL unit k -> base+500000+k, GROW unit k -> base+900000+k, probe -> base XOR 0x5EED

### FP-030 — `res >= floor((dd)/(gamma_t))`

* refuting graph (graph6, `n = 9`): `H~Fwtnv`
* at the witness: **LHS = 2**, **RHS = 3**, slack = -1
* found by: `FAM`; first hit at `n = 28` (`[DlRyDznkGm}~~MkobTtmMluCYekt{GtNU]f~n~~||~vUZBnm~~]|uFM}pVZn|~v`), then reduced to `n = 9`
* search cost: 0.08 CPU s (cap 3600 s); verification 7.60 CPU s
* gate (a) second code path: **PASS** — `scripts/gen` brute: LHS 2 / RHS 3, scal: LHS 2 / RHS 3
* gate (b) database sanity: **PASS** — 0 counterexamples over all 12,112 members of `D` through this arm's evaluator, 0 through the `scripts/gen` path on a 1500-graph sample; equality count 2216 vs 2216 recorded
* gate (c) third code path: **PASS** — LHS 2, RHS 3, slack -1
* invariants at the witness (third path): `dd = 6`, `gamma_t = 2`, `res = 2`
* seeds: base `20498385`; BASE_SEED(20260815) + 7919 * int(id suffix); FAM unit k -> base+1000+k, ANNEAL unit k -> base+500000+k, GROW unit k -> base+900000+k, probe -> base XOR 0x5EED

## Non-crossings — how close the search got

| id | verdict | best slack found | at (graph6) | source | evaluations | max order | n=9 bases swept | CPU s |
|---|---|---|---|---|---|---|---|---|
| FP-001 | HELD | 0 | `JsA?C??j}|?` | anneal n=11 unit=478 | 8255006 | 40 | 4600 | 3600.01 |
| FP-003 | HELD | 0 | `HHhGnv?` | n=9 exhaustive extension of GHhGns | 3832055 | 40 | 2420 | 3600.01 |
| FP-004 | HELD | 59/45 | `I~?I?WLA_` | anneal n=10 unit=337 | 8221897 | 40 | 5020 | 3600.0 |
| FP-005 | HELD | 0 | `HNz~v~w` | n=9 exhaustive extension of GNz~v{ | 4082999 | 40 | 2580 | 3600.07 |
| FP-006 | HELD | 0 | `KG??Aa?ccWC?` | anneal n=12 unit=100019 | 2120062 | 40 | 1160 | 3600.05 |
| FP-010 | HELD | 0 | `HKFCd[p` | anneal n=9 unit=22 | 713013 | 28 | 440 | 3600.4 |
| FP-011 | HELD | 0 | `H||~z~n` | anneal n=9 unit=112 | 3631766 | 40 | 2220 | 3600.03 |
| FP-013 | HELD | 0 | `HEyn~z~` | n=9 exhaustive extension of GEyn~w | 827357 | 28 | 520 | 3600.26 |
| FP-017 | HELD | 0 | `HvE@US@` | anneal n=9 unit=112 | 3531546 | 40 | 2160 | 3600.0 |
| FP-018 | HELD | 0 | `HFw_NI?` | n=9 exhaustive extension of GFw_NG | 1926345 | 40 | 1220 | 3600.79 |
| FP-019 | HELD | 0 | ``Hc]A`Me`` | anneal n=9 unit=13 | 283786 | 36 | 160 | 3600.86 |
| FP-024 | HELD | 0 | `HA?KJI?` | n=9 exhaustive extension of GA?KJG | 873290 | 40 | 560 | 3600.22 |
| FP-025 | HELD | 0 | `HXU]~z{` | n=9 exhaustive extension of GXU]~w | 686826 | 40 | 420 | 3600.26 |
| FP-026 | HELD | 0 | `HaOGnH?` | n=9 exhaustive extension of GaOGnG | 826737 | 40 | 500 | 3600.05 |
| FP-027 | HELD | 0 | `L?OEG?AI??AGDQ` | anneal n=13 unit=368 | 17558459 | 40 | 8697 | 3600.01 |
| FP-028 | HELD | 29/1995 | `T}v~~~|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~` | beam extension of order 20 | 18271896 | 40 | 8137 | 3600.01 |

Machine-readable copy: [`arm-generic.json`](arm-generic.json). Per-target raw run records: `arm-generic-runs/`.
