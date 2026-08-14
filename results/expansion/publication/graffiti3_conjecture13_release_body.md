## Summary

Graffiti³ Conjecture 13 is false for its empirically selected base `b=2`.
The known base-two pseudoprime

```text
n = 81,722,145 = 3 * 5 * 17 * 29 * 43 * 257
```

also satisfies the conjecture's totient premise, so it is an exact finite
counterexample. The connection appears unrecorded after a dated public-source
search; the integer itself is not new.

## Counterexample

The printed implication is

```text
phi(n) <= (9/19)n  ==>  n is not a Fermat pseudoprime to base b,
```

with the source noting `b=2` empirically. For the witness,

```text
phi(n)        = 38,535,168,
19*phi(n)     = 732,168,192,
9*n           = 735,499,305,
9*n-19*phi(n) = 3,331,113 > 0,
2^(n-1) mod n = 1.
```

The six displayed factors are prime, so `3` is a proper divisor and `n` is
composite. It therefore satisfies the premise while being a base-two Fermat
pseudoprime, contradicting the implication.

## Immutable artifacts

- [Verified result, search chronology, source/status audit, and novelty qualification](https://github.com/Kuberwastaken/c5-k4/blob/6b9f184/results/expansion/live-search-2026-08-14/graffiti3-conjecture13-result.md)
- [Canonical machine-readable candidate](https://github.com/Kuberwastaken/c5-k4/blob/6b9f184/results/expansion/live-search-2026-08-14/graffiti3-conjecture13-candidate-81722145.json)
- [No-`sorry`, warning-clean standalone Lean certificate](https://github.com/Kuberwastaken/c5-k4/blob/4ee6967/lean/Graffiti3Conjecture13Arithmetic.lean)
- [External Lean validation run](https://github.com/Kuberwastaken/c5-k4/actions/runs/31798269800)
- [Frozen search contract](https://github.com/Kuberwastaken/c5-k4/blob/b1fd235/results/expansion/live-search-2026-08-14/graffiti3-conjecture13-contract.md)
- [Independent candidate verifier](https://github.com/Kuberwastaken/c5-k4/blob/b1fd235/scripts/verify_graffiti3_conjecture13_candidate.py)
- [Primary preprint](https://doi.org/10.21203/rs.3.rs-8493329/v1)
- [OEIS A328691, recording the witness's older abundancy-index property](https://oeis.org/A328691)

The Lean module imports Mathlib directly because this conjecture is not a
`google-deepmind/formal-conjectures` declaration. It proves the factorization,
factor primality, compositeness, exact totient, modular residue, strict margin,
pseudoprime predicate, and failure of the source-normalized implication. It
does not assert enumeration minimality.

## Search and method outcome

The database-sanity gate recomputed all 1,999,999 integers from 2 through the
source's stated cutoff `2,000,000` and found zero crossings. Beyond that gate,
72 isolated workers evaluated three frozen arms:

- the locked A001567 catalogue produced nine certificates;
- 6,291,456 integers in disjoint generic blocks produced none;
- the complete 10,107-number Korselt-extension wall produced none.

The canonical witness is A001567 index 1886 and the first crossing among the
1,532 locked sequence entries from the first value above the source cutoff
through that index. That does not prove it is the globally least integer
counterexample.

This run is positive evidence for the repository's broader discovery program,
but it is not another successful wall-navigation transfer: the predicted
Carmichael/Korselt separating family stayed safe, while the source-locked
pseudoprime catalogue found the crossing. That distinction is retained rather
than retrofitting the result into the stronger methodology claim.

## Source and priority

The January 2026 Research Square source labels Conjecture 13 open. A dated
search through the exact formula and number, DOI/title, scholarly web, OEIS,
GitHub code and issues, the author repository, and pseudoprime literature found
no public connection between this witness and the Graffiti³ conjecture.

The number `81,722,145` was already known as a Poulet number and appears in
OEIS A328691 for a different abundancy-index record. “Apparently unrecorded as
of 2026-08-14” describes only the disproof connection and is not an absolute
priority claim; private or unindexed work cannot be excluded.

## AI assistance disclosure

OpenAI Codex and delegated coding agents assisted with target selection,
source interpretation, frozen search design, independent verification,
formal certification, prior-art research, and release preparation. The
repository owner remains responsible for the mathematical claim and
attribution.
