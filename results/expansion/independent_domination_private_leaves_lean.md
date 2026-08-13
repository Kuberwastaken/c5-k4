# Private-leaf independent domination formula: Lean report

Date: **2026-08-13 UTC**

Status: **warning-clean formalization; no public action**

Source:
[`lean/IndependentDominationPrivateLeaves.lean`](../../lean/IndependentDominationPrivateLeaves.lean)

## Honest abstraction boundary

The numerical experiment used a clique of centers with positive private-leaf
counts. The graph-specific fact is that every independent dominating set has
one of two structural forms:

1. no center is chosen, forcing every private leaf;
2. one center `i` is chosen, forcing every leaf owned by the other centers.

Rather than hiding that classification inside arithmetic, the Lean module
defines `PrivateLeafCertificate`. A supplied certificate must prove:

- `classify`: every independent dominating set is at least as large as one of
  those modeled choices;
- `realize`: every modeled choice has an actual independent dominating set of
  the stated order.

This is the exact construction-dependent obligation needed to transfer the
generic formula to a concrete graph.

## Compiled results

`privateLeafCost_lower` proves that if `M` is a positive upper bound for every
leaf count and does not exceed their total, then every modeled choice costs at
least

`1 + sum_i p_i - M`.

`privateLeafCost_at_max` proves that a center attaining leaf count `M` realizes
that lower bound.

`indepDominationNumber_eq_of_certificate` bridges an explicit optimum witness
and a universal lower bound to Formal Conjectures' `sInf` definition of
`SimpleGraph.indepDominationNumber`.

`indepDominationNumber_eq_privateLeafFormula` combines the structural
certificate and arithmetic results to prove

`indepDominationNumber G = 1 + sum_i p_i - M`.

Finally, `transferredProfile_indepDominationNumber_eq_twenty` proves that any
graph supplied with the certificate for leaf profile

`(4,6,5,5,5)`

has independent domination number exactly 20.

## Verification

The module compiled against the current Formal Conjectures environment:

```text
timeout 60s lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/IndependentDominationPrivateLeaves.lean
```

Result: success in approximately 6.8 seconds.

The `#print axioms` audit reports only:

- `propext`
- `Classical.choice`
- `Quot.sound`

There is no `sorry`, `sorryAx`, `native_decide`, or custom axiom. The concrete
finite arithmetic uses kernel-checked `decide`, `fin_cases`, `norm_num`, and
`omega` only.

## Scope

This formalizes the exact private-leaf coordinate formula and its graph
adapter. It does not assert that an arbitrary graph with the same degree
sequence has the private-leaf classification. Applying the result to a fully
defined `H(q,p)` graph requires constructing `PrivateLeafCertificate` by
checking the graph's center clique and private-leaf adjacency, which is the
remaining graph-encoding layer rather than an arithmetic gap.
