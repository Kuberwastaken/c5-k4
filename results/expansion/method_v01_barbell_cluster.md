# Method v0.1 development trial: WOWII 169/174/180/182 barbell neighborhood

**Frozen before construction evaluation:** 2026-08-12
**Method:** [`METHOD.md`](../../METHOD.md), commit
`75852aa4182c950efa7f8c9305f57d0c1cb2534a`
**Unit:** one correlated development-set cluster, not four independent trials

This report is intentionally incremental.  The source freeze, readings, search
bounds, and directional predictions below were written before evaluating any
new edge surgery or endpoint-clique substitution.

## Phase 0: source and status freeze

The authoritative local transcription is
[`data/wowii-conjectures.json`](../../data/wowii-conjectures.json), introduced
at commit `2455820ef9b925c0746cfb72561bca61105b1aa2` from DeLaViña's live WOWII
site and its recovered invariant definitions.  The upstream
`formal-conjectures` baseline checked for this trial is
`e751934294a381afd2d5fc1124c5953c8e25f9fa` (`origin/main`).  None of these
four statements currently has a Lean declaration there.  Exact GitHub searches
for `WOWII N` and `GraphConjectureN` found no matching issue or pull request;
numeric-only matches were unrelated repository issues/PRs.

The frozen statements are:

| id | residual convention `R=LHS-RHS` | pre-search status |
|---|---|---|
| 169 | `Ls - (1 + max_v dist_even(v) - min_v dist_even(v))` | source says open |
| 174 | `Ls+b - (n + lambda_max - 1)` | already false: live-page audit records the July 23, 2026 Apple Lamps order-11 counterexample |
| 180 | `Ls+b - (1 + alpha + max_v dist_even(v))` | source says open |
| 182 | `Ls+b - (Delta(B(G^2)) + diam(G))` | source says open |

Consequently, a 174 violation in this run can be only a
`RETRO_COUNTEREXAMPLE`.  No result below will be called novel without a later,
separate novelty audit.

### Frozen readings

- `dist_even(v)` is the number of vertices at even finite distance from `v`.
  The recovered definition counts `v` itself (distance zero).  For 169 the
  include/exclude-self convention cancels from the range.  For 180 both
  include-self and exclude-self readings are retained.
- `lambda(v)=alpha(G[N(v)])`; 174 uses its maximum over vertices.
- `B(H)` is the periphery of `H`.  The primary 182 reading selects
  `B(G^2)` and measures the selected vertices' degrees in `G^2`.  The alternate
  reading measures those degrees back in `G`.  Both are retained.
- `Ls` is computed exactly as `n-gamma_c` for connected graphs of order at
  least three (with the order-two spanning-tree case handled directly), and
  `b` is the maximum order of an induced bipartite subgraph.

Classification before search: 169 and 174 are `UNAMBIGUOUS`; 180 and 182 are
`MULTI_READING`.

## Phase 3: theorem-baseline subtraction

Let

```text
T173(G) = Ls(G)+b(G) - (n+1+chi_bipartite(G)).
```

Proved WOWII 173 gives `T173>=0`.  For the three `Ls+b` targets:

```text
R174      = T173 + 2 + chi_bipartite - lambda_max
R180,self = T173 + n + chi_bipartite - alpha - even_max,self
R182,H    = T173 + n + 1 + chi_bipartite - Delta_H(B(G^2)) - diam(G),
```

where `H` is `G^2` or `G`.  This decomposition will be recorded for every
tested graph.  It prevents a failure of the known baseline from being mistaken
for freedom in a correction term.

## Phase 4/5: frozen obstruction and directional predictions

The base family `D_L` is two triangles whose distinguished vertices are joined
by an `L`-edge path.  The earlier 176/172 work established that subdivision
raises metric separation while preserving a small maximum-leaf structure.
This trial asks whether bounded local surgery can move the adjacent residuals.

Predictions written before evaluation:

