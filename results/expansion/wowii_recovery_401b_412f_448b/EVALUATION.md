# EVALUATION — recovered wordings 401b / 412f / 448b

Wording recovered from Wayback is IDENTICAL to the published corpus
(see RECOVERY.md), so what follows evaluates *plausible readings* of the
published statements. All arithmetic exact (integers / Fraction).
Gate = DB-SANITY battery: connected atlas graphs n<=7, C5..C9, P7, Petersen,
K3,3, K4,4, K5,5, K7, stars K_{1,n} (n=2..8). A reading failing any gate graph
is a MIS-TRANSCRIPTION-class artifact and cannot be hunted.

## 401b — `gamma_2 <= FLOOR[3*Tdist_max / freq[T_max(v)]]` (open, Jan 2010)

- gamma_2: 2-domination number (def: every vertex in D or adjacent to >=2 in D).
- Tdist_max: maximum transmission. T(v): triangles at v; T_max=max; freq=count.

### Reading R-TRI (literal page semantics: T(v)=#triangles at v; freq[T_max] = #vertices attaining it)

**FAILS DB-SANITY GATE** on 8 graph(s); first witnesses:
- `atlas77`: gamma_2=5 > floor(3*Tdist_max/freq)= 4   [{'Tdist_max': 9, 'T_max': 0, 'freq': 6}]
- `atlas270`: gamma_2=6 > floor(3*Tdist_max/freq)= 4   [{'Tdist_max': 11, 'T_max': 0, 'freq': 7}]
- `K4,4`: gamma_2=4 > floor(3*Tdist_max/freq)= 3   [{'Tdist_max': 10, 'T_max': 0, 'freq': 8}]
- `K5,5`: gamma_2=4 > floor(3*Tdist_max/freq)= 3   [{'Tdist_max': 13, 'T_max': 0, 'freq': 10}]
- `star(1,5)`: gamma_2=5 > floor(3*Tdist_max/freq)= 4   [{'Tdist_max': 9, 'T_max': 0, 'freq': 6}]
- `star(1,6)`: gamma_2=6 > floor(3*Tdist_max/freq)= 4   [{'Tdist_max': 11, 'T_max': 0, 'freq': 7}]

Stars are inside Graffiti.pc's own database => under its own definitions this
reading cannot be what was tested. Verdict: **MIS-TRANSCRIPTION-CLASS**
(typo as published; e.g. plausibly intended freq of a distance quantity or an
inverted fraction) — NOT huntable. No reading of this shape survives.

### Reading R-TD (repair hypothesis: `freq[T_max(v)]` re-read as frequency of the
maximum TRANSMISSION value, i.e. #vertices attaining Tdist_max — motivated by
sibling 401a using Tdist_max/disp_avg)

**FAILS DB-SANITY GATE** on 6 graph(s):
- `atlas270`: gamma_2=6 > 5   [{'Tdist_max': 11, 'freq_of_Tdist_max': 6}]
- `K4,4`: gamma_2=4 > 3   [{'Tdist_max': 10, 'freq_of_Tdist_max': 8}]
- `K5,5`: gamma_2=4 > 3   [{'Tdist_max': 13, 'freq_of_Tdist_max': 10}]
- `star(1,6)`: gamma_2=6 > 5   [{'Tdist_max': 11, 'freq_of_Tdist_max': 6}]
- `star(1,7)`: gamma_2=7 > 5   [{'Tdist_max': 13, 'freq_of_Tdist_max': 7}]
- `star(1,8)`: gamma_2=8 > 5   [{'Tdist_max': 15, 'freq_of_Tdist_max': 8}]


## 412f — `|H| >= mu(G[V-N(P)])`, bipartite case `|H| >= c(G[V-N(P)]) + mu(...)`
(open, Jun 2010; H = union of all MAXIMUM critical independent sets; P = pendants)

Convention knobs evaluated:
- **CONV-LIT** (literal defs-page wording): U in the defining inequality ranges
  over ALL independent subsets *including empty*; critical := argmax deficit
  |S|-|N(S)|; H = union of argmax sets.
- **CONV-NE**: empty set excluded entirely; critical := argmax deficit among
  nonempty independent sets; 'maximum' = maximum-cardinality members.
  Sub-knob NE-ALL: H = union of ALL argmax sets (not just largest).

