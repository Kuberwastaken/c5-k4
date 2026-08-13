import GraphConjecture141BfsGirthBound

/-!
# WOWII 141: exceptional-root bipartite acyclicity
-/

namespace WrittenOnTheWallII.GraphConjecture141RadiusTwoAcyclic

open SimpleGraph Finset

universe u

variable {V : Type u} [DecidableEq V]

/-- A bipartite graph is acyclic when every vertex on one side, except
possibly a distinguished root, has at most one neighbor on the other side.
The exceptional root cannot lie on a cycle: the vertex two steps after it
would then have two distinct neighbors. -/
theorem isAcyclic_of_independent_parts_of_unique_neighbor_except_root
    (G : SimpleGraph V) (I X : Set V) (r : V)
    (hcover : I ∪ X = Set.univ)
    (hI : G.IsIndepSet I) (hX : G.IsIndepSet X) (hrI : r ∈ I)
    (huniq : ∀ i ∈ I, i ≠ r → ∀ x ∈ X, ∀ y ∈ X,
      G.Adj i x → G.Adj i y → x = y) :
    G.IsAcyclic := by
  intro v p hp
  have hlen : 3 ≤ p.length := hp.three_le_length
  have side (z : V) : z ∈ I ∨ z ∈ X := by
    have : z ∈ I ∪ X := by rw [hcover]; trivial
    simpa only [Set.mem_union] using this
  by_cases hr : r ∈ p.support
  · let q := p.rotate hr
    have hq : q.IsCycle := hp.rotate hr
    have hqlen : 3 ≤ q.length := hq.three_le_length
    have h12 : G.Adj q.snd (q.getVert 2) := by
      simpa using q.adj_getVert_succ (by omega : 1 < q.length)
    have h23 : G.Adj (q.getVert 2) (q.getVert 3) := by
      simpa using q.adj_getVert_succ (by omega : 2 < q.length)
    have hsX : q.snd ∈ X := by
      rcases side q.snd with hsI | hsX
      · exact (hI hrI hsI (q.adj_snd hq.not_nil).ne
          (q.adj_snd hq.not_nil)).elim
      · exact hsX
    have h2I : q.getVert 2 ∈ I := by
      rcases side (q.getVert 2) with h2I | h2X
      · exact h2I
      · exact (hX hsX h2X h12.ne h12).elim
    have h3X : q.getVert 3 ∈ X := by
      rcases side (q.getVert 3) with h3I | h3X
      · exact (hI h2I h3I h23.ne h23).elim
      · exact h3X
    have h2r : q.getVert 2 ≠ r := by
      have := hq.getVert_sub_one_ne_getVert_add_one
        (i := 1) (by omega : 1 ≤ q.length)
      simpa [q] using this.symm
    have hs3 : q.snd ≠ q.getVert 3 := by
      simpa using hq.getVert_sub_one_ne_getVert_add_one
        (i := 2) (by omega : 2 ≤ q.length)
    exact hs3 (huniq (q.getVert 2) h2I h2r q.snd hsX
      (q.getVert 3) h3X h12.symm h23)
  · have hvs : G.Adj v p.snd := p.adj_snd hp.not_nil
    have hvp : G.Adj v p.penultimate :=
      (p.adj_penultimate hp.not_nil).symm
    rcases side v with hvI | hvX
    · have hvne : v ≠ r := by
        intro hvr
        apply hr
        simpa [hvr] using p.start_mem_support
      have hsX : p.snd ∈ X := by
        rcases side p.snd with hsI | hsX
        · exact (hI hvI hsI hvs.ne hvs).elim
        · exact hsX
      have hpX : p.penultimate ∈ X := by
        rcases side p.penultimate with hpI | hpX
        · exact (hI hvI hpI hvp.ne hvp).elim
        · exact hpX
      exact hp.snd_ne_penultimate
        (huniq v hvI hvne p.snd hsX p.penultimate hpX hvs hvp)
    · have hsI : p.snd ∈ I := by
        rcases side p.snd with hsI | hsX
        · exact hsI
        · exact (hX hvX hsX hvs.ne hvs).elim
      have hsne : p.snd ≠ r := by
        intro hsr
        apply hr
        have hsTail := p.snd_mem_tail_support hp.not_nil
        have hsSupp : p.snd ∈ p.support := by
          exact List.mem_of_mem_tail hsTail
        simpa [hsr] using hsSupp
      have h12 : G.Adj p.snd (p.getVert 2) := by
        simpa using p.adj_getVert_succ (by omega : 1 < p.length)
      have h2X : p.getVert 2 ∈ X := by
        rcases side (p.getVert 2) with h2I | h2X
        · exact (hI hsI h2I h12.ne h12).elim
        · exact h2X
      have hv_ne_h2 : v ≠ p.getVert 2 := by
        simpa using hp.getVert_sub_one_ne_getVert_add_one
          (i := 1) (by omega : 1 ≤ p.length)
      exact hv_ne_h2
        (huniq p.snd hsI hsne v hvX (p.getVert 2) h2X hvs.symm h12)

/-- Exact layer certificate sufficient to rule out a cyclic radius-two
center.  The exceptional root is allowed arbitrary degree into the opposite
layer; every other even-layer vertex has a unique neighbor there. -/
structure RadiusTwoForestCertificate (G : SimpleGraph V) where
  even : Set V
  odd : Set V
  root : V
  cover : even ∪ odd = Set.univ
  evenIndependent : G.IsIndepSet even
  oddIndependent : G.IsIndepSet odd
  root_even : root ∈ even
  other_even_unique : ∀ i ∈ even, i ≠ root → ∀ x ∈ odd, ∀ y ∈ odd,
    G.Adj i x → G.Adj i y → x = y

/-- A radius-two forest certificate really proves acyclicity. -/
theorem RadiusTwoForestCertificate.isAcyclic
    {G : SimpleGraph V} (C : RadiusTwoForestCertificate G) :
    G.IsAcyclic := by
  exact isAcyclic_of_independent_parts_of_unique_neighbor_except_root
    G C.even C.odd C.root C.cover C.evenIndependent C.oddIndependent
      C.root_even C.other_even_unique

end WrittenOnTheWallII.GraphConjecture141RadiusTwoAcyclic
