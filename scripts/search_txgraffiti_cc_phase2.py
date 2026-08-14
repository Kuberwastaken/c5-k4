#!/usr/bin/env python3
"""Phase-two extremal-reservoir search for the TxGraffiti C-C wall."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import itertools
import random
import time

import networkx as nx
from pysat.card import CardEnc, EncType
from pysat.formula import CNF
from pysat.solvers import Solver

import method_v15_live_search_runtime as live
import search_txgraffiti_cc_live as base


SEED = 0xCC20260820
INTERNAL_STOP_SECONDS = 54.0
SOLVER_CAP_SECONDS = 4.0
MAX_WALL_CHILDREN_PER_KIND = 24
MAX_WALL_EXPANDED_STATES = 24
MAX_WALL_DEPTH = 3
WALL_BEAM_WIDTH = 24

# The phase-zero evaluator and repeated database gate use this module constant.
# Phase two tightens the old eight-second solve cap rather than weakening it.
base.SOLVER_CAP_SECONDS = SOLVER_CAP_SECONDS


@dataclass(frozen=True)
class ReservoirState:
    """A cubic base, one subdivision vertex per edge, and a matching on them."""

    t: int
    base_edges: tuple[tuple[int, int], ...]
    pairing: tuple[tuple[int, int], ...]
    origin: str


def normalized_pair(a: int, b: int) -> tuple[int, int]:
    return (a, b) if a < b else (b, a)


def normalized_pairing(rows: list[tuple[int, int]]) -> tuple[tuple[int, int], ...]:
    return tuple(sorted(normalized_pair(a, b) for a, b in rows))


def base_edges(graph: nx.Graph) -> tuple[tuple[int, int], ...]:
    graph = nx.convert_node_labels_to_integers(graph, ordering="sorted")
    return tuple(sorted(base.normalized_edge(u, v) for u, v in graph.edges()))


def graph_from_base_edges(t: int, edges: tuple[tuple[int, int], ...]) -> nx.Graph:
    graph = nx.Graph()
    graph.add_nodes_from(range(4 * t))
    graph.add_edges_from(edges)
    return graph


def validate_state(state: ReservoirState) -> None:
    if state.t < 1 or len(state.base_edges) != 6 * state.t:
        raise RuntimeError("reservoir state has the wrong base size")
    graph = graph_from_base_edges(state.t, state.base_edges)
    if not nx.is_connected(graph) or set(dict(graph.degree()).values()) != {3}:
        raise RuntimeError("reservoir base must be connected and cubic")
    flat = [vertex for pair in state.pairing for vertex in pair]
    if len(state.pairing) != 3 * state.t or sorted(flat) != list(range(6 * state.t)):
        raise RuntimeError("subdivision pairing is not a perfect matching")


def build_graph(state: ReservoirState) -> nx.Graph:
    """Build G and attach the data used to replay the structural mu* proof."""
    validate_state(state)
    reservoir_size = 4 * state.t
    graph = nx.Graph()
    graph.add_nodes_from(range(10 * state.t))
    for index, (u, v) in enumerate(state.base_edges):
        subdivision = reservoir_size + index
        graph.add_edge(u, subdivision)
        graph.add_edge(v, subdivision)
    matching: list[tuple[int, int]] = []
    for left, right in state.pairing:
        edge = (reservoir_size + left, reservoir_size + right)
        graph.add_edge(*edge)
        matching.append(normalized_pair(*edge))
    graph.graph.update({
        "origin": state.origin,
        "certified_t": state.t,
        "certified_reservoir": tuple(range(reservoir_size)),
        "certified_matching": tuple(sorted(matching)),
    })
    return graph


def verify_structural_mu_certificate(graph: nx.Graph) -> int:
    """Verify mu*(G)=3t from a maximal matching and the cubic counting bound."""
    t = graph.graph.get("certified_t")
    reservoir = set(graph.graph.get("certified_reservoir", ()))
    matching = {tuple(edge) for edge in graph.graph.get("certified_matching", ())}
    if type(t) is not int or t < 1 or len(graph) != 10 * t:
        raise RuntimeError("missing or invalid phase-two structural coordinate")
    if not nx.is_connected(graph) or set(dict(graph.degree()).values()) != {3}:
        raise RuntimeError("constructed graph is not connected cubic")
    if len(reservoir) != 4 * t or graph.subgraph(reservoir).number_of_edges() != 0:
        raise RuntimeError("certified unmatched reservoir is not independent")
    if len(matching) != 3 * t or not nx.is_matching(graph, matching):
        raise RuntimeError("certified core edges are not a matching of size 3t")
    if not nx.is_maximal_matching(graph, matching):
        raise RuntimeError("certified matching is not maximal")
    # For every maximal matching M in a cubic graph, its unmatched set U is
    # independent and 3|U| <= 4|M|. Hence n <= (10/3)|M| and |M| >= 3n/10.
    # Here n=10t and the displayed matching has 3t edges, proving equality.
    return 3 * t


def replay_no_small_independent_dominating_set(graph: nx.Graph, limit: int) -> bool:
    """Independent SAT replay of the claim i(G)>limit."""
    graph = base.relabel(graph)
    n = len(graph)
    formula = CNF()
    for u, v in graph.edges():
        formula.append([-(u + 1), -(v + 1)])
    for vertex in graph:
        formula.append([u + 1 for u in itertools.chain((vertex,), graph.neighbors(vertex))])
    bound = CardEnc.atmost(
        lits=list(range(1, n + 1)), bound=limit, top_id=n, encoding=EncType.seqcounter
    )
    formula.extend(bound.clauses)
    with Solver(name="cadical195", bootstrap_with=formula.clauses) as solver:
        return not solver.solve()


def exact_profile(graph: nx.Graph) -> dict[str, object]:
    matching = verify_structural_mu_certificate(graph)
    independent, witness = base.independent_domination(graph)
    residual = matching - independent
    payload: dict[str, object] = {
        "objective": residual,
        "crossing": residual < 0,
        "n": graph.number_of_nodes(),
        "m": graph.number_of_edges(),
        "degree": 3,
        "t": matching // 3,
        "independent_domination": independent,
        "minimum_maximal_matching": matching,
        "independent_dominating_witness": list(witness),
        "mu_star_certificate": {
            "upper": "displayed maximal matching on all subdivision vertices",
            "lower": "cubic counting bound 3|U|<=4|M| gives |M|>=3n/10",
            "value": matching,
        },
        "origin": str(graph.graph.get("origin", "unspecified")),
    }
    if residual < 0:
        if not replay_no_small_independent_dominating_set(graph, matching):
            raise RuntimeError("crossing failed independent SAT replay")
        if verify_structural_mu_certificate(graph) != matching:
            raise RuntimeError("crossing failed structural matching replay")
        payload["independent_replay"] = {
            "solver": "PySAT CaDiCaL 1.9.5",
            "claim": f"no independent dominating set of size at most {matching}",
            "result": "UNSAT",
        }
    return payload


def random_pairing(size: int, rng: random.Random) -> tuple[tuple[int, int], ...]:
    vertices = list(range(size))
    rng.shuffle(vertices)
    return normalized_pairing([(vertices[i], vertices[i + 1]) for i in range(0, size, 2)])


def distance_pairing(graph: nx.Graph) -> tuple[tuple[int, int], ...]:
    """Pair base edges to maximize their total distance in the line graph."""
    edges = base_edges(graph)
    line = nx.line_graph(nx.Graph(edges))
    line = nx.relabel_nodes(line, {edge: base.normalized_edge(*edge) for edge in line})
    distances = dict(nx.all_pairs_shortest_path_length(line))
    complete = nx.Graph()
    complete.add_nodes_from(range(len(edges)))
    scale = len(edges) ** 3 + 1
    for left, right in itertools.combinations(range(len(edges)), 2):
        distance = distances[edges[left]][edges[right]]
        tie_break = len(edges) ** 2 - (left * len(edges) + right)
        complete.add_edge(left, right, weight=distance * scale + tie_break)
    matching = nx.max_weight_matching(complete, maxcardinality=True, weight="weight")
    pairing = normalized_pairing(list(matching))
    if len(pairing) * 2 != len(edges):
        raise RuntimeError("distance pairing did not produce a perfect matching")
    return pairing


def adjacent_pairing(graph: nx.Graph) -> tuple[tuple[int, int], ...]:
    edges = base_edges(graph)
    index = {edge: i for i, edge in enumerate(edges)}
    line = nx.line_graph(nx.Graph(edges))
    line = nx.relabel_nodes(line, {edge: base.normalized_edge(*edge) for edge in line})
    matching = nx.max_weight_matching(line, maxcardinality=True)
    pairing = normalized_pairing([(index[base.normalized_edge(*a)], index[base.normalized_edge(*b)]) for a, b in matching])
    if len(pairing) * 2 != len(edges):
        raise RuntimeError("adjacent pairing did not produce a perfect matching")
    return pairing


def connected_random_cubic(t: int, rng: random.Random) -> nx.Graph:
    while True:
        graph = nx.random_regular_graph(3, 4 * t, seed=rng.randrange(2**63))
        if nx.is_connected(graph):
            return nx.convert_node_labels_to_integers(graph, ordering="sorted")


def state_from_base(graph: nx.Graph, pairing: tuple[tuple[int, int], ...], origin: str) -> ReservoirState:
    t, remainder = divmod(len(graph), 4)
    if remainder:
        raise RuntimeError("cubic base order is not divisible by four")
    state = ReservoirState(t, base_edges(graph), pairing, origin)
    validate_state(state)
    return state


def catalogue_states() -> list[ReservoirState]:
    bases = [
        ("K4", nx.complete_graph(4)),
        ("cube", nx.cubical_graph()),
        ("CL6", nx.circular_ladder_graph(6)),
        ("Frucht", nx.frucht_graph()),
        ("Moebius-Kantor", nx.moebius_kantor_graph()),
    ]
    states: list[ReservoirState] = []
    for name, graph in bases:
        graph = nx.convert_node_labels_to_integers(graph, ordering="sorted")
        states.append(state_from_base(graph, distance_pairing(graph), f"catalogue_{name}_distance"))
        states.append(state_from_base(graph, adjacent_pairing(graph), f"catalogue_{name}_adjacent"))
    return states


def seed_states() -> list[ReservoirState]:
    rng = random.Random(SEED ^ 0x57414C4C)
    states: list[ReservoirState] = []
    for t in (3, 4, 5):
        for index in range(2):
            graph = connected_random_cubic(t, rng)
            states.append(state_from_base(
                graph, distance_pairing(graph), f"wall_fresh_t{t}_seed_{index}"
            ))
    return states


def pairing_children(state: ReservoirState) -> list[ReservoirState]:
    rows: list[ReservoirState] = []
    for first_index, second_index in itertools.combinations(range(len(state.pairing)), 2):
        a, b = state.pairing[first_index]
        c, d = state.pairing[second_index]
        for replacements in (((a, c), (b, d)), ((a, d), (b, c))):
            pairing = list(state.pairing)
            pairing[first_index] = replacements[0]
            pairing[second_index] = replacements[1]
            rows.append(ReservoirState(
                state.t,
                state.base_edges,
                normalized_pairing(pairing),
                f"wall_pairing_switch_from_{state.origin}",
            ))
    return rows


def base_switch_children(state: ReservoirState) -> list[ReservoirState]:
    rows: list[ReservoirState] = []
    edge_set = set(state.base_edges)
    for first_index, second_index in itertools.combinations(range(len(state.base_edges)), 2):
        a, b = state.base_edges[first_index]
        c, d = state.base_edges[second_index]
        if len({a, b, c, d}) != 4:
            continue
        for replacements in (((a, c), (b, d)), ((a, d), (b, c))):
            replacements = tuple(base.normalized_edge(*edge) for edge in replacements)
            if replacements[0] == replacements[1] or any(edge in edge_set for edge in replacements):
                continue
            edges = list(state.base_edges)
            edges[first_index], edges[second_index] = replacements
            edges_tuple = tuple(sorted(edges))
            graph = graph_from_base_edges(state.t, edges_tuple)
            if not nx.is_connected(graph):
                continue
            # Sorting changed subdivision indices; rebuild the same pairing by
            # transporting old edge identities to their new sorted positions.
            old_to_new = {edge: index for index, edge in enumerate(edges_tuple)}
            transported: list[tuple[int, int]] = []
            old_edges = list(state.base_edges)
            old_edges[first_index], old_edges[second_index] = replacements
            for left, right in state.pairing:
                transported.append((old_to_new[old_edges[left]], old_to_new[old_edges[right]]))
            rows.append(ReservoirState(
                state.t,
                edges_tuple,
                normalized_pairing(transported),
                f"wall_base_switch_from_{state.origin}",
            ))
    return rows


def sampled_children(state: ReservoirState) -> list[ReservoirState]:
    material = repr((state.t, state.base_edges, state.pairing)).encode("ascii")
    child_seed = SEED ^ int.from_bytes(hashlib.sha256(material).digest()[:8], "big")
    rng = random.Random(child_seed)
    pairing = pairing_children(state)
    base_rows = base_switch_children(state)
    rng.shuffle(pairing)
    rng.shuffle(base_rows)
    return pairing[:MAX_WALL_CHILDREN_PER_KIND] + base_rows[:MAX_WALL_CHILDREN_PER_KIND]


def evaluate_state(
    recorder: live.GraphSearchRecorder, state: ReservoirState
) -> tuple[dict[str, object], ReservoirState] | None:
    graph = build_graph(state)
    row = recorder.evaluate(graph, base.applicable, exact_profile)
    if row is None:
        return None
    return row, state


def run_catalogue(recorder: live.GraphSearchRecorder, deadline: float) -> None:
    for state in catalogue_states():
        if time.monotonic() >= deadline:
            return
        evaluated = evaluate_state(recorder, state)
        if evaluated is not None and int(evaluated[0]["objective"]) < 0:
            recorder.ledger.checkpoint("crossing_found_independent_replay_passed")
            return


def run_generic(recorder: live.GraphSearchRecorder, deadline: float) -> None:
    rng = random.Random(SEED ^ 0x47454E45524943)
    while time.monotonic() < deadline:
        t = rng.choice((5, 6))
        graph = connected_random_cubic(t, rng)
        state = state_from_base(
            graph, random_pairing(6 * t, rng), f"generic_fresh_t{t}_objective_blind"
        )
        evaluated = evaluate_state(recorder, state)
        if evaluated is not None and int(evaluated[0]["objective"]) < 0:
            recorder.ledger.checkpoint("crossing_found_independent_replay_passed")
            return


def run_wall(recorder: live.GraphSearchRecorder, deadline: float) -> None:
    beam: list[tuple[dict[str, object], ReservoirState]] = []
    for state in seed_states():
        if time.monotonic() >= deadline:
            return
        evaluated = evaluate_state(recorder, state)
        if evaluated is None:
            continue
        row, retained = evaluated
        if int(row["objective"]) < 0:
            recorder.ledger.checkpoint("crossing_found_independent_replay_passed")
            return
        beam.append((row, retained))

    expanded = 0
    depth = 0
    while beam and depth < MAX_WALL_DEPTH and expanded < MAX_WALL_EXPANDED_STATES:
        if time.monotonic() >= deadline:
            return
        next_beam: list[tuple[dict[str, object], ReservoirState]] = []
        beam.sort(key=lambda item: (
            int(item[0]["objective"]),
            -int(item[0]["payload"]["independent_domination"]),
            str(item[0]["canonical_sha256"]),
        ))
        for _, parent in beam[:WALL_BEAM_WIDTH]:
            if expanded >= MAX_WALL_EXPANDED_STATES:
                break
            expanded += 1
            for child in sampled_children(parent):
                if time.monotonic() >= deadline:
                    return
                evaluated = evaluate_state(recorder, child)
                if evaluated is None:
                    continue
                row, retained = evaluated
                if int(row["objective"]) < 0:
                    recorder.ledger.checkpoint("crossing_found_independent_replay_passed")
                    return
                next_beam.append((row, retained))
        next_beam.sort(key=lambda item: (
            int(item[0]["objective"]),
            -int(item[0]["payload"]["independent_domination"]),
            str(item[0]["canonical_sha256"]),
        ))
        beam = next_beam[:WALL_BEAM_WIDTH]
        depth += 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--arm", choices=live.ARMS, required=True)
    args = parser.parse_args()
    ledger = live.ScientificJsonl.from_environment()
    if args.arm != ledger.arm:
        raise RuntimeError("CLI arm differs from the frozen runtime identity")
    recorder = live.GraphSearchRecorder(ledger, live.LabelgCanonicalizer.from_environment())
    base.database_gate(ledger)
    deadline = ledger.started + INTERNAL_STOP_SECONDS
    if args.arm == "CATALOGUE":
        run_catalogue(recorder, deadline)
    elif args.arm == "GENERIC":
        run_generic(recorder, deadline)
    else:
        run_wall(recorder, deadline)
    ledger.finish()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
