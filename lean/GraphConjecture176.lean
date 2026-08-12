/-
Copyright 2026 The Formal Conjectures Authors.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
-/

import FormalConjecturesUtil
import FormalConjecturesForMathlib.Combinatorics.SimpleGraph.Induced

/-!
# Written on the Wall II - Conjecture 176

*Reference:*
[E. DeLaVina, Written on the Wall II, Conjectures of Graffiti.pc](http://cms.dt.uh.edu/faculty/delavinae/research/wowII/)

The source-faithful reading is

`Ls(G) + b(G) ≥ |V(G)| + distMin_G(M(G²))`,

where `M(G²)` is the set of maximum-degree vertices of the square, but the
distance between those selected vertices is measured back in `G`.

The counterexample `D₇` consists of two triangles whose distinguished vertices
are joined by a path of seven edges. It has 12 vertices, `Ls ≤ 4`, `b = 10`,
and `M(D₇²) = {1, 6}`, whose vertices are distance 5 in `D₇`. Thus the
proposed inequality says `14 ≥ 17`.

Because the current `Ls` and `b` library definitions use noncomputable
suprema, the executable certificate packages their finite maximality
predicates. No unproved axiom or `sorry` is used.
-/

namespace WrittenOnTheWallII.GraphConjecture176

open SimpleGraph Finset

open scoped Classical in
noncomputable section

/-- A spanning subgraph tree remains a tree after transporting it back to the
ambient vertex type. -/
lemma spanningCoe_isTree {V : Type*} [Fintype V] [DecidableEq V]
    {G : SimpleGraph V} (T : G.Subgraph)
    (hsp : T.IsSpanning) (htree : T.coe.IsTree) : T.spanningCoe.IsTree := by
  exact (T.spanningCoeEquivCoeOfSpanning hsp).isTree_iff.mpr htree

/-- A spanning tree on at least three vertices has an internal vertex. -/
lemma nonleaves_nonempty {V : Type*} [Fintype V] [DecidableEq V]
    {G : SimpleGraph V} (T : G.Subgraph)
    (hsp : T.IsSpanning) (htree : T.coe.IsTree) (hcard : 3 ≤ Fintype.card V) :
    ({v : V | T.degree v ≠ 1} : Set V).Nonempty := by
  let H := T.spanningCoe
  have htreeH : H.IsTree := spanningCoe_isTree T hsp htree
  by_contra hn
  have hall : ∀ v : V, H.degree v = 1 := by
    intro v
    rw [Subgraph.degree_spanningCoe]
    by_contra hv
    exact hn ⟨v, hv⟩
  have hsum : ∑ v, H.degree v = Fintype.card V := by simp [hall]
  have hhand := H.sum_degrees_eq_twice_card_edges
  have hedge := htreeH.card_edgeFinset
  omega

/-- The internal vertices of every spanning tree on at least three vertices
form a connected dominating set of the ambient graph. -/
lemma nonleaves_connected_dominating {V : Type*} [Fintype V] [DecidableEq V]
    {G : SimpleGraph V} (T : G.Subgraph)
    (hsp : T.IsSpanning) (htree : T.coe.IsTree) (hcard : 3 ≤ Fintype.card V) :
    G.IsConnectedDominating {v : V | T.degree v ≠ 1} := by
  let H := T.spanningCoe
  let D : Set V := {v : V | T.degree v ≠ 1}
  have htreeH : H.IsTree := spanningCoe_isTree T hsp htree
  have hDne : D.Nonempty := nonleaves_nonempty T hsp htree hcard
  have hDpre : (H.induce D).Preconnected := by
    apply htreeH.isConnected.preconnected.induce_of_degree_eq_one
    intro v hv
    have hdegT : T.degree v = 1 := by simpa [D] using hv
    have hdegH : H.degree v = 1 := by simpa [H] using hdegT
    obtain ⟨w, hw, huw⟩ := degree_eq_one_iff_existsUnique_adj.mp hdegH
    intro a ha b hb
    exact (huw a ha).trans (huw b hb).symm
  letI : Nonempty D := Set.nonempty_coe_sort.mpr hDne
  have hDconnH : (H.induce D).Connected := ⟨hDpre⟩
  have hDconnG : (G.induce D).Connected := by
    apply hDconnH.mono
    intro a b hab
    exact T.spanningCoe_le hab
  refine ⟨?_, hDconnG⟩
  intro v
  by_cases hv : v ∈ D
  · exact Or.inl hv
  · right
    obtain ⟨d, hd⟩ := hDne
    obtain ⟨p, hp⟩ := htreeH.isConnected.exists_isPath v d
    have hvd : v ≠ d := by
      intro h
      subst d
      exact hv hd
    have hpn : ¬p.Nil := p.not_nil_of_ne hvd
    have hadj : H.Adj v p.snd := p.adj_snd hpn
    refine ⟨p.snd, ?_, T.spanningCoe_le hadj⟩
    by_contra hsnd
    have hdegT : T.degree p.snd = 1 := by simpa [D] using hsnd
    have hdegH : H.degree p.snd = 1 := by simpa [H] using hdegT
    have hsub : (H.neighborSet p.snd).Subsingleton := by
      obtain ⟨w, hw, huw⟩ := degree_eq_one_iff_existsUnique_adj.mp hdegH
      intro a ha b hb
      exact (huw a ha).trans (huw b hb).symm
    have hsndv : p.snd ≠ v := hadj.ne.symm
    have hsndd : p.snd ≠ d := by
      intro h
      have hsndD : p.snd ∈ D := by rw [h]; exact hd
      exact hsnd (by simpa [D] using hsndD)
    have hnot := hp.isTrail.not_mem_support_of_subsingleton_neighborSet
      hsndv hsndd hsub
    exact hnot (List.mem_of_mem_tail (p.snd_mem_tail_support hpn))

lemma leaves_add_le_card_of_connected_domination_lower_bound
    {V : Type*} [Fintype V] [DecidableEq V] {G : SimpleGraph V}
    (T : G.Subgraph) (hsp : T.IsSpanning) (htree : T.coe.IsTree)
    (hcard : 3 ≤ Fintype.card V) (k : ℕ)
    (hk : ∀ D : Finset V, G.IsConnectedDominating (D : Set V) → k ≤ D.card) :
    (T.verts.toFinset.filter fun v ↦ T.degree v = 1).card + k ≤ Fintype.card V := by
  let D : Finset V := Finset.univ.filter fun v ↦ T.degree v ≠ 1
  have hDdom : G.IsConnectedDominating (D : Set V) := by
    simpa [D] using nonleaves_connected_dominating T hsp htree hcard
  have hkD : k ≤ D.card := hk D hDdom
  have hverts : T.verts.toFinset = Finset.univ := by
    ext v
    simp [hsp v]
  rw [hverts]
  have hpartition :
      ((Finset.univ : Finset V).filter fun v ↦ T.degree v = 1).card +
        ((Finset.univ : Finset V).filter fun v ↦ ¬ T.degree v = 1).card =
          (Finset.univ : Finset V).card :=
    Finset.card_filter_add_card_filter_not
      (s := (Finset.univ : Finset V)) (p := fun v ↦ T.degree v = 1)
  change (Finset.univ.filter fun v ↦ T.degree v = 1).card + k ≤ Fintype.card V
  change k ≤ (Finset.univ.filter fun v ↦ T.degree v ≠ 1).card at hkD
  have hpartition' :
      ((Finset.univ : Finset V).filter fun v ↦ T.degree v = 1).card +
        ((Finset.univ : Finset V).filter fun v ↦ T.degree v ≠ 1).card =
          (Finset.univ : Finset V).card := by
    simpa only [not_not] using hpartition
  simpa using (show
    ((Finset.univ : Finset V).filter fun v ↦ T.degree v = 1).card + k ≤
      (Finset.univ : Finset V).card by
      omega)

lemma Ls_le_card_sub_of_connected_domination_lower_bound
    {V : Type*} [Fintype V] [DecidableEq V] {G : SimpleGraph V}
    [DecidableRel G.Adj] (hG : G.Connected) (hcard : 3 ≤ Fintype.card V) (k : ℕ)
    (hk : ∀ D : Finset V, G.IsConnectedDominating (D : Set V) → k ≤ D.card) :
    Ls G ≤ ((Fintype.card V - k : ℕ) : ℝ) := by
  unfold Ls
  apply csSup_le
  · obtain ⟨H, hHG, htreeH⟩ := hG.exists_isTree_le
    let T : G.Subgraph := G.toSubgraph H hHG
    have hsp : T.IsSpanning := SimpleGraph.toSubgraph.isSpanning H hHG
    have htree : T.coe.IsTree := by
      have e : T.coe ≃g H :=
        ⟨Equiv.Set.univ V, fun {a b} ↦ Iff.rfl⟩
      exact e.isTree_iff.mpr htreeH
    exact Set.Nonempty.image _ ⟨T, hsp, htree⟩
  · rintro y ⟨T, ⟨hsp, htree⟩, rfl⟩
    dsimp only
    have hleaves := leaves_add_le_card_of_connected_domination_lower_bound
      T hsp htree hcard k hk
    have hnat :
        (T.verts.toFinset.filter fun v ↦ T.degree v = 1).card ≤
          Fintype.card V - k := by
      omega
    exact_mod_cast hnat

end

/-- Two triangles whose distinguished vertices are joined by a path of seven edges. -/
def D7 : SimpleGraph (Fin 12) where
  Adj u v :=
    (u.1 < 8 ∧ v.1 < 8 ∧ (u.1 + 1 = v.1 ∨ v.1 + 1 = u.1)) ∨
    (u.1 = 0 ∧ (v.1 = 8 ∨ v.1 = 9)) ∨
    (v.1 = 0 ∧ (u.1 = 8 ∨ u.1 = 9)) ∨
    (u.1 = 8 ∧ v.1 = 9) ∨ (v.1 = 8 ∧ u.1 = 9) ∨
    (u.1 = 7 ∧ (v.1 = 10 ∨ v.1 = 11)) ∨
    (v.1 = 7 ∧ (u.1 = 10 ∨ u.1 = 11)) ∨
    (u.1 = 10 ∧ v.1 = 11) ∨ (v.1 = 10 ∧ u.1 = 11)
  symm := by
    rintro u v h
    rcases h with h | h | h | h | h | h | h | h | h
    · exact Or.inl ⟨h.2.1, h.1, h.2.2.symm.imp id id⟩
    · exact Or.inr (Or.inr (Or.inl ⟨h.1, h.2⟩))
    · exact Or.inr (Or.inl ⟨h.1, h.2⟩)
    · exact Or.inr (Or.inr (Or.inr (Or.inr (Or.inl ⟨h.1, h.2⟩))))
    · exact Or.inr (Or.inr (Or.inr (Or.inl ⟨h.1, h.2⟩)))
    · exact Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inl ⟨h.1, h.2⟩))))))
    · exact Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inl ⟨h.1, h.2⟩)))))
    · exact Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr ⟨h.1, h.2⟩)))))))
    · exact Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inl ⟨h.1, h.2⟩)))))))
  loopless := by
    intro u h
    rcases h with h | h | h | h | h | h | h | h | h <;> omega

