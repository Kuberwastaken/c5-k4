# WOWII 40 theorem-shadow at the one-edge `K_(2,c)` wall

Date: 2026-08-13 UTC

Status: analytic obstruction; no new computational trial opened.

## Question considered

The exact one-edge wall consists of `K_(2,c)` plus one edge inside the
`c`-vertex side, with

```text
(n,f,b,p)=(c+2,c,c+1,c-3).
```

The proposed next trial was required to choose one bounded surgery intended to
lower `f` without the compensating decrease in `b` or `p` seen for disjoint
matchings and shared-endpoint stars. Before freezing a new computation, the
full internal-edge neighborhood can be analyzed directly.

## Setup

Let `X,Y` be the two nonadjacent hubs, let `B` be the other `c` vertices, and
let `H` be an arbitrary graph added inside `B`. The resulting graph `G(H)` has
all edges from `{X,Y}` to `B`, no edge `XY`, and internal edge set `E(H)`.

The one-edge wall corresponds to `H=K_2` plus isolates. Any continuation using
only internal-side edge additions replaces `H` by a supergraph of this seed.

## Bipartite-rank obstruction

Suppose `b(G(H))>=c+1`. Since `G(H)` has `c+2` vertices, there is an induced
bipartite subgraph obtained by deleting at most one vertex.

- If the deleted vertex is a hub, the other hub remains adjacent to every
  vertex of `B`. Any edge of `H` would form a triangle with that hub. Therefore
  `H` must be edgeless.
- If the deleted vertex is `z in B`, both hubs remain. Every edge of `H-z`
  forms a triangle with either hub. Therefore `H-z` must be edgeless.

Consequently

```text
b(G(H)) >= c+1  ==>  vertexCover(H) <= 1.
```

A graph with vertex-cover number at most one is a star plus isolated vertices,
so it is a forest. Hence all `c` vertices of `B` themselves form an induced
forest and

```text
b(G(H)) >= c+1  ==>  f(G(H)) >= c.
```

The contrapositive is the desired obstruction:

```text
f(G(H)) < c  ==>  b(G(H)) <= c.
```

Thus no internal-edge surgery can lower the forest coordinate below the
one-edge wall while preserving its bipartite coordinate. The compensating
`b` movement observed for disjoint matchings is mathematically forced, not a
search accident.

## Path-cover obstruction

Minimum path-cover number is monotone nonincreasing under edge addition. Since
the one-edge wall has `p=c-3`, every internal-edge continuation satisfies

```text
p(G(H)) <= c-3.
```

If `b>=c+1`, the preceding argument gives `f>=c`, while

```text
ceil((p+b+1)/2)
  <= ceil(((c-3)+(c+1)+1)/2)
  = c.
```

So a strict crossing is impossible throughout the entire coordinate-preserving
internal-addition cone.

The star subcone explains the most recent exact trial more sharply. Preserving
`b=c+1` forces `H` to be a star. With one edge, `p=c-3` and equality holds. As
soon as a second edge shares the center, a spanning linear forest can use six
edges rather than five, so `p=c-4` and slack becomes one. Additional arms do
not undo that move.

## Decision

No single plausible coordinate-separating internal-side surgery remains:

- cyclic internal structure is necessary to make the `B` witness cease being
  a forest, but it forces `b<=c`;
- star structure preserves `b=c+1`, but also preserves `f>=c` and additional
  edges lower `p`;
- all edge additions weakly lower `p`, never raise it toward a crossing.

A surgery that also deletes or rewires hub incidences could escape the lemma,
but no such transformation is justified by the completed equality data. Picking
one now would be menu fishing rather than a prospectively motivated move.

Accordingly, no contract, database rerun, development solve, ledger, commit,
release, or public action was started. The strict outcome is
`THEOREM_SHADOW_OBSTRUCTION`, not `HOLD_BOUNDED`: the requested coordinate
direction is analytically empty within the natural internal-edge surgery
class.
