# WOWII 40 v0.15: explicit cactus-petal block certificates

**Date:** 2026-08-13

**Outcome:** a no-`sorry` block-level theorem packages the local structure of
bridge-connected cycle petals and proves that it supplies path-family rank at
least `2tau+1`. The entire cycle-flower family from v0.14 fits the certificate
uniformly.

**Read-only upstream snapshot:** `formal-conjectures`
`9a1636c4030039f70cf78b866c216d8b6c5f35b0`

## Why an explicit certificate

Mathlib does not currently expose a convenient finite block-cut tree API in
the form needed here. Introducing a bespoke theory of blocks, cut vertices,
ears, and cactus decompositions would obscure the actual combinatorial unit
used by the proof. The new file therefore formalizes the clean local object
that a cactus decomposition must produce.

For a graph `G` and coordinate `k`, a `CactusPetalCertificate G k` consists
of:

1. exactly `k` pairwise vertex-disjoint path supports;
2. every petal path has at least three vertices;
3. one additional bridge path with at least two vertices;
4. the bridge path is vertex-disjoint from the union of all petal paths.

Every support is required to come from an actual `G.Walk` satisfying
`IsPath`; these are not merely cardinality sets.

## Formal assembly

The Lean development proves:

- the bridge support is not already a petal;
- inserting it into the petal family preserves the complete
  `IsPathSupportFamily` predicate, including pairwise disjointness and path
  realizations;
- the assembled family has exactly `k+1` components;
- additivity of covered support orders gives rank at least

```text
k petal paths * at least 2 edges each
  + one bridge path * at least 1 edge
  = 2k+1.
```

The resulting theorem says:

```text
G.IsBipartite
and feedbackDeletion G = k
and CactusPetalCertificate G k
  -> WOWII 40.
```

The conclusion is the exact upstream real/ceiling statement, via the v0.13
path-family deficiency transfer.

## Generic flower family

Consider any `k>=1` vertex-disjoint even cycles, each joined by one bridge
from a chosen attachment vertex to a common center. This is the cycle-flower
family; v0.14 used four `C4` petals to refute the one-long-path lemma.

The petal certificate is obtained uniformly:

- in each even cycle, take a three-vertex path avoiding the chosen attachment
  vertex (or any longer such path);
- these `k` paths are disjoint because the cycles are vertex-disjoint;
- choose the center--attachment bridge from one petal as the extra two-vertex
  path;
- it is disjoint from all chosen petal paths because its attachment was
  deliberately avoided.

The cycles are vertex-disjoint, so every feedback set must meet each cycle;
deleting one vertex per cycle makes the flower acyclic. Thus `tau=k`.
Even-cycle flowers are bipartite. Consequently the formal structural theorem
applies to every member once these evident graph-specific witnesses are
instantiated.

For the exact 17-vertex four-`C4` obstruction, the certificate has four
three-vertex petal paths plus one bridge edge, giving rank
`4*2+1=9=2*4+1`. The graph has no ten-vertex path, but its five-component
linear forest pays the conjecture exactly. This is the intended block-level
resolution of the obstruction.

The file does not formalize a concrete indexed flower graph or reprove its
feedback number computationally; it formalizes the reusable certificate and
the complete theorem consuming it. This avoids presenting a conditional
block decomposition as a universal cactus theorem.

## EQKo compatibility

The construction is global and block-level. It does not assert that deleting
one vertex must increase linear-forest rank, so the `EQKo` pointwise
insertion counterexample remains intact. A graph may satisfy the certificate
with surplus rank, as `EQKo` does at `tau=1, ell=4` versus the required three.

## Verification

New file:

```text
lean/GraphConjecture40CactusBlocks.lean
```

After compiling its local import chain, the independent check was:

```text
timeout 60s env LEAN_PATH=/Users/kuber.mehta/Projects/c5-k4/lean \
  lake env lean -R /Users/kuber.mehta/Projects/c5-k4/lean \
  -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture40CactusBlocks.lean
```

It exited `0` in 7.19 seconds with no output. The source contains no
`native_decide`, `sorry`, `admit`, or custom axiom. Every subprocess stayed
within the 60-second cap.

## Remaining boundary

This closes the explicit bridge-connected petal class, not all connected
bipartite graphs or even every possible cactus presentation. The next theorem
would extract such local paths recursively from the leaf blocks of a formal
block-cut tree. The bookkeeping must handle:

- petals that share cut vertices rather than being vertex-disjoint;
- bridge-free 2-connected bipartite blocks;
- allocation of attachment vertices so harvested paths remain disjoint;
- surplus from blocks contributing more than one feedback unit.

The certificate theorem isolates that future work cleanly: once a
decomposition supplies paths of total rank `2tau+1`, all optimization and
ceiling transport is already formal.

Classification: **FORMAL CACTUS-PETAL STRUCTURAL CLASS; no full proof,
counterexample, release, or external claim.**