| target | obstruction on the base family | predicted useful move | term directions |
|---|---|---|---|
| 169 | the two ends are symmetric, pinning the even-distance range | asymmetric deletion | `Ls`: decrease/pinned; parity range: increase; `R`: decrease |
| 174 | endpoint-clique barbells have `lambda_max` locally capped while 173 supplies a nonnegative baseline | delete/add at most two edges to create a larger independent neighborhood without greatly raising `T173` | `lambda_max`: increase; `T173`: pinned/unknown; `R`: decrease |
| 180 | end symmetry couples `alpha` to the largest even-distance layer | asymmetric deletion or unequal endpoint cliques | `alpha`: nondecrease under deletion; `even_max`: increase/unknown; `T173`: pinned/unknown; `R`: decrease |
| 182 | diameter growth competes with loss of square-degree at the square periphery | deletion near one end, or unequal endpoint cliques | `diam`: increase; square-periphery degree: decrease/unknown; `T173`: pinned/unknown; net `R`: genuinely uncertain |

Edge additions are retained as a negative/control direction: `Ls` can only
increase and distances tend to contract, although changes in shortest-path
parity and square-periphery membership make the final residual nonmonotone.
Uniformly enlarging endpoint cliques is predicted mainly to test pinning rather
than to cross a wall.

## Phase 6: declared bounds

No bounds will be expanded after seeing results in this trial.

1. Bases: even `D_6`, `D_8`, and `D_10`.
2. Edge surgery: every automorphism-orbit representative at graph-edge
   symmetric-difference distance one or two from each base.  This includes
   additions, deletions, and one-add/one-delete combinations.  Disconnected
   outcomes are `NOT_APPLICABLE`.
3. Endpoint-clique substitution: `K_a` and `K_b` with
   `2 <= a <= b <= 5`, joined at distinguished vertices by a path.  The
   smallest fixed path grid sufficient to contain the three base scales is
   `L in {2,3,...,10}`.
4. Every exact optimization call has a 60-second wall-clock cap.  A timeout is
   a `TIMEOUT_BRACKET`, never a guessed value.
5. Controls: all connected Graph Atlas graphs of orders 2--7, `C5`--`C9`,
   `P7`, Petersen, `K3,3`, `K7`, stars `K1,r` for `2<=r<=8`, and complete
   bipartite graphs `K_a,b` for `1<=a<=b<=5`.

The exact discovery implementation is
[`search_method_v01_barbell.py`](../../scripts/search_method_v01_barbell.py).

## Incremental execution ledger

### Database-sanity gate — PASS

The exact gate checked **1,013 control encodings after exact graph6 dedup**
(995 connected Atlas graphs of orders 2--7 plus the retained named controls).
Every frozen reading held.  Minimum residuals and equality counts were:

| reading | minimum residual | equality controls |
|---|---:|---:|
| 169 | 0 | 92 |
| 174 | 0 | 29 |
| 180, self included | 0 | 135 |
| 180, self excluded | 1 | 0 |
| 182, degrees in `G^2` | 0 | 31 |
| 182, degrees back in `G` | 1 | 0 |

Runtime was 0.60 seconds.  The primary readings being exactly tight on many
historical controls makes this a meaningful sanity check rather than a vacuous
pass.  Construction evaluation may now begin without changing the readings.

### Endpoint-clique grid — 90/90 profiles completed

All `9 path lengths x 10 unordered endpoint pairs` completed with no timeout
and no violation under any reading.

| reading | minimum | exact equalities |
|---|---:|---:|
| 169 | 0 | 50 |
| 174 | 1 | 0 |
| 180, self included | 0 | 50 |
| 180, self excluded | 1 | 0 |
| 182, degrees in `G^2` | 0 | 20 |
| 182, degrees back in `G` | 1 | 0 |

The full grid exposes closed forms.  For `2<=a<=b<=5`, let
`K_a-P_L-K_b` mean that the endpoint cliques share the distinguished endpoints
of an `L`-edge path.  Exact enumeration gives

```text
n=L+a+b-1, gamma_c=L+1, Ls=a+b-2,
b=L+3, alpha=floor(L/2)+2, lambda_max=2, diam=L+2.
```

For every member of the declared grid:

