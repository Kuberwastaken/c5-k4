# Method v0.13: WOWII 61 one-step residual-gap preservation

Date: **2026-08-13 UTC**

Outcome: **the one-step residual degree-sum gap is preserved under weak degree-
prefix dominance whenever both canonical steps satisfy the exact local
admissibility condition of descending graphical degree lists.**

The mechanism is now elementary and formal:

```text
stepLoss(d :: rest) = 2d.
```

Weak prefix dominance at prefix one gives `targetHead <= sourceHead`, hence
target loss is at most source loss.  That inequality is exactly one-step
residual-gap preservation.

The certificate deliberately does not claim that its `StepAdmissible` predicate
has yet been derived in Lean from the explicit graph-realization predicate.
Mathematically, a positive maximum-degree vertex has `d` positive-degree
neighbors; formalizing that realization-to-sorted-list bridge is the remaining
interface task.  This lane does not prove WOWII 61.

## Frozen scope

- New certificate only: `lean/GraphConjecture61ResidualGap.lean`.
- New report only: `results/expansion/method_v13_61_residual_gap.md`.
- No existing file was edited.  No commit, push, release, issue, PR, or other
  external mutation was made.
- Every subprocess was individually capped at 60 seconds.

## Minimal obstruction search

Before attempting the proof, exact enumeration tested one-step residual-gap
preservation on all weakly prefix-ordered graphical degree sequences through
order eight.  No obstruction occurred.

The absence of an obstruction has a structural explanation.  For an admissible
descending Havel--Hakimi step with head `d`:

1. deleting the head removes `d` degree-sum units;
2. decrementing the next `d` positive entries removes another `d` units;
3. sorting preserves the sum.

Thus the total loss is exactly `2d`.  Only the first degree-prefix comparison
is needed to order two such losses.

The search was diagnostic support for the proof route, not promoted to a
general theorem or separate novelty claim.

## Explicit local admissibility

`StepAdmissible` is defined directly on a list:

```text
StepAdmissible [] = True

StepAdmissible (d :: rest) :=
  d <= length(rest)
  and every entry of rest.take d is positive.
```

This does not hide graphicality or termination premises.  It states precisely
what the Havel--Hakimi sum calculation consumes.  In a descending simple-graph
degree sequence, the property is supplied by the head vertex's `d` neighbors,
each of which has positive degree.

The certificate first proves that a positive natural-number list has length at
most its sum, then proves

```text
sum(map pred a) = sum(a) - length(a)
```

for positive `a`.  These facts control natural-number subtraction without any
integer coercion or hidden nonnegativity assumption.

## Exact step-loss theorem

Lean proves:

```text
StepAdmissible (d :: rest)
------------------------------------------
sum(step(d :: rest)) = sum(rest) - d
stepLoss(d :: rest) = 2d.
```

The proof explicitly splits `rest` into its first `d` entries and its tail,
computes the decremented prefix sum, and uses `mergeSort_perm` to show sorting
does not alter the result.

## Residual-gap theorem

The direct weak degree-prefix relation records equal lengths and all prefix-sum
comparisons.  Prefix one gives

```text
targetHead <= sourceHead.
```

With admissibility of both steps:

```text
targetLoss = 2 * targetHead
           <= 2 * sourceHead
            = sourceLoss.
```

Lean then proves the exact residual condition left by v0.12:

```text
sum(target) + sum(step(source))
  <= sum(source) + sum(step(target)).
```

The companion theorem `first_excess_le` states the equivalent local profile
comparison:

```text
targetLoss - 2 <= sourceLoss - 2.
```

Therefore the first chronological excess prefix is always ordered for
admissible weakly prefix-ordered degree lists.

## Concrete non-equality instance

Lean checks the first graphical transfer numerically:

```text
source = [2,1,1,0]
target = [1,1,1,1].
```

Both steps are admissible and the source weakly prefix-dominates the target.
The losses are

```text
sourceLoss = 4
targetLoss = 2,
```

so residual-gap preservation is strict rather than merely an equality case.

## Exact remaining boundary

The result proves time one.  Reapplying it at time two requires two additional
facts:

1. both successors remain admissible descending graphical degree sequences;
2. the source successor still weakly prefix-dominates the target successor.

The first is standard Havel--Hakimi graphicality preservation, but its bridge
from explicit `SimpleGraph` realizations to this list predicate remains to be
formalized locally.  The second is stronger and is known not to hold in every
naive orientation from earlier lanes; a coupled or zero-padded relation is
needed when successor dominance changes orientation.

Thus v0.13 closes the one-step residual algebra but does not silently assert a
full induction.  The next useful target is the explicit realization theorem

```text
IsGraphicalDescending (d :: rest) -> StepAdmissible (d :: rest),
```

followed by a precise analysis of successor prefix order.

## Verification

From the pinned `formal-conjectures` checkout:

```bash
timeout 60s lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture61ResidualGap.lean
```

Result: **PASS** in approximately seven seconds.  The source contains no
unfinished proof, custom axiom, or non-kernel evaluation tactic; the concrete
finite certificate is checked by the kernel using `decide`, `norm_num`, and
explicit arithmetic.

## Verdict

The one-step residual-gap candidate is true under its exact graphical local
condition.  Its proof reveals that the residual invariant is controlled only
by the two leading degrees: every admissible step loses twice its head.  The
remaining difficulty is no longer loss accounting, but preservation or
replacement of weak prefix order along coupled successor trajectories.
