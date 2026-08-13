import GraphConjecture141RadiusFour

/-!
# WOWII 141: unconditional closure through girth thirteen
-/

namespace WrittenOnTheWallII.GraphConjecture141GirthThirteenClosure

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture141Extraction
open WrittenOnTheWallII.GraphConjecture141DistanceFour
open WrittenOnTheWallII.GraphConjecture141GirthEleven
open WrittenOnTheWallII.GraphConjecture141GirthElevenClosure
open WrittenOnTheWallII.GraphConjecture141GirthNineClosure
open WrittenOnTheWallII.GraphConjecture141GirthSeven
open WrittenOnTheWallII.GraphConjecture141GirthSevenExistence
open WrittenOnTheWallII.GraphConjecture141RadiusFour
open WrittenOnTheWallII.GraphConjecture141RadiusGirth
open WrittenOnTheWallII.GraphConjecture141RadiusTwoAcyclic

universe u
variable {V : Type u} [Fintype V] [DecidableEq V] [Nonempty V]

/-- A chordless five-edge geodesic prefix, represented as the existing
four-edge prefix plus its next endpoint. -/
structure FiveEdgePrefix (G : SimpleGraph V) where
  base : FourEdgePrefix G
  t : V
  zt : G.Adj base.z t
  t_not_mem : t ∉ ({base.v, base.u, base.x, base.y, base.z} : Finset V)
  vt_nonadj : ¬G.Adj base.v t
  ut_nonadj : ¬G.Adj base.u t
  xt_nonadj : ¬G.Adj base.x t
  yt_nonadj : ¬G.Adj base.y t

