# Frozen prospective trial: Erdős 128 Mycielski lift of the equality carrier

Frozen: 2026-08-13 UTC, before constructing or evaluating the development
graph.

## Current DeepMind target and prior exposure

The sole target is `Erdos128.erdos_128` in current
`google-deepmind/formal-conjectures` commit
`9a1636c4030039f70cf78b866c216d8b6c5f35b0`.  The source file SHA-256 is
`4e95cb275ef07ed46a8fa206def1e59e175c1763d3a9dde416c121e10ac2ffce`.
It is tagged `research open` and asks whether a finite graph must contain a
triangle if every induced subgraph on a set `S` satisfying

```text
2*|S| + 1 >= |V|
```

has strictly more than `|V|^2/50` edges.

This is a current DeepMind Formal Conjectures target, not WoW I.  The existing
campaign inventory evaluated only fixed arsenal graphs and recorded the
balanced independent-set `C5` blow-ups at the strict-premise boundary.  No
structured Erdős 128 transformation trial or proof lane is recorded.

## Equality carrier and signed premise margin

Let `B2` be the independent-set blow-up of `C5` with five bags of order two.
It is triangle-free, has order ten, and its minimum induced-edge count among
eligible vertex sets is exactly two.  Therefore

```text
premiseMargin(B2) = 50*2 - 10^2 = 0.
```

The formal premise requires a strictly positive margin, so `B2` is an exact
equality carrier rather than a counterexample.

For any finite graph `G`, monotonicity under adding vertices means the minimum
over all eligible sizes is attained at
`k=ceil((|V|-1)/2)`: every larger eligible set contains a `k`-subset with no
more edges.  The evaluator nevertheless emits the minimizing set and directly
replays its edge count.

## Sole frozen transformation

Construct exactly one development graph: the Mycielski graph `M(B2)`.
For every original vertex `v`, add a shadow `v'`; retain all original edges;
for every original edge `uv`, add `u-v'` and `v-u'`; finally add one apex
adjacent to every shadow.  No other graph, iteration, parameter, mutation, or
adaptive follow-up is authorized.

The prospective rationale is that Mycielski lifting is a global
triangle-freeness-preserving transformation that duplicates every carrier
neighborhood and adds an apex constraint.  It changes induced-density geometry
without remaining inside the previously exhausted blow-up/interface-surgery
families.  The directional prediction is deliberately uncertain: duplicated
neighborhoods may raise half-set edge density, while the shadow layer may be a
large sparse obstruction.

## Database sanity gate

Before constructing `M(B2)`, evaluate exactly:

- every connected triangle-free Graph Atlas graph of orders 3--7;
- `C5`, `C7`, Petersen, `K(2,3)`, and `K(3,3)`;
- balanced independent-set `C5` blow-ups `B1` through `B4`.

For each graph emit graph6, order, edge count, triangle-free status, eligible
size, exact minimum induced-edge count, minimizing set, and signed margin.
The gate must reproduce margin zero on `B2` (the selected equality carrier),
reject no graph because of an implementation inconsistency, and classify
premise-false controls as such
rather than as holds.  Any unexpected premise-true triangle-free control is a
`DB_SANITY_REJECT` and stops development.

## Runtime, ledger, and taxonomy

- Every process and exact solve is capped below 60 seconds.
- Append, flush, and `fsync` every record before aggregate interpretation.
- `CANDIDATE`: triangle-free development graph with strictly positive margin.
- `PREMISE_FALSE_STRICT`: exact margin at most zero.
- `TIMEOUT_BRACKET`: any incomplete exact minimum; never a hold.
- `DB_SANITY_REJECT`: a gate inconsistency or unexpected triangle-free premise
  satisfaction.
- `HOLD_BOUNDED`: the one development graph is exact and not a candidate.

A candidate must be independently recomputed and receive a current
source/status/novelty audit.  No commit, push, release, issue, PR, README edit,
or other public action is authorized.
