# Method v0.16: WOWII 141 radius-two BFS obstruction

Date: 2026-08-13
Status: verified BFS-layer reduction; the final radius-two acyclicity lemma
remains

## Direct contradiction target

Instead of formalizing a full breadth-first tree and the general inequality
`girth <= 2*radius+1`, this pass targets only the consequence needed for
WOWII 141:

```text
connected and girth >= 8
  -> every vertex has another vertex at distance at least 3.
```

Negating the conclusion gives a radius-two center: a vertex `v` from which
every vertex lies at distance at most two.

## Verified layer extraction

[`lean/GraphConjecture141BfsGirthBound.lean`](../../lean/GraphConjecture141BfsGirthBound.lean)
proves:

- failure of the all-vertex distance-three property is equivalent to the
  existence of a radius-two center;
- in a connected graph, every vertex relative to such a center is exactly
  the root, a first-layer neighbor, or a distance-two vertex;
- at girth at least six the second layer is nonempty, since a universal
  center would make the graph an acyclic star; and
- every distance-two vertex has a first-layer parent, extracted from a
  shortest path of length two.

These statements use the repository's actual graph distance and shortest-
path APIs.  No BFS parent map or radius theorem is assumed.

## Exact remaining lemma

The residual is packaged as `NoCyclicRadiusTwoLayer G`:

```text
every radius-two center forces G to be acyclic.
```

Under girth at least eight, the intended layer proof is:

1. the first layer is independent, or there is a triangle;
2. every second-layer vertex has a unique first-layer parent, or there is a
   4-cycle;
3. the second layer is independent, or two parent paths and its internal
   edge create a cycle of length at most five; and
4. these properties make the graph a forest of rooted depth-two branches.

The first two ingredients already exist in earlier #141 files.  The third
and the final global acyclicity assembly require a cycle argument that treats
the exceptional root separately.  This pass exposes that exact statement
rather than hiding it in a radius hypothesis.

Lean proves that `NoCyclicRadiusTwoLayer G` plus `girth >= 8` yields
`EveryVertexHasDistanceAtLeastThree G`, completing the logical BFS reduction.

## Verification

From the `formal-conjectures` checkout:

```bash
timeout 60s lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture141BfsGirthBound.lean
```

Result: exit 0 in 9.5 seconds.  The file contains no proof placeholders,
native evaluation shortcuts, or custom axioms.
