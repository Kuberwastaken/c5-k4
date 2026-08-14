#!/usr/bin/env python3
"""Read-only verifier for the frozen TxGraffiti product campaign files."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[4]
MANIFEST = Path(__file__).with_name("manifest.json")


def main() -> int:
    value = json.loads(MANIFEST.read_text())
    errors: list[str] = []
    if value.get("status") != "FROZEN_UNEXECUTED_DEVELOPMENT":
        errors.append("status is not the frozen unexecuted state")
    if value.get("internal_wall_seconds") != 54 or value.get("external_wall_seconds") != 60:
        errors.append("runtime caps differ from 54/60 seconds")
    if value.get("arms") != ["CATALOGUE", "GENERIC", "WALL_NAVIGATION"]:
        errors.append("arm list differs from the frozen triplet")
    for relative, expected in value.get("frozen_files", {}).items():
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing: {relative}")
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected:
            errors.append(f"sha256 mismatch: {relative}: {actual}")
    if errors:
        print("FREEZE_INVALID")
        print("\n".join(errors))
        return 1
    print(f"FREEZE_OK files={len(value['frozen_files'])} campaign_id={value['campaign_id']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