omit [Fintype V] [Nonempty V] in
/-- A shortest path of length at least five supplies a chordless five-edge
prefix. -/
lemma exists_fiveEdgePrefix_of_connected_of_five_le_dist
    (G : SimpleGraph V) (hconn : G.Connected) (v w : V)
    (hdist : 5 ≤ G.dist v w) :
    ∃ P : FiveEdgePrefix G, P.base.v = v := by
  obtain ⟨p, hpPath, hpLength⟩ := hconn.exists_path_of_dist v w
  have hlen : 5 ≤ p.length := by omega
  have hinj : Function.Injective (fun i : Fin p.support.length =>
      p.support.get i) := p.isPath_iff_injective_get_support.mp hpPath
  have hne (i j : Nat) (hi : i ≤ p.length) (hj : j ≤ p.length)
      (hij : i ≠ j) : p.getVert i ≠ p.getVert j := by
    intro heq
    have hi' : i < p.support.length := by simp [p.length_support, hi]
    have hj' : j < p.support.length := by simp [p.length_support, hj]
    have hget : p.support.get ⟨i, hi'⟩ = p.support.get ⟨j, hj'⟩ := by
      simpa [p.getVert_eq_support_getElem hi,
        p.getVert_eq_support_getElem hj] using heq
    exact hij (congrArg Fin.val (hinj hget))
  have hshortcut (i j : Nat) (hi : i ≤ p.length) (hj : j ≤ p.length)
      (hgap : i + 1 < j) : ¬G.Adj (p.getVert i) (p.getVert j) := by
    intro hadj
    let q : G.Walk v w :=
      ((p.take i).append hadj.toWalk).append (p.drop j)
    have hq := G.dist_le q
    have htake : (p.take i).length = i := by
      simp [Walk.take_length, hi]
    have hdrop : (p.drop j).length = p.length - j := by
      simp [Walk.drop_length]
    simp only [q, Walk.length_append, Walk.length_cons, Walk.length_nil,
      zero_add] at hq
    rw [htake, hdrop, ← hpLength] at hq
    omega
  let a0 := p.getVert 0
  let a1 := p.getVert 1
  let a2 := p.getVert 2
  let a3 := p.getVert 3
  let a4 := p.getVert 4
  let a5 := p.getVert 5
  have h01 := hne 0 1 (by omega) (by omega) (by omega)
  have h02 := hne 0 2 (by omega) (by omega) (by omega)
  have h03 := hne 0 3 (by omega) (by omega) (by omega)
  have h04 := hne 0 4 (by omega) (by omega) (by omega)
  have h05 := hne 0 5 (by omega) (by omega) (by omega)
  have h12 := hne 1 2 (by omega) (by omega) (by omega)
  have h13 := hne 1 3 (by omega) (by omega) (by omega)
  have h14 := hne 1 4 (by omega) (by omega) (by omega)
  have h15 := hne 1 5 (by omega) (by omega) (by omega)
  have h23 := hne 2 3 (by omega) (by omega) (by omega)
  have h24 := hne 2 4 (by omega) (by omega) (by omega)
  have h25 := hne 2 5 (by omega) (by omega) (by omega)
  have h34 := hne 3 4 (by omega) (by omega) (by omega)
  have h35 := hne 3 5 (by omega) (by omega) (by omega)
  have h45 := hne 4 5 (by omega) (by omega) (by omega)
  have hcard : ({a0, a1, a2, a3, a4} : Finset V).card = 5 := by
    simp only [a0, a1, a2, a3, a4, p.getVert_zero]
    rw [Finset.card_insert_of_notMem, Finset.card_insert_of_notMem,
      Finset.card_insert_of_notMem, Finset.card_insert_of_notMem]
    · simp
    · simpa only [Finset.mem_singleton] using h34
    · simpa only [Finset.mem_insert, Finset.mem_singleton, not_or] using
        ⟨h23, h24⟩
    · simpa only [Finset.mem_insert, Finset.mem_singleton, not_or] using
        ⟨h12, h13, h14⟩
    · simpa only [Finset.mem_insert, Finset.mem_singleton, not_or,
        p.getVert_zero] using
        (show v ≠ p.getVert 1 ∧ v ≠ p.getVert 2 ∧
          v ≠ p.getVert 3 ∧ v ≠ p.getVert 4 by
            exact ⟨by simpa [p.getVert_zero] using h01,
              by simpa [p.getVert_zero] using h02,
              by simpa [p.getVert_zero] using h03,
              by simpa [p.getVert_zero] using h04⟩)
  let B : FourEdgePrefix G := {
    v := a0, u := a1, x := a2, y := a3, z := a4
    vu := p.adj_getVert_succ (by omega : 0 < p.length)
    ux := p.adj_getVert_succ (by omega : 1 < p.length)
    xy := p.adj_getVert_succ (by omega : 2 < p.length)
    yz := p.adj_getVert_succ (by omega : 3 < p.length)
    pairwise := hcard
    vx_nonadj := hshortcut 0 2 (by omega) (by omega) (by omega)
    vy_nonadj := hshortcut 0 3 (by omega) (by omega) (by omega)
    vz_nonadj := hshortcut 0 4 (by omega) (by omega) (by omega)
    uy_nonadj := hshortcut 1 3 (by omega) (by omega) (by omega)
    uz_nonadj := hshortcut 1 4 (by omega) (by omega) (by omega)
    xz_nonadj := hshortcut 2 4 (by omega) (by omega) (by omega)
  }
  let P : FiveEdgePrefix G := {
    base := B
    t := a5
    zt := p.adj_getVert_succ (by omega : 4 < p.length)
    t_not_mem := by
      simp only [B, a0, a1, a2, a3, a4, a5, Finset.mem_insert,
        Finset.mem_singleton, not_or]
      exact ⟨h05.symm, h15.symm, h25.symm, h35.symm, h45.symm⟩
    vt_nonadj := hshortcut 0 5 (by omega) (by omega) (by omega)
    ut_nonadj := hshortcut 1 5 (by omega) (by omega) (by omega)
    xt_nonadj := hshortcut 2 5 (by omega) (by omega) (by omega)
    yt_nonadj := hshortcut 3 5 (by omega) (by omega) (by omega)
  }
  refine ⟨P, ?_⟩
  exact p.getVert_zero

/-- A fourth leaf attached uniquely to a verified three-tail tree. -/
structure FourthLeafData (G : SimpleGraph V) [DecidableRel G.Adj] where
  base : ThreeVertexTailSplice G
  fourth : V
  fourth_not_mem : fourth ∉ insert base.third
    (insert base.second (insert base.first (insert base.center base.localSet)))
  fourth_unique_base :
    ∀ q ∈ insert base.third
      (insert base.second (insert base.first (insert base.center base.localSet))),
      G.Adj fourth q ↔ q = base.third

