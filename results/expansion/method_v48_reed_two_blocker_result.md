# Reed adjacent two-blocker: stopped at theorem-domain audit

Date: **2026-08-13 UTC**

Status: **stopped before transformed invariant evaluation**

## Carrier-coloring result

Exact enumeration found 9,720 labeled optimal eight-color partitions of
`C5[K3]`. Each consists of seven independent pairs and one singleton, and
each of the 15 vertices occurs as singleton in exactly 648 partitions.

This precisely explains the failed v47 blocker: every vertex omitted from its
neighborhood can be the sole reusable singleton color.

A deterministic CNF set-cover then sought two adjacent blocker vertices whose
available carrier colors could never be distinct. Two stronger coordinate
budgets were proved infeasible:

- `Delta<=9, omega<=6`: UNSAT;
- `Delta<=10, omega<=6`: UNSAT.

The first SAT budget with total coordinate growth at most three was
`Delta<=10, omega<=7`. Its frozen first model was

- `N(x)-{y} = B0 union B1 union B4`;
- `N(y)-{x} = B2 union B3 union B4`.

This model was frozen before constructing or evaluating the transformed
graph.

## Mandatory stop

The theorem-domain audit found that the frozen 17-vertex graph has
independence number 2. It therefore cannot contain an induced claw. A direct
claw scan found none, and an independent exhaustive scan of all four-vertex
subsets confirmed zero induced claws.

Thus the gadget fails the preregistered requirement that it escape the
claw-free class. Reed's conjecture is already proved for this class by King
and Reed (2014), DOI `10.1002/jgt.21797`.

Per protocol, the lane stopped immediately:

- transformed exact `chi/omega/Delta` evaluation: **not run**;
- adaptive neighborhood changes: **none**;
- counterexample or novelty claim: **none**;
- public action: **none**.

The negative result is still informative. Merely covering every old-color
reuse pattern can make the blockers eliminate the carrier's independent
triples as well, returning the construction to the proved `alpha<=2`
subclass. Any new trial must include an induced-claw constraint directly in
its frozen selection model rather than checking it only after selection.
