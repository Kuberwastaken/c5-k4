# Live finite-graph scalar-inequality search — 2026-08-14

## Scope and controls

- Repository lane: current finite graph scalar inequalities in
  `google-deepmind/formal-conjectures`, excluding anything already resolved or
  claimed either in this repository or in upstream issues/pull requests.
- Current upstream `main`: `b33d8678a28118c95d8d4f60b11faaf39ccff1e6`
  (resolved independently by `git ls-remote` and the GitHub commits API).
- Comparison baseline: `d16e05aded22b8c467a0a27c14b2311f53185006`, the
  latest complete finite-graph ranking in this repository. The only later
  finite-graph source changes are status/statement work on WOWII 145 and 200;
  no new open finite-graph scalar declaration was added.
- Statement parsing is against the exact Lean expressions at current upstream,
  not prose aliases. Every subprocess in this lane is externally hard-capped
  with `timeout 60s`; exact routines also use an internal cap no larger than 60
  seconds.

The existing result and live-upstream subtraction excludes independent
domination (the exact bound is Corollary 1.3 of Cho--Kim--Kim--Oum, 2023),
Reed (six prior target-specific lanes), Erdős 23/64/128/742, and all scalar
WOWII targets with an existing proof/disproof claim. In particular live GitHub
search found claims for 19 (PR 4559), 59 (PRs 4574/4583), 100 (issue 4920 and
PR 4515), 141 (PR 4454), 145/146, 160, 198a, 200, 291 (issue 4562), and 314.
The remaining direct, current, unclaimed scalar targets selected here are
WOWII 40, 61, and 133.

## Frozen arm meanings and budgets

Each selected target receives the same three discovery arms.

| arm | fixed meaning | process budget |
|---|---|---:|
| `CATALOGUE` | every connected Graph Atlas graph on 2--7 vertices, with the target's exact hypotheses | 1 process x 60 s |
| `GENERIC` | deterministic seeded Erdős--Rényi and degree-preserving random exploration on orders 8--11, with no target-specific construction | 1 process x 60 s |
| `WALL_NAVIGATION` | start only from exact equality/unit-wall catalogue rows and apply one-edge toggles or degree-preserving two-switches selected by theorem-subtracted coordinates | 1 process x 60 s |

Candidate rule: a strict negative residual must first survive a second
implementation, then the full Atlas/named-control database sanity gate, then a
fresh open+merged upstream novelty search. No numerical candidate is a claim
before all three checks.

## Attempt ledger

Rows are appended after each arm finishes.

| target | arm | budget | outcome | closest/improvement observation |
|---|---|---:|---|---|
| WOWII 40 | `CATALOGUE` | 995 graphs; 2.724 s / 60 s | `HOLD_BOUNDED`; 0 crossings, 0 timeouts | minimum residual 0; 175 equality rows |
| WOWII 40 | `GENERIC` | 175 connected rows generated from fixed-seed orders 8--11; 6.618 s / 60 s | `HOLD_BOUNDED`; 0 crossings, 0 timeouts | minimum residual 0; 22 equality rows; best new equality `IL~~~r{}w` has `(n,m,f,b,p,rhs)=(10,37,4,5,1,4)` |
| WOWII 40 | `WALL_NAVIGATION` | 700 distinct one-edge toggles from catalogue rows of residual at most 1; 1.087 s / 60 s | `HOLD_BOUNDED`; 0 crossings, 0 timeouts | 69/700 moves improved residual, 536 were neutral, 95 worsened; best change `-1`, stopping at equality; 157 equality outputs |
| WOWII 61 | `CATALOGUE` | 995 graphs; 1.932 s / 60 s | `HOLD_BOUNDED`; 0 crossings, 0 timeouts | minimum residual 0; 151 equality rows |
| WOWII 61 | `GENERIC` | 175 connected rows generated from fixed-seed orders 8--11; 4.076 s / 60 s | `HOLD_BOUNDED`; 0 crossings, 0 timeouts | minimum residual 0; 9 equality rows; `G}u@?_` reaches equality with `(n,m,f,residue,diameter)=(8,11,6,4,4)` |
| WOWII 61 | `WALL_NAVIGATION` | 700 distinct degree-preserving two-switches from catalogue rows of residual at most 1; 0.716 s / 60 s | `HOLD_BOUNDED`; 0 crossings, 0 timeouts | 27/700 moves improved residual, 611 were neutral, 62 worsened; best change `-1`, stopping at equality; 123 equality outputs |
| WOWII 133 | `CATALOGUE` | 995 graphs; 4.037 s / 60 s | `HOLD_BOUNDED`; 0 crossings, 0 timeouts | minimum residual 0; 44 equality rows |
| WOWII 133 | `GENERIC` | 174 connected rows generated from fixed-seed orders 8--11; 5.498 s / 60 s | `HOLD_BOUNDED`; 0 crossings, 0 timeouts | one equality row: `GjnL~g`, a connected 8-vertex 5-regular graph with a C4, `(path,radius)=(3,2)` |
| WOWII 133 | `WALL_NAVIGATION` | 700 distinct one-edge toggles from catalogue rows of residual at most 1; 0.552 s / 60 s | `HOLD_BOUNDED`; 0 crossings, 0 timeouts | 16/700 moves improved residual, 473 were neutral, 211 worsened; best change `-1`, stopping at equality; 26 equality outputs |

