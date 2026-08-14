# V2.1 operational correction

- Supersedes operational execution of v2; it does not rewrite v2 history.
- Cause: Python 3.9 has no `int.bit_count()` method.
- Observed scope: every one of the 18 round-zero constructors in GitHub Actions
  run `31809864013` failed at that method.
- Mathematical standing of v2 run: no assignment reached the exact adversary;
  no candidate and no counterexample were produced, so there is no mathematical result.
- Correction: explicit Python-3.9-compatible population count, plus synthetic
  executable smoke coverage for all three constructor paths.
- Unchanged cap: 54 seconds internal, 60 seconds external, 6-second kill grace.
- Unchanged trust boundary: exact source gate, hash-chained evidence,
  fail-closed predecessor validation, exact adversary, independent final.
