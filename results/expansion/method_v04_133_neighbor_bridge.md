# Method v0.4: WOWII 133 clean-neighbor bridge

Status: **ONE-EXTENSION BRANCH PROVED LOCALLY / NO SORRY**

Date: **2026-08-13 UTC**

Local artifact: `lean/GraphConjecture133Cubic.lean`

This bounded follow-up closes the finite-neighbor selection and contact
arguments left open by `method_v04_133_prepend_bridge.md`.  It goes one step
further than the minimum requested bridge: combining the new selection lemma
with the existing induced-list and radius-geodesic infrastructure proves the
complete path-length half of the triangle-containing branch,

```text
radius(G) + 2 <= path(G),
```

for every finite connected cubic C4-free graph.  It does not prove the
local-average floor formula, the triangle-free `radius+3` extension, or the
full WOWII 133 specialization.

## Compiled endpoint theorem

```lean
lemma radius_add_two_le_path_of_cubic_c4Free (G : SimpleGraph V)
    [DecidableRel G.Adj] (hconn : G.Connected)
    (hreg : G.IsRegularOfDegree 3) (hc4 : ¬HasC4 G) :
    G.radius.toNat + 2 ≤ path G
```

The proof uses exactly the hypotheses already present in the local theorem
target.  In particular, it does not assume triangle-freeness.

## Reusable lemma chain

The endpoint theorem is assembled from five new reusable facts.

1. `exists_radius_geodesic_support_with_dist` strengthens the earlier witness
   package by retaining both `p.length = G.dist u v` and
   `p.length = G.radius.toNat`.  The retained distance equality is essential
   for certified shortcut contradictions.
2. `exists_neighbor_head_ne_snd_not_adj_snd_of_cubic_c4Free` selects a neighbor
   `a` of the geodesic head which differs from, and is not adjacent to, the
   second geodesic vertex.
3. `eq_snd_of_mem_support_of_adj_head_of_geodesic` proves that the only support
   vertex adjacent to the head is the second vertex.  Consequently, the
   selected `a` is fresh.
4. `not_adj_getVert_pos_of_geodesic_of_c4Free` excludes every contact from `a`
   to a positive geodesic index.
5. `exists_inducedPath_cons_support_of_geodesic_of_cubic_c4Free` feeds those
   facts into `isInducedPath_cons_of_adj_head_of_not_adj_tail`, producing an
   induced list with `p.length + 2` vertices.

The intermediate package
`exists_clean_neighbor_of_geodesic_of_cubic_c4Free` exposes exactly the
interface promised by the previous report:

```lean
∃ a : V, G.Adj a u ∧ a ∉ p.support ∧
  ∀ x ∈ p.support.tail, ¬G.Adj a x
```

## Mathematical argument

Let the radius-realizing geodesic begin
`u = v0, v1, v2, ...`.  Cubicity gives three neighbors of `u`; after erasing
`v1`, exactly two remain.  If both remaining neighbors were adjacent to
`v1`, they and `u,v1` would form a four-cycle.  Hence one of them, call it
`a`, avoids `v1`.

Three short arguments make `a` clean.

- If `a` occurred on the geodesic, inducedness and adjacency to its head would
  force `a=v1`, contradicting the selection.
- An edge `a-v2` would create the four-cycle `u-v1-v2-a-u`.
- An edge from `a` to `vk` for `k>=3` would replace the first `k` geodesic
  edges by `u-a-vk`, producing a strictly shorter `u`--`v` walk.

The radius is at least two by the previously compiled small-radius lemma, so
`v2` always exists.  Prepending `a` therefore enlarges the radius geodesic by
one vertex, from `radius+1` to `radius+2`, and the repository-local `path`
maximum supplies the final inequality.

## Verification

Every build and search subprocess was explicitly capped at 60 seconds.  The
final warning-as-error build was:

```text
timeout 60s lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture133Cubic.lean
```

Result: exit status `0` in approximately 9.5 seconds.  A temporary
`#print axioms` audit for both the endpoint theorem and the clean-neighbor
package reported only `propext`, `Classical.choice`, and `Quot.sound`; it did
not report `sorryAx` or any project-specific axiom.  A capped source scan found
no `sorry`, `admit`, or custom `axiom`.

## Exact remaining boundary

The non-triangle-free path bound required by `CubicC4FreeSplit` is now closed.
Two independent obligations remain before the local split theorem can be
assembled:

1. prove the local-average identities
   `⌊l G⌋ = 3` in the triangle-free branch and `⌊l G⌋ = 2` when a
   triangle is present; and
2. in the triangle-free branch, select a clean two-edge branch rather than the
   single clean neighbor proved here, yielding `radius+3 <= path`.

The next path-specific bounded step is therefore the four-forward-neighbor
contact-slot argument described in `method_v04_133_lean.md`.  The present
proof provides its first clean neighbor and all walk/list plumbing, but does
not silently assume that one of the neighbor's two forward neighbors is also
clean.
