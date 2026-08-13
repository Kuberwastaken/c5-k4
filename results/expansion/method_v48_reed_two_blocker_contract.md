# Frozen prospective trial: adjacent two-blocker on C5[K3]

Frozen: **2026-08-13 UTC, before transformed exact invariant evaluation**

## Carrier reuse obstruction

Every optimal eight-coloring of `C5[K3]` consists of seven independent pairs
and one singleton, since the graph has 15 vertices and independence number 2.
Exact enumeration gives **9,720** labeled color partitions. Every carrier
vertex is the singleton in exactly **648** partitions.

This identifies the failure of the v47 one-vertex blocker: any omitted vertex
can be the singleton of an optimal coloring, so a neighborhood smaller than
the whole carrier cannot force a new color by itself.

## Deterministic selection rule

For two new adjacent vertices `x,y`, a carrier color class is reusable at a
new vertex exactly when it is disjoint from that vertex's neighborhood. An
eight-color extension exists precisely when `x` and `y` have two distinct
reusable carrier colors.

Before constructing or evaluating a transformed graph, a deterministic CNF
set-cover encoded all 9,720 carrier partitions and forbade such a pair of
distinct reusable colors. Candidate variables were the 30 carrier incidences
to `x,y`, in vertex order. Structural clauses bounded the new maximum degree
and cliques; Glucose4 used its first model under this fixed encoding.

The stricter budget `Delta<=9, omega<=6` was UNSAT. The budget
`Delta<=10, omega<=6` was also UNSAT. The first permitted total coordinate
growth at most three, `Delta<=10, omega<=7`, was SAT and returned the frozen
neighborhoods below.

## Frozen operation

Starting with bags `Bi={(i,0),(i,1),(i,2)}` of `C5[K3]`, add exactly two new
vertices `x,y`, add edge `xy`, and set

- `N(x) minus {y} = B0 union B1 union B4`;
- `N(y) minus {x} = B2 union B3 union B4`.

No other change, rotation, alternative SAT model, second neighborhood, or
adaptive variant is permitted.

The preregistered structural coordinates are `Delta=10` and `omega=7`:
vertices in `B4` gain two neighbors, each new vertex has degree ten, and the
largest new cliques have one blocker plus two adjacent carrier bags. The
carrier reuse CNF predicts that eight colors are impossible. Two fresh colors
give the unconditional range `9 <= chi <= 10`.

## Safety protocol

1. Re-run the exact 995-graph connected Atlas gate before transformed
   evaluation.
2. Verify the exact reuse catalogue and both UNSAT budgets from scratch.
3. Audit current source/status and theorem classes, including an explicit
   induced claw. A known-domain match is reported prominently; it cannot be
   treated as novelty.
4. Evaluate only this frozen graph with exact DSATUR coloring, exact clique
   search, and direct degree calculation.
5. Independently recompute `chi`, `omega`, and `Delta` with separate routines.

Reed's conjecture is a major human open conjecture. Any apparent numerical
failure is only an adversarial candidate requiring theorem-conflict resolution
and independent expert audit. No commit, push, release, issue, PR, or other
public action is authorized. Every subprocess has a hard 60-second cap.
