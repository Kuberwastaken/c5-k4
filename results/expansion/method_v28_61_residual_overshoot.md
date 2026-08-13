# WOWII 61: residual-gap overshoot is the exact missing bridge

## Outcome

This theorem-extraction pass converts the arbitrary-depth funding condition
from v0.27 into an equivalent statement about the degree sums remaining on the
two Havel--Hakimi trajectories.

New certificate:

```text
lean/GraphConjecture61ResidualOvershoot.lean
```

The exact missing conjecture-specific lemma is now isolated:

> Initial weak degree-prefix dominance of admissible graphical degree lists
> must prevent the signed source-minus-target residual degree-sum gap from
> ever exceeding its initial value.

No successor-prefix dominance is assumed or needed.  A first failure of the
funding invariant would force this residual gap to jump at least two units
above its initial value.

## Exact accounting identity

For source and target lists define

```text
gap_k = sum(HH^k(source)) - sum(HH^k(target))
```

as an integer, so its sign is retained.  Along locally admissible trajectories,
Lean proves

```text
gap_k = gap_0 - 2 * (cum_k(source) - cum_k(target)).
```

The proof combines:

- the previously formalized telescoping identity for remaining degree sum;
- the admissible-step theorem that cumulative loss equals twice the sum of
  eliminated heads;
- a proved definitional bridge between the two earlier modules' local copies
  of the cumulative trajectory functions.

It also proves that `AdmissibleFor k` restricts to `AdmissibleFor j` whenever
`j <= k`, allowing the identity to be used uniformly at every prefix.

## Pointwise equivalence

The accounting identity yields the exact iff

```text
cum_k(target) <= cum_k(source)
  ↔ gap_k <= gap_0.
```

Thus “the cumulative credit has not gone negative” and “the residual signed
gap has not overshot its starting value” are the same assertion, not merely
one-way sufficient conditions.

This matters because residual degree sums are a more natural target for a
graphical majorization argument than the individual heads of two successors.
The false successor-prefix route tried to preserve far more structure than is
actually required.

## First-failure theorem

Suppose depth `k` still has cumulative order, but its next head is not funded
by the bank from v0.27.  Lean proves

```text
gap_0 + 2 <= gap_(k+1).
```

The jump is at least two because every admissible eliminated head accounts for
two degree-sum units.  Therefore a smallest counterexample to the desired
bridge must exhibit a very concrete event: at its first bad depth the source's
signed residual degree-sum advantage becomes strictly larger than its entire
initial advantage.

The exhaustive order-ten search from v0.27 found no such event among 22,083
graphical degree sequences and 105,582,418 qualifying weak-prefix ordered
pairs.  That remains bounded evidence, not a proof.

## Global no-overshoot theorem

The formal predicate

```text
ResidualGapDoesNotOvershootThrough k source target
```

requires `gap_j <= gap_0` for every `j <= k`.  Under admissibility, Lean proves
both consequences needed by the preceding development:

```text
forall j <= k, cum_j(target) <= cum_j(source)
```

and

```text
HeadReversalsFundedThrough k source target.
```

The latter feeds directly into `GraphConjecture61FundedTrajectory.lean`.

## Smallest exact missing lemma

The certificate names the remaining list-side proposition

```text
DegreePrefixNoResidualOvershootBridge
```

which states that for every depth `k`, initial `DegreePrefixDominates` plus
admissibility of both trajectories implies no residual-gap overshoot through
`k`.

For descending graphical degree sequences the admissibility premises encode
the canonical positivity/counting behavior of Havel--Hakimi.  Consequently,
this proposition is the precise formal bridge still to be derived from
graphical weak majorization.  It contains no invented preservation property:
the order-four successor-prefix counterexample and order-five two-unit reversal
are both compatible with it.

## Verification

After compiling the local import chain one file at a time under the process
cap, the fresh check was:

```text
timeout 60s env LEAN_PATH=/Users/kuber.mehta/Projects/c5-k4/lean \
  lake env lean -R /Users/kuber.mehta/Projects/c5-k4/lean \
  -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture61ResidualOvershoot.lean
```

It exited `0` in 5.70 seconds with no output.  The source contains no `sorry`,
`admit`, `native_decide`, or custom axiom.

## Next proof rung

The next useful theorem should attack residual sums directly.  One possible
minimal form is a one-step barrier:

```text
initial degree-prefix dominance
current gap <= initial gap
graphical/admissible current states
------------------------------------------------
next gap <= initial gap.
```

Unlike successor-prefix dominance, this asks only that the scalar gap not
cross its original ceiling.  If this barrier is false, the first countermodel
must satisfy the formally proved `gap_(k+1) >= gap_0 + 2` certificate, giving a
sharp target for exact search and subsequent Lean certification.
