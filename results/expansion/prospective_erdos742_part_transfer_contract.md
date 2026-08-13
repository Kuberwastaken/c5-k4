# Frozen prospective trial: Erdős 742 one-vertex bipartition transfer

Frozen: **2026-08-13 UTC, before database or development evaluation**

## Current target

The current DeepMind declaration `Erdos742.erdos_742` formalizes the
Murty--Simon conjecture: every finite diameter-2-critical graph on `n`
vertices has at most `floor(n^2/4)` edges. The declaration remains
`research open` on upstream `main`.

This is an edge-density/diameter-criticality cluster, separate from the recent
Erdős 128, Dean, Reed, and WOWII lanes. Upstream also records Fan's theorem for
orders at most 24, so this order-10 trial is calibration inside a proved finite
range, never a novelty claim.

## Equality carrier and sole transformation

The exact carrier is the labeled complete bipartite graph `K5,5`, with parts

`A={0,1,2,3,4}` and `B={5,6,7,8,9}`.

It is diameter-2-critical and has 25 edges, attaining
`floor(10^2/4)=25`.

Freeze exactly one transformation: transfer canonical vertex 4 from `A` to
`B` and rebuild all cross-part edges, producing labeled `K4,6` with parts

`A'={0,1,2,3}` and `B'={4,5,6,7,8,9}`.

No alternate order, second transfer, edge surgery, or adaptive variant is
permitted. The development cap is one graph.

## Predicted coordinate direction

Complete bipartite structure should preserve the full premise:

- connected diameter exactly 2;
- deleting any edge raises the endpoint distance from 1 to 3, so the graph is
  diameter-2-critical.

The predicted output has 24 edges against the unchanged order-10 bound 25,
so the equality residual moves from zero to safe-side slack one.

## Mandatory protocol

1. Exhaust every connected diameter-2-critical Atlas graph of orders 3--7,
   plus named complete-bipartite and Petersen controls; verify the bound and
   retain deletion-diameter witnesses.
2. Reproduce `K5,5` equality before constructing the development graph.
3. Construct only frozen `K4,6`; exactly verify diameter, every singleton-edge
   deletion, edge count, and bound.
4. Independently verify criticality by the structural endpoint-distance
   criterion and replay all-pairs distances.
5. Stop on any ambiguity or numerical violation.

Every subprocess has a hard 60-second cap. The JSONL ledger is append-only.
No WoW I source, random search, commit, push, release, issue, PR, or other
public action is authorized.
