# Erdős 128 Mycielski-shadow Lean extraction

## Theorem

The prospective `M(B2)` trial failed the strict premise because its ten shadow
vertices form an eligible independent set.  The Lean extraction proves this
for every classical Mycielski graph, independently of the input graph.

The local module defines the classical construction on

```text
(Bool x V) + Unit,
```

where `false` is the original level, `true` the shadow level, and `Unit` the
apex.  It proves:

```text
|shadowSet| = |V|,
|V(M(G))| = 2|V|+1,
shadowSet is independent,
2|shadowSet|+1 = |V(M(G))|,
the induced shadow edge count is zero.
```

Therefore the universally quantified strict inequality in the current Formal
Conjectures Erdős 128 premise fails when instantiated at the shadow set.

The reusable abstract theorem is slightly stronger: any finite graph with an
eligible independent set fails the same strict positive-density premise.

## API boundary

Current Formal Conjectures already contains a generalized Mycielski definition
in the Erdős 750 module.  That source file also contains unrelated declarations
proved by `sorry`, so importing it cannot pass this lane's
warnings-as-errors/no-placeholder boundary.  The extraction consequently
defines only the classical construction locally, using the same standard
original/shadow/apex adjacency.  No result from the placeholder-bearing module
is imported or assumed.

This closes the Mycielski transformation direction for Erdős 128.  It does not
prove or disprove the conjecture itself.

## Verification

From the pinned current `formal-conjectures` Lake environment:

```text
timeout 55s lake env lean -DwarningAsError=true \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  /Users/kuber.mehta/Projects/c5-k4/lean/Erdos128MycielskiShadow.lean
```

The command exited zero in 6.1 seconds with no output.  The module contains no
`sorry`, `admit`, custom `axiom`, or native decision procedure.

No commit, push, release, issue, PR, or other public action was performed.
