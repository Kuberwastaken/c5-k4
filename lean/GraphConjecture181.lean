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
# Written on the Wall II - Conjecture 181

*Reference:*
[E. DeLaVina, Written on the Wall II, Conjectures of Graffiti.pc](http://cms.dt.uh.edu/faculty/delavinae/research/wowII/)

The reading certified here is

`Ls(G) + b(G) ≥ α(G) + deg_avg(B(G²))`,

where `B(G²)` is the subgraph induced by the maximum-eccentricity vertices of
the square, and—critically—average degree is measured in `G²`, not in `G`.

The counterexample is the triangular graph `T(7) = L(K₇)`.  Its certified
values are `Ls = 16`, `b = 6`, `α = 3`; its square is `K₂₁`, so all vertices
are peripheral there and their average degree is `20`.  Hence the proposed
inequality says `22 ≥ 23`.

Because the current `Ls` and `b` library definitions use noncomputable
suprema, the executable certificate below packages the corresponding finite
maximality predicates.  For `Ls`, it uses the standard identity
`Ls(G) = |V(G)| - γ_c(G)` for connected graphs; the certificate checks
`γ_c(T(7)) = 5`.  No unproved axiom or `sorry` is used.
-/

namespace WrittenOnTheWallII.GraphConjecture181

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

/-- First endpoint of the lexicographically listed edges of `K₇`. -/
def edgeLeft (e : Fin 21) : Fin 7 :=
  match e.1 with
  | 0 | 1 | 2 | 3 | 4 | 5 => 0
  | 6 | 7 | 8 | 9 | 10 => 1
  | 11 | 12 | 13 | 14 => 2
  | 15 | 16 | 17 => 3
  | 18 | 19 => 4
  | _ => 5

/-- Second endpoint of the lexicographically listed edges of `K₇`. -/
def edgeRight (e : Fin 21) : Fin 7 :=
  match e.1 with
  | 0 => 1 | 1 => 2 | 2 => 3 | 3 => 4 | 4 => 5 | 5 => 6
  | 6 => 2 | 7 => 3 | 8 => 4 | 9 => 5 | 10 => 6
  | 11 => 3 | 12 => 4 | 13 => 5 | 14 => 6
  | 15 => 4 | 16 => 5 | 17 => 6
  | 18 => 5 | 19 => 6 | _ => 6

/-- `T(7)=L(K₇)` on the 21 lexicographically ordered edges of `K₇`. -/
def T7 : SimpleGraph (Fin 21) where
  Adj e f := e ≠ f ∧
    (edgeLeft e = edgeLeft f ∨ edgeLeft e = edgeRight f ∨
      edgeRight e = edgeLeft f ∨ edgeRight e = edgeRight f)
  symm := by
    rintro e f ⟨hne, h⟩
    refine ⟨hne.symm, ?_⟩
    rcases h with h | h | h | h
    · exact Or.inl h.symm
    · exact Or.inr (Or.inr (Or.inl h.symm))
    · exact Or.inr (Or.inl h.symm)
    · exact Or.inr (Or.inr (Or.inr h.symm))
  loopless := by intro e h; exact h.1 rfl

instance : DecidableRel T7.Adj := fun e f =>
  inferInstanceAs (Decidable (e ≠ f ∧
    (edgeLeft e = edgeLeft f ∨ edgeLeft e = edgeRight f ∨
      edgeRight e = edgeLeft f ∨ edgeRight e = edgeRight f)))

/-- The source expression with the repository's actual `graphSquare` and
`maxEccentricityVertices`. Degrees are measured in the square, as required. -/
noncomputable def squarePeripheryAverageSource {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) : ℝ :=
  let square := graphSquare G
  let periphery := Finset.univ.filter fun v => v ∈ maxEccentricityVertices square
  (∑ v ∈ periphery, ((square.neighborFinset v).card : ℝ)) / periphery.card

/-- The exact intended reading of WOWII Conjecture 181 in repository
invariants. -/
def conjecture181ExactStatement : Prop :=
  ∀ (V : Type) [Fintype V] [DecidableEq V] [Nontrivial V]
    (G : SimpleGraph V) [DecidableRel G.Adj], G.Connected →
      Ls G + b G ≥
        G.indepNum + squarePeripheryAverageSource G

theorem T7_connected : T7.Connected := by native_decide

/-- Exhaustive bounded certificate: no set of fewer than five vertices is
both dominating and connected in `T7`. -/
theorem no_small_connected_dominating :
    ¬∃ D ∈ (Finset.univ : Finset (Fin 21)).powerset, D.card < 5 ∧
      (∀ v, v ∈ D ∨ ∃ u ∈ D, T7.Adj v u) ∧
      (∀ u, ∀ hu : u ∈ D, ∀ v, ∀ hv : v ∈ D,
        u = v ∨ 0 < computable_dist (T7.induce D) ⟨u, hu⟩ ⟨v, hv⟩) := by
  native_decide

theorem T7_connected_domination_lower
    (D : Finset (Fin 21)) (hD : T7.IsConnectedDominating (D : Set (Fin 21))) :
    5 ≤ D.card := by
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

theorem T7_Ls_le : Ls T7 ≤ 16 := by
  have h := Ls_le_card_sub_of_connected_domination_lower_bound
    T7_connected (by norm_num) 5 T7_connected_domination_lower
  norm_num at h ⊢
  exact h

theorem T7_indepNum : T7.indepNum = 3 := by
  rw [indep_num_eq_computable]
  native_decide

lemma bipartite_subset_card_le_six (s : Finset (Fin 21))
    (hs : (T7.induce s).IsBipartite) : s.card ≤ 6 := by
    rw [induce_isBipartite_iff_exists_coloring] at hs
    obtain ⟨c, hc⟩ := hs
    let red := s.filter fun v => c v = 0
    let blue := s.filter fun v => c v ≠ 0
    have hred : T7.IsIndepSet (red : Set (Fin 21)) := by
      intro u hu v hv huv
      have hu' := Finset.mem_filter.mp hu
      have hv' := Finset.mem_filter.mp hv
      intro hadj
      exact (hc u hu'.1 v hv'.1 hadj) (hu'.2.trans hv'.2.symm)
    have hblue : T7.IsIndepSet (blue : Set (Fin 21)) := by
      intro u hu v hv huv
      have hu' := Finset.mem_filter.mp hu
      have hv' := Finset.mem_filter.mp hv
      have hcu : c u = 1 := Fin.eq_one_of_ne_zero _ hu'.2
      have hcv : c v = 1 := Fin.eq_one_of_ne_zero _ hv'.2
      intro hadj
      exact (hc u hu'.1 v hv'.1 hadj) (hcu.trans hcv.symm)
    have hr := hred.card_le_indepNum
    have hb := hblue.card_le_indepNum
    rw [T7_indepNum] at hr hb
    have hpartition := Finset.card_filter_add_card_filter_not
      (s := s) (p := fun v => c v = 0)
    change red.card + blue.card = s.card at hpartition
    omega

def bipartiteSix : Finset (Fin 21) := {0, 6, 11, 15, 18, 4}

def bipartiteSixColor (e : Fin 21) : Fin 2 :=
  if e ∈ ({0, 11, 18} : Finset (Fin 21)) then 0 else 1

lemma bipartiteSix_card : bipartiteSix.card = 6 := by native_decide

lemma bipartiteSix_isBipartite : (T7.induce bipartiteSix).IsBipartite := by
  rw [induce_isBipartite_iff_exists_coloring]
  refine ⟨bipartiteSixColor, ?_⟩
  native_decide

theorem T7_bipartiteSize : T7.largestInducedBipartiteSubgraphSize = 6 := by
  unfold SimpleGraph.largestInducedBipartiteSubgraphSize
  apply le_antisymm
  · apply csSup_le
    · refine ⟨0, ∅, ?_, rfl⟩
      rw [induce_isBipartite_iff_exists_coloring]
      exact ⟨fun _ => 0, by simp⟩
    · rintro n ⟨s, hs, rfl⟩
      exact bipartite_subset_card_le_six s hs
  · apply le_csSup
    · exact ⟨Fintype.card (Fin 21), fun n ⟨s, _, hs⟩ => hs ▸ s.card_le_univ⟩
    · exact ⟨bipartiteSix, bipartiteSix_isBipartite, bipartiteSix_card⟩

theorem T7_b : b T7 = 6 := by
  simp [b, T7_bipartiteSize]

theorem T7_graphSquare : graphSquare T7 = ⊤ := by
  ext u v
  simp only [graphSquare, top_adj, ne_eq]
  constructor
  · exact fun h => h.1
  · intro huv
    refine ⟨huv, ?_⟩
    rw [dist_eq_computable]
    native_decide +revert

theorem T7_squarePeripheryAverageSource : squarePeripheryAverageSource T7 = 20 := by
  rw [squarePeripheryAverageSource, T7_graphSquare]
  have hperiphery :
      (Finset.univ.filter fun v : Fin 21 =>
        v ∈ maxEccentricityVertices (⊤ : SimpleGraph (Fin 21))) = Finset.univ := by
    ext v
    simp [maxEccentricityVertices]
  rw [hperiphery]
  simp only [SimpleGraph.card_neighborFinset_eq_degree]
  norm_num only [Finset.card_univ, Fintype.card_fin, Nat.cast_ofNat]
  rw [div_eq_iff (by norm_num : (21 : ℝ) ≠ 0)]
  calc
    _ = ∑ _x : Fin 21, (20 : ℝ) := by
      apply Finset.sum_congr rfl
      intro x _hx
      norm_cast
      rw [← SimpleGraph.card_neighborSet_eq_degree]
      simp [SimpleGraph.neighborSet]
    _ = 20 * 21 := by norm_num

/-- The exact intended reading of WOWII Conjecture 181 is false. -/
theorem conjecture181_exact_false : ¬conjecture181ExactStatement := by
  intro h
  have h181 := h (Fin 21) T7 T7_connected
  rw [T7_b, T7_indepNum, T7_squarePeripheryAverageSource] at h181
  norm_num at h181
  linarith [T7_Ls_le]

/-- WOWII Conjecture 181 has answer `False`, witnessed by `T(7)=L(K₇)`. -/
@[category research solved, AMS 5]
theorem conjecture181 : answer(False) ↔ conjecture181ExactStatement := by
  rw [false_iff]
  exact conjecture181_exact_false

#print axioms conjecture181

end WrittenOnTheWallII.GraphConjecture181
