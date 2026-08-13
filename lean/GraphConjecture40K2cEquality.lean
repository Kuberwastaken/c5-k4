import FormalConjecturesUtil

/-!
# WOWII 40: the `K_{2,c}` equality manifold

The cut-pair fusion search isolates complete bipartite graphs `K_{2,c}` as an
exact equality family for WOWII Conjecture 40.  This file proves from the
graph definitions that

* the largest induced forest has order `c + 1`, and
* the largest induced bipartite subgraph has the full order `c + 2`.

The current `pathCoverNumber` API is only an `sInf` definition and has no
lower-bound principle for bipartition imbalance.  Accordingly the final
source-shape equality theorem exposes the remaining exact fact
`pathCoverNumber K_{2,c} = c - 2` as a certificate premise.  No part of that
fact is silently assumed in the structural invariant lemmas.
-/

namespace WrittenOnTheWallII.GraphConjecture40K2cEquality

open SimpleGraph Finset

private lemma card_le_largestInducedForestSize
    {V : Type*} [Fintype V] (G : SimpleGraph V) (S : Finset V)
    (hS : (G.induce (S : Set V)).IsAcyclic) :
    S.card ≤ G.largestInducedForestSize := by
  unfold largestInducedForestSize
  apply le_csSup
  · exact ⟨Fintype.card V, fun n hn ↦ by
      obtain ⟨T, -, rfl⟩ := hn
      exact T.card_le_univ⟩
  · exact ⟨S, hS, rfl⟩

private lemma exists_largestInducedForestSize_witness
    {V : Type*} [Fintype V] (G : SimpleGraph V) :
    ∃ S : Finset V,
      (G.induce (S : Set V)).IsAcyclic ∧
      S.card = G.largestInducedForestSize := by
  let A : Set ℕ :=
    {n | ∃ S : Finset V, (G.induce (S : Set V)).IsAcyclic ∧ S.card = n}
  have hAne : A.Nonempty := by
    refine ⟨0, ∅, ?_, rfl⟩
    intro v
    have hv : False := by simpa using v.property
    exact hv.elim
  have hAbdd : BddAbove A := by
    exact ⟨Fintype.card V, fun n hn ↦ by
      obtain ⟨S, -, rfl⟩ := hn
      exact S.card_le_univ⟩
  have hmem : sSup A ∈ A := Nat.sSup_mem hAne hAbdd
  obtain ⟨S, hS, hcard⟩ := hmem
  exact ⟨S, hS, by simpa [largestInducedForestSize, A] using hcard⟩

private lemma largestInducedForestSize_lt_card_of_not_isAcyclic
    {V : Type*} [Fintype V] (G : SimpleGraph V)
    (hcyclic : ¬G.IsAcyclic) :
    G.largestInducedForestSize < Fintype.card V := by
  have hle : G.largestInducedForestSize ≤ Fintype.card V := by
    unfold largestInducedForestSize
    apply csSup_le
    · refine ⟨0, ∅, ?_, rfl⟩
      intro v
      simpa using v.property
    · rintro n ⟨S, -, rfl⟩
      exact S.card_le_univ
  apply lt_of_le_of_ne hle
  intro heq
  obtain ⟨S, hS, hcard⟩ := exists_largestInducedForestSize_witness G
  have hSuniv : S = Finset.univ := by
    apply Finset.eq_univ_of_card
    simp [hcard, heq]
  apply hcyclic
  subst S
  have hInd : (G.induce Set.univ).IsAcyclic := by
    have hset :
        ((↑(Finset.univ : Finset V) : Set V)) = Set.univ := by
      ext x
      simp
    rw [← hset]
    exact hS
  exact (SimpleGraph.induceUnivIso G).isAcyclic_iff.mp hInd

private lemma largestInducedBipartiteSubgraphSize_le_card
    {V : Type*} [Fintype V] [DecidableEq V] (G : SimpleGraph V) :
    G.largestInducedBipartiteSubgraphSize ≤ Fintype.card V := by
  unfold largestInducedBipartiteSubgraphSize
  apply csSup_le
  · refine ⟨0, ∅, ?_, rfl⟩
    rw [induce_isBipartite_iff_exists_coloring]
    exact ⟨fun _ ↦ 0, by simp⟩
  · rintro n ⟨S, -, rfl⟩
    exact S.card_le_univ

