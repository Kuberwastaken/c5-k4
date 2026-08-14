# OEIS A105720 DEVELOPMENT freeze

This directory freezes a prospective, target-specific search. It is not a result,
claim, release, or authorization to dispatch the workflow.

This is a **DEVELOPMENT finite-search comparator**, not evidence of a genuine
invariant-wall transfer. `WALL_NAVIGATION` is an operational arm name for an
ordered interval plus a lossless square-residue screen; it is not a structural
separating family.

## Statement and status gate

The target is the `research open` theorem `OeisA105720.conjecture` at immutable
`google-deepmind/formal-conjectures` commit
`942fb149e782a56c2719c543ab58e093f733acb4`.  Its exact shape is

```lean
∀ n : ℕ, 0 < n → (IsSquare (a n) ↔ (n = 3 ∨ n = 6 ∨ n = 4072))
```

For positive `n`, `a n` is the sum of the one-based primes `p_n` through
`p_(2*n)`, inclusive.  A claimable witness is therefore a positive
`n ∉ {3,6,4072}` for which that integer is an exact square.  The gate rejects
any source, declaration shape, source-database control, or upstream identity
that differs from `manifest.json`.

## Frozen arms

All arms have 24 disjoint shards and use a reusable content-addressed prime
table prepared once by the gate.

* `CATALOGUE`: every `n` in `[21,20020]`.
* `WALL_NAVIGATION`: every `n` in `[20021,120020]`, exact-square tested after
  the frozen square-residue screen modulo `64,63,65,11`.
* `GENERIC`: 96,000 distinct points in `[120021,250020]` selected by the frozen
  affine permutation `(65537*i + 17389) mod 130000`.

The domains are pairwise disjoint.  Known indices are controls and can never
be emitted as certificates.

## Execution discipline

Each search process has a 60-second external cap and a 54-second internal
deadline. Preparation's prime-table constructor is an independently capped
four-second child. Every evaluated row is appended to a hash-chained JSONL
ledger and `fsync`ed. The terminal receipt binds the ledger SHA-256, last row,
counters, arm, shard, exact campaign commit, source identity, and gate
attestation. A certificate is checked by a separate implementation which
reconstructs the needed primes and sum without importing discovery code.

Postprocessing runs with shell `set +e`: gate, search, certificate, terminal,
status-receipt, and SHA failures are all recorded and the first failure is
propagated. Artifacts alone make no mathematical or novelty claim.
