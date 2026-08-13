# Method v0.18: WOWII 61 cumulative eliminated-head credit

Date: **2026-08-13 UTC**

Outcome: **banked degree-loss credit is exactly twice the banked difference of
cumulative eliminated heads along admissible histories.**  The local
head-credit inequality is formally equivalent to extending cumulative
eliminated-head order by one step.

This isolates the minimal induction invariant:

```text
for every k,
  cumulativeTargetHeads(k) <= cumulativeSourceHeads(k).
```

It is exactly the cumulative residual/profile condition in head coordinates,
not a stronger successor-prefix assumption.

This lane does not derive that invariant generally from initial degree
majorization and does not prove WOWII 61.

## Frozen scope

- New certificate only: `lean/GraphConjecture61CumulativeCredit.lean`.
- New report only:
  `results/expansion/method_v18_61_cumulative_credit.md`.
- No existing file was edited.  No commit, push, release, issue, PR, or other
  public action was made.
- Every subprocess was capped at 60 seconds.

## Cumulative eliminated heads

The certificate defines

```text
headDegree [] = 0
headDegree (d :: rest) = d

cumulativeHeadSum(0,s) = 0
cumulativeHeadSum(k+1,s) =
  headDegree(s) + cumulativeHeadSum(k,step(s)).
```

`AdmissibleFor k s` states explicitly that the first `k` states are nonempty
and each satisfies the local Havel--Hakimi admissibility condition.  No
graphicality or termination premise is hidden.

## Exact loss-head identity

The source independently kernel-proves the list arithmetic needed for

```text
StepAdmissible(d :: rest) -> stepLoss(d :: rest) = 2d.
```

Structural induction on an admissible history then yields

```text
cumulativeStepLoss(k,s) = 2 * cumulativeHeadSum(k,s).
```

Thus the entire profile/loss calculus can be expressed using only the sequence
of eliminated maximum degrees.

## Exact credit identity

When cumulative target heads are bounded by cumulative source heads, Lean
proves

```text
credit(k)
  = cumulativeSourceLoss(k) - cumulativeTargetLoss(k)
  = 2 * (cumulativeSourceHeads(k) - cumulativeTargetHeads(k)).
```

Natural subtraction is exact because the head-order premise supplies the
required nonnegativity.

This is stronger clarification than merely observing that losses equal twice
heads pointwise: it identifies the actual bank balance after every prefix.

## Head credit is the induction step

Lean proves the central equivalence

```text
2 * targetHead(k) <= credit(k) + 2 * sourceHead(k)
```

if and only if

```text
cumulativeTargetHeads(k) + targetHead(k)
  <= cumulativeSourceHeads(k) + sourceHead(k).
```

The right side is precisely cumulative head order at time `k+1` after using
the recursion

```text
cumulativeHeadSum(k+1,s)
  = cumulativeHeadSum(k,s) + headDegree(step^[k](s)).
```

Therefore v0.17's local funding condition is not an independent lemma waiting
to be proved: it is exactly the one-step preservation statement for cumulative
eliminated-head order.

## Minimal invariant

The certificate defines

```text
CumulativeHeadDominates horizon source target :=
  for every k <= horizon,
    cumulativeTargetHeads(k) <= cumulativeSourceHeads(k).
```

It proves the reusable induction rule:

```text
CumulativeHeadDominates k source target
admissibility through k
head-credit inequality at time k
------------------------------------------------
CumulativeHeadDominates (k+1) source target.
```

This is the strongest honest result available from the credit approach.  It
removes successor prefix dominance, pointwise loss dominance, profile list
length constraints, and scalar-potential circularity.  What remains is one
specific cumulative maximum-degree inequality.

## Relation to initial majorization

At time zero, initial weak degree-prefix dominance gives

```text
targetHead(0) <= sourceHead(0),
```

so cumulative head order starts correctly.  At later times ordinary successor
head order can reverse: the order-four transfer reaches source head zero and
target head one.  The cumulative invariant survives because the source's
earlier head advantage is banked.

The desired general implication is now

```text
initial graphical weak degree-prefix dominance
------------------------------------------------
every prefix of canonical eliminated target heads
is bounded by the corresponding source prefix.
```

This implication is not proved here.  It appears to be the exact
Havel--Hakimi/majorization theorem underlying the project rather than a routine
algebraic corollary.

## Exact evidence and claim limit

The cumulative-head condition is equivalent, on admissible active histories,
to the cumulative residual condition audited previously.  The complete exact
scope remains:

```text
orders: 1 through 10
graphical sequences across separate orders: 22,083
weak graphical degree-prefix pairs: 105,582,418
cumulative-head failures: 0.
```

This is evidence only.  The Lean theorem does not invoke the audit, and the
report does not infer a general theorem from finite computation.

## Exact remaining boundary

Further progress requires a genuine majorization theorem for the sequence of
Havel--Hakimi heads.  Two plausible routes are:

1. characterize the cumulative eliminated-head sum after `k` steps as an
   extremal functional of the original degree sequence and prove that
   functional is monotone under graphical weak majorization;
2. construct a realization-aware coupled elimination showing that each target
   eliminated head can be charged either to the simultaneous source head or
   to previously unused source-head surplus.

Either route must explain the order-four head reversal while preserving the
cumulative sum.  Any proof demanding same-time head order is already refuted.

## Verification

From the pinned `formal-conjectures` checkout:

```bash
timeout 60s lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture61CumulativeCredit.lean
```

Result: **PASS** in approximately nine seconds.  The source contains no
unfinished proof, custom axiom, native evaluator, or external oracle.

## Verdict

The credit program has reached its irreducible combinatorial core.  Cumulative
degree-loss credit is twice cumulative eliminated-head surplus, and local
funding is exactly one-step preservation of cumulative head order.  The next
advance cannot come from more bookkeeping; it requires proving the monotonicity
of Havel--Hakimi head prefixes under graphical weak majorization.
