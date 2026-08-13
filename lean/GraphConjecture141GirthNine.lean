import GraphConjecture141DistanceTwoExistence

/-!
# WOWII 141: the two-vertex tail for girth eight and nine
-/

namespace WrittenOnTheWallII.GraphConjecture141GirthNine

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture141Extraction

universe u

variable {V : Type u} [Fintype V] [DecidableEq V] [Nonempty V]

/-- A maximum local star with a genuine two-vertex induced-tree tail. -/
structure TwoVertexTailSplice (G : SimpleGraph V) [DecidableRel G.Adj] where
  center : V
  localSet : Finset V
  first : V
  second : V
  localIndependent : G.IsIndepSet (localSet : Set V)
  localSubset : localSet ⊆ G.neighborFinset center
  localCard : localSet.card = indepNeighborsCard G center
  centerMaximal : indepNeighborsCard G center =
    Finset.univ.sup (indepNeighborsCard G)
  first_not_mem : first ∉ insert center localSet
  second_not_mem : second ∉ insert first (insert center localSet)
  inducedTree :
    (G.induce
      (↑(insert second (insert first (insert center localSet))) : Set V)).IsTree

omit [Nonempty V] in
/-- Exact cardinality of the star with a genuine two-vertex tail. -/
lemma card_twoVertexTail
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (W : TwoVertexTailSplice G) :
    (insert W.second (insert W.first (insert W.center W.localSet))).card =
      Finset.univ.sup (indepNeighborsCard G) + 3 := by
  have hcenter : W.center ∉ W.localSet := by
    intro hc
    exact G.loopless W.center (by
      rw [← mem_neighborFinset]
      exact W.localSubset hc)
  rw [Finset.card_insert_of_notMem W.second_not_mem,
    Finset.card_insert_of_notMem W.first_not_mem,
    Finset.card_insert_of_notMem hcenter, W.localCard, W.centerMaximal]

omit [Nonempty V] in
/-- A two-vertex tail pays the three vertices beyond maximum local
independence required at girth eight and nine. -/
theorem localIndependenceMax_add_three_le_largestInducedTreeSize
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (W : TwoVertexTailSplice G) :
    Finset.univ.sup (indepNeighborsCard G) + 3 ≤
      G.largestInducedTreeSize := by
  rw [← card_twoVertexTail G W]
  exact card_le_largestInducedTreeSize G _ W.inducedTree

omit [Nonempty V] in
/-- Exact upstream-shaped WOWII 141 in the girth-eight-or-nine range from a
two-vertex-tail certificate. -/
theorem conjecture141_of_girth_eight_or_nine_of_twoVertexTailSplice
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hgirthLower : 8 ≤ G.girth) (hgirthUpper : G.girth ≤ 9)
    (W : TwoVertexTailSplice G) :
    (G.girth / 2 : ℤ) - 1 +
        ((Finset.univ.sup (indepNeighborsCard G) : ℕ) : ℤ) ≤
      (largestInducedTreeSize G : ℤ) := by
  have htail := localIndependenceMax_add_three_le_largestInducedTreeSize G W
  have hhalf : G.girth / 2 ≤ 4 := by omega
  have htailZ :
      ((Finset.univ.sup (indepNeighborsCard G) + 3 : ℕ) : ℤ) ≤
        (largestInducedTreeSize G : ℤ) := by exact_mod_cast htail
  have hhalfZ : ((G.girth / 2 : ℕ) : ℤ) ≤ 4 := by exact_mod_cast hhalf
  omega

/-- The exact obstruction left by the next shortest-path splice.  For a
three-edge prefix `v-u-x-y`, the third vertex must have no chord back into
the local star except its prescribed edge to `x`. -/
def ThirdVertexChordExclusion (G : SimpleGraph V)
    (v x y : V) (A : Finset V) : Prop :=
  ¬G.Adj y v ∧ (∀ a ∈ A, ¬G.Adj y a) ∧ G.Adj x y

omit [Nonempty V] in
/-- A graph satisfying the explicit two-tail certificate closes the new
range; failure to build that certificate is therefore exactly a tail/chord
existence obstruction, not an arithmetic one. -/
theorem girthNine_reduced_to_twoVertexTail
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hgirthLower : 8 ≤ G.girth) (hgirthUpper : G.girth ≤ 9) :
    Nonempty (TwoVertexTailSplice G) →
      (G.girth / 2 : ℤ) - 1 +
          ((Finset.univ.sup (indepNeighborsCard G) : ℕ) : ℤ) ≤
        (largestInducedTreeSize G : ℤ) := by
  rintro ⟨W⟩
  exact conjecture141_of_girth_eight_or_nine_of_twoVertexTailSplice
    G hgirthLower hgirthUpper W

end WrittenOnTheWallII.GraphConjecture141GirthNine
