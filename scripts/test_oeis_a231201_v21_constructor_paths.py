"""Synthetic v2.1 constructor smoke tests; no frozen target domain/search is evaluated."""
from __future__ import annotations

import pathlib
import sys
import tempfile
import time
import types
import unittest
from unittest import mock

import construct_oeis_a231201_v21 as constructor
import oeis_a231201_v2_common as common


class _Ledger:
    def __init__(self) -> None:
        self.rows = []

    def append(self, value: dict) -> None:
        self.rows.append(value)


class _FakeModel:
    def __init__(self) -> None:
        self.variables = 0

    def new_bool_var(self, _name: str) -> int:
        self.variables += 1
        return 0

    def add(self, _constraint) -> None:
        return None

    def add_bool_or(self, _variables) -> None:
        return None

    def add_hint(self, _variable, _value: int) -> None:
        return None

    def add_decision_strategy(self, _ordered, _choose, _select) -> None:
        return None


class _Parameters:
    max_time_in_seconds = 0.0
    num_search_workers = 0
    random_seed = -1


class _FakeSolver:
    def __init__(self) -> None:
        self.parameters = _Parameters()
        self.wall_time = 0.0
        self.num_branches = 0
        self.num_conflicts = 0

    def solve(self, _model) -> int:
        return 0

    def status_name(self, _status: int) -> str:
        return "UNKNOWN"

    def value(self, _variable) -> int:
        raise AssertionError("UNKNOWN synthetic solver result must not be read")


def _fake_ortools_modules() -> dict[str, types.ModuleType]:
    cp_model = types.ModuleType("cp_model")
    cp_model.CpModel = _FakeModel
    cp_model.CpSolver = _FakeSolver
    cp_model.CHOOSE_FIRST = 0
    cp_model.SELECT_MAX_VALUE = 0
    cp_model.FEASIBLE = 1
    cp_model.OPTIMAL = 2
    cp_model.INFEASIBLE = 3
    ortools = types.ModuleType("ortools")
    sat = types.ModuleType("ortools.sat")
    python = types.ModuleType("ortools.sat.python")
    python.cp_model = cp_model
    return {
        "ortools": ortools,
        "ortools.sat": sat,
        "ortools.sat.python": python,
        "ortools.sat.python.cp_model": cp_model,
    }


class V21ConstructorPathTests(unittest.TestCase):
    def test_python39_population_count(self) -> None:
        self.assertEqual(constructor.population_count(0), 0)
        self.assertEqual(constructor.population_count((1 << 130) | 7), 4)
        with self.assertRaises(ValueError):
            constructor.population_count(-1)
        source = pathlib.Path(constructor.__file__).read_text()
        self.assertNotIn(".bit_count(", source)

    def test_deterministic_greedy_repair_path_on_synthetic_rows(self) -> None:
        assignment, stats = constructor.greedy(
            [1, 2, 4], "0_0", time.monotonic() + 1.0
        )
        common.validate_assignment(assignment, "0_0")
        self.assertEqual(stats["uncovered"], 0)

    def test_compressed_set_cover_cp_path_with_mock_solver_boundary(self) -> None:
        ledger = _Ledger()
        hint, _ = constructor.greedy([1, 2], "0_1", time.monotonic() + 1.0)
        with mock.patch.dict(sys.modules, _fake_ortools_modules()):
            status, assignment, rounds = constructor.compressed_cp(
                [1, 2], "0_1", hint, time.monotonic() + 1.0, ledger
            )
        self.assertEqual((status, assignment, rounds), ("UNKNOWN", None, 3))
        self.assertEqual(len(ledger.rows), 3)

    def test_small_basis_cegar_path_with_mock_growth_and_solver_boundaries(self) -> None:
        ledger = _Ledger()
        hint, _ = constructor.greedy([1], "1_2", time.monotonic() + 1.0)
        with tempfile.TemporaryDirectory() as td, mock.patch.dict(
            sys.modules, _fake_ortools_modules()
        ):
            work = pathlib.Path(td)
            artifacts = {}
            status, assignment, rounds = constructor.compressed_cp(
                [1],
                "1_2",
                hint,
                time.monotonic() + 1.0,
                ledger,
                growth_pool=[1, 2, 3],
                logical_start=4,
                work=work,
                artifacts=artifacts,
            )
            self.assertTrue((work / "basis-delta-0004.json").is_file())
        self.assertEqual((status, assignment, rounds), ("UNKNOWN", None, 3))
        self.assertIn("basis-delta-0004.json", artifacts)

    def test_frozen_caps_and_all_three_arm_names(self) -> None:
        self.assertEqual(
            (
                common.M["internal_seconds"],
                common.M["external_seconds"],
                common.M["external_kill_after_seconds"],
            ),
            (54, 60, 6),
        )
        self.assertEqual(
            common.M["arms"],
            [
                "COMPRESSED_SET_COVER_CP",
                "DETERMINISTIC_GREEDY_REPAIR",
                "SMALL_BASIS_CEGAR",
            ],
        )
        # The inherited run/CLI dispatch resolves these patched module globals.
        self.assertIs(constructor.v2.greedy, constructor.greedy)
        self.assertIs(constructor.v2.compressed_cp, constructor.compressed_cp)


if __name__ == "__main__":
    unittest.main()
