# Method v25: WOWII #59 residue coordinate of the cover threshold

Date: 2026-08-13

Local certificate: `lean/GraphConjecture59ResidueThreshold.lean`

## Outcome

The v24 order-slack theorem forces one of three target vertices to have degree
above `d`.  This checkpoint connects that fact to the actual Havel--Hakimi
definition of residue.

For every finite graph, Lean proves

```text
deg(x) > 0  ==>  residue(G) <= |V(G)| - 1.
```

The proof works directly with the descending degree sequence.  A positive
degree forces its head to be positive; the first Havel--Hakimi step removes
one list entry; the remaining recursive residue is bounded by the successor
list length.

Combining this with v24 yields

```text
R covered by N(x) union N(y) union N(z)
and 10 + 3d < |V|
  ==> residue(G) <= |V| - 1.
```

This is the exact unconditional residue gain: one vertex, independent of how
large the forced degree is.

## Why the gain cannot be promoted to residue three

Two concrete fourteen-vertex graphs certify both directions of the
obstruction.

### Sharpness of the one-vertex gain

For the star `K_1,13`, Lean proves the exact descending profile

```text
[13,1,1,1,1,1,1,1,1,1,1,1,1,1]
```

and computes its Havel--Hakimi residue as thirteen.  With a six-set and four
named rows chosen explicitly, its unused pool is covered by the center and
the v24 order premise holds for `d=1`.  Thus the general bound
`residue <= |V|-1` is attained.

### Residue three does not cap the forced degree

Let `H` be the join of `K_11` and an independent three-set.  Lean proves its
descending profile is

```text
[13,13,13,13,13,13,13,13,13,13,13,11,11,11]
```

and computes `residue(H)=3` by kernel-checked Havel--Hakimi reduction.  The
same explicit six-set, unused-pool cover, and `d=1` order premise coexist with
a target of degree thirteen.

Therefore neither implication needed by a degree-only closure exists:

- a high degree does not force low residue; and
- residue three does not impose a useful upper bound on that degree.

These are coordinate countermodels, not models of the complete hypothetical
`(residue,b,f)=(3,6,4)` corner.  In particular, the split graph's selected
six-set is not the established properly colored maximum bipartite core.  The
certificate rules out only the attempted inference from the cover/order/high-
degree data to residue, which is precisely the interface under audit.

## Consequence for the search

The complete-cover branch cannot close through maximum degree alone.  Any
residue contradiction must use more of the descending degree profile, such as
several forced degrees and their multiplicities, together with restrictions
coming from the `3+3` maximum bipartite core and `f=4`.  Otherwise the honest
next route remains a neighborhood-overlap forest exchange.

## Lean audit

`UnusedPool` and the new residue module were rebuilt into a fresh output
directory with the repository-pinned Lean 4.27 toolchain.  Each invocation
was capped at 60 seconds with warnings promoted to errors:

```text
ELAN_TOOLCHAIN=leanprover/lean4:v4.27.0
LEAN_PATH=/tmp/c5k4-59-v25-final.lDLoc5:/tmp/c5k4-59-v24-audit.CuZlTO:/tmp
timeout 60s lake env lean \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  -DwarningAsError=true \
  -o /tmp/c5k4-59-v25-final.lDLoc5/GraphConjecture59ResidueThreshold.olean \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture59ResidueThreshold.lean
```

Result: exit code 0; the two-module audit completed in about 11 seconds.  The
certificate contains no native computation, proof holes, or custom axioms.

WOWII #59 is already externally disproved; this is theorem extraction, not a
new counterexample or release candidate.