### Reading CONV-LIT
**FAILS DB-SANITY GATE** on 620 gate graph(s); witnesses:
- `atlas7`: |H|=0 < mu(G[V-N(P)])=1 [alpha_crit=0, best_deficit=0]
- `atlas18`: |H|=0 < mu(G[V-N(P)])=2 [alpha_crit=0, best_deficit=0]
- `atlas38`: |H|=0 < mu(G[V-N(P)])=2 [alpha_crit=0, best_deficit=0]
- `atlas42`: |H|=0 < mu(G[V-N(P)])=2 [alpha_crit=0, best_deficit=0]
- `atlas43`: |H|=0 < mu(G[V-N(P)])=2 [alpha_crit=0, best_deficit=0]
- `atlas47`: |H|=0 < mu(G[V-N(P)])=2 [alpha_crit=0, best_deficit=0]
- `atlas48`: |H|=0 < mu(G[V-N(P)])=2 [alpha_crit=0, best_deficit=0]
- `atlas49`: |H|=0 < mu(G[V-N(P)])=2 [alpha_crit=0, best_deficit=0]
Verdict: **MIS-TRANSCRIPTION-CLASS** under this convention — not huntable.

### Reading CONV-NE
**FAILS DB-SANITY GATE** on 224 gate graph(s); witnesses:
- `atlas142`: |H|=1 < mu(G[V-N(P)])=2 [alpha_crit=1, best_deficit=0]
- `atlas152`: |H|=2 < mu(G[V-N(P)])=3 [alpha_crit=1, best_deficit=-1]
- `atlas153`: |H|=2 < mu(G[V-N(P)])=3 [alpha_crit=1, best_deficit=-1]
- `atlas160`: |H|=1 < mu(G[V-N(P)])=2 [alpha_crit=1, best_deficit=0]
- `atlas165`: |H|=2 < mu(G[V-N(P)])=3 [alpha_crit=1, best_deficit=-1]
- `atlas167`: |H|=2 < mu(G[V-N(P)])=3 [alpha_crit=1, best_deficit=-1]
- `atlas169`: |H|=2 < mu(G[V-N(P)])=3 [alpha_crit=1, best_deficit=-1]
- `atlas171`: |H|=1 < mu(G[V-N(P)])=3 [alpha_crit=1, best_deficit=-1]
Verdict: **MIS-TRANSCRIPTION-CLASS** under this convention — not huntable.


## 448b — `alpha_2(G) <= |V-A| + |E(G[N(S)])| + rho(G)`
(open, Jan 2012; A = min-degree vertices, S = support vertices)

The page does not define `rho` explicitly anywhere in the defs database;
two plausible readings evaluated:
- **RHO-RAD**: rho = radius(G) (Greek-letter match r->rho; rad used elsewhere)
- **RHO-PCOV**: rho = p(G), the path covering number (corpus tagged `p_cov`)
Also cross-checked alpha_2 under the alternate 'induced max degree <= 2'
convention (does not change any verdict below). Hypothesis n > 3.

### Reading RHO-RAD
**FAILS DB-SANITY GATE** on 63 gate graph(s) (n>3); witnesses:
- `atlas13`: alpha_2=3 > |V-A|+|E(G[N(S)])|+rho = 1+0+1 = 2
- `atlas18`: alpha_2=2 > |V-A|+|E(G[N(S)])|+rho = 0+0+1 = 1
- `atlas29`: alpha_2=4 > |V-A|+|E(G[N(S)])|+rho = 1+0+1 = 2
- `atlas38`: alpha_2=3 > |V-A|+|E(G[N(S)])|+rho = 0+0+2 = 2
- `atlas42`: alpha_2=4 > |V-A|+|E(G[N(S)])|+rho = 1+0+1 = 2
- `atlas52`: alpha_2=2 > |V-A|+|E(G[N(S)])|+rho = 0+0+1 = 1
- `atlas77`: alpha_2=5 > |V-A|+|E(G[N(S)])|+rho = 1+0+1 = 2
- `atlas105`: alpha_2=4 > |V-A|+|E(G[N(S)])|+rho = 0+0+3 = 3
Verdict: **MIS-TRANSCRIPTION-CLASS** under this reading — not huntable.

