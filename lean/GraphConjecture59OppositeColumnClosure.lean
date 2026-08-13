import GraphConjecture59ThreeCoreClosure
import GraphConjecture59CoreCoverSynthesis

/-!
# WOWII 59: closure at the opposite endpoint of the missing core edge

In the surviving `K3,3-e` branch the missing edge joins an aligned row `a`
to an opposite-side column vertex `t`.  Three five-forest exchanges force an
exact new attachment profile on `t`.
-/

namespace WrittenOnTheWallII.GraphConjecture59OppositeColumnClosure

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture59FullFanPropagation
open WrittenOnTheWallII.GraphConjecture59PathAttachmentSplit

universe u
variable {V : Type u} [Fintype V] [DecidableEq V]

omit [Fintype V] in
/-- If the opposite endpoint `t` also misses `q`, the vertices can be added
as successive leaves along `q-d-t-b`, with `a` isolated. -/
theorem opposite_column_missing_q_isAcyclic
    (G : SimpleGraph V) (a b d t q : V)
    (hqa : ¬G.Adj q a) (hta : ¬G.Adj t a) (htq : ¬G.Adj t q)
    (hda : ¬G.Adj d a) (hba : ¬G.Adj b a)
    (hbd : ¬G.Adj b d) (hbq : ¬G.Adj b q) :
    (G.induce (({a, b, d, t, q} : Finset V) : Set V)).IsAcyclic := by
  have hI : G.IsIndepSet (({a, q} : Finset V) : Set V) := by
    intro x hx y hy hxy hadj
    change x ∈ ({a, q} : Finset V) at hx
    change y ∈ ({a, q} : Finset V) at hy
    simp only [mem_insert, mem_singleton] at hx hy
    rcases hx with rfl | rfl <;> rcases hy with rfl | rfl <;>
      simp_all [G.adj_comm]
  have hd :=
    _root_.WrittenOnTheWallII.GraphConjecture40Baseline.induce_insert_isAcyclic_of_indep
      G ({a, q} : Finset V) d hI
  have hd' :
      (G.induce (insert d ((({a, q} : Finset V) : Set V)))).IsAcyclic := by
    have hset :
        insert d ((({a, q} : Finset V) : Set V)) =
          (({d, a, q} : Finset V) : Set V) := by ext x; simp [or_left_comm]
    rw [hset]
    exact hd
  have hdt := induce_insert_isAcyclic_of_acyclic_of_unique_neighbor
    G (insert d ((({a, q} : Finset V) : Set V))) t hd' (by
      intro x hx y hy htx hty
      by_contra hxy
      change x = d ∨ x ∈ ({a, q} : Finset V) at hx
      change y = d ∨ y ∈ ({a, q} : Finset V) at hy
      simp only [mem_insert, mem_singleton] at hx hy
      rcases hx with rfl | rfl | rfl <;> rcases hy with rfl | rfl | rfl <;>
        simp_all [G.adj_comm])
  have hdtb := induce_insert_isAcyclic_of_acyclic_of_unique_neighbor
    G (insert t (insert d ((({a, q} : Finset V) : Set V)))) b hdt (by
      intro x hx y hy hbx hby
      by_contra hxy
      change x = t ∨ x = d ∨ x ∈ ({a, q} : Finset V) at hx
      change y = t ∨ y = d ∨ y ∈ ({a, q} : Finset V) at hy
      simp only [mem_insert, mem_singleton] at hx hy
      rcases hx with rfl | rfl | rfl | rfl <;>
        rcases hy with rfl | rfl | rfl | rfl <;> simp_all [G.adj_comm])
  have hset :
      (({a, b, d, t, q} : Finset V) : Set V) =
        insert b (insert t (insert d ((({a, q} : Finset V) : Set V)))) := by
    ext x
    simp [or_left_comm]
  rw [hset]
  exact hdtb

