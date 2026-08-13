# WOWII 40 v0.14: feedback-sized path families and a one-path obstruction

**Date:** 2026-08-13

**Outcome:** the tempting universal one-long-path lemma is falsified by an
exact 17-vertex bipartite cactus, while two stronger multi-component classes
are proved in no-`sorry` Lean.

**Read-only upstream snapshot:** `formal-conjectures`
`9a1636c4030039f70cf78b866c216d8b6c5f35b0`

## Bounded falsification first

The v0.12 sufficient condition suggested the possible universal lemma:

```text
connected bipartite and feedbackDeletion=k
  -> exists a path on at least 2k+2 vertices.
```

An exact bounded check covered all 71 connected bipartite Graph Atlas graphs
on 2--7 vertices. None violates the lemma. The check used exhaustive vertex
subsets for feedback deletion and exhaustive simple-path search and completed
under the 60-second cap.

The lemma is nevertheless false. Take four vertex-disjoint 4-cycles and a
new center `0`. In each cycle choose one attachment vertex and join it to `0`
by a bridge. With petals `(1,2,3,4)`, `(5,6,7,8)`, `(9,10,11,12)`, and
`(13,14,15,16)`, the edge set is

```text
12,23,34,41,01,
56,67,78,85,05,
9-10,10-11,11-12,12-9,0-9,
13-14,14-15,15-16,16-13,0-13.
```

This graph is connected and bipartite. Its four cycles are vertex-disjoint,
so every feedback set contains at least one vertex from each; deleting one
vertex per petal makes it acyclic. Hence `tau=4` exactly.

Deleting the center separates the four petals. A simple path can meet at most
two petals because it can traverse the center only once. Within each petal it
can contain at most all four vertices, so every simple path has at most
`4+1+4=9` vertices. The proposed threshold is `2tau+2=10`. Thus the universal
one-path lemma fails. This is the first obstruction in this four-`C4` flower
family; three petals have threshold eight and admit a nine-vertex path. No
claim of global minimality beyond the audited Atlas range is made.

## Formal replacement: many short paths

For a pairwise-disjoint path-support family `P`, v0.13 defined its covered
union `U`. The new file proves the exact additivity bridge

```text
U.card = sum_{s in P} s.card.
```

Therefore, if every component contains at least three vertices,

```text
U.card - P.card >= 2 * P.card.
```

Two structural sufficient classes follow.

### Uniform three-vertex class

At feedback coordinate `k`, if there are `k+1` pairwise-disjoint paths and
each has at least three vertices, their rank is at least `2k+2`, exceeding
the required `2k+1`. For bipartite graphs this formally proves WOWII 40.

### Exact-budget mixed class

A sharper theorem uses exactly the required rank. Suppose `P` has `k+1`
components, every component has at least two vertices, and a `k`-member
subfamily has at least three vertices per component. Then

```text
rank(P) >= 2k + 1.
```

Equivalently, this is `k` three-vertex paths plus one disjoint edge, with
larger components permitted. The formal theorem again closes the exact
upstream ceiling statement for bipartite graphs with `tau=k`.

This mixed certificate fits the four-petal obstruction: choose a three-vertex
path inside each petal avoiding its attachment vertex, then use the center--
attachment bridge of one petal as the fifth disjoint edge. Thus the branching
that destroys a single long path naturally supplies several short paths.

## EQKo check

The `EQKo` graph remains compatible. Its `tau=1, ell=4` exceeds the required
rank three. This lane does not infer a rank gain from deleting a particular
vertex; it certifies rank globally from disjoint paths. The known pointwise
insertion counterexample is therefore neither assumed nor hidden.

## Verification

New file:

```text
lean/GraphConjecture40FeedbackPathFamily.lean
```

After compiling the local import chain, the independent check was:

```text
timeout 60s env LEAN_PATH=/Users/kuber.mehta/Projects/c5-k4/lean \
  lake env lean -R /Users/kuber.mehta/Projects/c5-k4/lean \
  -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture40FeedbackPathFamily.lean
```

It exited `0` in 7.16 seconds with no output. The source contains no
`native_decide`, `sorry`, `admit`, or custom axiom. Every subprocess stayed
within the 60-second cap.

## Remaining boundary

The complete bipartite base now asks for a global theorem producing enough
short disjoint paths, rather than one long path. The most concrete target is:

```text
feedbackDeletion G = k
  -> a disjoint path family whose total rank is at least 2k+1.
```

The cactus obstruction shows why block decomposition is appropriate: cyclic
blocks may branch at cut vertices, defeating long paths while retaining
additive local rank. A block-tree proof can harvest short paths inside cyclic
leaf blocks and combine them without the false vertex-by-vertex insertion
rule exposed by `EQKo`.

Classification: **FORMAL MULTI-COMPONENT POSITIVE CLASS PLUS EXACT
ONE-PATH OBSTRUCTION; no full proof, release, or external claim.**
