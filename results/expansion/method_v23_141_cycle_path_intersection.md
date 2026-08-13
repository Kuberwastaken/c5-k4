# Method v0.23: WOWII #141 simple-cycle path intersection

Date: 2026-08-13
Status: cycle-side path decomposition verified; last-common-root-path splice remains

## Scope

This is a bounded support rung for the exact upstream WOWII #141 declaration.
It does not claim a full proof of the conjecture and does not alter the
existing radius-three certificate interface.

The preceding v0.22 development reduced the girth-ten radius-three step to a
cycle-peak property.  Its recurring technical need was to cut a simple cycle
at a vertex where another path meets it, leaving a genuine simple path rather
than an arbitrary closed walk.

## Formalized cycle surgery

[`lean/GraphConjecture141CyclePathIntersection.lean`](../../lean/GraphConjecture141CyclePathIntersection.lean)
proves `simple_cycle_path_decomposition_at_intersection`.

Given a simple cycle `c` and a vertex `i` in its support, the theorem rotates
`c` to a closed walk `q` based at `i` and certifies:

- `q` is still a simple cycle;
- `q.length = c.length`;
- `q.tail` is a simple path;
- `q.tail.dropLast` is a simple path;
- `i` is absent from `q.tail.dropLast.support`;
- `i` is adjacent to the two endpoints exposed by cutting the cycle; and
- those two cycle neighbors are distinct.

Thus deleting the selected intersection vertex turns the remaining cycle arc
into a clean simple path between its two neighbors.  Rotation length is proved
from the existing dart-list rotation theorem, and path simplicity is inherited
through the subwalk API.  The endpoint-exclusion proof uses nodup support and
the exact support of `Walk.dropLast`.

The file also records the small set-level helper
`support_inter_cycle_subsingleton_of_pairwise`, which packages the conclusion
that a path/cycle support intersection is a subsingleton once all common
vertices have been identified.

## Why this matters for the cycle peak

For a maximum-distance vertex `i` on a hypothetical cycle, the cycle theorem
now supplies two distinct neighbors and a simple complementary arc avoiding
`i`.  Therefore the cycle itself no longer needs to be manually normalized,
rotated, or stripped of its repeated basepoint during the girth contradiction.

This is exactly the standard simple-cycle/path-intersection primitive missing
from the v0.22 Lean interface.

## Exact remaining obstruction

The remaining work is on the two shortest paths from the BFS root to selected
cycle vertices—not on the cycle decomposition.

Lean still needs a lemma that:

1. chooses the last common vertex of two finite simple root paths;
2. splits both paths at that vertex;
3. proves the two suffix supports are internally disjoint; and
4. combines those suffixes with the relevant cycle edge or simple cycle arc
   into a `Walk.IsCycle`, with length bounded by the sum of the two root-path
   lengths plus the arc length.

For adjacent vertices in the same BFS layer `k<=3`, that construction should
produce a cycle of length at most `2k+1<=7`, contradicting girth at least ten.
The same splice with two distinct parents of a layer-`k` vertex should give a
cycle of length at most `2k<=6`, proving parent uniqueness.

Once this last-common-intersection splice is available, the intended cycle
peak follows: a maximum-rank cycle vertex cannot have a same-layer cycle
neighbor, while maximality rules out a higher neighbor, so both cycle
neighbors lie exactly one layer lower.

No claim beyond that reduction is made here.

## Verification

From the `formal-conjectures` checkout:

```bash
LEAN_PATH=/tmp/c5k4-141-cycle timeout 60s lake env lean \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture141CyclePathIntersection.lean
```

Result: exit code 0, no diagnostics, approximately seven seconds.  The file
contains no `sorry`, `admit`, `native_decide`, or custom axiom.
