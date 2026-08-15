"""Frozen catalogue for the three-arm test's control arm.

Committed BEFORE the conjecture population exists (see
results/experiment/PREREGISTRATION.md, tag prereg-three-arm-v1). The catalogue
arm is a pure lookup: it tests every target against exactly these graphs and
does no design step. Freezing it here means it cannot later be widened to
rescue, or narrowed to flatter, the wall arm.

Any change to this file after the population is frozen is a protocol violation
and must be recorded as such in the results.
"""
import itertools

import networkx as nx


def blowup(cycle_len, sizes):
    """C_k[K_m]-style blow-up: blobs on a cycle, complete join between adjacent."""
    if isinstance(sizes, int):
        sizes = [sizes] * cycle_len
    offs = [sum(sizes[:i]) for i in range(cycle_len)]
    n = sum(sizes)
    G = nx.Graph()
    G.add_nodes_from(range(n))

    def blob(v):
        for i in range(cycle_len - 1, -1, -1):
            if v >= offs[i]:
                return i

    for u in range(n):
        for v in range(u + 1, n):
            bu, bv = blob(u), blob(v)
            d = (bu - bv) % cycle_len
            if bu == bv or d == 1 or d == cycle_len - 1:
                G.add_edge(u, v)
    return G


def paley(q):
    """Paley graph on q ≡ 1 (mod 4) vertices, q prime."""
    assert q % 4 == 1
    squares = {(x * x) % q for x in range(1, q)}
    G = nx.Graph()
    G.add_nodes_from(range(q))
    for u in range(q):
        for v in range(u + 1, q):
            if (u - v) % q in squares:
                G.add_edge(u, v)
    return G


def broom(handle, bristles):
    G = nx.path_graph(handle)
    for i in range(bristles):
        G.add_edge(handle - 1, handle + i)
    return G


def double_star(a, b):
    G = nx.Graph()
    G.add_edge(0, 1)
    for i in range(a):
        G.add_edge(0, 2 + i)
    for j in range(b):
        G.add_edge(1, 2 + a + j)
    return G


def _named():
    out = {}
    # the campaign's own carriers
    for m in range(2, 7):
        out[f"C5[K{m}]"] = blowup(5, m)
    out["C7[K3]"] = blowup(7, 3)
    out["C9[K3]"] = blowup(9, 3)
    # triangular graphs — the lever that produced WOWII 181
    for n in range(7, 10):
        L = nx.line_graph(nx.complete_graph(n))
        out[f"T({n})"] = nx.convert_node_labels_to_integers(L)
    # classical extremal / pathological graphs
    out["Petersen"] = nx.petersen_graph()
    for n in range(5, 8):
        K = nx.Graph()
        verts = list(itertools.combinations(range(n), 2))
        K.add_nodes_from(range(len(verts)))
        for i, a in enumerate(verts):
            for j, b in enumerate(verts):
                if i < j and not set(a) & set(b):
                    K.add_edge(i, j)
        out[f"Kneser({n},2)"] = K
    for q in (13, 17, 29):
        out[f"Paley({q})"] = paley(q)
    for parts in [(2, 2, 2), (3, 3, 3), (2, 3, 4), (4, 4), (3, 5)]:
        out["K" + ",".join(map(str, parts))] = nx.complete_multipartite_graph(*parts)
    for k in (3, 4, 5):
        out[f"cocktail({k})"] = nx.complete_multipartite_graph(*([2] * k))
    for n in (3, 4, 5, 6):
        out[f"prism(C{n})"] = nx.cartesian_product(nx.cycle_graph(n), nx.complete_graph(2))
    out["MobiusKantor"] = nx.moebius_kantor_graph()
    for a, b in [(3, 3), (3, 4), (4, 4), (2, 5)]:
        out[f"K{a},{b}"] = nx.complete_bipartite_graph(a, b)
    for n in (5, 8, 12):
        out[f"star({n})"] = nx.star_graph(n)
    out["broom(4,3)"] = broom(4, 3)
    out["broom(6,4)"] = broom(6, 4)
    for k in (4, 8, 12):
        out[f"doublestar({k},{k})"] = double_star(k, k)
    return out


def catalogue():
    """The frozen catalogue: every named graph plus its complement.

    Returns {name: nx.Graph}. Complements are included because several of this
    campaign's witnesses were complement carriers (e.g. the triangle-free
    8-regular complement of C5[K4]).
    """
    base = _named()
    out = {}
    for name, G in base.items():
        G = nx.convert_node_labels_to_integers(G)
        out[name] = G
        C = nx.complement(G)
        if C.number_of_edges() and nx.is_connected(C):
            out[f"comp({name})"] = C
    return out


if __name__ == "__main__":
    cat = catalogue()
    print(f"frozen catalogue: {len(cat)} graphs")
    for name, G in sorted(cat.items(), key=lambda kv: kv[1].number_of_nodes()):
        print(f"  {name:24s} n={G.number_of_nodes():3d} m={G.number_of_edges():4d} "
              f"conn={nx.is_connected(G)}")
