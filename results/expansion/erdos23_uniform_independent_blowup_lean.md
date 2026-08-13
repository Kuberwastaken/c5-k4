# Erdős 23 uniform independent-blow-up certificate API

Date: **2026-08-13 UTC**

Status: **proved in Lean; no counterexample claim**

## Result

The module `lean/Erdos23UniformIndependentBlowup.lean` formalizes the reusable
exact mechanism behind the independently audited Andrásfai-successor v2 row.
For a uniform independent blow-up with bag size `s`, it proves that exact
maximum-cut and minimum-bipartization certificates transport with multiplier
`s^2`.

The API retains witnesses as data. A concrete graph adapter must provide:

1. a normalization taking every lifted cut assignment to a whole-bag
   quotient assignment whose cut is at least as large;
2. an exact lift multiplying the quotient cut by `s^2`;
3. a normalization taking every lifted bipartization assignment to a
   quotient assignment whose scaled deletion cost is no larger; and
4. an exact lift multiplying the quotient deletion cost by `s^2`.

From those named obligations, `MaxCertificate.uniformScale` and
`MinCertificate.uniformScale` construct exact lifted certificates. The
proposition-level theorems `max_uniformScale_spec` and
`min_uniformScale_spec` expose their witness and global-bound guarantees for
axiom auditing.

This is an honest adapter boundary. Mathlib does not currently supply the
specific independent-blow-up construction, bag partition, whole-bag rounding,
and edge-count formula as one ready-made graph API. The Lean module therefore
does not silently assume those facts or confuse arithmetic scaling with a
graph-level construction theorem. The earlier weighted-`C5` extraction
supplies one instance of the local whole-bag rounding argument; other quotient
families must discharge the same explicit adapter fields.

## Audited `A_14`, bag-five arithmetic

The module records only the independently audited quotient coordinates

```text
edges = 287, maximum cut = 238, bipartization = 49.
```

It then proves that bag size five gives

```text
edges = 7,175, maximum cut = 5,950, bipartization = 1,225,
1,225 + 456 = 41^2 = 1,681.
```

These are certificate inputs and their exact arithmetic consequences. The
file deliberately makes **no** claim that the observed Andrásfai formula
holds for every `A_k`.

## Verification

From the pinned `formal-conjectures` Lake environment:

```text
timeout 60s lake env lean -DwarningAsError=true \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  /Users/kuber.mehta/Projects/c5-k4/lean/Erdos23UniformIndependentBlowup.lean
```

The warning-as-error build completes within the cap. The module contains no
`sorry`, `admit`, `native_decide`, or custom axiom. Its `#print axioms` audit
reports only standard Lean/Mathlib foundations.

No commit, push, release, issue, pull request, or other public action was
performed.
