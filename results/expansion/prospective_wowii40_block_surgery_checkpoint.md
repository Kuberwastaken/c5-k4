# Prospective WOWII #40 block-surgery checkpoint

Date: 2026-08-13
Status: frozen trial complete; `INCONCLUSIVE`, with no exact crossing

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

## Final frozen result

The canonical trial scope is the first 1,200 distinct candidate names at their
first `graph_evaluated` or `graph_timeout` event in ledger order.  Its
newline-delimited name list has SHA-256
`cdef90b65b007d8779c1f0f8653dd30fc27810afc5ef4270302af72e96b3ca7d`.

Of those 1,200 candidates, 1,173 completed exact evaluation:

| lane | exact graphs |
|---|---:|
| one-off mutations | 901 |
| ear surgeries | 182 |
| nonuniform bipartite block trees | 55 |
| block substitutions | 35 |

Orders reach 17.  There are zero exact crossings, 69 exact tight cases, and
minimum slack zero.  Twenty-seven in-scope candidates remain unresolved after
the permitted bounded retries.  Under the frozen verdict definitions, that
makes the result `INCONCLUSIVE`, not `HOLD_BOUNDED`.

## Cap bookkeeping correction

The runner originally counted unique exactly completed graph6 strings but did
not count timed-out candidate names toward the 1,200 cap.  It consequently
evaluated 27 later candidates before the error was noticed.  Search stopped
immediately on detection.  Those append-only rows remain in the ledger for
auditability but are explicitly outside the frozen trial and play no role in
the result above.  The runner now counts each newly attempted candidate name,
including a timeout, while a retry of the same candidate consumes no new cap
slot.

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