instance instDecidableD7 : DecidableRel D7.Adj := fun u v =>
  inferInstanceAs (Decidable (
    (u.1 < 8 ∧ v.1 < 8 ∧ (u.1 + 1 = v.1 ∨ v.1 + 1 = u.1)) ∨
    (u.1 = 0 ∧ (v.1 = 8 ∨ v.1 = 9)) ∨
    (v.1 = 0 ∧ (u.1 = 8 ∨ u.1 = 9)) ∨
    (u.1 = 8 ∧ v.1 = 9) ∨ (v.1 = 8 ∧ u.1 = 9) ∨
    (u.1 = 7 ∧ (v.1 = 10 ∨ v.1 = 11)) ∨
    (v.1 = 7 ∧ (u.1 = 10 ∨ u.1 = 11)) ∨
    (u.1 = 10 ∧ v.1 = 11) ∨ (v.1 = 10 ∧ u.1 = 11)))

/-- The set `M(G²)` of maximum-degree vertices of the square, presented
through executable distances. -/
def squareMaximumDegreeVertices {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj] : Set V :=
  let squareDegree (v : V) :=
    (Finset.univ.filter fun w => v ≠ w ∧ computable_dist G v w ≤ 2).card
  {v | squareDegree v = Finset.univ.sup squareDegree}

