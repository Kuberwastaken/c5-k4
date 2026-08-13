# WOWII 19 line-graph endpoint coordinates: Lean extraction

Date: **2026-08-13 UTC**

Status: **WARNING-CLEAN REUSABLE LOCAL LEMMAS**

No commit, push, release, issue, PR, or other public action was taken in this
lane.

## Artifact and statements

`lean/LineGraphEndpointCliques.lean` works with mathlib's source-faithful
`SimpleGraph.lineGraph`, whose vertices are the edges of the original graph.
For an original vertex `u`, it defines `endpointClique G u` to be the
edge-vertices incident with `u` and proves:

- `endpointClique_pairwise_adj`: distinct edge-vertices through `u` are
  adjacent in `L(G)`;
- `neighborSet_subset_endpointCliques`: for an edge `uv`, every neighbor of
  its vertex in `L(G)` belongs to the `u`-endpoint clique or the `v`-endpoint
  clique;
- `independent_inter_endpointClique_subsingleton`: an independent line-graph
  set meets either endpoint clique in at most one vertex;
- `independent_ncard_le_two_of_subset_neighborSet`: every independent subset
  of the neighborhood of the edge-vertex `uv` has cardinality at most two.

The last theorem is the precise local-independence coordinate needed by the
WOWII 19 line-graph analysis.

## Bipartite selected-edge necessity

The extraction also reaches the stronger requested incidence statement.  For
a finite selected edge set `S`, `selectedIncidentEdges G S u` is the subset
incident with `u`.  Lean proves
`selectedIncidentEdges_card_le_two_of_induce_isBipartite`: if the line graph
induced by `S` is bipartite, then at most two selected edges meet every
original vertex.

This is exactly the maximum-degree-at-most-two necessity for the selected-edge
subgraph, expressed without introducing a competing subgraph encoding.

## Honest boundary

No converse or cycle equivalence is claimed.  In particular, maximum degree
at most two alone does not make an induced line subgraph bipartite: an odd
cycle component remains an obstruction.  Formalizing the complete
“disjoint paths and even cycles” characterization would require additional
component/cycle adapters and is outside this extraction.

## Verification

From `/Users/kuber.mehta/Projects/formal-conjectures`:

```bash
timeout 55s lake env lean -DwarningAsError=true \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  /Users/kuber.mehta/Projects/c5-k4/lean/LineGraphEndpointCliques.lean
```

Result: exit `0` in approximately 6.9 seconds.  Axiom output for the coverage,
independent-set bound, and selected-edge necessity contains only standard
`propext`, `Classical.choice`, and `Quot.sound`.  The source contains no
`sorry`, `admit`, `native_decide`, or custom `axiom`.

