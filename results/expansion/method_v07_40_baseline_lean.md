# WOWII 40 Rung 1: Lean proof of the source baseline

**Date:** 2026-08-13  
**Status:** proved locally, warning-clean, no `sorry`  
**Lean artifact:** `lean/GraphConjecture40Baseline.lean`

## Result

The first formal rung identified in
`results/expansion/method_v07_40_proof_ladder.md` is now proved. For every
finite connected graph on a nontrivial vertex type,

```text
largestInducedBipartiteSubgraphSize(G) + 2
  <= 2 * largestInducedForestSize(G).
```

The exact Lean theorem is:

```lean
theorem largestInducedBipartiteSubgraphSize_add_two_le_two_mul_forestSize
    (G : SimpleGraph V) [Nontrivial V] (hconn : G.Connected)
    (hfinite : 1 < Fintype.card V) :
    G.largestInducedBipartiteSubgraphSize + 2 ≤
      2 * G.largestInducedForestSize
```

This is the natural-number form of the source note
`f(G) >= b(G)/2 + 1`. It is a baseline only, not a proof of unrestricted
WOWII 40.

The traceable specialization is also closed in the exact real/ceiling shape
of the upstream declaration:

```lean
theorem conjecture40_of_pathCoverNumber_eq_one
    (G : SimpleGraph V) [Nontrivial V] (hconn : G.Connected)
    (hfinite : 1 < Fintype.card V)
    (hp : pathCoverNumber G = 1) :
    ⌈(((pathCoverNumber G : ℝ) + b G + 1) / 2)⌉ ≤
      G.largestInducedForestSize
```

No theorem containing an upstream `sorry` is used.

## Proof structure

The file first supplies the missing finite-optimization interfaces:

- `card_le_largestInducedForestSize` inserts any explicit acyclic induced
  witness into the `sSup` defining the forest invariant;
- `card_le_largestInducedBipartiteSubgraphSize` does the same for a bipartite
  witness;
- `exists_largestInducedBipartiteSubgraphSize_witness` proves that the finite
  bipartite `sSup` is attained, using `Nat.sSup_mem` and the ambient cardinality
  as an upper bound.

For acyclicity, the development proves a reusable criterion: a graph split
into two independent parts is acyclic when every vertex on the left has at
most one neighbor on the right. Its induced-subgraph form immediately yields

```text
I independent -> G[insert v I] acyclic.
```

For a maximum induced bipartite witness `S`, the existing explicit-coloring
equivalence supplies `c : V -> Fin 2`. The proof partitions `S` into

```text
A = {x in S | c(x)=0},
C = {x in S | c(x)!=0}.
```

Both classes are independent and `|A|+|C|=|S|`. Choose the larger class `I`.
Connectedness and nontriviality give an edge, so an independent set cannot be
all vertices; choose `v` outside `I`. Then `G[insert v I]` is a forest and

```text
f >= |I|+1 >= ceil(|S|/2)+1,
```

which is exactly `|S|+2 <= 2f`. Attainment of the bipartite maximum replaces
`|S|` by `B`.

For `pathCoverNumber G = 1`, `Int.ceil_le` reduces the upstream ceiling goal
to a real inequality. The cast of the natural baseline then closes it by
linear arithmetic.

## Verification

Every subprocess was externally capped at 60 seconds. The final build was run
from `/Users/kuber.mehta/Projects/formal-conjectures`:

```text
timeout 60s lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture40Baseline.lean
```

Result: **exit 0** in 6.71 seconds with no compiler output.

Temporary `#print axioms` checks for both public theorems reported exactly:

```text
[propext, Classical.choice, Quot.sound]
```

The audit commands were then removed and the warning-as-error build was rerun.
The final source contains no `sorry`, `admit`, custom `axiom`, `sorryAx`, or
project-specific axiom.

## Remaining boundary

Writing

```text
Sbasic(G) = 2f - (B+2),
```

the unrestricted conjecture still requires the exact residual inequality

```text
pathCoverNumber(G) - 1 <= Sbasic(G).
```

The new Lean theorem certifies the whole `p=1` branch and the source's stated
basic wall. It does not address the bipartite deficiency lemma
`ell >= 2*tau+1` or the slack-aware transfer from a maximum bipartite core.
