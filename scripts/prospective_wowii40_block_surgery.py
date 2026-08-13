#!/usr/bin/env python3
"""Frozen exact block-surgery trial for current DeepMind WOWII 40."""

from __future__ import annotations

import itertools
import json
import math
import signal
import time
from pathlib import Path

import networkx as nx


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "results/expansion/prospective_wowii40_block_surgery_ledger.jsonl"
CAP = 5


class SolveTimeout(RuntimeError):
    pass


def alarm_handler(_sig: int, _frame: object) -> None:
    raise SolveTimeout("60-second cap")


def append(record: dict[str, object]) -> None:
    with LEDGER.open("a", encoding="utf-8") as out:
        out.write(json.dumps(record, sort_keys=True) + "\n")
        out.flush()


def masks_of_size(n: int, size: int):
    for vertices in itertools.combinations(range(n), size):
        mask = 0
        for v in vertices:
            mask |= 1 << v
        yield mask, vertices


def induced_edges(adj: list[int], mask: int) -> int:
    return sum(bin(adj[v] & mask).count("1") for v in range(len(adj)) if mask >> v & 1) // 2


def is_forest_mask(adj: list[int], mask: int) -> bool:
    remaining = mask
    components = 0
    while remaining:
        components += 1
        seed = remaining & -remaining
        seen = seed
        frontier = seed
        while frontier:
            vbit = frontier & -frontier
            frontier ^= vbit
            v = vbit.bit_length() - 1
            new = adj[v] & mask & ~seen
            seen |= new
            frontier |= new
        remaining &= ~seen
    return induced_edges(adj, mask) == bin(mask).count("1") - components


def is_bipartite_mask(adj: list[int], mask: int) -> bool:
    uncolored = mask
    color1 = 0
    while uncolored:
        seed = uncolored & -uncolored
        queue = [seed.bit_length() - 1]
        colored = seed
        uncolored ^= seed
        while queue:
            v = queue.pop()
            vcolor = bool(color1 >> v & 1)
            nbrs = adj[v] & mask
            if ((nbrs & colored) & (color1 if vcolor else ~color1)):
                return False
            new = nbrs & uncolored
            while new:
                bit = new & -new
                new ^= bit
                u = bit.bit_length() - 1
                if not vcolor:
                    color1 |= bit
                colored |= bit
                uncolored ^= bit
                queue.append(u)
    return True


def largest_induced(adj: list[int], predicate) -> tuple[int, tuple[int, ...], int]:
    n = len(adj)
    checked = 0
    for size in range(n, 0, -1):
        for mask, vertices in masks_of_size(n, size):
            checked += 1
            if predicate(adj, mask):
                return size, vertices, checked
    return 0, (), checked


def pathable_masks(adj: list[int]) -> tuple[list[bool], list[tuple[int, ...] | None]]:
    n = len(adj)
    total = 1 << n
    endpoints = [0] * total
    parent: list[dict[int, int]] = [dict() for _ in range(total)]
    for v in range(n):
        endpoints[1 << v] = 1 << v
        parent[1 << v][v] = -1
    for mask in range(1, total):
        eps = endpoints[mask]
        while eps:
            bit = eps & -eps
            eps ^= bit
            v = bit.bit_length() - 1
            choices = adj[v] & ~mask & (total - 1)
            while choices:
                ubit = choices & -choices
                choices ^= ubit
                u = ubit.bit_length() - 1
                nxt = mask | ubit
                if not endpoints[nxt] & ubit:
                    endpoints[nxt] |= ubit
                    parent[nxt][u] = v
    pathable = [bool(x) for x in endpoints]
    witness: list[tuple[int, ...] | None] = [None] * total
    for mask in range(1, total):
        if not endpoints[mask]:
            continue
        end = (endpoints[mask] & -endpoints[mask]).bit_length() - 1
        order = [end]
        curmask = mask
        cur = end
        while parent[curmask][cur] != -1:
            prev = parent[curmask][cur]
            order.append(prev)
            curmask ^= 1 << cur
            cur = prev
        witness[mask] = tuple(reversed(order))
    return pathable, witness


def exact_path_cover(adj: list[int]) -> tuple[int, list[tuple[int, ...]], int]:
    n = len(adj)
    full = (1 << n) - 1
    pathable, witness = pathable_masks(adj)
    dp = [n + 1] * (1 << n)
    choice = [0] * (1 << n)
    dp[0] = 0
    transitions = 0
    for mask in range(1, full + 1):
        first = mask & -mask
        sub = mask
        while sub:
            if sub & first and pathable[sub]:
                transitions += 1
                value = 1 + dp[mask ^ sub]
                if value < dp[mask]:
                    dp[mask] = value
                    choice[mask] = sub
            sub = (sub - 1) & mask
    paths = []
    mask = full
    while mask:
        sub = choice[mask]
        if not sub:
            raise AssertionError("path-cover DP failed")
        paths.append(witness[sub] or ())
        mask ^= sub
    return dp[full], paths, transitions


def exact_record(name: str, family: str, graph: nx.Graph) -> dict[str, object]:
    graph = nx.convert_node_labels_to_integers(nx.Graph(graph))
    n = graph.number_of_nodes()
    adj = [0] * n
    for u, v in graph.edges():
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    start = time.monotonic()
    old = signal.signal(signal.SIGALRM, alarm_handler)
    signal.alarm(CAP)
    try:
        forest, fw, fc = largest_induced(adj, is_forest_mask)
        bip, bw, bc = largest_induced(adj, is_bipartite_mask)
        path_cover, paths, pc = exact_path_cover(adj)
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old)
    rhs = math.ceil((path_cover + bip + 1) / 2)
    return {
        "event": "graph_evaluated",
        "name": name,
        "family": family,
        "n": n,
        "m": graph.number_of_edges(),
        "graph6": nx.to_graph6_bytes(graph, header=False).decode().strip(),
        "edges": sorted([u, v] for u, v in graph.edges()),
        "forest": forest,
        "forest_witness": fw,
        "bipartite": bip,
        "bipartite_witness": bw,
        "path_cover": path_cover,
        "path_cover_paths": paths,
        "rhs": rhs,
        "slack": forest - rhs,
        "crossing": forest < rhs,
        "search_counts": {"forest_subsets": fc, "bipartite_subsets": bc, "path_cover_transitions": pc},
        "seconds": round(time.monotonic() - start, 6),
    }


