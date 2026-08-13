import FormalConjecturesUtil

/-!
# WOWII 141: the induced-star core and the small-girth branch

An independent set in the open neighborhood of `v`, together with `v`,
induces a star and hence a tree.  This proves the full conjectured inequality
whenever `girth G ≤ 5` (including the repository's `girth = 0` convention for
forests).
-/

namespace WrittenOnTheWallII.GraphConjecture141Extraction

open SimpleGraph Finset

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

omit [Fintype V] [DecidableEq V] in
/-- A bipartition in which every vertex on the left has at most one neighbor
on the right is acyclic. -/
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
      exact hs.resolve_left (fun hsI => hI hvI hsI hvs.ne hvs)
    have hpX : p.penultimate ∈ X := by
      have hpen : p.penultimate ∈ I ∨ p.penultimate ∈ X := by
        have : p.penultimate ∈ I ∪ X := by rw [hcover]; trivial
        simpa only [Set.mem_union] using this
      exact hpen.resolve_left (fun hpI => hI hvI hpI hvp.ne hvp)
    exact hp.snd_ne_penultimate
      (huniq v hvI p.snd hsX p.penultimate hpX hvs hvp)
  · have hsI : p.snd ∈ I := by
      have hs : p.snd ∈ I ∨ p.snd ∈ X := by
        have : p.snd ∈ I ∪ X := by rw [hcover]; trivial
        simpa only [Set.mem_union] using this
      exact hs.resolve_right (fun hsX => hX hvX hsX hvs.ne hvs)
    have h12 : G.Adj p.snd (p.getVert 2) := by
      simpa using p.adj_getVert_succ (by omega : 1 < p.length)
    have h2X : p.getVert 2 ∈ X := by
      have h2 : p.getVert 2 ∈ I ∨ p.getVert 2 ∈ X := by
        have : p.getVert 2 ∈ I ∪ X := by rw [hcover]; trivial
        simpa only [Set.mem_union] using this
      exact h2.resolve_left (fun h2I => hI hsI h2I h12.ne h12)
    have hv_ne_h2 : v ≠ p.getVert 2 := by
      simpa using hp.getVert_sub_one_ne_getVert_add_one
        (i := 1) (by omega : 1 ≤ p.length)
    exact hv_ne_h2
      (huniq p.snd hsI v hvX (p.getVert 2) h2X hvs.symm h12)

omit [Fintype V] in
/-- An independent subset of `N(v)`, together with `v`, induces a tree. -/
lemma induce_insert_isTree_of_indep_neighbors
    (G : SimpleGraph V) (v : V) (A : Finset V)
    (hA : G.IsIndepSet (A : Set V))
    (hAN : (A : Set V) ⊆ G.neighborSet v) :
    (G.induce (↑(insert v A) : Set V)).IsTree := by
  let H := G.induce (↑(insert v A) : Set V)
  have hconn : H.Connected := by
    rw [connected_iff_exists_forall_reachable]
    let c : ↑(insert v A : Finset V) := ⟨v, by simp⟩
    refine ⟨c, ?_⟩
    intro w
    by_cases hw : (w : V) = v
    · have hwc : w = c := Subtype.ext hw
      rw [hwc]
    · apply Adj.reachable
      apply SimpleGraph.induce_adj.mpr
      simpa [c] using hAN (by simpa [hw] using w.property)
  refine ⟨hconn, ?_⟩
  let I : Set ↑(insert v A : Finset V) := {x | (x : V) ∈ A}
  let X : Set ↑(insert v A : Finset V) := {x | (x : V) = v}
  apply isAcyclic_of_independent_parts_of_left_unique_neighbor I X
  · ext x
    simp only [I, X, Set.mem_union, Set.mem_setOf_eq, Set.mem_univ, iff_true]
    have hx : (x : V) = v ∨ (x : V) ∈ A := by
      simpa only [Finset.mem_insert] using x.property
    exact hx.symm
  · intro x hx y hy hxy hxyAdj
    apply hA hx hy
    · exact fun h => hxy (Subtype.ext h)
    · exact SimpleGraph.induce_adj.mp hxyAdj
  · intro x hx y hy hxy _
    exact hxy (Subtype.ext (hx.trans hy.symm))
  · intro i hi x hx y hy _ _
    exact Subtype.ext (hx.trans hy.symm)