/-- The exact source-faithful statement: the distinguished set is computed in
the square, while `distMin` is measured in the original graph. -/
def conjecture176ExactStatement : Prop :=
  open scoped Classical in
  ∀ (V : Type) [Fintype V] [DecidableEq V] [Nontrivial V]
    (G : SimpleGraph V) [DecidableRel G.Adj], G.Connected →
      Ls G + b G ≥ (Fintype.card V : ℝ) +
        distMin G (squareMaximumDegreeVertices G)

theorem D7_connected : D7.Connected := by native_decide

/-- Exhaustive certificate: no set of fewer than eight vertices is connected
and dominating in `D7`. -/
theorem no_small_connected_dominating :
    ¬∃ D ∈ (Finset.univ : Finset (Fin 12)).powerset, D.card < 8 ∧
      (∀ v, v ∈ D ∨ ∃ u ∈ D, D7.Adj v u) ∧
      (∀ u, ∀ hu : u ∈ D, ∀ v, ∀ hv : v ∈ D,
        u = v ∨ 0 < computable_dist (D7.induce D) ⟨u, hu⟩ ⟨v, hv⟩) := by
  native_decide

theorem D7_connected_domination_lower
    (D : Finset (Fin 12)) (hD : D7.IsConnectedDominating (D : Set (Fin 12))) :
    8 ≤ D.card := by
  by_contra h
  apply no_small_connected_dominating
  refine ⟨D, Finset.mem_powerset.mpr (Finset.subset_univ D), by omega, hD.1, ?_⟩
  intro u hu v hv
  by_cases huv : u = v
  · exact Or.inl huv
  · right
    rw [← dist_eq_computable]
    have hr := hD.2.preconnected ⟨u, hu⟩ ⟨v, hv⟩
    exact hr.pos_dist_of_ne (by simpa using huv)

