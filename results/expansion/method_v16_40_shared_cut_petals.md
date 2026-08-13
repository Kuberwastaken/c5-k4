# WOWII 40 v0.16: allocating a shared cut vertex

**Date:** 2026-08-13

**Outcome:** raw cactus petals may share one cut vertex; erasing that allocated
attachment is formally proved to preserve the petal count and produce a
pairwise-disjoint path family. The resulting shared-cut certificate implies
WOWII 40 through the v0.15 block theorem.

**Read-only upstream snapshot:** `formal-conjectures`
`9a1636c4030039f70cf78b866c216d8b6c5f35b0`

## Shared-cut certificate

For feedback coordinate `k`, the new `SharedCutPetalCertificate G k`
contains:

- a distinguished cut vertex `center`;
- exactly `k` raw petal vertex sets;
- the center belongs to every raw petal;
- distinct raw petals meet only at the center;
- after erasing the center, each petal is the support of an actual path with
  at least three vertices;
- one additional path of at least two vertices, disjoint from the union of
  all trimmed petals.

The trimmed-path requirement is intentional. Removing a cut vertex from an
arbitrary path support need not leave a single path; the certificate records
the path chosen inside each block after its attachment has been allocated.

## Formal trimming and allocation

Define

```text
trimmedPetals = image (erase center) rawPetals.
```

The Lean file proves the following nontrivial bookkeeping facts.

### Trimming is injective on raw petals

Because every raw petal contains the center, equality after erasing the
center implies equality before erasing it. Therefore the image has exactly
`k` members; trimming does not accidentally collapse two block certificates.

### Trimmed supports are disjoint

If a vertex lay in two trimmed petals, the raw-intersection hypothesis would
force it to equal the center. But membership in an erased set says precisely
that it is not the center. Hence distinct trimmed supports are disjoint.

### Path realizations survive

The certificate supplies actual path witnesses for each erased support, so
the trimmed image satisfies the complete `IsPathSupportFamily` predicate,
not merely a set-theoretic disjointness condition.

### The v0.15 certificate is recovered

The file proves that the covered union of the trimmed image is exactly the
biunion of the erased raw petals. Thus the additional bridge-disjointness
hypothesis transports without loss, and a full `CactusPetalCertificate G k`
is constructed.

The final theorem is:

```text
G.IsBipartite
and feedbackDeletion G = k
and SharedCutPetalCertificate G k
  -> WOWII 40.
```

The conclusion is again the exact upstream ceiling statement.

## Strong shared-center flowers

For even-cycle petals sharing a common center, erasing that center from any
`C_{2m}` petal leaves a path on `2m-1>=3` vertices. Distinct trimmed petals
are disjoint automatically.

There is an important feedback-count subtlety: if all cycles share the same
center, deleting that one vertex kills every cycle, so `tau=1` regardless of
the number of petals. The certificate should therefore select one trimmed
petal for the single feedback unit and use an edge in a second petal as the
extra disjoint path. This closes shared-center flowers with at least two even
petals. A lone even cycle remains covered more directly by the v0.11
four-vertex-path theorem.

For cactus chains or trees of blocks, the number of cycles need not equal the
feedback number when one cut vertex hits several cycles. The present theorem
does not conflate these quantities: it asks for exactly `k` allocated raw
petals, where `k` is separately certified as the feedback coordinate.

## Preserved obstruction

The v0.14 four-`C4` flower with bridge-disjoint petals remains a one-long-path
obstruction. It is covered already by v0.15 and also fits the new framework
vacuously by choosing an allocated center not shared between raw petals only
when the raw sets are presented with the stated common-center property. The
new theorem does not claim that every cactus admits one global shared center;
multiple allocation steps are still needed for a general block tree.

No new counterexample to WOWII 40 or to the global path-family rank target was
found. The obstruction remains to naive single-path and pointwise-insertion
proof routes, not to the conjectured inequality.

## Verification

New file:

```text
lean/GraphConjecture40SharedCutPetals.lean
```

After compiling the local import chain, the independent check was:

```text
timeout 60s env LEAN_PATH=/Users/kuber.mehta/Projects/c5-k4/lean \
  lake env lean -R /Users/kuber.mehta/Projects/c5-k4/lean \
  -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture40SharedCutPetals.lean
```

It exited `0` in 10.32 seconds with no output. The source contains no
`native_decide`, `sorry`, `admit`, or custom axiom. Every subprocess stayed
within the 60-second cap.

## Remaining boundary

This proves one allocation step at a shared cut vertex. A complete cactus
theorem now needs recursive selection along the block-cut tree:

1. choose leaf cyclic blocks;
2. allocate their parent cut vertices away;
3. harvest surviving three-vertex paths;
4. remove or contract processed leaves;
5. track when one cut deletion pays for several cycles.

The formal trimming lemma supplies the local induction move. What remains is
global feedback-number bookkeeping and the existence of enough allocated
blocks, not path-cover or ceiling arithmetic.

Classification: **FORMAL SHARED-CUT-PETAL STRUCTURAL CLASS; no full proof,
counterexample, release, or external claim.**
