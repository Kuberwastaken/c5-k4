#!/usr/bin/env python3
"""Frozen reverse-orientation Petersen-splice switch trial."""

from __future__ import annotations

import importlib.util
import json
import time
from pathlib import Path

import networkx as nx


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "results/expansion/prospective_alon_tarsi_petersen_reverse_switch_ledger.jsonl"
BASE_SCRIPT = ROOT / "scripts/prospective_alon_tarsi_petersen_splice_switch.py"
SPEC = importlib.util.spec_from_file_location("alon_tarsi_base", BASE_SCRIPT)
assert SPEC is not None and SPEC.loader is not None
BASE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BASE)


def emit(record: dict) -> None:
    with LEDGER.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")
        handle.flush()


def gate() -> None:
    for graph, expected in [(nx.cycle_graph(n), n) for n in (3, 4, 5)] + [
        (nx.petersen_graph(), 21)
    ]:
        exact, _, _ = BASE.minimum_cycle_cover_milp(graph)
        assert exact == expected == BASE.minimum_cycle_cover_dp(graph)
    carrier = BASE.petersen_splice()
    BASE.assert_premises(carrier)
    exact, cycle_count, _ = BASE.minimum_cycle_cover_milp(carrier)
    assert exact == 42
    atlas_checked = 0
    for graph in nx.graph_atlas_g():
        if not (2 <= graph.number_of_nodes() <= 6):
            continue
        if graph.number_of_edges() == 0 or not nx.is_connected(graph):
            continue
        if list(nx.bridges(graph)):
            continue
        exact, _, _ = BASE.minimum_cycle_cover_milp(graph)
        assert exact == BASE.minimum_cycle_cover_dp(graph)
        assert 5 * exact <= 7 * graph.number_of_edges()
        atlas_checked += 1
    emit(
        {
            "event": "database_gate_passed",
            "atlas_checked": atlas_checked,
            "petersen_tau": 21,
            "carrier_edges": 30,
            "carrier_tau": 42,
            "carrier_cycle_count": cycle_count,
        }
    )


def labelled_candidates(carrier: nx.Graph):
    forbidden = {BASE.edge(0, 10), BASE.edge(1, 11)}
    internal = sorted(
        BASE.edge(u, v)
        for u, v in carrier.edges()
        if BASE.edge(u, v) not in forbidden and not ({u, v} & {0, 10})
    )
    for u, v in internal:
        new_edges = (BASE.edge(0, v), BASE.edge(10, u))
        graph = carrier.copy()
        graph.remove_edges_from([(0, 10), (u, v)])
        if new_edges[0] == new_edges[1] or any(graph.has_edge(*e) for e in new_edges):
            continue
        graph.add_edges_from(new_edges)
        if nx.is_connected(graph) and not list(nx.bridges(graph)):
            yield (u, v), new_edges, graph


def main() -> None:
    started = time.monotonic()
    gate()
    labelled = list(labelled_candidates(BASE.petersen_splice()))
    representatives: list[tuple[tuple[int, int], nx.Graph]] = []
    assignments = []
    for old_edge, new_edges, graph in labelled:
        representative_id = None
        for candidate_id, representative in representatives:
            if nx.is_isomorphic(graph, representative):
                representative_id = candidate_id
                break
        if representative_id is None:
            representative_id = old_edge
            representatives.append((representative_id, graph))
        assignments.append((old_edge, new_edges, graph, representative_id))

    values = {}
    for representative_id, graph in representatives:
        exact, cycle_count, status = BASE.minimum_cycle_cover_milp(graph)
        values[representative_id] = (exact, cycle_count, status)

    crossings = 0
    for old_edge, new_edges, graph, representative_id in assignments:
        exact, cycle_count, status = values[representative_id]
        residual = 5 * exact - 7 * graph.number_of_edges()
        record = {
            "event": "candidate",
            "id": f"reverse_switch_{old_edge[0]}_{old_edge[1]}",
            "representative_id": f"reverse_switch_{representative_id[0]}_{representative_id[1]}",
            "deleted": [[0, 10], list(old_edge)],
            "added": [list(new_edges[0]), list(new_edges[1])],
            "nodes": graph.number_of_nodes(),
            "edges": graph.number_of_edges(),
            "bridgeless": True,
            "cycle_count_of_representative": cycle_count,
            "tau": exact,
            "cleared_residual": residual,
            "solver": "scipy_highs_milp_on_exact_isomorphism_representative",
            "solver_status": status,
        }
        if residual > 0:
            oracle = BASE.independent_branch_and_bound(graph)
            record["independent_tau"] = oracle
            record["oracle_agrees"] = oracle == exact
            if oracle != exact:
                emit(record)
                raise RuntimeError("crossing oracle mismatch")
            crossings += 1
        emit(record)
    emit(
        {
            "event": "trial_complete",
            "labelled_retained": len(assignments),
            "isomorphism_classes": len(representatives),
            "crossings": crossings,
            "elapsed_seconds": round(time.monotonic() - started, 6),
        }
    )
    print(
        json.dumps(
            {
                "labelled_retained": len(assignments),
                "isomorphism_classes": len(representatives),
                "crossings": crossings,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
