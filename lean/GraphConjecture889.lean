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

/--
Written on the Wall I, Conjecture 889, asked whether every nonempty finite
connected regular triangle-free graph $G$ has a blue clique on at least
$\max_v\operatorname{Odd}(v)/4$ vertices, with blue as defined in Conjecture
822. The answer is no, as witnessed by $\overline{C_5[K_4]}$.
-/
@[category research solved, AMS 5]
theorem conjecture889 : answer(False) ↔
    ∀ (V : Type*) [Fintype V] [DecidableEq V] [Nonempty V]
      (G : SimpleGraph V) [DecidableRel G.Adj], G.Connected →
      (∃ d, G.IsRegularOfDegree d) → G.CliqueFree 3 →
      (maxDistOdd G : ℝ) / 4 ≤ ((blueGraph G).cliqueNum : ℝ) := by
  sorry

end WrittenOnTheWallI.GraphConjecture889
