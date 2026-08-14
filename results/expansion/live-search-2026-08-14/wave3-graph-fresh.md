# Wave 3: fresh finite-graph empirical search

Date: 2026-08-14 UTC. Outcome: **`ZERO_BOUNDED`; no counterexample
candidate.** This is a live exploratory lane, not a proof and not an
uncontaminated benchmark result. The source pin is
`google-deepmind/formal-conjectures@b33d8678a28118c95d8d4f60b11faaf39ccff1e6`,
resolved independently by `git ls-remote` immediately before selection.

The lane deliberately did not reuse the original C5[K4]-only arsenal. It used
the Graph Atlas, random regular and Erdős--Rényi graphs, random labelled trees,
exact cycle-cover optimization, exact graceful-label CSP search, exact
chromatic subset tables, and invariant-preserving/local graph edits.

## Selection, source, and status gates

An exact case-insensitive scan of every pre-existing
`results/expansion/live-search-2026-08-14/*.md` found no occurrence of
`alon_tarsi_short_cycle_cover`, `graceful_tree_conjecture`, or `erdos_628`.
All three are direct finite-graph declarations: none has an asymptotic outer
quantifier, an infinite carrier, or an opaque-only proposition whose truth
cannot be crossed by a finite graph certificate.

Alon--Tarsi does have the syntactic wrapper `answer(sorry) ↔ <universal RHS>`.
It was retained because a finite bridgeless graph with `W_AT<0` would decide
the intended answer and correct the source RHS. Such a witness would not, by
itself, be described as a refutation of the opaque biconditional.

