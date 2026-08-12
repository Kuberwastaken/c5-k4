# WOWII family domination hunt — incremental results

| graph | n | m | reg | rad | diam | alpha | mu | gamma | gamma_t | gamma_2 | i | alpha_2 | maxine d/b/w | p | Tdist mn/mx | Tmax(freq) | maxNe i/e | NbarA mx/mn | even_max | xcheck |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C5[K2]=B(2,2,2,2,2) | 10 | 25 | True | 2 | 2 | 2 | 5 | 2 | 3 | 4 | 2 | 4 | 2/2/2 | 1 | 13/13 | 6(10) | 8/6 | 8/8 | 5 | OK |

> **C5[K2]=B(2,2,2,2,2)** (0.0s): violations: **VIOLATION 255 [Ne excl endpoints] lhs=3.0 rhs=3.3333333333333335**; **VIOLATION 256 [Ne excl endpoints] lhs=3.0 rhs=3.3333333333333335**; **VIOLATION 401b [R1 literal: freq[T_max] (triangles)] lhs=4.0 rhs=3.0**; **VIOLATION 401b [R2: freq[Tdist_max]] lhs=4.0 rhs=3.0**. closest holds: 308[NbarB (e in G, N in bar)|maxine_best] slack=0.000; 308[NbarB (e in G, N in bar)|maxine_det] slack=0.000; 382e[maxine_best] slack=0.000; 382e[maxine_det] slack=0.000; 422b[single] slack=0.000

| C5[K3] | 15 | 60 | True | 2 | 2 | 2 | 7 | 2 | 3 | 4 | 2 | 4 | 2/2/2 | 1 | 20/20 | 19(15) | 12/10 | 12/12 | 7 | OK |

> **C5[K3]** (0.3s): violations: none. closest holds: 255[Ne excl endpoints] slack=0.000; 256[Ne excl endpoints] slack=0.000; 382e[maxine_best] slack=0.000; 382e[maxine_det] slack=0.000; 401b[R1 literal: freq[T_max] (triangles)] slack=0.000

| C5[K4]-carrier-control | 20 | 110 | True | 2 | 2 | 2 | 10 | 2 | 3 | 4 | 2 | 4 | 2/2/2 | 1 | 27/27 | 39(20) | 16/14 | 16/16 | 9 | OK |

> **C5[K4]-carrier-control** (0.5s): violations: none. closest holds: 382e[maxine_best] slack=0.000; 382e[maxine_det] slack=0.000; 401b[R1 literal: freq[T_max] (triangles)] slack=0.000; 401b[R2: freq[Tdist_max]] slack=0.000; 422b[single] slack=0.000

| C5[K5] | 25 | 175 | True | 2 | 2 | 2 | 12 | 2 | 3 | 4 | 2 | 4 | 2/2/2 | 1 | 34/34 | 66(25) | 20/18 | 20/20 | 11 | OK |

> **C5[K5]** (0.7s): violations: none. closest holds: 382e[maxine_best] slack=0.000; 382e[maxine_det] slack=0.000; 401b[R1 literal: freq[T_max] (triangles)] slack=0.000; 401b[R2: freq[Tdist_max]] slack=0.000; 422b[single] slack=0.000

| C5[K6] | 30 | 255 | True | 2 | 2 | 2 | 15 | 2 | 3 | 4 | 2 | 4 | 2/2/2 | 1 | 41/41 | 100(30) | 24/22 | 24/24 | 13 | OK |

> **C5[K6]** (1.1s): violations: none. closest holds: 382e[maxine_best] slack=0.000; 382e[maxine_det] slack=0.000; 401b[R1 literal: freq[T_max] (triangles)] slack=0.000; 401b[R2: freq[Tdist_max]] slack=0.000; 422b[single] slack=0.000

| C7[K2] | 14 | 35 | True | 3 | 3 | 3 | 7 | 3 | 4 | 5 | 3 | 6 | 3/3/3 | 1 | 25/25 | 6(14) | 8/6 | 14/12 | 5 | OK |

