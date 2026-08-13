# Method v0.9: WOWII 61 realization-aware unit-loss coupling

Date: **2026-08-13 UTC**

Outcome: **a nontrivial realization-aware degree-sequence class now satisfies
the corrected weak-potential comparison.**  For complete Havel--Hakimi
trajectories whose every active step loses exactly two degree-sum units and
whose terminal list is all zero, Lean proves the closed form

```text
Phi(s) = 2 * length(s).
```

Consequently, any two realized lists in this class with the same order have
equal potential.  Weak prefix dominance supplies exactly that common-order
premise.

This does not prove WOWII 61, general graphical unit-transfer residue
monotonicity, or the unrestricted `GraphicalWeakPotentialMonotone` candidate.

## Frozen scope

- New certificate only: `lean/GraphConjecture61Coupling.lean`.
- New report only: `results/expansion/method_v09_61_coupling.md`.
- The v0.8 trajectory result was used as mathematical guidance, but no existing
  source file was edited.
- No commit, push, release, issue, PR, or other external mutation was made.

## Why this state is stronger than accumulated loss

The v0.8 lane proved that unconstrained accumulated scalar loss is circular:
terminal potential plus accumulated loss is exactly the initial potential.

The new inductive predicate `UnitLossTrajectory` adds two structural
restrictions at every stage:

1. the current head is positive and the next list is the actual canonical
   Havel--Hakimi successor;
2. that individual step loses exactly two units of degree sum.

The terminal constructor permits only an all-zero list.  This describes the
canonical elimination behavior of matching-type degree sequences.  The
predicate `RealizedUnitLossTrajectory` additionally requires an explicit
finite simple graph whose full descending degree list is the sequence;
numerical lists alone do not qualify.

## Closed-form potential theorem

At an all-zero terminal list of length `z`, Lean proves

```text
Phi(0^z) = 2z.
```

At each active step, the previously established recursion specializes to

```text
Phi(current) = Phi(successor) + 2.
```

Meanwhile `havelHakimiStep_length_cons` says the list length falls by exactly
one.  Induction therefore gives

```text
UnitLossTrajectory(s) -> Phi(s) = 2 * length(s).
```

This is not merely total-loss bookkeeping: the pointwise minimum-loss
condition classifies the entire elimination history and forces a closed form.

## Coupled monotonicity theorem

The certificate proves both

```text
RealizedUnitLossTrajectory(s)
RealizedUnitLossTrajectory(t)
WeakPrefixDominates(s,t)
--------------------------------
Phi(t) <= Phi(s)
```

and the stronger equality

```text
Phi(t) = Phi(s).
```

The graph realizations are explicit premises rather than inferred from degree
arithmetic.  The numerical conclusion follows because weak prefix dominance
contains `length(s) = length(t)` and both potentials equal twice that length.

## Concrete nonvacuity

Lean carries explicit `SimpleGraph (Fin 3)` realizations for

```text
s = [1,1,0]   (one edge plus one isolated vertex)
t = [0,0,0]   (the empty graph).
```

The source weakly prefix-dominates the target despite their unequal degree
sums.  Its canonical step is `[0,0]` with loss two, so both lists have certified
unit-loss trajectories.  The final theorem checks

```text
Phi([1,1,0]) = Phi([0,0,0]) = 6.
```

Thus the class theorem is neither vacuous nor restricted to equal-sum atomic
transfers.

## Exact boundary

This lane gives a genuine positive class but not the general coupling sought
for arbitrary graphical unit transfers.  When an elimination step has loss
greater than two, the closed form acquires additional local excess and the
current argument no longer compares the two histories.  A broader theorem
would need to couple where those excess units occur, not just their total.

The next plausible invariant is therefore a step-indexed excess profile

```text
excess_i = stepLoss_i - 2,
```

together with a realization-aware injection or prefix comparison between the
two profiles.  The v0.8 result warns that comparing only their total would
again be circular.

## Verification

From the pinned `formal-conjectures` checkout:

```bash
timeout 60s lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture61Coupling.lean
```

Result: **PASS** in approximately seven seconds.  The source contains no
`sorry`, `admit`, or custom `axiom`.  Every subprocess was individually capped
at 60 seconds.

## Verdict

The scalar-credit dead end now has its first structurally stronger replacement.
Matching-type realized elimination histories form a complete nontrivial class
on which corrected potential monotonicity holds with equality.  Generalization
requires coupling the distribution of per-step excess losses.
