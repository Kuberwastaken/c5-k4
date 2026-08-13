import FormalConjecturesUtil

/-!
# WOWII 183: the connected-domination-three tier

This file formalizes the paper proposition isolated in
`results/expansion/method_v04_183_tier_proof.md`: a distance-three geodesic,
together with the assertion that every connected dominating set has at least
three vertices, forces an induced bipartite subgraph on at least five
vertices.
-/

namespace WrittenOnTheWallII.GraphConjecture183GammaThree

open SimpleGraph Finset

variable {V : Type*} [Fintype V] [DecidableEq V]

omit [Fintype V] in
/-- A coloring of an induced subgraph extends over one new vertex provided
all of its new incident edges cross the two colors. -/
lemma induce_insert_isBipartite_of_coloring (G : SimpleGraph V) (s : Finset V)
    (v : V) (c : V → Fin 2)
    (hs : ∀ u ∈ s, ∀ w ∈ s, G.Adj u w → c u ≠ c w)
    (hv : ∀ u ∈ s, G.Adj v u → c v ≠ c u) :
    (G.induce (↑(insert v s) : Set V)).IsBipartite := by
  rw [induce_isBipartite_iff_exists_coloring]
  refine ⟨c, ?_⟩
  intro u hu w hw huw
  simp only [mem_insert] at hu hw
  rcases hu with rfl | hu <;> rcases hw with rfl | hw
  · exact (G.loopless _ huw).elim
  · exact hv w hw huw
  · exact fun h ↦ hv u hu huw.symm h.symm
  · exact hs u hu w hw huw

/-- The finite witness form of the `gamma_c >= 3` tier.