omit [Fintype V] in
/-- The star centered at `a` remains a forest after adding `t` whenever `t`
has at most one neighbor among the three leaves `u,v,p`. -/
theorem aligned_star_sparse_opposite_isAcyclic
    (G : SimpleGraph V) (a t u v p : V)
    (huv : ¬G.Adj u v) (hpu : ¬G.Adj p u) (hpv : ¬G.Adj p v)
    (hta : ¬G.Adj t a) (hsparse : ¬ThirdCoreCover G t p v u) :
    (G.induce (({a, t, u, v, p} : Finset V) : Set V)).IsAcyclic := by
  have hI : G.IsIndepSet (({u, v, p} : Finset V) : Set V) := by
    intro x hx y hy hxy hadj
    change x ∈ ({u, v, p} : Finset V) at hx
    change y ∈ ({u, v, p} : Finset V) at hy
    simp only [mem_insert, mem_singleton] at hx hy
    rcases hx with rfl | rfl | rfl <;> rcases hy with rfl | rfl | rfl <;>
      simp_all [G.adj_comm]
  have ha :=
    _root_.WrittenOnTheWallII.GraphConjecture40Baseline.induce_insert_isAcyclic_of_indep
      G ({u, v, p} : Finset V) a hI
  have ha' :
      (G.induce (insert a ((({u, v, p} : Finset V) : Set V)))).IsAcyclic := by
    have hset :
        insert a ((({u, v, p} : Finset V) : Set V)) =
          (({a, u, v, p} : Finset V) : Set V) := by ext x; simp
    rw [hset]
    exact ha
  have hat := induce_insert_isAcyclic_of_acyclic_of_unique_neighbor
    G (insert a ((({u, v, p} : Finset V) : Set V))) t ha' (by
      intro x hx y hy htx hty
      by_contra hxy
      change x = a ∨ x ∈ ({u, v, p} : Finset V) at hx
      change y = a ∨ y ∈ ({u, v, p} : Finset V) at hy
      simp only [mem_insert, mem_singleton] at hx hy
      rcases hx with rfl | rfl | rfl | rfl <;>
        rcases hy with rfl | rfl | rfl | rfl <;>
          simp_all [ThirdCoreCover, G.adj_comm])
  have hset :
      (({a, t, u, v, p} : Finset V) : Set V) =
        insert t (insert a ((({u, v, p} : Finset V) : Set V))) := by
    ext x
    simp [or_left_comm]
  rw [hset]
  exact hat

omit [Fintype V] in
/-- A path `u-c-v`, followed by a sparse `t`, followed by the possible leaf
`p`, is a forest. -/
theorem path_sparse_opposite_isAcyclic
    (G : SimpleGraph V) (t u c v p : V)
    (huv : ¬G.Adj u v) (hpu : ¬G.Adj p u)
    (hpc : ¬G.Adj p c) (hpv : ¬G.Adj p v)
    (hsparse : ¬ThirdCoreCover G t v c u) :
    (G.induce (({t, u, c, v, p} : Finset V) : Set V)).IsAcyclic := by
  have hI : G.IsIndepSet (({u, v} : Finset V) : Set V) := by
    intro x hx y hy hxy hadj
    change x ∈ ({u, v} : Finset V) at hx
    change y ∈ ({u, v} : Finset V) at hy
    simp only [mem_insert, mem_singleton] at hx hy
    rcases hx with rfl | rfl <;> rcases hy with rfl | rfl <;>
      simp_all [G.adj_comm]
  have hc :=
    _root_.WrittenOnTheWallII.GraphConjecture40Baseline.induce_insert_isAcyclic_of_indep
      G ({u, v} : Finset V) c hI
  have hc' :
      (G.induce (insert c ((({u, v} : Finset V) : Set V)))).IsAcyclic := by
    have hset :
        insert c ((({u, v} : Finset V) : Set V)) =
          (({c, u, v} : Finset V) : Set V) := by ext x; simp
    rw [hset]
    exact hc
  have hct := induce_insert_isAcyclic_of_acyclic_of_unique_neighbor
    G (insert c ((({u, v} : Finset V) : Set V))) t hc' (by
      intro x hx y hy htx hty
      by_contra hxy
      change x = c ∨ x ∈ ({u, v} : Finset V) at hx
      change y = c ∨ y ∈ ({u, v} : Finset V) at hy
      simp only [mem_insert, mem_singleton] at hx hy
      rcases hx with rfl | rfl | rfl <;> rcases hy with rfl | rfl | rfl <;>
        simp_all [ThirdCoreCover, G.adj_comm])
  have hctp := induce_insert_isAcyclic_of_acyclic_of_unique_neighbor
    G (insert t (insert c ((({u, v} : Finset V) : Set V)))) p hct (by
      intro x hx y hy hpx hpy
      by_contra hxy
      change x = t ∨ x = c ∨ x ∈ ({u, v} : Finset V) at hx
      change y = t ∨ y = c ∨ y ∈ ({u, v} : Finset V) at hy
      simp only [mem_insert, mem_singleton] at hx hy
      rcases hx with rfl | rfl | rfl | rfl <;>
        rcases hy with rfl | rfl | rfl | rfl <;> simp_all [G.adj_comm])
  have hset :
      (({t, u, c, v, p} : Finset V) : Set V) =
        insert p (insert t (insert c ((({u, v} : Finset V) : Set V)))) := by
    ext x
    simp only [Finset.coe_insert, Finset.coe_singleton, Set.mem_insert_iff,
      Set.mem_singleton_iff]
    aesop
  rw [hset]
  exact hctp

