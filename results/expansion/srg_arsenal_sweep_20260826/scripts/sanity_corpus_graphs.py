"""Deterministic reconstruction of the DB-sanity corpus graphs by name
(mirrors certify_sanity.build_sanity_corpus keys)."""
import networkx as nx

_CACHE = {}


def get_graph(name):
    if name in _CACHE:
        return _CACHE[name]
    G = None
    if name.startswith("atlas"):
        idx = int(name[len("atlas"):])
        for g in nx.graph_atlas_g():
            if g.number_of_nodes() >= 2 and nx.is_connected(g) and \
                    g.graph.get("index", idx) == idx:
                G = nx.convert_node_labels_to_integers(g)
                break
        if G is None:
            # fall back: index-th entry of atlas among connected 2..7
            conn = [g for g in nx.graph_atlas_g()
                    if 2 <= g.number_of_nodes() <= 7 and nx.is_connected(g)]
            G = nx.convert_node_labels_to_integers(conn[idx])
    elif name.startswith("C") and name[1].isdigit() and "[" not in name:
        G = nx.cycle_graph(int(name[1:]))
    elif name == "P7":
        G = nx.path_graph(7)
    elif name == "Petersen":
        G = nx.petersen_graph()
    elif name == "K3,3":
        G = nx.complete_bipartite_graph(3, 3)
    elif name == "K7":
        G = nx.complete_graph(7)
    elif name.startswith("K1,"):
        G = nx.star_graph(int(name[3:]))
    elif name == "K2,3":
        G = nx.complete_bipartite_graph(2, 3)
    elif name == "K2,4":
        G = nx.complete_bipartite_graph(2, 4)
    elif name == "K(2,2)":
        G = nx.complete_multipartite_graph(2, 2)
    elif name == "K(2,2,2)":
        G = nx.complete_multipartite_graph(2, 2, 2)
    elif name == "K(3,3)mp" or name == "K3,3mp":
        G = nx.complete_multipartite_graph(3, 3)
    else:
        raise KeyError(f"unknown sanity graph {name}")
    _CACHE[name] = G
    return G
