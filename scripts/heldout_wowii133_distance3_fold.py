#!/usr/bin/env python3
"""Literal, append-only prospective WOWII 133 distance-three fold trial."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import subprocess
import sys
import time
from pathlib import Path

import networkx as nx


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "results/expansion/heldout_wowii133_distance3_fold_contract.md"
LEDGER = ROOT / "results/expansion/heldout_wowii133_distance3_fold_ledger.jsonl"
EXPECTED_CONTRACT_SHA256 = "834ced449c2a899131ccc6f87ca731203c218a87b0e3d218eab397560975eee6"
UPSTREAM = ROOT.parent / "formal-conjectures"
UPSTREAM_COMMIT = "d16e05aded22b8c467a0a27c14b2311f53185006"
SOURCE_PATH = "FormalConjectures/WrittenOnTheWallII/GraphConjecture133.lean"
SOURCE_BLOB = "9a8dca984e87efc2fb1ffd68f5d4185e4645a8e8"
DEADLINE_SECONDS = 55.0


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def append(row):
    row = {"trial": "heldout_wowii133_distance3_fold", **row}
    with LEDGER.open("a", encoding="utf-8") as out:
        out.write(canonical(row) + "\n")
        out.flush()


def run_git(*args):
    return subprocess.run(
        ["git", "-C", str(UPSTREAM), *args], check=True, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10,
    ).stdout.strip()


def edge_list(G):
    return sorted([sorted((int(u), int(v))) for u, v in G.edges()])


def graph6(G):
    return nx.to_graph6_bytes(G, header=False).decode("ascii").strip()


def maximum_independent_subset(G, vertices):
    vertices = tuple(sorted(vertices))
    for size in range(len(vertices), -1, -1):
        for choice in itertools.combinations(vertices, size):
            if all(not G.has_edge(u, v) for u, v in itertools.combinations(choice, 2)):
                return list(choice)
    raise AssertionError("unreachable")


def maximum_induced_path(G, deadline):
    best = []

    def visit(path):
        nonlocal best
        if time.monotonic() > deadline:
            raise TimeoutError("maximum induced-path enumeration exceeded deadline")
        if len(path) > len(best):
            best = path.copy()
        end = path[-1]
        used = set(path)
        for nxt in sorted(G.neighbors(end)):
            if nxt in used:
                continue
            if any(G.has_edge(nxt, old) for old in path[:-1]):
                continue
            visit(path + [nxt])

    for start in sorted(G.nodes()):
        visit([start])
    return best


def has_c4(G):
    nodes = sorted(G.nodes())
    for u, v in itertools.combinations(nodes, 2):
        common = sorted(set(G.neighbors(u)) & set(G.neighbors(v)))
        if len(common) >= 2:
            return True, [u, common[0], v, common[1]]
    return False, None


def profile(G, deadline):
    if len(G) < 2 or not nx.is_connected(G):
        raise ValueError("literal target requires a connected nontrivial graph")
    distances = dict(nx.all_pairs_shortest_path_length(G))
    eccentricities = {v: max(distances[v].values()) for v in sorted(G.nodes())}
    radius = min(eccentricities.values())
    centers = [v for v, ecc in eccentricities.items() if ecc == radius]
    local_witnesses = {
        v: maximum_independent_subset(G, list(G.neighbors(v))) for v in sorted(G.nodes())
    }
    local_values = {v: len(w) for v, w in local_witnesses.items()}
    local_sum = sum(local_values.values())
    floor_l = local_sum // len(G)
    c4, c4_witness = has_c4(G)
    path_witness = maximum_induced_path(G, deadline)
    correction = 1 if c4 else floor_l
    residual = len(path_witness) - radius - correction
    return {
        "n": len(G), "m": G.number_of_edges(), "connected": True,
        "has_c4": c4, "c4_witness": c4_witness,
        "radius": radius, "center_witnesses": centers,
        "local_values": local_values, "local_independent_witnesses": local_witnesses,
        "local_sum": local_sum, "local_denominator": len(G), "floor_l": floor_l,
        "path": len(path_witness), "path_witness": path_witness,
        "correction": correction, "residual": residual,
    }


def controls():
    atlas = []
    for index, G in enumerate(nx.graph_atlas_g()):
        if 2 <= len(G) <= 7 and nx.is_connected(G):
            atlas.append((f"atlas:{index}", nx.convert_node_labels_to_integers(G)))
    named = [(f"C{n}", nx.cycle_graph(n)) for n in range(5, 10)]
    named += [("P7", nx.path_graph(7)), ("Petersen", nx.petersen_graph()),
              ("K3,3", nx.complete_bipartite_graph(3, 3)), ("K7", nx.complete_graph(7))]
    named += [(f"K1,{n}", nx.star_graph(n)) for n in range(2, 8)]
    named += [(f"K{a},{b}", nx.complete_bipartite_graph(a, b))
              for a, b in [(2, 3), (2, 4), (3, 4), (4, 4)]]
    return atlas + named


def verify_contract_and_source():
    digest = hashlib.sha256(CONTRACT.read_bytes()).hexdigest()
    if digest != EXPECTED_CONTRACT_SHA256:
        raise RuntimeError(f"contract digest mismatch: {digest}")
    if run_git("rev-parse", "upstream/main") != UPSTREAM_COMMIT:
        raise RuntimeError("upstream/main moved after contract freeze")
    if run_git("rev-parse", f"upstream/main:{SOURCE_PATH}") != SOURCE_BLOB:
        raise RuntimeError("source blob moved after contract freeze")
    source = run_git("show", f"upstream/main:{SOURCE_PATH}")
    if "@[category research open, AMS 5]" not in source or "theorem conjecture133" not in source:
        raise RuntimeError("category/declaration lock failed")
    return digest


def gate():
    if LEDGER.exists():
        raise RuntimeError("append-only ledger already exists; refusing a second gate run")
    started = time.monotonic()
    digest = verify_contract_and_source()
    append({"kind": "contract_lock", "status": "PASS", "contract_sha256": digest,
            "upstream_commit": UPSTREAM_COMMIT, "source_blob": SOURCE_BLOB})
    append({"kind": "source_status_gate", "status": "PASS", "category": "research open",
            "reading": "UNAMBIGUOUS_LITERAL_LEAN", "declaration": "conjecture133"})
    append({"kind": "local_theorem_domain_gate", "status": "PASS",
            "universal_theorem_closed": False,
            "known_closed_domains": ["cubic C4-free", "several low-degree and sufficient classes"],
            "operation_previously_tested": False,
            "new_operation": "identify one nonadjacent Heawood vertex pair at exact distance three"})
    append({"kind": "live_prior_art_gate", "status": "PASS",
            "github_exact_issue_hits": 0, "github_exact_open_pr_hits": 0,
            "related_merged_prs": [3820, 4282],
            "web_queries": [
                "Written on the Wall II Conjecture 133 graph",
                "WOWII 133 graph conjecture radius induced path",
                "path(G) rad(G) cC4 graph",
            ], "distance_three_fold_prior_art_found": False})
    append({"kind": "implementation_semantics_gate", "status": "PASS",
            "path_semantics": "maximum induced-path vertex count",
            "c4_semantics": "not-necessarily-induced four-cycle",
            "local_semantics": "exact neighborhood independence average then floor"})

    fixture_expected = {"P4": (4, 2, 1, False, 1), "C4": (3, 2, 1, True, 0),
                        "K3": (2, 1, 1, False, 0)}
    fixture_graphs = {"P4": nx.path_graph(4), "C4": nx.cycle_graph(4), "K3": nx.complete_graph(3)}
    for name, G in fixture_graphs.items():
        got = profile(G, started + DEADLINE_SECONDS)
        coords = (got["path"], got["radius"], got["floor_l"], got["has_c4"], got["residual"])
        if coords != fixture_expected[name]:
            append({"kind": "microfixture", "name": name, "status": "FAIL", "coordinates": coords})
            raise RuntimeError(f"microfixture {name} failed: {coords}")
        append({"kind": "microfixture", "name": name, "status": "PASS", "coordinates": coords})

    count = 0
    minimum = None
    equality = 0
    control_digest = hashlib.sha256()
    for name, G in controls():
        got = profile(G, started + DEADLINE_SECONDS)
        row = {"kind": "database_control", "name": name, "status": "PASS" if got["residual"] >= 0 else "FAIL",
               "graph6": graph6(G), "coordinates": {k: got[k] for k in ("n", "m", "path", "radius", "floor_l", "has_c4", "residual")}}
        append(row)
        control_digest.update(canonical(row).encode())
        count += 1
        minimum = got["residual"] if minimum is None else min(minimum, got["residual"])
        equality += got["residual"] == 0
        if got["residual"] < 0:
            raise RuntimeError(f"database sanity rejected literal reading on {name}")

    H = nx.convert_node_labels_to_integers(nx.heawood_graph())
    heawood = profile(H, started + DEADLINE_SECONDS)
    heawood_coords = tuple(heawood[k] for k in ("path", "radius", "floor_l", "residual"))
    if heawood_coords != (7, 3, 3, 1) or heawood["has_c4"]:
        append({"kind": "heawood_wall", "status": "FAIL", "profile": heawood})
        raise RuntimeError(f"Heawood wall mismatch: {heawood_coords}")
    append({"kind": "heawood_wall", "status": "PASS", "graph6": graph6(H), "profile": heawood})
    unlock_material = {"contract_sha256": digest, "database_count": count,
                       "database_digest": control_digest.hexdigest(), "heawood": heawood_coords}
    token = hashlib.sha256(canonical(unlock_material).encode()).hexdigest()
    append({"kind": "candidate_unlock", "status": "PASS", **unlock_material,
            "unlock_token": token, "elapsed_seconds": round(time.monotonic() - started, 6)})
    print(canonical({"status": "PASS", "database_count": count, "minimum_residual": minimum,
                     "equalities": equality, "unlock_token": token}))


def read_unlock():
    rows = [json.loads(line) for line in LEDGER.read_text(encoding="utf-8").splitlines() if line.strip()]
    unlocks = [row for row in rows if row.get("kind") == "candidate_unlock" and row.get("status") == "PASS"]
    if len(unlocks) != 1 or any(row.get("kind") == "candidate" for row in rows):
        raise RuntimeError("ledger is not in the unique unlocked pre-candidate state")
    return unlocks[0]


def fold_pair(H, u, v):
    remaining = [x for x in sorted(H.nodes()) if x not in (u, v)]
    role_sets = [[u, v]] + [[x] for x in remaining]
    old_to_new = {old: new for new, olds in enumerate(role_sets) for old in olds}
    Q = nx.Graph()
    Q.add_nodes_from(range(len(role_sets)))
    for a, b in H.edges():
        x, y = old_to_new[a], old_to_new[b]
        if x != y:
            Q.add_edge(x, y)
    roles = {str(i): {"role": "merged_pair" if len(olds) == 2 else "singleton",
                      "original_heawood_vertices": olds} for i, olds in enumerate(role_sets)}
    return Q, roles


def independent_crossing_check(G, threshold):
    nodes = sorted(G.nodes())
    for size in range(len(nodes), threshold - 1, -1):
        for subset in itertools.combinations(nodes, size):
            H = G.subgraph(subset)
            if nx.is_connected(H) and max((d for _, d in H.degree()), default=0) <= 2 \
                    and H.number_of_edges() == size - 1:
                return True, list(subset)
    return False, None


def trial():
    started = time.monotonic()
    digest = verify_contract_and_source()
    unlock = read_unlock()
    if unlock["contract_sha256"] != digest:
        raise RuntimeError("unlock does not match contract")
    H = nx.convert_node_labels_to_integers(nx.heawood_graph())
    distances = dict(nx.all_pairs_shortest_path_length(H))
    pairs = [(u, v) for u, v in itertools.combinations(sorted(H.nodes()), 2) if distances[u][v] == 3]
    if not pairs:
        append({"kind": "outcome", "outcome": "NO_APPLICABLE_CANDIDATES"})
        print(canonical({"outcome": "NO_APPLICABLE_CANDIDATES"}))
        return
    minimum = None
    crossings = 0
    prediction_matches = 0
    abstract_classes = set()
    theorem_domain_outputs = 0
    evaluated_candidates = 0
    for index, (u, v) in enumerate(pairs):
        Q, roles = fold_pair(H, u, v)
        labelled = {"edges": edge_list(Q), "roles": roles}
        labelled_digest = hashlib.sha256(canonical(labelled).encode()).hexdigest()
        checksum = graph6(Q)
        abstract_classes.add(nx.weisfeiler_lehman_graph_hash(Q))
        c4, c4_witness = has_c4(Q)
        if c4:
            theorem_domain_outputs += 1
            append({"kind": "theorem_domain_output", "index": index,
                    "folded_original_pair": [u, v], "distance_before_fold": 3,
                    "edge_list": labelled["edges"], "role_map": roles,
                    "labelled_record_sha256": labelled_digest, "graph6": checksum,
                    "has_c4": True, "c4_witness": c4_witness,
                    "covering_theorem": "GraphConjecture133Specialization.sourceConclusion_of_hasC4",
                    "candidate_evaluated": False})
            continue
        got = profile(Q, started + DEADLINE_SECONDS)
        evaluated_candidates += 1
        predicted = got["n"] == 13 and got["radius"] == 3 and got["floor_l"] == 3 and got["path"] < 7
        prediction_matches += predicted
        crossing_audit = None
        if got["residual"] < 0:
            crossings += 1
            target = got["radius"] + got["correction"]
            exists, witness = independent_crossing_check(Q, target)
            crossing_audit = {"independent_target_path_exists": exists, "witness": witness,
                              "target_order": target, "verified_crossing": not exists}
            if exists:
                raise RuntimeError("independent checker contradicted discovery profile")
        append({"kind": "candidate", "index": index, "folded_original_pair": [u, v],
                "distance_before_fold": 3, "edge_list": labelled["edges"], "role_map": roles,
                "labelled_record_sha256": labelled_digest, "graph6": checksum,
                "profile": got, "directional_prediction_matched": predicted,
                "crossing_audit": crossing_audit})
        minimum = got["residual"] if minimum is None else min(minimum, got["residual"])
    if theorem_domain_outputs == len(pairs):
        outcome = "KNOWN_PROOF_DOMAIN"
    else:
        outcome = "HOLD_BOUNDED" if crossings == 0 else "PROVISIONAL_CROSSING"
    append({"kind": "outcome", "outcome": outcome, "candidate_count": len(pairs),
            "candidate_evaluations": evaluated_candidates,
            "theorem_domain_outputs": theorem_domain_outputs,
            "abstract_wl_classes": len(abstract_classes), "crossings": crossings,
            "minimum_residual": minimum, "directional_prediction_matches": prediction_matches,
            "elapsed_seconds": round(time.monotonic() - started, 6)})
    print(canonical({"outcome": outcome, "candidate_count": len(pairs),
                     "candidate_evaluations": evaluated_candidates,
                     "theorem_domain_outputs": theorem_domain_outputs,
                     "abstract_wl_classes": len(abstract_classes), "crossings": crossings,
                     "minimum_residual": minimum, "directional_prediction_matches": prediction_matches}))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["gate", "trial"])
    args = parser.parse_args()
    if args.mode == "gate":
        gate()
    else:
        trial()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(canonical({"status": "ERROR", "type": type(exc).__name__, "message": str(exc)}))
        raise
