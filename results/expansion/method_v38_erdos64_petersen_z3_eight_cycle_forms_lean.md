# Erdős 64 Petersen `Z3` eight-cycle obstruction: Lean extraction

Date: **2026-08-13 UTC**

Status: **WARNING-CLEAN FINITE-FIELD OBSTRUCTION**

No commit, push, release, issue, PR, or other public action was taken.

## Derived base-cycle forms

For cotree coordinates in frozen order

```text
(a,b,c,d,e,f) = (x23,x27,x38,x68,x69,x79),
```

Petersen has exactly fifteen canonical simple 8-cycles.  Their oriented total
`Z3` voltages are:

| cycle | coefficient vector | form |
|---|---:|---|
| `01234975` | `100002` | `a-f` |
| `01238694` | `101210` | `a+c-d+e` |
| `01275834` | `012000` | `b-c` |
| `01279685` | `010121` | `b+d-e+f` |
| `01683275` | `212100` | `-a+b-c+d` |
| `01685794` | `000101` | `d+f` |
| `01694385` | `001010` | `c+e` |
| `01697234` | `120012` | `a-b+e-f` |
| `04321685` | `200100` | `-a+d` |
| `04386975` | `001212` | `c-d+e-f` |
| `04961275` | `010020` | `b-e` |
| `04972385` | `121002` | `a-b+c-f` |
| `12385796` | `101021` | `a+c-e+f` |
| `12794386` | `011201` | `b+c-d+f` |
| `23496857` | `120120` | `a-b+d-e` |

Coefficients are modulo three; `2` denotes `-1`.

## Structural proof

`lean/Erdos64PetersenZ3EightCycleForms.lean` defines these exact fifteen
forms.  The first six are linearly independent and therefore give basis
coordinates `y0,...,y5`.  Lean verifies symbolically that the other nine
forms become:

```text
y1-y2+y4, y0-y3+y5, -y2+y4, y1-y2+y4-y5,
y3-y5, y0-y2, y3-y4, -y0+y1+y3-y5,
y0-y1-y4+y5.
```

The covering proof then has two conceptual stages:

1. if some basis coordinate is zero, one of the first six cycles is already
   zero-voltage;
2. otherwise every `F3` coordinate is `1` or `-1`; the remaining forms block
   all 64 sign patterns (indeed indices 6 through 12 suffice).

This proves `exists_zero_voltage_eightCycle`: **every** assignment in
`Z3^6`, not merely the 728 nonzero connected assignments, gives zero total
voltage to a simple Petersen 8-cycle.  Thus the uniform 8-cycle outcome in
the completed prospective trial has an exact finite-field explanation.

This is not a disguised `native_decide` over the family.  The only finite
classification is the three-element lemma “nonzero in `F3` means `±1`,”
followed by transparent constant arithmetic on 64 basis-sign branches.

## Graph-cover adapter boundary

The file intentionally does not assert the graph-level consequence.  To
close that adapter in Lean still requires definitions and proofs that:

- the displayed cycles are simple cycles in the labelled Petersen graph;
- their totals are exactly the fifteen derived forms under the frozen edge
  orientation and tree gauge;
- a zero-voltage simple base cycle in the derived cyclic cover lifts to
  simple cycles of the same length.

The audited Python construction and witness ledger establish those facts
  computationally, but the Lean artifact is honestly the complete algebraic
  core rather than a graph-cover formalization.

## Verification

From `/Users/kuber.mehta/Projects/formal-conjectures`:

```bash
timeout 55s lake env lean -DwarningAsError=true \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  /Users/kuber.mehta/Projects/c5-k4/lean/Erdos64PetersenZ3EightCycleForms.lean
```

Result: exit `0` in approximately 9.2 seconds.  The axiom audit contains only
  standard `propext`, `Classical.choice`, and `Quot.sound`.  The source contains
  no `sorry`, `admit`, `native_decide`, or custom `axiom`.
