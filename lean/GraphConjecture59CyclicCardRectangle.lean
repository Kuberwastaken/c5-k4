import GraphConjecture59CoreProfileMultiplicity
import Mathlib.Combinatorics.SimpleGraph.ConcreteColorings

/-!
# WOWII 59: cyclic bipartite five-cards contain rectangles

This file bridges Mathlib's abstract cycle predicate to the `K₂,₂`
rectangle coordinates used by the exact `3+3` core-profile classifier.
-/

namespace WrittenOnTheWallII.GraphConjecture59CyclicCardRectangle

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture59CornerStructure

universe u
variable {V : Type u}

/-- Pairwise distinctness of four named vertices. -/
def PairwiseDistinctFour (a b c d : V) : Prop :=
  a ≠ b ∧ a ≠ c ∧ a ≠ d ∧ b ≠ c ∧ b ≠ d ∧ c ≠ d

/-- A cyclic bipartite graph on five vertices contains an explicit four-cycle.
The cycle length is at most five, at least three, and even, hence exactly
four. -/
theorem exists_four_cycle_of_bipartite_card_five
    [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) (hcard : Fintype.card V = 5)
    (hbip : G.IsBipartite) (hcyclic : ¬G.IsAcyclic) :
    ∃ a b c d, PairwiseDistinctFour a b c d ∧
      G.Adj a b ∧ G.Adj b c ∧ G.Adj c d ∧ G.Adj d a := by
  simp only [IsAcyclic] at hcyclic
  push_neg at hcyclic
  obtain ⟨v, p, hp⟩ := hcyclic
  have hpcons := hp
  rw [← p.cons_tail_eq hp.not_nil] at hpcons
  have hpath := (Walk.cons_isCycle_iff p.tail _).mp hpcons |>.1
  have hlt := hpath.length_lt
  have htail := Walk.length_tail_add_one hp.not_nil
  have hupper : p.length ≤ 5 := by omega
  have hlower := hp.three_le_length
  have heven := (two_colorable_iff_forall_loop_even.mp hbip) v p
  obtain ⟨k, hk⟩ := heven
  have hlen : p.length = 4 := by omega
  let a := p.getVert 0
  let b := p.getVert 1
  let c := p.getVert 2
  let d := p.getVert 3
  have hinj := hp.getVert_injOn'
  have habv : a ≠ b := by
    intro h
    have := hinj (by simp [hlen]) (by simp [hlen]) h
    omega
  have hacv : a ≠ c := by
    intro h
    have := hinj (by simp [hlen]) (by simp [hlen]) h
    omega
  have hadv : a ≠ d := by
    intro h
    have := hinj (by simp [hlen]) (by simp [hlen]) h
    omega
  have hbcv : b ≠ c := by
    intro h
    have := hinj (by simp [hlen]) (by simp [hlen]) h
    omega
  have hbdv : b ≠ d := by
    intro h
    have := hinj (by simp [hlen]) (by simp [hlen]) h
    omega
  have hcdv : c ≠ d := by
    intro h
    have := hinj (by simp [hlen]) (by simp [hlen]) h
    omega
  have hab : G.Adj a b := p.adj_getVert_succ (by omega)
  have hbc : G.Adj b c := p.adj_getVert_succ (by omega)
  have hcd : G.Adj c d := p.adj_getVert_succ (by omega)
  have hda0 := p.adj_getVert_succ (i := 3) (by omega)
  have hda : G.Adj d a := by
    have h4 : p.getVert 4 = v := by
      rw [← hlen]
      exact p.getVert_length
    have h0 : p.getVert 0 = v := p.getVert_zero
    simpa [a, d, h4, h0] using hda0
  exact ⟨a, b, c, d, ⟨habv, hacv, hadv, hbcv, hbdv, hcdv⟩,
    hab, hbc, hcd, hda⟩

