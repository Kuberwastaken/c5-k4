# Method v0.8: WOWII 59 low-residue extraction

Date: 2026-08-13

## Status and scope

This is proof extraction on an already-covered `formal-conjectures` target,
not a held-out discovery trial and not a new disproof claim.

At upstream commit `9a1636c4030039f70cf78b866c216d8b6c5f35b0`,
`FormalConjectures/WrittenOnTheWallII/GraphConjecture59.lean` states that every
finite connected simple graph satisfies

```text
ceil(sqrt(residue(G) * b(G))) <= f(G),
```

where `residue` is the Havel--Hakimi residue, `b` is the largest induced
bipartite order, and `f` is the largest induced forest order.

The general statement is already known to be false. Two open upstream PRs
record independent counterexamples:

- [#4574](https://github.com/google-deepmind/formal-conjectures/pull/4574):
  a 123-vertex witness with `(residue,b,f)=(101,122,111)`;
- [#4583](https://github.com/google-deepmind/formal-conjectures/pull/4583):
  a fully formalized 18-vertex witness with `(residue,b,f)=(10,17,13)`.

No priority or novelty is claimed here. The purpose of this lane is to recover
a clean region in which the conjectured inequality is genuinely a theorem.

## The theorem shadow

The elementary source baseline already formalized during the WOWII 40 lane is

```text
b(G) + 2 <= 2 f(G)
```

for every finite connected nontrivial graph. It comes from taking the larger
colour class of a maximum induced bipartite subgraph and adjoining one omitted
vertex; the resulting induced graph is a forest.

If `residue(G) <= 2`, then

```text
residue(G) * b(G) <= 2 b(G)
                         <= 4 f(G) - 4
                         <= f(G)^2,
```

where the last inequality is `(f(G)-2)^2 >= 0`. Nonnegativity of `f(G)` then
gives

```text
sqrt(residue(G) * b(G)) <= f(G),
```

and the integral right side absorbs the ceiling.

Thus WOWII 59 is true on the complete low-residue slice

```text
residue(G) <= 2.
```

This does not depend on the classical `residue(G) <= alpha(G)` theorem and it
does not invoke the open upstream declaration.

## Formal artifact

[`lean/GraphConjecture59Extraction.lean`](../../lean/GraphConjecture59Extraction.lean)
proves four rungs:

1. the exact generic radicand-square certificate implies the ceiling bound;
2. the WOWII 40 source baseline plus `residue <= 2` proves that certificate;
3. the resulting upstream-shaped WOWII 59 theorem on all connected
   low-residue graphs;
4. an arithmetic countermodel showing that the baseline alone cannot extend
   the same argument to coefficient three (`b=4`, `f=3`, `residue=3`).

The fourth rung is only an abstract numerical obstruction; it does not assert
that this invariant triple is graph-realizable.

## Verification and trust boundary

The dependency `GraphConjecture40Baseline.lean` and this file were compiled in
separate steps, with the former's `.olean` placed on the latter's Lean search
path:

```text
lake env lean -DwarningAsError=true -R /tmp \
  -o /tmp/GraphConjecture40Baseline.olean \
  /tmp/GraphConjecture40Baseline.lean

LEAN_PATH=/tmp lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture59Extraction.lean
```

Both commands completed within the 60-second cap; the final module took under
eight seconds and emitted no warnings or errors. The new file contains no
`sorry`, `admit`, custom axiom, native decision procedure, or imported upstream
conjecture theorem. Its only non-library proof dependency is the already
warning-clean, no-`sorry` WOWII 40 source-baseline module.

## Outcome

`THEOREM_SLICE`, not `DISPROOF` and not `HELD_OUT_SUCCESS`.

The extraction precisely explains a large safe region and puts a necessary
condition on every counterexample: it must have Havel--Hakimi residue at least
three. The known 18-vertex witness has residue ten, so it lies well beyond this
wall.
