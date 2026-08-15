# Generic arm — results

Arm 2 of the preregistered three-arm test ([`PREREGISTRATION.md`](PREREGISTRATION.md), tag `prereg-three-arm-v1`), run blind to the other two arms.

**Written incrementally; last update 2026-08-15T22:49:11Z.**

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
* all 30 frozen targets re-evaluated over all 12,112 members of `D` through this arm's own evaluator: **PASS — 0 counterexamples, and every recorded equality count, min slack and max slack reproduces exactly**

Every candidate crossing must pass both:

* **(a) second code path** — the witness is recomputed by `scripts/gen/invariants.py` (backend `scal`, plus the exhaustive `2^n` backend `brute` when `n ≤ 20`) and re-evaluated by `scripts/gen/expressions.py`; LHS, RHS and slack must agree exactly and the slack must be negative;
* **(b) database-sanity gate** — the same reading is re-evaluated over all 12,112 members of `D` (rebuilt from `scripts/gen/`); it must produce zero counterexamples there and reproduce the recorded equality count. A reading that also refutes members of `D` is a bug and is discarded.

Witnesses are then reduced mechanically (greedy vertex deletion while connected and slack < 0), which is why several are much smaller than the graph the search first hit.

## Counts

| verdict | targets |
|---|---|
| CROSSED | 12 |
| BRACKET | 8 |
| PENDING | 10 |
| **total** | **30** |

## Per-target results

