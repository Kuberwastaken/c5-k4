import GraphConjecture133CrossRowContacts

/-!
# WOWII 133: metric restrictions on cross-row contacts

Two sibling candidates joining geodesic indices `i<j` create a four-edge
detour between those indices.  Shortestness therefore forces `j-i<=4`.
-/

namespace WrittenOnTheWallII.GraphConjecture133MetricContactMatrices

open SimpleGraph

variable {V : Type*} [Fintype V] [DecidableEq V] [Nonempty V]

omit [Fintype V] [DecidableEq V] [Nonempty V] in
/-- The four-edge sibling route bounds the separation of two contacts on a
geodesic.  This is the strongest strict-shortcut restriction available from
the contact matrix alone. -/
theorem crossContact_index_gap_le_four {G : SimpleGraph V}
    {u v a b c : V} (p : G.Walk u v)
    (hp : p.length = G.dist u v) {i j : ℕ}
    (hi : i ≤ p.length) (hj : j ≤ p.length)
    (hia : G.Adj (p.getVert i) a) (hab : G.Adj a b)
    (hbc : G.Adj b c) (hcj : G.Adj c (p.getVert j)) :
    j ≤ i + 4 := by
  let q : G.Walk u v :=
    (((((p.take i).append hia.toWalk).append hab.toWalk).append hbc.toWalk).append
      hcj.toWalk).append (p.drop j)
  have hq : G.dist u v ≤ q.length := G.dist_le q
  have htake : (p.take i).length = i := by simp [Walk.take_length, hi]
  have hdrop : (p.drop j).length = p.length - j := by simp [Walk.drop_length]
  simp only [q, Walk.length_append, Walk.length_cons, Walk.length_nil,
    zero_add] at hq
  rw [htake, hdrop, ← hp] at hq
  omega

omit [Fintype V] [DecidableEq V] [Nonempty V] in
/-- A strict separation of five or more is incompatible with two contact
rows sharing a parent. -/
theorem not_crossContacts_of_gap_five {G : SimpleGraph V}
    {u v a b c : V} (p : G.Walk u v)
    (hp : p.length = G.dist u v) {i j : ℕ}
    (hi : i ≤ p.length) (hj : j ≤ p.length) (hgap : i + 5 ≤ j)
    (hia : G.Adj (p.getVert i) a) (hab : G.Adj a b)
    (hbc : G.Adj b c) :
    ¬G.Adj c (p.getVert j) := by
  intro hcj
  have := crossContact_index_gap_le_four p hp hi hj hia hab hbc hcj
  omega

/-- The abstract metric filter for early rows `0..4`: a pair of contact
indices survives exactly when its separation is at most four. -/
def EarlyMetricCompatible (i j : ℕ) : Prop :=
  i < 5 ∧ j < 5 ∧ (i ≤ j → j ≤ i + 4) ∧ (j ≤ i → i ≤ j + 4)

/-- Every pair of indices in the early window is metric-compatible.  Thus
the four-edge detour removes none of the twenty v0.15 matrices. -/
theorem earlyMetricCompatible_of_lt_five {i j : ℕ}
    (hi : i < 5) (hj : j < 5) :
    EarlyMetricCompatible i j := by
  unfold EarlyMetricCompatible
  omega

end WrittenOnTheWallII.GraphConjecture133MetricContactMatrices
