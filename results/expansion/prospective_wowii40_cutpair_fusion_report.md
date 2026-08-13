# WOWII 40 prospective two-hub cut-bottleneck trial

## Outcome

`HOLD_BOUNDED`, with all 12 development graphs exactly tight.

This construction successfully combined the two properties that the preceding
experiments separated: it preserved a certified path-cover bottleneck while
making forests from different petals incompatible through cross-petal cycles.
It reached the conjectured wall at every tested order but did not cross it.

## Frozen construction

The only inputs were two exact bipartite equality seeds:

- `C] = K_(2,2)`, with `(n,f,b,p)=(4,3,4,1)`;
- `Ds[ = K_(2,3)`, with `(n,f,b,p)=(5,4,5,1)`.

For every frozen multiset of two through five seeds, the two vertices in each
seed's canonical size-two color class were identified across all copies. The
two resulting nonadjacent hubs are `X,Y`. If the seed remainders contain `c`
vertices total, the fused graph is `K_(2,c)`, retaining the full equality-seed
provenance in its record.

This differs from the prior one-hub bouquets and cross-petal rings. There are
no cyclic ring edges and no freely chosen all-pairs edge additions. Instead,
two cut vertices are simultaneously fused across complete seed copies, and
every pair of vertices from different petals lies on a four-cycle through both
hubs.

## Gates and exact results

The exact 1,031-graph #40 sanity gate passed before any fusion was evaluated.
Both seed coordinate tuples and their canonical bipartitions were then
reverified by the exact evaluator.

The 18 frozen parameter pairs deduplicated to 12 graphs, one at each order 6
through 17. Every graph completed within the process cap:

| quantity | exact value |
|---|---|
| remainder components `c` | 4 through 15 |
| order `n` | `c+2` |
| largest induced forest `f` | `c+1` |
| largest induced bipartite order `b` | `c+2=n` |
| minimum path cover `p` | `c-2` |
| right side | `c+1` |
| slack | `0` for all 12 |

There were zero crossings and zero timeouts.

## Independent certificates

Deleting `{X,Y}` leaves exactly `c` singleton components. Across a path cover,
a path containing `s` separator vertices can meet at most `s+1` of those
components. Summing over all paths gives `c <= p+2`, hence `p>=c-2`. The
emitted path `z1-X-z2-Y-z3` plus `c-3` singleton paths gives equality.

The entire graph is bipartite, so `b=n`. For the forest number, one hub plus
all `c` remainder vertices gives an induced star of order `c+1`. Any induced
subgraph containing both hubs and two remainder vertices contains a four-cycle,
while using at most one remainder with both hubs has order at most three.
Therefore no larger induced forest exists and `f=c+1`.

All computational witnesses and these closed-form certificates were replayed
independently for every graph. The append-only record stream has SHA-256
`6e2d9ee1d5e052ff7f79605813697b74d378239d0d63f09dd5814feb38f4bbea`.

## Interpretation

This is the cleanest #40 wall geometry produced by the sequence: separator
fragmentation raises `p`, dense cross-petal four-cycles pin `f`, and
bipartiteness keeps `b=n`. The exact calculation nevertheless lands on

```text
f = ceil((p+b+1)/2)
```

identically. It exposes a sharp infinite equality mechanism rather than a
counterexample. Per the frozen protocol, this trial is closed and is not to be
retuned post hoc.

No commit, push, release, issue, PR, or public action was taken.
