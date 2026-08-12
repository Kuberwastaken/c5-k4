# DB-sanity gate report

Graphs checked: 1000 (connected atlas n<=7 + C5,C7,P7,Petersen,K33)

| conj | reading | checked | violations | verdict | examples (name,lhs,rhs) |
|---|---|---|---|---|---|
| 232 | eccB=member(=diam) | 1000 | 360 | DISCARD (transcription artifact) | [('atlas#14(n=4)', 2.0, 2.5), ('atlas#30(n=5)', 2.0, 2.5), ('atlas#35(n=5)', 2.0, 2.5), ('atlas#36(n=5)', 2.0, 2.5)] |
| 232 | eccB=set(def52,empty->0) | 1000 | 0 | VIABLE |  |
| 233 | eccB=member(=diam) | 1000 | 445 | DISCARD (transcription artifact) | [('atlas#14(n=4)', 2.0, 2.6666666666666665), ('atlas#30(n=5)', 2.0, 2.6666666666666665), ('atlas#31(n=5)', 3.0, 3.3333333333333335), ('atlas#35(n=5)', 2.0, 2.6666666666666665)] |
| 233 | eccB=set(def52,empty->0) | 1000 | 0 | VIABLE |  |
| 247 | p exact | 19 | 0 | VIABLE |  |
| 255 | Ne excl endpoints | 999 | 263 | DISCARD (transcription artifact) | [('atlas#7(n=3)', 2.0, 6.0), ('atlas#16(n=4)', 2.0, 4.0), ('atlas#18(n=4)', 2.0, 4.0), ('atlas#38(n=5)', 3.0, 5.0)] |
| 255 | Ne incl endpoints | 1000 | 0 | VIABLE |  |
| 256 | Ne excl endpoints | 999 | 109 | DISCARD (transcription artifact) | [('atlas#7(n=3)', 2.0, 6.0), ('atlas#16(n=4)', 2.0, 4.0), ('atlas#18(n=4)', 2.0, 4.0), ('atlas#38(n=5)', 3.0, 5.0)] |
| 256 | Ne incl endpoints | 1000 | 0 | VIABLE |  |
| 258 | exact-squared | 1000 | 0 | VIABLE |  |
| 268 | dist_avg(C)=def95 set->V nonzero | 1000 | 0 | VIABLE |  |
| 268 | dist_avg(C)=pairwise-within(empty->0) | 1000 | 0 | VIABLE |  |
| 271 | single | 1000 | 0 | VIABLE |  |
| 305 | NbarA excl | 994 | 42 | DISCARD (transcription artifact) | [('atlas#6(n=3)', 2.0, 0.0), ('atlas#13(n=4)', 2.0, 1.0), ('atlas#15(n=4)', 2.0, 1.0), ('atlas#16(n=4)', 2.0, 0.0)] |
| 305 | NbarA incl (locked) | 994 | 0 | VIABLE |  |
| 305 | NbarB (e in G, N in bar) | 999 | 15 | DISCARD (transcription artifact) | [('atlas#6(n=3)', 2.0, 1.0), ('atlas#7(n=3)', 2.0, 0.0), ('atlas#17(n=4)', 2.0, 1.0), ('atlas#18(n=4)', 2.0, 0.0)] |
| 308 | NbarA excl|maxine_best | 994 | 138 | DISCARD (transcription artifact) | [('atlas#6(n=3)', 2.0, 1.0), ('atlas#14(n=4)', 2.0, 1.5), ('atlas#15(n=4)', 2.0, 1.5), ('atlas#16(n=4)', 2.0, 1.0)] |
| 308 | NbarA excl|maxine_det | 994 | 154 | DISCARD (transcription artifact) | [('atlas#6(n=3)', 2.0, 1.0), ('atlas#14(n=4)', 2.0, 1.5), ('atlas#15(n=4)', 2.0, 1.5), ('atlas#16(n=4)', 2.0, 1.0)] |
| 308 | NbarA incl (locked)|maxine_best | 994 | 0 | VIABLE |  |
| 308 | NbarA incl (locked)|maxine_det | 994 | 0 | VIABLE |  |
| 308 | NbarB (e in G, N in bar)|maxine_best | 999 | 135 | DISCARD (transcription artifact) | [('atlas#6(n=3)', 2.0, 1.5), ('atlas#7(n=3)', 2.0, 0.5), ('atlas#15(n=4)', 2.0, 1.5), ('atlas#17(n=4)', 2.0, 1.0)] |
| 308 | NbarB (e in G, N in bar)|maxine_det | 999 | 146 | DISCARD (transcription artifact) | [('atlas#6(n=3)', 2.0, 1.5), ('atlas#7(n=3)', 2.0, 0.5), ('atlas#15(n=4)', 2.0, 1.5), ('atlas#17(n=4)', 2.0, 1.0)] |
| 310 | single | 999 | 0 | VIABLE |  |
| 382a-CANARY(proved) | single | 999 | 0 | VIABLE |  |
| 382e | maxine_best | 999 | 0 | VIABLE |  |
| 382e | maxine_det | 999 | 0 | VIABLE |  |
| 401b | R1 literal: freq[T_max] (triangles) | 999 | 2 | DISCARD (transcription artifact) | [('atlas#77(n=6)', 5.0, 4.0), ('atlas#270(n=7)', 6.0, 4.0)] |
| 401b | R2: freq[Tdist_max] | 999 | 1 | DISCARD (transcription artifact) | [('atlas#270(n=7)', 6.0, 5.0)] |
| 402 | single | 999 | 0 | VIABLE |  |
| 416 | P empty -> rhs=-2 | 407 | 0 | VIABLE |  |
| 416 | single | 52 | 0 | VIABLE |  |
| 422b | single | 997 | 0 | VIABLE |  |
| 430a | N(C) open | 997 | 0 | VIABLE |  |
| 430a | N[C] closed | 997 | 0 | VIABLE |  |
| 438b | single | 997 | 0 | VIABLE |  |
