# WOWII 40 v0.18: a genuine recursive leaf-block step

**Date:** 2026-08-13

**Outcome:** a no-`sorry` induction move proves that an allocated cyclic leaf
path of order at least three raises a remainder path-family certificate from
feedback budget `k` to budget `k+1`.

**Read-only upstream snapshot:** `formal-conjectures`
`9a1636c4030039f70cf78b866c216d8b6c5f35b0`

## Input to one block step

Let `P` be a disjoint path-support family already harvested from the
remainder. A `LeafBlockStep G P` contains:

- one support `S` in the selected leaf block;
- an actual path of `G` whose support is exactly `S`;
- `|S|>=3`;
- `S` is disjoint from every vertex covered by `P`.

This is the structure supplied by trimming the parent cut vertex from a
cyclic cactus leaf block. For an even cycle leaf block, three consecutive
internal vertices give such a path. The disjointness condition records the
allocation rule: internal leaf vertices have not been used by the remainder
certificate.

## Formal assembly theorem

The Lean file proves, rather than assumes, all family bookkeeping:

1. `S` is not already a member of `P`;
2. inserting `S` preserves pairwise disjointness;
3. inserting `S` preserves actual path realizations;
4. the covered-cardinality increment is exact:

```text
covered(insert S P).card = S.card + covered(P).card.
```

Suppose the remainder has the rank certificate

```text
P.card + (2k+1) <= covered(P).card.
```

After insertion, the component count increases by one and covered order
increases by at least three. Therefore

```text
(insert S P).card + (2(k+1)+1)
  <= covered(insert S P).card.
```

This is the exact recursive arithmetic needed by the bipartite deficiency
bound: one cyclic leaf path contributes at least two rank units, paying the
increment

```text
(2(k+1)+1) - (2k+1) = 2.
```

The final theorem combines this new rank certificate with v0.13 and proves
the exact upstream WOWII 40 statement for a bipartite graph whose certified
feedback coordinate is `k+1`.

## Why this is more than another wrapper

Earlier files established what a finished path family implies. This file
formalizes the inductive mutation of that family. It proves the inserted
support is new, constructs the enlarged `IsPathSupportFamily`, proves exact
covered-union growth, and derives the changed feedback-rank budget. These are
the local algebraic and combinatorial facts needed to iterate over a
block-cut tree.

The theorem deliberately separates two issues:

- **certificate recursion**, proved here;
- **feedback recursion**, still a graph-decomposition statement.

It assumes the final graph has feedback coordinate `k+1`; it does not yet
prove that deleting a chosen leaf block leaves a remainder of coordinate
exactly `k`. That equality is not universally automatic when one cut vertex
can hit several cyclic blocks.

## Universal-step boundary

The path-family step is universally true under its explicit allocation
hypothesis. A stronger statement saying every arbitrary chosen cyclic block
raises feedback deletion by one is false in shared-center flowers: several
cycles through one cut vertex together have feedback deletion one, so adding
another such petal need not change `tau` at all.

That is the smallest conceptual counterconfiguration: two cycles sharing one
cut vertex. Each individual cycle is cyclic, but their union still has a
one-vertex feedback set—the shared cut. Thus no induction may charge one
feedback unit per cyclic block without an independence or allocation
condition.

The corrected theorem here charges a leaf path only when the target feedback
budget really changes from `k` to `k+1`; shared-center clusters must first be
grouped as one feedback unit, as in v0.17.

`EQKo` remains compatible. The step never claims that deleting one arbitrary
vertex increases linear-forest rank; it inserts an explicit disjoint path and
computes its global rank contribution.

## Verification

New file:

```text
lean/GraphConjecture40LeafBlockStep.lean
```

After compiling the local import chain, the independent check was:

```text
timeout 60s env LEAN_PATH=/Users/kuber.mehta/Projects/c5-k4/lean \
  lake env lean -R /Users/kuber.mehta/Projects/c5-k4/lean \
  -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture40LeafBlockStep.lean
```

It exited `0` in 5.77 seconds with no output. The source contains no
`native_decide`, `sorry`, `admit`, or custom axiom. Every subprocess stayed
within the 60-second cap.

## Next step

The next genuine block theorem should define a recursive selection order and
prove the feedback bookkeeping:

1. cluster cyclic leaf blocks sharing a feedback cut vertex;
2. show removing an independent selected cluster lowers `tau` by one;
3. harvest either one trimmed path plus an extra edge, or enough disjoint
   leaf paths to pay two rank units;
4. invoke the formal `rank_step` proved here;
5. iterate until the remainder is acyclic.

The certificate induction is now complete; the remaining hard point is
matching selected block clusters to actual feedback-number decrements.

Classification: **FORMAL RECURSIVE LEAF-BLOCK RANK STEP; no full proof,
counterexample, release, or external claim.**
