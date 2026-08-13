import FormalConjecturesUtil

/-!
# WOWII 61: graphical degree-transfer boundary

This file carries degree-sequence graphicality by an explicit finite simple
graph realization.  It deliberately does not claim the still-missing general
residue monotonicity theorem.
-/

namespace WrittenOnTheWallII.GraphConjecture61GraphicalTransfer

open SimpleGraph

/-- The descending degree list of an explicitly decidable graph on `Fin n`.
The decidability witness is explicit so concrete realizations can be evaluated
without appealing to a merely numerical graphicality test. -/
def descendingDegreeList {n : ℕ} (G : SimpleGraph (Fin n))
    [DecidableRel G.Adj] : List ℕ :=
  (Finset.univ.val.map fun v ↦ G.degree v).sort (· ≥ ·)

/-- A list is graphical only when accompanied by an actual finite simple graph
whose complete descending degree list is exactly that list. -/
def IsGraphical (s : List ℕ) : Prop :=
  ∃ n : ℕ, ∃ G : SimpleGraph (Fin n), ∃ h : DecidableRel G.Adj,
    @descendingDegreeList n G h = s

/-- One nontrivial balancing transfer followed by descending re-sorting. -/
def DescendingUnitTransfer (s t : List ℕ) : Prop :=
  s.Pairwise (· ≥ ·) ∧
  ∃ pre middle post : List ℕ, ∃ a b : ℕ,
    s = pre ++ a :: middle ++ b :: post ∧
    b + 2 ≤ a ∧
    t = (pre ++ (a - 1) :: middle ++ (b + 1) :: post).mergeSort (· ≥ ·)

/-- The exact relation required by the next residue theorem: both endpoints
are carried by explicit graph realizations, not inferred graphical from their
entries. -/
def GraphicalUnitTransfer (s t : List ℕ) : Prop :=
  IsGraphical s ∧ IsGraphical t ∧ DescendingUnitTransfer s t

/-- The realization predicate fixes the list length to the order of its
witness graph. -/
theorem IsGraphical.exists_order_eq_length {s : List ℕ} (hs : IsGraphical s) :
    ∃ n : ℕ, n = s.length := by
  obtain ⟨n, G, h, rfl⟩ := hs
  refine ⟨n, ?_⟩
  simp [descendingDegreeList]

/-- A realized list is genuinely descending. -/
theorem IsGraphical.pairwise_ge {s : List ℕ} (hs : IsGraphical s) :
    s.Pairwise (· ≥ ·) := by
  obtain ⟨n, G, h, hseq⟩ := hs
  rw [← hseq]
  exact Multiset.pairwise_sort _ _

/-- Every entry of a realized degree list is strictly smaller than the list
length.  This is derived from the witness graph, not used as a replacement for
graphicality. -/
theorem IsGraphical.mem_lt_length {s : List ℕ} (hs : IsGraphical s)
    {d : ℕ} (hd : d ∈ s) : d < s.length := by
  obtain ⟨n, G, h, hseq⟩ := hs
  letI : DecidableRel G.Adj := h
  have hd' : d ∈ descendingDegreeList G := by simpa [hseq] using hd
  have hv : ∃ v : Fin n, G.degree v = d := by
    simpa [descendingDegreeList, eq_comm] using hd'
  obtain ⟨v, rfl⟩ := hv
  have hlen := congrArg List.length hseq
  simp [descendingDegreeList] at hlen
  simpa [hlen] using G.degree_lt_card_verts v

/-- The degree sum of every explicitly realized sequence is twice an edge
count. -/
theorem IsGraphical.sum_eq_twice {s : List ℕ} (hs : IsGraphical s) :
    ∃ m : ℕ, s.sum = 2 * m := by
  obtain ⟨n, G, h, hseq⟩ := hs
  letI : DecidableRel G.Adj := h
  refine ⟨G.edgeFinset.card, ?_⟩
  rw [← hseq]
  have hdegrees :
      (descendingDegreeList G).sum =
        (Finset.univ.val.map fun v ↦ G.degree v).sum := by
    have heq :
        (↑((Finset.univ.val.map fun v ↦ G.degree v).sort (· ≥ ·)) : Multiset ℕ) =
          Finset.univ.val.map fun v ↦ G.degree v := by
      exact Multiset.sort_eq _ _
    have hsum := congrArg Multiset.sum heq
    simpa [descendingDegreeList] using hsum
  rw [hdegrees]
  change (∑ v, G.degree v) = 2 * G.edgeFinset.card
  exact G.sum_degrees_eq_twice_card_edges

