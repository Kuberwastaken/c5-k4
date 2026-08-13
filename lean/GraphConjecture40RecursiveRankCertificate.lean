import GraphConjecture40SubtypePathTransport

/-!
# WOWII 40: recursive mixed-branch rank certificates

A recursive certificate tree combines exclude nodes (one child plus a leaf
path) and include nodes (two compatible children). Its soundness theorem is
the common induction principle behind both block-tree branches.
-/

namespace WrittenOnTheWallII.GraphConjecture40RecursiveRankCertificate

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture40OneVertexSeparation
open WrittenOnTheWallII.GraphConjecture40BlockTreeRecurrence
open WrittenOnTheWallII.GraphConjecture40IncludeBranchRecurrence
open WrittenOnTheWallII.GraphConjecture40IncludeRankComposition
open WrittenOnTheWallII.GraphConjecture40SubtypePathTransport

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

/-- Recursive proof tree for a path-family rank target. `exclude` adds one
feedback unit and a three-vertex leaf path; `include` adds two child
coordinates and joins their allocated families. -/
inductive RankTree (G : SimpleGraph V) :
    ℕ → Finset (Finset V) → Type u
  | atom {k : ℕ} {P : Finset (Finset V)}
      (hP : GraphConjecture40PathFamily.IsPathSupportFamily G P)
      (hrank : P.card + (2 * k + 1) ≤
        (GraphConjecture40PathFamily.coveredVertices P).card) :
      RankTree G k P
  | exclude {k : ℕ} {P : Finset (Finset V)}
      (child : RankTree G k P)
      (L : GraphConjecture40LeafBlockStep.LeafBlockStep G P) :
      RankTree G (k + 1) (insert L.support P)
  | join {kL kR : ℕ} {P Q : Finset (Finset V)}
      (left : RankTree G kL P) (right : RankTree G kR Q)
      (J : PathFamilyJoin G P Q) :
      RankTree G (kL + kR) (P ∪ Q)

namespace RankTree

omit [Fintype V] in
/-- Soundness of an arbitrary mixed exclude/include rank tree. -/
theorem sound {G : SimpleGraph V} {k : ℕ} {P : Finset (Finset V)}
    (T : RankTree G k P) :
    GraphConjecture40PathFamily.IsPathSupportFamily G P ∧
      P.card + (2 * k + 1) ≤
        (GraphConjecture40PathFamily.coveredVertices P).card := by
  induction T with
  | atom hP hrank => exact ⟨hP, hrank⟩
  | exclude child L ih =>
      exact ⟨L.insert_isPathSupportFamily ih.1, L.rank_step ih.1 ih.2⟩
  | join left right J ihL ihR =>
      exact ⟨J.union_isPathSupportFamily ihL.1 ihR.1,
        J.union_rank ihL.2 ihR.2⟩

/-- Any sound rank tree at the exact feedback coordinate proves WOWII 40 for
a bipartite graph. -/
theorem conjecture40_of_bipartite
    {G : SimpleGraph V} {k : ℕ} {P : Finset (Finset V)}
    (T : RankTree G k P) (hG : G.IsBipartite)
    (htau : GraphConjecture40Deficiency.feedbackDeletion G = k) :
    ⌈(((pathCoverNumber G : ℝ) + b G + 1) / 2)⌉ ≤
      G.largestInducedForestSize := by
  exact GraphConjecture40PathFamily.conjecture40_of_bipartite_of_pathFamily_rank
    G hG htau P T.sound.1 T.sound.2

end RankTree

/-- Canonical lift of a rank tree from an induced finset side into the ambient
graph. -/
def liftFinsetTree (G : SimpleGraph V) (A : Finset V)
    {k : ℕ} {P : Finset (Finset ↥(↑A : Set V))}
    (T : RankTree (G.induce (↑A : Set V)) k P) :
    RankTree G k (liftFamily A P) := by
  exact .atom (liftFamily_isPathSupportFamily A P T.sound.1)
    (liftFamily_rank A P T.sound.2)