theorem D7_Ls_le : Ls D7 ≤ 4 := by
  classical
  have h := Ls_le_card_sub_of_connected_domination_lower_bound
    D7_connected (by norm_num) 8 D7_connected_domination_lower
  norm_num at h ⊢
  exact h

/-- A bipartite induced subgraph cannot contain all three vertices of a triangle. -/
lemma triangle_not_subset_of_isBipartite (S : Finset (Fin 12))
    (hS : (D7.induce S).IsBipartite) {x y z : Fin 12}
    (hxy : D7.Adj x y) (hyz : D7.Adj y z) (hzx : D7.Adj z x) :
    ¬({x, y, z} : Finset (Fin 12)) ⊆ S := by
  classical
  rw [induce_isBipartite_iff_exists_coloring] at hS
  obtain ⟨color, hcolor⟩ := hS
  intro hsub
  have hx : x ∈ S := hsub (by simp)
  have hy : y ∈ S := hsub (by simp)
  have hz : z ∈ S := hsub (by simp)
  have hxy' := hcolor x hx y hy hxy
  have hyz' := hcolor y hy z hz hyz
  have hzx' := hcolor z hz x hx hzx
  omega

lemma bipartite_subset_card_le_ten (S : Finset (Fin 12))
    (hS : (D7.induce S).IsBipartite) : S.card ≤ 10 := by
  classical
  have hleft : ¬({0, 8, 9} : Finset (Fin 12)) ⊆ S :=
    triangle_not_subset_of_isBipartite S hS (by decide) (by decide) (by decide)
  have hright : ¬({7, 10, 11} : Finset (Fin 12)) ⊆ S :=
    triangle_not_subset_of_isBipartite S hS (by decide) (by decide) (by decide)
  obtain ⟨x, hxT, hxS⟩ := Finset.not_subset.mp hleft
  obtain ⟨y, hyT, hyS⟩ := Finset.not_subset.mp hright
  have hxy : x ≠ y := by
    intro h
    subst y
    simp only [Finset.mem_insert, Finset.mem_singleton] at hxT hyT
    rcases hxT with rfl | rfl | rfl <;> simp at hyT
  have hsubset : ({x, y} : Finset (Fin 12)) ⊆ Finset.univ \ S := by
    intro v hv
    simp only [Finset.mem_insert, Finset.mem_singleton] at hv
    rcases hv with rfl | rfl <;> simp [hxS, hyS]
  have hcard : 2 ≤ (Finset.univ \ S).card := by
    rw [← Finset.card_pair hxy]
    exact Finset.card_le_card hsubset
  have hpartition : (Finset.univ \ S).card + S.card = 12 := by
    simpa using Finset.card_sdiff_add_card_inter Finset.univ S
  omega