private lemma card_le_largestInducedBipartiteSubgraphSize
    {V : Type*} [Fintype V] (G : SimpleGraph V) (S : Finset V)
    (hS : (G.induce (S : Set V)).IsBipartite) :
    S.card ≤ G.largestInducedBipartiteSubgraphSize := by
  unfold largestInducedBipartiteSubgraphSize
  apply le_csSup
  · exact ⟨Fintype.card V, fun n hn ↦ by
      obtain ⟨T, -, rfl⟩ := hn
      exact T.card_le_univ⟩
  · exact ⟨S, hS, rfl⟩

private lemma isAcyclic_of_independent_parts_of_left_unique_neighbor
    {V : Type*} {G : SimpleGraph V} (I X : Set V)
    (hcover : I ∪ X = Set.univ)
    (hI : G.IsIndepSet I) (hX : G.IsIndepSet X)
    (huniq : ∀ i ∈ I, ∀ x ∈ X, ∀ y ∈ X,
      G.Adj i x → G.Adj i y → x = y) :
    G.IsAcyclic := by
  intro v p hp
  have hlen : 3 ≤ p.length := hp.three_le_length
  have hvs : G.Adj v p.snd := p.adj_snd hp.not_nil
  have hvp : G.Adj v p.penultimate := (p.adj_penultimate hp.not_nil).symm
  have hv_mem : v ∈ I ∨ v ∈ X := by
    have : v ∈ I ∪ X := by rw [hcover]; trivial
    simpa only [Set.mem_union] using this
  rcases hv_mem with hvI | hvX
  · have hsX : p.snd ∈ X := by
      have hs : p.snd ∈ I ∨ p.snd ∈ X := by
        have : p.snd ∈ I ∪ X := by rw [hcover]; trivial
        simpa only [Set.mem_union] using this
      exact hs.resolve_left (fun hsI ↦ hI hvI hsI hvs.ne hvs)
    have hpX : p.penultimate ∈ X := by
      have hpen : p.penultimate ∈ I ∨ p.penultimate ∈ X := by
        have : p.penultimate ∈ I ∪ X := by rw [hcover]; trivial
        simpa only [Set.mem_union] using this
      exact hpen.resolve_left (fun hpI ↦ hI hvI hpI hvp.ne hvp)
    exact hp.snd_ne_penultimate
      (huniq v hvI p.snd hsX p.penultimate hpX hvs hvp)
  · have hsI : p.snd ∈ I := by
      have hs : p.snd ∈ I ∨ p.snd ∈ X := by
        have : p.snd ∈ I ∪ X := by rw [hcover]; trivial
        simpa only [Set.mem_union] using this
      exact hs.resolve_right (fun hsX ↦ hX hvX hsX hvs.ne hvs)
    have h12 : G.Adj p.snd (p.getVert 2) := by
      simpa using p.adj_getVert_succ (by omega : 1 < p.length)
    have h2X : p.getVert 2 ∈ X := by
      have h2 : p.getVert 2 ∈ I ∨ p.getVert 2 ∈ X := by
        have : p.getVert 2 ∈ I ∪ X := by rw [hcover]; trivial
        simpa only [Set.mem_union] using this
      exact h2.resolve_left (fun h2I ↦ hI hsI h2I h12.ne h12)
    have hv_ne_h2 : v ≠ p.getVert 2 := by
      simpa using hp.getVert_sub_one_ne_getVert_add_one
        (i := 1) (by omega : 1 ≤ p.length)
    exact hv_ne_h2
      (huniq p.snd hsI v hvX (p.getVert 2) h2X hvs.symm h12)

private lemma induce_insert_isAcyclic_of_indep
    {V : Type*} [DecidableEq V] (G : SimpleGraph V)
    (I : Finset V) (v : V) (hI : G.IsIndepSet (I : Set V)) :
    (G.induce (↑(insert v I) : Set V)).IsAcyclic := by
  have hset : (↑(insert v I) : Set V) = (I : Set V) ∪ ({v} : Set V) := by
    ext x
    simp
  rw [hset]
  let I' : Set ↑((I : Set V) ∪ ({v} : Set V)) := {x | (x : V) ∈ I}
  let X' : Set ↑((I : Set V) ∪ ({v} : Set V)) := {x | (x : V) = v}
  apply isAcyclic_of_independent_parts_of_left_unique_neighbor I' X'
  · ext x
    simp only [I', X', Set.mem_union, Set.mem_setOf_eq, Set.mem_univ, iff_true]
    exact x.property
  · intro x hx y hy hxy hadj
    apply hI hx hy
    · intro hcoe
      exact hxy (Subtype.ext hcoe)
    · exact SimpleGraph.induce_adj.mp hadj
  · intro x hx y hy hxy _
    exact hxy (Subtype.ext (hx.trans hy.symm))
  · intro i hi x hx y hy _ _
    apply Subtype.ext
    exact hx.trans hy.symm

