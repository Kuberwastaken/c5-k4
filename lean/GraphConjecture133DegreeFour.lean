import GraphConjecture133Regular

/-!
# WOWII 133: the degree-four extension barrier

The obvious attempt to use all three off-geodesic neighbors at once cannot
produce a path: triangle-freeness makes those siblings pairwise nonadjacent.
This file formalizes that obstruction and the strongest unconditional
one-ended geodesic extension supplied by the same local hypotheses.
-/

namespace WrittenOnTheWallII.GraphConjecture133DegreeFour

open SimpleGraph
open WrittenOnTheWallII.GraphConjecture133Cubic
open WrittenOnTheWallII.GraphConjecture133Next
open WrittenOnTheWallII.GraphConjecture133Regular
open WrittenOnTheWallII.GraphConjecture133Specialization

variable {V : Type*} [Fintype V] [DecidableEq V] [Nonempty V]

omit [Fintype V] [DecidableEq V] [Nonempty V] in
/-- Two distinct neighbors of one vertex cannot be consecutive in an induced
path in a triangle-free graph.  In particular `[a,b,u]` is not the hoped-for
multi-neighbor prepend. -/
theorem siblingPrepend_not_inducedPath {G : SimpleGraph V} {a b u : V}
    (htri : G.CliqueFree 3) (hau : G.Adj a u) (hbu : G.Adj b u)
    (hab : a ≠ b) :
    ¬G.isInducedPath [a, b, u] := by
  have hnab : ¬G.Adj a b :=
    G.isIndepSet_neighborSet_of_triangleFree htri u
      (by simpa [G.mem_neighborSet, adj_comm] using hau)
      (by simpa [G.mem_neighborSet, adj_comm] using hbu)
      hab
  intro hp
  have hadj : G.Adj a b := by
    let i : Fin ([a, b, u] : List V).length := ⟨0, by simp⟩
    let j : Fin ([a, b, u] : List V).length := ⟨1, by simp⟩
    exact (hp.2 i j).mpr (by left; rfl)
  exact hnab hadj

