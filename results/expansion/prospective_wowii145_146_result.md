# Prospective WOWII 145/146 trial: bounded hold

Date: **2026-08-13 UTC**

Verdict: **HOLD_BOUNDED**.  The frozen carrier-surgery experiment produced no
counterexample to either current DeepMind Formal Conjectures declaration.

## Audit trail

The contract was written before any trial construction was evaluated:
`prospective_wowii145_146_contract.md`.  All graph-level output and the final
verdict were appended to `prospective_wowii145_146_ledger.jsonl`.

The implementation is `scripts/prospective_wowii145_146_trial.py`.  Both its
gate and discovery processes completed under the 60-second process cap.

## Mandatory database gate

The exact formal readings were evaluated on:

- all **995** connected nontrivial graphs in NetworkX's Graph Atlas;
- `C5--C9`, `P7`, Petersen, `K3,3`, `K7`, stars, complete bipartite graphs;
- uniform controls `C5[K_m]`, `1 <= m <= 4`.

This is **1,026 gate graphs** in total.  Exact subset enumeration supplied the
induced-tree optimum for every Atlas graph and every named graph through order
12.  Larger uniform controls were certified by explicit induced-tree
witnesses.  There were zero crossings and zero unresolved gate cases.

The implementation of `eccSet` maximizes distance to the boundary over
vertices outside it.  This is extensionally the current Lean definition:
vertices inside the nonempty boundary contribute zero, and when the boundary
is the whole vertex set both implementations return zero.

## Frozen discovery result

The four preregistered lanes produced **990 distinct labelled constructions**:

1. unequal five-cycle clique blow-ups;
2. one- and two-tail carrier surgery;
3. one and two pendant clique blocks;
4. portal replacements of a complete adjacent-blob join, optionally followed
   by a tail.

Orders ranged up to 30.  Every graph had an explicit induced-tree witness
large enough to prove both target inequalities directly.  Therefore no graph
needed an unproved optimizer value and the discovery had **zero inconclusive
cases**.

For #145 the smallest certified residual was already **8**.  Two exact
representatives were checked:

```text
portal:m2:p1:t0:       tree=5, lMin(complement)=2, ecc(B)=1, R145=8
unequal:1,1,1,1,2:    tree=4, lMin(complement)=2, ecc(B)=0, R145=8
```

For #146 the closest lower residual was **1**.  Exhaustive subset enumeration
confirmed the exact optimum on two order-21/22 representatives:

```text
carrier + one leaf:                 tree=5, radius(G^2)=1, ecc(B)=2, R146=1
carrier + two same-blob leaves:     tree=5, radius(G^2)=1, ecc(B)=2, R146=1
```

The exact searches checked 2,072,033 and 4,162,143 subsets respectively and
finished in 11.04 and 24.70 seconds.

## Structural diagnosis

The proposed separating move does increase `ecc(B)`, but it does not isolate
that coordinate:

- every new tail layer that moves the boundary also extends an explicit
  induced tree;
- #146 is the genuine near-wall target, but the first asymmetric move changes
  the carrier from `tree=4, ecc(B)=0` to `tree=5, ecc(B)=2`, stopping one unit
  short of a crossing;
- #145 is not locally close in these lanes.  Dense clique blobs keep the
  complement local-independence minimum at least two and usually much larger,
  so the product term dominates the metric gain.

The bounded result is therefore a theorem signal rather than a discovery
candidate.  A useful next step for #146 is to prove a metric compensation
lemma relating an induced diametral path (and one branch toward a vertex far
from the periphery) to `2 ecc(B)`.  For #145, further carrier surgery is low
priority unless a construction can first force
`lMin(complement G) = 1`; without that coordinate separation the wall is not
close.

There is a sharper common signal.  On all 995 connected Atlas graphs, exact
enumeration gives

```text
tree(G) - 2 ecc(B(G)) >= 0,
```

with equality on 40 graphs and no negative case.  If this factor-free bound is
proved generally, each current declaration follows immediately from its
explicit positivity hypothesis, since the other multiplicative factor is a
positive natural number.  This is now the highest-information continuation;
it targets one structural lemma instead of performing more low-yield carrier
surgery.

No novelty claim or public action follows from this trial.
