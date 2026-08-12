# Method v0.3 Lane P2: WOWII 133 cubic C4-free proof extraction

Status: **PROVED corrected cubic specialization / stronger shadow open**

Date: **2026-08-12 UTC**

Frozen inputs only: the six exact lift representatives and the first saved
minimum-residual representative at each completed cubic order
`10,12,14,16,18,20` from
`method_v02_133_search.jsonl`.  No graph was generated, no order-22/24 row was
used, and no Hoffman--Singleton optimization was run.

## Result

The frozen Lane P2 reduction contains a missing hypothesis.  A cubic C4-free
graph need not have independent open neighborhoods: C4-freeness does not
exclude triangles.  Consequently the sentence

```text
every connected cubic C4-free graph has
path(G) >= radius(G) + 3
```

is stronger than the cubic specialization of WOWII 133, not an equivalent
restatement of it.

The proof extraction nevertheless closes the **actual cubic C4-free branch**
of WOWII 133:

> **Theorem.** Let `G` be a finite connected simple cubic graph containing no
> (not necessarily induced) four-cycle.  If `l(G)` is the average independence
> number of the open neighborhoods, then
> `path(G) >= radius(G) + floor(l(G))`.

More precisely:

1. if `G` is triangle-free, then `path(G) >= radius(G) + 3`;
2. if `G` contains a triangle, then `floor(l(G)) = 2` and
   `path(G) >= radius(G) + 2`.

Thus the requested `radius+3` shadow is proved for the triangle-free stratum.
It remains unproved here for triangle-containing cubic C4-free graphs.  This is
not a proof of full WOWII 133, whose remaining C4-free noncubic branch is not
addressed.

Throughout, a C4 is a subgraph, so extra chords do not invalidate a displayed
four-cycle.

## Lemma 1: the radius is at least two

Let `c` be a center and write `r = radius(G)`.  A cubic connected graph cannot
have `r=0`.  If `r=1`, then `c` is adjacent to every other vertex, so cubicity
gives `|V(G)|=4`.  A simple cubic graph on four vertices is `K4`, which contains
a C4.  Therefore `r >= 2`.

## Lemma 2: one extra vertex in every cubic C4-free graph

Choose a peripheral vertex and a center--periphery geodesic

```text
P = c=v0, v1, v2, ..., vr.
```

Let `a,b` be the two neighbors of `c` other than `v1`.  They cannot both be
adjacent to `v1`, since then

```text
c-a-v1-b-c
```

is a C4.  Choose `a` not adjacent to `v1`.

The vertex `a` is not adjacent to `v2`, since
`c-a-v2-v1-c` would be a C4.  It is not adjacent to any `vi` for `i>=3`, since
`c-a-vi` would be a path of length two to a vertex whose distance from `c` is
`i`.  Hence

```text
a, c=v0, v1, ..., vr
```

is an induced path of order `r+2`.  The only possible extra chord involving
`a` has just been excluded, and a geodesic is induced.

This proves `path(G) >= radius(G)+2` without assuming triangle-freeness.

## Lemma 3: exact local-independence split

For every vertex `v`, its open neighborhood has three vertices.  It contains
at most one edge.  Indeed, two neighborhood edges may be named `xy` and `xz`,
and then

```text
y-x-z-v-y
```

is a C4.  Therefore

```text
alpha(G[N(v)]) = 3  if v lies in no triangle,
alpha(G[N(v)]) = 2  if v lies in a triangle.
```

If `G` is triangle-free, every summand in `l(G)` is three and `l(G)=3`.  If
`G` has a triangle, every summand lies in `{2,3}` and at least one is two, so
`2 <= l(G) < 3` and `floor(l(G))=2`.

This is the correction to the frozen sentence that C4-free cubic graphs have
independent open neighborhoods.

## Lemma 4: two extra vertices in the triangle-free stratum

Assume now that `G` is triangle-free and retain the geodesic `P` above.  Let
`a,b` again be the two neighbors of `c` off `P`.  Triangle-freeness shows that
neither is adjacent to `v1` and that `a` and `b` are nonadjacent.

Each of `a,b` has two neighbors other than `c`; call the resulting four-vertex
set `X`.  Its four members are distinct.  A common forward neighbor of `a`
and `b` would give the C4

```text
c-a-x-b-c.
```

No member `x` of `X` lies on `P`.  Moreover, its only possible contacts with
`P` are `v2` and, when it exists, `v3`:

