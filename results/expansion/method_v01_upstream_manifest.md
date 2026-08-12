# Method v0.1 upstream-manifest refresh

Audit date: **2026-08-12**. This is a selection audit, not a counterexample
search and not held-out evidence.

## Version lock

- Previous sweep: `google-deepmind/formal-conjectures` at `c9052e8577118ed0ada54462bd4ef1f3beff37d6`.
- Refreshed upstream: `547f309edcc2069c1f61c2465729031c10385540`.
- Comparison command:

  ```text
  git diff --name-status c9052e8..547f309e -- FormalConjectures
  ```

The exact source delta is one added file:

```text
A FormalConjectures/Arxiv/2605.02731/DeanCycles.lean
```

No previously swept declaration changed or disappeared. The earlier operational
manifest therefore remains intact, with one new source module and two new open
declarations representing one mathematical target cluster.

## Added declarations

At `547f309e`, `DeanCycles.lean` adds:

1. `dean_conjecture`: for every integer `k>=3`, every finite simple graph with
   minimum degree at least `k` has a cycle whose length is divisible by `k`;
2. `dean_conjecture.variants.five`: the `k=5` case.

The same file records `k=3`, `k=4`, and `k>=6` as solved, so the two open Lean
declarations are logically one remaining mathematical cluster: the `k=5`
case. They must not be counted as two independent method trials.

## Eligibility and prior development evidence

The target is an existing open finite-`SimpleGraph` universal statement and is
concretely falsifiable by one finite graph. It therefore passes the Method v0.1
scope and applicability filters.

It is not untouched. Before the upstream formalization landed, the campaign's
`breakthrough_targets.md` already ranked and evaluated Dean cycle divisibility.
Every admissible arsenal graph had an explicit cycle of length five; the result
was `HOLD_BOUNDED`. The new upstream file changes provenance and submission
relevance, not the evidential status.

## Residual/wall assessment

This is a Boolean existence property rather than a numerical invariant
inequality, so the ordinary signed residual is replaced by the minimum cycle
length divisible by five, with `infinity` when no such cycle exists.

Method fit is currently weak:

- clique blow-ups and windmills readily introduce 5-cycles;
- the dense carrier and triangular families are therefore safe-side controls,
  not equality-wall maps;
- complementing or bounded edge surgery can destroy a chosen 5-cycle but gives
  no present reason to preserve minimum degree at least five while excluding
  every cycle length divisible by five;
- no zero-slack numerical wall or one-invariant obstruction identity is known.

Accordingly this cluster is **eligible but low priority**. Method v0.1 should
not spend an open-ended search budget on it until a structural family with
minimum degree five and controlled cycle spectrum supplies an explicit wall.

## Refreshed selection result

| item | result |
|---|---|
| prior 77 declarations / 56 modules | unchanged |
| newly added open declarations | 2 |
| newly added mathematical clusters | 1 |
| newly eligible clusters | Dean `k=5` |
| prior campaign verdict | `HOLD_BOUNDED` |
| Method v0.1 rank | low; no wall-navigation signal |
| counterexample search in this audit | none |

The operational upstream corpus is now **79 open declarations in 57 modules**,
subject to the same declaration-level dependency rule used in the prior sweep.
At the mathematical-cluster level, the only addition is Dean's `k=5` case.

## Next refresh rule

Future refreshes compare from this exact upstream SHA. Added or modified
finite-graph declarations receive, in order:

1. applicability classification;
2. duplicate/variant clustering;
3. source and status lock;
4. prior-exposure check;
5. wall-signal score;
6. transformation-catalogue fit;
7. a committed prediction/budget manifest before any construction search.
