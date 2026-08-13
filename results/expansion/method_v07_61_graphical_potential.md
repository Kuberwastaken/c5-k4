# Method v0.7: WOWII 61 graphical one-step potential

Date: **2026-08-13 UTC**

Outcome: **the corrected potential now has a general one-step lifting theorem,
and the first false recursive strengthening has an exact graphical
counterexample.**  The full `GraphicalWeakPotentialMonotone` proposition is
not proved or asserted.

This lane does not prove WOWII 61, the Griggs--Kleitman inequality, or general
graphical-transfer residue monotonicity.

## Frozen scope

- New certificate only:
  `lean/GraphConjecture61GraphicalPotential.lean`.
- Parent recursive-potential result: commit `6bf23a9`.
- New report only:
  `results/expansion/method_v07_61_graphical_potential.md`.
- No committed source was edited and no commit, push, release, upstream
  mutation, or Maxine induction was attempted.

## Reused invariant

The certificate uses

```text
Phi(s) = 2 * residueAux(s) + sum(s)
stepLoss(s) = sum(s) - sum(havelHakimiStep(s)).
```

It independently re-establishes the two generic facts needed in this
standalone certificate:

```text
sum(havelHakimiStep(s)) <= sum(s)

Phi(d :: rest)
  = Phi(havelHakimiStep(d :: rest)) + stepLoss(d :: rest)
```

for positive `d`.

## Strongest proved recursive rung

The new theorem `residuePotential_le_of_oneStep_budget` states:

```text
Phi(step(t)) + stepLoss(t)
  <= Phi(step(s)) + stepLoss(s)
-------------------------------------------------
Phi(t) <= Phi(s)
```

when both list heads are positive.

This looks algebraically simple only after the correct invariant has been
found.  It is the exact recursion rule needed when the raw successor
potentials reverse order: the current comparison is recovered by carrying the
degree-sum loss as credit.

For the committed first graphical transfer,

```text
s = [2,1,1,0]
t = [1,1,1,1],
```

Lean checks both the weak-prefix relation and the loss-budgeted premise, then
recovers `Phi(t) <= Phi(s)` in
`committed_first_transfer_oneStep_budget`.

## First obstruction to naive successor induction

Exact enumeration of graphical weak-dominance pairs found the first failure
of the stronger claim

```text
Phi(t) <= Phi(s)  ->  Phi(step(t)) <= Phi(step(s)).
```

at order four.  The pair is

```text
s = [3,2,2,1]   (the paw graph)
t = [2,2,2,2]   (the four-cycle).
```

Both graphicality claims are carried by explicit `SimpleGraph (Fin 4)`
realizations in Lean.  The source weakly prefix-dominates the target, and

```text
Phi(s) = Phi(t) = 12.
```

But after one canonical step,

```text
Phi(step(s)) = 6
Phi(step(t)) = 8.
```

Thus successor order reverses by two.  The exact losses are

```text
stepLoss(s) = 6
stepLoss(t) = 4,
```

so the source carries exactly two additional units of loss credit.  Adding
that credit restores equality:

```text
8 + 4 = 6 + 6.
```

Lean certifies the complete realization and arithmetic table in
`first_successor_order_obstruction`.

This is not a counterexample to `GraphicalWeakPotentialMonotone`; that
candidate holds with equality on the current lists.  It is a counterexample
to the tempting inductive sublemma that discards `stepLoss`.

## Minimality and bounded falsification

The successor-order claim was checked exactly on all descending graphical
degree sequences through order four.  No failure occurs at orders one, two,
or three; the paw/four-cycle pair is the first by graph order.  The search
stopped once this exact witness was obtained and formalized.

The earlier v0.6 checks remain the evidence for the larger candidate:

- all graphical weak-dominance pairs through order nine;
- 526,772 exact graphical atomic-transfer successors through order ten; and
- 570,544 sampled graphical transfers through completed order 21

produced no failure of the corrected-potential direction.  Those checks are
not promoted to proof here.

## Exact remaining boundary

The full desired proposition remains

```text
IsGraphical s
IsGraphical t
WeakPrefixDominates s t
--------------------------------
Phi(t) <= Phi(s).
```

The v0.7 obstruction shows that a recursive proof cannot demand the same
potential order from the bare successors.  It must propagate the stronger
budgeted state

```text
Phi(step(t)) + credit_t
  <= Phi(step(s)) + credit_s,
```

where the credits include the exact `stepLoss` accumulated along the two
Havel--Hakimi trajectories.

A future proof must therefore establish a realization-aware invariant for
the accumulated loss budget, not merely weak dominance of each immediate
successor.  No unproved version of that invariant is asserted in this lane.

## Verification

From the pinned `formal-conjectures` checkout:

```bash
timeout 60s lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture61GraphicalPotential.lean
```

Result: **PASS** in approximately seven seconds.  The source contains no
`sorry`, `admit`, or custom `axiom`.  Every compile and falsification process
was individually bounded by 60 seconds.

## Verdict

The graphical-potential route remains viable, but its recursion is now more
precise: raw successor order is false at the first nontrivial four-vertex
obstruction, while exact loss-budgeted lifting is proved for all lists.  The
next mathematical task is to control accumulated `stepLoss` from explicit
graph realizations; searching for a same-order successor theorem would pursue
a formally refuted direction.
