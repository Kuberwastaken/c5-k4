# WOWII 40 v0.10: explicit path-cover witnesses

**Date:** 2026-08-13

**Outcome:** the elementary `sInf` API gap from v0.9 is closed with explicit
path covers; the deficiency equivalence and the connected acyclic base no
longer require numerical path-cover assumptions.

**Read-only upstream snapshot:** `formal-conjectures`
`9a1636c4030039f70cf78b866c216d8b6c5f35b0`

## What is formalized

The new Lean file works directly with the repository definition

```text
IsPathCover G P :=
  pairwise disjointness
  and coverage of univ
  and realization of every member as a path support

pathCoverNumber G := sInf {P.card | IsPathCover G P}.
```

It constructs two witnesses.

### Universal singleton cover

```text
{{v} | v in V(G)}
```

Every member is the support of a nil walk. The file proves disjointness,
coverage, realization, exact cardinality `n`, and the generic comparison

```text
IsPathCover G P -> pathCoverNumber G <= P.card.
```

Consequently:

```text
pathCoverNumber G <= n
```

for every finite graph.

### One-edge-plus-singletons cover

Given an edge `uv`, the second witness is

```text
{{u,v}} union {{x} | x != u and x != v}.
```

The two-vertex member is realized by `huv.toWalk`; all remaining members are
nil walks. The file proves that this is a path cover of exact cardinality
`n-1`. Hence:

```text
G.Adj u v -> pathCoverNumber G < n.
```

A connected nontrivial graph contains such an edge, giving the exact strict
bound needed by the zero-feedback base.

## Consequences for the deficiency development

The v0.9 equivalence

```text
p + B + 1 <= 2f  <->  2*tau + 1 <= ell + o
```

had an explicit `p <= n` premise solely because no path-cover comparison API
existed. The new theorem `integer_bound_iff_deficiency_bound` discharges that
premise for every finite graph.

Likewise, the v0.9 acyclic endpoint assumed `p < n`. The new endpoint

```text
conjecture40_of_isAcyclic
```

requires only the actual upstream structural hypotheses—connectedness,
nontriviality, and acyclicity—and proves WOWII 40 in the exact real/ceiling
shape. In deficiency language, the complete base case is now formal:

```text
connected nontrivial and tau=0
  -> o=0 and ell>=1
  -> ell+o >= 2*tau+1.
```

## Verification

New file:

```text
lean/GraphConjecture40PathCoverAPI.lean
```

After compiling its two local imported modules, the independent check was:

```text
timeout 60s env LEAN_PATH=/Users/kuber.mehta/Projects/c5-k4/lean \
  lake env lean -R /Users/kuber.mehta/Projects/c5-k4/lean \
  -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture40PathCoverAPI.lean
```

It exited `0` in 6.90 seconds with no output. The source contains no
`sorry`, `admit`, or custom axiom.

## Remaining boundary

The elementary optimization API is no longer the blocker. The unresolved
content begins at positive feedback deletion:

1. prove the connected bipartite base `ell >= 2*tau + 1`; or
2. prove a slack-aware transfer from a maximum bipartite core.

The `EQKo` graph still refutes the pointwise insertion shortcut recorded in
v0.9, but it does not affect either explicit path-cover construction here.
This lane makes no counterexample or full-conjecture claim.

Classification: **FORMAL API CLOSURE AND COMPLETE ZERO-DEFICIENCY BASE; no
release or external claim.**
