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
import Mathlib.Combinatorics.SimpleGraph.Connectivity.WalkCounting

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
def vertexDeficiency (G : SimpleGraph V) [DecidableRel G.Adj] (v : V) : ℕ :=
  ((Finset.univ.filter fun p : V × V =>
    p.1 ≠ p.2 ∧ G.Adj v p.1 ∧ G.Adj v p.2 ∧ ¬G.Adj p.1 p.2).card) / 2

/-- The number of vertices at odd graph distance from $v$. -/
noncomputable def distOdd (G : SimpleGraph V) (v : V) : ℕ :=
  (Finset.univ.filter fun w => Odd (G.dist v w)).card

/-- The minimum vertex deficiency of a nonempty finite graph. -/
def minVertexDeficiency (G : SimpleGraph V) [DecidableRel G.Adj]
    [Nonempty V] : ℕ :=
  (Finset.univ.image (vertexDeficiency G)).min' (by simp)

/-- The complete graph on seven vertices. -/
abbrev K7 : SimpleGraph (Fin 7) := completeGraph (Fin 7)

/-- The 21 edges of `K₇`, used as the vertex type of its line graph. -/
abbrev K7Edge : Type := {e : Sym2 (Fin 7) // e ∈ K7.edgeSet}

/-- The triangular graph `T(7)`, realized source-faithfully as the line graph of `K₇`. -/
abbrev T7 : SimpleGraph K7Edge := K7.lineGraph

instance : DecidableRel T7.Adj := fun e₁ e₂ =>
  decidable_of_iff
    (e₁ ≠ e₂ ∧ ∃ v : Fin 7, v ∈ (e₁ : Sym2 (Fin 7)) ∧ v ∈ (e₂ : Sym2 (Fin 7)))
    lineGraph_adj_iff_exists.symm

instance : Nonempty K7Edge :=
  ⟨⟨s(0, 1), by simp⟩⟩

/-- A computable version of the odd-distance count, for use by the certificate. -/
def computableDistOdd (G : SimpleGraph V) [DecidableRel G.Adj] (v : V) : ℕ :=
  (Finset.univ.filter fun w => Odd (G.computable_dist v w)).card

/-- A computable version of the even-distance count, for use by the certificate. -/
def computableDistEven (G : SimpleGraph V) [DecidableRel G.Adj] (v : V) : ℕ :=
  (Finset.univ.filter fun w => Even (G.computable_dist v w)).card

lemma distOdd_eq_computable (G : SimpleGraph V) [DecidableRel G.Adj] (v : V) :
    distOdd G v = computableDistOdd G v := by
  simp only [distOdd, computableDistOdd, G.dist_eq_computable]

lemma distEven_eq_computable (G : SimpleGraph V) [DecidableRel G.Adj] (v : V) :
    G.distEven v = computableDistEven G v := by
  simp only [SimpleGraph.distEven, computableDistEven, G.dist_eq_computable]

lemma T7_connected : T7.Connected := by native_decide

lemma T7_parity : (∑ v, distOdd T7 v) ≤ ∑ v, T7.distEven v := by
  simp_rw [distOdd_eq_computable, distEven_eq_computable]
  native_decide

lemma T7_minVertexDeficiency : minVertexDeficiency T7 = 20 := by native_decide

lemma T7_edgeFinset_card : T7.edgeFinset.card = 105 := by
  have h := T7.two_mul_card_edgeFinset
  have hpairs :
      (Finset.univ.filter fun (x : K7Edge × K7Edge) => T7.Adj x.1 x.2).card = 210 := by
    native_decide
  rw [hpairs] at h
  omega

lemma T7_cliqueNum : T7.cliqueNum = 6 := by
  have hfree : T7.CliqueFree 7 := by
    rw [← cliqueFinset_eq_empty_iff]
    native_decide
  have hnotfree : ¬T7.CliqueFree 6 := by
    rw [← cliqueFinset_eq_empty_iff]
    native_decide
  simp only [CliqueFree, not_forall, Classical.not_not] at hnotfree
  obtain ⟨s, hs⟩ := hnotfree
  apply le_antisymm
  · by_contra h
    have hseven : 7 ≤ T7.cliqueNum := by omega
    obtain ⟨t, ht⟩ := T7.exists_isNClique_cliqueNum
    exact hfree.mono hseven t ht
  · simpa [hs.card_eq] using hs.isClique.card_le_cliqueNum

/--
Written on the Wall I, Conjecture 191, asked whether every nonempty finite
simple connected graph $G$ satisfying
$\sum_v \operatorname{Odd}(v)\leq\sum_v \operatorname{Even}(v)$ also satisfies
$\min_v\operatorname{def}(v)\leq |E(G)|/\omega(G)$. The answer is no, as
witnessed by $T(7)=L(K_7)$ and every larger triangular graph.
-/
@[category research solved, AMS 5]
theorem conjecture191 : answer(False) ↔
    ∀ (V : Type) [Fintype V] [DecidableEq V] [Nonempty V]
      (G : SimpleGraph V) [DecidableRel G.Adj], G.Connected →
      (∑ v, distOdd G v) ≤ ∑ v, G.distEven v →
      (minVertexDeficiency G : ℝ) ≤
        (G.edgeFinset.card : ℝ) / (G.cliqueNum : ℝ) := by
  constructor
  · intro h
    exact h.elim
  · intro h
    have hT7 := h K7Edge T7 T7_connected T7_parity
    rw [T7_minVertexDeficiency, T7_edgeFinset_card, T7_cliqueNum] at hT7
    norm_num at hT7

#print axioms conjecture191

end WrittenOnTheWallI.GraphConjecture191
