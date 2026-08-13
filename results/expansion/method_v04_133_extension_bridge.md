# Method v0.4: WOWII 133 small-radius bridge

Status: **RADIUS LEMMA PROVED LOCALLY / ONE-EXTENSION STILL OPEN**

Date: **2026-08-13 UTC**

Local artifact: `lean/GraphConjecture133Cubic.lean`

This bounded follow-up addresses the first graph-specific obligation after the
geodesic and radius-witness bridges.  It proves that a finite connected cubic
C4-free graph has radius at least two.  It does not claim the subsequent
off-geodesic one-vertex extension or the full cubic specialization.

## Compiled theorem

```lean
lemma two_le_radius_toNat_of_cubic_c4Free (G : SimpleGraph V)
    [DecidableRel G.Adj] (hconn : G.Connected)
    (hreg : G.IsRegularOfDegree 3) (hc4 : ¬HasC4 G) :
    2 ≤ G.radius.toNat
```

The statement uses exactly the hypotheses available in the local theorem
target.  In particular, it does not assume triangle-freeness.

## Proof structure

1. Cubicity at any vertex gives nonzero degree, hence `V` is nontrivial.
2. Connectedness gives `G.radius ≠ ⊤`.  If `radius.toNat < 2`, exact `ENat`
   conversion therefore reduces the possibilities to radius zero or one.
3. Radius zero contradicts `radius_ne_zero_of_nontrivial`.
4. At radius one, choose a center `c`.  The theorem
   `eccent_eq_one_iff` says that `c` is adjacent to every other vertex.
5. Thus `univ = insert c (neighborFinset c)`.  Cubicity gives three
   neighbors, so `Fintype.card V = 4`.
6. Regularity of the complement gives degree zero at every vertex, hence
   `Gᶜ = ⊥` and `G = ⊤`.
7. An equivalence `V ≃ Fin 4` supplies four distinct vertices.  Since `G` is
   complete, they form a four-cycle, contradicting `¬HasC4 G`.

This formalizes Lemma 1 of `method_v03_133_proof.md` without replacing the
paper argument by finite computation.

## Remaining one-extension boundary

The desired next theorem is still

```text
radius(G) + 2 <= path(G).
```

The mathematics is unchanged: for a radius-realizing geodesic
`c=v0,v1,...,vr`, cubicity supplies two neighbors of `c` other than `v1`;
C4-freeness makes at least one avoid `v1`, and the metric/C4 argument excludes
contacts with every later geodesic vertex.

The first unformalized interface is now precise.  The existing
`exists_radius_geodesic_support` packages only endpoints, a walk, and its
support.  The extension proof needs a strengthened witness package exposing:

- the first and second support vertices (`v0`, `v1`) and, using the new radius
  lower bound, `v2`;
- an exact three-element `neighborFinset v0` together with the fact that `v1`
  belongs to it;
- a selected neighbor `a` outside `v1` whose adjacency to later support
  indices is ruled out; and
- a list lemma turning those facts into
  `G.isInducedPath (a :: p.support)`.

Mathlib has the required ingredients separately (`Walk.getVert`, support
indexing, `neighborFinset`, and finite-cardinality lemmas), but this local file
does not yet have the dependent-index plumbing joining them.  In particular,
the new radius theorem closes the `v2` existence issue; the remaining blocker
is the finite-neighbor selection plus the `Fin (length + 1)` case split needed
for the prepended-list induced-path biconditional.  No axiom or weakened
statement was introduced to bypass that boundary.

## Verification

Every search and build subprocess was explicitly capped at 60 seconds.  Final
command:

```text
timeout 60s lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture133Cubic.lean
```

Result: exit status `0` in approximately 9 seconds.  A temporary
`#print axioms` audit reported only `propext`, `Classical.choice`, and
`Quot.sound`; it did not report `sorryAx` or any project-specific axiom.  The
file contains no `sorry`, `admit`, or custom `axiom`.

## Next bounded step

Prove the representation-only lemma for prepending a clean neighbor to an
induced list, independently of radius and cubicity.  Once that compiles, enrich
`exists_radius_geodesic_support` with the first three indexed vertices and
perform the three-neighbor selection as a separate theorem.  Keeping those
steps separate will make any remaining failure attributable either to list
indexing or to the graph argument, rather than conflating both.
