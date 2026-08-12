# WOWII Invariant Glossary

Precise definitions for every invariant used by the WOWII conjectures, extracted from E. DeLaViña's own definitions database (`wowIIdefs.js`, recovered from the Wayback Machine, snapshot 2024-07-26 — the exact definitions the Graffiti.pc annotations link to via `printDefinitions`), cross-checked against the Lean formalizations in `formal-conjectures/FormalConjectures/WrittenOnTheWallII`. Definition text is DeLaViña's, verbatim (HTML cleaned); bracketed notes and compute hints are ours.

## Conventions used on the page

- **Greek letters** came from the Windows *Symbol* font in the original HTML; we have restored them: `μ` matching, `α` independence, `γ` domination variants, `λ` local independence, `δ`/`Δ` min/max degree, `σ`/`Σ` 2nd smallest / 2nd largest degree, `ω` clique, `κ` connectivity, `χ` chromatic/characteristic.
- **Named vertex sets** (recur constantly): `M` = vertices of maximum degree; `A` = vertices of minimum degree; `B` = periphery (maximum eccentricity); `C` = center (minimum eccentricity); `P` = pendants (degree-1 vertices); `H` = union of all maximum critical independent sets (in the 4xx lists).
- **`maximum of X(v)` / `minimum of X(v)` / `average of X(v)`**: max/min/mean of the vertex-local invariant X over all vertices of G. E.g. `average of λ(v)` = λ̄ (avg local independence).
- **`dist(S,T)`** distance between sets = min pairwise distance unless stated; `dist_avg(S,V)` = average over v in V of dist(v,S) (see defs 25/37/38/95). `dist_max(M)`/`dist(M)` = max distance between two max-degree vertices.
- **`CEIL[x]` / `FLOOR[x]`**: ceiling/floor — the discretization cliffs where several conjectures (58, 91, 109…) have already died.
- **Characteristic functions** `χ_P(G)` are 0/1 indicators of property P used as correction terms (C4-free, K3-free, claw-free, bipartite, regular, residue=2, tree).

## Invariants used in currently-open conjectures

Ordered by number of open conjectures using each (count in brackets).

### `γ_τ` — total domination number  [73 open]

> A subset of the vertices, D_t, of the graph is called a total dominating set of the graph if for every vertex v of the graph is adjacent to a vertex of D_t. The total domination number of a graph is the size of a smallest total dominating set of the graph.

*Compute:* NP-hard; small-n exact / ILP (total domination).

### `N(S)` — neighborhood of a subset of the vertices, S  [55 open]

> is the set of vertices that are adjacent to at least one vertex of S.

*Compute:* Trivial per set.

### `α(G)` — independence number of a graph  [53 open]

> The maximum number of vertices such that no two are adjacent.

*Compute:* NP-hard in general; exact fine to n~60 via networkx complement+clique or ILP.

### `<S> or G[S]` — Subgraph induced by S  [44 open]

> is a graph with vertex set S and edged set E(S) = {(u,v): u and v in S and u is adjacent to v in G}

*Compute:* Constructor.

### `p(G)` — path covering number  [37 open]

> The minimum number of vertex disjoint paths needed to cover the vertices of the graph.

*Compute:* Poly for trees (leaf-matching formula); NP-hard general (min path cover); small-n exact ok.

### `γ_2` — 2-domination number  [31 open]

> A subset of the vertices, D_2, of the graph is called a 2-dominating set of the graph if for every vertex v of the graph, either in v is D_2 or v is adjacent to 2 vertices of D_2. The 2-domination number of a graph is the size of a smallest 2-dominating set of the graph.

*Compute:* NP-hard; small-n exact / ILP (2-domination).

### `L_s(G)` — maximum number of leaves of a spanning tree  [29 open]

> A spanning tree of a graph is a subgraph that contains all the vertices and is a tree. Note that a graph may have many spanning trees. The maximum number of leaves of a spanning tree is maximum number of vertices of degree one(in the spanning tree) over all spanning trees of the graph.

