# Method v0.34: scalable tail assembly and WOWII #141 through girth fifteen

Date: 2026-08-13
Status: original conjecture closed for every connected graph of girth at most fifteen

## Result

[`lean/GraphConjecture141GirthFifteenClosure.lean`](../../lean/GraphConjecture141GirthFifteenClosure.lean)
turns the v0.33 distance-six witness into an induced tree of size
`maximum local independence + 6`.  It proves WOWII #141 for girth fourteen
and fifteen and exports `conjecture141_of_girth_le_fifteen`.

## Scalable representation

The new `SixEdgeGeodesicPrefix` stores one path, its exact length, simplicity,
and geodesicity instead of expanding every vertex and chord into structure
fields.  Two generic metric facts then replace the earlier bespoke chord
tables:

- the distance from the start to `path.getVert j` is exactly `j`;
- for `3 <= j <= 6`, vertex `j` has no neighbor in the initial open
  neighborhood and is adjacent among earlier prefix vertices exactly to
  vertex `j - 1`.

Both are immediate shortest-path consequences.  A neighbor in the initial
neighborhood would give distance at most two, and any nonconsecutive prefix
edge would shorten the prefix.

## Generic leaf extension

`induce_insert_isTree_of_isTree_of_unique_adj` is an ambient-finset theorem:
if an induced graph on `B` is a tree and a fresh vertex has exactly one
neighbor in `B`, inserting that vertex preserves the induced-tree property.
This packages the subtype-complement isomorphism once and is reusable for
every later tail rung.

Starting with the certified local star plus the distance-two vertex, the
module applies this theorem successively to prefix vertices 3, 4, 5, and 6.
The final retained finset has exactly

```text
maximum local independence + 6
```

vertices.  Since `girth / 2 <= 7` at girth fourteen or fifteen, this proves
the original inequality.

## Verification

The complete #141 chain from `GraphConjecture141Extraction` through
`GraphConjecture141GirthFifteenClosure` was rebuilt from source in a fresh
temporary directory.  Every Lean process used `-DwarningAsError=true`, was
individually capped at 60 seconds, and exited successfully.  The new module
contains no `sorry`, `admit`, `native_decide`, `#print`, or custom axiom.
