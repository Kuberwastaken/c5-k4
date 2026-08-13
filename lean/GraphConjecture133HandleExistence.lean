import GraphConjecture133DeepHandle

/-!
# WOWII 133: reducing deep-handle existence to early contacts

Shortestness automatically excludes late returns from vertices at distance
two or three behind a geodesic head.  Consequently only finitely many early
geodesic indices obstruct a clean three-handle.
-/

namespace WrittenOnTheWallII.GraphConjecture133HandleExistence

open SimpleGraph
open WrittenOnTheWallII.GraphConjecture133Cubic
open WrittenOnTheWallII.GraphConjecture133DeepHandle
open WrittenOnTheWallII.GraphConjecture133Regular
open WrittenOnTheWallII.GraphConjecture133Specialization

variable {V : Type*} [Fintype V] [DecidableEq V] [Nonempty V]

omit [Fintype V] [DecidableEq V] [Nonempty V] in
/-- A vertex reached by a two-edge handle at the head of a geodesic cannot
return to geodesic index four or later. -/
lemma not_adj_getVert_ge_four_of_twoStep {G : SimpleGraph V}
    {u v b c : V} (p : G.Walk u v) (hp : p.length = G.dist u v)
    (huc : G.Adj u c) (hcb : G.Adj c b) :
    ∀ k, 4 ≤ k → k ≤ p.length → ¬G.Adj b (p.getVert k) := by
  intro k hk hklen hbk
  let q : G.Walk u v :=
    (((huc.toWalk).append hcb.toWalk).append hbk.toWalk).append (p.drop k)
  have hq : G.dist u v ≤ q.length := G.dist_le q
  have hdrop : (p.drop k).length = p.length - k := by simp [Walk.drop_length]
  simp only [q, Walk.length_append, Walk.length_cons, Walk.length_nil,
    zero_add] at hq
  rw [hdrop, ← hp] at hq
  omega

omit [Fintype V] [DecidableEq V] [Nonempty V] in
/-- A vertex reached by a three-edge handle cannot return to geodesic index
five or later. -/
lemma not_adj_getVert_ge_five_of_threeStep {G : SimpleGraph V}
    {u v a b c : V} (p : G.Walk u v) (hp : p.length = G.dist u v)
    (huc : G.Adj u c) (hcb : G.Adj c b) (hba : G.Adj b a) :
    ∀ k, 5 ≤ k → k ≤ p.length → ¬G.Adj a (p.getVert k) := by
  intro k hk hklen hak
  let q : G.Walk u v :=
    ((((huc.toWalk).append hcb.toWalk).append hba.toWalk).append hak.toWalk).append
      (p.drop k)
  have hq : G.dist u v ≤ q.length := G.dist_le q
  have hdrop : (p.drop k).length = p.length - k := by simp [Walk.drop_length]
  simp only [q, Walk.length_append, Walk.length_cons, Walk.length_nil,
    zero_add] at hq
  rw [hdrop, ← hp] at hq
  omega

/-- A finite early-contact certificate.  The long-tail noncontact conditions
of `HasCleanRadiusThreeHandle` are absent: shortestness will supply them.
Only indices `1..3` for the distance-two vertex and `0..4` for the
distance-three vertex must be checked. -/
def HasEarlyEscapeRadiusThreeHandle (G : SimpleGraph V) : Prop :=
  ∃ (u v : V) (p : G.Walk u v) (a b c : V),
    p.length = G.dist u v ∧ p.length = G.radius.toNat ∧
    G.Adj c u ∧ c ∉ p.support ∧
      (∀ x ∈ p.support.tail, ¬G.Adj c x) ∧
    G.Adj b c ∧ b ∉ p.support ∧
      (∀ k, 1 ≤ k → k ≤ 3 → k ≤ p.length →
        ¬G.Adj b (p.getVert k)) ∧
    G.Adj a b ∧ a ≠ c ∧ a ∉ p.support ∧
      (∀ k, k ≤ 4 → k ≤ p.length → ¬G.Adj a (p.getVert k))

omit [Fintype V] [DecidableEq V] [Nonempty V] in
/-- The finite early-contact certificate produces the previously certified
clean three-handle. -/
lemma cleanThreeHandle_of_earlyEscape
    (G : SimpleGraph V) (htri : G.CliqueFree 3)
    (he : HasEarlyEscapeRadiusThreeHandle G) :
    HasCleanRadiusThreeHandle G := by
  obtain ⟨u, v, p, a, b, c, hpDist, hpRadius, hcu, hcfresh, hcclean,
    hbc, hbfresh, hbEarly, hab, hac, hafresh, haEarly⟩ := he
  refine ⟨u, v, p, a, b, c, hpDist, hpRadius, hcu, hcfresh, hcclean,
    hbc, ?_, ?_, hab, ?_, ?_⟩
  · simp only [List.mem_cons, not_or]
    exact ⟨hbc.ne, hbfresh⟩
  · intro x hx
    obtain ⟨k, hkx, hklen⟩ := Walk.mem_support_iff_exists_getVert.mp hx
    subst x
    by_cases hkzero : k = 0
    · subst k
      have hbu : b ≠ u := by
        intro heq
        subst b
        exact hbfresh p.start_mem_support
      simpa [Walk.getVert_zero] using
        G.isIndepSet_neighborSet_of_triangleFree htri c
          (by simpa [G.mem_neighborSet] using hbc.symm)
          (by simpa [G.mem_neighborSet] using hcu)
          hbu
    · by_cases hk : k ≤ 3
      · exact hbEarly k (by omega) hk hklen
      · exact not_adj_getVert_ge_four_of_twoStep
          p hpDist hcu.symm hbc.symm k (by omega) hklen
  · simp only [List.mem_cons, not_or]
    exact ⟨hab.ne, hac, hafresh⟩
  · intro x hx
    simp only [List.mem_cons] at hx
    rcases hx with rfl | hx
    · exact G.isIndepSet_neighborSet_of_triangleFree htri b
        (by simpa [G.mem_neighborSet] using hab.symm)
        (by simpa [G.mem_neighborSet] using hbc)
        hac
    · obtain ⟨k, hkx, hklen⟩ := Walk.mem_support_iff_exists_getVert.mp hx
      subst x
      by_cases hk : k ≤ 4
      · exact haEarly k hk hklen
      · exact not_adj_getVert_ge_five_of_threeStep
          p hpDist hcu.symm hbc.symm hab.symm k (by omega) hklen

/-- A connected triangle-free four-regular graph satisfying only the finite
early-contact certificate satisfies the exact source-shaped conjecture. -/
theorem degreeFourSpecialization_of_earlyEscape
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hconn : G.Connected) (hreg : G.IsRegularOfDegree 4)
    (htri : G.CliqueFree 3) (he : HasEarlyEscapeRadiusThreeHandle G) :
    SourceConclusion G := by
  apply degreeFourSpecialization_of_cleanThreeHandle G hconn hreg htri
  exact Or.inr (cleanThreeHandle_of_earlyEscape G htri he)

end WrittenOnTheWallII.GraphConjecture133HandleExistence