*Compute:* NP-hard (max-leaf spanning tree); exact via ILP/branch-and-bound; fine for n<=20 brute force over spanning trees is infeasible - use ILP: maximize leaves s.t. spanning tree constraints. 2-approx known (greedy).

### `γ_i(G) or i(G)` — independent domination number  [29 open]

> A subset of the vertices, D, of the graph is called a dominating set of the graph if for every vertex v of the graph, either in v is D or there exists an edge(u,v) with u in D. A dominating set of a graph G is said to be independent if no two vertices are adjacent. The independent domination number of a graph is the size of a smallest independent dominating set of the graph.

*Compute:* NP-hard; small-n exact search / ILP (min independent dominating set).

### `λ(v)` — local independence of a vertex  [25 open]

> The independence number of the subgraph induced by the neighbors of vertex v. The maximum of λ(v), also denoted λ_max(v), is the largest among all local independence of the vertices of the graph; the smallest of all local independence of vertices is denoted λ_min(v). The average of λ(v), λ_avg(v), is the average of all local independence of the vertices of the graph. Note: if maximum of λ(v) ≤ 2, then the graph is claw-free

*Compute:* Cheap for small degree: independence number of G[N(v)] per vertex; neighborhoods are small in sparse graphs. lambda_max / lambda_min / lambda_avg all derived.

### `bar(G)` — the complement of a graph, G  [23 open]

> Let G be a graph. The complement graph of G, denoted bar(G), is the graph on the same vertex set such that u and v are adjacent in bar(G) if and only if they are not adjacent in G.

*Compute:* Trivial.

### `b(G)` — bipartite number of a graph  [18 open]

> The maximum number of vertices of an induced bipartite subgraph of the graph.

*Compute:* NP-hard (max induced bipartite = n - min OCT); exact to n~30 brute force / ILP; use odd-cycle-transversal solvers.

### `A-B` — Set Difference  [18 open]

> The set of elements in A but not in B.

*Compute:* Trivial.

### `α \'(G)` — critical independence number of G  [17 open]

> is number of vertices of a largest critical independent set. A critical independent set S is a subset of the vertices of the graph that is independent and has the property that |S| - |N(S)| ≥ |U| - |N(U)| for any independent subset U of the vertices of G.

*Compute:* Polynomial! (Zhang; via matching / Konig-Egervary theory) - critical independence number.

### `dist_even(v)` — even distance from a vertex v  [15 open]

> The number of vertices whose distance from v is an even integer. The minimum of dist_even(v) is the smallest among all dist_even(v) for v a vertex of the graph. The maximum of dist_even(v) is the largest among all dist_even(v) for v a vertex of the graph. The average of dist_even(v) is the average of all dist_even(v) for v a vertex of the graph

*Compute:* Poly (BFS): #vertices at even distance from v (distance 0 counts - verify convention on d(v,v)=0; page examples imply v itself is counted).

### `μ(G)` — matching number  [14 open]

> The maximum number of edges such that no two have a vertex in common.

*Compute:* Polynomial: max matching (networkx.max_weight_matching / hopcroft_karp for bipartite).

### `α_κ` — k-independence number  [13 open]

> A subset of the vertices, D_k, of the graph is called a k-independent set of the graph if the subgraph induced by D_k has maximum degree at most k-1. The k-independence number of a graph is the order of a largest k-independent set of the graph.

*Compute:* NP-hard (max induced subgraph of max degree <= k-1); small-n exact.

### `tree(G)` — tree number of a graph  [12 open]

> The number of vertices of a largest induced tree of the graph.

*Compute:* NP-hard (max induced tree); small-n exact.

### `ecc(S)` — eccentricty of a set of vertices, S  [12 open]

> Let S be a subset of the vertices a graph. By the distance from a vertex, v, to a set we mean the smallest distance from v to any of the vertices of S. Then ecc(S) is the maximum of distances from vertices of V-S to the set S.

