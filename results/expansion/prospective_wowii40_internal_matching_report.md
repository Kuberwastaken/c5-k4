# WOWII 40 prospective internal-matching orbit surgery

## Outcome

`HOLD_BOUNDED`.

The frozen matching surgery lowered the induced-forest coordinate as intended,
but the exact bipartite and path-cover coordinates moved with it. Ten graphs
remained exactly tight; the other nineteen moved to positive slack. There were
no crossings, timeouts, or adaptive follow-up surgeries.

## Frozen mechanism

Starting from the exact `K_(2,c)` wall, the only allowed operation added a
size-`k` matching inside the `c`-vertex side. The frozen range was
`c=6,...,15` and `k=1,2,3`. Since all matchings of a fixed size lie in one
automorphism orbit of `K_(2,c)`, this gives one canonical graph per pair.

The pair `(c,k)=(6,3)` was preregistered as a structural rejection: deleting
the hubs leaves only three components, certifying merely `p>=1`. The remaining
29 graphs all retain the required `p>=2` bottleneck.

No edge deletion, second matching system, or retuned parameter was considered.

## Gates and exact results

The standard exact 1,031-graph #40 sanity gate passed before development. The
ten unsurgered wall graphs were then reverified with coordinates

```text
(n,f,b,p)=(c+2,c+1,c+2,c-2).
```

The 29 admissible surgeries produced:

| matching size | graphs | exact `(f,b,p)` | slack |
|---:|---:|---|---:|
| 1 | 10 | `(c,c+1,c-3)` | 0 |
| 2 | 10 | `(c,c,c-4)` | 1 |
| 3 | 9 | `(c,c,c-5)` | 2 |

Every preregistered coordinate formula was confirmed exactly.

## Independent certificates

After deleting the hubs `X,Y`, the remainder consists of `k` matching edges
and `c-2k` isolated vertices: `c-k` components total. The standard separator
count gives `p>=c-k-2`. Every emitted exact path cover has that many paths,
proving equality.

All `c` remainder vertices induce a forest, so `f>=c`. If a hub is retained,
both endpoints of a matching edge form a triangle with it, limiting the
remainder contribution to `c-k`; if both hubs are retained, any two remainder
vertices form a four-cycle. Thus `f<=c`.

For `b`, deleting both hubs keeps all `c` remainder vertices. Retaining both
hubs requires deleting at least one endpoint of each internal matching edge,
giving at most `c-k+2`; retaining one hub gives at most `c-k+1`. Therefore

```text
b=max(c,c-k+2).
```

These arguments and every emitted forest, bipartite, path-cover, and separator
witness were replayed independently for all 29 graphs. The append-only record
stream has SHA-256
`8c144f5547bf1d754dd40b635c72983f109b0c6a3415325fe25a06a571951291`.

## Interpretation

A single internal edge performs the desired forest suppression but preserves
the exact #40 wall. Further disjoint internal edges reduce the minimum path
cover and maximum induced-bipartite order enough to create safety rather than
a violation. This matching orbit is therefore closed: it supplies another
sharp equality mechanism, not a counterexample direction.

No commit, push, release, issue, PR, or public action was taken.
