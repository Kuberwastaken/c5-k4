import GraphConjecture59CoverDegree

/-!
# WOWII 59: the unused-pool premise

Four named outside rows and a six-vertex core consume at most ten vertices.
This file identifies the resulting order-dependent lower bound on the unused
candidate pool and proves that the established local density hypotheses alone
do not force that pool to be nonempty.
-/

namespace WrittenOnTheWallII.GraphConjecture59UnusedPool

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture59CoreExchange
open WrittenOnTheWallII.GraphConjecture59DenseAttachments
open WrittenOnTheWallII.GraphConjecture59CoverDegree

universe u
variable {V : Type u} [Fintype V] [DecidableEq V]

/-- Vertices not already consumed by a six-core and four named outside rows. -/
def unusedPool (S : Finset V) (w x y z : V) : Finset V :=
  univ \ (S ∪ {w, x, y, z})

omit [Fintype V] in
/-- Four named vertices occupy at most four places, even if some names repeat. -/
theorem card_four_vertices_le (w x y z : V) :
    ({w, x, y, z} : Finset V).card ≤ 4 := by
  have hw := card_insert_le w ({x, y, z} : Finset V)
  have hx := card_insert_le x ({y, z} : Finset V)
  have hy := card_insert_le y ({z} : Finset V)
  simp only [card_singleton] at hy
  omega

/-- A six-core and four named rows leave at least `|V|-10` unused vertices.
No attachment-density hypothesis is needed: density controls edges, whereas
this lower bound is purely an order budget. -/
theorem card_sub_ten_le_unusedPool
    (S : Finset V) (w x y z : V) (hSsix : S.card = 6) :
    Fintype.card V - 10 ≤ (unusedPool S w x y z).card := by
  have hrows := card_four_vertices_le w x y z
  have hused : (S ∪ {w, x, y, z}).card ≤ 10 := by
    have hunion := card_union_le S ({w, x, y, z} : Finset V)
    omega
  rw [unusedPool, card_sdiff_of_subset (subset_univ _), card_univ]
  omega

/-- If the unused pool is covered by three neighborhoods, graph order beyond
`10+3d` forces one of the three target degrees above `d`. -/
theorem one_degree_gt_of_unused_pool_cover
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (S : Finset V) (w x y z : V) (d : ℕ)
    (hSsix : S.card = 6)
    (hcover : ∀ p ∈ unusedPool S w x y z,
      G.Adj p x ∨ G.Adj p y ∨ G.Adj p z)
    (horder : 10 + 3 * d < Fintype.card V) :
    d < G.degree x ∨ d < G.degree y ∨ d < G.degree z := by
  apply one_degree_gt_of_three_cover G (unusedPool S w x y z) x y z d hcover
  have hlower := card_sub_ten_le_unusedPool S w x y z hSsix
  omega

namespace PoolCountermodel

/-- A ten-vertex model: a properly colored `3+3` core, joined completely to
four outside vertices, which themselves form a clique. -/
def graph : SimpleGraph (Fin 10) :=
  SimpleGraph.fromRel fun u v ↦
    (u.val < 3 ∧ 3 ≤ v.val ∧ v.val < 6) ∨
    (u.val < 6 ∧ 6 ≤ v.val) ∨
    (6 ≤ u.val ∧ 6 ≤ v.val)

instance : DecidableRel graph.Adj := by
  unfold graph
  infer_instance

def core : Finset (Fin 10) :=
  univ.filter fun v ↦ v.val < 6

def color (v : Fin 10) : Fin 2 :=
  if v.val < 3 then 0 else 1

/-- The countermodel satisfies the local six-core, proper-coloring, and four
dense-row hypotheses used by the row classification, yet its natural unused
pool is empty. -/
theorem dense_rows_with_empty_unused_pool :
    core.card = 6 ∧
    (∀ u ∈ core, ∀ v ∈ core, graph.Adj u v → color u ≠ color v) ∧
    (∀ k : Fin 2, (colorClass core color k).card = 3) ∧
    (∀ r ∈ ({6, 7, 8, 9} : Finset (Fin 10)), ∀ k : Fin 2,
      2 ≤ (colorAttachments graph core r color k).card) ∧
    unusedPool core 6 7 8 9 = ∅ := by
  decide

end PoolCountermodel

end WrittenOnTheWallII.GraphConjecture59UnusedPool
