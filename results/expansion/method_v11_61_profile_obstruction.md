# Method v0.11: WOWII 61 profile obstruction and padded repair

Date: **2026-08-13 UTC**

Outcome: **weak graphical prefix dominance does not force the v0.10
`PrefixExcessDominates` relation.**  The first obstruction occurs at order four:

```text
source = [2,1,1,0]   profile [2]
target = [1,1,1,1]   profile [0,0].
```

Both lists have explicit graph realizations and the source weakly
prefix-dominates the target.  The original coupling fails only because its
target-profile-length premise says `2 <= 1`.

Removing that artificial premise and comparing chronological prefixes with
implicit trailing-zero padding repairs the example.  Exact enumeration found
no failure of the repaired relation among all 656,935 weakly ordered graphical
degree-sequence pairs through order eight.

This is bounded evidence, not a proof that weak graphical prefix dominance
always forces the repaired coupling.  This lane does not prove WOWII 61.

## Frozen scope

- New Lean certificate only:
  `lean/GraphConjecture61ProfileObstruction.lean`.
- New report only:
  `results/expansion/method_v11_61_profile_obstruction.md`.
- Fixed-scope machine ledger only:
  `results/expansion/method_v11_61_profile_obstruction_ledger.json`.
- No existing file was edited.  No commit, push, release, issue, PR, or other
  external mutation was made.
- Every search and compile subprocess was capped at 60 seconds.

## Exact bounded search

For every order `n = 1,...,8`, the search generated every descending sequence
of length `n` with entries in `[0,n-1]`, retained exactly the simple-graphical
sequences using Havel--Hakimi reduction, and tested every ordered pair satisfying
weak prefix dominance.

For each sequence, it computed the canonical descending Havel--Hakimi history
and chronological profile

```text
excess_i = stepLoss_i - 2.
```

The complete counts were:

| order | graphical sequences | weak-dominance pairs | padded failures |
|---:|---:|---:|---:|
| 1 | 1 | 1 | 0 |
| 2 | 2 | 3 | 0 |
| 3 | 4 | 10 | 0 |
| 4 | 11 | 64 | 0 |
| 5 | 31 | 467 | 0 |
| 6 | 102 | 4,702 | 0 |
| 7 | 342 | 50,077 | 0 |
| 8 | 1,213 | 601,611 | 0 |

Total: 1,706 graphical sequences across the eight separate orders and 656,935
weak-dominance pairs.  The completed search took approximately 8.1 seconds.
The JSON ledger preserves the fixed scope, algorithm, individual counts, first
obstruction, repaired definition, and claim limit.

## First obstruction to v0.10

The first failing pair by graph order is

```text
s = [2,1,1,0]   (P3 plus an isolated vertex)
t = [1,1,1,1]   (a perfect matching on four vertices).
```

Their canonical histories are:

```text
[2,1,1,0] -> [0,0,0]
loss             4
profile          [2]

[1,1,1,1] -> [1,1,0] -> [0,0]
losses            2          2
profile          [0,0].
```

The source weakly prefix-dominates the target.  The corrected potentials are

```text
Phi(s) = 10
Phi(t) = 8,
```

so the desired direction holds.  Nevertheless, the old relation begins with

```text
length([0,0]) <= length([2]),
```

which is false.  The obstruction is therefore not a mathematical reversal of
the excess budget; it is an artifact of comparing unpadded trajectory lengths.

Lean formalizes both finite graphs, both complete profiles, weak prefix
dominance, failure of the old coupling, and the exact potential values in
`first_profileLength_obstruction`.

## Corrected zero-padded coupling

The repaired relation is

```text
PaddedPrefixExcessDominates source target :=
  for every k <= length(target),
    sum(target.take k) <= sum(source.take k).
```

No explicit source-length condition remains.  Once `k` passes the end of the
source list, `source.take k` is the full source list, exactly as though its
profile had trailing zero entries.

Lean proves generally that padded prefix dominance implies total profile-sum
dominance.  Combining this with the v0.10 closed form gives the fully formal
sufficient theorem

```text
RealizedExcessTrajectory s sourceProfile
RealizedExcessTrajectory t targetProfile
WeakPrefixDominates s t
PaddedPrefixExcessDominates sourceProfile targetProfile
--------------------------------------------------------
Phi(t) <= Phi(s).
```

The order-four obstruction satisfies the repaired coupling.

## What the zero-free search means

The repaired implication survived every graphical weak-dominance pair through
order eight, including more than six hundred thousand pairs at order eight.
This is meaningful support for the padded profile as the next candidate
coupling, especially because the stronger v0.10 relation failed already at
order four.

It is not promoted to a theorem.  In particular, the search only uses canonical
descending Havel--Hakimi histories; it does not establish a realization-level
vertex coupling, nor does it cover orders above eight.

## Next proof obligation

The exact candidate is now:

```text
IsGraphical s
IsGraphical t
WeakPrefixDominates s t
--------------------------------
PaddedPrefixExcessDominates (profile s) (profile t).
```

A proof would need to show that every chronological target excess prefix is
budgeted by the corresponding zero-padded source prefix.  A falsification lane
should first extend exact or isomorphism-reduced testing beyond order eight.
If the candidate continues to survive, the natural proof approach is a
coupled elimination invariant for partial degree-sum loss, because each profile
prefix is precisely cumulative loss minus twice the number of completed steps.

## Verification

From the pinned `formal-conjectures` checkout:

```bash
timeout 60s lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture61ProfileObstruction.lean
```

Result: **PASS** in approximately seven seconds.  The source contains no
`sorry`, `admit`, or custom `axiom`.

## Verdict

The first proposed chronological coupling was too strict for a simple reason:
one graph may reach its zero terminal in fewer active steps.  The first exact
graphical obstruction appears at order four and is fully formalized.  Implicit
zero padding removes that defect, retains the sufficient monotonicity theorem,
and survives an exact 656,935-pair audit through order eight.