| id | statement | verdict | witness (graph6) | n | LHS | RHS | found by | CPU s | gate (a) | gate (b) |
|---|---|---|---|---|---|---|---|---|---|---|
| FP-001 | `alpha <= ceil((Tdist_max - dist_even_min)/2) + 1` | **BRACKET** | — | — | — | — | — | 240.0 | n/a (no candidate) | n/a (no candidate) |
| FP-002 | `alpha >= dist_even_max - chi` | **CROSSED** | `L`cAwH@CxsVySP` | 13 | 5 | 6 | FAM | 0.05 | PASS | PASS |
| FP-003 | `alpha >= lambda_max - cutv` | **BRACKET** | — | — | — | — | — | 240.0 | n/a (no candidate) | n/a (no candidate) |
| FP-004 | `A >= floor((disp_min)/2) + dist_avg` | **BRACKET** | — | — | — | — | — | 240.0 | n/a (no candidate) | n/a (no candidate) |
| FP-005 | `A >= floor((n)/(gamma_t))` | **BRACKET** | — | — | — | — | — | 240.0 | n/a (no candidate) | n/a (no candidate) |
| FP-006 | `chi >= ceil((omega - chi_regular)/2) + 1` | **BRACKET** | — | — | — | — | — | 240.06 | n/a (no candidate) | n/a (no candidate) |
| FP-007 | `diam <= disp_max + gamma_2` | **CROSSED** | `HAgcACO` | 9 | 8 | 7 | FAM | 8.58 | PASS | PASS |
| FP-008 | `diam >= floor((A)/(ceil(lambda_1)))` | **CROSSED** | `I??????~w` | 10 | 2 | 3 | FAM | 0.29 | PASS | PASS |
| FP-009 | `gamma <= floor((lambda_avg)/2) + res` | **CROSSED** | `N?I@?CAOCc?C?C?Gg??` | 15 | 7 | 6 | FAM | 0.17 | PASS | PASS |
| FP-010 | `gamma <= gamma_2 - chi_C4free` | **BRACKET** | — | — | — | — | — | 240.29 | n/a (no candidate) | n/a (no candidate) |
| FP-011 | `gamma >= ceil((Tdist_min)/(m))` | **BRACKET** | — | — | — | — | — | 240.0 | n/a (no candidate) | n/a (no candidate) |
| FP-012 | `gamma_2 <= dist_even_max - chi_regular + 2` | **CROSSED** | `U??_GAA_OA??B@A?G?O?????O??C?O?@???G?AD?` | 22 | 14 | 13 | FAM | 0.54 | PASS | PASS |
| FP-013 | `gamma_2 >= ceil((Delta)/(Sigma_2))` | **BRACKET** | — | — | — | — | — | 240.02 | n/a (no candidate) | n/a (no candidate) |
| FP-014 | `gamma_2 >= floor((dist_even_min + disp_min)/2)` | **CROSSED** | `Q??????k|{Y[ao~w^gD~?[wBm??` | 18 | 5 | 6 | FAM | 0.53 | PASS | PASS |
| FP-015 | `gamma_i <= diam + mu - 1` | **CROSSED** | `UqP?GP?GC?G?C?C?C??G?O?A??A???O?A???G???` | 22 | 11 | 10 | FAM | 0.31 | PASS | PASS |
| FP-016 | `gamma_i <= floor((alpha)/2) + gamma` | **CROSSED** | `I_A_L?SVO` | 10 | 5 | 4 | ANNEAL | 105.81 | PASS | PASS |
| FP-017 | `gamma_t >= floor((cutv + chi_tree)/2) + 1` | PENDING | | | | | | | | |
| FP-018 | `gamma_t >= floor((gamma)/(disp_min))` | PENDING | | | | | | | | |
| FP-019 | `kappa <= floor((t)/2) + floor(lambda_1)` | PENDING | | | | | | | | |
| FP-020 | `kappa >= floor((disp_avg - ecc_avg)/2) + 1` | **CROSSED** | `RnE^`ySdG?BmABo_^{fcBo?QSogWK?` | 19 | 1 | 2 | FAM | 0.53 | PASS | PASS |
| FP-021 | `kappa >= floor((lambda_avg - disp_max)/2) + 1` | **CROSSED** | `I??Bzz{^?` | 10 | 1 | 2 | FAM | 13.13 | PASS | PASS |
| FP-022 | `lambda_max >= floor((dd - f_1)/2)` | **CROSSED** | `LZ~Rzv~}v^^~^~` | 13 | 2 | 3 | FAM | 0.01 | PASS | PASS |
| FP-023 | `lambda_max >= floor((gamma_2 - chi)/2) + 1` | **CROSSED** | `K??Q??E_OS[?` | 12 | 3 | 4 | FAM | 0.66 | PASS | PASS |
| FP-024 | `mu <= ceil((n - chi_tree)/2)` | PENDING | | | | | | | | |
| FP-025 | `mu >= floor((delta + lambda_min)/2)` | PENDING | | | | | | | | |
| FP-026 | `rad >= floor((disp_max)/(floor(lambda_1)))` | PENDING | | | | | | | | |
| FP-027 | `rad >= floor((ecc_avg)/2) + chi_bipartite` | PENDING | | | | | | | | |
| FP-028 | `res <= alpha + CW - 1` | PENDING | | | | | | | | |
| FP-029 | `res >= A - deg_avg` | PENDING | | | | | | | | |
| FP-030 | `res >= floor((dd)/(gamma_t))` | PENDING | | | | | | | | |

## Crossings in detail

### FP-002 — `alpha >= dist_even_max - chi`

* refuting graph (graph6, `n = 13`): `L`cAwH@CxsVySP`
* at the witness: **LHS = 5**, **RHS = 6**, slack = -1
* found by: `FAM`; first hit at `n = 37` (`daXBGTD?siq?{PoT@C?ZWfrf?jJw@tiw[POeBLJAyFy?BnA{dCdOd^C?K{gGf@hxWTEqBJzTY}dx{oPzWmcFkM`GfHCY{\DjdBZ|Be|EGEoLPWgb`), then reduced to `n = 13`
* search cost: 0.05 CPU s (cap 3600 s); verification 9.30 CPU s
* gate (a) second code path: **PASS** — `scripts/gen` brute: LHS 5 / RHS 6, scal: LHS 5 / RHS 6
* gate (b) database sanity: **PASS** — 0 counterexamples over all 12,112 members of `D` through this arm's evaluator, 0 through the `scripts/gen` path on a 1500-graph sample; equality count 249 vs 249 recorded
* seeds: base `20276653`; BASE_SEED(20260815) + 7919 * int(id suffix); FAM unit k -> base+1000+k, ANNEAL unit k -> base+500000+k, GROW unit k -> base+900000+k, probe -> base XOR 0x5EED

### FP-007 — `diam <= disp_max + gamma_2`

* refuting graph (graph6, `n = 9`): `HAgcACO`
* at the witness: **LHS = 8**, **RHS = 7**, slack = -1
* found by: `FAM`; first hit at `n = 18` (`QC?@?PGBA??_?@?CA???CGAAA??`), then reduced to `n = 9`
* search cost: 8.58 CPU s (cap 3600 s); verification 10.61 CPU s
* gate (a) second code path: **PASS** — `scripts/gen` brute: LHS 8 / RHS 7, scal: LHS 8 / RHS 7
* gate (b) database sanity: **PASS** — 0 counterexamples over all 12,112 members of `D` through this arm's evaluator, 0 through the `scripts/gen` path on a 1500-graph sample; equality count 6 vs 6 recorded
* seeds: base `20316248`; BASE_SEED(20260815) + 7919 * int(id suffix); FAM unit k -> base+1000+k, ANNEAL unit k -> base+500000+k, GROW unit k -> base+900000+k, probe -> base XOR 0x5EED

### FP-008 — `diam >= floor((A)/(ceil(lambda_1)))`

* refuting graph (graph6, `n = 10`): `I??????~w`
* at the witness: **LHS = 2**, **RHS = 3**, slack = -1
* found by: `FAM`; first hit at `n = 10` (`I??????~w`), then reduced to `n = 10`
* search cost: 0.29 CPU s (cap 3600 s); verification 26.11 CPU s
* gate (a) second code path: **PASS** — `scripts/gen` brute: LHS 2 / RHS 3, scal: LHS 2 / RHS 3
* gate (b) database sanity: **PASS** — 0 counterexamples over all 12,112 members of `D` through this arm's evaluator, 0 through the `scripts/gen` path on a 1500-graph sample; equality count 7 vs 7 recorded
* seeds: base `20324167`; BASE_SEED(20260815) + 7919 * int(id suffix); FAM unit k -> base+1000+k, ANNEAL unit k -> base+500000+k, GROW unit k -> base+900000+k, probe -> base XOR 0x5EED

### FP-009 — `gamma <= floor((lambda_avg)/2) + res`

* refuting graph (graph6, `n = 15`): `N?I@?CAOCc?C?C?Gg??`
* at the witness: **LHS = 7**, **RHS = 6**, slack = -1
* found by: `FAM`; first hit at `n = 15` (`N?I@?CAOCc?C?C?Gg??`), then reduced to `n = 15`
* search cost: 0.17 CPU s (cap 3600 s); verification 9.21 CPU s
* gate (a) second code path: **PASS** — `scripts/gen` brute: LHS 7 / RHS 6, scal: LHS 7 / RHS 6
* gate (b) database sanity: **PASS** — 0 counterexamples over all 12,112 members of `D` through this arm's evaluator, 0 through the `scripts/gen` path on a 1500-graph sample; equality count 704 vs 704 recorded
* seeds: base `20332086`; BASE_SEED(20260815) + 7919 * int(id suffix); FAM unit k -> base+1000+k, ANNEAL unit k -> base+500000+k, GROW unit k -> base+900000+k, probe -> base XOR 0x5EED

### FP-012 — `gamma_2 <= dist_even_max - chi_regular + 2`

* refuting graph (graph6, `n = 22`): `U??_GAA_OA??B@A?G?O?????O??C?O?@???G?AD?`
* at the witness: **LHS = 14**, **RHS = 13**, slack = -1
* found by: `FAM`; first hit at `n = 28` (`[??C??g?g_???COCG?_???@????B?gA??O?A????????_???C?A???G???@???Og`), then reduced to `n = 22`
* search cost: 0.54 CPU s (cap 3600 s); verification 10.42 CPU s
* gate (a) second code path: **PASS** — `scripts/gen` scal: LHS 14 / RHS 13
* gate (b) database sanity: **PASS** — 0 counterexamples over all 12,112 members of `D` through this arm's evaluator, 0 through the `scripts/gen` path on a 1500-graph sample; equality count 17 vs 17 recorded
* seeds: base `20355843`; BASE_SEED(20260815) + 7919 * int(id suffix); FAM unit k -> base+1000+k, ANNEAL unit k -> base+500000+k, GROW unit k -> base+900000+k, probe -> base XOR 0x5EED

### FP-014 — `gamma_2 >= floor((dist_even_min + disp_min)/2)`

* refuting graph (graph6, `n = 18`): `Q??????k|{Y[ao~w^gD~?[wBm??`
* at the witness: **LHS = 5**, **RHS = 6**, slack = -1
* found by: `FAM`; first hit at `n = 27` (`Z?????????????????F}gnKxV]BH{D}fATJ?j~w@|]?]~g?~^w?k{w?]to??`), then reduced to `n = 18`
* search cost: 0.53 CPU s (cap 3600 s); verification 15.42 CPU s
* gate (a) second code path: **PASS** — `scripts/gen` brute: LHS 5 / RHS 6, scal: LHS 5 / RHS 6
* gate (b) database sanity: **PASS** — 0 counterexamples over all 12,112 members of `D` through this arm's evaluator, 0 through the `scripts/gen` path on a 1500-graph sample; equality count 85 vs 85 recorded
* seeds: base `20371681`; BASE_SEED(20260815) + 7919 * int(id suffix); FAM unit k -> base+1000+k, ANNEAL unit k -> base+500000+k, GROW unit k -> base+900000+k, probe -> base XOR 0x5EED

### FP-015 — `gamma_i <= diam + mu - 1`

* refuting graph (graph6, `n = 22`): `UqP?GP?GC?G?C?C?C??G?O?A??A???O?A???G???`
* at the witness: **LHS = 11**, **RHS = 10**, slack = -1
* found by: `FAM`; first hit at `n = 39` (`fpa?OO__@?O?A?A?C?@????C??`???O????G?G?C??????OG????A???@???O????G?????O?@?????????a?????G???????G????C???????A?_?????@??????`), then reduced to `n = 22`
* search cost: 0.31 CPU s (cap 3600 s); verification 14.71 CPU s
* gate (a) second code path: **PASS** — `scripts/gen` scal: LHS 11 / RHS 10
* gate (b) database sanity: **PASS** — 0 counterexamples over all 12,112 members of `D` through this arm's evaluator, 0 through the `scripts/gen` path on a 1500-graph sample; equality count 3 vs 3 recorded
* seeds: base `20379600`; BASE_SEED(20260815) + 7919 * int(id suffix); FAM unit k -> base+1000+k, ANNEAL unit k -> base+500000+k, GROW unit k -> base+900000+k, probe -> base XOR 0x5EED

### FP-016 — `gamma_i <= floor((alpha)/2) + gamma`

* refuting graph (graph6, `n = 10`): `I_A_L?SVO`
* at the witness: **LHS = 5**, **RHS = 4**, slack = -1
* found by: `ANNEAL`; first hit at `n = 14` (`M[Gd_BgOKO[vXg\z?`), then reduced to `n = 10`
* search cost: 105.81 CPU s (cap 3600 s); verification 9.47 CPU s
* gate (a) second code path: **PASS** — `scripts/gen` brute: LHS 5 / RHS 4, scal: LHS 5 / RHS 4
* gate (b) database sanity: **PASS** — 0 counterexamples over all 12,112 members of `D` through this arm's evaluator, 0 through the `scripts/gen` path on a 1500-graph sample; equality count 290 vs 290 recorded
* seeds: base `20387519`; BASE_SEED(20260815) + 7919 * int(id suffix); FAM unit k -> base+1000+k, ANNEAL unit k -> base+500000+k, GROW unit k -> base+900000+k, probe -> base XOR 0x5EED

### FP-020 — `kappa >= floor((disp_avg - ecc_avg)/2) + 1`

* refuting graph (graph6, `n = 19`): `RnE^`ySdG?BmABo_^{fcBo?QSogWK?`
* at the witness: **LHS = 1**, **RHS = 2**, slack = -1
* found by: `FAM`; first hit at `n = 36` (`c@Q@c_aaPdG??ACBh?aOHKi??jAay`aqDP\rGgACA_FH?eC?????Bpg??o?Xc?O_`S?A?a_GOPdU]A@dOO_mDO@GGlo?QELaqFOTg?}?K?`), then reduced to `n = 19`
* search cost: 0.53 CPU s (cap 3600 s); verification 24.48 CPU s
* gate (a) second code path: **PASS** — `scripts/gen` brute: LHS 1 / RHS 2, scal: LHS 1 / RHS 2
* gate (b) database sanity: **PASS** — 0 counterexamples over all 12,112 members of `D` through this arm's evaluator, 0 through the `scripts/gen` path on a 1500-graph sample; equality count 1284 vs 1284 recorded
* seeds: base `20419195`; BASE_SEED(20260815) + 7919 * int(id suffix); FAM unit k -> base+1000+k, ANNEAL unit k -> base+500000+k, GROW unit k -> base+900000+k, probe -> base XOR 0x5EED

### FP-021 — `kappa >= floor((lambda_avg - disp_max)/2) + 1`

* refuting graph (graph6, `n = 10`): `I??Bzz{^?`
* at the witness: **LHS = 1**, **RHS = 2**, slack = -1
* found by: `FAM`; first hit at `n = 16` (`O???????????}~y~^~fvw`), then reduced to `n = 10`
* search cost: 13.13 CPU s (cap 3600 s); verification 13.76 CPU s
* gate (a) second code path: **PASS** — `scripts/gen` brute: LHS 1 / RHS 2, scal: LHS 1 / RHS 2
* gate (b) database sanity: **PASS** — 0 counterexamples over all 12,112 members of `D` through this arm's evaluator, 0 through the `scripts/gen` path on a 1500-graph sample; equality count 335 vs 335 recorded
* seeds: base `20427114`; BASE_SEED(20260815) + 7919 * int(id suffix); FAM unit k -> base+1000+k, ANNEAL unit k -> base+500000+k, GROW unit k -> base+900000+k, probe -> base XOR 0x5EED

### FP-022 — `lambda_max >= floor((dd - f_1)/2)`

* refuting graph (graph6, `n = 13`): `LZ~Rzv~}v^^~^~`
* at the witness: **LHS = 2**, **RHS = 3**, slack = -1
* found by: `FAM`; first hit at `n = 25` (`X~~qv~~}~~~v^l~~~^~Vz~~|~v~}~~~zy|~~tz~l~~~v^v~^n~~`), then reduced to `n = 13`
* search cost: 0.01 CPU s (cap 3600 s); verification 7.85 CPU s
* gate (a) second code path: **PASS** — `scripts/gen` brute: LHS 2 / RHS 3, scal: LHS 2 / RHS 3
* gate (b) database sanity: **PASS** — 0 counterexamples over all 12,112 members of `D` through this arm's evaluator, 0 through the `scripts/gen` path on a 1500-graph sample; equality count 380 vs 380 recorded
* seeds: base `20435033`; BASE_SEED(20260815) + 7919 * int(id suffix); FAM unit k -> base+1000+k, ANNEAL unit k -> base+500000+k, GROW unit k -> base+900000+k, probe -> base XOR 0x5EED

### FP-023 — `lambda_max >= floor((gamma_2 - chi)/2) + 1`

* refuting graph (graph6, `n = 12`): `K??Q??E_OS[?`
* at the witness: **LHS = 3**, **RHS = 4**, slack = -1
* found by: `FAM`; first hit at `n = 14` (`Mg???GO??BOA?ge??`), then reduced to `n = 12`
* search cost: 0.66 CPU s (cap 3600 s); verification 11.44 CPU s
* gate (a) second code path: **PASS** — `scripts/gen` brute: LHS 3 / RHS 4, scal: LHS 3 / RHS 4
* gate (b) database sanity: **PASS** — 0 counterexamples over all 12,112 members of `D` through this arm's evaluator, 0 through the `scripts/gen` path on a 1500-graph sample; equality count 30 vs 30 recorded
* seeds: base `20442952`; BASE_SEED(20260815) + 7919 * int(id suffix); FAM unit k -> base+1000+k, ANNEAL unit k -> base+500000+k, GROW unit k -> base+900000+k, probe -> base XOR 0x5EED

## Non-crossings — how close the search got

| id | verdict | best slack found | at (graph6) | source | evaluations | max order | n=9 bases swept | CPU s |
|---|---|---|---|---|---|---|---|---|
| FP-001 | BRACKET | 0 | `TsaCCA?_C?O?_?_?O?C??_?A??C??C??A???` | random bipartite p=0.70 n=21 | 503176 | 40 | 260 | 240.0 |
| FP-003 | BRACKET | 0 | `_k`[iXolrL]DoLip]{{juQ}T]^{XsC^TvsAwd~Qrfa_ro{kTSwLjKt@IcfjYW||BvN{_Ifx}jtrHt}naDaQg` | G(n,p) p=0.55 n=32 | 184848 | 40 | 100 | 240.0 |
| FP-004 | BRACKET | 7/5 | `IrS?OGD@w` | anneal n=10 unit=57 | 720931 | 40 | 440 | 240.0 |
| FP-005 | BRACKET | 0 | `g~z~~z}~~|z~~~~~~|~~z~~}~~~zn~~^~~zr~}~}~^~~n~~~|^~~~~~}~~~|~~Zvnry~~~zz~~~~vn~~~~|~n^~~~~n~n~v~~~l~~|Zf~~z~nYn~~~n~zn^~~|~~~n~~~~~` | G(n,p) p=0.92 n=40 | 381947 | 40 | 200 | 240.0 |
| FP-006 | BRACKET | 0 | `M??????PGE?CEWiO?` | random bipartite p=0.20 n=14 | 162072 | 40 | 80 | 240.06 |
| FP-010 | BRACKET | 0 | `HCCK@HO` | random tree n=9 | 112084 | 32 | 60 | 240.29 |
| FP-011 | BRACKET | 0 | `UXl|p~~n|vv~^^zH~~||zn~||~xuxqIDG~}nMvIg` | random geometric r=0.60 n=22 | 306798 | 40 | 160 | 240.0 |
| FP-013 | BRACKET | 0 | `J???????F~_` | random bipartite p=0.70 n=11 | 88774 | 28 | 40 | 240.02 |

Machine-readable copy: [`arm-generic.json`](arm-generic.json). Per-target raw run records: `arm-generic-runs/`.