### Reading RHO-PCOV
**FAILS DB-SANITY GATE** on 67 gate graph(s) (n>3); witnesses:
- `atlas16`: alpha_2=2 > |V-A|+|E(G[N(S)])|+rho = 0+0+1 = 1
- `atlas18`: alpha_2=2 > |V-A|+|E(G[N(S)])|+rho = 0+0+1 = 1
- `atlas38`: alpha_2=3 > |V-A|+|E(G[N(S)])|+rho = 0+0+1 = 1
- `atlas42`: alpha_2=4 > |V-A|+|E(G[N(S)])|+rho = 1+0+1 = 2
- `atlas52`: alpha_2=2 > |V-A|+|E(G[N(S)])|+rho = 0+0+1 = 1
- `atlas105`: alpha_2=4 > |V-A|+|E(G[N(S)])|+rho = 0+0+1 = 1
- `atlas126`: alpha_2=4 > |V-A|+|E(G[N(S)])|+rho = 1+0+2 = 3
- `atlas127`: alpha_2=4 > |V-A|+|E(G[N(S)])|+rho = 2+0+1 = 3
Verdict: **MIS-TRANSCRIPTION-CLASS** under this reading — not huntable.

## Independent recomputation of key gate witnesses (second code path)

Every verdict above is GATE-FAILURE (mis-transcription-class), so there is no
KILL_CANDIDATE to escalate. Per protocol step 3 the decisive gate witnesses
were nevertheless re-derived with independent implementations:

- 401b/R-TRI, `star(1,8)` (n=9): gamma_2(ILP)=8 vs floor(3*Tdist_max/freq[T_max]) = floor(3*15/9) = 5 -> violation CONFIRMED
  (nx.triangles T_max=0, freq=9; transmissions [8.0, 15.0],
   Tdist_max=15 attained by 8 vertices)
- 401b/R-TD, `star(1,8)`: gamma_2=8 vs floor(3*Tdist_max/freq_of_Tdist_max) = floor(45/8) = 5 -> violation CONFIRMED
- 401b/R-TD, `K5,5`: gamma_2(ILP)=4 vs floor(3*Tdist_max/freq_of_Tdist_max)=floor(3*13/10)=3 -> violation CONFIRMED (4 > 3)
- 412f/CONV-LIT, `K3`: independent sets {},{v1},{v2},{v3}; deficits 0,-1,-1,-1.
  Unique argmax = empty set => H = empty, |H|=0 < mu(K3)=1 -> violation CONFIRMED
- 412f/CONV-NE, `atlas152` (graph6 EhNG): best nonempty deficit=-1,
  argmax sets=[(0,), (3,)], max-cardinality union |H|=2 < mu(G)=3
  -> violation CONFIRMED (hand-checked: all pairs have deficit -2, singles -1)
- 448b/RHO-RAD, `star(1,6)`: alpha_2(brute)=6, alpha_2(ILP)=6;
  RHS = 1+0+radius(1) = 2 -> violation CONFIRMED
- 448b/RHO-PCOV, `star(1,6)`: passes (RHS=1+0+p=7 >= 7) BUT `K5,5`: 
  alpha_2(brute)=5, alpha_2(ILP)=5; p(K5,5)=1 ->
  RHS = 0+0+1 = 1 < 5 -> violation CONFIRMED

All recomputations agree with the primary runs (different algorithms: ILP vs
brute force, networkx triangles/floyd-warshall vs hand BFS sums).

## Bottom line

| entry | wording recovered differs from corpus? | readings evaluated | verdict per reading |
|---|---|---|---|
| 401b | **NO** (byte-identical since 2010-08 capture) | R-TRI (literal), R-TD (freq=Tdist_max frequency) | both **FAIL DB-SANITY GATE** (stars, K4,4/K5,5) -> MIS-TRANSCRIPTION-CLASS |
| 412f | **NO** (byte-identical since 2010-08 capture) | CONV-LIT (defs-page literal), CONV-NE (nonempty convention) | both **FAIL DB-SANITY GATE** (LIT: K3 among 620 failures, H=empty; NE: atlas152 etc., 224 graphs) -> MIS-TRANSCRIPTION-CLASS |
| 448b | **NO** (byte-identical since first capture 2016-10) | RHO-RAD (rho=radius), RHO-PCOV (rho=path cover) | both **FAIL DB-SANITY GATE** (stars resp. K4,4/K5,5) -> MIS-TRANSCRIPTION-CLASS |

**No KILL_CANDIDATE. Nothing becomes huntable**: the Wayback recovery proves
the published wording is the original wording, and under every plausible
reading of that wording the statements are violated inside Graffiti.pc's own
verification database (stars / K3 / complete bipartite graphs / small atlas
graphs). These three entries join #97 as DeLaVina's own published typos, not
transcription damage. Campaign action: none beyond documentation.
