# Erdős 628 Mycielski-edge Phase 1 addendum

Frozen: **2026-08-13 UTC, before evaluation**

This addendum authorizes exactly one graph: the Phase 0 equality seed after
deleting the embedded original-`C5` edge `{1,2}` inside `H5=M(M(C5))`.
Labels, the omitted seed cross edge `xu`, and every other adjacency remain
unchanged. No alternate edge, orbit representative, or adaptive move is
authorized.

The premise gate uses two independent exact oracle stacks:

1. deterministic DSATUR branch-and-bound for chromatic number and
   Bron--Kerbosch for maximum clique;
2. binary MILP coloring feasibility and a separate maximum-clique MILP.

Every certificate is replayed directly. Each process is capped at 60 seconds.
If the oracles do not both certify `chi=6` and clique number below six, the
trial stops with zero Tihany partition evaluations. Only premise survival
authorizes exhaustive evaluation of the exact `(a,b,k)=(2,5,6)` conclusion.

No commit, push, release, issue, pull request, or public action is authorized.
