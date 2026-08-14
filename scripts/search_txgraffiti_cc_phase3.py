#!/usr/bin/env python3
"""Phase-three t=2 pairing-orbit shards for the TxGraffiti C-C wall."""

from __future__ import annotations

import argparse
import hashlib
import time

import networkx as nx

import method_v15_live_search_runtime as live
import search_txgraffiti_cc_live as base
import search_txgraffiti_cc_phase2 as phase2


INTERNAL_STOP_SECONDS = 54.0
SOLVER_CAP_SECONDS = 4.0
BASE_GRAPH6 = ("Gs@ipo", "GsOiho", "GtPHOk", "Gv?IXW", "GtP@Ww")
ARM_SHARD = {"CATALOGUE": 0, "GENERIC": 1, "WALL_NAVIGATION": 2}
SHARD_COUNT = 3

base.SOLVER_CAP_SECONDS = SOLVER_CAP_SECONDS


def perfect_pairings(items: tuple[int, ...]):
    """Yield every perfect matching of the ordered item tuple lexicographically."""
    if not items:
        yield ()
        return
    first = items[0]
    for index in range(1, len(items)):
        second = items[index]
        remainder = items[1:index] + items[index + 1 :]
        for tail in perfect_pairings(remainder):
            yield tuple(sorted(((first, second),) + tail))


def edge_automorphisms(graph: nx.Graph) -> tuple[tuple[int, ...], ...]:
    edges = phase2.base_edges(graph)
    edge_index = {edge: index for index, edge in enumerate(edges)}
    permutations: set[tuple[int, ...]] = set()
    matcher = nx.algorithms.isomorphism.GraphMatcher(graph, graph)
    for mapping in matcher.isomorphisms_iter():
        permutations.add(tuple(
            edge_index[base.normalized_edge(mapping[u], mapping[v])] for u, v in edges
        ))
    return tuple(sorted(permutations))


def pairing_image(
    pairing: tuple[tuple[int, int], ...], permutation: tuple[int, ...]
) -> tuple[tuple[int, int], ...]:
    return phase2.normalized_pairing([
        (permutation[left], permutation[right]) for left, right in pairing
    ])


def pairing_orbit_representatives(graph: nx.Graph):
    automorphisms = edge_automorphisms(graph)
    seen: set[tuple[tuple[int, int], ...]] = set()
    for pairing in perfect_pairings(tuple(range(graph.number_of_edges()))):
        if pairing in seen:
            continue
        orbit = {pairing_image(pairing, permutation) for permutation in automorphisms}
        representative = min(orbit)
        seen.update(orbit)
        if pairing == representative:
            yield representative


def construction_states() -> list[phase2.ReservoirState]:
    rows: list[tuple[str, phase2.ReservoirState]] = []
    for encoded in BASE_GRAPH6:
        graph = nx.from_graph6_bytes(encoded.encode("ascii"))
        if len(graph) != 8 or not nx.is_connected(graph) or set(dict(graph.degree()).values()) != {3}:
            raise RuntimeError("frozen order-eight cubic base is invalid")
        for pairing in pairing_orbit_representatives(graph):
            state = phase2.state_from_base(
                graph, pairing, f"phase3_t2_base_{encoded}_pairing_orbit"
            )
            material = (encoded + "|" + repr(pairing)).encode("ascii")
            rows.append((hashlib.sha256(material).hexdigest(), state))
    rows.sort(key=lambda item: item[0])
    return [state for _, state in rows]


class ShardedRecorder:
    """Canonicalize once, then admit only this arm's exact graph-class shard."""

    def __init__(
        self, ledger: live.ScientificJsonl, canonicalizer: live.LabelgCanonicalizer, shard: int
    ):
        self.ledger = ledger
        self.canonicalizer = canonicalizer
        self.shard = shard
        self.seen: set[str] = set()

    def evaluate(self, graph: nx.Graph) -> dict[str, object] | None:
        canonical = self.canonicalizer.canonicalize(graph)
        assigned = int(canonical.sha256, 16) % SHARD_COUNT
        if assigned != self.shard:
            return None
        self.ledger.counters.proposed += 1
        if canonical.sha256 in self.seen:
            return None
        self.seen.add(canonical.sha256)
        self.ledger.counters.canonical_unique += 1
        if not base.applicable(graph):
            return None
        self.ledger.counters.hypothesis_survivor += 1
        result = dict(phase2.exact_profile(graph))
        objective = result.pop("objective")
        crossing = result.pop("crossing")
        return self.ledger.evaluated_candidate(
            canonical, objective=objective, crossing=crossing, payload=result
        )


def run_shard(recorder: ShardedRecorder, deadline: float) -> None:
    for state in construction_states():
        if time.monotonic() >= deadline:
            return
        graph = phase2.build_graph(state)
        row = recorder.evaluate(graph)
        if row is not None and int(row["objective"]) < 0:
            recorder.ledger.checkpoint("crossing_found_independent_replay_passed")
            return


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--arm", choices=live.ARMS, required=True)
    args = parser.parse_args()
    ledger = live.ScientificJsonl.from_environment()
    if args.arm != ledger.arm:
        raise RuntimeError("CLI arm differs from the frozen runtime identity")
    base.database_gate(ledger)
    recorder = ShardedRecorder(
        ledger, live.LabelgCanonicalizer.from_environment(), ARM_SHARD[args.arm]
    )
    run_shard(recorder, ledger.started + INTERNAL_STOP_SECONDS)
    ledger.finish()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
