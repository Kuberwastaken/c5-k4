# Method v0.17 proof extraction: WOWII 19 odd-cycle-transversal charge

Date: **2026-08-13 UTC**

Status: **general `b >= n-tau_odd` and exact WOWII 13 charge theorem proved; no failure in 5,516 deterministic order-8--10 controls**

## General theorem

[`lean/GraphConjecture19OddCycleTransversal.lean`](../../lean/GraphConjecture19OddCycleTransversal.lean)
defines `oddCycleTransversalNumber G` as the minimum cardinality of a vertex
set whose deletion leaves an induced bipartite graph.  It proves attainment of
that minimum and the general bound

```text
b(G) >= |V(G)| - tau_odd(G).
```

More strongly, it retains an arbitrary explicit transversal certificate `T`
and proves the exact sufficient charge

```text
|T| + diameter(G) + localMax(G) <= |V(G)| + 1
                         ==> WOWII 13.
```

The minimum-transversal-number form follows immediately.  This is precisely
the accounting suggested by the v0.16 multi-arm residuals: vertices outside a
diametral spine pay both for the large local independent neighborhood and for
the vertices removed to eliminate odd cycles.

## Deterministic bounded controls at orders 8--10

Because the local Graph Atlas ends at order seven and no `geng` binary is
installed, the next control was a deterministic seeded sample.  For each
`n in {8,9,10}` and each
`p in {0.12,0.20,0.30,0.40,0.50,0.60,0.75,0.90}`, up to 250 connected
`G(n,p)` graphs were accepted from a fixed PRNG seed `19017`.  This produced
5,516 connected graphs.

Every quantity was exact:

- neighborhood independence by exhaustive subset enumeration;
- diameter by exact shortest paths;
- `tau_odd` by cardinality-ordered exhaustive deletion sets and an exact
  bipartiteness test.

No charge violation was found:

```text
tau_odd + diameter + localMax <= n+1
```

held on all 5,516 controls.  Equality occurred repeatedly, including sparse
order-eight trees with `(tau,d,M)=(0,4,5)` and `(0,5,4)`.  This is a bounded
hold, not a proof and not exhaustive enumeration of all unlabeled graphs at
orders 8--10.

## Exact remaining gap

The full WOWII 13 problem is now reduced to proving the transversal charge
inequality itself:

```text
tau_odd(G) + diameter(G) + localMax(G) <= |V(G)| + 1.
```

Equivalently, a general multi-arm decomposition must find an odd-cycle
transversal whose cost is absorbed by surplus vertices beyond a diametral path
and a maximum independent neighborhood.  The current bounded evidence includes
all connected graphs through order seven and 5,516 deterministic controls at
orders 8--10, with no counterexample.

## Trust

The sampler completed in 16 seconds and every subprocess stayed below 60
seconds.  Lean compiled with `-DwarningAsError=true`, exit 0.  No
`native_decide`, `sorry`, `admit`, custom axiom, commit, push, or external
action was used.
