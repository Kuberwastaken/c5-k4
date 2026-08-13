# Method v0.25: WOWII 133 cross-branch parent distinctness

Date: **2026-08-13 UTC**

Outcome: **second parents selected below distinct endpoint branches are
distinct in every C4-free graph, once the standard second-choice freshness
condition `parent != endpoint` is retained.**  Combining this with v0.24 gives
the unconditional graph-level cross-branch constraint:

```text
distinct endpoint branches -> at most one shared third vertex.
```

The repeated same-slot ownership assignment from v0.22 shares three third
vertices across corresponding branches and is therefore eliminated.

This closes the identity loophole for that modular counterprofile.  It does not
eliminate every linear colored ownership design or prove WOWII 133.

## Frozen scope

- New certificate only: `lean/GraphConjecture133CrossBranchParents.lean`.
- New report only:
  `results/expansion/method_v25_133_cross_branch_parents.md`.
- Parent rung:
  `lean/GraphConjecture133CrossParentCompatibility.lean`.
- No existing file was edited.  No commit, push, release, issue, PR, or other
  public action was made.
- Every subprocess was capped at 60 seconds.

## Branch configuration

The local configuration is

```text
      c1 -- p1
     /
    u
     \
      c2 -- p2
```

with:

- `c1 != c2` from distinct first choices at the endpoint;
- `p1 != u` from the second-choice construction, which erases the preceding
  endpoint;
- all four displayed adjacencies.

If `p1 = p2`, the four distinct vertices form

```text
u -- c1 -- p1 -- c2 -- u.
```

C4-freeness rules this out.  Lean proves all required distinctness conditions
from adjacency, branch distinctness, and `p1 != u`.

## Why endpoint freshness is explicit

C4-freeness alone does not show `p1 != u`.  If the purported second parent
were the endpoint itself, the displayed edges would simply repeat the branch
edge and no four-vertex cycle would result.

The actual handle-choice construction removes the preceding vertex before
selecting a second choice, so `p1 != u` is a genuine established graph premise.
The new theorem retains it explicitly rather than hiding it inside a label or
claiming a false unconditional statement.

## Composition with common-third compatibility

The certificate independently proves the v0.24 graph fact:

```text
distinct vertices in a C4-free graph have at most one common neighbor.
```

It composes this with cross-branch parent distinctness to obtain:

```text
card(neighbors(p1) intersect neighbors(p2)) <= 1.
```

Thus any two second parents below distinct endpoint first choices share at most
one third neighbor.  No separate parent-identity hypothesis remains.

The named-edge version proves directly that two distinct shared thirds would
make the four-cycle

```text
p1 -- a -- p2 -- b -- p1.
```

## Elimination of repeated same-slot ownership

The earlier modular assignment used

```text
parentSlot(z) = z mod 3
```

in every branch.  Corresponding parent slots therefore owned identical
three-element third sets across branches.

Lean again proves the abstract intersection card is three and hence not at most
one.  The new distinctness theorem supplies the missing graph bridge: in an
actual C4-free endpoint-branch realization, those corresponding cross-branch
parents cannot collapse to the same graph vertex.

Therefore repeated same-slot ownership is fully incompatible with the graph
constraints, not merely incompatible under an optional distinctness assumption.

## What survives

The aggregate `(0,0,9)` profile is still not eliminated.  A linear three-partite
ownership design can give:

- one parent in each branch per third vertex;
- three third vertices per parent;
- at most one third for every cross-branch parent pair.

A Latin-square design on three parent slots has exactly these properties.
Unlike the repeated modular assignment, it saturates the C4-free intersection
bound without violating it.

The next useful rung should therefore test a Latin-square ownership profile
against blocker-target colors and saturated neighborhoods.  If it survives, a
new metric or target compatibility constraint is required; if it fails, the
failure will identify which cross-branch triple patterns C4-freeness excludes
beyond pairwise linearity.

## Genuine graph facts versus abstract checks

Genuine graph theorems:

- cross-branch second-parent distinctness;
- cross-branch common-neighbor card at most one;
- impossibility of two named shared thirds.

Abstract finite check:

- repeated same-slot ownership has third-set intersection card three.

The composition is honest because the graph theorem now discharges the only
identity loophole noted in v0.24.

## Verification

From the pinned `formal-conjectures` checkout:

```bash
timeout 60s lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture133CrossBranchParents.lean
```

Result: **PASS** in approximately seven seconds.  The source contains no
unfinished proof, custom axiom, native evaluator, or external oracle.

## Verdict

The modular colored counterprofile is now fully eliminated: cross-branch
parents cannot identify, and distinct C4-free parents share at most one third,
not three.  The viable obstruction space contracts to linear ownership designs
such as Latin squares; those are the next exact target.