/-- A connected triangle-free four-regular graph has radius at least two. -/
theorem two_le_radius_toNat_of_fourRegular_triangleFree
    (G : SimpleGraph V) [DecidableRel G.Adj] (hconn : G.Connected)
    (hreg : G.IsRegularOfDegree 4) (htri : G.CliqueFree 3) :
    2 ≤ G.radius.toNat := by
  have hnontrivial : Nontrivial V := by
    let v : V := Classical.ofNonempty
    apply G.nontrivial_of_degree_ne_zero (v := v)
    rw [hreg v]
    omega
  letI : Nontrivial V := hnontrivial
  have hrne : G.radius ≠ ⊤ := G.radius_ne_top_iff.mpr hconn
  by_contra hr
  have hrsmall : G.radius.toNat = 0 ∨ G.radius.toNat = 1 := by omega
  rcases hrsmall with hrzero | hrone
  · have hz : G.radius = 0 := by
      rcases ENat.toNat_eq_zero.mp hrzero with hz | htop
      · exact hz
      · exact (hrne htop).elim
    exact G.radius_ne_zero_of_nontrivial hz
  · have hradius : G.radius = 1 := (ENat.toNat_eq_iff one_ne_zero).mp hrone
    obtain ⟨c, hc⟩ := G.exists_eccent_eq_radius
    have hcadj : ∀ v, c ≠ v → G.Adj c v :=
      (G.eccent_eq_one_iff c).mp (hc.trans hradius)
    have huniv : Finset.univ = insert c (G.neighborFinset c) := by
      ext v
      simp only [Finset.mem_univ, Finset.mem_insert, G.mem_neighborFinset, true_iff]
      exact eq_or_ne c v |>.imp Eq.symm (hcadj v)
    have hcard : Fintype.card V = 5 := by
      have hcnot : c ∉ G.neighborFinset c := G.notMem_neighborFinset_self c
      have hdeg : (G.neighborFinset c).card = 4 := by
        rw [G.card_neighborFinset_eq_degree, hreg c]
      have := congrArg Finset.card huniv
      simp [hcnot, hdeg] at this
      omega
    have hcompreg : Gᶜ.IsRegularOfDegree 0 := by
      simpa [hcard] using hreg.compl
    have hcomp : Gᶜ = ⊥ := by
      ext u v
      simp only [bot_adj, iff_false]
      intro huv
      have hpos : 0 < Gᶜ.degree u := huv.degree_pos_left
      rw [hcompreg u] at hpos
      omega
    have htop : G = ⊤ := by
      simpa using congrArg (fun H : SimpleGraph V ↦ Hᶜ) hcomp
    let e : V ≃ Fin 5 := (Fintype.equivFin V).trans (finCongr hcard)
    let emb : Fin 3 ↪ V := (Fin.castLEEmb (by omega)).trans e.symm.toEmbedding
    let f : (⊤ : SimpleGraph (Fin 3)) ↪g G :=
      { toFun := emb
        inj' := emb.injective
        map_rel_iff' := by simp [htop] }
    exact (SimpleGraph.not_cliqueFree_of_top_embedding f) htri

omit [Nonempty V] in
/-- A four-regular triangle-free graph supplies an off-direction neighbor at
the head of every nontrivial walk. -/
lemma exists_off_neighbor_of_fourRegular_triangleFree
    (G : SimpleGraph V) [DecidableRel G.Adj] {u v : V} (p : G.Walk u v)
    (hp : ¬p.Nil) (hreg : G.IsRegularOfDegree 4) (htri : G.CliqueFree 3) :
    ∃ a : V, G.Adj a u ∧ a ≠ p.snd ∧ ¬G.Adj a p.snd := by
  classical
  have hus : G.Adj u p.snd := p.adj_snd hp
  let s := (G.neighborFinset u).erase p.snd
  have hsCard : s.card = 3 := by
    have hmem : p.snd ∈ G.neighborFinset u := by simpa using hus
    simp only [s]
    rw [Finset.card_erase_of_mem hmem, G.card_neighborFinset_eq_degree, hreg u]
  obtain ⟨a, ha⟩ := Finset.card_pos.mp (by omega : 0 < s.card)
  have hau : G.Adj a u := by
    simpa [adj_comm] using (Finset.mem_of_mem_erase ha)
  have hane : a ≠ p.snd := Finset.ne_of_mem_erase ha
  refine ⟨a, hau, hane, ?_⟩
  exact G.isIndepSet_neighborSet_of_triangleFree htri u
    (by simpa [G.mem_neighborSet, adj_comm] using hau)
    (by simpa [G.mem_neighborSet] using hus)
    hane

omit [Nonempty V] in
/-- C4-freeness and shortestness make the selected neighbor clean against the
entire positive-index tail of a geodesic. -/
lemma exists_clean_neighbor_of_fourRegular_triangleFree_c4Free
    (G : SimpleGraph V) [DecidableRel G.Adj] {u v : V} (p : G.Walk u v)
    (hp : p.length = G.dist u v) (hlen : 2 ≤ p.length)
    (hreg : G.IsRegularOfDegree 4) (htri : G.CliqueFree 3)
    (hc4 : ¬WrittenOnTheWallII.GraphConjecture133Cubic.HasC4 G) :
    ∃ a : V, G.Adj a u ∧ a ∉ p.support ∧
      ∀ x ∈ p.support.tail, ¬G.Adj a x := by
  have hnil : ¬p.Nil := by
    simpa [Walk.not_nil_iff_lt_length] using (show 0 < p.length by omega)
  obtain ⟨a, hau, hane, hanot⟩ :=
    exists_off_neighbor_of_fourRegular_triangleFree G p hnil hreg htri
  refine ⟨a, hau, ?_, ?_⟩
  · intro hamem
    exact hane (eq_snd_of_mem_support_of_adj_head_of_geodesic p hp hamem hau)
  · intro x hx
    have hinduced := isInducedPath_support_of_length_eq_dist p hp
    have hutail : u ∉ p.support.tail := by
      have hnodup := hinduced.1
      rw [p.support_eq_cons] at hnodup
      exact (List.nodup_cons.mp hnodup).1
    have hxmem : x ∈ p.support := by
      rw [p.support_eq_cons]
      exact List.mem_cons_of_mem u hx
    obtain ⟨k, hkx, hklen⟩ := Walk.mem_support_iff_exists_getVert.mp hxmem
    have hkpos : 1 ≤ k := by
      by_contra hk
      have hkzero : k = 0 := by omega
      subst k
      apply hutail
      have hxu : x = u := by simpa [Walk.getVert_zero] using hkx.symm
      simpa [hxu] using hx
    have hnot := not_adj_getVert_pos_of_geodesic_of_c4Free
      p hp hlen hc4 hau hane hanot k hkpos hklen
    simpa [hkx] using hnot

/-- The strongest one-ended extension obtained from only the local
degree-four, triangle-free, and C4-free hypotheses. -/
theorem radius_add_two_le_path_of_fourRegular_triangleFree_c4Free
    (G : SimpleGraph V) [DecidableRel G.Adj] (hconn : G.Connected)
    (hreg : G.IsRegularOfDegree 4) (htri : G.CliqueFree 3)
    (hc4 : ¬WrittenOnTheWallII.GraphConjecture133Cubic.HasC4 G) :
    G.radius.toNat + 2 ≤ path G := by
  obtain ⟨u, v, p, hpDist, hpLength, _hpInduced, _hpSupport⟩ :=
    exists_radius_geodesic_support_with_dist G hconn
  have hlen : 2 ≤ p.length := by
    rw [hpLength]
    exact two_le_radius_toNat_of_fourRegular_triangleFree G hconn hreg htri
  obtain ⟨a, hau, hafresh, hclean⟩ :=
    exists_clean_neighbor_of_fourRegular_triangleFree_c4Free
      G p hpDist hlen hreg htri hc4
  have haInduced : G.isInducedPath (a :: p.support) := by
    rw [p.support_eq_cons]
    apply isInducedPath_cons_of_adj_head_of_not_adj_tail
    · simpa [← p.support_eq_cons] using
        isInducedPath_support_of_length_eq_dist p hpDist
    · exact hau
    · simpa [← p.support_eq_cons] using hafresh
    · exact hclean
  have haLength : (a :: p.support).length = p.length + 2 := by
    simp [p.length_support]
  rw [← hpLength, ← haLength]
  exact path_ge_of_isInducedPath G (a :: p.support) haInduced

/-- In the C4-free four-regular triangle-free stratum, the exact conjecture is
equivalent to the still-missing `radius + 4 <= path` wall. -/
theorem sourceConclusion_iff_radius_add_four_le_path
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hreg : G.IsRegularOfDegree 4) (htri : G.CliqueFree 3)
    (hc4 : ¬WrittenOnTheWallII.GraphConjecture133Cubic.HasC4 G) :
    SourceConclusion G ↔ G.radius.toNat + 4 ≤ path G := by
  classical
  simp only [SourceConclusion,
    WrittenOnTheWallII.GraphConjecture133Cubic.HasC4] at hc4 ⊢
  simp only [hc4, ↓reduceIte, pow_one]
  rw [l_eq_regularDegree_of_triangleFree G 4 hreg htri]
  norm_num
  exact_mod_cast Iff.rfl

end WrittenOnTheWallII.GraphConjecture133DegreeFour
