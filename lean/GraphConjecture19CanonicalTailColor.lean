import GraphConjecture19CanonicalTail
import GraphConjecture19EndpointWitness

/-!
# WOWII 19/13: distance-parity coloring of the canonical tail
-/

open WrittenOnTheWallII.GraphConjecture19DiameterBaseline
open WrittenOnTheWallII.GraphConjecture19CanonicalTail
open WrittenOnTheWallII.GraphConjecture19EndpointWitness

namespace WrittenOnTheWallII.GraphConjecture19CanonicalTailColor

open SimpleGraph Finset

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

/-- Even endpoint distance receives color one. -/
noncomputable def tailColor (G : SimpleGraph V) (u : V) : V → Fin 2 :=
  fun x => if Even (G.dist u x) then 1 else 0

omit [Fintype V] [DecidableEq V] in
lemma dist_start_getVert {G : SimpleGraph V} {u v : V} (p : G.Walk u v)
    (hp : p.length = G.dist u v) {i : ℕ} (hi : i ≤ p.length) :
    G.dist u (p.getVert i) = i := by
  have h := dist_getVert_eq_natDist_of_length_eq_dist p hp
      (show 0 ≤ p.length by omega) hi
  simpa only [p.getVert_zero, Nat.dist_zero_left] using h

omit [Fintype V] [DecidableEq V] in
lemma even_ne_even_of_natDist_eq_one {i j : ℕ} (h : i.dist j = 1) :
    Even i ↔ ¬Even j := by
  rcases le_total i j with hij | hji
  · rw [Nat.dist_eq_sub_of_le hij] at h
    have : j = i + 1 := by omega
    subst j
    have he := Nat.even_add_one (n := i)
    tauto
  · rw [Nat.dist_comm, Nat.dist_eq_sub_of_le hji] at h
    have : i = j + 1 := by omega
    subst i
    have he := Nat.even_add_one (n := j)
    tauto

omit [Fintype V] in
/-- The endpoint-distance parity coloring properly colors the canonical tail. -/
lemma canonicalTail_colored
    {G : SimpleGraph V} {u v : V} (p : G.Walk u v)
    (hp : p.length = G.dist u v) :
    ∀ x ∈ canonicalTail p,
      ∀ y ∈ canonicalTail p,
        G.Adj x y → tailColor G u x ≠ tailColor G u y := by
  intro x hx y hy hxy
  obtain ⟨i, hi, rfl⟩ := Finset.mem_image.mp hx
  obtain ⟨j, hj, rfl⟩ := Finset.mem_image.mp hy
  have hi' := (mem_retainedIndices_iff p i).mp hi
  have hj' := (mem_retainedIndices_iff p j).mp hj
  have hil : i ≤ p.length := hi'.elim (fun h => by omega) (fun h => h.2)
  have hjl : j ≤ p.length := hj'.elim (fun h => by omega) (fun h => h.2)
  have hd := dist_getVert_eq_natDist_of_length_eq_dist p hp hil hjl
  have hadjDist : G.dist (p.getVert i) (p.getVert j) = 1 :=
    dist_eq_one_iff_adj.mpr hxy
  have hpar : Even i ↔ ¬Even j := even_ne_even_of_natDist_eq_one (hd ▸ hadjDist)
  simp only [tailColor, dist_start_getVert p hp hil, dist_start_getVert p hp hjl]
  by_cases hei : Even i <;> by_cases hej : Even j <;> simp_all

/-- Any edge from the endpoint neighborhood to the canonical tail lands at
even endpoint distance, hence at color one. -/
lemma canonicalTail_cross_colored
    {G : SimpleGraph V} [DecidableRel G.Adj] {u v : V} (p : G.Walk u v)
    (hp : p.length = G.dist u v) :
    ∀ a ∈ G.neighborFinset u,
      ∀ q ∈ canonicalTail p,
        G.Adj a q → tailColor G u q ≠ 0 := by
  intro a ha q hq haq
  obtain ⟨i, hi, rfl⟩ := Finset.mem_image.mp hq
  have hi' := (mem_retainedIndices_iff p i).mp hi
  have hil : i ≤ p.length := hi'.elim (fun h => by omega) (fun h => h.2)
  have hdist : G.dist u (p.getVert i) = i := dist_start_getVert p hp hil
  have hua : G.Adj u a := by simpa [mem_neighborFinset] using ha
  have htri : G.dist u (p.getVert i) ≤ G.dist u a + G.dist a (p.getVert i) :=
    haq.reachable.dist_triangle_right u
  rw [dist_eq_one_iff_adj.mpr hua, dist_eq_one_iff_adj.mpr haq, hdist] at htri
  have hei : Even i := by
    rcases hi' with rfl | hi2
    · exact ⟨0, by omega⟩
    · have : i = 2 := by omega
      subst i
      norm_num
  simp [tailColor, hdist, hei]

/-- The unconditional diametral-endpoint bound, assuming diameter at least two. -/
theorem diam_add_indepNeighborsCard_le_b_of_diametral_endpoint
    (G : SimpleGraph V) [DecidableRel G.Adj] (u v : V)
    (hconn : G.Connected) (huv : G.dist u v = G.diam)
    (hdiam : 2 ≤ G.diam) :
    (((G.diam + indepNeighborsCard G u : ℕ) : ℝ)) ≤ b G := by
  obtain ⟨p, hpPath, hpDist⟩ := hconn.exists_path_of_dist u v
  let Q := canonicalTail p
  have hcardOutside :=
    canonicalTail_card_and_outside_of_diametral p hpPath hpDist huv hdiam
  exact diam_add_indepNeighborsCard_le_b_of_endpoint_certificate
      G u Q (tailColor G u) hcardOutside.1 hcardOutside.2
      (canonicalTail_colored p hpDist) (canonicalTail_cross_colored p hpDist)

end WrittenOnTheWallII.GraphConjecture19CanonicalTailColor
