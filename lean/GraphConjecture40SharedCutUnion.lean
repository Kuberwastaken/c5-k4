import GraphConjecture40SeparatedUnion

/-!
# WOWII 40: unions meeting in one cut vertex

This file proves the cycle-localization lemma needed for the include-cut
dynamic-programming state. Two acyclic induced subgraphs which meet only at a
common cut vertex, with no other cross edges, have acyclic induced union.
-/

namespace WrittenOnTheWallII.GraphConjecture40SharedCutUnion

open SimpleGraph Finset

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

omit [Fintype V] in
/-- A simple path ending at the shared cut cannot leave the left side. -/
lemma Walk.support_subset_left_of_no_cross_to_cut
    (G : SimpleGraph V) (A B : Finset V) (c : V)
    (hcA : c ∈ A)
    (hcross : ∀ a ∈ A, a ≠ c → ∀ b ∈ B, b ≠ c → ¬G.Adj a b)
    {u v : ↥(↑(A ∪ B) : Set V)}
    (p : (G.induce (↑(A ∪ B) : Set V)).Walk u v)
    (hv : v.1 = c) (hp : p.IsPath) (hu : u.1 ∈ A) :
    ∀ z ∈ p.support, z.1 ∈ A := by
  induction p with
  | nil => simpa using hu
  | @cons u w v huw p ih =>
      have hu_ne : u.1 ≠ c := by
        intro huc
        have huv : u = v := Subtype.ext (huc.trans hv.symm)
        subst v
        have hpnil := (Walk.isPath_iff_eq_nil (Walk.cons huw p)).mp hp
        simp at hpnil
      have hwAB : w.1 ∈ A ∨ w.1 ∈ B := mem_union.mp w.property
      have hwA : w.1 ∈ A := by
        rcases hwAB with hwA | hwB
        · exact hwA
        · by_cases hwc : w.1 = c
          · simpa [hwc] using hcA
          · exact (hcross u.1 hu hu_ne w.1 hwB hwc huw).elim
      intro z hz
      simp only [Walk.support_cons, List.mem_cons] at hz
      rcases hz with rfl | hz
      · exact hu
      · exact ih hv hp.of_cons hwA z hz

omit [Fintype V] in
/-- A simple path ending at the shared cut cannot leave the right side. -/
lemma Walk.support_subset_right_of_no_cross_to_cut
    (G : SimpleGraph V) (A B : Finset V) (c : V)
    (hcB : c ∈ B)
    (hcross : ∀ a ∈ A, a ≠ c → ∀ b ∈ B, b ≠ c → ¬G.Adj a b)
    {u v : ↥(↑(A ∪ B) : Set V)}
    (p : (G.induce (↑(A ∪ B) : Set V)).Walk u v)
    (hv : v.1 = c) (hp : p.IsPath) (hu : u.1 ∈ B) :
    ∀ z ∈ p.support, z.1 ∈ B := by
  induction p with
  | nil => simpa using hu
  | @cons u w v huw p ih =>
      have hu_ne : u.1 ≠ c := by
        intro huc
        have huv : u = v := Subtype.ext (huc.trans hv.symm)
        subst v
        have hpnil := (Walk.isPath_iff_eq_nil (Walk.cons huw p)).mp hp
        simp at hpnil
      have hwAB : w.1 ∈ A ∨ w.1 ∈ B := mem_union.mp w.property
      have hwB : w.1 ∈ B := by
        rcases hwAB with hwA | hwB
        · by_cases hwc : w.1 = c
          · simpa [hwc] using hcB
          · exact (hcross w.1 hwA hwc u.1 hu hu_ne huw.symm).elim
        · exact hwB
      intro z hz
      simp only [Walk.support_cons, List.mem_cons] at hz
      rcases hz with rfl | hz
      · exact hu
      · exact ih hv hp.of_cons hwB z hz

omit [Fintype V] in
/-- If the cut does not occur on a walk, a walk beginning on the left stays
on the left. -/
lemma Walk.support_subset_left_of_no_cross_avoiding_cut
    (G : SimpleGraph V) (A B : Finset V) (c : V)
    (hcross : ∀ a ∈ A, a ≠ c → ∀ b ∈ B, b ≠ c → ¬G.Adj a b)
    {u v : ↥(↑(A ∪ B) : Set V)}
    (p : (G.induce (↑(A ∪ B) : Set V)).Walk u v)
    (hc : ∀ z ∈ p.support, z.1 ≠ c) (hu : u.1 ∈ A) :
    ∀ z ∈ p.support, z.1 ∈ A := by
  induction p with
  | nil => simpa using hu
  | @cons u w v huw p ih =>
      have hu_ne : u.1 ≠ c := hc u (by simp)
      have hw_ne : w.1 ≠ c := hc w (by simp)
      have hwAB : w.1 ∈ A ∨ w.1 ∈ B := mem_union.mp w.property
      have hwA : w.1 ∈ A := by
        rcases hwAB with hwA | hwB
        · exact hwA
        · exact (hcross u.1 hu hu_ne w.1 hwB hw_ne huw).elim
      intro z hz
      simp only [Walk.support_cons, List.mem_cons] at hz
      rcases hz with rfl | hz
      · exact hu
      · exact ih (fun z hz => hc z (by simp [hz])) hwA z hz

