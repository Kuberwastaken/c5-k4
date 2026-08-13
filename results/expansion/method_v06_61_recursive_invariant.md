# Method v0.6: WOWII 61 recursive potential

Date: **2026-08-13 UTC**

Outcome: **a sum-corrected recursive invariant is formalized and closes the
specific unequal-sum obstruction from the first graphical transfer.**  Its
unrestricted form has a smallest nongraphical counterexample, while the
realization-aware candidate survived the bounded exact tests performed here.
The general graphical monotonicity theorem is named but not asserted.

This remains a partial theorem-development result, not a proof of WOWII 61 or
the Griggs--Kleitman residue bound.

## Frozen scope

- New certificate only:
  `lean/GraphConjecture61RecursiveInvariant.lean`.
- Parent graphical-transfer result: commit `6490c66`.
- No committed file was edited.
- No Maxine induction, graph deletion theorem, upstream mutation, release,
  commit, or push was attempted.

## Candidate relation

`WeakPrefixDominates s t` requires:

1. both lists are descending;
2. they have equal length; and
3. every prefix sum of `s` is at least the matching prefix sum of `t`.

Unlike ordinary majorization, the total sums may differ.  This is essential:
the committed first transfer has successors `[0,0,0]` and `[1,1,0]`, whose
sums are zero and two.

The new corrected potential is

```text
Phi(s) = 2 * residueAux(s) + sum(s).
```

For a graphical degree list, `sum(s)` is twice the edge count, so `Phi` is
twice `residueAux + edgeCount`.  The candidate general proposition is named

```text
GraphicalWeakPotentialMonotone :=
  forall graphical s,t,
    WeakPrefixDominates s t -> Phi(t) <= Phi(s).
```

It is a definition of a proposition only.  No theorem or axiom claims it.

## Exact recursive rung

The certificate proves for every natural-number list:

```text
sum(havelHakimiStep s) <= sum(s).
```

It defines the exact loss

```text
stepLoss(s) = sum(s) - sum(havelHakimiStep s)
```

and proves, whenever the head `d` is positive,

```text
Phi(d :: rest)
  = Phi(havelHakimiStep (d :: rest)) + stepLoss(d :: rest).
```

This is `residuePotential_cons_eq_step_add_loss`.  It is a general symbolic
identity, not finite computation.  The proof uses the upstream recursion
equation for `residueAux` and a new proof that sorting, decrementing, and
dropping the head cannot increase the degree sum.

This is the precise correction absent from equal-sum majorization: recursive
states may have different sums, but their potential difference accounts for
that loss exactly.

## Committed example closes under the correction

Before recursion,

```text
[2,1,1,0] weakly prefix-dominates [1,1,1,1]
Phi([2,1,1,0]) = 10
Phi([1,1,1,1]) = 8.
```

After one Havel--Hakimi step, the dominance direction reverses:

```text
[1,1,0] weakly prefix-dominates [0,0,0]
Phi([1,1,0]) = Phi([0,0,0]) = 6.
```

Thus weak dominance permits the unequal sums, while the corrected potential
turns the previous obstruction into exact equality.  Lean certifies all of
these values and relations in:

- `first_transfer_weakPotential`;
- `first_transfer_successor_weakPotential`; and
- `first_transfer_recursive_accounting`.

The last theorem also checks the head-loss accounting directly:

```text
10 = 6 + 2*2
 8 = 6 + 2*1.
```

## Smallest unrestricted failure

The proposed potential theorem is false without graphical realizability:

```text
[1] weakly prefix-dominates [0]
Phi([1]) = 1
Phi([0]) = 2.
```

This is minimal by positive list length; the only empty list pair is equality.
Lean certifies the failure in `unrestricted_weakPotential_counterexample`.

The source `[1]` is not graphical, since a sole vertex cannot have degree one.
That exclusion is also proved from an explicit graph-realization predicate in
`not_graphical_singleton_one`.  Every graphical singleton is `[0]`, and the
candidate monotonicity theorem is formally proved at order one in
`graphicalWeakPotentialMonotone_singletons`.

## Bounded exact tests

All diagnostics used exact integer Havel--Hakimi evaluation and independently
checked graphicality.

### All graphical weak-dominance pairs

Every descending graphical degree sequence through order nine was enumerated.
No corrected-potential failure was found.  At order nine alone, 4,361
graphical sequences produced 7,477,797 weak-dominance pairs satisfying the
candidate inequality.

The unrestricted enumeration immediately found the singleton failure above,
which was then formalized rather than discarded.

### Atomic-transfer successors

For every graphical atomic transfer through order ten, the two
Havel--Hakimi successors were tested.  Across 526,772 transfers:

1. the successor lists were always comparable in at least one weak-prefix
   direction; and
2. the corrected potential was monotone in every applicable dominance
   direction.

No failure was found.

### Random larger-order diagnostic

A deterministic-seed scan completed graph orders four through 21:

- sampled graphs: 36,000;
- checked graphical atomic transfers: 570,544;
- incomparable successor pairs: 0;
- corrected-potential failures: 0.

The process reached its 60-second cap during the order-22 tranche.  That
incomplete tranche was discarded.  These diagnostics are evidence, not proof.

## Exact remaining lemma

The formal boundary is now:

```text
IsGraphical s
IsGraphical t
WeakPrefixDominates s t
--------------------------------
Phi(t) <= Phi(s).
```

A proof must exploit explicit realizability; the singleton counterexample
shows that descending numeric lists alone are insufficient.  Likely proof
routes are:

1. show that weak dominance between realized lists decomposes into
   realization-preserving edge additions and balancing transfers while
   controlling `Phi`; or
2. prove a direct Havel--Hakimi simulation theorem for the corrected
   potential, allowing dominance orientation to change between recursive
   states.

The second route now has the exact generic accounting identity it needs.  No
further general theorem was pursued in this bounded lane.

## Verification

From the pinned `formal-conjectures` checkout:

```bash
timeout 60s lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture61RecursiveInvariant.lean
```

Result: **PASS** in approximately seven seconds.  The source contains no
`sorry`, `admit`, or custom `axiom`.  Every compile and search subprocess was
individually bounded by 60 seconds.

## Verdict

The unequal-sum successor problem is no longer merely an obstruction: it has
a concrete corrected potential and a machine-checked recursion identity.  The
candidate fails immediately outside graphical sequences but survives all
realization-aware exact and sampled tests run here.  The next honest target is
the named graphical weak-potential monotonicity lemma, not another change of
numeric relation.
