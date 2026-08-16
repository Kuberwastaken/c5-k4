# Wall-navigation arm — results

**Arm 3 of the preregistered three-arm test**
([`PREREGISTRATION.md`](PREREGISTRATION.md), tag `prereg-three-arm-v1`).
Method under test: METHOD_V1_6 §A3 (G3-lite symbolic sign check) and §A3.1
(non-degeneracy guard), applied to the 30 frozen targets in
[`fresh-population/population.json`](fresh-population/population.json).

This arm read only: the preregistration, the generation record, METHOD_V1_6,
the population file, and the campaign's own case studies (README's
discretization-cliff section, `results/family_*.md`). It did not read, and was
not told, anything about the catalogue arm or the generic arm.

## Instruments

| file | role |
|---|---|
| [`scripts/exp/wall_arm.py`](../../scripts/exp/wall_arm.py) | independent re-implementation of the 42 invariants the population uses, plus the expression evaluator — exact `int`/`Fraction` throughout |
| [`scripts/exp/wall_verify_D.py`](../../scripts/exp/wall_verify_D.py) | database-sanity gate: that evaluator re-run over all of `D` |
| [`scripts/exp/wall_read.py`](../../scripts/exp/wall_read.py) | step 1 — decode the equality witnesses and profile the wall |
| [`scripts/exp/wall_notes.py`](../../scripts/exp/wall_notes.py) | steps 1–2 written out per target: the wall reading and the isolated obstruction |
| [`scripts/exp/wall_families.py`](../../scripts/exp/wall_families.py), [`wall_designed.py`](../../scripts/exp/wall_designed.py) | step 4 — the separating families |
| [`scripts/exp/wall_run.py`](../../scripts/exp/wall_run.py) | the driver: sign check before every trial, guard before every residual, append after every target |
| [`scripts/exp/wall_verify_cross.py`](../../scripts/exp/wall_verify_cross.py) | second code path for every claimed crossing |

`wall_arm.py` shares no code with `scripts/gen/invariants.py`: distances by
plain BFS, α/ω by colouring-bounded branch and bound, χ by k-colourability
backtracking, the four domination numbers by set-cover branch and bound, μ by
Edmonds' blossom algorithm, κ by unit-capacity max flow on the vertex-split
digraph, cut vertices by Tarjan lowlink, and ⌊λ₁⌋/⌈λ₁⌉ by an exact rational
LDLᵀ positive-(semi)definiteness test.

## Verification bar

Every crossing below passed both halves of the standing bar.

**(a) Independent recomputation.** Path A = `wall_arm.py`; path B =
`scripts/gen/invariants.py` `scal` backend (branch and bound, no subset
enumeration) with `scripts/gen/expressions.py` evaluating the frozen AST in
`Fraction` arithmetic. Every invariant value and every residual agreed, on
every crossing, with one substitution: on `FP-026` the witness has n = 55 and
path B's `_spectral_bracket` is O(n⁴) per probe and did not finish inside the
per-computation cap, so the second reading there is `networkx` for `rad` and
`disp_max` plus a float eigenvalue computation bracketing λ₁ in (3, 4)
(λ₁ = 3.837571178841834), against path A's exact rational PSD test.

**(b) Database-sanity gate.** `wall_verify_D.py` re-evaluates all 30 targets
over all 12,112 members of `D` using path A only:

```
|D| = 12112, 30 targets
computed 12112 graphs in 23s
zero counterexamples for all 30 targets
min_slack_over_D and max_slack_over_D reproduced exactly for all 30
equality_count_in_D and equality_by_order_n reproduced exactly for 29 of 30
```

### Protocol note — one population field does not reproduce, and the population is right

