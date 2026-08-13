# WOWII 40 prospective shared-endpoint internal-star trial

## Strongest result

`HOLD_BOUNDED`: every one of the 27 frozen graphs has exact slack one.

The shared-endpoint `P3` surgery and its preregistered `K_(1,3)` and `K_(1,4)`
companions all have the same exact coordinates:

```text
f=c,  b=c+1,  p=c-4.
```

Thus adding a second internal edge to the newly discovered one-edge wall moves
strictly inward by one unit. Extra arms through the same center do not change
any of the three invariants in the frozen range.

## Protocol

Before any computation, the trial froze exactly one orbit family:

- start with `K_(2,c)`;
- add an internal star `K_(1,r)` in the `c`-vertex side;
- use `c=7,...,15` and only `r=2,3,4`;
- evaluate all 27 graphs, with no deletion or second-stage surgery.

The contract preregistered the coordinate predictions and the full crossing
criterion. The standard 1,031-graph exact #40 sanity gate then passed before
any development graph was evaluated. Nine `r=1` starting walls were also
reverified exactly.

## Exact computation

| internal arms `r` | graphs | exact `(f,b,p)` | slack |
|---:|---:|---|---:|
| 2 (`P3`) | 9 | `(c,c+1,c-4)` | 1 |
| 3 | 9 | `(c,c+1,c-4)` | 1 |
| 4 | 9 | `(c,c+1,c-4)` | 1 |

There were zero crossings, zero timeouts, and zero prediction mismatches.

## Independent certificates

All `c` remainder vertices induce a star plus isolated vertices, so `f>=c`.
If one hub is retained, every internal star edge forms a triangle, requiring a
vertex cover of the star; retaining both hubs additionally makes every pair of
remainder vertices a four-cycle. These cases give `f<=c`.

Deleting the internal-star center leaves both hubs and `c-1` remainder
vertices, an induced `K_(2,c-1)` of order `c+1`. Conversely, retaining a hub
requires hitting every star-edge triangle, while deleting both hubs retains
only `c` vertices. Hence `b=c+1`.

For `p`, use the equivalent maximum spanning linear-forest formulation. Any
linear forest contains at most two internal star edges because the common
center has degree at most two. It contains at most four hub-incidence edges
because each of the two hubs also has degree at most two. These edge sets
exhaust the graph, so every spanning linear forest has at most six edges. The
emitted path-cover witnesses attain six edges, proving

```text
p=n-6=(c+2)-6=c-4.
```

All emitted witnesses and these independent bounds were replayed for all 27
graphs. The append-only stream has SHA-256
`2ccb5cf3f482be6fd44e65c96a506016df56385bf6afe3d405befeefcfe586d5`.

## Interpretation

The one-edge internal wall is isolated in this orbit direction. One additional
edge sharing its endpoint leaves `f` and `b` fixed but improves the spanning
linear forest by one edge, lowering `p` from `c-3` to `c-4`. Further arms are
absorbed by the same degree-two bottleneck and do not restore equality or
create a crossing.

No alternate surgery was attempted. No commit, release, push, issue, PR, or
public post was made.
