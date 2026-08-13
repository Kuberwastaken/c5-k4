# Method v0.35: WOWII 61 realization-spectrum trial

## Outcome

This frozen prospective lane found **no counterexample** to current DeepMind
WOWII 61, but it did return the predeclared `REALIZATION_CLIFF` outcome.
Among all connected nonisomorphic graphs of order eight, 36 fixed degree
sequences contain both a tight realization and another realization whose
residual is at least two larger.

The result is evidence that degree-sequence reasoning alone cannot determine
the conjecture's slack: the Havel--Hakimi residue is fixed within a stratum,
while diameter and maximum induced-forest order vary materially with the
realization. It is not a disproof, theorem, or public novelty claim.

The frozen protocol and append-only artifacts are:

- `results/expansion/prospective_wowii61_realization_spectrum_contract.md`;
- `results/expansion/prospective_wowii61_realization_spectrum_ledger.jsonl`;
- `results/expansion/prospective_wowii61_realization_spectrum_records.jsonl`.

No commit, push, issue, PR, release, or other public action was taken.

## Source and status gate

The target was frozen before development evaluation at upstream commit
`9a1636c4030039f70cf78b866c216d8b6c5f35b0`:

```text
largestInducedForestSize(G)
  >= residue(G) + ceil(diameter(G)/3).
```

The source SHA-256 was
`54620e7b70a9a98eaaf7ce10154f533046b9f6d36fa276c8923c1a7301a7e091`.
The recovered WOWII record and the current formal-conjectures source both
classified the statement as open, and target-specific read-only GitHub issue
and PR searches found no resolution claim at freeze time.

## Database sanity came first

Before any development stratum was evaluated, the exact evaluator replayed
1,030 connected controls: the connected nontrivial Graph Atlas graphs through
order seven and all frozen named controls. There were no violations or
timeouts. The minimum residual was zero:

| residual | 0 | 1 | 2 | 3 | 4 | 5 |
|---:|---:|---:|---:|---:|---:|---:|
| graphs | 159 | 574 | 281 | 10 | 5 | 1 |

For every graph, the evaluator reconstructed the complete Havel--Hakimi
trajectory, checked connectivity, computed diameter, and solved maximum
induced forest exactly by decreasing-cardinality subset enumeration.

## Complete order-eight spectrum

Nauty supplied all 11,117 connected nonisomorphic graphs of order eight,
partitioned into 863 exact degree-sequence strata. There were no timeouts and
no negative residuals:

| residual | 0 | 1 | 2 | 3 |
|---:|---:|---:|---:|---:|
| graphs | 338 | 3,866 | 6,485 | 428 |

Thirty-six strata met the frozen realization-cliff criterion: residual range
at least two, including a residual-zero realization.

The first such stratum has degree sequence
`[5,4,3,3,2,1,1,1]`. Both graphs below have residue four:

| graph6 | diameter | maximum induced forest | residual |
|---|---:|---:|---:|
| `G?AFMw` | 4 | 6 | `6 - 4 - ceil(4/3) = 0` |
| ``G?`FEs`` | 3 | 7 | `7 - 4 - ceil(3/3) = 2` |

An independent implementation decoded the graph6 strings, recomputed their
common degree sequence and full Havel--Hakimi trajectory, used all-source BFS
for diameter, and exhaustively checked induced subsets for acyclicity. It
agreed on every value. The graphs are nonisomorphic; the tight realization
has two triangles and the slack-two realization has three.

For the tight graph, vertices `{0,1,2,3,4,5}` certify an induced forest of
order six, and all eight seven-vertex induced subgraphs contain a cycle. For
the slack-two graph, vertices `{0,1,2,3,4,5,6}` certify order seven, while the
full graph contains triangle `(0,4,7)`.

## Frozen higher-order checkpoint

The trial next generated the complete frozen manifest of 20,000 positive
graphical sequences of orders 8--12, ordered by decreasing residue, then
increasing edge count, then lexicographically. This checkpoint evaluated the
first 600 strata. Deterministic connected Havel--Hakimi seeds and at most 256
degree-preserving switch attempts produced 880 exact realization evaluations:

| residual | 0 | 1 | 2 |
|---:|---:|---:|---:|
| realizations | 589 | 274 | 17 |

There were no negative residuals and no timeouts. A deeper pass over ten of
the especially wall-dense strata, allowing up to 64 retained realizations per
sequence within the same 256-attempt cap, produced 17 evaluations: 16 tight
and one at residual one. It found no additional cliff and no crossing.

The machine record now contains 12,014 exact evaluations representing 12,003
distinct graph6 encodings. The repeated encodings arise only from the deeper
replay of a previously sampled slice.

This is an incremental checkpoint, not the frozen `HOLD_BOUNDED` verdict for
the entire 20,000-sequence universe: 19,400 ranked strata and the optional
orders 13--18 random tail remain unevaluated.

## Mathematical signal

The complete order-eight result rules out any counterexample there and shows
that realization choice can move the residual by two even when residue is
held exactly fixed. The sampled high-residue frontier is unusually wall
dense: 589 of 880 breadth evaluations were tight, including 127 of 128 in
manifest positions 400--499.

That suggests a focused continuation rather than undirected graph sampling:

1. continue the frozen manifest in 100-sequence, sub-60-second checkpoints;
2. within tight strata, search switch components specifically for moves that
   increase `ceil(diameter/3)` without increasing the maximum induced forest;
3. treat degree-sequence transformations only as stratum selectors, preserving
   this lane's independence from the degree-geometry proof program; and
4. require the full candidate protocol before any counterexample claim.

