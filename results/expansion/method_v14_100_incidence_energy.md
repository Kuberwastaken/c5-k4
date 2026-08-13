# Method v0.14 — WOWII 100 incidence energy

Date: 2026-08-13  
Outcome: `PROVED_BRIDGE`  
Formal artifact: `lean/GraphConjecture100IncidenceEnergy.lean`

## Reading warning

This continues the exact upstream Lean expression containing
`degreeL2Norm Gᶜ`. The upstream prose instead discusses complement diameter.
The results here apply only to the degree-norm formalization.

## Graph-level E2 proof

Let `S` be a nonempty independent set of size `a`, and let `y,z` be distinct
vertices outside `S`. Write `t,u` for their complement-attachment counts into
`S`.

For each `s in S`, define the attachment multiplicity

```text
k(s) = |{y,z} ∩ N_Gᶜ(s)|.
```

The proof constructs the explicit complement-neighbor subset

```text
(S erase s) ∪ ({y,z} filtered by adjacency to s).
```

The two pieces are disjoint because `y,z` lie outside `S`, so

```text
degree_Gᶜ(s) >= a-1+k(s).
```

The exact square correction is

```text
(a-1+k)^2
 = (a-1)^2 + (2a-1)k + k(k-1),
```

and the final term is nonnegative for integral `k`. Summing over `S` uses the
formal incidence identity

```text
sum_{s in S} k(s) = t+u.
```

Finally `degree_Gᶜ(y)>=t` and `degree_Gᶜ(z)>=u`. Because `y,z` are distinct
and both outside `S`, their square contributions are disjoint from the sum over
`S`. This proves the full graph-level aggregate bound without double counting:

```text
sum_v degree_Gᶜ(v)^2
  >= a(a-1)^2 + (2a-1)(t+u) + t^2+u^2.       (E2)
```

## Connectedness bridge

Suppose an outside vertex `y` is a `G`-cross-edge witness for `S` and also has
at least one complement attachment `s in S`. Connectedness gives a `G`-neighbor
`z` of `s`. Independence forces `z` outside `S`, and the complement edge `ys`
forces `z != y`. Thus `z` is a second distinct outside cross-edge witness.

This is precisely the high-attachment branch: if `y` has no complement
attachment, its one-vertex attachment count is zero and the earlier v0.12
bound already applies.

## Formal declarations

The warning-clean file proves:

- `card_sub_one_add_pairAttachments_le_degree`;
- `sum_pairAttachments_eq`;
- `two_outside_energy_certificate`;
- `exists_second_outside_cross_witness`.

No energy or incidence statement is assumed as an axiom. The certificate
predicate is defined locally and then inhabited by the graph-level theorem.

## Relation to v0.13

Method v0.13 independently formalized the exact coordinate optimization:
the E2 package crosses every attachment pair for `alpha=8..11`, with positive
worst margins. This file closes the graph-theoretic E2 obligation and the
second-witness existence branch.

The two artifacts currently use namespace-local but definitionally identical
certificate predicates. Therefore this file records a proved bridge, while a
small adapter/import layer is still needed to state the combined unconditional
`alpha=8..11` theorem in one Lean declaration. No mathematical obligation
remains between the v0.13 optimizer and the v0.14 graph bound.

## Verification

With v0.8--v0.12 dependencies compiled into a temporary module path:

```bash
LEAN_PATH=/tmp/c5k4-proof100-incidence timeout 60s lake env lean \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture100IncidenceEnergy.lean
```

Result: exit code 0 in 9.4 seconds. The artifact contains no `native_decide`,
`sorry`, `admit`, custom axiom, or diagnostic command. Every subprocess stayed
below the mandatory 60-second wall-clock cap.

## Next step

Add a thin integration file importing v0.13 and v0.14, translate the local E2
certificate by unfolding both definitions, and combine:

1. the v0.12 one-witness favorable branch;
2. `exists_second_outside_cross_witness` in the high-attachment branch;
3. `two_outside_energy_certificate`;
4. the v0.13 coordinate optimizer.

That should yield the exact upstream degree-norm conclusion unconditionally
for connected graphs with `8<=alpha(G)<=11`. The remaining range after that
integration would be `4<=alpha(G)<=7`.
