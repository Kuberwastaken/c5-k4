#!/usr/bin/env python3
"""Pure contract helpers for the P1 production runtime closure.

This module has no launch, subprocess, filesystem, network, import-hook, or
fixture entry point.  The installed root-owned ELF executor implements the
contract; the bootstrap binds this source digest so its evidence vocabulary
cannot drift from the frozen exact-C review.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping


ARMS = ("CATALOGUE", "GENERIC", "WALL_NAVIGATION")
TREE_IDS = frozenset(f"{arm}-{index}" for arm in ARMS for index in range(8))
WALL_CAP_SECONDS = 60
ILP_CAP_SECONDS = 60
TREES_PER_ARM = 8
CPU_USEC_PER_TREE_MAX = 60_000_000
CPU_USEC_PER_ARM_MAX = 480_000_000
REQUIRED_ENFORCEMENT_FIELDS = frozenset({
    "descriptor_pinned_inputs", "network_denied", "whole_tree_cgroup_killed_or_reaped",
    "setsid_escape_contained", "descriptor_manifest_sha256", "namespace_inode_set_sha256",
    "process_tree_audit_sha256", "cgroup_v2_sha256", "evidence_locators",
})


class RuntimeContractError(ValueError):
    pass


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


def invocation_sha256(invocation: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_bytes(dict(invocation))).hexdigest()


def validate_completion_types(value: Mapping[str, Any]) -> None:
    """Reject Python bool/int aliasing and assertion-only completion shapes."""

    if value.get("network_denied") is not True or value.get("timed_out") is not False:
        raise RuntimeContractError("network/timeout evidence is not exact boolean truth")
    if type(value.get("returncode")) is not int or value["returncode"] != 0:
        raise RuntimeContractError("return code is not the non-boolean integer zero")
    if type(value.get("cpu_usec")) is not int or not 0 <= value["cpu_usec"] <= CPU_USEC_PER_TREE_MAX:
        raise RuntimeContractError("cgroup CPU evidence exceeds the tree budget")
    if type(value.get("wall_milliseconds")) is not int or not 0 <= value["wall_milliseconds"] <= 60_000:
        raise RuntimeContractError("monotonic wall evidence exceeds the tree cap")
    if not REQUIRED_ENFORCEMENT_FIELDS <= set(value):
        raise RuntimeContractError("kernel enforcement evidence closure is incomplete")
    if value.get("descriptor_pinned_inputs") is not True or value.get("whole_tree_cgroup_killed_or_reaped") is not True or value.get("setsid_escape_contained") is not True:
        raise RuntimeContractError("descriptor/cgroup/setsid evidence is not affirmative")