/-- The path on three vertices realizes `[2,1,1]`. -/
theorem graphical_two_one_one : IsGraphical [2, 1, 1] := by
  let h : DecidableRel (pathGraph 3).Adj := fun u v ↦
    decidable_of_iff (u.val + 1 = v.val ∨ v.val + 1 = u.val) pathGraph_adj.symm
  refine ⟨3, pathGraph 3, h, ?_⟩
  native_decide

/-- A concrete `P₃` plus one isolated vertex, used to expose the first
nonvacuous graphical transfer. -/
def pathThreeWithIsolated : SimpleGraph (Fin 4) :=
  SimpleGraph.fromRel fun u v ↦
    (u.val = 0 ∧ v.val = 1) ∨ (u.val = 1 ∧ v.val = 2)

instance pathThreeWithIsolated_decidableAdj :
    DecidableRel pathThreeWithIsolated.Adj := by
  unfold pathThreeWithIsolated
  infer_instance

/-- A concrete perfect matching on four vertices. -/
def matchingFour : SimpleGraph (Fin 4) :=
  SimpleGraph.fromRel fun u v ↦
    (u.val = 0 ∧ v.val = 1) ∨ (u.val = 2 ∧ v.val = 3)

instance matchingFour_decidableAdj : DecidableRel matchingFour.Adj := by
  unfold matchingFour
  infer_instance

theorem graphical_two_one_one_zero : IsGraphical [2, 1, 1, 0] := by
  refine ⟨4, pathThreeWithIsolated, inferInstance, ?_⟩
  native_decide

theorem graphical_one_one_one_one : IsGraphical [1, 1, 1, 1] := by
  refine ⟨4, matchingFour, inferInstance, ?_⟩
  native_decide

/-- The first nonvacuous graphical transfer: balancing the degree-two and
degree-zero entries turns `P₃ ⊎ K₁` into the degree sequence of `2K₂`. -/
theorem first_graphicalUnitTransfer :
    GraphicalUnitTransfer [2, 1, 1, 0] [1, 1, 1, 1] := by
  refine ⟨graphical_two_one_one_zero, graphical_one_one_one_one, by simp,
    [], [1, 1], [], 2, 0, ?_, by decide, ?_⟩
  · decide
  · native_decide

/-- The desired residue direction holds on that first transfer. -/
theorem first_graphicalUnitTransfer_residue :
    residueAux [1, 1, 1, 1] ≤ residueAux [2, 1, 1, 0] := by
  native_decide

/-- However, its two canonical successors have different degree sums.  A
naive induction cannot simply reapply equal-sum majorization after one
Havel--Hakimi step. -/
theorem first_graphicalUnitTransfer_successors :
    havelHakimiStep [2, 1, 1, 0] = [0, 0, 0] ∧
    havelHakimiStep [1, 1, 1, 1] = [1, 1, 0] ∧
    (havelHakimiStep [2, 1, 1, 0]).sum ≠
      (havelHakimiStep [1, 1, 1, 1]).sum := by
  native_decide

