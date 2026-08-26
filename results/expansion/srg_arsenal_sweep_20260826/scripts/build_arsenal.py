"""Build the extended SRG arsenal and certify its invariants.

Families (all vertex-transitive; explicit automorphism witnesses built):
  T(n)      = line graph of K_n,            n = 10..16
  KG(n,2)   = complement of T(n),           n = 10..16
  Paley(q)  prime q = 1 mod 4, q <= 101     (13,17,29,37,41,53,61,73,89,97,101)
  CP(m)     = K_{2,2,...,2}                 m = 2..8
  CMP(m)    = K_{2,...,2,1}                 m = 2..8
  comp(C5[K_m]),                            m = 2..8
  C7[K3], C9[K3]
  K_{3,3}, K_{3,3,3}

Writes cache/arsenal.gpickle + cache/arsenal_basic.json and prints a table.
"""
import json
import pickle
import sys
from fractions import Fraction
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
CACHE = HERE.parent / "cache"
CACHE.mkdir(exist_ok=True)


def T(n):
    """L(K_n) with vertex i = i-th edge of K_n in itertools.combinations order."""
    import itertools
    kedges = list(itertools.combinations(range(n), 2))
    pos = {e: i for i, e in enumerate(kedges)}
    LG = nx.line_graph(nx.complete_graph(n))
    return nx.relabel_nodes(LG, {e: pos[tuple(sorted(e))] for e in LG.nodes()},
                            copy=True)


def paley(q):
    squares = {(x * x) % q for x in range(1, q)}
    G = nx.Graph()
    G.add_nodes_from(range(q))
    for x in range(q):
        for y in range(x + 1, q):
            if (x - y) % q in squares:
                G.add_edge(x, y)
    return G


def lex_product(base, blob):
    """Lexicographic product base[K_blob]."""
    H = nx.Graph()
    bn = list(base.nodes())
    for i in bn:
        for j in range(blob):
            H.add_node((i, j))
    for i in bn:
        for a in range(blob):
            for b in range(a + 1, blob):
                H.add_edge((i, a), (i, b))
    for i, j in base.edges():
        for a in range(blob):
            for b in range(blob):
                H.add_edge((i, a), (j, b))
    return nx.convert_node_labels_to_integers(H)


# ------------------------------------------------ transitivity certificates

def _perm_check(G, p):
    """p: dict old->new; verify adjacency preservation both ways."""
    E = set(G.edges())
    for u, v in E:
        if (p[u], p[v]) not in E and (p[v], p[u]) not in E:
            return False
    return len(p) == G.number_of_nodes()


def transitivity_witness(G, family, param):
    """Return list of automorphism permutations whose orbit of node 0 covers V,
    each verified to preserve edges."""
    n = G.number_of_nodes()
    perms = []
    if family in ("T", "KG"):
        # S_k acts on edges of K_k (k = param); graph vertices are those edges
        import itertools
        kn = int(param)
        kedges = list(itertools.combinations(range(kn), 2))
        pos = {e: i for i, e in enumerate(kedges)}

        def im(x, a):
            return kn - 1 if x == a else (a if x == kn - 1 else x)

        for t in range(kn - 1):
            pi = {}
            for idx, (a, b) in enumerate(kedges):
                na, nb = sorted((im(a, t), im(b, t)))
                pi[idx] = pos[(na, nb)]
            perms.append(pi)
    elif family == "Paley":
        # translations x -> x + a
        for a in range(param):
            perms.append({x: (x + a) % param for x in range(param)})
    elif family in ("CP", "CMP", "multipartite"):
        parts = param["parts"]
        labels = []
        start = 0
        for sz in parts:
            labels.append(list(range(start, start + sz)))
            start += sz
        # adjacent-part swaps where sizes match
        for s in range(len(parts) - 1):
            if parts[s] == parts[s + 1]:
                pi = {}
                for t, part in enumerate(labels):
                    if t == s:
                        tgt = labels[s + 1]
                    elif t == s + 1:
                        tgt = labels[s]
                    else:
                        tgt = part
                    for j, v in enumerate(part):
                        pi[v] = tgt[j]
                perms.append(pi)
        # within-part cyclic shifts
        for s, part in enumerate(labels):
            if len(part) >= 2:
                pi = {}
                for t, q in enumerate(labels):
                    if t == s:
                        for j, v in enumerate(q):
                            pi[v] = q[(j + 1) % len(q)]
                    else:
                        for v in q:
                            pi[v] = v
                perms.append(pi)
    elif family == "compC5Km":
        m = param

        def idx(i, j, m=m):
            return i * m + j
        for rot in range(1, 5):
            pi = {}
            for i in range(5):
                for j in range(m):
                    pi[idx(i, j)] = idx((i + rot) % 5, j)
            perms.append(pi)
        if m >= 2:
            pi = {}
            for i in range(5):
                for j in range(m):
                    pi[idx(i, j)] = idx(i, (j + 1) % m)
            perms.append(pi)
    elif family == "CkK3":
        k = param

        def idx(i, j, k=k):
            return i * 3 + j
        for rot in range(1, k):
            pi = {}
            for i in range(k):
                for j in range(3):
                    pi[idx(i, j)] = idx((i + rot) % k, j)
            perms.append(pi)
        pi = {}
        for i in range(k):
            for j in range(3):
                pi[idx(i, j)] = idx(i, (j + 1) % 3)
        perms.append(pi)
    else:
        raise ValueError(family)
    # verify orbit of 0
    orbit = {0}
    frontier = {0}
    while frontier:
        nf = set()
        for pi in perms:
            for v in list(frontier):
                nf.add(pi[v])
                # inverse image
                inv = {vv: kk for kk, vv in pi.items()}
                nf.add(inv[v])
        frontier = nf - orbit
        orbit |= frontier
    ok_orbit = orbit == set(range(n))
    ok_perms = all(_perm_check(G, pi) for pi in perms)
    return {"orbit_full": ok_orbit, "perms_valid": ok_perms,
            "num_gens": len(perms)}


