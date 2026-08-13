import GraphConjecture59UnusedPool

/-!
# WOWII 59: residue coordinate of the unused-pool threshold

A covered unused pool can force a positive high degree.  This file proves the
exact general consequence for Havel--Hakimi residue and exhibits a star
showing that no low constant residue bound follows from that information.
-/

namespace WrittenOnTheWallII.GraphConjecture59ResidueThreshold

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture59CornerStructure
open WrittenOnTheWallII.GraphConjecture59UnusedPool

universe u
variable {V : Type u} [Fintype V] [DecidableEq V]

/-- Local length bound for the recursive residue computation. -/
theorem residueAux_le_length_local (s : List ℕ) : residueAux s ≤ s.length := by
  induction s using residueAux.induct with
  | case1 => simp [residueAux]
  | case2 s => simp only [residueAux.eq_2, List.length_cons]; omega
  | case3 d rest hd ih =>
      rw [residueAux.eq_3 d rest hd]
      calc
        residueAux (havelHakimiStep (d :: rest)) ≤
            (havelHakimiStep (d :: rest)).length := ih
        _ = rest.length := havelHakimiStep_length_cons d rest
        _ ≤ (d :: rest).length := by simp

omit [DecidableEq V] in
/-- A graph with any positive degree has residue at most one below its order.
This is the exact universal residue information supplied by merely forcing a
positive head in the descending degree sequence. -/
theorem residue_le_card_sub_one_of_positive_degree
    (G : SimpleGraph V) [DecidableRel G.Adj] (x : V)
    (hx : 0 < G.degree x) :
    residue G ≤ Fintype.card V - 1 := by
  let s := descendingDegreeSequence G
  have hxmem : G.degree x ∈ s := by
    simp [s, descendingDegreeSequence]
  have hsorted : s.Pairwise (· ≥ ·) := by
    exact Multiset.pairwise_sort _ _
  have hlen : s.length = Fintype.card V := by
    simp [s, descendingDegreeSequence]
  cases hseq : s with
  | nil => simp [hseq] at hxmem
  | cons d rest =>
      have hdx : G.degree x ≤ d := by
        have hhead := hsorted.rel_head hxmem
        simpa [hseq] using hhead
      have hd : d ≠ 0 := by omega
      have hrest : rest.length = Fintype.card V - 1 := by
        simp [hseq] at hlen
        omega
      unfold residue
      change residueAux s ≤ Fintype.card V - 1
      rw [hseq, residueAux.eq_3 d rest hd]
      calc
        residueAux (havelHakimiStep (d :: rest)) ≤
            (havelHakimiStep (d :: rest)).length :=
          residueAux_le_length_local _
        _ = rest.length := havelHakimiStep_length_cons d rest
        _ = Fintype.card V - 1 := hrest

/-- The v24 complete-cover/order threshold therefore saves one vertex in the
universal residue bound, but no more. -/
theorem residue_le_card_sub_one_of_unused_pool_cover
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (S : Finset V) (w x y z : V) (d : ℕ)
    (hSsix : S.card = 6)
    (hcover : ∀ p ∈ unusedPool S w x y z,
      G.Adj p x ∨ G.Adj p y ∨ G.Adj p z)
    (horder : 10 + 3 * d < Fintype.card V) :
    residue G ≤ Fintype.card V - 1 := by
  rcases one_degree_gt_of_unused_pool_cover
    G S w x y z d hSsix hcover horder with hx | hy | hz
  · exact residue_le_card_sub_one_of_positive_degree G x (by omega)
  · exact residue_le_card_sub_one_of_positive_degree G y (by omega)
  · exact residue_le_card_sub_one_of_positive_degree G z (by omega)

/-- The Havel--Hakimi residue of an all-zero list is its length. -/
theorem residueAux_replicate_zero (n : ℕ) :
    residueAux (List.replicate n 0) = n := by
  cases n with
  | zero => rw [List.replicate_zero, residueAux.eq_1]
  | succ n =>
      rw [List.replicate_succ, residueAux.eq_2]
      simp only [List.length_replicate]
      omega

/-- The star degree profile has residue equal to its number of leaves. -/
theorem residueAux_star_profile (n : ℕ) :
    residueAux ((n + 1) :: List.replicate (n + 1) 1) = n + 1 := by
  rw [residueAux.eq_3 (n + 1) (List.replicate (n + 1) 1) (by omega)]
  have hstep : havelHakimiStep
      ((n + 1) :: List.replicate (n + 1) 1) =
      List.replicate (n + 1) 0 := by
    simp [havelHakimiStep, List.splitAt_eq]
    apply List.mergeSort_eq_self (· ≥ ·)
    simp
  rw [hstep, residueAux_replicate_zero]

