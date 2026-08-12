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
# Written on the Wall II - Conjecture 64

*Reference:*
[E. DeLaVina, Written on the Wall II, Conjectures of Graffiti.pc](http://cms.dt.uh.edu/faculty/delavinae/research/wowII/)

## Counterexample

The conjecture is false for the lexicographic product $C_5[K_4]$ ($n = 20$,
$11$-regular). There $f(G) = 4$, $\alpha(G) = 2$ and
$n \bmod \Delta = 20 \bmod 11 = 9$, so the conjectured lower bound is
$\lceil\sqrt{2 \cdot 10}\rceil = 5 > 4$.

This counterexample, together with a smaller 18-vertex witness and the
infinite family $C_5[K_m]$ for $m \geq 4$, was first published by J. J.
Gebendorfer in July 2026; see
[Zenodo 10.5281/zenodo.21595503](https://doi.org/10.5281/zenodo.21595503).
-/

namespace WrittenOnTheWallII.GraphConjecture64

open SimpleGraph

namespace Counterexample

/-- The index of the four-vertex clique containing `v`. -/
private def block (v : Fin 20) : ℕ := v.val / 4

/-- The lexicographic product $C_5[K_4]$. -/
def graph : SimpleGraph (Fin 20) :=
  SimpleGraph.fromRel fun u v =>
    block u = block v ∨ (block u + 1) % 5 = block v

instance : DecidableRel graph.Adj := by
  unfold graph
  infer_instance

/-- The counterexample is connected. -/
@[category API, AMS 5]
lemma connected : graph.Connected := by
  native_decide

/-- Every vertex has degree eleven, so the maximum degree is eleven. -/
@[category API, AMS 5]
lemma maxDegree : graph.maxDegree = 11 := by
  native_decide

/-- The independence number of the counterexample is exactly two. -/
@[category API, AMS 5]
lemma indepNum : graph.indepNum = 2 := by
  rw [indep_num_eq_computable]
  native_decide

/-- Bipartiteness of an induced subgraph is inherited by restriction. -/
private lemma induce_isBipartite_of_subset {V : Type*} (G : SimpleGraph V)
    {s t : Finset V} (hts : t ⊆ s)
    (hs : (G.induce (s : Set V)).IsBipartite) :
    (G.induce (t : Set V)).IsBipartite := by
  classical
  rcases hs with ⟨c⟩
  exact ⟨SimpleGraph.Coloring.mk
    (fun v => c ⟨v, hts v.property⟩)
    (by
      intro u v huv
      exact c.valid huv)⟩

/-- Every five-vertex subset defeats every two-coloring. This is a finite
certificate checking `C(20, 5) * 2^5` small cases. -/
private lemma five_not_two_colorable :
    ∀ s : Finset (Fin 20), s.card = 5 →
      ∀ c : ↑(s : Set (Fin 20)) → Fin 2,
        ∃ u v, (graph.induce (s : Set (Fin 20))).Adj u v ∧ c u = c v := by
  native_decide

/-- No five-vertex induced subgraph is bipartite. -/
private lemma no_bipartite_five (s : Finset (Fin 20)) (hs : s.card = 5) :
    ¬(graph.induce (s : Set (Fin 20))).IsBipartite := by
  rintro ⟨c⟩
  obtain ⟨u, v, huv, hcolor⟩ := five_not_two_colorable s hs c
  exact c.valid huv hcolor

/-- Every induced bipartite subgraph has at most four vertices. -/
private lemma bipartite_card_le_four (s : Finset (Fin 20))
    (hs : (graph.induce (s : Set (Fin 20))).IsBipartite) : s.card ≤ 4 := by
  by_contra h
  push_neg at h
  obtain ⟨t, hts, htcard⟩ :=
    Finset.exists_subset_card_eq (n := 5) (s := s) (by omega)
  exact no_bipartite_five t htcard
    (induce_isBipartite_of_subset graph hts hs)

/-- Every induced forest has at most four vertices. -/
@[category API, AMS 5]
lemma largestInducedForestSize_le : graph.largestInducedForestSize ≤ 4 := by
  unfold SimpleGraph.largestInducedForestSize
  apply csSup_le
  · refine ⟨0, ∅, ?_, rfl⟩
    letI : Subsingleton ↑(↑(∅ : Finset (Fin 20)) : Set (Fin 20)) :=
      ⟨fun a _ => False.elim (by simpa using a.property)⟩
    exact SimpleGraph.IsAcyclic.of_subsingleton
  · rintro n ⟨s, hs, rfl⟩
    exact bipartite_card_le_four s hs.isBipartite

end Counterexample

/-- The numerical lower bound in Conjecture 64 is five on the counterexample. -/
lemma ceil_sqrt_twenty : ⌈Real.sqrt (20 : ℝ)⌉ = (5 : ℤ) := by
  rw [Int.ceil_eq_iff]
  constructor
  · norm_num
    exact (Real.lt_sqrt (by norm_num : (0 : ℝ) ≤ 4)).2 (by norm_num)
  · exact (Real.sqrt_le_iff).2 ⟨by norm_num, by norm_num⟩

/--
WOWII [Conjecture 64](http://cms.dt.uh.edu/faculty/delavinae/research/wowII/)
asked whether every simple connected graph $G$ satisfies
$f(G) \geq \lceil\sqrt{\alpha(G) \cdot (1 + (n \bmod \Delta(G)))}\rceil$.
The answer is no, as witnessed by $C_5[K_4]$.

In the displayed Lean expression, `G.indepNum`, `Fintype.card α`, `%`, and
`G.maxDegree` are combined in `ℕ`; that natural-number product is then coerced
to `ℝ` as the argument of `Real.sqrt`.
-/
@[category research solved, AMS 5]
theorem conjecture64 : answer(False) ↔
    ∀ (α : Type) [Fintype α] [DecidableEq α] [Nontrivial α]
      (G : SimpleGraph α) [DecidableRel G.Adj] (_h : G.Connected),
      ⌈Real.sqrt ((G.indepNum * (1 + Fintype.card α % G.maxDegree) : ℕ) : ℝ)⌉ ≤
        (G.largestInducedForestSize : ℝ) := by
  show False ↔ _
  rw [false_iff]
  intro h
  have hbad := h (Fin 20) Counterexample.graph Counterexample.connected
  rw [Counterexample.indepNum, Counterexample.maxDegree] at hbad
  norm_num [ceil_sqrt_twenty] at hbad
  have hf := Counterexample.largestInducedForestSize_le
  exact (by omega : ¬(5 : ℕ) ≤ Counterexample.graph.largestInducedForestSize)
    (by exact_mod_cast hbad)

end WrittenOnTheWallII.GraphConjecture64
