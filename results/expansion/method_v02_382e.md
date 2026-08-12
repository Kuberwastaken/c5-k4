# Method v0.2 Trial F: WOWII 382e

Status: **HOLD_BOUNDED**, with a secondary **THEOREM_SIGNAL**

Frozen by [`method_v02_wave2_manifest.md`](method_v02_wave2_manifest.md) before
this trial was evaluated.

## Source and readings

The recovered live WOWII record prints:

```text
If G is a connected graph n > 2 vertices, then gamma_2 <= Maxine + gamma.
```

The record is entry `382e`, remains marked open, and dates the statement to
January 2010.  Its March 2010 note records the theorem
`gamma_2 <= alpha + gamma`, but does not resolve the printed Maxine bound.
The recovered glossary defines Maxine as the order of the largest independent
set obtainable by repeatedly deleting a maximum-degree vertex until the
remaining graph is discrete.

Two readings were frozen before construction:

1. `maxine_best`: maximize the survivor count over every maximum-degree tie
   choice.  This is the source-faithful reading of "largest ... one gets".
2. `maxine_det`: at every tie delete the least-labelled maximum-degree vertex.
   This reproduces the deterministic campaign implementation, but depends on
   the supplied labelling and is therefore not by itself a graph invariant.

The residual convention is

```text
R_best(G) = Maxine_best(G) + gamma(G) - gamma_2(G),
R_det(G)  = Maxine_det(G)  + gamma(G) - gamma_2(G).
```

A crossing requires a negative residual.  The theorem in the source note
gives the necessary obstruction

```text
gamma_2 <= alpha + gamma,
```

so any crossing must have `Maxine < alpha` and must consume enough of that
greedy-independence deficit.

## Database-sanity gate

The prior campaign gate checked both readings on 999 applicable graphs: every
connected Graph Atlas graph on three through seven vertices, plus the named
cycle/path/Petersen/complete-bipartite controls.  Both readings had zero
violations.  Trial F independently replays that exact computation before any
search result is accepted.

## Frozen prediction and bounds

Uniform `C5` clique blow-ups and the two recorded nonuniform variants attain
`4 = 2 + 2`.  Reweighting that same cycle quotient cannot raise `gamma_2`
alone.  The frozen prediction is that a false-twin bundle or a clique
substitution over a non-cycle quotient may force one more two-dominator while
pinning both domination and the Maxine output at two.

The frozen construction bounds are:

- connected quotients through order eight;
- positive false-twin and clique substitutions, total order at most 60;
- structured double-hub, theta, and short-path cores first;
- exact domination and two-domination; 60 seconds per solve;
- immediate stop if a quotient necessary condition prunes all weights.

Results are appended below as each stage completes.

## Gate replay and complete small-graph baseline

The independent gate replay evaluated 1,005 applicable records (the connected
Atlas controls plus the frozen named controls).  It found zero violations on
either reading.  The minimum residual was zero; 60 records were tight for
`maxine_best` and 72 for `maxine_det`.

The complete Brendan McKay connected order-eight catalogue was then evaluated:

| catalogue | graphs | `Maxine_best < alpha` | minimum `R_best` | minimum `R_det` | crossings |
|---|---:|---:|---:|---:|---:|
| connected order 8 | 11,117 | 46 | 0 | 0 | 0 |

Thus a real greedy-independence deficit already occurs at order eight, but it
is not sufficient to cross 382e.  This stage finished in 6.99 seconds.  The
catalogue is McKay's CC-BY-4.0 graph6 file:
<https://users.cecs.anu.edu.au/~bdm/data/graph8c.g6>.

## Exact substitution formulas

For a quotient `Q` with positive bag weights `w`, the search avoids expanding
graphs of order up to 60.  It enumerates the selected count `x_v` in each twin
class exactly.

For a clique bag, an unselected vertex in bag `v` sees

```text
x_v + sum_{u~v} x_u.
```

For a false-twin bag it sees only

```text
sum_{u~v} x_u.
```

The threshold is one for domination and two for two-domination; a completely
selected bag has no outside vertex to constrain.  Counts above two are never
needed except for the option of selecting an entire false-twin bag.  This
gives an exhaustive product over at most four choices per quotient vertex.

Maxine is computed directly on the twin-class count state.  At every step the
degree of a remaining vertex in bag `v` is

```text
sum_{u~v} current_weight(u)                       (false twins)
current_weight(v)-1 + sum_{u~v} current_weight(u) (clique bag).
```

The best reading branches over all maximum-degree classes with memoization.
The deterministic reading follows the least remaining expanded label.

The source-note theorem supplies an exact prefilter.  If even one deterministic
Maxine performance has at least `alpha` survivors, then
`Maxine_best >= alpha`, and `gamma_2 <= alpha+gamma` proves the best reading
safe without enumerating the remaining ties.  Otherwise every tie choice is
computed before the candidate is accepted or rejected.

