# Method v0.21 proof extraction: metric intersection and tree closure

Date: **2026-08-13 UTC**

Status: **classical diameter--maximum-degree inequality and WOWII 13 for trees proved unconditionally in warning-clean no-`sorry` Lean**

[`lean/GraphConjecture19MetricIntersection.lean`](../../lean/GraphConjecture19MetricIntersection.lean)
closes the sole remaining v0.20 hinge.

The proof avoids explicit shortcut-walk surgery.  It maps the vertices in
`path.support intersect N(c)` back to their unique path indices and uses exact
shortest-path distances:

- for an arbitrary vertex `c`, any two neighbor indices have distance at most
  two, through the two-edge walk via `c`;
- a finite set of natural indices with pairwise distance at most two has at
  most three elements;
- if `c` itself is on the path at index `k`, every neighbor index has natural
  distance exactly one from `k`, so there are at most two.

The file proves all representation bridges:

- the finite set of neighbor indices;
- equality between its image and
  `path.support.toFinset intersect neighborFinset c`;
- cardinality preservation from path injectivity;
- the two elementary natural-index counting lemmas.

It then proves `DiametralNeighborhoodIntersectionBound G` for every finite
graph.  Combining with v0.20 yields the unconditional classical theorem

```lean
theorem diameter_add_maxDegree_le_card_add_one
    (hconn : G.Connected) :
    G.diam + G.maxDegree <= Fintype.card V + 1
```

under the necessary nonempty finite vertex type and decidable adjacency
instances.  Mathlib's diameter conventions are handled directly:
`exists_dist_eq_diam` selects endpoints even in degenerate diameter-zero
cases, and connectedness supplies a shortest path; the index proof remains
valid for empty or singleton neighbor-index sets.

Finally the theorem is inserted into v0.19 to obtain an unconditional
no-`sorry` WOWII 13 statement for finite connected acyclic graphs:

```lean
theorem wowii13_tree (hconn : G.Connected) (hacyc : G.IsAcyclic) :
  diameter + localMax - 1 <= b G
```

This closes the tree-charge lane completely.  It does not by itself prove
WOWII 13 for arbitrary connected graphs, because v0.19 uses acyclicity to
identify the whole graph as an induced bipartite witness.

## Trust

Compiled against the current `formal-conjectures` environment with
`-DwarningAsError=true`, exit 0.  Every subprocess remained below 60 seconds.
No `sorry`, `admit`, `native_decide`, custom axiom, commit, push, or public
action was used.