*Compute:* Poly: max over v in V-S of dist(v,S).

### `wtd(G)` — G well total dominated  [12 open]

> is a graph in which every minimal total dominating set is a minimum total dominating set

*Compute:* Expensive: must check every minimal total dominating set is minimum (enumeration); 0/1 property.

### `CEIL[x]` — ceiling of a number, x  [11 open]

> The smallest integer greater than or equal to x.

*Compute:* Function, not invariant: ceiling.

### `ecc(v)` — eccentricity of a vertex  [10 open]

> The eccentricity of a vertex, v, is the maximum of {dist_G(v,u)| u is a vertex of the graph}.

*Compute:* Poly.

### `B` — the periphery of G(previously called here set of boundary vertices)  [10 open]

> The periphery of G is the set of vertices of maximum eccentricity of the graph.

*Compute:* Poly: B = argmax ecc.

### `G^2` — Second power graph of G  [10 open]

> is the graph on the same vertex as G with two vertices adjacent if and only if their distance in G is 2 or less.

*Compute:* Poly: build G^2.

### `N(e)` — neighborhood of an edge  [10 open]

> Let e=(u,v) such that u and v are adjacent in the graph. The neighborhood of e is the set of vertices of V adjacent to at least one of u or v.

*Compute:* Poly: max/min over edges of |N(u) u N(v) \ {u,v}| - check page usage: 'maximum of {N(e)}' means max size of an edge neighborhood.

### `C (center)` — C (center)  [9 open]

> A center vertex is a vertex of minimum eccentricity. The center of the graph is the set of all vertices that are centers.

*Compute:* Poly: C = argmin ecc.

### `traceable(G)` — Hamiltonian path  [9 open]

> A graph is said to have a Hamiltonian path if there exist two vertices with a path between them which visits each vertex of the graph exactly once.

*Compute:* NP-hard decision (Hamiltonian path); small-n exact.

### `rad(G)` — radius of the graph  [8 open]

> The minimum of eccentricities of vertices of the graph.

*Compute:* Poly (BFS all-pairs).

### `Δ(G)` — maximum degree of a graph  [8 open]

> The degree of a vertex is the number of edges incident to the vertex. The maximum degree of the graph is the maximum of all degrees of the vertices of the graph

*Compute:* Trivial.

### `mode(G)` — mode of degrees of a graph  [8 open]

> the mode of the degree sequence is the most frequently occuring degree. In case there is more than one mode, mode_min is the smallest mode and mode_max the largest mode. In case there is more than one mode, dd_mode(G) is the number of distinct modes.

*Compute:* Trivial (mode_min/mode_max when tie).

### `support vertex` — A support vertex of G  [8 open]

> is a vertex that is adjacent to a leaf of G. A leaf of G is a vertex of degree 1

*Compute:* Trivial.

### `f(G)` — forest number of a graph  [7 open]

> The number of vertices of a largest induced forest of the graph.

*Compute:* NP-hard (max induced forest = n - min FVS); exact small n; good FVS solvers exist.

### `A(G)` — annihilation number  [7 open]

> is defined as follows: let d_1,d_2,...,d_n be the degree sequence of a graph G arranged in non-decreasing order. A(G) is the largest integer k such that the sum of the first k terms of the sequence is at most half the sum of the entire sequence(i.e. the size of G).

*Compute:* Trivial: greedy prefix of nondecreasing degree sequence vs |E|.

### `peN(S)` — Number of private external neighbors of S  [7 open]

> is the number of vertices of V(G)\\S that have exactly one nieghbor in S.

*Compute:* Trivial per set.

### `FLOOR[x]` — floor of a number, x  [6 open]

> The largest integer less than or equal to x.

*Compute:* Function: floor.

### `Tdist_? (v)` — total distance of a vertex  [6 open]

> is the sum of distances from v to all other vertices. Tdist_min(v) is the minimum total distance among all vertices. Tdist_max(v) is the maximum of total distance among all vertices.

*Compute:* Poly: Tdist(v) = sum of distances (transmission).