```text
R174 = 1
R169 = R180,self = 0                 if L is even
                   = a-1             if L is odd
R180,without-self = R180,self + 1
R182,square       = a-2              if L is even
                   = a-1              if L is odd
R182,back-in-G    = R182,square + 1.
```

Thus unequal endpoint cliques do not supply the predicted separation: on even
paths they preserve the 169/180 wall exactly, and the left endpoint order alone
controls the primary 182 slack.  The entire `lambda_max<=2` slice of 174 is
also theorem-shadowed by 173: for nonbipartite graphs
`R174=T173+2-lambda_max>=0`; this family stays one unit safe.

### Edit-orbit runs — 2,652/2,652 connected profiles completed

Automorphism reduction was performed relative to each unedited base.  Counts
include every orbit representative at symmetric-difference distance one or
two; disconnected representatives were retained in the ledger as
`NOT_APPLICABLE`.

| base | orbit representatives | connected profiles | disconnected | timeouts | violations |
|---|---:|---:|---:|---:|---:|
| `D6` | 421 | 360 | 61 | 0 | 0 |
| `D8` | 903 | 781 | 122 | 0 | 0 |
| `D10` | 1,728 | 1,511 | 217 | 0 | 0 |
| **total** | **3,052** | **2,652** | **400** | **0** | **0** |

Every connected profile held all six frozen readings.  Across each of the
three bases, the minimum vector was identical:

```text
(R169, R174, R180,self, R180,without-self, R182,square, R182,back-in-G)
= (0, 0, 0, 1, 0, 1).
```

The primary-reading equality counts, showing that the search repeatedly
reached but did not cross the walls, were:

| base | 169 | 174 | 180 | 182 |
|---|---:|---:|---:|---:|
| `D6` | 21 | 8 | 33 | 4 |
| `D8` | 31 | 13 | 45 | 4 |
| `D10` | 42 | 18 | 69 | 4 |

The preregistered directional prediction was only partly borne out.  Deletions
and mixed edits did increase parity ranges or `lambda_max` in some profiles,
but the 173 baseline and the other terms moved enough to absorb the gain.
For example, surgery can raise `lambda_max` to three or four while producing
only `R174=0`, not a crossing.  The alternate 180 and 182 readings remained
uniformly at least one unit safer than their primary counterparts.

## Validation

[`verify_method_v01_barbell.py`](../../scripts/verify_method_v01_barbell.py)
uses independent NetworkX induced-subgraph enumeration and `nx.power` rather
than the discovery program's bit masks and custom square.  It compares every
invariant on all 995 connected Atlas graphs of orders 2--7, checks graph6
round-trips, and verifies the displayed closed forms on all 90 endpoint-grid
members.  There were no apparent hits, so the candidate-only independent
recomputation/graph6 obligation was not triggered.

## Outcome ledger and method update

| target | outcome of this declared trial | interpretation |
|---|---|---|
| 169 | `HOLD_BOUNDED` | 90 endpoint members and 2,652 connected edit representatives hold; many exact walls |
| 174 | `HOLD_BOUNDED`; external target already false | theorem-shadowed on the endpoint family; surgery reaches equality only |
| 180 | `HOLD_BOUNDED` | primary reading repeatedly exact; alternate reading uniformly safer |
| 182 | `HOLD_BOUNDED` | primary reading has a thin equality locus; alternate reading uniformly safer |

This is one cluster-level zero, not four failed independent trials and not
evidence that any conjecture is true.  The learned transformation update is:

1. Endpoint clique order is a **pinning/calibration coordinate** for this
   cluster, not a useful separating coordinate: its residual effects have the
   closed forms above.
2. Two local edge toggles can reach all four primary walls but did not cross
   any.  A future development iteration must change a quotient-level feature
   or introduce a third invariant-controlling operation; silently expanding
   this run beyond two toggles would invalidate its declared bound.
3. Source-convention robustness is asymmetric: the primary readings are the
   sharp ones, while the plausible alternate readings carry a one-unit buffer
   throughout every tested family.

These updates were learned **after** the frozen run and therefore may inform a
later Method v0.2 development trial, but not this one.
