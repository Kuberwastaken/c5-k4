import GraphConjecture133HandleExistence

/-!
# WOWII 133: early-escape counting at depth two

In a C4-free graph, a fixed outside vertex can meet at most one member of a
star's leaf set.  A four-regular geodesic head has three off-direction
neighbors, so two early geodesic targets cannot block all three.
-/

namespace WrittenOnTheWallII.GraphConjecture133EarlyEscapeCombinatorics

open SimpleGraph
open WrittenOnTheWallII.GraphConjecture133Cubic

variable {V : Type*} [Fintype V] [DecidableEq V] [Nonempty V]

omit [Nonempty V] in
/-- Among neighbors of `c` other than `u`, at most one can also be adjacent
to a fixed distinct vertex `x`; two such vertices would form the four-cycle
`c-a-x-b-c`. -/
theorem card_common_forward_neighbors_le_one (G : SimpleGraph V)
    [DecidableRel G.Adj] (hc4 : ¬HasC4 G) {c u x : V} (hcx : c ≠ x) :
    (((G.neighborFinset c).erase u).filter (fun a ↦ G.Adj a x)).card ≤ 1 := by
  classical
  apply Finset.card_le_one.mpr
  intro a ha b hb
  simp only [Finset.mem_filter] at ha hb
  have hac : G.Adj a c := by
    simpa [adj_comm] using Finset.mem_of_mem_erase ha.1
  have hbc : G.Adj b c := by
    simpa [adj_comm] using Finset.mem_of_mem_erase hb.1
  by_contra hab
  apply hc4
  refine ⟨c, a, x, b, ?_, ?_, ?_, ?_, ?_, ?_, hac.symm, ha.2, hb.2.symm, hbc⟩
  · exact hac.ne.symm
  · exact hcx
  · exact hbc.ne.symm
  · exact ha.2.ne
  · exact hab
  · exact hb.2.ne.symm

omit [Nonempty V] in
/-- Three forward neighbors cannot all be covered by the two single-contact
sets belonging to targets `y` and `z`. -/
theorem exists_forward_neighbor_avoiding_two_targets
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hc4 : ¬HasC4 G) (hreg : G.IsRegularOfDegree 4)
    {c u y z : V} (huc : G.Adj u c) (hcy : c ≠ y) (hcz : c ≠ z) :
    ∃ b : V, G.Adj b c ∧ b ≠ u ∧ ¬G.Adj b y ∧ ¬G.Adj b z := by
  classical
  let s := (G.neighborFinset c).erase u
  let sy := s.filter (fun b ↦ G.Adj b y)
  let sz := s.filter (fun b ↦ G.Adj b z)
  have hucmem : u ∈ G.neighborFinset c := by simpa [adj_comm] using huc
  have hscard : s.card = 3 := by
    simp only [s]
    rw [Finset.card_erase_of_mem hucmem, G.card_neighborFinset_eq_degree, hreg c]
  have hsy : sy.card ≤ 1 := by
    simpa [sy, s] using card_common_forward_neighbors_le_one G hc4 hcy
  have hsz : sz.card ≤ 1 := by
    simpa [sz, s] using card_common_forward_neighbors_le_one G hc4 hcz
  have hunion : (sy ∪ sz).card ≤ 2 := by
    calc
      (sy ∪ sz).card ≤ sy.card + sz.card := Finset.card_union_le sy sz
      _ ≤ 2 := by omega
  have hnsub : ¬s ⊆ sy ∪ sz := by
    intro hsub
    have := Finset.card_le_card hsub
    omega
  obtain ⟨b, hbS, hb⟩ := Finset.not_subset.mp hnsub
  have hby : ¬G.Adj b y := by
    intro h
    exact hb (Finset.mem_union_left sz (by simp [sy, hbS, h]))
  have hbz : ¬G.Adj b z := by
    intro h
    exact hb (Finset.mem_union_right sy (by simp [sz, hbS, h]))
  exact ⟨b, by simpa [s, adj_comm] using Finset.mem_of_mem_erase hbS,
    Finset.ne_of_mem_erase hbS, hby, hbz⟩

omit [Nonempty V] in
/-- Applied to a geodesic, C4-freeness guarantees a depth-two continuation
that avoids exactly the two genuinely unresolved contacts `x₂` and `x₃`.
The contact with `x₁` is then excluded by the same four-cycle condition. -/
theorem exists_depthTwo_avoiding_first_three
    (G : SimpleGraph V) [DecidableRel G.Adj] {u v c : V}
    (p : G.Walk u v) (hlen : 3 ≤ p.length)
    (hreg : G.IsRegularOfDegree 4) (hc4 : ¬HasC4 G)
    (hcu : G.Adj c u) (hcfresh : c ∉ p.support)
    (_hclean : ∀ x ∈ p.support.tail, ¬G.Adj c x) :
    ∃ b : V, G.Adj b c ∧ b ≠ u ∧
      ∀ k, 1 ≤ k → k ≤ 3 → ¬G.Adj b (p.getVert k) := by
  have hcx2 : c ≠ p.getVert 2 := by
    intro h
    subst c
    exact hcfresh (p.getVert_mem_support 2)
  have hcx3 : c ≠ p.getVert 3 := by
    intro h
    subst c
    exact hcfresh (p.getVert_mem_support 3)
  obtain ⟨b, hbc, hbu, hbx2, hbx3⟩ :=
    exists_forward_neighbor_avoiding_two_targets
      G hc4 hreg hcu.symm hcx2 hcx3
  refine ⟨b, hbc, hbu, ?_⟩
  intro k hk1 hk3
  interval_cases k
  · intro hbx1
    apply hc4
    have hux1 : G.Adj u (p.getVert 1) := by
      simpa using p.adj_getVert_succ (by omega : 0 < p.length)
    refine ⟨u, c, b, p.getVert 1, ?_, ?_, ?_, ?_, ?_, ?_,
      hcu.symm, hbc.symm, hbx1, hux1.symm⟩
    · exact hcu.ne.symm
    · exact hbu.symm
    · exact hux1.ne
    · exact hbc.ne.symm
    · intro heq
      exact hcfresh (by rw [heq]; exact p.getVert_mem_support 1)
    · exact hbx1.ne
  · exact hbx2
  · exact hbx3

end WrittenOnTheWallII.GraphConjecture133EarlyEscapeCombinatorics
