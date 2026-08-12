/-
Copyright 2026 The Formal Conjectures Authors.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
-/

import FormalConjecturesUtil

/-!
# Written on the Wall I - Conjecture 889

*Reference:*
[S. Fajtlowicz, *Written on the Wall*, July 2004 version](https://web.archive.org/web/20240000000000id_/http://www.math.uh.edu/~clarson/wow-july2004.ps)

Conjecture 822 colors a nonedge blue when adding it preserves membership in
the graph class. For the class of triangle-free graphs, this says precisely
that the endpoints have no common neighbor. The helper `blueGraph` below
specializes that source definition rather than treating arbitrary pairs at
distance other than two as blue.

## Counterexample

The conjecture is false for $\overline{C_5[K_4]}$. This graph is connected,
$8$-regular, triangle-free, and has diameter two. Thus every vertex has exactly
eight vertices at odd distance, while every nonedge has a common neighbor.
The blue graph is therefore empty and has clique number $1<8/4=2$.
-/

namespace WrittenOnTheWallI.GraphConjecture889

open SimpleGraph

variable {V : Type*} [Fintype V] [DecidableEq V]

/-- The blue graph associated by Conjecture 822 to the class of triangle-free
graphs: a nonedge is blue exactly when its endpoints have no common neighbor. -/
def blueGraph (G : SimpleGraph V) : SimpleGraph V where
  Adj u v := u ≠ v ∧ ¬G.Adj u v ∧ Disjoint (G.neighborSet u) (G.neighborSet v)
  symm := by
    rintro u v ⟨huv, hnonedge, hdisjoint⟩
    exact ⟨huv.symm, fun h => hnonedge (G.symm h), hdisjoint.symm⟩
  loopless := by
    intro v h
    exact h.1 rfl

/-- The number of vertices at odd graph distance from $v$. -/
noncomputable def distOdd (G : SimpleGraph V) (v : V) : ℕ :=
  (Finset.univ.filter fun w => Odd (G.dist v w)).card

/-- The maximum odd-distance count of a nonempty finite graph. -/
noncomputable def maxDistOdd (G : SimpleGraph V) [Nonempty V] : ℕ :=
  (Finset.univ.image (distOdd G)).max' (by simp)

namespace Counterexample

/-- Vertices are a five-cycle coordinate and a four-element fiber. -/
abbrev Vertex := Fin 5 × Fin 4

/-- The complement of `C₅[K₄]`, presented as the four-fold independent blow-up
of the five-cycle. -/
abbrev graph : SimpleGraph Vertex :=
  (SimpleGraph.cycleGraph 5).comap Prod.fst

/-- A computable version of the odd-distance count. -/
def computableDistOdd (G : SimpleGraph V) [DecidableRel G.Adj] (v : V) : ℕ :=
  (Finset.univ.filter fun w => Odd (computable_dist G v w)).card

lemma distOdd_eq_computable (G : SimpleGraph V) [DecidableRel G.Adj] (v : V) :
    distOdd G v = computableDistOdd G v := by
  simp only [distOdd, computableDistOdd, dist_eq_computable]

lemma connected : graph.Connected := by
  decide +native

lemma regular : graph.IsRegularOfDegree 8 := by
  intro v
  native_decide +revert

lemma triangleFree : graph.CliqueFree 3 := by
  intro s hs
  obtain ⟨a, b, c, hab, hac, hbc, rfl⟩ := (is3Clique_iff.mp hs)
  have hab' : (SimpleGraph.cycleGraph 5).Adj a.1 b.1 := hab
  have hac' : (SimpleGraph.cycleGraph 5).Adj a.1 c.1 := hac
  have hbc' : (SimpleGraph.cycleGraph 5).Adj b.1 c.1 := hbc
  have hbase : ∀ x y z : Fin 5, (SimpleGraph.cycleGraph 5).Adj x y →
      (SimpleGraph.cycleGraph 5).Adj x z → (SimpleGraph.cycleGraph 5).Adj y z → False := by
    native_decide
  exact hbase a.1 b.1 c.1 hab' hac' hbc'

lemma distOdd_eq_eight (v : Vertex) : distOdd graph v = 8 := by
  rw [distOdd_eq_computable]
  native_decide +revert

lemma maxDistOdd_eq_eight : maxDistOdd graph = 8 := by
  unfold maxDistOdd
  rw [Finset.max'_eq_iff]
  simp [distOdd_eq_eight]

lemma blueGraph_eq_bot : blueGraph graph = ⊥ := by
  ext u v
  simp only [blueGraph, bot_adj, iff_false]
  rintro ⟨huv, hnonedge, hdisjoint⟩
  have hbase : ∀ x y : Fin 5, ¬(SimpleGraph.cycleGraph 5).Adj x y →
      ∃ z : Fin 5, (SimpleGraph.cycleGraph 5).Adj x z ∧
        (SimpleGraph.cycleGraph 5).Adj y z := by
    native_decide
  obtain ⟨z, huz, hvz⟩ := hbase u.1 v.1 hnonedge
  have huMem : (z, 0) ∈ graph.neighborSet u := huz
  have hvMem : (z, 0) ∈ graph.neighborSet v := hvz
  exact (Set.disjoint_left.1 hdisjoint) huMem hvMem

lemma blueCliqueNum_eq_one : (blueGraph graph).cliqueNum = 1 := by
  rw [blueGraph_eq_bot]
  have hmax : (⊥ : SimpleGraph Vertex).IsMaximumClique {(0, 0)} := by
    constructor
    · simp
    · intro t ht
      have : t.card ≤ 1 := by
        by_contra h
        have htwo : 2 ≤ t.card := by omega
        obtain ⟨u, hu, v, hv, huv⟩ := Finset.one_lt_card.mp (lt_of_lt_of_le Nat.one_lt_two htwo)
        exact ht hu hv huv
      simpa using this
  simpa using (SimpleGraph.maximumClique_card_eq_cliqueNum {(0, 0)} hmax).symm

end Counterexample

/--
Written on the Wall I, Conjecture 889, asked whether every nonempty finite
connected regular triangle-free graph $G$ has a blue clique on at least
$\max_v\operatorname{Odd}(v)/4$ vertices, with blue as defined in Conjecture
822. The answer is no, as witnessed by $\overline{C_5[K_4]}$.
-/
@[category research solved, AMS 5]
theorem conjecture889 : answer(False) ↔
    ∀ (V : Type) [Fintype V] [DecidableEq V] [Nonempty V]
      (G : SimpleGraph V) [DecidableRel G.Adj], G.Connected →
      (∃ d, G.IsRegularOfDegree d) → G.CliqueFree 3 →
      (maxDistOdd G : ℝ) / 4 ≤ ((blueGraph G).cliqueNum : ℝ) := by
  show False ↔ _
  rw [false_iff]
  intro h
  have hbad := h Counterexample.Vertex Counterexample.graph Counterexample.connected
    ⟨8, Counterexample.regular⟩ Counterexample.triangleFree
  rw [Counterexample.maxDistOdd_eq_eight, Counterexample.blueCliqueNum_eq_one] at hbad
  norm_num at hbad

end WrittenOnTheWallI.GraphConjecture889
