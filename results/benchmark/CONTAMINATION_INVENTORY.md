# Method v1.1 contamination inventory

This directory contains a source-configuration **example**, not a frozen C0
pool and not a benchmark target list. The builder is
[`scripts/build_benchmark_contamination_inventory.py`](../../scripts/build_benchmark_contamination_inventory.py).
Do not run the example directly: the builder rejects `template_only: true`.

The inventory is intentionally semantics-blind. At a pinned
`formal-conjectures` commit it reads only paths, `research open` annotations,
declaration names, and source bytes. It conservatively groups all open
declarations in one source module. It then searches frozen histories,
worktrees, release metadata, unversioned trees, and natural-language agent
turns for aliases generated from that registry metadata. Tool outputs are
excluded because a registry dump is not evidence that a target was considered.
The output records source/unit hashes and locators but no matched prose.

## Freeze procedure

1. Before C0, discover all research repositories, unversioned trees, release
   records, and agent-session stores without consulting candidate semantics.
2. Copy live or append-only inputs, especially sessions and release metadata,
   into immutable snapshots. Record the acquisition command and snapshot hash
   outside the source manifest.
3. Copy the example configuration, replace every placeholder, enumerate every
   discovered source, and set `template_only` to `false`.
4. Pin the exact upstream commit/tree and run the builder once against those
   immutable inputs. Freeze the configuration and inventory hashes in C0.
5. Any failed or omitted source makes otherwise unmatched units ineligible.
   Do not repair a sparse stratum by weakening this rule.

## Conservative limits

- A source module is only a provisional cluster. Siblings in different files,
  renamed declarations, aliases absent from registry metadata, and cross-corpus
  equivalents cannot be resolved without semantics. Identity ambiguity means
  exclusion during the later machine-only grouping review.
- A direct alias hit may be a false positive. That is acceptable here:
  `EXPOSED` is an exclusion decision, not a claim that substantive analysis
  occurred.
- A content-only match with no identity alias can be missed. Therefore all
  source discovery must be frozen before selection, and unexplained gaps or
  missing synchronized histories fail closed.
- `git_delta` excludes all commits reachable from the configured vendor-ref
  prefix. Use it only for a declaration-registry fork and separately include
  every campaign/sibling repository that contains user work.
- Registry-only exemptions are exceptional. They remove whole hashed scan
  units, so a mixed unit containing registry text and research discussion must
  never be exempted. Any exemption file is itself content-addressed in the
  inventory.
- The inventory does not classify strata, rank units, or select targets.

Example invocation after creating real immutable snapshots:

```bash
python3 scripts/build_benchmark_contamination_inventory.py \
  --formal-repo /absolute/path/to/formal-conjectures \
  --formal-ref <40-or-64-hex-commit> \
  --config results/benchmark/contamination-sources.c0.json \
  --output results/benchmark/contamination-inventory.c0.json
```
