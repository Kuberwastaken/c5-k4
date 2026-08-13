# Independent-domination leaf-transfer Lean extraction

Date: **2026-08-13 UTC**

Source: `lean/IndependentDominationLeafTransferCoordinates.lean`

## Formalized boundary

The extraction defines the two sides of the current upstream even-degree
declaration in its original orientation:

`(D+2)^2 * i <= (D^2+4) * n`.

It packages exact safe-side slack as

`(D+2)^2 * i + slack = (D^2+4) * n`

and proves a generic adapter from that equality to the inequality.  For the
completed transformed trial coordinates `(n,D,i)=(30,10,20)`, Lean proves:

- `Even 10`;
- `144*20 <= 104*30`;
- `144*20 + 240 = 104*30`;
- equivalently, `104*30 - 144*20 = 240`.

## Graph certificate boundary

The graph-level theorems take the exact invariant facts

`Fintype.card V = 30`, `G.maxDegree = 10`, and
`G.indepDominationNumber = 20`

as explicit premises.  From them they transfer parity, the upstream-oriented
inequality, and the exact residual.  They do not construct the leaf-transfer
graph or pretend that arithmetic proves its independent domination number.
Those invariant certificates remain the responsibility of the completed
exact trial and its structural/MILP audit.

## Verification

The final warning-as-error build was run from the unmodified
`formal-conjectures` Lake project under the required cap:

```text
timeout 60s lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/IndependentDominationLeafTransferCoordinates.lean
```

It passed.  The source uses no `sorry`, `native_decide`, or custom axiom.
`#print axioms` on the residual adapter reported only the standard dependencies
`propext`, `Classical.choice`, and `Quot.sound`.

This is a hold/slack certificate, not a disproof or proof of the universal
independent-domination conjecture.  No public action is authorized.