omit [Fintype V] in
/-- Right-side version of cut-avoiding walk localization. -/
lemma Walk.support_subset_right_of_no_cross_avoiding_cut
    (G : SimpleGraph V) (A B : Finset V) (c : V)
    (hcross : ∀ a ∈ A, a ≠ c → ∀ b ∈ B, b ≠ c → ¬G.Adj a b)
    {u v : ↥(↑(A ∪ B) : Set V)}
    (p : (G.induce (↑(A ∪ B) : Set V)).Walk u v)
    (hc : ∀ z ∈ p.support, z.1 ≠ c) (hu : u.1 ∈ B) :
    ∀ z ∈ p.support, z.1 ∈ B := by
  induction p with
  | nil => simpa using hu
  | @cons u w v huw p ih =>
      have hu_ne : u.1 ≠ c := hc u (by simp)
      have hw_ne : w.1 ≠ c := hc w (by simp)
      have hwAB : w.1 ∈ A ∨ w.1 ∈ B := mem_union.mp w.property
      have hwB : w.1 ∈ B := by
        rcases hwAB with hwA | hwB
        · exact (hcross w.1 hwA hw_ne u.1 hu hu_ne huw.symm).elim
        · exact hwB
      intro z hz
      simp only [Walk.support_cons, List.mem_cons] at hz
      rcases hz with rfl | hz
      · exact hu
      · exact ih (fun z hz => hc z (by simp [hz])) hwB z hz

