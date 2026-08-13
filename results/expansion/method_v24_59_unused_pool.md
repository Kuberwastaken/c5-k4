# Method v24: WOWII #59 unused-pool premise

Date: 2026-08-13

Local certificate: `lean/GraphConjecture59UnusedPool.lean`

## Outcome

The v23 complete-cover route needs a lower bound on a candidate pool before
its degree-sum inequality can produce a useful threshold.  This checkpoint
derives the exact order-budget bound supplied by the established six-core and
four named outside rows.

Define the natural unused pool by

```text
R = V \ (S union {w,x,y,z}).
```

Since `|S|=6` and four names occupy at most four vertices, Lean proves

```text
|V| - 10 <= |R|.
```

No density premise appears in this proof.  Attachment density constrains
edges, not the number of vertices left after the core and named rows have been
chosen.

## Connection to the complete-cover threshold

Combining the unused-pool bound with v23 gives the certified implication

```text
every p in R hits x or y or z
and 10 + 3d < |V|
  ==> deg(x)>d or deg(y)>d or deg(z)>d.
```

Thus the missing premise is now explicit: this branch needs graph order past
`10+3d`, or a stronger candidate pool obtained from additional structure.  It
cannot be recovered from dense attachment rows alone.

## Exact countermodel at the boundary

The module includes a ten-vertex graph with:

- a six-vertex core colored as `3+3`;
- a proper core coloring;
- four distinct outside vertices;
- all four outside rows having three attachments in each core color class;
- the outside four forming a clique; and
- an empty natural unused pool.

Lean verifies all these local core and dense-row properties together by
kernel reduction.  This is a countermodel to any attempted inference that the
already established local density hypotheses alone make the unused pool
nonempty.  It does not disprove WOWII #59 and makes no claim about satisfying
the conjecture's global low-residue corner.

## Consequence for the search

The unused-pool route is productive only when a global invariant supplies the
order slack.  The next useful comparison is therefore between the threshold
`(|V|-10)/3` and the degree sequence entering residue.  If low residue cannot
force enough order slack, the remaining option is a structural forest
exchange exploiting overlap among the covering neighborhoods.

## Lean audit

`CompatibilityExchange`, `CoverDegree`, and the new module were rebuilt into
a fresh local output directory with the repository-pinned Lean 4.27
toolchain.  Each invocation was capped at 60 seconds and promoted warnings to
errors; the complete three-module audit took 18.7 seconds:

```text
ELAN_TOOLCHAIN=leanprover/lean4:v4.27.0
LEAN_PATH=/tmp/c5k4-59-v24-audit
timeout 60s lake env lean \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  -DwarningAsError=true \
  -o /tmp/c5k4-59-v24-audit/GraphConjecture59UnusedPool.olean \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture59UnusedPool.lean
```

Result: exit code 0.  The certificate contains no native computation, proof
holes, or custom axioms.

WOWII #59 is already externally disproved; this is theorem extraction, not a
new counterexample or release candidate.
