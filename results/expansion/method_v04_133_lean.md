# Method v0.4: local Lean formalization audit for WOWII 133 cubic C4-free

Status: **EXACT STATEMENT COMPILES / FIRST TWO BRIDGES SUBSEQUENTLY RESOLVED**

Date: **2026-08-12 UTC**

Local artifact: `lean/GraphConjecture133Cubic.lean`

No file in `formal-conjectures` was edited.  No `sorry`, axiom, commit, push,
release, or upstream action was used.

**Follow-up (2026-08-13):** the first bridge described below has now been
proved without `sorry` as `isInducedPath_support_of_length_eq_dist`; see
`method_v04_133_geodesic_bridge.md`.  The historical audit below is retained to
show the exact boundary that the follow-up closed.

**Second follow-up (2026-08-13):** radius-realizing endpoint selection,
shortest-walk construction, exact support length, and the generic bound
`G.radius.toNat + 1 ≤ path G` are now proved without `sorry`; see
`method_v04_133_radius_bridge.md`.  The next boundary is the cubic/C4-free
one-vertex extension, not the metric representation API.

## Exact theorem target

The local Lean file defines:

```lean
def HasC4 (G : SimpleGraph V) : Prop :=
  ∃ a b c d : V,
    a ≠ b ∧ a ≠ c ∧ a ≠ d ∧ b ≠ c ∧ b ≠ d ∧ c ≠ d ∧
      G.Adj a b ∧ G.Adj b c ∧ G.Adj c d ∧ G.Adj d a

def CubicC4FreeSplit (G : SimpleGraph V) : Prop :=
  (G.CliqueFree 3 → ⌊l G⌋ = (3 : ℤ) ∧ G.radius.toNat + 3 ≤ path G) ∧
  (¬G.CliqueFree 3 → ⌊l G⌋ = (2 : ℤ) ∧ G.radius.toNat + 2 ≤ path G)

def CubicC4FreeConclusion (G : SimpleGraph V) : Prop :=
  (G.radius.toNat : ℝ) + (⌊l G⌋ : ℝ) ≤ (path G : ℝ)

def CubicC4FreeTheorem : Prop :=
  ∀ (G : SimpleGraph V),
    [DecidableRel G.Adj] →
    G.Connected →
    G.IsRegularOfDegree 3 →
    ¬HasC4 G →
    CubicC4FreeSplit G ∧ CubicC4FreeConclusion G
```

This deliberately does not state `radius+3` in the triangle-containing branch.
C4-freeness alone does not imply triangle-freeness.  The target is therefore
exactly the two-case paper theorem, not the stronger unresolved shadow and not
full WOWII 133.

`HasC4` is copied propositionally from upstream `GraphConjecture133.lean`, so
the local hypothesis excludes non-induced four-cycles exactly as the source
does.  Triangle-freeness is represented by mathlib's `G.CliqueFree 3`.

## No-sorry progress that compiles

Two reusable theorems are complete.

### Induced-list witness to `path`

```lean
theorem path_ge_of_isInducedPath (G : SimpleGraph V) (xs : List V)
    (hxs : G.isInducedPath xs) : xs.length ≤ path G
```

The proof unfolds the project-local `path`, inserts `xs.toFinset` into the
filtered finite set of induced paths, uses nodup to identify its cardinality
with `xs.length`, and applies the finite maximum bound.  This bridge was absent
from `FormalConjecturesForMathlib/.../VertexDistance.lean`.

### Case split to source inequality

```lean
theorem conclusion_of_split (G : SimpleGraph V)
    (h : CubicC4FreeSplit G) : CubicC4FreeConclusion G
```

This is a no-sorry proof by cases on `G.CliqueFree 3`, rewriting the appropriate
floor equality and casting the natural path bound to reals.  It verifies that
the formal two-case target really implies the intended cubic source inequality.

## First missing API/lemma

The paper proof begins by choosing a center--periphery geodesic.  Existing APIs
provide the pieces only in incompatible representations:

