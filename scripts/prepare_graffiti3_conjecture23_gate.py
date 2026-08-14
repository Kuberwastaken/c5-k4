#!/usr/bin/env python3
"""Prepare the shared, content-addressed Conjecture 23 database gate."""

from __future__ import annotations

import argparse
from pathlib import Path

import search_graffiti3_conjecture23 as target


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--campaign-commit", required=True)
    parser.add_argument("--gap", default="gap")
    parser.add_argument("--manifest", type=Path, default=target.DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not (len(args.campaign_commit) == 40
            and all(c in "0123456789abcdef" for c in args.campaign_commit)):
        raise target.SearchError("campaign commit must be exact lowercase 40-hex")
    target.prepare_database_gate(
        args.gap, args.campaign_commit, args.manifest, args.output,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
