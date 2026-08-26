
## batch appended 2026-08-26 06:52:41

| id | verdict | vio | hold | bracket | premise_false | undef | tag |
|---|---|---|---|---|---|---|---|
| 100 | HOLDS | 0 | 50 | 0 | 0 | 0 |  |
| 103 | HOLDS_PARTIAL | 0 | 30 | 0 | 0 | 20 | EXTERNALLY_RESOLVED |
| 108 | HOLDS_PARTIAL | 0 | 43 | 0 | 0 | 7 |  |
| 111 | VIOLATED_CANDIDATE | 116 | 84 | 0 | 0 | 0 |  |
| 133 | HOLDS_PARTIAL | 0 | 40 | 0 | 0 | 10 |  |
| 141 | HOLDS_PARTIAL | 0 | 49 | 0 | 0 | 1 | EXTERNALLY_RESOLVED |
| 142 | BRACKET | 0 | 84 | 14 | 0 | 2 |  |
| 144 | BRACKET | 0 | 90 | 8 | 0 | 2 |  |
| 145 | BRACKET | 0 | 79 | 7 | 0 | 0 |  |
| 146 | BRACKET | 0 | 86 | 14 | 0 | 0 | EXTERNALLY_RESOLVED |

### id 111
statement: If G is a simple connected graph, then α(G) ≤ CEIL[1 + |N(S)|* ( average of λ(v) - 1)], where S is the set of maximum degree vertices of the complement of the graph G the neighborhood is taken in the 

- [VIO] C7[K3] reading#0: reading A: alpha <= ceil(1 + |N_comp(S_comp)|*(lambda_avg_G-1)) :: LHS=3 > RHS=1
- [VIO] C7[K3] reading#2: reading C: open N_comp(S_comp), lambda_avg of COMPLEMENT :: LHS=3 > RHS=1
- [VIO] C9[K3] reading#0: reading A: alpha <= ceil(1 + |N_comp(S_comp)|*(lambda_avg_G-1)) :: LHS=4 > RHS=1
- [VIO] C9[K3] reading#2: reading C: open N_comp(S_comp), lambda_avg of COMPLEMENT :: LHS=4 > RHS=1
- [VIO] CMP(2) reading#0: reading A: alpha <= ceil(1 + |N_comp(S_comp)|*(lambda_avg_G-1)) :: LHS=2 > RHS=1
- [VIO] CMP(2) reading#2: reading C: open N_comp(S_comp), lambda_avg of COMPLEMENT :: LHS=2 > RHS=1
- [VIO] CMP(2) reading#3: reading D: closed N_comp[S_comp], lambda_avg of COMPLEMENT :: LHS=2 > RHS=1
- [VIO] CMP(3) reading#0: reading A: alpha <= ceil(1 + |N_comp(S_comp)|*(lambda_avg_G-1)) :: LHS=2 > RHS=1
- [VIO] CMP(3) reading#2: reading C: open N_comp(S_comp), lambda_avg of COMPLEMENT :: LHS=2 > RHS=1
- [VIO] CMP(3) reading#3: reading D: closed N_comp[S_comp], lambda_avg of COMPLEMENT :: LHS=2 > RHS=1
- [VIO] CMP(4) reading#0: reading A: alpha <= ceil(1 + |N_comp(S_comp)|*(lambda_avg_G-1)) :: LHS=2 > RHS=1
- [VIO] CMP(4) reading#2: reading C: open N_comp(S_comp), lambda_avg of COMPLEMENT :: LHS=2 > RHS=1
- [VIO] CMP(4) reading#3: reading D: closed N_comp[S_comp], lambda_avg of COMPLEMENT :: LHS=2 > RHS=1
- [VIO] CMP(5) reading#0: reading A: alpha <= ceil(1 + |N_comp(S_comp)|*(lambda_avg_G-1)) :: LHS=2 > RHS=1
- [VIO] CMP(5) reading#2: reading C: open N_comp(S_comp), lambda_avg of COMPLEMENT :: LHS=2 > RHS=1
- [VIO] CMP(5) reading#3: reading D: closed N_comp[S_comp], lambda_avg of COMPLEMENT :: LHS=2 > RHS=1
- [VIO] CMP(6) reading#0: reading A: alpha <= ceil(1 + |N_comp(S_comp)|*(lambda_avg_G-1)) :: LHS=2 > RHS=1
- [VIO] CMP(6) reading#2: reading C: open N_comp(S_comp), lambda_avg of COMPLEMENT :: LHS=2 > RHS=1
- [VIO] CMP(6) reading#3: reading D: closed N_comp[S_comp], lambda_avg of COMPLEMENT :: LHS=2 > RHS=1
- [VIO] CMP(7) reading#0: reading A: alpha <= ceil(1 + |N_comp(S_comp)|*(lambda_avg_G-1)) :: LHS=2 > RHS=1
- [VIO] CMP(7) reading#2: reading C: open N_comp(S_comp), lambda_avg of COMPLEMENT :: LHS=2 > RHS=1
- [VIO] CMP(7) reading#3: reading D: closed N_comp[S_comp], lambda_avg of COMPLEMENT :: LHS=2 > RHS=1
- [VIO] CMP(8) reading#0: reading A: alpha <= ceil(1 + |N_comp(S_comp)|*(lambda_avg_G-1)) :: LHS=2 > RHS=1
- [VIO] CMP(8) reading#2: reading C: open N_comp(S_comp), lambda_avg of COMPLEMENT :: LHS=2 > RHS=1
- [VIO] CMP(8) reading#3: reading D: closed N_comp[S_comp], lambda_avg of COMPLEMENT :: LHS=2 > RHS=1
- [VIO] CP(2) reading#0: reading A: alpha <= ceil(1 + |N_comp(S_comp)|*(lambda_avg_G-1)) :: LHS=2 > RHS=1
- [VIO] CP(2) reading#2: reading C: open N_comp(S_comp), lambda_avg of COMPLEMENT :: LHS=2 > RHS=1
- [VIO] CP(2) reading#3: reading D: closed N_comp[S_comp], lambda_avg of COMPLEMENT :: LHS=2 > RHS=1
- [VIO] CP(3) reading#0: reading A: alpha <= ceil(1 + |N_comp(S_comp)|*(lambda_avg_G-1)) :: LHS=2 > RHS=1
- [VIO] CP(3) reading#2: reading C: open N_comp(S_comp), lambda_avg of COMPLEMENT :: LHS=2 > RHS=1
- [VIO] CP(3) reading#3: reading D: closed N_comp[S_comp], lambda_avg of COMPLEMENT :: LHS=2 > RHS=1
- [VIO] CP(4) reading#0: reading A: alpha <= ceil(1 + |N_comp(S_comp)|*(lambda_avg_G-1)) :: LHS=2 > RHS=1
- [VIO] CP(4) reading#2: reading C: open N_comp(S_comp), lambda_avg of COMPLEMENT :: LHS=2 > RHS=1
- [VIO] CP(4) reading#3: reading D: closed N_comp[S_comp], lambda_avg of COMPLEMENT :: LHS=2 > RHS=1
- [VIO] CP(5) reading#0: reading A: alpha <= ceil(1 + |N_comp(S_comp)|*(lambda_avg_G-1)) :: LHS=2 > RHS=1
- [VIO] CP(5) reading#2: reading C: open N_comp(S_comp), lambda_avg of COMPLEMENT :: LHS=2 > RHS=1
- [VIO] CP(5) reading#3: reading D: closed N_comp[S_comp], lambda_avg of COMPLEMENT :: LHS=2 > RHS=1
- [VIO] CP(6) reading#0: reading A: alpha <= ceil(1 + |N_comp(S_comp)|*(lambda_avg_G-1)) :: LHS=2 > RHS=1
- [VIO] CP(6) reading#2: reading C: open N_comp(S_comp), lambda_avg of COMPLEMENT :: LHS=2 > RHS=1
- [VIO] CP(6) reading#3: reading D: closed N_comp[S_comp], lambda_avg of COMPLEMENT :: LHS=2 > RHS=1

### id 142
statement: If G is a simple connected graph, then tree(G) ≥ (2/3)*girth + ecc(B)

- [BRACKET] CMP(3) reading#0: tree >= (2/3)girth + ecc(B), ecc(B)=diam (members all diametral) :: LHS(lb)=3 < RHS(exact)=4; bounds insufficient
- [BRACKET] CMP(4) reading#0: tree >= (2/3)girth + ecc(B), ecc(B)=diam (members all diametral) :: LHS(lb)=3 < RHS(exact)=4; bounds insufficient
- [BRACKET] CMP(5) reading#0: tree >= (2/3)girth + ecc(B), ecc(B)=diam (members all diametral) :: LHS(lb)=3 < RHS(exact)=4; bounds insufficient
- [BRACKET] CMP(6) reading#0: tree >= (2/3)girth + ecc(B), ecc(B)=diam (members all diametral) :: LHS(lb)=3 < RHS(exact)=4; bounds insufficient
- [BRACKET] CMP(7) reading#0: tree >= (2/3)girth + ecc(B), ecc(B)=diam (members all diametral) :: LHS(lb)=3 < RHS(exact)=4; bounds insufficient
- [BRACKET] CMP(8) reading#0: tree >= (2/3)girth + ecc(B), ecc(B)=diam (members all diametral) :: LHS(lb)=3 < RHS(exact)=4; bounds insufficient
- [BRACKET] CP(2) reading#0: tree >= (2/3)girth + ecc(B), ecc(B)=diam (members all diametral) :: LHS(lb)=3 < RHS(exact)=14/3; bounds insufficient
- [BRACKET] CP(3) reading#0: tree >= (2/3)girth + ecc(B), ecc(B)=diam (members all diametral) :: LHS(lb)=3 < RHS(exact)=4; bounds insufficient
- [BRACKET] CP(4) reading#0: tree >= (2/3)girth + ecc(B), ecc(B)=diam (members all diametral) :: LHS(lb)=3 < RHS(exact)=4; bounds insufficient
- [BRACKET] CP(5) reading#0: tree >= (2/3)girth + ecc(B), ecc(B)=diam (members all diametral) :: LHS(lb)=3 < RHS(exact)=4; bounds insufficient
- [BRACKET] CP(6) reading#0: tree >= (2/3)girth + ecc(B), ecc(B)=diam (members all diametral) :: LHS(lb)=3 < RHS(exact)=4; bounds insufficient
- [BRACKET] CP(7) reading#0: tree >= (2/3)girth + ecc(B), ecc(B)=diam (members all diametral) :: LHS(lb)=3 < RHS(exact)=4; bounds insufficient
- [BRACKET] CP(8) reading#0: tree >= (2/3)girth + ecc(B), ecc(B)=diam (members all diametral) :: LHS(lb)=3 < RHS(exact)=4; bounds insufficient
- [BRACKET] K(3,3) reading#0: tree >= (2/3)girth + ecc(B), ecc(B)=diam (members all diametral) :: LHS(lb)=4 < RHS(exact)=14/3; bounds insufficient

### id 144
statement: If G is a simple connected graph, then tree(G) ≥ girth -1 + ecc(Centers)

- [BRACKET] CP(2) reading#0: tree >= girth - 1 + ecc(C) members (=radius) :: LHS(lb)=3 < RHS(exact)=5; bounds insufficient
- [BRACKET] CP(3) reading#0: tree >= girth - 1 + ecc(C) members (=radius) :: LHS(lb)=3 < RHS(exact)=4; bounds insufficient
- [BRACKET] CP(4) reading#0: tree >= girth - 1 + ecc(C) members (=radius) :: LHS(lb)=3 < RHS(exact)=4; bounds insufficient
- [BRACKET] CP(5) reading#0: tree >= girth - 1 + ecc(C) members (=radius) :: LHS(lb)=3 < RHS(exact)=4; bounds insufficient
- [BRACKET] CP(6) reading#0: tree >= girth - 1 + ecc(C) members (=radius) :: LHS(lb)=3 < RHS(exact)=4; bounds insufficient
- [BRACKET] CP(7) reading#0: tree >= girth - 1 + ecc(C) members (=radius) :: LHS(lb)=3 < RHS(exact)=4; bounds insufficient
- [BRACKET] CP(8) reading#0: tree >= girth - 1 + ecc(C) members (=radius) :: LHS(lb)=3 < RHS(exact)=4; bounds insufficient
- [BRACKET] K(3,3) reading#0: tree >= girth - 1 + ecc(C) members (=radius) :: LHS(lb)=4 < RHS(exact)=5; bounds insufficient

### id 145
statement: If G is a simple connected graph, then tree(G) ≥ 2*ecc(B)/ λ_min( bar(G) )

- [BRACKET] CP(2) reading#0: tree >= 2*ecc(B)/lambda_min(bar), ecc(B)=diam :: LHS(lb)=3 < RHS(exact)=4; bounds insufficient
- [BRACKET] CP(3) reading#0: tree >= 2*ecc(B)/lambda_min(bar), ecc(B)=diam :: LHS(lb)=3 < RHS(exact)=4; bounds insufficient
- [BRACKET] CP(4) reading#0: tree >= 2*ecc(B)/lambda_min(bar), ecc(B)=diam :: LHS(lb)=3 < RHS(exact)=4; bounds insufficient
- [BRACKET] CP(5) reading#0: tree >= 2*ecc(B)/lambda_min(bar), ecc(B)=diam :: LHS(lb)=3 < RHS(exact)=4; bounds insufficient
- [BRACKET] CP(6) reading#0: tree >= 2*ecc(B)/lambda_min(bar), ecc(B)=diam :: LHS(lb)=3 < RHS(exact)=4; bounds insufficient
- [BRACKET] CP(7) reading#0: tree >= 2*ecc(B)/lambda_min(bar), ecc(B)=diam :: LHS(lb)=3 < RHS(exact)=4; bounds insufficient
- [BRACKET] CP(8) reading#0: tree >= 2*ecc(B)/lambda_min(bar), ecc(B)=diam :: LHS(lb)=3 < RHS(exact)=4; bounds insufficient

### id 146
statement: If G is a simple connected graph, then tree(G) ≥ 2*ecc(B)/rad(G^2 )

- [BRACKET] CMP(2) reading#0: tree >= 2*ecc(B)/rad(G^2), ecc(B)=diam :: LHS(lb)=2 < RHS(exact)=4; bounds insufficient
- [BRACKET] CMP(3) reading#0: tree >= 2*ecc(B)/rad(G^2), ecc(B)=diam :: LHS(lb)=3 < RHS(exact)=4; bounds insufficient
- [BRACKET] CMP(4) reading#0: tree >= 2*ecc(B)/rad(G^2), ecc(B)=diam :: LHS(lb)=3 < RHS(exact)=4; bounds insufficient
- [BRACKET] CMP(5) reading#0: tree >= 2*ecc(B)/rad(G^2), ecc(B)=diam :: LHS(lb)=3 < RHS(exact)=4; bounds insufficient
- [BRACKET] CMP(6) reading#0: tree >= 2*ecc(B)/rad(G^2), ecc(B)=diam :: LHS(lb)=3 < RHS(exact)=4; bounds insufficient
- [BRACKET] CMP(7) reading#0: tree >= 2*ecc(B)/rad(G^2), ecc(B)=diam :: LHS(lb)=3 < RHS(exact)=4; bounds insufficient
- [BRACKET] CMP(8) reading#0: tree >= 2*ecc(B)/rad(G^2), ecc(B)=diam :: LHS(lb)=3 < RHS(exact)=4; bounds insufficient
- [BRACKET] CP(2) reading#0: tree >= 2*ecc(B)/rad(G^2), ecc(B)=diam :: LHS(lb)=3 < RHS(exact)=4; bounds insufficient
- [BRACKET] CP(3) reading#0: tree >= 2*ecc(B)/rad(G^2), ecc(B)=diam :: LHS(lb)=3 < RHS(exact)=4; bounds insufficient
- [BRACKET] CP(4) reading#0: tree >= 2*ecc(B)/rad(G^2), ecc(B)=diam :: LHS(lb)=3 < RHS(exact)=4; bounds insufficient
- [BRACKET] CP(5) reading#0: tree >= 2*ecc(B)/rad(G^2), ecc(B)=diam :: LHS(lb)=3 < RHS(exact)=4; bounds insufficient
- [BRACKET] CP(6) reading#0: tree >= 2*ecc(B)/rad(G^2), ecc(B)=diam :: LHS(lb)=3 < RHS(exact)=4; bounds insufficient
- [BRACKET] CP(7) reading#0: tree >= 2*ecc(B)/rad(G^2), ecc(B)=diam :: LHS(lb)=3 < RHS(exact)=4; bounds insufficient
- [BRACKET] CP(8) reading#0: tree >= 2*ecc(B)/rad(G^2), ecc(B)=diam :: LHS(lb)=3 < RHS(exact)=4; bounds insufficient

## batch appended 2026-08-26 06:52:41

| id | verdict | vio | hold | bracket | premise_false | undef | tag |
|---|---|---|---|---|---|---|---|
| 154 | HOLDS | 0 | 50 | 0 | 0 | 0 |  |
| 155 | HOLDS | 0 | 50 | 0 | 0 | 0 |  |
| 157 | HOLDS | 0 | 50 | 0 | 0 | 0 |  |
| 160 | HOLDS | 0 | 50 | 0 | 0 | 0 |  |
| 161 | HOLDS | 0 | 50 | 0 | 0 | 0 |  |
| 162 | HOLDS | 0 | 50 | 0 | 0 | 0 |  |
| 165 | HOLDS | 0 | 50 | 0 | 0 | 0 |  |
| 166 | HOLDS | 0 | 50 | 0 | 0 | 0 |  |
| 169 | HOLDS | 0 | 50 | 0 | 0 | 0 |  |
| 171 | HOLDS | 0 | 50 | 0 | 0 | 0 |  |

## batch appended 2026-08-26 06:52:41

| id | verdict | vio | hold | bracket | premise_false | undef | tag |
|---|---|---|---|---|---|---|---|
| 172 | HOLDS | 0 | 100 | 0 | 0 | 0 |  |
| 174 | BRACKET | 0 | 45 | 4 | 0 | 1 | EXTERNALLY_RESOLVED |
| 176 | BRACKET | 0 | 46 | 3 | 0 | 1 |  |
| 177 | HOLDS_PARTIAL | 0 | 49 | 0 | 0 | 1 |  |
| 178 | HOLDS_PARTIAL | 0 | 49 | 0 | 0 | 1 | EXTERNALLY_RESOLVED |
| 179 | HOLDS_PARTIAL | 0 | 49 | 0 | 0 | 1 |  |
| 180 | BRACKET | 0 | 48 | 1 | 0 | 1 |  |
| 181 | BRACKET | 0 | 47 | 2 | 0 | 1 |  |
| 182 | BRACKET | 0 | 46 | 3 | 0 | 1 |  |
| 183 | BRACKET | 0 | 46 | 3 | 0 | 1 |  |

### id 174
statement: If G is a simple connected graph on at least 2 vertices, then L_s(G) + b(G) ≥ n + maximum of λ(v) -1.

- [BRACKET] Paley(101) reading#0: L_s + b >= n + lambda_max - 1 [externally refuted 2026-07-23] :: LHS(lb)=85 < RHS(exact)=105; bounds insufficient
- [BRACKET] Paley(53) reading#0: L_s + b >= n + lambda_max - 1 [externally refuted 2026-07-23] :: LHS(lb)=55 < RHS(exact)=57; bounds insufficient
- [BRACKET] Paley(73) reading#0: L_s + b >= n + lambda_max - 1 [externally refuted 2026-07-23] :: LHS(lb)=73 < RHS(exact)=77; bounds insufficient
- [BRACKET] T(12) reading#0: L_s + b >= n + lambda_max - 1 [externally refuted 2026-07-23] :: LHS(lb)=45 < RHS(exact)=67; bounds insufficient

### id 176
statement: If G is a simple connected graph on at least 2 vertices, then L_s(G) + b(G) ≥ n + dist_min(M^2 ), where M^2 is the set of vertices of maximum degree of G^2.

- [BRACKET] Paley(101) reading#0: L_s + b >= n + dist_min(M(G^2))  [KILLED 2026-08] :: LHS(lb)=85 < RHS(exact)=102; bounds insufficient
- [BRACKET] Paley(73) reading#0: L_s + b >= n + dist_min(M(G^2))  [KILLED 2026-08] :: LHS(lb)=73 < RHS(exact)=74; bounds insufficient
- [BRACKET] T(12) reading#0: L_s + b >= n + dist_min(M(G^2))  [KILLED 2026-08] :: LHS(lb)=45 < RHS(exact)=67; bounds insufficient

### id 180
statement: If G is a simple connected graph on at least 2 vertices, then L_s(G) + b(G) ≥ 1 + α(G) + maximum of dist_even(v).

- [BRACKET] T(12) reading#0: L_s + b >= 1 + alpha + max dist_even :: LHS(lb)=45 < RHS(exact)=53; bounds insufficient

### id 181
statement: If G is a simple connected graph on at least 2 vertices, then L_s(G) + b(G) ≥ α(G) + deg_avg(B(G^2 )).

- [BRACKET] Paley(101) reading#0: L_s + b >= alpha + deg_avg(B(G^2)) [KILLED via T(7) 2026-08] :: LHS(lb)=85 < RHS(exact)=100; bounds insufficient
- [BRACKET] T(12) reading#0: L_s + b >= alpha + deg_avg(B(G^2)) [KILLED via T(7) 2026-08] :: LHS(lb)=45 < RHS(exact)=65; bounds insufficient

### id 182
statement: If G is a simple connected graph on at least 2 vertices, then L_s(G) + b(G) ≥ Δ(B(G^2 )) + diam(G).

- [BRACKET] Paley(101) reading#0: L_s + b >= Delta(B(G^2)) + diam :: LHS(lb)=85 < RHS(exact)=102; bounds insufficient
- [BRACKET] Paley(73) reading#0: L_s + b >= Delta(B(G^2)) + diam :: LHS(lb)=73 < RHS(exact)=74; bounds insufficient
- [BRACKET] T(12) reading#0: L_s + b >= Delta(B(G^2)) + diam :: LHS(lb)=45 < RHS(exact)=67; bounds insufficient

### id 183
statement: If G is a simple connected graph on at least 2 vertices, then L_s(G) + b(G) ≥ Δ(G^2 ) + 2*rad(G^2 ).

- [BRACKET] Paley(101) reading#0: L_s + b >= Delta(G^2) + 2*rad(G^2) :: LHS(lb)=85 < RHS(exact)=102; bounds insufficient
- [BRACKET] Paley(73) reading#0: L_s + b >= Delta(G^2) + 2*rad(G^2) :: LHS(lb)=73 < RHS(exact)=74; bounds insufficient
- [BRACKET] T(12) reading#0: L_s + b >= Delta(G^2) + 2*rad(G^2) :: LHS(lb)=45 < RHS(exact)=67; bounds insufficient

## batch appended 2026-08-26 06:52:41

| id | verdict | vio | hold | bracket | premise_false | undef | tag |
|---|---|---|---|---|---|---|---|
| 184 | BRACKET | 0 | 93 | 5 | 0 | 2 |  |
| 185 | BRACKET | 0 | 46 | 3 | 0 | 1 |  |
| 186 | HOLDS_PARTIAL | 0 | 98 | 0 | 0 | 2 |  |
| 189 | HOLDS | 0 | 35 | 0 | 15 | 0 |  |
| 19 | HOLDS_PARTIAL | 0 | 60 | 0 | 0 | 40 |  |
| 190 | HOLDS | 0 | 33 | 0 | 17 | 0 |  |
| 194 | BRACKET | 0 | 34 | 1 | 15 | 0 |  |
| 198a | BRACKET | 0 | 8 | 20 | 22 | 0 | EXTERNALLY_RESOLVED |
| 199 | BRACKET | 0 | 42 | 8 | 0 | 0 |  |
| 2 | BRACKET | 0 | 148 | 2 | 0 | 0 |  |

### id 184
statement: If G is a simple connected graph on at least 2 vertices, then L_s(G) + b(G) ≥ Δ(G^2 ) + 2*dist_avg(B(G^2 ),V(G^2 )).

- [BRACKET] Paley(101) reading#0: L_s + b >= Delta(G^2) + 2*dist_avg(B(G^2),V(G^2)) [pairs avg] :: LHS(lb)=85 < RHS(exact)=102; bounds insufficient
- [BRACKET] Paley(101) reading#1: alt per-vertex avg: 2*avg_v dist_{G2}(v, B(G2)) :: LHS(lb)=85 < RHS(exact)=100; bounds insufficient
- [BRACKET] Paley(73) reading#0: L_s + b >= Delta(G^2) + 2*dist_avg(B(G^2),V(G^2)) [pairs avg] :: LHS(lb)=73 < RHS(exact)=74; bounds insufficient
- [BRACKET] T(12) reading#0: L_s + b >= Delta(G^2) + 2*dist_avg(B(G^2),V(G^2)) [pairs avg] :: LHS(lb)=45 < RHS(exact)=67; bounds insufficient
- [BRACKET] T(12) reading#1: alt per-vertex avg: 2*avg_v dist_{G2}(v, B(G2)) :: LHS(lb)=45 < RHS(exact)=65; bounds insufficient

### id 185
statement: If G is a simple connected graph on at least 2 vertices, then L_s(G) + b(G) ≥ Δ(G^2 ) + 2*dist_avg(G^2 ).

- [BRACKET] Paley(101) reading#0: L_s + b >= Delta(G^2) + 2*dist_avg(G^2) :: LHS(lb)=85 < RHS(exact)=102; bounds insufficient
- [BRACKET] Paley(73) reading#0: L_s + b >= Delta(G^2) + 2*dist_avg(G^2) :: LHS(lb)=73 < RHS(exact)=74; bounds insufficient
- [BRACKET] T(12) reading#0: L_s + b >= Delta(G^2) + 2*dist_avg(G^2) :: LHS(lb)=45 < RHS(exact)=67; bounds insufficient

### id 194
statement: If G is a simple connected graph with n > 1 such that α(G) ≤ 1 + λ_avg(G), then G has a Hamiltonian path.

- [BRACKET] comp(C5[K5]) reading#0: alpha <= 1 + lambda_avg ==> G has a Hamiltonian path :: no ham path found within search budget

### id 198a
statement: If G is a simple connected graph with n > 1 such that b(G) ≤ 2 + ecc_avg(G), then G has a Hamiltonian path.

- [BRACKET] KG(11,2) reading#0: b <= 2 + ecc_avg(M) ==> G has a Hamiltonian path :: premise undecidable: b not exactly certified ({'value': 19, 'certified': False, 'secs': 60.0})
- [BRACKET] KG(12,2) reading#0: b <= 2 + ecc_avg(M) ==> G has a Hamiltonian path :: premise undecidable: b not exactly certified ({'value': 21, 'certified': False, 'secs': 60.0})
- [BRACKET] KG(13,2) reading#0: b <= 2 + ecc_avg(M) ==> G has a Hamiltonian path :: premise undecidable: b not exactly certified ({'value': 23, 'certified': False, 'secs': 60.0})
- [BRACKET] KG(14,2) reading#0: b <= 2 + ecc_avg(M) ==> G has a Hamiltonian path :: premise undecidable: b not exactly certified ({'value': 25, 'certified': False, 'secs': 60.0})
- [BRACKET] KG(15,2) reading#0: b <= 2 + ecc_avg(M) ==> G has a Hamiltonian path :: premise undecidable: b not exactly certified ({'value': 27, 'certified': False, 'secs': 60.0})
- [BRACKET] KG(16,2) reading#0: b <= 2 + ecc_avg(M) ==> G has a Hamiltonian path :: premise undecidable: b not exactly certified ({'value': 29, 'certified': False, 'secs': 60.0})
- [BRACKET] Paley(101) reading#0: b <= 2 + ecc_avg(M) ==> G has a Hamiltonian path :: premise undecidable: b not exactly certified ({'value': 10, 'certified': False, 'secs': 60.0})
- [BRACKET] Paley(53) reading#0: b <= 2 + ecc_avg(M) ==> G has a Hamiltonian path :: premise undecidable: b not exactly certified ({'value': 10, 'certified': False, 'secs': 60.0})
- [BRACKET] Paley(61) reading#0: b <= 2 + ecc_avg(M) ==> G has a Hamiltonian path :: premise undecidable: b not exactly certified ({'value': 10, 'certified': False, 'secs': 60.0})
- [BRACKET] Paley(73) reading#0: b <= 2 + ecc_avg(M) ==> G has a Hamiltonian path :: premise undecidable: b not exactly certified ({'value': 10, 'certified': False, 'secs': 60.0})
- [BRACKET] Paley(89) reading#0: b <= 2 + ecc_avg(M) ==> G has a Hamiltonian path :: premise undecidable: b not exactly certified ({'value': 10, 'certified': False, 'secs': 60.0})
- [BRACKET] Paley(97) reading#0: b <= 2 + ecc_avg(M) ==> G has a Hamiltonian path :: premise undecidable: b not exactly certified ({'value': 12, 'certified': False, 'secs': 60.0})
- [BRACKET] T(10) reading#0: b <= 2 + ecc_avg(M) ==> G has a Hamiltonian path :: premise undecidable: b not exactly certified ({'value': 10, 'certified': False, 'secs': 60.0})
- [BRACKET] T(11) reading#0: b <= 2 + ecc_avg(M) ==> G has a Hamiltonian path :: premise undecidable: b not exactly certified ({'bracket': True})
- [BRACKET] T(12) reading#0: b <= 2 + ecc_avg(M) ==> G has a Hamiltonian path :: premise undecidable: b not exactly certified ({'value': 12, 'certified': False, 'secs': 60.0})
- [BRACKET] T(13) reading#0: b <= 2 + ecc_avg(M) ==> G has a Hamiltonian path :: premise undecidable: b not exactly certified ({'value': 12, 'certified': False, 'secs': 60.0})
- [BRACKET] T(14) reading#0: b <= 2 + ecc_avg(M) ==> G has a Hamiltonian path :: premise undecidable: b not exactly certified ({'value': 14, 'certified': False, 'secs': 60.0})
- [BRACKET] T(15) reading#0: b <= 2 + ecc_avg(M) ==> G has a Hamiltonian path :: premise undecidable: b not exactly certified ({'value': 14, 'certified': False, 'secs': 60.0})
- [BRACKET] T(16) reading#0: b <= 2 + ecc_avg(M) ==> G has a Hamiltonian path :: premise undecidable: b not exactly certified ({'value': 16, 'certified': False, 'secs': 60.0})
- [BRACKET] comp(C5[K8]) reading#0: b <= 2 + ecc_avg(M) ==> G has a Hamiltonian path :: premise undecidable: b not exactly certified ({'value': 32, 'certified': False, 'secs': 60.0})

### id 199
statement: If G is a simple connected graph with n > 1 such that tree(G) - 2 ≤ κ(G), then G has a Hamiltonian path.

- [BRACKET] KG(16,2) reading#0: tree - 2 <= kappa ==> G has a Hamiltonian path :: premise undecidable: tree not exactly certified ({'value': 14, 'certified': False, 'secs': 60.0})
- [BRACKET] Paley(101) reading#0: tree - 2 <= kappa ==> G has a Hamiltonian path :: premise undecidable: tree not exactly certified ({'value': 10, 'certified': False, 'secs': 60.0})
- [BRACKET] Paley(89) reading#0: tree - 2 <= kappa ==> G has a Hamiltonian path :: premise undecidable: tree not exactly certified ({'value': 10, 'certified': False, 'secs': 60.0})
- [BRACKET] Paley(97) reading#0: tree - 2 <= kappa ==> G has a Hamiltonian path :: premise undecidable: tree not exactly certified ({'value': 11, 'certified': False, 'secs': 60.0})
- [BRACKET] T(14) reading#0: tree - 2 <= kappa ==> G has a Hamiltonian path :: premise undecidable: tree not exactly certified ({'value': 13, 'certified': False, 'secs': 60.0})
- [BRACKET] T(15) reading#0: tree - 2 <= kappa ==> G has a Hamiltonian path :: premise undecidable: tree not exactly certified ({'value': 14, 'certified': False, 'secs': 60.0})
- [BRACKET] T(16) reading#0: tree - 2 <= kappa ==> G has a Hamiltonian path :: premise undecidable: tree not exactly certified ({'value': 15, 'certified': False, 'secs': 60.0})
- [BRACKET] comp(C5[K5]) reading#0: tree - 2 <= kappa ==> G has a Hamiltonian path :: no ham path found within search budget

### id 2
statement: If G is a simple connected graph, then L_s(G) ≥ 2(average of λ(v) - 1)

- [BRACKET] CP(2) reading#1: alt precedence: L_s >= 2*lambda_avg - 1 :: LHS(lb)=2 < RHS(exact)=3; bounds insufficient
- [BRACKET] K(3,3) reading#1: alt precedence: L_s >= 2*lambda_avg - 1 :: LHS(lb)=4 < RHS(exact)=5; bounds insufficient

## batch appended 2026-08-26 06:54:31

| id | verdict | vio | hold | bracket | premise_false | undef | tag |
|---|---|---|---|---|---|---|---|
| 200 | BRACKET | 0 | 21 | 7 | 22 | 0 | EXTERNALLY_RESOLVED |
| 209 | HOLDS | 0 | 17 | 0 | 33 | 0 | EXTERNALLY_RESOLVED |
| 213 | HOLDS | 0 | 16 | 0 | 34 | 0 |  |
| 217 | BRACKET | 0 | 48 | 2 | 0 | 0 |  |
| 232 | BRACKET | 0 | 0 | 100 | 0 | 0 |  |
| 233 | BRACKET | 0 | 0 | 100 | 0 | 0 |  |
| 235 | VIOLATED_CANDIDATE | 3 | 0 | 97 | 0 | 0 |  |
| 241 | BRACKET | 0 | 0 | 50 | 0 | 0 |  |
| 242 | BRACKET | 0 | 0 | 50 | 0 | 0 |  |
| 247 | BRACKET | 0 | 0 | 48 | 0 | 2 |  |

### id 200
statement: If G is a simple connected graph with n > 1 such that tree(G) =CEIL[1 + λ_avg(G)], then G has a Hamiltonian path.

- [BRACKET] KG(16,2) reading#0: tree == ceil(1 + lambda_avg) [externally refuted] ==> G has a Hamiltonian path :: premise undecidable: tree not exactly certified ({'value': 14, 'certified': False, 'secs': 60.0})
- [BRACKET] Paley(101) reading#0: tree == ceil(1 + lambda_avg) [externally refuted] ==> G has a Hamiltonian path :: premise undecidable: tree not exactly certified ({'value': 10, 'certified': False, 'secs': 60.0})
- [BRACKET] Paley(89) reading#0: tree == ceil(1 + lambda_avg) [externally refuted] ==> G has a Hamiltonian path :: premise undecidable: tree not exactly certified ({'value': 10, 'certified': False, 'secs': 60.0})
- [BRACKET] Paley(97) reading#0: tree == ceil(1 + lambda_avg) [externally refuted] ==> G has a Hamiltonian path :: premise undecidable: tree not exactly certified ({'value': 11, 'certified': False, 'secs': 60.0})
- [BRACKET] T(14) reading#0: tree == ceil(1 + lambda_avg) [externally refuted] ==> G has a Hamiltonian path :: premise undecidable: tree not exactly certified ({'value': 13, 'certified': False, 'secs': 60.0})
- [BRACKET] T(15) reading#0: tree == ceil(1 + lambda_avg) [externally refuted] ==> G has a Hamiltonian path :: premise undecidable: tree not exactly certified ({'value': 14, 'certified': False, 'secs': 60.0})
- [BRACKET] T(16) reading#0: tree == ceil(1 + lambda_avg) [externally refuted] ==> G has a Hamiltonian path :: premise undecidable: tree not exactly certified ({'value': 15, 'certified': False, 'secs': 60.0})

### id 217
statement: If G is a simple connected graph with n > 1 such that L(G) ≤ 4*χ_residue=2(G) + 2, then G has a Hamiltonian path.

- [BRACKET] T(16) reading#0: L(G) (#pendants) <= 4*chi_residue=2(G) + 2 ==> G has a Hamiltonian path :: no ham path found within search budget
- [BRACKET] comp(C5[K5]) reading#0: L(G) (#pendants) <= 4*chi_residue=2(G) + 2 ==> G has a Hamiltonian path :: no ham path found within search budget

### id 232
statement: If G is a simple connected graph, then γ_t(G) ≥ 0.5*[radius(G) + ecc(B) ]

