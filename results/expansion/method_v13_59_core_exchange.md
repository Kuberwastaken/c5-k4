# Method v0.13: WOWII 59 one-for-one core exchange

Date: 2026-08-13

## Scope

This pass continues structural proof extraction around the hypothetical
low-residue corner

```text
(residue(G), b(G), f(G)) = (3,6,4).
```

WOWII 59 is already externally disproved. This is not a counterexample,
novelty, release, or held-out-success claim.

## Setup

Let `S` be a six-vertex induced bipartite core with `b(G)=6`, let `x` be an
outside vertex, and fix a valid coloring

```text
c : S -> Fin 2.
```

Method v0.12 proved that `x` attaches to both color classes. For a color `k`,
write `A_k(x)` for the attachments of `x` in `S` having color `k`.

## Exact exchange dichotomy

Suppose `|A_k(x)| <= 1`. Because v0.12 guarantees that `A_k(x)` is nonempty,
it has a unique vertex `v`. Delete `v` and insert `x`.

Every remaining neighbor of `x` has color different from `k`; otherwise it
would be a second member of `A_k(x)`. Therefore assigning color `k` to `x`
extends the restricted coloring of `S - {v}`. The exchanged set

```text
T = (S - {v}) union {x}
```

is again an induced bipartite six-set.

This yields the sharp alternative, separately on each side:

```text
either |A_k(x)| >= 2,
or deleting the unique k-colored attachment and inserting x gives a new
bipartite six-core.
```

Equivalently, if no one-for-one exchange through either color is bipartite,
then

```text
|A_0(x)| >= 2 and |A_1(x)| >= 2.
```

Thus every exchange-resistant outside vertex has at least four core
attachments, with at least two on each side. This is strictly stronger than
the v0.12 mixed-parity/two-attachment bound.

## Interaction with `f(G)=4`

When `f(G)=4`, every exchanged bipartite six-core is deletion-critical too:
deleting any one of its vertices leaves a five-vertex induced graph that cannot
be acyclic.

So a sparse-side attachment does not disappear as an exceptional case. It
transports the entire corner structure to a new core containing the outside
vertex. Repeated exchanges therefore give a natural closure process:

- exchange whenever an outside vertex has only one attachment on some color
  side;
- otherwise that vertex is certified to have at least two attachments on each
  side.

No termination or global residue consequence of this process is claimed yet.

## Formal artifact

[`lean/GraphConjecture59CoreExchange.lean`](../../lean/GraphConjecture59CoreExchange.lean)
proves:

1. compatibility of the vacated color after erasing its unique attachment;
2. bipartiteness and exact cardinality six of the exchanged core;
3. deletion-criticality of the exchanged core when `f=4`;
4. the per-color exchange dichotomy;
5. the two-attachments-on-each-side conclusion when all exchanges fail.

The arguments are symbolic graph proofs. This pass uses no bounded search and
no native computation.

## Verification

After compiling the warning-clean v0.8-v0.12 local dependencies into temporary
`.olean` files, the new module was checked with

```text
LEAN_PATH=/tmp lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture59CoreExchange.lean
```

It completed in 7.5 seconds with no warnings or errors. The file contains no
`sorry`, `admit`, custom axiom, `native_decide`, or imported upstream
conjecture proof.

## Remaining universal bridge

The unresolved configurations now split cleanly:

1. **exchangeable:** move to a new deletion-critical six-core containing the
   outside vertex;
2. **exchange-resistant:** the outside vertex has at least four attachments,
   at least two in each color class.

For a `3+3` core such as `K3,3` or `K3,3-e`, exchange resistance leaves only
attachment sizes `2+2`, `2+3`, `3+2`, or `3+3`. These are small enough for an
exact next classification. The likely next theorem is that one of these dense
mixed-parity patterns either produces a five-vertex forest after a compensating
two-vertex deletion or forces a degree-sequence transformation incompatible
with ambient Havel--Hakimi residue three.

## Outcome

`EXACT_CORE_EXCHANGE_DICHOTOMY`.

Universal exclusion is not yet reached, but every outside vertex is now either
absorbed into another deletion-critical core or forced into a dense, finite
attachment-pattern regime.