def bipartiteTen : Finset (Fin 12) := Finset.univ \ {9, 11}

def bipartiteTenColor (v : Fin 12) : Fin 2 :=
  if v = 0 ∨ v = 2 ∨ v = 4 ∨ v = 6 ∨ v = 10 then 0 else 1

lemma bipartiteTen_card : bipartiteTen.card = 10 := by native_decide

lemma bipartiteTen_isBipartite : (D7.induce bipartiteTen).IsBipartite := by
  rw [induce_isBipartite_iff_exists_coloring]
  exact ⟨bipartiteTenColor, by native_decide⟩

theorem D7_bipartiteSize : D7.largestInducedBipartiteSubgraphSize = 10 := by
  classical
  unfold SimpleGraph.largestInducedBipartiteSubgraphSize
  apply le_antisymm
  · apply csSup_le
    · refine ⟨0, ∅, ?_, rfl⟩
      rw [induce_isBipartite_iff_exists_coloring]
      exact ⟨fun _ => 0, by simp⟩
    · rintro n ⟨S, hS, rfl⟩
      exact bipartite_subset_card_le_ten S hS
  · apply le_csSup
    · exact ⟨Fintype.card (Fin 12), fun n ⟨S, _, hS⟩ => hS ▸ S.card_le_univ⟩
    · exact ⟨bipartiteTen, bipartiteTen_isBipartite, bipartiteTen_card⟩

theorem D7_b : b D7 = 10 := by
  classical
  simp [b, D7_bipartiteSize]

theorem D7_square_max_degree_vertices :
    @squareMaximumDegreeVertices (Fin 12) inferInstance inferInstance D7 instDecidableD7 =
      ({1, 6} : Set (Fin 12)) := by
  ext v
  simp only [squareMaximumDegreeVertices, Set.mem_setOf_eq, Set.mem_insert_iff,
    Set.mem_singleton_iff]
  fin_cases v <;> native_decide

theorem D7_distMin_square_max_degree_vertices :
    distMin D7 ({1, 6} : Set (Fin 12)) = 5 := by
  rw [show ({1, 6} : Set (Fin 12)) = ↑({1, 6} : Finset (Fin 12)) by simp,
    distMin_eq_computableDistMin]
  native_decide

/-- The source-faithful reading of WOWII Conjecture 176 is false. -/
theorem conjecture176_exact_false : ¬conjecture176ExactStatement := by
  classical
  intro h
  have h176 := h (Fin 12) D7 D7_connected
  rw [D7_b, D7_square_max_degree_vertices,
    D7_distMin_square_max_degree_vertices] at h176
  norm_num at h176
  linarith [D7_Ls_le]

/-- WOWII Conjecture 176 has answer `False`, witnessed by `D7`. -/
@[category research solved, AMS 5]
theorem conjecture176 : answer(False) ↔ conjecture176ExactStatement := by
  classical
  rw [false_iff]
  exact conjecture176_exact_false

#print axioms conjecture176

end WrittenOnTheWallII.GraphConjecture176
