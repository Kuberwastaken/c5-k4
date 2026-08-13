# Method v1.2 source snapshot prototype

This directory contains protocol-development inputs only. Nothing here is S0.
Do not run the production form until the exact policy, this builder, and the P0
attestation schema are public in P0A/P0T.

## Safe pre-P0 dry run

`discover` without `--p0-attestation` always labels its output
`prototype_only: true`. Missing `ai-chats`, unsynchronized local session roots,
missing release exports, unsupported/unmerged worktree objects, and unknown
repository paths are reported as fail-closed completeness failures. Dirty
research worktrees are expected and are content-addressed, not rejected.

```sh
python3 scripts/build_benchmark_v12_source_snapshot.py discover \
  --projects-root /Users/kuber.mehta/Projects \
  --policy results/benchmark/v1.2-protocol/source-path-purpose-policy.json
```

The command reads directory names, Git object metadata, and exact current-tree
bytes solely to hash the worktree overlay. It does not decode or emit candidate
semantics, mutate a repository, fetch refs, or copy histories.

## Required post-P0 inputs

Before production discovery:

1. synchronize every local Codex and Claude JSONL source into a committed and
   published `ai-chats` repository;
2. preserve a JSON export of the complete c5-k4 GitHub release metadata at the
   cutoff;
3. ensure every relevant Git tip exists locally and leave each research
   worktree unchanged between discovery, S0, and contamination replay; and
4. retain the actual non-self-referential P0T artifact and separately record
   its exact public commit and remote URL. Its committed P0A must freeze the
   SHA-256 of the exact policy file and the
   `source_discovery_contract_sha256` printed by a pre-P0 dry run. That digest
   binds the projects root, ai-chats path, every local session mirror root and
   subtree, and every release export path; production discovery rejects any
   substitution.

The production discovery shape is:

```sh
python3 scripts/build_benchmark_v12_source_snapshot.py discover \
  --projects-root /Users/kuber.mehta/Projects \
  --policy results/benchmark/v1.2-protocol/source-path-purpose-policy.json \
  --ai-chats-repo /ABSOLUTE/PATH/TO/ai-chats \
  --session-mirror codex-local=codex:/ABSOLUTE/LOCAL/CODEX/SESSIONS:codex \
  --session-mirror claude-local=claude:/ABSOLUTE/LOCAL/CLAUDE/SESSIONS:claude \
  --release-snapshot c5-k4-github=/ABSOLUTE/PATH/releases.json \
  --p0-attestation /ABSOLUTE/PATH/p0-attestation.json \
  --p0t-commit EXACT_40_HEX_PUBLIC_COMMIT \
  --public-remote-url https://github.com/Kuberwastaken/c5-k4.git \
  --protocol-repo /Users/kuber.mehta/Projects/c5-k4 \
  --output /ABSOLUTE/PATH/sources-config.json
```

The mirror syntax is `ID=FORMAT:LOCAL_ROOT:AI_CHATS_SUBDIR`. Every retained
local `.jsonl` path and Git blob ID must occur in the pinned ai-chats subtree.
The archive may contain older files omitted by the local seven-day retention
window. A current path with stale bytes still fails without exposing turn text,
and the later scan covers the complete pinned archive subtree.

Acquire S0 only after inspecting machine-readable completeness fields and
recording the actual UTC cutoff:

```sh
python3 scripts/build_benchmark_v12_source_snapshot.py acquire \
  --sources-config /ABSOLUTE/PATH/sources-config.json \
  --policy results/benchmark/v1.2-protocol/source-path-purpose-policy.json \
  --p0-attestation /ABSOLUTE/PATH/p0-attestation.json \
  --p0t-commit EXACT_40_HEX_PUBLIC_COMMIT \
  --public-remote-url https://github.com/Kuberwastaken/c5-k4.git \
  --protocol-repo /Users/kuber.mehta/Projects/c5-k4 \
  --acquired-at 2026-08-13T00:00:00Z \
  --output /ABSOLUTE/PATH/source-snapshot-S0.json
```

Replace the sample timestamp; it is deliberately not inferred from the clock.
The acquisition command rechecks public P0T, exact Git tips, all corpus hashes,
all session mirrors, release bytes, and the complete staged/unstaged/untracked
worktree overlay. Any drift aborts without writing a partial manifest. The
overlay contains metadata and hashes only; the later contamination builder
must validate the same rows and scan their exact current bytes in addition to
the pinned Git history.
