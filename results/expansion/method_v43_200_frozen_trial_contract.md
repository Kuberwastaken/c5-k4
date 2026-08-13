# Frozen prospective trial: WOWII 200

Frozen: **2026-08-13 UTC, before any development-family evaluation**

## Exact current reading

The current DeepMind declaration in
`FormalConjectures/WrittenOnTheWallII/GraphConjecture200.lean` quantifies over a
finite nontrivial vertex type and assumes:

1. `G` is a simple connected graph;
2. `(largestInducedTreeSize G : ℝ) = ⌈1 + averageIndepNeighbors G⌉`.

Here `largestInducedTreeSize` is the maximum number of vertices in an induced
tree and `averageIndepNeighbors` is the arithmetic mean, over all vertices, of
the independence number of the open neighborhood. The ceiling is Lean's
integer ceiling coerced for the real-valued equality. The conclusion is the
existence of a Hamiltonian walk/path visiting every vertex exactly once.

A crossing is therefore a connected, nontraceable graph satisfying that exact
equality.

## Mandatory pre-evaluation database/status gate

Before evaluating any development-family graph:

- audit the local WOWII transcription/status data;
- inspect the live upstream module, issue, and PR state;
- inspect the source registry status where available;
- if a counterexample/proof proposal for #200 already exists, stop immediately
  as `PRIOR_ART_STOP`, recording no development-family evaluation rows.

This gate is intentionally first. Atlas and family computation are prohibited
if prior art is confirmed.

## Frozen family grammar (only if the gate clears)

1. **Nontraceable block graphs:** block-cut trees with 2--7 clique blocks of
   orders 2--5, emphasizing three or more branches at articulation vertices.
2. **Articulation sums:** one-vertex sums of paths, cliques, cycles, and
   traceable cores, total order at most 16.
3. **Clique/path blow-ups:** paths of 3--7 bags, bag orders 1--4, with complete
   joins only between consecutive bags; retain only connected nontraceable
   members.
4. **Near-traceable surgeries:** one edge deletion/addition, pendant-path move,
   vertex split, or clique-ear attachment from a traceable member of the first
   three families, chosen without adapting the grammar after results are seen.

At most 20,000 generated labeled instances, 3,000 exact connected
nontraceable profiles, order at most 16. Stop at the first independently
verified equality crossing or when the caps are exhausted.

## Exact evaluation (only if the gate clears)

- `averageIndepNeighbors`: exact rational sum of exact neighborhood independence
  numbers, using exhaustive subsets/branch-and-bound and retaining witnesses.
- `largestInducedTreeSize`: descending exact subset enumeration, retaining an
  induced-tree vertex witness and certifying all larger subsets fail.
- nontraceability: exact Hamiltonian-path subset DP; retain the full terminal
  DP obstruction table/hash, with an independent endpoint/path search for any
  candidate.
- equality: integer/rational arithmetic only; compute
  `ceil(1 + sumLocalAlpha / n)` without floating point.

## Candidate verification

Any crossing must be independently recomputed, receive an explicit edge list
and graph6 encoding, have its induced-tree witness replayed, and have
nontraceability checked by a separately implemented exact search. Every
subprocess has a hard 60-second cap.

No commit, push, release, issue, PR, or other public-state change is authorized.

