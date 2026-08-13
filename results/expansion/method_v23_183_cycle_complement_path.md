# Method v0.23: #183 cycle-complement path closure

## Result

`GraphConjecture183CycleComplementPath.lean` proves the concrete family fact
previously isolated as `CyclePairComplementPathProperty`.  Thus the explicit
root-sensitive adjacent pair from v0.22 now has an unconditional proof that
its deletion leaves a connected bipartite graph for every cycle order
`n >= 5`.

The `C3` exception remains separate, exactly as in v0.22.

## Fixed pair `{0,1}`

The retained vertices are enumerated by

```text
Fin (n - 2) -> Fin n
i           |-> i + 2.
```

Lean proves this is an equivalence onto the complement of `{0,1}`.  It then
proves the induced cycle adjacency relation is exactly `pathGraph (n - 2)`.
The only delicate arithmetic point is excluding modular wrap: between values
in `2, ..., n-1`, a modular difference of one is an ordinary difference of
one when `n >= 5`.

The resulting graph isomorphism transports `pathGraph_connected` and
`pathGraph.bicoloring` to the induced complement.

## Fixed pair `{2,3}` and the root-sensitive choice

Translation by two on `Fin n` restricts to an equivalence

```text
complement {0,1}  ≃  complement {2,3}.
```

Cancellation in the additive group `Fin n` proves that translation preserves
the cycle adjacency relation, so it upgrades to an isomorphism between the two
induced complements.  Connectivity and bipartiteness therefore transfer to
the `{2,3}` branch as well.

A final case split on `rootSensitiveCyclePair` proves
`cyclePairComplementPathProperty : CyclePairComplementPathProperty`.

## Verification

The full recursive dependency chain was compiled from source into the fresh
directory `/tmp/c5k4_183_path_audit.AVX4t1`.  Each module used:

```bash
LEAN_PATH=/tmp/c5k4_183_path_audit.AVX4t1 timeout 60s lake env lean \
  -DwarningAsError=true \
  -o /tmp/c5k4_183_path_audit.AVX4t1/<MODULE>.olean \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  /Users/kuber.mehta/Projects/c5-k4/lean/<MODULE>.lean
```

All modules, including `GraphConjecture183CycleComplementPath`, exited `0`
with no Lean output.  Every invocation was individually capped at 60 seconds.
The new module contains no `sorry`, `admit`, `native_decide`, `#print`, or
custom axiom declaration.
