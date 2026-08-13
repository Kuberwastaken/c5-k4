# Method v0.20: WOWII 141 reusable third-leaf assembly

Date: 2026-08-13
Status: third-leaf assembly and exact girth-ten/eleven arithmetic verified;
global distance-four and local chord existence remain

## Next arithmetic rung

At girth ten or eleven, WOWII 141 requires

```text
max_v indepNeighborsCard(G,v) + 4 <= largestInducedTreeSize(G).
```

Thus the verified maximum local star must retain three tail vertices.

## Three-tail certificate

[`lean/GraphConjecture141GirthEleven.lean`](../../lean/GraphConjecture141GirthEleven.lean)
defines `ThreeVertexTailSplice G`, records the three genuinely new vertices,
and proves the exact cardinal identity

```text
|{center} union localSet union {first,second,third}|
  = max_v indepNeighborsCard(G,v) + 4.
```

It follows formally that this induced-tree certificate proves the exact
upstream inequality throughout `10 <= girth(G) <= 11`.

## Reusable third-leaf assembly

The more substantial result is `ThirdLeafData`.  It takes any already
verified `TwoVertexTailSplice` and a new vertex whose unique neighbor in the
entire retained tree is the old tail endpoint.

Lean proves that adjoining this third leaf preserves `IsTree`:

1. delete the new vertex from the enlarged induced graph;
2. construct the explicit graph isomorphism from that nested induced
   complement to the old two-tail induced graph;
3. transport the old `IsTree` certificate; and
4. invoke the generic unique-leaf extension theorem.

The result constructs `ThreeVertexTailSplice`; no final tree property is
assumed.  Therefore explicit third-leaf adjacency data alone closes the
girth-ten/eleven range.

## Remaining global and local work

Two existence statements remain before the range is unconditional:

1. **Global distance four.** A connected graph of girth at least ten should
   have, from every vertex, a vertex at distance at least four.  The natural
   proof extends the completed radius-two BFS contradiction to a radius-three
   layering, or proves the general bound `girth <= 2*radius+1`.
2. **Local fourth-prefix chord exclusions.** A shortest prefix
   `v-u-x-y-z` must make `z` uniquely adjacent to `y` in the retained
   star-plus-two-tail tree.  Every prohibited chord closes a cycle of length
   at most seven and should contradict girth at least ten.

The representation-heavy repeated-leaf assembly, exact cardinality, and
integer arithmetic are now complete.  Future work can focus exclusively on
these graph-existence and chord arguments.

## Verification

From the `formal-conjectures` checkout:

```bash
timeout 60s lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture141GirthEleven.lean
```

Result: exit 0.  The file contains no proof placeholders, native evaluation
shortcuts, or custom axioms.