def glue_bicliques(spec: tuple[tuple[int, int, str], ...]) -> nx.Graph:
    graph = nx.Graph()
    cut = None
    nxt = 0
    for a, b, side in spec:
        left = list(range(nxt, nxt + a)); nxt += a
        right = list(range(nxt, nxt + b)); nxt += b
        if cut is not None:
            target = left if side == "L" else right
            old = target[0]
            graph = nx.contracted_nodes(graph, cut, old, self_loops=False) if old in graph else graph
            target[0] = cut
        graph.add_nodes_from(left + right)
        graph.add_edges_from(itertools.product(left, right))
        cut = right[-1] if side == "L" else left[-1]
    return nx.convert_node_labels_to_integers(graph)


def ear_graph(lengths: tuple[int, ...], twin: bool) -> nx.Graph:
    graph = nx.Graph([(0, 1)])
    nxt = 2
    for length in lengths:
        internal = list(range(nxt, nxt + length - 1)); nxt += length - 1
        nx.add_path(graph, [0] + internal + [1])
    if twin and graph.number_of_nodes() < 18:
        source = 2
        new = graph.number_of_nodes()
        graph.add_node(new)
        graph.add_edges_from((new, q) for q in list(graph.neighbors(source)))
    return graph


def substituted_path(sizes: tuple[int, ...], kinds: tuple[str, ...], interface: str) -> nx.Graph:
    graph = nx.Graph()
    blocks = []
    nxt = 0
    for size, kind in zip(sizes, kinds):
        block = list(range(nxt, nxt + size)); nxt += size
        graph.add_nodes_from(block)
        if kind == "clique": graph.add_edges_from(itertools.combinations(block, 2))
        blocks.append(block)
    for left, right in zip(blocks, blocks[1:]):
        if interface == "complete": graph.add_edges_from(itertools.product(left, right))
        elif interface == "matching": graph.add_edges_from(zip(left, right))
        else: graph.add_edge(left[-1], right[0])
    return graph


def candidates():
    seen = set()
    def emit(name, family, graph):
        if not (3 <= graph.number_of_nodes() <= 18) or not nx.is_connected(graph): return
        key = nx.weisfeiler_lehman_graph_hash(graph) + str(sorted(d for _, d in graph.degree()))
        if key in seen: return
        seen.add(key)
        yield name, family, graph
    for blocks in range(2, 5):
        for raw in itertools.product(((2, 2, "L"), (2, 3, "R"), (3, 2, "L"), (3, 4, "R")), repeat=blocks):
            yield from emit(f"biclique_tree_{raw}", "nonuniform_bipartite_block_tree", glue_bicliques(raw))
    for count in range(2, 5):
        for lengths in itertools.product(range(2, 6), repeat=count):
            for twin in (False, True):
                yield from emit(f"ears_{lengths}_twin{int(twin)}", "ear_surgery", ear_graph(lengths, twin))
    for blocks in range(3, 7):
        patterns = [tuple(2 if i % 2 == 0 else 3 for i in range(blocks)),
                    tuple(1 if i in (0, blocks - 1) else 3 for i in range(blocks)),
                    tuple(2 + (i == blocks // 2) * 2 for i in range(blocks))]
        for sizes in patterns:
            for kinds in (tuple("indep" for _ in sizes), tuple("clique" if i % 2 else "indep" for i in range(blocks))):
                for interface in ("portal", "matching", "complete"):
                    yield from emit(f"subst_{sizes}_{kinds}_{interface}", "block_substitution", substituted_path(sizes, kinds, interface))


def main() -> None:
    evaluated = crossings = timeouts = 0
    best = 999
    already = set()
    timed_out_names = set()
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if record.get("event") == "graph_evaluated":
            already.add(record.get("graph6"))
        elif record.get("event") == "graph_timeout":
            timed_out_names.add(record.get("name"))
    priority = {"ear_surgery": 0, "block_substitution": 1,
                "nonuniform_bipartite_block_tree": 2}
    work = sorted(candidates(), key=lambda item:
                  (priority[item[1]], item[2].number_of_nodes(), item[0]))
    for name, family, graph in work:
        if evaluated >= 1200: break
        graph6 = nx.to_graph6_bytes(nx.convert_node_labels_to_integers(graph),
                                    header=False).decode().strip()
        if graph6 in already:
            continue
        if name in timed_out_names:
            continue
        try:
            record = exact_record(name, family, graph)
        except SolveTimeout:
            append({"event": "graph_timeout", "name": name, "family": family, "n": graph.number_of_nodes()})
            timeouts += 1
            continue
        append(record)
        evaluated += 1
        best = min(best, int(record["slack"]))
        crossings += int(bool(record["crossing"]))
    append({"event": "construction_sweep_complete", "graphs_evaluated": evaluated,
            "crossings": crossings, "timeouts": timeouts, "minimum_slack": best})
    print(json.dumps({"evaluated": evaluated, "crossings": crossings, "timeouts": timeouts, "minimum_slack": best}))


if __name__ == "__main__":
    main()
