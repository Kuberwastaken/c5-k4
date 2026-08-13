# Method v25: WOWII #59 complete path-obstruction split

Date: 2026-08-13

Local certificate: `lean/GraphConjecture59PathObstructionSplit.lean`

## Alternate-core result

The v24 forest construction is now tried twice: first with aligned core `a`,
then with aligned core `b`. The path center and the unused core are deleted in
each attempt.

If either exchange compatibility condition holds, the existing five-vertex
builder proves

```text
f(G) >= 5.
```

The distinctness and v21 compatibility packages are formally transported
through the core swap.

## Complete failure normal form

Lean proves that both aligned-core attempts fail simultaneously if and only
if one of two obstruction families occurs:

```text
1. q has a neighbor in the outside triple; or
2. p~q, p~a, and p~b.
```

The second case is the complete core-extension fan. It explains why merely
changing the retained aligned core may fail: `p` is then a double neighbor for
both possible incidence cuts.

Consequently the formal path split is

```text
f(G) >= 5
or q hits the outside triple
or the complete core-extension fan occurs.
```

This is an exact propositional partition of the two v24 exchange failures,
not a claim that either obstruction prevents every possible forest witness.

## Closed subcase

If `q` avoids all three outside vertices and the complete fan is absent, one
of the two aligned-core exchanges must succeed. The path branch then yields
`f(G)>=5` without any further assumptions.

## Scope and next step

WOWII #59 is already externally disproved. This is theorem extraction, not a
new counterexample.

The complete dependency chain from `GraphConjecture40Baseline` through the
v24 path branch and this module was rebuilt in a fresh temporary directory,
with warnings promoted to errors and every process capped at 60 seconds. The
separate v19 synchronization branch was rebuilt as well. Every module passed.
The final target check completed in 7.54 seconds with exit code zero and no
warnings. The file contains no proof holes, native computation, or custom
axioms.

The remaining path work is sharply localized:

1. when `q` hits the outside triple, align the chosen path endpoints so that
   at most one is hit, or use the hit vertex in a different exchange;
2. in the complete fan, exploit the forced edges from `p` to both cores and
   `q` rather than treating them only as obstructions.
