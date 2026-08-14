# Wave 2 live-search runtime increment — 2026-08-14

Status: **implemented and locally tested; live-development support only**

This increment adds the minimum runtime semantics exposed by the baseline
replay without changing the frozen search families or the Method v1.5 triplet
infrastructure:

- `scripts/method_v15_live_search_runtime.py` imports the existing v1.5
  triplet runtime for the three arm names, canonical JSON encoding, and the
  fixed 60-second cap.
- Graph identity is the exact canonical graph6 row returned by a required,
  frozen nauty `labelg` executable. There is no WL/hash or labelled-graph6
  fallback. The returned graph is independently checked for isomorphism before
  its domain-separated SHA-256 is accepted.
- Each worker gets a fresh per-tree JSONL file. The start checkpoint, every
  exact evaluation, explicit checkpoints, and the completed summary are each
  appended, flushed, and `fsync`ed immediately in a hash chain.
- Every row carries the same five cumulative counters: `proposed`,
  `canonical_unique`, `hypothesis_survivor`, `exact_evaluated`, and
  `objective_scored`.
- The `run` subcommand starts a new process group and enforces the fixed
  60-second cap on the whole group, with TERM followed by KILL after one second.
  A timeout preserves and accepts only a nonempty valid JSONL prefix.
- `scripts/lint_method_v15_live_search_output.py` rejects empty/noncanonical or
  truncated JSONL, broken row chains/digests, mixed identities, inconsistent or
  regressing counters, duplicate evaluated canonical identities, rows beyond
  the wall cap, missing successful summaries, and graph6 rows that do not
  replay to the exact `labelg` canonical form.

## Tests run

```text
python3 -m py_compile scripts/method_v15_live_search_runtime.py scripts/lint_method_v15_live_search_output.py scripts/test_method_v15_live_search_runtime.py
python3 scripts/test_method_v15_live_search_runtime.py -v
python3 scripts/test_method_v15_triplet_production_adapter.py -q
python3 scripts/test_run_benchmark_v15_triplet.py -q
```

Result: seven tests passed. They cover exact relabeling deduplication, a durable
prefix before summary, stage-separated counters, linter corruption detection,
fail-closed bad canonicalizer output, stale-output rejection, and hard killing
of a TERM-ignoring worker. The existing production-adapter and triplet-runner
suites also passed (10 and 11 tests respectively).

An end-to-end `GENERIC-0` wrapper smoke test also completed in 216 ms, emitted
three durable rows (start, evaluated candidate, summary), and passed the
standalone linter.

## Real-arm invocation

A real worker imports `ScientificJsonl`, `LabelgCanonicalizer`, and
`GraphSearchRecorder`; constructs both first objects with `from_environment()`;
calls `recorder.evaluate(graph, hypothesis, evaluator)` for each proposal; and
calls `ledger.finish()` after its proposal loop. The evaluator returns an exact
`objective` (`int`, exact string, or null), a boolean `crossing` when scored,
and any target-specific payload fields.

The sealed tree launcher invokes that worker through the cap wrapper:

```text
python3 scripts/method_v15_live_search_runtime.py run \
  --arm GENERIC \
  --tree-index 0 \
  --output /private/results/generic-0.jsonl \
  --labelg /frozen/tools/nauty/labelg \
  -- python3 /frozen/arms/generic_graph_arm.py
```

The wrapper supplies `C5K4_ARM`, `C5K4_TREE_INDEX`,
`C5K4_SCIENTIFIC_JSONL`, and `C5K4_LABELG` to the worker, kills its complete
process group at 60 seconds, and runs the scientific linter before accepting
either a completed stream or a valid timeout prefix. The production envelope
must bind the exact `labelg` executable digest and worker argv as it binds the
other per-tree inputs.
