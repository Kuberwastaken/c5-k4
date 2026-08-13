# WOWII #40 bipartition-star Lean extraction

## Extracted obstruction

The cross-petal trial exposed a reusable reason its balanced bipartite,
Hamiltonian outputs could not cross #40.  For any two nonempty disjoint
independent classes `A,B`, choose a vertex from the smaller class and add it to
the larger class.  The induced graph is a star with possible isolated
vertices, hence a forest of order

```text
max(|A|,|B|) + 1.
```

The Lean module proves this without assuming that the two classes cover the
graph and without assuming connectivity.  It then derives the invariant lower
bound and its balanced specialization.

Finally, under explicit full-bipartition, `b(G)=|V|`, and
`pathCoverNumber(G)=1` hypotheses, it proves the exact real/ceiling expression
used by current Formal Conjectures WOWII #40.  For `|A|=|B|`, the right side is
`|A|+1`, which is already supplied by the induced star.

## Scope and honesty

The arithmetic corollary keeps `b(G)=|V|` and `pathCoverNumber(G)=1` explicit.
This avoids pretending that the repository automatically recovers those
equalities from an arbitrary pair of independent finsets.  The structural
lemma itself is stronger and needs neither equality, covering, nor
connectivity.

This is a theorem extraction from a negative prospective trial, not a proof of
WOWII #40 in general and not a new disproof.  No countermodels are discarded:
the conclusion requires both opposite classes to be nonempty, which is exactly
what permits the extra vertex.

## Verification

The local dependency `GraphConjecture40Baseline.lean` was first compiled into
a fresh temporary module directory.  The new module was then elaborated from
the pinned `formal-conjectures` Lake environment with that directory on
`LEAN_PATH`:

```text
timeout 55s lake env lean -DwarningAsError=true \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture40BipartitionStar.lean
```

The final process exited zero in 6.5 seconds with no output.  The source has no
`sorry`, `admit`, custom `axiom`, or native decision procedure.
Fresh `.olean` compilation followed by `#print axioms` reports only Lean's
standard `propext`, `Classical.choice`, and `Quot.sound` foundations for all
three principal theorems.

No commit, push, release, issue, PR, or other public action was performed.
