# Method v0.13: #183 corrected attachment/trunk fold

## Outcome

The v0.11 construction has now been ported completely to the corrected
attachment interface from v0.12.  Every root, attachment edge, trunk condition,
and connectivity argument is indexed only by membership in the selected
non-root component set `C`; the isolated component containing `x` is never
asked to provide an impossible attachment edge.

Lean proves:

- every corrected attachment/rooted-trunk branch is connected;
- the finite union of all branches with `x` is connected;
- that union dominates all ambient vertices;
- under claw-freeness, attachments selected for distinct outside components
  are distinct, so the attachment image has cardinality `|C|`; and
- corrected trunk data converts through the v0.10 component fold into the
  exact `OutsideBudgetCertificate` consumed by the invariant-transfer theorem.

## Remaining exact boundary

`LocalCorrectedTrunkData` contains no global connected-domination premise and
no aggregate cardinality premise.  It asks only for rooted trunks and
component-supported bipartite witnesses, together with the local inequalities
`|T_c|+1 <= |B_c|` and the root witness inequality `1 <= |B_root|`.

The aggregate arithmetic is now also discharged.  Lean proves that the
selected set costs at most one for `x`, plus `|T_c|+1` for every selected
component.  Therefore local bounds `|T_c|+1 <= |B_c|`, together with a
one-vertex witness in the root component, imply the full displayed inequality.
The certificate fold now includes the root component explicitly, so its
singleton witness pays exactly for the global vertex `x`.

`correctedTrunkDataOfLocal` derives the formerly caller-supplied
`card_le_sum`, and `outsideBudgetCertificate_of_localCorrectedTrunks` produces
the final outside certificate directly from this local interface.

The only remaining issue is actual local construction.  The corrected
nontrivial trunk principle supplies the needed rooted trunk and budget on
components of order at least two; selected singleton components still require
their own explicit trunk/witness construction and local payment proof.

## Verification

After compiling the parent modules into a temporary module directory, the
strict child command was:

```bash
LEAN_PATH=/tmp/c5k4_183_attachment_selection_v1 timeout 60s lake env lean \
  -DwarningAsError=true \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture183CorrectedFold.lean
```

Result: exit code `0` in 10.8 seconds.  The module contains no `native_decide`,
`sorry`, `admit`, `#print`, or custom axiom declaration.
