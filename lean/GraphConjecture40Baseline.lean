import FormalConjecturesUtil

/-!
# WOWII 40: the source baseline

This file formalizes the elementary inequality quoted in the source note for
Written on the Wall II, Conjecture 40:

`largestInducedBipartiteSubgraphSize G + 2 ≤ 2 * largestInducedForestSize G`

for every finite connected nontrivial graph.  It also supplies the finite
`sSup` witness/comparison lemmas needed by the proof and closes the
`pathCoverNumber G = 1` specialization in the exact upstream shape.
-/

namespace WrittenOnTheWallII.GraphConjecture40Baseline

open SimpleGraph Finset

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

omit [DecidableEq V] in
/-- An explicit induced forest bounds the repository's `sSup` invariant. -/
lemma card_le_largestInducedForestSize
    (G : SimpleGraph V) (S : Finset V)
    (hS : (G.induce (S : Set V)).IsAcyclic) :
    S.card ≤ G.largestInducedForestSize := by
  unfold largestInducedForestSize
  apply le_csSup
  · exact ⟨Fintype.card V, fun n hn ↦ by
      obtain ⟨T, -, rfl⟩ := hn
      exact T.card_le_univ⟩
  · exact ⟨S, hS, rfl⟩

omit [DecidableEq V] in
/-- An explicit induced bipartite subgraph bounds the repository's `sSup`
invariant. -/
lemma card_le_largestInducedBipartiteSubgraphSize
    (G : SimpleGraph V) (S : Finset V)
    (hS : (G.induce (S : Set V)).IsBipartite) :
    S.card ≤ G.largestInducedBipartiteSubgraphSize := by
  unfold largestInducedBipartiteSubgraphSize
  apply le_csSup
  · exact ⟨Fintype.card V, fun n hn ↦ by
      obtain ⟨T, -, rfl⟩ := hn
      exact T.card_le_univ⟩
  · exact ⟨S, hS, rfl⟩

omit [DecidableEq V] in
/-- The finite `sSup` defining the largest induced bipartite order is attained. -/
lemma exists_largestInducedBipartiteSubgraphSize_witness
    (G : SimpleGraph V) (_hfinite : 1 < Fintype.card V) :
    ∃ S : Finset V,
      (G.induce (S : Set V)).IsBipartite ∧
      S.card = G.largestInducedBipartiteSubgraphSize := by
  classical
  let A : Set ℕ :=
    {n | ∃ S : Finset V, (G.induce (S : Set V)).IsBipartite ∧ S.card = n}
  have hAne : A.Nonempty := by
    refine ⟨0, ∅, ?_, rfl⟩
    rw [induce_isBipartite_iff_exists_coloring]
    exact ⟨fun _ ↦ 0, by simp⟩
  have hAbdd : BddAbove A := by
    exact ⟨Fintype.card V, fun n hn ↦ by
      obtain ⟨S, -, rfl⟩ := hn
      exact S.card_le_univ⟩
  have hmem : sSup A ∈ A := Nat.sSup_mem hAne hAbdd
  obtain ⟨S, hS, hcard⟩ := hmem
  exact ⟨S, hS, by simpa [largestInducedBipartiteSubgraphSize, A] using hcard⟩

omit [Fintype V] [DecidableEq V] in
/-- A bipartition whose left vertices have at most one neighbor on the right
is acyclic. -/
lemma isAcyclic_of_independent_parts_of_left_unique_neighbor
    {G : SimpleGraph V} (I X : Set V)
    (hcover : I ∪ X = Set.univ)
    (hI : G.IsIndepSet I)
    (hX : G.IsIndepSet X)
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

omit [Fintype V] [DecidableEq V] in
/-- Induced-subgraph form of the preceding acyclicity criterion. -/
lemma induce_union_isAcyclic_of_left_unique_neighbor
    (G : SimpleGraph V) (I X : Set V)
    (hI : G.IsIndepSet I)
    (hX : G.IsIndepSet X)
    (huniq : ∀ i ∈ I, ∀ x ∈ X, ∀ y ∈ X,
      G.Adj i x → G.Adj i y → x = y) :
    (G.induce (I ∪ X)).IsAcyclic := by
  let I' : Set ↑(I ∪ X) := {v | (v : V) ∈ I}
  let X' : Set ↑(I ∪ X) := {v | (v : V) ∈ X}
  apply isAcyclic_of_independent_parts_of_left_unique_neighbor I' X'
  · ext v
    simp only [I', X', Set.mem_union, Set.mem_setOf_eq, Set.mem_univ, iff_true]
    exact v.property
  · intro u hu v hv huv hadj
    apply hI hu hv
    · intro hcoe
      exact huv (Subtype.ext hcoe)
    · exact SimpleGraph.induce_adj.mp hadj
  · intro u hu v hv huv hadj
    apply hX hu hv
    · intro hcoe
      exact huv (Subtype.ext hcoe)
    · exact SimpleGraph.induce_adj.mp hadj
  · intro i hi x hx y hy hix hiy
    apply Subtype.ext
    exact huniq i hi x hx y hy (SimpleGraph.induce_adj.mp hix)
      (SimpleGraph.induce_adj.mp hiy)