- `xc` would form a triangle with the branch edge `ca` (or `cb`);
- `xv1` would give the C4 `c-a-x-v1-c` (or the analogous cycle through `b`);
- `xvi` for `i>=4` would give a path of length three from `c` to `vi`, shorter
  than the geodesic distance `i`.

There are fewer available contact edges at `v2,v3` than there are members of
`X`:

| radius | free incident edges at the possible contact vertices |
|---:|---:|
| `r=2` | two at the endpoint `v2` |
| `r=3` | one at internal `v2`, two at endpoint `v3` |
| `r>=4` | one each at internal `v2` and `v3` |

Thus at most three of the four distinct members of `X` contact `P`.  Choose a
member `x` with no contact, and let `a` be its neighbor in `{a,b}`.  Lemma 2's
argument also shows that `a` has no contact with `P` except `c`.  Consequently

```text
x, a, c=v0, v1, ..., vr
```

is an induced path of order `r+3`.  This proves the stronger shadow throughout
the triangle-free cubic C4-free stratum.

## Cubic specialization of the source theorem

If `G` is triangle-free, Lemmas 3 and 4 give

```text
path(G) >= radius(G)+3 = radius(G)+floor(l(G)).
```

If `G` contains a triangle, Lemmas 2 and 3 give

```text
path(G) >= radius(G)+2 = radius(G)+floor(l(G)).
```

This proves the actual WOWII 133 inequality for all connected cubic C4-free
graphs.  The already-recorded diameter-geodesic argument handles the
C4-present branch, but noncubic C4-free graphs remain outside this result.

## Refuted intermediate lemmas

The fixed records reject two tempting shortcuts.

1. **False:** a forward neighbor at distance two from `c` can contact only
   `v2`.  In saved representative `2lift:Petersen:0`, the center--periphery
   geodesic `[4,2,12,18,15,5]` has off-geodesic branch vertex `6` and forward
   vertex `8`, with `8` adjacent to `v3=18`.  A distance-three contact does not
   shorten the geodesic.
2. **False:** every forward neighbor avoids `v2` and `v3`, so either child can
   be prepended.  The fixed-data checker finds a contact on 1,500 of the 1,628
   applicable center--periphery geodesics.  The first is in
   `2lift:Petersen:0` on `[0,8,18,15,11,1]`; branch `2` has forward vertex `12`
   adjacent to `v2=18`.  The correct proof chooses among all four forward
   vertices and uses degree capacity.

The stronger statement for triangle-containing graphs was neither proved nor
refuted by the frozen data.  All eleven cubic representatives in the fixed
12-row check are triangle-free; `2lift:C5:0` is also triangle-free but is a
degree-two control, so the cubic lemmas are inapplicable to it.  It still has
the saved exact inequality `path=9 >= radius+3=8`.

## Fixed-data audit

Run:

```text
python3 scripts/method_v03_133_lemma_check.py
```

The checker reads no graph source other than the frozen v0.2 ledger.  It
checks connectedness, cubicity where applicable, C4-freeness, saved radius,
and every center--periphery geodesic.  Results:

| fixed representative | radius | applicable geodesics | direct two-extension |
|---|---:|---:|---:|
| `2lift:C5:0` | 5 | N/A (degree two) | exact target holds (`9>=8`) |
| `2lift:Petersen:0` | 5 | 160 | 160 |
| `2lift:Petersen:1` | 5 | 120 | 120 |
| `2lift:Petersen:2` | 5 | 176 | 176 |
| `2lift:Petersen:3` | 5 | 120 | 120 |
| `2lift:Petersen:4` | 5 | 240 | 240 |
| `cubic-c4free-10:0` | 2 | 60 | 60 |
| `cubic-c4free-12:0` | 3 | 64 | 64 |
| `cubic-c4free-14:0` | 3 | 168 | 168 |
| `cubic-c4free-16:139` | 4 | 64 | 64 |
| `cubic-c4free-18:1` | 4 | 216 | 216 |
| `cubic-c4free-20:3` | 5 | 240 | 240 |

Total: all **1,628** applicable geodesics have the constructive two-vertex
extension promised by Lemma 4.  This computation is a countermodel guard for
the intermediate lemmas, not evidence substituted for their proof.

## Scope boundary

This result is a genuine partial theorem for WOWII 133: it proves its cubic
C4-free specialization (and the stronger `radius+3` form when triangle-free).
It does **not** prove full WOWII 133, does not settle the stronger
triangle-containing `radius+3` shadow, and does not justify any upstream status
change.
