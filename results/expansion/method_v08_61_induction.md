# Method v0.8: WOWII 61 trajectory induction

Date: **2026-08-13 UTC**

Outcome: **the one-step corrected-potential identity now telescopes along an
arbitrary positive-head Havel--Hakimi trajectory.  The same certificate proves
that accumulated loss credit is exactly the lost degree sum, so this state is
equivalent to the original potential comparison rather than a stronger
induction hypothesis.**

This lane does not prove WOWII 61, the Griggs--Kleitman residue inequality, or
the general graphical weak-majorization proposition.

## Frozen scope

- New certificate only: `lean/GraphConjecture61Induction.lean`.
- Parent one-step result:
  `lean/GraphConjecture61GraphicalPotential.lean` at the inherited checkpoint.
- New report only:
  `results/expansion/method_v08_61_induction.md`.
- No existing file was edited.  No commit, push, release, issue, PR, or other
  external mutation was made in this lane.

## Exact trajectory state

The certificate independently restates the already established potential and
loss:

```text
Phi(s) = 2 * residueAux(s) + sum(s)
loss(s) = sum(s) - sum(step(s)).
```

It then defines

```text
cumulativeLoss(0,s) = 0
cumulativeLoss(k+1,s) = loss(s) + cumulativeLoss(k,step(s)).
```

`ActiveFor k s` is an explicit recursive premise saying that the first `k`
trajectory states each have a nonzero head.  This premise is not hidden: it is
exactly what permits Lean to use the positive-head recursion equation for
`residueAux`.

## Multi-step theorem

Lean proves, for every active trajectory,

```text
Phi(s) = Phi(step^[k](s)) + cumulativeLoss(k,s).
```

Therefore terminal budget order lifts to initial order for trajectories of
possibly different lengths:

```text
Phi(step^[kt](t)) + cumulativeLoss(kt,t)
  <= Phi(step^[ks](s)) + cumulativeLoss(ks,s)
------------------------------------------------
Phi(t) <= Phi(s).
```

This is the requested full telescoping/induction theorem.  It neither assumes
graphicality nor manufactures it for successor lists; those facts would have
to be supplied separately in any realization-aware proof.

## The decisive boundary

The stronger information is negative but exact.  For every list and every
number of steps, positivity is not needed to prove

```text
sum(s) = sum(step^[k](s)) + cumulativeLoss(k,s),
```

and hence

```text
cumulativeLoss(k,s) = sum(s) - sum(step^[k](s)).
```

The theorem `trajectory_budget_iff_initial_potential` then proves that, under
the explicit active-trajectory premises,

```text
terminal potential + accumulated loss is ordered
```

if and only if

```text
the initial potentials are ordered.
```

Thus iterating the scalar `stepLoss` credit does not create the missing
inductive strength.  It records exact accounting and simply transports the
original goal to a later point.  This rules out presenting accumulated scalar
loss as a proof of graphical weak-potential monotonicity.

The certificate also derives

```text
residueAux(s) = residueAux(step^[k](s))
```

along every active trajectory by subtracting the separately proved sum
identity from the potential identity.

## Concrete nonvacuity

`pathThreeWithIsolated_oneStep_certificate` instantiates the theorem at

```text
s = [2,1,1,0].
```

The head is positive, the canonical successor is `[0,0,0]`, the exact loss is
four, and Lean checks the complete potential decomposition.  This is an
actual positive-head trajectory, not a zero-step specialization.

## Remaining proof obligation

The desired general candidate remains

```text
IsGraphical s
IsGraphical t
WeakPrefixDominates s t
--------------------------------
Phi(t) <= Phi(s).
```

The v0.8 result shows that a successful induction must carry a genuinely
stronger realization-aware relation than one scalar accumulated-loss credit.
Candidates include a coupled matching between the two elimination histories,
or a structural theorem controlling the residue directly under graphical
unit transfers.  Immediate-successor potential order is already false, and
the accumulated scalar repair is now proved equivalent to the original goal.

## Verification

From the pinned `formal-conjectures` checkout:

```bash
timeout 60s lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture61Induction.lean
```

Result: **PASS** in approximately seven seconds.  The source contains no
`sorry`, `admit`, or custom `axiom`.  Every subprocess was individually capped
at 60 seconds.

## Verdict

The exact finite induction is complete, but it exposes rather than closes the
central gap.  Havel--Hakimi loss credit telescopes perfectly and has no slack;
as a result it cannot by itself prove the graphical weak-majorization theorem.
The next useful move must add combinatorial coupling information, not more
scalar bookkeeping.
