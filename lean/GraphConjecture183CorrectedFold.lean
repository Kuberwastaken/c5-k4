import GraphConjecture183SelectionExistence

/-!
# WOWII 183: corrected attachment/trunk fold

This ports the v0.11 domination, connectivity, injectivity, and certificate
construction to `SelectedAttachmentData`, whose attachment conditions are
correctly indexed only by non-root outside components.
-/

namespace WrittenOnTheWallII.GraphConjecture183CorrectedFold

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture183OutsideBudget
open WrittenOnTheWallII.GraphConjecture183ComponentFold
open WrittenOnTheWallII.GraphConjecture183Attachment
open WrittenOnTheWallII.GraphConjecture183ComponentAssembly
open WrittenOnTheWallII.GraphConjecture183AttachmentSelection
open WrittenOnTheWallII.GraphConjecture183SelectionExistence

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

/-- `x` together with exactly the branches indexed by the corrected non-root
component collection. -/
def correctedSelectedSet (G : SimpleGraph V) (x : V)
    (S : SelectedAttachmentData G x)
    (T : (outsideGraph G x).ConnectedComponent →
      Finset (outsideVertices G x)) : Finset V :=
  insert x (S.C.biUnion fun c => attachmentBranch G x (S.attach c) (T c))

/-- The witness fold includes the root component as well as every selected
non-root component. -/
noncomputable def correctedWitnessComponents (G : SimpleGraph V) (x : V)
    (S : SelectedAttachmentData G x) :
    Finset (outsideGraph G x).ConnectedComponent := by
  classical
  exact insert (rootOutsideComponent G x) S.C

/-- Correctly indexed local trunks and component bipartite witnesses. -/
structure CorrectedTrunkData (G : SimpleGraph V) (x : V) where
  selection : SelectedAttachmentData G x
  trunk : (outsideGraph G x).ConnectedComponent →
    Finset (outsideVertices G x)
  B : (outsideGraph G x).ConnectedComponent →
    Finset (outsideVertices G x)
  root_mem : ∀ c ∈ selection.C, selection.root c ∈ trunk c
  trunk_supported : ∀ c ∈ selection.C, (↑(trunk c) : Set _) ⊆ c.supp
  trunk_dominates : ∀ c ∈ selection.C, ∀ y, y ∈ c.supp →
    y ∈ trunk c ∨ ∃ z ∈ trunk c, (outsideGraph G x).Adj y z
  trunk_connected : ∀ c ∈ selection.C,
    (G.induce (↑(trunkVertices G x (trunk c)) : Set V)).Connected
  witness_supported : ∀ c, (↑(B c) : Set _) ⊆ c.supp
  witness_bipartite : ∀ c,
    ((outsideGraph G x).induce (↑(B c) : Set _)).IsBipartite
  card_le_sum : (correctedSelectedSet G x selection trunk).card ≤
    ∑ c ∈ correctedWitnessComponents G x selection, (B c).card

omit [Fintype V] in
lemma corrected_root_mem_trunkVertices (G : SimpleGraph V) (x : V)
    (A : CorrectedTrunkData G x) (c) (hc : c ∈ A.selection.C) :
    (A.selection.root c).1 ∈ trunkVertices G x (A.trunk c) := by
  exact Finset.mem_image.mpr ⟨A.selection.root c, A.root_mem c hc, rfl⟩

omit [Fintype V] in
/-- Each selected corrected branch is connected. -/
theorem corrected_attachmentBranch_connected (G : SimpleGraph V) (x : V)
    (A : CorrectedTrunkData G x) (c) (hc : c ∈ A.selection.C) :
    (G.induce (↑(attachmentBranch G x (A.selection.attach c)
      (A.trunk c)) : Set V)).Connected := by
  have hpair := connected_induce_union
    (A.trunk_connected c hc).preconnected
    (induce_singleton_connected G (A.selection.attach c)).preconnected
    (corrected_root_mem_trunkVertices G x A c hc)
    (Set.mem_singleton (A.selection.attach c))
    (A.selection.attach_adj_root c hc).symm
  have heq :
      (↑(attachmentBranch G x (A.selection.attach c) (A.trunk c)) : Set V) =
        (↑(trunkVertices G x (A.trunk c)) : Set V) ∪
          {A.selection.attach c} := by
    ext v
    simp [attachmentBranch]
  rw [heq]
  exact hpair

