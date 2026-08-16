"""Steps 1-2 written out: what the wall looks like, and what pins it.

`WALL[tid]` -- the structural reading of the equality members recorded with the
target (their full invariant profiles are recomputed by `wall_read.py`).
`OBSTRUCTION[tid]` -- the invariant that must move for the inequality to fail,
and what currently holds it in place.
`CLOSING[tid]` -- for HELD targets, the argument that closes the lane (a proof
where one exists, otherwise the structural reason no construction moves the
obstruction).
"""

WALL = {
 "FP-001": "All 16 equality members are complete bipartite graphs K_{a,b} (a<=b), "
           "including the stars K_{1,n-1}: bipartite, triangle-free, omega=chi=2, "
           "gamma_t=2, disp_min=disp_max=1 (biregular). On K_{a,b}: alpha=b, "
           "Tdist_max=a+2b-2, dist_even_min=a, so RHS = (b-1)+1 = b = alpha exactly.",
 "FP-002": "All 249 equality members sit at n=8, the database edge, and are "
           "non-bipartite, non-regular, non-tree. dist_even_max is 6 or 7, i.e. "
           "n-2 or n-1: the tight members carry a near-universal vertex u plus a "
           "pendant v, so dist_even(v) = 1 + |V - {u,v}| = n-1. Witness GCc`N{ has "
           "degrees [1,3,3,3,3,3,3,7] = pendant + (K_1 joined to 2K_3).",
 "FP-003": "6696 equality members, cutv pinned at 0 across the recorded 300, with "
           "alpha = lambda_max on every one: the wall is the whole 2-connected "
           "diameter-2 bulk of D where a maximum independent set already lives "
           "inside a single neighbourhood.",
 "FP-004": "Exactly two equality members in all of D: K_2 and K_3. Everything is "
           "pinned (dd=1, CW=1, res=1, A=1, diam=rad=1, dist_avg=1, disp=1, "
           "alpha=1, chi_reg=1). The wall is the complete graphs, truncated at n=3.",
 "FP-005": "3922 equality members, 300 recorded at n=8 with A=4=floor(n/2), "
           "gamma_t=2 and mu=4 pinned. The wall is exactly the graphs that attain "
           "A = floor(n/2) and have a dominating edge.",
 "FP-006": "5731 equality members; chi_regular pinned at 0 across the recorded 300 "
           "and chi = omega on every one. The wall is the whole perfect-graph bulk "
           "of D.",
 "FP-007": "6 equality members: five at n=8 and one at n=7, all thin trees or "
           "near-trees with 4-6 cut vertices, delta=1, disp_max=2, alpha=4, "
           "gamma=3, gamma_t=4 pinned. The extreme member G_CKJ? is the path P_8 "
           "itself (diam 7, gamma_2 5).",
 "FP-008": "7 equality members, delta=sigma_2=1, kappa=1, disp_min=1, chi_C4free=1 "
           "pinned; five of the seven are trees. The n=8, n=7 and n=5 members are "
           "the stars K_{1,7}, K_{1,6}, K_{1,4} (plus near-stars). On K_{1,s}: "
           "A = s, diam = 2, lambda_1 = sqrt(s).",
 "FP-009": "704 equality members; the recorded 300 all sit at n=8 with lambda_avg "
           "< 2, so floor(lambda_avg/2) = 0 and the bound degenerates to "
           "gamma <= res. Every recorded member has gamma = res exactly and 1-4 "
           "cut vertices.",
 "FP-010": "216 equality members spread over every order 3..8. The C4-free ones "
           "have gamma_2 = gamma + 1 exactly; the C4-containing ones have "
           "gamma_2 = gamma. The wall is therefore two separate strata glued by "
           "the characteristic function.",
 "FP-011": "1509 equality members; 217 of the recorded 300 have gamma = 1 and "
           "Tdist_min = 7 = n-1 <= m, i.e. a universal vertex. The wall is the "
           "dominating-vertex stratum, where Tdist_min/m <= 1 = gamma.",
 "FP-012": "17 equality members: the complete graphs K_2..K_8 (gamma_2=2, "
           "dist_even_max=1, regular), the 7-cycle, and ten 8-vertex trees / "
           "near-trees with 4 or more pendant vertices, gamma_2 = 6 and "
           "dist_even_max = 4 = n/2. disp_min is pinned at 1.",
 "FP-013": "39 equality members with diam=2, rad=1, dist_even_min=1, gamma=1, "
           "gamma_t=2, gamma_i=1 pinned: a universal vertex is present on every "
           "one. 24 of them have Delta=7=n-1 and Sigma_2=6, giving RHS=2=gamma_2; "
           "the star K_{1,7} is the other extreme (Sigma_2=1, gamma_2=7=RHS).",
 "FP-014": "85 equality members, 81 at n=8, all 2-connected (cutv=0, f_1=0) and "
           "non-bipartite with gamma_2 = 2 or 3 and dist_even_min = 1, 2 or 4. "
           "gamma_2=2 forces diameter 2 and a dominating pair; dist_even_min is "
           "held down to 2 by the same density.",
 "FP-015": "3 equality members: K_2, K_3, and G_ACDo at n=8 -- the balanced double "
           "star S(3,3) (two adjacent centres with three leaves each), with "
           "diam=3, mu=2, gamma_i=4.",
 "FP-016": "290 equality members with gamma_t pinned at 2. The recorded 290 have "
           "alpha = gamma_i = 3 and gamma = 2 almost everywhere: the wall is "
           "'alpha odd and gamma_i = floor(alpha/2) + gamma'.",
 "FP-017": "400 equality members; the recorded 300 all have kappa=1, delta=1, "
           "lambda_min=1 and cutv=2 (290 of 300) with gamma_t=2. The wall is the "
           "one-bridge stratum: two cut vertices and a dominating edge.",
 "FP-018": "4972 equality members with disp_min pinned at 1 across all 300 "
           "recorded, and gamma = gamma_t on every one.",
 "FP-019": "175 equality members with kappa = floor(lambda_1) on every one and "
           "t in {0,1}; delta = kappa on 144 of 175. The wall is 'kappa = delta = "
           "floor(lambda_1)', i.e. the (near-)regular sparse stratum.",
 "FP-020": "1284 equality members; the recorded 300 all have kappa=1, delta=1, "
           "lambda_min=1, non-bipartite, non-regular. disp_avg sits in [2, 21/8] "
           "and ecc_avg in [15/8, 21/8]: the two averages are within 1 of each "
           "other on the entire wall, so the floor term is 0.",
 "FP-021": "335 equality members; disp_max is pinned at 2 on 295 of the recorded "
           "300 and kappa at 1 on 299 of 300. lambda_avg runs 7/4 to 3 -- always "
           "less than disp_max + 2, so the floor term is 0 and the bound reads "
           "kappa >= 1.",
 "FP-022": "380 equality members, mu pinned at 4 and n at 8, non-bipartite and "
           "C4-containing throughout. lambda_max = 2 on 285 of 300 with dd = 4 and "
           "f_1 = 0, so the bound reads 2 >= floor(4/2).",
 "FP-023": "30 equality members: 27 at n=8, all with kappa=1 and 3-6 cut vertices, "
           "gamma_2 in {5,6}, chi in {2,3}, lambda_max in {2,3}. G_CKJ? (the path "
           "P_8) and GA?KJG (a tree) are the extreme members; disp_min is pinned "
           "at 1 on 29 of 30.",
 "FP-024": "10407 equality members -- the largest wall in the population -- mu "
           "pinned at 4 = ceil(n/2) with n=8 and chi_tree=0. The wall is every "
           "graph with a (near-)perfect matching.",
 "FP-025": "58 equality members with nothing pinned. They split into two strata: "
           "the complete bipartite graphs K_{a,a} and K_{a,b} (delta = lam_min = "
           "mu) and the complete/near-complete graphs (delta = n-1, lam_min = 1, "
           "mu = floor(n/2)).",
 "FP-026": "747 equality members; the recorded 300 all have rad = 1 (a universal "
           "vertex) with disp_max = floor(lambda_1) exactly, values 2, 3 or 4. "
           "The wall is 'universal vertex, and the number of distinct neighbour "
           "degrees equals floor(lambda_1)'.",
 "FP-027": "215 equality members, all bipartite (chi_bip=1, t=0, omega=chi=2). "
           "The wall is the bipartite stratum where ecc_avg sits in "
           "[2 rad - 2, 2 rad).",
 "FP-028": "7 equality members: exactly the complete graphs K_2..K_8. Everything "
           "is pinned: CW=1, alpha=1, res=1, dd=1, diam=rad=1, chi_reg=1.",
 "FP-029": "32 equality members, all at n=8 with m=8, Delta=3, delta=1, deg_avg=2, "
           "res=3, A=5, kappa=1, disp_min=1 all pinned. The wall is a single "
           "degree sequence: unicyclic graphs with degree sequence "
           "(1,1,2,2,2,2,3,3) or (1,1,1,2,2,3,3,3).",
 "FP-030": "2216 equality members; the recorded 300 have n=8, mu=4, gamma_t=2, "
           "non-bipartite, non-regular, and dd = 4 or 5 with res = 2, so "
           "floor(dd/gamma_t) = 2 = res exactly.",
}

