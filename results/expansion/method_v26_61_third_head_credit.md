# WOWII 61: exact third-head credit and second-step endpoint flags

## Scope

This pass advances the Havel--Hakimi proof program from the completed two-head
comparison to depth three.  It deliberately does **not** assume that ordinary
degree-prefix dominance is preserved by the successor operation: v0.14 already
gave a formal counterexample to that tempting recursion.

The new certificate is:

```text
lean/GraphConjecture61ThirdHeadCredit.lean
```

## Exact credit identity

For a degree list `s`, define

```text
thirdHead s = headDegree (HH (HH s)).
```

The file proves the exact decomposition

```text
cumulativeHeadSum 3 s = cumulativeHeadSum 2 s + thirdHead s
```

and, whenever the source has weak two-head surplus, the equivalence

```text
cum₃ target ≤ cum₃ source
  ↔ thirdHead target ≤ (cum₂ source - cum₂ target) + thirdHead source.
```

Thus the already accumulated surplus is a literal integer credit account.  A
later head may reverse without breaking the cumulative comparison precisely
when that reversal fits inside the bank.

## Exact second-step flag split

Suppose the first successors have a common positive prefix

```text
HH source = d :: e :: sourceTail
HH target = d :: e :: targetTail
```

and both successor tails are bounded above by `e`.  The existing endpoint
criterion says that the next head is exactly `e` if an undecremented copy of
`e` survives beyond the first `d` successor entries, and is exactly `e - 1`
otherwise.

There are four possible pairs of survival flags.  The new theorem divides
them exactly:

| source flag | target flag | third-head effect | needed bank |
|---|---|---|---|
| survives | survives | tie | weak `cum₂` order |
| survives | does not | source leads by one | weak `cum₂` order |
| does not | does not | tie | weak `cum₂` order |
| does not | survives | target leads by one | **strict** `cum₂` order |

The first three rows are packaged by
`cumulativeHeadSum_three_of_secondStep_survival`: the implication “target
survives → source survives” rules out only the bad row.

The last row is characterized by the iff theorem
`cumulativeHeadSum_three_iff_two_strict_of_bad_secondStep_flag`.  In this row,

```text
cum₃ target ≤ cum₃ source ↔ cum₂ target < cum₂ source.
```

This is both sufficient and necessary; the single unit of strict earlier
surplus pays exactly for the single endpoint reversal.

## Small graphical countermodel to the naive weak extension

Weak two-head order alone cannot be promoted to depth three.  The file
kernel-checks the concrete pair

```text
source = [2,1,1]          (the degree sequence of P₃)
target = [1,1,1,1,1,1]  (the degree sequence of 3K₂).
```

Their eliminated-head traces begin

```text
source: 2, 0, 0
target: 1, 1, 1.
```

Hence both two-head sums equal `2`, but at depth three the target has `3 > 2`.
This is an actual graphical countermodel, not merely an abstract arithmetic
assignment, and it shows why some local credit or flag premise is necessary.

## Verification

The local import chain was compiled first, one process per file under the
60-second cap.  The fresh independent check was then:

```text
timeout 60s env LEAN_PATH=/Users/kuber.mehta/Projects/c5-k4/lean \
  lake env lean -R /Users/kuber.mehta/Projects/c5-k4/lean \
  -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture61ThirdHeadCredit.lean
```

It exited `0` in 7.64 seconds with no output.  The file contains no `sorry`,
`admit`, `native_decide`, or custom axiom.  The finite countermodel is reduced
by ordinary kernel-checked simplification and `norm_num`.

## Verdict and next frontier

The depth-three local theorem is complete.  It identifies the exact extra bit
of state missing from a naive recursive proof: the next endpoint-survival
flag, plus the integer credit already banked by earlier heads.

For WOWII 61 itself, the remaining global problem is no longer “prove
successor dominance.”  It is to show that every bad endpoint reversal along
the two Havel--Hakimi trajectories is funded by an earlier strict surplus (or
to find a graphical pair satisfying the conjecture's full premises where the
credit account first goes negative).  The present theorem is the local
induction step that such a global amortized argument must use.
