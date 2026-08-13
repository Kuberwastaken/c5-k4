#!/usr/bin/env python3
"""Apply a frozen contamination inventory to the pre-contamination C0 pool."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


SCHEMA = "c5k4-eligible-cluster-pool-1.1"


def apply_contamination(pool: dict, inventory: dict) -> dict:
    pool_upstream = pool["upstream"]
    upstream = {
        "commit": pool_upstream["commit"],
        "tree": pool_upstream["tree"],
    }
    if inventory["upstream"] != upstream:
        raise ValueError("pool and contamination inventory upstream differ")

    contamination_rows = {row["cluster_id"]: row for row in inventory["clusters"]}
    if len(contamination_rows) != len(inventory["clusters"]):
        raise ValueError("duplicate contamination cluster_id")
    if {row["cluster_id"] for row in pool["clusters"]} != set(contamination_rows):
        raise ValueError("pool and contamination cluster sets differ")

    rows = []
    for source in pool["clusters"]:
        contamination = contamination_rows[source["cluster_id"]]
        if source["path"] != contamination["path"]:
            raise ValueError(f"path mismatch for {source['cluster_id']}")
        if source["module_blob_sha256"] != contamination["source_blob_sha256"]:
            raise ValueError(f"module blob mismatch for {source['cluster_id']}")
        source_names = [row["name"] for row in source["declarations"]]
        contamination_names = [row["name"] for row in contamination["declarations"]]
        if source_names != contamination_names:
            raise ValueError(f"declaration mismatch for {source['cluster_id']}")
        pre_eligible = source["eligible"]
        unexposed = contamination["exposure_status"] == "UNEXPOSED"
        eligible = pre_eligible and unexposed
        row = dict(source)
        row.update(
            pre_contamination_eligible=pre_eligible,
            eligible=eligible,
            stratum=source["stratum"] if eligible else None,
            eligibility_scope="CONTAMINATION_APPLIED",
            contamination_status=contamination["exposure_status"],
            contamination_basis=contamination["exposure_basis"],
        )
        rows.append(row)

    return {
        "schema_version": SCHEMA,
        "upstream": upstream,
        "contamination": {
            "applied": True,
            "inventory_sha256": inventory["inventory_sha256"],
            "identity_ambiguity_means_exclusion": True,
        },
        "clusters": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pool", type=Path, required=True)
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError("refusing to overwrite an existing contamination overlay")
    output = apply_contamination(
        json.loads(args.pool.read_text(encoding="utf-8")),
        json.loads(args.inventory.read_text(encoding="utf-8")),
    )
    args.output.write_text(
        json.dumps(output, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