omit [Fintype V] in
/-- An independent set together with one new vertex induces a forest. -/
lemma induce_insert_isAcyclic_of_indep
    (G : SimpleGraph V) (I : Finset V) (v : V)
    (hI : G.IsIndepSet (I : Set V)) :
    (G.induce (↑(insert v I) : Set V)).IsAcyclic := by
  have hset : (↑(insert v I) : Set V) = (I : Set V) ∪ ({v} : Set V) := by
    ext x
    simp
  rw [hset]
  apply induce_union_isAcyclic_of_left_unique_neighbor G (I : Set V) {v} hI
  · intro x hx y hy hxy hadj
    simp only [Set.mem_singleton_iff] at hx hy
    exact hxy (hx.trans hy.symm)
  · intro i hi x hx y hy _ _
    simpa only [Set.mem_singleton_iff] using hx.trans hy.symm

omit [Fintype V] in
/-- An independent set in a connected nontrivial graph omits a vertex. -/
lemma exists_not_mem_of_indep_of_connected
    {G : SimpleGraph V} [Nontrivial V] (hconn : G.Connected)
    (I : Finset V) (hI : G.IsIndepSet (I : Set V)) :
    ∃ v, v ∉ I := by
  let x : V := Classical.choice inferInstance
  obtain ⟨y, hxy⟩ := hconn.preconnected.exists_adj_of_nontrivial x
  by_cases hxI : x ∈ I
  · refine ⟨y, ?_⟩
    intro hyI
    exact hI hxI hyI hxy.ne hxy
  · exact ⟨x, hxI⟩

/-- Every explicit induced bipartite witness obeys the source baseline. -/
lemma bipartite_witness_add_two_le_two_mul_forestSize
    (G : SimpleGraph V) [Nontrivial V] (hconn : G.Connected)
    (S : Finset V) (hS : (G.induce (S : Set V)).IsBipartite) :
    S.card + 2 ≤ 2 * G.largestInducedForestSize := by
  obtain ⟨c, hc⟩ := (induce_isBipartite_iff_exists_coloring G S).mp hS
  let A := S.filter fun x ↦ c x = 0
  let C := S.filter fun x ↦ c x ≠ 0
  have hpart : A.card + C.card = S.card := by
    simpa [A, C] using
      (Finset.card_filter_add_card_filter_not
        (s := S) (p := fun x ↦ c x = 0))
  have hAind : G.IsIndepSet (A : Set V) := by
    intro x hx y hy hxy hadj
    have hcx : c x = 0 := (Finset.mem_filter.mp hx).2
    have hcy : c y = 0 := (Finset.mem_filter.mp hy).2
    exact (hc x (Finset.mem_filter.mp hx).1 y (Finset.mem_filter.mp hy).1 hadj)
      (hcx.trans hcy.symm)
  have hCind : G.IsIndepSet (C : Set V) := by
    intro x hx y hy hxy hadj
    have hcx : c x ≠ 0 := (Finset.mem_filter.mp hx).2
    have hcy : c y ≠ 0 := (Finset.mem_filter.mp hy).2
    have hcxy : c x = c y := by
      rw [Fin.eq_one_of_ne_zero (c x) hcx, Fin.eq_one_of_ne_zero (c y) hcy]
    exact (hc x (Finset.mem_filter.mp hx).1 y (Finset.mem_filter.mp hy).1 hadj) hcxy
  rcases le_total C.card A.card with hCA | hAC
  · obtain ⟨v, hv⟩ := exists_not_mem_of_indep_of_connected hconn A hAind
    have hforest : (insert v A).card ≤ G.largestInducedForestSize :=
      card_le_largestInducedForestSize G (insert v A)
        (induce_insert_isAcyclic_of_indep G A v hAind)
    rw [Finset.card_insert_of_notMem hv] at hforest
    omega
  · obtain ⟨v, hv⟩ := exists_not_mem_of_indep_of_connected hconn C hCind
    have hforest : (insert v C).card ≤ G.largestInducedForestSize :=
      card_le_largestInducedForestSize G (insert v C)
        (induce_insert_isAcyclic_of_indep G C v hCind)
    rw [Finset.card_insert_of_notMem hv] at hforest
    omega

/-- The elementary baseline quoted in the source note for WOWII 40. -/
theorem largestInducedBipartiteSubgraphSize_add_two_le_two_mul_forestSize
    (G : SimpleGraph V) [Nontrivial V] (hconn : G.Connected)
    (hfinite : 1 < Fintype.card V) :
    G.largestInducedBipartiteSubgraphSize + 2 ≤
      2 * G.largestInducedForestSize := by
  obtain ⟨S, hS, hcard⟩ :=
    exists_largestInducedBipartiteSubgraphSize_witness G hfinite
  rw [← hcard]
  exact bipartite_witness_add_two_le_two_mul_forestSize G hconn S hS

/-- The `pathCoverNumber = 1` specialization in the exact real/ceiling shape
of the upstream conjecture. -/
theorem conjecture40_of_pathCoverNumber_eq_one
    (G : SimpleGraph V) [Nontrivial V] (hconn : G.Connected)
    (hfinite : 1 < Fintype.card V)
    (hp : pathCoverNumber G = 1) :
    ⌈(((pathCoverNumber G : ℝ) + b G + 1) / 2)⌉ ≤
      G.largestInducedForestSize := by
  have hbase :=
    largestInducedBipartiteSubgraphSize_add_two_le_two_mul_forestSize
      G hconn hfinite
  have hbaseR :
      (G.largestInducedBipartiteSubgraphSize : ℝ) + 2 ≤
        2 * (G.largestInducedForestSize : ℝ) := by
    exact_mod_cast hbase
  rw [Int.ceil_le]
  rw [hp]
  unfold b
  norm_num
  linarith

end WrittenOnTheWallII.GraphConjecture40Baseline