All nine processes exited normally. No ILP or exact-search timeout occurred.
The repeated `-1` wall improvement is a genuine directional advantage over
the generic arms, but it produced equality rather than a negative residual and
therefore is not a candidate.

## Exact statement and theorem-subtraction audit

### WOWII 40

The evaluated Lean conclusion is

```text
ceil((pathCoverNumber(G) + b(G) + 1) / 2) <= f(G),
```

where `pathCoverNumber` is the minimum number of ordinary vertex-disjoint
paths covering the vertices, `b` is maximum induced bipartite order, and `f`
is maximum induced forest order. The signed residual is the left-to-right
slack `R40=f-ceil((p+b+1)/2)`.

The theorem subtraction used the repository's proved baseline
`b+2 <= 2f`. It leaves the exact unpaid coordinate
`p-1 <= 2f-(b+2)`. Equality/unit rows were therefore navigated by one-edge
toggles, measuring whether the toggle increased path-cover demand faster than
the baseline forest surplus. Sixty-nine moves improved the full residual by
one, but every such move stopped at zero.

### WOWII 61

The evaluated Lean conclusion is

```text
residue(G) + ceil(diameter(G)/3) <= f(G).
```

The Havel--Hakimi residue uses the full terminal zero suffix, not WOWII 291's
first-zero iteration. The signed residual is
`R61=f-residue-ceil(diameter/3)`. Degree-preserving two-switches hold the
residue term exactly, so the wall arm isolates the competition between each
new three-distance-layer threshold and the induced-forest compensation.
Twenty-seven moves lowered the residual by one; none made it negative.

### WOWII 133

The evaluated Lean conclusion is

```text
radius(G) + (hasC4(G) ? 1 : floor(average_v alpha(G[N(v)])))
  <= largestInducedPathOrder(G).
```

Here `hasC4` means a four-cycle as a subgraph, even when it has chords. The
C4-present branch subtracts the standard diametric/geodesic baseline
`path>=radius+1`; only the C4-free correction can create an unpaid term.
The wall arm began at equality/unit rows and used one-edge toggles to test
whether radius/local-independence moved faster than induced-path order.
Sixteen moves improved by one, again stopping at equality.

## Database sanity and independent replay

The `CATALOGUE` arm is also a fresh statement-reading gate: all 995 connected
Graph Atlas graphs on 2--7 vertices were evaluated for each target and none
crossed. A separate named-control pass checked 27 rows for WOWII 40, 46 for
WOWII 61, and 19 for WOWII 133 (cycles, `P7`, Petersen, `K3,3`, `K7`, stars,
and complete bipartite graphs as applicable). It found zero crossings and zero
timeouts; every target had minimum residual zero.

The closest non-catalogue generic equality for each target was then replayed
without calling the discovery evaluator:

| target | graph6 | independent result |
|---|---|---|
| WOWII 40 | `IL~~~r{}w` | exhaustive subset checks give `f=4`, `b=5`; explicit Hamilton path `0-3-2-1-4-6-5-8-9-7` gives ordinary `p=1`; hence RHS 4 and residual 0 |
| WOWII 61 | `G}u@?_` | exhaustive induced-forest enumeration gives `f=6`; an independent Havel--Hakimi implementation gives residue 4; all-pairs distances give diameter 4; residual `6-4-2=0` |
| WOWII 133 | `GjnL~g` | exhaustive induced-path and neighbourhood-independent-set enumeration gives path 3, radius 2, average local independence 2; an explicit four-cycle exists, so the correction is 1 and residual 0 |

During this replay, an intentionally separate WOWII 40 checker initially
treated the path-cover paths as **induced** paths and printed a spurious
residual `-1`. This conflicts with the exact `pathCoverNumber` reading. The
row was discarded immediately; the explicit ordinary Hamilton path above
reproduces `p=1` and the primary residual zero. No candidate or claim was made
from the invalid parse.

## Live upstream novelty/status gate

At upstream `b33d8678`, all three files still carry
`@[category research open]` and an unresolved declaration. GitHub searches
covering open and closed issues/PRs found:

- WOWII 40: issue 4702 reports equivalent-deficiency work and exhaustive
  verification through order 11, but no proof or disproof claim;
- WOWII 61: no target-specific mathematical issue or PR; the broad module
  reorganization PR 4688 is not a resolution claim;
- WOWII 133: no open proof/disproof issue or PR; closed PR 4282 is a statement
  correction, not a resolution.

Thus these were legitimate current open/unclaimed targets, but the present
bounded rows supply no new claim. The order-at-most-11 WOWII 40 generic rows
also lie inside the already announced finite verification range in issue
4702, so they are calibration rather than a novelty contribution.

## Terminal result

`ZERO_COMPLETE_WITHIN_BUDGET`: **3 targets, 9 discovery arms, 5,609 exact
graph evaluations, 0 crossings, 0 timeouts.** No candidate was sent for
verification or novelty promotion. The main improvement observation is
comparative: wall navigation achieved a one-unit residual improvement on all
three targets, while the frozen generic arms merely rediscovered equality;
the controlling compensation term activated exactly at the conjectured wall.

No repository file other than this report was edited. No git add, commit,
push, release, issue, or pull request was performed.
