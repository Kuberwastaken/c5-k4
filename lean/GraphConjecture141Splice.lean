import GraphConjecture141Extraction

/-!
# WOWII 141: a certified one-vertex splice

The induced star pays the conjecture through girth five.  At girth six and
seven exactly one more retained vertex is needed.  This file isolates that
next rung as a reusable, finite certificate: a maximum local independent star
whose vertex set can be enlarged by one vertex while remaining an induced
tree.
-/

namespace WrittenOnTheWallII.GraphConjecture141Splice

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture141Extraction

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

/-- A one-vertex splice at `v`: `A` is a maximum independent set in `N(v)`,
and adjoining `x` to the induced star retains an induced tree.  The explicit
nonmembership field records that the splice really gains a vertex. -/
structure OneVertexSplice (G : SimpleGraph V) [DecidableRel G.Adj] where
  center : V
  localSet : Finset V
  extra : V
  localIndependent : G.IsIndepSet (localSet : Set V)
  localSubset : localSet ⊆ G.neighborFinset center
  localCard : localSet.card = indepNeighborsCard G center
  centerMaximal : indepNeighborsCard G center =
    Finset.univ.sup (indepNeighborsCard G)
  extra_not_mem : extra ∉ insert center localSet
  inducedTree :
    (G.induce (↑(insert extra (insert center localSet)) : Set V)).IsTree

/-- The exact cardinal gain supplied by a genuine one-vertex splice. -/
lemma card_splice (G : SimpleGraph V) [DecidableRel G.Adj]
    (W : OneVertexSplice G) :
    (insert W.extra (insert W.center W.localSet)).card =
      Finset.univ.sup (indepNeighborsCard G) + 2 := by
  have hcenter : W.center ∉ W.localSet := by
    intro hc
    have hadj : G.Adj W.center W.center := by
      rw [← mem_neighborFinset]
      exact W.localSubset hc
    exact G.loopless W.center hadj
  rw [Finset.card_insert_of_notMem W.extra_not_mem,
    Finset.card_insert_of_notMem hcenter, W.localCard, W.centerMaximal]

/-- A certified one-vertex splice pays two vertices beyond maximum local
independence. -/
theorem localIndependenceMax_add_two_le_largestInducedTreeSize
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (W : OneVertexSplice G) :
    Finset.univ.sup (indepNeighborsCard G) + 2 ≤
      G.largestInducedTreeSize := by
  rw [← card_splice G W]
  exact card_le_largestInducedTreeSize G _ W.inducedTree

/-- The exact WOWII 141 statement follows through girth seven from a
one-vertex splice certificate. -/
theorem conjecture141_of_girth_le_seven_of_oneVertexSplice
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hgirth : G.girth ≤ 7) (W : OneVertexSplice G) :
    (G.girth / 2 : ℤ) - 1 +
        ((Finset.univ.sup (indepNeighborsCard G) : ℕ) : ℤ) ≤
      (largestInducedTreeSize G : ℤ) := by
  have hsplice := localIndependenceMax_add_two_le_largestInducedTreeSize G W
  have hhalf : G.girth / 2 ≤ 3 := by omega
  have hspliceZ :
      ((Finset.univ.sup (indepNeighborsCard G) + 2 : ℕ) : ℤ) ≤
        (largestInducedTreeSize G : ℤ) := by exact_mod_cast hsplice
  have hhalfZ : ((G.girth / 2 : ℕ) : ℤ) ≤ 3 := by exact_mod_cast hhalf
  omega

/-- In the genuinely new girth-six-or-seven range, one splice is sufficient.
The lower bound is retained to make the scope of the new rung explicit. -/
theorem conjecture141_of_girth_six_or_seven_of_oneVertexSplice
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hgirthLower : 6 ≤ G.girth) (hgirthUpper : G.girth ≤ 7)
    (W : OneVertexSplice G) :
    (G.girth / 2 : ℤ) - 1 +
        ((Finset.univ.sup (indepNeighborsCard G) : ℕ) : ℤ) ≤
      (largestInducedTreeSize G : ℤ) := by
  have _ := hgirthLower
  exact conjecture141_of_girth_le_seven_of_oneVertexSplice G hgirthUpper W

end WrittenOnTheWallII.GraphConjecture141Splice