omit [Nonempty V] in
lemma fourthLeaf_inducedTree
    (G : SimpleGraph V) [DecidableRel G.Adj] (D : FourthLeafData G) :
    (G.induce (↑(insert D.fourth (insert D.base.third
      (insert D.base.second (insert D.base.first
        (insert D.base.center D.base.localSet))))) : Set V)).IsTree := by
  let B : Finset V := insert D.base.third
    (insert D.base.second (insert D.base.first
      (insert D.base.center D.base.localSet)))
  let S : Finset V := insert D.fourth B
  let H := G.induce (↑S : Set V)
  let t : (S : Set V) := ⟨D.fourth, by simp [S]⟩
  have ht_unique : ∃! q : (S : Set V), H.Adj t q := by
    let z : (S : Set V) := ⟨D.base.third, by simp [S, B]⟩
    refine ⟨z, ?_, ?_⟩
    · apply SimpleGraph.induce_adj.mpr
      exact (D.fourth_unique_base D.base.third (by simp)).mpr rfl
    · intro q htq
      apply Subtype.ext
      have htqG : G.Adj D.fourth (q : V) := SimpleGraph.induce_adj.mp htq
      have hqS : (q : V) = D.fourth ∨ (q : V) ∈ B := by
        simpa [S] using q.property
      rcases hqS with hqt | hqB
      · exact (G.loopless D.fourth (hqt ▸ htqG)).elim
      · exact (D.fourth_unique_base q (by simpa [B] using hqB)).mp htqG
  have hbase : (H.induce ({t}ᶜ : Set (S : Set V))).IsTree := by
    let f : (↥({t}ᶜ : Set (S : Set V))) → (↥(↑B : Set V)) := fun q =>
      ⟨q.val.val, by
        have hqS : q.val.val = D.fourth ∨ q.val.val ∈ B := by
          simpa [S] using q.val.property
        rcases hqS with hqt | hqB
        · exfalso
          apply q.property
          apply Subtype.ext
          exact hqt
        · exact hqB⟩
    have hf_inj : Function.Injective f := by
      intro q q' h
      apply Subtype.ext
      apply Subtype.ext
      simpa [f] using congrArg Subtype.val h
    have hf_surj : Function.Surjective f := by
      intro q
      let qs : (S : Set V) := ⟨q, by
        change (q : V) ∈ insert D.fourth B
        exact Finset.mem_insert_of_mem q.property⟩
      have hqst : qs ≠ t := by
        intro h
        apply D.fourth_not_mem
        have hqfourth : (q : V) = D.fourth := congrArg Subtype.val h
        simpa [B, hqfourth] using q.property
      let q' : (↥({t}ᶜ : Set (S : Set V))) := ⟨qs, by
        simpa only [Set.mem_compl_iff, Set.mem_singleton_iff] using hqst⟩
      refine ⟨q', ?_⟩
      apply Subtype.ext
      rfl
    let e : (↥({t}ᶜ : Set (S : Set V))) ≃ (↥(↑B : Set V)) :=
      Equiv.ofBijective f ⟨hf_inj, hf_surj⟩
    let iso : H.induce ({t}ᶜ : Set (S : Set V)) ≃g
        G.induce (↑B : Set V) := {
      toEquiv := e
      map_rel_iff' := by intro q q'; rfl
    }
    apply iso.isTree_iff.mpr
    exact D.base.inducedTree
  simpa [H, S, B] using
    isTree_of_induce_compl_singleton_isTree_of_existsUnique_adj
      H t hbase ht_unique

omit [Nonempty V] in
lemma card_fourthLeafData
    (G : SimpleGraph V) [DecidableRel G.Adj] (D : FourthLeafData G) :
    (insert D.fourth (insert D.base.third
      (insert D.base.second (insert D.base.first
        (insert D.base.center D.base.localSet))))).card =
      Finset.univ.sup (indepNeighborsCard G) + 5 := by
  have hcenter : D.base.center ∉ D.base.localSet := by
    intro hc
    exact G.loopless D.base.center (by
      rw [← mem_neighborFinset]
      exact D.base.localSubset hc)
  rw [Finset.card_insert_of_notMem D.fourth_not_mem,
    Finset.card_insert_of_notMem D.base.third_not_mem,
    Finset.card_insert_of_notMem D.base.second_not_mem,
    Finset.card_insert_of_notMem D.base.first_not_mem,
    Finset.card_insert_of_notMem hcenter,
    D.base.localCard, D.base.centerMaximal]

