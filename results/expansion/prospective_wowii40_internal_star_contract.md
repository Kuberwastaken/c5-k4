# Frozen prospective trial: shared-endpoint internal stars on the WOWII 40 wall

Frozen: 2026-08-13 UTC, before any computation in this trial.

## New starting point

The completed internal-matching trial discovered a new exact wall: adding one
edge inside the `c`-vertex side of `K_(2,c)` gives

```text
(n,f,b,p) = (c+2,c,c+1,c-3),
```

and remains tight for WOWII 40. This is the starting object, but this document
defines a new frozen trial rather than adaptively extending the old run.

## Single frozen orbit-surgery family

Let `X,Y` be the two degree-`c` hubs and `z_0,...,z_(c-1)` the remainder
vertices. Add an internal star with center `z_0` and exactly `r` arms:

```text
z_0--z_1, z_0--z_2, ..., z_0--z_r.
```

The case `r=2` is the requested two-edge `P3` surgery. The same preregistered
bounded menu includes only `r=3,4`; no other internal graph, deletion, or
follow-up mutation is allowed.

Frozen parameters:

```text
c in {7,8,...,15},   r in {2,3,4}.
```

All size-`r` internal stars lie in one orbit under the remainder-side `S_c`
action. Hence there are exactly 27 canonical graphs, orders 9 through 17.
The lower endpoint `c=7` leaves at least two vertices outside the largest
frozen star and supports the explicit path constructions below.

This is distinct from the generation trial (two-hub fusion), the disjoint
internal matching orbit, one-hub bouquets, cross-petal rings/all-pairs edges,
and critical cloning. Its defining feature is two or more internal edges with
one shared endpoint.

## Preregistered coordinate movement

Deleting `{X,Y}` leaves one `K_(1,r)` component and `c-r-1` isolated
components, for `c-r` components total. This certifies

```text
p >= c-r-2,
```

but that component bound need not be sharp because a path can use the hubs to
enter different arms of the same star. The stronger frozen prediction is

```text
p = c-4
```

for every `r=2,3,4`: a spanning linear forest can absorb the star center, two
arms, both hubs, and appropriate outside vertices, while the remaining degree
constraints force `c-4` paths. The exact solver and an independent certificate
must decide this; it is not assumed.

All `c` remainder vertices induce a star plus isolates, giving a forest of
order `c`. Retaining a hub makes every internal star edge a triangle, while
retaining both hubs makes every pair of remainder vertices a four-cycle. The
frozen prediction is

```text
f = c.
```

For bipartite order, deleting the star center retains both hubs and all other
remainder vertices, giving order `c+1`. The predicted exact value is

```text
b = c+1.
```

Thus the predicted coordinate change from the one-edge wall is

```text
Delta f=0, Delta b=0, Delta p=-1,
```

and predicted slack is one.

## Crossing criterion fixed before solving

For every frozen graph, a strict crossing is exactly

```text
f < ceil((p+b+1)/2).
```

Under the predicted `f=c,b=c+1`, this requires `p>=c-1`. Since adding edges
cannot increase minimum path-cover number above the starting `K_(2,c)` value
`c-2`, the preregistered formulas predict no crossing. A candidate can arise
only if exact computation falsifies the forest or bipartite predictions in the
direction needed by the full inequality. No alternate surgery will be tried.

## Gate, exactness, and strict outcomes

1. Rerun the exact 1,031-graph #40 database gate before development.
2. Reverify the `r=1` starting wall for every `c=7,...,15`.
3. Evaluate all 27 frozen graphs with exact forest, bipartite, and path-cover
   witnesses and incremental JSONL writes.
4. Independently replay separator, forest, bipartite, and path-cover
   certificates.
5. Cap every solve and process at 60 seconds.

Strict outcome taxonomy:

- `DB_SANITY_REJECT`: the reading fails the control gate;
- `CANDIDATE`: a strict crossing survives independent recomputation;
- `HOLD_BOUNDED`: all exact results are noncrossing;
- `INCONCLUSIVE`: any potentially crossing exact solve times out.

No commit, release, push, issue, PR, or public post is authorized.
