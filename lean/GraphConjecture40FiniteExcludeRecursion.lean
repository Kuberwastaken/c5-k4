import GraphConjecture40TwoLevelRecursion

/-!
# WOWII 40: arbitrary finite exclude recursion

The depth-two construction is generalized to an explicitly certified finite
chain. A dependent exclude trace follows the changing subtype graph after
each cut deletion; a leaf-step chain follows the changing path family in the
original ambient graph.
-/

namespace WrittenOnTheWallII.GraphConjecture40FiniteExcludeRecursion

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture40OneVertexSeparation
open WrittenOnTheWallII.GraphConjecture40BlockTreeRecurrence

universe u

/-- A finite graph packaged with the instances required by the state API. -/
structure FiniteGraph where
  Vertex : Type u
  fintypeVertex : Fintype Vertex
  decidableEqVertex : DecidableEq Vertex
  graph : SimpleGraph Vertex

namespace FiniteGraph

instance (X : FiniteGraph) : Fintype X.Vertex := X.fintypeVertex
instance (X : FiniteGraph) : DecidableEq X.Vertex := X.decidableEqVertex

def of {W : Type u} [Fintype W] [DecidableEq W]
    (H : SimpleGraph W) : FiniteGraph :=
  ⟨W, inferInstance, inferInstance, H⟩

def delete (X : FiniteGraph) (v : X.Vertex) : FiniteGraph :=
  of (GraphConjecture40FeedbackRecursion.deleteVertex X.graph v)

end FiniteGraph

/-- An explicit chain of exclude-dominant one-vertex separations. The graph
type changes at each constructor to the subtype obtained by deleting the
chosen cut. -/
inductive ExcludeTrace : (X : FiniteGraph) → ℕ → Type (u + 1)
  | nil (X : FiniteGraph) : ExcludeTrace X 0
  | cons {X : FiniteGraph}
      (D : OneVertexSeparation X.graph)
      (hdom : includeStateSum D ≤ excludeStateSum D)
      {n : ℕ}
      (tail : ExcludeTrace (X.delete D.cut) n) :
      ExcludeTrace X (n + 1)

namespace ExcludeTrace

/-- Feedback coordinate at the terminal graph of an exclude trace. -/
noncomputable def terminalFeedback
    {X : FiniteGraph} {n : ℕ} (T : ExcludeTrace X n) : ℕ :=
  match T with
  | .nil X => GraphConjecture40Deficiency.feedbackDeletion X.graph
  | .cons _ _ tail => terminalFeedback tail

/-- Every certified exclude step contributes exactly one feedback unit. -/
theorem feedbackDeletion_eq_terminalFeedback_add_depth
    {X : FiniteGraph} {n : ℕ} (T : ExcludeTrace X n) :
    GraphConjecture40Deficiency.feedbackDeletion X.graph =
      T.terminalFeedback + n := by
  induction T with
  | nil X => simp [terminalFeedback]
  | @cons X D hdom n tail ih =>
      have hstep :=
        WrittenOnTheWallII.GraphConjecture40RecursiveLeafStep.feedbackDeletion_eq_succ_of_exclude_dominates
          D hdom
      change GraphConjecture40Deficiency.feedbackDeletion
        (GraphConjecture40FeedbackRecursion.deleteVertex X.graph D.cut) =
          tail.terminalFeedback + n at ih
      simp only [terminalFeedback]
      omega

end ExcludeTrace

section LeafSteps

variable {V : Type u} [Fintype V] [DecidableEq V]
variable (G : SimpleGraph V)

/-- Explicit sequence of allocated leaf paths. Its index is the number of
rank-raising insertions, and its family index records the current family. -/
inductive LeafStepChain : Finset (Finset V) → ℕ → Type u
  | nil (P : Finset (Finset V)) : LeafStepChain P 0
  | cons {P : Finset (Finset V)}
      (L : GraphConjecture40LeafBlockStep.LeafBlockStep G P)
      {n : ℕ}
      (tail : LeafStepChain (insert L.support P) n) :
      LeafStepChain P (n + 1)

namespace LeafStepChain

/-- Path family obtained after all certified leaf insertions. -/
def terminalFamily :
    {P : Finset (Finset V)} → {n : ℕ} → LeafStepChain G P n →
      Finset (Finset V)
  | _, _, .nil P => P
  | _, _, .cons _ tail => terminalFamily tail

