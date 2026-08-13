# Method v19: WOWII #100 upstream-signature bridge

## Purpose

The v18 closure proves a stronger local theorem, but its namespace and theorem
name do not make the upstream replacement completely obvious.  This rung adds
a tiny review-facing corollary whose hypotheses and conclusion match the
current declaration in

```text
FormalConjectures/WrittenOnTheWallII/GraphConjecture100.lean
```

## Exact upstream declaration audited

At the time of this audit, upstream declares:

```lean
theorem conjecture100 (G : SimpleGraph α) [DecidableRel G.Adj]
    (h : G.Connected) (hGc : Gᶜ.Connected) :
    let maxL := (Finset.univ.image (indepNeighborsCard G)).max' (by simp)
    (G.indepNum : ℝ) ≤
      ⌈((maxL : ℝ) + (1 / 2) * (degreeL2Norm Gᶜ : ℝ)) / 2⌉ := by
  sorry
```

The surrounding variables are exactly:

```lean
variable {α : Type*} [Fintype α] [DecidableEq α] [Nontrivial α]
```

## Bridge theorem

Artifact:

```text
lean/GraphConjecture100UpstreamBridge.lean
```

It defines, in the upstream namespace,

```text
WrittenOnTheWallII.GraphConjecture100.conjecture100_upstream_bridge
```

with the same graph parameter, typeclasses, connectedness hypotheses, local
maximum, coercions, ceiling, and `degreeL2Norm Gᶜ` conclusion.  Its entire
proof is:

```lean
exact conjecture100_of_connected G h
```

The upstream complement-connectedness hypothesis is accepted but unused,
because v18 proves the strictly stronger connected-only theorem.

## Semantic caveat

The upstream module's prose says that `length(Gᶜ)` is interpreted as the
diameter of the complement and discusses `Gᶜ.ediam.toNat`.  However, the Lean
declaration currently displayed in that same file contains
`degreeL2Norm Gᶜ` instead.

This bridge matches and proves the Lean declaration exactly.  It does not
identify the squared-degree norm with complement diameter, and it must not be
presented as a proof of the historical diameter reading without a separate
formalization and proof.

## Verification

After generating the v18 dependency object, the bridge was checked with:

```bash
LEAN_PATH=/tmp/c5k4-proof100-bridge timeout 60s lake env lean \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture100UpstreamBridge.lean
```

Result: exit code 0, no diagnostics, approximately six seconds.  The bridge
contains no `sorry`, `admit`, `native_decide`, or custom axiom.

The dependency object was generated locally only for verification.  No
generated `.olean` artifact belongs in the repository.

## Review consequence

The proof term required to replace the upstream placeholder is now explicit
and minimal.  A reviewer does not need to reconstruct equivalence between a
local residual theorem and the upstream target: elaboration directly checks
that v18 inhabits the precise upstream signature, with `hGc` merely stronger
than necessary.
