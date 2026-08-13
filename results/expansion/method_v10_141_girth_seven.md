# Method v0.10: WOWII 141 leaf-extension bridge

Date: 2026-08-13
Status: verified structural reduction for girth 6 and 7; the max-center
distance-two existence bridge remains open

## Result

The v0.9 certificate left one representation-sensitive step implicit: a
vertex attached as a leaf to an induced tree should preserve `IsTree`.  The
new file
[`lean/GraphConjecture141GirthSeven.lean`](../../lean/GraphConjecture141GirthSeven.lean)
now proves that graph lemma in full generality:

```text
H[{x}ᶜ] is a tree
and x has exactly one neighbor in H
  -> H is a tree.
```

The proof is direct rather than cardinality-based:

- connectivity is obtained by mapping paths from the induced complement and
  using the unique leaf edge;
- a cycle containing `x` is rotated to start at `x`, where its distinct first
  and last neighbors contradict uniqueness; and
- a cycle avoiding `x` is lifted into `H[{x}ᶜ]`, contradicting the base
  tree's acyclicity.

## Distance-two leaf data

`DistanceTwoLeafData G` is the strongest clean hypothesis reached in this
pass.  It records a center `v`, a globally maximizing local independent set
`A`, an extra vertex `x`, and an attachment `a in A`, with:

```text
x notin {v} union A,
x nonadjacent to v,
and, among A, x is adjacent exactly to a.
```

The file proves from these adjacency facts—not from an assumed tree field—that

```text
G[{x,v} union A] is a tree.
```

This produces the v0.9 `OneVertexSplice` automatically and proves the exact
upstream-shaped WOWII 141 inequality throughout the genuinely new range

```text
6 <= girth(G) <= 7.
```

under `DistanceTwoLeafData G`.

## Verification

From the `formal-conjectures` checkout:

```bash
timeout 60s lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture141GirthSeven.lean
```

Result: exit 0 in 7.0 seconds.  The certificate contains no proof
placeholders or custom axioms.

## Honest remaining boundary

The unconditional girth-six/seven theorem was not claimed.  What remains is
an existence theorem for `DistanceTwoLeafData` at a center maximizing
`indepNeighborsCard`.

Mathematically, girth at least six supplies the expected local facts:

- triangle-freeness makes the whole neighborhood independent;
- 4-cycle-freeness prevents a distance-two vertex from attaching to two
  retained neighbors; and
- a finite positive girth excludes the whole connected graph being merely a
  star.

The unresolved formal point is coordinating those facts at a center that
attains the global local-independence maximum and extracting the required
distance-two witness in the repository's girth API.  The v0.10 result reduces
that task to constructing `DistanceTwoLeafData`; all induced-subgraph,
unique-leaf, cardinality, and exact-invariant transport is complete.
