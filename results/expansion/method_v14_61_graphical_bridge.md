# Method v0.14: WOWII 61 admissibility bridge and successor obstruction

Date: **2026-08-13 UTC**

Outcome: **the local admissibility bridge is formal for every positive regular
degree shape, while exact search and Lean isolate the first obstruction to
using ordinary weak prefix dominance as the recursive successor relation.**

The obstruction is the already central order-four pair

```text
[2,1,1,0] -> [0,0,0]
[1,1,1,1] -> [1,1,0].
```

The source weakly prefix-dominates the target initially, but not after one
canonical step.  Both initial steps satisfy the exact local admissibility
condition.  The weaker residual degree-sum coupling survives.

This lane does not prove the general graph-realization-to-admissibility bridge,
successor prefix preservation, or WOWII 61.

## Frozen scope

- New certificate only: `lean/GraphConjecture61GraphicalBridge.lean`.
- New report only: `results/expansion/method_v14_61_graphical_bridge.md`.
- No existing file was edited.  No commit, push, release, issue, PR, or other
  external mutation was made.
- Every subprocess was capped at 60 seconds.

## Formal admissibility bridge

The exact list-side property remains

```text
StepAdmissible (d :: rest) :=
  d <= length(rest)
  and every entry of rest.take d is positive.
```

Lean now proves the infinite degree-shape theorem

```text
0 < d
d <= n
--------------------------------------
StepAdmissible (d :: replicate n d).
```

This covers every positive regular simple-graph degree sequence once its known
degree shape is supplied.  Two named specializations make the realized
families explicit mathematically:

- complete graphs: degree `n` repeated `n+1` times;
- cycles of order at least three: degree two at every vertex.

The all-zero terminal shape is also proved admissible.

The certificate intentionally does not assert a general theorem taking an
arbitrary explicit `SimpleGraph` realization, sorting its degree multiset, and
returning `StepAdmissible`.  That proof requires a formal counting bridge:
the maximum-degree vertex's `d` distinct neighbors all contribute positive
entries, and sorting places at least `d` such entries immediately after the
head.  This finite multiset/sort interface is not hidden as an assumption.

## Exact successor search

An exact search generated all descending graphical degree sequences and all
weak prefix ordered pairs by increasing order.  It tested whether the canonical
successors retained the same dominance orientation.

Results:

```text
orders 1,2,3: no failure
order 4: first failure
```

The first failure is

```text
source = [2,1,1,0]   (P3 plus an isolated vertex)
target = [1,1,1,1]   (a four-vertex perfect matching).
```

Their initial prefix sums are ordered source over target.  Their successors
have degree sums zero and two respectively, so source-over-target weak prefix
dominance is impossible after the step.

This exact search used Havel--Hakimi graphicality and stopped at the first
obstruction.  It is a minimality audit, not a full induction theorem.

## Kernel-checked obstruction

Lean proves both initial lists are `StepAdmissible` and proves their weak degree-
prefix order.  It then proves the general admissible successor-sum identity

```text
sum(havelHakimiStep(d :: rest)) = sum(rest) - d.
```

The proof explicitly splits the tail, computes the sum of the decremented
positive prefix, and uses merge-sort permutation invariance.  Applying this
identity gives successor sums zero and two.  If successor prefix dominance
held, its full-prefix instance would say two is at most zero, a contradiction.

No native evaluator is used: all concrete claims are checked by the kernel
with `decide`, `norm_num`, explicit list reasoning, and the general sum theorem.

## Corrected one-step relation

The file records

```text
ResidualCoupledStep source target :=
  DegreePrefixDominates source target
  and sum(target) + sum(step(source))
        <= sum(source) + sum(step(target)).
```

The obstructing pair satisfies this corrected coupling strictly.  This agrees
with v0.13: local admissibility makes each loss twice its head, so initial
prefix-one order controls the residual total gap even though the entire
successor prefix relation reverses.

The residual relation is a valid one-step replacement, not yet a recursive
relation.  Reapplying it requires a new coupled state that remains meaningful
after successor dominance changes orientation.

## Exact remaining boundary

Two separate tasks remain:

1. formalize the arbitrary-realization bridge from sorted graph degrees to
   `StepAdmissible` using neighbor-support counting and sorting;
2. replace same-orientation successor dominance by a relation compatible with
   the zero-padded excess profile, since ordinary prefix dominance is formally
   refuted at the first nontrivial order.

A plausible next formal object is a coupled state carrying initial degree-
prefix order together with all residual total gaps reached so far, without
requiring successor prefix order itself.

## Verification

From the pinned `formal-conjectures` checkout:

```bash
timeout 60s lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture61GraphicalBridge.lean
```

Result: **PASS** in approximately eight seconds.  The source contains no
unfinished proof, custom axiom, or non-kernel evaluation tactic.

## Verdict

The admissibility interface now covers infinite regular graph families, and
the naive recursive relation is decisively closed: weak degree-prefix dominance
need not survive one canonical step, first failing at order four.  Residual
degree-sum coupling is the correct one-step invariant; the remaining challenge
is to make it recursive without reintroducing the refuted successor-prefix
premise.