namespace StarCountermodel

/-- The fourteen-vertex star, oriented only for `fromRel`; the resulting
simple graph symmetrizes the relation. -/
def graph : SimpleGraph (Fin 14) :=
  SimpleGraph.fromRel fun u v ↦ u.val = 0 ∧ v.val ≠ 0

instance : DecidableRel graph.Adj := by
  unfold graph
  infer_instance

def profile : List ℕ :=
  13 :: List.replicate 13 1

/-- Exact descending degree profile of the concrete star. -/
theorem descending_degree_profile :
    descendingDegreeSequence graph = profile := by
  unfold descendingDegreeSequence
  rw [show Finset.univ.val.map (fun v : Fin 14 ↦ graph.degree v) =
      (↑profile : Multiset ℕ) by decide]
  rw [Multiset.coe_sort]
  apply List.mergeSort_eq_self (· ≥ ·)
  simp [profile]

/-- The concrete star has residue thirteen. -/
theorem residue_eq_thirteen : residue graph = 13 := by
  unfold residue
  change residueAux (descendingDegreeSequence graph) = 13
  rw [descending_degree_profile]
  simpa [profile] using residueAux_star_profile 12

def core : Finset (Fin 14) :=
  {1, 2, 3, 4, 5, 6}

/-- The same star satisfies the v24 pool-cover and order-slack premises for
`d=1`, while its actual residue is thirteen rather than at most three. -/
theorem covered_pool_high_degree_does_not_force_low_residue :
    core.card = 6 ∧
    (∀ p ∈ unusedPool core 7 0 8 9,
      graph.Adj p 0 ∨ graph.Adj p 8 ∨ graph.Adj p 9) ∧
    10 + 3 * 1 < Fintype.card (Fin 14) ∧
    residue graph = 13 := by
  exact ⟨by decide, by decide, by decide, residue_eq_thirteen⟩

end StarCountermodel

namespace SplitResidueThreeCountermodel

/-- Join of an eleven-vertex clique and a three-vertex independent set. -/
def graph : SimpleGraph (Fin 14) :=
  SimpleGraph.fromRel fun u _ ↦ u.val < 11

instance : DecidableRel graph.Adj := by
  unfold graph
  infer_instance

def profile : List ℕ :=
  List.replicate 11 13 ++ List.replicate 3 11

/-- Exact descending degree profile: eleven universal vertices followed by
three vertices of degree eleven. -/
theorem descending_degree_profile :
    descendingDegreeSequence graph = profile := by
  unfold descendingDegreeSequence
  rw [show Finset.univ.val.map (fun v : Fin 14 ↦ graph.degree v) =
      (↑profile : Multiset ℕ) by decide]
  rw [Multiset.coe_sort]
  apply List.mergeSort_eq_self (· ≥ ·)
  simp [profile]

/-- Despite maximum degree thirteen, the split graph has residue exactly
three. -/
theorem residue_eq_three : residue graph = 3 := by
  unfold residue
  change residueAux (descendingDegreeSequence graph) = 3
  rw [descending_degree_profile]
  change residueAux
    [13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 11, 11, 11] = 3
  set_option maxRecDepth 10000 in
    norm_num [residueAux, havelHakimiStep, List.splitAt_eq, List.mergeSort]

def core : Finset (Fin 14) :=
  {1, 2, 3, 4, 5, 6}

/-- Residue three, a degree-thirteen target, and the v24 pool-cover/order
premises coexist.  Hence residue three supplies no useful upper bound on the
degree forced by that branch. -/
theorem residue_three_does_not_bound_the_forced_degree :
    core.card = 6 ∧
    (∀ p ∈ unusedPool core 7 0 8 9,
      graph.Adj p 0 ∨ graph.Adj p 8 ∨ graph.Adj p 9) ∧
    10 + 3 * 1 < Fintype.card (Fin 14) ∧
    graph.degree 0 = 13 ∧
    residue graph = 3 := by
  exact ⟨by decide, by decide, by decide, by decide, residue_eq_three⟩

end SplitResidueThreeCountermodel

end WrittenOnTheWallII.GraphConjecture59ResidueThreshold