## Structured cores

The structured-first stage covered the frozen double-hub, theta, and path
cores.  It used both substitution types, every uniform weight through total
order 60, every one-bundle weight through total order 60, and every two-bundle
pair with each exceptional weight at most six (and total order at most 60).

| cores | substitution records | minimum `R_best` | minimum `R_det` | timeouts | crossings |
|---:|---:|---:|---:|---:|---:|
| 19 nonisomorphic cores | 27,976 | 0 | 0 | 0 | 0 |

The stage reached equality 299 times on the source-faithful reading and 695
times on the deterministic reading.  It did not cross.

## Complete quotient wall sweep

The generic stage considered every connected unlabeled quotient of orders
three through eight: 994 connected Atlas graphs on orders three through seven
and all 11,117 connected order-eight graphs.  Consistent with Method v0.2, the
weight optimization was restricted to the 261 quotients already lying on the
unweighted 382e wall or already exhibiting `Maxine_best < alpha`.

For every selected quotient it tested both substitution types, all uniform
weights, and every possible single exceptional bundle through total expanded
order 60.  Results were written in 93 reporting blocks:

| quotients inspected | selected quotients | substitution records | theorem-pruned | fully evaluated after prune | timeouts | crossings |
|---:|---:|---:|---:|---:|---:|---:|
| 12,111 | 261 | 212,502 | 199,599 | 12,903 | 0 | 0 |

Among the candidates surviving the theorem prefilter, the minimum exact
residual was still zero on both readings.  The summed single-core CPU time was
861.14 seconds; every individual Maxine solve respected the 60-second cap.
One symmetric quotient initially exceeded a coarse 60-second reporting shard,
not an individual solve.  Re-sharding and applying the deterministic-performance
theorem prefilter completed that quotient exactly; it is included in the table
and no incomplete record is counted.

## Unrestricted-weight coverage

The systematic wall sweep does not claim to enumerate every positive weight
composition through order 60; that composition space is enormous.  To test
the frozen prediction outside the single-bundle shapes, a reproducible seeded
stage (`seed=382`) sampled 20,000 unrestricted positive compositions over all
12,111 quotients and both substitution types:

| trials | theorem-pruned | fully evaluated after prune | minimum `R_best` | minimum `R_det` | timeouts | crossings |
|---:|---:|---:|---:|---:|---:|---:|
| 20,000 | 19,073 | 927 | 0 | 0 | 0 | 0 |

This is coverage, not exhaustiveness, and is not promoted to a truth claim.

## Independent verification

[`method_v02_382e_verify.py`](../../scripts/method_v02_382e_verify.py) uses an
explicit expanded graph and independently enumerates vertex subsets and all
Maxine tie choices.  On 250 seeded clique/false-twin expansions of order at
most 12 it agreed exactly with the quotient engine on `gamma`, `gamma_2`,
`Maxine_det`, and `Maxine_best`.

## Outcome

Primary outcome: **HOLD_BOUNDED**.

Secondary classification: **THEOREM_SIGNAL**.  The trial repeatedly reaches
equality, including on 158 order-eight graphs for the source-faithful reading,
yet neither the complete small-graph universe nor the prospectively chosen
substitution directions cross.  More importantly, the source theorem reduces
the entire risk region to graphs satisfying

```text
Maxine_best < alpha
and
gamma_2 - gamma > Maxine_best.
```

The first inequality occurs on 46 connected order-eight graphs, so the result
is not the vacuous assertion that Maxine always equals independence.  The
second separation is what persistently fails in this trial.  No stronger
lemma is claimed, and no novelty audit or Lean certificate is warranted
because there is no witness.

The failed pre-evaluation assumption is instructive: changing twin-bundle
weights can create a Maxine deficit, but it did not raise the two-domination
increment beyond that deficit.  A future trial should change the adjacency
geometry controlling `gamma_2-gamma`, not merely enlarge this weight search.

## Reproduction

```bash
timeout 60s python3 scripts/method_v02_382e_search.py gate

curl -fsSL https://users.cecs.anu.edu.au/~bdm/data/graph8c.g6 \
  | timeout 60s python3 scripts/method_v02_382e_search.py catalogue \
      --graph6 - --time-cap 58

timeout 60s python3 scripts/method_v02_382e_search.py structured \
  --max-order 60 --two-bundle-cap 6 --solve-cap 60

timeout 60s python3 scripts/method_v02_382e_verify.py
```

The complete quotient wall sweep is reporting-sharded; its one-line JSON
records are preserved in `method_v02_382e_substitutions.jsonl`.  The seeded
unrestricted-weight run is preserved in `method_v02_382e_sample.jsonl`.
