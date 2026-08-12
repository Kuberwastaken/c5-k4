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
# Written on the Wall II - Conjecture 309

*Reference:*
[E. DeLaVina, Written on the Wall II, Conjectures of Graffiti.pc](http://cms.dt.uh.edu/faculty/delavinae/research/wowII/)

## Counterexample

The conjecture is false for the blown-up 5-cycles $C_5[K_k]$ for every
$k \ge 3$ (J. J. Gebendorfer, Zenodo, doi:10.5281/zenodo.21553295, July
2026, building on the $C_5[K_4]$ carrier from the disproofs of
Conjectures 63/85). For $C_5[K_4]$: $\gamma_t = 3$, every vertex has
$\operatorname{dist\_even}(v) = 9$ and $\operatorname{even\_horizontal}(v)
= 28$, and every complement edge has $|N_{\bar G}(e)| = 16$, so the
conjectured upper bound is $\frac{1}{2}(-19 + 16) = -\tfrac32 < 3$.
$C_5$ itself attains equality ($3 \le 3$).
-/

namespace WrittenOnTheWallII.GraphConjecture309

open SimpleGraph

variable {V : Type} [Fintype V] [DecidableEq V]

/-- `evenHorizontal G v` counts the edges of `G` whose two endpoints lie at
the same even distance from `v` ("even horizontal edges" in DeLaVina's
vocabulary). Proposed companion to `SimpleGraph.distEven`. -/
def evenHorizontal (G : SimpleGraph V) [DecidableRel G.Adj] (v : V) : ℕ :=
  (G.edgeFinset.filter fun e =>
    let distances := e.toFinset.image (G.computable_dist v)
    distances.card = 1 ∧ ∃ d ∈ distances, Even d).card

/-- The maximum correction `dist_even(v) - even_horizontal(v)`. -/
noncomputable def maxEvenCorrection (G : SimpleGraph V) [Nonempty V]
    [DecidableRel G.Adj] : ℤ :=
  (Finset.univ.image
    (fun v => (G.distEven v : ℤ) - (evenHorizontal G v : ℤ))).max' (by simp)

/-- The minimum complement-edge neighborhood-union order.  This is an option
because a complete graph has no complement edge. -/
def minComplementEdgeNeighborhood (G : SimpleGraph V) [DecidableRel G.Adj] : Option ℕ :=
  ((Gᶜ.edgeFinset).image
    (fun e => Sym2.lift ⟨fun u w =>
      ((Gᶜ.neighborFinset u) ∪ (Gᶜ.neighborFinset w)).card,
      fun u w => by
        change ((Gᶜ.neighborFinset u) ∪ (Gᶜ.neighborFinset w)).card =
          ((Gᶜ.neighborFinset w) ∪ (Gᶜ.neighborFinset u)).card
        rw [Finset.union_comm]⟩ e)).min

/-- The exact finite universal statement printed as WOWII 309. -/
def conjecture309Statement : Prop :=
  ∀ (V : Type) [Fintype V] [DecidableEq V] [Nonempty V]
    (G : SimpleGraph V) [DecidableRel G.Adj], G.Connected → 2 < Fintype.card V →
    ∀ mt ∈ minComplementEdgeNeighborhood G,
      (G.totalDominationNumber : ℝ) ≤
        ((maxEvenCorrection G : ℝ) + (mt : ℝ)) / 2

namespace Counterexample

/-- Vertices of the five four-vertex cliques. -/
abbrev Vertex := Fin 5 × Fin 4

/-- The carrier `C₅[K₄]`. -/
def graph : SimpleGraph Vertex where
  Adj u v := u ≠ v ∧
    (u.1 = v.1 ∨ (SimpleGraph.cycleGraph 5).Adj u.1 v.1)
  symm := by
    rintro u v ⟨hne, h⟩
    exact ⟨hne.symm, h.elim (fun h => Or.inl h.symm)
      (fun h => Or.inr ((SimpleGraph.cycleGraph 5).symm h))⟩
  loopless := by
    intro v h
    exact h.1 rfl

instance : DecidableRel graph.Adj := fun u v =>
  inferInstanceAs (Decidable (u ≠ v ∧
    (u.1 = v.1 ∨ (SimpleGraph.cycleGraph 5).Adj u.1 v.1)))

/-- Computable even-distance count for the finite certificate. -/
def computableDistEven (G : SimpleGraph V) [DecidableRel G.Adj] (v : V) : ℕ :=
  (Finset.univ.filter fun w => Even (G.computable_dist v w)).card

lemma distEven_eq_computable (G : SimpleGraph V) [DecidableRel G.Adj] (v : V) :
    G.distEven v = computableDistEven G v := by
  simp only [SimpleGraph.distEven, computableDistEven, G.dist_eq_computable]

lemma connected : graph.Connected := by native_decide

lemma maxEvenCorrection_eq : maxEvenCorrection graph = -19 := by
  unfold maxEvenCorrection
  simp_rw [distEven_eq_computable]
  native_decide

lemma minComplementEdgeNeighborhood_eq :
    minComplementEdgeNeighborhood graph = some 16 := by
  native_decide

end Counterexample

/--
WOWII [Conjecture 309](http://cms.dt.uh.edu/faculty/delavinae/research/wowII/)
asked whether every simple connected graph $G$ with $n > 2$ satisfies
$\gamma_t(G) \leq \frac{1}{2}\left[\max_v\{\operatorname{dist\_even}(v) -
\operatorname{even\_horizontal}(v)\} + \min_{e \in E(\bar G)}
|N_{\bar G}(e)|\right]$, where the minimum ranges over edges of the
complement and neighborhoods are taken in the complement (the two
endpoints of $e$ belong to $N_{\bar G}(e)$ since they are adjacent in
$\bar G$). The answer is no, as witnessed by $C_5[K_3]$ and every larger
blown-up 5-cycle.
-/
@[category research solved, AMS 5]
theorem conjecture309 : answer(False) ↔ conjecture309Statement := by
  constructor
  · intro h
    exact h.elim
  · intro h
    have hbad := h Counterexample.Vertex Counterexample.graph
      Counterexample.connected (by native_decide) 16
      (by simp [Counterexample.minComplementEdgeNeighborhood_eq])
    rw [Counterexample.maxEvenCorrection_eq] at hbad
    have hnonneg : (0 : ℝ) ≤ Counterexample.graph.totalDominationNumber := by positivity
    norm_num at hbad
    linarith

end WrittenOnTheWallII.GraphConjecture309