omit [Fintype V] in
/-- Iterating `LeafBlockStep.rank_step` raises the required rank by exactly
two per certified leaf. -/
theorem terminal_rank
    {P : Finset (Finset V)} {n k : ℕ}
    (C : LeafStepChain G P n)
    (hP : GraphConjecture40PathFamily.IsPathSupportFamily G P)
    (hrank : P.card + (2 * k + 1) ≤
      (GraphConjecture40PathFamily.coveredVertices P).card) :
    C.terminalFamily.card + (2 * (k + n) + 1) ≤
      (GraphConjecture40PathFamily.coveredVertices C.terminalFamily).card := by
  induction C generalizing k with
  | nil P => simpa using hrank
  | @cons P L n tail ih =>
      have hPnext := L.insert_isPathSupportFamily hP
      have hrankNext := L.rank_step hP hrank
      have htail := ih hPnext hrankNext
      simp only [terminalFamily]
      omega

omit [Fintype V] in
/-- The terminal family remains a family of disjoint path supports. -/
theorem terminal_isPathSupportFamily
    {P : Finset (Finset V)} {n : ℕ}
    (C : LeafStepChain G P n)
    (hP : GraphConjecture40PathFamily.IsPathSupportFamily G P) :
    GraphConjecture40PathFamily.IsPathSupportFamily G C.terminalFamily := by
  induction C with
  | nil P => exact hP
  | @cons P L n tail ih =>
      exact ih (L.insert_isPathSupportFamily hP)

end LeafStepChain

end LeafSteps

section Coupled

variable {V : Type u} [Fintype V] [DecidableEq V]
variable {G : SimpleGraph V}

/-- Arbitrary-depth coupled recurrence: an exclude trace of depth `n` and a
leaf-step chain of the same depth prove both `tau=k+n` and the matching
`2*(k+n)+1` path-family rank target. -/
theorem finite_exclude_trace_feedback_and_rank
    {n k : ℕ}
    (T : ExcludeTrace (FiniteGraph.of G) n)
    (hbase : T.terminalFeedback = k)
    (P : Finset (Finset V))
    (hP : GraphConjecture40PathFamily.IsPathSupportFamily G P)
    (hrank : P.card + (2 * k + 1) ≤
      (GraphConjecture40PathFamily.coveredVertices P).card)
    (C : LeafStepChain G P n) :
    GraphConjecture40Deficiency.feedbackDeletion G = k + n ∧
      C.terminalFamily.card + (2 * (k + n) + 1) ≤
        (GraphConjecture40PathFamily.coveredVertices C.terminalFamily).card := by
  constructor
  · have ht := T.feedbackDeletion_eq_terminalFeedback_add_depth
    change GraphConjecture40Deficiency.feedbackDeletion G =
      T.terminalFeedback + n at ht
    omega
  · exact LeafStepChain.terminal_rank G C hP hrank

/-- End-to-end arbitrary finite exclude-chain theorem for bipartite graphs. -/
theorem conjecture40_of_bipartite_of_finite_exclude_trace
    {n k : ℕ}
    (T : ExcludeTrace (FiniteGraph.of G) n)
    (hbase : T.terminalFeedback = k)
    (hG : G.IsBipartite)
    (P : Finset (Finset V))
    (hP : GraphConjecture40PathFamily.IsPathSupportFamily G P)
    (hrank : P.card + (2 * k + 1) ≤
      (GraphConjecture40PathFamily.coveredVertices P).card)
    (C : LeafStepChain G P n) :
    ⌈(((pathCoverNumber G : ℝ) + b G + 1) / 2)⌉ ≤
      G.largestInducedForestSize := by
  have hpair := finite_exclude_trace_feedback_and_rank
    T hbase P hP hrank C
  exact GraphConjecture40PathFamily.conjecture40_of_bipartite_of_pathFamily_rank
    G hG hpair.1 (LeafStepChain.terminalFamily G C)
      (LeafStepChain.terminal_isPathSupportFamily G C hP) hpair.2

end Coupled

end WrittenOnTheWallII.GraphConjecture40FiniteExcludeRecursion
