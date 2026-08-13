# Method v1.1 C0 machine freeze

This directory is preparation for a prospective freeze. It contains no C1
selection and no semantic evaluation of a benchmark target.

The upstream registry is pinned to
`google-deepmind/formal-conjectures@7a38c469ec329d0c97c068e03c58834f61628e7e`
with tree `daa36d0d9e82133dfd83488d89594d92b4940fb7`. The inventory and pool
are built directly from that Git tree. They expose path/declaration syntax
metadata and hashes, never statement text.

`question-cluster-pool.json` conservatively merges every open declaration in a
source module. Its `eligible` field is explicitly **pre-contamination**:
`true` means only that the fixed syntax classifier assigned one unambiguous
stratum. C1 selection must consume a contamination-applied overlay satisfying

```text
final eligible = pre-contamination eligible AND inventory status UNEXPOSED.
```

The pool must not be sampled directly. Identity uncertainty, incomplete scans,
and ambiguous cross-module siblings all fail closed.

The C0 artifact commit cannot contain its own commit hash. The manifest must
therefore be constructed only after the final contamination overlay,
randomness contract, and selector schema are fixed. Its artifact commit leaves
the chronology placeholders null; after that commit is public, an attestation
commit may fill `c0_commit` and `c0_published_at_utc`, set `phase` to
`C0_FROZEN`, and must still leave the future randomness value and all
C1/evaluation fields null.

Deterministic replay:

```bash
PYTHONPATH=scripts python3 -m unittest scripts/test_build_benchmark_c0_pool.py
python3 scripts/build_benchmark_c0_pool.py \
  --formal-repo /Users/kuber.mehta/Projects/formal-conjectures \
  --formal-ref 7a38c469ec329d0c97c068e03c58834f61628e7e \
  --classifier results/benchmark/c0/five-strata-classifier.json \
  --inventory results/benchmark/c0/open-inventory.json \
  --pool results/benchmark/c0/question-cluster-pool.json
```
