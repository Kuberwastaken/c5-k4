import GraphConjecture19CenterAttachmentClassification

/-!
# WOWII 19/13: the fundamental endpoint's tree attachment
-/

namespace WrittenOnTheWallII.GraphConjecture19CenterTreeAttachment

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture19UnicyclicDecomposition
open WrittenOnTheWallII.GraphConjecture19FundamentalCycle
open WrittenOnTheWallII.GraphConjecture19CenterAttachmentClassification

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

omit [Fintype V] [DecidableEq V] in
/-- The first vertex after `extraRight` on any fundamental tree path lies in
that path's support. -/
lemma snd_mem_support_of_not_nil
    {G : SimpleGraph V} {a b : V} (q : G.Walk a b) (hq : ¬q.Nil) :
    q.snd ∈ q.support := by
  cases q with
  | nil => exact (hq Walk.Nil.nil).elim
  | cons h q => simp

/-- In the center-left saturated independent-neighborhood branch, the first
tree attachment of `extraRight` on every fundamental path is a noncenter
vertex of the geodesic. -/
theorem fundamentalPath_snd_mem_path_and_ne_center
    {G : SimpleGraph V} [DecidableRel G.Adj]
    (D : TreePlusOneEdge G) (P : Finset V) (c : V)
    (hc : D.extraLeft = c)
    (hRightOff : D.extraRight ∉ P)
    (hsat : P ∪ G.neighborFinset c = Finset.univ)
    (hcenter : G.IsIndepSet (G.neighborSet c))
    (q : D.tree.Walk D.extraRight D.extraLeft) :
    q.snd ∈ P ∧ q.snd ≠ c ∧ D.tree.Adj D.extraRight q.snd := by
  have hqNotNil : ¬q.Nil := by
    intro hnil
    exact D.endpoints_ne hnil.eq.symm
  have hrightSnd : D.tree.Adj D.extraRight q.snd := q.adj_snd hqNotNil
  have hsndNeCenter : q.snd ≠ c := by
    intro hsnd
    apply D.extra_not_tree
    simpa [hc, hsnd, adj_comm] using hrightSnd
  have hrightN : D.extraRight ∈ G.neighborFinset c :=
    off_path_mem_center_neighborhood P c D.extraRight hsat hRightOff
  have hsndCover : q.snd ∈ P ∪ G.neighborFinset c := by
    rw [hsat]
    simp
  have hsndP : q.snd ∈ P := by
    rcases Finset.mem_union.mp hsndCover with hsndP | hsndN
    · exact hsndP
    · have hrightSet : D.extraRight ∈ G.neighborSet c := by
        simpa [mem_neighborFinset] using hrightN
      have hsndSet : q.snd ∈ G.neighborSet c := by
        simpa [mem_neighborFinset] using hsndN
      have hrightSndG : G.Adj D.extraRight q.snd :=
        D.adj_iff.mpr (Or.inl hrightSnd)
      exact (hcenter hrightSet hsndSet hrightSndG.ne hrightSndG).elim
  exact ⟨hsndP, hsndNeCenter, hrightSnd⟩

/-- Existence form: the off-path added-edge endpoint has a genuine tree
attachment to a noncenter geodesic vertex. -/
theorem exists_fundamental_tree_attachment_on_path
    {G : SimpleGraph V} [DecidableRel G.Adj]
    (D : TreePlusOneEdge G) (P : Finset V) (c : V)
    (hc : D.extraLeft = c)
    (hRightOff : D.extraRight ∉ P)
    (hsat : P ∪ G.neighborFinset c = Finset.univ)
    (hcenter : G.IsIndepSet (G.neighborSet c)) :
    ∃ x : V, x ∈ P ∧ x ≠ c ∧ D.tree.Adj D.extraRight x := by
  obtain ⟨q, _hq, _hunique⟩ :=
    WrittenOnTheWallII.GraphConjecture19FundamentalCycle.TreePlusOneEdge.existsUnique_fundamentalPath
      D
  exact ⟨q.snd,
    fundamentalPath_snd_mem_path_and_ne_center
      D P c hc hRightOff hsat hcenter q⟩

/-- Every ordinary off-path vertex has its center edge in the tree, whereas
`extraRight` has both the added center edge and a certified tree attachment to
the geodesic.  This separates the fundamental-cycle carrier from all ordinary
off-path vertices. -/
theorem center_tree_attachment_split
    {G : SimpleGraph V} [DecidableRel G.Adj]
    (D : TreePlusOneEdge G) (P : Finset V) (c : V)
    (hc : D.extraLeft = c)
    (hRightOff : D.extraRight ∉ P)
    (hsat : P ∪ G.neighborFinset c = Finset.univ)
    (hcenter : G.IsIndepSet (G.neighborSet c)) :
    (∀ z ∈ Finset.univ \ P, z ≠ D.extraRight → D.tree.Adj c z) ∧
      ∃ x : V, x ∈ P ∧ x ≠ c ∧ D.tree.Adj D.extraRight x := by
  constructor
  · intro z hz hzRight
    exact (classify_off_path_attachments_center_left
      D P c hc hRightOff hsat hcenter z hz).2.1 hzRight
  · exact exists_fundamental_tree_attachment_on_path
      D P c hc hRightOff hsat hcenter

end WrittenOnTheWallII.GraphConjecture19CenterTreeAttachment