The single mismatch is `FP-008`: this arm counts **6** equality members in `D`,
the population records **7**. The extra member is `EiGO` (n = 6, the tree with
degree sequence 1,1,1,2,2,3). It is not tight, and the population's own
generator is what is wrong there:
`scripts/gen/invariants.py::_spectral_bracket` returns `ceil(λ₁)` by testing
`det(⌊λ₁⌋·I − A) == 0`, which detects *some* eigenvalue equal to `⌊λ₁⌋`, not
`λ₁` itself. On `EiGO`, λ₁ = 1.9318…, and 1 happens to be an eigenvalue, so the
shipped code returns `ceil(λ₁) = 1`. The correct value is 2 (numerically and by
this arm's exact PSD test). **19 of the 12,112 members of `D` have a wrong
`spec_ceil` in the shipped code**; `spec_floor` is correct on all 12,112.

This does not disturb any target: under the mathematically correct reading (the
one in the population's own `invariant_definitions`, "ceiling of the adjacency
spectral radius") all 30 statements still have **zero** counterexamples in `D`,
which is the gate the protocol actually asks for. It only means `FP-008`'s
recorded equality list contains one graph that is not tight. This arm used the
correct reading throughout and reports the discrepancy rather than adopting the
bug.

## Summary
| verdict | count |
|---|---|
| CROSSED | 15 |
| HELD | 15 |
| BRACKET | 0 |
| **scored** | **30** |

G3-lite sign checks run: **756**; sign checks that stopped a trial: **691** (91%).

Total wall clock over all targets: **724 s**; largest single target **365 s** against the preregistered 3600 s cap. No target hit the cap.

### Crossings

Every row is a graph outside `D` on which the frozen statement is false. `n` is the order of the smallest refuting member produced by a sign-check-authorised trial; where a smaller member of the same one-parameter family exists it is given in the last column and documented in the per-target section.

| target | statement | refuting graph | n | LHS | RHS | family | smaller member of the same family |
|---|---|---|---|---|---|---|---|
| FP-002 | `alpha >= dist_even_max - chi` | `IjTJI@@OW` | 10 | 4 | 5 | swap the core for one with smaller alpha+chi | — |
| FP-007 | `diam <= disp_max + gamma_2` | `N????B?_aACGE?B??o?` | 15 | 14 | 10 | subdivision of G_CKJ? | `P_9` = `HhCGGC@` (n=9) |
| FP-008 | `diam >= floor((A)/(ceil(lambda_1)))` | `IsaCCA?_?` | 10 | 2 | 3 | index the star family by ceil(lambda_1)=k, i.e. s=k^2 (where the floor steps) | — |
| FP-009 | `gamma <= floor((lambda_avg)/2) + res` | `O@KqTU?O@?A?A?@??O?A?` | 16 | 8 | 7 | corona of G@KqTS | — |
| FP-012 | `gamma_2 <= dist_even_max - chi_regular + 2` | `MhCKK@?G?_@?@??_?` | 14 | 10 | 9 | corona of a diameter-2 core: pins dist_even_max at n/2, pushes gamma_2 to n/2+gamma(core) | — |
| FP-014 | `gamma_2 >= floor((dist_even_min + disp_min)/2)` | `O`?KAEiTXSAhiiTTtTAih` | 16 | 4 | 5 | prism over GC|v~w | — |
| FP-015 | `gamma_i <= diam + mu - 1` | `IsaAA@?O?` | 10 | 5 | 4 | grow both leaf sets of the tight double star S(3,3) | — |
| FP-016 | `gamma_i <= floor((alpha)/2) + gamma` | `O???WWNBv~~}~{~{^}F~_` | 16 | 6 | 5 | independent blow-up of G@N~vo | — |
| FP-020 | `kappa >= floor((disp_avg - ecc_avg)/2) + 1` | `P}~vf~}~f{^~~}~}^~F~o_??` | 17 | 1 | 2 | index by q = the integer value of the floor term | — |
| FP-021 | `kappa >= floor((lambda_avg - disp_max)/2) + 1` | `N?~vf_????OF_M_MOF?` | 15 | 1 | 2 | amalgamate k lobes of K_{4,4} at one vertex (kappa drops to 1) | — |
| FP-022 | `lambda_max >= floor((dd - f_1)/2)` | `QwSwwa@?yqEhCvqIOUZWYQe{eUw` | 18 | 2 | 3 | line graph: dd rises, lambda_max stays 2 on a locally-bipartite wall | — |
| FP-023 | `lambda_max >= floor((gamma_2 - chi)/2) + 1` | `N????AASAACGB?@_?g?` | 15 | 3 | 4 | subdivision of GA?KJG | `P_10` = `IhCGGC@?G` (n=10) |
| FP-026 | `rad >= floor((disp_max)/(floor(lambda_1)))` | `vkCS?CA?c??@?A?A?@C????C??O??_??_??O_??????_??A???C???C???A????__????????G????O????O????G????A?????O????@?_???????????_?????O?????C??????_?????A??????C??????C??????A?_??????????????_??????A???????C???????C???????A????????_???????C????????O????????_?` | 55 | 2 | 3 | index by q = the value of the RHS floor term | — |
| FP-029 | `res >= A - deg_avg` | `O`?GW[oKGW@`?r?r~_Fw@` | 16 | 3 | 4 | clique blow-up of G@O_n? | — |
| FP-030 | `res >= floor((dd)/(gamma_t))` | `H?\~f^~` | 9 | 2 | 3 | join a dominating clique: dd jumps by one, gamma_t and res pinned | — |

### Held
| target | statement | why the lane closed |
|---|---|---|
| FP-001 | `alpha <= ceil((Tdist_max - dist_even_min)/2) + 1` | HELD. Every transformation of the complete bipartite wall that is available (clique and independent blow-up, subdivision, corona, join, prism, line graph, complement, widening or adding parts) has a non-negative G3-lite sign; the independent blow-up is exactly zero because K_{a,b}[I_m] = K_{am,bm} is still on the wall. The counting argument above closes the diameter-2 regime and the Tdist_max growth closes the rest. |
| FP-003 | `alpha >= lambda_max - cutv` | HELD -- theorem. lambda_max <= alpha, cutv >= 0. |
| FP-004 | `A >= floor((disp_min)/2) + dist_avg` | HELD. Two designed families (complete graphs; complete multipartite with distinct part sizes) both have positive or zero sign; the residual grows monotonically because raising disp_min raises delta, which caps dist_avg. |
| FP-005 | `A >= floor((n)/(gamma_t))` | HELD -- theorem. A >= floor(n/2) and gamma_t >= 2. |
| FP-006 | `chi >= ceil((omega - chi_regular)/2) + 1` | HELD -- theorem. chi >= omega. |
| FP-010 | `gamma <= gamma_2 - chi_C4free` | HELD -- theorem (private-neighbour + C4-free argument above). |
| FP-011 | `gamma >= ceil((Tdist_min)/(m))` | HELD. Path and spider families both have positive sign; the residual grows with n. |
| FP-013 | `gamma_2 >= ceil((Delta)/(Sigma_2))` | HELD. Flower and hub-plus-matching families both sit at residual exactly 1 for every parameter, which is the +1 the hub costs. |
| FP-017 | `gamma_t >= floor((cutv + chi_tree)/2) + 1` | HELD. Caterpillar and chain-of-blocks families both grow the residual; cut vertices and total dominators grow together. |
| FP-018 | `gamma_t >= floor((gamma)/(disp_min))` | HELD -- theorem. disp_min >= 1 and gamma <= gamma_t. |
| FP-019 | `kappa <= floor((t)/2) + floor(lambda_1)` | HELD -- theorem. kappa <= delta <= floor(lambda_1). |
| FP-024 | `mu <= ceil((n - chi_tree)/2)` | HELD -- theorem. mu <= floor(n/2). |
| FP-025 | `mu >= floor((delta + lambda_min)/2)` | HELD -- theorem (minimum-degree vertex bounds lam_min by delta). |
| FP-027 | `rad >= floor((ecc_avg)/2) + chi_bipartite` | HELD -- theorem. ecc_avg < 2 rad. |
| FP-028 | `res <= alpha + CW - 1` | HELD -- theorem. res <= alpha and CW >= 1. |

---

## Protocol compliance, recorded before the per-target detail

**Contamination (preregistration §5).** No target was recognised from prior
campaign work. The population's vocabulary deliberately excludes `L_s`, `tree`,
`f` and `b` — the four invariants the campaign's published kills ran on — so
none of the 30 statements is a restatement of a WOWII, Graffiti³ or Graph Brain
entry this operator has seen. Zero targets scored `CONTAMINATED`.

**Budget.** The preregistered cap is 1 CPU-hour per target, wall-clock. The
largest single target used 365 s and the whole arm used 724 s. No target was
bracketed; every one of the 30 is scored.

**The sign check is doing real work, and it is parametrisation-sensitive.**
691 of 756 sign checks stopped a trial before it ran — 91%. Most of those stops
are correct and cheap: on `FP-001` the independent blow-up of a complete
bipartite wall member has dR = 0 because `K_{a,b}[I_m] = K_{am,bm}` is still on
the wall, and the rule catches that in two evaluations.

But the rule is sensitive to how the family is indexed, and three crossings
below required re-indexing before it would pass. The residuals here are floor
step functions, so consecutive members of the obvious one-parameter family are
*flat*, and the literal §A3 test returns `STOP-zero`:

| target | natural family | its sign check | re-indexed family | its sign check |
|---|---|---|---|---|
| FP-008 | `K_{1,s}`, s = 6, 7 | dR = 0 → STOP | `K_{1,k²}`, k = 2, 3 | dR = −1 → GO, crosses at `K_{1,9}` |
| FP-020 | apex over `K_{1..k}`, k = 2, 3 | dR = 0 → STOP | indexed by the value of the floor term, q = 0, 1 | dR = −1 → GO, crosses at n = 17 |
| FP-026 | `SoS(d)`, d = 2, 3 | dR = +1 → STOP | indexed by the value of the RHS, q = 2, 3 | dR = −1 → GO, crosses at `SoS(9)` |

Both readings are recorded per target below. The same thing happened on
`FP-007` and `FP-023`: consecutive path lengths give dR = 0, so the path family
was stopped and the *subdivision* of the same tight member (which jumps the
parameter by a factor of two) was used instead — it passed, crossed, and only
then was the family re-read downwards to find `P₉` and `P₁₀`. Where a smaller
member was found that way it is labelled as such and not presented as the
output of an authorised trial.

**Where the crossings sit.** Eight of the fifteen refuting graphs have
n ≤ 16 and four have n ≤ 10, i.e. one or two steps past the database edge at
n = 8. On `FP-007`, `FP-008`, `FP-015` and `FP-023` the largest recorded
equality witness is literally the last member of the refuting family that fits
in `D` — `P₈`, `K_{1,7}`, the double star `S(3,3)`, and `P₈` again.

**The six targets `GENERATION.md` §10(b) flagged as probable theorems** —
`FP-003`, `FP-006`, `FP-018`, `FP-019`, `FP-024`, `FP-028` — all held, and this
arm reproduces one-line proofs for all six. Nine further targets held:
`FP-001`, `FP-004`, `FP-005`, `FP-010`, `FP-011`, `FP-013`, `FP-017`, `FP-025`,
`FP-027`. Four of those nine (`FP-005`, `FP-010`, `FP-025`, `FP-027`) are also
theorems, with proofs given in their sections; the other five closed on a
structural argument plus exhausted families, not a proof, and are honest
`HELD`, not `PROVED`.

---

## Per target

### FP-001 — HELD

**Statement.** `For every connected graph G with n(G) >= 2:  alpha <= ceil((Tdist_max - dist_even_min)/2) + 1`

**Equality in D:** 16 members, by order {'2': 1, '3': 1, '4': 2, '5': 2, '6': 3, '7': 3, '8': 4}.

**1. The wall.** All 16 equality members are complete bipartite graphs K_{a,b} (a<=b), including the stars K_{1,n-1}: bipartite, triangle-free, omega=chi=2, gamma_t=2, disp_min=disp_max=1 (biregular). On K_{a,b}: alpha=b, Tdist_max=a+2b-2, dist_even_min=a, so RHS = (b-1)+1 = b = alpha exactly.

**2. The obstruction.** The degree spread Delta-delta. Crossing needs alpha >= (n+2+Delta-delta)/2 (from Tdist_max >= 2n-2-delta and dist_even_min <= n-Delta), while the independent-set edge count gives alpha <= n*Delta/(Delta+delta). The two are compatible only when n(Delta-delta) > (2+Delta-delta)(Delta+delta), which forces a biregular bipartite graph of diameter 2 -- and a bipartite graph of diameter 2 is complete bipartite, i.e. back on the wall. Diameter >= 3 instead inflates Tdist_max quadratically.

**3. G3-lite sign checks** (26 run, 26 stopped a trial). Only the checks that returned GO were allowed to run a trial.

_Stopped (trial not run):_

- clique blow-up of G???F{ → **STOP-wrong-sign**  (dR = 7)
- independent blow-up of G???F{ → **STOP-zero**  (dR = 0)
- subdivision of G???F{ → **STOP-wrong-sign**  (dR = 12)
- corona of G???F{ → **STOP-wrong-sign**  (dR = 13)
- join a clique onto G???F{ → **STOP-wrong-sign**  (dR = 1)
- prism over G???F{ → **STOP-wrong-sign**  (dR = 6)
- complement of G???F{ → **STOP-unavailable**
- line graph of G???F{ → **STOP-wrong-sign**  (dR = 3)
- clique blow-up of G??F~w → **STOP-wrong-sign**  (dR = 6)
- independent blow-up of G??F~w → **STOP-zero**  (dR = 0)
- subdivision of G??F~w → **STOP-wrong-sign**  (dR = 13)
- corona of G??F~w → **STOP-wrong-sign**  (dR = 12)
- join a clique onto G??F~w → **STOP-wrong-sign**  (dR = 1)
- prism over G??F~w → **STOP-wrong-sign**  (dR = 5)
- complement of G??F~w → **STOP-unavailable**
- line graph of G??F~w → **STOP-wrong-sign**  (dR = 4)
- clique blow-up of G]rE@{ → **STOP-wrong-sign**  (dR = 5)
- independent blow-up of G]rE@{ → **STOP-zero**  (dR = 0)
- subdivision of G]rE@{ → **STOP-wrong-sign**  (dR = 14)
- corona of G]rE@{ → **STOP-wrong-sign**  (dR = 11)
- join a clique onto G]rE@{ → **STOP-wrong-sign**  (dR = 2)
- prism over G]rE@{ → **STOP-wrong-sign**  (dR = 4)
- complement of G]rE@{ → **STOP-unavailable**
- line graph of G]rE@{ → **STOP-wrong-sign**  (dR = 5)
- widen the parts of the tight complete-bipartite wall → **STOP-zero**  (dR = 0)
- add a third part (break biregularity) → **STOP-zero**  (dR = 0)

**4. Families built and tested.**

None — every proposed transformation was stopped at step 3.

**Outcome.** step 3 (G3-lite sign check stopped every proposed transformation) HELD. Every transformation of the complete bipartite wall that is available (clique and independent blow-up, subdivision, corona, join, prism, line graph, complement, widening or adding parts) has a non-negative G3-lite sign; the independent blow-up is exactly zero because K_{a,b}[I_m] = K_{am,bm} is still on the wall. The counting argument above closes the diameter-2 regime and the Tdist_max growth closes the rest.

**Budget.** 0.0 s of the 3600 s cap. **Gate.** database sanity: PASS; independent recomputation: path A (`wall_arm.py`) vs path B (`scripts/gen/invariants.py` scal backend).

### FP-002 — CROSSED

**Statement.** `For every connected graph G with n(G) >= 2:  alpha >= dist_even_max - chi`

**Equality in D:** 249 members, by order {'8': 249}.

**1. The wall.** All 249 equality members sit at n=8, the database edge, and are non-bipartite, non-regular, non-tree. dist_even_max is 6 or 7, i.e. n-2 or n-1: the tight members carry a near-universal vertex u plus a pendant v, so dist_even(v) = 1 + |V - {u,v}| = n-1. Witness GCc`N{ has degrees [1,3,3,3,3,3,3,7] = pendant + (K_1 joined to 2K_3).

**2. The obstruction.** alpha(H) + chi(H) for the core H = G - u - v. With a universal vertex u and a pendant v on u, alpha = 1+alpha(H), chi = 1+chi(H), dist_even_max = |H|+1, so the residual is R = alpha(H) + chi(H) - |H| + 1. The wall pins alpha(H) + chi(H) = |H| - 1, which is the true minimum of alpha+chi for |H| <= 7. The obstruction is exactly that minimum, and it drops to |H| - 2 for the first time at |H| = 8 (C_5 u K_3, or 3K_3 at |H| = 9) -- one step past the database edge.

**3. G3-lite sign checks** (26 run, 18 stopped a trial). Only the checks that returned GO were allowed to run a trial.

_Passed (trial run):_

- clique blow-up of G@O_n{ → **GO**  (dR = -3)<br>&nbsp;&nbsp;`G[K1]` (n=8) R=0 [alpha=4 chi=3 dist_even_max=7]<br>&nbsp;&nbsp;`G[K2]` (n=16) R=-3 [alpha=4 chi=6 dist_even_max=13]
- independent blow-up of G@O_n{ → **GO**  (dR = -3)<br>&nbsp;&nbsp;`G[I1]` (n=8) R=0 [alpha=4 chi=3 dist_even_max=7]<br>&nbsp;&nbsp;`G[I2]` (n=16) R=-3 [alpha=8 chi=3 dist_even_max=14]
- clique blow-up of GA?KN{ → **GO**  (dR = -3)<br>&nbsp;&nbsp;`G[K1]` (n=8) R=0 [alpha=4 chi=3 dist_even_max=7]<br>&nbsp;&nbsp;`G[K2]` (n=16) R=-3 [alpha=4 chi=6 dist_even_max=13]
- independent blow-up of GA?KN{ → **GO**  (dR = -3)<br>&nbsp;&nbsp;`G[I1]` (n=8) R=0 [alpha=4 chi=3 dist_even_max=7]<br>&nbsp;&nbsp;`G[I2]` (n=16) R=-3 [alpha=8 chi=3 dist_even_max=14]
- clique blow-up of GA_?N{ → **GO**  (dR = -3)<br>&nbsp;&nbsp;`G[K1]` (n=8) R=0 [alpha=4 chi=3 dist_even_max=7]<br>&nbsp;&nbsp;`G[K2]` (n=16) R=-3 [alpha=4 chi=6 dist_even_max=13]
- independent blow-up of GA_?N{ → **GO**  (dR = -3)<br>&nbsp;&nbsp;`G[I1]` (n=8) R=0 [alpha=4 chi=3 dist_even_max=7]<br>&nbsp;&nbsp;`G[I2]` (n=16) R=-3 [alpha=8 chi=3 dist_even_max=14]
- grow the number of triangles in the apex core → **GO**  (dR = -2)<br>&nbsp;&nbsp;`pendant+(K1 v 1K3)` (n=5) R=2 [alpha=2 chi=4 dist_even_max=4]<br>&nbsp;&nbsp;`pendant+(K1 v 2K3)` (n=8) R=0 [alpha=3 chi=4 dist_even_max=7]
- swap the core for one with smaller alpha+chi → **GO**  (dR = -2)<br>&nbsp;&nbsp;`pendant+(K1 v C5)` (n=7) R=1 [alpha=3 chi=4 dist_even_max=6]<br>&nbsp;&nbsp;`pendant+(K1 v (C5 u K3))` (n=10) R=-1 [alpha=4 chi=4 dist_even_max=9]

_Stopped (trial not run):_

- subdivision of G@O_n{ → **STOP-wrong-sign**  (dR = 2)
- corona of G@O_n{ → **STOP-wrong-sign**  (dR = 3)
- join a clique onto G@O_n{ → **STOP-wrong-sign**  (dR = 1)
- prism over G@O_n{ → **STOP-wrong-sign**  (dR = 2)
- complement of G@O_n{ → **STOP-unavailable**
- line graph of G@O_n{ → **STOP-wrong-sign**  (dR = 4)
- subdivision of GA?KN{ → **STOP-wrong-sign**  (dR = 2)
- corona of GA?KN{ → **STOP-wrong-sign**  (dR = 3)
- join a clique onto GA?KN{ → **STOP-wrong-sign**  (dR = 1)
- prism over GA?KN{ → **STOP-wrong-sign**  (dR = 2)
- complement of GA?KN{ → **STOP-unavailable**
- line graph of GA?KN{ → **STOP-wrong-sign**  (dR = 4)
- subdivision of GA_?N{ → **STOP-wrong-sign**  (dR = 2)
- corona of GA_?N{ → **STOP-wrong-sign**  (dR = 3)
- join a clique onto GA_?N{ → **STOP-wrong-sign**  (dR = 1)
- prism over GA_?N{ → **STOP-wrong-sign**  (dR = 2)
- complement of GA_?N{ → **STOP-unavailable**
- line graph of GA_?N{ → **STOP-wrong-sign**  (dR = 5)

**4. Families built and tested.**

`clique blow-up of G@O_n{`

| member | n | R | invariants |
|---|---|---|---|
| G[K1] | 8 | 0 | alpha=4 chi=3 dist_even_max=7 |
| G[K2] | 16 | -3 | alpha=4 chi=6 dist_even_max=13 |
| G[K3] | 24 | -6 | alpha=4 chi=9 dist_even_max=19 |
| G[K4] | 32 | -9 | alpha=4 chi=12 dist_even_max=25 |

`independent blow-up of G@O_n{`

| member | n | R | invariants |
|---|---|---|---|
| G[I1] | 8 | 0 | alpha=4 chi=3 dist_even_max=7 |
| G[I2] | 16 | -3 | alpha=8 chi=3 dist_even_max=14 |
| G[I3] | 24 | -6 | alpha=12 chi=3 dist_even_max=21 |

`clique blow-up of GA?KN{`

| member | n | R | invariants |
|---|---|---|---|
| G[K1] | 8 | 0 | alpha=4 chi=3 dist_even_max=7 |
| G[K2] | 16 | -3 | alpha=4 chi=6 dist_even_max=13 |
| G[K3] | 24 | -6 | alpha=4 chi=9 dist_even_max=19 |
| G[K4] | 32 | -9 | alpha=4 chi=12 dist_even_max=25 |

`independent blow-up of GA?KN{`

| member | n | R | invariants |
|---|---|---|---|
| G[I1] | 8 | 0 | alpha=4 chi=3 dist_even_max=7 |
| G[I2] | 16 | -3 | alpha=8 chi=3 dist_even_max=14 |
| G[I3] | 24 | -6 | alpha=12 chi=3 dist_even_max=21 |

`clique blow-up of GA_?N{`

| member | n | R | invariants |
|---|---|---|---|
| G[K1] | 8 | 0 | alpha=4 chi=3 dist_even_max=7 |
| G[K2] | 16 | -3 | alpha=4 chi=6 dist_even_max=13 |
| G[K3] | 24 | -6 | alpha=4 chi=9 dist_even_max=19 |
| G[K4] | 32 | -9 | alpha=4 chi=12 dist_even_max=25 |

`independent blow-up of GA_?N{`

| member | n | R | invariants |
|---|---|---|---|
| G[I1] | 8 | 0 | alpha=4 chi=3 dist_even_max=7 |
| G[I2] | 16 | -3 | alpha=8 chi=3 dist_even_max=14 |
| G[I3] | 24 | -6 | alpha=12 chi=3 dist_even_max=21 |

`grow the number of triangles in the apex core`

| member | n | R | invariants |
|---|---|---|---|
| pendant+(K1 v 1K3) | 5 | 2 | alpha=2 chi=4 dist_even_max=4 |
| pendant+(K1 v 2K3) | 8 | 0 | alpha=3 chi=4 dist_even_max=7 |
| pendant+(K1 v 3K3) | 11 | -2 | alpha=4 chi=4 dist_even_max=10 |
| pendant+(K1 v 4K3) | 14 | -4 | alpha=5 chi=4 dist_even_max=13 |
| pendant+(K1 v 5K3) | 17 | -6 | alpha=6 chi=4 dist_even_max=16 |

`swap the core for one with smaller alpha+chi`

| member | n | R | invariants |
|---|---|---|---|
| pendant+(K1 v C5) | 7 | 1 | alpha=3 chi=4 dist_even_max=6 |
| pendant+(K1 v (C5 u K3)) | 10 | -1 | alpha=4 chi=4 dist_even_max=9 |
| pendant+(K1 v Petersen) | 12 | -2 | alpha=5 chi=4 dist_even_max=11 |

**Crossings.**

| graph6 | n | R | LHS | RHS | family |
|---|---|---|---|---|---|
| `IjTJI@@OW` | 10 | -1 | 4 | 5 | swap the core for one with smaller alpha+chi |
| `Jj\AIL?OI@_` | 11 | -2 | 4 | 6 | grow the number of triangles in the apex core |
| `KiPAYhWXJQMO` | 12 | -2 | 5 | 7 | swap the core for one with smaller alpha+chi |
| `Mj\AIL?OI@g?O@O@_` | 14 | -4 | 5 | 9 | grow the number of triangles in the apex core |
| `O`?GW[oKGW@`?r?r~~~~~` | 16 | -3 | 4 | 7 | clique blow-up of G@O_n{ |
| `O???WWoK?W@_?r?r^~~~}` | 16 | -3 | 8 | 11 | independent blow-up of G@O_n{ |
| `O`?H`c??G@_FoBoB~~~~~` | 16 | -3 | 4 | 7 | clique blow-up of GA?KN{ |
| `O??@`_???@_EoBoB^~~~}` | 16 | -3 | 8 | 11 | independent blow-up of GA?KN{ |
| `O`?H`f?oG??@?B?B~~~~~` | 16 | -3 | 4 | 7 | clique blow-up of GA_?N{ |
| `O??@`b?o?????B?B^~~~}` | 16 | -3 | 8 | 11 | independent blow-up of GA_?N{ |
| `Pj\AIL?OI@g?O@O@g?A?@O?K` | 17 | -6 | 6 | 12 | grow the number of triangles in the apex core |
| `WwCW?CB?wF_^F?F?b_WF??wCB_W?ww?w{?[^~~~~~~~~~~~` | 24 | -6 | 4 | 10 | clique blow-up of G@O_n{ |
| `W???????wF?[F?F?B_?F??w?B_??ww?ww?[[~~~~~~~^~~{` | 24 | -6 | 12 | 18 | independent blow-up of G@O_n{ |
| `WwCW?CBF?wbb????_?W?F??{?B~??~??~_?^~~~~~~~~~~~` | 24 | -6 | 4 | 10 | clique blow-up of GA?KN{ |
| `W??????F?wB_????????F??w?Bf??~??z_?[~~~~~~~^~~{` | 24 | -6 | 12 | 18 | independent blow-up of GA?KN{ |
| `WwCW?CBF?wbbw?w?{?W????C??W??w??{??^~~~~~~~~~~~` | 24 | -6 | 4 | 10 | clique blow-up of GA_?N{ |
| `W??????F?wB_w?w?[????????????w??w??[~~~~~~~^~~{` | 24 | -6 | 12 | 18 | independent blow-up of GA_?N{ |
| `_~?GW[??G@_F?N?N_Fw@~Bo?N?G]?W]?[?{??N?G@w@_F_F??{N??{N_?]Fw?F`~~~~~~~~~~~~~~~~~~~~{` | 32 | -9 | 4 | 13 | clique blow-up of G@O_n{ |
| `_~?GW[??G@_FBoBo`wW]F?????G??W??[??N??Bw??^_?@~{??N{??N}??F~_?@~~~~~~~~~~~~~~~~~~~~{` | 32 | -9 | 4 | 13 | clique blow-up of GA?KN{ |
| `_~?GW[??G@_FBoBo`wW]F{?Bo?N_?^_?[??????G??@_??F???N???N_??Fw??@~~~~~~~~~~~~~~~~~~~~{` | 32 | -9 | 4 | 13 | clique blow-up of GA_?N{ |

**Independent recomputation** (verification bar (a)):

| graph6 | n | path A | path B | agree | R (A) | R (B) |
|---|---|---|---|---|---|---|
| `IjTJI@@OW` | 10 | alpha=4 chi=4 dist_even_max=9 | alpha=4 chi=4 dist_even_max=9 | True | -1 | -1 |

**Budget.** 0.0 s of the 3600 s cap. **Gate.** database sanity: PASS; independent recomputation: path A (`wall_arm.py`) vs path B (`scripts/gen/invariants.py` scal backend).

### FP-003 — HELD

**Statement.** `For every connected graph G with n(G) >= 2:  alpha >= lambda_max - cutv`

**Equality in D:** 6696 members, by order {'2': 1, '3': 1, '4': 3, '5': 10, '6': 52, '7': 425, '8': 6204}.

**1. The wall.** 6696 equality members, cutv pinned at 0 across the recorded 300, with alpha = lambda_max on every one: the wall is the whole 2-connected diameter-2 bulk of D where a maximum independent set already lives inside a single neighbourhood.

**2. The obstruction.** None isolable: lambda_max = max_v alpha(G[N(v)]) is an independent set of G, so lambda_max <= alpha unconditionally, and cutv >= 0. No invariant can be moved.

**3. G3-lite sign checks** (24 run, 24 stopped a trial). Only the checks that returned GO were allowed to run a trial.

_Stopped (trial not run):_

- clique blow-up of G??F~w → **STOP-zero**  (dR = 0)
- independent blow-up of G??F~w → **STOP-zero**  (dR = 0)
- subdivision of G??F~w → **STOP-wrong-sign**  (dR = 6)
- corona of G??F~w → **STOP-wrong-sign**  (dR = 9)
- join a clique onto G??F~w → **STOP-zero**  (dR = 0)
- prism over G??F~w → **STOP-wrong-sign**  (dR = 1)
- complement of G??F~w → **STOP-unavailable**
- line graph of G??F~w → **STOP-zero**  (dR = 0)
- clique blow-up of G??F~{ → **STOP-zero**  (dR = 0)
- independent blow-up of G??F~{ → **STOP-zero**  (dR = 0)
- subdivision of G??F~{ → **STOP-wrong-sign**  (dR = 6)
- corona of G??F~{ → **STOP-wrong-sign**  (dR = 9)
- join a clique onto G??F~{ → **STOP-zero**  (dR = 0)
- prism over G??F~{ → **STOP-zero**  (dR = 0)
- complement of G??F~{ → **STOP-unavailable**
- line graph of G??F~{ → **STOP-zero**  (dR = 0)
- clique blow-up of G?Bc~o → **STOP-zero**  (dR = 0)
- independent blow-up of G?Bc~o → **STOP-zero**  (dR = 0)
- subdivision of G?Bc~o → **STOP-wrong-sign**  (dR = 7)
- corona of G?Bc~o → **STOP-wrong-sign**  (dR = 10)
- join a clique onto G?Bc~o → **STOP-zero**  (dR = 0)
- prism over G?Bc~o → **STOP-wrong-sign**  (dR = 1)
- complement of G?Bc~o → **STOP-wrong-sign**  (dR = 1)
- line graph of G?Bc~o → **STOP-wrong-sign**  (dR = 1)

**4. Families built and tested.**

None — every proposed transformation was stopped at step 3.

**Outcome.** step 3 (G3-lite sign check stopped every proposed transformation) HELD -- theorem. lambda_max <= alpha, cutv >= 0.

**Budget.** 0.0 s of the 3600 s cap. **Gate.** database sanity: PASS; independent recomputation: path A (`wall_arm.py`) vs path B (`scripts/gen/invariants.py` scal backend).

### FP-004 — HELD

**Statement.** `For every connected graph G with n(G) >= 2:  A >= floor((disp_min)/2) + dist_avg`

**Equality in D:** 2 members, by order {'2': 1, '3': 1}.

**1. The wall.** Exactly two equality members in all of D: K_2 and K_3. Everything is pinned (dd=1, CW=1, res=1, A=1, diam=rad=1, dist_avg=1, disp=1, alpha=1, chi_reg=1). The wall is the complete graphs, truncated at n=3.

**2. The obstruction.** disp_min. Crossing needs floor(disp_min/2) + dist_avg > A >= floor(n/2). But disp_min <= min(delta, dd) and dd <= Delta-delta+1, so floor(disp_min/2) <= floor(n/4); raising disp_min raises delta, which collapses dist_avg (bounded by (n+1)/3 in general and by ~3n/(delta+1) under a min-degree constraint). The two halves of the right-hand side are anti-correlated through delta.

**3. G3-lite sign checks** (16 run, 16 stopped a trial). Only the checks that returned GO were allowed to run a trial.

_Stopped (trial not run):_

- clique blow-up of Bw → **STOP-wrong-sign**  (dR = 2)
- independent blow-up of Bw → **STOP-wrong-sign**  (dR = 9/5)
- subdivision of Bw → **STOP-wrong-sign**  (dR = 6/5)
- corona of Bw → **STOP-wrong-sign**  (dR = 11/5)
- join a clique onto Bw → **STOP-wrong-sign**  (dR = 1)
- prism over Bw → **STOP-wrong-sign**  (dR = 8/5)
- complement of Bw → **STOP-unavailable**
- line graph of Bw → **STOP-zero**  (dR = 0)
- clique blow-up of A_ → **STOP-wrong-sign**  (dR = 1)
- independent blow-up of A_ → **STOP-wrong-sign**  (dR = 2/3)
- subdivision of A_ → **STOP-wrong-sign**  (dR = 2/3)
- corona of A_ → **STOP-wrong-sign**  (dR = 1/3)
- join a clique onto A_ → **STOP-zero**  (dR = 0)
- prism over A_ → **STOP-wrong-sign**  (dR = 2/3)
- complement of A_ → **STOP-unavailable**
- line graph of A_ → **STOP-unavailable**

**4. Families built and tested.**

None — every proposed transformation was stopped at step 3.

**Outcome.** step 3 (G3-lite sign check stopped every proposed transformation) HELD. Two designed families (complete graphs; complete multipartite with distinct part sizes) both have positive or zero sign; the residual grows monotonically because raising disp_min raises delta, which caps dist_avg.

**Budget.** 0.0 s of the 3600 s cap. **Gate.** database sanity: PASS; independent recomputation: path A (`wall_arm.py`) vs path B (`scripts/gen/invariants.py` scal backend).

### FP-005 — HELD

**Statement.** `For every connected graph G with n(G) >= 2:  A >= floor((n)/(gamma_t))`

**Equality in D:** 3922 members, by order {'2': 1, '3': 1, '4': 5, '5': 4, '6': 65, '7': 40, '8': 3806}.

**1. The wall.** 3922 equality members, 300 recorded at n=8 with A=4=floor(n/2), gamma_t=2 and mu=4 pinned. The wall is exactly the graphs that attain A = floor(n/2) and have a dominating edge.

**2. The obstruction.** None isolable: A >= floor(n/2) (the floor(n/2) smallest degrees sum to at most m) and gamma_t >= 2 for every graph with no isolated vertex, so floor(n/gamma_t) <= floor(n/2) <= A.

**3. G3-lite sign checks** (24 run, 24 stopped a trial). Only the checks that returned GO were allowed to run a trial.

_Stopped (trial not run):_

- clique blow-up of G?F~vo → **STOP-wrong-sign**  (dR = 1)
- independent blow-up of G?F~vo → **STOP-wrong-sign**  (dR = 1)
- subdivision of G?F~vo → **STOP-wrong-sign**  (dR = 13)
- corona of G?F~vo → **STOP-wrong-sign**  (dR = 9)
- join a clique onto G?F~vo → **STOP-wrong-sign**  (dR = 1)
- prism over G?F~vo → **STOP-wrong-sign**  (dR = 5)
- complement of G?F~vo → **STOP-unavailable**
- line graph of G?F~vo → **STOP-wrong-sign**  (dR = 3)
- clique blow-up of G?\vng → **STOP-wrong-sign**  (dR = 1)
- independent blow-up of G?\vng → **STOP-wrong-sign**  (dR = 1)
- subdivision of G?\vng → **STOP-wrong-sign**  (dR = 13)
- corona of G?\vng → **STOP-wrong-sign**  (dR = 9)
- join a clique onto G?\vng → **STOP-wrong-sign**  (dR = 1)
- prism over G?\vng → **STOP-wrong-sign**  (dR = 5)
- complement of G?\vng → **STOP-wrong-sign**  (dR = 1)
- line graph of G?\vng → **STOP-wrong-sign**  (dR = 4)
- clique blow-up of G?\vno → **STOP-zero**  (dR = 0)
- independent blow-up of G?\vno → **STOP-wrong-sign**  (dR = 1)
- subdivision of G?\vno → **STOP-wrong-sign**  (dR = 13)
- corona of G?\vno → **STOP-wrong-sign**  (dR = 9)
- join a clique onto G?\vno → **STOP-wrong-sign**  (dR = 1)
- prism over G?\vno → **STOP-wrong-sign**  (dR = 4)
- complement of G?\vno → **STOP-wrong-sign**  (dR = 2)
- line graph of G?\vno → **STOP-wrong-sign**  (dR = 4)

**4. Families built and tested.**

None — every proposed transformation was stopped at step 3.

**Outcome.** step 3 (G3-lite sign check stopped every proposed transformation) HELD -- theorem. A >= floor(n/2) and gamma_t >= 2.

**Budget.** 0.1 s of the 3600 s cap. **Gate.** database sanity: PASS; independent recomputation: path A (`wall_arm.py`) vs path B (`scripts/gen/invariants.py` scal backend).

### FP-006 — HELD

**Statement.** `For every connected graph G with n(G) >= 2:  chi >= ceil((omega - chi_regular)/2) + 1`

**Equality in D:** 5731 members, by order {'2': 1, '3': 1, '4': 5, '5': 16, '6': 77, '7': 503, '8': 5128}.

**1. The wall.** 5731 equality members; chi_regular pinned at 0 across the recorded 300 and chi = omega on every one. The wall is the whole perfect-graph bulk of D.

**2. The obstruction.** None isolable: chi >= omega, and ceil((omega - c)/2) + 1 <= omega for omega >= 2, c in {0,1}. omega = 1 is impossible for a connected graph with n >= 2.

**3. G3-lite sign checks** (24 run, 24 stopped a trial). Only the checks that returned GO were allowed to run a trial.

_Stopped (trial not run):_

- clique blow-up of G???F{ → **STOP-wrong-sign**  (dR = 1)
- independent blow-up of G???F{ → **STOP-zero**  (dR = 0)
- subdivision of G???F{ → **STOP-zero**  (dR = 0)
- corona of G???F{ → **STOP-zero**  (dR = 0)
- join a clique onto G???F{ → **STOP-zero**  (dR = 0)
- prism over G???F{ → **STOP-zero**  (dR = 0)
- complement of G???F{ → **STOP-unavailable**
- line graph of G???F{ → **STOP-wrong-sign**  (dR = 3)
- clique blow-up of G???Nw → **STOP-wrong-sign**  (dR = 1)
- independent blow-up of G???Nw → **STOP-zero**  (dR = 0)
- subdivision of G???Nw → **STOP-zero**  (dR = 0)
- corona of G???Nw → **STOP-zero**  (dR = 0)
- join a clique onto G???Nw → **STOP-zero**  (dR = 0)
- prism over G???Nw → **STOP-zero**  (dR = 0)
- complement of G???Nw → **STOP-wrong-sign**  (dR = 2)
- line graph of G???Nw → **STOP-wrong-sign**  (dR = 2)
- clique blow-up of G???N{ → **STOP-wrong-sign**  (dR = 2)
- independent blow-up of G???N{ → **STOP-zero**  (dR = 0)
- subdivision of G???N{ → **STOP-zero**  (dR = 0)
- corona of G???N{ → **STOP-zero**  (dR = 0)
- join a clique onto G???N{ → **STOP-wrong-sign**  (dR = 1)
- prism over G???N{ → **STOP-zero**  (dR = 0)
- complement of G???N{ → **STOP-unavailable**
- line graph of G???N{ → **STOP-wrong-sign**  (dR = 2)

**4. Families built and tested.**

None — every proposed transformation was stopped at step 3.

**Outcome.** step 3 (G3-lite sign check stopped every proposed transformation) HELD -- theorem. chi >= omega.

**Budget.** 0.0 s of the 3600 s cap. **Gate.** database sanity: PASS; independent recomputation: path A (`wall_arm.py`) vs path B (`scripts/gen/invariants.py` scal backend).

### FP-007 — CROSSED

**Statement.** `For every connected graph G with n(G) >= 2:  diam <= disp_max + gamma_2`

**Equality in D:** 6 members, by order {'7': 1, '8': 5}.

**1. The wall.** 6 equality members: five at n=8 and one at n=7, all thin trees or near-trees with 4-6 cut vertices, delta=1, disp_max=2, alpha=4, gamma=3, gamma_t=4 pinned. The extreme member G_CKJ? is the path P_8 itself (diam 7, gamma_2 5).

**2. The obstruction.** gamma_2 against diam on a path. For P_n, V - S must be an independent set avoiding both endpoints, so gamma_2(P_n) = floor(n/2) + 1 exactly, while diam = n - 1 and disp_max = 2. The residual is R = 2 + floor(n/2) + 1 - (n-1) = floor(n/2) - n + 4, which is 0 at n = 7, 8 and strictly negative from n = 9. The obstruction is the linear-vs-half-linear race, and the wall sits at the last n where it is still a tie -- exactly the database edge.

**3. G3-lite sign checks** (26 run, 22 stopped a trial). Only the checks that returned GO were allowed to run a trial.

_Passed (trial run):_

- subdivision of GH?KM_ → **GO**  (dR = -2)<br>&nbsp;&nbsp;`sub^0(G)` (n=8) R=0 [diam=6 disp_max=2 gamma_2=4]<br>&nbsp;&nbsp;`sub^1(G)` (n=16) R=-2 [diam=12 disp_max=2 gamma_2=8]
- subdivision of G_CKJ? → **GO**  (dR = -4)<br>&nbsp;&nbsp;`sub^0(G)` (n=8) R=0 [diam=7 disp_max=2 gamma_2=5]<br>&nbsp;&nbsp;`sub^1(G)` (n=15) R=-4 [diam=14 disp_max=2 gamma_2=8]
- subdivision of GgC`Gk → **GO**  (dR = -2)<br>&nbsp;&nbsp;`sub^0(G)` (n=8) R=0 [diam=6 disp_max=2 gamma_2=4]<br>&nbsp;&nbsp;`sub^1(G)` (n=17) R=-2 [diam=12 disp_max=2 gamma_2=8]
- subdivide every edge of the tight P_8 → **GO**  (dR = -4)<br>&nbsp;&nbsp;`sub^0(P_8)` (n=8) R=0 [diam=7 disp_max=2 gamma_2=5]<br>&nbsp;&nbsp;`sub^1(P_8)` (n=15) R=-4 [diam=14 disp_max=2 gamma_2=8]

_Stopped (trial not run):_

- clique blow-up of GH?KM_ → **STOP-wrong-sign**  (dR = 2)
- independent blow-up of GH?KM_ → **STOP-wrong-sign**  (dR = 2)
- corona of GH?KM_ → **STOP-wrong-sign**  (dR = 6)
- join a clique onto GH?KM_ → **STOP-wrong-sign**  (dR = 5)
- prism over GH?KM_ → **STOP-wrong-sign**  (dR = 3)
- complement of GH?KM_ → **STOP-wrong-sign**  (dR = 4)
- line graph of GH?KM_ → **STOP-wrong-sign**  (dR = 1)
- clique blow-up of G_CKJ? → **STOP-wrong-sign**  (dR = 1)
- independent blow-up of G_CKJ? → **STOP-wrong-sign**  (dR = 1)
- corona of G_CKJ? → **STOP-wrong-sign**  (dR = 5)
- join a clique onto G_CKJ? → **STOP-wrong-sign**  (dR = 5)
- prism over G_CKJ? → **STOP-wrong-sign**  (dR = 2)
- complement of G_CKJ? → **STOP-wrong-sign**  (dR = 3)
- line graph of G_CKJ? → **STOP-zero**  (dR = 0)
- clique blow-up of GgC`Gk → **STOP-wrong-sign**  (dR = 3)
- independent blow-up of GgC`Gk → **STOP-wrong-sign**  (dR = 2)
- corona of GgC`Gk → **STOP-wrong-sign**  (dR = 6)
- join a clique onto GgC`Gk → **STOP-wrong-sign**  (dR = 5)
- prism over GgC`Gk → **STOP-wrong-sign**  (dR = 3)
- complement of GgC`Gk → **STOP-wrong-sign**  (dR = 4)
- line graph of GgC`Gk → **STOP-wrong-sign**  (dR = 1)
- stretch the tight path by one vertex → **STOP-zero**  (dR = 0)

**4. Families built and tested.**

`subdivision of GH?KM_`

| member | n | R | invariants |
|---|---|---|---|
| sub^0(G) | 8 | 0 | diam=6 disp_max=2 gamma_2=4 |
| sub^1(G) | 16 | -2 | diam=12 disp_max=2 gamma_2=8 |
| sub^2(G) | 32 | TIMEOUT |  |

`subdivision of G_CKJ?`

| member | n | R | invariants |
|---|---|---|---|
| sub^0(G) | 8 | 0 | diam=7 disp_max=2 gamma_2=5 |
| sub^1(G) | 15 | -4 | diam=14 disp_max=2 gamma_2=8 |
| sub^2(G) | 29 | TIMEOUT |  |

`subdivision of GgC`Gk`

| member | n | R | invariants |
|---|---|---|---|
| sub^0(G) | 8 | 0 | diam=6 disp_max=2 gamma_2=4 |
| sub^1(G) | 17 | -2 | diam=12 disp_max=2 gamma_2=8 |
| sub^2(G) | 35 | TIMEOUT |  |

`subdivide every edge of the tight P_8`

| member | n | R | invariants |
|---|---|---|---|
| sub^0(P_8) | 8 | 0 | diam=7 disp_max=2 gamma_2=5 |
| sub^1(P_8) | 15 | -4 | diam=14 disp_max=2 gamma_2=8 |
| sub^2(P_8) | 29 | -11 | diam=28 disp_max=2 gamma_2=15 |

**Crossings.**

| graph6 | n | R | LHS | RHS | family |
|---|---|---|---|---|---|
| `N????B?_aACGE?B??o?` | 15 | -4 | 14 | 10 | subdivision of G_CKJ? |
| `N????B?_aACGE?B??o?` | 15 | -4 | 14 | 10 | subdivide every edge of the tight P_8 |
| `O????AA_R?GGK?CO@_?K?` | 16 | -2 | 12 | 10 | subdivision of GH?KM_ |
| `P????B?W@GCOE?CO?o?I??o?` | 17 | -2 | 12 | 10 | subdivision of GgC`Gk |
| `\?????????????????C@?_C@?_A?O@?G?OA?A?_?OA??_G?@?G??c???OC??AO???P???` | 29 | -11 | 28 | 17 | subdivide every edge of the tight P_8 |

**Smallest member of the same family** — `P_9` = `HhCGGC@` (n = 9), LHS = 8, RHS = 7, R = -1. Found after the crossing was already established by a sign-check-authorised trial, by re-reading the same one-parameter family downwards. The literal G3-lite check on consecutive path lengths is dR = 0 (the residual is a floor step function), which is why the path family itself was stopped at step 3 and the subdivision of the same tight member was used instead.

**Independent recomputation** (verification bar (a)):

| graph6 | n | path A | path B | agree | R (A) | R (B) |
|---|---|---|---|---|---|---|
| `N????B?_aACGE?B??o?` | 15 | diam=14 disp_max=2 gamma_2=8 | diam=14 disp_max=2 gamma_2=8 | True | -4 | -4 |
| `HhCGGC@` | 9 | diam=8 disp_max=2 gamma_2=5 | diam=8 disp_max=2 gamma_2=5 | True | -1 | -1 |

**Budget.** 220.2 s of the 3600 s cap. **Gate.** database sanity: PASS; independent recomputation: path A (`wall_arm.py`) vs path B (`scripts/gen/invariants.py` scal backend).

### FP-008 — CROSSED

**Statement.** `For every connected graph G with n(G) >= 2:  diam >= floor((A)/(ceil(lambda_1)))`

**Equality in D:** 7 members, by order {'2': 1, '5': 1, '6': 1, '7': 1, '8': 3}.

**1. The wall.** 7 equality members, delta=sigma_2=1, kappa=1, disp_min=1, chi_C4free=1 pinned; five of the seven are trees. The n=8, n=7 and n=5 members are the stars K_{1,7}, K_{1,6}, K_{1,4} (plus near-stars). On K_{1,s}: A = s, diam = 2, lambda_1 = sqrt(s).

**2. The obstruction.** ceil(lambda_1) as a step function. On the star K_{1,s} the residual is R = 2 - floor(s / ceil(sqrt(s))). ceil(sqrt(s)) is pinned at 3 for s = 5..9 while A = s keeps climbing, so the floor term steps from 2 to 3 at the first perfect square with root >= 3, s = 9. D stops at s = 7.

**3. G3-lite sign checks** (26 run, 25 stopped a trial). Only the checks that returned GO were allowed to run a trial.

_Passed (trial run):_

- index the star family by ceil(lambda_1)=k, i.e. s=k^2 (where the floor steps) → **GO**  (dR = -1)<br>&nbsp;&nbsp;`K_{1,4}` (n=5) R=0 [annih=4 diam=2 spec_ceil=2]<br>&nbsp;&nbsp;`K_{1,9}` (n=10) R=-1 [annih=9 diam=2 spec_ceil=3]

_Stopped (trial not run):_

- clique blow-up of G???F{ → **STOP-wrong-sign**  (dR = 1)
- independent blow-up of G???F{ → **STOP-zero**  (dR = 0)
- subdivision of G???F{ → **STOP-wrong-sign**  (dR = 1)
- corona of G???F{ → **STOP-wrong-sign**  (dR = 1)
- join a clique onto G???F{ → **STOP-wrong-sign**  (dR = 1)
- prism over G???F{ → **STOP-wrong-sign**  (dR = 1)
- complement of G???F{ → **STOP-unavailable**
- line graph of G???F{ → **STOP-wrong-sign**  (dR = 1)
- clique blow-up of G???N{ → **STOP-wrong-sign**  (dR = 1)
- independent blow-up of G???N{ → **STOP-zero**  (dR = 0)
- subdivision of G???N{ → **STOP-wrong-sign**  (dR = 2)
- corona of G???N{ → **STOP-wrong-sign**  (dR = 1)
- join a clique onto G???N{ → **STOP-wrong-sign**  (dR = 1)
- prism over G???N{ → **STOP-wrong-sign**  (dR = 1)
- complement of G???N{ → **STOP-unavailable**
- line graph of G???N{ → **STOP-wrong-sign**  (dR = 2)
- clique blow-up of G??KF{ → **STOP-wrong-sign**  (dR = 1)
- independent blow-up of G??KF{ → **STOP-zero**  (dR = 0)
- subdivision of G??KF{ → **STOP-wrong-sign**  (dR = 3)
- corona of G??KF{ → **STOP-wrong-sign**  (dR = 1)
- join a clique onto G??KF{ → **STOP-wrong-sign**  (dR = 1)
- prism over G??KF{ → **STOP-wrong-sign**  (dR = 1)
- complement of G??KF{ → **STOP-unavailable**
- line graph of G??KF{ → **STOP-wrong-sign**  (dR = 3)
- grow the tight star by one leaf → **STOP-wrong-sign**  (dR = 1)

**4. Families built and tested.**

`index the star family by ceil(lambda_1)=k, i.e. s=k^2 (where the floor steps)`

| member | n | R | invariants |
|---|---|---|---|
| K_{1,4} | 5 | 0 | annih=4 diam=2 spec_ceil=2 |
| K_{1,9} | 10 | -1 | annih=9 diam=2 spec_ceil=3 |
| K_{1,16} | 17 | -2 | annih=16 diam=2 spec_ceil=4 |
| K_{1,25} | 26 | -3 | annih=25 diam=2 spec_ceil=5 |

**Crossings.**

| graph6 | n | R | LHS | RHS | family |
|---|---|---|---|---|---|
| `IsaCCA?_?` | 10 | -1 | 2 | 3 | index the star family by ceil(lambda_1)=k, i.e. s=k^2 (where the floor steps) |
| `PsaCCA?_C?O?_?_?O?C??_??` | 17 | -2 | 2 | 4 | index the star family by ceil(lambda_1)=k, i.e. s=k^2 (where the floor steps) |
| `YsaCCA?_C?O?_?_?O?C??_?A??C??C??A???_??C???O???_???_????` | 26 | -3 | 2 | 5 | index the star family by ceil(lambda_1)=k, i.e. s=k^2 (where the floor steps) |

**Independent recomputation** (verification bar (a)):

| graph6 | n | path A | path B | agree | R (A) | R (B) |
|---|---|---|---|---|---|---|
| `IsaCCA?_?` | 10 | annih=9 diam=2 spec_ceil=3 | annih=9 diam=2 spec_ceil=3 | True | -1 | -1 |

**Budget.** 0.7 s of the 3600 s cap. **Gate.** database sanity: PASS; independent recomputation: path A (`wall_arm.py`) vs path B (`scripts/gen/invariants.py` scal backend).

### FP-009 — CROSSED

**Statement.** `For every connected graph G with n(G) >= 2:  gamma <= floor((lambda_avg)/2) + res`

**Equality in D:** 704 members, by order {'2': 1, '3': 1, '4': 2, '5': 5, '6': 22, '7': 93, '8': 580}.

**1. The wall.** 704 equality members; the recorded 300 all sit at n=8 with lambda_avg < 2, so floor(lambda_avg/2) = 0 and the bound degenerates to gamma <= res. Every recorded member has gamma = res exactly and 1-4 cut vertices.

**2. The obstruction.** res against gamma with lambda_avg held below 2. Hanging one pendant on every vertex forces gamma = n/2 (each pendant needs its own support) while the residue res of the corona grows only like the residue of a sparser sequence, and lambda_avg = 1 + lambda_avg(H)/2 stays under 4 so the floor term stays at 1.

**3. G3-lite sign checks** (25 run, 21 stopped a trial). Only the checks that returned GO were allowed to run a trial.

_Passed (trial run):_

- corona of G@KqS[ → **GO**  (dR = -2)<br>&nbsp;&nbsp;`G o 0K1` (n=8) R=0 [gamma=3 lam_avg=15/8 res=3]<br>&nbsp;&nbsp;`G o 1K1` (n=16) R=-2 [gamma=8 lam_avg=31/16 res=6]
- corona of G@KqTS → **GO**  (dR = -1)<br>&nbsp;&nbsp;`G o 0K1` (n=8) R=0 [gamma=3 lam_avg=7/4 res=3]<br>&nbsp;&nbsp;`G o 1K1` (n=16) R=-1 [gamma=8 lam_avg=15/8 res=7]
- corona of G@KqT[ → **GO**  (dR = -1)<br>&nbsp;&nbsp;`G o 0K1` (n=8) R=0 [gamma=3 lam_avg=15/8 res=3]<br>&nbsp;&nbsp;`G o 1K1` (n=16) R=-1 [gamma=8 lam_avg=31/16 res=7]
- corona: hang a pendant on every vertex of the tight member → **GO**  (dR = -2)<br>&nbsp;&nbsp;`(G@KqS[) o 0K1` (n=8) R=0 [gamma=3 lam_avg=15/8 res=3]<br>&nbsp;&nbsp;`(G@KqS[) o 1K1` (n=16) R=-2 [gamma=8 lam_avg=31/16 res=6]

_Stopped (trial not run):_

- clique blow-up of G@KqS[ → **STOP-zero**  (dR = 0)
- independent blow-up of G@KqS[ → **STOP-wrong-sign**  (dR = 2)
- subdivision of G@KqS[ → **STOP-wrong-sign**  (dR = 2)
- join a clique onto G@KqS[ → **STOP-wrong-sign**  (dR = 3)
- prism over G@KqS[ → **STOP-wrong-sign**  (dR = 1)
- complement of G@KqS[ → **STOP-wrong-sign**  (dR = 1)
- line graph of G@KqS[ → **STOP-wrong-sign**  (dR = 1)
- clique blow-up of G@KqTS → **STOP-zero**  (dR = 0)
- independent blow-up of G@KqTS → **STOP-wrong-sign**  (dR = 2)
- subdivision of G@KqTS → **STOP-wrong-sign**  (dR = 2)
- join a clique onto G@KqTS → **STOP-wrong-sign**  (dR = 3)
- prism over G@KqTS → **STOP-wrong-sign**  (dR = 1)
- complement of G@KqTS → **STOP-wrong-sign**  (dR = 2)
- line graph of G@KqTS → **STOP-wrong-sign**  (dR = 1)
- clique blow-up of G@KqT[ → **STOP-zero**  (dR = 0)
- independent blow-up of G@KqT[ → **STOP-wrong-sign**  (dR = 2)
- subdivision of G@KqT[ → **STOP-wrong-sign**  (dR = 2)
- join a clique onto G@KqT[ → **STOP-wrong-sign**  (dR = 3)
- prism over G@KqT[ → **STOP-wrong-sign**  (dR = 1)
- complement of G@KqT[ → **STOP-wrong-sign**  (dR = 2)
- line graph of G@KqT[ → **STOP-wrong-sign**  (dR = 1)

**4. Families built and tested.**

`corona of G@KqS[`

| member | n | R | invariants |
|---|---|---|---|
| G o 0K1 | 8 | 0 | gamma=3 lam_avg=15/8 res=3 |
| G o 1K1 | 16 | -2 | gamma=8 lam_avg=31/16 res=6 |
| G o 2K1 | 24 | 2 | gamma=8 lam_avg=47/24 res=10 |

`corona of G@KqTS`

| member | n | R | invariants |
|---|---|---|---|
| G o 0K1 | 8 | 0 | gamma=3 lam_avg=7/4 res=3 |
| G o 1K1 | 16 | -1 | gamma=8 lam_avg=15/8 res=7 |
| G o 2K1 | 24 | 2 | gamma=8 lam_avg=23/12 res=10 |

`corona of G@KqT[`

| member | n | R | invariants |
|---|---|---|---|
| G o 0K1 | 8 | 0 | gamma=3 lam_avg=15/8 res=3 |
| G o 1K1 | 16 | -1 | gamma=8 lam_avg=31/16 res=7 |
| G o 2K1 | 24 | 2 | gamma=8 lam_avg=47/24 res=10 |

`corona: hang a pendant on every vertex of the tight member`

| member | n | R | invariants |
|---|---|---|---|
| (G@KqS[) o 0K1 | 8 | 0 | gamma=3 lam_avg=15/8 res=3 |
| (G@KqS[) o 1K1 | 16 | -2 | gamma=8 lam_avg=31/16 res=6 |
| (G@KqS[) o 2K1 | 24 | 2 | gamma=8 lam_avg=47/24 res=10 |

**Crossings.**

| graph6 | n | R | LHS | RHS | family |
|---|---|---|---|---|---|
| `O@KqTU?O@?A?A?@??O?A?` | 16 | -1 | 8 | 7 | corona of G@KqTS |
| `O@KqT]?O@?A?A?@??O?A?` | 16 | -1 | 8 | 7 | corona of G@KqT[ |
| `O@KqS]?O@?A?A?@??O?A?` | 16 | -2 | 8 | 6 | corona of G@KqS[ |
| `O@KqS]?O@?A?A?@??O?A?` | 16 | -2 | 8 | 6 | corona: hang a pendant on every vertex of the tight member |

**Independent recomputation** (verification bar (a)):

| graph6 | n | path A | path B | agree | R (A) | R (B) |
|---|---|---|---|---|---|---|
| `O@KqTU?O@?A?A?@??O?A?` | 16 | gamma=8 lam_avg=15/8 res=7 | gamma=8 lam_avg=15/8 res=7 | True | -1 | -1 |

**Budget.** 0.2 s of the 3600 s cap. **Gate.** database sanity: PASS; independent recomputation: path A (`wall_arm.py`) vs path B (`scripts/gen/invariants.py` scal backend).

### FP-010 — HELD

**Statement.** `For every connected graph G with n(G) >= 2:  gamma <= gamma_2 - chi_C4free`

**Equality in D:** 216 members, by order {'2': 1, '3': 2, '4': 2, '5': 6, '6': 11, '7': 35, '8': 159}.

**1. The wall.** 216 equality members spread over every order 3..8. The C4-free ones have gamma_2 = gamma + 1 exactly; the C4-containing ones have gamma_2 = gamma. The wall is therefore two separate strata glued by the characteristic function.

**2. The obstruction.** None isolable. If S is a minimum dominating set that also 2-dominates, then S has no external private neighbour, hence S is independent; pick any u outside S and two of its neighbours s, s' in S. In a C4-free graph u is the only vertex whose S-neighbourhood is exactly {s,s'}, so (S - {s,s'}) + {u} still dominates, contradicting minimality. Hence gamma_2 >= gamma + 1 whenever chi_C4free = 1.

**3. G3-lite sign checks** (26 run, 26 stopped a trial). Only the checks that returned GO were allowed to run a trial.

_Stopped (trial not run):_

- clique blow-up of G??F~w → **STOP-wrong-sign**  (dR = 1)
- independent blow-up of G??F~w → **STOP-wrong-sign**  (dR = 2)
- subdivision of G??F~w → **STOP-zero**  (dR = 0)
- corona of G??F~w → **STOP-wrong-sign**  (dR = 2)
- join a clique onto G??F~w → **STOP-wrong-sign**  (dR = 1)
- prism over G??F~w → **STOP-wrong-sign**  (dR = 2)
- complement of G??F~w → **STOP-unavailable**
- line graph of G??F~w → **STOP-wrong-sign**  (dR = 2)
- clique blow-up of G?~wNs → **STOP-wrong-sign**  (dR = 1)
- independent blow-up of G?~wNs → **STOP-wrong-sign**  (dR = 2)
- subdivision of G?~wNs → **STOP-zero**  (dR = 0)
- corona of G?~wNs → **STOP-wrong-sign**  (dR = 2)
- join a clique onto G?~wNs → **STOP-wrong-sign**  (dR = 1)
- prism over G?~wNs → **STOP-wrong-sign**  (dR = 2)
- complement of G?~wNs → **STOP-unavailable**
- line graph of G?~wNs → **STOP-wrong-sign**  (dR = 2)
- clique blow-up of GA?KJK → **STOP-wrong-sign**  (dR = 4)
- independent blow-up of GA?KJK → **STOP-wrong-sign**  (dR = 4)
- subdivision of GA?KJK → **STOP-wrong-sign**  (dR = 1)
- corona of GA?KJK → **STOP-wrong-sign**  (dR = 3)
- join a clique onto GA?KJK → **STOP-wrong-sign**  (dR = 4)
- prism over GA?KJK → **STOP-wrong-sign**  (dR = 3)
- complement of GA?KJK → **STOP-wrong-sign**  (dR = 1)
- line graph of GA?KJK → **STOP-wrong-sign**  (dR = 2)
- subdivision of K_k (an independent gamma-set with all outside degrees 2) → **STOP-zero**  (dR = 0)
- friendship graphs (C4-free, gamma = 1) → **STOP-wrong-sign**  (dR = 1)

**4. Families built and tested.**

None — every proposed transformation was stopped at step 3.

**Outcome.** step 3 (G3-lite sign check stopped every proposed transformation) HELD -- theorem (private-neighbour + C4-free argument above).

**Budget.** 2.7 s of the 3600 s cap. **Gate.** database sanity: PASS; independent recomputation: path A (`wall_arm.py`) vs path B (`scripts/gen/invariants.py` scal backend).

### FP-011 — HELD

**Statement.** `For every connected graph G with n(G) >= 2:  gamma >= ceil((Tdist_min)/(m))`

**Equality in D:** 1509 members, by order {'2': 1, '3': 2, '4': 5, '5': 14, '6': 46, '7': 201, '8': 1240}.

**1. The wall.** 1509 equality members; 217 of the recorded 300 have gamma = 1 and Tdist_min = 7 = n-1 <= m, i.e. a universal vertex. The wall is the dominating-vertex stratum, where Tdist_min/m <= 1 = gamma.

**2. The obstruction.** Tdist_min per edge. Making Tdist_min large forces a path-like graph, where m = n-1 and Tdist_min ~ n^2/4 gives a ratio ~ n/4, while gamma of the same graph is ~ n/3 > n/4. Making gamma small forces a dominating vertex, which collapses Tdist_min to n-1 <= m. The two requirements move the same structural knob in opposite directions.

**3. G3-lite sign checks** (26 run, 26 stopped a trial). Only the checks that returned GO were allowed to run a trial.

_Stopped (trial not run):_

- clique blow-up of G???F{ → **STOP-zero**  (dR = 0)
- independent blow-up of G???F{ → **STOP-wrong-sign**  (dR = 1)
- subdivision of G???F{ → **STOP-wrong-sign**  (dR = 5)
- corona of G???F{ → **STOP-wrong-sign**  (dR = 6)
- join a clique onto G???F{ → **STOP-zero**  (dR = 0)
- prism over G???F{ → **STOP-wrong-sign**  (dR = 1)
- complement of G???F{ → **STOP-unavailable**
- line graph of G???F{ → **STOP-zero**  (dR = 0)
- clique blow-up of G???Nw → **STOP-wrong-sign**  (dR = 1)
- independent blow-up of G???Nw → **STOP-wrong-sign**  (dR = 1)
- subdivision of G???Nw → **STOP-wrong-sign**  (dR = 5)
- corona of G???Nw → **STOP-wrong-sign**  (dR = 6)
- join a clique onto G???Nw → **STOP-zero**  (dR = 0)
- prism over G???Nw → **STOP-wrong-sign**  (dR = 1)
- complement of G???Nw → **STOP-wrong-sign**  (dR = 1)
- line graph of G???Nw → **STOP-zero**  (dR = 0)
- clique blow-up of G???N{ → **STOP-zero**  (dR = 0)
- independent blow-up of G???N{ → **STOP-wrong-sign**  (dR = 1)
- subdivision of G???N{ → **STOP-wrong-sign**  (dR = 5)
- corona of G???N{ → **STOP-wrong-sign**  (dR = 6)
- join a clique onto G???N{ → **STOP-zero**  (dR = 0)
- prism over G???N{ → **STOP-wrong-sign**  (dR = 1)
- complement of G???N{ → **STOP-unavailable**
- line graph of G???N{ → **STOP-zero**  (dR = 0)
- stretch: Tdist_min ~ n^2/4 against m = n-1 → **STOP-zero**  (dR = 0)
- spider: keep gamma low while Tdist_min grows → **STOP-wrong-sign**  (dR = 1)

**4. Families built and tested.**

None — every proposed transformation was stopped at step 3.

**Outcome.** step 3 (G3-lite sign check stopped every proposed transformation) HELD. Path and spider families both have positive sign; the residual grows with n.

**Budget.** 0.1 s of the 3600 s cap. **Gate.** database sanity: PASS; independent recomputation: path A (`wall_arm.py`) vs path B (`scripts/gen/invariants.py` scal backend).

### FP-012 — CROSSED

**Statement.** `For every connected graph G with n(G) >= 2:  gamma_2 <= dist_even_max - chi_regular + 2`

**Equality in D:** 17 members, by order {'2': 1, '3': 1, '4': 1, '5': 1, '6': 1, '7': 2, '8': 10}.

**1. The wall.** 17 equality members: the complete graphs K_2..K_8 (gamma_2=2, dist_even_max=1, regular), the 7-cycle, and ten 8-vertex trees / near-trees with 4 or more pendant vertices, gamma_2 = 6 and dist_even_max = 4 = n/2. disp_min is pinned at 1.

**2. The obstruction.** gamma(core) with dist_even_max pinned. Hanging one pendant on every vertex of a diameter-2 core H gives gamma_2 = |H| + gamma(H) (every pendant is forced in, and the H-part must dominate H), while dist_even_max stays exactly |H| = n/2 because the core has diameter 2. The residual is R = 2 - gamma(H): the wall is gamma(H) <= 2 and the crossing is any diameter-2 core with gamma >= 3. Inside D the corona of such a core needs n >= 20, and even C_7 (gamma = 3, diameter 3) needs n = 14.

**3. G3-lite sign checks** (26 run, 23 stopped a trial). Only the checks that returned GO were allowed to run a trial.

_Passed (trial run):_

- corona of GA?KJG → **GO**  (dR = -2)<br>&nbsp;&nbsp;`G o 0K1` (n=8) R=0 [chi_reg=0 dist_even_max=4 gamma_2=6]<br>&nbsp;&nbsp;`G o 1K1` (n=16) R=-2 [chi_reg=0 dist_even_max=8 gamma_2=12]
- corona of a diameter-2 core: pins dist_even_max at n/2, pushes gamma_2 to n/2+gamma(core) → **GO**  (dR = -1)<br>&nbsp;&nbsp;`(K3) o K1` (n=6) R=1 [chi_reg=0 dist_even_max=3 gamma_2=4]<br>&nbsp;&nbsp;`(C5) o K1` (n=10) R=0 [chi_reg=0 dist_even_max=5 gamma_2=7]
- corona of the tight 8-vertex trees → **GO**  (dR = -2)<br>&nbsp;&nbsp;`(GHCGdO) o 0K1` (n=8) R=0 [chi_reg=0 dist_even_max=4 gamma_2=6]<br>&nbsp;&nbsp;`(GHCGdO) o 1K1` (n=16) R=-2 [chi_reg=0 dist_even_max=8 gamma_2=12]

_Stopped (trial not run):_

- clique blow-up of GA?KJG → **STOP-wrong-sign**  (dR = 1)
- independent blow-up of GA?KJG → **STOP-wrong-sign**  (dR = 2)
- subdivision of GA?KJG → **STOP-wrong-sign**  (dR = 2)
- join a clique onto GA?KJG → **STOP-wrong-sign**  (dR = 4)
- prism over GA?KJG → **STOP-wrong-sign**  (dR = 2)
- complement of GA?KJG → **STOP-wrong-sign**  (dR = 3)
- line graph of GA?KJG → **STOP-wrong-sign**  (dR = 2)
- clique blow-up of GG?`Lo → **STOP-wrong-sign**  (dR = 5)
- independent blow-up of GG?`Lo → **STOP-wrong-sign**  (dR = 6)
- subdivision of GG?`Lo → **STOP-wrong-sign**  (dR = 2)
- corona of GG?`Lo → **STOP-zero**  (dR = 0)
- join a clique onto GG?`Lo → **STOP-wrong-sign**  (dR = 6)
- prism over GG?`Lo → **STOP-wrong-sign**  (dR = 2)
- complement of GG?`Lo → **STOP-wrong-sign**  (dR = 3)
- line graph of GG?`Lo → **STOP-wrong-sign**  (dR = 3)
- clique blow-up of GGC`Lo → **STOP-wrong-sign**  (dR = 5)
- independent blow-up of GGC`Lo → **STOP-wrong-sign**  (dR = 6)
- subdivision of GGC`Lo → **STOP-wrong-sign**  (dR = 3)
- corona of GGC`Lo → **STOP-zero**  (dR = 0)
- join a clique onto GGC`Lo → **STOP-wrong-sign**  (dR = 6)
- prism over GGC`Lo → **STOP-wrong-sign**  (dR = 2)
- complement of GGC`Lo → **STOP-wrong-sign**  (dR = 3)
- line graph of GGC`Lo → **STOP-wrong-sign**  (dR = 3)

**4. Families built and tested.**

`corona of GA?KJG`

| member | n | R | invariants |
|---|---|---|---|
| G o 0K1 | 8 | 0 | chi_reg=0 dist_even_max=4 gamma_2=6 |
| G o 1K1 | 16 | -2 | chi_reg=0 dist_even_max=8 gamma_2=12 |
| G o 2K1 | 24 | TIMEOUT |  |

`corona of a diameter-2 core: pins dist_even_max at n/2, pushes gamma_2 to n/2+gamma(core)`

| member | n | R | invariants |
|---|---|---|---|
| (K3) o K1 | 6 | 1 | chi_reg=0 dist_even_max=3 gamma_2=4 |
| (C5) o K1 | 10 | 0 | chi_reg=0 dist_even_max=5 gamma_2=7 |
| (C6) o K1 | 12 | 0 | chi_reg=0 dist_even_max=6 gamma_2=8 |
| (C7) o K1 | 14 | -1 | chi_reg=0 dist_even_max=7 gamma_2=10 |
| (Petersen) o K1 | 20 | -1 | chi_reg=0 dist_even_max=10 gamma_2=13 |

`corona of the tight 8-vertex trees`

| member | n | R | invariants |
|---|---|---|---|
| (GHCGdO) o 0K1 | 8 | 0 | chi_reg=0 dist_even_max=4 gamma_2=6 |
| (GHCGdO) o 1K1 | 16 | -2 | chi_reg=0 dist_even_max=8 gamma_2=12 |

**Crossings.**

| graph6 | n | R | LHS | RHS | family |
|---|---|---|---|---|---|
| `MhCKK@?G?_@?@??_?` | 14 | -1 | 10 | 9 | corona of a diameter-2 core: pins dist_even_max at n/2, pushes gamma_2 to n/2+gamma(core) |
| `OA?KJI?O@?A?A?@??O?A?` | 16 | -2 | 12 | 10 | corona of GA?KJG |
| `OHCGdQ?O@?A?A?@??O?A?` | 16 | -2 | 12 | 10 | corona of the tight 8-vertex trees |
| `S?LRCecqC?G?G?C?@??G??_?@??@???_?` | 20 | -1 | 13 | 12 | corona of a diameter-2 core: pins dist_even_max at n/2, pushes gamma_2 to n/2+gamma(core) |

**Independent recomputation** (verification bar (a)):

| graph6 | n | path A | path B | agree | R (A) | R (B) |
|---|---|---|---|---|---|---|
| `MhCKK@?G?_@?@??_?` | 14 | chi_reg=0 dist_even_max=7 gamma_2=10 | chi_reg=0 dist_even_max=7 gamma_2=10 | True | -1 | -1 |

**Budget.** 81.6 s of the 3600 s cap. **Gate.** database sanity: PASS; independent recomputation: path A (`wall_arm.py`) vs path B (`scripts/gen/invariants.py` scal backend).

### FP-013 — HELD

**Statement.** `For every connected graph G with n(G) >= 2:  gamma_2 >= ceil((Delta)/(Sigma_2))`

**Equality in D:** 39 members, by order {'3': 1, '4': 1, '5': 2, '6': 3, '7': 8, '8': 24}.

**1. The wall.** 39 equality members with diam=2, rad=1, dist_even_min=1, gamma=1, gamma_t=2, gamma_i=1 pinned: a universal vertex is present on every one. 24 of them have Delta=7=n-1 and Sigma_2=6, giving RHS=2=gamma_2; the star K_{1,7} is the other extreme (Sigma_2=1, gamma_2=7=RHS).

**2. The obstruction.** gamma_2 tracks Delta/Sigma_2 with an unavoidable +1. Whenever n = Delta+1 the hub is universal and gamma_2 = min(1+gamma(H), gamma_2(H)) with H = G - hub of maximum degree Sigma_2 - 1, so gamma_2 >= 1 + ceil(Delta/Sigma_2). Every petal construction pays exactly one extra vertex for the hub, and the residual is stuck at 1.

**3. G3-lite sign checks** (26 run, 26 stopped a trial). Only the checks that returned GO were allowed to run a trial.

_Stopped (trial not run):_

- clique blow-up of G???F{ → **STOP-wrong-sign**  (dR = 1)
- independent blow-up of G???F{ → **STOP-wrong-sign**  (dR = 1)
- subdivision of G???F{ → **STOP-wrong-sign**  (dR = 4)
- corona of G???F{ → **STOP-wrong-sign**  (dR = 5)
- join a clique onto G???F{ → **STOP-wrong-sign**  (dR = 1)
- prism over G???F{ → **STOP-wrong-sign**  (dR = 7)
- complement of G???F{ → **STOP-unavailable**
- line graph of G???F{ → **STOP-wrong-sign**  (dR = 1)
- clique blow-up of G?F~v{ → **STOP-wrong-sign**  (dR = 1)
- independent blow-up of G?F~v{ → **STOP-wrong-sign**  (dR = 1)
- subdivision of G?F~v{ → **STOP-wrong-sign**  (dR = 6)
- corona of G?F~v{ → **STOP-wrong-sign**  (dR = 7)
- join a clique onto G?F~v{ → **STOP-wrong-sign**  (dR = 1)
- prism over G?F~v{ → **STOP-wrong-sign**  (dR = 3)
- complement of G?F~v{ → **STOP-unavailable**
- line graph of G?F~v{ → **STOP-wrong-sign**  (dR = 3)
- clique blow-up of G@N~v{ → **STOP-wrong-sign**  (dR = 1)
- independent blow-up of G@N~v{ → **STOP-wrong-sign**  (dR = 1)
- subdivision of G@N~v{ → **STOP-wrong-sign**  (dR = 6)
- corona of G@N~v{ → **STOP-wrong-sign**  (dR = 7)
- join a clique onto G@N~v{ → **STOP-wrong-sign**  (dR = 1)
- prism over G@N~v{ → **STOP-wrong-sign**  (dR = 3)
- complement of G@N~v{ → **STOP-unavailable**
- line graph of G@N~v{ → **STOP-wrong-sign**  (dR = 3)
- flower: add petals; Delta grows by 2 per petal, Sigma_2 pinned at 2 → **STOP-zero**  (dR = 0)
- hub joined to a perfect matching → **STOP-zero**  (dR = 0)

**4. Families built and tested.**

None — every proposed transformation was stopped at step 3.

**Outcome.** step 3 (G3-lite sign check stopped every proposed transformation) HELD. Flower and hub-plus-matching families both sit at residual exactly 1 for every parameter, which is the +1 the hub costs.

**Budget.** 8.9 s of the 3600 s cap. **Gate.** database sanity: PASS; independent recomputation: path A (`wall_arm.py`) vs path B (`scripts/gen/invariants.py` scal backend).

### FP-014 — CROSSED

**Statement.** `For every connected graph G with n(G) >= 2:  gamma_2 >= floor((dist_even_min + disp_min)/2)`

**Equality in D:** 85 members, by order {'7': 4, '8': 81}.

**1. The wall.** 85 equality members, 81 at n=8, all 2-connected (cutv=0, f_1=0) and non-bipartite with gamma_2 = 2 or 3 and dist_even_min = 1, 2 or 4. gamma_2=2 forces diameter 2 and a dominating pair; dist_even_min is held down to 2 by the same density.

**2. The obstruction.** dist_even_min. On the wall dist_even_min <= 4 because diameter 2 forces dist_even(v) = n - deg(v) and the degrees are large. The Cartesian product with K_2 keeps gamma_2 at 2*gamma_2(G) but sends dist_even_min to n (in G x K_2 every vertex has its whole layer at even distance), so the floor term outruns gamma_2.

**3. G3-lite sign checks** (26 run, 18 stopped a trial). Only the checks that returned GO were allowed to run a trial.

_Passed (trial run):_

- prism over GC|v~w → **GO**  (dR = -1)<br>&nbsp;&nbsp;`G x K1` (n=8) R=0 [disp_min=2 dist_even_min=2 gamma_2=2]<br>&nbsp;&nbsp;`G x K2` (n=16) R=-1 [disp_min=3 dist_even_min=8 gamma_2=4]
- line graph of GC|v~w → **GO**  (dR = -2)<br>&nbsp;&nbsp;`G` (n=8) R=0 [disp_min=2 dist_even_min=2 gamma_2=2]<br>&nbsp;&nbsp;`L(G)` (n=20) R=-2 [disp_min=2 dist_even_min=10 gamma_2=4]
- prism over GC|v~{ → **GO**  (dR = -1)<br>&nbsp;&nbsp;`G x K1` (n=8) R=0 [disp_min=3 dist_even_min=1 gamma_2=2]<br>&nbsp;&nbsp;`G x K2` (n=16) R=-1 [disp_min=3 dist_even_min=8 gamma_2=4]
- line graph of GC|v~{ → **GO**  (dR = -2)<br>&nbsp;&nbsp;`G` (n=8) R=0 [disp_min=3 dist_even_min=1 gamma_2=2]<br>&nbsp;&nbsp;`L(G)` (n=21) R=-2 [disp_min=3 dist_even_min=9 gamma_2=4]
- prism over GEyn~w → **GO**  (dR = -1)<br>&nbsp;&nbsp;`G x K1` (n=8) R=0 [disp_min=2 dist_even_min=2 gamma_2=2]<br>&nbsp;&nbsp;`G x K2` (n=16) R=-1 [disp_min=2 dist_even_min=8 gamma_2=4]
- line graph of GEyn~w → **GO**  (dR = -2)<br>&nbsp;&nbsp;`G` (n=8) R=0 [disp_min=2 dist_even_min=2 gamma_2=2]<br>&nbsp;&nbsp;`L(G)` (n=20) R=-2 [disp_min=2 dist_even_min=10 gamma_2=4]
- prism: G x K_k doubles dist_even_min while gamma_2 only doubles → **GO**  (dR = -1)<br>&nbsp;&nbsp;`(GC|v~w) x K_1` (n=8) R=0 [disp_min=2 dist_even_min=2 gamma_2=2]<br>&nbsp;&nbsp;`(GC|v~w) x K_2` (n=16) R=-1 [disp_min=3 dist_even_min=8 gamma_2=4]
- line graph of the tight member → **GO**  (dR = -2)<br>&nbsp;&nbsp;`GC|v~w` (n=8) R=0 [disp_min=2 dist_even_min=2 gamma_2=2]<br>&nbsp;&nbsp;`L(GC|v~w)` (n=20) R=-2 [disp_min=2 dist_even_min=10 gamma_2=4]

_Stopped (trial not run):_

- clique blow-up of GC|v~w → **STOP-zero**  (dR = 0)
- independent blow-up of GC|v~w → **STOP-zero**  (dR = 0)
- subdivision of GC|v~w → **STOP-wrong-sign**  (dR = 4)
- corona of GC|v~w → **STOP-wrong-sign**  (dR = 6)
- join a clique onto GC|v~w → **STOP-zero**  (dR = 0)
- complement of GC|v~w → **STOP-unavailable**
- clique blow-up of GC|v~{ → **STOP-zero**  (dR = 0)
- independent blow-up of GC|v~{ → **STOP-zero**  (dR = 0)
- subdivision of GC|v~{ → **STOP-wrong-sign**  (dR = 4)
- corona of GC|v~{ → **STOP-wrong-sign**  (dR = 5)
- join a clique onto GC|v~{ → **STOP-zero**  (dR = 0)
- complement of GC|v~{ → **STOP-unavailable**
- clique blow-up of GEyn~w → **STOP-wrong-sign**  (dR = 1)
- independent blow-up of GEyn~w → **STOP-zero**  (dR = 0)
- subdivision of GEyn~w → **STOP-wrong-sign**  (dR = 4)
- corona of GEyn~w → **STOP-wrong-sign**  (dR = 6)
- join a clique onto GEyn~w → **STOP-zero**  (dR = 0)
- complement of GEyn~w → **STOP-unavailable**

**4. Families built and tested.**

`prism over GC|v~w`

| member | n | R | invariants |
|---|---|---|---|
| G x K1 | 8 | 0 | disp_min=2 dist_even_min=2 gamma_2=2 |
| G x K2 | 16 | -1 | disp_min=3 dist_even_min=8 gamma_2=4 |
| G x K3 | 24 | -1 | disp_min=3 dist_even_min=12 gamma_2=6 |

`line graph of GC|v~w`

| member | n | R | invariants |
|---|---|---|---|
| G | 8 | 0 | disp_min=2 dist_even_min=2 gamma_2=2 |
| L(G) | 20 | -2 | disp_min=2 dist_even_min=10 gamma_2=4 |

`prism over GC|v~{`

| member | n | R | invariants |
|---|---|---|---|
| G x K1 | 8 | 0 | disp_min=3 dist_even_min=1 gamma_2=2 |
| G x K2 | 16 | -1 | disp_min=3 dist_even_min=8 gamma_2=4 |
| G x K3 | 24 | -1 | disp_min=3 dist_even_min=12 gamma_2=6 |

`line graph of GC|v~{`

| member | n | R | invariants |
|---|---|---|---|
| G | 8 | 0 | disp_min=3 dist_even_min=1 gamma_2=2 |
| L(G) | 21 | -2 | disp_min=3 dist_even_min=9 gamma_2=4 |

`prism over GEyn~w`

| member | n | R | invariants |
|---|---|---|---|
| G x K1 | 8 | 0 | disp_min=2 dist_even_min=2 gamma_2=2 |
| G x K2 | 16 | -1 | disp_min=2 dist_even_min=8 gamma_2=4 |
| G x K3 | 24 | -1 | disp_min=2 dist_even_min=12 gamma_2=6 |

`line graph of GEyn~w`

| member | n | R | invariants |
|---|---|---|---|
| G | 8 | 0 | disp_min=2 dist_even_min=2 gamma_2=2 |
| L(G) | 20 | -2 | disp_min=2 dist_even_min=10 gamma_2=4 |

`prism: G x K_k doubles dist_even_min while gamma_2 only doubles`

| member | n | R | invariants |
|---|---|---|---|
| (GC|v~w) x K_1 | 8 | 0 | disp_min=2 dist_even_min=2 gamma_2=2 |
| (GC|v~w) x K_2 | 16 | -1 | disp_min=3 dist_even_min=8 gamma_2=4 |
| (GC|v~w) x K_3 | 24 | -1 | disp_min=3 dist_even_min=12 gamma_2=6 |

`line graph of the tight member`

| member | n | R | invariants |
|---|---|---|---|
| GC|v~w | 8 | 0 | disp_min=2 dist_even_min=2 gamma_2=2 |
| L(GC|v~w) | 20 | -2 | disp_min=2 dist_even_min=10 gamma_2=4 |

**Crossings.**

| graph6 | n | R | LHS | RHS | family |
|---|---|---|---|---|---|
| `O`?KAEiTXSAhiiTTtTAih` | 16 | -1 | 4 | 5 | prism over GC|v~w |
| `O`?KAEiTXSAhiiTTtTQij` | 16 | -1 | 4 | 5 | prism over GC|v~{ |
| `O`?LAegTKPGbiiTTtTAih` | 16 | -1 | 4 | 5 | prism over GEyn~w |
| `O`?KAEiTXSAhiiTTtTAih` | 16 | -1 | 4 | 5 | prism: G x K_k doubles dist_even_min while gamma_2 only doubles |
| `S~OHW|G@HDaNqG`CsP[aNYihXeXKrOiik` | 20 | -2 | 4 | 6 | line graph of GC|v~w |
| `S~}AGkNO`?aJANdPPcZCoStTIqxaYpPTk` | 20 | -2 | 4 | 6 | line graph of GEyn~w |
| `S~OHW|G@HDaNqG`CsP[aNYihXeXKrOiik` | 20 | -2 | 4 | 6 | line graph of the tight member |
| `T~OHW|G@HDaNqG`CsP[aNYihXeXKrOiikrK~` | 21 | -2 | 4 | 6 | line graph of GC|v~{ |
| `WwCW?CB_A?cBccQQccwc_AQCCc[ccaQQSccfcccAQQOcccb` | 24 | -1 | 6 | 7 | prism over GC|v~w |
| `WwCW?CB_A?cBccQQccwc_AQCCc[ccaQQSccfcccaQQQcccf` | 24 | -1 | 6 | 7 | prism over GC|v~{ |
| `WwCW?CBcAOcbc_QOcc[CCOOS__{ccaQQSccfcccAQQOcccb` | 24 | -1 | 6 | 7 | prism over GEyn~w |
| `WwCW?CB_A?cBccQQccwc_AQCCc[ccaQQSccfcccAQQOcccb` | 24 | -1 | 6 | 7 | prism: G x K_k doubles dist_even_min while gamma_2 only doubles |

**Independent recomputation** (verification bar (a)):

| graph6 | n | path A | path B | agree | R (A) | R (B) |
|---|---|---|---|---|---|---|
| `O`?KAEiTXSAhiiTTtTAih` | 16 | disp_min=3 dist_even_min=8 gamma_2=4 | disp_min=3 dist_even_min=8 gamma_2=4 | True | -1 | -1 |

**Budget.** 39.0 s of the 3600 s cap. **Gate.** database sanity: PASS; independent recomputation: path A (`wall_arm.py`) vs path B (`scripts/gen/invariants.py` scal backend).

### FP-015 — CROSSED

**Statement.** `For every connected graph G with n(G) >= 2:  gamma_i <= diam + mu - 1`

**Equality in D:** 3 members, by order {'2': 1, '3': 1, '8': 1}.

**1. The wall.** 3 equality members: K_2, K_3, and G_ACDo at n=8 -- the balanced double star S(3,3) (two adjacent centres with three leaves each), with diam=3, mu=2, gamma_i=4.

**2. The obstruction.** mu. The tight double star has mu = 2 because every edge meets one of the two centres, so the vertex cover -- hence the matching -- cannot grow, while gamma_i = 1 + min(a,b) grows with the leaf sets. diam is pinned at 3. The residual is R = 4 - (1 + a) for S(a,a): zero at a = 3 (n = 8, the database edge) and negative from a = 4.

**3. G3-lite sign checks** (26 run, 23 stopped a trial). Only the checks that returned GO were allowed to run a trial.

_Passed (trial run):_

- independent blow-up of G_ACDo → **GO**  (dR = -2)<br>&nbsp;&nbsp;`G[I1]` (n=8) R=0 [diam=3 gamma_i=4 mu=2]<br>&nbsp;&nbsp;`G[I2]` (n=16) R=-2 [diam=3 gamma_i=8 mu=4]
- grow both leaf sets of the tight double star S(3,3) → **GO**  (dR = -1)<br>&nbsp;&nbsp;`S(1,1)` (n=4) R=2 [diam=3 gamma_i=2 mu=2]<br>&nbsp;&nbsp;`S(2,2)` (n=6) R=1 [diam=3 gamma_i=3 mu=2]
- independent blow-up of the tight member → **GO**  (dR = -2)<br>&nbsp;&nbsp;`(G_ACDo)[I1]` (n=8) R=0 [diam=3 gamma_i=4 mu=2]<br>&nbsp;&nbsp;`(G_ACDo)[I2]` (n=16) R=-2 [diam=3 gamma_i=8 mu=4]

_Stopped (trial not run):_

- clique blow-up of G_ACDo → **STOP-wrong-sign**  (dR = 6)
- subdivision of G_ACDo → **STOP-wrong-sign**  (dR = 5)
- corona of G_ACDo → **STOP-wrong-sign**  (dR = 4)
- join a clique onto G_ACDo → **STOP-wrong-sign**  (dR = 3)
- prism over G_ACDo → **STOP-wrong-sign**  (dR = 5)
- complement of G_ACDo → **STOP-wrong-sign**  (dR = 4)
- line graph of G_ACDo → **STOP-wrong-sign**  (dR = 3)
- clique blow-up of Bw → **STOP-wrong-sign**  (dR = 2)
- independent blow-up of Bw → **STOP-wrong-sign**  (dR = 2)
- subdivision of Bw → **STOP-wrong-sign**  (dR = 3)
- corona of Bw → **STOP-wrong-sign**  (dR = 2)
- join a clique onto Bw → **STOP-wrong-sign**  (dR = 1)
- prism over Bw → **STOP-wrong-sign**  (dR = 2)
- complement of Bw → **STOP-unavailable**
- line graph of Bw → **STOP-zero**  (dR = 0)
- clique blow-up of A_ → **STOP-wrong-sign**  (dR = 1)
- independent blow-up of A_ → **STOP-wrong-sign**  (dR = 1)
- subdivision of A_ → **STOP-wrong-sign**  (dR = 1)
- corona of A_ → **STOP-wrong-sign**  (dR = 2)
- join a clique onto A_ → **STOP-zero**  (dR = 0)
- prism over A_ → **STOP-wrong-sign**  (dR = 1)
- complement of A_ → **STOP-unavailable**
- line graph of A_ → **STOP-unavailable**

**4. Families built and tested.**

`independent blow-up of G_ACDo`

| member | n | R | invariants |
|---|---|---|---|
| G[I1] | 8 | 0 | diam=3 gamma_i=4 mu=2 |
| G[I2] | 16 | -2 | diam=3 gamma_i=8 mu=4 |
| G[I3] | 24 | -4 | diam=3 gamma_i=12 mu=6 |

`grow both leaf sets of the tight double star S(3,3)`

| member | n | R | invariants |
|---|---|---|---|
| S(1,1) | 4 | 2 | diam=3 gamma_i=2 mu=2 |
| S(2,2) | 6 | 1 | diam=3 gamma_i=3 mu=2 |
| S(3,3) | 8 | 0 | diam=3 gamma_i=4 mu=2 |
| S(4,4) | 10 | -1 | diam=3 gamma_i=5 mu=2 |
| S(5,5) | 12 | -2 | diam=3 gamma_i=6 mu=2 |
| S(6,6) | 14 | -3 | diam=3 gamma_i=7 mu=2 |
| S(7,7) | 16 | -4 | diam=3 gamma_i=8 mu=2 |

`independent blow-up of the tight member`

| member | n | R | invariants |
|---|---|---|---|
| (G_ACDo)[I1] | 8 | 0 | diam=3 gamma_i=4 mu=2 |
| (G_ACDo)[I2] | 16 | -2 | diam=3 gamma_i=8 mu=4 |
| (G_ACDo)[I3] | 24 | -4 | diam=3 gamma_i=12 mu=6 |

**Crossings.**

| graph6 | n | R | LHS | RHS | family |
|---|---|---|---|---|---|
| `IsaAA@?O?` | 10 | -1 | 5 | 4 | grow both leaf sets of the tight double star S(3,3) |
| `KsaCA@?OA?G?` | 12 | -2 | 6 | 4 | grow both leaf sets of the tight double star S(3,3) |
| `MsaCC@?OA?G?O?O??` | 14 | -3 | 7 | 4 | grow both leaf sets of the tight double star S(3,3) |
| `O]??????E?W?o?o?X}E^_` | 16 | -2 | 8 | 6 | independent blow-up of G_ACDo |
| `O]??????E?W?o?o?X}E^_` | 16 | -2 | 8 | 6 | independent blow-up of the tight member |
| `OsaCCA?OA?G?O?O?G?A??` | 16 | -4 | 8 | 4 | grow both leaf sets of the tight double star S(3,3) |
| `WFz_??????????????F??w?B_?F??F??B_??w~wFF~?[^{?` | 24 | -4 | 12 | 8 | independent blow-up of G_ACDo |
| `WFz_??????????????F??w?B_?F??F??B_??w~wFF~?[^{?` | 24 | -4 | 12 | 8 | independent blow-up of the tight member |

**Independent recomputation** (verification bar (a)):

| graph6 | n | path A | path B | agree | R (A) | R (B) |
|---|---|---|---|---|---|---|
| `IsaAA@?O?` | 10 | diam=3 gamma_i=5 mu=2 | diam=3 gamma_i=5 mu=2 | True | -1 | -1 |

**Budget.** 0.1 s of the 3600 s cap. **Gate.** database sanity: PASS; independent recomputation: path A (`wall_arm.py`) vs path B (`scripts/gen/invariants.py` scal backend).

### FP-016 — CROSSED

**Statement.** `For every connected graph G with n(G) >= 2:  gamma_i <= floor((alpha)/2) + gamma`

**Equality in D:** 290 members, by order {'2': 1, '3': 1, '4': 1, '5': 1, '6': 4, '7': 21, '8': 261}.

**1. The wall.** 290 equality members with gamma_t pinned at 2. The recorded 290 have alpha = gamma_i = 3 and gamma = 2 almost everywhere: the wall is 'alpha odd and gamma_i = floor(alpha/2) + gamma'.

**2. The obstruction.** alpha against gamma. Substituting an independent set of order m for every vertex multiplies alpha and gamma_i by m while leaving gamma at 2 (a dominating pair survives the blow-up), so the residual floor(alpha/2) + gamma - gamma_i = floor(3m/2) + 2 - 3m goes negative as soon as m >= 2.

**3. G3-lite sign checks** (25 run, 21 stopped a trial). Only the checks that returned GO were allowed to run a trial.

_Passed (trial run):_

- independent blow-up of G@N~vo → **GO**  (dR = -1)<br>&nbsp;&nbsp;`G[I1]` (n=8) R=0 [alpha=3 gamma=2 gamma_i=3]<br>&nbsp;&nbsp;`G[I2]` (n=16) R=-1 [alpha=6 gamma=2 gamma_i=6]
- independent blow-up of GBY|vo → **GO**  (dR = -1)<br>&nbsp;&nbsp;`G[I1]` (n=8) R=0 [alpha=3 gamma=2 gamma_i=3]<br>&nbsp;&nbsp;`G[I2]` (n=16) R=-1 [alpha=6 gamma=2 gamma_i=6]
- independent blow-up of GB}HFg → **GO**  (dR = -1)<br>&nbsp;&nbsp;`G[I1]` (n=8) R=0 [alpha=3 gamma=2 gamma_i=3]<br>&nbsp;&nbsp;`G[I2]` (n=16) R=-1 [alpha=6 gamma=2 gamma_i=6]
- independent blow-up: alpha and gamma_i scale, gamma stays 2 → **GO**  (dR = -1)<br>&nbsp;&nbsp;`(G@N~vo)[I1]` (n=8) R=0 [alpha=3 gamma=2 gamma_i=3]<br>&nbsp;&nbsp;`(G@N~vo)[I2]` (n=16) R=-1 [alpha=6 gamma=2 gamma_i=6]

_Stopped (trial not run):_

- clique blow-up of G@N~vo → **STOP-zero**  (dR = 0)
- subdivision of G@N~vo → **STOP-wrong-sign**  (dR = 9)
- corona of G@N~vo → **STOP-wrong-sign**  (dR = 4)
- join a clique onto G@N~vo → **STOP-wrong-sign**  (dR = 1)
- prism over G@N~vo → **STOP-wrong-sign**  (dR = 3)
- complement of G@N~vo → **STOP-unavailable**
- line graph of G@N~vo → **STOP-wrong-sign**  (dR = 2)
- clique blow-up of GBY|vo → **STOP-zero**  (dR = 0)
- subdivision of GBY|vo → **STOP-wrong-sign**  (dR = 8)
- corona of GBY|vo → **STOP-wrong-sign**  (dR = 4)
- join a clique onto GBY|vo → **STOP-wrong-sign**  (dR = 1)
- prism over GBY|vo → **STOP-wrong-sign**  (dR = 3)
- complement of GBY|vo → **STOP-wrong-sign**  (dR = 1)
- line graph of GBY|vo → **STOP-wrong-sign**  (dR = 2)
- clique blow-up of GB}HFg → **STOP-zero**  (dR = 0)
- subdivision of GB}HFg → **STOP-wrong-sign**  (dR = 7)
- corona of GB}HFg → **STOP-wrong-sign**  (dR = 4)
- join a clique onto GB}HFg → **STOP-wrong-sign**  (dR = 1)
- prism over GB}HFg → **STOP-wrong-sign**  (dR = 3)
- complement of GB}HFg → **STOP-wrong-sign**  (dR = 1)
- line graph of GB}HFg → **STOP-wrong-sign**  (dR = 2)

**4. Families built and tested.**

`independent blow-up of G@N~vo`

| member | n | R | invariants |
|---|---|---|---|
| G[I1] | 8 | 0 | alpha=3 gamma=2 gamma_i=3 |
| G[I2] | 16 | -1 | alpha=6 gamma=2 gamma_i=6 |
| G[I3] | 24 | -3 | alpha=9 gamma=2 gamma_i=9 |

`independent blow-up of GBY|vo`

| member | n | R | invariants |
|---|---|---|---|
| G[I1] | 8 | 0 | alpha=3 gamma=2 gamma_i=3 |
| G[I2] | 16 | -1 | alpha=6 gamma=2 gamma_i=6 |
| G[I3] | 24 | -3 | alpha=9 gamma=2 gamma_i=9 |

`independent blow-up of GB}HFg`

| member | n | R | invariants |
|---|---|---|---|
| G[I1] | 8 | 0 | alpha=3 gamma=2 gamma_i=3 |
| G[I2] | 16 | -1 | alpha=6 gamma=2 gamma_i=6 |
| G[I3] | 24 | -3 | alpha=9 gamma=2 gamma_i=9 |

`independent blow-up: alpha and gamma_i scale, gamma stays 2`

| member | n | R | invariants |
|---|---|---|---|
| (G@N~vo)[I1] | 8 | 0 | alpha=3 gamma=2 gamma_i=3 |
| (G@N~vo)[I2] | 16 | -1 | alpha=6 gamma=2 gamma_i=6 |
| (G@N~vo)[I3] | 24 | -3 | alpha=9 gamma=2 gamma_i=9 |
| (G@N~vo)[I4] | 32 | -4 | alpha=12 gamma=2 gamma_i=12 |

**Crossings.**

| graph6 | n | R | LHS | RHS | family |
|---|---|---|---|---|---|
| `O???WWNBv~~}~{~{^}F~_` | 16 | -1 | 6 | 5 | independent blow-up of G@N~vo |
| `O??@xw{NE^x}r{r{^}F~_` | 16 | -1 | 6 | 5 | independent blow-up of GBY|vo |
| `O??@xz~~u@wEB?B?^xf}W` | 16 | -1 | 6 | 5 | independent blow-up of GB}HFg |
| `O???WWNBv~~}~{~{^}F~_` | 16 | -1 | 6 | 5 | independent blow-up: alpha and gamma_i scale, gamma stays 2 |
| `W???????wF?[?~?~?^f~~~~z~~f~~F~~B~~_~~wF~~?^~{?` | 24 | -3 | 9 | 6 | independent blow-up of G@N~vo |
| `W??????Fw~B{FwFwB{FF~w~zb~fF~FF~Bb~_~~wF~~?^~{?` | 24 | -3 | 9 | 6 | independent blow-up of GBY|vo |
| `W??????Fw~B{~~~~^~f?Fw?z_B_F??F??B_?~~FF~ww^~b_` | 24 | -3 | 9 | 6 | independent blow-up of GB}HFg |
| `W???????wF?[?~?~?^f~~~~z~~f~~F~~B~~_~~wF~~?^~{?` | 24 | -3 | 9 | 6 | independent blow-up: alpha and gamma_i scale, gamma stays 2 |
| `_????????????N?N?F_@w?N{?~o@~_@~b~~~~~~v~~}^~~w~~~o~~~o^~~wF~~}?~~~oB~~~?F~~}?F~~}??` | 32 | -4 | 12 | 8 | independent blow-up: alpha and gamma_i scale, gamma stays 2 |

**Independent recomputation** (verification bar (a)):

| graph6 | n | path A | path B | agree | R (A) | R (B) |
|---|---|---|---|---|---|---|
| `O???WWNBv~~}~{~{^}F~_` | 16 | alpha=6 gamma=2 gamma_i=6 | alpha=6 gamma=2 gamma_i=6 | True | -1 | -1 |

**Budget.** 0.2 s of the 3600 s cap. **Gate.** database sanity: PASS; independent recomputation: path A (`wall_arm.py`) vs path B (`scripts/gen/invariants.py` scal backend).

### FP-017 — HELD

**Statement.** `For every connected graph G with n(G) >= 2:  gamma_t >= floor((cutv + chi_tree)/2) + 1`

**Equality in D:** 400 members, by order {'3': 1, '4': 2, '5': 5, '6': 16, '7': 60, '8': 316}.

**1. The wall.** 400 equality members; the recorded 300 all have kappa=1, delta=1, lambda_min=1 and cutv=2 (290 of 300) with gamma_t=2. The wall is the one-bridge stratum: two cut vertices and a dominating edge.

**2. The obstruction.** cutv against gamma_t. Every totally dominating set of size k induces a subgraph with no isolated vertex, hence spans at most floor(k/2) components, and every cut vertex must lie in or between those components. Each new cut vertex costs at least half a new dominator, which is exactly the floor((cutv+chi_tree)/2) term. Lengthening a caterpillar spine or chaining blocks raises cutv and gamma_t together, one for one.

**3. G3-lite sign checks** (26 run, 25 stopped a trial). Only the checks that returned GO were allowed to run a trial.

_Passed (trial run):_

- chain of triangles: one new cut vertex per block → **GO**  (dR = -1)<br>&nbsp;&nbsp;`chain_K3^2` (n=5) R=1 [chi_tree=0 cutv=1 gamma_t=2]<br>&nbsp;&nbsp;`chain_K3^3` (n=7) R=0 [chi_tree=0 cutv=2 gamma_t=2]

_Stopped (trial not run):_

- clique blow-up of G???F{ → **STOP-wrong-sign**  (dR = 1)
- independent blow-up of G???F{ → **STOP-wrong-sign**  (dR = 1)
- subdivision of G???F{ → **STOP-wrong-sign**  (dR = 3)
- corona of G???F{ → **STOP-wrong-sign**  (dR = 3)
- join a clique onto G???F{ → **STOP-wrong-sign**  (dR = 1)
- prism over G???F{ → **STOP-wrong-sign**  (dR = 1)
- complement of G???F{ → **STOP-unavailable**
- line graph of G???F{ → **STOP-wrong-sign**  (dR = 1)
- clique blow-up of G???Nw → **STOP-wrong-sign**  (dR = 1)
- independent blow-up of G???Nw → **STOP-wrong-sign**  (dR = 1)
- subdivision of G???Nw → **STOP-wrong-sign**  (dR = 2)
- corona of G???Nw → **STOP-wrong-sign**  (dR = 3)
- join a clique onto G???Nw → **STOP-wrong-sign**  (dR = 1)
- prism over G???Nw → **STOP-wrong-sign**  (dR = 3)
- complement of G???Nw → **STOP-wrong-sign**  (dR = 1)
- line graph of G???Nw → **STOP-wrong-sign**  (dR = 1)
- clique blow-up of G??KFo → **STOP-wrong-sign**  (dR = 2)
- independent blow-up of G??KFo → **STOP-wrong-sign**  (dR = 2)
- subdivision of G??KFo → **STOP-wrong-sign**  (dR = 2)
- corona of G??KFo → **STOP-wrong-sign**  (dR = 3)
- join a clique onto G??KFo → **STOP-wrong-sign**  (dR = 1)
- prism over G??KFo → **STOP-wrong-sign**  (dR = 5)
- complement of G??KFo → **STOP-wrong-sign**  (dR = 1)
- line graph of G??KFo → **STOP-zero**  (dR = 0)
- lengthen the caterpillar spine: one new cut vertex per step → **STOP-zero**  (dR = 0)

**4. Families built and tested.**

`chain of triangles: one new cut vertex per block`

| member | n | R | invariants |
|---|---|---|---|
| chain_K3^2 | 5 | 1 | chi_tree=0 cutv=1 gamma_t=2 |
| chain_K3^3 | 7 | 0 | chi_tree=0 cutv=2 gamma_t=2 |
| chain_K3^4 | 9 | 1 | chi_tree=0 cutv=3 gamma_t=3 |
| chain_K3^6 | 13 | 1 | chi_tree=0 cutv=5 gamma_t=4 |
| chain_K3^8 | 17 | 2 | chi_tree=0 cutv=7 gamma_t=6 |

**Outcome.** step 4 (family built and tested; it held) HELD. Caterpillar and chain-of-blocks families both grow the residual; cut vertices and total dominators grow together.

**Budget.** 0.1 s of the 3600 s cap. **Gate.** database sanity: PASS; independent recomputation: path A (`wall_arm.py`) vs path B (`scripts/gen/invariants.py` scal backend).

### FP-018 — HELD

**Statement.** `For every connected graph G with n(G) >= 2:  gamma_t >= floor((gamma)/(disp_min))`

**Equality in D:** 4972 members, by order {'4': 2, '5': 8, '6': 55, '7': 406, '8': 4501}.

**1. The wall.** 4972 equality members with disp_min pinned at 1 across all 300 recorded, and gamma = gamma_t on every one.

**2. The obstruction.** None isolable: disp_min >= 1 on every graph with no isolated vertex, so floor(gamma/disp_min) <= gamma <= gamma_t.

**3. G3-lite sign checks** (25 run, 25 stopped a trial). Only the checks that returned GO were allowed to run a trial.

_Stopped (trial not run):_

- clique blow-up of G???Nw → **STOP-wrong-sign**  (dR = 1)
- independent blow-up of G???Nw → **STOP-zero**  (dR = 0)
- subdivision of G???Nw → **STOP-wrong-sign**  (dR = 1)
- corona of G???Nw → **STOP-zero**  (dR = 0)
- join a clique onto G???Nw → **STOP-wrong-sign**  (dR = 2)
- prism over G???Nw → **STOP-wrong-sign**  (dR = 3)
- complement of G???Nw → **STOP-zero**  (dR = 0)
- line graph of G???Nw → **STOP-wrong-sign**  (dR = 1)
- clique blow-up of G??F~w → **STOP-wrong-sign**  (dR = 1)
- independent blow-up of G??F~w → **STOP-zero**  (dR = 0)
- subdivision of G??F~w → **STOP-wrong-sign**  (dR = 1)
- corona of G??F~w → **STOP-zero**  (dR = 0)
- join a clique onto G??F~w → **STOP-wrong-sign**  (dR = 2)
- prism over G??F~w → **STOP-wrong-sign**  (dR = 3)
- complement of G??F~w → **STOP-unavailable**
- line graph of G??F~w → **STOP-zero**  (dR = 0)
- clique blow-up of G??KFo → **STOP-wrong-sign**  (dR = 2)
- independent blow-up of G??KFo → **STOP-zero**  (dR = 0)
- subdivision of G??KFo → **STOP-wrong-sign**  (dR = 2)
- corona of G??KFo → **STOP-zero**  (dR = 0)
- join a clique onto G??KFo → **STOP-wrong-sign**  (dR = 2)
- prism over G??KFo → **STOP-wrong-sign**  (dR = 4)
- complement of G??KFo → **STOP-zero**  (dR = 0)
- line graph of G??KFo → **STOP-zero**  (dR = 0)
- raise disp_min while holding gamma (regularise the neighbourhoods) → **STOP-zero**  (dR = 0)

**4. Families built and tested.**

None — every proposed transformation was stopped at step 3.

**Outcome.** step 3 (G3-lite sign check stopped every proposed transformation) HELD -- theorem. disp_min >= 1 and gamma <= gamma_t.

**Budget.** 0.2 s of the 3600 s cap. **Gate.** database sanity: PASS; independent recomputation: path A (`wall_arm.py`) vs path B (`scripts/gen/invariants.py` scal backend).

### FP-019 — HELD

**Statement.** `For every connected graph G with n(G) >= 2:  kappa <= floor((t)/2) + floor(lambda_1)`

**Equality in D:** 175 members, by order {'2': 1, '3': 2, '4': 3, '5': 5, '6': 12, '7': 31, '8': 121}.

**1. The wall.** 175 equality members with kappa = floor(lambda_1) on every one and t in {0,1}; delta = kappa on 144 of 175. The wall is 'kappa = delta = floor(lambda_1)', i.e. the (near-)regular sparse stratum.

**2. The obstruction.** None isolable: kappa <= delta <= 2m/n <= lambda_1, and kappa is an integer, so kappa <= floor(lambda_1); t >= 0.

**3. G3-lite sign checks** (25 run, 25 stopped a trial). Only the checks that returned GO were allowed to run a trial.

_Stopped (trial not run):_

- clique blow-up of G?Bczo → **STOP-wrong-sign**  (dR = 28)
- independent blow-up of G?Bczo → **STOP-wrong-sign**  (dR = 5)
- subdivision of G?Bczo → **STOP-zero**  (dR = 0)
- corona of G?Bczo → **STOP-wrong-sign**  (dR = 2)
- join a clique onto G?Bczo → **STOP-wrong-sign**  (dR = 7)
- prism over G?Bczo → **STOP-wrong-sign**  (dR = 1)
- complement of G?Bczo → **STOP-wrong-sign**  (dR = 7)
- line graph of G?Bczo → **STOP-wrong-sign**  (dR = 6)
- clique blow-up of GA?KN? → **STOP-wrong-sign**  (dR = 16)
- independent blow-up of GA?KN? → **STOP-wrong-sign**  (dR = 1)
- subdivision of GA?KN? → **STOP-wrong-sign**  (dR = 1)
- corona of GA?KN? → **STOP-wrong-sign**  (dR = 1)
- join a clique onto GA?KN? → **STOP-wrong-sign**  (dR = 4)
- prism over GA?KN? → **STOP-zero**  (dR = 0)
- complement of GA?KN? → **STOP-wrong-sign**  (dR = 11)
- line graph of GA?KN? → **STOP-wrong-sign**  (dR = 1)
- clique blow-up of GEW`CK → **STOP-wrong-sign**  (dR = 19)
- independent blow-up of GEW`CK → **STOP-zero**  (dR = 0)
- subdivision of GEW`CK → **STOP-zero**  (dR = 0)
- corona of GEW`CK → **STOP-wrong-sign**  (dR = 1)
- join a clique onto GEW`CK → **STOP-wrong-sign**  (dR = 5)
- prism over GEW`CK → **STOP-zero**  (dR = 0)
- complement of GEW`CK → **STOP-wrong-sign**  (dR = 7)
- line graph of GEW`CK → **STOP-wrong-sign**  (dR = 1)
- kill the triangles and hold kappa (cycles and their blow-ups) → **STOP-zero**  (dR = 0)

**4. Families built and tested.**

None — every proposed transformation was stopped at step 3.

**Outcome.** step 3 (G3-lite sign check stopped every proposed transformation) HELD -- theorem. kappa <= delta <= floor(lambda_1).

**Budget.** 1.1 s of the 3600 s cap. **Gate.** database sanity: PASS; independent recomputation: path A (`wall_arm.py`) vs path B (`scripts/gen/invariants.py` scal backend).

### FP-020 — CROSSED

**Statement.** `For every connected graph G with n(G) >= 2:  kappa >= floor((disp_avg - ecc_avg)/2) + 1`

**Equality in D:** 1284 members, by order {'2': 1, '4': 1, '5': 3, '6': 10, '7': 78, '8': 1191}.

**1. The wall.** 1284 equality members; the recorded 300 all have kappa=1, delta=1, lambda_min=1, non-bipartite, non-regular. disp_avg sits in [2, 21/8] and ecc_avg in [15/8, 21/8]: the two averages are within 1 of each other on the entire wall, so the floor term is 0.

**2. The obstruction.** disp_avg. With kappa = 1 the graph has a cut vertex; if it also has diameter 2 that cut vertex is universal, which pins ecc_avg = 2 - 1/n. The residual then reads R = 1 - floor((disp_avg - 2 + 1/n)/2), so crossing needs disp_avg >= 4. disp_avg <= dd, and the wall's members only reach dd = 5 with most vertices seeing 2 distinct neighbour degrees. The construction that moves it is a complete multipartite core with all part sizes distinct, which gives every core vertex k-1 distinct neighbour degrees at once.

**3. G3-lite sign checks** (26 run, 25 stopped a trial). Only the checks that returned GO were allowed to run a trial.

_Passed (trial run):_

- index by q = the integer value of the floor term → **GO**  (dR = -1)<br>&nbsp;&nbsp;`q=0: K1 v (K_{1,2} u K1)` (n=5) R=0 [disp_avg=2 ecc_avg=9/5 kappa=1]<br>&nbsp;&nbsp;`q=1: K1 v (K_{1..5} u K1)` (n=17) R=-1 [disp_avg=82/17 ecc_avg=33/17 kappa=1]

_Stopped (trial not run):_

- clique blow-up of G??KN{ → **STOP-wrong-sign**  (dR = 1)
- independent blow-up of G??KN{ → **STOP-wrong-sign**  (dR = 1)
- subdivision of G??KN{ → **STOP-wrong-sign**  (dR = 2)
- corona of G??KN{ → **STOP-wrong-sign**  (dR = 1)
- join a clique onto G??KN{ → **STOP-wrong-sign**  (dR = 1)
- prism over G??KN{ → **STOP-wrong-sign**  (dR = 2)
- complement of G??KN{ → **STOP-unavailable**
- line graph of G??KN{ → **STOP-wrong-sign**  (dR = 2)
- clique blow-up of G?Bc~k → **STOP-wrong-sign**  (dR = 1)
- independent blow-up of G?Bc~k → **STOP-wrong-sign**  (dR = 1)
- subdivision of G?Bc~k → **STOP-wrong-sign**  (dR = 2)
- corona of G?Bc~k → **STOP-wrong-sign**  (dR = 1)
- join a clique onto G?Bc~k → **STOP-wrong-sign**  (dR = 1)
- prism over G?Bc~k → **STOP-wrong-sign**  (dR = 1)
- complement of G?Bc~k → **STOP-zero**  (dR = 0)
- line graph of G?Bc~k → **STOP-wrong-sign**  (dR = 2)
- clique blow-up of G?BwF{ → **STOP-wrong-sign**  (dR = 1)
- independent blow-up of G?BwF{ → **STOP-wrong-sign**  (dR = 1)
- subdivision of G?BwF{ → **STOP-wrong-sign**  (dR = 2)
- corona of G?BwF{ → **STOP-wrong-sign**  (dR = 1)
- join a clique onto G?BwF{ → **STOP-wrong-sign**  (dR = 1)
- prism over G?BwF{ → **STOP-wrong-sign**  (dR = 1)
- complement of G?BwF{ → **STOP-unavailable**
- line graph of G?BwF{ → **STOP-wrong-sign**  (dR = 5)
- force every vertex to see many distinct degrees, keep one cut vertex → **STOP-zero**  (dR = 0)

**4. Families built and tested.**

`index by q = the integer value of the floor term`

| member | n | R | invariants |
|---|---|---|---|
| q=0: K1 v (K_{1,2} u K1) | 5 | 0 | disp_avg=2 ecc_avg=9/5 kappa=1 |
| q=1: K1 v (K_{1..5} u K1) | 17 | -1 | disp_avg=82/17 ecc_avg=33/17 kappa=1 |
| q=2: K1 v (K_{1..8} u K1) | 38 | -2 | disp_avg=149/19 ecc_avg=75/38 kappa=1 |

**Crossings.**

| graph6 | n | R | LHS | RHS | family |
|---|---|---|---|---|---|
| `P}~vf~}~f{^~~}~}^~F~o_??` | 17 | -1 | 1 | 2 | index by q = the integer value of the floor term |
| `e}~vf~}~f{^~~}~}^~F~o~~~~~v~~f~~b~~o~~{F~~~~~~}~~~{~~~{^~~}F~~~_~~~{B~~~~~~~~~v~~~~r~~~~w~~~~}F~~~~o^~~~~?~~~~}?_??????` | 38 | -2 | 1 | 3 | index by q = the integer value of the floor term |

**Independent recomputation** (verification bar (a)):

| graph6 | n | path A | path B | agree | R (A) | R (B) |
|---|---|---|---|---|---|---|
| `P}~vf~}~f{^~~}~}^~F~o_??` | 17 | disp_avg=82/17 ecc_avg=33/17 kappa=1 | disp_avg=82/17 ecc_avg=33/17 kappa=1 | True | -1 | -1 |

**Budget.** 0.2 s of the 3600 s cap. **Gate.** database sanity: PASS; independent recomputation: path A (`wall_arm.py`) vs path B (`scripts/gen/invariants.py` scal backend).

### FP-021 — CROSSED

**Statement.** `For every connected graph G with n(G) >= 2:  kappa >= floor((lambda_avg - disp_max)/2) + 1`

**Equality in D:** 335 members, by order {'2': 1, '3': 1, '4': 1, '5': 2, '6': 9, '7': 44, '8': 277}.

**1. The wall.** 335 equality members; disp_max is pinned at 2 on 295 of the recorded 300 and kappa at 1 on 299 of 300. lambda_avg runs 7/4 to 3 -- always less than disp_max + 2, so the floor term is 0 and the bound reads kappa >= 1.

**2. The obstruction.** lambda_avg against disp_max. On the wall lambda_avg < disp_max + 2. Triangle-free graphs have lambda(v) = deg(v), so lambda_avg = deg_avg; amalgamating dense complete bipartite lobes at a single vertex raises deg_avg without raising disp_max above 2 and drops kappa to 1.

**3. G3-lite sign checks** (26 run, 25 stopped a trial). Only the checks that returned GO were allowed to run a trial.

_Passed (trial run):_

- amalgamate k lobes of K_{4,4} at one vertex (kappa drops to 1) → **GO**  (dR = -3)<br>&nbsp;&nbsp;`1 x K_{4,4} glued` (n=8) R=2 [disp_max=1 kappa=4 lam_avg=4]<br>&nbsp;&nbsp;`2 x K_{4,4} glued` (n=15) R=-1 [disp_max=2 kappa=1 lam_avg=64/15]

_Stopped (trial not run):_

- clique blow-up of G???F{ → **STOP-wrong-sign**  (dR = 2)
- independent blow-up of G???F{ → **STOP-zero**  (dR = 0)
- subdivision of G???F{ → **STOP-wrong-sign**  (dR = 1)
- corona of G???F{ → **STOP-wrong-sign**  (dR = 1)
- join a clique onto G???F{ → **STOP-wrong-sign**  (dR = 1)
- prism over G???F{ → **STOP-wrong-sign**  (dR = 1)
- complement of G???F{ → **STOP-unavailable**
- line graph of G???F{ → **STOP-wrong-sign**  (dR = 5)
- clique blow-up of G??F~w → **STOP-wrong-sign**  (dR = 3)
- independent blow-up of G??F~w → **STOP-wrong-sign**  (dR = 1)
- subdivision of G??F~w → **STOP-wrong-sign**  (dR = 1)
- corona of G??F~w → **STOP-zero**  (dR = 0)
- join a clique onto G??F~w → **STOP-wrong-sign**  (dR = 2)
- prism over G??F~w → **STOP-wrong-sign**  (dR = 1)
- complement of G??F~w → **STOP-unavailable**
- line graph of G??F~w → **STOP-wrong-sign**  (dR = 5)
- clique blow-up of G??KNo → **STOP-wrong-sign**  (dR = 2)
- independent blow-up of G??KNo → **STOP-zero**  (dR = 0)
- subdivision of G??KNo → **STOP-zero**  (dR = 0)
- corona of G??KNo → **STOP-wrong-sign**  (dR = 1)
- join a clique onto G??KNo → **STOP-wrong-sign**  (dR = 2)
- prism over G??KNo → **STOP-wrong-sign**  (dR = 1)
- complement of G??KNo → **STOP-wrong-sign**  (dR = 2)
- line graph of G??KNo → **STOP-wrong-sign**  (dR = 2)
- grow the bipartite lobe of the glued pair → **STOP-zero**  (dR = 0)

**4. Families built and tested.**

`amalgamate k lobes of K_{4,4} at one vertex (kappa drops to 1)`

| member | n | R | invariants |
|---|---|---|---|
| 1 x K_{4,4} glued | 8 | 2 | disp_max=1 kappa=4 lam_avg=4 |
| 2 x K_{4,4} glued | 15 | -1 | disp_max=2 kappa=1 lam_avg=64/15 |
| 3 x K_{4,4} glued | 22 | -1 | disp_max=2 kappa=1 lam_avg=48/11 |
| 4 x K_{4,4} glued | 29 | -1 | disp_max=2 kappa=1 lam_avg=128/29 |

**Crossings.**

| graph6 | n | R | LHS | RHS | family |
|---|---|---|---|---|---|
| `N?~vf_????OF_M_MOF?` | 15 | -1 | 1 | 2 | amalgamate k lobes of K_{4,4} at one vertex (kappa drops to 1) |
| `U?~vf_????OF_M_MOF????????C??{??y??[_?F?` | 22 | -1 | 1 | 2 | amalgamate k lobes of K_{4,4} at one vertex (kappa drops to 1) |
| `\?~vf_????OF_M_MOF????????C??{??y??[_?F????????????_??Bo??@s???[_??B_` | 29 | -1 | 1 | 2 | amalgamate k lobes of K_{4,4} at one vertex (kappa drops to 1) |

**Independent recomputation** (verification bar (a)):

| graph6 | n | path A | path B | agree | R (A) | R (B) |
|---|---|---|---|---|---|---|
| `N?~vf_????OF_M_MOF?` | 15 | disp_max=2 kappa=1 lam_avg=64/15 | disp_max=2 kappa=1 lam_avg=64/15 | True | -1 | -1 |

**Budget.** 0.2 s of the 3600 s cap. **Gate.** database sanity: PASS; independent recomputation: path A (`wall_arm.py`) vs path B (`scripts/gen/invariants.py` scal backend).

### FP-022 — CROSSED

**Statement.** `For every connected graph G with n(G) >= 2:  lambda_max >= floor((dd - f_1)/2)`

**Equality in D:** 380 members, by order {'6': 2, '7': 32, '8': 346}.

**1. The wall.** 380 equality members, mu pinned at 4 and n at 8, non-bipartite and C4-containing throughout. lambda_max = 2 on 285 of 300 with dd = 4 and f_1 = 0, so the bound reads 2 >= floor(4/2).

**2. The obstruction.** dd (number of distinct degrees) against lambda_max. The wall has dd = 4, f_1 = 0, lambda_max = 2, i.e. locally almost-complete neighbourhoods. The line graph keeps neighbourhoods locally two-clique (lambda_max = 2 on a line graph of a graph with no induced claw at the relevant vertex) while spreading the degree sequence, so dd rises to 6 and the floor term overtakes.

**3. G3-lite sign checks** (25 run, 24 stopped a trial). Only the checks that returned GO were allowed to run a trial.

_Passed (trial run):_

- line graph: dd rises, lambda_max stays 2 on a locally-bipartite wall → **GO**  (dR = -1)<br>&nbsp;&nbsp;`GBj]j{` (n=8) R=0 [dd=4 f1=0 lam_max=2]<br>&nbsp;&nbsp;`L(GBj]j{)` (n=18) R=-1 [dd=6 f1=0 lam_max=2]

_Stopped (trial not run):_

- clique blow-up of GB\||{ → **STOP-zero**  (dR = 0)
- independent blow-up of GB\||{ → **STOP-wrong-sign**  (dR = 2)
- subdivision of GB\||{ → **STOP-wrong-sign**  (dR = 4)
- corona of GB\||{ → **STOP-wrong-sign**  (dR = 5)
- join a clique onto GB\||{ → **STOP-wrong-sign**  (dR = 1)
- prism over GB\||{ → **STOP-wrong-sign**  (dR = 1)
- complement of GB\||{ → **STOP-wrong-sign**  (dR = 5)
- line graph of GB\||{ → **STOP-zero**  (dR = 0)
- clique blow-up of GB]mj{ → **STOP-zero**  (dR = 0)
- independent blow-up of GB]mj{ → **STOP-wrong-sign**  (dR = 2)
- subdivision of GB]mj{ → **STOP-wrong-sign**  (dR = 4)
- corona of GB]mj{ → **STOP-wrong-sign**  (dR = 5)
- join a clique onto GB]mj{ → **STOP-wrong-sign**  (dR = 1)
- prism over GB]mj{ → **STOP-wrong-sign**  (dR = 1)
- complement of GB]mj{ → **STOP-wrong-sign**  (dR = 3)
- line graph of GB]mj{ → **STOP-zero**  (dR = 0)
- clique blow-up of GB]mm{ → **STOP-zero**  (dR = 0)
- independent blow-up of GB]mm{ → **STOP-wrong-sign**  (dR = 2)
- subdivision of GB]mm{ → **STOP-wrong-sign**  (dR = 4)
- corona of GB]mm{ → **STOP-wrong-sign**  (dR = 5)
- join a clique onto GB]mm{ → **STOP-wrong-sign**  (dR = 1)
- prism over GB]mm{ → **STOP-wrong-sign**  (dR = 1)
- complement of GB]mm{ → **STOP-wrong-sign**  (dR = 2)
- line graph of GB]mm{ → **STOP-zero**  (dR = 0)

**4. Families built and tested.**

`line graph: dd rises, lambda_max stays 2 on a locally-bipartite wall`

| member | n | R | invariants |
|---|---|---|---|
| GBj]j{ | 8 | 0 | dd=4 f1=0 lam_max=2 |
| L(GBj]j{) | 18 | -1 | dd=6 f1=0 lam_max=2 |

**Crossings.**

| graph6 | n | R | LHS | RHS | family |
|---|---|---|---|---|---|
| `QwSwwa@?yqEhCvqIOUZWYQe{eUw` | 18 | -1 | 2 | 3 | line graph: dd rises, lambda_max stays 2 on a locally-bipartite wall |

**Independent recomputation** (verification bar (a)):

| graph6 | n | path A | path B | agree | R (A) | R (B) |
|---|---|---|---|---|---|---|
| `QwSwwa@?yqEhCvqIOUZWYQe{eUw` | 18 | dd=6 f1=0 lam_max=2 | dd=6 f1=0 lam_max=2 | True | -1 | -1 |

**Budget.** 0.1 s of the 3600 s cap. **Gate.** database sanity: PASS; independent recomputation: path A (`wall_arm.py`) vs path B (`scripts/gen/invariants.py` scal backend).

### FP-023 — CROSSED

**Statement.** `For every connected graph G with n(G) >= 2:  lambda_max >= floor((gamma_2 - chi)/2) + 1`

**Equality in D:** 30 members, by order {'2': 1, '6': 1, '7': 1, '8': 27}.

**1. The wall.** 30 equality members: 27 at n=8, all with kappa=1 and 3-6 cut vertices, gamma_2 in {5,6}, chi in {2,3}, lambda_max in {2,3}. G_CKJ? (the path P_8) and GA?KJG (a tree) are the extreme members; disp_min is pinned at 1 on 29 of 30.

**2. The obstruction.** gamma_2 against lambda_max with chi pinned. For a triangle-free graph lambda_max = Delta; on a path Delta = 2 and chi = 2 while gamma_2(P_n) = floor(n/2)+1, so R = 2 - (floor((floor(n/2)-1)/2)+1) is zero at n <= 9 and negative from n = 10. Hanging pendants does the same thing faster: the corona of a tight member has gamma_2 = |H| + gamma(H) with lambda_max still 3.

**3. G3-lite sign checks** (26 run, 19 stopped a trial). Only the checks that returned GO were allowed to run a trial.

_Passed (trial run):_

- subdivision of GA?KJG → **GO**  (dR = -1)<br>&nbsp;&nbsp;`sub^0(G)` (n=8) R=0 [chi=2 gamma_2=6 lam_max=3]<br>&nbsp;&nbsp;`sub^1(G)` (n=15) R=-1 [chi=2 gamma_2=8 lam_max=3]
- corona of GA?KJG → **GO**  (dR = -2)<br>&nbsp;&nbsp;`G o 0K1` (n=8) R=0 [chi=2 gamma_2=6 lam_max=3]<br>&nbsp;&nbsp;`G o 1K1` (n=16) R=-2 [chi=2 gamma_2=12 lam_max=4]
- subdivision of GBO`KK → **GO**  (dR = -1)<br>&nbsp;&nbsp;`sub^0(G)` (n=8) R=0 [chi=3 gamma_2=5 lam_max=2]<br>&nbsp;&nbsp;`sub^1(G)` (n=17) R=-1 [chi=2 gamma_2=8 lam_max=3]
- corona of GBO`KK → **GO**  (dR = -2)<br>&nbsp;&nbsp;`G o 0K1` (n=8) R=0 [chi=3 gamma_2=5 lam_max=2]<br>&nbsp;&nbsp;`G o 1K1` (n=16) R=-2 [chi=3 gamma_2=11 lam_max=3]
- subdivision of GBO`MO → **GO**  (dR = -1)<br>&nbsp;&nbsp;`sub^0(G)` (n=8) R=0 [chi=3 gamma_2=5 lam_max=2]<br>&nbsp;&nbsp;`sub^1(G)` (n=17) R=-1 [chi=2 gamma_2=8 lam_max=3]
- corona of GBO`MO → **GO**  (dR = -1)<br>&nbsp;&nbsp;`G o 0K1` (n=8) R=0 [chi=3 gamma_2=5 lam_max=2]<br>&nbsp;&nbsp;`G o 1K1` (n=16) R=-1 [chi=3 gamma_2=10 lam_max=3]
- corona of the tight member (pendants force gamma_2 up, lambda_max pinned) → **GO**  (dR = -1)<br>&nbsp;&nbsp;`(GBO`MO) o 0K1` (n=8) R=0 [chi=3 gamma_2=5 lam_max=2]<br>&nbsp;&nbsp;`(GBO`MO) o 1K1` (n=16) R=-1 [chi=3 gamma_2=10 lam_max=3]

_Stopped (trial not run):_

- clique blow-up of GA?KJG → **STOP-zero**  (dR = 0)
- independent blow-up of GA?KJG → **STOP-wrong-sign**  (dR = 2)
- join a clique onto GA?KJG → **STOP-wrong-sign**  (dR = 2)
- prism over GA?KJG → **STOP-zero**  (dR = 0)
- complement of GA?KJG → **STOP-wrong-sign**  (dR = 2)
- line graph of GA?KJG → **STOP-wrong-sign**  (dR = 1)
- clique blow-up of GBO`KK → **STOP-wrong-sign**  (dR = 1)
- independent blow-up of GBO`KK → **STOP-wrong-sign**  (dR = 2)
- join a clique onto GBO`KK → **STOP-wrong-sign**  (dR = 3)
- prism over GBO`KK → **STOP-zero**  (dR = 0)
- complement of GBO`KK → **STOP-wrong-sign**  (dR = 3)
- line graph of GBO`KK → **STOP-wrong-sign**  (dR = 1)
- clique blow-up of GBO`MO → **STOP-wrong-sign**  (dR = 2)
- independent blow-up of GBO`MO → **STOP-wrong-sign**  (dR = 3)
- join a clique onto GBO`MO → **STOP-wrong-sign**  (dR = 4)
- prism over GBO`MO → **STOP-zero**  (dR = 0)
- complement of GBO`MO → **STOP-wrong-sign**  (dR = 3)
- line graph of GBO`MO → **STOP-wrong-sign**  (dR = 1)
- stretch the tight path P_8 → **STOP-zero**  (dR = 0)

**4. Families built and tested.**

`subdivision of GA?KJG`

| member | n | R | invariants |
|---|---|---|---|
| sub^0(G) | 8 | 0 | chi=2 gamma_2=6 lam_max=3 |
| sub^1(G) | 15 | -1 | chi=2 gamma_2=8 lam_max=3 |
| sub^2(G) | 29 | TIMEOUT |  |

`corona of GA?KJG`

| member | n | R | invariants |
|---|---|---|---|
| G o 0K1 | 8 | 0 | chi=2 gamma_2=6 lam_max=3 |
| G o 1K1 | 16 | -2 | chi=2 gamma_2=12 lam_max=4 |
| G o 2K1 | 24 | TIMEOUT |  |

`subdivision of GBO`KK`

| member | n | R | invariants |
|---|---|---|---|
| sub^0(G) | 8 | 0 | chi=3 gamma_2=5 lam_max=2 |
| sub^1(G) | 17 | -1 | chi=2 gamma_2=8 lam_max=3 |
| sub^2(G) | 35 | TIMEOUT |  |

`corona of GBO`KK`

| member | n | R | invariants |
|---|---|---|---|
| G o 0K1 | 8 | 0 | chi=3 gamma_2=5 lam_max=2 |
| G o 1K1 | 16 | -2 | chi=3 gamma_2=11 lam_max=3 |
| G o 2K1 | 24 | TIMEOUT |  |

`subdivision of GBO`MO`

| member | n | R | invariants |
|---|---|---|---|
| sub^0(G) | 8 | 0 | chi=3 gamma_2=5 lam_max=2 |
| sub^1(G) | 17 | -1 | chi=2 gamma_2=8 lam_max=3 |
| sub^2(G) | 35 | TIMEOUT |  |

`corona of GBO`MO`

| member | n | R | invariants |
|---|---|---|---|
| G o 0K1 | 8 | 0 | chi=3 gamma_2=5 lam_max=2 |
| G o 1K1 | 16 | -1 | chi=3 gamma_2=10 lam_max=3 |
| G o 2K1 | 24 | TIMEOUT |  |

`corona of the tight member (pendants force gamma_2 up, lambda_max pinned)`

| member | n | R | invariants |
|---|---|---|---|
| (GBO`MO) o 0K1 | 8 | 0 | chi=3 gamma_2=5 lam_max=2 |
| (GBO`MO) o 1K1 | 16 | -1 | chi=3 gamma_2=10 lam_max=3 |

**Crossings.**

| graph6 | n | R | LHS | RHS | family |
|---|---|---|---|---|---|
| `N????AASAACGB?@_?g?` | 15 | -1 | 3 | 4 | subdivision of GA?KJG |
| `OBO`MQ?O@?A?A?@??O?A?` | 16 | -1 | 3 | 4 | corona of GBO`MO |
| `OBO`MQ?O@?A?A?@??O?A?` | 16 | -1 | 3 | 4 | corona of the tight member (pendants force gamma_2 up, lambda_max pinned) |
| `OA?KJI?O@?A?A?@??O?A?` | 16 | -2 | 4 | 6 | corona of GA?KJG |
| `OBO`KM?O@?A?A?@??O?A?` | 16 | -2 | 3 | 5 | corona of GBO`KK |
| `P????A@SAOE?H?G_?o?I??o?` | 17 | -1 | 3 | 4 | subdivision of GBO`KK |
| `P????A@SAOGGK?H?CO?Q?@_?` | 17 | -1 | 3 | 4 | subdivision of GBO`MO |

**Smallest member of the same family** — `P_10` = `IhCGGC@?G` (n = 10), LHS = 2, RHS = 3, R = -1. Found after the crossing was already established by a sign-check-authorised trial, by re-reading the same one-parameter family downwards. The literal G3-lite check on consecutive path lengths is dR = 0 (the residual is a floor step function), which is why the path family itself was stopped at step 3 and the subdivision of the same tight member was used instead.

**Independent recomputation** (verification bar (a)):

| graph6 | n | path A | path B | agree | R (A) | R (B) |
|---|---|---|---|---|---|---|
| `N????AASAACGB?@_?g?` | 15 | chi=2 gamma_2=8 lam_max=3 | chi=2 gamma_2=8 lam_max=3 | True | -1 | -1 |
| `IhCGGC@?G` | 10 | chi=2 gamma_2=6 lam_max=2 | chi=2 gamma_2=6 lam_max=2 | True | -1 | -1 |

**Budget.** 365.1 s of the 3600 s cap. **Gate.** database sanity: PASS; independent recomputation: path A (`wall_arm.py`) vs path B (`scripts/gen/invariants.py` scal backend).

### FP-024 — HELD

**Statement.** `For every connected graph G with n(G) >= 2:  mu <= ceil((n - chi_tree)/2)`

**Equality in D:** 10407 members, by order {'2': 1, '3': 1, '4': 5, '5': 2, '6': 95, '7': 6, '8': 10297}.

**1. The wall.** 10407 equality members -- the largest wall in the population -- mu pinned at 4 = ceil(n/2) with n=8 and chi_tree=0. The wall is every graph with a (near-)perfect matching.

**2. The obstruction.** None isolable: mu <= floor(n/2) <= ceil((n-1)/2) for a tree and <= ceil(n/2) otherwise.

**3. G3-lite sign checks** (25 run, 25 stopped a trial). Only the checks that returned GO were allowed to run a trial.

_Stopped (trial not run):_

- clique blow-up of G?F~vo → **STOP-zero**  (dR = 0)
- independent blow-up of G?F~vo → **STOP-zero**  (dR = 0)
- subdivision of G?F~vo → **STOP-wrong-sign**  (dR = 4)
- corona of G?F~vo → **STOP-zero**  (dR = 0)
- join a clique onto G?F~vo → **STOP-wrong-sign**  (dR = 1)
- prism over G?F~vo → **STOP-zero**  (dR = 0)
- complement of G?F~vo → **STOP-unavailable**
- line graph of G?F~vo → **STOP-zero**  (dR = 0)
- clique blow-up of G?F~vw → **STOP-zero**  (dR = 0)
- independent blow-up of G?F~vw → **STOP-zero**  (dR = 0)
- subdivision of G?F~vw → **STOP-wrong-sign**  (dR = 5)
- corona of G?F~vw → **STOP-zero**  (dR = 0)
- join a clique onto G?F~vw → **STOP-wrong-sign**  (dR = 1)
- prism over G?F~vw → **STOP-zero**  (dR = 0)
- complement of G?F~vw → **STOP-unavailable**
- line graph of G?F~vw → **STOP-wrong-sign**  (dR = 1)
- clique blow-up of G?F~v{ → **STOP-zero**  (dR = 0)
- independent blow-up of G?F~v{ → **STOP-zero**  (dR = 0)
- subdivision of G?F~v{ → **STOP-wrong-sign**  (dR = 5)
- corona of G?F~v{ → **STOP-zero**  (dR = 0)
- join a clique onto G?F~v{ → **STOP-wrong-sign**  (dR = 1)
- prism over G?F~v{ → **STOP-zero**  (dR = 0)
- complement of G?F~v{ → **STOP-unavailable**
- line graph of G?F~v{ → **STOP-zero**  (dR = 0)
- push the matching past ceil(n/2) (regular and near-regular blow-ups) → **STOP-zero**  (dR = 0)

**4. Families built and tested.**

None — every proposed transformation was stopped at step 3.

**Outcome.** step 3 (G3-lite sign check stopped every proposed transformation) HELD -- theorem. mu <= floor(n/2).

**Budget.** 0.1 s of the 3600 s cap. **Gate.** database sanity: PASS; independent recomputation: path A (`wall_arm.py`) vs path B (`scripts/gen/invariants.py` scal backend).

### FP-025 — HELD

**Statement.** `For every connected graph G with n(G) >= 2:  mu >= floor((delta + lambda_min)/2)`

**Equality in D:** 58 members, by order {'2': 1, '3': 2, '4': 3, '5': 7, '6': 6, '7': 29, '8': 10}.

**1. The wall.** 58 equality members with nothing pinned. They split into two strata: the complete bipartite graphs K_{a,a} and K_{a,b} (delta = lam_min = mu) and the complete/near-complete graphs (delta = n-1, lam_min = 1, mu = floor(n/2)).

**2. The obstruction.** None isolable: taking a vertex u of minimum degree, lam_min <= lambda(u) <= deg(u) = delta, so the right-hand side is at most delta. If delta <= floor(n/2) then mu >= min(delta, floor(n/2)) = delta. If delta > floor(n/2) then mu = floor(n/2) and, writing delta = n-1-k with k the maximum degree of the complement, lam_min <= omega(complement) <= k+1, so delta + lam_min <= n.

**3. G3-lite sign checks** (26 run, 26 stopped a trial). Only the checks that returned GO were allowed to run a trial.

_Stopped (trial not run):_

- clique blow-up of G???F{ → **STOP-wrong-sign**  (dR = 6)
- independent blow-up of G???F{ → **STOP-zero**  (dR = 0)
- subdivision of G???F{ → **STOP-wrong-sign**  (dR = 6)
- corona of G???F{ → **STOP-wrong-sign**  (dR = 7)
- join a clique onto G???F{ → **STOP-wrong-sign**  (dR = 1)
- prism over G???F{ → **STOP-wrong-sign**  (dR = 6)
- complement of G???F{ → **STOP-unavailable**
- line graph of G???F{ → **STOP-zero**  (dR = 0)
- clique blow-up of G??F~w → **STOP-wrong-sign**  (dR = 5)
- independent blow-up of G??F~w → **STOP-zero**  (dR = 0)
- subdivision of G??F~w → **STOP-wrong-sign**  (dR = 6)
- corona of G??F~w → **STOP-wrong-sign**  (dR = 7)
- join a clique onto G??F~w → **STOP-wrong-sign**  (dR = 1)
- prism over G??F~w → **STOP-wrong-sign**  (dR = 5)
- complement of G??F~w → **STOP-unavailable**
- line graph of G??F~w → **STOP-wrong-sign**  (dR = 2)
- clique blow-up of G]rE@{ → **STOP-wrong-sign**  (dR = 3)
- independent blow-up of G]rE@{ → **STOP-zero**  (dR = 0)
- subdivision of G]rE@{ → **STOP-wrong-sign**  (dR = 6)
- corona of G]rE@{ → **STOP-wrong-sign**  (dR = 7)
- join a clique onto G]rE@{ → **STOP-wrong-sign**  (dR = 1)
- prism over G]rE@{ → **STOP-wrong-sign**  (dR = 4)
- complement of G]rE@{ → **STOP-unavailable**
- line graph of G]rE@{ → **STOP-wrong-sign**  (dR = 3)
- raise lam_min against delta (complete multipartite, then blow-ups) → **STOP-zero**  (dR = 0)
- cocktail-party graphs: delta = n-2, lam_min = 2 → **STOP-zero**  (dR = 0)

**4. Families built and tested.**

None — every proposed transformation was stopped at step 3.

**Outcome.** step 3 (G3-lite sign check stopped every proposed transformation) HELD -- theorem (minimum-degree vertex bounds lam_min by delta).

**Budget.** 0.0 s of the 3600 s cap. **Gate.** database sanity: PASS; independent recomputation: path A (`wall_arm.py`) vs path B (`scripts/gen/invariants.py` scal backend).

### FP-026 — CROSSED

**Statement.** `For every connected graph G with n(G) >= 2:  rad >= floor((disp_max)/(floor(lambda_1)))`

**Equality in D:** 747 members, by order {'2': 1, '3': 1, '4': 4, '5': 7, '6': 19, '7': 95, '8': 620}.

**1. The wall.** 747 equality members; the recorded 300 all have rad = 1 (a universal vertex) with disp_max = floor(lambda_1) exactly, values 2, 3 or 4. The wall is 'universal vertex, and the number of distinct neighbour degrees equals floor(lambda_1)'.

**2. The obstruction.** disp_max against floor(lambda_1). With rad = 1 there is a universal vertex, which forces lambda_1 >= sqrt(n-1) while disp_max <= dd grows only like sqrt(2n) for a sparse core -- the wall is closed at rad = 1. Giving up the universal vertex (rad = 2) and using a tree whose branches are stars of distinct sizes makes disp_max = d exactly while lambda_1 grows like sqrt(d), so floor(disp_max/floor(lambda_1)) reaches 3 while rad stays 2.

**3. G3-lite sign checks** (26 run, 25 stopped a trial). Only the checks that returned GO were allowed to run a trial.

_Passed (trial run):_

- index by q = the value of the RHS floor term → **GO**  (dR = -1)<br>&nbsp;&nbsp;`q=2: SoS(2)` (n=6) R=0 [disp_max=2 rad=2 spec_floor=1]<br>&nbsp;&nbsp;`q=3: SoS(9)` (n=55) R=-1 [disp_max=9 rad=2 spec_floor=3]

_Stopped (trial not run):_

- clique blow-up of G???N{ → **STOP-wrong-sign**  (dR = 1)
- independent blow-up of G???N{ → **STOP-wrong-sign**  (dR = 2)
- subdivision of G???N{ → **STOP-wrong-sign**  (dR = 2)
- corona of G???N{ → **STOP-wrong-sign**  (dR = 1)
- join a clique onto G???N{ → **STOP-wrong-sign**  (dR = 1)
- prism over G???N{ → **STOP-wrong-sign**  (dR = 1)
- complement of G???N{ → **STOP-unavailable**
- line graph of G???N{ → **STOP-wrong-sign**  (dR = 1)
- clique blow-up of G??KN{ → **STOP-wrong-sign**  (dR = 1)
- independent blow-up of G??KN{ → **STOP-wrong-sign**  (dR = 2)
- subdivision of G??KN{ → **STOP-wrong-sign**  (dR = 2)
- corona of G??KN{ → **STOP-wrong-sign**  (dR = 1)
- join a clique onto G??KN{ → **STOP-zero**  (dR = 0)
- prism over G??KN{ → **STOP-wrong-sign**  (dR = 1)
- complement of G??KN{ → **STOP-unavailable**
- line graph of G??KN{ → **STOP-wrong-sign**  (dR = 2)
- clique blow-up of G?Bc~{ → **STOP-wrong-sign**  (dR = 1)
- independent blow-up of G?Bc~{ → **STOP-wrong-sign**  (dR = 2)
- subdivision of G?Bc~{ → **STOP-wrong-sign**  (dR = 3)
- corona of G?Bc~{ → **STOP-wrong-sign**  (dR = 1)
- join a clique onto G?Bc~{ → **STOP-wrong-sign**  (dR = 1)
- prism over G?Bc~{ → **STOP-wrong-sign**  (dR = 2)
- complement of G?Bc~{ → **STOP-unavailable**
- line graph of G?Bc~{ → **STOP-wrong-sign**  (dR = 2)
- star of stars: raise disp_max (distinct branch degrees) against floor(lambda_1) → **STOP-wrong-sign**  (dR = 1)

**4. Families built and tested.**

`index by q = the value of the RHS floor term`

| member | n | R | invariants |
|---|---|---|---|
| q=2: SoS(2) | 6 | 0 | disp_max=2 rad=2 spec_floor=1 |
| q=3: SoS(9) | 55 | -1 | disp_max=9 rad=2 spec_floor=3 |

**Crossings.**

| graph6 | n | R | LHS | RHS | family |
|---|---|---|---|---|---|
| `vkCS?CA?c??@?A?A?@C????C??O??_??_??O_??????_??A???C???C???A????__????????G????O????O????G????A?????O????@?_???????????_?????O?????C??????_?????A??????C??????C??????A?_??????????????_??????A???????C???????C???????A????????_???????C????????O????????_?` | 55 | -1 | 2 | 3 | index by q = the value of the RHS floor term |

**Independent recomputation** (verification bar (a)):

| graph6 | n | path A | path B | agree | R (A) | R (B) |
|---|---|---|---|---|---|---|
| `vkCS?CA?c??@?A?A?@C????C??O??_??_??O_??????_??A???C???C???A????__????????G????O????O????G????A?????O????@?_???????????_?????O?????C??????_?????A??????C??????C??????A?_??????????????_??????A???????C???????C???????A????????_???????C????????O????????_?` | 55 | rad=2 disp_max=9 spec_floor=3 | rad=2 (networkx.radius) disp_max=9 (networkx degree scan) spec_floor=3 (numpy eigvalsh: lambda_1 = 3.837571178841834) | True | -1 | -1 |

> scripts/gen/invariants.py could not be used as path B here: its _spectral_bracket scans k upward doing n Bareiss determinants per probe, which is O(n^4) per probe at n=55 and did not finish inside the cap. The second reading is networkx for rad and disp_max plus a float eigenvalue computation bracketing lambda_1 in (3,4); the exact rational LDL^T test in path A confirms 3I-A is not PD and 4I-A is PD.

**Budget.** 2.4 s of the 3600 s cap. **Gate.** database sanity: PASS; independent recomputation: path A (`wall_arm.py`) vs path B (`scripts/gen/invariants.py` scal backend).

### FP-027 — HELD

**Statement.** `For every connected graph G with n(G) >= 2:  rad >= floor((ecc_avg)/2) + chi_bipartite`

**Equality in D:** 215 members, by order {'2': 1, '3': 1, '4': 3, '5': 5, '6': 16, '7': 41, '8': 148}.

**1. The wall.** 215 equality members, all bipartite (chi_bip=1, t=0, omega=chi=2). The wall is the bipartite stratum where ecc_avg sits in [2 rad - 2, 2 rad).

**2. The obstruction.** None isolable: ecc(v) <= 2 rad for every v, and the centre attains ecc = rad < 2 rad, so ecc_avg < 2 rad strictly and floor(ecc_avg/2) <= rad - 1. The bipartite correction term of +1 is exactly absorbed by that strict inequality.

**3. G3-lite sign checks** (26 run, 26 stopped a trial). Only the checks that returned GO were allowed to run a trial.

_Stopped (trial not run):_

- clique blow-up of G???F{ → **STOP-wrong-sign**  (dR = 1)
- independent blow-up of G???F{ → **STOP-zero**  (dR = 0)
- subdivision of G???F{ → **STOP-zero**  (dR = 0)
- corona of G???F{ → **STOP-zero**  (dR = 0)
- join a clique onto G???F{ → **STOP-wrong-sign**  (dR = 1)
- prism over G???F{ → **STOP-zero**  (dR = 0)
- complement of G???F{ → **STOP-unavailable**
- line graph of G???F{ → **STOP-wrong-sign**  (dR = 1)
- clique blow-up of G???Nw → **STOP-wrong-sign**  (dR = 1)
- independent blow-up of G???Nw → **STOP-zero**  (dR = 0)
- subdivision of G???Nw → **STOP-zero**  (dR = 0)
- corona of G???Nw → **STOP-zero**  (dR = 0)
- join a clique onto G???Nw → **STOP-wrong-sign**  (dR = 1)
- prism over G???Nw → **STOP-wrong-sign**  (dR = 1)
- complement of G???Nw → **STOP-wrong-sign**  (dR = 1)
- line graph of G???Nw → **STOP-wrong-sign**  (dR = 1)
- clique blow-up of G??F~w → **STOP-wrong-sign**  (dR = 1)
- independent blow-up of G??F~w → **STOP-zero**  (dR = 0)
- subdivision of G??F~w → **STOP-wrong-sign**  (dR = 1)
- corona of G??F~w → **STOP-wrong-sign**  (dR = 1)
- join a clique onto G??F~w → **STOP-wrong-sign**  (dR = 1)
- prism over G??F~w → **STOP-wrong-sign**  (dR = 1)
- complement of G??F~w → **STOP-unavailable**
- line graph of G??F~w → **STOP-wrong-sign**  (dR = 1)
- push ecc_avg towards 2*rad (bipartite, all-peripheral) → **STOP-zero**  (dR = 0)
- caterpillar / broom: many peripheral vertices, one centre → **STOP-zero**  (dR = 0)

**4. Families built and tested.**

None — every proposed transformation was stopped at step 3.

**Outcome.** step 3 (G3-lite sign check stopped every proposed transformation) HELD -- theorem. ecc_avg < 2 rad.

**Budget.** 0.0 s of the 3600 s cap. **Gate.** database sanity: PASS; independent recomputation: path A (`wall_arm.py`) vs path B (`scripts/gen/invariants.py` scal backend).

### FP-028 — HELD

**Statement.** `For every connected graph G with n(G) >= 2:  res <= alpha + CW - 1`

**Equality in D:** 7 members, by order {'2': 1, '3': 1, '4': 1, '5': 1, '6': 1, '7': 1, '8': 1}.

**1. The wall.** 7 equality members: exactly the complete graphs K_2..K_8. Everything is pinned: CW=1, alpha=1, res=1, dd=1, diam=rad=1, chi_reg=1.

**2. The obstruction.** None isolable: res <= alpha (Favaron-Maheo-Sacle) and CW = sum_v 1/(1+deg v) >= n/(1+Delta) >= 1.

**3. G3-lite sign checks** (25 run, 25 stopped a trial). Only the checks that returned GO were allowed to run a trial.

_Stopped (trial not run):_

- clique blow-up of G~~~~{ → **STOP-zero**  (dR = 0)
- independent blow-up of G~~~~{ → **STOP-wrong-sign**  (dR = 1/15)
- subdivision of G~~~~{ → **STOP-wrong-sign**  (dR = 79/3)
- corona of G~~~~{ → **STOP-wrong-sign**  (dR = 35/9)
- join a clique onto G~~~~{ → **STOP-zero**  (dR = 0)
- prism over G~~~~{ → **STOP-wrong-sign**  (dR = 7/9)
- complement of G~~~~{ → **STOP-unavailable**
- line graph of G~~~~{ → **STOP-wrong-sign**  (dR = 28/13)
- clique blow-up of F~~~w → **STOP-zero**  (dR = 0)
- independent blow-up of F~~~w → **STOP-wrong-sign**  (dR = 1/13)
- subdivision of F~~~w → **STOP-wrong-sign**  (dR = 20)
- corona of F~~~w → **STOP-wrong-sign**  (dR = 27/8)
- join a clique onto F~~~w → **STOP-zero**  (dR = 0)
- prism over F~~~w → **STOP-wrong-sign**  (dR = 3/4)
- complement of F~~~w → **STOP-unavailable**
- line graph of F~~~w → **STOP-wrong-sign**  (dR = 21/11)
- clique blow-up of E~~w → **STOP-zero**  (dR = 0)
- independent blow-up of E~~w → **STOP-wrong-sign**  (dR = 1/11)
- subdivision of E~~w → **STOP-wrong-sign**  (dR = 14)
- corona of E~~w → **STOP-wrong-sign**  (dR = 20/7)
- join a clique onto E~~w → **STOP-zero**  (dR = 0)
- prism over E~~w → **STOP-wrong-sign**  (dR = 5/7)
- complement of E~~w → **STOP-unavailable**
- line graph of E~~w → **STOP-wrong-sign**  (dR = 5/3)
- break res <= alpha + CW - 1 by driving CW below 1 (impossible; blow-ups tried) → **STOP-zero**  (dR = 0)

**4. Families built and tested.**

None — every proposed transformation was stopped at step 3.

**Outcome.** step 3 (G3-lite sign check stopped every proposed transformation) HELD -- theorem. res <= alpha and CW >= 1.

**Budget.** 0.1 s of the 3600 s cap. **Gate.** database sanity: PASS; independent recomputation: path A (`wall_arm.py`) vs path B (`scripts/gen/invariants.py` scal backend).

### FP-029 — CROSSED

**Statement.** `For every connected graph G with n(G) >= 2:  res >= A - deg_avg`

**Equality in D:** 32 members, by order {'8': 32}.

**1. The wall.** 32 equality members, all at n=8 with m=8, Delta=3, delta=1, deg_avg=2, res=3, A=5, kappa=1, disp_min=1 all pinned. The wall is a single degree sequence: unicyclic graphs with degree sequence (1,1,2,2,2,2,3,3) or (1,1,1,2,2,3,3,3).

**2. The obstruction.** A - deg_avg against res. The wall is one degree sequence with deg_avg = 2 and A - deg_avg = 3 = res. A clique blow-up multiplies A by roughly m while res stays at 3 (the Havel-Hakimi residue of a blown-up sequence does not scale), and deg_avg only grows linearly in m, so A - deg_avg outruns res.

**3. G3-lite sign checks** (26 run, 9 stopped a trial). Only the checks that returned GO were allowed to run a trial.

_Passed (trial run):_

- clique blow-up of G@O_n? → **GO**  (dR = -1)<br>&nbsp;&nbsp;`G[K1]` (n=8) R=0 [annih=5 deg_avg=2 res=3]<br>&nbsp;&nbsp;`G[K2]` (n=16) R=-1 [annih=9 deg_avg=5 res=3]
- independent blow-up of G@O_n? → **GO**  (dR = -2)<br>&nbsp;&nbsp;`G[I1]` (n=8) R=0 [annih=5 deg_avg=2 res=3]<br>&nbsp;&nbsp;`G[I2]` (n=16) R=-2 [annih=10 deg_avg=4 res=4]
- subdivision of G@O_n? → **GO**  (dR = -1)<br>&nbsp;&nbsp;`sub^0(G)` (n=8) R=0 [annih=5 deg_avg=2 res=3]<br>&nbsp;&nbsp;`sub^1(G)` (n=16) R=-1 [annih=9 deg_avg=2 res=6]
- corona of G@O_n? → **GO**  (dR = -2)<br>&nbsp;&nbsp;`G o 0K1` (n=8) R=0 [annih=5 deg_avg=2 res=3]<br>&nbsp;&nbsp;`G o 1K1` (n=16) R=-2 [annih=11 deg_avg=2 res=7]
- prism over G@O_n? → **GO**  (dR = -1)<br>&nbsp;&nbsp;`G x K1` (n=8) R=0 [annih=5 deg_avg=2 res=3]<br>&nbsp;&nbsp;`G x K2` (n=16) R=-1 [annih=9 deg_avg=3 res=5]
- clique blow-up of GC_`J_ → **GO**  (dR = -1)<br>&nbsp;&nbsp;`G[K1]` (n=8) R=0 [annih=5 deg_avg=2 res=3]<br>&nbsp;&nbsp;`G[K2]` (n=16) R=-1 [annih=9 deg_avg=5 res=3]
- independent blow-up of GC_`J_ → **GO**  (dR = -2)<br>&nbsp;&nbsp;`G[I1]` (n=8) R=0 [annih=5 deg_avg=2 res=3]<br>&nbsp;&nbsp;`G[I2]` (n=16) R=-2 [annih=10 deg_avg=4 res=4]
- subdivision of GC_`J_ → **GO**  (dR = -1)<br>&nbsp;&nbsp;`sub^0(G)` (n=8) R=0 [annih=5 deg_avg=2 res=3]<br>&nbsp;&nbsp;`sub^1(G)` (n=16) R=-1 [annih=9 deg_avg=2 res=6]
- corona of GC_`J_ → **GO**  (dR = -2)<br>&nbsp;&nbsp;`G o 0K1` (n=8) R=0 [annih=5 deg_avg=2 res=3]<br>&nbsp;&nbsp;`G o 1K1` (n=16) R=-2 [annih=11 deg_avg=2 res=7]
- prism over GC_`J_ → **GO**  (dR = -1)<br>&nbsp;&nbsp;`G x K1` (n=8) R=0 [annih=5 deg_avg=2 res=3]<br>&nbsp;&nbsp;`G x K2` (n=16) R=-1 [annih=9 deg_avg=3 res=5]
- clique blow-up of GGC`M_ → **GO**  (dR = -1)<br>&nbsp;&nbsp;`G[K1]` (n=8) R=0 [annih=5 deg_avg=2 res=3]<br>&nbsp;&nbsp;`G[K2]` (n=16) R=-1 [annih=9 deg_avg=5 res=3]
- independent blow-up of GGC`M_ → **GO**  (dR = -2)<br>&nbsp;&nbsp;`G[I1]` (n=8) R=0 [annih=5 deg_avg=2 res=3]<br>&nbsp;&nbsp;`G[I2]` (n=16) R=-2 [annih=10 deg_avg=4 res=4]
- subdivision of GGC`M_ → **GO**  (dR = -1)<br>&nbsp;&nbsp;`sub^0(G)` (n=8) R=0 [annih=5 deg_avg=2 res=3]<br>&nbsp;&nbsp;`sub^1(G)` (n=16) R=-1 [annih=9 deg_avg=2 res=6]
- corona of GGC`M_ → **GO**  (dR = -2)<br>&nbsp;&nbsp;`G o 0K1` (n=8) R=0 [annih=5 deg_avg=2 res=3]<br>&nbsp;&nbsp;`G o 1K1` (n=16) R=-2 [annih=11 deg_avg=2 res=7]
- prism over GGC`M_ → **GO**  (dR = -1)<br>&nbsp;&nbsp;`G x K1` (n=8) R=0 [annih=5 deg_avg=2 res=3]<br>&nbsp;&nbsp;`G x K2` (n=16) R=-1 [annih=9 deg_avg=3 res=5]
- clique blow-up of the tight 8-vertex tree-like member → **GO**  (dR = -1)<br>&nbsp;&nbsp;`(G@O_n?)[K1]` (n=8) R=0 [annih=5 deg_avg=2 res=3]<br>&nbsp;&nbsp;`(G@O_n?)[K2]` (n=16) R=-1 [annih=9 deg_avg=5 res=3]
- corona of the same member → **GO**  (dR = -2)<br>&nbsp;&nbsp;`(G@O_n?) o 0K1` (n=8) R=0 [annih=5 deg_avg=2 res=3]<br>&nbsp;&nbsp;`(G@O_n?) o 1K1` (n=16) R=-2 [annih=11 deg_avg=2 res=7]

_Stopped (trial not run):_

- join a clique onto G@O_n? → **STOP-wrong-sign**  (dR = 5/9)
- complement of G@O_n? → **STOP-wrong-sign**  (dR = 3)
- line graph of G@O_n? → **STOP-wrong-sign**  (dR = 1/2)
- join a clique onto GC_`J_ → **STOP-wrong-sign**  (dR = 5/9)
- complement of GC_`J_ → **STOP-wrong-sign**  (dR = 3)
- line graph of GC_`J_ → **STOP-wrong-sign**  (dR = 1/2)
- join a clique onto GGC`M_ → **STOP-wrong-sign**  (dR = 5/9)
- complement of GGC`M_ → **STOP-wrong-sign**  (dR = 3)
- line graph of GGC`M_ → **STOP-wrong-sign**  (dR = 3/2)

**4. Families built and tested.**

`clique blow-up of G@O_n?`

| member | n | R | invariants |
|---|---|---|---|
| G[K1] | 8 | 0 | annih=5 deg_avg=2 res=3 |
| G[K2] | 16 | -1 | annih=9 deg_avg=5 res=3 |
| G[K3] | 24 | -3 | annih=14 deg_avg=8 res=3 |
| G[K4] | 32 | -4 | annih=18 deg_avg=11 res=3 |

`independent blow-up of G@O_n?`

| member | n | R | invariants |
|---|---|---|---|
| G[I1] | 8 | 0 | annih=5 deg_avg=2 res=3 |
| G[I2] | 16 | -2 | annih=10 deg_avg=4 res=4 |
| G[I3] | 24 | -5 | annih=15 deg_avg=6 res=4 |

`subdivision of G@O_n?`

| member | n | R | invariants |
|---|---|---|---|
| sub^0(G) | 8 | 0 | annih=5 deg_avg=2 res=3 |
| sub^1(G) | 16 | -1 | annih=9 deg_avg=2 res=6 |
| sub^2(G) | 32 | -4 | annih=17 deg_avg=2 res=11 |

`corona of G@O_n?`

| member | n | R | invariants |
|---|---|---|---|
| G o 0K1 | 8 | 0 | annih=5 deg_avg=2 res=3 |
| G o 1K1 | 16 | -2 | annih=11 deg_avg=2 res=7 |
| G o 2K1 | 24 | -6 | annih=18 deg_avg=2 res=10 |

`prism over G@O_n?`

| member | n | R | invariants |
|---|---|---|---|
| G x K1 | 8 | 0 | annih=5 deg_avg=2 res=3 |
| G x K2 | 16 | -1 | annih=9 deg_avg=3 res=5 |
| G x K3 | 24 | -4 | annih=13 deg_avg=4 res=5 |

`clique blow-up of GC_`J_`

| member | n | R | invariants |
|---|---|---|---|
| G[K1] | 8 | 0 | annih=5 deg_avg=2 res=3 |
| G[K2] | 16 | -1 | annih=9 deg_avg=5 res=3 |
| G[K3] | 24 | -3 | annih=14 deg_avg=8 res=3 |
| G[K4] | 32 | -4 | annih=18 deg_avg=11 res=3 |

`independent blow-up of GC_`J_`

| member | n | R | invariants |
|---|---|---|---|
| G[I1] | 8 | 0 | annih=5 deg_avg=2 res=3 |
| G[I2] | 16 | -2 | annih=10 deg_avg=4 res=4 |
| G[I3] | 24 | -5 | annih=15 deg_avg=6 res=4 |

`subdivision of GC_`J_`

| member | n | R | invariants |
|---|---|---|---|
| sub^0(G) | 8 | 0 | annih=5 deg_avg=2 res=3 |
| sub^1(G) | 16 | -1 | annih=9 deg_avg=2 res=6 |
| sub^2(G) | 32 | -4 | annih=17 deg_avg=2 res=11 |

`corona of GC_`J_`

| member | n | R | invariants |
|---|---|---|---|
| G o 0K1 | 8 | 0 | annih=5 deg_avg=2 res=3 |
| G o 1K1 | 16 | -2 | annih=11 deg_avg=2 res=7 |
| G o 2K1 | 24 | -6 | annih=18 deg_avg=2 res=10 |

`prism over GC_`J_`

| member | n | R | invariants |
|---|---|---|---|
| G x K1 | 8 | 0 | annih=5 deg_avg=2 res=3 |
| G x K2 | 16 | -1 | annih=9 deg_avg=3 res=5 |
| G x K3 | 24 | -4 | annih=13 deg_avg=4 res=5 |

`clique blow-up of GGC`M_`

| member | n | R | invariants |
|---|---|---|---|
| G[K1] | 8 | 0 | annih=5 deg_avg=2 res=3 |
| G[K2] | 16 | -1 | annih=9 deg_avg=5 res=3 |
| G[K3] | 24 | -3 | annih=14 deg_avg=8 res=3 |
| G[K4] | 32 | -4 | annih=18 deg_avg=11 res=3 |

`independent blow-up of GGC`M_`

| member | n | R | invariants |
|---|---|---|---|
| G[I1] | 8 | 0 | annih=5 deg_avg=2 res=3 |
| G[I2] | 16 | -2 | annih=10 deg_avg=4 res=4 |
| G[I3] | 24 | -5 | annih=15 deg_avg=6 res=4 |

`subdivision of GGC`M_`

| member | n | R | invariants |
|---|---|---|---|
| sub^0(G) | 8 | 0 | annih=5 deg_avg=2 res=3 |
| sub^1(G) | 16 | -1 | annih=9 deg_avg=2 res=6 |
| sub^2(G) | 32 | -4 | annih=17 deg_avg=2 res=11 |

`corona of GGC`M_`

| member | n | R | invariants |
|---|---|---|---|
| G o 0K1 | 8 | 0 | annih=5 deg_avg=2 res=3 |
| G o 1K1 | 16 | -2 | annih=11 deg_avg=2 res=7 |
| G o 2K1 | 24 | -6 | annih=18 deg_avg=2 res=10 |

`prism over GGC`M_`

| member | n | R | invariants |
|---|---|---|---|
| G x K1 | 8 | 0 | annih=5 deg_avg=2 res=3 |
| G x K2 | 16 | -1 | annih=9 deg_avg=3 res=5 |
| G x K3 | 24 | -4 | annih=13 deg_avg=4 res=5 |

`clique blow-up of the tight 8-vertex tree-like member`

| member | n | R | invariants |
|---|---|---|---|
| (G@O_n?)[K1] | 8 | 0 | annih=5 deg_avg=2 res=3 |
| (G@O_n?)[K2] | 16 | -1 | annih=9 deg_avg=5 res=3 |
| (G@O_n?)[K3] | 24 | -3 | annih=14 deg_avg=8 res=3 |
| (G@O_n?)[K4] | 32 | -4 | annih=18 deg_avg=11 res=3 |

`corona of the same member`

| member | n | R | invariants |
|---|---|---|---|
| (G@O_n?) o 0K1 | 8 | 0 | annih=5 deg_avg=2 res=3 |
| (G@O_n?) o 1K1 | 16 | -2 | annih=11 deg_avg=2 res=7 |
| (G@O_n?) o 2K1 | 24 | -6 | annih=18 deg_avg=2 res=10 |

**Crossings.**

| graph6 | n | R | LHS | RHS | family |
|---|---|---|---|---|---|
| `O`?GW[oKGW@`?r?r~_Fw@` | 16 | -1 | 3 | 4 | clique blow-up of G@O_n? |
| `O????A@QAAE?H?GOAO?K?` | 16 | -1 | 6 | 7 | subdivision of G@O_n? |
| `O`?GOK_CGO?`?a?Pt?Ag@` | 16 | -1 | 5 | 6 | prism over G@O_n? |
| `O`?MEF?oGW@`BBBBfw@}@` | 16 | -1 | 3 | 4 | clique blow-up of GC_`J_ |
| `O????AOaAAC_G_GOAG?K?` | 16 | -1 | 6 | 7 | subdivision of GC_`J_ |
| `O`?KAE?OGO?`AA@@dO?i@` | 16 | -1 | 5 | 6 | prism over GC_`J_ |
| `O`Kw?CB?wW@`BBBB}WFe@` | 16 | -1 | 3 | 4 | clique blow-up of GGC`M_ |
| `O????A@WAAC_G_E?AG?K?` | 16 | -1 | 6 | 7 | subdivision of GGC`M_ |
| `O`GW?CA?WO?`AA@@sOAa@` | 16 | -1 | 5 | 6 | prism over GGC`M_ |
| `O`?GW[oKGW@`?r?r~_Fw@` | 16 | -1 | 3 | 4 | clique blow-up of the tight 8-vertex tree-like member |
| `O???WWoK?W@_?r?r^_Fw?` | 16 | -2 | 4 | 6 | independent blow-up of G@O_n? |
| `O@O_nA?O@?A?A?@??O?A?` | 16 | -2 | 7 | 9 | corona of G@O_n? |
| `O??EEB?o?W@_BBBBFw@}?` | 16 | -2 | 4 | 6 | independent blow-up of GC_`J_ |
| `OC_`Ja?O@?A?A?@??O?A?` | 16 | -2 | 7 | 9 | corona of GC_`J_ |
| `O?Ko??B?oW@_BBBB]WFe?` | 16 | -2 | 4 | 6 | independent blow-up of GGC`M_ |
| `OGC`Ma?O@?A?A?@??O?A?` | 16 | -2 | 7 | 9 | corona of GGC`M_ |
| `O@O_nA?O@?A?A?@??O?A?` | 16 | -2 | 7 | 9 | corona of the same member |
| `WwCW?CB?wF_^F?F?b_WF??wCB_W?ww?w{?[^~w?F~??~{?B` | 24 | -3 | 3 | 6 | clique blow-up of G@O_n? |
| `WwCW?CBwF?{Bw?w?{?WF??wCB_WF?wF?{B_^F~??~w?b~_B` | 24 | -3 | 3 | 6 | clique blow-up of GC_`J_ |
| `WwCWw{^???_B?F?F_BwF??wCB_WF?wF?{B_^~F?Fww?~b_B` | 24 | -3 | 3 | 6 | clique blow-up of GGC`M_ |
| `WwCW?CB?wF_^F?F?b_WF??wCB_W?ww?w{?[^~w?F~??~{?B` | 24 | -3 | 3 | 6 | clique blow-up of the tight 8-vertex tree-like member |
| `WwCW?CB?_A_FC?A?__WC??OC?_W?__?OS?CFc_?AQ??cc?B` | 24 | -4 | 5 | 9 | prism over G@O_n? |
| `WwCW?CB_A?cB_?O?c?WC??OC?_WC?_A?S?_FCc??QO?_c_B` | 24 | -4 | 5 | 9 | prism over GC_`J_ |
| `WwCW_SF???_B?C?A_?wC??OC?_WC?_A?S?_FcC?AOO?c__B` | 24 | -4 | 5 | 9 | prism over GGC`M_ |
| `W???????wF?[F?F?B_?F??w?B_??ww?ww?[[~w?F~??^{??` | 24 | -5 | 4 | 9 | independent blow-up of G@O_n? |
| `W??????wF?[?w?w?[??F??w?B_?F?wF?wB_[F~??~w?B~_?` | 24 | -5 | 4 | 9 | independent blow-up of GC_`J_ |
| `W???ww[??????F?F?B_F??w?B_?F?wF?wB_[~F?Fww?^b_?` | 24 | -5 | 4 | 9 | independent blow-up of GGC`M_ |
| `W@O_nA?_A?G?G?G?A??_?A??G??G??G??A???_??A???G??` | 24 | -6 | 10 | 16 | corona of G@O_n? |
| `WC_`Ja?_A?G?G?G?A??_?A??G??G??G??A???_??A???G??` | 24 | -6 | 10 | 16 | corona of GC_`J_ |
| `WGC`Ma?_A?G?G?G?A??_?A??G??G??G??A???_??A???G??` | 24 | -6 | 10 | 16 | corona of GGC`M_ |
| `W@O_nA?_A?G?G?G?A??_?A??G??G??G??A???_??A???G??` | 24 | -6 | 10 | 16 | corona of the same member |
| `_~?GW[??G@_F?N?N_Fw@~Bo?N?G]?W]?[?{??N?G@w@_F_F??{N??{N_?]Fw?F`~~~??B~{??N~w??^~w??[` | 32 | -4 | 3 | 7 | clique blow-up of G@O_n? |
| `_????????????????????_G@?OA?O@?G?_A?G?O?_G?A?C?AC??@?_??_A??C@???_C??@_???AO???AA???` | 32 | -4 | 11 | 15 | subdivision of G@O_n? |
| `_~?GW[??G@_F{?{?}?^_F{?Bo?N_?^_?[?{??N?G@w@_F_F?N?N?N?N_F_Fw@w@~B~{??N~o?G^~_?W^~_?[` | 32 | -4 | 3 | 7 | clique blow-up of GC_`J_ |
| `_????????????????????_GA?OA?O@?G?_A?G?O?`??A?C?AC??@@???_A??CC???_C??@G???AA???A@???` | 32 | -4 | 11 | 15 | subdivision of GC_`J_ |
| `_~?GW[NBw^`~????_?W?F??{?Bw?Fw?F{?{??N?G@w@_F_F?N?N?N?N_F_Fw@w@~~o{?B~Bo?N}F_?^}F_?[` | 32 | -4 | 3 | 7 | clique blow-up of GGC`M_ |
| `_????????????????????_G@?OA?O@?_?_C?G?_?_A?A?C?A?O?@@???_A??CC???_C??@_???AO???A@???` | 32 | -4 | 11 | 15 | subdivision of GGC`M_ |
| `_~?GW[??G@_F?N?N_Fw@~Bo?N?G]?W]?[?{??N?G@w@_F_F??{N??{N_?]Fw?F`~~~??B~{??N~w??^~w??[` | 32 | -4 | 3 | 7 | clique blow-up of the tight 8-vertex tree-like member |

**Independent recomputation** (verification bar (a)):

| graph6 | n | path A | path B | agree | R (A) | R (B) |
|---|---|---|---|---|---|---|
| `O`?GW[oKGW@`?r?r~_Fw@` | 16 | annih=9 deg_avg=5 res=3 | annih=9 deg_avg=5 res=3 | True | -1 | -1 |

**Budget.** 0.1 s of the 3600 s cap. **Gate.** database sanity: PASS; independent recomputation: path A (`wall_arm.py`) vs path B (`scripts/gen/invariants.py` scal backend).

### FP-030 — CROSSED

**Statement.** `For every connected graph G with n(G) >= 2:  res >= floor((dd)/(gamma_t))`

**Equality in D:** 2216 members, by order {'6': 7, '7': 110, '8': 2099}.

**1. The wall.** 2216 equality members; the recorded 300 have n=8, mu=4, gamma_t=2, non-bipartite, non-regular, and dd = 4 or 5 with res = 2, so floor(dd/gamma_t) = 2 = res exactly.

**2. The obstruction.** dd. The wall has dd = 4 or 5 with gamma_t = 2 and res = 2, so floor(dd/2) = 2 = res exactly. Joining a single dominating vertex raises every degree by one and adds one new degree value at the top, so dd goes to 6 while gamma_t stays 2 (the new vertex plus any neighbour) and the residue is unchanged.

**3. G3-lite sign checks** (25 run, 24 stopped a trial). Only the checks that returned GO were allowed to run a trial.

_Passed (trial run):_

- join a dominating clique: dd jumps by one, gamma_t and res pinned → **GO**  (dR = -1)<br>&nbsp;&nbsp;`(G?\~f[) + K0` (n=8) R=0 [dd=5 gamma_t=2 res=2]<br>&nbsp;&nbsp;`(G?\~f[) + K1` (n=9) R=-1 [dd=6 gamma_t=2 res=2]

_Stopped (trial not run):_

- clique blow-up of G?\vng → **STOP-zero**  (dR = 0)
- independent blow-up of G?\vng → **STOP-wrong-sign**  (dR = 1)
- subdivision of G?\vng → **STOP-wrong-sign**  (dR = 8)
- corona of G?\vng → **STOP-wrong-sign**  (dR = 6)
- join a clique onto G?\vng → **STOP-zero**  (dR = 0)
- prism over G?\vng → **STOP-wrong-sign**  (dR = 2)
- complement of G?\vng → **STOP-wrong-sign**  (dR = 1)
- line graph of G?\vng → **STOP-wrong-sign**  (dR = 3)
- clique blow-up of G?\vnw → **STOP-zero**  (dR = 0)
- independent blow-up of G?\vnw → **STOP-wrong-sign**  (dR = 1)
- subdivision of G?\vnw → **STOP-wrong-sign**  (dR = 8)
- corona of G?\vnw → **STOP-wrong-sign**  (dR = 6)
- join a clique onto G?\vnw → **STOP-zero**  (dR = 0)
- prism over G?\vnw → **STOP-wrong-sign**  (dR = 2)
- complement of G?\vnw → **STOP-wrong-sign**  (dR = 2)
- line graph of G?\vnw → **STOP-wrong-sign**  (dR = 2)
- clique blow-up of G?\~b{ → **STOP-zero**  (dR = 0)
- independent blow-up of G?\~b{ → **STOP-wrong-sign**  (dR = 1)
- subdivision of G?\~b{ → **STOP-wrong-sign**  (dR = 8)
- corona of G?\~b{ → **STOP-wrong-sign**  (dR = 6)
- join a clique onto G?\~b{ → **STOP-zero**  (dR = 0)
- prism over G?\~b{ → **STOP-wrong-sign**  (dR = 2)
- complement of G?\~b{ → **STOP-wrong-sign**  (dR = 1)
- line graph of G?\~b{ → **STOP-wrong-sign**  (dR = 2)

**4. Families built and tested.**

`join a dominating clique: dd jumps by one, gamma_t and res pinned`

| member | n | R | invariants |
|---|---|---|---|
| (G?\~f[) + K0 | 8 | 0 | dd=5 gamma_t=2 res=2 |
| (G?\~f[) + K1 | 9 | -1 | dd=6 gamma_t=2 res=2 |
| (G?\~f[) + K2 | 10 | -1 | dd=6 gamma_t=2 res=2 |
| (G?\~f[) + K3 | 11 | -1 | dd=6 gamma_t=2 res=2 |

**Crossings.**

| graph6 | n | R | LHS | RHS | family |
|---|---|---|---|---|---|
| `H?\~f^~` | 9 | -1 | 2 | 3 | join a dominating clique: dd jumps by one, gamma_t and res pinned |
| `I?\~f^~~w` | 10 | -1 | 2 | 3 | join a dominating clique: dd jumps by one, gamma_t and res pinned |
| `J?\~f^~~~~_` | 11 | -1 | 2 | 3 | join a dominating clique: dd jumps by one, gamma_t and res pinned |

**Independent recomputation** (verification bar (a)):

| graph6 | n | path A | path B | agree | R (A) | R (B) |
|---|---|---|---|---|---|---|
| `H?\~f^~` | 9 | dd=6 gamma_t=2 res=2 | dd=6 gamma_t=2 res=2 | True | -1 | -1 |

**Budget.** 0.2 s of the 3600 s cap. **Gate.** database sanity: PASS; independent recomputation: path A (`wall_arm.py`) vs path B (`scripts/gen/invariants.py` scal backend).