### `deg_avg(G)` — average degree of a graph  [5 open]

> The average of the degrees of all vertices of the graph.

*Compute:* Trivial: 2m/n.

### `girth(G)` — girth of a graph  [5 open]

> the number of vertices of a smallest cycle of the graph.

*Compute:* Poly.

### `γ(G) or domination(G)` — domination number  [5 open]

> A subset of the vertices, D, of the graph is called a dominating set of the graph if for every vertex v of the graph, either in v is D or there exists an edge(u,v) with u in D. The domination number of a graph is the size of a smallest dominating set of the graph.

*Compute:* NP-hard; small-n exact / ILP.

### `median(degseq)` — median of the degree sequence(lower and upper)  [5 open]

> Let d_1 ≤ d_2 ≤... ≤ d_n-1 ≤ d_n be the degree sequence in nondecreasing order. If the graph has an odd number of vertices, then median of the ordered degree sequence is the d_(n+1)/2+1 degree; otherwise it is the average of the degrees d_n/2 and d_n/2+1. If the graph has an odd number of vertices then the lower and upper median are precisely the median degree of the graph; if the number of vertices is even, then the lower median is the d_n/2 degree and the upper median is the d_(n+2)/2 degree.

*Compute:* Trivial.

### `N[S]` — closed neighborhood of a subset of the vertices, S  [5 open]

> is the(set) union of N(S) and S.

*Compute:* Trivial.

### `maxine` — Maxine of G  [5 open]

> is the order of the largest independent set that one gets from the greedy algorithm that proceeds by removing a vertex of maximum degree until the subgraph is discrete.

*Compute:* Poly: greedy max-degree-removal independent set.

### `dist_? (M)` — distance between maximum degree vertices  [4 open]

> Let M be the set of vertices of maximum degree of the graph. Then dist_max(M) = maximum{dist_G(u,v) | u and v are in M} and dist_min(M) = minimum{dist_G(u,v) | u and v are in M}.

*Compute:* Poly: max distance between two max-degree vertices.

### `T(v)` — Number of triangles incident to a vertex  [4 open]

> the number of triangles incident to a vertex v, is the number of distinct complete subgraphs on three vertices that include vertex v. Compute T(v) for each vertex and we end up with a sequence of length n. T_min(v) is the smallest value of the sequence and T_max(v) the largest. freq[T_max(v)] is the frequency of the value T_max(v)

*Compute:* Poly.

### `δ(G)` — minimum degree of a graph  [4 open]

> The degree of a vertex is the number of edges incident to the vertex. The minimum degree of the graph is the minimum of all degrees of the vertices of the graph

*Compute:* Trivial.

### `n` — number of vertices  [4 open]

> The number of vertices of the graph.

*Compute:* Trivial.

### `dist_avg(S)` — average distance from a set  [4 open]

> Let S be a subset of vertices. The average of all dist_G(S,v)>0 where v is in V. The dist_G(S,v)> is the miminimum of dist(s,v) where s is in S.

*Compute:* Poly.

### `E_G(S)` — subset of edges of G induced by a subset of vertices, S  [4 open]

> For S a subset of the vertices. The subset of edges of G induced by vertices of S is the set of(u,v) such that u and v are in S and are adjacent in G.

*Compute:* Trivial per set.

### `isolates(G)` — Number of isolates of G  [4 open]

> is the number of vertices of G of degree zero.

*Compute:* Trivial (in induced subgraphs).

### `res(G)` — residue of a graph  [3 open]

> Order the degree sequence in nondecreasing order d_1 ≥ d_2 ≥... ≥ d_n-1 ≥ d_n, remove d_1 and subtract one from each of the next d_1 entries of the ordered sequence. Now with the resulting sequence order again and repeat that is remove the largest entry and subtract one of the subsequent values of the sequence. Continue until the sequence is a zero sequence. The residue is the number of zeros at the end of this process.

*Compute:* Poly: Havel-Hakimi residue on degree sequence.