omit [DecidableEq V] in
/-- Any explicit induced tree bounds `largestInducedTreeSize`. -/
lemma card_le_largestInducedTreeSize
    (G : SimpleGraph V) (S : Finset V)
    (hS : (G.induce (S : Set V)).IsTree) :
    S.card ≤ G.largestInducedTreeSize := by
  unfold largestInducedTreeSize
  apply le_csSup
  · exact ⟨Fintype.card V, fun n hn => by
      obtain ⟨T, rfl, -⟩ := hn
      exact T.card_le_univ⟩
  · exact ⟨S, rfl, hS⟩

omit [DecidableEq V] in
/-- A maximum independent set in the induced open neighborhood, mapped back
to ambient vertices. -/
lemma exists_local_indep_witness (G : SimpleGraph V) [DecidableRel G.Adj] (v : V) :
    ∃ A : Finset V,
      G.IsIndepSet (A : Set V) ∧
      A ⊆ G.neighborFinset v ∧
      A.card = indepNeighborsCard G v := by
  classical
  let H := G.induce (G.neighborSet v)
  obtain ⟨S, hS⟩ := H.exists_isNIndepSet_indepNum
  let A : Finset V := S.map (Function.Embedding.subtype _)
  refine ⟨A, ?_, ?_, ?_⟩
  · intro x hx y hy hxy hxyAdj
    obtain ⟨x', hx'S, hx'eq⟩ := Finset.mem_map.mp hx
    obtain ⟨y', hy'S, hy'eq⟩ := Finset.mem_map.mp hy
    subst x
    subst y
    apply hS.isIndepSet hx'S hy'S
    · exact fun h => hxy (congrArg Subtype.val h)
    · exact hxyAdj
  · intro x hx
    obtain ⟨x', -, hx'eq⟩ := Finset.mem_map.mp hx
    rw [← hx'eq, mem_neighborFinset]
    exact x'.property
  · rw [Finset.card_map, hS.card_eq]
    rfl

/-- The invariant-native induced-star bound. -/
theorem indepNeighborsCard_add_one_le_largestInducedTreeSize
    (G : SimpleGraph V) [DecidableRel G.Adj] (v : V) :
    indepNeighborsCard G v + 1 ≤ G.largestInducedTreeSize := by
  obtain ⟨A, hA, hAN, hcard⟩ := exists_local_indep_witness G v
  have hvA : v ∉ A := by
    intro hv
    exact G.loopless v (by
      rw [← mem_neighborFinset]
      exact hAN hv)
  rw [← hcard, ← Finset.card_insert_of_notMem hvA]
  apply card_le_largestInducedTreeSize
  apply induce_insert_isTree_of_indep_neighbors G v A hA
  intro x hx
  rw [← coe_neighborFinset]
  exact hAN hx

/-- Maximizing the induced-star bound over all centers. -/
theorem localIndependenceMax_add_one_le_largestInducedTreeSize
    (G : SimpleGraph V) [Nonempty V] [DecidableRel G.Adj] :
    Finset.univ.sup (indepNeighborsCard G) + 1 ≤ G.largestInducedTreeSize := by
  apply Nat.add_le_of_le_sub (by
    have hnonempty : (Finset.univ : Finset V).Nonempty := Finset.univ_nonempty
    obtain ⟨v, -⟩ := hnonempty
    exact (indepNeighborsCard_add_one_le_largestInducedTreeSize G v).trans'
      (Nat.le_add_left 1 _))
  apply Finset.sup_le
  intro v _
  have h := indepNeighborsCard_add_one_le_largestInducedTreeSize G v
  omega

/-- WOWII 141 holds outright in the small-girth branch. -/
theorem conjecture141_of_girth_le_five
    (G : SimpleGraph V) [Nonempty V] [DecidableRel G.Adj]
    (hgirth : G.girth ≤ 5) :
    (G.girth / 2 : ℤ) - 1 + ((Finset.univ.sup (indepNeighborsCard G) : ℕ) : ℤ) ≤
      (largestInducedTreeSize G : ℤ) := by
  have hstar := localIndependenceMax_add_one_le_largestInducedTreeSize G
  have hhalf : G.girth / 2 ≤ 2 := by omega
  have hstarZ :
      ((Finset.univ.sup (indepNeighborsCard G) + 1 : ℕ) : ℤ) ≤
        (largestInducedTreeSize G : ℤ) := by exact_mod_cast hstar
  have hhalfZ : ((G.girth / 2 : ℕ) : ℤ) ≤ 2 := by exact_mod_cast hhalf
  omega

end WrittenOnTheWallII.GraphConjecture141Extraction
