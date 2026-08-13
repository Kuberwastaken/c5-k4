# Erdős 128 low-separator obstruction: Lean theorem report

Date: **2026-08-13 UTC**

Status: **three theorems compile warning-clean; no public action**

Source: [`lean/Erdos128LowSeparator.lean`](../../lean/Erdos128LowSeparator.lean)

## Strongest honest generalization

The canonical Hajós computation does not justify saying that every Hajós join
destroys the Erdős 128 premise. What it does expose is a general witness
mechanism:

> If two disjoint local pieces form a globally eligible half-order vertex set,
> and their two internal induced-edge budgets plus every separator-crossing
> edge stay at or below the global `n^2/50` threshold, their union refutes the
> universal strict-density premise.

The Lean module formalizes this mechanism without assuming a particular graph
composition.

## Compiled statements

1. `strict_density_premise_fails_of_eligible_edge_bound`

   Any single eligible vertex set whose induced edge count is bounded by `q`
   with `50*q <= n^2` contradicts the current formal premise, which requires
   strict inequality for every eligible set.

2. `strict_density_premise_fails_of_low_separator_union`

   For disjoint finite local pieces `A,B`, if their union is eligible and its
   induced edge count is bounded by `eA+eB+c`, then
   `50*(eA+eB+c) <= n^2` suffices to refute the strict premise. The parameter
   `c` is the complete separator/cross-edge budget.

3. `order_nineteen_two_edge_witness_fails`

   An exact arithmetic adapter for the recorded graph: in an order-19 graph,
   any nine-vertex induced subgraph with at most two edges refutes the strict
   premise. This matches the independently verified Hajós witness.

## Verification

Compiled against the current Formal Conjectures environment with warnings as
errors:

```text
timeout 60s lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/Erdos128LowSeparator.lean
```

Result: success in approximately 6.4 seconds.

The three `#print axioms` checks report only:

- `propext`
- `Classical.choice`
- `Quot.sound`

There is no `sorryAx`, custom axiom, `native_decide`, or `sorry` in the
module.

## Mathematical consequence

The theorem explains why low-order-separator composition is dangerous for the
strict induced-density premise. Eligible-set cardinality is additive across
the two local pieces, while induced edges are only the two local budgets plus
the small crossing budget. If that additive edge budget grows more slowly than
the global quadratic threshold, one explicit union witness defeats the
premise.

For the recorded order-19 canonical Hajós join, the union witness has nine
vertices and only two induced edges, so `50*2=100 <= 361=19^2`. The general
Lean theorem discharges the premise failure from precisely those certified
coordinates.

This is an abstract obstruction theorem. A graph-specific adapter for a broad
composition family would still need to construct `A,B` and prove its induced
edge budget uniformly; this report does not claim that all Hajós joins admit
the same witness.