omit [Nonempty V] in
theorem conjecture141_of_girth_twelve_or_thirteen_of_fourthLeafData
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hgirthLower : 12 ≤ G.girth) (hgirthUpper : G.girth ≤ 13)
    (D : FourthLeafData G) :
    (G.girth / 2 : ℤ) - 1 +
        ((Finset.univ.sup (indepNeighborsCard G) : ℕ) : ℤ) ≤
      (largestInducedTreeSize G : ℤ) := by
  have htree : (insert D.fourth (insert D.base.third
      (insert D.base.second (insert D.base.first
        (insert D.base.center D.base.localSet))))).card ≤
      G.largestInducedTreeSize :=
    card_le_largestInducedTreeSize G _ (fourthLeaf_inducedTree G D)
  rw [card_fourthLeafData G D] at htree
  have hhalf : G.girth / 2 ≤ 6 := by omega
  have htreeZ :
      ((Finset.univ.sup (indepNeighborsCard G) + 5 : ℕ) : ℤ) ≤
        (largestInducedTreeSize G : ℤ) := by exact_mod_cast htree
  have hhalfZ : ((G.girth / 2 : ℕ) : ℤ) ≤ 6 := by exact_mod_cast hhalf
  omega

omit [Nonempty V] in
/-- At girth at least twelve, the fifth endpoint has no edge back into the
initial open neighborhood.  Such an edge would close a seven-cycle. -/
lemma fifth_vertex_not_adj_neighborSet
    (G : SimpleGraph V) [DecidableRel G.Adj] (hgirth : 12 ≤ G.girth)
    (P : FiveEdgePrefix G) :
    ∀ a ∈ G.neighborFinset P.base.v, ¬G.Adj P.t a := by
  intro a ha hta
  have hva : G.Adj P.base.v a := by
    simpa [G.mem_neighborFinset] using ha
  obtain ⟨hvu, hvx, hvy, hvz, hux, huy, huz, hxy, hxz, hyz⟩ :=
    fourEdgePrefix_vertices_pairwise G P.base
  have ht := P.t_not_mem
  simp only [Finset.mem_insert, Finset.mem_singleton, not_or] at ht
  obtain ⟨htv, htu, htx, hty, htz⟩ := ht
  have hav : a ≠ P.base.v := hva.ne.symm
  have hau : a ≠ P.base.u := by
    intro h
    subst a
    exact P.ut_nonadj hta.symm
  have hax : a ≠ P.base.x := by
    intro h
    subst a
    exact P.xt_nonadj hta.symm
  have hay : a ≠ P.base.y := by
    intro h
    subst a
    exact P.yt_nonadj hta.symm
  have haz : a ≠ P.base.z := by
    intro h
    subst a
    exact P.base.vz_nonadj hva
  have hat : a ≠ P.t := hta.ne.symm
  have huv := hvu.symm
  have hxv := hvx.symm
  have hyv := hvy.symm
  have hzv := hvz.symm
  have hxu := hux.symm
  have hyu := huy.symm
  have hzu := huz.symm
  have hyx := hxy.symm
  have hzx := hxz.symm
  have hzy := hyz.symm
  have hvt : P.base.v ≠ P.t := fun h => htv h.symm
  have hut : P.base.u ≠ P.t := fun h => htu h.symm
  have hxt : P.base.x ≠ P.t := fun h => htx h.symm
  have hyt : P.base.y ≠ P.t := fun h => hty h.symm
  have hzt : P.base.z ≠ P.t := fun h => htz h.symm
  have hva' : P.base.v ≠ a := fun h => hav h.symm
  have hua : P.base.u ≠ a := fun h => hau h.symm
  have hxa : P.base.x ≠ a := fun h => hax h.symm
  have hya : P.base.y ≠ a := fun h => hay h.symm
  have hza : P.base.z ≠ a := fun h => haz h.symm
  have hta' : P.t ≠ a := fun h => hat h.symm
  let c : G.Walk P.base.v P.base.v :=
    .cons P.base.vu (.cons P.base.ux (.cons P.base.xy
      (.cons P.base.yz (.cons P.zt (.cons hta
        (.cons hva.symm .nil))))))
  have hc : c.IsCycle := by
    simp_all [c, Walk.isCycle_def, Walk.isTrail_def]
  have hshort := G.girth_le_length hc
  simp only [c, Walk.length_cons, Walk.length_nil] at hshort
  omega

