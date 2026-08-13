# Method v1.4 terminal pre-C0 result

Method v1.4 completed its sole preregistered registry build and terminated at
the DB-sanity gate with `NO_ELIGIBLE_BENCHMARK_PRE_C0`.

- Frozen design: 12 clusters with quotas `3/3/2/2/2` and equal-budget
  Catalogue, Generic, and Wall-Navigation arms.
- Upstream: `google-deepmind/formal-conjectures` commit
  `158727e43d3be335f902ac7ef6b9beb819e38c9d`.
- Registry population: 728 open question clusters.
- Eligible after exact S0 contamination replay: 0.
- Entropy used: no.
- Clusters selected: 0.
- C0 created: no.
- Retry, repin, or relaxed exclusion: no.

[`F0A.json`](F0A.json) is the non-self-referential failure artifact. The
preflight input, both raw resolver receipts, exact registry-build input, six
production registry artifacts, and the producer envelope are preserved here.
The 101,190,589-byte provenance inventory exceeds GitHub's ordinary per-file
limit, so that one exact JSON file is stored through Git LFS; its SHA-256 is
recorded in `F0A.json` and the registry output envelope.

The five stratum counts replay as `0/3`, `0/3`, `0/2`, `0/2`, and `0/2`.
Accordingly, the frozen stopping rule forbids C0, randomness retrieval,
selection, evaluation, backfill, or another registry build under v1.4.