> **C7[K2]** (0.2s): violations: **VIOLATION 255 [Ne excl endpoints] lhs=4.0 rhs=4.666666666666667**; **VIOLATION 256 [Ne excl endpoints] lhs=4.0 rhs=4.666666666666667**. closest holds: 401b[R1 literal: freq[T_max] (triangles)] slack=0.000; 401b[R2: freq[Tdist_max]] slack=0.000; 422b[single] slack=0.000; 438b[single] slack=0.000; 255[Ne incl endpoints] slack=0.500

| C7[K3] | 21 | 84 | True | 3 | 3 | 3 | 10 | 3 | 4 | 5 | 3 | 6 | 3/3/3 | 1 | 38/38 | 19(21) | 12/10 | 21/18 | 7 | OK |

> **C7[K3]** (0.5s): violations: **VIOLATION 255 [Ne excl endpoints] lhs=4.0 rhs=4.2**; **VIOLATION 256 [Ne excl endpoints] lhs=4.0 rhs=4.2**. closest holds: 401b[R1 literal: freq[T_max] (triangles)] slack=0.000; 401b[R2: freq[Tdist_max]] slack=0.000; 422b[single] slack=0.000; 438b[single] slack=0.000; 255[Ne incl endpoints] slack=0.500

| C7[K4] | 28 | 154 | True | 3 | 3 | 3 | 14 | 3 | 4 | 5 | 3 | 6 | 3/3/3 | 1 | 51/51 | 39(28) | 16/14 | 28/24 | 9 | OK |

> **C7[K4]** (1.1s): violations: none. closest holds: 255[Ne excl endpoints] slack=0.000; 256[Ne excl endpoints] slack=0.000; 401b[R1 literal: freq[T_max] (triangles)] slack=0.000; 401b[R2: freq[Tdist_max]] slack=0.000; 422b[single] slack=0.000

| C9[K3] | 27 | 108 | True | 4 | 4 | 4 | 13 | 3 | 5 | 6 | 3 | 8 | 4/4/4 | 1 | 62/62 | 19(27) | 12/10 | 27/24 | 13 | OK |

> **C9[K3]** (1.2s): violations: **VIOLATION 255 [Ne excl endpoints] lhs=5.0 rhs=5.4**; **VIOLATION 256 [Ne excl endpoints] lhs=5.0 rhs=5.4**. closest holds: 401b[R1 literal: freq[T_max] (triangles)] slack=0.000; 401b[R2: freq[Tdist_max]] slack=0.000; 438b[single] slack=0.000; 255[Ne incl endpoints] slack=0.500; 256[Ne incl endpoints] slack=0.500

| B(4,4,3,4,3) | 18 | 88 | False | 2 | 2 | 2 | 9 | 2 | 3 | 4 | 2 | 4 | 2/2/2 | 1 | 24/25 | 33(8) | 15/13 | 15/14 | 9 | OK |

> **B(4,4,3,4,3)** (0.5s): violations: none. closest holds: 382e[maxine_best] slack=0.000; 382e[maxine_det] slack=0.000; 430a[N(C) open] slack=0.000; 430a[N[C] closed] slack=0.000; 438b[single] slack=0.000

| B(4,2,4,2,4) | 16 | 68 | False | 2 | 2 | 2 | 8 | 2 | 3 | 4 | 2 | 4 | 2/2/2 | 1 | 21/23 | 28(8) | 14/12 | 14/12 | 9 | OK |

> **B(4,2,4,2,4)** (0.4s): violations: none. closest holds: 382e[maxine_best] slack=0.000; 382e[maxine_det] slack=0.000; 430a[N(C) open] slack=0.000; 430a[N[C] closed] slack=0.000; 438b[single] slack=0.000

| B(4,1,4,1,4) | 14 | 50 | False | 2 | 2 | 2 | 7 | 2 | 3 | 3 | 2 | 4 | 2/2/2 | 1 | 18/21 | 24(8) | 13/11 | 13/10 | 9 | OK |

> **B(4,1,4,1,4)** (0.2s): violations: none. closest holds: 430a[N(C) open] slack=0.000; 430a[N[C] closed] slack=0.000; 438b[single] slack=0.000; 255[Ne excl endpoints] slack=0.455; 308[NbarB (e in G, N in bar)|maxine_best] slack=0.500