omit [Fintype V] [DecidableEq V] in
/-- A cycle supported inside an acyclic induced side is impossible. -/
lemma cycle_false_of_support_subset
    (G : SimpleGraph V) (A U : Finset V)
    (hA : (G.induce (↑A : Set V)).IsAcyclic)
    {v : ↥(↑U : Set V)} (p : (G.induce (↑U : Set V)).Walk v v)
    (hp : p.IsCycle) (hs : ∀ z ∈ p.support, z.1 ∈ A) : False := by
  let f : p.toSubgraph.coe →g G.induce (↑A : Set V) :=
    { toFun := fun z => ⟨z.1.1, hs z.1 (p.mem_verts_toSubgraph.mp z.2)⟩
      map_rel' := fun hadj => p.toSubgraph.coe_adj_sub _ _ hadj }
  have hf : Function.Injective f := by
    intro x y h
    have h' := congrArg Subtype.val h
    change x.1.1 = y.1.1 at h'
    exact Subtype.ext (Subtype.ext h')
  have hpSub : p.mapToSubgraph.IsCycle := by
    apply (Walk.map_isCycle_iff_of_injective SimpleGraph.Subgraph.hom_injective).mp
    rw [Walk.map_mapToSubgraph_hom]
    exact hp
  exact hA (p.mapToSubgraph.map f) (hpSub.map hf)

omit [Fintype V] in
/-- Two induced forests glued only at a shared cut vertex remain acyclic. -/
theorem induce_union_isAcyclic_of_shared_cut
    (G : SimpleGraph V) (A B : Finset V) (c : V)
    (hcA : c ∈ A) (hcB : c ∈ B)
    (hcross : ∀ a ∈ A, a ≠ c → ∀ b ∈ B, b ≠ c → ¬G.Adj a b)
    (hA : (G.induce (↑A : Set V)).IsAcyclic)
    (hB : (G.induce (↑B : Set V)).IsAcyclic) :
    (G.induce (↑(A ∪ B) : Set V)).IsAcyclic := by
  intro v p hp
  let cv : ↥(↑(A ∪ B) : Set V) := ⟨c, mem_union_left B hcA⟩
  by_cases hcv : cv ∈ p.support
  · let q := p.rotate hcv
    have hq : q.IsCycle := hp.rotate hcv
    generalize hqe : q = q' at hq
    cases q' with
    | nil => exact hq.not_nil Walk.nil_nil
    | @cons u w v huw qtail =>
        have hpath : qtail.IsPath := (Walk.cons_isCycle_iff qtail huw).mp hq |>.1
        have hwAB : w.1 ∈ A ∨ w.1 ∈ B := mem_union.mp w.property
        rcases hwAB with hwA | hwB
        · have htail := Walk.support_subset_left_of_no_cross_to_cut
            G A B c hcA hcross qtail rfl hpath hwA
          have hs : ∀ z ∈ (Walk.cons huw qtail).support, z.1 ∈ A := by
            intro z hz
            simp only [Walk.support_cons, List.mem_cons] at hz
            rcases hz with rfl | hz
            · exact hcA
            · exact htail z hz
          exact cycle_false_of_support_subset G A (A ∪ B) hA
            (Walk.cons huw qtail) hq hs
        · have htail := Walk.support_subset_right_of_no_cross_to_cut
            G A B c hcB hcross qtail rfl hpath hwB
          have hs : ∀ z ∈ (Walk.cons huw qtail).support, z.1 ∈ B := by
            intro z hz
            simp only [Walk.support_cons, List.mem_cons] at hz
            rcases hz with rfl | hz
            · exact hcB
            · exact htail z hz
          exact cycle_false_of_support_subset G B (A ∪ B) hB
            (Walk.cons huw qtail) hq hs
  · have hcavoid : ∀ z ∈ p.support, z.1 ≠ c := by
      intro z hz hzc
      apply hcv
      have : z = cv := Subtype.ext hzc
      simpa [this] using hz
    have hvAB : v.1 ∈ A ∨ v.1 ∈ B := mem_union.mp v.property
    rcases hvAB with hvA | hvB
    · have hs := Walk.support_subset_left_of_no_cross_avoiding_cut
        G A B c hcross p hcavoid hvA
      exact cycle_false_of_support_subset G A (A ∪ B) hA p hp hs
    · have hs := Walk.support_subset_right_of_no_cross_avoiding_cut
        G A B c hcross p hcavoid hvB
      exact cycle_false_of_support_subset G B (A ∪ B) hB p hp hs

open WrittenOnTheWallII.GraphConjecture40OneVertexSeparation

/-- Maximum order of an induced forest constrained to a side and required to
contain the designated cut vertex. -/
noncomputable def forestOrderWithinIncluding
    (G : SimpleGraph V) (A : Finset V) (c : V) : ℕ :=
  sSup {n | ∃ S : Finset V, S ⊆ A ∧
    (G.induce (S : Set V)).IsAcyclic ∧ c ∈ S ∧ S.card = n}

omit [Fintype V] in
lemma exists_forestOrderWithinIncluding_witness
    (G : SimpleGraph V) (A : Finset V) (c : V) (hcA : c ∈ A) :
    ∃ S : Finset V, S ⊆ A ∧ (G.induce (S : Set V)).IsAcyclic ∧ c ∈ S ∧
      S.card = forestOrderWithinIncluding G A c := by
  let X : Set ℕ := {n | ∃ S : Finset V, S ⊆ A ∧
    (G.induce (S : Set V)).IsAcyclic ∧ c ∈ S ∧ S.card = n}
  have hne : X.Nonempty := by
    refine ⟨1, {c}, by simpa, ?_, by simp, by simp⟩
    exact GraphConjecture40Baseline.induce_insert_isAcyclic_of_indep
      G ∅ c (by simp)
  have hbdd : BddAbove X := ⟨A.card, fun n hn ↦ by
    obtain ⟨S, hSA, -, -, rfl⟩ := hn
    exact card_le_card hSA⟩
  obtain ⟨S, hSA, hS, hc, hcard⟩ := Nat.sSup_mem hne hbdd
  exact ⟨S, hSA, hS, hc,
    by simpa [forestOrderWithinIncluding, X] using hcard⟩

omit [Fintype V] [DecidableEq V] in
lemma card_le_forestOrderWithinIncluding
    (G : SimpleGraph V) (A : Finset V) (c : V) (S : Finset V)
    (hSA : S ⊆ A) (hS : (G.induce (S : Set V)).IsAcyclic) (hc : c ∈ S) :
    S.card ≤ forestOrderWithinIncluding G A c := by
  unfold forestOrderWithinIncluding
  apply le_csSup
  · exact ⟨A.card, fun n hn ↦ by
      obtain ⟨T, hTA, -, -, rfl⟩ := hn
      exact card_le_card hTA⟩
  · exact ⟨S, hSA, hS, hc, rfl⟩

namespace OneVertexSeparation

variable {G : SimpleGraph V}

/-- A global forest containing the cut restricts to the two include-state
side forests; inclusion-exclusion counts their shared cut once. -/
theorem forestOrderIncluding_add_one_le_sum_withinIncluding
    (D : OneVertexSeparation G) :
    GraphConjecture40CutVertexSum.forestOrderIncluding G D.cut + 1 ≤
      forestOrderWithinIncluding G D.left D.cut +
        forestOrderWithinIncluding G D.right D.cut := by
  obtain ⟨S, hS, hc, hcard⟩ :=
    GraphConjecture40CutVertexSum.exists_forestOrderIncluding_witness G D.cut
  let SL := S ∩ D.left
  let SR := S ∩ D.right
  have hSLsub : SL ⊆ D.left := inter_subset_right
  have hSRsub : SR ⊆ D.right := inter_subset_right
  have hSLacyc : (G.induce (SL : Set V)).IsAcyclic := by
    exact hS.embedding (G.induceHomOfLE (by
      intro x hx
      exact (mem_inter.mp hx).1))
  have hSRacyc : (G.induce (SR : Set V)).IsAcyclic := by
    exact hS.embedding (G.induceHomOfLE (by
      intro x hx
      exact (mem_inter.mp hx).1))
  have hcSL : D.cut ∈ SL := mem_inter.mpr ⟨hc, D.cut_mem_left⟩
  have hcSR : D.cut ∈ SR := mem_inter.mpr ⟨hc, D.cut_mem_right⟩
  have hleft := card_le_forestOrderWithinIncluding G D.left D.cut SL
    hSLsub hSLacyc hcSL
  have hright := card_le_forestOrderWithinIncluding G D.right D.cut SR
    hSRsub hSRacyc hcSR
  have hunion : SL ∪ SR = S := by
    dsimp [SL, SR]
    ext x
    have hxcover : x ∈ D.left ∨ x ∈ D.right := by
      exact mem_union.mp (by rw [D.cover]; simp)
    simp only [mem_union, mem_inter]
    tauto
  have hinter : SL ∩ SR = {D.cut} := by
    ext x
    constructor
    · intro hx
      have hxLR : x ∈ D.left ∩ D.right :=
        mem_inter.mpr ⟨(mem_inter.mp (mem_inter.mp hx).1).2,
          (mem_inter.mp (mem_inter.mp hx).2).2⟩
      simpa [D.inter] using hxLR
    · intro hx
      have hxc : x = D.cut := by simpa using hx
      subst x
      exact mem_inter.mpr ⟨hcSL, hcSR⟩
  have hcards := card_union_add_card_inter SL SR
  rw [hunion, hinter, card_singleton, hcard] at hcards
  omega

/-- Side include-state witnesses glue through the common cut to give a global
including forest. -/
theorem sum_withinIncluding_le_forestOrderIncluding_add_one
    (D : OneVertexSeparation G) :
    forestOrderWithinIncluding G D.left D.cut +
        forestOrderWithinIncluding G D.right D.cut ≤
      GraphConjecture40CutVertexSum.forestOrderIncluding G D.cut + 1 := by
  obtain ⟨A, hAL, hAacyc, hcA, hAcard⟩ :=
    exists_forestOrderWithinIncluding_witness G D.left D.cut D.cut_mem_left
  obtain ⟨B, hBR, hBacyc, hcB, hBcard⟩ :=
    exists_forestOrderWithinIncluding_witness G D.right D.cut D.cut_mem_right
  have hinter : A ∩ B = {D.cut} := by
    ext x
    constructor
    · intro hx
      have hxLR : x ∈ D.left ∩ D.right :=
        mem_inter.mpr ⟨hAL (mem_inter.mp hx).1, hBR (mem_inter.mp hx).2⟩
      simpa [D.inter] using hxLR
    · intro hx
      have hxc : x = D.cut := by simpa using hx
      subst x
      exact mem_inter.mpr ⟨hcA, hcB⟩
  have hcross : ∀ a ∈ A, a ≠ D.cut → ∀ b ∈ B, b ≠ D.cut →
      ¬G.Adj a b := by
    intro a ha hac b hb hbc
    exact D.no_cross a (hAL ha) hac b (hBR hb) hbc
  have hacyc := induce_union_isAcyclic_of_shared_cut G A B D.cut
    hcA hcB hcross hAacyc hBacyc
  have hglobal := GraphConjecture40CutVertexSum.card_le_forestOrderIncluding
    G D.cut (A ∪ B) hacyc (mem_union_left B hcA)
  have hcards := card_union_add_card_inter A B
  rw [hinter, card_singleton, hAcard, hBcard] at hcards
  omega

/-- Exact include-cut state formula for a one-vertex separation. -/
theorem forestOrderIncluding_add_one_eq_sum_withinIncluding
    (D : OneVertexSeparation G) :
    GraphConjecture40CutVertexSum.forestOrderIncluding G D.cut + 1 =
      forestOrderWithinIncluding G D.left D.cut +
        forestOrderWithinIncluding G D.right D.cut := by
  exact le_antisymm (forestOrderIncluding_add_one_le_sum_withinIncluding D)
    (sum_withinIncluding_le_forestOrderIncluding_add_one D)

end OneVertexSeparation

end WrittenOnTheWallII.GraphConjecture40SharedCutUnion