The vertices `x-a-d-z` exhibit a distance-three geodesic.  The domination
hypothesis is the finite, pointwise form of `3 ≤ connectedDominationNumber G`.
The conclusion retains the actual five-vertex induced bipartite witness.
-/
theorem exists_induced_bipartite_five_of_dist_three
    (G : SimpleGraph V) {x a d z : V}
    (hdist : G.dist x z = 3)
    (hxa : G.Adj x a) (had : G.Adj a d) (hdz : G.Adj d z)
    (hgamma : ∀ D : Finset V,
      G.IsConnectedDominating (↑D : Set V) → 3 ≤ D.card) :
    ∃ S : Finset V, S.card = 5 ∧ (G.induce (↑S : Set V)).IsBipartite := by
  classical
  let P : Finset V := {x, a, d, z}
  let A : Finset V := {x, d}
  let C : Finset V := {a, z}
  have hPAC : P = A ∪ C := by
    ext u
    simp only [P, A, C, mem_insert, mem_singleton, mem_union]
    tauto
  have hxb : ¬G.Adj x d := by
    intro hxd
    have hle := G.dist_le (hxd.toWalk.append hdz.toWalk)
    simp only [Walk.length_append, Walk.length_cons, Walk.length_nil,
      zero_add] at hle
    omega
  have hxz : ¬G.Adj x z := by
    intro hxz
    have hle := G.dist_le hxz.toWalk
    simp only [Walk.length_cons, Walk.length_nil, zero_add] at hle
    omega
  have haz : ¬G.Adj a z := by
    intro haz
    have hle := G.dist_le (hxa.toWalk.append haz.toWalk)
    simp only [Walk.length_append, Walk.length_cons, Walk.length_nil,
      zero_add] at hle
    omega
  have hdistinct : ({x, a, d, z} : Finset V).card = 4 := by
    have hxa_ne : x ≠ a := hxa.ne
    have had_ne : a ≠ d := had.ne
    have hdz_ne : d ≠ z := hdz.ne
    have hxd_ne : x ≠ d := by
      intro h
      subst d
      exact hxz hdz
    have hxz_ne : x ≠ z := by
      intro h
      subst z
      simp at hdist
    have haz_ne : a ≠ z := by
      intro h
      subst z
      exact hxz hxa
    simp [hxa_ne, had_ne, hdz_ne, hxd_ne, hxz_ne, haz_ne]
  have hPcolor : ∀ u ∈ P, ∀ w ∈ P, G.Adj u w →
      (if u ∈ A then (0 : Fin 2) else 1) ≠
        (if w ∈ A then (0 : Fin 2) else 1) := by
    intro u hu w hw huw heq
    have huP : u = x ∨ u = a ∨ u = d ∨ u = z := by
      simpa only [P, mem_insert, mem_singleton] using hu
    have hwP : w = x ∨ w = a ∨ w = d ∨ w = z := by
      simpa only [P, mem_insert, mem_singleton] using hw
    by_cases huA : u ∈ A
    · have hwA : w ∈ A := by
        by_contra hn
        simp [huA, hn] at heq
      have huPair : u = x ∨ u = d := by simpa [A] using huA
      have hwPair : w = x ∨ w = d := by simpa [A] using hwA
      rcases huPair with rfl | rfl <;> rcases hwPair with rfl | rfl
      · exact G.loopless _ huw
      · exact hxb huw
      · exact hxb huw.symm
      · exact G.loopless _ huw
    · have hwA : w ∉ A := by
        intro hwA
        simp [huA, hwA] at heq
      have huPair : u = a ∨ u = z := by
        rcases huP with rfl | rfl | rfl | rfl
        · exact (huA (by simp [A])).elim
        · exact Or.inl rfl
        · exact (huA (by simp [A])).elim
        · exact Or.inr rfl
      have hwPair : w = a ∨ w = z := by
        rcases hwP with rfl | rfl | rfl | rfl
        · exact (hwA (by simp [A])).elim
        · exact Or.inl rfl
        · exact (hwA (by simp [A])).elim
        · exact Or.inr rfl
      rcases huPair with rfl | rfl <;> rcases hwPair with rfl | rfl
      · exact G.loopless _ huw
      · exact haz huw
      · exact haz huw.symm
      · exact G.loopless _ huw
  by_cases hA : ∃ v, v ∉ P ∧ ∀ u ∈ A, ¬G.Adj v u
  · obtain ⟨v, hvP, hvA⟩ := hA
    let c : V → Fin 2 := fun u ↦ if u = v then 0 else if u ∈ A then 0 else 1
    refine ⟨insert v P, ?_, ?_⟩
    · rw [card_insert_of_notMem hvP, show P.card = 4 by simpa [P] using hdistinct]
    · apply induce_insert_isBipartite_of_coloring G P v c
      · intro u hu w hw huw
        have huv : u ≠ v := fun h ↦ hvP (h ▸ hu)
        have hwv : w ≠ v := fun h ↦ hvP (h ▸ hw)
        simpa [c, huv, hwv] using hPcolor u hu w hw huw
      · intro u hu huv
        have huA : u ∉ A := by
          intro huA
          exact hvA u huA huv
        have huv_ne : u ≠ v := huv.ne.symm
        simp [c, huv_ne, huA]
  · have hAall : ∀ v, v ∉ P → ∃ u ∈ A, G.Adj v u := by
      intro v hvP
      by_contra hn
      push_neg at hn
      exact hA ⟨v, hvP, hn⟩
    by_cases hC : ∃ v, v ∉ P ∧ ∀ u ∈ C, ¬G.Adj v u
    · obtain ⟨v, hvP, hvC⟩ := hC
      let c : V → Fin 2 := fun u ↦ if u ∈ A then 0 else 1
      refine ⟨insert v P, ?_, ?_⟩
      · rw [card_insert_of_notMem hvP, show P.card = 4 by simpa [P] using hdistinct]
      · apply induce_insert_isBipartite_of_coloring G P v c
        · simpa [c] using hPcolor
        · intro u hu huv
          have hvAnot : v ∉ A := by
            intro hvA
            have hvP' : v ∈ P := by
              rcases (show v = x ∨ v = d by simpa [A] using hvA) with rfl | rfl <;>
                simp [P]
            exact hvP hvP'
          have huA : u ∈ A := by
            rw [hPAC] at hu
            rcases Finset.mem_union.mp hu with huA | huC
            · exact huA
            · exact (hvC u huC huv).elim
          simp [c, hvAnot, huA]
    · have hCall : ∀ v, v ∉ P → ∃ u ∈ C, G.Adj v u := by
        intro v hvP
        by_contra hn
        push_neg at hn
        exact hC ⟨v, hvP, hn⟩
      let D : Finset V := {a, d}
      have hDdom : G.IsDominating (↑D : Set V) := by
        intro v
        by_cases hvD : v ∈ D
        · exact Or.inl hvD
        · right
          by_cases hvP : v ∈ P
          · simp only [P, D, mem_insert, mem_singleton] at hvP hvD
            rcases hvP with (rfl | rfl | rfl | rfl)
            · exact ⟨a, by simp [D], hxa⟩
            · exact (hvD (by simp)).elim
            · exact (hvD (by simp)).elim
            · exact ⟨d, by simp [D], hdz.symm⟩
          · obtain ⟨u, huA, hvu⟩ := hAall v hvP
            obtain ⟨w, hwC, hvw⟩ := hCall v hvP
            have hua : u = x ∨ u = d := by simpa [A] using huA
            have hwc : w = a ∨ w = z := by simpa [C] using hwC
            by_cases hvd : G.Adj v d
            · exact ⟨d, by simp [D], hvd⟩
            · by_cases hva : G.Adj v a
              · exact ⟨a, by simp [D], hva⟩
              · have hvx : G.Adj v x := by
                  rcases hua with rfl | rfl
                  · exact hvu
                  · exact (hvd hvu).elim
                have hvz : G.Adj v z := by
                  rcases hwc with rfl | rfl
                  · exact (hva hvw).elim
                  · exact hvw
                have hle := G.dist_le (hvx.symm.toWalk.append hvz.toWalk)
                simp only [Walk.length_append, Walk.length_cons, Walk.length_nil,
                  zero_add] at hle
                omega
      have hDconn : (G.induce (↑D : Set V)).Connected := by
        letI : Nonempty (↑D : Set V) := ⟨⟨a, by simp [D]⟩⟩
        constructor
        intro u v
        by_cases huv : u = v
        · subst v
          exact .rfl
        · have hu : u.1 = a ∨ u.1 = d := by
            simpa [D] using u.2
          have hv : v.1 = a ∨ v.1 = d := by
            simpa [D] using v.2
          rcases hu with hu | hu <;> rcases hv with hv | hv
          · exact (huv (Subtype.ext (hu.trans hv.symm))).elim
          · apply Adj.reachable
            change G.Adj u.1 v.1
            simpa [hu, hv] using had
          · apply Adj.reachable
            change G.Adj u.1 v.1
            simpa [hu, hv] using had.symm
          · exact (huv (Subtype.ext (hu.trans hv.symm))).elim
      have hthree := hgamma D ⟨hDdom, hDconn⟩
      have hDcard : D.card = 2 := by
        have had_ne : a ≠ d := had.ne
        simp [D, had_ne]
      omega

