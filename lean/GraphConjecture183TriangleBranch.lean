import GraphConjecture183CycleComplementPath

/-!
# WOWII 183: the separate triangle branch

The triangle does not need a weaker budget.  Relative to any prescribed root,
delete the other two vertices.  The retained singleton is connected,
bipartite, and dominates both deleted vertices; after adding the mandatory
attachment its order is two, exactly the order of a maximum induced-bipartite
witness in `C3`.
-/

namespace WrittenOnTheWallII.GraphConjecture183TriangleBranch

open SimpleGraph
open WrittenOnTheWallII.GraphConjecture183TwoDeletionTrunk

/-- The two vertices following `r` cyclically are exactly the vertices other
than `r` in `Fin 3`. -/
def trianglePair (r : Fin 3) : Fin 3 × Fin 3 := (r + 1, r + 2)

theorem trianglePair_avoids_root (r : Fin 3) :
    r ≠ (trianglePair r).1 ∧ r ≠ (trianglePair r).2 := by
  fin_cases r <;> decide

/-- Deleting the two non-root vertices of `C3 = K3` is a good two-deletion:
the retained root singleton is the connected bipartite dominating set. -/
theorem trianglePair_isGoodTwoDeletion (r : Fin 3) :
    IsGoodTwoDeletion (cycleGraph 3) (trianglePair r).1 (trianglePair r).2 := by
  fin_cases r
  · simp [IsGoodTwoDeletion, trianglePair, cycleGraph_three_eq_top,
      SimpleGraph.connected_iff]
    refine ⟨⟨0, by decide⟩, ?_, ⟨0, by decide⟩, ⟨0, by decide⟩⟩
    refine ⟨Coloring.mk (fun _ => 0) ?_⟩
    intro a b hab
    exfalso
    apply hab.ne
    apply Subtype.ext
    · obtain ⟨a, ha⟩ := a
      obtain ⟨b, hb⟩ := b
      simp only [Set.mem_compl_iff, Set.mem_insert_iff, Set.mem_singleton_iff,
        not_or] at ha hb
      fin_cases a <;> fin_cases b <;> simp_all
  · simp [IsGoodTwoDeletion, trianglePair, cycleGraph_three_eq_top,
      SimpleGraph.connected_iff]
    refine ⟨⟨1, by decide⟩, ?_, ⟨1, by decide⟩, ⟨1, by decide⟩⟩
    refine ⟨Coloring.mk (fun _ => 0) ?_⟩
    intro a b hab
    exfalso
    apply hab.ne
    apply Subtype.ext
    · obtain ⟨a, ha⟩ := a
      obtain ⟨b, hb⟩ := b
      simp only [Set.mem_compl_iff, Set.mem_insert_iff, Set.mem_singleton_iff,
        not_or] at ha hb
      fin_cases a <;> fin_cases b <;> simp_all
  · simp [IsGoodTwoDeletion, trianglePair, cycleGraph_three_eq_top,
      SimpleGraph.connected_iff]
    refine ⟨⟨2, by decide⟩, ?_, ⟨2, by decide⟩, ⟨2, by decide⟩⟩
    refine ⟨Coloring.mk (fun _ => 0) ?_⟩
    intro a b hab
    exfalso
    apply hab.ne
    apply Subtype.ext
    · obtain ⟨a, ha⟩ := a
      obtain ⟨b, hb⟩ := b
      simp only [Set.mem_compl_iff, Set.mem_insert_iff, Set.mem_singleton_iff,
        not_or] at ha hb
      fin_cases a <;> fin_cases b <;> simp_all

/-- Exact local arithmetic for the triangle: the one-vertex trunk plus its
attachment costs two vertices, equal to the two-vertex bipartite witness. -/
theorem triangle_exact_local_budget : 1 + 1 ≤ 2 := by
  omega

/-- The abstract two-deletion budget specializes without loss at component
order three. -/
theorem triangle_twoDeletion_budget : 1 + 1 ≤ 2 := by
  exact twoDeletion_budget 1 2 3 (by omega) (by omega)

end WrittenOnTheWallII.GraphConjecture183TriangleBranch