/-- With a fixed bipartition, the four-cycle alternates between its sides and
therefore becomes two vertices with two distinct common neighbors: a
`K₂,₂` rectangle. -/
theorem exists_rectangle_of_bipartiteWith_card_five
    [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) (I X : Set V)
    (hcard : Fintype.card V = 5)
    (hbw : G.IsBipartiteWith I X) (hcyclic : ¬G.IsAcyclic) :
    ∃ i₁ i₂ x₁ x₂,
      i₁ ∈ I ∧ i₂ ∈ I ∧ x₁ ∈ X ∧ x₂ ∈ X ∧
      i₁ ≠ i₂ ∧ x₁ ≠ x₂ ∧
      G.Adj i₁ x₁ ∧ G.Adj i₁ x₂ ∧
      G.Adj i₂ x₁ ∧ G.Adj i₂ x₂ := by
  obtain ⟨a, b, c, d, hdist, hab, hbc, hcd, hda⟩ :=
    exists_four_cycle_of_bipartite_card_five
      G hcard hbw.isBipartite hcyclic
  have haSupport : a ∈ G.support := (G.mem_support).2 ⟨b, hab⟩
  have haSide := isBipartiteWith_support_subset hbw haSupport
  rcases haSide with haI | haX
  · have hbX := hbw.mem_of_mem_adj haI hab
    have hcI := hbw.mem_of_mem_adj' hbX hbc.symm
    have hdX := hbw.mem_of_mem_adj hcI hcd
    exact ⟨a, c, b, d, haI, hcI, hbX, hdX, hdist.2.1,
      hdist.2.2.2.2.1, hab, hda.symm, hbc.symm, hcd⟩
  · have hbI := hbw.mem_of_mem_adj' haX hab.symm
    have hcX := hbw.mem_of_mem_adj hbI hbc
    have hdI := hbw.mem_of_mem_adj' hcX hcd.symm
    exact ⟨b, d, a, c, hbI, hdI, haX, hcX, hdist.2.2.2.2.1,
      hdist.2.1, hab.symm, hbc, hda, hcd.symm⟩

/-- **Composition with the exact WOWII #59 corner.** If `S` is a bipartite
six-core and the global induced-forest number is four, deleting any core
vertex leaves four distinct vertices spanning a `K₂,₂`.  This is exactly
the rectangle premise consumed by the v26 `3+3` profile classifier after the
two color classes are labeled by `Fin 3`. -/
theorem corner_deletion_contains_rectangle
    [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) (S : Finset V)
    (hSbip : (G.induce (S : Set V)).IsBipartite)
    (hSsix : S.card = 6)
    (hf : G.largestInducedForestSize = 4)
    {z : V} (hz : z ∈ S) :
    ∃ a b c d,
      a ∈ S.erase z ∧ b ∈ S.erase z ∧
      c ∈ S.erase z ∧ d ∈ S.erase z ∧
      PairwiseDistinctFour a b c d ∧
      G.Adj a c ∧ G.Adj a d ∧ G.Adj b c ∧ G.Adj b d := by
  have hcardData := every_single_deletion_bipartite_and_cyclic
    G S hSbip hSsix hf hz
  let T := S.erase z
  let H := G.induce (T : Set V)
  have hTcard : T.card = 5 := by
    simp [T, card_erase_of_mem hz, hSsix]
  have htypecard : Fintype.card {v // v ∈ T} = 5 := by
    simpa using hTcard
  have hHbip : H.IsBipartite := by
    simpa [H, T] using hcardData.1
  have hHcyclic : ¬H.IsAcyclic := by
    simpa [H, T] using hcardData.2
  obtain ⟨I, X, hbw⟩ := hHbip.exists_isBipartiteWith
  obtain ⟨a, b, c, d, haI, hbI, hcX, hdX, habv, hcdv,
      hac, had, hbc, hbd⟩ :=
    exists_rectangle_of_bipartiteWith_card_five
      H I X htypecard hbw hHcyclic
  have hdist : PairwiseDistinctFour a b c d :=
    ⟨habv, hac.ne, had.ne, hbc.ne, hbd.ne, hcdv⟩
  have hdistV : PairwiseDistinctFour (a : V) b c d := by
    simpa [PairwiseDistinctFour] using hdist
  exact ⟨a, b, c, d, a.property, b.property, c.property, d.property,
    hdistV, hac, had, hbc, hbd⟩

end WrittenOnTheWallII.GraphConjecture59CyclicCardRectangle
