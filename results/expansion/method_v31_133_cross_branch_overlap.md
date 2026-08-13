# Method v0.31: WOWII 133 cross-branch overlap

## Outcome

Replacing the unavailable “three clean parents below one first choice” premise
with the proved configuration—one clean parent from each of three first
branches—does **not** close the blocker count.

Each clean parent exposes three genuine third choices.  C4-freeness gives

```text
|A ∩ B| <= 1,
|A ∩ C| <= 1,
|B ∩ C| <= 1.
```

The sharp union lower bound is only

```text
|A ∪ B ∪ C| >= 6.
```

Four internal targets still have eight outside-neighbor slots.  Thus the
correct comparison is

```text
6 <= distinct thirds <= 8,
```

which is compatible.

Lean also certifies the exact extremal survivor: three pairwise-shared thirds,
three private thirds, no triple-shared third, and a capacity-respecting
blocker assignment.  The remaining obstruction must therefore use residual
degree completion or additional metric geometry; local overlap and blocker
capacity alone are exhausted.

Lean certificate:

- `lean/GraphConjecture133CrossBranchOverlap.lean`.

## Sharp union lower bound

Let `A,B,C` be the three third-choice finsets.  Each has cardinality three.

First,

```text
|A ∪ B| >= 3 + 3 - 1 = 5.
```

Next,

```text
(A ∪ B) ∩ C
  subset (A ∩ C) ∪ (B ∩ C),
```

whose cardinality is at most two.  Adding the third triple therefore gives

```text
|(A ∪ B) ∪ C| >= 5 + 3 - 2 = 6.
```

`six_le_card_union_three` formalizes this argument using exact finite-set
inclusion-exclusion.  No assumption is made about whether all three pairwise
intersections use the same vertex.

The bound is sharp.

## Equality classification

`union_six_forces_triangle_overlap` proves that equality at six forces

```text
|A ∩ B| = |A ∩ C| = |B ∩ C| = 1,
|A ∩ B ∩ C| = 0.
```

Hence the three pairwise intersection vertices are distinct.  The six-point
configuration has the form

```text
A = {xAB, xAC, a},
B = {xAB, xBC, b},
C = {xAC, xBC, c}.
```

This is the exact triangle-overlap pattern surviving the cross-branch
common-neighbor bound.

## Explicit blocker survivor

The Lean model uses vertices `0..5`:

```text
A = {0,1,3},
B = {0,2,4},
C = {1,2,5}.
```

The blocker colors are

```text
vertex: 0 1 2 3 4 5
target: 0 1 2 2 1 0.
```

Their loads are

```text
(2,2,2,0),
```

so every internal target respects capacity two.

Within each parent triple, the three blocker targets are distinct:

```text
A uses {0,1,2},
B uses {0,2,1},
C uses {1,2,0}.
```

This meets the additional C4 restriction that two different thirds sharing
one parent cannot contact the same target.

Lean verifies:

- `three_thirds_per_parent`;
- `cross_parent_intersection_eq_one`;
- `triple_intersection_empty`;
- `sharp_union_card_six`;
- `target_capacity_two`;
- `blocker_injective_on_parent`;
- `every_third_has_internal_blocker`.

`cross_branch_capacity_survivor` packages all of them into one theorem.

This is an incidence certificate, not a completed graph counterexample.  It
shows exactly that the currently extracted local constraints are mutually
consistent.

## Degree completion signature

The survivor is not locally degree-saturated at its third vertices:

- each pair-shared third has two parent edges and one blocker edge, leaving
  one fourth-degree slot;
- each private third has one parent edge and one blocker edge, leaving two
  fourth-degree slots.

Thus the six thirds carry nine residual degree stubs in total.
`residual_degree_signature` certifies the local equations

```text
2 + 1 + 1 = 4,
1 + 1 + 2 = 4.
```

This is the first place where the cross-branch survivor differs materially
from the eliminated Latin `(0,0,9)` kernel: its triple-owned thirds were
already saturated, while the sharp six-point pattern must attach nine more
edges somewhere.

## Exact remaining condition

The next question is whether those nine residual stubs can be completed while
preserving all graph requirements:

1. four-regularity;
2. triangle- and C4-freeness;
3. the already saturated parent neighborhoods;
4. the selected geodesic and its distance labels;
5. no newly exposed clean handle or induced-path rerouting.

The smallest honest next model should fix the six-point triangle-overlap core
and its blocker coloring, then enumerate only residual adjacencies of those
six thirds.  Immediate rejection rules are:

- an edge to an owning parent or blocker already counted twice;
- any triangle through a parent or target;
- any C4 through two parents, two blockers, or a parent and target;
- degree above four;
- adjacency to a forbidden geodesic index.

If no residual completion exists, the first failed rule supplies the missing
graph lemma.  If a completion exists, local three-parent counting is
definitively insufficient and the proof must use global path rerouting.

## What this means for the proof route

The v0.30 theorem remains valuable: if one branch ever supplies three clean
parents, the `9 > 8` argument closes immediately.

Under only the currently proved one-clean-parent-per-branch statement,
however, the best general lower bound is six and is realized by the explicit
survivor above.  Claiming a contradiction from eight target slots would be an
overcount.

## Verification

The file is self-contained over `FormalConjecturesUtil`.  It uses ordinary
finite-set proofs and kernel computation only, with no holes, custom axioms,
or native-decision shortcuts.