| declaration | pinned file SHA-256 | status sanity before compute |
|---|---|---|
| `Arxiv.2607.06396.alon_tarsi_short_cycle_cover` | `a69122ed8dd201b75b73d5ff682cf692c898816f78a6b2936fe0d92875604e7d` | current file is `research open`; statement PR [#4850](https://github.com/google-deepmind/formal-conjectures/pull/4850) merged; issue #4813 was a formalization request; all-state exact-name search found no solution or counterexample claim |
| `GracefulLabeling.graceful_tree_conjecture` | `9f18982429c0719977609873953a7d858f3cc06cef494b4932e0b0926017ffc0` | current file is `research open`; statement PR [#4189](https://github.com/google-deepmind/formal-conjectures/pull/4189) merged and #4188 is its closed duplicate; no resolving issue or PR was found |
| `Erdos628.erdos_628` | `bfbb3849502978d17ffdab475e782b5f8556ba2122f64f8b3eee0c32f9cb66a0` | current file is `research open`; statement PR [#4311](https://github.com/google-deepmind/formal-conjectures/pull/4311) merged and issue #840 was the formalization request; the current Erdős Problems data classifies #628 as `falsifiable`, meaning it appears open but a finite counterexample would disprove it, not that it is already false |

The source/database sanity was also native to each target. For Alon--Tarsi,
the literal definition is a multiset of simple cycles covering every edge and
the published conjecture is the same `7m/5` bound; a triangle gives the
expected positive control. For graceful labeling, the source's proved one- and
two-vertex tests agree with the evaluator, and the catalogue contains the
standard `1,1,1,2,3,6,11` nonisomorphic-tree counts through order seven. For
Erdős 628, the source records the `k=5,a=b=3` case as solved; the evaluator's
small boundary `C5` has `k=3`, clique number two, and an exact `(2,2)` split.
These checks preceded the frozen discovery invocations.

## Exact walls and arm definitions

Every final discovery invocation was wrapped independently in
`timeout -s KILL 60s`; all exited normally. The arm meanings were fixed across
targets: `CATALOGUE` exhausts the applicable small database, `GENERIC` uses a
target-independent seeded generator, and `WALL_NAVIGATION` begins from exact
equality/tight seeds and applies local edits chosen around a necessary integer
wall.

### Alon--Tarsi short cycle cover

Let `L(G)` be the exact minimum total length of a cycle cover and `m=|E|`.
The integral residual

```text
W_AT(G) = 7m - 5L(G)
```

is nonnegative exactly when the rational conclusion holds; a counterexample
requires `W_AT < 0`. The Petersen graph is an exact equality seed:
`m=15`, `L=21`, and `W_AT=0`. The wall arm used degree-preserving two-switches
from Petersen and circular-ladder seeds, retaining connected bridgeless
states. Each `L` was solved as a binary set-cover MILP over the complete list
of undirected simple cycles, with integral objective and exact post-solve edge
coverage checks.

### Graceful tree conjecture

For a tree with `m=n-1`, labels must be a permutation of `0..m`. Define
`D(T)=m-M(T)`, where `M(T)` is the maximum number of distinct nonzero edge
differences under such a permutation. A graceful labeling is exactly the
equality wall `D=0`; a proved counterexample requires an exhaustive CSP result
`D>0`. A further necessary invariant is parity: the required differences
`1..m` contain exactly `ceil(m/2)` odd values, so exactly that many tree edges
must join opposite-parity labels. The exact CSP enforced label and difference
uniqueness (hence this parity count) and used complement-label symmetry. The
wall arm applied one-edge tree exchanges from a graceful path, preserving
order, size, connectedness, and acyclicity.

### Erdős 628 / Erdős--Lovász Tihany

For fixed admissible `a+b=k+1`, define the exact split score

```text
S(G,a,b) = max_U min(chi(G[U])-a, chi(G[V-U])-b).
```

The conclusion is equivalent to `S >= 0`; equality rows have `S=0`, and a
counterexample necessarily has `S<0` while also satisfying `chi(G)=k` and
`omega(G)<k`. All induced-subgraph chromatic numbers were computed exactly by
subset dynamic programming. The wall arm started from `C5`, Petersen, and the
Mycielski graph of `C5`, applied one-edge toggles, and scored only connected
states surviving the exact chromatic/clique hypotheses.

## Frozen arm receipts

| target | arm | exact completed work | elapsed / cap | closest result |
|---|---|---:|---:|---|
| Alon--Tarsi | `CATALOGUE` | 578 connected bridgeless Atlas states through order 7 (including the one-vertex zero-edge boundary) | 13.293 s / 60 s | no crossing; closest nonempty row `C~ = K4`, `m=6,L=8,W_AT=2` |
| Alon--Tarsi | `GENERIC` | 785 distinct connected bridgeless random regular graphs, orders 8--11 | 38.516 s / 60 s | no crossing; `GpTL?k`, `(n,m,L,W_AT)=(8,12,16,4)` |
| Alon--Tarsi | `WALL_NAVIGATION` | 797 distinct seed/two-switch states | 23.039 s / 60 s | no crossing; Petersen equality `IheA@GUAo`, `(10,15,21,0)` |
| graceful tree | `CATALOGUE` | all 25 nonisomorphic Atlas trees through order 7; 1,257 CSP nodes | 0.051 s / 60 s | every tree has a full graceful certificate |
| graceful tree | `GENERIC` | 282 completed distinct-hash random labelled trees, orders 8--13; 13,322,631 CSP nodes; one in-progress state discarded at the internal 58 s stop | 58.002 s / 60 s | no crossing; retained order-13 equality `LGPSA?_A?GO_O?` |
| graceful tree | `WALL_NAVIGATION` | 305 completed distinct-hash tree-exchange states; 8,628,028 CSP nodes | 39.099 s / 60 s | every state reached `D=0` |
| Erdős 628 | `CATALOGUE` | all 996 connected Atlas graphs; 37 survived `omega<chi` | 0.582 s / 60 s | no crossing; minimum split score `0`, including `C5` |
| Erdős 628 | `GENERIC` | 533 connected distinct graph6 rows from seeded `G(n,p)`, orders 8--11; 30 eligible | 3.402 s / 60 s | no crossing; `JRzDgBG?gI?`, `(n,m,k,omega,a,b,S)=(11,19,4,3,2,3,0)` |
| Erdős 628 | `WALL_NAVIGATION` | 584 connected distinct graph6 edit states; 20 eligible | 4.231 s / 60 s | no crossing; `IheI@AVYo`, `(10,19,4,3,2,3,0)` |

No numerical optimizer timeout was promoted as a result. Two preflight harness
faults (an unavailable Python integer convenience method and a no-op dense
two-switch seed) were caught before the receipts above; their runs were
discarded, the evaluator was repaired, and the same frozen seeds and hard caps
were replayed from scratch.

## Independent exact replay

The retained tight row for each declaration was checked by a separate,
short evaluator that did not call the discovery routine.

- **Alon--Tarsi `K4`:** independent permutation enumeration generated every
  simple cycle, then exhaustive subset enumeration found minimum cover length
  eight. One optimum consists of the two 4-cycles with edge sets
  `{01,03,12,23}` and `{01,02,13,23}`. Thus `W_AT=7*6-5*8=2`. No cover of
  length at most seven exists in the exhaustive list.
- **Graceful order-13 row:** direct certificate replay checked that
  `LGPSA?_A?GO_O?` is a tree, that
  `[2,0,4,8,12,1,5,10,6,3,9,7,11]` is exactly a permutation of `0..12`, and
  that its edge differences are exactly `1,2,...,12`.
- **Erdős 628 generic row:** an independent backtracking coloring evaluator
  obtained `chi(G)=4` and maximum-clique enumeration obtained `omega(G)=3`.
  For vertex set `{0,2}`, the two induced chromatic numbers are exactly `2`
  and `3`, independently certifying the tight `(a,b)=(2,3)` conclusion.

## Terminal classification and method signal

- Alon--Tarsi: **`HOLD_BOUNDED`**, 2,160 exact bridgeless graph evaluations,
  with the wall arm recovering the Petersen equality seed and no negative
  integer residual.
- Graceful tree: **`HOLD_BOUNDED`**, 612 completed exact tree CSP searches and
  a direct order-13 certificate; the one unfinished generic state is excluded,
  not interpreted as evidence.
- Erdős 628: **`HOLD_BOUNDED`**, 2,113 exact graph evaluations, 87 eligible
  hypothesis rows, and minimum split score zero.

The principal empirical signal is target-specific. Cycle-cover navigation can
sit exactly on the Petersen `7/5` wall, so future effort should move among
snark-like equality states rather than generic dense graphs. Graceful-tree
search is certificate-rich and therefore poorly served by flat random trees;
future work should optimize parity-constrained near-graceful residuals at much
larger orders. Erdős 628 produced many exact split equalities, suggesting a
useful next wall is not more Atlas enumeration but chromatic-critical graph
generation that preserves both `chi=k` and `omega<k` at every move.

Claimable counterexamples: **zero**. No candidate notification, repository
commit, issue, pull request, release, or other outward action was made.
