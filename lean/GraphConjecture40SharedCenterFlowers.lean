import GraphConjecture40SharedCutPetals

/-!
# WOWII 40: shared-center flowers

For feedback coordinate one, one even petal supplies a three-vertex path
after the shared center is trimmed, and a second petal supplies a center edge
disjoint from that path.  This file packages those concrete witnesses and
constructs the v0.16 shared-cut certificate.
-/

namespace WrittenOnTheWallII.GraphConjecture40SharedCenterFlowers

open SimpleGraph Finset

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

/-- The exact local data harvested from two petals sharing a center. The
first petal contributes `petalPath`; an edge from the center into a second
petal contributes the extra rank unit. -/
structure SharedCenterFlowerData (G : SimpleGraph V) where
  center : V
  petalStart : V
  petalEnd : V
  petalPath : G.Walk petalStart petalEnd
  petalPath_isPath : petalPath.IsPath
  petalPath_three : 3 ≤ petalPath.support.toFinset.card
  center_not_petalPath : center ∉ petalPath.support.toFinset
  secondVertex : V
  secondEdge : G.Adj center secondVertex
  secondVertex_not_petalPath : secondVertex ∉ petalPath.support.toFinset

namespace SharedCenterFlowerData

variable {G : SimpleGraph V}

def rawPetal (F : SharedCenterFlowerData G) : Finset V :=
  insert F.center F.petalPath.support.toFinset

def rawPetals (F : SharedCenterFlowerData G) : Finset (Finset V) :=
  {F.rawPetal}

def bridge (F : SharedCenterFlowerData G) : Finset V :=
  {F.center, F.secondVertex}

omit [Fintype V] in
lemma erase_center_rawPetal (F : SharedCenterFlowerData G) :
    F.rawPetal.erase F.center = F.petalPath.support.toFinset := by
  simp [rawPetal, F.center_not_petalPath]

omit [Fintype V] in
lemma bridge_disjoint_petalPath (F : SharedCenterFlowerData G) :
    Disjoint F.bridge F.petalPath.support.toFinset := by
  rw [Finset.disjoint_left]
  intro x hx hxp
  simp only [bridge, mem_insert, mem_singleton] at hx
  rcases hx with rfl | rfl
  · exact F.center_not_petalPath hxp
  · exact F.secondVertex_not_petalPath hxp

omit [Fintype V] in
/-- Two shared-center petals instantiate the allocated shared-cut
certificate at feedback coordinate one. -/
def toSharedCutPetalCertificate (F : SharedCenterFlowerData G) :
    GraphConjecture40SharedCutPetals.SharedCutPetalCertificate G 1 where
  center := F.center
  rawPetals := F.rawPetals
  raw_card := by simp [rawPetals]
  center_mem := by
    intro s hs
    simp only [rawPetals, mem_singleton] at hs
    subst s
    exact mem_insert_self _ _
  meet_only_center := by
    intro s hs t ht hne
    simp only [rawPetals, mem_singleton] at hs ht
    subst s
    subst t
    exact (hne rfl).elim
  trimmed_path := by
    intro s hs
    simp only [rawPetals, mem_singleton] at hs
    subst s
    exact ⟨F.petalStart, F.petalEnd, F.petalPath,
      F.petalPath_isPath, F.erase_center_rawPetal⟩
  trimmed_three := by
    intro s hs
    simp only [rawPetals, mem_singleton] at hs
    subst s
    rw [F.erase_center_rawPetal]
    exact F.petalPath_three
  bridge := F.bridge
  bridge_path := ⟨F.center, F.secondVertex, F.secondEdge.toWalk,
    Walk.IsPath.of_adj F.secondEdge, by simp [bridge]⟩
  bridge_two := by simp [bridge, F.secondEdge.ne]
  bridge_disjoint := by
    simpa [rawPetals, F.erase_center_rawPetal] using
      F.bridge_disjoint_petalPath

end SharedCenterFlowerData

/-- Exact WOWII 40 theorem for the abstract shared-center flower class. -/
theorem conjecture40_of_sharedCenterFlower
    (G : SimpleGraph V) (hG : G.IsBipartite)
    (htau : GraphConjecture40Deficiency.feedbackDeletion G = 1)
    (F : SharedCenterFlowerData G) :
    ⌈(((pathCoverNumber G : ℝ) + b G + 1) / 2)⌉ ≤
      G.largestInducedForestSize := by
  exact GraphConjecture40SharedCutPetals.conjecture40_of_bipartite_of_sharedCutPetalCertificate
    G hG htau F.toSharedCutPetalCertificate

end WrittenOnTheWallII.GraphConjecture40SharedCenterFlowers