### `diam(G)` — diameter of a graph  [3 open]

> The maximum of eccentricities of vertices of the graph.

*Compute:* Poly.

### `path(G)` — path number of a graph  [3 open]

> The number of vertices of a largest induced path of the graph.

*Compute:* NP-hard (longest induced path); small-n exact.

### `χ_C4(G)` — C_4 -free characteristic function  [3 open]

> is 1 if G is C_4 -free(not necessarily induced) and 0 otherwise.

*Compute:* Poly: C4-free indicator (0/1).

### `R(v)` — a radial circle centered at a center vertex v  [3 open]

> is the of vertices at distance radius from vertex v.

*Compute:* Poly (BFS layers from a center).

### `E(S)` — Edges induced by a vertex set  [3 open]

> is the set of edges induced by the vertices of S.

*Compute:* Trivial.

### `σ(G)` — second smallest degree of the degree sequence  [3 open]

> order the degree sequence in nondecreasing order d_1 ≤ d_2 ≤... ≤ d_n-1 ≤ d_n, the second smallest degree of the sequence is the 2nd entry.

*Compute:* Trivial: 2nd smallest degree.

### `κ(G)` — connectivity number  [3 open]

> is the fewest number of vertices whose removal disconnects the graph.

*Compute:* Poly (vertex connectivity).

### `WP( bar(G) )` — Welsh-Powell of the complement of G  [3 open]

> is the largest k such that the k + d_k is less than or equal to n, where the degree sequence is order in nondecreasing order, that is d_1 <= d_2 <=... d_n.

*Compute:* Trivial: Welsh-Powell bound on complement degree sequence.

### `disp(v)` — disparity of a vertex  [3 open]

> is the number of distinct degrees that occur among it neighbors. This is computed for each vertex. Then the maximum, minimum and average are computed over all and denoted, disp_max, disp_min and disp_avg, respectively

*Compute:* Poly: #distinct degrees among neighbors, per vertex; then max/min/avg.

### `c(G)` — A component of a graph is a maximal connected subgraph  [3 open]

> is the number of components of G and c_L(G) is the order of a largest component of G.

*Compute:* Poly.

### `|S|` — cardinality of a set, S  [2 open]

> The number of elements of the set.

*Compute:* Trivial.

### `dist_avg(C)` — average distance between center vertices  [2 open]

> Let C be the set of vertices of minimum eccentricity of the graph. Then dist_avg is the average of all nonzero dist_G(u,v) such that u and v are in C.

*Compute:* Poly.

### `dist_avg(S,V)` — average distance from each vertex of a set of vertices  [2 open]

> Let S be a subset of vertices. The average of all dist_G(s,v)>0 such that s is in S and v is in V.

*Compute:* Poly.

### `E(G)` — Edge Set  [2 open]

> The set of edges of G.

*Compute:* Trivial.

### `ecc_avg(S)` — average of eccentricities of vertices in S  [2 open]

> is average of eccentricities of vertices in S.

*Compute:* Poly.

### `dd(G)` — number of distinct degrees  [2 open]

> The number of distinct values of the degree sequence of the graph

*Compute:* Trivial.

### `HH_k(G)` — kth step for a zero in the Havil-Hakimi process  [2 open]

> Order the degree sequence in non-increasing order d_1 ≥ d_2 ≥... ≥ d_n-1 ≥ d_n, remove d_1 and subtract one from each of the next d_1 entries of the ordered sequence. Now with the resulting sequence order again, and repeat that is remove the largest entry and subtract one of the subsequent values of the sequence. Continue until a zero occurs in a resulting sequence. kth step for a zero in the Havil-Hakimi process is the number of iterations until a zero occurs.

*Compute:* Poly: Havel-Hakimi step count to first zero.

### `pN(S)` — Number of private neighbors of S  [2 open]

> is the number of vertices of V(G) that have exactly one nieghbor in S.

*Compute:* Trivial per set.

### `n mod Δ(G)` — n modulus maximum degree  [1 open]