def lex_index_C5Km(i, j, m):
    return i * m + j


def build_all():
    A = {}

    for n in range(10, 17):
        A[f"T({n})"] = {"G": T(n), "family": "T", "param": n}
        A[f"KG({n},2)"] = {"G": nx.complement(T(n)), "family": "KG", "param": n}

    for q in (13, 17, 29, 37, 41, 53, 61, 73, 89, 97, 101):
        A[f"Paley({q})"] = {"G": paley(q), "family": "Paley", "param": q}

    for m in range(2, 9):
        A[f"CP({m})"] = {"G": nx.complete_multipartite_graph(*([2] * m)),
                         "family": "CP",
                         "param": {"parts": [2] * m}}
    for m in range(2, 9):
        parts = [2] * (m - 1) + [1]
        A[f"CMP({m})"] = {"G": nx.complete_multipartite_graph(*parts),
                          "family": "CMP",
                          "param": {"parts": parts}}
    for m in range(2, 9):
        base = nx.cycle_graph(5)
        H = lex_product(base, m)
        A[f"comp(C5[K{m}])"] = {"G": nx.complement(H), "family": "compC5Km",
                                "param": m}
    for k in (7, 9):
        H = lex_product(nx.cycle_graph(k), 3)
        A[f"C{k}[K3]"] = {"G": H, "family": "CkK3", "param": k}

    A["K(3,3)"] = {"G": nx.complete_multipartite_graph(3, 3),
                   "family": "multipartite", "param": {"parts": [3, 3]}}
    A["K(3,3,3)"] = {"G": nx.complete_multipartite_graph(3, 3, 3),
                     "family": "multipartite", "param": {"parts": [3, 3, 3]}}

    return A


if __name__ == "__main__":
    A = build_all()
    basic = {}
    with (CACHE / "arsenal.gpickle").open("wb") as f:
        pickle.dump({k: v["G"] for k, v in A.items()}, f)
    meta = {}
    for name, rec in A.items():
        G = rec["G"]
        degs = sorted(d for _, d in G.degree())
        vt = None
        try:
            vt = transitivity_witness(G, rec["family"], rec["param"])
        except Exception as e:
            vt = {"error": str(e)}
        meta[name] = {
            "family": rec["family"], "param": str(rec["param"]),
            "n": G.number_of_nodes(), "m": G.number_of_edges(),
            "delta": degs[0], "Delta": degs[-1],
            "regular": degs[0] == degs[-1],
            "vt": vt,
        }
        print(f"{name:18s} n={G.number_of_nodes():4d} m={G.number_of_edges():6d} "
              f"deg={degs[0]}..{degs[-1]} vt={vt.get('orbit_full')},{vt.get('perms_valid')}")
    (CACHE / "arsenal_meta.json").write_text(json.dumps(meta, indent=1))
    print(f"{len(A)} graphs")
