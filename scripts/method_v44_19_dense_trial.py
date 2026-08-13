#!/usr/bin/env python3
"""Exact frozen dense/symmetric trial for current DeepMind WOWII 19."""

import argparse
import itertools
import json
from fractions import Fraction

import networkx as nx


def alpha_with_witness(G, vertices):
    vs = list(vertices)
    for k in range(len(vs), -1, -1):
        for S in itertools.combinations(vs, k):
            if all(not G.has_edge(u, v) for u, v in itertools.combinations(S, 2)):
                return k, list(S)
    raise AssertionError


def bipartite_number(G):
    vs = list(G)
    for k in range(len(vs), -1, -1):
        for S in itertools.combinations(vs, k):
            H = G.subgraph(S)
            if nx.is_bipartite(H):
                colors = nx.bipartite.color(H) if S else {}
                return k, list(S), colors
    raise AssertionError


def profile(G, name):
    G = nx.convert_node_labels_to_integers(G)
    if len(G) < 2 or not nx.is_connected(G):
        return None
    ecc = nx.eccentricity(G)
    local = []
    for v in G:
        a, W = alpha_with_witness(G, G.neighbors(v))
        local.append((a, v, W))
    lam, lv, lW = max(local)
    b, bW, colors = bipartite_number(G)
    avg = Fraction(sum(ecc.values()), len(G))
    floor_avg = avg.numerator // avg.denominator
    rhs = lam + floor_avg
    return {
        "name": name, "n": len(G), "m": G.number_of_edges(),
        "graph6": nx.to_graph6_bytes(G, header=False).decode().strip(),
        "edges": [list(e) for e in sorted(G.edges())],
        "eccentricities": [ecc[v] for v in G], "sumEcc": sum(ecc.values()),
        "avgEcc": f"{avg.numerator}/{avg.denominator}", "floorAvgEcc": floor_avg,
        "maxLocalAlpha": lam, "localAlphaVertex": lv,
        "localAlphaWitness": lW, "b": b, "bWitness": bW,
        "bColoring": {str(v): colors[v] for v in colors},
        "rhs": rhs, "residual": b-rhs, "crossing": b < rhs,
    }


class Unique:
    def __init__(self):
        self.buckets = {}
        self.keys = set()

    def add(self, name, G):
        G = nx.convert_node_labels_to_integers(G)
        certificate = nx.to_graph6_bytes(G, header=False).decode().strip()
        key = (len(G), G.number_of_edges(), nx.weisfeiler_lehman_graph_hash(G),
               tuple(sorted(dict(G.degree()).values())), certificate)
        if key in self.keys:
            return False
        self.keys.add(key)
        bucket_key = key[:3]
        bucket = self.buckets.setdefault(bucket_key, [])
        bucket.append((name, G.copy()))
        return True

    def items(self):
        for bucket in self.buckets.values():
            yield from bucket


def lex_blowup(H, sizes, clique):
    G = nx.Graph()
    bags = {}
    at = 0
    for v, s in zip(H.nodes(), sizes):
        bags[v] = list(range(at, at+s)); at += s
        if clique:
            G.add_edges_from(itertools.combinations(bags[v], 2))
        else:
            G.add_nodes_from(bags[v])
    for u, v in H.edges():
        G.add_edges_from(itertools.product(bags[u], bags[v]))
    return G


def named_bases():
    out = []
    for n in range(2, 9):
        out += [(f"P{n}", nx.path_graph(n)), (f"C{n}", nx.cycle_graph(n)),
                (f"K{n}", nx.complete_graph(n))]
    for a in range(1, 6):
        for b in range(a, 7):
            out.append((f"K{a},{b}", nx.complete_bipartite_graph(a, b)))
    for n in range(4, 9): out.append((f"W{n}", nx.wheel_graph(n)))
    out.append(("Petersen", nx.petersen_graph()))
    out.append(("diamond", nx.complete_graph(4)))
    out[-1][1].remove_edge(0, 1)
    return out