> For Δ(G) ≥ 2, n mod Δ(G) is the remainder upon division of n(number of vertices of G) by Δ(G).

*Compute:* Trivial.

### `dist_? (A)` — distance between minimum degree vertices  [1 open]

> Let A be the set of vertices of minimum degree of the graph. Then dist_max(A) = maximum{dist_G(u,v) | u and v are in A} and dist_min(A) = minimum{dist_G(u,v) | u and v are in A}. dist_avg(A) is the average of all nonzero dist_G(u,v) such that u and v are in A

*Compute:* Poly.

### `even_mode(G)` — mode of even degrees of a graph  [1 open]

> the mode of the even degrees of the degree sequence is the most frequently occuring degree that is an even integer. In case there is more than one mode, even_mode_min is the smallest and even_mode_max the largest.

*Compute:* Trivial.

### `length(G)` — length of a graph  [1 open]

> the square root of the sum of the squares of degrees.

*Compute:* Trivial: sqrt(sum deg^2).

### `LN(x)` — LN  [1 open]

> the natural logarithm of x.

*Compute:* Function: natural log.

### `α_c(G)` — alphacore of a graph  [1 open]

> The cardinality of the intersection of all maximum independent sets of G.

*Compute:* Requires enumerating all maximum independent sets (expensive but ok small n).

### `f_1(G)` — frequency of degree one  [1 open]

> The number of vertices of degree one of the graph. Also known as the number of pendant vertices. Note, if the graph is a tree, then this is equivalent to the number of leaves of the tree

*Compute:* Trivial: #vertices of degree 1.

### `dist_avg(B)` — average distance between boundary vertices  [1 open]

> Let B be the set of vertices of maximum eccentricity of the graph. Then dist_avg is the average of all nonzero dist_G(u,v) such that u and v are in B.

*Compute:* Poly.

### `Δ(S)` — maximum degree among vertices of a subset of vertices, S  [1 open]

> maximum {deg_G(v) | v in S}

*Compute:* Trivial.

### `dist_avg(B,V)` — average distance from periphery vertices(previously called here boundary vertices)  [1 open]

> Let B be the set of vertices of maximum eccentricity. The average of all dist_G(b,v)>0 such that b is in B and v is in V.

*Compute:* Poly: avg over v in V of dist(v, B) (B = periphery).

### `ecc_avg(S)` — average eccentricty of a set of vertices, S  [1 open]

> Let S be a subset of the vertices a graph. Then ecc_avg(S) is the average of all ecc(v) such that v is in S. In case S = V(G) the number is denoted as ecc_avg(G)

*Compute:* Poly.

### `χ_residue=2(G)` — residue = 2 characteristic function  [1 open]

> is 1 if the residue of G is equal to 2, otherwise the value is 0.

*Compute:* Poly: residue==2 indicator.

### `χ_bipartite(G)` — bipartite characteristic function  [1 open]

> is 1 if G is a bipartite graph and 0 otherwise.

*Compute:* Poly: bipartite indicator.

### `t(G)` — number of triangles of a graph  [1 open]

> The number of subgraphs isomorphic to a complete graph on 3 vertices of the graph

*Compute:* Poly: triangle count.

### `even horizontal(v)` — even horizontal of a vertex  [1 open]

> is the number of edges whose endpoints are at the same even distance from vertex v.

*Compute:* Poly: edges with both ends at equal even distance from v.

### `ecc_avg(G)` — average eccentricty of G  [1 open]

> is average of eccentricities of vertices of G.

*Compute:* Poly.

### `dist_odd(v)` — odd distance from a vertex v  [1 open]

> The number of vertices whose distance from v is an odd integer. The minimum of dist_odd(v) is the smallest among all dist_odd(v) for v a vertex of the graph. The maximum of dist_odd(v) is the largest among all dist_odd(v) for v a vertex of the graph. The average of dist_odd(v) is the average of all dist_odd(v) for v a vertex of the graph

