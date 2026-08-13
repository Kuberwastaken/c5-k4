import GraphConjecture40RecursiveRankCertificate

/-!
# WOWII 40: concrete cactus rank-tree extraction

Mathlib currently has no finite cactus/block-tree decomposition predicate or
leaf-block existence theorem. This file performs the first honest structural
extraction available from the repository's concrete cactus witnesses: petal,
shared-cut, and shared-center flower data become `RankTree` certificates.
-/

namespace WrittenOnTheWallII.GraphConjecture40CactusRankExtraction

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture40RecursiveRankCertificate

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]
variable {G : SimpleGraph V}

/-- A concrete cactus petal certificate is an atom of the general recursive
rank-tree language. -/
def cactusPetalToRankTree {k : ℕ}
    (C : GraphConjecture40CactusBlocks.CactusPetalCertificate G k) :
    RankTree G k (insert C.bridge C.petals) :=
  .atom C.insert_bridge_isPathSupportFamily C.insert_bridge_rank

/-- Allocated shared-cut petals extract to a rank tree after trimming their
common center. -/
def sharedCutPetalToRankTree {k : ℕ}
    (C : GraphConjecture40SharedCutPetals.SharedCutPetalCertificate G k) :
    RankTree G k
      (insert C.bridge C.toCactusPetalCertificate.petals) :=
  cactusPetalToRankTree C.toCactusPetalCertificate

omit [Fintype V] in
/-- The extracted shared-cut tree uses exactly the trimmed petal family. -/
theorem sharedCutPetalToRankTree_family_eq {k : ℕ}
    (C : GraphConjecture40SharedCutPetals.SharedCutPetalCertificate G k) :
    C.toCactusPetalCertificate.petals = C.trimmedPetals := rfl

/-- A two-petal shared-center flower is a concrete rank-tree atom at feedback
coordinate one. -/
def sharedCenterFlowerToRankTree
    (F : GraphConjecture40SharedCenterFlowers.SharedCenterFlowerData G) :
    RankTree G 1
      (insert F.toSharedCutPetalCertificate.bridge
        F.toSharedCutPetalCertificate.toCactusPetalCertificate.petals) :=
  sharedCutPetalToRankTree F.toSharedCutPetalCertificate

/-- A single graph edge supplies the acyclic (`k=0`) base rank atom. -/
def edgeBaseRankTree {u v : V} (h : G.Adj u v) :
    RankTree G 0 {{u, v}} := by
  apply RankTree.atom
  · constructor
    · intro s hs t ht hne
      simp only [mem_singleton] at hs ht
      subst s
      subst t
      exact (hne rfl).elim
    · intro s hs
      simp only [mem_singleton] at hs
      subst s
      exact ⟨u, v, h.toWalk, Walk.IsPath.of_adj h, by simp⟩
  · have huv : u ≠ v := h.ne
    simp [GraphConjecture40PathFamily.coveredVertices, huv]

/-- Concrete acyclic base extraction: an acyclic graph with an edge has
feedback coordinate zero and an explicit rank tree. -/
theorem conjecture40_of_bipartite_acyclic_edge
    (hG : G.IsBipartite) (hacyc : G.IsAcyclic)
    {u v : V} (h : G.Adj u v) :
    ⌈(((pathCoverNumber G : ℝ) + b G + 1) / 2)⌉ ≤
      G.largestInducedForestSize := by
  have htau : GraphConjecture40Deficiency.feedbackDeletion G = 0 := by
    unfold GraphConjecture40Deficiency.feedbackDeletion
    rw [GraphConjecture40Deficiency.largestInducedForestSize_eq_card_of_isAcyclic
      G hacyc]
    omega
  exact (edgeBaseRankTree h).conjecture40_of_bipartite hG htau

/-- A shared-center flower together with the standard apex-forest structural
hypotheses needs no externally supplied feedback-coordinate equality: the
graph structure proves `tau=1`, while the flower extracts the matching rank
tree. -/
theorem conjecture40_of_bipartite_sharedCenterFlower_apexForest
    (hG : G.IsBipartite)
    (F : GraphConjecture40SharedCenterFlowers.SharedCenterFlowerData G)
    (hdelete :
      (GraphConjecture40FeedbackRecursion.deleteVertex G F.center).IsAcyclic)
    (hcyclic : ¬G.IsAcyclic) :
    ⌈(((pathCoverNumber G : ℝ) + b G + 1) / 2)⌉ ≤
      G.largestInducedForestSize := by
  have htau :=
    GraphConjecture40CactusFeedbackUnit.feedbackDeletion_eq_one_of_apex_forest
      G F.center hdelete hcyclic
  exact (sharedCenterFlowerToRankTree F).conjecture40_of_bipartite hG htau

/-- General concrete cactus-petal extraction theorem in the recursive-tree
interface. -/
theorem conjecture40_of_bipartite_cactusPetalRankTree
    (hG : G.IsBipartite) {k : ℕ}
    (htau : GraphConjecture40Deficiency.feedbackDeletion G = k)
    (C : GraphConjecture40CactusBlocks.CactusPetalCertificate G k) :
    ⌈(((pathCoverNumber G : ℝ) + b G + 1) / 2)⌉ ≤
      G.largestInducedForestSize :=
  (cactusPetalToRankTree C).conjecture40_of_bipartite hG htau

end WrittenOnTheWallII.GraphConjecture40CactusRankExtraction
