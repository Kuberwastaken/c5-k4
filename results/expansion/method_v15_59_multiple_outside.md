# Method v0.15: WOWII 59 pairs of dense outside rows

Date: 2026-08-13

## Scope

This pass performs the first complete two-outside-vertex audit over the dense
`3+3` cores isolated in v0.14, then formalizes the strongest universal pair-row
structure. WOWII 59 is already externally disproved; this is theorem
extraction, not a novelty or held-out claim.

## Exact pair audit

The 16 labelled dense attachment rows from v0.14 were paired with replacement.
For each unordered pair, both possibilities for the edge between the two
outside vertices were tested over each core:

```text
cores: K3,3 and K3,3-e
dense rows per outside vertex: 16
unordered row pairs with replacement: 136
outside-pair adjacency: absent or present
rows per core: 272
total rows: 544
```

Every eight-vertex graph was evaluated exactly by descending subset
enumeration for `b` and `f`, and by Havel--Hakimi reduction for residue. The
complete audit finished in 3.4 seconds.

### Complete outcomes

| core | `(b,f,residue)` | rows |
|---|---:|---:|
| `K3,3` | `(6,4,2)` | 185 |
| `K3,3` | `(6,5,2)` | 87 |
| `K3,3-e` | `(6,4,2)` | 113 |
| `K3,3-e` | `(6,5,2)` | 159 |

Thus:

- all 544 rows retain `b=6`—no larger induced bipartite exchange appears at
  the level of the full eight-vertex induced graph;
- 246 rows force `f=5` and are incompatible with the corner;
- the remaining 298 rows retain `f=4`;
- **every one of all 544 rows has residue exactly two**;
- zero rows have the corner-compatible triple `(b,f,residue)=(6,4,3)`.

The last fact is exact for the eight-vertex extension, not for an arbitrary
larger ambient graph. Further outside vertices can change the ambient degree
sequence.

## Universal pair-row overlap theorem

The strongest invariant-independent mechanism is a pigeonhole constraint.
On either core color side there are three vertices. Each exchange-resistant
outside row uses at least two of them. Therefore two such rows overlap on that
side:

```text
|A_k(x)| >= 2,
|A_k(y)| >= 2,
A_k(x), A_k(y) subset of a 3-set
  => A_k(x) intersect A_k(y) is nonempty.
```

Applying this for `k=0` and `k=1` proves that every pair of dense outside
vertices has two distinct common core neighbors, one in each color class.

If the outside vertices are adjacent, those two common neighbors close two
triangles on the same outside edge, one through each core color. This gives a
strong local obstruction that is invisible in the single-row analysis.

## Formal artifact

[`lean/GraphConjecture59MultipleOutside.lean`](../../lean/GraphConjecture59MultipleOutside.lean)
proves without computation:

1. nonempty intersection of two dense attachment rows in one color class;
2. existence of a common neighbor in each color;
3. existence of two distinct opposite-color common neighbors;
4. when the outside pair is adjacent, existence of two explicit 3-cliques
   sharing that outside edge.

The intersection proof uses finite inclusion-exclusion:

```text
|A union B| + |A intersect B| = |A| + |B|,
```

with `|A union B|<=3` and both row sizes at least two.

## Verification

After compiling the warning-clean v0.8-v0.14 dependencies into temporary
`.olean` files, the new module was checked with

```text
LEAN_PATH=/tmp lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture59MultipleOutside.lean
```

It completed in 9.7 seconds with no warnings or errors. The file contains no
`sorry`, `admit`, custom axiom, `native_decide`, or imported upstream
conjecture proof.

## Interpretation

The exhaustive pair audit materially strengthens the residue signal:

- all 32 one-outside extensions had residue two;
- now all 544 two-outside extensions also have residue two;
- this remains true whether the outside pair is adjacent or nonadjacent;
- nearly 55% of pair rows retain `f=4`, so forest-number exclusion alone still
  cannot explain the zero corner.

The formal overlap theorem suggests the next global coordinate. Dense outside
rows form a highly intersecting family on each three-vertex color class.
Because the possible subsets are only the three 2-subsets and the full
3-subset, several outside vertices must repeat or strongly align attachment
patterns. A next exact theorem should classify triples of rows up to the
`S_3 x S_3` core symmetry and convert repeated patterns into either a
five-vertex forest or a degree-sequence/residue potential bound.

## Outcome

`EXACT_PAIR_AUDIT_PLUS_COMMON_NEIGHBOR_THEOREM`.

No pair extension realizes the low-residue corner. Universally, every dense
outside pair shares distinct common neighbors of both colors, and adjacent
pairs close two triangles. The remaining gap is accumulation over arbitrarily
many outside vertices and its effect on the ambient Havel--Hakimi sequence.