/-- The five-edge prefix constructs the complete fourth-leaf certificate. -/
noncomputable def fourthLeafDataOfFiveEdgePrefix
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hgirth : 12 ≤ G.girth) (P : FiveEdgePrefix G)
    (hvmax : indepNeighborsCard G P.base.v =
      Finset.univ.sup (indepNeighborsCard G)) :
    FourthLeafData G := by
  obtain ⟨hvu, hvx, hvy, hvz, hux, huy, huz, hxy, hxz, hyz⟩ :=
    fourEdgePrefix_vertices_pairwise G P.base
  let A := G.neighborFinset P.base.v
  let D1 : DistanceTwoLeafData G := {
    center := P.base.v
    localSet := A
    extra := P.base.x
    attachment := P.base.u
    localIndependent := by
      simpa [A, ← coe_neighborFinset] using
        locallyIndependent_of_six_le_girth G (by omega) P.base.v
    localSubset := Finset.Subset.rfl
    localCard := by
      change (G.neighborFinset P.base.v).card =
        indepNeighborsCard G P.base.v
      rw [G.card_neighborFinset_eq_degree]
      exact (indepNeighborsCard_eq_degree_of_independent_neighborhood
        G P.base.v (locallyIndependent_of_six_le_girth
          G (by omega) P.base.v)).symm
    centerMaximal := hvmax
    attachment_mem := by simpa [A, G.mem_neighborFinset] using P.base.vu
    extra_not_mem := by
      simp only [Finset.mem_insert, not_or]
      refine ⟨hvx.symm, ?_⟩
      intro hxA
      exact P.base.vx_nonadj (by simpa [A, G.mem_neighborFinset] using hxA)
    center_extra_nonadj := P.base.vx_nonadj
    extra_unique_local := by
      intro a ha
      constructor
      · intro hxa
        apply unique_neighbor_attachment_of_six_le_girth
          G (by omega) P.base.vu P.base.ux hvx.symm a
        · simpa [A, G.mem_neighborFinset] using ha
        · exact hxa
      · intro hau'
        subst a
        exact P.base.ux.symm
  }
  let D2 : SecondLeafData G := {
    base := D1
    second := P.base.y
    second_not_mem := by
      change P.base.y ∉ insert P.base.x
        (insert P.base.v (G.neighborFinset P.base.v))
      simp only [Finset.mem_insert, not_or]
      refine ⟨hxy.symm, hvy.symm, ?_⟩
      intro hyN
      exact P.base.vy_nonadj (by simpa [G.mem_neighborFinset] using hyN)
    second_unique_base := by
      intro q hq
      change q ∈ insert P.base.x
        (insert P.base.v (G.neighborFinset P.base.v)) at hq
      change G.Adj P.base.y q ↔ q = P.base.x
      simp only [Finset.mem_insert] at hq
      rcases hq with rfl | rfl | hqN
      · exact ⟨fun _ => rfl, fun _ => P.base.xy.symm⟩
      · exact ⟨fun h => (P.base.vy_nonadj h.symm).elim,
          fun h => (hvx h).elim⟩
      · constructor
        · intro hyq
          exact (third_vertex_not_adj_neighborSet G (by omega)
            P.base.vu P.base.ux P.base.xy hvu hvx hvy hux huy hxy
            P.base.vx_nonadj P.base.vy_nonadj P.base.uy_nonadj
            q hqN hyq).elim
        · intro hqx
          subst q
          exact P.base.xy.symm
  }
  let D3 : ThirdLeafData G := {
    base := D2.toTwoVertexTailSplice G
    third := P.base.z
    third_not_mem := by
      change P.base.z ∉ insert P.base.y (insert P.base.x
        (insert P.base.v (G.neighborFinset P.base.v)))
      simp only [Finset.mem_insert, not_or]
      refine ⟨hyz.symm, hxz.symm, hvz.symm, ?_⟩
      intro hzN
      exact P.base.vz_nonadj (by simpa [G.mem_neighborFinset] using hzN)
    third_unique_base := by
      intro q hq
      change q ∈ insert P.base.y (insert P.base.x
        (insert P.base.v (G.neighborFinset P.base.v))) at hq
      change G.Adj P.base.z q ↔ q = P.base.y
      simp only [Finset.mem_insert] at hq
      rcases hq with rfl | rfl | rfl | hqN
      · exact ⟨fun _ => rfl, fun _ => P.base.yz.symm⟩
      · exact ⟨fun h => (P.base.xz_nonadj h.symm).elim,
          fun h => (hxy h).elim⟩
      · exact ⟨fun h => (P.base.vz_nonadj h.symm).elim,
          fun h => (hvy h).elim⟩
      · constructor
        · intro hzq
          exact (fourth_vertex_not_adj_neighborSet G (by omega)
            P.base q hqN hzq).elim
        · intro hqy
          subst q
          exact P.base.yz.symm
  }
  let B3 := D3.toThreeVertexTailSplice G
  have ht := P.t_not_mem
  simp only [Finset.mem_insert, Finset.mem_singleton, not_or] at ht
  obtain ⟨htv, _htu, htx, hty, htz⟩ := ht
  refine {
    base := B3
    fourth := P.t
    fourth_not_mem := ?_
    fourth_unique_base := ?_
  }
  · have hraw : P.t ∉ insert P.base.z (insert P.base.y
        (insert P.base.x (insert P.base.v
          (G.neighborFinset P.base.v)))) := by
      simp only [Finset.mem_insert, not_or]
      refine ⟨htz, hty, htx, htv, ?_⟩
      intro htN
      exact P.vt_nonadj (by simpa [G.mem_neighborFinset] using htN)
    simpa [B3, D3, D2, D1, A, ThirdLeafData.toThreeVertexTailSplice,
      SecondLeafData.toTwoVertexTailSplice] using hraw
  · intro q hq
    have hqRaw : q ∈ insert P.base.z (insert P.base.y
        (insert P.base.x (insert P.base.v
          (G.neighborFinset P.base.v)))) := by
      simpa [B3, D3, D2, D1, A, ThirdLeafData.toThreeVertexTailSplice,
        SecondLeafData.toTwoVertexTailSplice] using hq
    have hraw : G.Adj P.t q ↔ q = P.base.z := by
      simp only [Finset.mem_insert] at hqRaw
      rcases hqRaw with rfl | rfl | rfl | rfl | hqN
      · exact ⟨fun _ => rfl, fun _ => P.zt.symm⟩
      · exact ⟨fun h => (P.yt_nonadj h.symm).elim,
          fun h => (hyz h).elim⟩
      · exact ⟨fun h => (P.xt_nonadj h.symm).elim,
          fun h => (hxz h).elim⟩
      · exact ⟨fun h => (P.vt_nonadj h.symm).elim,
          fun h => (hvz h).elim⟩
      · constructor
        · intro htq
          exact (fifth_vertex_not_adj_neighborSet G hgirth P q hqN htq).elim
        · intro hqz
          subst q
          exact P.zt.symm
    simpa [B3, D3, D2, D1, A, ThirdLeafData.toThreeVertexTailSplice,
      SecondLeafData.toTwoVertexTailSplice] using hraw

