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
# Written on the Wall I - Conjecture 191

*Reference:*
[S. Fajtlowicz, *Written on the Wall*, July 2004 version](https://web.archive.org/web/20240000000000id_/http://www.math.uh.edu/~clarson/wow-july2004.ps)

The section heading restricts the conjecture to connected graphs for which the
sum of the odd-distance counts is at most the sum of the even-distance
counts. In the source, the deficiency of a vertex is the number of nonedges
among its neighbors and `size` means the number of edges.

## Counterexample

The conjecture is false for the triangular graph $T(7)=L(K_7)$. Its minimum
vertex deficiency is $20$, whereas $|E|/\omega=105/6=17.5$. More generally,
$T(n)$ is a counterexample for every $n\geq 7$: its minimum deficiency is
$(n-2)(n-3)$ and $|E|/\omega=n(n-2)/2$.
-/

namespace WrittenOnTheWallI.GraphConjecture191

open SimpleGraph

variable {V : Type*} [Fintype V] [DecidableEq V]

/-- The deficiency of $v$: the number of nonedges induced by its neighborhood. -/
noncomputable def vertexDeficiency (G : SimpleGraph V) [DecidableRel G.Adj] (v : V) : ℕ :=
  (Gᶜ.edgeFinset.filter fun e => e.toFinset ⊆ G.neighborFinset v).card

/-- The number of vertices at odd graph distance from $v$. -/
noncomputable def distOdd (G : SimpleGraph V) (v : V) : ℕ :=
  (Finset.univ.filter fun w => Odd (G.dist v w)).card

/-- The minimum vertex deficiency of a nonempty finite graph. -/
noncomputable def minVertexDeficiency (G : SimpleGraph V) [DecidableRel G.Adj]
    [Nonempty V] : ℕ :=
  (Finset.univ.image (vertexDeficiency G)).min' (by simp)

/--
Written on the Wall I, Conjecture 191, asked whether every nonempty finite
simple connected graph $G$ satisfying
$\sum_v \operatorname{Odd}(v)\leq\sum_v \operatorname{Even}(v)$ also satisfies
$\min_v\operatorname{def}(v)\leq |E(G)|/\omega(G)$. The answer is no, as
witnessed by $T(7)=L(K_7)$ and every larger triangular graph.
-/
@[category research solved, AMS 5]
theorem conjecture191 : answer(False) ↔
    ∀ (V : Type*) [Fintype V] [DecidableEq V] [Nonempty V]
      (G : SimpleGraph V) [DecidableRel G.Adj], G.Connected →
      (∑ v, distOdd G v) ≤ ∑ v, G.distEven v →
      (minVertexDeficiency G : ℝ) ≤
        (G.edgeFinset.card : ℝ) / (G.cliqueNum : ℝ) := by
  sorry

end WrittenOnTheWallI.GraphConjecture191