OBSTRUCTION = {
 "FP-001": "The degree spread Delta-delta. Crossing needs "
           "alpha >= (n+2+Delta-delta)/2 (from Tdist_max >= 2n-2-delta and "
           "dist_even_min <= n-Delta), while the independent-set edge count gives "
           "alpha <= n*Delta/(Delta+delta). The two are compatible only when "
           "n(Delta-delta) > (2+Delta-delta)(Delta+delta), which forces a "
           "biregular bipartite graph of diameter 2 -- and a bipartite graph of "
           "diameter 2 is complete bipartite, i.e. back on the wall. Diameter >= 3 "
           "instead inflates Tdist_max quadratically.",
 "FP-002": "alpha(H) + chi(H) for the core H = G - u - v. With a universal vertex "
           "u and a pendant v on u, alpha = 1+alpha(H), chi = 1+chi(H), "
           "dist_even_max = |H|+1, so the residual is "
           "R = alpha(H) + chi(H) - |H| + 1. The wall pins "
           "alpha(H) + chi(H) = |H| - 1, which is the true minimum of alpha+chi "
           "for |H| <= 7. The obstruction is exactly that minimum, and it drops "
           "to |H| - 2 for the first time at |H| = 8 (C_5 u K_3, or 3K_3 at "
           "|H| = 9) -- one step past the database edge.",
 "FP-003": "None isolable: lambda_max = max_v alpha(G[N(v)]) is an independent set "
           "of G, so lambda_max <= alpha unconditionally, and cutv >= 0. No "
           "invariant can be moved.",
 "FP-004": "disp_min. Crossing needs floor(disp_min/2) + dist_avg > A >= "
           "floor(n/2). But disp_min <= min(delta, dd) and dd <= Delta-delta+1, so "
           "floor(disp_min/2) <= floor(n/4); raising disp_min raises delta, which "
           "collapses dist_avg (bounded by (n+1)/3 in general and by ~3n/(delta+1) "
           "under a min-degree constraint). The two halves of the right-hand side "
           "are anti-correlated through delta.",
 "FP-005": "None isolable: A >= floor(n/2) (the floor(n/2) smallest degrees sum to "
           "at most m) and gamma_t >= 2 for every graph with no isolated vertex, "
           "so floor(n/gamma_t) <= floor(n/2) <= A.",
 "FP-006": "None isolable: chi >= omega, and ceil((omega - c)/2) + 1 <= omega for "
           "omega >= 2, c in {0,1}. omega = 1 is impossible for a connected graph "
           "with n >= 2.",
 "FP-007": "gamma_2 against diam on a path. For P_n, V - S must be an independent "
           "set avoiding both endpoints, so gamma_2(P_n) = floor(n/2) + 1 exactly, "
           "while diam = n - 1 and disp_max = 2. The residual is "
           "R = 2 + floor(n/2) + 1 - (n-1) = floor(n/2) - n + 4, which is 0 at "
           "n = 7, 8 and strictly negative from n = 9. The obstruction is the "
           "linear-vs-half-linear race, and the wall sits at the last n where it "
           "is still a tie -- exactly the database edge.",
 "FP-008": "ceil(lambda_1) as a step function. On the star K_{1,s} the residual is "
           "R = 2 - floor(s / ceil(sqrt(s))). ceil(sqrt(s)) is pinned at 3 for "
           "s = 5..9 while A = s keeps climbing, so the floor term steps from 2 to "
           "3 at the first perfect square with root >= 3, s = 9. D stops at "
           "s = 7.",
 "FP-009": "res against gamma with lambda_avg held below 2. Hanging one pendant on "
           "every vertex forces gamma = n/2 (each pendant needs its own support) "
           "while the residue res of the corona grows only like the residue of a "
           "sparser sequence, and lambda_avg = 1 + lambda_avg(H)/2 stays under 4 "
           "so the floor term stays at 1.",
 "FP-010": "None isolable. If S is a minimum dominating set that also 2-dominates, "
           "then S has no external private neighbour, hence S is independent; pick "
           "any u outside S and two of its neighbours s, s' in S. In a C4-free "
           "graph u is the only vertex whose S-neighbourhood is exactly {s,s'}, so "
           "(S - {s,s'}) + {u} still dominates, contradicting minimality. Hence "
           "gamma_2 >= gamma + 1 whenever chi_C4free = 1.",
 "FP-011": "Tdist_min per edge. Making Tdist_min large forces a path-like graph, "
           "where m = n-1 and Tdist_min ~ n^2/4 gives a ratio ~ n/4, while gamma "
           "of the same graph is ~ n/3 > n/4. Making gamma small forces a "
           "dominating vertex, which collapses Tdist_min to n-1 <= m. The two "
           "requirements move the same structural knob in opposite directions.",
 "FP-012": "gamma(core) with dist_even_max pinned. Hanging one pendant on every "
           "vertex of a diameter-2 core H gives gamma_2 = |H| + gamma(H) (every "
           "pendant is forced in, and the H-part must dominate H), while "
           "dist_even_max stays exactly |H| = n/2 because the core has diameter 2. "
           "The residual is R = 2 - gamma(H): the wall is gamma(H) <= 2 and the "
           "crossing is any diameter-2 core with gamma >= 3. Inside D the corona "
           "of such a core needs n >= 20, and even C_7 (gamma = 3, diameter 3) "
           "needs n = 14.",
 "FP-013": "gamma_2 tracks Delta/Sigma_2 with an unavoidable +1. Whenever n = "
           "Delta+1 the hub is universal and gamma_2 = min(1+gamma(H), gamma_2(H)) "
           "with H = G - hub of maximum degree Sigma_2 - 1, so "
           "gamma_2 >= 1 + ceil(Delta/Sigma_2). Every petal construction pays "
           "exactly one extra vertex for the hub, and the residual is stuck at 1.",
 "FP-014": "dist_even_min. On the wall dist_even_min <= 4 because diameter 2 forces "
           "dist_even(v) = n - deg(v) and the degrees are large. The Cartesian "
           "product with K_2 keeps gamma_2 at 2*gamma_2(G) but sends "
           "dist_even_min to n (in G x K_2 every vertex has its whole layer at "
           "even distance), so the floor term outruns gamma_2.",
 "FP-015": "mu. The tight double star has mu = 2 because every edge meets one of "
           "the two centres, so the vertex cover -- hence the matching -- cannot "
           "grow, while gamma_i = 1 + min(a,b) grows with the leaf sets. diam is "
           "pinned at 3. The residual is R = 4 - (1 + a) for S(a,a): zero at a = 3 "
           "(n = 8, the database edge) and negative from a = 4.",
 "FP-016": "alpha against gamma. Substituting an independent set of order m for "
           "every vertex multiplies alpha and gamma_i by m while leaving gamma at "
           "2 (a dominating pair survives the blow-up), so the residual "
           "floor(alpha/2) + gamma - gamma_i = floor(3m/2) + 2 - 3m goes negative "
           "as soon as m >= 2.",
 "FP-017": "cutv against gamma_t. Every totally dominating set of size k induces a "
           "subgraph with no isolated vertex, hence spans at most floor(k/2) "
           "components, and every cut vertex must lie in or between those "
           "components. Each new cut vertex costs at least half a new dominator, "
           "which is exactly the floor((cutv+chi_tree)/2) term. Lengthening a "
           "caterpillar spine or chaining blocks raises cutv and gamma_t together, "
           "one for one.",
 "FP-018": "None isolable: disp_min >= 1 on every graph with no isolated vertex, so "
           "floor(gamma/disp_min) <= gamma <= gamma_t.",
 "FP-019": "None isolable: kappa <= delta <= 2m/n <= lambda_1, and kappa is an "
           "integer, so kappa <= floor(lambda_1); t >= 0.",
 "FP-020": "disp_avg. With kappa = 1 the graph has a cut vertex; if it also has "
           "diameter 2 that cut vertex is universal, which pins "
           "ecc_avg = 2 - 1/n. The residual then reads "
           "R = 1 - floor((disp_avg - 2 + 1/n)/2), so crossing needs "
           "disp_avg >= 4. disp_avg <= dd, and the wall's members only reach "
           "dd = 5 with most vertices seeing 2 distinct neighbour degrees. The "
           "construction that moves it is a complete multipartite core with all "
           "part sizes distinct, which gives every core vertex k-1 distinct "
           "neighbour degrees at once.",
 "FP-021": "lambda_avg against disp_max. On the wall lambda_avg < disp_max + 2. "
           "Triangle-free graphs have lambda(v) = deg(v), so lambda_avg = deg_avg; "
           "amalgamating dense complete bipartite lobes at a single vertex raises "
           "deg_avg without raising disp_max above 2 and drops kappa to 1.",
 "FP-022": "dd (number of distinct degrees) against lambda_max. The wall has "
           "dd = 4, f_1 = 0, lambda_max = 2, i.e. locally almost-complete "
           "neighbourhoods. The line graph keeps neighbourhoods locally "
           "two-clique (lambda_max = 2 on a line graph of a graph with no "
           "induced claw at the relevant vertex) while spreading the degree "
           "sequence, so dd rises to 6 and the floor term overtakes.",
 "FP-023": "gamma_2 against lambda_max with chi pinned. For a triangle-free graph "
           "lambda_max = Delta; on a path Delta = 2 and chi = 2 while "
           "gamma_2(P_n) = floor(n/2)+1, so R = 2 - (floor((floor(n/2)-1)/2)+1) "
           "is zero at n <= 9 and negative from n = 10. Hanging pendants does the "
           "same thing faster: the corona of a tight member has gamma_2 = "
           "|H| + gamma(H) with lambda_max still 3.",
 "FP-024": "None isolable: mu <= floor(n/2) <= ceil((n-1)/2) for a tree and "
           "<= ceil(n/2) otherwise.",
 "FP-025": "None isolable: taking a vertex u of minimum degree, "
           "lam_min <= lambda(u) <= deg(u) = delta, so the right-hand side is at "
           "most delta. If delta <= floor(n/2) then mu >= min(delta, floor(n/2)) "
           "= delta. If delta > floor(n/2) then mu = floor(n/2) and, writing "
           "delta = n-1-k with k the maximum degree of the complement, "
           "lam_min <= omega(complement) <= k+1, so delta + lam_min <= n.",
 "FP-026": "disp_max against floor(lambda_1). With rad = 1 there is a universal "
           "vertex, which forces lambda_1 >= sqrt(n-1) while disp_max <= dd grows "
           "only like sqrt(2n) for a sparse core -- the wall is closed at rad = 1. "
           "Giving up the universal vertex (rad = 2) and using a tree whose "
           "branches are stars of distinct sizes makes disp_max = d exactly while "
           "lambda_1 grows like sqrt(d), so floor(disp_max/floor(lambda_1)) "
           "reaches 3 while rad stays 2.",
 "FP-027": "None isolable: ecc(v) <= 2 rad for every v, and the centre attains "
           "ecc = rad < 2 rad, so ecc_avg < 2 rad strictly and "
           "floor(ecc_avg/2) <= rad - 1. The bipartite correction term of +1 is "
           "exactly absorbed by that strict inequality.",
 "FP-028": "None isolable: res <= alpha (Favaron-Maheo-Sacle) and "
           "CW = sum_v 1/(1+deg v) >= n/(1+Delta) >= 1.",
 "FP-029": "A - deg_avg against res. The wall is one degree sequence with "
           "deg_avg = 2 and A - deg_avg = 3 = res. A clique blow-up multiplies "
           "A by roughly m while res stays at 3 (the Havel-Hakimi residue of a "
           "blown-up sequence does not scale), and deg_avg only grows linearly in "
           "m, so A - deg_avg outruns res.",
 "FP-030": "dd. The wall has dd = 4 or 5 with gamma_t = 2 and res = 2, so "
           "floor(dd/2) = 2 = res exactly. Joining a single dominating vertex "
           "raises every degree by one and adds one new degree value at the top, "
           "so dd goes to 6 while gamma_t stays 2 (the new vertex plus any "
           "neighbour) and the residue is unchanged.",
}

