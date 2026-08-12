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

Draft formulation in the google-deepmind/formal-conjectures house style.
Not yet built against the repo; see the README of Kuberwastaken/c5-k4.

## Counterexample

The conjecture is false for the lexicographic product $C_5[K_4]$ ($n = 20$,
$11$-regular). There $f(G) = 4$, $\alpha(G) = 2$ and
$n \bmod \Delta = 20 \bmod 11 = 9$, so the conjectured lower bound is
$\lceil\sqrt{2 \cdot 10}\rceil = 5 > 4$. The violation persists for
$C_5[K_m]$ for every $m \ge 4$, with equality at $m = 3$.
First refuted (same carrier graph, plus an 18-vertex witness) by
J. J. Gebendorfer, Zenodo, July 2026.
-/

namespace WrittenOnTheWallII.GraphConjecture64

open SimpleGraph

/--
WOWII [Conjecture 64](http://cms.dt.uh.edu/faculty/delavinae/research/wowII/)
asked whether every simple connected graph $G$ satisfies
$f(G) \geq \lceil\sqrt{\alpha(G) \cdot (1 + (n \bmod \Delta(G)))}\rceil$.
The answer is no, as witnessed by $C_5[K_4]$.
-/
@[category research solved, AMS 5]
theorem conjecture64 : answer(False) ↔
    ∀ (α : Type) [Fintype α] [DecidableEq α] [Nontrivial α]
      (G : SimpleGraph α) (_h : G.Connected),
      ⌈Real.sqrt (G.indepNum * (1 + Fintype.card α % G.maxDegree))⌉ ≤
        (G.largestInducedForestSize : ℝ) := by
  sorry

end WrittenOnTheWallII.GraphConjecture64
