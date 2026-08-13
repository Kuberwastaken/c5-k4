# Method v0.17: WOWII 61 head-credit reduction

Date: **2026-08-13 UTC**

Outcome: **the local credit-funding condition is formally equivalent to a
head-degree inequality at every pair of admissible active states.**

```text
targetLoss <= credit + sourceLoss
```

becomes exactly

```text
2 * targetHead <= credit + 2 * sourceHead.
```

The head-credit condition has no failure in the complete graphical weak-prefix
audit through order ten, because the v0.16 local credit theorem and this formal
equivalence identify the two predicates on admissible active histories.

This lane does not prove that initial graphical weak prefix order forces the
head-credit inequality in all orders, and it does not prove WOWII 61.

## Frozen scope

- New certificate only: `lean/GraphConjecture61HeadCredit.lean`.
- New report only: `results/expansion/method_v17_61_head_credit.md`.
- No existing file was edited.  No commit, push, release, issue, PR, or other
  external mutation was made.
- Every subprocess was capped at 60 seconds.

## Reused admissible loss theorem

The certificate independently carries the exact list-side graphical condition

```text
StepAdmissible (d :: rest) :=
  d <= length(rest)
  and every entry of rest.take d is positive.
```

It kernel-proves the supporting arithmetic and list facts:

```text
length(a) <= sum(a)                       for positive a
sum(map pred a) = sum(a) - length(a)      for positive a
sum(step(d :: rest)) = sum(rest) - d      under admissibility
stepLoss(d :: rest) = 2d.                 under admissibility
```

The successor-sum proof explicitly splits the tail, computes the decremented
prefix, and uses merge-sort permutation invariance.  No evaluator or external
certificate is used.

## Exact funding equivalence

For arbitrary natural credit and two admissible nonempty degree lists, Lean
proves

```text
stepLoss(target) <= credit + stepLoss(source)
  iff
2 * targetHead <= credit + 2 * sourceHead.
```

This is direct rewriting by the two exact loss identities.  It reduces the
remaining local credit problem from whole successor lists to three natural
numbers: the current credit and the two heads.

## Time-indexed interface

`HeadCreditFundedAt k source target` explicitly carries:

1. decompositions of both `k`-th canonical iterates into a head and tail;
2. admissibility of both current lists;
3. the head-credit inequality using the actual cumulative credit at time `k`.

Lean proves both interfaces:

```text
HeadCreditFundedAt k source target
  -> local credit budget at time k,
```

and, given explicit current decompositions and admissibility,

```text
local credit budget at time k
  -> HeadCreditFundedAt k source target.
```

Thus the time-indexed head predicate is neither weaker nor stronger than local
funding on active admissible states.

## Exact bounded search

The head-credit predicate was evaluated on the same complete canonical
graphical histories used in v0.12 and v0.16:

```text
orders: 1 through 10
graphical sequences across separate orders: 22,083
initial weak graphical degree-prefix pairs: 105,582,418
head-credit failures: 0.
```

At each common active time, the search computed

```text
credit = cumulativeSourceLoss - cumulativeTargetLoss
```

and tested

```text
2 * targetHead <= credit + 2 * sourceHead.
```

Terminal zero states were skipped rather than assigned a fictitious positive
head.  The result is exact finite evidence only.  It is also consistent with
the formal equivalence: the earlier audit found no local-credit/cumulative-
residual failure in the same scope.

## Minimal zero-credit obstruction remains repaired

At order four:

```text
source [2,1,1,0] -> [0,0,0]
target [1,1,1,1] -> [1,1,0].
```

After the first step the source has banked two units of credit.  At the next
active target step, the effective heads are source zero and target one, so

```text
zero-credit head rule: 2 <= 0       false
banked head-credit rule: 2 <= 2 + 0 true.
```

The same order-four pair is therefore the first obstruction to discarding
credit, while the funded rule holds with equality.

## Strongest formal class

Every pair of active admissible iterates satisfying the head-credit inequality
belongs to the local-credit class of v0.16.  Consequently, chaining
`HeadCreditFundedAt` over a horizon supplies cumulative solvency and the
chronological excess-profile conclusion via the already isolated local rule.

The file also proves admissibility for every positive regular degree shape

```text
d :: replicate n d, with 0 < d and d <= n.
```

This gives an infinite explicit class where the loss-to-head reduction is
immediately available at the current state.

## Remaining graph-theoretic obligation

The target is now a head-credit theorem:

```text
initial graphical weak prefix dominance
canonical coupled histories through time k
credit solvent through time k
------------------------------------------------
2 * targetHead(k) <= credit(k) + 2 * sourceHead(k).
```

Ordinary successor head order is false, as the order-four example shows.  The
proof must explain how earlier head advantage, stored as credit, controls later
head reversal.  Since every admissible loss is twice the head, no additional
degree-sum algebra remains hidden behind this statement.

A plausible next move is to rewrite credit as twice the cumulative difference
of eliminated heads on fully admissible histories.  The desired inequality
would then become a prefix comparison between cumulative head sums, potentially
closer to the original degree-prefix majorization.

## Verification

From the pinned `formal-conjectures` checkout:

```bash
timeout 60s lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture61HeadCredit.lean
```

Result: **PASS** in approximately seven seconds.  The source contains no
unfinished proof, custom axiom, native evaluator, or external oracle.

## Verdict

The local funding problem is now a pure head inequality.  Exact admissible
loss evaluation removes the successor lists entirely, and the head-credit rule
is formally interchangeable with v0.16's local credit rule.  It survives the
complete order-ten graphical audit; the remaining task is to derive it from
initial graphical weak prefix structure rather than take it as the defining
solvency condition.