/-- Strong paper form: in a finite connected graph, a distance-three pair and
the lower bound three on connected dominating sets force a five-vertex
induced bipartite subgraph.  The intermediate geodesic vertices are extracted
from a shortest path rather than supplied as hypotheses. -/
theorem exists_induced_bipartite_five_of_connected
    (G : SimpleGraph V) (hconn : G.Connected) {x z : V}
    (hdist : G.dist x z = 3)
    (hgamma : ∀ D : Finset V,
      G.IsConnectedDominating (↑D : Set V) → 3 ≤ D.card) :
    ∃ S : Finset V, S.card = 5 ∧ (G.induce (↑S : Set V)).IsBipartite := by
  obtain ⟨p, _hpPath, hpLength⟩ := hconn.exists_path_of_dist x z
  let a := p.getVert 1
  let d := p.getVert 2
  have hpThree : p.length = 3 := hpLength.trans hdist
  have hzero : 0 < p.length := by omega
  have hone : 1 < p.length := by omega
  have htwo : 2 < p.length := by omega
  have hxa : G.Adj x a := by
    simpa [a] using p.adj_getVert_succ hzero
  have had : G.Adj a d := by
    simpa [a, d] using p.adj_getVert_succ hone
  have hdz : G.Adj d z := by
    rw [← p.getVert_length]
    simpa [d, hpThree] using p.adj_getVert_succ htwo
  exact exists_induced_bipartite_five_of_dist_three G hdist hxa had hdz hgamma

