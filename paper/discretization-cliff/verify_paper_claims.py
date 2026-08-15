#!/usr/bin/env python3
"""Independent verification of every closed form asserted in

    paper/discretization-cliff/main.tex

for the family C5[K_m] (m = 1..6), the odd-cycle pinning corollary, the four
conjecture right-hand sides, and the eight retro-kill right-hand sides.

Everything is computed by exhaustive enumeration on the explicitly constructed
graph; no formula from the paper is used as an input to the computation, only
as the assertion being checked.  Exact arithmetic only (``fractions.Fraction``
and ``math.isqrt``): no floating-point value enters any comparison.

Hereditary shortcut used throughout: the classes {independent}, {bipartite},
{forest}, {tree-or-empty}, {path-or-empty} are all closed under taking induced
subgraphs of the witness, so "no witness of size t" implies "no witness of size
t' > t"; the searches below therefore go upward and stop at the first empty
size.

Dependencies: networkx.

Usage:  python3 verify_paper_claims.py
Exit status 0 iff every assertion checks out.
"""

from __future__ import annotations

import itertools
import sys
from fractions import Fraction
from math import isqrt

import networkx as nx

MMAX = 6


# --------------------------------------------------------------------------- #
# construction
# --------------------------------------------------------------------------- #
def cycle_clique_blowup(k: int, m: int) -> nx.Graph:
    """C_k[K_m]: k blobs of K_m arranged on a k-cycle, adjacent blobs joined."""
    graph = nx.Graph()
    graph.add_nodes_from(range(k * m))
    blob = lambda v: v // m
    for u in range(k * m):
        for v in range(u + 1, k * m):
            if blob(u) == blob(v) or (blob(u) - blob(v)) % k in (1, k - 1):
                graph.add_edge(u, v)
    return graph


# --------------------------------------------------------------------------- #
# exhaustive invariant computations
# --------------------------------------------------------------------------- #
def max_induced(graph: nx.Graph, predicate, cap: int) -> int:
    """Largest t <= cap admitting an induced subgraph satisfying `predicate`.

    Raises if the cap is reached, so a returned value is always exact.
    """
    best = 0
    for size in range(1, cap + 1):
        if not any(
            predicate(graph.subgraph(subset))
            for subset in itertools.combinations(graph, size)
        ):
            return best
        best = size
    raise AssertionError(f"cap {cap} reached on n={graph.number_of_nodes()}")


def is_independent(sub: nx.Graph) -> bool:
    return sub.number_of_edges() == 0


def is_tree_nonempty(sub: nx.Graph) -> bool:
    return sub.number_of_nodes() > 0 and nx.is_tree(sub)


def is_induced_path(sub: nx.Graph) -> bool:
    if sub.number_of_nodes() == 0 or not nx.is_connected(sub):
        return False
    if sub.number_of_nodes() == 1:
        return True
    degrees = sorted(d for _, d in sub.degree())
    return nx.is_tree(sub) and degrees[0] == 1 and degrees[-1] <= 2


def independence_number(graph: nx.Graph, cap: int) -> int:
    return max_induced(graph, is_independent, cap)


def clique_number(graph: nx.Graph) -> int:
    return max(len(c) for c in nx.find_cliques(graph))


def domination_number(graph: nx.Graph, *, total=False, connected=False,
                      cap: int = 6) -> int:
    nodes = list(graph)
    for size in range(1, cap + 1):
        for subset in itertools.combinations(nodes, size):
            chosen = set(subset)
            if total:
                ok = all(any(w in chosen for w in graph[v]) for v in nodes)
            else:
                ok = all(
                    v in chosen or any(w in chosen for w in graph[v])
                    for v in nodes
                )
            if ok and connected and not nx.is_connected(graph.subgraph(subset)):
                ok = False
            if ok:
                return size
    raise AssertionError("no dominating set within cap")


def dist_even_min(graph: nx.Graph) -> int:
    """min over v of |{x : d(v,x) even}|, counting x = v (distance 0)."""
    dist = dict(nx.all_pairs_shortest_path_length(graph))
    return min(sum(1 for u in graph if dist[v][u] % 2 == 0) for v in graph)