CLOSING = {
 "FP-001": "HELD. Every transformation of the complete bipartite wall that is "
           "available (clique and independent blow-up, subdivision, corona, join, "
           "prism, line graph, complement, widening or adding parts) has a "
           "non-negative G3-lite sign; the independent blow-up is exactly zero "
           "because K_{a,b}[I_m] = K_{am,bm} is still on the wall. The counting "
           "argument above closes the diameter-2 regime and the Tdist_max growth "
           "closes the rest.",
 "FP-003": "HELD -- theorem. lambda_max <= alpha, cutv >= 0.",
 "FP-004": "HELD. Two designed families (complete graphs; complete multipartite "
           "with distinct part sizes) both have positive or zero sign; the "
           "residual grows monotonically because raising disp_min raises delta, "
           "which caps dist_avg.",
 "FP-005": "HELD -- theorem. A >= floor(n/2) and gamma_t >= 2.",
 "FP-006": "HELD -- theorem. chi >= omega.",
 "FP-010": "HELD -- theorem (private-neighbour + C4-free argument above).",
 "FP-011": "HELD. Path and spider families both have positive sign; the residual "
           "grows with n.",
 "FP-013": "HELD. Flower and hub-plus-matching families both sit at residual "
           "exactly 1 for every parameter, which is the +1 the hub costs.",
 "FP-017": "HELD. Caterpillar and chain-of-blocks families both grow the residual; "
           "cut vertices and total dominators grow together.",
 "FP-018": "HELD -- theorem. disp_min >= 1 and gamma <= gamma_t.",
 "FP-019": "HELD -- theorem. kappa <= delta <= floor(lambda_1).",
 "FP-024": "HELD -- theorem. mu <= floor(n/2).",
 "FP-025": "HELD -- theorem (minimum-degree vertex bounds lam_min by delta).",
 "FP-027": "HELD -- theorem. ecc_avg < 2 rad.",
 "FP-028": "HELD -- theorem. res <= alpha and CW >= 1.",
}
