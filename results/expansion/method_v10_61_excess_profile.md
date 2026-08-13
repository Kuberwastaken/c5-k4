# Method v0.10: WOWII 61 excess-loss profiles

Date: **2026-08-13 UTC**

Outcome: **the unit-loss class now extends to arbitrary certified
Havel--Hakimi trajectories with step-indexed excess profiles.**  Lean proves
the exact closed form

```text
Phi(s) = 2 * length(s) + sum(excessProfile(s))
```

and proves corrected-potential monotonicity whenever realized source and target
trajectories have the same graph order and the source profile prefix-dominates
the target profile.

The explicit `P3` to `K2 + K1` example has source step loss four, so this
strictly extends the v0.9 unit-loss class.

This lane does not prove WOWII 61 or unrestricted graphical weak-potential
monotonicity.

## Frozen scope

- New certificate only: `lean/GraphConjecture61ExcessProfile.lean`.
- New report only:
  `results/expansion/method_v10_61_excess_profile.md`.
- No existing file was edited.  No commit, push, release, issue, PR, or other
  external mutation was made.

## Step-indexed profile

For each positive canonical elimination step, define

```text
excess = stepLoss - 2.
```

The inductive proposition

```text
ExcessTrajectory sequence profile
```

records these excesses in chronological order.  Its active-step constructor
requires all of the following explicitly:

1. the current list has a nonzero head;
2. the next state is exactly `havelHakimiStep current`;
3. the current loss is at least two, so subtraction is exact;
4. the tail profile certifies the complete successor trajectory.

Its terminal constructor permits only a list consisting entirely of zeros.
`RealizedExcessTrajectory` additionally carries an explicit finite simple
graph whose complete descending degree list is the initial sequence.

## Exact closed form

At a zero terminal of length `z`, the potential is `2z`.  At an active step,

```text
Phi(current) = Phi(successor) + stepLoss
             = Phi(successor) + 2 + excess.
```

The successor has one fewer list entry.  Structural induction therefore gives

```text
ExcessTrajectory s p -> Phi(s) = 2 * length(s) + sum(p).
```

This theorem generalizes v0.9, where every profile entry was zero.

## Prefix coupling

`PrefixExcessDominates source target` requires

```text
length(target) <= length(source)
```

and, for every prefix through the target trajectory,

```text
sum(target.take k) <= sum(source.take k).
```

The source may continue for additional active steps.  Lean proves that this
chronological prefix relation implies total profile-sum order.  The proof does
not replace the relation with an unchecked scalar assumption: it derives the
total comparison at the full target prefix and bounds that source prefix by
the full source sum.

Combining the profile closed form, profile total order, and the common graph
order supplied by `WeakPrefixDominates` yields

```text
RealizedExcessTrajectory s sourceProfile
RealizedExcessTrajectory t targetProfile
WeakPrefixDominates s t
PrefixExcessDominates sourceProfile targetProfile
--------------------------------------------------
Phi(t) <= Phi(s).
```

This is a genuinely stronger coupled state than the circular accumulated-loss
budget: it compares every chronological prefix of local excess, not merely the
final total.

## Strict extension example

The source is the three-vertex path:

```text
s = [2,1,1].
```

Lean carries the explicit `pathGraph 3` realization.  Its first canonical step
has loss four and reaches `[0,0]`, giving excess profile

```text
[4 - 2] = [2].
```

The target is one edge plus one isolated vertex:

```text
t = [1,1,0].
```

It has an explicit `SimpleGraph (Fin 3)` realization, first-step loss two, and
profile `[0]`.  Lean certifies

```text
WeakPrefixDominates [2,1,1] [1,1,0]
PrefixExcessDominates [2] [0]
Phi([1,1,0]) = 6 <= 8 = Phi([2,1,1]).
```

Since the source has a non-unit loss, it is outside the v0.9 class.

## Exact remaining boundary

The new theorem reduces the general graphical candidate to a concrete
realization-aware question:

```text
Does graphical weak prefix dominance induce a chronological prefix coupling
of the two canonical excess-loss profiles, perhaps after an admissible
coupled choice of maximum-degree vertices?
```

That implication is not asserted.  It can fail for raw canonical histories if
local excess is shifted between time steps even when final residue order is
correct.  The next lane should test this prefix implication exactly on
realized degree-sequence pairs and either formalize its first obstruction or
prove it on a broader graph class.

## Verification

From the pinned `formal-conjectures` checkout:

```bash
timeout 60s lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture61ExcessProfile.lean
```

Result: **PASS** in approximately seven seconds.  The source contains no
`sorry`, `admit`, or custom `axiom`.  Every subprocess was individually capped
at 60 seconds.

## Verdict

The v0.9 equality class has become an exact profile calculus.  Local
above-baseline losses now form a chronological invariant whose prefix order
is sufficient for corrected-potential monotonicity, and `P3` supplies the first
fully realized non-unit-loss instance.  The unresolved issue is whether graph
realizations and weak degree dominance force such a profile coupling.