/-- The complete bipartite graph `K_{2,c}`. -/
abbrev K2c (c : ℕ) : SimpleGraph (Fin 2 ⊕ Fin c) :=
  completeBipartiteGraph (Fin 2) (Fin c)

/-- The right class of `K_{2,c}` as a finite vertex set. -/
def rightVertices (c : ℕ) : Finset (Fin 2 ⊕ Fin c) :=
  Finset.univ.map ⟨Sum.inr, Sum.inr_injective⟩

lemma rightVertices_card (c : ℕ) : (rightVertices c).card = c := by
  simp [rightVertices]

lemma left_one_not_mem_rightVertices (c : ℕ) :
    (Sum.inl 1 : Fin 2 ⊕ Fin c) ∉ rightVertices c := by
  simp [rightVertices]

/-- The right class contains no edges. -/
lemma rightVertices_isIndepSet (c : ℕ) :
    (K2c c).IsIndepSet (rightVertices c : Set (Fin 2 ⊕ Fin c)) := by
  intro x hx y hy _hxy hxy
  cases x <;> cases y <;>
    simp [rightVertices, K2c, completeBipartiteGraph] at hx hy hxy

/-- Deleting the left vertex `0` leaves an induced star, hence a forest of
order `c+1`. -/
lemma K2c_forest_lower_bound (c : ℕ) :
    c + 1 ≤ (K2c c).largestInducedForestSize := by
  let S : Finset (Fin 2 ⊕ Fin c) :=
    insert (Sum.inl 1) (rightVertices c)
  have hS : ((K2c c).induce (S : Set (Fin 2 ⊕ Fin c))).IsAcyclic := by
    exact induce_insert_isAcyclic_of_indep
      (K2c c) (rightVertices c) (Sum.inl 1) (rightVertices_isIndepSet c)
  have hcard : S.card = c + 1 := by
    simp [S, left_one_not_mem_rightVertices, rightVertices_card]
  rw [← hcard]
  exact card_le_largestInducedForestSize (K2c c) S hS

private lemma four_cycle_not_acyclic
    {V : Type*} (G : SimpleGraph V) (a b c d : V)
    (hab : G.Adj a b) (hbc : G.Adj b c)
    (hcd : G.Adj c d) (hda : G.Adj d a)
    (habv : a ≠ b) (hacv : a ≠ c) (hadv : a ≠ d)
    (hbcv : b ≠ c) (hbdv : b ≠ d) (hcdv : c ≠ d) :
    ¬G.IsAcyclic := by
  intro hacyclic
  let p : G.Walk a a :=
    Walk.cons hab (Walk.cons hbc (Walk.cons hcd (Walk.cons hda Walk.nil)))
  apply hacyclic p
  rw [Walk.isCycle_def]
  simp [p, habv, hacv, hadv, hbcv, hbdv, hcdv, ne_comm]

/-- For `c ≥ 2`, `K_{2,c}` contains its evident four-cycle. -/
lemma K2c_not_isAcyclic (c : ℕ) (hc : 2 ≤ c) : ¬(K2c c).IsAcyclic := by
  let r0 : Fin c := ⟨0, by omega⟩
  let r1 : Fin c := ⟨1, by omega⟩
  apply four_cycle_not_acyclic (K2c c)
      (Sum.inl 0) (Sum.inr r0) (Sum.inl 1) (Sum.inr r1)
  all_goals simp [K2c, completeBipartiteGraph, r0, r1]

/-- Exact induced-forest order of the family. -/
theorem K2c_largestInducedForestSize (c : ℕ) (hc : 2 ≤ c) :
    (K2c c).largestInducedForestSize = c + 1 := by
  have hlower := K2c_forest_lower_bound c
  have hupper := largestInducedForestSize_lt_card_of_not_isAcyclic
    (K2c c) (K2c_not_isAcyclic c hc)
  rw [Fintype.card_sum, Fintype.card_fin, Fintype.card_fin] at hupper
  omega

/-- The standard two-coloring of `K_{2,c}`. -/
lemma K2c_isBipartite (c : ℕ) : (K2c c).IsBipartite := by
  refine ⟨Coloring.mk (fun v ↦ if v.isLeft then 0 else 1) ?_⟩
  intro u v huv
  cases u <;> cases v <;>
    simp [K2c, completeBipartiteGraph] at huv ⊢

