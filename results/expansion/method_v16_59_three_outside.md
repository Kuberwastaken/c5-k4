# Method v0.16: WOWII 59 three dense outside rows

Date: 2026-08-13

## Scope

This pass exhausts triples of dense attachment rows over the two explicit
`3+3` cores and formalizes the resulting three-row incidence dichotomy. WOWII
59 is already externally disproved; this is structural proof extraction, not a
novelty or held-out claim.

## Exact triple audit

The 16 dense labelled rows from v0.14 were chosen with replacement in unordered
triples. Every one of the eight graphs on the three outside vertices was then
added:

```text
cores: K3,3 and K3,3-e
row multisets: C(16+3-1,3) = 816
outside adjacency patterns: 2^3 = 8
rows per core: 6,528
total raw rows: 13,056
```

Each nine-vertex graph was evaluated by independent bit-mask routines:

- bipartiteness by explicit two-color traversal;
- acyclicity by union-find cycle detection;
- Havel--Hakimi residue from its degree list.

The complete run finished in 17.22 seconds, below the fixed 60-second cap.

### Symmetry reduction

Rows were canonicalized under simultaneous permutation of the three outside
vertices and side-preserving core symmetries:

- `S3 x S3` on the two sides of `K3,3`;
- permutations fixing each endpoint of the missing edge on `K3,3-e`.

The outside permutation acts on both attachment rows and the outside adjacency
graph. This yields 2,426 exact canonical orbits. Side-swapping symmetries were
not used, so this is a conservative orbit quotient rather than a minimum
uncolored-isomorphism count.

## Raw outcomes

### `K3,3`

| `(b,f,residue)` | rows |
|---|---:|
| `(6,4,2)` | 2,074 |
| `(6,5,2)` | 4,343 |
| `(7,5,2)` | 66 |
| `(7,6,2)` | 36 |
| `(7,6,3)` | 9 |

### `K3,3-e`

| `(b,f,residue)` | rows |
|---|---:|
| `(6,4,2)` | 1,114 |
| `(6,5,2)` | 5,264 |
| `(6,5,3)` | 3 |
| `(6,6,2)` | 36 |
| `(7,5,2)` | 50 |
| `(7,6,2)` | 46 |
| `(7,6,3)` | 15 |

There are zero raw rows and zero canonical orbits with

```text
(b,f,residue) = (6,4,3).
```

Unlike the one- and two-outside audits, residue three finally appears—but every
such row is already excluded by `f>=5` or `b>=7`. All 3,188 raw rows retaining
the corner values `b=6,f=4` still have residue two.

At orbit level the corner-compatible count remains zero. The unique
`K3,3` residue-three orbit has `(7,6,3)`; the ten `K3,3-e` residue-three orbits
have `(6,5,3)` or `(7,6,3)`.

## Formal three-row incidence theorem

On one three-vertex color side, let `A,B,C` be the attachment sets of three
dense outside rows. Each is a subset of a common three-set and has size at
least two. There is an exact dichotomy:

```text
A intersect B intersect C is nonempty,
```

or

```text
|A|=|B|=|C|=2 and A,B,C are pairwise distinct.
```

Why this is exact:

- if any row has size three, it is the whole color class, and the other two
  size-at-least-two rows intersect;
- if two rows coincide, their common two-set intersects the third row;
- therefore failure of triple intersection forces three distinct two-subsets;
- conversely the three distinct two-subsets of a three-set have empty triple
  intersection.

Thus each color side is either **aligned** around a vertex shared by all three
outside rows, or is the unique **rotating-complement** pattern where the three
rows omit three different core vertices.

## Formal artifact

[`lean/GraphConjecture59ThreeOutside.lean`](../../lean/GraphConjecture59ThreeOutside.lean)
proves without computation:

1. the two-large-subsets intersection lemma on a three-set;
2. the exact three-subset classification above;
3. its specialization to three dense graph attachment rows on each color side.

## Verification

After compiling the warning-clean v0.8-v0.15 dependencies into temporary
`.olean` files, the module was checked with

```text
LEAN_PATH=/tmp lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture59ThreeOutside.lean
```

It completed in 6.1 seconds with no warnings or errors. The file contains no
`sorry`, `admit`, custom axiom, `native_decide`, or imported upstream
conjecture proof.

## Interpretation

The exact residue signal has now survived three expansion levels:

- every one-outside extension has residue two;
- every two-outside extension has residue two;
- with three outside vertices, residue three can occur, but never while both
  `b=6` and `f=4` survive.

The formal incidence theorem reduces arbitrary triples to two patterns per
color side. Combining the sides gives four coarse regimes:

1. aligned/aligned;
2. aligned/rotating;
3. rotating/aligned;
4. rotating/rotating.

These are the natural next formal cases. In an aligned side, one core vertex is
adjacent to all three outside vertices. In a rotating side, every core vertex
is omitted once and used twice. Those sharply different degree contributions
should make the Havel--Hakimi or forest/bipartite obstruction tractable without
enumerating all 16^3 labelled rows again.

## Outcome

`EXACT_TRIPLE_ORBIT_AUDIT_PLUS_INCIDENCE_DICHOTOMY`.

No three-row extension realizes the low-residue corner. Residue-three rows
appear for the first time but are always excluded by another corner invariant.
Formally, every color side is now reduced to aligned or rotating-complement
incidence.
