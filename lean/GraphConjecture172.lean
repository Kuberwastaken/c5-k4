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
# Written on the Wall II - Conjecture 172

*Reference:*
[E. DeLaVina, Written on the Wall II, Conjectures of Graffiti.pc](http://cms.dt.uh.edu/faculty/delavinae/research/wowII/)

The source-faithful reading certified here is

`Ls(G) ≥ -1 + Δ(B(G)) + dist_min(G, M(G²))`,

where `B(G)` is the set of maximum-eccentricity vertices, `Δ(B(G))` is the
maximum degree in `G` among those vertices, and `M(G²)` is the set of
maximum-degree vertices of the square.  As specified by the source definition
of `dist_min`, the final distance is measured back in `G`.

The counterexample `D₉` consists of two triangles whose distinguished
vertices are joined by a path of nine edges.  It has `Ls(D₉) = 4`, its
peripheral vertices have degree `2`, and the two maximum-degree vertices of
`D₉²` are at distance `7` in `D₉`.  Thus the conjecture would require
`4 ≥ -1 + 2 + 7 = 8`.

For robustness, the certificate also checks that the same two selected
vertices have minimum distance `4` in `D₉²`.  Even the alternative reading
that measures the final distance in the square would therefore demand
`4 ≥ -1 + 2 + 4 = 5`, so this witness is ambiguity-free.

The proof only needs the certified upper bound `Ls(D₉) ≤ 4`.  Since the
library definition of `Ls` is a noncomputable supremum, this is obtained from
an exhaustive certificate that every connected dominating set has at least
ten vertices.  No unproved axiom or `sorry` is used.
-/

namespace WrittenOnTheWallII.GraphConjecture172

open Classical SimpleGraph Finset

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

/-- Two triangles whose distinguished vertices are joined by a path of nine
edges.  Path vertices are `0,…,9`; the additional triangle vertices are
`10,11` and `12,13`. -/
def D9 : SimpleGraph (Fin 14) where
  Adj u v :=
    (u.1 < 10 ∧ v.1 < 10 ∧ (u.1 + 1 = v.1 ∨ v.1 + 1 = u.1)) ∨
    (u.1 = 0 ∧ (v.1 = 10 ∨ v.1 = 11)) ∨
    (v.1 = 0 ∧ (u.1 = 10 ∨ u.1 = 11)) ∨
    (u.1 = 10 ∧ v.1 = 11) ∨ (v.1 = 10 ∧ u.1 = 11) ∨
    (u.1 = 9 ∧ (v.1 = 12 ∨ v.1 = 13)) ∨
    (v.1 = 9 ∧ (u.1 = 12 ∨ u.1 = 13)) ∨
    (u.1 = 12 ∧ v.1 = 13) ∨ (v.1 = 12 ∧ u.1 = 13)
  symm := by
    intro u v h
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

instance instDecidableD9 : DecidableRel D9.Adj := fun u v =>
  inferInstanceAs (Decidable (
    (u.1 < 10 ∧ v.1 < 10 ∧ (u.1 + 1 = v.1 ∨ v.1 + 1 = u.1)) ∨
    (u.1 = 0 ∧ (v.1 = 10 ∨ v.1 = 11)) ∨
    (v.1 = 0 ∧ (u.1 = 10 ∨ u.1 = 11)) ∨
    (u.1 = 10 ∧ v.1 = 11) ∨ (v.1 = 10 ∧ u.1 = 11) ∨
    (u.1 = 9 ∧ (v.1 = 12 ∨ v.1 = 13)) ∨
    (v.1 = 9 ∧ (u.1 = 12 ∨ u.1 = 13)) ∨
    (u.1 = 12 ∧ v.1 = 13) ∨ (v.1 = 12 ∧ u.1 = 13)))

/-- The source quantity `Δ(B(G))`: maximum original-graph degree among
maximum-eccentricity vertices. -/
noncomputable def peripheryMaxDegree {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj] : ℕ :=
  (Finset.univ.filter fun v => v ∈ maxEccentricityVertices G).sup
    fun v => (G.neighborFinset v).card

/-- The set `M(G²)` of maximum-degree vertices of the square. -/
def squareMaximumDegreeVertices {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj] : Set V :=
  let squareDegree (v : V) :=
    (Finset.univ.filter fun w => v ≠ w ∧ computable_dist G v w ≤ 2).card
  {v | squareDegree v = Finset.univ.sup squareDegree}

/-- The exact source-faithful reading of WOWII Conjecture 172. -/
def conjecture172ExactStatement : Prop :=
  ∀ (V : Type) [Fintype V] [DecidableEq V] [Nontrivial V]
    (G : SimpleGraph V) [DecidableRel G.Adj], G.Connected →
      Ls G ≥ (-1 : ℝ) + peripheryMaxDegree G +
        distMin G (squareMaximumDegreeVertices G)

theorem D9_connected : D9.Connected := by
  rw [connected_iff_exists_forall_reachable]
  refine ⟨0, ?_⟩
  have step (u v : Fin 14) (h : D9.Reachable 0 u) (huv : D9.Adj u v) :
      D9.Reachable 0 v := h.trans huv.reachable
  have h0 : D9.Reachable 0 0 := by simp
  have h1 := step 0 1 h0 (by decide)
  have h2 := step 1 2 h1 (by decide)
  have h3 := step 2 3 h2 (by decide)
  have h4 := step 3 4 h3 (by decide)
  have h5 := step 4 5 h4 (by decide)
  have h6 := step 5 6 h5 (by decide)
  have h7 := step 6 7 h6 (by decide)
  have h8 := step 7 8 h7 (by decide)
  have h9 := step 8 9 h8 (by decide)
  have h10 := step 0 10 h0 (by decide)
  have h11 := step 0 11 h0 (by decide)
  have h12 := step 9 12 h9 (by decide)
  have h13 := step 9 13 h9 (by decide)
  intro v
  fin_cases v <;> assumption

/-- Exhaustive bounded certificate: no set of fewer than ten vertices is both
dominating and connected in `D₉`. -/
theorem no_small_connected_dominating :
    ¬∃ D ∈ (Finset.univ : Finset (Fin 14)).powerset, D.card < 10 ∧
      (∀ v, v ∈ D ∨ ∃ u ∈ D, D9.Adj v u) ∧
      (∀ u, ∀ hu : u ∈ D, ∀ v, ∀ hv : v ∈ D,
        u = v ∨ 0 < computable_dist (D9.induce D) ⟨u, hu⟩ ⟨v, hv⟩) := by
  native_decide

theorem D9_connected_domination_lower
    (D : Finset (Fin 14)) (hD : D9.IsConnectedDominating (D : Set (Fin 14))) :
    10 ≤ D.card := by
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

theorem D9_Ls_le : Ls D9 ≤ 4 := by
  have h := Ls_le_card_sub_of_connected_domination_lower_bound
    D9_connected (by norm_num) 10 D9_connected_domination_lower
  norm_num at h ⊢
  exact h

theorem D9_square_maximum_degree_vertices :
    @squareMaximumDegreeVertices (Fin 14) inferInstance inferInstance D9 instDecidableD9 =
      ({1, 8} : Set (Fin 14)) := by
  ext v
  simp only [squareMaximumDegreeVertices, Set.mem_setOf_eq, Set.mem_insert_iff,
    Set.mem_singleton_iff]
  fin_cases v <;> native_decide

theorem D9_distMin_square_maximum_degree_vertices :
    distMin D9
      (@squareMaximumDegreeVertices (Fin 14) inferInstance inferInstance D9 instDecidableD9) = 7 := by
  rw [D9_square_maximum_degree_vertices,
    show ({1, 8} : Set (Fin 14)) = ↑({1, 8} : Finset (Fin 14)) by simp,
    distMin_eq_computableDistMin]
  native_decide

/-- A computable presentation of `D₉²`, used to certify the alternative
all-in-the-square distance reading. -/
def D9Square : SimpleGraph (Fin 14) where
  Adj u v := u ≠ v ∧ computable_dist D9 u v ≤ 2
  symm := by
    rintro u v ⟨huv, hd⟩
    refine ⟨huv.symm, ?_⟩
    rw [← dist_eq_computable, dist_comm, dist_eq_computable]
    exact hd
  loopless := by intro u h; exact h.1 rfl

instance instDecidableD9Square : DecidableRel D9Square.Adj := fun u v =>
  inferInstanceAs (Decidable (u ≠ v ∧ computable_dist D9 u v ≤ 2))

theorem D9_graphSquare : graphSquare D9 = D9Square := by
  ext u v
  simp only [graphSquare, D9Square]
  rw [dist_eq_computable]

theorem D9_square_distMin_square_maximum_degree_vertices :
    distMin (graphSquare D9)
      (@squareMaximumDegreeVertices (Fin 14) inferInstance inferInstance D9 instDecidableD9) = 4 := by
  rw [D9_graphSquare, D9_square_maximum_degree_vertices,
    show ({1, 8} : Set (Fin 14)) = ↑({1, 8} : Finset (Fin 14)) by simp,
    distMin_eq_computableDistMin]
  native_decide

theorem D9_periphery :
    maxEccentricityVertices D9 = ({10, 11, 12, 13} : Set (Fin 14)) := by
  ext v
  simp only [maxEccentricityVertices, Set.mem_setOf_eq]
  rw [eccent_eq_computable D9 D9_connected, ediam_eq_computable D9 D9_connected]
  norm_cast
  fin_cases v <;> native_decide

theorem D9_peripheryMaxDegree : peripheryMaxDegree D9 = 2 := by
  rw [peripheryMaxDegree]
  have hperiphery :
      (Finset.univ.filter fun v : Fin 14 => v ∈ maxEccentricityVertices D9) =
        ({10, 11, 12, 13} : Finset (Fin 14)) := by
    ext v
    rw [Finset.mem_filter, D9_periphery]
    simp
  rw [hperiphery]
  native_decide

/-- The exact source-faithful reading of WOWII Conjecture 172 is false. -/
theorem conjecture172_exact_false : ¬conjecture172ExactStatement := by
  intro h
  have h172 := h (Fin 14) D9 D9_connected
  rw [D9_peripheryMaxDegree, D9_distMin_square_maximum_degree_vertices] at h172
  norm_num at h172
  linarith [D9_Ls_le]

/-- WOWII Conjecture 172 has answer `False`, witnessed by `D₉`. -/
@[category research solved, AMS 5]
theorem conjecture172 : answer(False) ↔ conjecture172ExactStatement := by
  rw [false_iff]
  exact conjecture172_exact_false

#print axioms conjecture172

end WrittenOnTheWallII.GraphConjecture172