/-- State-aware exclude node. The child rank tree is already transported into
the parent ambient graph; the separator recurrence identifies its coordinate
with the cut-deleted remainder and the leaf constructor pays the next unit. -/
theorem conjecture40_of_bipartite_of_excludeNode
    {G : SimpleGraph V} (D : OneVertexSeparation G) (hG : G.IsBipartite)
    (hdom : includeStateSum D ≤ excludeStateSum D)
    {k : ℕ}
    (hrem : GraphConjecture40Deficiency.feedbackDeletion
      (GraphConjecture40FeedbackRecursion.deleteVertex G D.cut) = k)
    {P : Finset (Finset V)} (child : RankTree G k P)
    (L : GraphConjecture40LeafBlockStep.LeafBlockStep G P) :
    ⌈(((pathCoverNumber G : ℝ) + b G + 1) / 2)⌉ ≤
      G.largestInducedForestSize := by
  have htau :=
    WrittenOnTheWallII.GraphConjecture40RecursiveLeafStep.feedbackDeletion_eq_succ_of_exclude_dominates
      D hdom
  have htau' : GraphConjecture40Deficiency.feedbackDeletion G = k + 1 := by
    omega
  exact (RankTree.exclude child L).conjecture40_of_bipartite hG htau'

/-- Include-node constructor from two genuinely recursive subtype children,
with the shared cut allocated away from the right child. -/
def includeSubtype
    {G : SimpleGraph V} (D : OneVertexSeparation G)
    {kL kR : ℕ}
    {P : Finset (Finset ↥(↑D.left : Set V))}
    {Q : Finset (Finset ↥(↑D.right : Set V))}
    (left : RankTree (G.induce (↑D.left : Set V)) kL P)
    (right : RankTree (G.induce (↑D.right : Set V)) kR Q)
    (hcutQ : (⟨D.cut, D.cut_mem_right⟩ : ↥(↑D.right : Set V)) ∉
      GraphConjecture40PathFamily.coveredVertices Q) :
    RankTree G (kL + kR)
      (liftFamily D.left P ∪ liftFamily D.right Q) := by
  exact .join (liftFinsetTree G D.left left)
    (liftFinsetTree G D.right right)
    (liftedFamilies_join_of_right_avoids_cut D P Q left.sound.1 hcutQ)

/-- State-aware include node: the recursive child indices are identified with
the two side include-deficiencies, so the resulting tree index is exactly the
parent feedback coordinate. -/
theorem includeSubtype_feedback_eq
    {G : SimpleGraph V} (D : OneVertexSeparation G)
    (hdom : excludeStateSum D ≤ includeStateSum D)
    {kL kR : ℕ}
    (hL : includeDeficiency (G.induce (↑D.left : Set V))
      ⟨D.cut, D.cut_mem_left⟩ = kL)
    (hR : includeDeficiency (G.induce (↑D.right : Set V))
      ⟨D.cut, D.cut_mem_right⟩ = kR) :
    GraphConjecture40Deficiency.feedbackDeletion G = kL + kR :=
  feedbackDeletion_eq_add_of_include_dominates D hdom hL hR

/-- End-to-end recursive include node. -/
theorem conjecture40_of_bipartite_of_includeSubtype
    {G : SimpleGraph V} (D : OneVertexSeparation G) (hG : G.IsBipartite)
    (hdom : excludeStateSum D ≤ includeStateSum D)
    {kL kR : ℕ}
    (hL : includeDeficiency (G.induce (↑D.left : Set V))
      ⟨D.cut, D.cut_mem_left⟩ = kL)
    (hR : includeDeficiency (G.induce (↑D.right : Set V))
      ⟨D.cut, D.cut_mem_right⟩ = kR)
    {P : Finset (Finset ↥(↑D.left : Set V))}
    {Q : Finset (Finset ↥(↑D.right : Set V))}
    (left : RankTree (G.induce (↑D.left : Set V)) kL P)
    (right : RankTree (G.induce (↑D.right : Set V)) kR Q)
    (hcutQ : (⟨D.cut, D.cut_mem_right⟩ : ↥(↑D.right : Set V)) ∉
      GraphConjecture40PathFamily.coveredVertices Q) :
    ⌈(((pathCoverNumber G : ℝ) + b G + 1) / 2)⌉ ≤
      G.largestInducedForestSize := by
  exact (includeSubtype D left right hcutQ).conjecture40_of_bipartite hG
    (includeSubtype_feedback_eq D hdom hL hR)

end WrittenOnTheWallII.GraphConjecture40RecursiveRankCertificate
