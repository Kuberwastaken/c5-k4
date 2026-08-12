#!/usr/bin/env python3
"""Check the Method v0.3 Lane P2 lemmas on the frozen 12 graph records.

This script performs no graph generation.  It reads exactly the six saved
2-lift representatives and the first saved minimum-residual representative
for each completed cubic order 10, 12, 14, 16, 18, and 20.
"""

from __future__ import annotations

import json
from pathlib import Path

import networkx as nx


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "results/expansion/method_v02_133_search.jsonl"

EXPECTED_LIFTS = (
    "2lift:C5:0",
    "2lift:Petersen:0",
    "2lift:Petersen:1",
    "2lift:Petersen:2",
    "2lift:Petersen:3",
    "2lift:Petersen:4",
)
EXPECTED_MINIMA = {
    10: "cubic-c4free-10:0",
    12: "cubic-c4free-12:0",
    14: "cubic-c4free-14:0",
    16: "cubic-c4free-16:139",
    18: "cubic-c4free-18:1",
    20: "cubic-c4free-20:3",
}


def has_c4(graph: nx.Graph) -> bool:
    """A simple graph has a C4 iff some vertex pair has two common neighbors."""
    vertices = list(graph)
    return any(
        len(set(graph[u]) & set(graph[v])) >= 2
        for i, u in enumerate(vertices)
        for v in vertices[i + 1 :]
    )


def is_induced_path(graph: nx.Graph, path: list[int]) -> bool:
    if len(set(path)) != len(path):
        return False
    return all(graph.has_edge(path[i], path[i + 1]) for i in range(len(path) - 1)) and all(
        not graph.has_edge(path[i], path[j])
        for i in range(len(path))
        for j in range(i + 2, len(path))
    )


def frozen_rows() -> list[dict]:
    rows = [json.loads(line) for line in LEDGER.read_text().splitlines()]
    by_name: dict[str, dict] = {}
    for row in rows:
        if row.get("name") is not None:
            by_name.setdefault(row["name"], row)
    names = (*EXPECTED_LIFTS, *(EXPECTED_MINIMA[n] for n in sorted(EXPECTED_MINIMA)))
    selected = [by_name[name] for name in names]
    assert len(selected) == 12
    assert all(row["n"] <= 20 for row in selected)
    return selected


def check_geodesic(graph: nx.Graph, path: list[int]) -> tuple[bool, tuple[int, int] | None]:
    """Check the triangle-free four-neighbor extension lemma on one geodesic.

    The return value says whether the over-strong claim that every forward
    neighbor avoids both possible contacts v2 and v3 survives.
    """
    radius = len(path) - 1
    assert radius >= 2
    c, v1, v2 = path[:3]
    assert is_induced_path(graph, path)
    assert sum(nx.triangles(graph).values()) == 0

    eligible = [a for a in graph[c] if a != v1 and not graph.has_edge(a, v1)]
    assert len(eligible) == 2
    all_forward_clean = True
    first_v3_contact: tuple[int, int] | None = None
    candidates: list[list[int]] = []
    forward_union: set[int] = set()
    for a in eligible:
        forward = [z for z in graph[a] if z != c]
        assert len(forward) == 2
        for z in forward:
            assert z not in path
            contacts = {vertex for vertex in path if graph.has_edge(z, vertex)}
            allowed_contacts = {v2}
            if radius >= 3:
                allowed_contacts.add(path[3])
            assert contacts <= allowed_contacts
            if contacts:
                all_forward_clean = False
            if radius >= 3 and path[3] in contacts and first_v3_contact is None:
                first_v3_contact = (a, z)
            candidates.append([z, a, *path])
            forward_union.add(z)

    # C4-freeness makes the four forward vertices distinct.  Their only path
    # contacts consume free degree slots at v2/v3, of which there are at most
    # three.  Hence at least one candidate is induced.
    assert len(forward_union) == 4
    assert any(is_induced_path(graph, candidate) for candidate in candidates)
    return all_forward_clean, first_v3_contact


def main() -> None:
    total_geodesics = 0
    direct = 0
    overstrong_failures = 0
    first_overstrong: tuple[str, list[int]] | None = None
    first_v3: tuple[str, list[int], int, int] | None = None

    for row in frozen_rows():
        graph = nx.from_graph6_bytes(row["graph6"].encode())
        assert nx.is_connected(graph)
        assert not has_c4(graph)
        eccentricity = nx.eccentricity(graph)
        radius = min(eccentricity.values())
        assert radius == row["radius"]
        if not all(degree == 3 for _, degree in graph.degree()):
            # C10 is retained because the frozen manifest says all six lift
            # representatives.  It is a degree-two control, so cubic lemmas
            # are inapplicable; its saved exact path still clears radius + 3.
            assert row["name"] == "2lift:C5:0"
            assert row["path"] >= radius + 3
            print(
                f"N/A  {row['name']}: noncubic lift control, "
                f"exact path={row['path']} >= radius+3={radius + 3}"
            )
            continue

        row_geodesics = 0
        row_direct = 0
        for center in (v for v in graph if eccentricity[v] == radius):
            for endpoint in graph:
                if nx.shortest_path_length(graph, center, endpoint) != radius:
                    continue
                for path in nx.all_shortest_paths(graph, center, endpoint):
                    all_forward_clean, v3_contact = check_geodesic(graph, path)
                    row_geodesics += 1
                    total_geodesics += 1
                    direct += 1
                    row_direct += 1
                    if not all_forward_clean:
                        overstrong_failures += 1
                        if first_overstrong is None:
                            first_overstrong = (row["name"], path)
                    if v3_contact is not None and first_v3 is None:
                        first_v3 = (row["name"], path, *v3_contact)

        print(
            f"PASS {row['name']}: radius={radius}, "
            f"center-periphery geodesics={row_geodesics}, direct={row_direct}"
        )

    assert total_geodesics == direct
    assert overstrong_failures > 0
    assert first_overstrong is not None
    assert first_v3 is not None
    print(
        "PASS constructive lemma: "
        f"all {total_geodesics} applicable geodesics have a direct "
        "two-vertex extension"
    )
    print(
        "REFUTED over-strong lemma 'every forward neighbor avoids v2 and v3': "
        f"{overstrong_failures} geodesics; first={first_overstrong[0]} "
        f"path={first_overstrong[1]}"
    )
    print(
        "REFUTED incomplete contact lemma 'only v2 can be met': "
        f"first={first_v3[0]} path={first_v3[1]} "
        f"branch={first_v3[2]} forward={first_v3[3]} meets v3"
    )


if __name__ == "__main__":
    main()
