#!/usr/bin/env python3
"""Frozen second prospective WOWII 19 trial: graph squares of equality seeds."""

import importlib.util
import json
from pathlib import Path

import networkx as nx


SEEDS = [
    ("substitute_0_3_0", "D~{"), ("substitute_0_3_2", "Ds{"),
    ("substitute_0_0_0", "E~~w"), ("substitute_0_0_1", "E~z_"),
    ("substitute_0_1_1", "E?~w"), ("substitute_1_3_0", "Fj[{G"),
    ("substitute_1_3_1", "FiO{G"), ("blocks_(3, 5)_path_False", "G{CGGc"),
    ("substitute_1_1_0", "G~{GNc"), ("substitute_1_1_1", "G?{GNc"),
    ("substitute_3_3_0", "I{CWw[@CG"), ("substitute_3_3_1", "I{CO_[@CG"),
    ("substitute_1_0_0", "Jz\\ww{^F{F_"), ("substitute_1_0_1", "JzX_w{^F{F_"),
    ("substitute_3_1_0", "J~~~_C@?GC_"), ("substitute_3_1_1", "J?~~_C@?GC_"),
    ("substitute_1_2_0", "Mz\\ww{^F{Fo^_~_~_"),
    ("substitute_1_2_1", "MzX_w{^F{Fo]_{_{?"),
    ("substitute_3_0_0", "S~~{CEB_wF_@?B?@_?w?N?{[BpwFbwFb{"),
    ("substitute_0_3_0_surgery_0", "Dn{"), ("substitute_0_3_0_surgery_1", "D~k"),
    ("substitute_0_3_0_surgery_2", "D~w"), ("substitute_0_3_2_surgery_0", "Do{"),
    ("substitute_0_3_2_surgery_1", "Du{"), ("substitute_0_3_2_surgery_2", "Ds["),
    ("substitute_0_0_0_surgery_0", "E~nw"), ("substitute_0_0_0_surgery_1", "E~}w"),
    ("substitute_0_0_0_surgery_2", "En~w"), ("substitute_0_0_1_surgery_0", "E~~_"),
    ("substitute_0_0_1_surgery_1", "E}z_"), ("substitute_0_0_1_surgery_2", "E|z_"),
    ("substitute_0_0_2_surgery_0", "E~r_"), ("substitute_0_0_2_surgery_1", "EvZ_"),
    ("substitute_0_1_1_surgery_0", "EG~w"),
    ("blocks_(3, 5)_path_True_surgery_0", "F{C[?"),
    ("substitute_1_3_0_surgery_2", "Fb[}G"),
    ("substitute_1_3_1_surgery_0", "FgP{G"),
    ("substitute_1_3_1_surgery_1", "FiO}G"),
    ("blocks_(3, 5)_path_False_surgery_2", "G{SGGc"),
    ("substitute_1_1_0_surgery_0", "G~{KN_"),
    ("substitute_1_1_0_surgery_1", "G~{?Nc"),
    ("substitute_1_1_0_surgery_2", "G^{KNc"),
    ("blocks_(3, 7)_path_True_surgery_1", "H}?GGE@"),
    ("substitute_2_1_0_surgery_1", "I~{?GC@}G"),
    ("substitute_3_3_0_surgery_2", "I{CWg[HCG"),
    ("substitute_3_3_1_surgery_1", "I{CO_WBCG"),
    ("substitute_3_3_1_surgery_2", "I{CO_[BCG"),
    ("substitute_1_0_0_surgery_0", "Jz\\xww^F{F_"),
    ("substitute_1_0_0_surgery_1", "Jy\\ww{^F|F_"),
    ("substitute_3_1_0_surgery_0", "J~~}_C@?GC_"),
    ("substitute_3_1_1_surgery_0", "J?z~_C@CGC_"),
    ("substitute_3_1_1_surgery_1", "J?~~_c??GC_"),
    ("substitute_1_2_0_surgery_0", "Mz\\yw{^F[Fo^_~_~_"),
    ("substitute_1_2_0_surgery_1", "Mz|wg{^F{Fo^_~_~_"),
    ("substitute_1_2_0_surgery_2", "Mz\\ww{^F{Fs^_~_~_"),
    ("substitute_1_2_1_surgery_1", "MzX?w{^F|Fo]_{_{?"),
]


def evaluator_module():
    path = Path(__file__).with_name("prospective_wowii19_new_discovery.py")
    spec = importlib.util.spec_from_file_location("wowii19_first_trial", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def decode(graph6):
    return nx.convert_node_labels_to_integers(nx.from_graph6_bytes(graph6.encode()))


def distinct_squares():
    representatives = []
    for name, graph6 in SEEDS:
        graph = decode(graph6)
        square = nx.power(graph, 2)
        fingerprint = (len(square), square.number_of_edges(), nx.weisfeiler_lehman_graph_hash(square))
        duplicate = None
        for old_name, old_square, old_fingerprint, aliases in representatives:
            if fingerprint == old_fingerprint and nx.is_isomorphic(square, old_square):
                duplicate = aliases
                break
        if duplicate is not None:
            duplicate.append(name)
        else:
            representatives.append((name, square, fingerprint, [name]))
    return representatives


def main():
    evaluator = evaluator_module()
    outputs, timeouts = [], 0
    squares = distinct_squares()
    for name, graph, _, aliases in squares:
        try:
            result = evaluator.evaluate(
                f"square_of_{name}", graph,
                {"transformation": "graph_square", "seed_aliases": aliases},
            )
        except TimeoutError:
            timeouts += 1
            outputs.append({"name": f"square_of_{name}", "status": "TIMEOUT", "n": len(graph)})
            continue
        outputs.append(result)
    outputs.sort(key=lambda row: (row.get("slack", 999), row["n"], row["name"]))
    print(json.dumps({"summary": {
        "seed_rows": len(SEEDS), "distinct_squares": len(squares),
        "crossings": sum(row.get("slack", 0) < 0 for row in outputs),
        "timeouts": timeouts,
    }}))
    for row in outputs:
        print(json.dumps(row))


if __name__ == "__main__":
    main()
