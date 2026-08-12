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
# Graph Brain independence-number upper bound 081

*Reference:*
[Graph Brain, open independence-number conjectures, upper bound 081](https://github.com/math1um/objects-invariants-properties/issues/421)

The author-posted expression is

`independence_number(x) <= 2*diameter(x)/(edge_con(x) - vertex_con(x))`.

The source evaluator maps division by zero to positive infinity.  The
predicate `upper081Bound` below records that semantics explicitly rather than
using Lean's convention `a / 0 = 0`.

## Counterexample certificate

Two copies of $K_5$ sharing one hub have nine vertices and invariant tuple
$(\alpha,D,\lambda,\kappa)=(2,2,4,1)$.  Thus the claimed right-hand side is
$4/(4-1)=4/3<2$.  The executable computation of these four values and the
small-graph database gate live in
`certificates/graphbrain-alpha-upper-081/` in Kuberwastaken/c5-k4.

The current mathlib snapshot has no edge- or vertex-connectivity invariant.
This file therefore supplies source-faithful finite definitions and formally
checks the exact arithmetic reduction from the independently certified tuple.
Formal verification of the four windmill equalities remains a separate graph-
cut API task; no axiom or `sorry` is used here.
-/

namespace GraphBrain.AlphaUpper081

open SimpleGraph

variable {V : Type*} [Fintype V] [DecidableEq V]

/-- The least number of graph edges whose deletion makes the graph
disconnected.  The set is nonempty for every finite graph with at least two
vertices; `sInf ∅ = 0` handles the remaining degenerate cases. -/
noncomputable def edgeConnectivity (G : SimpleGraph V) : ℕ :=
  sInf {k : ℕ | ∃ F : Finset (Sym2 V),
    (F : Set (Sym2 V)) ⊆ G.edgeSet ∧ F.card = k ∧
      ¬(G.deleteEdges (F : Set (Sym2 V))).Connected}

/-- The least number of vertices whose deletion disconnects the graph or
leaves at most one vertex.  The second alternative gives the standard value
`n - 1` on `K_n`, matching the Graph Brain/NetworkX convention. -/
noncomputable def vertexConnectivity (G : SimpleGraph V) : ℕ :=
  sInf {k : ℕ | ∃ S : Finset V, S.card = k ∧
    (Fintype.card {v : V // v ∉ S} ≤ 1 ∨
      ¬(G.induce (S : Set V)ᶜ).Connected)}

/-- Graph Brain's upper-081 bound, including its evaluator's convention that
a zero denominator returns positive infinity and hence a vacuous hold. -/
def upper081Bound (G : SimpleGraph V) : Prop :=
  edgeConnectivity G = vertexConnectivity G ∨
    (G.indepNum : ℝ) ≤
      2 * (G.diam : ℝ) /
        ((edgeConnectivity G : ℝ) - (vertexConnectivity G : ℝ))

/-- The universal connected-graph statement posted as Graph Brain upper-081. -/
def upper081Statement : Prop :=
  ∀ (V : Type*) [Fintype V] [DecidableEq V] [Nontrivial V]
    (G : SimpleGraph V), G.Connected → upper081Bound G

/-- Exact arithmetic core of the order-nine counterexample certificate.

Supplying any connected graph with the windmill's independently checked
invariant tuple `(2, 2, 4, 1)` refutes the posted bound. -/
@[category test, AMS 5]
theorem invariantTuple_2_2_4_1_refutes
    (G : SimpleGraph V)
    (hα : G.indepNum = 2) (hD : G.diam = 2)
    (hλ : edgeConnectivity G = 4) (hκ : vertexConnectivity G = 1) :
    ¬upper081Bound G := by
  simp [upper081Bound, hα, hD, hλ, hκ]
  norm_num

/-- A certified realization of the windmill invariant tuple disproves the
universal Graph Brain statement.  This theorem isolates exactly the four
finite-graph equalities still to be discharged by a future connectivity API. -/
@[category research solved, AMS 5]
theorem upper081Statement_false_of_windmill_certificate
    (W : SimpleGraph (Fin 9)) (hW : W.Connected)
    (hα : W.indepNum = 2) (hD : W.diam = 2)
    (hλ : edgeConnectivity W = 4) (hκ : vertexConnectivity W = 1) :
    ¬upper081Statement := by
  intro h
  exact invariantTuple_2_2_4_1_refutes W hα hD hλ hκ (h (Fin 9) W hW)

end GraphBrain.AlphaUpper081
