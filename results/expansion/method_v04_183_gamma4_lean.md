# Method v0.4 Lane P1: Lean proof of the WOWII 183 `gamma_c >= 4` tier

Date: **2026-08-13**. Status: **complete, warning-clean Lean formalization of
the paper theorem; this does not by itself prove WOWII 183**.

## Formalized theorem

The new file

```text
lean/GraphConjecture183GammaFour.lean
```

imports the existing `GraphConjecture183GammaThree` development and proves
the multi-vertex augmentation theorem from
`method_v04_183_multiext.md`. Its invariant-native endpoint is:

```lean
theorem six_le_b_of_connectedDominationNumber
    (G : SimpleGraph V) (hconn : G.Connected) {x z : V}
    (hdist : G.dist x z = 3)
    (hgamma : 4 ≤ G.connectedDominationNumber) :
    (6 : ℝ) ≤ b G
```

The proof first establishes the stronger explicit-witness statement:

```lean
∃ S : Finset V,
  S.card = 6 ∧ (G.induce (↑S : Set V)).IsBipartite
```

Thus the invariant inequality is not obtained by a nonconstructive numerical
shortcut: the six vertices survive in the formal interface.

## Formal proof structure

Fix a shortest path `P = x-a-d-z`. Assume for contradiction that no
six-vertex induced bipartite subgraph exists.

1. A five-vertex endpoint-leaf extension of `P` forces an explicit connected
   dominating triple. This is the formal counterpart of the maximum
   bipartite-set coloring argument.
2. Consequently every vertex outside `P` that touches `P` must touch `a` or
   `d`.
3. Let `R` be the vertices outside `P` anticomplete to `P`. If `R` contains
   two distinct vertices, adjoining them to `P` gives the explicit
   six-vertex bipartite witness, whether or not those two vertices are
   adjacent.
4. If `R` is empty, `{a,d}` is a connected dominating set.
5. If `R={r}`, connectedness supplies a first neighbor `y` on a path from
   `r` to `x`. The set `{a,d,y}` is connected and dominates the graph.

The last two cases contradict the hypothesis that all connected dominating
sets have at least four vertices. This proves the explicit witness theorem.
Shortest-path extraction then removes the supplied intermediate vertices,
and the existing repository definitions convert the result to
`largestInducedBipartiteSubgraphSize` and `b G`.

## Verification

Because the file imports the neighboring local Lean module, verification was
performed with a temporary `.olean` outside the repository and every command
was externally capped at 60 seconds:

```text
timeout 60s lake env lean -DwarningAsError=true \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  -o /tmp/c5k4-lean/GraphConjecture183GammaThree.olean \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture183GammaThree.lean

timeout 60s lake env bash -lc \
  'export LEAN_PATH=/tmp/c5k4-lean:$LEAN_PATH; \
   lean -DwarningAsError=true \
     -R /Users/kuber.mehta/Projects/c5-k4/lean \
     /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture183GammaFour.lean'
```

Result: **exit 0**, with the second command completing in approximately 11
seconds. The source contains no `sorry`, `admit`, or custom axiom. A temporary
axiom audit performed before the clean build reported exactly:

```text
[propext, Classical.choice, Quot.sound]
```

These are standard Lean/Mathlib foundations; `sorryAx` is absent.

## Exact campaign boundary

This formalizes the paper result

```text
distance-three pair and gamma_c(G) >= 4  ==>  b(G) >= 6.
```

Together with `GraphConjecture183GammaThree.lean`, both low connected-
domination tiers isolated by the #183 analysis now have no-sorry certificates.
The full conjecture still requires the source-specific unique-distance-three
and claw-free structure to control larger connected-domination values and its
cut-vertex branch. No full-conjecture or public-release claim follows from
this tier theorem alone.