omit [Fintype V] in
/-- The corrected selected set dominates every ambient vertex. -/
theorem correctedSelectedSet_isDominating (G : SimpleGraph V) (x : V)
    (A : CorrectedTrunkData G x) :
    G.IsDominating (↑(correctedSelectedSet G x A.selection A.trunk) : Set V) := by
  intro v
  by_cases hvx : v = x
  · exact Or.inl (by simp [correctedSelectedSet, hvx])
  by_cases hxv : G.Adj x v
  · exact Or.inr ⟨x, by simp [correctedSelectedSet], hxv.symm⟩
  let y : outsideVertices G x := ⟨v, hxv⟩
  let c := (outsideGraph G x).connectedComponentMk y
  have hc : c ∈ A.selection.C := A.selection.covers y hvx
  rcases A.trunk_dominates c hc y ConnectedComponent.connectedComponentMk_mem with
    hyT | ⟨z, hzT, hyz⟩
  · exact Or.inl (by
      change v ∈ correctedSelectedSet G x A.selection A.trunk
      apply Finset.mem_insert.mpr
      right
      apply Finset.mem_biUnion.mpr
      exact ⟨c, hc, Finset.mem_insert_of_mem
        (Finset.mem_image.mpr ⟨y, hyT, rfl⟩)⟩)
  · exact Or.inr ⟨z.1, by
      change z.1 ∈ correctedSelectedSet G x A.selection A.trunk
      apply Finset.mem_insert.mpr
      right
      apply Finset.mem_biUnion.mpr
      exact ⟨c, hc, Finset.mem_insert_of_mem
        (Finset.mem_image.mpr ⟨z, hzT, rfl⟩)⟩, hyz⟩

omit [Fintype V] in
lemma correctedSelectedSet_connected_aux (G : SimpleGraph V) (x : V)
    (A : CorrectedTrunkData G x)
    (C : Finset (outsideGraph G x).ConnectedComponent)
    (hC : C ⊆ A.selection.C) :
    (G.induce (↑(insert x (C.biUnion fun c => attachmentBranch G x
      (A.selection.attach c) (A.trunk c))) : Set V)).Connected := by
  classical
  induction C using Finset.induction_on with
  | empty =>
      letI : Subsingleton (↥(↑({x} : Finset V) : Set V)) :=
        ⟨fun a b => Subtype.ext
          ((Finset.mem_singleton.mp a.property).trans
            (Finset.mem_singleton.mp b.property).symm)⟩
      simp only [Finset.biUnion_empty, Finset.insert_empty]
      rw [connected_iff]
      exact ⟨Preconnected.of_subsingleton, ⟨⟨x, by simp⟩⟩⟩
  | @insert c C hc ih =>
      have hcsel : c ∈ A.selection.C := hC (Finset.mem_insert_self c C)
      have hCsel : C ⊆ A.selection.C :=
        fun d hd => hC (Finset.mem_insert_of_mem hd)
      have hglue := connected_induce_union (ih hCsel).preconnected
        (corrected_attachmentBranch_connected G x A c hcsel).preconnected
        (show x ∈ (↑(insert x (C.biUnion fun d => attachmentBranch G x
          (A.selection.attach d) (A.trunk d))) : Set V) by simp)
        (show A.selection.attach c ∈
          (↑(attachmentBranch G x (A.selection.attach c) (A.trunk c)) : Set V) by
            simp [attachmentBranch])
        (A.selection.attach_adj_x c hcsel)
      have heq :
          (↑(insert x ((insert c C).biUnion fun d => attachmentBranch G x
            (A.selection.attach d) (A.trunk d))) : Set V) =
          (↑(insert x (C.biUnion fun d => attachmentBranch G x
            (A.selection.attach d) (A.trunk d))) : Set V) ∪
          (↑(attachmentBranch G x (A.selection.attach c)
            (A.trunk c)) : Set V) := by
        ext v
        simp [Finset.biUnion_insert]
        aesop
      rw [heq]
      exact hglue

omit [Fintype V] in
theorem correctedSelectedSet_isConnectedDominating
    (G : SimpleGraph V) (x : V) (A : CorrectedTrunkData G x) :
    G.IsConnectedDominating
      (↑(correctedSelectedSet G x A.selection A.trunk) : Set V) := by
  exact ⟨correctedSelectedSet_isDominating G x A,
    correctedSelectedSet_connected_aux G x A A.selection.C (by rfl)⟩

