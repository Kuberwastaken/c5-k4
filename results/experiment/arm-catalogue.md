# Arm 1 — catalogue (control arm)

Preregistered protocol: [`PREREGISTRATION.md`](PREREGISTRATION.md), tag `prereg-three-arm-v1`.

Method: pure lookup. Every one of the 30 frozen targets in [`fresh-population/population.json`](fresh-population/population.json) is evaluated on every one of the 68 graphs of the frozen catalogue [`scripts/exp/catalogue.py`](../../scripts/exp/catalogue.py). No graph was constructed, tuned or selected for any target; the catalogue file was imported, never edited.

**Status:** complete — 30/30 targets scored.

| verdict | count |
|---|---|
| CROSSED | 8 |
| HELD | 22 |
| BRACKET | 0 |

## Results

| id | statement | verdict | refuting graph | LHS | RHS | s |
|---|---|---|---|---|---|---|
| FP-001 | `alpha <= ceil((Tdist_max - dist_even_min)/2) + 1` | **HELD** | — | — | — | 16.2 |
| FP-002 | `alpha >= dist_even_max - chi` | **CROSSED** | `comp(C5[K4])` (+9 more) | 8 | 9 | 16.4 |
| FP-003 | `alpha >= lambda_max - cutv` | **HELD** | — | — | — | 16.5 |
| FP-004 | `A >= floor((disp_min)/2) + dist_avg` | **HELD** | — | — | — | 16.1 |
| FP-005 | `A >= floor((n)/(gamma_t))` | **HELD** | — | — | — | 17.2 |
| FP-006 | `chi >= ceil((omega - chi_regular)/2) + 1` | **HELD** | — | — | — | 16.3 |
| FP-007 | `diam <= disp_max + gamma_2` | **HELD** | — | — | — | 17.4 |
| FP-008 | `diam >= floor((A)/(ceil(lambda_1)))` | **CROSSED** | `star(12)` (+2 more) | 2 | 3 | 16.1 |
| FP-009 | `gamma <= floor((lambda_avg)/2) + res` | **HELD** | — | — | — | 16.6 |
| FP-010 | `gamma <= gamma_2 - chi_C4free` | **HELD** | — | — | — | 17.6 |
| FP-011 | `gamma >= ceil((Tdist_min)/(m))` | **HELD** | — | — | — | 16.3 |
| FP-012 | `gamma_2 <= dist_even_max - chi_regular + 2` | **CROSSED** | `doublestar(4,4)` (+2 more) | 8 | 7 | 17.4 |
| FP-013 | `gamma_2 >= ceil((Delta)/(Sigma_2))` | **HELD** | — | — | — | 17.4 |
| FP-014 | `gamma_2 >= floor((dist_even_min + disp_min)/2)` | **CROSSED** | `comp(Kneser(6,2))` (+19 more) | 3 | 4 | 17.4 |
| FP-015 | `gamma_i <= diam + mu - 1` | **CROSSED** | `doublestar(4,4)` (+2 more) | 5 | 4 | 16.3 |
| FP-016 | `gamma_i <= floor((alpha)/2) + gamma` | **CROSSED** | `comp(C5[K4])` (+4 more) | 8 | 7 | 16.5 |
| FP-017 | `gamma_t >= floor((cutv + chi_tree)/2) + 1` | **HELD** | — | — | — | 17.2 |
| FP-018 | `gamma_t >= floor((gamma)/(disp_min))` | **HELD** | — | — | — | 17.4 |
| FP-019 | `kappa <= floor((t)/2) + floor(lambda_1)` | **HELD** | — | — | — | 16.1 |
| FP-020 | `kappa >= floor((disp_avg - ecc_avg)/2) + 1` | **HELD** | — | — | — | 16.1 |
| FP-021 | `kappa >= floor((lambda_avg - disp_max)/2) + 1` | **HELD** | — | — | — | 16.5 |
| FP-022 | `lambda_max >= floor((dd - f_1)/2)` | **HELD** | — | — | — | 16.5 |
| FP-023 | `lambda_max >= floor((gamma_2 - chi)/2) + 1` | **CROSSED** | `MobiusKantor` | 3 | 4 | 17.9 |
| FP-024 | `mu <= ceil((n - chi_tree)/2)` | **HELD** | — | — | — | 16.1 |
| FP-025 | `mu >= floor((delta + lambda_min)/2)` | **HELD** | — | — | — | 16.5 |
| FP-026 | `rad >= floor((disp_max)/(floor(lambda_1)))` | **HELD** | — | — | — | 16.1 |
| FP-027 | `rad >= floor((ecc_avg)/2) + chi_bipartite` | **HELD** | — | — | — | 16.1 |
| FP-028 | `res <= alpha + CW - 1` | **HELD** | — | — | — | 16.2 |
| FP-029 | `res >= A - deg_avg` | **CROSSED** | `broom(6,4)` (+3 more) | 5 | 26/5 | 16.1 |
| FP-030 | `res >= floor((dd)/(gamma_t))` | **HELD** | — | — | — | 17.2 |