- [BRACKET] C7[K3] reading#0: gamma_t >= 0.5*(radius + ecc(B)), ecc(B)=diam :: LHS(ub)=4 >= RHS(exact)=3 but kinds cannot certify hold
- [BRACKET] C7[K3] reading#1: gamma_t >= 0.5*(radius + ecc_def52(B)) :: LHS(ub)=4 >= RHS(exact)=3 but kinds cannot certify hold
- [BRACKET] C9[K3] reading#0: gamma_t >= 0.5*(radius + ecc(B)), ecc(B)=diam :: LHS(ub)=5 >= RHS(exact)=4 but kinds cannot certify hold
- [BRACKET] C9[K3] reading#1: gamma_t >= 0.5*(radius + ecc_def52(B)) :: LHS(ub)=5 >= RHS(exact)=4 but kinds cannot certify hold
- [BRACKET] CMP(2) reading#0: gamma_t >= 0.5*(radius + ecc(B)), ecc(B)=diam :: LHS(ub)=2 >= RHS(exact)=3/2 but kinds cannot certify hold
- [BRACKET] CMP(2) reading#1: gamma_t >= 0.5*(radius + ecc_def52(B)) :: LHS(ub)=2 >= RHS(exact)=3/2 but kinds cannot certify hold
- [BRACKET] CMP(3) reading#0: gamma_t >= 0.5*(radius + ecc(B)), ecc(B)=diam :: LHS(ub)=2 >= RHS(exact)=3/2 but kinds cannot certify hold
- [BRACKET] CMP(3) reading#1: gamma_t >= 0.5*(radius + ecc_def52(B)) :: LHS(ub)=2 >= RHS(exact)=3/2 but kinds cannot certify hold
- [BRACKET] CMP(4) reading#0: gamma_t >= 0.5*(radius + ecc(B)), ecc(B)=diam :: LHS(ub)=2 >= RHS(exact)=3/2 but kinds cannot certify hold
- [BRACKET] CMP(4) reading#1: gamma_t >= 0.5*(radius + ecc_def52(B)) :: LHS(ub)=2 >= RHS(exact)=3/2 but kinds cannot certify hold
- [BRACKET] CMP(5) reading#0: gamma_t >= 0.5*(radius + ecc(B)), ecc(B)=diam :: LHS(ub)=2 >= RHS(exact)=3/2 but kinds cannot certify hold
- [BRACKET] CMP(5) reading#1: gamma_t >= 0.5*(radius + ecc_def52(B)) :: LHS(ub)=2 >= RHS(exact)=3/2 but kinds cannot certify hold
- [BRACKET] CMP(6) reading#0: gamma_t >= 0.5*(radius + ecc(B)), ecc(B)=diam :: LHS(ub)=2 >= RHS(exact)=3/2 but kinds cannot certify hold
- [BRACKET] CMP(6) reading#1: gamma_t >= 0.5*(radius + ecc_def52(B)) :: LHS(ub)=2 >= RHS(exact)=3/2 but kinds cannot certify hold
- [BRACKET] CMP(7) reading#0: gamma_t >= 0.5*(radius + ecc(B)), ecc(B)=diam :: LHS(ub)=2 >= RHS(exact)=3/2 but kinds cannot certify hold
- [BRACKET] CMP(7) reading#1: gamma_t >= 0.5*(radius + ecc_def52(B)) :: LHS(ub)=2 >= RHS(exact)=3/2 but kinds cannot certify hold
- [BRACKET] CMP(8) reading#0: gamma_t >= 0.5*(radius + ecc(B)), ecc(B)=diam :: LHS(ub)=2 >= RHS(exact)=3/2 but kinds cannot certify hold
- [BRACKET] CMP(8) reading#1: gamma_t >= 0.5*(radius + ecc_def52(B)) :: LHS(ub)=2 >= RHS(exact)=3/2 but kinds cannot certify hold
- [BRACKET] CP(2) reading#0: gamma_t >= 0.5*(radius + ecc(B)), ecc(B)=diam :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] CP(2) reading#1: gamma_t >= 0.5*(radius + ecc_def52(B)) :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] CP(3) reading#0: gamma_t >= 0.5*(radius + ecc(B)), ecc(B)=diam :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] CP(3) reading#1: gamma_t >= 0.5*(radius + ecc_def52(B)) :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] CP(4) reading#0: gamma_t >= 0.5*(radius + ecc(B)), ecc(B)=diam :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] CP(4) reading#1: gamma_t >= 0.5*(radius + ecc_def52(B)) :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] CP(5) reading#0: gamma_t >= 0.5*(radius + ecc(B)), ecc(B)=diam :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] CP(5) reading#1: gamma_t >= 0.5*(radius + ecc_def52(B)) :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] CP(6) reading#0: gamma_t >= 0.5*(radius + ecc(B)), ecc(B)=diam :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] CP(6) reading#1: gamma_t >= 0.5*(radius + ecc_def52(B)) :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] CP(7) reading#0: gamma_t >= 0.5*(radius + ecc(B)), ecc(B)=diam :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] CP(7) reading#1: gamma_t >= 0.5*(radius + ecc_def52(B)) :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] CP(8) reading#0: gamma_t >= 0.5*(radius + ecc(B)), ecc(B)=diam :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] CP(8) reading#1: gamma_t >= 0.5*(radius + ecc_def52(B)) :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] K(3,3) reading#0: gamma_t >= 0.5*(radius + ecc(B)), ecc(B)=diam :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] K(3,3) reading#1: gamma_t >= 0.5*(radius + ecc_def52(B)) :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] K(3,3,3) reading#0: gamma_t >= 0.5*(radius + ecc(B)), ecc(B)=diam :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] K(3,3,3) reading#1: gamma_t >= 0.5*(radius + ecc_def52(B)) :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] KG(10,2) reading#0: gamma_t >= 0.5*(radius + ecc(B)), ecc(B)=diam :: LHS(ub)=3 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] KG(10,2) reading#1: gamma_t >= 0.5*(radius + ecc_def52(B)) :: LHS(ub)=3 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] KG(11,2) reading#0: gamma_t >= 0.5*(radius + ecc(B)), ecc(B)=diam :: LHS(ub)=3 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] KG(11,2) reading#1: gamma_t >= 0.5*(radius + ecc_def52(B)) :: LHS(ub)=3 >= RHS(exact)=2 but kinds cannot certify hold

### id 233
statement: If G is a simple connected graph, then γ_t(G) ≥ (2/3) * ( 1+ecc(B) )

- [BRACKET] C7[K3] reading#0: gamma_t >= (2/3)*(1 + ecc(B)=diam) :: LHS(ub)=4 >= RHS(exact)=8/3 but kinds cannot certify hold
- [BRACKET] C7[K3] reading#1: gamma_t >= (2/3)*(1 + ecc_def52(B)) :: LHS(ub)=4 >= RHS(exact)=2/3 but kinds cannot certify hold
- [BRACKET] C9[K3] reading#0: gamma_t >= (2/3)*(1 + ecc(B)=diam) :: LHS(ub)=5 >= RHS(exact)=10/3 but kinds cannot certify hold
- [BRACKET] C9[K3] reading#1: gamma_t >= (2/3)*(1 + ecc_def52(B)) :: LHS(ub)=5 >= RHS(exact)=2/3 but kinds cannot certify hold
- [BRACKET] CMP(2) reading#0: gamma_t >= (2/3)*(1 + ecc(B)=diam) :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] CMP(2) reading#1: gamma_t >= (2/3)*(1 + ecc_def52(B)) :: LHS(ub)=2 >= RHS(exact)=4/3 but kinds cannot certify hold
- [BRACKET] CMP(3) reading#0: gamma_t >= (2/3)*(1 + ecc(B)=diam) :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] CMP(3) reading#1: gamma_t >= (2/3)*(1 + ecc_def52(B)) :: LHS(ub)=2 >= RHS(exact)=4/3 but kinds cannot certify hold
- [BRACKET] CMP(4) reading#0: gamma_t >= (2/3)*(1 + ecc(B)=diam) :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] CMP(4) reading#1: gamma_t >= (2/3)*(1 + ecc_def52(B)) :: LHS(ub)=2 >= RHS(exact)=4/3 but kinds cannot certify hold
- [BRACKET] CMP(5) reading#0: gamma_t >= (2/3)*(1 + ecc(B)=diam) :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] CMP(5) reading#1: gamma_t >= (2/3)*(1 + ecc_def52(B)) :: LHS(ub)=2 >= RHS(exact)=4/3 but kinds cannot certify hold
- [BRACKET] CMP(6) reading#0: gamma_t >= (2/3)*(1 + ecc(B)=diam) :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] CMP(6) reading#1: gamma_t >= (2/3)*(1 + ecc_def52(B)) :: LHS(ub)=2 >= RHS(exact)=4/3 but kinds cannot certify hold
- [BRACKET] CMP(7) reading#0: gamma_t >= (2/3)*(1 + ecc(B)=diam) :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] CMP(7) reading#1: gamma_t >= (2/3)*(1 + ecc_def52(B)) :: LHS(ub)=2 >= RHS(exact)=4/3 but kinds cannot certify hold
- [BRACKET] CMP(8) reading#0: gamma_t >= (2/3)*(1 + ecc(B)=diam) :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] CMP(8) reading#1: gamma_t >= (2/3)*(1 + ecc_def52(B)) :: LHS(ub)=2 >= RHS(exact)=4/3 but kinds cannot certify hold
- [BRACKET] CP(2) reading#0: gamma_t >= (2/3)*(1 + ecc(B)=diam) :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] CP(2) reading#1: gamma_t >= (2/3)*(1 + ecc_def52(B)) :: LHS(ub)=2 >= RHS(exact)=2/3 but kinds cannot certify hold
- [BRACKET] CP(3) reading#0: gamma_t >= (2/3)*(1 + ecc(B)=diam) :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] CP(3) reading#1: gamma_t >= (2/3)*(1 + ecc_def52(B)) :: LHS(ub)=2 >= RHS(exact)=2/3 but kinds cannot certify hold
- [BRACKET] CP(4) reading#0: gamma_t >= (2/3)*(1 + ecc(B)=diam) :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] CP(4) reading#1: gamma_t >= (2/3)*(1 + ecc_def52(B)) :: LHS(ub)=2 >= RHS(exact)=2/3 but kinds cannot certify hold
- [BRACKET] CP(5) reading#0: gamma_t >= (2/3)*(1 + ecc(B)=diam) :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] CP(5) reading#1: gamma_t >= (2/3)*(1 + ecc_def52(B)) :: LHS(ub)=2 >= RHS(exact)=2/3 but kinds cannot certify hold
- [BRACKET] CP(6) reading#0: gamma_t >= (2/3)*(1 + ecc(B)=diam) :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] CP(6) reading#1: gamma_t >= (2/3)*(1 + ecc_def52(B)) :: LHS(ub)=2 >= RHS(exact)=2/3 but kinds cannot certify hold
- [BRACKET] CP(7) reading#0: gamma_t >= (2/3)*(1 + ecc(B)=diam) :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] CP(7) reading#1: gamma_t >= (2/3)*(1 + ecc_def52(B)) :: LHS(ub)=2 >= RHS(exact)=2/3 but kinds cannot certify hold
- [BRACKET] CP(8) reading#0: gamma_t >= (2/3)*(1 + ecc(B)=diam) :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] CP(8) reading#1: gamma_t >= (2/3)*(1 + ecc_def52(B)) :: LHS(ub)=2 >= RHS(exact)=2/3 but kinds cannot certify hold
- [BRACKET] K(3,3) reading#0: gamma_t >= (2/3)*(1 + ecc(B)=diam) :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] K(3,3) reading#1: gamma_t >= (2/3)*(1 + ecc_def52(B)) :: LHS(ub)=2 >= RHS(exact)=2/3 but kinds cannot certify hold
- [BRACKET] K(3,3,3) reading#0: gamma_t >= (2/3)*(1 + ecc(B)=diam) :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] K(3,3,3) reading#1: gamma_t >= (2/3)*(1 + ecc_def52(B)) :: LHS(ub)=2 >= RHS(exact)=2/3 but kinds cannot certify hold
- [BRACKET] KG(10,2) reading#0: gamma_t >= (2/3)*(1 + ecc(B)=diam) :: LHS(ub)=3 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] KG(10,2) reading#1: gamma_t >= (2/3)*(1 + ecc_def52(B)) :: LHS(ub)=3 >= RHS(exact)=2/3 but kinds cannot certify hold
- [BRACKET] KG(11,2) reading#0: gamma_t >= (2/3)*(1 + ecc(B)=diam) :: LHS(ub)=3 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] KG(11,2) reading#1: gamma_t >= (2/3)*(1 + ecc_def52(B)) :: LHS(ub)=3 >= RHS(exact)=2/3 but kinds cannot certify hold

### id 235
statement: If G is a simple connected graph, then γ_t(G) ≥ (2/3) ecc(B) + χ_bipartite(G).

- [BRACKET] C7[K3] reading#0: gamma_t >= (2/3)*ecc(B)=diam + chi_bipartite :: LHS(ub)=4 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] C7[K3] reading#1: gamma_t >= (2/3)*ecc_def52(B) + chi_bipartite :: LHS(ub)=4 >= RHS(exact)=0 but kinds cannot certify hold
- [BRACKET] C9[K3] reading#0: gamma_t >= (2/3)*ecc(B)=diam + chi_bipartite :: LHS(ub)=5 >= RHS(exact)=8/3 but kinds cannot certify hold
- [BRACKET] C9[K3] reading#1: gamma_t >= (2/3)*ecc_def52(B) + chi_bipartite :: LHS(ub)=5 >= RHS(exact)=0 but kinds cannot certify hold
- [VIO] CMP(2) reading#0: gamma_t >= (2/3)*ecc(B)=diam + chi_bipartite :: gamma-style LHS<=2 < RHS=7/3
- [BRACKET] CMP(2) reading#1: gamma_t >= (2/3)*ecc_def52(B) + chi_bipartite :: LHS(ub)=2 >= RHS(exact)=5/3 but kinds cannot certify hold
- [BRACKET] CMP(3) reading#0: gamma_t >= (2/3)*ecc(B)=diam + chi_bipartite :: LHS(ub)=2 >= RHS(exact)=4/3 but kinds cannot certify hold
- [BRACKET] CMP(3) reading#1: gamma_t >= (2/3)*ecc_def52(B) + chi_bipartite :: LHS(ub)=2 >= RHS(exact)=2/3 but kinds cannot certify hold
- [BRACKET] CMP(4) reading#0: gamma_t >= (2/3)*ecc(B)=diam + chi_bipartite :: LHS(ub)=2 >= RHS(exact)=4/3 but kinds cannot certify hold
- [BRACKET] CMP(4) reading#1: gamma_t >= (2/3)*ecc_def52(B) + chi_bipartite :: LHS(ub)=2 >= RHS(exact)=2/3 but kinds cannot certify hold
- [BRACKET] CMP(5) reading#0: gamma_t >= (2/3)*ecc(B)=diam + chi_bipartite :: LHS(ub)=2 >= RHS(exact)=4/3 but kinds cannot certify hold
- [BRACKET] CMP(5) reading#1: gamma_t >= (2/3)*ecc_def52(B) + chi_bipartite :: LHS(ub)=2 >= RHS(exact)=2/3 but kinds cannot certify hold
- [BRACKET] CMP(6) reading#0: gamma_t >= (2/3)*ecc(B)=diam + chi_bipartite :: LHS(ub)=2 >= RHS(exact)=4/3 but kinds cannot certify hold
- [BRACKET] CMP(6) reading#1: gamma_t >= (2/3)*ecc_def52(B) + chi_bipartite :: LHS(ub)=2 >= RHS(exact)=2/3 but kinds cannot certify hold
- [BRACKET] CMP(7) reading#0: gamma_t >= (2/3)*ecc(B)=diam + chi_bipartite :: LHS(ub)=2 >= RHS(exact)=4/3 but kinds cannot certify hold
- [BRACKET] CMP(7) reading#1: gamma_t >= (2/3)*ecc_def52(B) + chi_bipartite :: LHS(ub)=2 >= RHS(exact)=2/3 but kinds cannot certify hold
- [BRACKET] CMP(8) reading#0: gamma_t >= (2/3)*ecc(B)=diam + chi_bipartite :: LHS(ub)=2 >= RHS(exact)=4/3 but kinds cannot certify hold
- [BRACKET] CMP(8) reading#1: gamma_t >= (2/3)*ecc_def52(B) + chi_bipartite :: LHS(ub)=2 >= RHS(exact)=2/3 but kinds cannot certify hold
- [VIO] CP(2) reading#0: gamma_t >= (2/3)*ecc(B)=diam + chi_bipartite :: gamma-style LHS<=2 < RHS=7/3
- [BRACKET] CP(2) reading#1: gamma_t >= (2/3)*ecc_def52(B) + chi_bipartite :: LHS(ub)=2 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] CP(3) reading#0: gamma_t >= (2/3)*ecc(B)=diam + chi_bipartite :: LHS(ub)=2 >= RHS(exact)=4/3 but kinds cannot certify hold
- [BRACKET] CP(3) reading#1: gamma_t >= (2/3)*ecc_def52(B) + chi_bipartite :: LHS(ub)=2 >= RHS(exact)=0 but kinds cannot certify hold
- [BRACKET] CP(4) reading#0: gamma_t >= (2/3)*ecc(B)=diam + chi_bipartite :: LHS(ub)=2 >= RHS(exact)=4/3 but kinds cannot certify hold
- [BRACKET] CP(4) reading#1: gamma_t >= (2/3)*ecc_def52(B) + chi_bipartite :: LHS(ub)=2 >= RHS(exact)=0 but kinds cannot certify hold
- [BRACKET] CP(5) reading#0: gamma_t >= (2/3)*ecc(B)=diam + chi_bipartite :: LHS(ub)=2 >= RHS(exact)=4/3 but kinds cannot certify hold
- [BRACKET] CP(5) reading#1: gamma_t >= (2/3)*ecc_def52(B) + chi_bipartite :: LHS(ub)=2 >= RHS(exact)=0 but kinds cannot certify hold
- [BRACKET] CP(6) reading#0: gamma_t >= (2/3)*ecc(B)=diam + chi_bipartite :: LHS(ub)=2 >= RHS(exact)=4/3 but kinds cannot certify hold
- [BRACKET] CP(6) reading#1: gamma_t >= (2/3)*ecc_def52(B) + chi_bipartite :: LHS(ub)=2 >= RHS(exact)=0 but kinds cannot certify hold
- [BRACKET] CP(7) reading#0: gamma_t >= (2/3)*ecc(B)=diam + chi_bipartite :: LHS(ub)=2 >= RHS(exact)=4/3 but kinds cannot certify hold
- [BRACKET] CP(7) reading#1: gamma_t >= (2/3)*ecc_def52(B) + chi_bipartite :: LHS(ub)=2 >= RHS(exact)=0 but kinds cannot certify hold
- [BRACKET] CP(8) reading#0: gamma_t >= (2/3)*ecc(B)=diam + chi_bipartite :: LHS(ub)=2 >= RHS(exact)=4/3 but kinds cannot certify hold
- [BRACKET] CP(8) reading#1: gamma_t >= (2/3)*ecc_def52(B) + chi_bipartite :: LHS(ub)=2 >= RHS(exact)=0 but kinds cannot certify hold
- [VIO] K(3,3) reading#0: gamma_t >= (2/3)*ecc(B)=diam + chi_bipartite :: gamma-style LHS<=2 < RHS=7/3
- [BRACKET] K(3,3) reading#1: gamma_t >= (2/3)*ecc_def52(B) + chi_bipartite :: LHS(ub)=2 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] K(3,3,3) reading#0: gamma_t >= (2/3)*ecc(B)=diam + chi_bipartite :: LHS(ub)=2 >= RHS(exact)=4/3 but kinds cannot certify hold
- [BRACKET] K(3,3,3) reading#1: gamma_t >= (2/3)*ecc_def52(B) + chi_bipartite :: LHS(ub)=2 >= RHS(exact)=0 but kinds cannot certify hold
- [BRACKET] KG(10,2) reading#0: gamma_t >= (2/3)*ecc(B)=diam + chi_bipartite :: LHS(ub)=3 >= RHS(exact)=4/3 but kinds cannot certify hold
- [BRACKET] KG(10,2) reading#1: gamma_t >= (2/3)*ecc_def52(B) + chi_bipartite :: LHS(ub)=3 >= RHS(exact)=0 but kinds cannot certify hold
- [BRACKET] KG(11,2) reading#0: gamma_t >= (2/3)*ecc(B)=diam + chi_bipartite :: LHS(ub)=3 >= RHS(exact)=4/3 but kinds cannot certify hold
- [BRACKET] KG(11,2) reading#1: gamma_t >= (2/3)*ecc_def52(B) + chi_bipartite :: LHS(ub)=3 >= RHS(exact)=0 but kinds cannot certify hold

### id 241
statement: If G is a tree, then γ_t(G) ≥ FLOOR[number of components(<N[S]>) + dist_avg(C)], where <N[S]> is the subgraph induced by the closed neighborhood of the set of vertices of degree two and C is the set o

- [BRACKET] C7[K3] reading#0: gamma_t >= floor[components(<N[S_deg2]>) + dist_avg(C within)] :: LHS(ub)=4 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] C9[K3] reading#0: gamma_t >= floor[components(<N[S_deg2]>) + dist_avg(C within)] :: LHS(ub)=5 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] CMP(2) reading#0: gamma_t >= floor[components(<N[S_deg2]>) + dist_avg(C within)] :: LHS(ub)=2 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] CMP(3) reading#0: gamma_t >= floor[components(<N[S_deg2]>) + dist_avg(C within)] :: LHS(ub)=2 >= RHS(exact)=0 but kinds cannot certify hold
- [BRACKET] CMP(4) reading#0: gamma_t >= floor[components(<N[S_deg2]>) + dist_avg(C within)] :: LHS(ub)=2 >= RHS(exact)=0 but kinds cannot certify hold
- [BRACKET] CMP(5) reading#0: gamma_t >= floor[components(<N[S_deg2]>) + dist_avg(C within)] :: LHS(ub)=2 >= RHS(exact)=0 but kinds cannot certify hold
- [BRACKET] CMP(6) reading#0: gamma_t >= floor[components(<N[S_deg2]>) + dist_avg(C within)] :: LHS(ub)=2 >= RHS(exact)=0 but kinds cannot certify hold
- [BRACKET] CMP(7) reading#0: gamma_t >= floor[components(<N[S_deg2]>) + dist_avg(C within)] :: LHS(ub)=2 >= RHS(exact)=0 but kinds cannot certify hold
- [BRACKET] CMP(8) reading#0: gamma_t >= floor[components(<N[S_deg2]>) + dist_avg(C within)] :: LHS(ub)=2 >= RHS(exact)=0 but kinds cannot certify hold
- [BRACKET] CP(2) reading#0: gamma_t >= floor[components(<N[S_deg2]>) + dist_avg(C within)] :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] CP(3) reading#0: gamma_t >= floor[components(<N[S_deg2]>) + dist_avg(C within)] :: LHS(ub)=2 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] CP(4) reading#0: gamma_t >= floor[components(<N[S_deg2]>) + dist_avg(C within)] :: LHS(ub)=2 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] CP(5) reading#0: gamma_t >= floor[components(<N[S_deg2]>) + dist_avg(C within)] :: LHS(ub)=2 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] CP(6) reading#0: gamma_t >= floor[components(<N[S_deg2]>) + dist_avg(C within)] :: LHS(ub)=2 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] CP(7) reading#0: gamma_t >= floor[components(<N[S_deg2]>) + dist_avg(C within)] :: LHS(ub)=2 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] CP(8) reading#0: gamma_t >= floor[components(<N[S_deg2]>) + dist_avg(C within)] :: LHS(ub)=2 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] K(3,3) reading#0: gamma_t >= floor[components(<N[S_deg2]>) + dist_avg(C within)] :: LHS(ub)=2 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] K(3,3,3) reading#0: gamma_t >= floor[components(<N[S_deg2]>) + dist_avg(C within)] :: LHS(ub)=2 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] KG(10,2) reading#0: gamma_t >= floor[components(<N[S_deg2]>) + dist_avg(C within)] :: LHS(ub)=3 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] KG(11,2) reading#0: gamma_t >= floor[components(<N[S_deg2]>) + dist_avg(C within)] :: LHS(ub)=3 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] KG(12,2) reading#0: gamma_t >= floor[components(<N[S_deg2]>) + dist_avg(C within)] :: LHS(ub)=3 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] KG(13,2) reading#0: gamma_t >= floor[components(<N[S_deg2]>) + dist_avg(C within)] :: LHS(ub)=3 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] KG(14,2) reading#0: gamma_t >= floor[components(<N[S_deg2]>) + dist_avg(C within)] :: LHS(ub)=3 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] KG(15,2) reading#0: gamma_t >= floor[components(<N[S_deg2]>) + dist_avg(C within)] :: LHS(ub)=3 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] KG(16,2) reading#0: gamma_t >= floor[components(<N[S_deg2]>) + dist_avg(C within)] :: LHS(ub)=3 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] Paley(101) reading#0: gamma_t >= floor[components(<N[S_deg2]>) + dist_avg(C within)] :: LHS(ub)=5 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] Paley(13) reading#0: gamma_t >= floor[components(<N[S_deg2]>) + dist_avg(C within)] :: LHS(ub)=4 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] Paley(17) reading#0: gamma_t >= floor[components(<N[S_deg2]>) + dist_avg(C within)] :: LHS(ub)=4 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] Paley(29) reading#0: gamma_t >= floor[components(<N[S_deg2]>) + dist_avg(C within)] :: LHS(ub)=4 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] Paley(37) reading#0: gamma_t >= floor[components(<N[S_deg2]>) + dist_avg(C within)] :: LHS(ub)=4 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] Paley(41) reading#0: gamma_t >= floor[components(<N[S_deg2]>) + dist_avg(C within)] :: LHS(ub)=4 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] Paley(53) reading#0: gamma_t >= floor[components(<N[S_deg2]>) + dist_avg(C within)] :: LHS(ub)=4 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] Paley(61) reading#0: gamma_t >= floor[components(<N[S_deg2]>) + dist_avg(C within)] :: LHS(ub)=4 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] Paley(73) reading#0: gamma_t >= floor[components(<N[S_deg2]>) + dist_avg(C within)] :: LHS(ub)=5 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] Paley(89) reading#0: gamma_t >= floor[components(<N[S_deg2]>) + dist_avg(C within)] :: LHS(ub)=5 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] Paley(97) reading#0: gamma_t >= floor[components(<N[S_deg2]>) + dist_avg(C within)] :: LHS(ub)=5 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] T(10) reading#0: gamma_t >= floor[components(<N[S_deg2]>) + dist_avg(C within)] :: LHS(ub)=6 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] T(11) reading#0: gamma_t >= floor[components(<N[S_deg2]>) + dist_avg(C within)] :: LHS(ub)=7 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] T(12) reading#0: gamma_t >= floor[components(<N[S_deg2]>) + dist_avg(C within)] :: LHS(ub)=8 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] T(13) reading#0: gamma_t >= floor[components(<N[S_deg2]>) + dist_avg(C within)] :: LHS(ub)=8 >= RHS(exact)=1 but kinds cannot certify hold

