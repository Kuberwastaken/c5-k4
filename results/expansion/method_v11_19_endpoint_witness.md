# Method v0.11 proof extraction: WOWII 19 endpoint witness

Date: **2026-08-13 UTC**

Status: **explicit finite witness assembly proved in warning-clean no-`sorry` Lean**

[`lean/GraphConjecture19EndpointWitness.lean`](../../lean/GraphConjecture19EndpointWitness.lean)
closes the representation layer left by method v0.10.  It takes an independent
neighborhood layer `A` and an explicitly alternating-colored retained tail
`Q`, proves that the induced graph on `A union Q` is bipartite, proves the exact
disjoint-union cardinality, and inserts the witness into the repository's
`sSup` definition of `b`.

The endpoint theorem automatically extracts a maximum independent set from
`N(u)`.  Given a retained-tail certificate with

```text
|Q| = diameter(G),
Q intersects N(u) trivially,
Q has a valid alternating coloring,
every A--Q edge lands in the nonzero color of Q,
```

it proves the stronger exact bound

```text
b(G) >= diameter(G) + indepNeighborsCard(G,u).
```

It also exports the immediate WOWII 13-shaped corollary with the final
subtraction by one.

This is deliberately certificate-parametric.  Method v0.10 already proves the
graph-theoretic facts needed for the canonical choice
`Q={x_0,x_2,...,x_d}`: shortest-path chordlessness, non-overlap with `N(u)`,
and absence of cross edges beyond `x_2`.  The only remaining endpoint-local
step is packaging those indexed vertices and their parity into the certificate
interface.  The global WOWII 13 obstruction remains separate: a
`lambda`-maximizing vertex need not be assumed diametral, so a full proof still
needs a max-to-endpoint coupling or max-minus-one endpoint lemma.

Build audit:

```text
lake env lean -R .../c5-k4/lean -DwarningAsError=true \
  .../GraphConjecture19EndpointWitness.lean
```

Result: **exit 0**.  There is no `sorry`, `admit`, custom `axiom`, or embedded
`#print`; no upstream conjecture theorem is imported.
