# Graffiti³ Conjecture 2: double-star counterexamples

Date: 2026-08-14 UTC

Status: **VERIFIED NEW COUNTEREXAMPLE; RELEASE PENDING FORMAL CERTIFICATE**

Corrected replay commit: `79e9e0dc6790489f2e168a46661a0c971fe1191c`

Corrected GitHub Actions run:
[`31789142496`](https://github.com/Kuberwastaken/c5-k4/actions/runs/31789142496)

## Statement and source reading

Conjecture 2 of Randy Davila's January 2026 preprint
[*Graffiti³: Compact Theory Libraries for Automated Mathematical Discovery*](https://doi.org/10.21203/rs.3.rs-8493329/v1)
asserts that every nontrivial connected graph satisfies

```text
alpha(G) <= RGA2(G),
RGA2(G) = sum_{uv in E(G)} 2 sqrt(d2(u)d2(v))/(d2(u)+d2(v)),
```

where `d2(u)` is the number of vertices within distance at most two of `u`.
The literal closed-ball reading includes `u`, since its distance from itself is
zero. The displayed formula is unambiguous even though the manuscript's index
name differs from some conventional GA/RGA nomenclature.

## Search hit

Let `DS(11,12)` have adjacent centers `x,y`, 11 leaves adjacent only to `x`,
and 12 leaves adjacent only to `y`. It is a connected 25-vertex tree. All 23
leaves are independent, and no larger independent set exists, so

```text
alpha(DS(11,12)) = 23.
```

The closed distance-two ball sizes are

```text
d2(x) = d2(y) = 25,
d2(a) = 13  for each of the 11 left leaves,
d2(b) = 14  for each of the 12 right leaves.
```

Therefore

```text
RGA2(DS(11,12))
  = 1 + 55 sqrt(13)/19 + 40 sqrt(14)/13
  = 22.949914072489667... < 23.
```

An exact rational-square certificate is

```text
sqrt(13) < 1803/500, because 1803^2 - 13*500^2 = 809 > 0,
sqrt(14) < 1871/500, because 1871^2 - 14*500^2 = 641 > 0.
```

It follows that

```text
RGA2(DS(11,12))
  < 1 + (55/19)(1803/500) + (40/13)(1871/500)
  = 566921/24700
  = 23 - 1179/24700 < 23 = alpha.
```

The frozen catalogue and wall-navigation arms reached the same canonical graph
independently, after 99 and 85 exact unique evaluations respectively. The
generic arm exhausted all 6,000 proposals (5,818 isomorphism-unique graphs)
without a crossing.

## Family explanation

For the balanced double star `DS(k,k)`, the two centers have closed `d2` value
`2k+2`, every leaf has value `k+2`, and all `2k` leaves form a maximum
independent set. Hence

```text
alpha(DS(k,k)) = 2k,
RGA2(DS(k,k)) = 1 + 4k sqrt(2(k+1)(k+2))/(3k+4).
```

The inequality reverses for every `k >= 12`. After moving the positive terms
and squaring, the strict gap is equivalent to positivity of

```text
4k^4 - 36k^3 - 87k^2 - 40k + 16.
```

This polynomial is `7744` at `k=12` and increasing thereafter. The especially
clean witness `DS(12,12)` has

```text
alpha = 24,
RGA2 = 1 + 12 sqrt(91)/5 = 23.894540834... < 24.
```

An exact enumeration of the double-star parameter pairs shows that order 25
is the first order at which this family crosses; this is not a global
minimum-counterexample claim.

## Evidence and novelty discipline

The first run at commit `b168383` exposed the candidate but used integer-keyed
JSON objects for `d2`. Parsing changes those keys to strings and made the
internal row hashes non-replayable for two-digit labels. Artifact-level
checksums were intact, but that ledger is rejected as release evidence. The
version 1.1 replay changed only `d2` serialization and the ledger schema. All
three corrected artifact checksum manifests and all three ledger chains replay
exactly; both directed arms reproduce the same graph and exact upper bound.

A separate search through 2026-08-14 covered the exact title, DOI, displayed
formula, invariant variants, double-star/bistar terminology, later scholarly
records, the companion repository's branches, commits, issues and pull
requests, and related GA-index literature. It found no public resolution or
claim to this counterexample. The source remains a January 2026 v1 preprint;
no later version or erratum was found. This cannot exclude private or
unindexed work, but it clears the repository's public novelty gate.

The frozen [contract](graffiti3-conjecture2-contract.md) and
[manifest](graffiti3-conjecture2-manifest.json) preserve the pre-search and
serialization-replay chronology. A release requires the pending warning-clean,
no-`sorry` Lean arithmetic certificate; no upstream issue or pull request is
opened automatically.