### id 242
statement: If G is a tree, then γ_t(G) ≥ (1/2)[number of components(<N[S]> + ecc_avg(G)], where <N[S]> is the subgraph induced by the closed neighborhood of the set of vertices of degree two.

- [BRACKET] C7[K3] reading#0: gamma_t >= (1/2)[components(<N[S_deg2]>) + ecc_avg(G)] :: LHS(ub)=4 >= RHS(exact)=3/2 but kinds cannot certify hold
- [BRACKET] C9[K3] reading#0: gamma_t >= (1/2)[components(<N[S_deg2]>) + ecc_avg(G)] :: LHS(ub)=5 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] CMP(2) reading#0: gamma_t >= (1/2)[components(<N[S_deg2]>) + ecc_avg(G)] :: LHS(ub)=2 >= RHS(exact)=4/3 but kinds cannot certify hold
- [BRACKET] CMP(3) reading#0: gamma_t >= (1/2)[components(<N[S_deg2]>) + ecc_avg(G)] :: LHS(ub)=2 >= RHS(exact)=9/10 but kinds cannot certify hold
- [BRACKET] CMP(4) reading#0: gamma_t >= (1/2)[components(<N[S_deg2]>) + ecc_avg(G)] :: LHS(ub)=2 >= RHS(exact)=13/14 but kinds cannot certify hold
- [BRACKET] CMP(5) reading#0: gamma_t >= (1/2)[components(<N[S_deg2]>) + ecc_avg(G)] :: LHS(ub)=2 >= RHS(exact)=17/18 but kinds cannot certify hold
- [BRACKET] CMP(6) reading#0: gamma_t >= (1/2)[components(<N[S_deg2]>) + ecc_avg(G)] :: LHS(ub)=2 >= RHS(exact)=21/22 but kinds cannot certify hold
- [BRACKET] CMP(7) reading#0: gamma_t >= (1/2)[components(<N[S_deg2]>) + ecc_avg(G)] :: LHS(ub)=2 >= RHS(exact)=25/26 but kinds cannot certify hold
- [BRACKET] CMP(8) reading#0: gamma_t >= (1/2)[components(<N[S_deg2]>) + ecc_avg(G)] :: LHS(ub)=2 >= RHS(exact)=29/30 but kinds cannot certify hold
- [BRACKET] CP(2) reading#0: gamma_t >= (1/2)[components(<N[S_deg2]>) + ecc_avg(G)] :: LHS(ub)=2 >= RHS(exact)=3/2 but kinds cannot certify hold
- [BRACKET] CP(3) reading#0: gamma_t >= (1/2)[components(<N[S_deg2]>) + ecc_avg(G)] :: LHS(ub)=2 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] CP(4) reading#0: gamma_t >= (1/2)[components(<N[S_deg2]>) + ecc_avg(G)] :: LHS(ub)=2 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] CP(5) reading#0: gamma_t >= (1/2)[components(<N[S_deg2]>) + ecc_avg(G)] :: LHS(ub)=2 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] CP(6) reading#0: gamma_t >= (1/2)[components(<N[S_deg2]>) + ecc_avg(G)] :: LHS(ub)=2 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] CP(7) reading#0: gamma_t >= (1/2)[components(<N[S_deg2]>) + ecc_avg(G)] :: LHS(ub)=2 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] CP(8) reading#0: gamma_t >= (1/2)[components(<N[S_deg2]>) + ecc_avg(G)] :: LHS(ub)=2 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] K(3,3) reading#0: gamma_t >= (1/2)[components(<N[S_deg2]>) + ecc_avg(G)] :: LHS(ub)=2 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] K(3,3,3) reading#0: gamma_t >= (1/2)[components(<N[S_deg2]>) + ecc_avg(G)] :: LHS(ub)=2 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] KG(10,2) reading#0: gamma_t >= (1/2)[components(<N[S_deg2]>) + ecc_avg(G)] :: LHS(ub)=3 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] KG(11,2) reading#0: gamma_t >= (1/2)[components(<N[S_deg2]>) + ecc_avg(G)] :: LHS(ub)=3 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] KG(12,2) reading#0: gamma_t >= (1/2)[components(<N[S_deg2]>) + ecc_avg(G)] :: LHS(ub)=3 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] KG(13,2) reading#0: gamma_t >= (1/2)[components(<N[S_deg2]>) + ecc_avg(G)] :: LHS(ub)=3 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] KG(14,2) reading#0: gamma_t >= (1/2)[components(<N[S_deg2]>) + ecc_avg(G)] :: LHS(ub)=3 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] KG(15,2) reading#0: gamma_t >= (1/2)[components(<N[S_deg2]>) + ecc_avg(G)] :: LHS(ub)=3 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] KG(16,2) reading#0: gamma_t >= (1/2)[components(<N[S_deg2]>) + ecc_avg(G)] :: LHS(ub)=3 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] Paley(101) reading#0: gamma_t >= (1/2)[components(<N[S_deg2]>) + ecc_avg(G)] :: LHS(ub)=5 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] Paley(13) reading#0: gamma_t >= (1/2)[components(<N[S_deg2]>) + ecc_avg(G)] :: LHS(ub)=4 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] Paley(17) reading#0: gamma_t >= (1/2)[components(<N[S_deg2]>) + ecc_avg(G)] :: LHS(ub)=4 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] Paley(29) reading#0: gamma_t >= (1/2)[components(<N[S_deg2]>) + ecc_avg(G)] :: LHS(ub)=4 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] Paley(37) reading#0: gamma_t >= (1/2)[components(<N[S_deg2]>) + ecc_avg(G)] :: LHS(ub)=4 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] Paley(41) reading#0: gamma_t >= (1/2)[components(<N[S_deg2]>) + ecc_avg(G)] :: LHS(ub)=4 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] Paley(53) reading#0: gamma_t >= (1/2)[components(<N[S_deg2]>) + ecc_avg(G)] :: LHS(ub)=4 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] Paley(61) reading#0: gamma_t >= (1/2)[components(<N[S_deg2]>) + ecc_avg(G)] :: LHS(ub)=4 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] Paley(73) reading#0: gamma_t >= (1/2)[components(<N[S_deg2]>) + ecc_avg(G)] :: LHS(ub)=5 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] Paley(89) reading#0: gamma_t >= (1/2)[components(<N[S_deg2]>) + ecc_avg(G)] :: LHS(ub)=5 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] Paley(97) reading#0: gamma_t >= (1/2)[components(<N[S_deg2]>) + ecc_avg(G)] :: LHS(ub)=5 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] T(10) reading#0: gamma_t >= (1/2)[components(<N[S_deg2]>) + ecc_avg(G)] :: LHS(ub)=6 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] T(11) reading#0: gamma_t >= (1/2)[components(<N[S_deg2]>) + ecc_avg(G)] :: LHS(ub)=7 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] T(12) reading#0: gamma_t >= (1/2)[components(<N[S_deg2]>) + ecc_avg(G)] :: LHS(ub)=8 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] T(13) reading#0: gamma_t >= (1/2)[components(<N[S_deg2]>) + ecc_avg(G)] :: LHS(ub)=8 >= RHS(exact)=1 but kinds cannot certify hold

### id 247
statement: If G is a simple connected degree-regular graph, then γ_t(G) ≥ 2* p(G)

- [BRACKET] C7[K3] reading#0: gamma_t >= 2*p_cov(G) :: LHS(ub)=4 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] C9[K3] reading#0: gamma_t >= 2*p_cov(G) :: LHS(ub)=5 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] CMP(2) reading#0: gamma_t >= 2*p_cov(G) :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] CMP(3) reading#0: gamma_t >= 2*p_cov(G) :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] CMP(4) reading#0: gamma_t >= 2*p_cov(G) :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] CMP(5) reading#0: gamma_t >= 2*p_cov(G) :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] CMP(6) reading#0: gamma_t >= 2*p_cov(G) :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] CMP(7) reading#0: gamma_t >= 2*p_cov(G) :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] CMP(8) reading#0: gamma_t >= 2*p_cov(G) :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] CP(2) reading#0: gamma_t >= 2*p_cov(G) :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] CP(3) reading#0: gamma_t >= 2*p_cov(G) :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] CP(4) reading#0: gamma_t >= 2*p_cov(G) :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] CP(5) reading#0: gamma_t >= 2*p_cov(G) :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] CP(6) reading#0: gamma_t >= 2*p_cov(G) :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] CP(7) reading#0: gamma_t >= 2*p_cov(G) :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] CP(8) reading#0: gamma_t >= 2*p_cov(G) :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] K(3,3) reading#0: gamma_t >= 2*p_cov(G) :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] K(3,3,3) reading#0: gamma_t >= 2*p_cov(G) :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] KG(10,2) reading#0: gamma_t >= 2*p_cov(G) :: LHS(ub)=3 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] KG(11,2) reading#0: gamma_t >= 2*p_cov(G) :: LHS(ub)=3 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] KG(12,2) reading#0: gamma_t >= 2*p_cov(G) :: LHS(ub)=3 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] KG(13,2) reading#0: gamma_t >= 2*p_cov(G) :: LHS(ub)=3 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] KG(14,2) reading#0: gamma_t >= 2*p_cov(G) :: LHS(ub)=3 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] KG(15,2) reading#0: gamma_t >= 2*p_cov(G) :: LHS(ub)=3 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] KG(16,2) reading#0: gamma_t >= 2*p_cov(G) :: LHS(ub)=3 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] Paley(101) reading#0: gamma_t >= 2*p_cov(G) :: LHS(ub)=5 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] Paley(13) reading#0: gamma_t >= 2*p_cov(G) :: LHS(ub)=4 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] Paley(17) reading#0: gamma_t >= 2*p_cov(G) :: LHS(ub)=4 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] Paley(29) reading#0: gamma_t >= 2*p_cov(G) :: LHS(ub)=4 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] Paley(37) reading#0: gamma_t >= 2*p_cov(G) :: LHS(ub)=4 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] Paley(41) reading#0: gamma_t >= 2*p_cov(G) :: LHS(ub)=4 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] Paley(53) reading#0: gamma_t >= 2*p_cov(G) :: LHS(ub)=4 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] Paley(61) reading#0: gamma_t >= 2*p_cov(G) :: LHS(ub)=4 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] Paley(73) reading#0: gamma_t >= 2*p_cov(G) :: LHS(ub)=5 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] Paley(89) reading#0: gamma_t >= 2*p_cov(G) :: LHS(ub)=5 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] Paley(97) reading#0: gamma_t >= 2*p_cov(G) :: LHS(ub)=5 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] T(10) reading#0: gamma_t >= 2*p_cov(G) :: LHS(ub)=6 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] T(11) reading#0: gamma_t >= 2*p_cov(G) :: LHS(ub)=7 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] T(12) reading#0: gamma_t >= 2*p_cov(G) :: LHS(ub)=8 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] T(13) reading#0: gamma_t >= 2*p_cov(G) :: LHS(ub)=8 >= RHS(exact)=2 but kinds cannot certify hold

## batch appended 2026-08-26 06:54:31

| id | verdict | vio | hold | bracket | premise_false | undef | tag |
|---|---|---|---|---|---|---|---|
| 252 | VIOLATED_CANDIDATE | 48 | 0 | 2 | 0 | 0 |  |
| 253 | VIOLATED_CANDIDATE | 49 | 0 | 1 | 0 | 0 |  |
| 255 | VIOLATED_CANDIDATE | 12 | 0 | 38 | 0 | 0 |  |
| 256 | VIOLATED_CANDIDATE | 18 | 0 | 32 | 0 | 0 |  |
| 258 | BRACKET | 0 | 0 | 1 | 0 | 49 |  |
| 259 | BRACKET | 0 | 0 | 1 | 0 | 49 |  |
| 260 | BRACKET | 0 | 0 | 1 | 0 | 49 |  |
| 261 | BRACKET | 0 | 0 | 1 | 0 | 49 |  |
| 267 | BRACKET | 0 | 0 | 57 | 0 | 43 |  |
| 268 | BRACKET | 0 | 0 | 50 | 0 | 0 |  |

### id 252
statement: If G is a simple connected C_4 -free graph, then γ_t(G) ≥ mode_min(G)

- [VIO] C7[K3] reading#0: gamma_t >= mode_min :: gamma-style LHS<=4 < RHS=8
- [VIO] C9[K3] reading#0: gamma_t >= mode_min :: gamma-style LHS<=5 < RHS=8
- [BRACKET] CMP(2) reading#0: gamma_t >= mode_min :: LHS(ub)=2 >= RHS(exact)=1 but kinds cannot certify hold
- [VIO] CMP(3) reading#0: gamma_t >= mode_min :: gamma-style LHS<=2 < RHS=3
- [VIO] CMP(4) reading#0: gamma_t >= mode_min :: gamma-style LHS<=2 < RHS=5
- [VIO] CMP(5) reading#0: gamma_t >= mode_min :: gamma-style LHS<=2 < RHS=7
- [VIO] CMP(6) reading#0: gamma_t >= mode_min :: gamma-style LHS<=2 < RHS=9
- [VIO] CMP(7) reading#0: gamma_t >= mode_min :: gamma-style LHS<=2 < RHS=11
- [VIO] CMP(8) reading#0: gamma_t >= mode_min :: gamma-style LHS<=2 < RHS=13
- [BRACKET] CP(2) reading#0: gamma_t >= mode_min :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [VIO] CP(3) reading#0: gamma_t >= mode_min :: gamma-style LHS<=2 < RHS=4
- [VIO] CP(4) reading#0: gamma_t >= mode_min :: gamma-style LHS<=2 < RHS=6
- [VIO] CP(5) reading#0: gamma_t >= mode_min :: gamma-style LHS<=2 < RHS=8
- [VIO] CP(6) reading#0: gamma_t >= mode_min :: gamma-style LHS<=2 < RHS=10
- [VIO] CP(7) reading#0: gamma_t >= mode_min :: gamma-style LHS<=2 < RHS=12
- [VIO] CP(8) reading#0: gamma_t >= mode_min :: gamma-style LHS<=2 < RHS=14
- [VIO] K(3,3) reading#0: gamma_t >= mode_min :: gamma-style LHS<=2 < RHS=3
- [VIO] K(3,3,3) reading#0: gamma_t >= mode_min :: gamma-style LHS<=2 < RHS=6
- [VIO] KG(10,2) reading#0: gamma_t >= mode_min :: gamma-style LHS<=3 < RHS=28
- [VIO] KG(11,2) reading#0: gamma_t >= mode_min :: gamma-style LHS<=3 < RHS=36
- [VIO] KG(12,2) reading#0: gamma_t >= mode_min :: gamma-style LHS<=3 < RHS=45
- [VIO] KG(13,2) reading#0: gamma_t >= mode_min :: gamma-style LHS<=3 < RHS=55
- [VIO] KG(14,2) reading#0: gamma_t >= mode_min :: gamma-style LHS<=3 < RHS=66
- [VIO] KG(15,2) reading#0: gamma_t >= mode_min :: gamma-style LHS<=3 < RHS=78
- [VIO] KG(16,2) reading#0: gamma_t >= mode_min :: gamma-style LHS<=3 < RHS=91
- [VIO] Paley(101) reading#0: gamma_t >= mode_min :: gamma-style LHS<=5 < RHS=50
- [VIO] Paley(13) reading#0: gamma_t >= mode_min :: gamma-style LHS<=4 < RHS=6
- [VIO] Paley(17) reading#0: gamma_t >= mode_min :: gamma-style LHS<=4 < RHS=8
- [VIO] Paley(29) reading#0: gamma_t >= mode_min :: gamma-style LHS<=4 < RHS=14
- [VIO] Paley(37) reading#0: gamma_t >= mode_min :: gamma-style LHS<=4 < RHS=18
- [VIO] Paley(41) reading#0: gamma_t >= mode_min :: gamma-style LHS<=4 < RHS=20
- [VIO] Paley(53) reading#0: gamma_t >= mode_min :: gamma-style LHS<=4 < RHS=26
- [VIO] Paley(61) reading#0: gamma_t >= mode_min :: gamma-style LHS<=4 < RHS=30
- [VIO] Paley(73) reading#0: gamma_t >= mode_min :: gamma-style LHS<=5 < RHS=36
- [VIO] Paley(89) reading#0: gamma_t >= mode_min :: gamma-style LHS<=5 < RHS=44
- [VIO] Paley(97) reading#0: gamma_t >= mode_min :: gamma-style LHS<=5 < RHS=48
- [VIO] T(10) reading#0: gamma_t >= mode_min :: gamma-style LHS<=6 < RHS=16
- [VIO] T(11) reading#0: gamma_t >= mode_min :: gamma-style LHS<=7 < RHS=18
- [VIO] T(12) reading#0: gamma_t >= mode_min :: gamma-style LHS<=8 < RHS=20
- [VIO] T(13) reading#0: gamma_t >= mode_min :: gamma-style LHS<=8 < RHS=22

### id 253
statement: If G is a simple connected graph such that girth ≥ 5, then γ_t(G) ≥ 1 + mode_min(G)

- [VIO] C7[K3] reading#0: gamma_t >= 1 + mode_min :: gamma-style LHS<=4 < RHS=9
- [VIO] C9[K3] reading#0: gamma_t >= 1 + mode_min :: gamma-style LHS<=5 < RHS=9
- [BRACKET] CMP(2) reading#0: gamma_t >= 1 + mode_min :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [VIO] CMP(3) reading#0: gamma_t >= 1 + mode_min :: gamma-style LHS<=2 < RHS=4
- [VIO] CMP(4) reading#0: gamma_t >= 1 + mode_min :: gamma-style LHS<=2 < RHS=6
- [VIO] CMP(5) reading#0: gamma_t >= 1 + mode_min :: gamma-style LHS<=2 < RHS=8
- [VIO] CMP(6) reading#0: gamma_t >= 1 + mode_min :: gamma-style LHS<=2 < RHS=10
- [VIO] CMP(7) reading#0: gamma_t >= 1 + mode_min :: gamma-style LHS<=2 < RHS=12
- [VIO] CMP(8) reading#0: gamma_t >= 1 + mode_min :: gamma-style LHS<=2 < RHS=14
- [VIO] CP(2) reading#0: gamma_t >= 1 + mode_min :: gamma-style LHS<=2 < RHS=3
- [VIO] CP(3) reading#0: gamma_t >= 1 + mode_min :: gamma-style LHS<=2 < RHS=5
- [VIO] CP(4) reading#0: gamma_t >= 1 + mode_min :: gamma-style LHS<=2 < RHS=7
- [VIO] CP(5) reading#0: gamma_t >= 1 + mode_min :: gamma-style LHS<=2 < RHS=9
- [VIO] CP(6) reading#0: gamma_t >= 1 + mode_min :: gamma-style LHS<=2 < RHS=11
- [VIO] CP(7) reading#0: gamma_t >= 1 + mode_min :: gamma-style LHS<=2 < RHS=13
- [VIO] CP(8) reading#0: gamma_t >= 1 + mode_min :: gamma-style LHS<=2 < RHS=15
- [VIO] K(3,3) reading#0: gamma_t >= 1 + mode_min :: gamma-style LHS<=2 < RHS=4
- [VIO] K(3,3,3) reading#0: gamma_t >= 1 + mode_min :: gamma-style LHS<=2 < RHS=7
- [VIO] KG(10,2) reading#0: gamma_t >= 1 + mode_min :: gamma-style LHS<=3 < RHS=29
- [VIO] KG(11,2) reading#0: gamma_t >= 1 + mode_min :: gamma-style LHS<=3 < RHS=37
- [VIO] KG(12,2) reading#0: gamma_t >= 1 + mode_min :: gamma-style LHS<=3 < RHS=46
- [VIO] KG(13,2) reading#0: gamma_t >= 1 + mode_min :: gamma-style LHS<=3 < RHS=56
- [VIO] KG(14,2) reading#0: gamma_t >= 1 + mode_min :: gamma-style LHS<=3 < RHS=67
- [VIO] KG(15,2) reading#0: gamma_t >= 1 + mode_min :: gamma-style LHS<=3 < RHS=79
- [VIO] KG(16,2) reading#0: gamma_t >= 1 + mode_min :: gamma-style LHS<=3 < RHS=92
- [VIO] Paley(101) reading#0: gamma_t >= 1 + mode_min :: gamma-style LHS<=5 < RHS=51
- [VIO] Paley(13) reading#0: gamma_t >= 1 + mode_min :: gamma-style LHS<=4 < RHS=7
- [VIO] Paley(17) reading#0: gamma_t >= 1 + mode_min :: gamma-style LHS<=4 < RHS=9
- [VIO] Paley(29) reading#0: gamma_t >= 1 + mode_min :: gamma-style LHS<=4 < RHS=15
- [VIO] Paley(37) reading#0: gamma_t >= 1 + mode_min :: gamma-style LHS<=4 < RHS=19
- [VIO] Paley(41) reading#0: gamma_t >= 1 + mode_min :: gamma-style LHS<=4 < RHS=21
- [VIO] Paley(53) reading#0: gamma_t >= 1 + mode_min :: gamma-style LHS<=4 < RHS=27
- [VIO] Paley(61) reading#0: gamma_t >= 1 + mode_min :: gamma-style LHS<=4 < RHS=31
- [VIO] Paley(73) reading#0: gamma_t >= 1 + mode_min :: gamma-style LHS<=5 < RHS=37
- [VIO] Paley(89) reading#0: gamma_t >= 1 + mode_min :: gamma-style LHS<=5 < RHS=45
- [VIO] Paley(97) reading#0: gamma_t >= 1 + mode_min :: gamma-style LHS<=5 < RHS=49
- [VIO] T(10) reading#0: gamma_t >= 1 + mode_min :: gamma-style LHS<=6 < RHS=17
- [VIO] T(11) reading#0: gamma_t >= 1 + mode_min :: gamma-style LHS<=7 < RHS=19
- [VIO] T(12) reading#0: gamma_t >= 1 + mode_min :: gamma-style LHS<=8 < RHS=21
- [VIO] T(13) reading#0: gamma_t >= 1 + mode_min :: gamma-style LHS<=8 < RHS=23

### id 255
statement: If G is a simple connected graph, then γ_t(G) ≥ 2*|C|/[ maximum of {N(e): e an edge of G} ], where C is the set of vertices that are centers of G.

- [VIO] C7[K3] reading#0: gamma_t >= 2*|C|/max|N(e)| :: gamma-style LHS<=4 < RHS=21/5
- [VIO] C9[K3] reading#0: gamma_t >= 2*|C|/max|N(e)| :: gamma-style LHS<=5 < RHS=27/5
- [BRACKET] CMP(2) reading#0: gamma_t >= 2*|C|/max|N(e)| :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] CMP(3) reading#0: gamma_t >= 2*|C|/max|N(e)| :: LHS(ub)=2 >= RHS(exact)=2/3 but kinds cannot certify hold
- [BRACKET] CMP(4) reading#0: gamma_t >= 2*|C|/max|N(e)| :: LHS(ub)=2 >= RHS(exact)=2/5 but kinds cannot certify hold
- [BRACKET] CMP(5) reading#0: gamma_t >= 2*|C|/max|N(e)| :: LHS(ub)=2 >= RHS(exact)=2/7 but kinds cannot certify hold
- [BRACKET] CMP(6) reading#0: gamma_t >= 2*|C|/max|N(e)| :: LHS(ub)=2 >= RHS(exact)=2/9 but kinds cannot certify hold
- [BRACKET] CMP(7) reading#0: gamma_t >= 2*|C|/max|N(e)| :: LHS(ub)=2 >= RHS(exact)=2/11 but kinds cannot certify hold
- [BRACKET] CMP(8) reading#0: gamma_t >= 2*|C|/max|N(e)| :: LHS(ub)=2 >= RHS(exact)=2/13 but kinds cannot certify hold
- [VIO] CP(2) reading#0: gamma_t >= 2*|C|/max|N(e)| :: gamma-style LHS<=2 < RHS=4
- [VIO] CP(3) reading#0: gamma_t >= 2*|C|/max|N(e)| :: gamma-style LHS<=2 < RHS=3
- [VIO] CP(4) reading#0: gamma_t >= 2*|C|/max|N(e)| :: gamma-style LHS<=2 < RHS=8/3
- [VIO] CP(5) reading#0: gamma_t >= 2*|C|/max|N(e)| :: gamma-style LHS<=2 < RHS=5/2
- [VIO] CP(6) reading#0: gamma_t >= 2*|C|/max|N(e)| :: gamma-style LHS<=2 < RHS=12/5
- [VIO] CP(7) reading#0: gamma_t >= 2*|C|/max|N(e)| :: gamma-style LHS<=2 < RHS=7/3
- [VIO] CP(8) reading#0: gamma_t >= 2*|C|/max|N(e)| :: gamma-style LHS<=2 < RHS=16/7
- [VIO] K(3,3) reading#0: gamma_t >= 2*|C|/max|N(e)| :: gamma-style LHS<=2 < RHS=3
- [VIO] K(3,3,3) reading#0: gamma_t >= 2*|C|/max|N(e)| :: gamma-style LHS<=2 < RHS=18/7
- [BRACKET] KG(10,2) reading#0: gamma_t >= 2*|C|/max|N(e)| :: LHS(ub)=3 >= RHS(exact)=30/13 but kinds cannot certify hold
- [BRACKET] KG(11,2) reading#0: gamma_t >= 2*|C|/max|N(e)| :: LHS(ub)=3 >= RHS(exact)=110/49 but kinds cannot certify hold
- [BRACKET] KG(12,2) reading#0: gamma_t >= 2*|C|/max|N(e)| :: LHS(ub)=3 >= RHS(exact)=11/5 but kinds cannot certify hold
- [BRACKET] KG(13,2) reading#0: gamma_t >= 2*|C|/max|N(e)| :: LHS(ub)=3 >= RHS(exact)=13/6 but kinds cannot certify hold
- [BRACKET] KG(14,2) reading#0: gamma_t >= 2*|C|/max|N(e)| :: LHS(ub)=3 >= RHS(exact)=182/85 but kinds cannot certify hold
- [BRACKET] KG(15,2) reading#0: gamma_t >= 2*|C|/max|N(e)| :: LHS(ub)=3 >= RHS(exact)=70/33 but kinds cannot certify hold
- [BRACKET] KG(16,2) reading#0: gamma_t >= 2*|C|/max|N(e)| :: LHS(ub)=3 >= RHS(exact)=40/19 but kinds cannot certify hold
- [BRACKET] Paley(101) reading#0: gamma_t >= 2*|C|/max|N(e)| :: LHS(ub)=5 >= RHS(exact)=101/37 but kinds cannot certify hold
- [BRACKET] Paley(13) reading#0: gamma_t >= 2*|C|/max|N(e)| :: LHS(ub)=4 >= RHS(exact)=13/4 but kinds cannot certify hold
- [BRACKET] Paley(17) reading#0: gamma_t >= 2*|C|/max|N(e)| :: LHS(ub)=4 >= RHS(exact)=34/11 but kinds cannot certify hold
- [BRACKET] Paley(29) reading#0: gamma_t >= 2*|C|/max|N(e)| :: LHS(ub)=4 >= RHS(exact)=29/10 but kinds cannot certify hold
- [BRACKET] Paley(37) reading#0: gamma_t >= 2*|C|/max|N(e)| :: LHS(ub)=4 >= RHS(exact)=37/13 but kinds cannot certify hold
- [BRACKET] Paley(41) reading#0: gamma_t >= 2*|C|/max|N(e)| :: LHS(ub)=4 >= RHS(exact)=82/29 but kinds cannot certify hold
- [BRACKET] Paley(53) reading#0: gamma_t >= 2*|C|/max|N(e)| :: LHS(ub)=4 >= RHS(exact)=53/19 but kinds cannot certify hold
- [BRACKET] Paley(61) reading#0: gamma_t >= 2*|C|/max|N(e)| :: LHS(ub)=4 >= RHS(exact)=61/22 but kinds cannot certify hold
- [BRACKET] Paley(73) reading#0: gamma_t >= 2*|C|/max|N(e)| :: LHS(ub)=5 >= RHS(exact)=146/53 but kinds cannot certify hold
- [BRACKET] Paley(89) reading#0: gamma_t >= 2*|C|/max|N(e)| :: LHS(ub)=5 >= RHS(exact)=178/65 but kinds cannot certify hold
- [BRACKET] Paley(97) reading#0: gamma_t >= 2*|C|/max|N(e)| :: LHS(ub)=5 >= RHS(exact)=194/71 but kinds cannot certify hold
- [BRACKET] T(10) reading#0: gamma_t >= 2*|C|/max|N(e)| :: LHS(ub)=6 >= RHS(exact)=45/11 but kinds cannot certify hold
- [BRACKET] T(11) reading#0: gamma_t >= 2*|C|/max|N(e)| :: LHS(ub)=7 >= RHS(exact)=22/5 but kinds cannot certify hold
- [BRACKET] T(12) reading#0: gamma_t >= 2*|C|/max|N(e)| :: LHS(ub)=8 >= RHS(exact)=33/7 but kinds cannot certify hold
- [BRACKET] T(13) reading#0: gamma_t >= 2*|C|/max|N(e)| :: LHS(ub)=8 >= RHS(exact)=156/31 but kinds cannot certify hold

### id 256
statement: If G is a simple connected graph, then γ_t(G) ≥ 2*|N(A)|/[ maximum of {N(e): e an edge of G} ], where A is the set of vertices of minimum degree.

- [VIO] C7[K3] reading#0: gamma_t >= 2*|N(A)|/max|N(e)| :: gamma-style LHS<=4 < RHS=21/5
- [VIO] C9[K3] reading#0: gamma_t >= 2*|N(A)|/max|N(e)| :: gamma-style LHS<=5 < RHS=27/5
- [BRACKET] CMP(2) reading#0: gamma_t >= 2*|N(A)|/max|N(e)| :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [VIO] CMP(3) reading#0: gamma_t >= 2*|N(A)|/max|N(e)| :: gamma-style LHS<=2 < RHS=10/3
- [VIO] CMP(4) reading#0: gamma_t >= 2*|N(A)|/max|N(e)| :: gamma-style LHS<=2 < RHS=14/5
- [VIO] CMP(5) reading#0: gamma_t >= 2*|N(A)|/max|N(e)| :: gamma-style LHS<=2 < RHS=18/7
- [VIO] CMP(6) reading#0: gamma_t >= 2*|N(A)|/max|N(e)| :: gamma-style LHS<=2 < RHS=22/9
- [VIO] CMP(7) reading#0: gamma_t >= 2*|N(A)|/max|N(e)| :: gamma-style LHS<=2 < RHS=26/11
- [VIO] CMP(8) reading#0: gamma_t >= 2*|N(A)|/max|N(e)| :: gamma-style LHS<=2 < RHS=30/13
- [VIO] CP(2) reading#0: gamma_t >= 2*|N(A)|/max|N(e)| :: gamma-style LHS<=2 < RHS=4
- [VIO] CP(3) reading#0: gamma_t >= 2*|N(A)|/max|N(e)| :: gamma-style LHS<=2 < RHS=3
- [VIO] CP(4) reading#0: gamma_t >= 2*|N(A)|/max|N(e)| :: gamma-style LHS<=2 < RHS=8/3
- [VIO] CP(5) reading#0: gamma_t >= 2*|N(A)|/max|N(e)| :: gamma-style LHS<=2 < RHS=5/2
- [VIO] CP(6) reading#0: gamma_t >= 2*|N(A)|/max|N(e)| :: gamma-style LHS<=2 < RHS=12/5
- [VIO] CP(7) reading#0: gamma_t >= 2*|N(A)|/max|N(e)| :: gamma-style LHS<=2 < RHS=7/3
- [VIO] CP(8) reading#0: gamma_t >= 2*|N(A)|/max|N(e)| :: gamma-style LHS<=2 < RHS=16/7
- [VIO] K(3,3) reading#0: gamma_t >= 2*|N(A)|/max|N(e)| :: gamma-style LHS<=2 < RHS=3
- [VIO] K(3,3,3) reading#0: gamma_t >= 2*|N(A)|/max|N(e)| :: gamma-style LHS<=2 < RHS=18/7
- [BRACKET] KG(10,2) reading#0: gamma_t >= 2*|N(A)|/max|N(e)| :: LHS(ub)=3 >= RHS(exact)=30/13 but kinds cannot certify hold
- [BRACKET] KG(11,2) reading#0: gamma_t >= 2*|N(A)|/max|N(e)| :: LHS(ub)=3 >= RHS(exact)=110/49 but kinds cannot certify hold
- [BRACKET] KG(12,2) reading#0: gamma_t >= 2*|N(A)|/max|N(e)| :: LHS(ub)=3 >= RHS(exact)=11/5 but kinds cannot certify hold
- [BRACKET] KG(13,2) reading#0: gamma_t >= 2*|N(A)|/max|N(e)| :: LHS(ub)=3 >= RHS(exact)=13/6 but kinds cannot certify hold
- [BRACKET] KG(14,2) reading#0: gamma_t >= 2*|N(A)|/max|N(e)| :: LHS(ub)=3 >= RHS(exact)=182/85 but kinds cannot certify hold
- [BRACKET] KG(15,2) reading#0: gamma_t >= 2*|N(A)|/max|N(e)| :: LHS(ub)=3 >= RHS(exact)=70/33 but kinds cannot certify hold
- [BRACKET] KG(16,2) reading#0: gamma_t >= 2*|N(A)|/max|N(e)| :: LHS(ub)=3 >= RHS(exact)=40/19 but kinds cannot certify hold
- [BRACKET] Paley(101) reading#0: gamma_t >= 2*|N(A)|/max|N(e)| :: LHS(ub)=5 >= RHS(exact)=101/37 but kinds cannot certify hold
- [BRACKET] Paley(13) reading#0: gamma_t >= 2*|N(A)|/max|N(e)| :: LHS(ub)=4 >= RHS(exact)=13/4 but kinds cannot certify hold
- [BRACKET] Paley(17) reading#0: gamma_t >= 2*|N(A)|/max|N(e)| :: LHS(ub)=4 >= RHS(exact)=34/11 but kinds cannot certify hold
- [BRACKET] Paley(29) reading#0: gamma_t >= 2*|N(A)|/max|N(e)| :: LHS(ub)=4 >= RHS(exact)=29/10 but kinds cannot certify hold
- [BRACKET] Paley(37) reading#0: gamma_t >= 2*|N(A)|/max|N(e)| :: LHS(ub)=4 >= RHS(exact)=37/13 but kinds cannot certify hold
- [BRACKET] Paley(41) reading#0: gamma_t >= 2*|N(A)|/max|N(e)| :: LHS(ub)=4 >= RHS(exact)=82/29 but kinds cannot certify hold
- [BRACKET] Paley(53) reading#0: gamma_t >= 2*|N(A)|/max|N(e)| :: LHS(ub)=4 >= RHS(exact)=53/19 but kinds cannot certify hold
- [BRACKET] Paley(61) reading#0: gamma_t >= 2*|N(A)|/max|N(e)| :: LHS(ub)=4 >= RHS(exact)=61/22 but kinds cannot certify hold
- [BRACKET] Paley(73) reading#0: gamma_t >= 2*|N(A)|/max|N(e)| :: LHS(ub)=5 >= RHS(exact)=146/53 but kinds cannot certify hold
- [BRACKET] Paley(89) reading#0: gamma_t >= 2*|N(A)|/max|N(e)| :: LHS(ub)=5 >= RHS(exact)=178/65 but kinds cannot certify hold
- [BRACKET] Paley(97) reading#0: gamma_t >= 2*|N(A)|/max|N(e)| :: LHS(ub)=5 >= RHS(exact)=194/71 but kinds cannot certify hold
- [BRACKET] T(10) reading#0: gamma_t >= 2*|N(A)|/max|N(e)| :: LHS(ub)=6 >= RHS(exact)=45/11 but kinds cannot certify hold
- [BRACKET] T(11) reading#0: gamma_t >= 2*|N(A)|/max|N(e)| :: LHS(ub)=7 >= RHS(exact)=22/5 but kinds cannot certify hold
- [BRACKET] T(12) reading#0: gamma_t >= 2*|N(A)|/max|N(e)| :: LHS(ub)=8 >= RHS(exact)=33/7 but kinds cannot certify hold
- [BRACKET] T(13) reading#0: gamma_t >= 2*|N(A)|/max|N(e)| :: LHS(ub)=8 >= RHS(exact)=156/31 but kinds cannot certify hold

### id 258
statement: If G is a simple connected graph, then γ_t(G) ≥ 2*even_max(G)/L(G), where even_max(G) = maximum {even(w): even(w) = |{u: dist(w,u} is even}|}.

- [BRACKET] CMP(2) reading#0: gamma_t >= 2*even_max/L(G) :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold

### id 259
statement: If G is a simple connected graph, then γ_t(G) ≥ 2*|N(M)-M|/L(G), where M is the set of vertices of maximum degree.

- [BRACKET] CMP(2) reading#0: gamma_t >= 2*|N(M)-M|/L(G) :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold

### id 260
statement: If G is a simple connected graph, then γ_t(G) ≥ 2*|N(B)-B|/L(G), where B is the set of vertices of maximum maximum eccentricity.

- [BRACKET] CMP(2) reading#0: gamma_t >= 2*|N(B)-B|/L(G) :: LHS(ub)=2 >= RHS(exact)=1 but kinds cannot certify hold

### id 261
statement: If G is a simple connected graph, then γ_t(G) ≥ 2*|N(S)-S|/L(G), where S is the set of vertices of degree two.

- [BRACKET] CMP(2) reading#0: gamma_t >= 2*|N(S_deg2)-S_deg2|/L(G) :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold

### id 267
statement: If G is a simple connected graph such that girth(G) ≥ 5, then γ_t(G) ≥ CEIL[dist_avg(A,V)], where A is the set of minimum degree vertices.

- [BRACKET] C7[K3] reading#0: gamma_t >= ceil[dist_avg(A,V)] pairs-average :: LHS(ub)=4 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] C9[K3] reading#0: gamma_t >= ceil[dist_avg(A,V)] pairs-average :: LHS(ub)=5 >= RHS(exact)=3 but kinds cannot certify hold
- [BRACKET] CMP(2) reading#0: gamma_t >= ceil[dist_avg(A,V)] pairs-average :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] CMP(2) reading#1: alt per-vertex average :: LHS(ub)=2 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] CMP(3) reading#0: gamma_t >= ceil[dist_avg(A,V)] pairs-average :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] CMP(3) reading#1: alt per-vertex average :: LHS(ub)=2 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] CMP(4) reading#0: gamma_t >= ceil[dist_avg(A,V)] pairs-average :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] CMP(4) reading#1: alt per-vertex average :: LHS(ub)=2 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] CMP(5) reading#0: gamma_t >= ceil[dist_avg(A,V)] pairs-average :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] CMP(5) reading#1: alt per-vertex average :: LHS(ub)=2 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] CMP(6) reading#0: gamma_t >= ceil[dist_avg(A,V)] pairs-average :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] CMP(6) reading#1: alt per-vertex average :: LHS(ub)=2 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] CMP(7) reading#0: gamma_t >= ceil[dist_avg(A,V)] pairs-average :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] CMP(7) reading#1: alt per-vertex average :: LHS(ub)=2 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] CMP(8) reading#0: gamma_t >= ceil[dist_avg(A,V)] pairs-average :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] CMP(8) reading#1: alt per-vertex average :: LHS(ub)=2 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] CP(2) reading#0: gamma_t >= ceil[dist_avg(A,V)] pairs-average :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] CP(3) reading#0: gamma_t >= ceil[dist_avg(A,V)] pairs-average :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] CP(4) reading#0: gamma_t >= ceil[dist_avg(A,V)] pairs-average :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] CP(5) reading#0: gamma_t >= ceil[dist_avg(A,V)] pairs-average :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] CP(6) reading#0: gamma_t >= ceil[dist_avg(A,V)] pairs-average :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] CP(7) reading#0: gamma_t >= ceil[dist_avg(A,V)] pairs-average :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] CP(8) reading#0: gamma_t >= ceil[dist_avg(A,V)] pairs-average :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] K(3,3) reading#0: gamma_t >= ceil[dist_avg(A,V)] pairs-average :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] K(3,3,3) reading#0: gamma_t >= ceil[dist_avg(A,V)] pairs-average :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] KG(10,2) reading#0: gamma_t >= ceil[dist_avg(A,V)] pairs-average :: LHS(ub)=3 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] KG(11,2) reading#0: gamma_t >= ceil[dist_avg(A,V)] pairs-average :: LHS(ub)=3 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] KG(12,2) reading#0: gamma_t >= ceil[dist_avg(A,V)] pairs-average :: LHS(ub)=3 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] KG(13,2) reading#0: gamma_t >= ceil[dist_avg(A,V)] pairs-average :: LHS(ub)=3 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] KG(14,2) reading#0: gamma_t >= ceil[dist_avg(A,V)] pairs-average :: LHS(ub)=3 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] KG(15,2) reading#0: gamma_t >= ceil[dist_avg(A,V)] pairs-average :: LHS(ub)=3 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] KG(16,2) reading#0: gamma_t >= ceil[dist_avg(A,V)] pairs-average :: LHS(ub)=3 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] Paley(101) reading#0: gamma_t >= ceil[dist_avg(A,V)] pairs-average :: LHS(ub)=5 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] Paley(13) reading#0: gamma_t >= ceil[dist_avg(A,V)] pairs-average :: LHS(ub)=4 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] Paley(17) reading#0: gamma_t >= ceil[dist_avg(A,V)] pairs-average :: LHS(ub)=4 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] Paley(29) reading#0: gamma_t >= ceil[dist_avg(A,V)] pairs-average :: LHS(ub)=4 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] Paley(37) reading#0: gamma_t >= ceil[dist_avg(A,V)] pairs-average :: LHS(ub)=4 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] Paley(41) reading#0: gamma_t >= ceil[dist_avg(A,V)] pairs-average :: LHS(ub)=4 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] Paley(53) reading#0: gamma_t >= ceil[dist_avg(A,V)] pairs-average :: LHS(ub)=4 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] Paley(61) reading#0: gamma_t >= ceil[dist_avg(A,V)] pairs-average :: LHS(ub)=4 >= RHS(exact)=2 but kinds cannot certify hold

### id 268
statement: If G is a simple connected graph, then γ_t(G) ≥ FLOOR[1+dist_avg(C)], where C is the set of center vertices.

- [BRACKET] C7[K3] reading#0: gamma_t >= floor[1 + dist_avg(C within)] :: LHS(ub)=4 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] C9[K3] reading#0: gamma_t >= floor[1 + dist_avg(C within)] :: LHS(ub)=5 >= RHS(exact)=3 but kinds cannot certify hold
- [BRACKET] CMP(2) reading#0: gamma_t >= floor[1 + dist_avg(C within)] :: LHS(ub)=2 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] CMP(3) reading#0: gamma_t >= floor[1 + dist_avg(C within)] :: LHS(ub)=2 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] CMP(4) reading#0: gamma_t >= floor[1 + dist_avg(C within)] :: LHS(ub)=2 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] CMP(5) reading#0: gamma_t >= floor[1 + dist_avg(C within)] :: LHS(ub)=2 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] CMP(6) reading#0: gamma_t >= floor[1 + dist_avg(C within)] :: LHS(ub)=2 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] CMP(7) reading#0: gamma_t >= floor[1 + dist_avg(C within)] :: LHS(ub)=2 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] CMP(8) reading#0: gamma_t >= floor[1 + dist_avg(C within)] :: LHS(ub)=2 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] CP(2) reading#0: gamma_t >= floor[1 + dist_avg(C within)] :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] CP(3) reading#0: gamma_t >= floor[1 + dist_avg(C within)] :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] CP(4) reading#0: gamma_t >= floor[1 + dist_avg(C within)] :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] CP(5) reading#0: gamma_t >= floor[1 + dist_avg(C within)] :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] CP(6) reading#0: gamma_t >= floor[1 + dist_avg(C within)] :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] CP(7) reading#0: gamma_t >= floor[1 + dist_avg(C within)] :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] CP(8) reading#0: gamma_t >= floor[1 + dist_avg(C within)] :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] K(3,3) reading#0: gamma_t >= floor[1 + dist_avg(C within)] :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] K(3,3,3) reading#0: gamma_t >= floor[1 + dist_avg(C within)] :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] KG(10,2) reading#0: gamma_t >= floor[1 + dist_avg(C within)] :: LHS(ub)=3 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] KG(11,2) reading#0: gamma_t >= floor[1 + dist_avg(C within)] :: LHS(ub)=3 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] KG(12,2) reading#0: gamma_t >= floor[1 + dist_avg(C within)] :: LHS(ub)=3 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] KG(13,2) reading#0: gamma_t >= floor[1 + dist_avg(C within)] :: LHS(ub)=3 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] KG(14,2) reading#0: gamma_t >= floor[1 + dist_avg(C within)] :: LHS(ub)=3 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] KG(15,2) reading#0: gamma_t >= floor[1 + dist_avg(C within)] :: LHS(ub)=3 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] KG(16,2) reading#0: gamma_t >= floor[1 + dist_avg(C within)] :: LHS(ub)=3 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] Paley(101) reading#0: gamma_t >= floor[1 + dist_avg(C within)] :: LHS(ub)=5 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] Paley(13) reading#0: gamma_t >= floor[1 + dist_avg(C within)] :: LHS(ub)=4 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] Paley(17) reading#0: gamma_t >= floor[1 + dist_avg(C within)] :: LHS(ub)=4 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] Paley(29) reading#0: gamma_t >= floor[1 + dist_avg(C within)] :: LHS(ub)=4 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] Paley(37) reading#0: gamma_t >= floor[1 + dist_avg(C within)] :: LHS(ub)=4 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] Paley(41) reading#0: gamma_t >= floor[1 + dist_avg(C within)] :: LHS(ub)=4 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] Paley(53) reading#0: gamma_t >= floor[1 + dist_avg(C within)] :: LHS(ub)=4 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] Paley(61) reading#0: gamma_t >= floor[1 + dist_avg(C within)] :: LHS(ub)=4 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] Paley(73) reading#0: gamma_t >= floor[1 + dist_avg(C within)] :: LHS(ub)=5 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] Paley(89) reading#0: gamma_t >= floor[1 + dist_avg(C within)] :: LHS(ub)=5 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] Paley(97) reading#0: gamma_t >= floor[1 + dist_avg(C within)] :: LHS(ub)=5 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] T(10) reading#0: gamma_t >= floor[1 + dist_avg(C within)] :: LHS(ub)=6 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] T(11) reading#0: gamma_t >= floor[1 + dist_avg(C within)] :: LHS(ub)=7 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] T(12) reading#0: gamma_t >= floor[1 + dist_avg(C within)] :: LHS(ub)=8 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] T(13) reading#0: gamma_t >= floor[1 + dist_avg(C within)] :: LHS(ub)=8 >= RHS(exact)=2 but kinds cannot certify hold

## batch appended 2026-08-26 06:54:31

| id | verdict | vio | hold | bracket | premise_false | undef | tag |
|---|---|---|---|---|---|---|---|
| 269 | VIOLATED_CANDIDATE | 9 | 0 | 41 | 0 | 0 |  |
| 271 | BRACKET | 0 | 0 | 50 | 0 | 0 |  |
| 281 | HOLDS | 0 | 50 | 0 | 0 | 0 |  |
| 287 | HOLDS | 0 | 50 | 0 | 0 | 0 |  |
| 290 | HOLDS | 0 | 50 | 0 | 0 | 0 |  |
| 291 | BRACKET | 0 | 99 | 1 | 0 | 0 | EXTERNALLY_RESOLVED |
| 298 | HOLDS | 0 | 50 | 0 | 0 | 0 |  |
| 299 | HOLDS | 0 | 50 | 0 | 0 | 0 |  |
| 300 | HOLDS | 0 | 50 | 0 | 0 | 0 | EXTERNALLY_RESOLVED |
| 302 | HOLDS | 0 | 50 | 0 | 0 | 0 |  |

### id 269
statement: If G is a simple connected C_4 -free graph, then γ_t(G) ≥ CEIL[1+dist_avg(C)], where C is the set of center vertices.

- [BRACKET] C7[K3] reading#0: gamma_t >= ceil[1 + dist_avg(C within)] :: LHS(ub)=4 >= RHS(exact)=3 but kinds cannot certify hold
- [BRACKET] C9[K3] reading#0: gamma_t >= ceil[1 + dist_avg(C within)] :: LHS(ub)=5 >= RHS(exact)=4 but kinds cannot certify hold
- [BRACKET] CMP(2) reading#0: gamma_t >= ceil[1 + dist_avg(C within)] :: LHS(ub)=2 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] CMP(3) reading#0: gamma_t >= ceil[1 + dist_avg(C within)] :: LHS(ub)=2 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] CMP(4) reading#0: gamma_t >= ceil[1 + dist_avg(C within)] :: LHS(ub)=2 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] CMP(5) reading#0: gamma_t >= ceil[1 + dist_avg(C within)] :: LHS(ub)=2 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] CMP(6) reading#0: gamma_t >= ceil[1 + dist_avg(C within)] :: LHS(ub)=2 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] CMP(7) reading#0: gamma_t >= ceil[1 + dist_avg(C within)] :: LHS(ub)=2 >= RHS(exact)=1 but kinds cannot certify hold
- [BRACKET] CMP(8) reading#0: gamma_t >= ceil[1 + dist_avg(C within)] :: LHS(ub)=2 >= RHS(exact)=1 but kinds cannot certify hold
- [VIO] CP(2) reading#0: gamma_t >= ceil[1 + dist_avg(C within)] :: gamma-style LHS<=2 < RHS=3
- [VIO] CP(3) reading#0: gamma_t >= ceil[1 + dist_avg(C within)] :: gamma-style LHS<=2 < RHS=3
- [VIO] CP(4) reading#0: gamma_t >= ceil[1 + dist_avg(C within)] :: gamma-style LHS<=2 < RHS=3
- [VIO] CP(5) reading#0: gamma_t >= ceil[1 + dist_avg(C within)] :: gamma-style LHS<=2 < RHS=3
- [VIO] CP(6) reading#0: gamma_t >= ceil[1 + dist_avg(C within)] :: gamma-style LHS<=2 < RHS=3
- [VIO] CP(7) reading#0: gamma_t >= ceil[1 + dist_avg(C within)] :: gamma-style LHS<=2 < RHS=3
- [VIO] CP(8) reading#0: gamma_t >= ceil[1 + dist_avg(C within)] :: gamma-style LHS<=2 < RHS=3
- [VIO] K(3,3) reading#0: gamma_t >= ceil[1 + dist_avg(C within)] :: gamma-style LHS<=2 < RHS=3
- [VIO] K(3,3,3) reading#0: gamma_t >= ceil[1 + dist_avg(C within)] :: gamma-style LHS<=2 < RHS=3
- [BRACKET] KG(10,2) reading#0: gamma_t >= ceil[1 + dist_avg(C within)] :: LHS(ub)=3 >= RHS(exact)=3 but kinds cannot certify hold
- [BRACKET] KG(11,2) reading#0: gamma_t >= ceil[1 + dist_avg(C within)] :: LHS(ub)=3 >= RHS(exact)=3 but kinds cannot certify hold
- [BRACKET] KG(12,2) reading#0: gamma_t >= ceil[1 + dist_avg(C within)] :: LHS(ub)=3 >= RHS(exact)=3 but kinds cannot certify hold
- [BRACKET] KG(13,2) reading#0: gamma_t >= ceil[1 + dist_avg(C within)] :: LHS(ub)=3 >= RHS(exact)=3 but kinds cannot certify hold
- [BRACKET] KG(14,2) reading#0: gamma_t >= ceil[1 + dist_avg(C within)] :: LHS(ub)=3 >= RHS(exact)=3 but kinds cannot certify hold
- [BRACKET] KG(15,2) reading#0: gamma_t >= ceil[1 + dist_avg(C within)] :: LHS(ub)=3 >= RHS(exact)=3 but kinds cannot certify hold
- [BRACKET] KG(16,2) reading#0: gamma_t >= ceil[1 + dist_avg(C within)] :: LHS(ub)=3 >= RHS(exact)=3 but kinds cannot certify hold
- [BRACKET] Paley(101) reading#0: gamma_t >= ceil[1 + dist_avg(C within)] :: LHS(ub)=5 >= RHS(exact)=3 but kinds cannot certify hold
- [BRACKET] Paley(13) reading#0: gamma_t >= ceil[1 + dist_avg(C within)] :: LHS(ub)=4 >= RHS(exact)=3 but kinds cannot certify hold
- [BRACKET] Paley(17) reading#0: gamma_t >= ceil[1 + dist_avg(C within)] :: LHS(ub)=4 >= RHS(exact)=3 but kinds cannot certify hold
- [BRACKET] Paley(29) reading#0: gamma_t >= ceil[1 + dist_avg(C within)] :: LHS(ub)=4 >= RHS(exact)=3 but kinds cannot certify hold
- [BRACKET] Paley(37) reading#0: gamma_t >= ceil[1 + dist_avg(C within)] :: LHS(ub)=4 >= RHS(exact)=3 but kinds cannot certify hold
- [BRACKET] Paley(41) reading#0: gamma_t >= ceil[1 + dist_avg(C within)] :: LHS(ub)=4 >= RHS(exact)=3 but kinds cannot certify hold
- [BRACKET] Paley(53) reading#0: gamma_t >= ceil[1 + dist_avg(C within)] :: LHS(ub)=4 >= RHS(exact)=3 but kinds cannot certify hold
- [BRACKET] Paley(61) reading#0: gamma_t >= ceil[1 + dist_avg(C within)] :: LHS(ub)=4 >= RHS(exact)=3 but kinds cannot certify hold
- [BRACKET] Paley(73) reading#0: gamma_t >= ceil[1 + dist_avg(C within)] :: LHS(ub)=5 >= RHS(exact)=3 but kinds cannot certify hold
- [BRACKET] Paley(89) reading#0: gamma_t >= ceil[1 + dist_avg(C within)] :: LHS(ub)=5 >= RHS(exact)=3 but kinds cannot certify hold
- [BRACKET] Paley(97) reading#0: gamma_t >= ceil[1 + dist_avg(C within)] :: LHS(ub)=5 >= RHS(exact)=3 but kinds cannot certify hold
- [BRACKET] T(10) reading#0: gamma_t >= ceil[1 + dist_avg(C within)] :: LHS(ub)=6 >= RHS(exact)=3 but kinds cannot certify hold
- [BRACKET] T(11) reading#0: gamma_t >= ceil[1 + dist_avg(C within)] :: LHS(ub)=7 >= RHS(exact)=3 but kinds cannot certify hold
- [BRACKET] T(12) reading#0: gamma_t >= ceil[1 + dist_avg(C within)] :: LHS(ub)=8 >= RHS(exact)=3 but kinds cannot certify hold
- [BRACKET] T(13) reading#0: gamma_t >= ceil[1 + dist_avg(C within)] :: LHS(ub)=8 >= RHS(exact)=3 but kinds cannot certify hold

### id 271
statement: If G is a simple connected graph, then γ_t(G) ≥ CEIL[SQRT[2*dist_max(M)]], where M is the set of vertices of maximum degree.

- [BRACKET] C7[K3] reading#0: gamma_t >= ceil[sqrt(2*dist_max(M))] :: LHS(ub)=4 >= RHS(exact)=3 but kinds cannot certify hold
- [BRACKET] C9[K3] reading#0: gamma_t >= ceil[sqrt(2*dist_max(M))] :: LHS(ub)=5 >= RHS(exact)=3 but kinds cannot certify hold
- [BRACKET] CMP(2) reading#0: gamma_t >= ceil[sqrt(2*dist_max(M))] :: LHS(ub)=2 >= RHS(exact)=0 but kinds cannot certify hold
- [BRACKET] CMP(3) reading#0: gamma_t >= ceil[sqrt(2*dist_max(M))] :: LHS(ub)=2 >= RHS(exact)=0 but kinds cannot certify hold
- [BRACKET] CMP(4) reading#0: gamma_t >= ceil[sqrt(2*dist_max(M))] :: LHS(ub)=2 >= RHS(exact)=0 but kinds cannot certify hold
- [BRACKET] CMP(5) reading#0: gamma_t >= ceil[sqrt(2*dist_max(M))] :: LHS(ub)=2 >= RHS(exact)=0 but kinds cannot certify hold
- [BRACKET] CMP(6) reading#0: gamma_t >= ceil[sqrt(2*dist_max(M))] :: LHS(ub)=2 >= RHS(exact)=0 but kinds cannot certify hold
- [BRACKET] CMP(7) reading#0: gamma_t >= ceil[sqrt(2*dist_max(M))] :: LHS(ub)=2 >= RHS(exact)=0 but kinds cannot certify hold
- [BRACKET] CMP(8) reading#0: gamma_t >= ceil[sqrt(2*dist_max(M))] :: LHS(ub)=2 >= RHS(exact)=0 but kinds cannot certify hold
- [BRACKET] CP(2) reading#0: gamma_t >= ceil[sqrt(2*dist_max(M))] :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] CP(3) reading#0: gamma_t >= ceil[sqrt(2*dist_max(M))] :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] CP(4) reading#0: gamma_t >= ceil[sqrt(2*dist_max(M))] :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] CP(5) reading#0: gamma_t >= ceil[sqrt(2*dist_max(M))] :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] CP(6) reading#0: gamma_t >= ceil[sqrt(2*dist_max(M))] :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] CP(7) reading#0: gamma_t >= ceil[sqrt(2*dist_max(M))] :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] CP(8) reading#0: gamma_t >= ceil[sqrt(2*dist_max(M))] :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] K(3,3) reading#0: gamma_t >= ceil[sqrt(2*dist_max(M))] :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] K(3,3,3) reading#0: gamma_t >= ceil[sqrt(2*dist_max(M))] :: LHS(ub)=2 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] KG(10,2) reading#0: gamma_t >= ceil[sqrt(2*dist_max(M))] :: LHS(ub)=3 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] KG(11,2) reading#0: gamma_t >= ceil[sqrt(2*dist_max(M))] :: LHS(ub)=3 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] KG(12,2) reading#0: gamma_t >= ceil[sqrt(2*dist_max(M))] :: LHS(ub)=3 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] KG(13,2) reading#0: gamma_t >= ceil[sqrt(2*dist_max(M))] :: LHS(ub)=3 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] KG(14,2) reading#0: gamma_t >= ceil[sqrt(2*dist_max(M))] :: LHS(ub)=3 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] KG(15,2) reading#0: gamma_t >= ceil[sqrt(2*dist_max(M))] :: LHS(ub)=3 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] KG(16,2) reading#0: gamma_t >= ceil[sqrt(2*dist_max(M))] :: LHS(ub)=3 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] Paley(101) reading#0: gamma_t >= ceil[sqrt(2*dist_max(M))] :: LHS(ub)=5 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] Paley(13) reading#0: gamma_t >= ceil[sqrt(2*dist_max(M))] :: LHS(ub)=4 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] Paley(17) reading#0: gamma_t >= ceil[sqrt(2*dist_max(M))] :: LHS(ub)=4 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] Paley(29) reading#0: gamma_t >= ceil[sqrt(2*dist_max(M))] :: LHS(ub)=4 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] Paley(37) reading#0: gamma_t >= ceil[sqrt(2*dist_max(M))] :: LHS(ub)=4 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] Paley(41) reading#0: gamma_t >= ceil[sqrt(2*dist_max(M))] :: LHS(ub)=4 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] Paley(53) reading#0: gamma_t >= ceil[sqrt(2*dist_max(M))] :: LHS(ub)=4 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] Paley(61) reading#0: gamma_t >= ceil[sqrt(2*dist_max(M))] :: LHS(ub)=4 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] Paley(73) reading#0: gamma_t >= ceil[sqrt(2*dist_max(M))] :: LHS(ub)=5 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] Paley(89) reading#0: gamma_t >= ceil[sqrt(2*dist_max(M))] :: LHS(ub)=5 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] Paley(97) reading#0: gamma_t >= ceil[sqrt(2*dist_max(M))] :: LHS(ub)=5 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] T(10) reading#0: gamma_t >= ceil[sqrt(2*dist_max(M))] :: LHS(ub)=6 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] T(11) reading#0: gamma_t >= ceil[sqrt(2*dist_max(M))] :: LHS(ub)=7 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] T(12) reading#0: gamma_t >= ceil[sqrt(2*dist_max(M))] :: LHS(ub)=8 >= RHS(exact)=2 but kinds cannot certify hold
- [BRACKET] T(13) reading#0: gamma_t >= ceil[sqrt(2*dist_max(M))] :: LHS(ub)=8 >= RHS(exact)=2 but kinds cannot certify hold

### id 291
statement: If G is a simple connected graph such that n(G)> 2, then γ_t(G) ≤ k + frequency t_min(v), where k is the first step in which a zero appears in the Havil-Hakimi process.

- [BRACKET] CMP(2) reading#1: alt: HH_k + T_min :: LHS(ub)=2 > RHS(exact)=1; bounds insufficient

## batch appended 2026-08-26 06:54:31

| id | verdict | vio | hold | bracket | premise_false | undef | tag |
|---|---|---|---|---|---|---|---|
| 304 | BRACKET | 0 | 49 | 1 | 0 | 0 |  |
| 305 | BRACKET | 0 | 34 | 16 | 0 | 0 |  |
| 308 | BRACKET | 0 | 49 | 1 | 0 | 0 |  |
| 309 | BRACKET | 0 | 7 | 43 | 0 | 0 | KILLED_PRIOR_CAMPAIGN |
| 310 | HOLDS | 0 | 50 | 0 | 0 | 0 |  |
| 314 | BRACKET | 0 | 0 | 10 | 40 | 0 |  |
| 316 | BRACKET | 0 | 0 | 1 | 49 | 0 |  |
| 317 | BRACKET | 0 | 0 | 12 | 38 | 0 |  |
| 318 | BRACKET | 0 | 0 | 3 | 47 | 0 |  |
| 319 | BRACKET | 0 | 0 | 7 | 43 | 0 |  |

### id 304
statement: If G is a simple connected graph such that n(G)> 2, then γ_t(G) ≤ (1/2)*[(frequency of λ_max( bar(G) )) + maximum of N_bar(G)(e)]

- [BRACKET] CMP(2) reading#0: gamma_t <= (freq(lambda_max(bar)) + max|N_bar(e)|)/2 :: LHS(ub)=2 > RHS(exact)=1; bounds insufficient

### id 305
statement: If G is a simple connected graph such that n(G)> 2, then γ_t(G) ≤ CEIL[(2/3)*maximum of |N_bar(G)(e)|]

- [BRACKET] CMP(2) reading#0: gamma_t <= ceil[(2/3)*max|N_bar(e)|] :: LHS(ub)=2 > RHS(exact)=0; bounds insufficient
- [BRACKET] CMP(3) reading#0: gamma_t <= ceil[(2/3)*max|N_bar(e)|] :: LHS(ub)=2 > RHS(exact)=0; bounds insufficient
- [BRACKET] CMP(4) reading#0: gamma_t <= ceil[(2/3)*max|N_bar(e)|] :: LHS(ub)=2 > RHS(exact)=0; bounds insufficient
- [BRACKET] CMP(5) reading#0: gamma_t <= ceil[(2/3)*max|N_bar(e)|] :: LHS(ub)=2 > RHS(exact)=0; bounds insufficient
- [BRACKET] CMP(6) reading#0: gamma_t <= ceil[(2/3)*max|N_bar(e)|] :: LHS(ub)=2 > RHS(exact)=0; bounds insufficient
- [BRACKET] CMP(7) reading#0: gamma_t <= ceil[(2/3)*max|N_bar(e)|] :: LHS(ub)=2 > RHS(exact)=0; bounds insufficient
- [BRACKET] CMP(8) reading#0: gamma_t <= ceil[(2/3)*max|N_bar(e)|] :: LHS(ub)=2 > RHS(exact)=0; bounds insufficient
- [BRACKET] CP(2) reading#0: gamma_t <= ceil[(2/3)*max|N_bar(e)|] :: LHS(ub)=2 > RHS(exact)=0; bounds insufficient
- [BRACKET] CP(3) reading#0: gamma_t <= ceil[(2/3)*max|N_bar(e)|] :: LHS(ub)=2 > RHS(exact)=0; bounds insufficient
- [BRACKET] CP(4) reading#0: gamma_t <= ceil[(2/3)*max|N_bar(e)|] :: LHS(ub)=2 > RHS(exact)=0; bounds insufficient
- [BRACKET] CP(5) reading#0: gamma_t <= ceil[(2/3)*max|N_bar(e)|] :: LHS(ub)=2 > RHS(exact)=0; bounds insufficient
- [BRACKET] CP(6) reading#0: gamma_t <= ceil[(2/3)*max|N_bar(e)|] :: LHS(ub)=2 > RHS(exact)=0; bounds insufficient
- [BRACKET] CP(7) reading#0: gamma_t <= ceil[(2/3)*max|N_bar(e)|] :: LHS(ub)=2 > RHS(exact)=0; bounds insufficient
- [BRACKET] CP(8) reading#0: gamma_t <= ceil[(2/3)*max|N_bar(e)|] :: LHS(ub)=2 > RHS(exact)=0; bounds insufficient
- [BRACKET] K(3,3) reading#0: gamma_t <= ceil[(2/3)*max|N_bar(e)|] :: LHS(ub)=2 > RHS(exact)=1; bounds insufficient
- [BRACKET] K(3,3,3) reading#0: gamma_t <= ceil[(2/3)*max|N_bar(e)|] :: LHS(ub)=2 > RHS(exact)=1; bounds insufficient

### id 308
statement: If G is a simple connected graph such that n(G)> 2, then γ_t(G) ≤ (1/2)*[maxine(G) + minimum of |N_bar(G)(e)|]

- [BRACKET] CMP(2) reading#0: gamma_t <= (maxine + min|N_bar(e)|)/2 :: LHS(ub)=2 > RHS(exact)=3/2; bounds insufficient

### id 309
statement: If G is a simple connected graph such that n(G)> 2, then γ_t(G) ≤ (1/2)*[maximum {dist_even(v) - even horizontal(v): v in V(G)} + minimum of |N_bar(G)(e)|]

- [BRACKET] CMP(2) reading#0: gamma_t <= (1/2)[max(dist_even - even_horizontal) + min|N_bar(e)|]  [KILLED 2026-07-25] :: LHS(ub)=2 > RHS(exact)=1; bounds insufficient
- [BRACKET] CMP(3) reading#0: gamma_t <= (1/2)[max(dist_even - even_horizontal) + min|N_bar(e)|]  [KILLED 2026-07-25] :: LHS(ub)=2 > RHS(exact)=1; bounds insufficient
- [BRACKET] CMP(4) reading#0: gamma_t <= (1/2)[max(dist_even - even_horizontal) + min|N_bar(e)|]  [KILLED 2026-07-25] :: LHS(ub)=2 > RHS(exact)=1; bounds insufficient
- [BRACKET] CMP(5) reading#0: gamma_t <= (1/2)[max(dist_even - even_horizontal) + min|N_bar(e)|]  [KILLED 2026-07-25] :: LHS(ub)=2 > RHS(exact)=1; bounds insufficient
- [BRACKET] CMP(6) reading#0: gamma_t <= (1/2)[max(dist_even - even_horizontal) + min|N_bar(e)|]  [KILLED 2026-07-25] :: LHS(ub)=2 > RHS(exact)=1; bounds insufficient
- [BRACKET] CMP(7) reading#0: gamma_t <= (1/2)[max(dist_even - even_horizontal) + min|N_bar(e)|]  [KILLED 2026-07-25] :: LHS(ub)=2 > RHS(exact)=1; bounds insufficient
- [BRACKET] CMP(8) reading#0: gamma_t <= (1/2)[max(dist_even - even_horizontal) + min|N_bar(e)|]  [KILLED 2026-07-25] :: LHS(ub)=2 > RHS(exact)=1; bounds insufficient
- [BRACKET] CP(2) reading#0: gamma_t <= (1/2)[max(dist_even - even_horizontal) + min|N_bar(e)|]  [KILLED 2026-07-25] :: LHS(ub)=2 > RHS(exact)=1; bounds insufficient
- [BRACKET] CP(3) reading#0: gamma_t <= (1/2)[max(dist_even - even_horizontal) + min|N_bar(e)|]  [KILLED 2026-07-25] :: LHS(ub)=2 > RHS(exact)=1; bounds insufficient
- [BRACKET] CP(4) reading#0: gamma_t <= (1/2)[max(dist_even - even_horizontal) + min|N_bar(e)|]  [KILLED 2026-07-25] :: LHS(ub)=2 > RHS(exact)=1; bounds insufficient
- [BRACKET] CP(5) reading#0: gamma_t <= (1/2)[max(dist_even - even_horizontal) + min|N_bar(e)|]  [KILLED 2026-07-25] :: LHS(ub)=2 > RHS(exact)=1; bounds insufficient
- [BRACKET] CP(6) reading#0: gamma_t <= (1/2)[max(dist_even - even_horizontal) + min|N_bar(e)|]  [KILLED 2026-07-25] :: LHS(ub)=2 > RHS(exact)=1; bounds insufficient
- [BRACKET] CP(7) reading#0: gamma_t <= (1/2)[max(dist_even - even_horizontal) + min|N_bar(e)|]  [KILLED 2026-07-25] :: LHS(ub)=2 > RHS(exact)=1; bounds insufficient
- [BRACKET] CP(8) reading#0: gamma_t <= (1/2)[max(dist_even - even_horizontal) + min|N_bar(e)|]  [KILLED 2026-07-25] :: LHS(ub)=2 > RHS(exact)=1; bounds insufficient
- [BRACKET] KG(10,2) reading#0: gamma_t <= (1/2)[max(dist_even - even_horizontal) + min|N_bar(e)|]  [KILLED 2026-07-25] :: LHS(ub)=3 > RHS(exact)=-17/2; bounds insufficient
- [BRACKET] KG(11,2) reading#0: gamma_t <= (1/2)[max(dist_even - even_horizontal) + min|N_bar(e)|]  [KILLED 2026-07-25] :: LHS(ub)=3 > RHS(exact)=-14; bounds insufficient
- [BRACKET] KG(12,2) reading#0: gamma_t <= (1/2)[max(dist_even - even_horizontal) + min|N_bar(e)|]  [KILLED 2026-07-25] :: LHS(ub)=3 > RHS(exact)=-41/2; bounds insufficient
- [BRACKET] KG(13,2) reading#0: gamma_t <= (1/2)[max(dist_even - even_horizontal) + min|N_bar(e)|]  [KILLED 2026-07-25] :: LHS(ub)=3 > RHS(exact)=-28; bounds insufficient
- [BRACKET] KG(14,2) reading#0: gamma_t <= (1/2)[max(dist_even - even_horizontal) + min|N_bar(e)|]  [KILLED 2026-07-25] :: LHS(ub)=3 > RHS(exact)=-73/2; bounds insufficient
- [BRACKET] KG(15,2) reading#0: gamma_t <= (1/2)[max(dist_even - even_horizontal) + min|N_bar(e)|]  [KILLED 2026-07-25] :: LHS(ub)=3 > RHS(exact)=-46; bounds insufficient
- [BRACKET] KG(16,2) reading#0: gamma_t <= (1/2)[max(dist_even - even_horizontal) + min|N_bar(e)|]  [KILLED 2026-07-25] :: LHS(ub)=3 > RHS(exact)=-113/2; bounds insufficient
- [BRACKET] Paley(101) reading#0: gamma_t <= (1/2)[max(dist_even - even_horizontal) + min|N_bar(e)|]  [KILLED 2026-07-25] :: LHS(ub)=5 > RHS(exact)=-250; bounds insufficient
- [BRACKET] Paley(13) reading#0: gamma_t <= (1/2)[max(dist_even - even_horizontal) + min|N_bar(e)|]  [KILLED 2026-07-25] :: LHS(ub)=4 > RHS(exact)=3; bounds insufficient
- [BRACKET] Paley(17) reading#0: gamma_t <= (1/2)[max(dist_even - even_horizontal) + min|N_bar(e)|]  [KILLED 2026-07-25] :: LHS(ub)=4 > RHS(exact)=2; bounds insufficient
- [BRACKET] Paley(29) reading#0: gamma_t <= (1/2)[max(dist_even - even_horizontal) + min|N_bar(e)|]  [KILLED 2026-07-25] :: LHS(ub)=4 > RHS(exact)=-7; bounds insufficient
- [BRACKET] Paley(37) reading#0: gamma_t <= (1/2)[max(dist_even - even_horizontal) + min|N_bar(e)|]  [KILLED 2026-07-25] :: LHS(ub)=4 > RHS(exact)=-18; bounds insufficient
- [BRACKET] Paley(41) reading#0: gamma_t <= (1/2)[max(dist_even - even_horizontal) + min|N_bar(e)|]  [KILLED 2026-07-25] :: LHS(ub)=4 > RHS(exact)=-25; bounds insufficient
- [BRACKET] Paley(53) reading#0: gamma_t <= (1/2)[max(dist_even - even_horizontal) + min|N_bar(e)|]  [KILLED 2026-07-25] :: LHS(ub)=4 > RHS(exact)=-52; bounds insufficient
- [BRACKET] Paley(61) reading#0: gamma_t <= (1/2)[max(dist_even - even_horizontal) + min|N_bar(e)|]  [KILLED 2026-07-25] :: LHS(ub)=4 > RHS(exact)=-75; bounds insufficient
- [BRACKET] Paley(73) reading#0: gamma_t <= (1/2)[max(dist_even - even_horizontal) + min|N_bar(e)|]  [KILLED 2026-07-25] :: LHS(ub)=5 > RHS(exact)=-117; bounds insufficient
- [BRACKET] Paley(89) reading#0: gamma_t <= (1/2)[max(dist_even - even_horizontal) + min|N_bar(e)|]  [KILLED 2026-07-25] :: LHS(ub)=5 > RHS(exact)=-187; bounds insufficient
- [BRACKET] Paley(97) reading#0: gamma_t <= (1/2)[max(dist_even - even_horizontal) + min|N_bar(e)|]  [KILLED 2026-07-25] :: LHS(ub)=5 > RHS(exact)=-228; bounds insufficient
- [BRACKET] T(10) reading#0: gamma_t <= (1/2)[max(dist_even - even_horizontal) + min|N_bar(e)|]  [KILLED 2026-07-25] :: LHS(ub)=6 > RHS(exact)=-50; bounds insufficient
- [BRACKET] T(11) reading#0: gamma_t <= (1/2)[max(dist_even - even_horizontal) + min|N_bar(e)|]  [KILLED 2026-07-25] :: LHS(ub)=7 > RHS(exact)=-83; bounds insufficient
- [BRACKET] T(12) reading#0: gamma_t <= (1/2)[max(dist_even - even_horizontal) + min|N_bar(e)|]  [KILLED 2026-07-25] :: LHS(ub)=8 > RHS(exact)=-127; bounds insufficient
- [BRACKET] T(13) reading#0: gamma_t <= (1/2)[max(dist_even - even_horizontal) + min|N_bar(e)|]  [KILLED 2026-07-25] :: LHS(ub)=8 > RHS(exact)=-367/2; bounds insufficient
- [BRACKET] T(14) reading#0: gamma_t <= (1/2)[max(dist_even - even_horizontal) + min|N_bar(e)|]  [KILLED 2026-07-25] :: LHS(ub)=9 > RHS(exact)=-254; bounds insufficient
- [BRACKET] T(15) reading#0: gamma_t <= (1/2)[max(dist_even - even_horizontal) + min|N_bar(e)|]  [KILLED 2026-07-25] :: LHS(ub)=10 > RHS(exact)=-340; bounds insufficient
- [BRACKET] T(16) reading#0: gamma_t <= (1/2)[max(dist_even - even_horizontal) + min|N_bar(e)|]  [KILLED 2026-07-25] :: LHS(ub)=10 > RHS(exact)=-443; bounds insufficient
- [BRACKET] comp(C5[K5]) reading#0: gamma_t <= (1/2)[max(dist_even - even_horizontal) + min|N_bar(e)|]  [KILLED 2026-07-25] :: LHS(ub)=3 > RHS(exact)=3/2; bounds insufficient

### id 314
statement: Let G is a simple connected graph with n > 1. If G is triangle-free and path number ≤ 4, then G is well total dominated.

- [BRACKET] CMP(2) reading#0: triangle-free and path_number <= 4 ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] CP(2) reading#0: triangle-free and path_number <= 4 ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] K(3,3) reading#0: triangle-free and path_number <= 4 ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] comp(C5[K2]) reading#0: triangle-free and path_number <= 4 ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] comp(C5[K3]) reading#0: triangle-free and path_number <= 4 ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] comp(C5[K4]) reading#0: triangle-free and path_number <= 4 ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] comp(C5[K5]) reading#0: triangle-free and path_number <= 4 ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] comp(C5[K6]) reading#0: triangle-free and path_number <= 4 ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] comp(C5[K7]) reading#0: triangle-free and path_number <= 4 ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] comp(C5[K8]) reading#0: triangle-free and path_number <= 4 ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration

### id 316
statement: Let G is a simple connected graph with n > 1. Let P be the pendant vertices of G. If |P| ≥ deg_avg( bar(G) ), then G is well total dominated.

- [BRACKET] CMP(2) reading#0: |P| >= deg_avg(bar) ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration

### id 317
statement: Let G is a simple connected graph with n > 1. If tree number ≥ |E( bar(G) )|, then G is well total dominated.

- [BRACKET] CMP(2) reading#0: tree_number >= |E(bar)| ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] CMP(3) reading#0: tree_number >= |E(bar)| ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] CMP(4) reading#0: tree_number >= |E(bar)| ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] CP(2) reading#0: tree_number >= |E(bar)| ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] CP(3) reading#0: tree_number >= |E(bar)| ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] KG(16,2) reading#0: tree_number >= |E(bar)| ==> G is well total dominated :: premise undecidable: tree not exactly certified ({'value': 14, 'certified': False, 'secs': 60.0})
- [BRACKET] Paley(101) reading#0: tree_number >= |E(bar)| ==> G is well total dominated :: premise undecidable: tree not exactly certified ({'value': 10, 'certified': False, 'secs': 60.0})
- [BRACKET] Paley(89) reading#0: tree_number >= |E(bar)| ==> G is well total dominated :: premise undecidable: tree not exactly certified ({'value': 10, 'certified': False, 'secs': 60.0})
- [BRACKET] Paley(97) reading#0: tree_number >= |E(bar)| ==> G is well total dominated :: premise undecidable: tree not exactly certified ({'value': 11, 'certified': False, 'secs': 60.0})
- [BRACKET] T(14) reading#0: tree_number >= |E(bar)| ==> G is well total dominated :: premise undecidable: tree not exactly certified ({'value': 13, 'certified': False, 'secs': 60.0})
- [BRACKET] T(15) reading#0: tree_number >= |E(bar)| ==> G is well total dominated :: premise undecidable: tree not exactly certified ({'value': 14, 'certified': False, 'secs': 60.0})
- [BRACKET] T(16) reading#0: tree_number >= |E(bar)| ==> G is well total dominated :: premise undecidable: tree not exactly certified ({'value': 15, 'certified': False, 'secs': 60.0})

### id 318
statement: Let G is a simple connected graph with n > 1. If maximum dist_even(v) ≥ |E( bar(G) )|, then G is well total dominated.

- [BRACKET] CMP(2) reading#0: max dist_even >= |E(bar)| ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] CMP(3) reading#0: max dist_even >= |E(bar)| ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] CP(2) reading#0: max dist_even >= |E(bar)| ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration

### id 319
statement: Let G is a simple connected graph with n > 1. If maximum dist_even(v) = γ(G), then G is well total dominated.

- [BRACKET] CP(2) reading#0: max dist_even == gamma(G) ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] CP(3) reading#0: max dist_even == gamma(G) ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] CP(4) reading#0: max dist_even == gamma(G) ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] CP(5) reading#0: max dist_even == gamma(G) ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] CP(6) reading#0: max dist_even == gamma(G) ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] CP(7) reading#0: max dist_even == gamma(G) ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] CP(8) reading#0: max dist_even == gamma(G) ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration

## batch appended 2026-08-26 06:54:31

| id | verdict | vio | hold | bracket | premise_false | undef | tag |
|---|---|---|---|---|---|---|---|
| 320 | BRACKET | 0 | 0 | 1 | 49 | 0 |  |
| 321 | BRACKET | 0 | 0 | 4 | 46 | 0 |  |
| 322 | BRACKET | 0 | 0 | 16 | 34 | 0 |  |
| 323 | BRACKET | 0 | 0 | 5 | 45 | 0 |  |
| 324 | BRACKET | 0 | 0 | 32 | 68 | 0 |  |
| 325 | BRACKET | 0 | 0 | 16 | 34 | 0 |  |
| 326 | PREMISE_FALSE_EVERYWHERE | 0 | 0 | 0 | 50 | 0 |  |
| 328 | PREMISE_FALSE_EVERYWHERE | 0 | 0 | 0 | 50 | 0 |  |
| 340 | PREMISE_FALSE_EVERYWHERE | 0 | 0 | 0 | 50 | 0 |  |
| 341 | PREMISE_FALSE_EVERYWHERE | 0 | 0 | 0 | 50 | 0 |  |

### id 320
statement: Let G is a simple connected graph with n > 1. If maximum dist_even(v) = Tdist_min(G), then G is well total dominated.

- [BRACKET] CMP(2) reading#0: max dist_even == Tdist_min ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration

### id 321
statement: Let G is a simple connected graph with n > 1. If ecc_avg(G) ≥ (1/3)*Tdist_max(G), then G is well total dominated.

- [BRACKET] CMP(2) reading#0: ecc_avg(G) >= (1/3)*Tdist_max ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] CMP(3) reading#0: ecc_avg(G) >= (1/3)*Tdist_max ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] CP(2) reading#0: ecc_avg(G) >= (1/3)*Tdist_max ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] CP(3) reading#0: ecc_avg(G) >= (1/3)*Tdist_max ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration

### id 322
statement: Let G is a simple connected graph with n ≥ 5. If λ_max( bar(G) ) ≤ 1, then G is well total dominated.

- [BRACKET] CMP(2) reading#0: lambda_max(bar) <= 1 (n>=5) ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] CMP(3) reading#0: lambda_max(bar) <= 1 (n>=5) ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] CMP(4) reading#0: lambda_max(bar) <= 1 (n>=5) ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] CMP(5) reading#0: lambda_max(bar) <= 1 (n>=5) ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] CMP(6) reading#0: lambda_max(bar) <= 1 (n>=5) ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] CMP(7) reading#0: lambda_max(bar) <= 1 (n>=5) ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] CMP(8) reading#0: lambda_max(bar) <= 1 (n>=5) ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] CP(2) reading#0: lambda_max(bar) <= 1 (n>=5) ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] CP(3) reading#0: lambda_max(bar) <= 1 (n>=5) ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] CP(4) reading#0: lambda_max(bar) <= 1 (n>=5) ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] CP(5) reading#0: lambda_max(bar) <= 1 (n>=5) ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] CP(6) reading#0: lambda_max(bar) <= 1 (n>=5) ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] CP(7) reading#0: lambda_max(bar) <= 1 (n>=5) ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] CP(8) reading#0: lambda_max(bar) <= 1 (n>=5) ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] K(3,3) reading#0: lambda_max(bar) <= 1 (n>=5) ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] K(3,3,3) reading#0: lambda_max(bar) <= 1 (n>=5) ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration

### id 323
statement: Let G is a simple connected graph with n > 1. If maximum of {|N_bar(G)(e)|: e an edge of bar(G) } ≤ 1 + maximum {dist_odd(v) - odd horizontal(v): v in V(G)}, then G is well total dominated.

- [BRACKET] CMP(2) reading#0: max|N_bar(e)| <= 1 + max(dist_odd - odd_horizontal) ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] CMP(3) reading#0: max|N_bar(e)| <= 1 + max(dist_odd - odd_horizontal) ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] CP(2) reading#0: max|N_bar(e)| <= 1 + max(dist_odd - odd_horizontal) ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] CP(3) reading#0: max|N_bar(e)| <= 1 + max(dist_odd - odd_horizontal) ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] K(3,3) reading#0: max|N_bar(e)| <= 1 + max(dist_odd - odd_horizontal) ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration

### id 324
statement: Let G is a simple connected graph with n > 1. If maximum of {|N_bar(G)(e)|: e an edge of bar(G) } ≤ 1 + residue(G), then G is well total dominated.

- [BRACKET] CMP(2) reading#0: min?/max? |N_bar(e)| <= 1 + residue: reading max ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] CMP(2) reading#1: alt reading min: min|N_bar(e)| <= 1 + residue ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] CMP(3) reading#0: min?/max? |N_bar(e)| <= 1 + residue: reading max ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] CMP(3) reading#1: alt reading min: min|N_bar(e)| <= 1 + residue ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] CMP(4) reading#0: min?/max? |N_bar(e)| <= 1 + residue: reading max ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] CMP(4) reading#1: alt reading min: min|N_bar(e)| <= 1 + residue ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] CMP(5) reading#0: min?/max? |N_bar(e)| <= 1 + residue: reading max ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] CMP(5) reading#1: alt reading min: min|N_bar(e)| <= 1 + residue ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] CMP(6) reading#0: min?/max? |N_bar(e)| <= 1 + residue: reading max ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] CMP(6) reading#1: alt reading min: min|N_bar(e)| <= 1 + residue ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] CMP(7) reading#0: min?/max? |N_bar(e)| <= 1 + residue: reading max ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] CMP(7) reading#1: alt reading min: min|N_bar(e)| <= 1 + residue ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] CMP(8) reading#0: min?/max? |N_bar(e)| <= 1 + residue: reading max ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] CMP(8) reading#1: alt reading min: min|N_bar(e)| <= 1 + residue ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] CP(2) reading#0: min?/max? |N_bar(e)| <= 1 + residue: reading max ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] CP(2) reading#1: alt reading min: min|N_bar(e)| <= 1 + residue ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] CP(3) reading#0: min?/max? |N_bar(e)| <= 1 + residue: reading max ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] CP(3) reading#1: alt reading min: min|N_bar(e)| <= 1 + residue ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] CP(4) reading#0: min?/max? |N_bar(e)| <= 1 + residue: reading max ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] CP(4) reading#1: alt reading min: min|N_bar(e)| <= 1 + residue ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] CP(5) reading#0: min?/max? |N_bar(e)| <= 1 + residue: reading max ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] CP(5) reading#1: alt reading min: min|N_bar(e)| <= 1 + residue ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] CP(6) reading#0: min?/max? |N_bar(e)| <= 1 + residue: reading max ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] CP(6) reading#1: alt reading min: min|N_bar(e)| <= 1 + residue ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] CP(7) reading#0: min?/max? |N_bar(e)| <= 1 + residue: reading max ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] CP(7) reading#1: alt reading min: min|N_bar(e)| <= 1 + residue ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] CP(8) reading#0: min?/max? |N_bar(e)| <= 1 + residue: reading max ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] CP(8) reading#1: alt reading min: min|N_bar(e)| <= 1 + residue ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] K(3,3) reading#0: min?/max? |N_bar(e)| <= 1 + residue: reading max ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] K(3,3) reading#1: alt reading min: min|N_bar(e)| <= 1 + residue ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] K(3,3,3) reading#0: min?/max? |N_bar(e)| <= 1 + residue: reading max ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] K(3,3,3) reading#1: alt reading min: min|N_bar(e)| <= 1 + residue ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration

### id 325
statement: Let G is a simple connected graph with n > 1. If minimum of {|N_bar(G)(e)|: e an edge of bar(G) } ≤ 1 + number of components of <N[S}> where S is the set of vertices of degree two, then G is well tota

- [BRACKET] CMP(2) reading#0: min|N_bar(e)| <= 1 + components(<N[S_deg2]>) ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] CMP(3) reading#0: min|N_bar(e)| <= 1 + components(<N[S_deg2]>) ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] CMP(4) reading#0: min|N_bar(e)| <= 1 + components(<N[S_deg2]>) ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] CMP(5) reading#0: min|N_bar(e)| <= 1 + components(<N[S_deg2]>) ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] CMP(6) reading#0: min|N_bar(e)| <= 1 + components(<N[S_deg2]>) ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] CMP(7) reading#0: min|N_bar(e)| <= 1 + components(<N[S_deg2]>) ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] CMP(8) reading#0: min|N_bar(e)| <= 1 + components(<N[S_deg2]>) ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] CP(2) reading#0: min|N_bar(e)| <= 1 + components(<N[S_deg2]>) ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] CP(3) reading#0: min|N_bar(e)| <= 1 + components(<N[S_deg2]>) ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] CP(4) reading#0: min|N_bar(e)| <= 1 + components(<N[S_deg2]>) ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] CP(5) reading#0: min|N_bar(e)| <= 1 + components(<N[S_deg2]>) ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] CP(6) reading#0: min|N_bar(e)| <= 1 + components(<N[S_deg2]>) ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] CP(7) reading#0: min|N_bar(e)| <= 1 + components(<N[S_deg2]>) ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] CP(8) reading#0: min|N_bar(e)| <= 1 + components(<N[S_deg2]>) ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] K(3,3) reading#0: min|N_bar(e)| <= 1 + components(<N[S_deg2]>) ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration
- [BRACKET] K(3,3,3) reading#0: min|N_bar(e)| <= 1 + components(<N[S_deg2]>) ==> G is well total dominated :: no non-minimum minimal TDS found; wtd=TRUE not certifiable without enumeration

## batch appended 2026-08-26 06:54:31

| id | verdict | vio | hold | bracket | premise_false | undef | tag |
|---|---|---|---|---|---|---|---|
| 342 | PREMISE_FALSE_EVERYWHERE | 0 | 0 | 0 | 50 | 0 |  |
| 343 | PREMISE_FALSE_EVERYWHERE | 0 | 0 | 0 | 50 | 0 |  |
| 344 | PREMISE_FALSE_EVERYWHERE | 0 | 0 | 0 | 50 | 0 |  |
| 348 | PREMISE_FALSE_EVERYWHERE | 0 | 0 | 0 | 50 | 0 |  |
| 351 | PREMISE_FALSE_EVERYWHERE | 0 | 0 | 0 | 50 | 0 |  |
| 352 | PREMISE_FALSE_EVERYWHERE | 0 | 0 | 0 | 50 | 0 |  |
| 353 | PREMISE_FALSE_EVERYWHERE | 0 | 0 | 0 | 50 | 0 |  |
| 354 | PREMISE_FALSE_EVERYWHERE | 0 | 0 | 0 | 50 | 0 |  |
| 356 | PREMISE_FALSE_EVERYWHERE | 0 | 0 | 0 | 50 | 0 |  |
| 358 | PREMISE_FALSE_EVERYWHERE | 0 | 0 | 0 | 50 | 0 |  |

## batch appended 2026-08-26 06:54:31

| id | verdict | vio | hold | bracket | premise_false | undef | tag |
|---|---|---|---|---|---|---|---|
| 359 | PREMISE_FALSE_EVERYWHERE | 0 | 0 | 0 | 50 | 0 |  |
| 360 | PREMISE_FALSE_EVERYWHERE | 0 | 0 | 0 | 50 | 0 |  |
| 361 | PREMISE_FALSE_EVERYWHERE | 0 | 0 | 0 | 50 | 0 |  |
| 362 | PREMISE_FALSE_EVERYWHERE | 0 | 0 | 0 | 50 | 0 |  |
| 363 | PREMISE_FALSE_EVERYWHERE | 0 | 0 | 0 | 50 | 0 |  |
| 364 | PREMISE_FALSE_EVERYWHERE | 0 | 0 | 0 | 50 | 0 |  |
| 365 | PREMISE_FALSE_EVERYWHERE | 0 | 0 | 0 | 50 | 0 |  |
| 367 | PREMISE_FALSE_EVERYWHERE | 0 | 0 | 0 | 50 | 0 |  |
| 369 | PREMISE_FALSE_EVERYWHERE | 0 | 0 | 0 | 50 | 0 |  |
| 372 | PREMISE_FALSE_EVERYWHERE | 0 | 0 | 0 | 50 | 0 |  |

## batch appended 2026-08-26 06:54:31

| id | verdict | vio | hold | bracket | premise_false | undef | tag |
|---|---|---|---|---|---|---|---|
| 373 | PREMISE_FALSE_EVERYWHERE | 0 | 0 | 0 | 50 | 0 |  |
| 374 | PREMISE_FALSE_EVERYWHERE | 0 | 0 | 0 | 50 | 0 |  |
| 375 | PREMISE_FALSE_EVERYWHERE | 0 | 0 | 0 | 50 | 0 |  |
| 376 | PREMISE_FALSE_EVERYWHERE | 0 | 0 | 0 | 50 | 0 |  |
| 377 | PREMISE_FALSE_EVERYWHERE | 0 | 0 | 0 | 50 | 0 |  |
| 378 | PREMISE_FALSE_EVERYWHERE | 0 | 0 | 0 | 50 | 0 |  |
| 379 | PREMISE_FALSE_EVERYWHERE | 0 | 0 | 0 | 50 | 0 |  |
| 380 | PREMISE_FALSE_EVERYWHERE | 0 | 0 | 0 | 50 | 0 |  |
| 381 | PREMISE_FALSE_EVERYWHERE | 0 | 0 | 0 | 50 | 0 |  |
| 382b | HOLDS | 0 | 50 | 0 | 0 | 0 |  |

## batch appended 2026-08-26 06:54:31

| id | verdict | vio | hold | bracket | premise_false | undef | tag |
|---|---|---|---|---|---|---|---|
| 382c | HOLDS | 0 | 50 | 0 | 0 | 0 |  |
| 382d | HOLDS | 0 | 50 | 0 | 0 | 0 |  |
| 382e | HOLDS | 0 | 50 | 0 | 0 | 0 |  |
| 384b | HOLDS | 0 | 50 | 0 | 0 | 0 |  |
| 387 | HOLDS | 0 | 100 | 0 | 0 | 0 |  |
| 389a | HOLDS | 0 | 100 | 0 | 0 | 0 |  |
| 391 | HOLDS_PARTIAL | 0 | 48 | 0 | 0 | 2 | EXTERNALLY_RESOLVED |
| 392b | HOLDS | 0 | 50 | 0 | 0 | 0 |  |
| 392c | HOLDS | 0 | 50 | 0 | 0 | 0 |  |
| 392d | HOLDS | 0 | 50 | 0 | 0 | 0 |  |

## batch appended 2026-08-26 06:54:32

| id | verdict | vio | hold | bracket | premise_false | undef | tag |
|---|---|---|---|---|---|---|---|
| 392e | HOLDS | 0 | 50 | 0 | 0 | 0 |  |
| 392f | HOLDS | 0 | 50 | 0 | 0 | 0 |  |
| 393a | HOLDS | 0 | 50 | 0 | 0 | 0 |  |
| 393b | HOLDS | 0 | 50 | 0 | 0 | 0 |  |
| 393c | HOLDS | 0 | 50 | 0 | 0 | 0 |  |
| 393d | HOLDS | 0 | 50 | 0 | 0 | 0 |  |
| 394 | HOLDS | 0 | 50 | 0 | 0 | 0 |  |
| 395a | HOLDS | 0 | 50 | 0 | 0 | 0 |  |
| 395b | HOLDS_PARTIAL | 0 | 7 | 0 | 0 | 43 |  |
| 396 | HOLDS | 0 | 50 | 0 | 0 | 0 |  |

## batch appended 2026-08-26 06:54:37

| id | verdict | vio | hold | bracket | premise_false | undef | tag |
|---|---|---|---|---|---|---|---|
| 397c | HOLDS | 0 | 50 | 0 | 0 | 0 |  |
| 398 | BRACKET | 0 | 1 | 49 | 0 | 0 |  |
| 399a | HOLDS | 0 | 50 | 0 | 0 | 0 |  |
| 399b | HOLDS | 0 | 50 | 0 | 0 | 0 |  |
| 399c | HOLDS | 0 | 50 | 0 | 0 | 0 |  |
| 40 | HOLDS_PARTIAL | 0 | 29 | 0 | 0 | 21 |  |
| 400c | HOLDS | 0 | 50 | 0 | 0 | 0 |  |
| 401a | HOLDS | 0 | 50 | 0 | 0 | 0 |  |
| 401b | BRACKET | 0 | 21 | 29 | 0 | 0 | KNOWN_CORRUPT_READING |
| 402 | HOLDS | 0 | 50 | 0 | 0 | 0 |  |

### id 398
statement: If G is a connected graph on n > 2 vertices, then γ_2 ≤ |E( G [ V - NN((P)) ]) | + |{ v: |N(v) ∩ [ V - N(P) ] | = 1}| + | Ε( P,V-P ) |, where P is the set of pendants.

- [BRACKET] C7[K3] reading#0: 398: |E(G[V-NN(P)])| + |{v:|N(v) cap [V-N(P)]|=1}| + |E(P,V-P)| :: LHS(ub)=5 > RHS(exact)=0; bounds insufficient
- [BRACKET] C9[K3] reading#0: 398: |E(G[V-NN(P)])| + |{v:|N(v) cap [V-N(P)]|=1}| + |E(P,V-P)| :: LHS(ub)=6 > RHS(exact)=0; bounds insufficient
- [BRACKET] CMP(3) reading#0: 398: |E(G[V-NN(P)])| + |{v:|N(v) cap [V-N(P)]|=1}| + |E(P,V-P)| :: LHS(ub)=2 > RHS(exact)=0; bounds insufficient
- [BRACKET] CMP(4) reading#0: 398: |E(G[V-NN(P)])| + |{v:|N(v) cap [V-N(P)]|=1}| + |E(P,V-P)| :: LHS(ub)=2 > RHS(exact)=0; bounds insufficient
- [BRACKET] CMP(5) reading#0: 398: |E(G[V-NN(P)])| + |{v:|N(v) cap [V-N(P)]|=1}| + |E(P,V-P)| :: LHS(ub)=2 > RHS(exact)=0; bounds insufficient
- [BRACKET] CMP(6) reading#0: 398: |E(G[V-NN(P)])| + |{v:|N(v) cap [V-N(P)]|=1}| + |E(P,V-P)| :: LHS(ub)=2 > RHS(exact)=0; bounds insufficient
- [BRACKET] CMP(7) reading#0: 398: |E(G[V-NN(P)])| + |{v:|N(v) cap [V-N(P)]|=1}| + |E(P,V-P)| :: LHS(ub)=2 > RHS(exact)=0; bounds insufficient
- [BRACKET] CMP(8) reading#0: 398: |E(G[V-NN(P)])| + |{v:|N(v) cap [V-N(P)]|=1}| + |E(P,V-P)| :: LHS(ub)=2 > RHS(exact)=0; bounds insufficient
- [BRACKET] CP(2) reading#0: 398: |E(G[V-NN(P)])| + |{v:|N(v) cap [V-N(P)]|=1}| + |E(P,V-P)| :: LHS(ub)=2 > RHS(exact)=0; bounds insufficient
- [BRACKET] CP(3) reading#0: 398: |E(G[V-NN(P)])| + |{v:|N(v) cap [V-N(P)]|=1}| + |E(P,V-P)| :: LHS(ub)=2 > RHS(exact)=0; bounds insufficient
- [BRACKET] CP(4) reading#0: 398: |E(G[V-NN(P)])| + |{v:|N(v) cap [V-N(P)]|=1}| + |E(P,V-P)| :: LHS(ub)=2 > RHS(exact)=0; bounds insufficient
- [BRACKET] CP(5) reading#0: 398: |E(G[V-NN(P)])| + |{v:|N(v) cap [V-N(P)]|=1}| + |E(P,V-P)| :: LHS(ub)=2 > RHS(exact)=0; bounds insufficient
- [BRACKET] CP(6) reading#0: 398: |E(G[V-NN(P)])| + |{v:|N(v) cap [V-N(P)]|=1}| + |E(P,V-P)| :: LHS(ub)=2 > RHS(exact)=0; bounds insufficient
- [BRACKET] CP(7) reading#0: 398: |E(G[V-NN(P)])| + |{v:|N(v) cap [V-N(P)]|=1}| + |E(P,V-P)| :: LHS(ub)=2 > RHS(exact)=0; bounds insufficient
- [BRACKET] CP(8) reading#0: 398: |E(G[V-NN(P)])| + |{v:|N(v) cap [V-N(P)]|=1}| + |E(P,V-P)| :: LHS(ub)=2 > RHS(exact)=0; bounds insufficient
- [BRACKET] K(3,3) reading#0: 398: |E(G[V-NN(P)])| + |{v:|N(v) cap [V-N(P)]|=1}| + |E(P,V-P)| :: LHS(ub)=3 > RHS(exact)=0; bounds insufficient
- [BRACKET] K(3,3,3) reading#0: 398: |E(G[V-NN(P)])| + |{v:|N(v) cap [V-N(P)]|=1}| + |E(P,V-P)| :: LHS(ub)=3 > RHS(exact)=0; bounds insufficient
- [BRACKET] KG(10,2) reading#0: 398: |E(G[V-NN(P)])| + |{v:|N(v) cap [V-N(P)]|=1}| + |E(P,V-P)| :: LHS(ub)=4 > RHS(exact)=0; bounds insufficient
- [BRACKET] KG(11,2) reading#0: 398: |E(G[V-NN(P)])| + |{v:|N(v) cap [V-N(P)]|=1}| + |E(P,V-P)| :: LHS(ub)=4 > RHS(exact)=0; bounds insufficient
- [BRACKET] KG(12,2) reading#0: 398: |E(G[V-NN(P)])| + |{v:|N(v) cap [V-N(P)]|=1}| + |E(P,V-P)| :: LHS(ub)=4 > RHS(exact)=0; bounds insufficient
- [BRACKET] KG(13,2) reading#0: 398: |E(G[V-NN(P)])| + |{v:|N(v) cap [V-N(P)]|=1}| + |E(P,V-P)| :: LHS(ub)=4 > RHS(exact)=0; bounds insufficient
- [BRACKET] KG(14,2) reading#0: 398: |E(G[V-NN(P)])| + |{v:|N(v) cap [V-N(P)]|=1}| + |E(P,V-P)| :: LHS(ub)=4 > RHS(exact)=0; bounds insufficient
- [BRACKET] KG(15,2) reading#0: 398: |E(G[V-NN(P)])| + |{v:|N(v) cap [V-N(P)]|=1}| + |E(P,V-P)| :: LHS(ub)=4 > RHS(exact)=0; bounds insufficient
- [BRACKET] KG(16,2) reading#0: 398: |E(G[V-NN(P)])| + |{v:|N(v) cap [V-N(P)]|=1}| + |E(P,V-P)| :: LHS(ub)=4 > RHS(exact)=0; bounds insufficient
- [BRACKET] Paley(101) reading#0: 398: |E(G[V-NN(P)])| + |{v:|N(v) cap [V-N(P)]|=1}| + |E(P,V-P)| :: LHS(ub)=7 > RHS(exact)=0; bounds insufficient
- [BRACKET] Paley(13) reading#0: 398: |E(G[V-NN(P)])| + |{v:|N(v) cap [V-N(P)]|=1}| + |E(P,V-P)| :: LHS(ub)=4 > RHS(exact)=0; bounds insufficient
- [BRACKET] Paley(17) reading#0: 398: |E(G[V-NN(P)])| + |{v:|N(v) cap [V-N(P)]|=1}| + |E(P,V-P)| :: LHS(ub)=5 > RHS(exact)=0; bounds insufficient
- [BRACKET] Paley(29) reading#0: 398: |E(G[V-NN(P)])| + |{v:|N(v) cap [V-N(P)]|=1}| + |E(P,V-P)| :: LHS(ub)=5 > RHS(exact)=0; bounds insufficient
- [BRACKET] Paley(37) reading#0: 398: |E(G[V-NN(P)])| + |{v:|N(v) cap [V-N(P)]|=1}| + |E(P,V-P)| :: LHS(ub)=6 > RHS(exact)=0; bounds insufficient
- [BRACKET] Paley(41) reading#0: 398: |E(G[V-NN(P)])| + |{v:|N(v) cap [V-N(P)]|=1}| + |E(P,V-P)| :: LHS(ub)=5 > RHS(exact)=0; bounds insufficient
- [BRACKET] Paley(53) reading#0: 398: |E(G[V-NN(P)])| + |{v:|N(v) cap [V-N(P)]|=1}| + |E(P,V-P)| :: LHS(ub)=6 > RHS(exact)=0; bounds insufficient
- [BRACKET] Paley(61) reading#0: 398: |E(G[V-NN(P)])| + |{v:|N(v) cap [V-N(P)]|=1}| + |E(P,V-P)| :: LHS(ub)=6 > RHS(exact)=0; bounds insufficient
- [BRACKET] Paley(73) reading#0: 398: |E(G[V-NN(P)])| + |{v:|N(v) cap [V-N(P)]|=1}| + |E(P,V-P)| :: LHS(ub)=6 > RHS(exact)=0; bounds insufficient
- [BRACKET] Paley(89) reading#0: 398: |E(G[V-NN(P)])| + |{v:|N(v) cap [V-N(P)]|=1}| + |E(P,V-P)| :: LHS(ub)=7 > RHS(exact)=0; bounds insufficient
- [BRACKET] Paley(97) reading#0: 398: |E(G[V-NN(P)])| + |{v:|N(v) cap [V-N(P)]|=1}| + |E(P,V-P)| :: LHS(ub)=7 > RHS(exact)=0; bounds insufficient
- [BRACKET] T(10) reading#0: 398: |E(G[V-NN(P)])| + |{v:|N(v) cap [V-N(P)]|=1}| + |E(P,V-P)| :: LHS(ub)=5 > RHS(exact)=0; bounds insufficient
- [BRACKET] T(11) reading#0: 398: |E(G[V-NN(P)])| + |{v:|N(v) cap [V-N(P)]|=1}| + |E(P,V-P)| :: LHS(ub)=6 > RHS(exact)=0; bounds insufficient
- [BRACKET] T(12) reading#0: 398: |E(G[V-NN(P)])| + |{v:|N(v) cap [V-N(P)]|=1}| + |E(P,V-P)| :: LHS(ub)=6 > RHS(exact)=0; bounds insufficient
- [BRACKET] T(13) reading#0: 398: |E(G[V-NN(P)])| + |{v:|N(v) cap [V-N(P)]|=1}| + |E(P,V-P)| :: LHS(ub)=7 > RHS(exact)=0; bounds insufficient
- [BRACKET] T(14) reading#0: 398: |E(G[V-NN(P)])| + |{v:|N(v) cap [V-N(P)]|=1}| + |E(P,V-P)| :: LHS(ub)=7 > RHS(exact)=0; bounds insufficient

### id 401b
statement: Let G be a connected graph on n > 2 vertices. Then γ_2 ≤ FLOOR[3*Tdist_max / freq[T_max(v)]].

- [BRACKET] KG(11,2) reading#0: 401b: floor(3*Tdist_max/freq[T_max]) [KNOWN CORRUPT per README] :: LHS(ub)=4 > RHS(exact)=3; bounds insufficient
- [BRACKET] KG(12,2) reading#0: 401b: floor(3*Tdist_max/freq[T_max]) [KNOWN CORRUPT per README] :: LHS(ub)=4 > RHS(exact)=3; bounds insufficient
- [BRACKET] KG(13,2) reading#0: 401b: floor(3*Tdist_max/freq[T_max]) [KNOWN CORRUPT per README] :: LHS(ub)=4 > RHS(exact)=3; bounds insufficient
- [BRACKET] KG(14,2) reading#0: 401b: floor(3*Tdist_max/freq[T_max]) [KNOWN CORRUPT per README] :: LHS(ub)=4 > RHS(exact)=3; bounds insufficient
- [BRACKET] KG(15,2) reading#0: 401b: floor(3*Tdist_max/freq[T_max]) [KNOWN CORRUPT per README] :: LHS(ub)=4 > RHS(exact)=3; bounds insufficient
- [BRACKET] KG(16,2) reading#0: 401b: floor(3*Tdist_max/freq[T_max]) [KNOWN CORRUPT per README] :: LHS(ub)=4 > RHS(exact)=3; bounds insufficient
- [BRACKET] Paley(101) reading#0: 401b: floor(3*Tdist_max/freq[T_max]) [KNOWN CORRUPT per README] :: LHS(ub)=7 > RHS(exact)=4; bounds insufficient
- [BRACKET] Paley(17) reading#0: 401b: floor(3*Tdist_max/freq[T_max]) [KNOWN CORRUPT per README] :: LHS(ub)=5 > RHS(exact)=4; bounds insufficient
- [BRACKET] Paley(29) reading#0: 401b: floor(3*Tdist_max/freq[T_max]) [KNOWN CORRUPT per README] :: LHS(ub)=5 > RHS(exact)=4; bounds insufficient
- [BRACKET] Paley(37) reading#0: 401b: floor(3*Tdist_max/freq[T_max]) [KNOWN CORRUPT per README] :: LHS(ub)=6 > RHS(exact)=4; bounds insufficient
- [BRACKET] Paley(41) reading#0: 401b: floor(3*Tdist_max/freq[T_max]) [KNOWN CORRUPT per README] :: LHS(ub)=5 > RHS(exact)=4; bounds insufficient
- [BRACKET] Paley(53) reading#0: 401b: floor(3*Tdist_max/freq[T_max]) [KNOWN CORRUPT per README] :: LHS(ub)=6 > RHS(exact)=4; bounds insufficient
- [BRACKET] Paley(61) reading#0: 401b: floor(3*Tdist_max/freq[T_max]) [KNOWN CORRUPT per README] :: LHS(ub)=6 > RHS(exact)=4; bounds insufficient
- [BRACKET] Paley(73) reading#0: 401b: floor(3*Tdist_max/freq[T_max]) [KNOWN CORRUPT per README] :: LHS(ub)=6 > RHS(exact)=4; bounds insufficient
- [BRACKET] Paley(89) reading#0: 401b: floor(3*Tdist_max/freq[T_max]) [KNOWN CORRUPT per README] :: LHS(ub)=7 > RHS(exact)=4; bounds insufficient
- [BRACKET] Paley(97) reading#0: 401b: floor(3*Tdist_max/freq[T_max]) [KNOWN CORRUPT per README] :: LHS(ub)=7 > RHS(exact)=4; bounds insufficient
- [BRACKET] T(10) reading#0: 401b: floor(3*Tdist_max/freq[T_max]) [KNOWN CORRUPT per README] :: LHS(ub)=5 > RHS(exact)=4; bounds insufficient
- [BRACKET] T(11) reading#0: 401b: floor(3*Tdist_max/freq[T_max]) [KNOWN CORRUPT per README] :: LHS(ub)=6 > RHS(exact)=4; bounds insufficient
- [BRACKET] T(12) reading#0: 401b: floor(3*Tdist_max/freq[T_max]) [KNOWN CORRUPT per README] :: LHS(ub)=6 > RHS(exact)=5; bounds insufficient
- [BRACKET] T(13) reading#0: 401b: floor(3*Tdist_max/freq[T_max]) [KNOWN CORRUPT per README] :: LHS(ub)=7 > RHS(exact)=5; bounds insufficient
- [BRACKET] T(14) reading#0: 401b: floor(3*Tdist_max/freq[T_max]) [KNOWN CORRUPT per README] :: LHS(ub)=7 > RHS(exact)=5; bounds insufficient
- [BRACKET] T(15) reading#0: 401b: floor(3*Tdist_max/freq[T_max]) [KNOWN CORRUPT per README] :: LHS(ub)=8 > RHS(exact)=5; bounds insufficient
- [BRACKET] T(16) reading#0: 401b: floor(3*Tdist_max/freq[T_max]) [KNOWN CORRUPT per README] :: LHS(ub)=8 > RHS(exact)=5; bounds insufficient
- [BRACKET] comp(C5[K3]) reading#0: 401b: floor(3*Tdist_max/freq[T_max]) [KNOWN CORRUPT per README] :: LHS(ub)=5 > RHS(exact)=4; bounds insufficient
- [BRACKET] comp(C5[K4]) reading#0: 401b: floor(3*Tdist_max/freq[T_max]) [KNOWN CORRUPT per README] :: LHS(ub)=5 > RHS(exact)=4; bounds insufficient
- [BRACKET] comp(C5[K5]) reading#0: 401b: floor(3*Tdist_max/freq[T_max]) [KNOWN CORRUPT per README] :: LHS(ub)=5 > RHS(exact)=4; bounds insufficient
- [BRACKET] comp(C5[K6]) reading#0: 401b: floor(3*Tdist_max/freq[T_max]) [KNOWN CORRUPT per README] :: LHS(ub)=5 > RHS(exact)=4; bounds insufficient
- [BRACKET] comp(C5[K7]) reading#0: 401b: floor(3*Tdist_max/freq[T_max]) [KNOWN CORRUPT per README] :: LHS(ub)=5 > RHS(exact)=4; bounds insufficient
- [BRACKET] comp(C5[K8]) reading#0: 401b: floor(3*Tdist_max/freq[T_max]) [KNOWN CORRUPT per README] :: LHS(ub)=5 > RHS(exact)=4; bounds insufficient

## batch appended 2026-08-26 06:55:30

| id | verdict | vio | hold | bracket | premise_false | undef | tag |
|---|---|---|---|---|---|---|---|
| 404 | VIOLATED_CANDIDATE | 47 | 0 | 0 | 0 | 3 |  |
| 405 | HOLDS_PARTIAL | 0 | 47 | 0 | 0 | 3 |  |
| 406 | VIOLATED_CANDIDATE | 47 | 0 | 0 | 0 | 3 |  |
| 407 | HOLDS_PARTIAL | 0 | 45 | 0 | 0 | 5 |  |
| 410a | HOLDS_PARTIAL | 0 | 47 | 0 | 0 | 3 |  |
| 410b | HOLDS_PARTIAL | 0 | 47 | 0 | 0 | 3 |  |
| 412a | HOLDS_PARTIAL | 0 | 47 | 0 | 0 | 3 |  |
| 412b | HOLDS_PARTIAL | 0 | 47 | 0 | 0 | 3 |  |
| 412d | BRACKET | 0 | 0 | 47 | 0 | 3 |  |
| 412e | BRACKET | 0 | 0 | 47 | 0 | 3 |  |

### id 404
statement: Let G be a tree on n > 2 vertices and H the union of all maximum critical independent sets of G. Then number of peN(H) ≤ 2( | S | -1), where S is the set of support vertices of G.

- [VIO] C7[K3] reading#0: 404: peN(H) <= 2(|S_support|-1) :: LHS=0 > RHS=-2
- [VIO] C9[K3] reading#0: 404: peN(H) <= 2(|S_support|-1) :: LHS=0 > RHS=-2
- [VIO] CMP(3) reading#0: 404: peN(H) <= 2(|S_support|-1) :: LHS=0 > RHS=-2
- [VIO] CMP(4) reading#0: 404: peN(H) <= 2(|S_support|-1) :: LHS=0 > RHS=-2
- [VIO] CMP(5) reading#0: 404: peN(H) <= 2(|S_support|-1) :: LHS=0 > RHS=-2
- [VIO] CMP(6) reading#0: 404: peN(H) <= 2(|S_support|-1) :: LHS=0 > RHS=-2
- [VIO] CMP(7) reading#0: 404: peN(H) <= 2(|S_support|-1) :: LHS=0 > RHS=-2
- [VIO] CMP(8) reading#0: 404: peN(H) <= 2(|S_support|-1) :: LHS=0 > RHS=-2
- [VIO] CP(3) reading#0: 404: peN(H) <= 2(|S_support|-1) :: LHS=0 > RHS=-2
- [VIO] CP(4) reading#0: 404: peN(H) <= 2(|S_support|-1) :: LHS=0 > RHS=-2
- [VIO] CP(5) reading#0: 404: peN(H) <= 2(|S_support|-1) :: LHS=0 > RHS=-2
- [VIO] CP(6) reading#0: 404: peN(H) <= 2(|S_support|-1) :: LHS=0 > RHS=-2
- [VIO] CP(7) reading#0: 404: peN(H) <= 2(|S_support|-1) :: LHS=0 > RHS=-2
- [VIO] CP(8) reading#0: 404: peN(H) <= 2(|S_support|-1) :: LHS=0 > RHS=-2
- [VIO] K(3,3,3) reading#0: 404: peN(H) <= 2(|S_support|-1) :: LHS=0 > RHS=-2
- [VIO] KG(10,2) reading#0: 404: peN(H) <= 2(|S_support|-1) :: LHS=0 > RHS=-2
- [VIO] KG(11,2) reading#0: 404: peN(H) <= 2(|S_support|-1) :: LHS=0 > RHS=-2
- [VIO] KG(12,2) reading#0: 404: peN(H) <= 2(|S_support|-1) :: LHS=0 > RHS=-2
- [VIO] KG(13,2) reading#0: 404: peN(H) <= 2(|S_support|-1) :: LHS=0 > RHS=-2
- [VIO] KG(14,2) reading#0: 404: peN(H) <= 2(|S_support|-1) :: LHS=0 > RHS=-2
- [VIO] KG(15,2) reading#0: 404: peN(H) <= 2(|S_support|-1) :: LHS=0 > RHS=-2
- [VIO] KG(16,2) reading#0: 404: peN(H) <= 2(|S_support|-1) :: LHS=0 > RHS=-2
- [VIO] Paley(101) reading#0: 404: peN(H) <= 2(|S_support|-1) :: LHS=0 > RHS=-2
- [VIO] Paley(13) reading#0: 404: peN(H) <= 2(|S_support|-1) :: LHS=0 > RHS=-2
- [VIO] Paley(17) reading#0: 404: peN(H) <= 2(|S_support|-1) :: LHS=0 > RHS=-2
- [VIO] Paley(29) reading#0: 404: peN(H) <= 2(|S_support|-1) :: LHS=0 > RHS=-2
- [VIO] Paley(37) reading#0: 404: peN(H) <= 2(|S_support|-1) :: LHS=0 > RHS=-2
- [VIO] Paley(41) reading#0: 404: peN(H) <= 2(|S_support|-1) :: LHS=0 > RHS=-2
- [VIO] Paley(53) reading#0: 404: peN(H) <= 2(|S_support|-1) :: LHS=0 > RHS=-2
- [VIO] Paley(61) reading#0: 404: peN(H) <= 2(|S_support|-1) :: LHS=0 > RHS=-2
- [VIO] Paley(73) reading#0: 404: peN(H) <= 2(|S_support|-1) :: LHS=0 > RHS=-2
- [VIO] Paley(89) reading#0: 404: peN(H) <= 2(|S_support|-1) :: LHS=0 > RHS=-2
- [VIO] Paley(97) reading#0: 404: peN(H) <= 2(|S_support|-1) :: LHS=0 > RHS=-2
- [VIO] T(10) reading#0: 404: peN(H) <= 2(|S_support|-1) :: LHS=0 > RHS=-2
- [VIO] T(11) reading#0: 404: peN(H) <= 2(|S_support|-1) :: LHS=0 > RHS=-2
- [VIO] T(12) reading#0: 404: peN(H) <= 2(|S_support|-1) :: LHS=0 > RHS=-2
- [VIO] T(13) reading#0: 404: peN(H) <= 2(|S_support|-1) :: LHS=0 > RHS=-2
- [VIO] T(14) reading#0: 404: peN(H) <= 2(|S_support|-1) :: LHS=0 > RHS=-2
- [VIO] T(15) reading#0: 404: peN(H) <= 2(|S_support|-1) :: LHS=0 > RHS=-2
- [VIO] T(16) reading#0: 404: peN(H) <= 2(|S_support|-1) :: LHS=0 > RHS=-2

### id 406
statement: Let G be a tree on n > 2 vertices and H the union of all maximum critical independent sets of G. Then number of peN(H) ≤ peN(V-L) - 2, where L is the set of leaves of G.

- [VIO] C7[K3] reading#0: 406: peN(H) <= peN(V-L) - 2 :: LHS=0 > RHS=-2
- [VIO] C9[K3] reading#0: 406: peN(H) <= peN(V-L) - 2 :: LHS=0 > RHS=-2
- [VIO] CMP(3) reading#0: 406: peN(H) <= peN(V-L) - 2 :: LHS=0 > RHS=-2
- [VIO] CMP(4) reading#0: 406: peN(H) <= peN(V-L) - 2 :: LHS=0 > RHS=-2
- [VIO] CMP(5) reading#0: 406: peN(H) <= peN(V-L) - 2 :: LHS=0 > RHS=-2
- [VIO] CMP(6) reading#0: 406: peN(H) <= peN(V-L) - 2 :: LHS=0 > RHS=-2
- [VIO] CMP(7) reading#0: 406: peN(H) <= peN(V-L) - 2 :: LHS=0 > RHS=-2
- [VIO] CMP(8) reading#0: 406: peN(H) <= peN(V-L) - 2 :: LHS=0 > RHS=-2
- [VIO] CP(3) reading#0: 406: peN(H) <= peN(V-L) - 2 :: LHS=0 > RHS=-2
- [VIO] CP(4) reading#0: 406: peN(H) <= peN(V-L) - 2 :: LHS=0 > RHS=-2
- [VIO] CP(5) reading#0: 406: peN(H) <= peN(V-L) - 2 :: LHS=0 > RHS=-2
- [VIO] CP(6) reading#0: 406: peN(H) <= peN(V-L) - 2 :: LHS=0 > RHS=-2
- [VIO] CP(7) reading#0: 406: peN(H) <= peN(V-L) - 2 :: LHS=0 > RHS=-2
- [VIO] CP(8) reading#0: 406: peN(H) <= peN(V-L) - 2 :: LHS=0 > RHS=-2
- [VIO] K(3,3,3) reading#0: 406: peN(H) <= peN(V-L) - 2 :: LHS=0 > RHS=-2
- [VIO] KG(10,2) reading#0: 406: peN(H) <= peN(V-L) - 2 :: LHS=0 > RHS=-2
- [VIO] KG(11,2) reading#0: 406: peN(H) <= peN(V-L) - 2 :: LHS=0 > RHS=-2
- [VIO] KG(12,2) reading#0: 406: peN(H) <= peN(V-L) - 2 :: LHS=0 > RHS=-2
- [VIO] KG(13,2) reading#0: 406: peN(H) <= peN(V-L) - 2 :: LHS=0 > RHS=-2
- [VIO] KG(14,2) reading#0: 406: peN(H) <= peN(V-L) - 2 :: LHS=0 > RHS=-2
- [VIO] KG(15,2) reading#0: 406: peN(H) <= peN(V-L) - 2 :: LHS=0 > RHS=-2
- [VIO] KG(16,2) reading#0: 406: peN(H) <= peN(V-L) - 2 :: LHS=0 > RHS=-2
- [VIO] Paley(101) reading#0: 406: peN(H) <= peN(V-L) - 2 :: LHS=0 > RHS=-2
- [VIO] Paley(13) reading#0: 406: peN(H) <= peN(V-L) - 2 :: LHS=0 > RHS=-2
- [VIO] Paley(17) reading#0: 406: peN(H) <= peN(V-L) - 2 :: LHS=0 > RHS=-2
- [VIO] Paley(29) reading#0: 406: peN(H) <= peN(V-L) - 2 :: LHS=0 > RHS=-2
- [VIO] Paley(37) reading#0: 406: peN(H) <= peN(V-L) - 2 :: LHS=0 > RHS=-2
- [VIO] Paley(41) reading#0: 406: peN(H) <= peN(V-L) - 2 :: LHS=0 > RHS=-2
- [VIO] Paley(53) reading#0: 406: peN(H) <= peN(V-L) - 2 :: LHS=0 > RHS=-2
- [VIO] Paley(61) reading#0: 406: peN(H) <= peN(V-L) - 2 :: LHS=0 > RHS=-2
- [VIO] Paley(73) reading#0: 406: peN(H) <= peN(V-L) - 2 :: LHS=0 > RHS=-2
- [VIO] Paley(89) reading#0: 406: peN(H) <= peN(V-L) - 2 :: LHS=0 > RHS=-2
- [VIO] Paley(97) reading#0: 406: peN(H) <= peN(V-L) - 2 :: LHS=0 > RHS=-2
- [VIO] T(10) reading#0: 406: peN(H) <= peN(V-L) - 2 :: LHS=0 > RHS=-2
- [VIO] T(11) reading#0: 406: peN(H) <= peN(V-L) - 2 :: LHS=0 > RHS=-2
- [VIO] T(12) reading#0: 406: peN(H) <= peN(V-L) - 2 :: LHS=0 > RHS=-2
- [VIO] T(13) reading#0: 406: peN(H) <= peN(V-L) - 2 :: LHS=0 > RHS=-2
- [VIO] T(14) reading#0: 406: peN(H) <= peN(V-L) - 2 :: LHS=0 > RHS=-2
- [VIO] T(15) reading#0: 406: peN(H) <= peN(V-L) - 2 :: LHS=0 > RHS=-2
- [VIO] T(16) reading#0: 406: peN(H) <= peN(V-L) - 2 :: LHS=0 > RHS=-2

### id 412d
statement: Let G be a connected bipartite graph on n > 2 vertices and H the union of all maximum critical independent sets of G. Then |H| ≥ γ_T(G).

- [BRACKET] C7[K3] reading#0: 412d: |H| >= gamma_t :: LHS(lb)=0 < RHS(exact)=4; bounds insufficient
- [BRACKET] C9[K3] reading#0: 412d: |H| >= gamma_t :: LHS(lb)=0 < RHS(exact)=5; bounds insufficient
- [BRACKET] CMP(3) reading#0: 412d: |H| >= gamma_t :: LHS(lb)=0 < RHS(exact)=2; bounds insufficient
- [BRACKET] CMP(4) reading#0: 412d: |H| >= gamma_t :: LHS(lb)=0 < RHS(exact)=2; bounds insufficient
- [BRACKET] CMP(5) reading#0: 412d: |H| >= gamma_t :: LHS(lb)=0 < RHS(exact)=2; bounds insufficient
- [BRACKET] CMP(6) reading#0: 412d: |H| >= gamma_t :: LHS(lb)=0 < RHS(exact)=2; bounds insufficient
- [BRACKET] CMP(7) reading#0: 412d: |H| >= gamma_t :: LHS(lb)=0 < RHS(exact)=2; bounds insufficient
- [BRACKET] CMP(8) reading#0: 412d: |H| >= gamma_t :: LHS(lb)=0 < RHS(exact)=2; bounds insufficient
- [BRACKET] CP(3) reading#0: 412d: |H| >= gamma_t :: LHS(lb)=0 < RHS(exact)=2; bounds insufficient
- [BRACKET] CP(4) reading#0: 412d: |H| >= gamma_t :: LHS(lb)=0 < RHS(exact)=2; bounds insufficient
- [BRACKET] CP(5) reading#0: 412d: |H| >= gamma_t :: LHS(lb)=0 < RHS(exact)=2; bounds insufficient
- [BRACKET] CP(6) reading#0: 412d: |H| >= gamma_t :: LHS(lb)=0 < RHS(exact)=2; bounds insufficient
- [BRACKET] CP(7) reading#0: 412d: |H| >= gamma_t :: LHS(lb)=0 < RHS(exact)=2; bounds insufficient
- [BRACKET] CP(8) reading#0: 412d: |H| >= gamma_t :: LHS(lb)=0 < RHS(exact)=2; bounds insufficient
- [BRACKET] K(3,3,3) reading#0: 412d: |H| >= gamma_t :: LHS(lb)=0 < RHS(exact)=2; bounds insufficient
- [BRACKET] KG(10,2) reading#0: 412d: |H| >= gamma_t :: LHS(lb)=0 < RHS(exact)=3; bounds insufficient
- [BRACKET] KG(11,2) reading#0: 412d: |H| >= gamma_t :: LHS(lb)=0 < RHS(exact)=3; bounds insufficient
- [BRACKET] KG(12,2) reading#0: 412d: |H| >= gamma_t :: LHS(lb)=0 < RHS(exact)=3; bounds insufficient
- [BRACKET] KG(13,2) reading#0: 412d: |H| >= gamma_t :: LHS(lb)=0 < RHS(exact)=3; bounds insufficient
- [BRACKET] KG(14,2) reading#0: 412d: |H| >= gamma_t :: LHS(lb)=0 < RHS(exact)=3; bounds insufficient
- [BRACKET] KG(15,2) reading#0: 412d: |H| >= gamma_t :: LHS(lb)=0 < RHS(exact)=3; bounds insufficient
- [BRACKET] KG(16,2) reading#0: 412d: |H| >= gamma_t :: LHS(lb)=0 < RHS(exact)=3; bounds insufficient
- [BRACKET] Paley(101) reading#0: 412d: |H| >= gamma_t :: LHS(lb)=0 < RHS(exact)=5; bounds insufficient
- [BRACKET] Paley(13) reading#0: 412d: |H| >= gamma_t :: LHS(lb)=0 < RHS(exact)=4; bounds insufficient
- [BRACKET] Paley(17) reading#0: 412d: |H| >= gamma_t :: LHS(lb)=0 < RHS(exact)=4; bounds insufficient
- [BRACKET] Paley(29) reading#0: 412d: |H| >= gamma_t :: LHS(lb)=0 < RHS(exact)=4; bounds insufficient
- [BRACKET] Paley(37) reading#0: 412d: |H| >= gamma_t :: LHS(lb)=0 < RHS(exact)=4; bounds insufficient
- [BRACKET] Paley(41) reading#0: 412d: |H| >= gamma_t :: LHS(lb)=0 < RHS(exact)=4; bounds insufficient
- [BRACKET] Paley(53) reading#0: 412d: |H| >= gamma_t :: LHS(lb)=0 < RHS(exact)=4; bounds insufficient
- [BRACKET] Paley(61) reading#0: 412d: |H| >= gamma_t :: LHS(lb)=0 < RHS(exact)=4; bounds insufficient
- [BRACKET] Paley(73) reading#0: 412d: |H| >= gamma_t :: LHS(lb)=0 < RHS(exact)=5; bounds insufficient
- [BRACKET] Paley(89) reading#0: 412d: |H| >= gamma_t :: LHS(lb)=0 < RHS(exact)=5; bounds insufficient
- [BRACKET] Paley(97) reading#0: 412d: |H| >= gamma_t :: LHS(lb)=0 < RHS(exact)=5; bounds insufficient
- [BRACKET] T(10) reading#0: 412d: |H| >= gamma_t :: LHS(lb)=0 < RHS(exact)=6; bounds insufficient
- [BRACKET] T(11) reading#0: 412d: |H| >= gamma_t :: LHS(lb)=0 < RHS(exact)=7; bounds insufficient
- [BRACKET] T(12) reading#0: 412d: |H| >= gamma_t :: LHS(lb)=0 < RHS(exact)=8; bounds insufficient
- [BRACKET] T(13) reading#0: 412d: |H| >= gamma_t :: LHS(lb)=0 < RHS(exact)=8; bounds insufficient
- [BRACKET] T(14) reading#0: 412d: |H| >= gamma_t :: LHS(lb)=0 < RHS(exact)=9; bounds insufficient
- [BRACKET] T(15) reading#0: 412d: |H| >= gamma_t :: LHS(lb)=0 < RHS(exact)=10; bounds insufficient
- [BRACKET] T(16) reading#0: 412d: |H| >= gamma_t :: LHS(lb)=0 < RHS(exact)=10; bounds insufficient

### id 412e
statement: Let G be a connected bipartite graph on n > 2 vertices, P the set of pendant vertices and H the union of all maximum critical independent sets of G. Then |H| ≥ 1 + Δ(G[N(N(P))])

- [BRACKET] C7[K3] reading#0: 412e: |H| >= 1 + Delta(G[N(N(P))]) :: LHS(lb)=0 < RHS(exact)=1; bounds insufficient
- [BRACKET] C9[K3] reading#0: 412e: |H| >= 1 + Delta(G[N(N(P))]) :: LHS(lb)=0 < RHS(exact)=1; bounds insufficient
- [BRACKET] CMP(3) reading#0: 412e: |H| >= 1 + Delta(G[N(N(P))]) :: LHS(lb)=0 < RHS(exact)=1; bounds insufficient
- [BRACKET] CMP(4) reading#0: 412e: |H| >= 1 + Delta(G[N(N(P))]) :: LHS(lb)=0 < RHS(exact)=1; bounds insufficient
- [BRACKET] CMP(5) reading#0: 412e: |H| >= 1 + Delta(G[N(N(P))]) :: LHS(lb)=0 < RHS(exact)=1; bounds insufficient
- [BRACKET] CMP(6) reading#0: 412e: |H| >= 1 + Delta(G[N(N(P))]) :: LHS(lb)=0 < RHS(exact)=1; bounds insufficient
- [BRACKET] CMP(7) reading#0: 412e: |H| >= 1 + Delta(G[N(N(P))]) :: LHS(lb)=0 < RHS(exact)=1; bounds insufficient
- [BRACKET] CMP(8) reading#0: 412e: |H| >= 1 + Delta(G[N(N(P))]) :: LHS(lb)=0 < RHS(exact)=1; bounds insufficient
- [BRACKET] CP(3) reading#0: 412e: |H| >= 1 + Delta(G[N(N(P))]) :: LHS(lb)=0 < RHS(exact)=1; bounds insufficient
- [BRACKET] CP(4) reading#0: 412e: |H| >= 1 + Delta(G[N(N(P))]) :: LHS(lb)=0 < RHS(exact)=1; bounds insufficient
- [BRACKET] CP(5) reading#0: 412e: |H| >= 1 + Delta(G[N(N(P))]) :: LHS(lb)=0 < RHS(exact)=1; bounds insufficient
- [BRACKET] CP(6) reading#0: 412e: |H| >= 1 + Delta(G[N(N(P))]) :: LHS(lb)=0 < RHS(exact)=1; bounds insufficient
- [BRACKET] CP(7) reading#0: 412e: |H| >= 1 + Delta(G[N(N(P))]) :: LHS(lb)=0 < RHS(exact)=1; bounds insufficient
- [BRACKET] CP(8) reading#0: 412e: |H| >= 1 + Delta(G[N(N(P))]) :: LHS(lb)=0 < RHS(exact)=1; bounds insufficient
- [BRACKET] K(3,3,3) reading#0: 412e: |H| >= 1 + Delta(G[N(N(P))]) :: LHS(lb)=0 < RHS(exact)=1; bounds insufficient
- [BRACKET] KG(10,2) reading#0: 412e: |H| >= 1 + Delta(G[N(N(P))]) :: LHS(lb)=0 < RHS(exact)=1; bounds insufficient
- [BRACKET] KG(11,2) reading#0: 412e: |H| >= 1 + Delta(G[N(N(P))]) :: LHS(lb)=0 < RHS(exact)=1; bounds insufficient
- [BRACKET] KG(12,2) reading#0: 412e: |H| >= 1 + Delta(G[N(N(P))]) :: LHS(lb)=0 < RHS(exact)=1; bounds insufficient
- [BRACKET] KG(13,2) reading#0: 412e: |H| >= 1 + Delta(G[N(N(P))]) :: LHS(lb)=0 < RHS(exact)=1; bounds insufficient
- [BRACKET] KG(14,2) reading#0: 412e: |H| >= 1 + Delta(G[N(N(P))]) :: LHS(lb)=0 < RHS(exact)=1; bounds insufficient
- [BRACKET] KG(15,2) reading#0: 412e: |H| >= 1 + Delta(G[N(N(P))]) :: LHS(lb)=0 < RHS(exact)=1; bounds insufficient
- [BRACKET] KG(16,2) reading#0: 412e: |H| >= 1 + Delta(G[N(N(P))]) :: LHS(lb)=0 < RHS(exact)=1; bounds insufficient
- [BRACKET] Paley(101) reading#0: 412e: |H| >= 1 + Delta(G[N(N(P))]) :: LHS(lb)=0 < RHS(exact)=1; bounds insufficient
- [BRACKET] Paley(13) reading#0: 412e: |H| >= 1 + Delta(G[N(N(P))]) :: LHS(lb)=0 < RHS(exact)=1; bounds insufficient
- [BRACKET] Paley(17) reading#0: 412e: |H| >= 1 + Delta(G[N(N(P))]) :: LHS(lb)=0 < RHS(exact)=1; bounds insufficient
- [BRACKET] Paley(29) reading#0: 412e: |H| >= 1 + Delta(G[N(N(P))]) :: LHS(lb)=0 < RHS(exact)=1; bounds insufficient
- [BRACKET] Paley(37) reading#0: 412e: |H| >= 1 + Delta(G[N(N(P))]) :: LHS(lb)=0 < RHS(exact)=1; bounds insufficient
- [BRACKET] Paley(41) reading#0: 412e: |H| >= 1 + Delta(G[N(N(P))]) :: LHS(lb)=0 < RHS(exact)=1; bounds insufficient
- [BRACKET] Paley(53) reading#0: 412e: |H| >= 1 + Delta(G[N(N(P))]) :: LHS(lb)=0 < RHS(exact)=1; bounds insufficient
- [BRACKET] Paley(61) reading#0: 412e: |H| >= 1 + Delta(G[N(N(P))]) :: LHS(lb)=0 < RHS(exact)=1; bounds insufficient
- [BRACKET] Paley(73) reading#0: 412e: |H| >= 1 + Delta(G[N(N(P))]) :: LHS(lb)=0 < RHS(exact)=1; bounds insufficient
- [BRACKET] Paley(89) reading#0: 412e: |H| >= 1 + Delta(G[N(N(P))]) :: LHS(lb)=0 < RHS(exact)=1; bounds insufficient
- [BRACKET] Paley(97) reading#0: 412e: |H| >= 1 + Delta(G[N(N(P))]) :: LHS(lb)=0 < RHS(exact)=1; bounds insufficient
- [BRACKET] T(10) reading#0: 412e: |H| >= 1 + Delta(G[N(N(P))]) :: LHS(lb)=0 < RHS(exact)=1; bounds insufficient
- [BRACKET] T(11) reading#0: 412e: |H| >= 1 + Delta(G[N(N(P))]) :: LHS(lb)=0 < RHS(exact)=1; bounds insufficient
- [BRACKET] T(12) reading#0: 412e: |H| >= 1 + Delta(G[N(N(P))]) :: LHS(lb)=0 < RHS(exact)=1; bounds insufficient
- [BRACKET] T(13) reading#0: 412e: |H| >= 1 + Delta(G[N(N(P))]) :: LHS(lb)=0 < RHS(exact)=1; bounds insufficient
- [BRACKET] T(14) reading#0: 412e: |H| >= 1 + Delta(G[N(N(P))]) :: LHS(lb)=0 < RHS(exact)=1; bounds insufficient
- [BRACKET] T(15) reading#0: 412e: |H| >= 1 + Delta(G[N(N(P))]) :: LHS(lb)=0 < RHS(exact)=1; bounds insufficient
- [BRACKET] T(16) reading#0: 412e: |H| >= 1 + Delta(G[N(N(P))]) :: LHS(lb)=0 < RHS(exact)=1; bounds insufficient

## batch appended 2026-08-26 06:56:09

| id | verdict | vio | hold | bracket | premise_false | undef | tag |
|---|---|---|---|---|---|---|---|
| 412f | BRACKET | 0 | 0 | 47 | 0 | 3 | KNOWN_CORRUPT_READING |
| 413a | BRACKET | 0 | 41 | 6 | 0 | 3 |  |
| 413b | HOLDS_PARTIAL | 0 | 47 | 0 | 0 | 3 |  |
| 415a | HOLDS_PARTIAL | 0 | 47 | 0 | 0 | 3 |  |
| 415b | HOLDS_PARTIAL | 0 | 47 | 0 | 0 | 3 |  |
| 415c | HOLDS_PARTIAL | 0 | 47 | 0 | 0 | 3 |  |
| 416 | HOLDS_PARTIAL | 0 | 47 | 0 | 0 | 3 |  |
| 418b | UNSUPPORTED | 0 | 0 | 2 | 0 | 0 |  |
| 418c | UNSUPPORTED | 0 | 0 | 2 | 0 | 0 |  |
| 420b | HOLDS | 0 | 50 | 0 | 0 | 0 |  |

### id 412f
statement: Let G be a connected graph on n > 2 vertices, P the set of pendant vertices and H the union of all maximum critical independent sets of G. Then |H| ≥ μ(G[V-N(P)]), and if G is also bipartite then, the

- [BRACKET] C7[K3] reading#0: 412f: |H| >= mu(G[V-N(P)]) [KNOWN CORRUPT per README] :: LHS(lb)=0 < RHS(exact)=10; bounds insufficient
- [BRACKET] C9[K3] reading#0: 412f: |H| >= mu(G[V-N(P)]) [KNOWN CORRUPT per README] :: LHS(lb)=0 < RHS(exact)=13; bounds insufficient
- [BRACKET] CMP(3) reading#0: 412f: |H| >= mu(G[V-N(P)]) [KNOWN CORRUPT per README] :: LHS(lb)=0 < RHS(exact)=2; bounds insufficient
- [BRACKET] CMP(4) reading#0: 412f: |H| >= mu(G[V-N(P)]) [KNOWN CORRUPT per README] :: LHS(lb)=0 < RHS(exact)=3; bounds insufficient
- [BRACKET] CMP(5) reading#0: 412f: |H| >= mu(G[V-N(P)]) [KNOWN CORRUPT per README] :: LHS(lb)=0 < RHS(exact)=4; bounds insufficient
- [BRACKET] CMP(6) reading#0: 412f: |H| >= mu(G[V-N(P)]) [KNOWN CORRUPT per README] :: LHS(lb)=0 < RHS(exact)=5; bounds insufficient
- [BRACKET] CMP(7) reading#0: 412f: |H| >= mu(G[V-N(P)]) [KNOWN CORRUPT per README] :: LHS(lb)=0 < RHS(exact)=6; bounds insufficient
- [BRACKET] CMP(8) reading#0: 412f: |H| >= mu(G[V-N(P)]) [KNOWN CORRUPT per README] :: LHS(lb)=0 < RHS(exact)=7; bounds insufficient
- [BRACKET] CP(3) reading#0: 412f: |H| >= mu(G[V-N(P)]) [KNOWN CORRUPT per README] :: LHS(lb)=0 < RHS(exact)=3; bounds insufficient
- [BRACKET] CP(4) reading#0: 412f: |H| >= mu(G[V-N(P)]) [KNOWN CORRUPT per README] :: LHS(lb)=0 < RHS(exact)=4; bounds insufficient
- [BRACKET] CP(5) reading#0: 412f: |H| >= mu(G[V-N(P)]) [KNOWN CORRUPT per README] :: LHS(lb)=0 < RHS(exact)=5; bounds insufficient
- [BRACKET] CP(6) reading#0: 412f: |H| >= mu(G[V-N(P)]) [KNOWN CORRUPT per README] :: LHS(lb)=0 < RHS(exact)=6; bounds insufficient
- [BRACKET] CP(7) reading#0: 412f: |H| >= mu(G[V-N(P)]) [KNOWN CORRUPT per README] :: LHS(lb)=0 < RHS(exact)=7; bounds insufficient
- [BRACKET] CP(8) reading#0: 412f: |H| >= mu(G[V-N(P)]) [KNOWN CORRUPT per README] :: LHS(lb)=0 < RHS(exact)=8; bounds insufficient
- [BRACKET] K(3,3,3) reading#0: 412f: |H| >= mu(G[V-N(P)]) [KNOWN CORRUPT per README] :: LHS(lb)=0 < RHS(exact)=4; bounds insufficient
- [BRACKET] KG(10,2) reading#0: 412f: |H| >= mu(G[V-N(P)]) [KNOWN CORRUPT per README] :: LHS(lb)=0 < RHS(exact)=22; bounds insufficient
- [BRACKET] KG(11,2) reading#0: 412f: |H| >= mu(G[V-N(P)]) [KNOWN CORRUPT per README] :: LHS(lb)=0 < RHS(exact)=27; bounds insufficient
- [BRACKET] KG(12,2) reading#0: 412f: |H| >= mu(G[V-N(P)]) [KNOWN CORRUPT per README] :: LHS(lb)=0 < RHS(exact)=33; bounds insufficient
- [BRACKET] KG(13,2) reading#0: 412f: |H| >= mu(G[V-N(P)]) [KNOWN CORRUPT per README] :: LHS(lb)=0 < RHS(exact)=39; bounds insufficient
- [BRACKET] KG(14,2) reading#0: 412f: |H| >= mu(G[V-N(P)]) [KNOWN CORRUPT per README] :: LHS(lb)=0 < RHS(exact)=45; bounds insufficient
- [BRACKET] KG(15,2) reading#0: 412f: |H| >= mu(G[V-N(P)]) [KNOWN CORRUPT per README] :: LHS(lb)=0 < RHS(exact)=52; bounds insufficient
- [BRACKET] KG(16,2) reading#0: 412f: |H| >= mu(G[V-N(P)]) [KNOWN CORRUPT per README] :: LHS(lb)=0 < RHS(exact)=60; bounds insufficient
- [BRACKET] Paley(101) reading#0: 412f: |H| >= mu(G[V-N(P)]) [KNOWN CORRUPT per README] :: LHS(lb)=0 < RHS(exact)=50; bounds insufficient
- [BRACKET] Paley(13) reading#0: 412f: |H| >= mu(G[V-N(P)]) [KNOWN CORRUPT per README] :: LHS(lb)=0 < RHS(exact)=6; bounds insufficient
- [BRACKET] Paley(17) reading#0: 412f: |H| >= mu(G[V-N(P)]) [KNOWN CORRUPT per README] :: LHS(lb)=0 < RHS(exact)=8; bounds insufficient
- [BRACKET] Paley(29) reading#0: 412f: |H| >= mu(G[V-N(P)]) [KNOWN CORRUPT per README] :: LHS(lb)=0 < RHS(exact)=14; bounds insufficient
- [BRACKET] Paley(37) reading#0: 412f: |H| >= mu(G[V-N(P)]) [KNOWN CORRUPT per README] :: LHS(lb)=0 < RHS(exact)=18; bounds insufficient
- [BRACKET] Paley(41) reading#0: 412f: |H| >= mu(G[V-N(P)]) [KNOWN CORRUPT per README] :: LHS(lb)=0 < RHS(exact)=20; bounds insufficient
- [BRACKET] Paley(53) reading#0: 412f: |H| >= mu(G[V-N(P)]) [KNOWN CORRUPT per README] :: LHS(lb)=0 < RHS(exact)=26; bounds insufficient
- [BRACKET] Paley(61) reading#0: 412f: |H| >= mu(G[V-N(P)]) [KNOWN CORRUPT per README] :: LHS(lb)=0 < RHS(exact)=30; bounds insufficient
- [BRACKET] Paley(73) reading#0: 412f: |H| >= mu(G[V-N(P)]) [KNOWN CORRUPT per README] :: LHS(lb)=0 < RHS(exact)=36; bounds insufficient
- [BRACKET] Paley(89) reading#0: 412f: |H| >= mu(G[V-N(P)]) [KNOWN CORRUPT per README] :: LHS(lb)=0 < RHS(exact)=44; bounds insufficient
- [BRACKET] Paley(97) reading#0: 412f: |H| >= mu(G[V-N(P)]) [KNOWN CORRUPT per README] :: LHS(lb)=0 < RHS(exact)=48; bounds insufficient
- [BRACKET] T(10) reading#0: 412f: |H| >= mu(G[V-N(P)]) [KNOWN CORRUPT per README] :: LHS(lb)=0 < RHS(exact)=22; bounds insufficient
- [BRACKET] T(11) reading#0: 412f: |H| >= mu(G[V-N(P)]) [KNOWN CORRUPT per README] :: LHS(lb)=0 < RHS(exact)=27; bounds insufficient
- [BRACKET] T(12) reading#0: 412f: |H| >= mu(G[V-N(P)]) [KNOWN CORRUPT per README] :: LHS(lb)=0 < RHS(exact)=33; bounds insufficient
- [BRACKET] T(13) reading#0: 412f: |H| >= mu(G[V-N(P)]) [KNOWN CORRUPT per README] :: LHS(lb)=0 < RHS(exact)=39; bounds insufficient
- [BRACKET] T(14) reading#0: 412f: |H| >= mu(G[V-N(P)]) [KNOWN CORRUPT per README] :: LHS(lb)=0 < RHS(exact)=45; bounds insufficient
- [BRACKET] T(15) reading#0: 412f: |H| >= mu(G[V-N(P)]) [KNOWN CORRUPT per README] :: LHS(lb)=0 < RHS(exact)=52; bounds insufficient
- [BRACKET] T(16) reading#0: 412f: |H| >= mu(G[V-N(P)]) [KNOWN CORRUPT per README] :: LHS(lb)=0 < RHS(exact)=60; bounds insufficient

### id 413a
statement: Let G be a connected graph on n > 2 vertices, A the set of minimum degree vertices and H the union of all maximum critical independent sets of G. Then |H| ≥ κ(G) * α(G[V-A]) + μ(G[N(N(P))]

- [BRACKET] CMP(3) reading#0: 413a: |H| >= kappa*alpha(G[V-A]) + mu(G[N(N(P))]) :: LHS(lb)=0 < RHS(exact)=3; bounds insufficient
- [BRACKET] CMP(4) reading#0: 413a: |H| >= kappa*alpha(G[V-A]) + mu(G[N(N(P))]) :: LHS(lb)=0 < RHS(exact)=5; bounds insufficient
- [BRACKET] CMP(5) reading#0: 413a: |H| >= kappa*alpha(G[V-A]) + mu(G[N(N(P))]) :: LHS(lb)=0 < RHS(exact)=7; bounds insufficient
- [BRACKET] CMP(6) reading#0: 413a: |H| >= kappa*alpha(G[V-A]) + mu(G[N(N(P))]) :: LHS(lb)=0 < RHS(exact)=9; bounds insufficient
- [BRACKET] CMP(7) reading#0: 413a: |H| >= kappa*alpha(G[V-A]) + mu(G[N(N(P))]) :: LHS(lb)=0 < RHS(exact)=11; bounds insufficient
- [BRACKET] CMP(8) reading#0: 413a: |H| >= kappa*alpha(G[V-A]) + mu(G[N(N(P))]) :: LHS(lb)=0 < RHS(exact)=13; bounds insufficient

### id 418b
statement: Let G be a connected graph on n > 3 vertices, A the set of minimum degree vertices of G. Then i(G) ≤ α(G[V-A]) + |E(G[N(A)])|*p(G).

- [BRACKET] C7[K3] reading#0: 418b: i <= alpha(G[V-A]) + |E(G[N(A)])|*p_cov :: LHS(ub)=3 > RHS(exact)=0; bounds insufficient
- [BRACKET] C9[K3] reading#0: 418b: i <= alpha(G[V-A]) + |E(G[N(A)])|*p_cov :: LHS(ub)=3 > RHS(exact)=0; bounds insufficient

### id 418c
statement: Let G be a connected graph on n > 3 vertices, A the set of minimum degree vertices of G. Then i(G) ≤ α(G[V-A]) + |E(G[N(A)])| + |A ∩ I_c |.

- [BRACKET] C7[K3] reading#0: 418c: i <= alpha(G[V-A]) + |E(G[N(A)])| + |A cap I_core| :: LHS(ub)=3 > RHS(exact)=0; bounds insufficient
- [BRACKET] C9[K3] reading#0: 418c: i <= alpha(G[V-A]) + |E(G[N(A)])| + |A cap I_core| :: LHS(ub)=3 > RHS(exact)=0; bounds insufficient

## batch appended 2026-08-26 06:58:38

| id | verdict | vio | hold | bracket | premise_false | undef | tag |
|---|---|---|---|---|---|---|---|
| 420c | BRACKET | 0 | 40 | 10 | 0 | 0 |  |
| 421b | BRACKET | 0 | 46 | 4 | 0 | 0 |  |
| 421c | BRACKET | 0 | 49 | 1 | 0 | 0 |  |
| 422a | HOLDS | 0 | 50 | 0 | 0 | 0 |  |
| 422b | HOLDS_PARTIAL | 0 | 7 | 0 | 0 | 43 |  |
| 422c | HOLDS | 0 | 50 | 0 | 0 | 0 |  |
| 422d | BRACKET | 0 | 49 | 1 | 0 | 0 |  |
| 423 | HOLDS | 0 | 50 | 0 | 0 | 0 |  |
| 425d | BRACKET | 0 | 42 | 8 | 0 | 0 |  |
| 425e | BRACKET | 0 | 41 | 9 | 0 | 0 |  |

### id 420c
statement: Let G be a connected graph on n > 3 vertices, S the set of support vertices of G and T_min be the set of vertices incident with the fewest triangles. Then i(G) ≤ α(G[V(G)-N(S)]) + 4(|T_min |-1).

- [BRACKET] CMP(2) reading#0: 420c: i <= alpha(G[V-N(S_support)]) + 4(|T_min|-1) :: LHS(ub)=1 > RHS(exact)=-3; bounds insufficient
- [BRACKET] CP(2) reading#0: 420c: i <= alpha(G[V-N(S_support)]) + 4(|T_min|-1) :: LHS(ub)=2 > RHS(exact)=-2; bounds insufficient
- [BRACKET] K(3,3) reading#0: 420c: i <= alpha(G[V-N(S_support)]) + 4(|T_min|-1) :: LHS(ub)=3 > RHS(exact)=-1; bounds insufficient
- [BRACKET] comp(C5[K2]) reading#0: 420c: i <= alpha(G[V-N(S_support)]) + 4(|T_min|-1) :: LHS(ub)=4 > RHS(exact)=0; bounds insufficient
- [BRACKET] comp(C5[K3]) reading#0: 420c: i <= alpha(G[V-N(S_support)]) + 4(|T_min|-1) :: LHS(ub)=6 > RHS(exact)=2; bounds insufficient
- [BRACKET] comp(C5[K4]) reading#0: 420c: i <= alpha(G[V-N(S_support)]) + 4(|T_min|-1) :: LHS(ub)=8 > RHS(exact)=4; bounds insufficient
- [BRACKET] comp(C5[K5]) reading#0: 420c: i <= alpha(G[V-N(S_support)]) + 4(|T_min|-1) :: LHS(ub)=10 > RHS(exact)=6; bounds insufficient
- [BRACKET] comp(C5[K6]) reading#0: 420c: i <= alpha(G[V-N(S_support)]) + 4(|T_min|-1) :: LHS(ub)=12 > RHS(exact)=8; bounds insufficient
- [BRACKET] comp(C5[K7]) reading#0: 420c: i <= alpha(G[V-N(S_support)]) + 4(|T_min|-1) :: LHS(ub)=14 > RHS(exact)=10; bounds insufficient
- [BRACKET] comp(C5[K8]) reading#0: 420c: i <= alpha(G[V-N(S_support)]) + 4(|T_min|-1) :: LHS(ub)=16 > RHS(exact)=12; bounds insufficient

### id 421b
statement: Let G be a connected graph on n > 3 vertices and M_λ the vertices of maximum local independence. Then i(G) ≤ γ(G)FLOOR[0.5|N_max(e)| - 1].

- [BRACKET] CMP(2) reading#0: 421b: i <= gamma*floor(0.5*max|N(e)| - 1) :: LHS(ub)=1 > RHS(exact)=-1; bounds insufficient
- [BRACKET] CMP(3) reading#0: 421b: i <= gamma*floor(0.5*max|N(e)| - 1) :: LHS(ub)=1 > RHS(exact)=0; bounds insufficient
- [BRACKET] CP(2) reading#0: 421b: i <= gamma*floor(0.5*max|N(e)| - 1) :: LHS(ub)=2 > RHS(exact)=0; bounds insufficient
- [BRACKET] K(3,3) reading#0: 421b: i <= gamma*floor(0.5*max|N(e)| - 1) :: LHS(ub)=3 > RHS(exact)=2; bounds insufficient

### id 421c
statement: Let G be a connected graph on n > 3 vertices and M_λ the vertices of maximum local independence. Then i(G) ≤ γ(G)(|N[M_λ ]| - 3).

- [BRACKET] CMP(2) reading#0: 421c: i <= gamma*(|N[M_minlambda]| - 3) :: LHS(ub)=1 > RHS(exact)=0; bounds insufficient

### id 422d
statement: Let G be a connected graph on n > 3 vertices and D the set of vertices each of whose closed neighborhood contains the closed neighborhood of some other vertex. Then i(G) ≤ α(G[V-D])+FLOOR[ (|Ε (G[D])|

- [BRACKET] CP(2) reading#0: 422d: i <= alpha(G[V-D2]) + floor((|E(G[D2])|+1)/3), D:=D2 (low-confidence set id) :: LHS(ub)=2 > RHS(exact)=1; bounds insufficient

### id 425d
statement: Let G be a connected graph on n > 3 vertices and P the set of pendants of G. Then i(G) ≤ |T_min(G)| + sum of K_4(v)) + γ(G[V-N(P)]).

- [BRACKET] K(3,3) reading#0: 425d: i <= T_min + sum K_4(v) + gamma(G[V-N(P)]) :: LHS(ub)=3 > RHS(exact)=2; bounds insufficient
- [BRACKET] comp(C5[K2]) reading#0: 425d: i <= T_min + sum K_4(v) + gamma(G[V-N(P)]) :: LHS(ub)=4 > RHS(exact)=3; bounds insufficient
- [BRACKET] comp(C5[K3]) reading#0: 425d: i <= T_min + sum K_4(v) + gamma(G[V-N(P)]) :: LHS(ub)=6 > RHS(exact)=3; bounds insufficient
- [BRACKET] comp(C5[K4]) reading#0: 425d: i <= T_min + sum K_4(v) + gamma(G[V-N(P)]) :: LHS(ub)=8 > RHS(exact)=3; bounds insufficient
- [BRACKET] comp(C5[K5]) reading#0: 425d: i <= T_min + sum K_4(v) + gamma(G[V-N(P)]) :: LHS(ub)=10 > RHS(exact)=3; bounds insufficient
- [BRACKET] comp(C5[K6]) reading#0: 425d: i <= T_min + sum K_4(v) + gamma(G[V-N(P)]) :: LHS(ub)=12 > RHS(exact)=3; bounds insufficient
- [BRACKET] comp(C5[K7]) reading#0: 425d: i <= T_min + sum K_4(v) + gamma(G[V-N(P)]) :: LHS(ub)=14 > RHS(exact)=3; bounds insufficient
- [BRACKET] comp(C5[K8]) reading#0: 425d: i <= T_min + sum K_4(v) + gamma(G[V-N(P)]) :: LHS(ub)=16 > RHS(exact)=3; bounds insufficient

### id 425e
statement: Let G be a connected graph on n > 3 vertices and D the set of neighbor dominators of G. Then i(G) ≤ 4|T_min(G)| + |E(G[D])|

- [BRACKET] CMP(2) reading#0: 425e: i <= 4*T_min + |E(G[D2])| (D:=D2 low-conf) :: LHS(ub)=1 > RHS(exact)=0; bounds insufficient
- [BRACKET] K(3,3) reading#0: 425e: i <= 4*T_min + |E(G[D2])| (D:=D2 low-conf) :: LHS(ub)=3 > RHS(exact)=0; bounds insufficient
- [BRACKET] comp(C5[K2]) reading#0: 425e: i <= 4*T_min + |E(G[D2])| (D:=D2 low-conf) :: LHS(ub)=4 > RHS(exact)=0; bounds insufficient
- [BRACKET] comp(C5[K3]) reading#0: 425e: i <= 4*T_min + |E(G[D2])| (D:=D2 low-conf) :: LHS(ub)=6 > RHS(exact)=0; bounds insufficient
- [BRACKET] comp(C5[K4]) reading#0: 425e: i <= 4*T_min + |E(G[D2])| (D:=D2 low-conf) :: LHS(ub)=8 > RHS(exact)=0; bounds insufficient
- [BRACKET] comp(C5[K5]) reading#0: 425e: i <= 4*T_min + |E(G[D2])| (D:=D2 low-conf) :: LHS(ub)=10 > RHS(exact)=0; bounds insufficient
- [BRACKET] comp(C5[K6]) reading#0: 425e: i <= 4*T_min + |E(G[D2])| (D:=D2 low-conf) :: LHS(ub)=12 > RHS(exact)=0; bounds insufficient
- [BRACKET] comp(C5[K7]) reading#0: 425e: i <= 4*T_min + |E(G[D2])| (D:=D2 low-conf) :: LHS(ub)=14 > RHS(exact)=0; bounds insufficient
- [BRACKET] comp(C5[K8]) reading#0: 425e: i <= 4*T_min + |E(G[D2])| (D:=D2 low-conf) :: LHS(ub)=16 > RHS(exact)=0; bounds insufficient

## batch appended 2026-08-26 06:58:40

| id | verdict | vio | hold | bracket | premise_false | undef | tag |
|---|---|---|---|---|---|---|---|
| 426 | HOLDS_PARTIAL | 0 | 7 | 0 | 0 | 43 |  |
| 427 | BRACKET | 0 | 7 | 43 | 0 | 0 |  |
| 430a | NO_EVALUABLE_READINGS | 0 | 0 | 0 | 0 | 0 | KILLED_PRIOR_CAMPAIGN |
| 430c | HOLDS | 0 | 50 | 0 | 0 | 0 |  |
| 431a | BRACKET | 0 | 42 | 8 | 0 | 0 |  |
| 431b | HOLDS_PARTIAL | 0 | 7 | 0 | 0 | 43 |  |
| 431c | BRACKET | 0 | 41 | 9 | 0 | 0 |  |
| 432a | BRACKET | 0 | 35 | 15 | 0 | 0 |  |
| 432b | HOLDS | 0 | 50 | 0 | 0 | 0 |  |
| 433 | BRACKET | 0 | 7 | 43 | 0 | 0 |  |

### id 427
statement: Let G be a connected graph on n > 3 vertices and M the vertices of maximum degree. Then i(G) ≤ |E(C,V-C)| + FLOOR[(2/3)|E(G[V-N(P)])|].

- [BRACKET] C7[K3] reading#0: 427: i <= |E(C,V-C)| + floor[(2/3)|E(G[V-N(P)])|] :: LHS(ub)=3 > RHS(exact)=0; bounds insufficient
- [BRACKET] C9[K3] reading#0: 427: i <= |E(C,V-C)| + floor[(2/3)|E(G[V-N(P)])|] :: LHS(ub)=3 > RHS(exact)=0; bounds insufficient
- [BRACKET] CP(2) reading#0: 427: i <= |E(C,V-C)| + floor[(2/3)|E(G[V-N(P)])|] :: LHS(ub)=2 > RHS(exact)=0; bounds insufficient
- [BRACKET] CP(3) reading#0: 427: i <= |E(C,V-C)| + floor[(2/3)|E(G[V-N(P)])|] :: LHS(ub)=2 > RHS(exact)=0; bounds insufficient
- [BRACKET] CP(4) reading#0: 427: i <= |E(C,V-C)| + floor[(2/3)|E(G[V-N(P)])|] :: LHS(ub)=2 > RHS(exact)=0; bounds insufficient
- [BRACKET] CP(5) reading#0: 427: i <= |E(C,V-C)| + floor[(2/3)|E(G[V-N(P)])|] :: LHS(ub)=2 > RHS(exact)=0; bounds insufficient
- [BRACKET] CP(6) reading#0: 427: i <= |E(C,V-C)| + floor[(2/3)|E(G[V-N(P)])|] :: LHS(ub)=2 > RHS(exact)=0; bounds insufficient
- [BRACKET] CP(7) reading#0: 427: i <= |E(C,V-C)| + floor[(2/3)|E(G[V-N(P)])|] :: LHS(ub)=2 > RHS(exact)=0; bounds insufficient
- [BRACKET] CP(8) reading#0: 427: i <= |E(C,V-C)| + floor[(2/3)|E(G[V-N(P)])|] :: LHS(ub)=2 > RHS(exact)=0; bounds insufficient
- [BRACKET] K(3,3) reading#0: 427: i <= |E(C,V-C)| + floor[(2/3)|E(G[V-N(P)])|] :: LHS(ub)=3 > RHS(exact)=0; bounds insufficient
- [BRACKET] K(3,3,3) reading#0: 427: i <= |E(C,V-C)| + floor[(2/3)|E(G[V-N(P)])|] :: LHS(ub)=3 > RHS(exact)=0; bounds insufficient
- [BRACKET] KG(10,2) reading#0: 427: i <= |E(C,V-C)| + floor[(2/3)|E(G[V-N(P)])|] :: LHS(ub)=3 > RHS(exact)=0; bounds insufficient
- [BRACKET] KG(11,2) reading#0: 427: i <= |E(C,V-C)| + floor[(2/3)|E(G[V-N(P)])|] :: LHS(ub)=3 > RHS(exact)=0; bounds insufficient
- [BRACKET] KG(12,2) reading#0: 427: i <= |E(C,V-C)| + floor[(2/3)|E(G[V-N(P)])|] :: LHS(ub)=3 > RHS(exact)=0; bounds insufficient
- [BRACKET] KG(13,2) reading#0: 427: i <= |E(C,V-C)| + floor[(2/3)|E(G[V-N(P)])|] :: LHS(ub)=3 > RHS(exact)=0; bounds insufficient
- [BRACKET] KG(14,2) reading#0: 427: i <= |E(C,V-C)| + floor[(2/3)|E(G[V-N(P)])|] :: LHS(ub)=3 > RHS(exact)=0; bounds insufficient
- [BRACKET] KG(15,2) reading#0: 427: i <= |E(C,V-C)| + floor[(2/3)|E(G[V-N(P)])|] :: LHS(ub)=3 > RHS(exact)=0; bounds insufficient
- [BRACKET] KG(16,2) reading#0: 427: i <= |E(C,V-C)| + floor[(2/3)|E(G[V-N(P)])|] :: LHS(ub)=3 > RHS(exact)=0; bounds insufficient
- [BRACKET] Paley(101) reading#0: 427: i <= |E(C,V-C)| + floor[(2/3)|E(G[V-N(P)])|] :: LHS(ub)=5 > RHS(exact)=0; bounds insufficient
- [BRACKET] Paley(13) reading#0: 427: i <= |E(C,V-C)| + floor[(2/3)|E(G[V-N(P)])|] :: LHS(ub)=3 > RHS(exact)=0; bounds insufficient
- [BRACKET] Paley(17) reading#0: 427: i <= |E(C,V-C)| + floor[(2/3)|E(G[V-N(P)])|] :: LHS(ub)=3 > RHS(exact)=0; bounds insufficient
- [BRACKET] Paley(29) reading#0: 427: i <= |E(C,V-C)| + floor[(2/3)|E(G[V-N(P)])|] :: LHS(ub)=4 > RHS(exact)=0; bounds insufficient
- [BRACKET] Paley(37) reading#0: 427: i <= |E(C,V-C)| + floor[(2/3)|E(G[V-N(P)])|] :: LHS(ub)=4 > RHS(exact)=0; bounds insufficient
- [BRACKET] Paley(41) reading#0: 427: i <= |E(C,V-C)| + floor[(2/3)|E(G[V-N(P)])|] :: LHS(ub)=5 > RHS(exact)=0; bounds insufficient
- [BRACKET] Paley(53) reading#0: 427: i <= |E(C,V-C)| + floor[(2/3)|E(G[V-N(P)])|] :: LHS(ub)=5 > RHS(exact)=0; bounds insufficient
- [BRACKET] Paley(61) reading#0: 427: i <= |E(C,V-C)| + floor[(2/3)|E(G[V-N(P)])|] :: LHS(ub)=4 > RHS(exact)=0; bounds insufficient
- [BRACKET] Paley(73) reading#0: 427: i <= |E(C,V-C)| + floor[(2/3)|E(G[V-N(P)])|] :: LHS(ub)=5 > RHS(exact)=0; bounds insufficient
- [BRACKET] Paley(89) reading#0: 427: i <= |E(C,V-C)| + floor[(2/3)|E(G[V-N(P)])|] :: LHS(ub)=5 > RHS(exact)=0; bounds insufficient
- [BRACKET] Paley(97) reading#0: 427: i <= |E(C,V-C)| + floor[(2/3)|E(G[V-N(P)])|] :: LHS(ub)=5 > RHS(exact)=0; bounds insufficient
- [BRACKET] T(10) reading#0: 427: i <= |E(C,V-C)| + floor[(2/3)|E(G[V-N(P)])|] :: LHS(ub)=5 > RHS(exact)=0; bounds insufficient
- [BRACKET] T(11) reading#0: 427: i <= |E(C,V-C)| + floor[(2/3)|E(G[V-N(P)])|] :: LHS(ub)=5 > RHS(exact)=0; bounds insufficient
- [BRACKET] T(12) reading#0: 427: i <= |E(C,V-C)| + floor[(2/3)|E(G[V-N(P)])|] :: LHS(ub)=6 > RHS(exact)=0; bounds insufficient
- [BRACKET] T(13) reading#0: 427: i <= |E(C,V-C)| + floor[(2/3)|E(G[V-N(P)])|] :: LHS(ub)=6 > RHS(exact)=0; bounds insufficient
- [BRACKET] T(14) reading#0: 427: i <= |E(C,V-C)| + floor[(2/3)|E(G[V-N(P)])|] :: LHS(ub)=7 > RHS(exact)=0; bounds insufficient
- [BRACKET] T(15) reading#0: 427: i <= |E(C,V-C)| + floor[(2/3)|E(G[V-N(P)])|] :: LHS(ub)=7 > RHS(exact)=0; bounds insufficient
- [BRACKET] T(16) reading#0: 427: i <= |E(C,V-C)| + floor[(2/3)|E(G[V-N(P)])|] :: LHS(ub)=8 > RHS(exact)=0; bounds insufficient
- [BRACKET] comp(C5[K2]) reading#0: 427: i <= |E(C,V-C)| + floor[(2/3)|E(G[V-N(P)])|] :: LHS(ub)=4 > RHS(exact)=0; bounds insufficient
- [BRACKET] comp(C5[K3]) reading#0: 427: i <= |E(C,V-C)| + floor[(2/3)|E(G[V-N(P)])|] :: LHS(ub)=6 > RHS(exact)=0; bounds insufficient
- [BRACKET] comp(C5[K4]) reading#0: 427: i <= |E(C,V-C)| + floor[(2/3)|E(G[V-N(P)])|] :: LHS(ub)=8 > RHS(exact)=0; bounds insufficient
- [BRACKET] comp(C5[K5]) reading#0: 427: i <= |E(C,V-C)| + floor[(2/3)|E(G[V-N(P)])|] :: LHS(ub)=10 > RHS(exact)=0; bounds insufficient

### id 431a
statement: Let G be a connected graph on n > 3 vertices and D the set of vertices of degree two of G. Then i(G) ≤ residue(G)+ peN(N(D)) + |T_min(G)|.

- [BRACKET] K(3,3) reading#0: 431a: residue + peN(N(D_dominators)) + T_min (D:=neighbor dominators, low-conf) :: LHS(ub)=3 > RHS(exact)=2; bounds insufficient
- [BRACKET] comp(C5[K2]) reading#0: 431a: residue + peN(N(D_dominators)) + T_min (D:=neighbor dominators, low-conf) :: LHS(ub)=4 > RHS(exact)=2; bounds insufficient
- [BRACKET] comp(C5[K3]) reading#0: 431a: residue + peN(N(D_dominators)) + T_min (D:=neighbor dominators, low-conf) :: LHS(ub)=6 > RHS(exact)=3; bounds insufficient
- [BRACKET] comp(C5[K4]) reading#0: 431a: residue + peN(N(D_dominators)) + T_min (D:=neighbor dominators, low-conf) :: LHS(ub)=8 > RHS(exact)=3; bounds insufficient
- [BRACKET] comp(C5[K5]) reading#0: 431a: residue + peN(N(D_dominators)) + T_min (D:=neighbor dominators, low-conf) :: LHS(ub)=10 > RHS(exact)=3; bounds insufficient
- [BRACKET] comp(C5[K6]) reading#0: 431a: residue + peN(N(D_dominators)) + T_min (D:=neighbor dominators, low-conf) :: LHS(ub)=12 > RHS(exact)=3; bounds insufficient
- [BRACKET] comp(C5[K7]) reading#0: 431a: residue + peN(N(D_dominators)) + T_min (D:=neighbor dominators, low-conf) :: LHS(ub)=14 > RHS(exact)=3; bounds insufficient
- [BRACKET] comp(C5[K8]) reading#0: 431a: residue + peN(N(D_dominators)) + T_min (D:=neighbor dominators, low-conf) :: LHS(ub)=16 > RHS(exact)=3; bounds insufficient

### id 431c
statement: Let G be a connected graph on n > 3 vertices. Then i(G) ≤ residue(G) * |T_max(v)| + dd(G).

- [BRACKET] CP(2) reading#0: 431c: residue*T_max + dd :: LHS(ub)=2 > RHS(exact)=1; bounds insufficient
- [BRACKET] K(3,3) reading#0: 431c: residue*T_max + dd :: LHS(ub)=3 > RHS(exact)=1; bounds insufficient
- [BRACKET] comp(C5[K2]) reading#0: 431c: residue*T_max + dd :: LHS(ub)=4 > RHS(exact)=1; bounds insufficient
- [BRACKET] comp(C5[K3]) reading#0: 431c: residue*T_max + dd :: LHS(ub)=6 > RHS(exact)=1; bounds insufficient
- [BRACKET] comp(C5[K4]) reading#0: 431c: residue*T_max + dd :: LHS(ub)=8 > RHS(exact)=1; bounds insufficient
- [BRACKET] comp(C5[K5]) reading#0: 431c: residue*T_max + dd :: LHS(ub)=10 > RHS(exact)=1; bounds insufficient
- [BRACKET] comp(C5[K6]) reading#0: 431c: residue*T_max + dd :: LHS(ub)=12 > RHS(exact)=1; bounds insufficient
- [BRACKET] comp(C5[K7]) reading#0: 431c: residue*T_max + dd :: LHS(ub)=14 > RHS(exact)=1; bounds insufficient
- [BRACKET] comp(C5[K8]) reading#0: 431c: residue*T_max + dd :: LHS(ub)=16 > RHS(exact)=1; bounds insufficient

### id 432a
statement: Let G be a connected graph on n > 3 vertices. Then i(G) ≤ annihilation number + minimum{vertices at even distance from v - vertices at odd distance from v}.

- [BRACKET] CMP(3) reading#0: 432a: annihilation + min(dist_even - dist_odd) :: LHS(ub)=1 > RHS(exact)=-1; bounds insufficient
- [BRACKET] CMP(4) reading#0: 432a: annihilation + min(dist_even - dist_odd) :: LHS(ub)=1 > RHS(exact)=-2; bounds insufficient
- [BRACKET] CMP(5) reading#0: 432a: annihilation + min(dist_even - dist_odd) :: LHS(ub)=1 > RHS(exact)=-3; bounds insufficient
- [BRACKET] CMP(6) reading#0: 432a: annihilation + min(dist_even - dist_odd) :: LHS(ub)=1 > RHS(exact)=-4; bounds insufficient
- [BRACKET] CMP(7) reading#0: 432a: annihilation + min(dist_even - dist_odd) :: LHS(ub)=1 > RHS(exact)=-5; bounds insufficient
- [BRACKET] CMP(8) reading#0: 432a: annihilation + min(dist_even - dist_odd) :: LHS(ub)=1 > RHS(exact)=-6; bounds insufficient
- [BRACKET] CP(3) reading#0: 432a: annihilation + min(dist_even - dist_odd) :: LHS(ub)=2 > RHS(exact)=1; bounds insufficient
- [BRACKET] CP(4) reading#0: 432a: annihilation + min(dist_even - dist_odd) :: LHS(ub)=2 > RHS(exact)=0; bounds insufficient
- [BRACKET] CP(5) reading#0: 432a: annihilation + min(dist_even - dist_odd) :: LHS(ub)=2 > RHS(exact)=-1; bounds insufficient
- [BRACKET] CP(6) reading#0: 432a: annihilation + min(dist_even - dist_odd) :: LHS(ub)=2 > RHS(exact)=-2; bounds insufficient
- [BRACKET] CP(7) reading#0: 432a: annihilation + min(dist_even - dist_odd) :: LHS(ub)=2 > RHS(exact)=-3; bounds insufficient
- [BRACKET] CP(8) reading#0: 432a: annihilation + min(dist_even - dist_odd) :: LHS(ub)=2 > RHS(exact)=-4; bounds insufficient
- [BRACKET] K(3,3,3) reading#0: 432a: annihilation + min(dist_even - dist_odd) :: LHS(ub)=3 > RHS(exact)=1; bounds insufficient
- [BRACKET] KG(15,2) reading#0: 432a: annihilation + min(dist_even - dist_odd) :: LHS(ub)=3 > RHS(exact)=1; bounds insufficient
- [BRACKET] KG(16,2) reading#0: 432a: annihilation + min(dist_even - dist_odd) :: LHS(ub)=3 > RHS(exact)=-2; bounds insufficient

### id 433
statement: Let G be a connected graph on n > 3 vertices and P the set of pendants of G. Then i(G) ≤ 0.5|N(M)|*FLOOR[2*sum of inverses of degrees of G^2 ].

- [BRACKET] C7[K3] reading#0: 433: i <= 0.5*|N(M)|*floor(2*sum(1/deg of G^2)) :: LHS(ub)=3 > RHS(exact)=0; bounds insufficient
- [BRACKET] C9[K3] reading#0: 433: i <= 0.5*|N(M)|*floor(2*sum(1/deg of G^2)) :: LHS(ub)=3 > RHS(exact)=0; bounds insufficient
- [BRACKET] CP(2) reading#0: 433: i <= 0.5*|N(M)|*floor(2*sum(1/deg of G^2)) :: LHS(ub)=2 > RHS(exact)=0; bounds insufficient
- [BRACKET] CP(3) reading#0: 433: i <= 0.5*|N(M)|*floor(2*sum(1/deg of G^2)) :: LHS(ub)=2 > RHS(exact)=0; bounds insufficient
- [BRACKET] CP(4) reading#0: 433: i <= 0.5*|N(M)|*floor(2*sum(1/deg of G^2)) :: LHS(ub)=2 > RHS(exact)=0; bounds insufficient
- [BRACKET] CP(5) reading#0: 433: i <= 0.5*|N(M)|*floor(2*sum(1/deg of G^2)) :: LHS(ub)=2 > RHS(exact)=0; bounds insufficient
- [BRACKET] CP(6) reading#0: 433: i <= 0.5*|N(M)|*floor(2*sum(1/deg of G^2)) :: LHS(ub)=2 > RHS(exact)=0; bounds insufficient
- [BRACKET] CP(7) reading#0: 433: i <= 0.5*|N(M)|*floor(2*sum(1/deg of G^2)) :: LHS(ub)=2 > RHS(exact)=0; bounds insufficient
- [BRACKET] CP(8) reading#0: 433: i <= 0.5*|N(M)|*floor(2*sum(1/deg of G^2)) :: LHS(ub)=2 > RHS(exact)=0; bounds insufficient
- [BRACKET] K(3,3) reading#0: 433: i <= 0.5*|N(M)|*floor(2*sum(1/deg of G^2)) :: LHS(ub)=3 > RHS(exact)=0; bounds insufficient
- [BRACKET] K(3,3,3) reading#0: 433: i <= 0.5*|N(M)|*floor(2*sum(1/deg of G^2)) :: LHS(ub)=3 > RHS(exact)=0; bounds insufficient
- [BRACKET] KG(10,2) reading#0: 433: i <= 0.5*|N(M)|*floor(2*sum(1/deg of G^2)) :: LHS(ub)=3 > RHS(exact)=0; bounds insufficient
- [BRACKET] KG(11,2) reading#0: 433: i <= 0.5*|N(M)|*floor(2*sum(1/deg of G^2)) :: LHS(ub)=3 > RHS(exact)=0; bounds insufficient
- [BRACKET] KG(12,2) reading#0: 433: i <= 0.5*|N(M)|*floor(2*sum(1/deg of G^2)) :: LHS(ub)=3 > RHS(exact)=0; bounds insufficient
- [BRACKET] KG(13,2) reading#0: 433: i <= 0.5*|N(M)|*floor(2*sum(1/deg of G^2)) :: LHS(ub)=3 > RHS(exact)=0; bounds insufficient
- [BRACKET] KG(14,2) reading#0: 433: i <= 0.5*|N(M)|*floor(2*sum(1/deg of G^2)) :: LHS(ub)=3 > RHS(exact)=0; bounds insufficient
- [BRACKET] KG(15,2) reading#0: 433: i <= 0.5*|N(M)|*floor(2*sum(1/deg of G^2)) :: LHS(ub)=3 > RHS(exact)=0; bounds insufficient
- [BRACKET] KG(16,2) reading#0: 433: i <= 0.5*|N(M)|*floor(2*sum(1/deg of G^2)) :: LHS(ub)=3 > RHS(exact)=0; bounds insufficient
- [BRACKET] Paley(101) reading#0: 433: i <= 0.5*|N(M)|*floor(2*sum(1/deg of G^2)) :: LHS(ub)=5 > RHS(exact)=0; bounds insufficient
- [BRACKET] Paley(13) reading#0: 433: i <= 0.5*|N(M)|*floor(2*sum(1/deg of G^2)) :: LHS(ub)=3 > RHS(exact)=0; bounds insufficient
- [BRACKET] Paley(17) reading#0: 433: i <= 0.5*|N(M)|*floor(2*sum(1/deg of G^2)) :: LHS(ub)=3 > RHS(exact)=0; bounds insufficient
- [BRACKET] Paley(29) reading#0: 433: i <= 0.5*|N(M)|*floor(2*sum(1/deg of G^2)) :: LHS(ub)=4 > RHS(exact)=0; bounds insufficient
- [BRACKET] Paley(37) reading#0: 433: i <= 0.5*|N(M)|*floor(2*sum(1/deg of G^2)) :: LHS(ub)=4 > RHS(exact)=0; bounds insufficient
- [BRACKET] Paley(41) reading#0: 433: i <= 0.5*|N(M)|*floor(2*sum(1/deg of G^2)) :: LHS(ub)=5 > RHS(exact)=0; bounds insufficient
- [BRACKET] Paley(53) reading#0: 433: i <= 0.5*|N(M)|*floor(2*sum(1/deg of G^2)) :: LHS(ub)=5 > RHS(exact)=0; bounds insufficient
- [BRACKET] Paley(61) reading#0: 433: i <= 0.5*|N(M)|*floor(2*sum(1/deg of G^2)) :: LHS(ub)=4 > RHS(exact)=0; bounds insufficient
- [BRACKET] Paley(73) reading#0: 433: i <= 0.5*|N(M)|*floor(2*sum(1/deg of G^2)) :: LHS(ub)=5 > RHS(exact)=0; bounds insufficient
- [BRACKET] Paley(89) reading#0: 433: i <= 0.5*|N(M)|*floor(2*sum(1/deg of G^2)) :: LHS(ub)=5 > RHS(exact)=0; bounds insufficient
- [BRACKET] Paley(97) reading#0: 433: i <= 0.5*|N(M)|*floor(2*sum(1/deg of G^2)) :: LHS(ub)=5 > RHS(exact)=0; bounds insufficient
- [BRACKET] T(10) reading#0: 433: i <= 0.5*|N(M)|*floor(2*sum(1/deg of G^2)) :: LHS(ub)=5 > RHS(exact)=0; bounds insufficient
- [BRACKET] T(11) reading#0: 433: i <= 0.5*|N(M)|*floor(2*sum(1/deg of G^2)) :: LHS(ub)=5 > RHS(exact)=0; bounds insufficient
- [BRACKET] T(12) reading#0: 433: i <= 0.5*|N(M)|*floor(2*sum(1/deg of G^2)) :: LHS(ub)=6 > RHS(exact)=0; bounds insufficient
- [BRACKET] T(13) reading#0: 433: i <= 0.5*|N(M)|*floor(2*sum(1/deg of G^2)) :: LHS(ub)=6 > RHS(exact)=0; bounds insufficient
- [BRACKET] T(14) reading#0: 433: i <= 0.5*|N(M)|*floor(2*sum(1/deg of G^2)) :: LHS(ub)=7 > RHS(exact)=0; bounds insufficient
- [BRACKET] T(15) reading#0: 433: i <= 0.5*|N(M)|*floor(2*sum(1/deg of G^2)) :: LHS(ub)=7 > RHS(exact)=0; bounds insufficient
- [BRACKET] T(16) reading#0: 433: i <= 0.5*|N(M)|*floor(2*sum(1/deg of G^2)) :: LHS(ub)=8 > RHS(exact)=0; bounds insufficient
- [BRACKET] comp(C5[K2]) reading#0: 433: i <= 0.5*|N(M)|*floor(2*sum(1/deg of G^2)) :: LHS(ub)=4 > RHS(exact)=0; bounds insufficient
- [BRACKET] comp(C5[K3]) reading#0: 433: i <= 0.5*|N(M)|*floor(2*sum(1/deg of G^2)) :: LHS(ub)=6 > RHS(exact)=0; bounds insufficient
- [BRACKET] comp(C5[K4]) reading#0: 433: i <= 0.5*|N(M)|*floor(2*sum(1/deg of G^2)) :: LHS(ub)=8 > RHS(exact)=0; bounds insufficient
- [BRACKET] comp(C5[K5]) reading#0: 433: i <= 0.5*|N(M)|*floor(2*sum(1/deg of G^2)) :: LHS(ub)=10 > RHS(exact)=0; bounds insufficient

## batch appended 2026-08-26 06:58:40

| id | verdict | vio | hold | bracket | premise_false | undef | tag |
|---|---|---|---|---|---|---|---|
| 434a | HOLDS | 0 | 50 | 0 | 0 | 0 |  |
| 434a-dup2 | HOLDS | 0 | 50 | 0 | 0 | 0 |  |
| 434b | HOLDS | 0 | 50 | 0 | 0 | 0 |  |
| 434c | HOLDS | 0 | 50 | 0 | 0 | 0 |  |
| 434d | HOLDS | 0 | 50 | 0 | 0 | 0 |  |
| 434e | BRACKET | 0 | 41 | 9 | 0 | 0 |  |
| 435 | HOLDS | 0 | 50 | 0 | 0 | 0 |  |
| 436c | BRACKET | 0 | 49 | 1 | 0 | 0 |  |
| 438a | HOLDS | 0 | 50 | 0 | 0 | 0 |  |
| 438b | HOLDS | 0 | 50 | 0 | 0 | 0 |  |

### id 434e
statement: Let G be a connected graph on n > 3 vertices and C the center of G, i.e. the set of vertices of minimum eccentricity of G. Then i(G) ≤ SW(G^c ) - ecc(C) + 2, where ecc(C) is the eccentricity of the se

- [BRACKET] CP(2) reading#0: 434e-alt member: SW(comp) - radius + 2 :: LHS(ub)=2 > RHS(exact)=1; bounds insufficient
- [BRACKET] CP(3) reading#0: 434e-alt member: SW(comp) - radius + 2 :: LHS(ub)=2 > RHS(exact)=1; bounds insufficient
- [BRACKET] CP(4) reading#0: 434e-alt member: SW(comp) - radius + 2 :: LHS(ub)=2 > RHS(exact)=1; bounds insufficient
- [BRACKET] CP(5) reading#0: 434e-alt member: SW(comp) - radius + 2 :: LHS(ub)=2 > RHS(exact)=1; bounds insufficient
- [BRACKET] CP(6) reading#0: 434e-alt member: SW(comp) - radius + 2 :: LHS(ub)=2 > RHS(exact)=1; bounds insufficient
- [BRACKET] CP(7) reading#0: 434e-alt member: SW(comp) - radius + 2 :: LHS(ub)=2 > RHS(exact)=1; bounds insufficient
- [BRACKET] CP(8) reading#0: 434e-alt member: SW(comp) - radius + 2 :: LHS(ub)=2 > RHS(exact)=1; bounds insufficient
- [BRACKET] K(3,3) reading#0: 434e-alt member: SW(comp) - radius + 2 :: LHS(ub)=3 > RHS(exact)=2; bounds insufficient
- [BRACKET] K(3,3,3) reading#0: 434e-alt member: SW(comp) - radius + 2 :: LHS(ub)=3 > RHS(exact)=2; bounds insufficient

### id 436c
statement: Let G be a connected graph on n > 3 vertices. Then α_2(G) ≤ k* WP( bar(G) ) + Δ(G[D]), where Δ(G[D]) is the maximum degree of the subgraph induced by the nighbor dominators and k is the kth step for a

- [BRACKET] CMP(2) reading#0: 436c: alpha_2 <= HH_k*WP(bar) + Delta(G[D_dominators]) :: LHS(ub)=3 > RHS(exact)=2; bounds insufficient

## batch appended 2026-08-26 07:03:22

| id | verdict | vio | hold | bracket | premise_false | undef | tag |
|---|---|---|---|---|---|---|---|
| 439 | BRACKET | 0 | 6 | 44 | 0 | 0 |  |
| 442 | HOLDS | 0 | 50 | 0 | 0 | 0 |  |
| 443 | BRACKET | 0 | 42 | 1 | 0 | 7 |  |
| 444 | HOLDS | 0 | 50 | 0 | 0 | 0 |  |
| 446 | BRACKET | 0 | 6 | 1 | 0 | 43 |  |
| 448a | BRACKET | 0 | 49 | 1 | 0 | 0 |  |
| 448b | BRACKET | 0 | 0 | 50 | 0 | 0 | KNOWN_CORRUPT_READING |
| 449 | HOLDS | 0 | 50 | 0 | 0 | 0 |  |
| 450 | NO_EVALUABLE_READINGS | 0 | 0 | 0 | 0 | 50 |  |
| 59 | HOLDS_PARTIAL | 0 | 30 | 0 | 0 | 20 |  |

### id 439
statement: Let G be a connected graph on n > 3 vertices. Then α_2(G) ≤ |N(M)| + FLOOR[2(CW(G) -1)], where M is the set of maximum degree vertices and CW(G) is the Caro-Wei invariant of G.

- [BRACKET] C7[K3] reading#0: 439: alpha_2 <= |N(M)| + floor[2(CW-1)] :: LHS(ub)=6 > RHS(exact)=2; bounds insufficient
- [BRACKET] C9[K3] reading#0: 439: alpha_2 <= |N(M)| + floor[2(CW-1)] :: LHS(ub)=8 > RHS(exact)=4; bounds insufficient
- [BRACKET] CMP(2) reading#0: 439: alpha_2 <= |N(M)| + floor[2(CW-1)] :: LHS(ub)=3 > RHS(exact)=2; bounds insufficient
- [BRACKET] CP(2) reading#0: 439: alpha_2 <= |N(M)| + floor[2(CW-1)] :: LHS(ub)=3 > RHS(exact)=0; bounds insufficient
- [BRACKET] CP(3) reading#0: 439: alpha_2 <= |N(M)| + floor[2(CW-1)] :: LHS(ub)=3 > RHS(exact)=0; bounds insufficient
- [BRACKET] CP(4) reading#0: 439: alpha_2 <= |N(M)| + floor[2(CW-1)] :: LHS(ub)=3 > RHS(exact)=0; bounds insufficient
- [BRACKET] CP(5) reading#0: 439: alpha_2 <= |N(M)| + floor[2(CW-1)] :: LHS(ub)=3 > RHS(exact)=0; bounds insufficient
- [BRACKET] CP(6) reading#0: 439: alpha_2 <= |N(M)| + floor[2(CW-1)] :: LHS(ub)=3 > RHS(exact)=0; bounds insufficient
- [BRACKET] CP(7) reading#0: 439: alpha_2 <= |N(M)| + floor[2(CW-1)] :: LHS(ub)=3 > RHS(exact)=0; bounds insufficient
- [BRACKET] CP(8) reading#0: 439: alpha_2 <= |N(M)| + floor[2(CW-1)] :: LHS(ub)=3 > RHS(exact)=0; bounds insufficient
- [BRACKET] K(3,3) reading#0: 439: alpha_2 <= |N(M)| + floor[2(CW-1)] :: LHS(ub)=4 > RHS(exact)=1; bounds insufficient
- [BRACKET] K(3,3,3) reading#0: 439: alpha_2 <= |N(M)| + floor[2(CW-1)] :: LHS(ub)=4 > RHS(exact)=0; bounds insufficient
- [BRACKET] KG(10,2) reading#0: 439: alpha_2 <= |N(M)| + floor[2(CW-1)] :: LHS(ub)=10 > RHS(exact)=1; bounds insufficient
- [BRACKET] KG(11,2) reading#0: 439: alpha_2 <= |N(M)| + floor[2(CW-1)] :: LHS(ub)=11 > RHS(exact)=0; bounds insufficient
- [BRACKET] KG(12,2) reading#0: 439: alpha_2 <= |N(M)| + floor[2(CW-1)] :: LHS(ub)=12 > RHS(exact)=0; bounds insufficient
- [BRACKET] KG(13,2) reading#0: 439: alpha_2 <= |N(M)| + floor[2(CW-1)] :: LHS(ub)=13 > RHS(exact)=0; bounds insufficient
- [BRACKET] KG(14,2) reading#0: 439: alpha_2 <= |N(M)| + floor[2(CW-1)] :: LHS(ub)=14 > RHS(exact)=0; bounds insufficient
- [BRACKET] KG(15,2) reading#0: 439: alpha_2 <= |N(M)| + floor[2(CW-1)] :: LHS(ub)=15 > RHS(exact)=0; bounds insufficient
- [BRACKET] KG(16,2) reading#0: 439: alpha_2 <= |N(M)| + floor[2(CW-1)] :: LHS(ub)=16 > RHS(exact)=0; bounds insufficient
- [BRACKET] Paley(101) reading#0: 439: alpha_2 <= |N(M)| + floor[2(CW-1)] :: LHS(ub)=10 > RHS(exact)=1; bounds insufficient
- [BRACKET] Paley(13) reading#0: 439: alpha_2 <= |N(M)| + floor[2(CW-1)] :: LHS(ub)=5 > RHS(exact)=1; bounds insufficient
- [BRACKET] Paley(17) reading#0: 439: alpha_2 <= |N(M)| + floor[2(CW-1)] :: LHS(ub)=5 > RHS(exact)=1; bounds insufficient
- [BRACKET] Paley(29) reading#0: 439: alpha_2 <= |N(M)| + floor[2(CW-1)] :: LHS(ub)=6 > RHS(exact)=1; bounds insufficient
- [BRACKET] Paley(37) reading#0: 439: alpha_2 <= |N(M)| + floor[2(CW-1)] :: LHS(ub)=7 > RHS(exact)=1; bounds insufficient
- [BRACKET] Paley(41) reading#0: 439: alpha_2 <= |N(M)| + floor[2(CW-1)] :: LHS(ub)=7 > RHS(exact)=1; bounds insufficient
- [BRACKET] Paley(53) reading#0: 439: alpha_2 <= |N(M)| + floor[2(CW-1)] :: LHS(ub)=8 > RHS(exact)=1; bounds insufficient
- [BRACKET] Paley(61) reading#0: 439: alpha_2 <= |N(M)| + floor[2(CW-1)] :: LHS(ub)=8 > RHS(exact)=1; bounds insufficient
- [BRACKET] Paley(73) reading#0: 439: alpha_2 <= |N(M)| + floor[2(CW-1)] :: LHS(ub)=8 > RHS(exact)=1; bounds insufficient
- [BRACKET] Paley(89) reading#0: 439: alpha_2 <= |N(M)| + floor[2(CW-1)] :: LHS(ub)=9 > RHS(exact)=1; bounds insufficient
- [BRACKET] Paley(97) reading#0: 439: alpha_2 <= |N(M)| + floor[2(CW-1)] :: LHS(ub)=9 > RHS(exact)=1; bounds insufficient
- [BRACKET] T(10) reading#0: 439: alpha_2 <= |N(M)| + floor[2(CW-1)] :: LHS(ub)=7 > RHS(exact)=3; bounds insufficient
- [BRACKET] T(11) reading#0: 439: alpha_2 <= |N(M)| + floor[2(CW-1)] :: LHS(ub)=8 > RHS(exact)=3; bounds insufficient
- [BRACKET] T(12) reading#0: 439: alpha_2 <= |N(M)| + floor[2(CW-1)] :: LHS(ub)=9 > RHS(exact)=4; bounds insufficient
- [BRACKET] T(13) reading#0: 439: alpha_2 <= |N(M)| + floor[2(CW-1)] :: LHS(ub)=9 > RHS(exact)=4; bounds insufficient
- [BRACKET] T(14) reading#0: 439: alpha_2 <= |N(M)| + floor[2(CW-1)] :: LHS(ub)=10 > RHS(exact)=5; bounds insufficient
- [BRACKET] T(15) reading#0: 439: alpha_2 <= |N(M)| + floor[2(CW-1)] :: LHS(ub)=11 > RHS(exact)=5; bounds insufficient
- [BRACKET] T(16) reading#0: 439: alpha_2 <= |N(M)| + floor[2(CW-1)] :: LHS(ub)=11 > RHS(exact)=6; bounds insufficient
- [BRACKET] comp(C5[K2]) reading#0: 439: alpha_2 <= |N(M)| + floor[2(CW-1)] :: LHS(ub)=5 > RHS(exact)=2; bounds insufficient
- [BRACKET] comp(C5[K3]) reading#0: 439: alpha_2 <= |N(M)| + floor[2(CW-1)] :: LHS(ub)=7 > RHS(exact)=2; bounds insufficient
- [BRACKET] comp(C5[K4]) reading#0: 439: alpha_2 <= |N(M)| + floor[2(CW-1)] :: LHS(ub)=9 > RHS(exact)=2; bounds insufficient

### id 443
statement: Let G be a connected graph on n > 3 vertices. Then α_2(G) ≤ sum of disparities - |N(A_c )| -2, where A_c is the intersection of all maximum independent sets of G.

- [BRACKET] CP(2) reading#0: 443: alpha_2 <= sum(disparities) - |N(A_core)| - 2 :: LHS(ub)=3 > RHS(exact)=2; bounds insufficient

### id 446
statement: Let G be a connected graph on n > 3 vertices. Then α_2(G) ≤ p Ν(Α) + |V\S|, where A is the set of minimum degree vertices and S is the set of support vertices.

- [BRACKET] CMP(2) reading#0: 446: alpha_2 <= rho(<N(A)> radius reading) + |V-S_support| :: LHS(ub)=3 > RHS(exact)=2; bounds insufficient

### id 448a
statement: Let G be a connected graph on n > 3 vertices. Then α_2(G) ≤ |H_n/2 | + |E(G[V-H_n/2 ])| + ρ(G), where H_n/2 is the set of vertices of degree greater than n/2 in G.

- [BRACKET] CMP(2) reading#0: 448a: alpha_2 <= |H_{n/2}| + |E(G[V-H_{n/2}])| + radius :: LHS(ub)=3 > RHS(exact)=2; bounds insufficient

### id 448b
statement: Let G be a connected graph on n > 3 vertices. Then α_2(G) ≤ |V-A| + |E(G[N(S)])| + ρ(G), where A is the set of vertices of minimum degree and S is the set of support vertices in G.

- [BRACKET] C7[K3] reading#0: 448b: alpha_2 <= |V-A| + |E(G[N(S_support)])| + radius [KNOWN CORRUPT per README] :: LHS(ub)=6 > RHS(exact)=3; bounds insufficient
- [BRACKET] C9[K3] reading#0: 448b: alpha_2 <= |V-A| + |E(G[N(S_support)])| + radius [KNOWN CORRUPT per README] :: LHS(ub)=8 > RHS(exact)=4; bounds insufficient
- [BRACKET] CMP(2) reading#0: 448b: alpha_2 <= |V-A| + |E(G[N(S_support)])| + radius [KNOWN CORRUPT per README] :: LHS(ub)=3 > RHS(exact)=2; bounds insufficient
- [BRACKET] CMP(3) reading#0: 448b: alpha_2 <= |V-A| + |E(G[N(S_support)])| + radius [KNOWN CORRUPT per README] :: LHS(ub)=3 > RHS(exact)=2; bounds insufficient
- [BRACKET] CMP(4) reading#0: 448b: alpha_2 <= |V-A| + |E(G[N(S_support)])| + radius [KNOWN CORRUPT per README] :: LHS(ub)=3 > RHS(exact)=2; bounds insufficient
- [BRACKET] CMP(5) reading#0: 448b: alpha_2 <= |V-A| + |E(G[N(S_support)])| + radius [KNOWN CORRUPT per README] :: LHS(ub)=3 > RHS(exact)=2; bounds insufficient
- [BRACKET] CMP(6) reading#0: 448b: alpha_2 <= |V-A| + |E(G[N(S_support)])| + radius [KNOWN CORRUPT per README] :: LHS(ub)=3 > RHS(exact)=2; bounds insufficient
- [BRACKET] CMP(7) reading#0: 448b: alpha_2 <= |V-A| + |E(G[N(S_support)])| + radius [KNOWN CORRUPT per README] :: LHS(ub)=3 > RHS(exact)=2; bounds insufficient
- [BRACKET] CMP(8) reading#0: 448b: alpha_2 <= |V-A| + |E(G[N(S_support)])| + radius [KNOWN CORRUPT per README] :: LHS(ub)=3 > RHS(exact)=2; bounds insufficient
- [BRACKET] CP(2) reading#0: 448b: alpha_2 <= |V-A| + |E(G[N(S_support)])| + radius [KNOWN CORRUPT per README] :: LHS(ub)=3 > RHS(exact)=2; bounds insufficient
- [BRACKET] CP(3) reading#0: 448b: alpha_2 <= |V-A| + |E(G[N(S_support)])| + radius [KNOWN CORRUPT per README] :: LHS(ub)=3 > RHS(exact)=2; bounds insufficient
- [BRACKET] CP(4) reading#0: 448b: alpha_2 <= |V-A| + |E(G[N(S_support)])| + radius [KNOWN CORRUPT per README] :: LHS(ub)=3 > RHS(exact)=2; bounds insufficient
- [BRACKET] CP(5) reading#0: 448b: alpha_2 <= |V-A| + |E(G[N(S_support)])| + radius [KNOWN CORRUPT per README] :: LHS(ub)=3 > RHS(exact)=2; bounds insufficient
- [BRACKET] CP(6) reading#0: 448b: alpha_2 <= |V-A| + |E(G[N(S_support)])| + radius [KNOWN CORRUPT per README] :: LHS(ub)=3 > RHS(exact)=2; bounds insufficient
- [BRACKET] CP(7) reading#0: 448b: alpha_2 <= |V-A| + |E(G[N(S_support)])| + radius [KNOWN CORRUPT per README] :: LHS(ub)=3 > RHS(exact)=2; bounds insufficient
- [BRACKET] CP(8) reading#0: 448b: alpha_2 <= |V-A| + |E(G[N(S_support)])| + radius [KNOWN CORRUPT per README] :: LHS(ub)=3 > RHS(exact)=2; bounds insufficient
- [BRACKET] K(3,3) reading#0: 448b: alpha_2 <= |V-A| + |E(G[N(S_support)])| + radius [KNOWN CORRUPT per README] :: LHS(ub)=4 > RHS(exact)=2; bounds insufficient
- [BRACKET] K(3,3,3) reading#0: 448b: alpha_2 <= |V-A| + |E(G[N(S_support)])| + radius [KNOWN CORRUPT per README] :: LHS(ub)=4 > RHS(exact)=2; bounds insufficient
- [BRACKET] KG(10,2) reading#0: 448b: alpha_2 <= |V-A| + |E(G[N(S_support)])| + radius [KNOWN CORRUPT per README] :: LHS(ub)=10 > RHS(exact)=2; bounds insufficient
- [BRACKET] KG(11,2) reading#0: 448b: alpha_2 <= |V-A| + |E(G[N(S_support)])| + radius [KNOWN CORRUPT per README] :: LHS(ub)=11 > RHS(exact)=2; bounds insufficient
- [BRACKET] KG(12,2) reading#0: 448b: alpha_2 <= |V-A| + |E(G[N(S_support)])| + radius [KNOWN CORRUPT per README] :: LHS(ub)=12 > RHS(exact)=2; bounds insufficient
- [BRACKET] KG(13,2) reading#0: 448b: alpha_2 <= |V-A| + |E(G[N(S_support)])| + radius [KNOWN CORRUPT per README] :: LHS(ub)=13 > RHS(exact)=2; bounds insufficient
- [BRACKET] KG(14,2) reading#0: 448b: alpha_2 <= |V-A| + |E(G[N(S_support)])| + radius [KNOWN CORRUPT per README] :: LHS(ub)=14 > RHS(exact)=2; bounds insufficient
- [BRACKET] KG(15,2) reading#0: 448b: alpha_2 <= |V-A| + |E(G[N(S_support)])| + radius [KNOWN CORRUPT per README] :: LHS(ub)=15 > RHS(exact)=2; bounds insufficient
- [BRACKET] KG(16,2) reading#0: 448b: alpha_2 <= |V-A| + |E(G[N(S_support)])| + radius [KNOWN CORRUPT per README] :: LHS(ub)=16 > RHS(exact)=2; bounds insufficient
- [BRACKET] Paley(101) reading#0: 448b: alpha_2 <= |V-A| + |E(G[N(S_support)])| + radius [KNOWN CORRUPT per README] :: LHS(ub)=10 > RHS(exact)=2; bounds insufficient
- [BRACKET] Paley(13) reading#0: 448b: alpha_2 <= |V-A| + |E(G[N(S_support)])| + radius [KNOWN CORRUPT per README] :: LHS(ub)=5 > RHS(exact)=2; bounds insufficient
- [BRACKET] Paley(17) reading#0: 448b: alpha_2 <= |V-A| + |E(G[N(S_support)])| + radius [KNOWN CORRUPT per README] :: LHS(ub)=5 > RHS(exact)=2; bounds insufficient
- [BRACKET] Paley(29) reading#0: 448b: alpha_2 <= |V-A| + |E(G[N(S_support)])| + radius [KNOWN CORRUPT per README] :: LHS(ub)=6 > RHS(exact)=2; bounds insufficient
- [BRACKET] Paley(37) reading#0: 448b: alpha_2 <= |V-A| + |E(G[N(S_support)])| + radius [KNOWN CORRUPT per README] :: LHS(ub)=7 > RHS(exact)=2; bounds insufficient
- [BRACKET] Paley(41) reading#0: 448b: alpha_2 <= |V-A| + |E(G[N(S_support)])| + radius [KNOWN CORRUPT per README] :: LHS(ub)=7 > RHS(exact)=2; bounds insufficient
- [BRACKET] Paley(53) reading#0: 448b: alpha_2 <= |V-A| + |E(G[N(S_support)])| + radius [KNOWN CORRUPT per README] :: LHS(ub)=8 > RHS(exact)=2; bounds insufficient
- [BRACKET] Paley(61) reading#0: 448b: alpha_2 <= |V-A| + |E(G[N(S_support)])| + radius [KNOWN CORRUPT per README] :: LHS(ub)=8 > RHS(exact)=2; bounds insufficient
- [BRACKET] Paley(73) reading#0: 448b: alpha_2 <= |V-A| + |E(G[N(S_support)])| + radius [KNOWN CORRUPT per README] :: LHS(ub)=8 > RHS(exact)=2; bounds insufficient
- [BRACKET] Paley(89) reading#0: 448b: alpha_2 <= |V-A| + |E(G[N(S_support)])| + radius [KNOWN CORRUPT per README] :: LHS(ub)=9 > RHS(exact)=2; bounds insufficient
- [BRACKET] Paley(97) reading#0: 448b: alpha_2 <= |V-A| + |E(G[N(S_support)])| + radius [KNOWN CORRUPT per README] :: LHS(ub)=9 > RHS(exact)=2; bounds insufficient
- [BRACKET] T(10) reading#0: 448b: alpha_2 <= |V-A| + |E(G[N(S_support)])| + radius [KNOWN CORRUPT per README] :: LHS(ub)=7 > RHS(exact)=2; bounds insufficient
- [BRACKET] T(11) reading#0: 448b: alpha_2 <= |V-A| + |E(G[N(S_support)])| + radius [KNOWN CORRUPT per README] :: LHS(ub)=8 > RHS(exact)=2; bounds insufficient
- [BRACKET] T(12) reading#0: 448b: alpha_2 <= |V-A| + |E(G[N(S_support)])| + radius [KNOWN CORRUPT per README] :: LHS(ub)=9 > RHS(exact)=2; bounds insufficient
- [BRACKET] T(13) reading#0: 448b: alpha_2 <= |V-A| + |E(G[N(S_support)])| + radius [KNOWN CORRUPT per README] :: LHS(ub)=9 > RHS(exact)=2; bounds insufficient

## batch appended 2026-08-26 07:03:22

| id | verdict | vio | hold | bracket | premise_false | undef | tag |
|---|---|---|---|---|---|---|---|
| 61 | HOLDS_PARTIAL | 0 | 36 | 0 | 0 | 14 |  |
| 63 | VIOLATED_CANDIDATE | 6 | 24 | 0 | 0 | 20 | KILLED_PRIOR_CAMPAIGN |
| 64 | VIOLATED_CANDIDATE | 4 | 32 | 0 | 0 | 14 | KILLED_PRIOR_CAMPAIGN |
| 65 | HOLDS_PARTIAL | 0 | 36 | 0 | 0 | 14 |  |
| 66 | HOLDS_PARTIAL | 0 | 18 | 0 | 0 | 32 |  |
| 72 | BRACKET | 0 | 99 | 1 | 0 | 0 |  |
| 76 | BRACKET | 0 | 49 | 1 | 0 | 0 |  |
| 84 | HOLDS | 0 | 50 | 0 | 0 | 0 |  |
| 85 | BRACKET | 0 | 49 | 1 | 0 | 0 | KILLED_PRIOR_CAMPAIGN |
| 96 | HOLDS | 0 | 50 | 0 | 0 | 0 |  |

### id 63
statement: If G is a simple connected graph, then f(G) ≥ CEIL[(minimum of dist_even(v) + b(G) + 1)/3]

- [VIO] KG(10,2) reading#0: f >= ceil((min dist_even + b + 1)/3)  [KILLED 2026-07-23] :: LHS=10 < RHS=12
- [VIO] Paley(29) reading#0: f >= ceil((min dist_even + b + 1)/3)  [KILLED 2026-07-23] :: LHS=7 < RHS=8
- [VIO] Paley(37) reading#0: f >= ceil((min dist_even + b + 1)/3)  [KILLED 2026-07-23] :: LHS=8 < RHS=10
- [VIO] Paley(41) reading#0: f >= ceil((min dist_even + b + 1)/3)  [KILLED 2026-07-23] :: LHS=8 < RHS=11
- [VIO] comp(C5[K6]) reading#0: f >= ceil((min dist_even + b + 1)/3)  [KILLED 2026-07-23] :: LHS=14 < RHS=15
- [VIO] comp(C5[K7]) reading#0: f >= ceil((min dist_even + b + 1)/3)  [KILLED 2026-07-23] :: LHS=16 < RHS=17

### id 64
statement: If G is a simple connected graph, then f(G) ≥ CEIL[(sqrt[ α(G) * (1 + (n mod Δ(G))] ]

- [VIO] KG(10,2) reading#0: f >= ceil(sqrt(alpha*(1 + n mod Delta)))  [KILLED 2026-07-26] :: LHS=10 < RHS=13
- [VIO] KG(11,2) reading#0: f >= ceil(sqrt(alpha*(1 + n mod Delta)))  [KILLED 2026-07-26] :: LHS=11 < RHS=15
- [VIO] KG(12,2) reading#0: f >= ceil(sqrt(alpha*(1 + n mod Delta)))  [KILLED 2026-07-26] :: LHS=12 < RHS=16
- [VIO] KG(13,2) reading#0: f >= ceil(sqrt(alpha*(1 + n mod Delta)))  [KILLED 2026-07-26] :: LHS=13 < RHS=17

### id 72
statement: If G is a simple connected graph, then tree(G) ≥ CEIL[average of ecc(v) + maximum of λ(v) /3]

- [BRACKET] CMP(2) reading#1: alt grouping: tree >= ceil(ecc_avg + lambda_max/3) :: LHS(lb)=2 < RHS(exact)=3; bounds insufficient

### id 76
statement: If G is a simple connected graph, then tree(G) ≥ freq[T_max(v)]/FLOOR[deg_avg(G)]

- [BRACKET] CMP(2) reading#0: tree >= freq[T_max]/floor(deg_avg) :: LHS(lb)=2 < RHS(exact)=3; bounds insufficient

### id 85
statement: If G is a simple connected graph, then tree(G) ≥ CEIL[sqrt(1 + 2*minimum of dist_even(v))]

- [BRACKET] Paley(101) reading#0: tree >= ceil(sqrt(1 + 2*min dist_even))  [KILLED 2026-07-23] :: LHS(lb)=10 < RHS(exact)=11; bounds insufficient

## batch appended 2026-08-26 07:04:31

| id | verdict | vio | hold | bracket | premise_false | undef | tag |
|---|---|---|---|---|---|---|---|

## batch appended 2026-08-26 07:05:07

| id | verdict | vio | hold | bracket | premise_false | undef | tag |
|---|---|---|---|---|---|---|---|
| agx-survey-C8 | BRACKET | 0 | 196 | 4 | 0 | 0 |  |
| agx-survey-C11 | HOLDS | 0 | 100 | 0 | 0 | 0 |  |
| agx-survey-C15 | BRACKET | 0 | 50 | 18 | 0 | 0 |  |
| agx-survey-C17 | UNPARSEABLE_SOURCE | 0 | 0 | 0 | 0 | 0 |  |
| agx-survey-C29 | UNPARSEABLE_SOURCE | 0 | 0 | 0 | 0 | 0 |  |
| agx-survey-C30 | VIOLATED_CANDIDATE | 1 | 49 | 0 | 0 | 0 |  |
| agx-survey-C31 | UNPARSEABLE_SOURCE | 0 | 0 | 0 | 0 | 0 |  |
| agx-survey-C32 | HOLDS | 0 | 50 | 0 | 0 | 0 |  |
| agx-survey-C33 | BRACKET | 0 | 49 | 1 | 0 | 0 |  |
| agx-survey-C36 | HOLDS | 0 | 150 | 0 | 0 | 0 |  |

### id agx-survey-C8
statement: Let G be a connected graph on n ⩾ 3 vertices with index λ1 , vertex connectivity ν and edge connectivity κ. Then λ1 λ1 λ1 − ν ⩽ n − 3 + t ; λ1 − κ ⩽ n − 3 + t ; ⩽ n − 2 + t ; and ⩽ n − 2 + t, ν ν wher

- [BRACKET] CMP(2) reading#0: C8a: lam1 - nu <= n - 3 + t (t=t(3)) :: values too close to decide exactly
- [BRACKET] CMP(2) reading#1: C8b: lam1 - kappa <= n - 3 + t :: values too close to decide exactly
- [BRACKET] CMP(2) reading#2: C8c: lam1/nu <= n - 2 + t :: values too close to decide exactly
- [BRACKET] CMP(2) reading#3: C8d: lam1/kappa <= n - 2 + t :: values too close to decide exactly

### id agx-survey-C15
statement: Let G be a connected graph on n vertices with clique number ω and second largest eigen- value λ2 . Then • if n is odd, |λ2 | · ω ⩽ m − 2 with equality if and only if G is composed of K n+1 and K n−1 l

- [BRACKET] CP(2) reading#1: C15even: |lambda2|*omega - m <= value at extremal graph (two linked K_{n/2}) :: LHS(exact)=-4 <= RHS(ub)=-1.1458980337503144 but kinds cannot certify hold
- [BRACKET] CP(3) reading#1: C15even: |lambda2|*omega - m <= value at extremal graph (two linked K_{n/2}) :: LHS(exact)=-12 <= RHS(ub)=-0.07179676972448945 but kinds cannot certify hold
- [BRACKET] CP(4) reading#1: C15even: |lambda2|*omega - m <= value at extremal graph (two linked K_{n/2}) :: LHS(exact)=-24 <= RHS(ub)=0.956439237389592 but kinds cannot certify hold
- [BRACKET] CP(5) reading#1: C15even: |lambda2|*omega - m <= value at extremal graph (two linked K_{n/2}) :: LHS(exact)=-40 <= RHS(ub)=1.970562748477139 but kinds cannot certify hold
- [BRACKET] CP(6) reading#1: C15even: |lambda2|*omega - m <= value at extremal graph (two linked K_{n/2}) :: LHS(exact)=-60 <= RHS(ub)=2.978713763747791 but kinds cannot certify hold
- [BRACKET] CP(7) reading#1: C15even: |lambda2|*omega - m <= value at extremal graph (two linked K_{n/2}) :: LHS(exact)=-84 <= RHS(ub)=3.983866769659329 but kinds cannot certify hold
- [BRACKET] CP(8) reading#1: C15even: |lambda2|*omega - m <= value at extremal graph (two linked K_{n/2}) :: LHS(exact)=-112 <= RHS(ub)=4.98733974326457 but kinds cannot certify hold
- [BRACKET] K(3,3) reading#1: C15even: |lambda2|*omega - m <= value at extremal graph (two linked K_{n/2}) :: LHS(exact)=-9 <= RHS(ub)=-0.07179676972448945 but kinds cannot certify hold
- [BRACKET] KG(12,2) reading#1: C15even: |lambda2|*omega - m <= value at extremal graph (two linked K_{n/2}) :: LHS(exact)=-1479 <= RHS(ub)=29.999133448222665 but kinds cannot certify hold
- [BRACKET] KG(13,2) reading#1: C15even: |lambda2|*omega - m <= value at extremal graph (two linked K_{n/2}) :: LHS(exact)=-2139 <= RHS(ub)=35.99937421752702 but kinds cannot certify hold
- [BRACKET] KG(16,2) reading#1: C15even: |lambda2|*omega - m <= value at extremal graph (two linked K_{n/2}) :: LHS(exact)=-5452 <= RHS(ub)=56.999731110495304 but kinds cannot certify hold
- [BRACKET] T(12) reading#1: C15even: |lambda2|*omega - m <= value at extremal graph (two linked K_{n/2}) :: LHS(exact)=-572 <= RHS(ub)=29.999133448222665 but kinds cannot certify hold
- [BRACKET] T(13) reading#1: C15even: |lambda2|*omega - m <= value at extremal graph (two linked K_{n/2}) :: LHS(exact)=-750 <= RHS(ub)=35.99937421752702 but kinds cannot certify hold
- [BRACKET] T(16) reading#1: C15even: |lambda2|*omega - m <= value at extremal graph (two linked K_{n/2}) :: LHS(exact)=-1500 <= RHS(ub)=56.999731110495304 but kinds cannot certify hold
- [BRACKET] comp(C5[K2]) reading#1: C15even: |lambda2|*omega - m <= value at extremal graph (two linked K_{n/2}) :: LHS(exact)=-22 + 2*sqrt(5) <= RHS(ub)=1.970562748477139 but kinds cannot certify hold
- [BRACKET] comp(C5[K4]) reading#1: C15even: |lambda2|*omega - m <= value at extremal graph (two linked K_{n/2}) :: LHS(exact)=-84 + 4*sqrt(5) <= RHS(ub)=6.991596045155774 but kinds cannot certify hold
- [BRACKET] comp(C5[K6]) reading#1: C15even: |lambda2|*omega - m <= value at extremal graph (two linked K_{n/2}) :: LHS(exact)=-186 + 6*sqrt(5) <= RHS(ub)=11.99606293110034 but kinds cannot certify hold
- [BRACKET] comp(C5[K8]) reading#1: C15even: |lambda2|*omega - m <= value at extremal graph (two linked K_{n/2}) :: LHS(exact)=-328 + 8*sqrt(5) <= RHS(ub)=16.99772208385201 but kinds cannot certify hold

### id agx-survey-C30
statement: Let G be a connected graph on n vertices with proximity π and algebraic connectivity a. Then ⎧   ⎨ 3n+1 n−1 1 − cos π if n is odd, 2 n  π · a ⩾ ⎩ 3n−2 π n 1 − cos 2 n if n is even, with equality i

- [VIO] CMP(2) reading#0: C30odd: pi*a >= (3n+1)/pi*(1-cos(pi/n))/2 :: LHS=1 < RHS=15/(2*pi)

### id agx-survey-C33
statement: Let G be a connected graph on n vertices with index λ1 and algebraic connectivity a. Then • a − λ1 ⩾ 3 − n − t, where 0 < t < 1 and t 3 + (2n − 3)t 2 + (n2 − 3n + 1)t − 1 = 0, with equality if and onl

- [BRACKET] CMP(2) reading#0: C33a: a - lam1 >= 3 - n - t :: values too close to decide exactly

## batch appended 2026-08-26 07:05:07

| id | verdict | vio | hold | bracket | premise_false | undef | tag |
|---|---|---|---|---|---|---|---|
| agx-survey-C37 | HOLDS | 0 | 300 | 0 | 0 | 0 |  |
| agx-survey-C39 | HOLDS | 0 | 50 | 0 | 0 | 0 |  |
| agx-survey-C40 | HOLDS | 0 | 50 | 0 | 0 | 0 |  |
| agx-survey-C42 | VIOLATED_CANDIDATE | 8 | 10 | 0 | 0 | 2 |  |
| agx-form1-T45-r5-upper | UNPARSEABLE_SOURCE | 0 | 0 | 0 | 0 | 0 |  |
| agx-form1-T45-r19-upper | UNPARSEABLE_SOURCE | 0 | 0 | 0 | 0 | 0 |  |
| agx-form1-T45-r23-upper | UNPARSEABLE_SOURCE | 0 | 0 | 0 | 0 | 0 |  |
| agx-form1-T45-r29-lower | UNPARSEABLE_SOURCE | 0 | 0 | 0 | 0 | 0 |  |
| agx-form1-T45-r29-upper | UNPARSEABLE_SOURCE | 0 | 0 | 0 | 0 | 0 |  |
| agx-form1-T45-r31-lower | UNPARSEABLE_SOURCE | 0 | 0 | 0 | 0 | 0 |  |

### id agx-survey-C42
statement: Let G be a triangle-free graph on n vertices with m edges, independence number α. If p− (D) denotes the number of negative distance eigenvalues of G then m/α ⩽ p− (D) and m/α ⩽ n − p− (D). As far as w

- [VIO] K(3,3) reading#1: C42ii: m/alpha <= n - p-(D) :: LHS=3 > RHS=2
- [VIO] comp(C5[K2]) reading#1: C42ii: m/alpha <= n - p-(D) :: LHS=5 > RHS=3
- [VIO] comp(C5[K3]) reading#1: C42ii: m/alpha <= n - p-(D) :: LHS=15/2 > RHS=3
- [VIO] comp(C5[K4]) reading#1: C42ii: m/alpha <= n - p-(D) :: LHS=10 > RHS=3
- [VIO] comp(C5[K5]) reading#1: C42ii: m/alpha <= n - p-(D) :: LHS=25/2 > RHS=3
- [VIO] comp(C5[K6]) reading#1: C42ii: m/alpha <= n - p-(D) :: LHS=15 > RHS=3
- [VIO] comp(C5[K7]) reading#1: C42ii: m/alpha <= n - p-(D) :: LHS=35/2 > RHS=3
- [VIO] comp(C5[K8]) reading#1: C42ii: m/alpha <= n - p-(D) :: LHS=20 > RHS=3

## batch appended 2026-08-26 07:05:07

| id | verdict | vio | hold | bracket | premise_false | undef | tag |
|---|---|---|---|---|---|---|---|
| agx-form1-T45-r31-upper | UNPARSEABLE_SOURCE | 0 | 0 | 0 | 0 | 0 |  |
| agx-form1-T45-r35-lower | UNPARSEABLE_SOURCE | 0 | 0 | 0 | 0 | 0 |  |
| agx-form1-T45-r35-upper | UNPARSEABLE_SOURCE | 0 | 0 | 0 | 0 | 0 |  |
| agx-form1-T45-r40-lower | UNPARSEABLE_SOURCE | 0 | 0 | 0 | 0 | 0 |  |
| agx-form1-T45-r42-lower | UNPARSEABLE_SOURCE | 0 | 0 | 0 | 0 | 0 |  |
| agx-form1-T45-r43-upper | UNPARSEABLE_SOURCE | 0 | 0 | 0 | 0 | 0 |  |
| agx-form1-T45-r45-upper | UNPARSEABLE_SOURCE | 0 | 0 | 0 | 0 | 0 |  |
| agx-form1-T45-r47-upper | UNPARSEABLE_SOURCE | 0 | 0 | 0 | 0 | 0 |  |
| agx-form1-T45-r49-upper | UNPARSEABLE_SOURCE | 0 | 0 | 0 | 0 | 0 |  |
| agx-form1-T45-r51-upper | UNPARSEABLE_SOURCE | 0 | 0 | 0 | 0 | 0 |  |

## batch appended 2026-08-26 07:05:07

| id | verdict | vio | hold | bracket | premise_false | undef | tag |
|---|---|---|---|---|---|---|---|
| agx-form1-T45-r53-upper | UNPARSEABLE_SOURCE | 0 | 0 | 0 | 0 | 0 |  |
| agx-form1-T45-r55-lower | UNPARSEABLE_SOURCE | 0 | 0 | 0 | 0 | 0 |  |
| agx-form1-T45-r59-lower | UNPARSEABLE_SOURCE | 0 | 0 | 0 | 0 | 0 |  |
| agx-form1-T45-r61-upper | UNPARSEABLE_SOURCE | 0 | 0 | 0 | 0 | 0 |  |
| agx-form1-T45-r63-lower | UNPARSEABLE_SOURCE | 0 | 0 | 0 | 0 | 0 |  |
| agx-form1-T45-r65-upper | UNPARSEABLE_SOURCE | 0 | 0 | 0 | 0 | 0 |  |
| agx-form1-T45-r67-lower | UNPARSEABLE_SOURCE | 0 | 0 | 0 | 0 | 0 |  |
| agx-form1-T45-r69-upper | UNPARSEABLE_SOURCE | 0 | 0 | 0 | 0 | 0 |  |
| agx-form1-T45-r70-lower | UNPARSEABLE_SOURCE | 0 | 0 | 0 | 0 | 0 |  |
| agx-form1-T45-r71-upper | UNPARSEABLE_SOURCE | 0 | 0 | 0 | 0 | 0 |  |

## batch appended 2026-08-26 07:05:07

| id | verdict | vio | hold | bracket | premise_false | undef | tag |
|---|---|---|---|---|---|---|---|
| agx-form1-T45-r72-lower | UNPARSEABLE_SOURCE | 0 | 0 | 0 | 0 | 0 |  |
| agx-form1-T45-r75-lower | UNPARSEABLE_SOURCE | 0 | 0 | 0 | 0 | 0 |  |
| agx-form1-T45-r77-lower | UNPARSEABLE_SOURCE | 0 | 0 | 0 | 0 | 0 |  |
| agx-form1-T45-r79-lower | UNPARSEABLE_SOURCE | 0 | 0 | 0 | 0 | 0 |  |
| agx-form1-T45-r81-lower | UNPARSEABLE_SOURCE | 0 | 0 | 0 | 0 | 0 |  |
| agx-form1-T45-r83-lower | UNPARSEABLE_SOURCE | 0 | 0 | 0 | 0 | 0 |  |
| agx-form1-T45-r86-lower | UNPARSEABLE_SOURCE | 0 | 0 | 0 | 0 | 0 |  |
| agx-form1-T45-r88-lower | UNPARSEABLE_SOURCE | 0 | 0 | 0 | 0 | 0 |  |
| agx-form1-T45-r90-lower | UNPARSEABLE_SOURCE | 0 | 0 | 0 | 0 | 0 |  |
| agx-form1-T45-r92-lower | UNPARSEABLE_SOURCE | 0 | 0 | 0 | 0 | 0 |  |

## batch appended 2026-08-26 07:05:07

| id | verdict | vio | hold | bracket | premise_false | undef | tag |
|---|---|---|---|---|---|---|---|
| agx-form1-T45-r98-lower | UNPARSEABLE_SOURCE | 0 | 0 | 0 | 0 | 0 |  |
| agx-form1-T45-r99-lower | UNPARSEABLE_SOURCE | 0 | 0 | 0 | 0 | 0 |  |
| agx-form1-T45-r100-lower | UNPARSEABLE_SOURCE | 0 | 0 | 0 | 0 | 0 |  |
| agx-form1-T45-r104-lower | UNPARSEABLE_SOURCE | 0 | 0 | 0 | 0 | 0 |  |
| agx-form1-T45-r108-lower | UNPARSEABLE_SOURCE | 0 | 0 | 0 | 0 | 0 |  |
| agx-form1-T45-r110-lower | UNPARSEABLE_SOURCE | 0 | 0 | 0 | 0 | 0 |  |
| agx-form1-T45-r112-lower | UNPARSEABLE_SOURCE | 0 | 0 | 0 | 0 | 0 |  |
| agx-form1-T45-r115-lower | UNPARSEABLE_SOURCE | 0 | 0 | 0 | 0 | 0 |  |
| agx-form1-T45-r115-upper | UNPARSEABLE_SOURCE | 0 | 0 | 0 | 0 | 0 |  |
| agx-form1-T45-r116-lower | UNPARSEABLE_SOURCE | 0 | 0 | 0 | 0 | 0 |  |

## batch appended 2026-08-26 07:05:07

| id | verdict | vio | hold | bracket | premise_false | undef | tag |
|---|---|---|---|---|---|---|---|
| agx-form1-T45-r117-lower | UNPARSEABLE_SOURCE | 0 | 0 | 0 | 0 | 0 |  |
| agx-form1-T45-r119-lower | UNPARSEABLE_SOURCE | 0 | 0 | 0 | 0 | 0 |  |
| agx-form1-T45-r123-lower | UNPARSEABLE_SOURCE | 0 | 0 | 0 | 0 | 0 |  |
| agx-form1-T45-r127-lower | UNPARSEABLE_SOURCE | 0 | 0 | 0 | 0 | 0 |  |
| agx-form1-T45-r130-lower | UNPARSEABLE_SOURCE | 0 | 0 | 0 | 0 | 0 |  |
| agx-form1-T45-r131-lower | UNPARSEABLE_SOURCE | 0 | 0 | 0 | 0 | 0 |  |
| agx-form1-T45-r132-lower | UNPARSEABLE_SOURCE | 0 | 0 | 0 | 0 | 0 |  |
| agx-form1-T45-r139-lower | UNPARSEABLE_SOURCE | 0 | 0 | 0 | 0 | 0 |  |
| agx-form1-T45-r141-upper | UNPARSEABLE_SOURCE | 0 | 0 | 0 | 0 | 0 |  |
| agx-form1-T45-r143-lower | UNPARSEABLE_SOURCE | 0 | 0 | 0 | 0 | 0 |  |

## correction pass appended 2026-08-26 (post-sweep fixes, same day)

During candidate triage, builder defects were found and fixed; the affected
entries above were re-evaluated and their corrected verdicts are
authoritative over any earlier batch row:

| id | earlier row | corrected verdict | reason |
|---|---|---|---|
| 252 | VIOLATED_CANDIDATE | BRACKET | C4-free premise was not gated; after gating, premise false on 49/50 arsenal graphs |
| 253 | VIOLATED_CANDIDATE | BRACKET | girth>=5 premise was not gated; premise false on 49/50 |
| 269 | VIOLATED_CANDIDATE | BRACKET | C4-free premise not gated; premise false on 49/50 |
| 404/405/406/407 | VIOLATED_CANDIDATE / partial | PREMISE_FALSE_EVERYWHERE | tree-hypothesis premise added |
| 418b | UNSUPPORTED | BRACKET | p_cov raised at build time on T(14..16); made lazy |
| 418c | UNSUPPORTED | BRACKET | A_core raised at build time; made lazy |

Gate dispositions for all VIOLATED_CANDIDATE flags (DB-SANITY corpus =
1016 graphs: connected atlas n<=7, C5..C9, P7, Petersen, K3,3, K7,
K1,k stars, bicliques, complete multipartite, C5[K2], C5[K3]):

- 63, 64: violations real but conjectures already killed by this campaign;
  new arsenal witnesses recorded (KG(10..13,2), Paley(29/37/41),
  comp(C5[K6]/[K7])). Not novel.
- 111 readings A/C/D: GATE-FAIL - violate 100-200 sanity graphs each
  (C5..C9, stars, bicliques...). Mis-transcription of the N(S) convention.
  Faithful closed-neighborhood reading B passes gate and HOLDS everywhere.
- 235 reading "ecc(B)=diam": GATE-FAIL - 76 sanity violations incl P7/stars.
- 255: GATE-FAIL - 273 sanity violations incl C5..C9 and Petersen.
- 256: GATE-FAIL - 117+ sanity violations incl Petersen/K7.
- AGX C30 reading#0: GATE-FAIL (violates stars/paths; true statement is
  tight on P_n) -> reconstruction rejected.
- AGX C42ii: GATE-FAIL (violates C5, K3,3, P7 under literal reading).
  Flag: corpora/autographix.json C42 entry is likely miscopied; exact check
  D(K3,3) spec = {7^1, 1^1, (-2)^4} gives p-=4, n-p-=2 < m/alpha=3.

NET RESULT: no new claimable kill from this sweep. All 220 open WOWII
entries and all evaluable open AGX entries are now screened against the
extended arsenal with zero unexplained violations. New corroborating
witness families for prior kills #63/#64 are logged above.
