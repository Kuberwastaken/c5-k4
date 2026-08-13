# Frozen prospective trial: Erdős 128 canonical Hajós join

Frozen: **2026-08-13 UTC, before constructing or evaluating the development graph**

## Current target and lane separation

The current DeepMind declaration `Erdos128.erdos_128` asks whether every
finite graph in which each induced subgraph on a formally eligible half-order
vertex set has strictly more than `n^2/50` edges must contain a triangle.
Upstream `main` blob SHA at freeze is
`8fdaf7eaa6629dfd5aaad6521f7c84a6a9e96dca` and the declaration remains
`research open`.

This is an induced-density/triangle cluster, disjoint from the completed Reed
chromatic/clique/degree lanes. The existing Erdős 128 prospective lane closes
ordinary Mycielski lifting because its shadow set is an eligible independent
set. This trial uses graph composition instead.

## Exact tight carrier

Let `B2` be the independent-set blow-up of `C5` with two vertices per bag,
labeled consecutively `0..9`. It is triangle-free. For its formally minimal
eligible size five, the exact minimum induced edge count is two, giving

`50*2 - 10^2 = 0`.

Thus `B2` lies exactly on the strict-premise boundary.

## Sole frozen transformation

Take two labeled copies of `B2`, on `0..9` and `10..19`. In the first copy
choose canonical carrier edge `(0,2)`; in the second choose `(10,12)`.

Perform exactly one canonical Hajós join:

1. delete `(0,2)` and `(10,12)`;
2. identify vertex `10` with vertex `0`;
3. add edge `(2,12)`;
4. relabel the resulting 19 vertices increasingly.

No alternate edge, endpoint identification, second join, switch, or adaptive
variant is permitted. The development cap is one graph.

## Predicted coordinate direction

The output is predicted to have order 19, 39 edges, and remain triangle-free.
The formal minimum eligible size is nine, and the strict premise requires at
least eight induced edges because `50e > 19^2 = 361`.

The preregistered prediction is `PREMISE_FALSE_STRICT`: the identified-vertex
bottleneck should allow a nine-vertex set assembled from sparse carrier
pieces on both sides with at most seven induced edges. A positive margin would
instead be an adversarial counterexample candidate and trigger immediate
independent recomputation and status review.

## Mandatory protocol

1. Re-run the exact connected triangle-free Atlas/named-control database gate,
   including the `B2` equality calibration, before development evaluation.
2. Construct only the frozen join and verify its canonical digest, order,
   edge count, and triangle-free certificate.
3. Enumerate every eligible subset exactly to obtain the minimum induced edge
   count and a replayable witness; each process is capped at 60 seconds.
4. Independently recompute the minimum using a separately implemented
   branch-and-bound search and replay the witness directly.
5. Stop on ambiguity or any positive strict-premise margin.

No WoW I source, random search, commit, push, release, issue, PR, or other
public action is authorized.
