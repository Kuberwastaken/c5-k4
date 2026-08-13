# Method v0.4: WOWII 133 geodesic-to-induced-list bridge

Status: **PROVED LOCALLY / NO SORRY**

Date: **2026-08-13 UTC**

Local artifact: `lean/GraphConjecture133Cubic.lean`

This follow-up addresses only the first missing lemma recorded in
`method_v04_133_lean.md`.  It does not attempt the radius selection, cubic
neighbor arguments, local-independence split, or four-forward-neighbor lemma.

## Compiled theorem

```lean
lemma isInducedPath_support_of_length_eq_dist
    {G : SimpleGraph V} {u v : V}
    (p : G.Walk u v) (hp : p.length = G.dist u v) :
    G.isInducedPath p.support
```

The theorem needs no finiteness, decidable-equality, or nonemptiness assumption.
It uses `Walk.support` as the canonical ordered vertex list, exactly matching
the list accepted by the repository-local `SimpleGraph.isInducedPath`.

## Proof structure

The target predicate has two parts.

1. **No repeated vertices.** Mathlib's
   `Walk.isPath_of_length_eq_dist hp` proves that a shortest walk is a path;
   `Walk.IsPath.support_nodup` gives `p.support.Nodup` directly.
2. **Adjacency iff consecutive indices.** The existing
   `Walk.getVert_comp_val_eq_get_support` rewrites `p.support.get i` as
   `p.getVert i`.  Consecutive indices are adjacent by
   `Walk.adj_getVert_succ`.

For the reverse direction, suppose `i<j` and the vertices at `i,j` are
adjacent.  The proof constructs the walk

```text
(p.take i) ++ edge(getVert i, getVert j) ++ (p.drop j).
```

Its length is

```text
i + 1 + (p.length - j).
```

Since `p.length = dist u v`, `SimpleGraph.dist_le` applied to the shortcut
forces `j ≤ i+1`; together with `i<j`, this gives `j=i+1`.  The case `j<i` is
symmetric.  Equality `i=j` contradicts graph looplessness.  This proves the
full biconditional required by `isInducedPath`, not merely chordlessness or
`Walk.IsPath`.

## API findings

The bridge required no new projection.  The relevant existing APIs are:

- `Walk.support`, with `Walk.length_support`;
- `Walk.getVert_comp_val_eq_get_support`;
- `Walk.adj_getVert_succ`;
- `Walk.take`, `Walk.drop`, and their length lemmas;
- `Walk.append` and `Walk.length_append`;
- `Walk.isPath_of_length_eq_dist`;
- `SimpleGraph.dist_le`.

The earlier apparent gap was therefore a missing composition lemma rather than
a representation impossibility.  The new theorem is that composition lemma.

## Verification

Every compile was explicitly capped at 60 seconds.  Final command:

```text
timeout 60s lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture133Cubic.lean
```

Result: exit status `0` in approximately 6.3 seconds.  The file contains no
`sorry`, `admit`, or custom axiom.

## Next boundary

The first bridge from the prior plan is now closed.  Per the frozen scope, no
later cubic lemma was attempted.  The next independent task would be selecting
a finite radius-realizing shortest walk and proving its support length is
`G.radius.toNat + 1`; that is intentionally outside this follow-up.
