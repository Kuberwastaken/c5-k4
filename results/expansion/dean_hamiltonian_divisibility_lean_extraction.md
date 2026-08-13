# Dean Hamiltonian-divisibility Lean extraction

Date: **2026-08-13 UTC**

Source: `lean/DeanHamiltonianDivisibility.lean`

## Formalized statements

The extraction records the exact theorem boundary used after the completed
Dean `k=5` two-switch trial:

1. `of_hamiltonianCycle`: if a supplied Hamiltonian cycle lies in a finite
   graph and `k` divides the graph order, then the graph has a cycle length
   divisible by `k`;
2. `of_isHamiltonian`: the corresponding graph-level statement for a
   non-singleton Hamiltonian graph;
3. `order_ten_five`: a Hamiltonian graph on ten vertices has the explicit
   cycle length `m=10`, and therefore satisfies the Dean `k=5` conclusion.

The proof uses mathlib's genuine `SimpleGraph.Walk.IsHamiltonianCycle`,
`SimpleGraph.IsHamiltonian`, `SimpleGraph.cycleLengths`, and the library lemma
`IsHamiltonianCycle.length_eq`.  It does not replace graph structure with an
arithmetic certificate.

## Singleton convention boundary

Mathlib defines a singleton graph to be Hamiltonian by convention, although
it has no graph-theoretic cycle.  Consequently the graph-level reusable lemma
explicitly assumes `Fintype.card V ≠ 1`.  The order-ten adapter discharges this
premise arithmetically.  This prevents the extraction from silently claiming
a cycle in the conventional singleton case.

## Connection to the trial

Every graph in the frozen order-ten Dean lane was 5-regular.  Dirac's theorem
explains externally why those graphs are Hamiltonian: their minimum degree is
`5 = 10/2`.  This extraction deliberately does **not** assume, formalize, or
reprove Dirac's theorem.  It certifies the downstream implication needed by
the theorem-shadow: once Hamiltonicity is supplied, the Hamiltonian 10-cycle
is a cycle whose length is divisible by five.

Thus the Lean result supports the trial's fixed-order stopping explanation;
it is not a proof of Dean's general `k=5` conjecture.

## Verification and trust audit

The final warning-as-error command, run from the unmodified
`formal-conjectures` Lake project, was:

```text
timeout 60s lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/DeanHamiltonianDivisibility.lean
```

It passed in **5.45 seconds**, within the required 60-second cap.  The source
contains no `sorry`, `native_decide`, or custom axiom.  `#print axioms` for the
order-ten theorem reported only the standard dependencies
`propext`, `Classical.choice`, and `Quot.sound`.

No public action is authorized by this extraction.
