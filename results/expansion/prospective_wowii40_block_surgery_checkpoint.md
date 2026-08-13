# Prospective WOWII #40 block-surgery checkpoint

Date: 2026-08-13
Status: frozen trial active; no crossing yet

## Scope and status

The exact current DeepMind statement remains `research open`:

```text
largest induced forest >=
  ceil((path cover number + largest induced bipartite order + 1) / 2).
```

The local WOWII database agrees with this reading and records the historical
open marker plus the proved path-cover-one case.

The precise post-freeze GitHub audit found upstream issue #4702.  Its linked
work gives the equivalent deficiency inequality, reduces the bipartite case
conditionally to two open lemmas, and reports exhaustive dual-engine
verification of every connected graph through order eleven.  Consequently,
the Atlas/control sweep here is calibration only; prospective novelty begins
above order eleven and must be compared against the issue's artifacts.

## Frozen mechanism

This lane deliberately avoids the repository's earlier cactus proof
extraction.  It searches bounded block substitutions, ear surgeries, and
nonuniform complete-bipartite block trees, targeting graphs where overlapping
cycles lower the maximum induced forest while path-cover fragmentation and a
large bipartite induced subgraph raise the conjectured right side.

The contract was written before development evaluation at
[`prospective_wowii40_block_surgery_contract.md`](prospective_wowii40_block_surgery_contract.md).
All graph records and timeouts are append-only in
[`prospective_wowii40_block_surgery_ledger.jsonl`](prospective_wowii40_block_surgery_ledger.jsonl).

## Exact bounded results

The first completed checkpoint contains 260 development graphs:

| lane | exact graphs |
|---|---:|
| ear surgeries | 178 |
| nonuniform bipartite block trees | 47 |
| block substitutions | 35 |

Orders reach 17.  Sixteen candidates hit the deliberately shortened
five-second exact-solve cap and are logged `INCONCLUSIVE`; the frozen contract
allows up to 60 seconds, so these remain available for selective reruns.

There are zero crossings.  Ten graphs are exactly tight and the minimum slack
is zero.  The current result is therefore `NO_CROSSING_YET`, not the frozen
trial's final `HOLD_BOUNDED` verdict: only 260 of the allowed 1,200 development
graphs have completed.

## Sanity gate

An independent control pass evaluated 1,030 graphs:

- every connected Atlas graph of orders three through seven;
- paths, cycles, and complete graphs of orders three through nine;
- Petersen;
- complete bipartite controls with side sizes two through six.

No sanity graph crosses the inequality.  This is consistent with upstream
issue #4702's much larger exhaustive verification through order eleven.

## Exact evaluator

[`scripts/prospective_wowii40_block_surgery.py`](../../scripts/prospective_wowii40_block_surgery.py)
computes:

- induced-forest and induced-bipartite maxima by descending exhaustive subset
  search, with maximum witnesses and search counts;
- path-cover number by exact Hamiltonian-subset endpoint DP followed by exact
  set-partition DP, with every covering path emitted;
- graph6, edge lists, exact right side, and slack for every completed graph.

No commit, push, release, issue, PR, or other public action was performed.