| comp(C5[K4]) | 20 | 80 | True | 2 | 2 | 8 | 10 | 3 | 3 | 5 | 8 | 8 | 8/8/8 | 1 | 30/30 | 0(20) | 16/14 | 16/12 | 12 | OK |

> **comp(C5[K4])** (0.4s): violations: **VIOLATION 401b [R1 literal: freq[T_max] (triangles)] lhs=5.0 rhs=4.0**; **VIOLATION 401b [R2: freq[Tdist_max]] lhs=5.0 rhs=4.0**. closest holds: 422b[single] slack=0.000; 255[Ne excl endpoints] slack=0.143; 256[Ne excl endpoints] slack=0.143; 255[Ne incl endpoints] slack=0.500; 256[Ne incl endpoints] slack=0.500


---
## FINAL VERDICT (2026-08-12)

**NEW KILLS: none.** Under every DB-sanity-viable reading, all 18 target conjectures hold on
all 13 family graphs (C5[K2,3,4,5,6], C7[K2,3,4], C9[K3], B(4,4,3,4,3), B(4,2,4,2,4),
B(4,1,4,1,4), comp(C5[K4])). All CBC solves Optimal (none hit the 60s cap); every NP invariant
independently confirmed by exact blob-count-vector enumeration (0 mismatches); proved canary
382a: 0 violations on 1000 gate graphs and slack-0-tight on C5[K2] (4 = 2*2-0).

**Gate-refuted transcription artifact (documented, NOT a kill): conjecture 401b**
`gamma_2 <= floor[3*Tdist_max / freq[T_max(v)]]` as transcribed is violated by
K1,5 (gamma_2=5 > floor(3*9/6)=4) and K1,6 (gamma_2=6 > floor(3*11/7)=4) — stars inside
Graffiti.pc's own trivial range, so the recorded formula cannot be what the program conjectured.
Both readings (freq of triangle-max; freq of transmission-max) fail the gate. The family
"violations" it produced — C5[K2]: gamma_2=4 > floor(39/10)=3; comp(C5[K4]): gamma_2=5 >
floor(90/20)=4 (both gamma_2 values double-confirmed by BnB/blob-vector) — are therefore
discarded per protocol. 401b is unattackable from this transcription; needs the original page.

Likewise discarded: 255/256 under the excl-endpoints N(e) reading (fails gate on C7 itself);
locked incl-endpoints reading holds family-wide (min slack 0.5).

**Closest misses (viable readings), slack = lhs-rhs / rhs-lhs:**
| conj | tightest family witness | lhs vs rhs |
|---|---|---|
| 382e | all C5[K_m], B(4,4,3,4,3), B(4,2,4,2,4): gamma_2 = maxine+gamma | 4 = 2+2, slack 0 |
| 422b | comp(C5[K4]): i = alpha(G[M])+gamma(G[V-M])^2 | 8 = 8+0, slack 0 (also C5/C7 uniform: 2=2, 3=3) |
| 430a | B(4,1,4,1,4) & all C5-blowups: i = alpha(G[N(C)])+2*floor(CW-1) | 2 = 2+0, slack 0 |
| 438b | B(4,1,4,1,4), C5[K_m] (4=2*2), C7[K2/K3] (6=6), C9[K3] (8=8) | slack 0 |
| 255/256 | comp(C5[K4]), C7[K2] | 3 vs 2.5; 4 vs 3.5 — slack 0.5 |
| 247/268/271 | comp(C5[K4]) | 3 vs 2 — slack 1 |
| 402 | comp(C5[K4]): gamma_2=5 vs 2*(0+0+3)=6 | slack 1 |

Slack-0 walls: 382e/422b/430a/438b are *exactly tight* on multiple family members —
the blown-up-C5 geometry saturates them but cannot cross; a kill needs a mechanism that
raises gamma_2 (resp. i, alpha_2) while pinning maxine+gamma (resp. the RHS sets), which
uniform/non-uniform cycle blowups cannot do (window arguments cap the LHS at exactly the RHS).
