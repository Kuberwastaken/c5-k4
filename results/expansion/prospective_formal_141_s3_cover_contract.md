# Frozen addendum: WOWII #141 nonabelian `S3` permutation lift

Frozen: 2026-08-13 UTC, before candidate evaluation

Parent one-off: `prospective_formal_oneoff_141_contract.md`

## Motivation and scope

The parent trial selected current DeepMind WOWII #141 from the existing
formal-conjectures equality map.  Its sole cyclic `Z3` cover was exactly
infeasible: 423 short-cycle nonzero-circulation constraints conflict.

This addendum changes the transformation class, not the target or seed.  It
tests one genuinely nonabelian three-sheet permutation lift of the same
residual-one seed `B = complement(C5[K3])`.  No cyclic voltage assignment,
subdivision, deletion, attachment, graph power, random lift, or alternate seed
is allowed.

The exact residual remains

```text
R141(G) = tree(G) - (girth(G) // 2 - 1 + lambda_max(G)).
```

## Frozen `S3` lift

Use the same deterministic seed labelling and lexicographic BFS spanning tree
as the parent trial.  Gauge-fix every tree-edge permutation to the identity.
For each sorted cotree edge `u<v`, assign a permutation of `{0,1,2}`.  The
oriented lifted edges are

```text
(u,s) -- (v,p_uv(s)).
```

Reverse traversal applies `p_uv^{-1}`.  For every simple base cycle of length
four or five, require the ordered permutation product around the cycle to be
fixed-point-free.  In `S3`, this means the product is one of the two 3-cycles.
This removes every same-length lift of the seed's 4-/5-cycles while retaining
the exact covering map.

## Frozen exact solver and objective

Represent permutations by their image tuples and order the six elements of
`S3` lexicographically.  The objective is the lexicographically minimum vector
of permutation ranks over sorted cotree edges.

Use exact finite-domain constraint programming only:

1. maintain a six-element bit-domain for each of the 31 cotree variables;
2. enforce generalized arc consistency on every cycle-product constraint by
   enumerating the at most `6^5` local assignments;
3. select the first non-singleton cotree variable in sorted edge order;
4. branch on remaining permutation ranks in ascending order;
5. stop at the first feasible leaf, which is the frozen lexicographic optimum;
6. cap the search at 250,000 branch states and 55 wall-clock seconds.

`INFEASIBLE` is an exact exhaustion result.  Reaching either cap is
`SOLVER_TIMEOUT`; no heuristic assignment, relaxed constraint, fourth sheet,
new seed, or retuning is allowed after the outcome.

## Mandatory database gate

Before the permutation solver runs, rerun the parent trial's full exact gate:
every connected Graph Atlas graph of orders 2--7, its frozen named cycles,
paths, stars, complete and complete-bipartite graphs, Petersen, and the seed.

For each graph retain exact girth, all neighborhood-independence values,
maximum induced-tree order, and a replayed maximum-tree witness.  Any negative
residual, timeout, or mismatch is `GATE_FAIL` and prevents cover solving.

## Candidate verification and decision rule

For a feasible assignment verify independently:

- simplicity and connectedness;
- three vertices in every fiber and the exact edge-covering bijection;
- every stored 4-/5-cycle monodromy is fixed-point-free;
- every lifted local independence value equals six, hence
  `lambda_max(lift)=lambda_max(seed)=6`;
- exact girth by edge-deletion shortest paths.

Then search exhaustively for any induced tree on

```text
target = girth // 2 - 1 + lambda_max
```

vertices.  A replayed target tree is an exact decision-level hold.  Only when
the exhaustive decision search returns no witness may the evaluator compute
the exact maximum induced-tree order by descending subsets.  Any apparent
crossing requires an independent replay before status/novelty work.

## Resources, ledger, and verdicts

- Every operating-system process is capped at 60 seconds.
- Gate, solver, target search, and exact fallback each have an internal cap of
  at most 55 seconds.
- Every phase and candidate row is flushed immediately to
  `results/expansion/prospective_formal_141_s3_cover_ledger.jsonl`.

Verdicts are `GATE_FAIL`, `NO_APPLICABLE_CANDIDATES`, `HOLD_BOUNDED`,
`HOLD_WITH_TIMEOUTS`, and `CROSSING_VERIFIED`.

## Public-action rule

This lane may write only its local evaluator, append-only ledger, and result
report.  It may not commit, push, release, open an issue, open a PR, or take
any other public action.