def frozen_bases():
    U = Unique()
    named = named_bases()
    # Named line graphs.
    for name, H in named:
        L = nx.line_graph(H)
        if 2 <= len(L) <= 14 and nx.is_connected(L): U.add(f"line:{name}", L)
    # Connected Atlas line graphs.
    for i, H in enumerate(nx.graph_atlas_g()):
        if len(H) >= 2 and nx.is_connected(H):
            L = nx.line_graph(H)
            if 2 <= len(L) <= 14 and nx.is_connected(L): U.add(f"line:atlas:{i}", L)
    # Complements of named bases and current line outputs.
    comp_sources = named + list(U.items())
    for name, H in comp_sources:
        C = nx.complement(H)
        if 2 <= len(C) <= 14 and nx.is_connected(C): U.add(f"complement:{name}", C)
    # Uniform and nonuniform blow-ups.
    quotients = [(f"P{n}", nx.path_graph(n)) for n in range(3, 6)]
    quotients += [(f"C{n}", nx.cycle_graph(n)) for n in range(3, 7)]
    quotients += [("claw", nx.star_graph(3)), ("diamond", named[-1][1])]
    for name, H in quotients:
        for m in range(2, 5):
            for clique in (False, True):
                G = lex_blowup(H, [m]*len(H), clique)
                if len(G) <= 14: U.add(f"blowup:{name}:{'K' if clique else 'E'}{m}", G)
        if name.startswith(("P", "C")):
            for sizes in itertools.product((1, 2, 3), repeat=len(H)):
                if sum(sizes) > 14 or len(set(sizes)) == 1: continue
                for clique in (False, True):
                    U.add(f"weighted:{name}:{sizes}:{'K' if clique else 'E'}", lex_blowup(H, sizes, clique))
    # Joins.
    join_parts = []
    for n in range(1, 6):
        join_parts += [(f"K{n}", nx.complete_graph(n)), (f"E{n}", nx.empty_graph(n))]
        if n >= 2: join_parts.append((f"P{n}", nx.path_graph(n)))
        if n >= 3: join_parts.append((f"C{n}", nx.cycle_graph(n)))
    for i, (an, A) in enumerate(join_parts):
        for bn, B in join_parts[i:]:
            if len(A)+len(B) <= 12:
                U.add(f"join:{an}:{bn}", nx.full_join(A, B, rename=("A-", "B-")))
    return U


def atlas_gate():
    rows=[]
    for i,G in enumerate(nx.graph_atlas_g()):
        if 2 <= len(G) <= 7 and nx.is_connected(G): rows.append(profile(G,f"atlas:{i}"))
    rows.sort(key=lambda p:(p["residual"],p["n"],p["m"]))
    return {"event":"atlas_gate","connected":len(rows),
            "crossings":[p for p in rows if p["crossing"]],
            "tight_count":sum(p["residual"]==0 for p in rows),"closest":rows[:12]}


def controls():
    gs=[("K5",nx.complete_graph(5)),("C5",nx.cycle_graph(5)),
        ("C6",nx.cycle_graph(6)),("K3,4",nx.complete_bipartite_graph(3,4)),
        ("Petersen",nx.petersen_graph())]
    for m in (2,):
        gs.append((f"C5[K{m}]",lex_blowup(nx.cycle_graph(5),[m]*5,True)))
    return [profile(G,n) for n,G in gs]


def family_run():
    U=frozen_bases(); seeds=list(U.items())
    # Canonical one-edge perturbations of the frozen named outputs.
    capped = False
    for name,G in seeds:
        for u,v in list(G.edges()):
            if len(U.keys) >= 8000:
                capped = True; break
            H=G.copy(); H.remove_edge(u,v)
            if nx.is_connected(H): U.add(f"delete:{name}:{u}-{v}",H)
        if capped: break
        missing=list(nx.non_edges(G))
        for u,v in missing:
            if len(U.keys) >= 8000:
                capped = True; break
            H=G.copy(); H.add_edge(u,v); U.add(f"add:{name}:{u}-{v}",H)
        if capped: break
    rows=[]; generated=0
    for name,G in U.items():
        generated+=1
        if generated>8000 or len(rows)>=2000: break
        if 2<=len(G)<=14 and nx.is_connected(G): rows.append(profile(G,name))
    rows.sort(key=lambda p:(p["residual"],p["n"],p["m"]))
    return {"event":"family_result","generated_unique":len(U.keys),
            "exact":len(rows),"crossings":[p for p in rows if p["crossing"]],
            "tight_count":sum(p["residual"]==0 for p in rows),"closest":rows[:20]}


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("mode",choices=("atlas","family")); a=ap.parse_args()
    print(json.dumps({"controls":controls(),**(atlas_gate() if a.mode=="atlas" else family_run())},sort_keys=True))


if __name__=="__main__": main()
