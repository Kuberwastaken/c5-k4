import FormalConjecturesUtil

/-!
# WOWII 133: noncubic C4-free reductions

This file moves beyond the completed cubic specialization without claiming
the full conjecture.  It identifies the local invariant exactly on every
triangle-free graph and formalizes the matching structure forced on every
neighborhood by C4-freeness.
-/

namespace WrittenOnTheWallII.GraphConjecture133Next

open SimpleGraph

variable {V : Type*} [Fintype V] [DecidableEq V] [Nonempty V]

/-- Four distinct vertices forming a not-necessarily-induced four-cycle. -/
def HasC4 (G : SimpleGraph V) : Prop :=
  ∃ a b c d : V,
    a ≠ b ∧ a ≠ c ∧ a ≠ d ∧ b ≠ c ∧ b ≠ d ∧ c ≠ d ∧
      G.Adj a b ∧ G.Adj b c ∧ G.Adj c d ∧ G.Adj d a

omit [DecidableEq V] [Nonempty V] in
/-- In a triangle-free graph, the entire open neighborhood is independent,
so its independence number is exactly the degree. -/
lemma indepNeighborsCard_eq_degree_of_triangleFree (G : SimpleGraph V)
    [DecidableRel G.Adj] (htri : G.CliqueFree 3) (v : V) :
    indepNeighborsCard G v = G.degree v := by
  unfold indepNeighborsCard
  rw [← G.card_neighborSet_eq_degree]
  symm
  apply maximumIndepSet_card_eq_indepNum
  constructor
  · intro x _hx y _hy hxy
    change ¬G.Adj x.val y.val
    exact G.isIndepSet_neighborSet_of_triangleFree htri v x.property y.property
      (Subtype.coe_injective.ne hxy)
  · intro t _ht
    exact Finset.card_le_univ t

omit [DecidableEq V] [Nonempty V] in
/-- Triangle-freeness identifies the WOWII local-neighborhood average exactly
with the ordinary average degree (cast from the repository's rational-valued
invariant). -/
lemma l_eq_averageDegree_of_triangleFree (G : SimpleGraph V)
    [DecidableRel G.Adj] (htri : G.CliqueFree 3) :
    l G = ((averageDegree G : ℚ) : ℝ) := by
  unfold l averageIndepNeighbors indepNeighbors averageDegree
  simp_rw [indepNeighborsCard_eq_degree_of_triangleFree G htri]
  push_cast
  rfl

omit [DecidableEq V] [Nonempty V] in
/-- The corresponding floor identity used by the C4-free branch of WOWII
133. -/
lemma floor_l_eq_floor_averageDegree_of_triangleFree (G : SimpleGraph V)
    [DecidableRel G.Adj] (htri : G.CliqueFree 3) :
    ⌊l G⌋ = ⌊((averageDegree G : ℚ) : ℝ)⌋ := by
  rw [l_eq_averageDegree_of_triangleFree G htri]

/-- The exact source-shaped inequality in the C4-free branch. -/
def C4FreeBranchConclusion (G : SimpleGraph V) : Prop :=
  (G.radius.toNat : ℝ) + (⌊l G⌋ : ℝ) ≤ (path G : ℝ)

/-- The reduced average-degree wall obtained in the triangle-free stratum. -/
def TriangleFreeAverageDegreeConclusion (G : SimpleGraph V)
    [DecidableRel G.Adj] : Prop :=
  (G.radius.toNat : ℝ) +
      (⌊((averageDegree G : ℚ) : ℝ)⌋ : ℝ) ≤ (path G : ℝ)

omit [Nonempty V] in
/-- On every triangle-free graph, the C4-free branch of WOWII 133 is exactly
the average-degree path wall.  C4-freeness is not needed for the algebraic
identity, but is the stratum in which the source exponent selects this
branch. -/
theorem c4FreeBranch_iff_averageDegree_of_triangleFree (G : SimpleGraph V)
    [DecidableRel G.Adj] (htri : G.CliqueFree 3) :
    C4FreeBranchConclusion G ↔ TriangleFreeAverageDegreeConclusion G := by
  unfold C4FreeBranchConclusion TriangleFreeAverageDegreeConclusion
  rw [floor_l_eq_floor_averageDegree_of_triangleFree G htri]

omit [DecidableEq V] in
/-- A triangle-free regular graph has local-neighborhood average exactly its
regular degree, with no cubic restriction. -/
lemma l_eq_regularDegree_of_triangleFree (G : SimpleGraph V)
    [DecidableRel G.Adj] (d : ℕ) (hreg : G.IsRegularOfDegree d)
    (htri : G.CliqueFree 3) :
    l G = (d : ℝ) := by
  unfold l averageIndepNeighbors indepNeighbors
  simp_rw [indepNeighborsCard_eq_degree_of_triangleFree G htri]
  have hdeg : ∀ v, G.degree v = d := hreg
  simp_rw [hdeg]
  simp [Fintype.card_ne_zero]

/-- Thus, for every regular degree `d`, the triangle-free branch is exactly
`radius + d ≤ path`. -/
theorem c4FreeBranch_iff_radius_add_degree_of_regular_triangleFree
    (G : SimpleGraph V) [DecidableRel G.Adj] (d : ℕ)
    (hreg : G.IsRegularOfDegree d) (htri : G.CliqueFree 3) :
    C4FreeBranchConclusion G ↔
      (G.radius.toNat : ℝ) + (d : ℝ) ≤ (path G : ℝ) := by
  unfold C4FreeBranchConclusion
  rw [l_eq_regularDegree_of_triangleFree G d hreg htri]
  norm_num

omit [DecidableEq V] [Nonempty V] in
/-- C4-freeness forces the graph induced by each open neighborhood to have
degree at most one at every vertex.  Equivalently, its non-isolated edges form
a matching.  This is the structural starting point for the triangle-corrected
average formula in the remaining noncubic branch. -/
lemma degree_induce_neighborSet_le_one_of_c4Free (G : SimpleGraph V)
    [DecidableRel G.Adj] (hc4 : ¬HasC4 G) (v : V)
    (w : G.neighborSet v) :
    (G.induce (G.neighborSet v)).degree w ≤ 1 := by
  classical
  let H := G.induce (G.neighborSet v)
  change H.degree w ≤ 1
  by_contra hle
  have hlarge : 1 < (H.neighborFinset w).card := by
    rw [H.card_neighborFinset_eq_degree]
    omega
  obtain ⟨a, ha, b, hb, hab⟩ := Finset.one_lt_card.mp hlarge
  have hwa : H.Adj w a := by
    simpa [H.mem_neighborFinset] using ha
  have hwb : H.Adj w b := by
    simpa [H.mem_neighborFinset] using hb
  have hva : G.Adj v a.val := a.property
  have hvw : G.Adj v w.val := w.property
  have hvb : G.Adj v b.val := b.property
  have haw : G.Adj a.val w.val := by
    simpa [H, induce_adj] using hwa.symm
  have hwb' : G.Adj w.val b.val := by
    simpa [H, induce_adj] using hwb
  apply hc4
  refine ⟨v, a.val, w.val, b.val, ?_, ?_, ?_, ?_, ?_, ?_,
    hva, haw, hwb', hvb.symm⟩
  · exact hva.ne
  · exact hvw.ne
  · exact hvb.ne
  · exact haw.ne
  · exact fun h ↦ hab (Subtype.ext h)
  · exact hwb'.ne

end WrittenOnTheWallII.GraphConjecture133Next
