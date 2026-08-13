# Method v28: WOWII #59 relabeled core profile

Date: 2026-08-13

Local certificate: `lean/GraphConjecture59RelabeledCoreProfile.lean`

## Outcome

This checkpoint completes the coordinate transport left open by v27.  Given
a properly two-colored bipartite six-core whose two color classes each have
three vertices, Lean now constructs explicit equivalences

```text
Fin 3 ≃ {v ∈ S | c(v)=0},    Fin 3 ≃ {v ∈ S | c(v)=1}.
```

The adjacency relation transported through these equivalences is a Boolean
`3 x 3` matrix.  For each of its six vertices, the v27 cyclic-card theorem
supplies a color-aligned `K2,2` rectangle after deleting that vertex.  The new
transport proof converts those six graph rectangles into the two families of
common-neighbor inequalities defining matrix deletion criticality.

The resulting end-to-end theorem is
`exists_relabeling_with_exact_core_profile`.  From the original graph,
coloring, class-cardinality, and `largestInducedForestSize = 4` hypotheses it
constructs the relabeling and certifies exactly one of:

```text
8 cross-edges and 4 core vertices of internal degree 3; or
9 cross-edges and 6 core vertices of internal degree 3.
```

Since the core is bipartite with parts of size three, these are precisely the
profiles of `K3,3-e` and `K3,3`.  No implicit identification between an
abstract color class and `Fin 3` remains.

## Finite classifier

The label-independent matrix classifier quantifies over all Boolean `3 x 3`
matrices and is discharged with Lean's kernel-reduced `decide`.  This is the
same finite space as the earlier nine-bit-mask theorem, but makes the final
composition direct and avoids a second mask-encoding transport.  It does not
use `native_decide`.

## Lean audit

The complete new module, including the relabeling transport and finite
classifier, was rebuilt with the repository-pinned Lean 4.27 toolchain, a
60-second process cap, and warnings as errors:

```text
ELAN_TOOLCHAIN=leanprover/lean4:v4.27.0 \
LEAN_PATH=/tmp/c5k4-59-v27-audit.Q5a01Z:/tmp \
timeout 60s lake env lean \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture59RelabeledCoreProfile.lean
```

Result: exit code 0 in 10.84 seconds.  A source audit found no `sorry`,
`admit`, `native_decide`, custom axioms, or diagnostic `#print` commands.

WOWII #59 is already externally disproved.  This is theorem extraction for
the local method program, not a new counterexample or release candidate.
