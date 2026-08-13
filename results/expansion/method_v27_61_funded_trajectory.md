# WOWII 61: globally funded Havel--Hakimi reversals

## Scope and outcome

This pass replaces the false idea of successor-prefix dominance with an exact
amortized invariant along the entire Havel--Hakimi trajectory.

New certificate:

```text
lean/GraphConjecture61FundedTrajectory.lean
```

The result has two layers:

1. a one-unit endpoint reversal is paid exactly by one unit of earlier strict
   cumulative surplus;
2. arbitrary larger reversals are paid by the exact accumulated head-credit
   bank, yielding a global induction theorem without successor dominance.

The bounded full-premise search found **no negative credit through order 10**.
It did, however, find the smallest obstruction to treating every reversal as
unit-sized: an order-five pair whose third head reverses by two and consumes a
two-unit bank exactly.

## Exact local funding law

At trajectory depth `k`, write

```text
head_k(s) = head(HH^k(s))
bank_k(source,target) = cum_k(source) - cum_k(target).
```

Under the already established comparison

```text
cum_k(target) <= cum_k(source),
```

Lean proves the exact equivalence

```text
cum_(k+1)(target) <= cum_(k+1)(source)
  ↔ head_k(target) <= bank_k(source,target) + head_k(source).
```

This is the local amortized rule.  It measures a reversal against accumulated
credit, not against a conjecturally preserved relation between the successor
lists.

For the endpoint-specialized case

```text
head_k(target) = head_k(source) + 1,
```

the rule sharpens to

```text
cum_(k+1)(target) <= cum_(k+1)(source)
  ↔ cum_k(target) < cum_k(source).
```

Thus one earlier strict unit is both necessary and sufficient to fund the bad
one-bit endpoint flag.

## Global theorem

`HeadReversalsFundedThrough k source target` requires the exact bank inequality
at every depth below `k`.  Lean proves

```text
HeadReversalsFundedThrough k source target
  -> forall j <= k, cum_j(target) <= cum_j(source).
```

The proof is an induction on trajectory depth using only the local bank.  It
never assumes that degree-prefix dominance survives a Havel--Hakimi step.

The file also retains the narrower
`UnitReversalsFundedThrough` theorem.  That theorem is useful for the exact
second-step survival-flag split developed in v0.26, but the new order-five
boundary shows why the unrestricted global invariant must allow a larger
withdrawal.

## Two exact boundary examples

### First unit reversal: order four

```text
source = [2,1,1,0]  (P3 plus an isolate)
target = [1,1,1,1] (a perfect matching)
```

The source weakly prefix-dominates the target.  Their head traces begin

```text
source: 2,0,0,0
target: 1,1,0,0.
```

The target's one-unit reversal at the second head consumes the source's
one-unit initial bank.  Lean proves that this pair is unit-funded through all
four depths and therefore retains cumulative-head order throughout.

### First non-unit reversal: order five

```text
source = [4,4,2,2,2]
target = [3,3,3,3,2].
```

Both are graphical, descending, have order five and degree sum fourteen, and
the source weakly prefix-dominates the target.  Their head traces begin

```text
source: 4,3,0,...
target: 3,2,2,...
```

After two heads the source has banked `7 - 5 = 2`.  At the third head the
target reverses by exactly two, consuming the entire bank and restoring a tie
at cumulative value seven.  Lean proves all of these numerical facts, proves
that the unit-only rule fails at this depth, and proves that the general bank
rule holds.

This pair is therefore not a negative-credit counterexample.  It is the
smallest exact countermodel to the proposed restriction that every local bad
reversal has size one.

## Bounded full-premise search

An exact increasing-order search enumerated every descending graphical degree
sequence of orders one through ten.  For every ordered same-order pair
`(source,target)` satisfying ordinary weak degree-prefix dominance, it computed
the entire canonical Havel--Hakimi head traces and tested every cumulative
prefix.

Counts were:

| order | graphical sequences | qualifying ordered pairs |
|---:|---:|---:|
| 1 | 1 | 1 |
| 2 | 2 | 3 |
| 3 | 4 | 10 |
| 4 | 11 | 64 |
| 5 | 31 | 467 |
| 6 | 102 | 4,702 |
| 7 | 342 | 50,077 |
| 8 | 1,213 | 601,611 |
| 9 | 4,361 | 7,477,797 |
| 10 | 16,016 | 97,447,686 |
| **total** | **22,083** | **105,582,418** |

No qualifying pair had

```text
cum_k(target) > cum_k(source)
```

at any depth.  This is bounded evidence only, not a theorem that initial
degree-prefix dominance always funds the whole Havel--Hakimi trajectory.

## Verification

After compiling the local v0.22--v0.26 import chain, the fresh check was:

```text
timeout 60s env LEAN_PATH=/Users/kuber.mehta/Projects/c5-k4/lean \
  lake env lean -R /Users/kuber.mehta/Projects/c5-k4/lean \
  -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture61FundedTrajectory.lean
```

It exited `0` in 6.57 seconds with no output.  The source contains no `sorry`,
`admit`, `native_decide`, or custom axiom.  Concrete computations use ordinary
kernel reduction, simplification, `norm_num`, and bounded `interval_cases`.

## Verdict and remaining bridge

The amortized induction mechanism is now formal at arbitrary depth.  Local
head reversals are harmless exactly when earlier eliminated heads have banked
enough surplus, and this statement needs no successor-prefix hypothesis.

The remaining substantive conjecture-specific step is to derive
`HeadReversalsFundedThrough` from the initial weak degree-prefix dominance of
two graphical sequences.  The exhaustive order-ten search gives strong finite
support for that bridge while the order-five example rules out a proof that
only analyzes one-bit endpoint reversals.  A successful proof must compare the
whole current bank with potentially multi-unit local withdrawals.