/-- Exact induced-bipartite order of the family. -/
theorem K2c_largestInducedBipartiteSubgraphSize (c : ℕ) :
    (K2c c).largestInducedBipartiteSubgraphSize = c + 2 := by
  apply le_antisymm
  · simpa [K2c, Nat.add_comm] using
      largestInducedBipartiteSubgraphSize_le_card (K2c c)
  · have hfull :
        (((K2c c).induce
          ((Finset.univ : Finset (Fin 2 ⊕ Fin c)) : Set (Fin 2 ⊕ Fin c))).IsBipartite) := by
      obtain ⟨color⟩ := K2c_isBipartite c
      rw [induce_isBipartite_iff_exists_coloring]
      exact ⟨fun v ↦ color v, fun u _ v _ huv ↦ color.valid huv⟩
    have h :=
      card_le_largestInducedBipartiteSubgraphSize
        (K2c c) (Finset.univ : Finset (Fin 2 ⊕ Fin c)) hfull
    simpa [K2c, Nat.add_comm] using h

/-- Real-valued `b` coordinate used by the upstream statement. -/
theorem K2c_b (c : ℕ) : b (K2c c) = c + 2 := by
  unfold b
  rw [K2c_largestInducedBipartiteSubgraphSize]
  norm_num

private def pathSupportCover {V : Type*} [Fintype V] [DecidableEq V]
    (S : Finset V) : Finset (Finset V) :=
  insert S ((Finset.univ \ S).image fun x ↦ {x})

private lemma pathSupportCover_isPathCover
    {V : Type*} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) {a z : V} (p : G.Walk a z)
    (hp : p.IsPath) (hcard : 2 ≤ p.support.toFinset.card) :
    IsPathCover G (pathSupportCover p.support.toFinset) := by
  let S := p.support.toFinset
  have hS_not_singleton : ∀ x : V, S ≠ {x} := by
    intro x hx
    have := congrArg Finset.card hx
    simp [S] at this
    omega
  refine ⟨?_, ?_, ?_⟩
  · intro s₁ hs₁ s₂ hs₂ hne
    simp only [pathSupportCover, mem_insert, mem_image, mem_sdiff,
      mem_univ, true_and] at hs₁ hs₂
    rcases hs₁ with rfl | ⟨x, hxS, rfl⟩
    · rcases hs₂ with hsame | ⟨y, hyS, rfl⟩
      · exact (hne hsame.symm).elim
      · rw [Finset.disjoint_singleton_right]
        exact hyS
    · rcases hs₂ with hsame | ⟨y, hyS, rfl⟩
      · have hxS' : x ∉ S := hxS
        subst s₂
        rw [Finset.disjoint_singleton_left]
        exact hxS'
      · simpa using hne
  · intro x _
    by_cases hx : x ∈ S
    · apply mem_biUnion.mpr
      exact ⟨S, mem_insert_self _ _, hx⟩
    · apply mem_biUnion.mpr
      refine ⟨{x}, ?_, by simp⟩
      change {x} ∈ pathSupportCover S
      exact mem_insert_of_mem (mem_image.mpr
        ⟨x, by simp [hx], rfl⟩)
  · intro s hs
    simp only [pathSupportCover, mem_insert, mem_image, mem_sdiff,
      mem_univ, true_and] at hs
    rcases hs with hS | ⟨x, -, rfl⟩
    · exact ⟨a, z, p, hp, hS⟩
    · exact ⟨x, x, .nil, Walk.IsPath.nil, by simp⟩

private lemma pathSupportCover_card
    {V : Type*} [Fintype V] [DecidableEq V]
    (S : Finset V) (hcard : 2 ≤ S.card) :
    (pathSupportCover S).card + S.card = Fintype.card V + 1 := by
  have hS_not_image : S ∉
      (Finset.univ \ S).image (fun x : V ↦ ({x} : Finset V)) := by
    intro h
    simp only [mem_image, mem_sdiff, mem_univ, true_and] at h
    obtain ⟨x, -, hx⟩ := h
    have hc := congrArg Finset.card hx
    simp at hc
    omega
  unfold pathSupportCover
  rw [card_insert_of_notMem hS_not_image, card_image_of_injective]
  · rw [card_sdiff_of_subset (Finset.subset_univ S), card_univ]
    have hle := S.card_le_univ
    omega
  · intro x y h
    simpa using h

