# Frozen prospective trial: internal-side matching surgery on the `K_(2,c)` wall

Frozen: 2026-08-13 UTC, before database or development evaluation.

## Starting wall and coordinate analysis

The completed two-hub fusion trial produced the exact equality family
`K_(2,c)` with

```text
n=c+2,  f=c+1,  b=c+2,  p=c-2
```

for `c>=4`. This trial applies one orbit-surgery mechanism only: add a matching
inside the size-`c` color class. There is no edge deletion, second-stage
mutation, retuning, or post-result family extension.

## Frozen orbit surgery

Label the two degree-`c` hubs `X,Y` and the other vertices
`z_0,...,z_(c-1)`. For matching size `k`, add exactly

```text
z_0--z_1, z_2--z_3, ..., z_(2k-2)--z_(2k-1).
```

All size-`k` matchings form one orbit under the `S_c` action on the remainder
side, so this is canonical up to isomorphism.

Frozen parameters:

```text
c in {6,7,...,15},   k in {1,2,3}.
```

Thus there are exactly 30 raw/distinct graphs, orders 8 through 17. No other
matching size or edge system may be tried.

This differs from the generation trial: it does not fuse equality seeds or
alter the separator. It performs a bounded internal-side orbit addition on an
already-generated wall graph. It also differs from bouquets, rings, all-pairs
cross edges, and critical cloning.

## Preregistered formulas and unknowns

Removing `{X,Y}` leaves `c-k` components: `k` edges and `c-2k` isolated
vertices. The separator count certifies

```text
p >= c-k-2 >= 1.
```

For the frozen range, `p>=2` except the nonexistent endpoint `c=6,k>2`; the
actual frozen minimum is `c-k-2=1` at `(6,3)`. To satisfy the trial's required
path bottleneck, `(6,3)` is preregistered as a structural rejection before
invariant evaluation. Every evaluated pair has `c-k-2>=2`.

The explicit cover using one path through three components and one path for
every other component predicts `p=c-k-2`.

The whole remainder side induces a matching plus isolates, hence is a forest
of order `c`. Any induced forest retaining a hub can use at most one endpoint
of each matching edge; both hubs additionally make every pair of remainder
vertices a four-cycle. The frozen prediction is `f=c`.

For the largest induced bipartite order, two competing witnesses are known:

- delete both hubs and retain all `c` remainder vertices;
- retain both hubs and delete one endpoint of every matching edge, giving
  order `c-k+2`.

Thus the prediction is

```text
b = max(c,c-k+2),
```

but this remains an exact-computation target rather than an assumed value.
Under all three predicted identities, `k=1` stays tight and `k>=2` moves to
positive slack. A different result in any coordinate is the only prospective
route to a crossing.

## Gate, exactness, and classification

- Rerun the standard exact 1,031-graph #40 database gate first.
- Reverify the unsurgered `K_(2,c)` inputs exactly.
- Evaluate the 29 admissible preregistered pairs after rejecting `(6,3)` by its
  separator certificate.
- Emit exact maximum induced-forest, maximum induced-bipartite, and minimum
  path-cover witnesses plus the separator components.
- Independently replay witnesses and the closed-form upper/lower certificates.
- Cap every solve and process at 60 seconds. Timeout is `INCONCLUSIVE`.
- Outcomes: `DB_SANITY_REJECT`, `CANDIDATE`, `HOLD_BOUNDED`, `INCONCLUSIVE`.

No adaptive second surgery, commit, push, release, issue, PR, or public action
is authorized.
