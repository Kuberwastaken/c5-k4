## Summary

Graffiti³ Conjecture 2 is false under the preprint's displayed formula and
literal closed-distance-two definition. A 25-vertex double star gives an exact
counterexample, and balanced double stars give an infinite counterexample
family.

The result was found prospectively by navigating away from the conjecture's
star equality wall. Two frozen arms independently reached the same canonical
graph.

## Counterexample

Let `DS(11,12)` be the tree obtained by joining the centers of stars with 11
and 12 leaves. Its 23 leaves form a maximum independent set. With `d₂(u)` the
number of vertices at distance at most two from `u`, including `u`,

- both centers have `d₂=25`;
- the 11 left leaves have `d₂=13`;
- the 12 right leaves have `d₂=14`.

Therefore

```text
alpha = 23,
RGA² = 1 + 55 sqrt(13)/19 + 40 sqrt(14)/13
     = 22.949914072489667... < 23.
```

The rational-square bounds `sqrt(13)<1803/500` and
`sqrt(14)<1871/500` give the exact upper certificate

```text
RGA² < 566921/24700 = 23 - 1179/24700.
```

For the balanced family,

```text
alpha(DS(k,k)) = 2k,
RGA²(DS(k,k)) = 1 + 4k sqrt(2(k+1)(k+2))/(3k+4),
```

which is below `2k` for every `k>=12`. The cleaner companion witness
`DS(12,12)` has `RGA² = 1+12 sqrt(91)/5 < 24 = alpha`.

## Immutable artifacts

- [Derivation, source/status audit, run chronology, and exact certificate](https://github.com/Kuberwastaken/c5-k4/blob/c936765/results/expansion/live-search-2026-08-14/graffiti3-conjecture2-result.md)
- [Independent standard-library verifier](https://github.com/Kuberwastaken/c5-k4/blob/66d3b1a/scripts/verify_graffiti3_conjecture2_double_star.py)
- [No-`sorry` Lean arithmetic certificate](https://github.com/Kuberwastaken/c5-k4/blob/88fd614/lean/Graffiti3Conjecture2Arithmetic.lean)
- [Frozen search contract](https://github.com/Kuberwastaken/c5-k4/blob/b168383/results/expansion/live-search-2026-08-14/graffiti3-conjecture2-contract.md)
- [Primary preprint](https://doi.org/10.21203/rs.3.rs-8493329/v1)

The Lean file proves the radical reductions, both strict arithmetic
inequalities, and an abstract `alpha>=23` refutation wrapper. Because the
current `formal-conjectures` corpus has no declaration of this Graffiti³
statement, it deliberately does not claim a full formalization of the graph,
distance-two invariant, or edge sum.

## Search and audit chronology

The database-sanity gate found exact equality precisely on the six nontrivial
Atlas stars. The frozen wall-navigation arm split the star hub; the separately
frozen catalogue arm reached the same double star. The generic arm exhausted
6,000 proposals without a crossing.

The first execution exposed the candidate but used integer-keyed `d₂` JSON
objects, making its internal ledger hashes non-replayable after parsing. That
run is rejected as release evidence. A serialization-only v1.1 replay retained
the identical proposal order and arithmetic; all three artifact checksums and
ledger chains replay, and both directed arms reproduce the same canonical
witness.

## Source, notation, and priority

The January 2026 source labels Conjecture 2 open and defines `d₂(u)` as the
number of vertices within distance at most two. The displayed edge formula is
unambiguous, although its RGA/2-degree naming differs from some established
index terminology.

A dated search through the source DOI and title, exact formula fragments,
later scholarly records, double-star/bistar and GA-index literature, and the
companion repository's branches, commits, issues, and pull requests found no
public proof, counterexample, erratum, or prior claim. “Apparently unrecorded
as of 2026-08-14” is a search-limited conclusion, not absolute priority.

## AI assistance disclosure

OpenAI Codex and delegated coding agents assisted with target selection,
source interpretation, frozen search design, independent verification,
formal certification, prior-art research, and release preparation. The
repository owner remains responsible for the mathematical claim and
attribution.
