# Method v0.9: #183 corrected assembly rungs

## Outcome

The corrected `NontrivialRootedTrunkPrinciple` is not merely a renamed
interface: it is satisfiable.  The Lean module proves it for every finite
complete graph by choosing the root singleton as the connected dominating set
and a second vertex as a two-vertex induced-bipartite witness.

This directly tests the correction against the singleton contradiction found
in v0.8.  The side condition `2 <= S.ncard` supplies a genuinely distinct
second vertex, so the proof cannot pass through an empty or contradictory
hypothesis.

The module additionally constructs `OutsideBudgetCertificate` explicitly for
every complete graph and every root `x`: both the connected dominating set and
the outside bipartite witness are the singleton `{x}`.  Consequently it proves
`NontrivialComponentConstruction (completeGraph V) x`.  Thus both the repaired
trunk premise and the repaired end-to-end construction interface have concrete
models.

## Component assembly rungs

The module also proves the two reusable layers needed for a later finite
component fold:

1. bipartite induced witnesses on anticomplete finite vertex sets patch to a
   bipartite witness on their union;
2. if the sets are disjoint, the patched witness order is exactly the sum of
   the two orders and hence gives the corresponding lower bound on `b`;
3. summing `d_i + 1 <= b_i` pays one surplus unit for each nontrivial
   component; and
4. singleton components may be added equally to both sides without consuming
   that surplus.

These statements are honest unconditional theorems.  They do not yet choose
attachment neighbors or prove that the union of the rooted trunks dominates
and connects the ambient graph, so `NontrivialComponentConstruction` remains
the explicit final construction boundary.

## Verification

After compiling the two parent modules into a temporary module directory, the
strict child check was run from the `formal-conjectures` checkout:

```bash
LEAN_PATH=/tmp/c5k4_183_corrected_check_v2 timeout 60s lake env lean \
  -DwarningAsError=true \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture183CorrectedAssembly.lean
```

Result: exit code `0`.  Repository scans found no `sorry`, `admit`, `#print`,
or custom axiom declaration.