omit [Fintype V] [DecidableEq V] in
/-- The claw-free attachment-injectivity theorem now has exactly the corrected
selected-component hypotheses. -/
theorem corrected_attach_injective
    (G : SimpleGraph V) (x : V) (hclaw : IsClawFree G)
    (S : SelectedAttachmentData G x) {c d}
    (hc : c ∈ S.C) (hd : d ∈ S.C)
    (hattach : S.attach c = S.attach d) : c = d := by
  by_contra hcd
  have hpd : G.Adj (S.attach c) (S.root d).1 := by
    rw [hattach]
    exact S.attach_adj_root d hd
  have huv : (S.root c).1 ≠ (S.root d).1 := by
    intro huv
    apply hcd
    have huvsub : S.root c = S.root d := Subtype.ext huv
    have hrdc : S.root c ∈ d.supp := by
      rw [huvsub]
      exact S.root_supported d hd
    exact ConnectedComponent.eq_of_common_vertex (S.root_supported c hc) hrdc
  rcases hclaw (S.attach_adj_x c hc).symm (S.attach_adj_root c hc) hpd
      (S.root_ne_x c hc).symm (S.root_ne_x d hd).symm huv with hxr | hxr | hrr
  · exact (S.root c).property hxr
  · exact (S.root d).property hxr
  · apply hcd
    have hcomp := ConnectedComponent.connectedComponentMk_eq_of_adj
      (G := outsideGraph G x) hrr
    have hrc := (ConnectedComponent.mem_supp_iff c (S.root c)).mp
      (S.root_supported c hc)
    have hrd := (ConnectedComponent.mem_supp_iff d (S.root d)).mp
      (S.root_supported d hd)
    exact hrc.symm.trans (hcomp.trans hrd)

omit [Fintype V] in
theorem corrected_attachment_image_card
    (G : SimpleGraph V) (x : V) (hclaw : IsClawFree G)
    (S : SelectedAttachmentData G x) :
    (S.C.image S.attach).card = S.C.card := by
  rw [Finset.card_image_iff]
  intro c hc d hd h
  exact corrected_attach_injective G x hclaw S hc hd h

omit [Fintype V] in
/-- The selected ambient set costs at most `x`, one attachment per component,
and the sum of the trunk orders.  No disjointness hypothesis is needed for this
upper bound. -/
theorem correctedSelectedSet_card_le (G : SimpleGraph V) (x : V)
    (S : SelectedAttachmentData G x)
    (T : (outsideGraph G x).ConnectedComponent →
      Finset (outsideVertices G x)) :
    (correctedSelectedSet G x S T).card ≤
      1 + ∑ c ∈ S.C, ((T c).card + 1) := by
  classical
  calc
    (correctedSelectedSet G x S T).card ≤
        1 + (S.C.biUnion fun c => attachmentBranch G x (S.attach c) (T c)).card := by
      unfold correctedSelectedSet
      exact (Finset.card_insert_le _ _).trans_eq (by omega)
    _ ≤ 1 + ∑ c ∈ S.C, (attachmentBranch G x (S.attach c) (T c)).card := by
      exact Nat.add_le_add_left Finset.card_biUnion_le 1
    _ ≤ 1 + ∑ c ∈ S.C, ((T c).card + 1) := by
      gcongr with c hc
      unfold attachmentBranch trunkVertices
      calc
        #(insert (S.attach c) (Finset.image Subtype.val (T c))) ≤
            1 + #(Finset.image Subtype.val (T c)) := by
          simpa [Nat.add_comm] using
            (Finset.card_insert_le (S.attach c) (Finset.image Subtype.val (T c)))
        _ ≤ 1 + #(T c) := Nat.add_le_add_left Finset.card_image_le 1
        _ = #(T c) + 1 := by omega