/-- A realized three-vertex degree list cannot contain both zero and two: a
degree-two vertex would have to be adjacent to the degree-zero vertex. -/
theorem IsGraphical.not_mem_zero_and_two_of_length_eq_three
    {s : List ℕ} (hs : IsGraphical s) (hlen_s : s.length = 3)
    (hzero_s : 0 ∈ s) (htwo_s : 2 ∈ s) : False := by
  obtain ⟨n, G, h, hseq⟩ := hs
  have hn : n = 3 := by
    have hlen := congrArg List.length hseq
    simp [descendingDegreeList] at hlen
    omega
  subst n
  letI : DecidableRel G.Adj := h
  have hzero_mem : 0 ∈ descendingDegreeList G := by
    rw [hseq]
    exact hzero_s
  have htwo_mem : 2 ∈ descendingDegreeList G := by
    rw [hseq]
    exact htwo_s
  have hzero : ∃ v : Fin 3, G.degree v = 0 := by
    have hz : 0 = G.degree 0 ∨ 0 = G.degree 1 ∨ 0 = G.degree 2 := by
      simpa [descendingDegreeList] using hzero_mem
    rcases hz with hz | hz | hz
    · exact ⟨0, hz.symm⟩
    · exact ⟨1, hz.symm⟩
    · exact ⟨2, hz.symm⟩
  have htwo : ∃ u : Fin 3, G.degree u = 2 := by
    have ht : 2 = G.degree 0 ∨ 2 = G.degree 1 ∨ 2 = G.degree 2 := by
      simpa [descendingDegreeList] using htwo_mem
    rcases ht with ht | ht | ht
    · exact ⟨0, ht.symm⟩
    · exact ⟨1, ht.symm⟩
    · exact ⟨2, ht.symm⟩
  obtain ⟨v, hv⟩ := hzero
  obtain ⟨u, hu⟩ := htwo
  have huv : u ≠ v := by
    intro huv
    subst v
    omega
  have hnotAdj : ¬ G.Adj u v := by
    intro hadj
    have humem : u ∈ G.neighborFinset v :=
      (G.mem_neighborFinset v u).2 hadj.symm
    have hempty : G.neighborFinset v = ∅ := by
      apply Finset.card_eq_zero.mp
      exact hv
    rw [hempty] at humem
    simp at humem
  have hsub : G.neighborFinset u ⊆ (Finset.univ.erase u).erase v := by
    intro w hw
    have hadj : G.Adj u w := (G.mem_neighborFinset u w).1 hw
    simp only [Finset.mem_erase, Finset.mem_univ, and_true]
    constructor
    · intro hwv
      subst w
      exact hnotAdj hadj
    · exact hadj.ne.symm
  have hcard_target : ((Finset.univ.erase u).erase v).card = 1 := by
    have hv_mem : v ∈ Finset.univ.erase u := by simp [huv.symm]
    rw [Finset.card_erase_of_mem hv_mem]
    rw [Finset.card_erase_of_mem (Finset.mem_univ u)]
    simp
  have hcard_source : (G.neighborFinset u).card = 2 := by
    exact hu
  have hle := Finset.card_le_card hsub
  rw [hcard_source, hcard_target] at hle
  omega

/-- The unrestricted length-three residue counterexample is excluded by the
realization-aware predicate: `[2,2,0]` is not a simple-graph degree list. -/
theorem not_graphical_two_two_zero : ¬ IsGraphical [2, 2, 0] := by
  intro hs
  exact hs.not_mem_zero_and_two_of_length_eq_three (by decide) (by simp) (by simp)

/-- Therefore the old unrestricted counterexample is not a graphical atomic
transfer, even though its target is realized by `pathGraph 3`. -/
theorem not_graphicalUnitTransfer_old_counterexample :
    ¬ GraphicalUnitTransfer [2, 2, 0] [2, 1, 1] := by
  intro h
  exact not_graphical_two_two_zero h.1

/-- No nontrivial graphical balancing transfer exists on at most three
vertices.  The gap forces entries `2` and `0`; the degree bound forces length
three; and the realization lemma then rules that pair out. -/
theorem not_graphicalUnitTransfer_of_length_le_three
    {s t : List ℕ} (hst : GraphicalUnitTransfer s t)
    (hlen : s.length ≤ 3) : False := by
  rcases hst with ⟨hs, _ht, _hdescending,
    pre, middle, post, a, b, hs_decomp, hgap, _ht_decomp⟩
  have ha_mem : a ∈ s := by
    rw [hs_decomp]
    simp
  have hb_mem : b ∈ s := by
    rw [hs_decomp]
    simp
  have ha_lt := hs.mem_lt_length ha_mem
  have hb_lt := hs.mem_lt_length hb_mem
  have ha : a = 2 := by omega
  have hb : b = 0 := by omega
  have hlen_eq : s.length = 3 := by omega
  subst a
  subst b
  exact hs.not_mem_zero_and_two_of_length_eq_three hlen_eq hb_mem ha_mem

/-- Hence the desired residue direction is formally valid through order three
(vacuously: there is no graphical atomic transfer in that range). -/
theorem residueAux_monotone_graphicalUnitTransfer_length_le_three
    {s t : List ℕ} (hst : GraphicalUnitTransfer s t)
    (hlen : s.length ≤ 3) : residueAux t ≤ residueAux s := by
  exact (not_graphicalUnitTransfer_of_length_le_three hst hlen).elim

/-- The exact unresolved proposition after carrying both realizations.  It is
named as data rather than asserted as a theorem. -/
def GraphicalTransferResidueMonotone : Prop :=
  ∀ s t : List ℕ, GraphicalUnitTransfer s t → residueAux t ≤ residueAux s

/-- Interface exposing precisely what the missing proposition would supply. -/
theorem residueAux_le_of_graphicalUnitTransfer
    (hmono : GraphicalTransferResidueMonotone)
    {s t : List ℕ} (hst : GraphicalUnitTransfer s t) :
    residueAux t ≤ residueAux s :=
  hmono s t hst

end WrittenOnTheWallII.GraphConjecture61GraphicalTransfer
