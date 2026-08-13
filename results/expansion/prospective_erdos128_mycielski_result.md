# Erdős 128 single-Mycielski prospective result

Date: 2026-08-13 UTC

## Outcome

`HOLD_BOUNDED`, with the sole development graph classified
`PREMISE_FALSE_STRICT`.

The trial targeted the current DeepMind Formal Conjectures declaration
`Erdos128.erdos_128`, not WoW I.  Its contract was frozen before development
construction or evaluation in
[`prospective_erdos128_mycielski_contract.md`](prospective_erdos128_mycielski_contract.md).

## Database gate

The exact gate evaluated 97 connected triangle-free controls:

- every connected triangle-free Graph Atlas graph of orders 3--7;
- `C5`, `C7`, Petersen, `K(2,3)`, and `K(3,3)`;
- balanced independent-set `C5` blow-ups `B1` through `B4`.

No control unexpectedly satisfied the strict premise.  The selected equality
carrier `B2` reproduced

```text
n=10, eligible size=5, minimum induced edges=2,
50*2 - 10^2 = 0.
```

The larger even carrier `B4` independently also had margin zero; the odd
orders `B1,B3` lay on the premise-false side because of integer parity.

## Sole prospective transformation

Exactly one graph was constructed: the ordinary Mycielski lift `M(B2)`.

| coordinate | exact value |
|---|---:|
| order | 21 |
| edges | 70 |
| triangle-free | yes |
| minimum eligible size | 10 |
| minimum induced edges | 0 |
| premise margin | `50*0 - 21^2 = -441` |
| classification | `PREMISE_FALSE_STRICT` |

The emitted minimizing witness is precisely the ten shadow vertices
`{10,...,19}`.  The evaluator directly replayed that the induced edge count is
zero.  Since zero is an absolute lower bound, this is also an exact minimum;
the primary enumeration reached it after 352,706 candidate subsets.

## Structural interpretation

Mycielski lifting preserves triangle-freeness but cannot approach the Erdős
128 strict premise.  For any input of order `n`, the `n` shadow vertices are
independent, while the output has order `2n+1`.  They satisfy the formal
eligibility threshold with equality:

```text
2*n + 1 = |V(M(G))|.
```

Thus every ordinary Mycielski lift contains an eligible induced subgraph with
zero edges.  The negative result closes this entire transformation direction,
not merely the evaluated `B2` instance.  It does not prove or disprove Erdős
128 in general.

All 101 events were written incrementally to
[`prospective_erdos128_mycielski_ledger.jsonl`](prospective_erdos128_mycielski_ledger.jsonl).
No timeout, candidate, novelty gate, commit, push, release, issue, PR, README
edit, or public action occurred.

