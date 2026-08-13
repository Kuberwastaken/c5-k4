# Method v0.23 proof extraction: portable odd-unicyclic core

Date: **2026-08-13 UTC**

Status: **blanket theorem proved for an explicit portable cycle-core certificate; generic unique-cycle decomposition remains outside Mathlib**

[`lean/GraphConjecture19OddUnicyclic.lean`](../../lean/GraphConjecture19OddUnicyclic.lean)
defines `OddUnicyclicCoreCertificate G`.  It contains only concrete graph data:

- one cycle vertex whose deletion leaves an induced bipartite graph;
- a maximum-degree vertex;
- a specific diametral shortest path;
- an extra cycle-core vertex outside the path/neighborhood union in the two
  equality-danger configurations of the classical diameter--degree proof.

The last fields are structural surplus witnesses, not numerical inequality
hypotheses.  They express exactly how a unique odd cycle contributes the unit
that distinguishes

```text
diameter + maximumDegree <= n
```

from the universal `<=n+1` bound.

The Lean proof reuses v0.21's unconditional path-neighborhood bounds.  If the
maximum-degree vertex lies on the diametral path, its neighborhood meets the
path in at most two vertices and the supplied cycle-core vertex lies outside
their union.  If it lies off the path, the intersection has at most three;
intersection at most two closes directly, while equality three uses the
supplied vertex outside the union after adjoining the maximum-degree vertex.
Exact Finset cardinality then proves the sharpened order bound.

Combining that bound with the deletion certificate and v0.22 proves WOWII 13
for every graph carrying `OddUnicyclicCoreCertificate`.

## Honest scope boundary

This is a blanket theorem for a portable explicit decomposition class, but not
yet a theorem that every abstract connected odd-unicyclic graph admits the
certificate.  Mathlib has no unicyclic, pseudoforest, cactus, unique-cycle, or
cycle-core API.  Establishing certificate existence from a conventional
edge-count/unique-cycle definition would require a separate foundational
development of the unique cycle and the attached tree components.

No counterexample to the intended structural theorem is known: v0.22 checked
all 54 exhaustive Atlas unicyclic graphs and 5,750 deterministic larger
unicyclic graphs.  This file does not turn that evidence into an axiom or place
the desired dichotomy itself inside the certificate.  Instead it isolates the
strictly structural surplus vertices whose existence the missing unique-cycle
decomposition must provide.

## Trust

Lean compiled with `-DwarningAsError=true`, exit 0, with every subprocess under
60 seconds.  No `sorry`, `admit`, `native_decide`, custom axiom, placeholder,
commit, push, or public action was used.
