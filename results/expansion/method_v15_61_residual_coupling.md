# Method v0.15: WOWII 61 cumulative residual coupling

Date: **2026-08-13 UTC**

Outcome: **pointwise one-step loss coupling is not recursively preserved, but
the corrected cumulative residual state gives exactly the chronological
profile-prefix conclusion without any successor prefix-dominance premise.**

The first pointwise obstruction is again order four:

```text
source [2,1,1,0] losses 4,0
target [1,1,1,1] losses 2,2.
```

The first losses are ordered, but the second losses reverse (`2 <= 0` is
false).  Cumulatively, however, the prefixes are

```text
source 4,4
target 2,4,
```

so the source's earlier credit exactly budgets the later reversal.

This lane does not prove that weak graphical degree-prefix dominance forces
the cumulative state in all orders, and it does not prove WOWII 61.

## Frozen scope

- New certificate only: `lean/GraphConjecture61ResidualCoupling.lean`.
- New report only:
  `results/expansion/method_v15_61_residual_coupling.md`.
- No existing file was edited.  No commit, push, release, issue, PR, or other
  external mutation was made.
- Every subprocess was capped at 60 seconds.

## First attempted recursive state

The certificate first defines the natural pointwise recursion

```text
ResidualCouplingFor 0 source target = True

ResidualCouplingFor (k+1) source target =
  stepLoss(target) <= stepLoss(source)
  and ResidualCouplingFor k (step(source)) (step(target)).
```

No successor prefix relation appears.  Lean proves that this state orders the
total accumulated loss and therefore the accumulated excess after subtracting
the common `2k` baseline.

It also proves that its one-step loss premise is equivalent to the residual
degree-sum inequality

```text
sum(target) + sum(step(source))
  <= sum(source) + sum(step(target)).
```

Thus this is exactly the recursive version suggested by v0.13, not a newly
invented stronger numerical condition.

## Minimal exact obstruction

Exact graphical degree-sequence search by increasing order found no pointwise
recursive failure through order three.  The first failure is

```text
source = [2,1,1,0]
target = [1,1,1,1].
```

The source initially weakly prefix-dominates the target.  Canonical elimination
gives

```text
source: [2,1,1,0] -> [0,0,0] -> [0,0]
losses:                  4          0

target: [1,1,1,1] -> [1,1,0] -> [0,0]
losses:                  2         2.
```

At the second layer, target loss two is not at most source loss zero.  Therefore
the pointwise recursive state is false even though the desired potential order
and the zero-padded profile order both hold.

This is an actual minimal obstruction to the proposed recursive invariant, not
a counterexample to WOWII 61.

## Correct cumulative state

The repaired invariant is

```text
CumulativeResidualCouplingFor k source target :=
  for every j <= k,
    cumulativeLoss(j,target) <= cumulativeLoss(j,source).
```

It permits a later target loss to exceed the corresponding source loss when
the source accumulated enough earlier credit.  No successor degree-prefix
orientation is required.

Lean proves:

```text
ResidualCouplingFor k source target
  -> CumulativeResidualCouplingFor k source target,
```

so the corrected state genuinely weakens the failed pointwise recursion.

## Exact sufficient profile invariant

Define

```text
cumulativeExcess(k,s) = cumulativeLoss(k,s) - 2k.
```

Because both histories subtract the identical baseline, Lean proves for every
prefix `j <= k`:

```text
CumulativeResidualCouplingFor k source target
------------------------------------------------
cumulativeExcess(j,target) <= cumulativeExcess(j,source).
```

This is the exact chronological excess-profile conclusion while the two
histories are coupled for `j` steps.  It is conditional on the cumulative
state, but it is neither circularly restating potential order nor assuming
successor prefix dominance.

## Telescoping and iterate form

Lean independently proves the all-list identity

```text
sum(s) = sum(step^[k](s)) + cumulativeLoss(k,s).
```

Consequently, the cumulative state is equivalent in direction to requiring
every iterate residual gap

```text
sum(target) + sum(step^[j](source))
  <= sum(source) + sum(step^[j](target))
```

for all `j <= k`.  The certificate proves this iterate presentation from the
cumulative coupling at every prefix.

## Exact bounded preservation evidence

The cumulative condition is the same zero-padded residual/profile condition
audited in v0.11 and v0.12.  It has no failure among all weakly prefix-ordered
graphical degree-sequence pairs through order ten:

```text
orders: 1 through 10
graphical sequences across separate orders: 22,083
weak-dominance pairs: 105,582,418
cumulative residual failures: 0.
```

The pointwise condition failed at order four, while the cumulative repair
survived the complete order-ten scope.  These are exact finite results, not a
general theorem inferred from computation.

## Remaining proof obligation

The target proposition is now sharply isolated:

```text
graphical source and target
weak degree-prefix dominance source over target
------------------------------------------------
CumulativeResidualCouplingFor every relevant prefix.
```

Equivalently, every target cumulative degree loss must be budgeted by the
source cumulative degree loss.  The order-four obstruction shows this cannot
be proved by ordering individual successor losses.  A proof must preserve the
banked source credit across reversals.

A useful next formal step is a credit-balance recursion

```text
credit_(j+1) = credit_j + sourceLoss_j - targetLoss_j
```

over integers or naturals with an explicit nonnegativity invariant.  That form
may support local graphical transfer arguments even when the instantaneous
loss difference is negative.

## Verification

From the pinned `formal-conjectures` checkout:

```bash
timeout 60s lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture61ResidualCoupling.lean
```

Result: **PASS** in approximately eight seconds.  The source contains no
unfinished proof, custom axiom, native evaluator, or external oracle.

## Verdict

The naive loss-by-loss recursion is formally too strong and fails at the first
nontrivial order.  The correct state is cumulative: earlier excess loss is
banked as credit and may pay for a later reversal.  Lean proves that this state
is exactly sufficient for every chronological excess-prefix conclusion, and
the state remains obstruction-free in the complete order-ten graphical audit.
