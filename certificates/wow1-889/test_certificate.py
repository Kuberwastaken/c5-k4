#!/usr/bin/env python3
"""Regression tests for the WoW-I #889 executable certificate."""

from __future__ import annotations

import unittest

from verify_certificate import (
    blue_graph_for_triangle_free_property,
    certificate,
    complement_c5_clique_blowup,
    distances_from,
    is_triangle_free,
)


class CertificateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.graph = complement_c5_clique_blowup(4)

    def test_witness_profile(self) -> None:
        self.assertEqual(len(self.graph), 20)
        self.assertEqual({len(row) for row in self.graph}, {8})
        self.assertEqual(sum(map(len, self.graph)) // 2, 80)
        self.assertTrue(is_triangle_free(self.graph))
        distance_rows = [distances_from(self.graph, vertex) for vertex in range(20)]
        self.assertTrue(all(max(row) == 2 for row in distance_rows))
        self.assertEqual(
            {sum(distance % 2 == 1 for distance in row) for row in distance_rows},
            {8},
        )

    def test_every_nonedge_is_red_under_definition_822(self) -> None:
        blue = blue_graph_for_triangle_free_property(self.graph)
        self.assertTrue(all(not row for row in blue))

        for u in range(20):
            for v in range(u + 1, 20):
                if v not in self.graph[u]:
                    self.assertTrue(
                        self.graph[u] & self.graph[v],
                        f"nonedge {u, v} lacks a common neighbor",
                    )

    def test_machine_readable_contradiction(self) -> None:
        result = certificate()
        self.assertTrue(result["verified"])
        self.assertEqual(result["odd_distance"]["w"], 8)
        self.assertEqual(result["blue_graph"], {"edges": 0, "clique_number": 1})
        self.assertEqual(result["claimed_clique_size"], 2)
        self.assertEqual(result["contradiction"], "1 < 2")


if __name__ == "__main__":
    unittest.main()
