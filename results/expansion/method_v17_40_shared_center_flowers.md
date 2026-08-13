# WOWII 40 v0.17: explicit shared-center flower data

**Date:** 2026-08-13

**Outcome:** a truthful abstract shared-center even-flower structure is
instantiated into the v0.16 shared-cut certificate at `tau=1`, yielding an
exact no-`sorry` WOWII 40 theorem.

**Read-only upstream snapshot:** `formal-conjectures`
`9a1636c4030039f70cf78b866c216d8b6c5f35b0`

## Minimal flower data

Rather than introduce a bulky indexed graph whose cycle and feedback
invariants would require a separate finite-computation development, the new
file defines exactly the local witnesses supplied by two even petals sharing
a center.

A `SharedCenterFlowerData G` contains:

- a shared center `c`;
- an actual path in a first petal with support order at least three;
- proof that `c` is not in that path support;
- a vertex `x` in a second petal adjacent to `c`;
- proof that `x` is not in the first path support.

This is strictly structural data in `G`: the path is a `G.Walk` with
`IsPath`, and the second-petal edge is a `G.Adj` proof.

## Constructing the shared-cut certificate

The raw first petal is defined as

```text
insert c firstPath.support.
```

Erasing the allocated center recovers the first path support exactly. The
additional bridge is the two-vertex support `{c,x}`. Since neither endpoint
belongs to the first path, the bridge is disjoint from the trimmed petal.

The Lean file proves these facts and constructs

```text
SharedCutPetalCertificate G 1.
```

The certificate has:

```text
one trimmed petal path: rank at least 2,
one second-petal edge: rank exactly 1,
total rank: at least 3 = 2*tau+1.
```

The final theorem assumes the two global facts appropriate to a shared-center
even flower:

```text
G.IsBipartite,
feedbackDeletion G = 1.
```

Together with `SharedCenterFlowerData G`, it proves WOWII 40 in the exact
upstream real/ceiling presentation.

## Why `tau=1` is explicit

Any number of cycles sharing one common center can all be destroyed by
deleting that center, so a non-acyclic shared-center flower has feedback
deletion one. The present file consumes that invariant equality rather than
formalizing a particular indexed cycle graph and reproving non-acyclicity and
optimality for it.

For a conventional flower of at least two even cycles, the local data is
immediate:

1. choose three consecutive non-center vertices in the first cycle;
2. use the center edge into the second cycle.

The cycles meet only at the center, so both disjointness obligations hold.
A single even cycle is already covered by the earlier long-path theorem and
does not provide a genuinely distinct second-petal edge.

## Preserved boundaries

This closes the strong shared-center class but does not claim that every
cactus has one global center. In a block tree with several cut vertices, the
v0.16 trimming step must be applied recursively and the feedback coordinate
must be distributed across selected blocks.

The four bridge-connected `C4` petals from v0.14 remain the obstruction to a
universal one-long-path proof. Their cycles do not all share the external
center as a cycle vertex; they are handled by the v0.15 bridge-petal theorem.
No pointwise feedback insertion claim is introduced, so `EQKo` remains
untouched.

## Verification

New file:

```text
lean/GraphConjecture40SharedCenterFlowers.lean
```

After compiling the local import chain, the final warning-as-error invocation
exited `0` with no output:

```text
timeout 60s env LEAN_PATH=/Users/kuber.mehta/Projects/c5-k4/lean \
  lake env lean -R /Users/kuber.mehta/Projects/c5-k4/lean \
  -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture40SharedCenterFlowers.lean
```

The final invocation took 5.06 seconds. The source contains no
`native_decide`, `sorry`, `admit`, or custom axiom. Each subprocess stayed
below the 60-second cap.

## Next step

The explicit local flower step is now complete. Further #40 progress should
target recursive block selection rather than add more certificate wrappers:

- formalize a finite leaf-block elimination order;
- show a cyclic leaf block supplies either a trimmed three-vertex path or
  compensating rank surplus;
- track when one cut vertex hits multiple cyclic blocks;
- assemble the harvested supports with the v0.13 family theorem.

Classification: **FORMAL SHARED-CENTER FLOWER CLASS; no full proof,
counterexample, release, or external claim.**
