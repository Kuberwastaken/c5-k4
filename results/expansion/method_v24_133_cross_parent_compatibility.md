# Method v0.24: WOWII 133 cross-parent compatibility

Date: **2026-08-13 UTC**

Outcome: **C4-freeness gives the missing cross-parent intersection constraint,
and it eliminates the specific modular colored ownership counterprofile from
v0.22 whenever same-slot parents in different branches are distinct graph
vertices.**

Two distinct vertices in a C4-free graph have at most one common neighbor.
Therefore two second parents can share at most one third-choice vertex.  The
modular v0.22 assignment makes same-slot parents across branches share all
three owned third vertices, so it cannot be realized by distinct parents in a
C4-free graph.

This rules out that particular abstract counterprofile.  It does not eliminate
all seven aggregate multiplicity profiles, prove that all cross-branch parents
are distinct, or prove WOWII 133.

## Frozen scope

- New certificate only:
  `lean/GraphConjecture133CrossParentCompatibility.lean`.
- New report only:
  `results/expansion/method_v24_133_cross_parent_compatibility.md`.
- Parent context:
  `lean/GraphConjecture133DegreeCompletion.lean` and
  `lean/GraphConjecture133ColoredOwnership.lean`.
- No existing file was edited.  No commit, push, release, issue, PR, or other
  public action was made.
- Every subprocess was capped at 60 seconds.

## Generic C4-free theorem

Lean proves:

```text
p != q
G has no four-cycle
--------------------------------
card(neighbors(p) intersect neighbors(q)) <= 1.
```

If two distinct common neighbors `a,b` existed, they would form the four-cycle

```text
p -- a -- q -- b -- p.
```

The proof carries all six pairwise distinctness conditions explicitly from
simple-graph adjacency, `p != q`, and `a != b`.

This theorem is independent of regularity and metric assumptions.  It is a
genuine global compatibility condition on local neighborhoods.

## Saturated-parent specialization

For two second parents with explicit third triples

```text
{a1,a2,a3}
{b1,b2,b3},
```

Lean proves that each triple is a subset of its parent's neighborhood, hence

```text
card({a1,a2,a3} intersect {b1,b2,b3}) <= 1.
```

This is the cross-branch analogue of the earlier same-branch disjointness
theorem:

- same branch: intersection is zero because both parents also share the same
  first-choice vertex, and any shared third would make a C4;
- different branches: intersection may be one, but never two or three, for
  distinct parents.

The separate theorem `not_two_shared_thirds` packages the direct contradiction
from two named shared thirds.

## Sharpness

The bound one is locally sharp.  Lean verifies that two abstract triples with
exactly one common element have intersection card one, under the explicit
cross-distinctness assumptions.

This finite-set control does not assert that every such overlap embeds in the
full metric configuration.  It shows only that C4-freeness itself permits one
shared third and forbids two.

## Consequence for the v0.22 modular model

The modular ownership model assigned third vertex `z` to parent slot
`z mod 3` in every branch.  Thus each same-slot parent owns the same three
third vertices across all branches.

Lean proves exactly:

```text
card(ownedThirds(branch1,slot)
     intersect ownedThirds(branch2,slot)) = 3.
```

It then proves this violates the C4-free intersection bound `<= 1`.

Therefore the v0.22 colored ownership assignment is not graph-realizable under
the following honest condition:

```text
same-slot parents from different branches denote distinct graph vertices.
```

The Lean abstract contradiction is stated at the finite ownership-set level;
the graph theorem supplies the reason any distinct-parent realization would
have to satisfy the bound.

## Remaining identity loophole

The current rung does not prove that cross-branch second parents are distinct.
If two branch labels refer to the same graph vertex, the common-neighbor theorem
for distinct vertices does not apply, and identical third triples are expected.

Whether such parent identification is possible depends on the earlier metric
roles:

```text
u -- c1 -- p
u -- c2 -- p
```

with distinct first choices `c1,c2`.  This itself forms a four-cycle

```text
u-c1-p-c2-u
```

when all four vertices are distinct.  The natural next theorem should therefore
prove cross-branch parent distinctness from C4-freeness and the branch
adjacencies.  Combining that theorem with v0.24 would fully eliminate the
modular same-slot realization.

## What survives after modular elimination

The abstract `(0,0,9)` profile is not eliminated in general.  A different
colored design could distribute the nine triple-owned vertices so that every
pair of cross-branch parents intersects in at most one third.  Combinatorially,
this becomes a three-partite linear hypergraph or Latin-square-type design:

- each third vertex selects one parent from each branch;
- each parent has load three;
- any cross-branch parent pair occurs at most once.

Such designs exist abstractly, so after proving parent distinctness the next
question is whether target colors, metric placement, or saturated blocker
neighborhoods rule them out.  The modular design was simply too repetitive.

## Genuine graph facts versus abstract checks

Genuine graph theorems:

- distinct vertices have at most one common neighbor in a C4-free graph;
- two distinct saturated parents share at most one third choice;
- sharing two named thirds is impossible.

Abstract finite checks:

- the modular ownership sets have intersection card three;
- a one-overlap triple pair attains the numerical bound.

The report does not claim that an arbitrary linear ownership design is a graph
or that the entire aggregate obstruction has been removed.

## Verification

From the pinned `formal-conjectures` checkout:

```bash
timeout 60s lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture133CrossParentCompatibility.lean
```

Result: **PASS** in approximately seven seconds.  The source contains no
unfinished proof, custom axiom, native evaluator, or external oracle.

## Verdict

Cross-parent compatibility supplies the first genuine graph constraint that
cuts the colored counterprofile: distinct C4-free parents may share at most one
third vertex, whereas the modular model shares three.  The next exact bridge is
cross-branch parent distinctness; beyond that, only linear rather than repeated
ownership designs remain viable.
