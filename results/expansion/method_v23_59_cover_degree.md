# Method v23: WOWII #59 complete-cover degree pressure

Date: 2026-08-13

Local certificate: `lean/GraphConjecture59CoverDegree.lean`

## Outcome

The v22 compatibility exchange has two exact failure modes: a candidate pool
is completely covered either by three outside-side neighborhoods or by two
core-side neighborhoods.  This checkpoint formalizes the strongest immediate
degree consequences of those covers.

If every vertex of `P` is adjacent to at least one of `x,y,z`, then

```text
|P| <= deg(x) + deg(y) + deg(z).
```

If every vertex of `Q` is adjacent to at least one of `a,b`, then

```text
|Q| <= deg(a) + deg(b).
```

These bounds are deliberately stated without disjoint-neighborhood
assumptions.  Overlap only makes the union smaller, so ordinary union-cardinal
bounds suffice.

## Exact link to the v22 obstruction

Theorems `degree_sum_of_outside_selection_failure` and
`degree_sum_of_core_selection_failure` consume the blocker-filter equalities
from v22 directly.  Thus the compatibility branch now has a certified
dichotomy:

1. a candidate survives each blocker cover, producing the seven-vertex
   bipartite witness from v21; or
2. failure forces the corresponding degree-sum inequality above.

There is no informal change of obstruction between the two modules.

## Pigeonhole thresholds

The module also proves the quantitative residue interface:

```text
3d < |P|  ==>  max(deg(x),deg(y),deg(z)) > d,
2d < |Q|  ==>  max(deg(a),deg(b)) > d.
```

These are useful when a future branch supplies a lower bound on the candidate
pool and an upper threshold on the relevant core degrees.  The two-cover
branch is sharper and should be tested first against any available
degree-sequence or deletion-residue estimate.

## What this does not prove

A complete cover alone does not imply the residue inequality sought in #59.
The present dense-row hypotheses do not yet give a pool-cardinality lower
bound strong enough to force a specific degree threshold.  Claiming a residue
exit at this point would therefore add an unstated assumption.

The next honest step is one of:

- derive a certified lower bound on `|P|` or `|Q|` from the existing row/core
  hypotheses and compare it with the degree-sequence budget; or
- use overlap in the covering neighborhoods to build an explicit acyclic
  exchange, which can improve the crude union bound.

## Lean audit

The dependency chain through v20--v22 and the new module were rebuilt using
the repository-pinned Lean 4.27 toolchain.  The final check was:

```text
ELAN_TOOLCHAIN=leanprover/lean4:v4.27.0 \
LEAN_PATH=/tmp/c5k4-59-cover-audit \
timeout 60s lake env lean \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  -DwarningAsError=true \
  -o /tmp/GraphConjecture59CoverDegree.olean \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture59CoverDegree.lean
```

Result: exit code 0 in 6.4 seconds.  The certificate contains no native
computation, proof holes, or custom axioms.

WOWII #59 is already externally disproved; this is theorem extraction, not a
new counterexample or release candidate.
