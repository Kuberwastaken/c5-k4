"""Lite invariant battery over the DB-sanity corpus (atlas connected n<=7 +
named calibration graphs). Results cached to cache/cert_sanity/."""
import json
import pickle
import sys
import time
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import invlib as iv
import certify as C

SAN = HERE.parent / "cache" / "cert_sanity"
SAN.mkdir(parents=True, exist_ok=True)


def build_sanity_corpus():
    Gs = {}
    for g in nx.graph_atlas_g():
        n = g.number_of_nodes()
        if 2 <= n <= 7 and nx.is_connected(g):
            key = f"atlas{g.graph.get('index', len(Gs))}"
            Gs[key] = nx.convert_node_labels_to_integers(g)
    for k in range(5, 10):
        Gs[f"C{k}"] = nx.cycle_graph(k)
    Gs["P7"] = nx.path_graph(7)
    Gs["Petersen"] = nx.petersen_graph()
    Gs["K3,3"] = nx.complete_bipartite_graph(3, 3)
    Gs["K7"] = nx.complete_graph(7)
    for k in range(3, 8):
        Gs[f"K1,{k}"] = nx.star_graph(k)
    for (a, b) in ((2, 3), (2, 4)):
        Gs[f"K{a},{b}"] = nx.complete_bipartite_graph(a, b)
    Gs["K(2,2)"] = nx.complete_multipartite_graph(2, 2)
    Gs["K(2,2,2)"] = nx.complete_multipartite_graph(2, 2, 2)
    Gs["K(3,3)mp"] = nx.complete_multipartite_graph(3, 3)
    import build_arsenal as BA
    Gs["C5[K2]"] = BA.lex_product(nx.cycle_graph(5), 2)
    Gs["C5[K3]"] = BA.lex_product(nx.cycle_graph(5), 3)
    return Gs


def main():
    # lite mode: skip expensive searches irrelevant to gate decisions
    iv.well_total_dominated_search = lambda *a, **k: {"found": False}
    orig_ham = iv.ham_path_search
    iv.ham_path_search = lambda G, **k: orig_ham(G, restarts=30,
                                                 backtrack_budget=20000)
    Gs = build_sanity_corpus()
    print(f"{len(Gs)} sanity graphs", flush=True)
    for name, G in Gs.items():
        out = SAN / (name.replace("/", "_").replace("(", "_")
                     .replace(")", "").replace(",", "_").replace("[", "_")
                     .replace("]", "") + ".json")
        if out.exists():
            continue
        t0 = time.time()
        try:
            rec = C.certify(name, G)
            rec.pop("wtd_search", None)
            out.write_text(json.dumps(rec, indent=1, default=str))
            print(f"done {name} {time.time()-t0:.1f}s", flush=True)
        except Exception as e:
            print(f"FAILED {name}: {e!r}", flush=True)


if __name__ == "__main__":
    main()
