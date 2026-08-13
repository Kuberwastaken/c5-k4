import GraphConjecture40CactusBlocks

/-!
# WOWII 40: petals sharing one allocated cut vertex

Raw cactus petals need not be vertex-disjoint: several blocks may share a cut
vertex.  If that attachment vertex can be trimmed from every petal while
retaining a three-vertex path, the trimmed supports are disjoint and the
v0.15 cactus-petal certificate applies.
-/

namespace WrittenOnTheWallII.GraphConjecture40SharedCutPetals

open SimpleGraph Finset

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

/-- Raw petals sharing only `center`, together with path realizations after
that center is allocated away. -/
structure SharedCutPetalCertificate (G : SimpleGraph V) (k : ℕ) where
  center : V
  rawPetals : Finset (Finset V)
  raw_card : rawPetals.card = k
  center_mem : ∀ s ∈ rawPetals, center ∈ s
  meet_only_center : ∀ s ∈ rawPetals, ∀ t ∈ rawPetals,
    s ≠ t → ∀ x, x ∈ s → x ∈ t → x = center
  trimmed_path : ∀ s ∈ rawPetals,
    ∃ (a z : V) (p : G.Walk a z),
      p.IsPath ∧ s.erase center = p.support.toFinset
  trimmed_three : ∀ s ∈ rawPetals, 3 ≤ (s.erase center).card
  bridge : Finset V
  bridge_path : ∃ (a z : V) (p : G.Walk a z),
    p.IsPath ∧ bridge = p.support.toFinset
  bridge_two : 2 ≤ bridge.card
  bridge_disjoint : Disjoint bridge
    (rawPetals.biUnion fun s ↦ s.erase center)

namespace SharedCutPetalCertificate

variable {G : SimpleGraph V} {k : ℕ}

def trimmedPetals (C : SharedCutPetalCertificate G k) :
    Finset (Finset V) :=
  C.rawPetals.image fun s ↦ s.erase C.center

omit [Fintype V] in
lemma erase_center_injective_on (C : SharedCutPetalCertificate G k) :
    Set.InjOn (fun s : Finset V ↦ s.erase C.center) C.rawPetals := by
  intro s hs t ht heq
  ext x
  by_cases hx : x = C.center
  · subst x
    exact iff_of_true (C.center_mem s hs) (C.center_mem t ht)
  · have hm := congrArg (fun q : Finset V ↦ x ∈ q) heq
    simpa [hx] using hm

omit [Fintype V] in
lemma trimmedPetals_card (C : SharedCutPetalCertificate G k) :
    C.trimmedPetals.card = k := by
  unfold trimmedPetals
  rw [Finset.card_image_iff.mpr C.erase_center_injective_on, C.raw_card]

omit [Fintype V] in
lemma trimmedPetals_isPathSupportFamily
    (C : SharedCutPetalCertificate G k) :
    GraphConjecture40PathFamily.IsPathSupportFamily G C.trimmedPetals := by
  refine ⟨?_, ?_⟩
  · intro S hS T hT hne
    simp only [trimmedPetals, mem_image] at hS hT
    obtain ⟨s, hs, rfl⟩ := hS
    obtain ⟨t, ht, rfl⟩ := hT
    have hst : s ≠ t := by
      intro h
      subst t
      exact hne rfl
    rw [Finset.disjoint_left]
    intro x hxs hxt
    have hxne : x ≠ C.center := (mem_erase.mp hxs).1
    have hxcenter := C.meet_only_center s hs t ht hst x
      (mem_erase.mp hxs).2 (mem_erase.mp hxt).2
    exact hxne hxcenter
  · intro S hS
    simp only [trimmedPetals, mem_image] at hS
    obtain ⟨s, hs, rfl⟩ := hS
    exact C.trimmed_path s hs

omit [Fintype V] in
lemma trimmedPetals_three (C : SharedCutPetalCertificate G k) :
    ∀ S ∈ C.trimmedPetals, 3 ≤ S.card := by
  intro S hS
  simp only [trimmedPetals, mem_image] at hS
  obtain ⟨s, hs, rfl⟩ := hS
  exact C.trimmed_three s hs

omit [Fintype V] in
lemma covered_trimmedPetals (C : SharedCutPetalCertificate G k) :
    GraphConjecture40PathFamily.coveredVertices C.trimmedPetals =
      C.rawPetals.biUnion (fun s ↦ s.erase C.center) := by
  ext x
  simp [GraphConjecture40PathFamily.coveredVertices, trimmedPetals]

omit [Fintype V] in
/-- Trimming the shared cut vertex produces the disjoint v0.15 certificate. -/
def toCactusPetalCertificate (C : SharedCutPetalCertificate G k) :
    GraphConjecture40CactusBlocks.CactusPetalCertificate G k where
  petals := C.trimmedPetals
  bridge := C.bridge
  petals_family := C.trimmedPetals_isPathSupportFamily
  petals_card := C.trimmedPetals_card
  petals_three := C.trimmedPetals_three
  bridge_path := C.bridge_path
  bridge_two := C.bridge_two
  bridge_disjoint := by
    rw [C.covered_trimmedPetals]
    exact C.bridge_disjoint

end SharedCutPetalCertificate

/-- Shared-cut-petal structural class for WOWII 40. -/
theorem conjecture40_of_bipartite_of_sharedCutPetalCertificate
    (G : SimpleGraph V) (hG : G.IsBipartite)
    {k : ℕ}
    (htau : GraphConjecture40Deficiency.feedbackDeletion G = k)
    (C : SharedCutPetalCertificate G k) :
    ⌈(((pathCoverNumber G : ℝ) + b G + 1) / 2)⌉ ≤
      G.largestInducedForestSize := by
  exact GraphConjecture40CactusBlocks.conjecture40_of_bipartite_of_cactusPetalCertificate
    G hG htau C.toCactusPetalCertificate

end WrittenOnTheWallII.GraphConjecture40SharedCutPetals
