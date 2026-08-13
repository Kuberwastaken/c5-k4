# Frozen prospective addendum: two-hub cut-bottleneck fusion for WOWII 40

Frozen: 2026-08-13 UTC, before database or development evaluation.

## Exact obstruction being targeted

The rooted bouquet trial preserved path-cover fragmentation but let petal
forests coexist. The cross-petal ring trial made their forests incompatible,
but every output became Hamiltonian. This trial freezes a two-vertex separator
that enforces both effects simultaneously:

- deleting the two hubs exposes many components, certifying `pathCover >= 2`;
- every edge respects one fixed bipartition, so `b=n` exactly;
- vertices originating in different petals lie on new four-cycles through the
  shared hubs, preventing all petal forest witnesses from coexisting.

## Frozen exact equality seeds

Use only these two already-exact bipartite equality seeds:

| seed | graph6 | structure | `(n,f,b,p)` |
|---|---|---|---|
| `c4_wall` | `C]` | `K_(2,2)` | `(4,3,4,1)` |
| `k23_wall` | `Ds[` | `K_(2,3)` | `(5,4,5,1)` |

The evaluator must independently reverify these coordinates before fusion.
In each seed, choose the size-two color class canonically by lexicographically
least sorted vertex pair among valid bipartitions; call its vertices `x,y`.

## Frozen fusion and edge system

For every pair `(a,b)` of nonnegative integers with

```text
2 <= a+b <= 5,
```

take `a` disjoint copies of `c4_wall` and `b` disjoint copies of `k23_wall`,
then identify every copy's `x` vertices into one hub `X` and every copy's `y`
vertices into another hub `Y`. No edge `XY` and no other edge is added.

Equivalently, if the petal remainders contain

```text
c = 2a + 3b
```

vertices, the output is `K_(2,c)`. The construction is retained through its
seed-fusion provenance rather than inserted as a named control.

This is not a rooted one-hub bouquet, a ring or all-pairs cross-edge system, a
path-shaped block tree, an edge mutation, or a one-vertex critical clone ray.
It simultaneously identifies a separator pair across complete equality
seeds. The resulting four-cycles cross seed boundaries through both hubs.

## Frozen certificates and prediction

Removing `{X,Y}` leaves exactly `c` isolated components. A vertex-disjoint path
cover can use `X,Y` to meet at most three of them, hence

```text
pathCover >= c-2 >= 2.
```

The explicit cover `z1-X-z2-Y-z3` plus `c-3` singleton paths proves equality
`p=c-2`. All vertices form a bipartite witness, so `b=n=c+2`. Every induced
forest contains at most one hub together with all `c` remainder vertices, or
both hubs with at most one remainder vertex; therefore `f=c+1`.

The frozen prediction is exact equality:

```text
ceil((p+b+1)/2) = ceil(((c-2)+(c+2)+1)/2) = c+1 = f.
```

The computational trial must verify rather than assume these identities.

## Gate, bounds, and outcomes

- Rerun the standard exact 1,031-graph #40 database gate before fusion.
- Evaluate all 18 frozen parameter pairs, canonically deduplicating isomorphic
  outputs; orders are 6 through 17.
- Exact maximum induced forest, maximum induced bipartite order, and minimum
  path cover must include explicit witnesses.
- Directly replay the two-hub component-count lower-bound certificate.
- Every solve and process is capped at 60 seconds; timeout is `INCONCLUSIVE`.
- Outcomes are `DB_SANITY_REJECT`, `CANDIDATE`, `HOLD_BOUNDED`, or
  `INCONCLUSIVE`.

No retuning, commit, push, release, issue, PR, or public action is authorized.
