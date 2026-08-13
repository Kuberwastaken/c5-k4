# Alon--Tarsi fixed-edge subdivision theorem shadow: Lean extraction

Date: **2026-08-13 UTC**

Status: **WARNING-CLEAN EXACT ARITHMETIC AND CERTIFICATE INTERFACE**

No commit, push, release, issue, PR, or other public action was taken.

## Formal artifact

`lean/AlonTarsiFixedEdgeSubdivisionArithmetic.lean` isolates the theorem
shadow behind the completed Petersen-edge subdivision trial.

The reusable abstract interface is
`SuppressExtendCertificate baseScc subdividedScc t`, with two explicit
fields:

```text
baseScc + t <= subdividedScc   (suppression lower certificate)
subdividedScc <= baseScc + t   (extension upper certificate).
```

Lean proves these imply the exact identity

```text
subdividedScc = baseScc + t.
```

It also proves the general integer residual transport formula: if both the
shortest cover length and edge count increase by `t`, then

```text
(7*subdividedEdges - 5*subdividedScc)
  = (7*baseEdges - 5*baseScc) + 2*t.
```

Using Petersen's exact baseline `(edges,scc)=(15,21)`, the specialized family
has:

```text
scc(G_t)   = 21+t,
|E(G_t)|   = 15+t,
7|E(G_t)|  = 5*scc(G_t) + 2*t,
5*scc(G_t) <= 7|E(G_t)|,
R(G_t)     = 2*t.
```

For every `t>0`, Lean additionally proves the inequality is strict.
`petersen_fixed_edge_subdivision_shadow` packages the equality, inequality,
and exact natural residual in one theorem after receiving the abstract
certificate and edge-count equation.

## Honest adapter boundary

This file does not import or invent a graph-level shortest-cycle-cover
invariant absent from the upstream API.  In particular, it does not claim to
prove inside Lean that:

- suppressing the degree-two path maps every cycle cover to a Petersen cover
  with the required length decrease;
- Petersen has shortest cycle-cover length 21;
- the selected edge can be carried by edge-transitivity to an edge covered
  exactly once in a length-21 cover;
- extending that selected cycle produces a cover of length `21+t`.

Those are precisely the two inequalities carried by
`SuppressExtendCertificate`.  The completed exact computation and explicit
cover witnesses motivate them, but the formal theorem leaves the adapter
visible rather than representing those graph facts as already proved.

## Verification

From `/Users/kuber.mehta/Projects/formal-conjectures`:

```bash
timeout 55s lake env lean -DwarningAsError=true \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  /Users/kuber.mehta/Projects/c5-k4/lean/AlonTarsiFixedEdgeSubdivisionArithmetic.lean
```

Result: exit `0` in approximately 6.0 seconds.  The exact sandwich theorem is
axiom-free; the arithmetic results use only standard Lean/mathlib axioms
(`propext`, `Classical.choice`, and/or `Quot.sound`).  The source contains no
`sorry`, `admit`, `native_decide`, or custom `axiom`.
