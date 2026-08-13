# Frozen prospective addendum: line graphs of the #40 checkpoint wall

Frozen: 2026-08-13 UTC, before evaluating any transformed graph.

## Input checkpoint

This trial uses exactly the ten equality rows in the current frozen #40
block-surgery checkpoint, before its later one-off mutation expansion. No
post-checkpoint equality row may be substituted after results are observed.

Write

```text
tau_F = n - largest_induced_forest,
tau_B = n - largest_induced_bipartite_order,
L     = n - path_cover_number.
```

The conjecture is equivalent to

```text
L + tau_B >= 2*tau_F + 1.
```

The explicit obstruction learned from the ten equality rows is that their
residual

```text
R = L + tau_B - 2*tau_F
```

is only `1` or `2`; the ceiling accounts for the two adjacent parity walls.
Thus a crossing requires a transformation that raises feedback-vertex burden
without granting a matching increase in linear-forest capacity or odd-cycle
transversal safety.

## Frozen separating transformation

For each checkpoint equality seed `G`, construct the line graph `L(G)`. A
vertex of `L(G)` represents an edge of `G`, with adjacency for incident edges.
This globally turns every high-degree incidence star into a clique. The
prospective prediction is that these overlapping incidence cliques can raise
`tau_F` faster than the compensating coordinates `L` and `tau_B`.

Line graphs are not block substitutions, ear surgeries, complete-bipartite
block trees, one/two-edge mutations, or any other family in the frozen #40
checkpoint contract. No other transformation may be added to this trial.

## Frozen gate and budget

1. Before evaluating a line graph, repeat exact sanity on every connected
   Graph Atlas graph of orders three through seven plus paths, cycles, and
   complete graphs of orders three through nine, Petersen, and complete
   bipartite graphs with side sizes two through six.
2. Decode the ten checkpoint graph6 witnesses exactly.
3. Construct `L(G)`, retain connected outputs of orders 3 through 18, and
   canonically deduplicate isomorphic outputs.
4. Evaluate every retained output, at most ten graphs.
5. Every process and exact solve is capped at 60 seconds. A timeout is
   `INCONCLUSIVE`, never a crossing.

Every result must include exact maximum induced-forest, maximum induced-
bipartite, and minimum path-cover witnesses. A strict crossing triggers an
independent recomputation plus current source/status/novelty audit.

Outcomes are `DB_SANITY_REJECT`, `CANDIDATE`, `HOLD_BOUNDED`, or
`INCONCLUSIVE`. No commit, push, release, issue, PR, or other public action is
authorized.