/-- Repository-invariant form of the preceding explicit witness theorem. -/
theorem five_le_largestInducedBipartiteSubgraphSize_of_dist_three
    (G : SimpleGraph V) {x a d z : V}
    (hdist : G.dist x z = 3)
    (hxa : G.Adj x a) (had : G.Adj a d) (hdz : G.Adj d z)
    (hgamma : ∀ D : Finset V,
      G.IsConnectedDominating (↑D : Set V) → 3 ≤ D.card) :
    5 ≤ G.largestInducedBipartiteSubgraphSize := by
  obtain ⟨S, hScard, hSbip⟩ :=
    exists_induced_bipartite_five_of_dist_three G hdist hxa had hdz hgamma
  unfold largestInducedBipartiteSubgraphSize
  apply le_csSup
  · exact ⟨Fintype.card V, fun n ⟨t, _ht, htn⟩ ↦ htn ▸ t.card_le_univ⟩
  · exact ⟨S, hSbip, hScard⟩

/-- Exact repository-invariant corollary of the strong connected paper form. -/
theorem five_le_largestInducedBipartiteSubgraphSize_of_connected
    (G : SimpleGraph V) (hconn : G.Connected) {x z : V}
    (hdist : G.dist x z = 3)
    (hgamma : ∀ D : Finset V,
      G.IsConnectedDominating (↑D : Set V) → 3 ≤ D.card) :
    5 ≤ G.largestInducedBipartiteSubgraphSize := by
  obtain ⟨S, hScard, hSbip⟩ :=
    exists_induced_bipartite_five_of_connected G hconn hdist hgamma
  unfold largestInducedBipartiteSubgraphSize
  apply le_csSup
  · exact ⟨Fintype.card V, fun n ⟨t, _ht, htn⟩ ↦ htn ▸ t.card_le_univ⟩
  · exact ⟨S, hSbip, hScard⟩

/-- Invariant-native statement of the proved tier: the actual
`connectedDominationNumber` lower bound implies the actual largest-induced-
bipartite-subgraph lower bound. -/
theorem five_le_largestInducedBipartiteSubgraphSize_of_connectedDominationNumber
    (G : SimpleGraph V) (hconn : G.Connected) {x z : V}
    (hdist : G.dist x z = 3)
    (hgamma : 3 ≤ G.connectedDominationNumber) :
    5 ≤ G.largestInducedBipartiteSubgraphSize := by
  apply five_le_largestInducedBipartiteSubgraphSize_of_connected G hconn hdist
  intro D hD
  apply hgamma.trans
  unfold connectedDominationNumber
  apply csInf_le
  · exact ⟨0, fun n _hn ↦ Nat.zero_le n⟩
  · exact ⟨D, hD, rfl⟩

/-- The same result in terms of the real-valued upstream notation `b G`. -/
theorem five_le_b_of_connectedDominationNumber
    (G : SimpleGraph V) (hconn : G.Connected) {x z : V}
    (hdist : G.dist x z = 3)
    (hgamma : 3 ≤ G.connectedDominationNumber) :
    (5 : ℝ) ≤ b G := by
  unfold b
  exact_mod_cast
    five_le_largestInducedBipartiteSubgraphSize_of_connectedDominationNumber
      G hconn hdist hgamma

end WrittenOnTheWallII.GraphConjecture183GammaThree
