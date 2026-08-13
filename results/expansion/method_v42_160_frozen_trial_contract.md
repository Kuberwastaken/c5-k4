# Frozen prospective trial: WOWII 160

Frozen: **2026-08-13 UTC, before candidate evaluation**

## Target

For a finite simple connected graph, current DeepMind `160.lean` asserts

`max local independence + max triangles-at-a-vertex * C4free <= Ls`,

where `C4free=1` iff the graph has no (not necessarily induced) four-cycle.
This trial searches only the active `C4free=1` wall.

## Frozen family grammar

1. **Block graphs:** block-cut paths and stars of 2--6 clique blocks, each
   block order 2--5, blocks meeting only in designated cut vertices.
2. **Friendship/windmill variants:** 2--7 triangles sharing a hub, with at
   most one pendant leaf or pendant triangle attached to each nonhub portal.
3. **Triangle cactus with constrained portals:** trees of 2--6 triangles;
   child triangles share exactly one prescribed portal with the parent, with
   optional pendant paths of length 1--2 at unused portals.
4. **Degree-preserving C4-free surgery:** from the preceding graphs, one move
   among edge subdivision, moving one pendant branch between equal-degree
   portals, or replacing one hub edge by a length-2 handle.

Total order is at most 16. At most 20,000 labeled generated instances and at
most 3,000 connected C4-free exact profiles. No adaptive family expansion is
allowed after results are seen.

## Exact invariants

- C4-free: independently reject any vertex pair with two distinct common
  neighbors (equivalent to existence of a simple 4-cycle).
- `maxT`: maximum number of edges induced by a vertex neighborhood.
- `maxL`: maximum independent-set cardinality in a vertex neighborhood,
  enumerated exactly.
- `Ls`: maximum number of leaves in a spanning tree. Primary evaluator uses
  `Ls = n - gamma_c`, where `gamma_c` is the minimum connected dominating-set
  size (for connected graphs of order at least 2), by exact subset enumeration.
- Crossing rule: `Ls < maxL + maxT`.

## Mandatory gates

1. Confirm the exact current Lean statement, especially non-induced C4 and
   real-valued `Ls` comparison.
2. Exhaust all connected unlabeled Atlas graphs of orders 2--7 and compare
   named controls (`K3`, claw, friendship `F2`, paths, cycles).
3. Any crossing must be independently recomputed:
   - enumerate spanning trees directly (or exact MILP with a 60-second cap)
     to confirm `Ls`;
   - separately recompute neighborhood independence, triangle counts, and
     C4-freeness;
   - record graph6 and explicit edge list.
4. Run repository/source/issue/PR status sanity before any novelty claim.

Every subprocess is capped at 60 seconds. No novelty/release claim, commit,
push, issue, PR, or public action is authorized by this trial.

