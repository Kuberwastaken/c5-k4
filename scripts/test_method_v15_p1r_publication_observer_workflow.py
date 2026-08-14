#!/usr/bin/env python3
"""Adversarial static contract for the canonical P1R publication observer."""

import copy
from pathlib import Path
import unittest

import yaml


ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / ".github/workflows/method-v15-p1r-publication-observer.yml"
CHECKOUT = "actions/checkout@d23441a48e516b6c34aea4fa41551a30e30af803"


def validate(value: dict) -> None:
    if value.get("on") != {"push": {"branches": ["method-v1.5-p1r"], "paths": ["results/benchmark/v1.5-protocol/P1R.json"]}}:
        raise ValueError("non-canonical trigger")
    if value.get("permissions") != {"contents": "read"} or set(value.get("jobs", {})) != {"observe-exact-p1r-publication"}:
        raise ValueError("permissions/job closure")
    job = value["jobs"]["observe-exact-p1r-publication"]
    if job.get("runs-on") != "ubuntu-24.04" or len(job.get("steps", [])) != 2:
        raise ValueError("runner/step closure")
    checkout, observe = job["steps"]
    if checkout.get("uses") != CHECKOUT or checkout.get("with") != {"fetch-depth": "2", "persist-credentials": "false"}:
        raise ValueError("checkout closure")
    run = observe.get("run", "")
    if 'test "$GITHUB_RUN_ATTEMPT" = "1"' not in run or 'verify_benchmark_v15_p1r_publication.py --commit "$GITHUB_SHA"' not in run:
        raise ValueError("first-attempt strict validator absent")


class WorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.value = yaml.load(PATH.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)

    def test_exact_contract(self) -> None:
        validate(self.value)

    def test_broad_branch_tag_action_permissions_rerun_or_weak_validator_rejected(self) -> None:
        mutations = (
            lambda v: v["on"]["push"].__setitem__("branches", ["main"]),
            lambda v: v["permissions"].__setitem__("contents", "write"),
            lambda v: v["jobs"]["observe-exact-p1r-publication"]["steps"][0].__setitem__("uses", "actions/checkout@v6"),
            lambda v: v["jobs"]["observe-exact-p1r-publication"]["steps"][1].__setitem__("run", "true"),
        )
        for mutate in mutations:
            value = copy.deepcopy(self.value); mutate(value)
            with self.assertRaises(ValueError):
                validate(value)


if __name__ == "__main__":
    unittest.main()
