# Frozen formal-conjectures one-off: WOWII #141 voltage lift

Frozen: 2026-08-13 UTC, before transformation evaluation

## Equality-map-only selection

Selection uses only the concretely applicable equality/near-equality map in
`results/expansion/method_v02_upstream_selection.md`.  Reed, Erdős 23, and
the exhausted WOWII 19/40/61/133 lanes are excluded by instruction.

| remaining mapped wall | closest recorded evidence | disposition |
|---|---|---|
| independent domination | optimal Petersen slack 48 | reject: no equality or unit wall |
| Erdős 64 | Boolean safe-side cycles | reject: no separable numerical wall |
| Erdős 128 | strict premise fails at equality | reject: premise boundary, not conclusion wall |
| Erdős 742 | margins 20 and 10; transformations break criticality | reject: not near equality |
| WOWII 59 | residual one at `C5[K2]` | reject: competing upstream disproofs already recorded; no clean fresh one-off |
| **WOWII 141** | **residual one at `complement(C5[K3])`** | **select: covers fix every neighborhood graph and can raise girth** |
| WOWII 145 | surviving-reading margin at least 3.5 | reject: not a unit wall |
| WOWII 146 | minimum residual 4 | reject: not a unit wall |
| WOWII 160 | official-reading residual 15 | reject: not near equality |
| WOWII 198a | equality occurs in the implication premise | reject: not a false-conclusion wall |
| WOWII 200 | seed fails the equality hypothesis | reject: not applicable |
| WOWII 291 | margin 34 | reject: not near equality |
| WOWII 314 | implication vacuous on the seed | reject: not applicable |

This table is the complete selection authority for this one-off.  No other
corpus, newly generated equality, or retrospective candidate is used.

## Exact target

Current DeepMind
`FormalConjectures/WrittenOnTheWallII/GraphConjecture141.lean` states, for a
connected finite nontrivial simple graph,

```text
tree(G) >= floor(girth(G)/2) - 1 + lambda_max(G),
```

where `tree` is maximum induced-tree order, girth is zero on an acyclic graph,
and `lambda_max` is maximum open-neighborhood independence.  Define

```text
R141 = tree - (girth // 2 - 1 + lambda_max).
```

A negative exact residual is a crossing.

## Frozen seed and single transformation

The sole seed is `B = complement(C5[K3])`, the residual-one graph named by the
existing equality map.  Label the five independent parts consecutively and
join exactly the part pairs at distance two on the five-cycle.

The sole transformation is one canonical connected `Z_3` voltage lift:

1. choose the lexicographic BFS spanning tree of `B` and gauge-fix its edge
   voltages to zero;
2. assign each sorted cotree edge a voltage in `{0,1,2}`;
3. require the signed circulation of every simple base cycle of length four
   or five to be nonzero modulo three;
4. among feasible assignments, minimize the deterministic integer objective
   `sum((i+1) * voltage_i)` over sorted cotree edges;
5. construct the 3-sheet lift with edge `(u,s)--(v,s+voltage(u,v))` for
   oriented base edge `u<v`.

The modular system is solved as a bounded integer linear program.  If it is
infeasible or times out, the verdict is respectively
`NO_APPLICABLE_CANDIDATES` or `HOLD_WITH_TIMEOUTS`; no replacement
transformation is allowed.

This is an explicit invariant separation.  A graph cover is locally
isomorphic, so every open-neighborhood graph and `lambda_max` are fixed.
Nonzero circulation removes all lifted 4- and 5-cycles, targeting the girth
coordinate.  Exact induced-tree response is not predicted post hoc.

## Gate and exact evaluation

Before solving the voltage system, evaluate every connected Graph Atlas graph
of orders 2--7, cycles `C3--C12`, paths `P2--P12`, stars `K1,2--K1,10`,
complete graphs `K2--K10`, complete bipartite graphs `K(a,b)` for
`1 <= a <= b <= 6`, Petersen, and the seed.

For each control compute exact girth, every local neighborhood independence
number, and exact maximum induced-tree order by descending subsets.  Retain an
induced-tree witness and independently replay it.  Any negative residual,
timeout, or certificate mismatch is `GATE_FAIL`.

For the transformed graph:

- verify connectedness, simplicity, the covering fibers, every lifted edge,
  local-neighborhood isomorphism, all voltage constraints, and exact girth;
- first search exhaustively for an induced tree of target order.  A witness is
  an exact decision-level hold certificate;
- only if no target tree exists, compute the exact maximum by descending
  subsets and independently replay a negative result before any crossing;
- preserve graph6, voltages, invariant values, witnesses, and solver status.

Every operating-system process is capped at 60 seconds.  The MILP and each
exact search receive at most 55 seconds.  Every row is appended immediately to
`results/expansion/prospective_formal_oneoff_141_ledger.jsonl`.

Verdicts are `GATE_FAIL`, `NO_APPLICABLE_CANDIDATES`, `HOLD_BOUNDED`,
`HOLD_WITH_TIMEOUTS`, and `CROSSING_VERIFIED`.

## Public-action rule

This lane may write only its local evaluator, append-only ledger, and result
report.  It may not commit, push, release, open an issue, open a PR, or take
any other public action.