/-- **Unconditional girth-twelve/thirteen closure.** -/
theorem conjecture141_of_girth_twelve_or_thirteen
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hconn : G.Connected)
    (hgirthLower : 12 ≤ G.girth) (hgirthUpper : G.girth ≤ 13) :
    (G.girth / 2 : ℤ) - 1 +
        ((Finset.univ.sup (indepNeighborsCard G) : ℕ) : ℤ) ≤
      (largestInducedTreeSize G : ℤ) := by
  obtain ⟨v, hvmax⟩ := exists_maximum_local_center G
  have hfive := everyVertexHasDistanceAtLeastFive_of_connected_of_ten_le_girth
    G hconn (by omega)
  obtain ⟨w, hvw⟩ := hfive v
  obtain ⟨P, hpv⟩ :=
    exists_fiveEdgePrefix_of_connected_of_five_le_dist G hconn v w hvw
  have hPmax : indepNeighborsCard G P.base.v =
      Finset.univ.sup (indepNeighborsCard G) := by
    simpa [hpv] using hvmax
  let D := fourthLeafDataOfFiveEdgePrefix G hgirthLower P hPmax
  exact conjecture141_of_girth_twelve_or_thirteen_of_fourthLeafData
    G hgirthLower hgirthUpper D

/-- **WOWII 141 is closed unconditionally through girth thirteen.** -/
theorem conjecture141_of_girth_le_thirteen
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hconn : G.Connected) (hgirth : G.girth ≤ 13) :
    (G.girth / 2 : ℤ) - 1 +
        ((Finset.univ.sup (indepNeighborsCard G) : ℕ) : ℤ) ≤
      (largestInducedTreeSize G : ℤ) := by
  by_cases heleven : G.girth ≤ 11
  · exact conjecture141_of_girth_le_eleven G hconn heleven
  · exact conjecture141_of_girth_twelve_or_thirteen
      G hconn (by omega) hgirth

end WrittenOnTheWallII.GraphConjecture141GirthThirteenClosure