omit [Fintype V] in
/-- The root component's one-unit witness pays for the global vertex `x`,
while every selected component's local `|T|+1` budget pays for its trunk and
attachment.  This discharges the entire aggregate cardinality inequality. -/
theorem corrected_card_le_sum_of_local_budgets (G : SimpleGraph V) (x : V)
    (S : SelectedAttachmentData G x)
    (T B : (outsideGraph G x).ConnectedComponent →
      Finset (outsideVertices G x))
    (hlocal : ∀ c ∈ S.C, (T c).card + 1 ≤ (B c).card)
    (hroot : 1 ≤ (B (rootOutsideComponent G x)).card) :
    (correctedSelectedSet G x S T).card ≤
      ∑ c ∈ correctedWitnessComponents G x S, (B c).card := by
  classical
  have htrunks : ∑ c ∈ S.C, ((T c).card + 1) ≤
      ∑ c ∈ S.C, (B c).card := by
    exact sum_le_sum fun c hc => hlocal c hc
  have hnot : rootOutsideComponent G x ∉ S.C := S.excludes_root
  unfold correctedWitnessComponents
  rw [Finset.sum_insert hnot]
  exact (correctedSelectedSet_card_le G x S T).trans (by omega)

/-- Clean local construction interface.  Unlike `CorrectedTrunkData`, this
structure asks only for component-local trunk and witness facts.  Its two
numerical fields are precisely the local non-root budgets and the one-unit
root witness; the aggregate inequality is derived below. -/
structure LocalCorrectedTrunkData (G : SimpleGraph V) (x : V) where
  selection : SelectedAttachmentData G x
  trunk : (outsideGraph G x).ConnectedComponent →
    Finset (outsideVertices G x)
  B : (outsideGraph G x).ConnectedComponent →
    Finset (outsideVertices G x)
  root_mem : ∀ c ∈ selection.C, selection.root c ∈ trunk c
  trunk_supported : ∀ c ∈ selection.C, (↑(trunk c) : Set _) ⊆ c.supp
  trunk_dominates : ∀ c ∈ selection.C, ∀ y, y ∈ c.supp →
    y ∈ trunk c ∨ ∃ z ∈ trunk c, (outsideGraph G x).Adj y z
  trunk_connected : ∀ c ∈ selection.C,
    (G.induce (↑(trunkVertices G x (trunk c)) : Set V)).Connected
  witness_supported : ∀ c, (↑(B c) : Set _) ⊆ c.supp
  witness_bipartite : ∀ c,
    ((outsideGraph G x).induce (↑(B c) : Set _)).IsBipartite
  local_budget : ∀ c ∈ selection.C, (trunk c).card + 1 ≤ (B c).card
  root_budget : 1 ≤ (B (rootOutsideComponent G x)).card

/-- The aggregate `card_le_sum` field is a theorem of the local budgets, not a
caller-supplied global premise. -/
noncomputable def correctedTrunkDataOfLocal (G : SimpleGraph V) (x : V)
    (A : LocalCorrectedTrunkData G x) : CorrectedTrunkData G x where
  selection := A.selection
  trunk := A.trunk
  B := A.B
  root_mem := A.root_mem
  trunk_supported := A.trunk_supported
  trunk_dominates := A.trunk_dominates
  trunk_connected := A.trunk_connected
  witness_supported := A.witness_supported
  witness_bipartite := A.witness_bipartite
  card_le_sum := corrected_card_le_sum_of_local_budgets G x A.selection
    A.trunk A.B A.local_budget A.root_budget

/-- The corrected fold now constructs the exact outside certificate, with no
impossible root-component attachment premise. -/
noncomputable def correctedComponentFoldInput (G : SimpleGraph V) (x : V)
    (A : CorrectedTrunkData G x) : ComponentFoldInput G x where
  D := correctedSelectedSet G x A.selection A.trunk
  C := correctedWitnessComponents G x A.selection
  B := A.B
  supported := A.witness_supported
  bipartite := A.witness_bipartite
  dominating := correctedSelectedSet_isConnectedDominating G x A
  card_le_sum := A.card_le_sum

noncomputable def outsideBudgetCertificate_of_correctedTrunks (G : SimpleGraph V) (x : V)
    (A : CorrectedTrunkData G x) : OutsideBudgetCertificate G x :=
  outsideBudgetCertificate_of_componentFoldInput G x
    (correctedComponentFoldInput G x A)

/-- End-to-end certificate constructor from component-local facts only. -/
noncomputable def outsideBudgetCertificate_of_localCorrectedTrunks
    (G : SimpleGraph V) (x : V) (A : LocalCorrectedTrunkData G x) :
    OutsideBudgetCertificate G x :=
  outsideBudgetCertificate_of_correctedTrunks G x
    (correctedTrunkDataOfLocal G x A)

end WrittenOnTheWallII.GraphConjecture183CorrectedFold
