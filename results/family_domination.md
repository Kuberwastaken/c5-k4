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