/-- Failure of any one of the three forced opposite-column conditions gives
an explicit induced forest of order five. -/
theorem opposite_column_forced_profile
    (G : SimpleGraph V) (a b d t u c v p q : V)
    (hcardQ : ({a, b, d, t, q} : Finset V).card = 5)
    (hcardStar : ({a, t, u, v, p} : Finset V).card = 5)
    (hcardPath : ({t, u, c, v, p} : Finset V).card = 5)
    (hqa : ¬G.Adj q a) (hqb : ¬G.Adj q b)
    (hta : ¬G.Adj t a)
    (hda : ¬G.Adj d a) (hba : ¬G.Adj b a) (hbd : ¬G.Adj b d)
    (huv : ¬G.Adj u v) (hpu : ¬G.Adj p u)
    (hpc : ¬G.Adj p c) (hpv : ¬G.Adj p v)
    (hf : G.largestInducedForestSize = 4) :
    G.Adj t q ∧ ThirdCoreCover G t p v u ∧
      ThirdCoreCover G t v c u := by
  have forceOfAcyclic (X : Finset V) (hcard : X.card = 5)
      (hacyc : (G.induce (X : Set V)).IsAcyclic) : False := by
    have hbound :=
      _root_.WrittenOnTheWallII.GraphConjecture40Baseline.card_le_largestInducedForestSize
        G X hacyc
    rw [hcard, hf] at hbound
    omega
  have htq : G.Adj t q := by
    by_contra htq
    exact forceOfAcyclic {a, b, d, t, q} hcardQ
      (opposite_column_missing_q_isAcyclic
        G a b d t q hqa hta htq hda hba hbd
          (by simpa [G.adj_comm] using hqb))
  have hstar : ThirdCoreCover G t p v u := by
    by_contra hsparse
    exact forceOfAcyclic {a, t, u, v, p} hcardStar
      (aligned_star_sparse_opposite_isAcyclic
        G a t u v p huv hpu hpv hta hsparse)
  have hpath : ThirdCoreCover G t v c u := by
    by_contra hsparse
    exact forceOfAcyclic {t, u, c, v, p} hcardPath
      (path_sparse_opposite_isAcyclic
        G t u c v p huv hpu hpc hpv hsparse)
  exact ⟨htq, hstar, hpath⟩

omit [Fintype V] [DecidableEq V] in
/-- The two forced covers have a compact exact form: `t` either sees both
path endpoints, or it sees the center and `p` together with one endpoint. -/
theorem two_opposite_covers_iff_exact_patterns
    (G : SimpleGraph V) (t u c v p : V) :
    (ThirdCoreCover G t p v u ∧ ThirdCoreCover G t v c u) ↔
      (G.Adj t u ∧ G.Adj t v) ∨
      (G.Adj t u ∧ G.Adj t c ∧ G.Adj t p) ∨
      (G.Adj t c ∧ G.Adj t v ∧ G.Adj t p) := by
  simp only [ThirdCoreCover]
  tauto

/-- Five explicit distinct neighbors certify the new degree consequence for
the deficient opposite-column endpoint. -/
theorem five_le_degree_of_fixed_three_and_cover
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (t b d q u v p : V)
    (hnodup : [b, d, q, u, v, p].Nodup)
    (htb : G.Adj t b) (htd : G.Adj t d) (htq : G.Adj t q)
    (hcover : ThirdCoreCover G t p v u) :
    5 ≤ G.degree t := by
  have fiveOfPair (x y : V) (hx : G.Adj t x) (hy : G.Adj t y)
      (hxy : [b, d, q, x, y].Nodup) : 5 ≤ G.degree t := by
    let N : Finset V := [b, d, q, x, y].toFinset
    have hNcard : N.card = 5 := by
      simpa [N] using List.toFinset_card_of_nodup hxy
    have hsub : N ⊆ G.neighborFinset t := by
      intro z hz
      simp only [N, List.mem_toFinset, List.mem_cons, List.not_mem_nil,
        or_false] at hz
      rcases hz with rfl | rfl | rfl | rfl | rfl <;>
        simp_all [G.mem_neighborFinset]
    have hcard := card_le_card hsub
    rw [hNcard, G.card_neighborFinset_eq_degree] at hcard
    exact hcard
  have hsubseqUV : [b, d, q, u, v].Nodup := by
    exact List.Nodup.sublist (by simp) hnodup
  have hsubseqUP : [b, d, q, u, p].Nodup := by
    exact List.Nodup.sublist (by simp) hnodup
  have hsubseqVP : [b, d, q, v, p].Nodup := by
    exact List.Nodup.sublist (by simp) hnodup
  rcases hcover with h | h | h
  · exact fiveOfPair u v h.1 h.2 hsubseqUV
  · exact fiveOfPair u p h.1 h.2 hsubseqUP
  · exact fiveOfPair v p h.1 h.2 hsubseqVP

end WrittenOnTheWallII.GraphConjecture59OppositeColumnClosure