## Crossings in detail

### FP-002 — `alpha >= dist_even_max - chi`

| graph | graph6 | n | m | LHS | RHS | slack | 2nd path |
|---|---|---|---|---|---|---|---|
| comp(C5[K4]) | `S????Bo{F_]?~o~o^wF}?B~?N{?^w?^w?` | 20 | 80 | 8 | 9 | -1 | agree |
| T(7) | `Tn@}W]^ooQn`wcqfmj`AtIBuWlL`C{bpknaY` | 21 | 105 | 3 | 4 | -1 | agree |
| comp(Kneser(7,2)) | `T~~}DERa{NkWShQdgpxbKITSdKwpeohTkKXn` | 21 | 105 | 3 | 4 | -1 | agree |
| comp(C5[K5]) | `X???????Fo^?}?}?^?F~_~{B~oF~_F~_?F~_@~w?N~??~{?@~w?` | 25 | 125 | 10 | 12 | -2 | agree |
| C9[K3] | `Z~~ww{^?wF_^?F?F_Bw?F??{?Bw??w??{??^???w??F_??^w??Fw??F{??Bw` | 27 | 108 | 4 | 6 | -2 | agree |
| T(8) | `[xP]^@NFFioOdfk`o[y\GKWW@cwg{hoaOoD^yU?SSnAanToADD}A[JVnsJKFAWlc` | 28 | 168 | 4 | 9 | -5 | agree |
| Paley(29) | `\hfNNdxnI{dxDxa{gnHDxcVdGnHGnGcVeHDxPGnLCa{yHDxyHDx|Ca{nPGnHyHDxfgcVc` | 29 | 203 | 4 | 7 | -3 | agree |
| comp(Paley(29)) | `\UWooYEOtBYEyE\BVOuyEZgYvOuvOvZgXuyEmvOqz\BDuyEDuyEAz\BOmvOuDuyEWVZgW` | 29 | 203 | 4 | 7 | -3 | agree |
| comp(C5[K6]) | `]???????????~?~?^_Fw?~?B{?F~wF~wB~{?~~?F~w?^~_??~~??~~??^~_?F~w??~~??B~{??` | 30 | 180 | 12 | 15 | -3 | agree |
| T(9) | `c`MGclRKxoA^`onQ{ADIfBB@?kIX?Z@`kkOzGFN]fh?WkYwoBJEB_agX_DTXsU?A]IPpCaQppSI]wkECD?VgAMKRVF|AiWFoR?TqGSOwjk` | 36 | 252 | 4 | 13 | -9 | agree |

Invariant values at `comp(C5[K4])`: `alpha = 8`, `chi = 3`, `dist_even_max = 12`

Gate: PASS — 0 counterexamples in `D` under this arm's reading (path A) and 0 (path B); recorded equality witnesses all tight: True.

### FP-008 — `diam >= floor((A)/(ceil(lambda_1)))`

| graph | graph6 | n | m | LHS | RHS | slack | 2nd path |
|---|---|---|---|---|---|---|---|
| star(12) | `LsaCCA?_C?O?_?` | 13 | 12 | 2 | 3 | -1 | agree |
| doublestar(8,8) | `QsaCCA?_A?G?O?O?G?A??O?@???` | 18 | 17 | 3 | 4 | -1 | agree |
| doublestar(12,12) | `YsaCCA?_C?O?_?_?G?A??O?@??A??A??@???O??A???G???O???O????` | 26 | 25 | 3 | 6 | -3 | agree |

Invariant values at `star(12)`: `annih = 12`, `diam = 2`, `spec_ceil = 4`

Gate: PASS — 0 counterexamples in `D` under this arm's reading (path A) and 0 (path B); recorded equality witnesses all tight: False.

### FP-012 — `gamma_2 <= dist_even_max - chi_regular + 2`

| graph | graph6 | n | m | LHS | RHS | slack | 2nd path |
|---|---|---|---|---|---|---|---|
| doublestar(4,4) | `IsaAA@?O?` | 10 | 9 | 8 | 7 | -1 | agree |
| doublestar(8,8) | `QsaCCA?_A?G?O?O?G?A??O?@???` | 18 | 17 | 16 | 11 | -5 | agree |
| doublestar(12,12) | `YsaCCA?_C?O?_?_?G?A??O?@??A??A??@???O??A???G???O???O????` | 26 | 25 | 24 | 15 | -9 | agree |

Invariant values at `doublestar(4,4)`: `chi_reg = 0`, `dist_even_max = 5`, `gamma_2 = 8`

Gate: PASS — 0 counterexamples in `D` under this arm's reading (path A) and 0 (path B); recorded equality witnesses all tight: True.

### FP-014 — `gamma_2 >= floor((dist_even_min + disp_min)/2)`

| graph | graph6 | n | m | LHS | RHS | slack | 2nd path |
|---|---|---|---|---|---|---|---|
| comp(Kneser(6,2)) | `N~~DKmNXaihfKuIlbLw` | 15 | 60 | 3 | 4 | -1 | agree |
| C5[K4] | `S~~~~{NBw^`~?N?N_Fw@~{?~oB~_F~_F{` | 20 | 110 | 4 | 5 | -1 | agree |
| comp(C5[K4]) | `S????Bo{F_]?~o~o^wF}?B~?N{?^w?^w?` | 20 | 80 | 5 | 6 | -1 | agree |
| Kneser(7,2) | `T??@yxk\BoRfjUlYVME[rtijYrFMXNUiRreO` | 21 | 105 | 5 | 6 | -1 | agree |
| T(7) | `Tn@}W]^ooQn`wcqfmj`AtIBuWlL`C{bpknaY` | 21 | 105 | 4 | 6 | -2 | agree |
| comp(C7[K3]) | `T??FFB_~Fw^_~w~w^{F~w~~B~{?~~?~~?^~_` | 21 | 126 | 4 | 5 | -1 | agree |
| comp(Kneser(7,2)) | `T~~}DERa{NkWShQdgpxbKITSdKwpeohTkKXn` | 21 | 105 | 4 | 6 | -2 | agree |
| comp(T(7)) | `TO}@f`_NNlO]FZLWPS]|It{HfQq]zB[MRO\d` | 21 | 105 | 5 | 6 | -1 | agree |
| C5[K5] | `X~~~~~~~wN_~@~@~_~w?^?B{?Nw?^w?^~w?^}?F~o?~~?B~}?F~` | 25 | 175 | 4 | 6 | -2 | agree |
| comp(C5[K5]) | `X???????Fo^?}?}?^?F~_~{B~oF~_F~_?F~_@~w?N~??~{?@~w?` | 25 | 125 | 5 | 8 | -3 | agree |
| C9[K3] | `Z~~ww{^?wF_^?F?F_Bw?F??{?Bw??w??{??^???w??F_??^w??Fw??F{??Bw` | 27 | 108 | 6 | 7 | -1 | agree |
| comp(C9[K3]) | `Z??FFB_~Fw^_~w~w^{F~w~~B~{F~~F~~B~~_~~~F~~w^~~_F~~wF~~wB~~{?` | 27 | 243 | 3 | 5 | -2 | agree |
| T(8) | `[xP]^@NFFioOdfk`o[y\GKWW@cwg{hoaOoD^yU?SSnAanToADD}A[JVnsJKFAWlc` | 28 | 168 | 4 | 8 | -4 | agree |
| comp(T(8)) | `[Em`_}owwTNnYWR]NbDavrff}ZFVBUN\nNy_Dh~jjO|\OiN|yy@|bsgOJsrw|fQZ` | 28 | 210 | 4 | 7 | -3 | agree |
| Paley(29) | `\hfNNdxnI{dxDxa{gnHDxcVdGnHGnGcVeHDxPGnLCa{yHDxyHDx|Ca{nPGnHyHDxfgcVc` | 29 | 203 | 5 | 8 | -3 | agree |
| comp(Paley(29)) | `\UWooYEOtBYEyE\BVOuyEZgYvOuvOvZgXuyEmvOqz\BDuyEDuyEAz\BOmvOuDuyEWVZgW` | 29 | 203 | 5 | 8 | -3 | agree |
| C5[K6] | `]~~~~~~~~~~~?~?~_^wF~?~{B~w?Fw?F{?B~??~w?F~_?^~~??~~??~~_?^~w?F~~??~~{?B~w` | 30 | 255 | 4 | 7 | -3 | agree |
| comp(C5[K6]) | `]???????????~?~?^_Fw?~?B{?F~wF~wB~{?~~?F~w?^~_??~~??~~??^~_?F~w??~~??B~{??` | 30 | 180 | 5 | 9 | -4 | agree |
| T(9) | `c`MGclRKxoA^`onQ{ADIfBB@?kIX?Z@`kkOzGFN]fh?WkYwoBJEB_agX_DTXsU?A]IPpCaQppSI]wkECD?VgAMKRVF|AiWFoR?TqGSOwjk` | 36 | 252 | 5 | 11 | -6 | agree |
| comp(T(9)) | `c]pvZQkrEN|_]NOlB|ytW{{}~Rte~c}]RRnCvwo`WU~fRdFN{sx{^\Ve^yieJh~|`tmMz\lMMjt`FRxzy~gV|prkgwA|TfwNk~iLvjnFSR` | 36 | 378 | 4 | 8 | -4 | agree |

Invariant values at `comp(Kneser(6,2))`: `disp_min = 1`, `dist_even_min = 7`, `gamma_2 = 3`

Gate: PASS — 0 counterexamples in `D` under this arm's reading (path A) and 0 (path B); recorded equality witnesses all tight: True.

### FP-015 — `gamma_i <= diam + mu - 1`

| graph | graph6 | n | m | LHS | RHS | slack | 2nd path |
|---|---|---|---|---|---|---|---|
| doublestar(4,4) | `IsaAA@?O?` | 10 | 9 | 5 | 4 | -1 | agree |
| doublestar(8,8) | `QsaCCA?_A?G?O?O?G?A??O?@???` | 18 | 17 | 9 | 4 | -5 | agree |
| doublestar(12,12) | `YsaCCA?_C?O?_?_?G?A??O?@??A??A??@???O??A???G???O???O????` | 26 | 25 | 13 | 4 | -9 | agree |

Invariant values at `doublestar(4,4)`: `diam = 3`, `gamma_i = 5`, `mu = 2`

Gate: PASS — 0 counterexamples in `D` under this arm's reading (path A) and 0 (path B); recorded equality witnesses all tight: True.

### FP-016 — `gamma_i <= floor((alpha)/2) + gamma`

| graph | graph6 | n | m | LHS | RHS | slack | 2nd path |
|---|---|---|---|---|---|---|---|
| comp(C5[K4]) | `S????Bo{F_]?~o~o^wF}?B~?N{?^w?^w?` | 20 | 80 | 8 | 7 | -1 | agree |
| comp(C7[K3]) | `T??FFB_~Fw^_~w~w^{F~w~~B~{?~~?~~?^~_` | 21 | 126 | 6 | 5 | -1 | agree |
| comp(C5[K5]) | `X???????Fo^?}?}?^?F~_~{B~oF~_F~_?F~_@~w?N~??~{?@~w?` | 25 | 125 | 10 | 8 | -2 | agree |
| comp(C9[K3]) | `Z??FFB_~Fw^_~w~w^{F~w~~B~{F~~F~~B~~_~~~F~~w^~~_F~~wF~~wB~~{?` | 27 | 243 | 6 | 5 | -1 | agree |
| comp(C5[K6]) | `]???????????~?~?^_Fw?~?B{?F~wF~wB~{?~~?F~w?^~_??~~??~~??^~_?F~w??~~??B~{??` | 30 | 180 | 12 | 9 | -3 | agree |

Invariant values at `comp(C5[K4])`: `alpha = 8`, `gamma = 3`, `gamma_i = 8`

Gate: PASS — 0 counterexamples in `D` under this arm's reading (path A) and 0 (path B); recorded equality witnesses all tight: True.

### FP-023 — `lambda_max >= floor((gamma_2 - chi)/2) + 1`

| graph | graph6 | n | m | LHS | RHS | slack | 2nd path |
|---|---|---|---|---|---|---|---|
| MobiusKantor | `OhEGHC@AG?_PO@?Ga?K?P` | 16 | 24 | 3 | 4 | -1 | agree |

Invariant values at `MobiusKantor`: `chi = 2`, `gamma_2 = 8`, `lam_max = 3`

Gate: PASS — 0 counterexamples in `D` under this arm's reading (path A) and 0 (path B); recorded equality witnesses all tight: True.

### FP-029 — `res >= A - deg_avg`

| graph | graph6 | n | m | LHS | RHS | slack | 2nd path |
|---|---|---|---|---|---|---|---|
| broom(6,4) | `IhCGGGC@?` | 10 | 9 | 5 | 26/5 | -1/5 | agree |
| MobiusKantor | `OhEGHC@AG?_PO@?Ga?K?P` | 16 | 24 | 4 | 5 | -1 | agree |
| C9[K3] | `Z~~ww{^?wF_^?F?F_Bw?F??{?Bw??w??{??^???w??F_??^w??Fw??F{??Bw` | 27 | 108 | 3 | 5 | -2 | agree |
| T(9) | `c`MGclRKxoA^`onQ{ADIfBB@?kIX?Z@`kkOzGFN]fh?WkYwoBJEB_agX_DTXsU?A]IPpCaQppSI]wkECD?VgAMKRVF|AiWFoR?TqGSOwjk` | 36 | 252 | 3 | 4 | -1 | agree |

Invariant values at `broom(6,4)`: `annih = 7`, `deg_avg = 9/5`, `res = 5`

Gate: PASS — 0 counterexamples in `D` under this arm's reading (path A) and 0 (path B); recorded equality witnesses all tight: True.

## Targets read twice: `ceil(lambda_1)`

`scripts/gen/invariants._spectral_bracket` decides `ceil(lambda_1)` with `if det(fl*I - A) == 0: return fl, fl`, which tests whether `fl = floor(lambda_1)` is *an* eigenvalue rather than the *largest* one. On `P_5` (graph6 `Dh_`, spectrum ±√3, ±1, 0) it returns `ceil(lambda_1) = 1` where the true value is 2; **19 of the 12,112 members of `D` are affected**, `floor(lambda_1)` on none of them. This arm uses the mathematically correct `ceil(lambda_1)` (exact, via the Perron null-space test in [`arm_catalogue_spec.py`](../../scripts/exp/arm_catalogue_spec.py)) and reports every target naming it under **both** readings, so no verdict can hinge on the discrepancy.

| id | verdict, corrected reading | verdict, generator's reading | generator reading: counterexamples in `D` |
|---|---|---|---|
| FP-008 | **CROSSED** | CROSSED | 0 |

## Verification

**Second code path.** Every invariant and every statement was computed twice: path A is the campaign's own `scripts/gen/invariants.py` + `scripts/gen/expressions.py`; path B (`scripts/exp/arm_catalogue_pathb.py`) shares no code with it — SAT (`python-sat`) for the chromatic, matching and four domination numbers, `networkx.max_weight_clique` for independence, clique and local independence, a vertex-splitting max-flow for connectivity, and a separate `Fraction` evaluator for the expression AST. Invariant disagreements on the catalogue: **0**.


**Two substitutions inside path A, both recorded.** (1) The chromatic number: `scripts/gen/invariants._chromatic_brute` is a static-order branch and bound that does not terminate on T(9), C5[K5] or C5[K6] (> 60 s each), so path A uses saturation-ordered branch and bound closed between an explicit greedy colouring and the bound `max(omega, ceil(n/alpha))` ([`arm_catalogue_chi.py`](../../scripts/exp/arm_catalogue_chi.py)); path B's chromatic number is SAT-based and independent of it. (2) `ceil(lambda_1)`, for the reason given above. Neither substitution changes any value on `D`: the slack histograms below reproduce `population.json` exactly on 29 of 30 targets, the exception being the one target that names `ceil(lambda_1)`.

**Database-sanity gate.** `D` was rebuilt from `scripts/gen/graph_db.py` (12112 graphs, sha256 `08a53734416cc3f4`, recorded `08a53734416cc3f4` — match) and all 30 targets were re-evaluated over all of it under this arm's reading, through both paths. Invariant/slack path mismatches over `D`: 0.

| id | counterexamples in `D` (A / B) | equality count mine / recorded | slack histogram identical to population.json | recorded witnesses tight | gate |
|---|---|---|---|---|---|
| FP-001 | 0 / 0 | 16 / 16 | yes | yes | PASS |
| FP-002 | 0 / 0 | 249 / 249 | yes | yes | PASS |
| FP-003 | 0 / 0 | 6696 / 6696 | yes | yes | PASS |
| FP-004 | 0 / 0 | 2 / 2 | yes | yes | PASS |
| FP-005 | 0 / 0 | 3922 / 3922 | yes | yes | PASS |
| FP-006 | 0 / 0 | 5731 / 5731 | yes | yes | PASS |
| FP-007 | 0 / 0 | 6 / 6 | yes | yes | PASS |
| FP-008 | 0 / 0 | 6 / 7 | no | no | PASS |
| FP-009 | 0 / 0 | 704 / 704 | yes | yes | PASS |
| FP-010 | 0 / 0 | 216 / 216 | yes | yes | PASS |
| FP-011 | 0 / 0 | 1509 / 1509 | yes | yes | PASS |
| FP-012 | 0 / 0 | 17 / 17 | yes | yes | PASS |
| FP-013 | 0 / 0 | 39 / 39 | yes | yes | PASS |
| FP-014 | 0 / 0 | 85 / 85 | yes | yes | PASS |
| FP-015 | 0 / 0 | 3 / 3 | yes | yes | PASS |
| FP-016 | 0 / 0 | 290 / 290 | yes | yes | PASS |
| FP-017 | 0 / 0 | 400 / 400 | yes | yes | PASS |
| FP-018 | 0 / 0 | 4972 / 4972 | yes | yes | PASS |
| FP-019 | 0 / 0 | 175 / 175 | yes | yes | PASS |
| FP-020 | 0 / 0 | 1284 / 1284 | yes | yes | PASS |
| FP-021 | 0 / 0 | 335 / 335 | yes | yes | PASS |
| FP-022 | 0 / 0 | 380 / 380 | yes | yes | PASS |
| FP-023 | 0 / 0 | 30 / 30 | yes | yes | PASS |
| FP-024 | 0 / 0 | 10407 / 10407 | yes | yes | PASS |
| FP-025 | 0 / 0 | 58 / 58 | yes | yes | PASS |
| FP-026 | 0 / 0 | 747 / 747 | yes | yes | PASS |
| FP-027 | 0 / 0 | 215 / 215 | yes | yes | PASS |
| FP-028 | 0 / 0 | 7 / 7 | yes | yes | PASS |
| FP-029 | 0 / 0 | 32 / 32 | yes | yes | PASS |
| FP-030 | 0 / 0 | 2216 / 2216 | yes | yes | PASS |

## Budget

Preregistered cap: 1 CPU-hour per target. Seconds charged to a target = its own evaluation time over the 68 catalogue graphs plus the wall clock of every invariant block it names, in **both** code paths, summed over all 68 graphs. Shared invariant work is therefore charged in full to every target that needs it, which over-counts rather than under-counts. Shared setup wall clock was 0.0 s in total.

The whole database-sanity gate (rebuilding `D` and re-evaluating all 30 targets over all 12,112 graphs through both paths) cost 95 s once; the last column charges that entire cost again to *every* target. The largest figure anywhere below is 113 s against a 3600 s cap, so no target came close to the budget and none is a bracket for time.

| id | s charged | s evaluation only | s incl. whole gate |
|---|---|---|---|
| FP-001 | 16.18 | 0.0184 | 111.3 |
| FP-002 | 16.36 | 0.0178 | 111.5 |
| FP-003 | 16.55 | 0.0171 | 111.6 |
| FP-004 | 16.13 | 0.0185 | 111.2 |
| FP-005 | 17.23 | 0.0145 | 112.3 |
| FP-006 | 16.34 | 0.0149 | 111.4 |
| FP-007 | 17.40 | 0.0120 | 112.5 |
| FP-008 | 16.13 | 0.0126 | 111.2 |
| FP-009 | 16.64 | 0.0175 | 111.7 |
| FP-010 | 17.55 | 0.0157 | 112.7 |
| FP-011 | 16.28 | 0.0153 | 111.4 |
| FP-012 | 17.41 | 0.0142 | 112.5 |
| FP-013 | 17.41 | 0.0132 | 112.5 |
| FP-014 | 17.41 | 0.0146 | 112.5 |
| FP-015 | 16.29 | 0.0150 | 111.4 |
| FP-016 | 16.49 | 0.0137 | 111.6 |
| FP-017 | 17.23 | 0.0137 | 112.3 |
| FP-018 | 17.37 | 0.0126 | 112.5 |
| FP-019 | 16.13 | 0.0147 | 111.2 |
| FP-020 | 16.13 | 0.0131 | 111.2 |
| FP-021 | 16.49 | 0.0132 | 111.6 |
| FP-022 | 16.49 | 0.0124 | 111.6 |
| FP-023 | 17.94 | 0.0134 | 113.0 |
| FP-024 | 16.13 | 0.0132 | 111.2 |
| FP-025 | 16.49 | 0.0136 | 111.6 |
| FP-026 | 16.13 | 0.0132 | 111.2 |
| FP-027 | 16.13 | 0.0139 | 111.2 |
| FP-028 | 16.18 | 0.0137 | 111.3 |
| FP-029 | 16.13 | 0.0163 | 111.2 |
| FP-030 | 17.23 | 0.0137 | 112.3 |