- `SimpleGraph.exists_edist_eq_radius_of_finite` chooses endpoints at radius;
- connectedness converts finite `edist` to `dist`;
- `SimpleGraph.Connected.exists_path_of_dist` supplies a shortest `G.Walk` and
  proves `Walk.IsPath`;
- the WOWII invariant `SimpleGraph.path`, however, recognizes only a
  `List V` satisfying the separate predicate `SimpleGraph.isInducedPath`.

There is no theorem converting a shortest walk (or `Walk.IsPath` plus
`Walk.length = G.dist`) into `G.isInducedPath` for a vertex list, and no existing
theorem directly asserting that a geodesic is induced in this local sense.
Searches of mathlib's `SimpleGraph/Metric`, `Paths`, `Walks`, and the
FormalConjectures helper modules found only `Walk.isPath_of_length_eq_dist` and
`Reachable.exists_path_of_dist`; neither supplies the chordlessness biconditional
required by `isInducedPath`:

```lean
∀ i j : Fin xs.length,
  G.Adj (xs.get i) (xs.get j) ↔
    i.val + 1 = j.val ∨ j.val + 1 = i.val
```

This is the first unresolved formal lemma on the paper route.  The full proof
stops here rather than postulating it or weakening the result.

## Required lemma ladder

The following keeps the paper mathematics unchanged.

1. **Walk/list representation bridge.** Establish the length, indexing,
   nodup, and consecutive-adjacency facts for the canonical vertex list of a
   walk.  If no suitable public list projection exists, define one locally and
   prove it agrees with `Walk.support`/`Walk.getVert`.
2. **Geodesics are induced.** If `p.length = G.dist u v`, prove the associated
   vertex list satisfies `G.isInducedPath`.  A chord between nonconsecutive
   indices yields a strictly shorter `u-v` walk, contradicting `dist_le`.
3. **Finite radius geodesic (subsequently resolved through the generic
   `radius+1` path bound).** Combine
   `exists_edist_eq_radius_of_finite`, connectedness, and
   `Connected.exists_path_of_dist`; prove the list has length
   `G.radius.toNat + 1`.  The remaining claim that it has at least three
   vertices uses cubicity plus C4-freeness to exclude radius zero and one.
4. **One-extension lemma.** Extract the two off-geodesic neighbors of the
   center from `neighborFinset` cardinality three.  C4-freeness proves at least
   one avoids `v1`; metric and C4 arguments exclude all later contacts.  Prepend
   it and use `path_ge_of_isInducedPath` to obtain `radius+2`.
5. **Local independence split.** Prove every cubic C4-free neighborhood has at
   most one edge.  Then prove `indepNeighborsCard G v` is three off triangles
   and two on triangles.  Sum these values in `averageIndepNeighbors`; in the
   non-triangle-free case at least one summand is two, giving `2 ≤ l G < 3` and
   hence `⌊l G⌋=2`.  In the triangle-free case all summands are three.
6. **Four-forward-neighbor extension.** Under `CliqueFree 3`, enumerate the
   four distinct forward neighbors of the two off-geodesic center neighbors.
   Show their only possible geodesic contacts are `v2,v3`.  Translate the
   degree-three contact-slot count for radii 2, 3, and at least 4 into a finite
   pigeonhole argument.  Prepend the clean two-vertex branch to get
   `radius+3`.
7. Assemble `CubicC4FreeSplit`; apply `conclusion_of_split`.

The largest engineering cost is expected in steps 1, 3, 4, and 6 because the
current invariant uses list indices while the mature metric API uses walks.
Step 5 has useful mathlib support
(`isIndepSet_neighborSet_of_triangleFree`), but the exact independence-number
equalities still require upper-bound/cardinality plumbing.

## Verification

From the unmodified local checkout of `formal-conjectures`:

```text
lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture133Cubic.lean
```

The command succeeds.  A source scan also finds no `sorry`, `admit`, or custom
axiom in the local file.

## Scope

This is a compiled exact statement plus two proved infrastructure lemmas, not a
completed formal proof of the specialization.  It makes no claim about the
stronger triangle-containing `radius+3` statement, noncubic C4-free graphs, or
full WOWII 133.