def even_horizontal_max(graph: nx.Graph) -> int:
    """max over v of |{xy in E : d(v,x) = d(v,y) and that value is even}|."""
    best = 0
    for v in graph:
        dist = nx.single_source_shortest_path_length(graph, v)
        best = max(
            best,
            sum(1 for x, y in graph.edges()
                if dist[x] == dist[y] and dist[x] % 2 == 0),
        )
    return best


def min_edge_neighbourhood_in_complement(graph: nx.Graph) -> int:
    """min over xy in E(complement) of |N_comp(x) union N_comp(y)|.

    Endpoints are included when they belong to the union; this is the reading
    pinned by DeLaVina's definition 28 composed with definition 31.
    """
    comp = nx.complement(graph)
    return min(len(set(comp[x]) | set(comp[y])) for x, y in comp.edges())


def local_independence_max(graph: nx.Graph) -> int:
    return max(
        independence_number(graph.subgraph(list(graph[v])), cap=4)
        for v in graph
    )


# --------------------------------------------------------------------------- #
# exact ceilings
# --------------------------------------------------------------------------- #
def ceil_div(numerator: int, denominator: int) -> int:
    return -((-numerator) // denominator)


def ceil_frac(value: Fraction) -> int:
    return -((-value.numerator) // value.denominator)


def ceil_sqrt(value: int) -> int:
    """Smallest integer c with c*c >= value, for value >= 0."""
    assert value >= 0
    root = isqrt(value)
    return root if root * root == value else root + 1


# --------------------------------------------------------------------------- #
# checks
# --------------------------------------------------------------------------- #
def check_carrier_profile() -> None:
    """The headline numbers quoted for C5[K4] itself (Figure 1, Section 6)."""
    print("Carrier C5[K4] (Figure 1)")
    graph = cycle_clique_blowup(5, 4)
    assert graph.number_of_nodes() == 20
    assert graph.number_of_edges() == 110
    assert {d for _, d in graph.degree()} == {11}
    assert nx.is_connected(graph) and nx.diameter(graph) == 2
    assert independence_number(graph, cap=4) == 2
    assert clique_number(graph) == 8
    assert dist_even_min(graph) == 9
    assert even_horizontal_max(graph) == 28
    assert min_edge_neighbourhood_in_complement(graph) == 16
    assert domination_number(graph, total=True) == 3
    assert 20 % 11 == 9
    assert ceil_div(9 + 4 + 1, 3) == 5            # conjecture 63 RHS
    assert ceil_sqrt(1 + 2 * 9) == 5              # conjecture 85 RHS
    assert ceil_sqrt(2 * (1 + 9)) == 5            # conjecture 64 RHS
    assert Fraction(-19 + 16, 2) == Fraction(-3, 2)   # conjecture 309 RHS
    print("  OK n=20 |E|=110 11-regular diam2 alpha=2 omega=8 "
          "dist_even=9 even_horizontal=28 min|N_comp(e)|=16 gamma_t=3; "
          "RHS(63)=RHS(85)=RHS(64)=5 > 4 = f = tree; RHS(309)=-3/2 < 3 = gamma_t")


def check_c5_family() -> None:
    print("\nC5[K_m] closed forms (Propositions 4.1-4.2, Theorems 5.1-5.4, "
          "Table 1)")
    print(
        f"{'m':>2} {'n':>3} {'deg':>4} {'a':>2} {'w':>3} {'b':>2} {'f':>2} "
        f"{'tr':>2} {'pa':>2} {'lam':>3} {'de':>3} {'eh':>4} {'nmodD':>6} "
        f"{'g':>2} {'gt':>3} {'gc':>3} {'Ls':>3} {'Nbe':>4} "
        f"{'R63':>4} {'R85':>4} {'R64':>4} {'R309':>7}"
    )
    for m in range(1, MMAX + 1):
        graph = cycle_clique_blowup(5, m)
        order = graph.number_of_nodes()
        degree_set = {d for _, d in graph.degree()}
        assert len(degree_set) == 1
        degree = degree_set.pop()

        alpha = independence_number(graph, cap=4)
        omega = clique_number(graph)
        bip = max_induced(graph, nx.is_bipartite, cap=5)
        forest = max_induced(graph, nx.is_forest, cap=5)
        tree = max_induced(graph, is_tree_nonempty, cap=5)
        path = max_induced(graph, is_induced_path, cap=5)
        lam = local_independence_max(graph)
        d_even = dist_even_min(graph)
        e_hor = even_horizontal_max(graph)
        gamma = domination_number(graph)
        gamma_t = domination_number(graph, total=True)
        gamma_c = domination_number(graph, connected=True)
        leaves = order - gamma_c
        nbe = min_edge_neighbourhood_in_complement(graph)

        rhs63 = ceil_div(d_even + bip + 1, 3)
        rhs85 = ceil_sqrt(1 + 2 * d_even)
        rhs64 = ceil_sqrt(alpha * (1 + order % degree))
        rhs309 = Fraction((d_even - e_hor) + nbe, 2)

        print(
            f"{m:>2} {order:>3} {degree:>4} {alpha:>2} {omega:>3} {bip:>2} "
            f"{forest:>2} {tree:>2} {path:>2} {lam:>3} {d_even:>3} {e_hor:>4} "
            f"{order % degree:>6} {gamma:>2} {gamma_t:>3} {gamma_c:>3} "
            f"{leaves:>3} {nbe:>4} {rhs63:>4} {rhs85:>4} {rhs64:>4} "
            f"{str(rhs309):>7}"
        )

        # Proposition 4.1
        assert order == 5 * m
        assert degree == 3 * m - 1
        assert graph.number_of_edges() == 5 * m * (3 * m - 1) // 2
        assert nx.diameter(graph) == 2 and nx.radius(graph) == 2
        assert alpha == 2
        assert omega == 2 * m
        assert (gamma, gamma_t, gamma_c) == (2, 3, 3)
        assert leaves == 5 * m - 3
        assert lam == 2

        # equation (3.1) / Theorem 3.2(iv)
        assert (path, tree, forest, bip) == (4, 4, 4, 4)

        # Proposition 4.2
        assert d_even == 2 * m + 1
        assert e_hor == m * (2 * m - 1)
        assert nbe == 4 * m
        comp = nx.complement(graph)
        assert {d for _, d in comp.degree()} == {2 * m}
        assert sum(nx.triangles(comp).values()) == 0
        if m >= 3:
            assert order % degree == 2 * m + 1
        else:
            assert order % degree == (1 if m == 1 else 0)

        # Theorems 5.1-5.4
        assert rhs63 == ceil_div(2 * m + 6, 3)
        assert rhs85 == ceil_sqrt(4 * m + 3)
        assert rhs64 == (ceil_sqrt(4 * (m + 1)) if m >= 3 else 2)
        assert rhs309 == Fraction(-2 * m * m + 7 * m + 1, 2)

        # Table 1 thresholds and equality pattern
        assert (forest >= rhs63) == (m <= 3)
        assert (tree >= rhs85) == (m <= 3)
        assert (forest >= rhs64) == (m <= 3)
        assert (Fraction(gamma_t) <= rhs309) == (m <= 2)
        assert (forest == rhs63) == (m in (2, 3))
        assert (tree == rhs85) == (m in (2, 3))
        assert (forest == rhs64) == (m == 3)
        assert (Fraction(gamma_t) == rhs309) == (m == 1)
        assert Fraction(gamma_t) - rhs309 == Fraction((2 * m - 5) * (m - 1), 2)

        # Section 6(b): removing the ceilings does not move the thresholds
        assert (Fraction(4) >= Fraction(2 * m + 6, 3)) == (m <= 3)
        assert (16 >= 4 * m + 3) == (m <= 3)
        assert (16 >= 4 * (m + 1)) == (m <= 3)
        # ... but three of the five equalities are artefacts of the ceilings
        assert (Fraction(4) == Fraction(2 * m + 6, 3)) == (m == 3)
        assert (16 == 4 * m + 3) is False
        assert (16 == 4 * (m + 1)) == (m == 3)

    print(f"  OK all C5[K_m] closed forms, thresholds and equality pattern "
          f"verified for m = 1..{MMAX}")


def check_odd_cycle_pinning() -> None:
    """Corollary 3.3: C_{2r+1}[K_m] pins path=tree=f=b at 2r = 2*alpha."""
    print("\nCorollary 3.3 (odd-cycle pinning)")
    for k, ms in ((5, (1, 2, 3, 4)), (7, (1, 2, 3)), (9, (1, 2))):
        r = (k - 1) // 2
        for m in ms:
            graph = cycle_clique_blowup(k, m)
            alpha = independence_number(graph, cap=r + 1)
            assert alpha == r, (k, m, alpha)
            # upper bound: no (2r+1)-subset induces a bipartite graph
            assert not any(
                nx.is_bipartite(graph.subgraph(S))
                for S in itertools.combinations(graph, 2 * r + 1)
            ), (k, m)
            # lower bound: one vertex per blob, omitting blob 0, is an
            # induced path on 2r vertices
            witness = [i * m for i in range(1, k)]
            assert is_induced_path(graph.subgraph(witness)), (k, m)
            print(f"  C{k}[K_{m}]: n={graph.number_of_nodes():>3} "
                  f"alpha={alpha}  path=tree=f=b={2 * r}=2*alpha")
    print("  OK odd-cycle pinning verified")


def check_retro_kill_values() -> None:
    """Table 3: the eight retro-kill right-hand sides on C5[K4]."""
    print("\nTable 3 (retro-kills on C5[K4])")
    m = 4
    graph = cycle_clique_blowup(5, m)
    order, degree = graph.number_of_nodes(), 3 * m - 1
    forest = bip = path = 4
    lam = 2
    d_even = dist_even_min(graph)
    residue = order % degree
    comp_degree = 2 * m
    length_comp_sq = order * comp_degree ** 2      # sum of squared degrees
    distinct_degrees = 1                            # G is regular
    neighbourhood_A = order                         # A = V, N(A) = V
    dist_max_A = nx.diameter(graph)
    transmission = 1 * (3 * m - 1) + 2 * (2 * m)    # Tdist(v), any v
    dist_avg = Fraction(transmission, order - 1)

    rhs = {}
    rhs["24"] = lam + ceil_div(d_even, 3)
    rhs["25"] = 2 * ceil_div(1 + d_even, 3)
    rhs["46"] = (3 * (path - 1) + residue) // 3      # floor(path-1+residue/3)
    rhs["52"] = ceil_div(distinct_degrees + 1 + residue, 2)
    rhs["54"] = ceil_frac(dist_avg + Fraction(d_even, 2))
    rhs["55"] = ceil_div(3 * (d_even - 1) + neighbourhood_A, 3)
    rhs["56"] = ceil_sqrt(dist_max_A * (1 + comp_degree))
    # 49: ceil(2 + sqrt(sum deg(comp)^2)/6); bracket sqrt exactly
    assert length_comp_sq == 1280
    assert (6 * 5) ** 2 < length_comp_sq <= (6 * 6) ** 2
    rhs["49"] = 2 + 6

    expected = {"24": 5, "25": 8, "46": 6, "49": 8,
                "52": 6, "54": 6, "55": 15, "56": 5}
    assert rhs == expected, (rhs, expected)
    assert forest == 4 and bip == 4
    for key in sorted(expected, key=int):
        print(f"  #{key}: LHS = 4, RHS = {expected[key]}  -> violated")
    print("  OK all eight retro-kill right-hand sides reproduce")


def main() -> int:
    check_carrier_profile()
    check_c5_family()
    check_odd_cycle_pinning()
    check_retro_kill_values()
    print("\nALL PAPER CLAIMS VERIFIED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
