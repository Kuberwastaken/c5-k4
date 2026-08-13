# Method v0.8: WOWII 133 exact reduction and cubic closure

Date: 2026-08-13

Local certificate: `lean/GraphConjecture133Specialization.lean`

## Result

This checkpoint closes the original source-shaped WOWII 133 inequality for
two honest classes:

1. every connected graph containing a not-necessarily-induced four-cycle;
2. every connected cubic graph, with or without a four-cycle.

The second class is strictly stronger than the previously certified
**C4-free cubic** specialization.  If a cubic graph contains a four-cycle,
the source characteristic exponent is zero and the conjecture reduces to
the universal bound

```text
radius(G) + 1 <= path(G).
```

If it is C4-free, the result is exactly the corrected cubic theorem already
proved in `GraphConjecture133Cubic.lean`.  The new theorem
`cubicSpecialization` performs this split inside the exact upstream-shaped
formula.

## Triangle-corrected reduction

The representation bridge from v0.7 is now consumed, not merely recorded.
For every finite C4-free graph it gives

```text
l(G) = (2 |E(G)| - 3 t(G)) / |V(G)|,
```

where `t(G)` is the number of 3-cliques.  The theorem
`c4FreeBranch_iff_triangleCorrected` proves an equivalence between the
C4-free branch of WOWII 133 and the single explicit inequality

```text
radius(G)
  + floor((2 |E(G)| - 3 t(G)) / |V(G)|)
  <= path(G).
```

Thus the exact remaining graph inequality for the unrestricted C4-free case
is now isolated: prove the displayed triangle-corrected path wall.  No
neighborhood-independence representation issue remains.

For a triangle-free `d`-regular graph this specializes further to

```text
radius(G) + d <= path(G),
```

as established in the earlier `GraphConjecture133Next.lean`.  The cubic case
is closed; arbitrary regular degree and arbitrary nonregular C4-free graphs
remain open.

## Lean audit

The new file contains no proof holes or custom axiom.  It was checked
against the current `formal-conjectures` environment with local dependency
oleans and warnings promoted to errors:

```text
LEAN_PATH=/tmp/c5k4-133-specialization:/tmp/c5k4-133-v07-check \
  timeout 60s lake env lean \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture133Specialization.lean
```

Result: exit code 0 in 7.5 seconds.

This is a partial theorem for the still-open conjecture, not a claim that
WOWII 133 is settled in full and not a counterexample release candidate.
