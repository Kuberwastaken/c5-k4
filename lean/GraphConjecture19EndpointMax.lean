import GraphConjecture19StarBound
import GraphConjecture19CanonicalTailColor

/-!
# WOWII 19/13: corrected endpoint-maximum reduction
-/

namespace WrittenOnTheWallII.GraphConjecture19EndpointMax

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture19StarBound
open WrittenOnTheWallII.GraphConjecture19CanonicalTailColor

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

/-- Finite maximum local independence number. -/
noncomputable def localMax [Nonempty V] (G : SimpleGraph V) : ℕ :=
  (Finset.univ.image (indepNeighborsCard G)).max'
    (Finset.univ_nonempty.image _)

omit [DecidableEq V] in
/-- The finite local maximum is attained. -/
lemma exists_indepNeighborsCard_eq_localMax [Nonempty V] (G : SimpleGraph V) :
    ∃ v : V, indepNeighborsCard G v = localMax G := by
  classical
  have hm := Finset.max'_mem
    (Finset.univ.image (indepNeighborsCard G))
    (Finset.univ_nonempty.image (indepNeighborsCard G))
  obtain ⟨v, _hv, hv⟩ := Finset.mem_image.mp hm
  exact ⟨v, hv⟩

/-- The maximum induced star gives `b >= localMax + 1`. -/
theorem localMax_add_one_le_b [Nonempty V]
    (G : SimpleGraph V) [DecidableRel G.Adj] :
    (((localMax G + 1 : ℕ) : ℝ)) ≤ b G := by
  obtain ⟨v, hv⟩ := exists_indepNeighborsCard_eq_localMax G
  have hI : G.IsIndepSet ((∅ : Finset V) : Set V) := by simp
  have hIout : ∀ x ∈ (∅ : Finset V), x ≠ v ∧ ¬G.Adj v x := by simp
  have hstar := indepNeighborsCard_add_card_add_one_le_b
    G v (∅ : Finset V) hI hIout
  simpa [hv] using hstar

/-- WOWII 13 is immediate from the maximum induced star when diameter is at
most two. -/
theorem wowii13_of_diam_le_two [Nonempty V]
    (G : SimpleGraph V) [DecidableRel G.Adj] (hdiam : G.diam ≤ 2) :
    (G.diam : ℝ) + (localMax G : ℝ) - 1 ≤ b G := by
  have hstar := localMax_add_one_le_b G
  have harith : (G.diam : ℝ) + (localMax G : ℝ) - 1 ≤
      ((localMax G + 1 : ℕ) : ℝ) := by
    have hdR : (G.diam : ℝ) ≤ 2 := by exact_mod_cast hdiam
    norm_num at hstar ⊢
    linarith
  exact harith.trans hstar

/-- Corrected sufficient endpoint lemma.  If a diametral endpoint loses at
most one unit of local independence relative to the global maximum, the
canonical endpoint witness proves WOWII 13. -/
theorem wowii13_of_diametral_endpoint_within_one [Nonempty V]
    (G : SimpleGraph V) [DecidableRel G.Adj] (u v : V)
    (hconn : G.Connected) (huv : G.dist u v = G.diam)
    (hdiam : 2 ≤ G.diam)
    (hlocal : localMax G ≤ indepNeighborsCard G u + 1) :
    (G.diam : ℝ) + (localMax G : ℝ) - 1 ≤ b G := by
  have hend := diam_add_indepNeighborsCard_le_b_of_diametral_endpoint
    G u v hconn huv hdiam
  have harith : (G.diam : ℝ) + (localMax G : ℝ) - 1 ≤
      ((G.diam + indepNeighborsCard G u : ℕ) : ℝ) := by
    have hlR : (localMax G : ℝ) ≤ (indepNeighborsCard G u : ℝ) + 1 := by
      exact_mod_cast hlocal
    norm_num at hend ⊢
    linarith
  exact harith.trans hend

end WrittenOnTheWallII.GraphConjecture19EndpointMax