*Compute:* Poly (BFS): #vertices at odd distance from v.

### `odd horizontal(v)` — odd horizontal of a vertex  [1 open]

> is the number of edges whose endpoints are at the same odd distance from vertex v.

*Compute:* Poly.

### `dist_avg(C,V)` — average distance from center vertices  [1 open]

> Let C be the set of vertices of minimum eccentricity of the graph. Then dist_avg(C,V) is the average of all nonzero dist_G(u,v) such that u is in C and and v is in V.

*Compute:* Poly: avg over v of dist(v, C).

### `v_c(G)` — vertex cover number of G  [1 open]

> is number of vertices of a smallest subset S of the vertices of the graph such that each edge of the graph has at least one endpoint in S.

*Compute:* = n - alpha(G); NP-hard, small-n fine.

### `q1(degseq)` — 1st quartile of the degree sequence  [1 open]

> Let d_1 ≤ d_2 ≤... ≤ d_n-1 ≤ d_n be the degree sequence in nondecreasing order. The 1st quartile is the d_(n)/4 degree.

*Compute:* Trivial.

### `κ_v(G)` — number of cut vertices of G  [1 open]

> ; a cut vertex is whose removal from the graph increases the number of components of the graph.

*Compute:* Poly (articulation points).

### `|E(S,T)|` — Number of edges of G between S and T  [1 open]

> is the number of edges of G with one endpoint in S and the other in T.

*Compute:* Trivial.

### `SW(G)` — Szekeres-Wilf invariant  [1 open]

> the maximum of minimum degrees over all subgraphs of G.

*Compute:* Poly: degeneracy+1-style (max over subgraphs of min degree) = graph degeneracy.

### `neighbor dominator` — neighbor dominator  [1 open]

> vertex v(neighbor) dominates u if N[u] is contained in N[v]

*Compute:* Poly per pair: N[u] subset of N[v].

### `CW(G)` — Caro-Wei invariant  [1 open]

> the sum of the reciprocals of one plus the degrees.

*Compute:* Trivial: sum 1/(1+deg(v)).

## Appendix: remaining definitions (not used by any open conjecture)