private lemma pathCoverNumber_le_card_of_isPathCover
    {V : Type*} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) (P : Finset (Finset V))
    (hP : IsPathCover G P) :
    pathCoverNumber G ≤ P.card := by
  unfold pathCoverNumber
  exact Nat.sInf_le ⟨P, rfl, hP⟩

private lemma pathCoverNumber_add_four_le_card_of_five_vertex_path
    {V : Type*} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) {a z : V} (p : G.Walk a z)
    (hp : p.IsPath) (hcard : 5 ≤ p.support.toFinset.card) :
    pathCoverNumber G + 4 ≤ Fintype.card V := by
  have hcover := pathSupportCover_isPathCover G p hp (by omega)
  have hle := pathCoverNumber_le_card_of_isPathCover
    G _ hcover
  have hc := pathSupportCover_card p.support.toFinset (by omega)
  omega

/-- `K_{2,c}` has an alternating path through both left vertices and three
right vertices.  Completing that path by singleton vertices gives the exact
upper half of the path-cover formula. -/
theorem K2c_pathCoverNumber_le (c : ℕ) (hc : 3 ≤ c) :
    pathCoverNumber (K2c c) ≤ c - 2 := by
  let r0 : Fin c := ⟨0, by omega⟩
  let r1 : Fin c := ⟨1, by omega⟩
  let r2 : Fin c := ⟨2, by omega⟩
  let a : Fin 2 ⊕ Fin c := Sum.inr r0
  let z : Fin 2 ⊕ Fin c := Sum.inr r2
  have h01 : (K2c c).Adj a (Sum.inl 0) := by
    simp [K2c, completeBipartiteGraph, a]
  have h12 : (K2c c).Adj (Sum.inl 0) (Sum.inr r1) := by
    simp [K2c, completeBipartiteGraph]
  have h23 : (K2c c).Adj (Sum.inr r1) (Sum.inl 1) := by
    simp [K2c, completeBipartiteGraph]
  have h34 : (K2c c).Adj (Sum.inl 1) z := by
    simp [K2c, completeBipartiteGraph, z]
  let p : (K2c c).Walk a z :=
    Walk.cons h01 (Walk.cons h12 (Walk.cons h23 (Walk.cons h34 Walk.nil)))
  have hp : p.IsPath := by
    rw [Walk.isPath_def]
    simp [p, a, z, r0, r1, r2]
  have hsupport : p.support.toFinset.card = 5 := by
    simp [p, a, z, r0, r1, r2]
  have hrank := pathCoverNumber_add_four_le_card_of_five_vertex_path
    (K2c c) p hp (by omega)
  rw [Fintype.card_sum, Fintype.card_fin, Fintype.card_fin] at hrank
  omega

/-- Exact source-ceiling equality on `K_{2,c}`, conditional only on the one
family invariant for which the repository currently lacks a reusable lower-
bound API. -/
theorem K2c_source_ceiling_equality
    (c : ℕ) (hc : 4 ≤ c)
    (hpathLower : c - 2 ≤ pathCoverNumber (K2c c)) :
    ⌈(((pathCoverNumber (K2c c) : ℝ) + b (K2c c) + 1) / 2)⌉ =
      (K2c c).largestInducedForestSize := by
  have hpath : pathCoverNumber (K2c c) = c - 2 := by
    apply le_antisymm (K2c_pathCoverNumber_le c (by omega)) hpathLower
  rw [hpath, K2c_b, K2c_largestInducedForestSize c (by omega)]
  rw [Nat.cast_sub (by omega : 2 ≤ c)]
  rw [Int.ceil_eq_iff]
  constructor <;> push_cast <;> norm_num <;> linarith

/-- In particular, every certified member of the family attains WOWII 40
with equality. -/
theorem K2c_conjecture40_equality_certificate
    (c : ℕ) (hc : 4 ≤ c)
    (hpathLower : c - 2 ≤ pathCoverNumber (K2c c)) :
    ⌈(((pathCoverNumber (K2c c) : ℝ) + b (K2c c) + 1) / 2)⌉ ≤
      (K2c c).largestInducedForestSize := by
  exact (K2c_source_ceiling_equality c hc hpathLower).le

#print axioms K2c_largestInducedForestSize
#print axioms K2c_largestInducedBipartiteSubgraphSize
#print axioms K2c_pathCoverNumber_le
#print axioms K2c_source_ceiling_equality

end WrittenOnTheWallII.GraphConjecture40K2cEquality
