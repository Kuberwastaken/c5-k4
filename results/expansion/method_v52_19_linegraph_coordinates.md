# WOWII 19 line-graph coordinate theorem

Date: **2026-08-13 UTC**

Status: **THEOREM_COORDINATE_LEMMA**.  No new prospective computation was
opened.

## Input wall

The completed part of the frozen line-graph trial produced five exact equality
outputs:

| graph6 | average eccentricity | local maximum | `b` |
|---|---:|---:|---:|
| `Ib~Tzjhhw` | `2` | `2` | `4` |
| `Hb~Tzjh` | `2` | `2` | `4` |
| `Glq^vg` | `2` | `2` | `4` |
| `ExdW` | `2` | `2` | `4` |
| `GmFooS` | `25/8` | `2` | `5` |

Thus every row has

```text
b(L(G)) = floor(averageEccentricity(L(G)) + 2),
```

but the metric/rank pair is not unique: four rows lie at `(2,4)`, while one
lies at `(25/8,5)`.  The common coordinate is the local maximum, and that
coordinate has a universal line-graph explanation.

## Exact coordinate reduction

Let `G` be a finite simple graph and let `L(G)` be its line graph.

### Local independence

Fix the line-graph vertex represented by a seed edge `e={u,v}`.  Every
neighbor of `e` is either another edge incident with `u` or another edge
incident with `v`.  The `u`-incident edges form a clique in `L(G)`, as do the
`v`-incident edges.  An independent subset of this neighborhood therefore
contains at most one edge from each clique.  Hence

```text
alpha(L(G)[N(e)]) <= 2,
localMax(L(G)) <= 2.
```

All five equality outputs attain this ceiling.

### Induced-bipartite rank

For a seed-edge set `F subset E(G)`, the line graph induced by the vertices
`F` is exactly the line graph of the selected-edge subgraph `(V(G),F)`.

That induced line graph is bipartite if and only if:

1. every seed vertex has selected degree at most two; and
2. every cycle in the selected-edge subgraph is even.

For the forward implication, three selected edges incident at one seed vertex
would form a triangle in the line graph.  With maximum degree at most two,
every nontrivial component is a path or a cycle; an odd seed cycle has the
same odd cycle as its line graph.  Conversely, the line graph of a disjoint
union of paths and even cycles is a disjoint union of paths and even cycles,
and is bipartite.

Therefore the invariant has the exact seed-domain formula

```text
b(L(G)) = max { |F| : Delta(V(G),F) <= 2
                      and every cycle of (V(G),F) is even }.
```

This is the even-linear edge rank used by the independent audit.  It explains
why the second verifier could optimize over seed edges rather than induced
line-graph vertices.

### Metric coordinate

For distinct seed edges `e` and `f` in one connected component,

```text
dist_L(G)(e,f) = 1 + min { dist_G(x,y) : x in e, y in f }.
```

Indeed, an edge-incidence walk of length `k` from `e` to `f` supplies an
endpoint path of length `k-1` in `G`; conversely, a shortest endpoint path,
with `e` and `f` appended, supplies an incidence walk one edge longer.  Thus
average eccentricity of the line graph is genuinely an edge metric of the
seed and is not definitionally determined by the even-linear rank.

## Obstruction exposed by the five walls

The local term cannot be increased inside the line-graph class: it is already
at its universal ceiling two.  Consequently a strict WOWII 19 crossing in
this class must satisfy

```text
maximum even-linear seed-edge rank
  < floor(average edge eccentricity + 2).
```

A useful next operation would therefore have to raise the floor of average
edge eccentricity without increasing the even-linear rank by the same integer
amount.  The five walls do not select one such operation.  Subdivision,
attachment, deletion, and covering transformations affect different seed
edge sets and would constitute a menu rather than one analytically compelled
move.

The protocol-valid continuation is therefore this coordinate theorem, not a
new computational trial.  In particular, the ten unresolved rows from the
preceding trial were not revisited through a new cap or solver formulation.
No database run, candidate evaluation, commit, release, or public action was
performed.
