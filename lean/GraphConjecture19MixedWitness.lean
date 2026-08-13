import GraphConjecture19EndpointMax

/-!
# WOWII 19/13: mixed maximum-local-star and eccentric geodesic witness
-/

namespace WrittenOnTheWallII.GraphConjecture19MixedWitness

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture19CanonicalTail
open WrittenOnTheWallII.GraphConjecture19CanonicalTailColor
open WrittenOnTheWallII.GraphConjecture19EndpointWitness
open WrittenOnTheWallII.GraphConjecture19EndpointMax

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

/-- The canonical-tail construction works from any chosen start vertex to any
vertex at distance at least two; diameter maximality is not required. -/
theorem dist_add_indepNeighborsCard_le_b
    (G : SimpleGraph V) [DecidableRel G.Adj] (c w : V)
    (hconn : G.Connected) (hdist : 2 ≤ G.dist c w) :
    (((G.dist c w + indepNeighborsCard G c : ℕ) : ℝ)) ≤ b G := by
  obtain ⟨p, hpPath, hpDist⟩ := hconn.exists_path_of_dist c w
  let Q := canonicalTail p
  have hQcard : Q.card = G.dist c w := by
    dsimp [Q]
    rw [card_canonicalTail p hpPath (by omega), hpDist]
  have hQoutside : ∀ q ∈ Q, q = c ∨ ¬G.Adj c q := by
    exact fun q hq => canonicalTail_outside_openNeighborhood p hpDist q hq
  obtain ⟨A, hA, hAN, hAcard⟩ :=
    _root_.WrittenOnTheWallII.GraphConjecture19StarBound.exists_local_indep_witness G c
  have hdisj : Disjoint A Q := by
    rw [Finset.disjoint_left]
    intro x hxA hxQ
    have hxN : G.Adj c x := by simpa [mem_neighborFinset] using hAN hxA
    rcases hQoutside x hxQ with hxEq | hxnot
    · subst x
      exact G.loopless _ hxN
    · exact hxnot hxN
  have hcrossA : ∀ a ∈ A, ∀ q ∈ Q,
      G.Adj a q → tailColor G c q ≠ 0 := by
    intro a ha q hq haq
    exact canonicalTail_cross_colored p hpDist a (hAN ha) q hq haq
  have hb := card_add_card_le_b_of_colored_attachment
    G A Q (tailColor G c) hA hdisj
      (canonicalTail_colored p hpDist) hcrossA
  rw [hAcard, hQcard] at hb
  norm_num at hb ⊢
  linarith

/-- Correct mixed sufficient condition: if a vertex attaining the global
local maximum lies within one eccentricity unit of the diameter, its own
farthest geodesic proves WOWII 13. -/
theorem wowii13_of_localMax_vertex_with_long_geodesic
    (G : SimpleGraph V) [Nonempty V] [DecidableRel G.Adj] (c w : V)
    (hconn : G.Connected)
    (hcmax : indepNeighborsCard G c = localMax G)
    (hlong : G.diam ≤ G.dist c w + 1)
    (hdist : 2 ≤ G.dist c w) :
    (G.diam : ℝ) + (localMax G : ℝ) - 1 ≤ b G := by
  have hb := dist_add_indepNeighborsCard_le_b G c w hconn hdist
  have hlongR : (G.diam : ℝ) ≤ (G.dist c w : ℝ) + 1 := by
    exact_mod_cast hlong
  norm_num at hb ⊢
  rw [← hcmax]
  linarith

/-- Eccentricity-native form of the long-geodesic condition. -/
theorem wowii13_of_localMax_vertex_eccentricity_ge_diam_sub_one
    (G : SimpleGraph V) [Nonempty V] [DecidableRel G.Adj] (c : V)
    (hconn : G.Connected)
    (hcmax : indepNeighborsCard G c = localMax G)
    (hecc : G.diam ≤ (G.eccent c).toNat + 1)
    (heccTwo : 2 ≤ (G.eccent c).toNat) :
    (G.diam : ℝ) + (localMax G : ℝ) - 1 ≤ b G := by
  obtain ⟨w, hw⟩ := G.exists_edist_eq_eccent_of_finite c
  have hdist : G.dist c w = (G.eccent c).toNat := by
    exact congrArg ENat.toNat hw
  apply wowii13_of_localMax_vertex_with_long_geodesic G c w hconn hcmax
  · simpa [hdist] using hecc
  · simpa [hdist] using heccTwo

end WrittenOnTheWallII.GraphConjecture19MixedWitness
