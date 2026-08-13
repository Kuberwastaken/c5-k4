# Method v0.16: WOWII 61 explicit credit balance

Date: **2026-08-13 UTC**

Outcome: **cumulative residual coupling now has an exact local recursion.**  At
each canonical Havel--Hakimi step, the source may bank earlier excess degree
loss as natural-number credit.  A later target loss may exceed the simultaneous
source loss precisely when the banked credit covers it.

Lean proves that the local credit rule is equivalent to cumulative residual
coupling at every prefix.  Thus the repair is not an additional unmotivated
assumption; it is the recursive normal form of the v0.15 invariant.

This lane does not prove that graphical weak prefix dominance always supplies
the local credit budget, and it does not prove WOWII 61.

## Frozen scope

- New certificate only: `lean/GraphConjecture61CreditBalance.lean`.
- New report only: `results/expansion/method_v16_61_credit_balance.md`.
- No existing file was edited.  No commit, push, release, issue, PR, or other
  external mutation was made.
- Every subprocess was capped at 60 seconds.

## Explicit credit

For source and target degree lists, define

```text
credit(k) = cumulativeSourceLoss(k) - cumulativeTargetLoss(k).
```

Whenever the coupling has remained solvent through time `k`, natural
subtraction is exact and Lean proves

```text
credit(k) + cumulativeTargetLoss(k)
  = cumulativeSourceLoss(k).
```

The exact update equation is

```text
credit(k+1)
  = credit(k) + sourceLoss(k) - targetLoss(k).
```

This makes the order-four phenomenon transparent: the source first earns two
units of credit, then spends both when the target's second loss exceeds the
source's second loss by two.

## Local solvency rule

The recursive local condition is

```text
targetLoss(k) <= credit(k) + sourceLoss(k).
```

Unlike the failed pointwise condition, it does not require
`targetLoss(k) <= sourceLoss(k)`.  Earlier source advantage is retained rather
than discarded at the successor boundary.

The certificate packages the condition through a fixed horizon:

```text
LocalCreditRuleFor horizon source target :=
  for every k < horizon,
    targetLoss(k) <= credit(k) + sourceLoss(k).
```

It separately packages cumulative solvency:

```text
CreditSolventFor horizon source target :=
  for every k <= horizon,
    cumulativeTargetLoss(k) <= cumulativeSourceLoss(k).
```

## Exact equivalence

Lean proves both directions:

```text
LocalCreditRuleFor k source target
  -> CreditSolventFor k source target

CreditSolventFor k source target
  -> LocalCreditRuleFor k source target.
```

The forward proof inducts over prefix length.  At each step, the local budget
and the exact credit identity extend cumulative solvency by one.

The reverse proof compares cumulative losses at times `j` and `j+1`, then
subtracts the already solvent prefix through the exact credit equation.

Therefore

```text
LocalCreditRuleFor k source target
  iff CreditSolventFor k source target.
```

This is the requested explicit natural-number credit recursion equivalent to
cumulative residual coupling.

## Strongest formally preserved class

The strongest class proved in this lane is every source-target pair satisfying
the local credit rule through its chosen horizon.  For that entire class Lean
proves

```text
cumulativeTargetLoss(k) - 2k
  <= cumulativeSourceLoss(k) - 2k.
```

This is the coupled chronological excess conclusion needed by the profile
method.  No successor prefix-dominance premise appears.

The certificate also proves a one-step extension theorem: solvency through
time `k` plus the single local budget at time `k` yields solvency through
`k+1`.  This is the reusable induction rule that v0.15 lacked.

## Minimal obstruction to the zero-credit rule

Exact graphical search confirms that discarding banked credit first fails at
order four.  The minimal pair is

```text
source = [2,1,1,0]   losses 4,0
target = [1,1,1,1]   losses 2,2.
```

At time zero, target loss two is at most source loss four, and the source banks
credit two.  At time one:

```text
zero-credit rule: 2 <= 0       false
banked-credit rule: 2 <= 2 + 0 true.
```

Thus the first obstruction is repaired exactly, with no slack.

## Exact bounded preservation evidence

Because the local credit rule is formally equivalent to cumulative residual
coupling, the complete v0.11--v0.12 audit applies unchanged:

```text
orders: 1 through 10
graphical sequences across separate orders: 22,083
weak graphical degree-prefix pairs: 105,582,418
local credit failures: 0.
```

This is exact finite evidence.  It is not promoted to a theorem that graphical
weak prefix dominance always funds the credit account.

## Remaining proof obligation

The general problem is reduced to a local funding theorem:

```text
given the current graph realizations, original weak degree-prefix order,
and nonnegative banked credit,
show targetLoss <= credit + sourceLoss.
```

At time zero, v0.13 proves the rule because admissible loss is twice the head
and prefix one orders the heads.  At later times the successor head order may
reverse, but the account contains precisely the earlier head/loss advantage.

The next useful proof target is therefore a head-credit inequality along
canonical elimination:

```text
2 * targetHead(k) <= credit(k) + 2 * sourceHead(k)
```

under explicit graphical admissibility.  Exact search should first test this
head form separately; if it survives, it is algebraically identical to the
local funding condition but exposes the graph-theoretic quantity to control.

## Verification

From the pinned `formal-conjectures` checkout:

```bash
timeout 60s lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture61CreditBalance.lean
```

Result: **PASS** in approximately ten seconds.  The source contains no
unfinished proof, custom axiom, native evaluator, or external oracle.

## Verdict

The cumulative repair is now fully recursive.  Credit is an explicit natural
balance, its update law is proved, and local solvency is exactly equivalent to
all-prefix cumulative residual coupling.  The minimal order-four reversal is
funded with equality.  What remains is the graph-theoretic theorem guaranteeing
that weakly ordered graphical histories never overdraw this account.
