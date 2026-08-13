# Method v17: WOWII #100 witness classification

## Result

The final unresolved independence-number range is now closed for connected
graphs under the exact upstream Lean reading:

```text
4 <= alpha(G) <= 7
```

The formal theorem is

```text
conjecture100_of_connected_of_indepNum_four_to_seven
```

and assumes only that `G` is finite, nontrivial, and connected.  Complement
connectedness is not needed in this range.

As throughout the #100 audit, this result follows the actual upstream term
`degreeL2Norm Gᶜ`.  It does not reinterpret that term as the complement
diameter appearing in the historical prose.  The prose/formalization caveat
therefore remains fully in force.

## Classification

Fix a maximum independent set `S`.  Call a vertex a cross witness when it is
outside `S` and adjacent in `G` to at least one member of `S`.

Connectedness supplies a cross witness covering every `s ∈ S`: take any
neighbor of `s`; independence forces that neighbor outside `S`.  Starting
from one witness, classical case splitting gives an exhaustive trichotomy:

1. exactly one cross witness;
2. exactly two cross witnesses;
3. at least three distinct cross witnesses.

This is formalized without enumerating graphs or vertex sets.

## One-witness branch

If `y` is the unique cross witness, coverage forces `y` adjacent to every
member of `S`.  Its complement attachment count is consequently zero.

The existing one-witness attachment/energy tradeoff then gives a strict
residual inequality in each of the four rows `a=4,5,6,7`.  The file packages
this as `conjecture100_of_zero_attachment_four_to_seven`.

## Two-witness branch

Suppose `y,z` are the exhaustive cross witnesses, and write

```text
T = {s in S | Gᶜ.Adj y s},
U = {s in S | Gᶜ.Adj z s}.
```

Every `s ∈ S` is adjacent in `G` to `y` or `z`.  Hence no `s` can belong to
both `T` and `U`; formally, `T` and `U` are disjoint.  Therefore

```text
|T| + |U| <= |S|.
```

This is exactly the missing constraint.  Without it, the raw two-witness
energy package has one bad upper corner in every row:

```text
(t,u) = (a-1,a-1).
```

Coverage excludes those corners.  Lean proves the strict residual inequality
for every integer coordinate satisfying

```text
4 <= a <= 7,
t+1 <= a,
u+1 <= a,
t+u <= a.
```

The graph-level v14 incidence certificate then closes the entire branch.

## Three-witness branch

For three distinct cross witnesses, each complement attachment count is at
most `a-1`, because each witness has at least one genuine `G`-edge into `S`.

This file supplies the previously missing graph-level derivation of the v16
aggregate certificate

```text
E3(a,t,u,v)
  = a(a-1)^2
    + (2a-1)(t+u+v)
    + t^2+u^2+v^2.
```

It counts triple incidences over `S`, proves the pointwise complement-degree
lower bounds, adds the three outside degree squares, and embeds the resulting
partial sum into the full degree-square sum.  The v16 optimizer then closes
all coordinates in `a=4,...,7`.

## Formal inventory

Artifact:

```text
lean/GraphConjecture100WitnessClassification.lean
```

Important declarations:

- `sum_tripleAttachments_eq`;
- `card_sub_one_add_tripleAttachments_le_degree`;
- `three_outside_energy_certificate`;
- `two_attachment_margin_four_to_seven_of_sum_le`;
- `CrossWitness`;
- `cross_witness_covers`;
- `cross_witness_trichotomy`;
- `zero_attachment_of_unique_cross_witness`;
- `two_attachment_sum_le_of_exhaustive`;
- `conjecture100_of_zero_attachment_four_to_seven`;
- `conjecture100_of_two_outside_energy_of_sum_le`;
- `conjecture100_of_connected_of_indepNum_four_to_seven`.

## Verification

```bash
LEAN_PATH=/tmp/c5k4-proof100-three timeout 60s lake env lean \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture100WitnessClassification.lean
```

Result: exit code 0, no diagnostics, approximately 11 seconds on the working
machine.  The artifact contains no `sorry`, `admit`, `native_decide`, or custom
axiom.

## Consequence for the #100 program

Together with the earlier exact-reading rungs, the connected-graph
independence ranges now stand as follows:

```text
alpha = 2                 proved earlier (with the earlier stated hypotheses)
alpha = 3                 proved earlier (with the earlier stated hypotheses)
alpha = 4,...,7           proved here from connectedness
alpha = 8,...,11          proved in v15 from connectedness
alpha >= 12               proved in v12 from connectedness
```

Thus the former `4 <= alpha <= 7` residual is no longer conditional: the
combinatorial witness extraction and every energy branch are now formally
assembled.
