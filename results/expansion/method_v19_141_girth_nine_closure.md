# Method v0.19: WOWII 141 closed through girth nine

Date: 2026-08-13
Status: verified unconditional theorem for every connected finite graph with
`girth <= 9`; not a resolution of the unrestricted conjecture

## Final chord exclusion

[`lean/GraphConjecture141GirthNineClosure.lean`](../../lean/GraphConjecture141GirthNineClosure.lean)
proves the last local lemma.  For the chordless shortest-path prefix

```text
v -- u -- x -- y
```

and any neighbor `a` of `v`, an edge `y-a` closes

```text
v-u-x-y-a-v,
```

a cycle of length five.  Every possible vertex collision is already excluded
by shortest-path distinctness or one of the prefix shortcut nonedges.
Therefore girth at least eight forces `y` to have no neighbor in `N(v)`.

## Full certificate construction

At a center attaining maximum local independence, the file now constructs:

1. the full independent neighborhood `A=N(v)`;
2. `DistanceTwoLeafData` from `v-u-x`, with the unique attachment of `x`
   supplied by the earlier 4-cycle exclusion; and
3. `SecondLeafData` from `y`, whose only neighbor in the retained first-stage
   tree is `x`.

The v0.15 second-leaf theorem then derives the induced-tree field, rather than
assuming it.  Its cardinality is exactly

```text
max_v indepNeighborsCard(G,v) + 3,
```

which pays the WOWII 141 right side at girth eight and nine.

## Unconditional closure

The global v0.18 theorem supplies a distance-three vertex from every center
of a connected graph with girth at least eight.  The v0.14 shortest-path
lemma supplies `v-u-x-y`.  Composing all stages proves the exact upstream
statement without extra hypotheses for

```text
8 <= girth(G) <= 9.
```

Finally, combining this with the already verified girth-at-most-seven theorem
gives:

```text
G.Connected and girth(G) <= 9
  -> floor(girth(G)/2) - 1 + max_v indepNeighborsCard(G,v)
       <= largestInducedTreeSize(G).
```

This is a genuine partial theorem for the open WOWII conjecture, covering all
connected finite graphs through girth nine.

## Verification

From the `formal-conjectures` checkout:

```bash
timeout 60s lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture141GirthNineClosure.lean
```

Result: exit 0 in 10.3 seconds.  The file contains no proof placeholders,
native evaluation shortcuts, or custom axioms.

## Next range

At girth ten and eleven, the inequality requires four vertices beyond maximum
local independence.  The same program suggests a three-vertex tail.  The
global step becomes distance at least four from the chosen center, and the
local step excludes chords from the fourth prefix vertex back into the star
and earlier tail.  A scalable proof should now generalize the repeated leaf
assembly and radius-layer argument rather than add another bespoke pair of
files.
