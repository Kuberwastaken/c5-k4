# Method v0.21: #183 two-deletion trunks

## Corrected threshold

The numerical repair is now formal:

```text
|T| + 2 <= n
n <= |B| + 1
----------------
|T| + 1 <= |B|.
```

The final line is exactly the local budget after adding the mandatory
attachment vertex.  `TwoDeletionComponentData` packages the corresponding
graph facts, and `twoDeletionComponent_local_package` feeds them directly to
the v0.14 fold.

## Odd-cycle geometry

For a cycle, deleting two adjacent vertices leaves a connected path.  The pair
must be chosen so that each deleted vertex retains a neighbor outside the pair;
this excludes the triangle, where deleting an adjacent pair leaves a singleton
and neither deleted vertex has a distinct retained neighbor in the required
configuration.

The exact structural predicate `IsGoodTwoDeletion` requires:

- a distinct adjacent pair;
- connected and bipartite complement of the pair; and
- a retained neighbor dominating each deleted vertex.

Lean proves that the retained complement is connected dominating and induced
bipartite.  For odd cycles of length at least five, any adjacent pair satisfies
this geometry.  The remaining formal step is a concrete cycle-family model (or
a general cycle API theorem) connecting that familiar fact to
`IsGoodTwoDeletion` and transporting the retained finset into an outside
component.

Thus the one-deletion obstruction is overcome on the correct structural class;
the exceptional odd cycle is `C3`, which needs a different local branch.

## Verification

The strict command was:

```bash
LEAN_PATH=/tmp/c5k4_183_attachment_selection_v1 timeout 60s lake env lean \
  -DwarningAsError=true \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture183TwoDeletionTrunk.lean
```

Result: exit code `0`.  The module contains no `native_decide`, `sorry`,
`admit`, `#print`, or custom axiom declaration.
