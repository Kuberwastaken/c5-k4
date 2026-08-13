# Method v0.11: WOWII 141 maximum-center existence reduction

Date: 2026-08-13
Status: verified construction and girth chord exclusions; one exact
distance-two existence hypothesis remains

## What is now unconditional from girth

The new Lean file
[`lean/GraphConjecture141GirthSevenExistence.lean`](../../lean/GraphConjecture141GirthSevenExistence.lean)
proves directly from `6 <= girth(G)` that every open neighborhood is
independent.  A hypothetical edge between two neighbors closes a 3-cycle,
contradicting the girth lower bound.

It also proves the exact 4-cycle exclusion needed by the splice.  If

```text
v -- u -- x
```

is a simple two-edge path and another neighbor `a` of `v` is adjacent to
`x`, then `v-u-x-a-v` is a 4-cycle.  Thus at girth at least six, `u` is the
unique attachment of `x` back into `N(v)`.

These proofs use the repository's actual `Walk.IsCycle` and `girth_le_length`
API; triangle- and 4-cycle-freeness are not inserted as assumptions.

## Maximum center and constructed certificate

The finite supremum

```text
Finset.univ.sup (indepNeighborsCard G)
```

is proved to be attained by some vertex.  From an attained center, local
independence, and a suitable two-edge path, the file constructs every field
of `DistanceTwoLeafData G`:

- the full `neighborFinset` is the maximum local independent set;
- its cardinality equals `indepNeighborsCard`;
- the extra vertex is outside the star and nonadjacent to its center; and
- girth forces its attachment to the retained neighborhood to be unique.

Combined with v0.10, this produces the induced star-plus-leaf tree and the
exact upstream-shaped WOWII 141 conclusion for `6 <= girth(G) <= 7`.

## Sharp remaining hypothesis

The result is reduced to `MaximumCenterHasDistanceTwoPath G`:

```text
for every center attaining maximum local independence,
there exist u,x with v--u--x, x != v, and x nonadjacent to v.
```

The final theorem assumes only this property in addition to the girth range;
all independence and unique-attachment facts are derived from girth.

Mathematically, the property should follow because a connected graph with
positive finite girth cannot have a maximizing center whose entire component
is its closed neighborhood: at girth at least six that would be an acyclic
star.  The repository obstacle is a formal extraction connecting
`exists_girth_eq_length`, connectedness, and a specified maximum center.  No
unconditional theorem is claimed until that path-existence bridge is proved.

## Verification

From the `formal-conjectures` checkout:

```bash
timeout 60s lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture141GirthSevenExistence.lean
```

Result: exit 0 in 6.5 seconds.  The file has no proof placeholders or custom
axioms.