- **`temp(v)`** (temperature of a vertex): deg(v)/(n(G)-deg(v)). The maximum of temp(v) is the maximum of all temp(v) for v a vertex of G.
- **`N_G( bar(e) )`** (neighborhood of a nonedge of G): Let bar(e) =(u,v) such that u and v are not adjacent in the graph, G. The neighborhood of bar(e) is the set of vertices adjacent(in G) to at least one of u or v.
- **`S(v,k)`** (surface of a sphere): Let v be a vertex of G. The set of all vertices whose distance from v is k is S(v,k).
- **`L(T)`** (number of leaves of a tree, T): The number of vertices of degree one of the tree. Also called the number of pendant vertices
- **`dist_avg(V)`** (average distance of graph): average of all dist_G(u,v) such that u and v are distinct vertices of the graph.
- **`dist_avg(M)`** (average distance between maximum degree vertices): Let M be the set of vertices of maximum degree of the graph. Then dist_avg is the average of all nonzero dist_G(u,v) such that u and v are in M.
- **`M(G)`** (set of vertices of maximum degree of the graph G): note we may use M if there is no confusion which graph is under discussion
- **`dist_avg(M,V)`** (average distance from maximum degree vertices): Let M be the set of vertices of maximum degree of the graph with vertex set V. Then dist_avg(M,V) is the average of all nonzero dist_G(u,v) such that u is in M and and v is in V.
- **`dp(G)`** (number of diametrical pairs of a graph): The number of pairs of vertices of a graph, G, which are at distance diam(G)
- **`∑ deg_G(v)`** (sum of degrees of a graph): The sum of all degrees of the graph G.
- **`progressive-join(G,H)`** (progressive join of two graphs G and H): take the union of G and H. Enumerate the vertices of G as 0,1,...,n(G)-1. Enumerate the vertices of H as 0,1,...,n(H)-1. Then for every vertex i of G join it to vertices j of H such that i => j. This operation is not well defined in the sense that it depends on enumeration.
- **`n mod 2`** (n modulus 2): The number n mod 2 is the remainder upon division of n(number of vertices of G) by 2.
- **`ω(G)`** (clique number of a graph): The maximum number of vertices such that every two are adjacent.
- **`circumference(G)`** (induced circumference of a graph): the number of vertices of a largest induced cycle of the graph.
- **`freq(degree k)`** (frequency of degree k): The number of occurances of degree k among the vertices of the graph.
- **`δ(G)`** (Let S be a subset of the vertices of G): = min{deg_G(v): v in S}
- **`δ(S)`** (minimum degree among vertices of a subset, of vertices, S): minimum {deg_G(v) | v in S}
- **`d_1 ≤ d_2 ≤... ≤ d_n-1 ≤ d_n`** (ordered degree sequence): the degree sequence ordered in nondecreasing order.
- **`Σ(G)`** (second largest degree of the degree sequence): order the degree sequence in nondecreasing order d_1 ≤ d_2 ≤... ≤ d_n-1 ≤ d_n, the second largest degree of the sequence is the(n-1)th entry.
- **`u(G)`** (unique maximum independent set characteristic function): is 1 if G is has a unique independent set and 0 otherwise.
- **`Δ(R)`** (maximum degree of vertices on radial circles): is the maximum of degrees of vertices on radial circles. A radial circle is the set of vertices at distance radius from a center vertex.
- **`t(G)`** (tree characteristic function): is 1 if G is a tree and 0 otherwise.
- **`χ_K3(G)`** (K_3 -free characteristic function): is 1 if G is K_3 -free(i.e. triangle-free) and 0 otherwise.
- **`χ_claw`** (Claw-free characteristic function): is 1 if G is Claw-free, i.e. if it is K(1,3) free, and 0 otherwise.
- **`χ(G)`** (Chromatic number): the fewest number of colors needed to color the vertices of the graph in such a way that adjacent vertices receive different colors.
- **`χ_regular(G)`** (regular graph characteristic function): is 1 if G is regular, that is if maximum and minimum degrees are the same and 0 otherwise.
- **`2-B(G)`** (number of 2-distance diametrical pairs of a graph): The number of pairs of vertices of the boundary of a graph, which are at distance two
- **`horizontal(v)`** (edges horizontal to a vertex): is the number of edges whose endpoints are at the same distance from vertex v.
- **`deg_{avg}(S)`** (average degree of vertices of a subset of vertices, S): is the average of deg_G(v) for v in S

## Notes on precision

- Def 42 (residue): the page says "nondecreasing" but displays `d_1 ≥ d_2 ≥ …`; the process is on the *non-increasing* sequence (matches the Lean `SimpleGraph.residue` docstring: descending order, Havel-Hakimi until all zeros; residue = number of zeros).
- Def 89 (annihilation): equivalently (Lean `annihilationNumber`) the largest k such that the k smallest degrees sum to at most |E| (half of the degree sum).
- `b`, `f`, `tree`, `path` are *induced-subgraph order* invariants (largest induced bipartite / forest / tree / path — number of vertices), per both the page definitions and the Lean `largestInduced*Size` definitions. `p(G)` (path covering number) is different: minimum number of vertex-disjoint paths covering V(G).
- `L_s(G)`: maximum leaves over spanning trees; note `L_s(G) = n - γ_c(G)` (connected domination), used on the page at #190.
- Eccentricity of a *set* (def 52): `ecc(S) = max over v of dist(v,S)` — not the max eccentricity of members of S. But `ecc_avg(S)` (defs 36/108) averages vertex eccentricities `ecc(v)` for v in S. Watch this asymmetry; it is DeLaViña's.
- `λ(v)` (local independence) on a vertex with no neighbors is α(∅)=0; for connected graphs with n>1 every vertex has a neighbor, so λ(v) ≥ 1.
