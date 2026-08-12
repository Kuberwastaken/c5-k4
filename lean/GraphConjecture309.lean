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

Draft formulation in the google-deepmind/formal-conjectures house style.
Not yet built against the repo; `evenHorizontal` is a proposed ForMathlib
addition (companion to `SimpleGraph.distEven`, added in PR #4592).

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
noncomputable def evenHorizontal (G : SimpleGraph V) (v : V) : ℕ :=
  (G.edgeFinset.filter fun e =>
    Sym2.lift ⟨fun u w => G.dist v u = G.dist v w ∧ Even (G.dist v u),
      fun u w => by simp [and_comm, eq_comm]⟩ e).card

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
theorem conjecture309 : answer(False) ↔
    ∀ (V : Type) [Fintype V] [DecidableEq V]
      (G : SimpleGraph V) (_h : G.Connected) (_hn : 2 < Fintype.card V),
      letI maxTerm := (Finset.univ.image
        (fun v => (G.distEven v : ℤ) - (evenHorizontal G v : ℤ))).max' (by simp)
      letI minTerm := ((Gᶜ.edgeFinset).image
        (fun e => Sym2.lift ⟨fun u w =>
          ((Gᶜ.neighborFinset u) ∪ (Gᶜ.neighborFinset w)).card,
          fun u w => by simp [Finset.union_comm]⟩ e)).min
      ∀ mt ∈ minTerm,
        (G.totalDominationNumber : ℝ) ≤ ((maxTerm : ℝ) + (mt : ℝ)) / 2 := by
  sorry

end WrittenOnTheWallII.GraphConjecture309
