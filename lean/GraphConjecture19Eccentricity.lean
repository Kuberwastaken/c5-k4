import FormalConjecturesUtil

/-!
# WOWII 19: finite maxima and the eccentricity-average floor

This file isolates two elementary parts of the proposed bound.  First, the
`sSup` of the finitely many local independence numbers is an attained maximum.
Second, if a connected finite graph is not self-centered, its average
eccentricity is strictly below its diameter, giving the expected integral
floor bound.
-/

namespace WrittenOnTheWallII.GraphConjecture19Eccentricity

open SimpleGraph Finset

universe u

variable {V : Type u} [Fintype V]

/-- The finite maximum used to normalize the upstream `sSup` expression. -/
noncomputable def maxIndepNeighbors [Nonempty V] (G : SimpleGraph V) : ℝ :=
  let values := Finset.univ.image (indepNeighbors G)
  values.max' (Finset.univ_nonempty.image _)

/-- The supremum of the range of `indepNeighbors` is its ordinary finite
maximum. -/
lemma sSup_range_indepNeighbors_eq_maxIndepNeighbors [Nonempty V]
    (G : SimpleGraph V) :
    sSup (Set.range (indepNeighbors G)) = maxIndepNeighbors G := by
  classical
  unfold maxIndepNeighbors
  rw [← (Finset.univ_nonempty.image (indepNeighbors G)).csSup_eq_max']
  congr 1
  ext x
  simp

/-- In particular, the finite supremum is attained at a vertex. -/
lemma exists_indepNeighbors_eq_sSup [Nonempty V] (G : SimpleGraph V) :
    ∃ v : V, indepNeighbors G v = sSup (Set.range (indepNeighbors G)) := by
  classical
  let values := Finset.univ.image (indepNeighbors G)
  have hvalues : values.Nonempty := Finset.univ_nonempty.image _
  have hmem : values.max' hvalues ∈ values := Finset.max'_mem values hvalues
  obtain ⟨v, _hv, hvmax⟩ := Finset.mem_image.mp hmem
  refine ⟨v, ?_⟩
  rw [sSup_range_indepNeighbors_eq_maxIndepNeighbors]
  simpa [maxIndepNeighbors, values] using hvmax

/-- Normalization directly in terms of the natural-valued local invariant. -/
lemma exists_indepNeighborsCard_cast_eq_sSup [Nonempty V] (G : SimpleGraph V) :
    ∃ v : V, (indepNeighborsCard G v : ℝ) =
      sSup (Set.range (indepNeighbors G)) := by
  simpa [indepNeighbors] using exists_indepNeighbors_eq_sSup G

/-- Adding the attained local invariant commutes exactly with integer floor. -/
lemma exists_floor_add_sSup_eq_floor_add_indepNeighborsCard
    [Nonempty V] (G : SimpleGraph V) (x : ℝ) :
    ∃ v : V,
      ⌊x + sSup (Set.range (indepNeighbors G))⌋ =
        ⌊x⌋ + (indepNeighborsCard G v : ℤ) := by
  obtain ⟨v, hv⟩ := exists_indepNeighborsCard_cast_eq_sSup G
  refine ⟨v, ?_⟩
  rw [← hv, Int.floor_add_natCast]

/-- Connectedness makes every eccentricity finite and bounded by the natural
diameter. -/
lemma eccent_toNat_le_diam (G : SimpleGraph V) [Nonempty V]
    (hconn : G.Connected) (v : V) :
    (G.eccent v).toNat ≤ G.diam := by
  exact ENat.toNat_le_toNat G.eccent_le_ediam
    (SimpleGraph.connected_iff_ediam_ne_top.mp hconn)

/-- A strict extended-eccentricity inequality remains strict after `toNat`
when connectedness guarantees finiteness. -/
lemma eccent_toNat_lt_diam (G : SimpleGraph V) [Nonempty V]
    (hconn : G.Connected) {v : V} (hv : G.eccent v < G.ediam) :
    (G.eccent v).toNat < G.diam := by
  have hed : G.ediam ≠ ⊤ := SimpleGraph.connected_iff_ediam_ne_top.mp hconn
  have hecc : G.eccent v ≠ ⊤ := ne_top_of_le_ne_top hed G.eccent_le_ediam
  apply ENat.coe_lt_coe.mp
  simpa [SimpleGraph.diam, ENat.coe_toNat hecc, ENat.coe_toNat hed] using hv

/-- If one vertex has eccentricity below the diameter, the real average of
the natural eccentricities is strictly below the diameter. -/
lemma average_eccentricity_lt_diam_of_exists_lt_ediam
    (G : SimpleGraph V) [Nonempty V] (hconn : G.Connected)
    (hnotcentered : ∃ v : V, G.eccent v < G.ediam) :
    (∑ v : V, ((G.eccent v).toNat : ℝ)) / (Fintype.card V : ℝ) <
      (G.diam : ℝ) := by
  obtain ⟨w, hw⟩ := hnotcentered
  have hsumNat : (∑ v : V, (G.eccent v).toNat) <
      ∑ _v : V, G.diam := by
    apply Finset.sum_lt_sum
    · intro v _hv
      exact eccent_toNat_le_diam G hconn v
    · exact ⟨w, Finset.mem_univ w, eccent_toNat_lt_diam G hconn hw⟩
  have hsumReal : (∑ v : V, ((G.eccent v).toNat : ℝ)) <
      (Fintype.card V : ℝ) * (G.diam : ℝ) := by
    have hsumNat' : (∑ v : V, (G.eccent v).toNat) <
        Fintype.card V * G.diam := by
      simpa using hsumNat
    exact_mod_cast hsumNat'
  have hcard : (0 : ℝ) < Fintype.card V := by
    exact_mod_cast Fintype.card_pos
  rw [div_lt_iff₀ hcard]
  simpa [mul_comm] using hsumReal

/-- Integral form needed by the WOWII 19 proof: a non-self-centered graph
loses at least one whole unit after flooring its average eccentricity. -/
lemma floor_average_eccentricity_le_diam_sub_one
    (G : SimpleGraph V) [Nonempty V] (hconn : G.Connected)
    (hnotcentered : ∃ v : V, G.eccent v < G.ediam) :
    ⌊(∑ v ∈ Finset.univ, ((G.eccent v).toNat : ℝ)) /
      (Fintype.card V : ℝ)⌋ ≤ (G.diam : ℤ) - 1 := by
  have havg := average_eccentricity_lt_diam_of_exists_lt_ediam
    G hconn hnotcentered
  have hfloor :
      ⌊(∑ v ∈ Finset.univ, ((G.eccent v).toNat : ℝ)) /
          (Fintype.card V : ℝ)⌋ < (G.diam : ℤ) := by
    rw [Int.floor_lt]
    simpa using havg
  omega

/-- The finite-maximum and average-floor statements assemble without any
rounding loss: the local term is an integer, so it passes through `floor`. -/
lemma exists_floor_average_add_sSup_le_diam_add_indepNeighborsCard_sub_one
    (G : SimpleGraph V) [Nonempty V] (hconn : G.Connected)
    (hnotcentered : ∃ v : V, G.eccent v < G.ediam) :
    ∃ v : V,
      ⌊(∑ u ∈ Finset.univ, ((G.eccent u).toNat : ℝ)) /
          (Fintype.card V : ℝ) +
          sSup (Set.range (indepNeighbors G))⌋ ≤
        (G.diam : ℤ) + (indepNeighborsCard G v : ℤ) - 1 := by
  let avg : ℝ :=
    (∑ u ∈ Finset.univ, ((G.eccent u).toNat : ℝ)) /
      (Fintype.card V : ℝ)
  obtain ⟨v, hv⟩ :=
    exists_floor_add_sSup_eq_floor_add_indepNeighborsCard G avg
  refine ⟨v, ?_⟩
  change ⌊avg + sSup (Set.range (indepNeighbors G))⌋ ≤ _
  rw [hv]
  have havg : ⌊avg⌋ ≤ (G.diam : ℤ) - 1 := by
    exact floor_average_eccentricity_le_diam_sub_one G hconn hnotcentered
  omega

end WrittenOnTheWallII.GraphConjecture19Eccentricity
