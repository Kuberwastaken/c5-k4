# Method v0.21: WOWII 61 tight second-head interval

Date: **2026-08-13 UTC**

Outcome: **the second canonical Havel--Hakimi head has a universal tight
two-sided bound.**  For a descending list `d :: e :: tail` with positive `d`,

```text
e - 1 <= headDegree(step(d :: e :: tail)) <= e.
```

This proves a genuine two-sequence monotonicity theorem: if the source strictly
dominates the target at the top-two degree prefix, then the target's first two
canonical eliminated heads sum to at most the source's.

The equality case of top-two prefix sums is not claimed.  It requires knowing
which endpoint of the interval each sequence attains.  This lane does not prove
full `k=2` monotonicity or WOWII 61.

## Frozen scope

- New certificate only: `lean/GraphConjecture61SecondHead.lean`.
- New report only: `results/expansion/method_v21_61_second_head.md`.
- No existing file was edited.  No commit, push, release, issue, PR, or other
  public action was made.
- Every subprocess was capped at 60 seconds.

## Upper bound

For any tail whose entries are all at most `e`, every entry in its canonical
successor is also at most `e`.  Lean proves this by transporting membership
through the merge-sort permutation:

- untouched entries retain the original bound;
- decremented entries satisfy `x - 1 <= x <= e`.

The successor of a list with nonempty tail is nonempty by the exact
Havel--Hakimi length theorem.  Its head is one of its entries, hence

```text
secondHead <= e.
```

## Lower bound

When `d > 0`, the first tail entry `e` belongs to `tail.take d`.  Therefore
`e - 1` belongs to the decremented prefix and survives merge sorting.

The successor is descending, so its head dominates every member, giving

```text
e - 1 <= secondHead.
```

Together:

```text
e - 1 <= secondHead <= e.
```

Since these are consecutive natural numbers, the second head is exactly one of
`e-1` or `e`.  The proof uses ordinary kernel-checked membership, permutation,
and pairwise-order reasoning.

## Both endpoints are real

Lean certifies graphical controls attaining both endpoints:

```text
[2,2,2,2]   -> [2,1,1]     second head = 2
[2,2,2,1,1] -> [1,1,1,1]   second head = 1.
```

Thus neither side can be improved universally.  The difference records whether
an undecremented entry of degree `e` remains competitive after the first step.

## Strict top-two monotonicity

Let source begin `ds, es` and target begin `dt, et`.  The target upper bound
and source lower bound give

```text
target cumulative two-head sum <= dt + et
source cumulative two-head sum >= ds + es - 1.
```

If

```text
dt + et < ds + es,
```

integrality supplies exactly the missing unit.  Lean proves

```text
cumulativeHeadSum 2 target <= cumulativeHeadSum 2 source.
```

The assumptions are explicit:

- source head is positive, so its second entry is actually decremented;
- target tail is bounded by its second entry, as in a descending sequence;
- strict top-two prefix dominance.

No graphicality assumption is needed beyond these degree-list properties.

## Remaining equality case

Under weak prefix majorization, the only unresolved `k=2` case is

```text
dt + et = ds + es.
```

The tight interval shows exactly what could go wrong: target may attain its
upper endpoint `et` while source attains its lower endpoint `es-1`.  A full
proof must rule out that endpoint combination using the remaining graphical
prefix constraints, or produce a graphical counterexample.

The previous complete order-ten audit found no failure of cumulative-head
monotonicity among 105,582,418 graphical weak-majorization pairs.  That is
evidence that graphicality resolves the equality case, not a proof of it.

## Candidate exact endpoint criterion

After decrementing the first `d` tail entries, the successor head equals `e`
exactly when an entry of original value `e` survives undecremented, or another
entry remains at `e`; otherwise it is `e-1` under the descending positive-head
conditions.

Formalizing this criterion requires counting the multiplicity of `e` relative
to the decrement boundary `d`.  The next proof target should state the endpoint
using `count e rest > d` (with care for equal entries and truncation), then use
the equal top-two prefix plus graphical weak-prefix constraints to compare the
source and target endpoint flags.

## Verification

From the pinned `formal-conjectures` checkout:

```bash
timeout 60s lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture61SecondHead.lean
```

Result: **PASS** in approximately nine seconds.  The source contains no
unfinished proof, custom axiom, native evaluator, or external oracle.

## Verdict

The second canonical head is now localized to a one-unit interval, and that
interval is sharp.  This closes `k=2` monotonicity whenever the source has a
strict top-two prefix advantage.  The entire remaining `k=2` problem is the
equal-prefix endpoint comparison, a substantially narrower graphical
multiplicity question.
