# Method v16: WOWII #100 three-witness energy rung

## Reading and scope

This rung follows the exact upstream Lean statement, whose spectral term is
`degreeL2Norm Gᶜ`.  It does not substitute the complement-diameter wording in
the historical prose.

The previously certified ranges are

```text
alpha = 2, 3; alpha = 8,...,11; and alpha >= 12.
```

Thus the only remaining independence-number rows are `4 <= alpha <= 7`.
This file gives a warning-as-error Lean certificate for the complete
three-witness coordinate box in those rows.  It is deliberately reported as a
conditional rung: this step does not claim that connectedness by itself has
already been formalized to produce three distinct outside witnesses.

## Three-witness package

Let `S` be an independent set of size `a`, and let three distinct vertices
outside `S` have complement-attachment counts `t`, `u`, and `v` into `S`.
The aggregate complement-degree energy contributed by `S` and those witnesses
has the lower bound

```text
E3(a,t,u,v)
  = a(a-1)^2
    + (2a-1)(t+u+v)
    + t^2+u^2+v^2.
```

If `m = min(t,u,v)`, a local witness also supplies

```text
L >= a-m,
```

where `L` is the maximum independent-neighborhood count used upstream.
The exact residual inequality needed by the extraction theorem is therefore

```text
(2a-4+2m)^2 < E3(a,t,u,v).
```

Lean proves this strictly for every integer coordinate satisfying

```text
4 <= a <= 7,
0 <= t,u,v <= a-1.
```

The optimizer first replaces all three coordinates by their minimum, using
monotonicity of the linear and square terms, and then checks the bounded
`(a,m)` grid.  No graph enumeration, native-code evaluation, or untrusted
axiom is used.

## Exact worst margins

For auditability, the Lean file records a worst coordinate in each row and the
strict residual margin `E3 - (2a-4+2m)^2`:

| `a` | worst recorded `(t,u,v)` | margin |
|---:|:---:|---:|
| 4 | `(0,0,0)` | 20 |
| 5 | `(4,4,4)` | 40 |
| 6 | `(5,5,5)` | 66 |
| 7 | `(6,6,6)` | 110 |

Thus there is no residual numerical gap inside the three-witness coordinate
box: all four remaining rows cross strictly.  The only outstanding gap toward
an unconditional connected-graph theorem is combinatorial—extracting the
required witness configuration, or separately treating graphs with fewer than
three cross-boundary witness vertices.

The latter small-endpoint cases look promising but are not silently folded
into this result.  With exactly two cross-boundary endpoints, their attachment
sets are constrained by coverage of `S`; that should combine with the v14
two-witness energy theorem.  With one endpoint, its complement attachment is
zero.  Formalizing that classification is the next honest rung.

## Formal artifact and verification

Artifact:

```text
lean/GraphConjecture100ThreeWitness.lean
```

It contains:

- `ThreeOutsideEnergyCertificate`;
- `three_attachment_margin_four_to_seven`;
- `conjecture100_of_three_outside_energy_certificate`;
- `worst_three_witness_margins`.

Verification command:

```bash
LEAN_PATH=/tmp/c5k4-proof100-three timeout 60s lake env lean \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture100ThreeWitness.lean
```

Result: exit code 0, no diagnostics, approximately 21 seconds on the working
machine.  The file contains no `sorry`, `admit`, `native_decide`, or custom
axiom.
