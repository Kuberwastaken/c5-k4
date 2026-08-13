# Method v26: WOWII #59 deletion-critical core multiplicity

Date: 2026-08-13

Local certificate: `lean/GraphConjecture59CoreProfileMultiplicity.lean`

## Outcome

The v25 audit showed that one large degree has essentially no residue content.
This checkpoint replaces that scalar with the smallest full-profile datum
forced by the `3+3` bipartite six-core and the `f(G)=4` deletion obstruction.

Label the two core color classes by `Fin 3` and encode their nine possible
cross-edges by a mask in `Fin 512`.  Deletion criticality says that deleting
any left or right vertex leaves a rectangle `K2,2`, hence a four-cycle, in the
remaining `2+3` or `3+2` matrix.

Lean proves the exact equivalence

```text
deletion-critical  <=>  at least 8 of the 9 cross-edges are present.
```

It follows that the only descending internal degree profiles are

```text
[3,3,3,3,3,3]
[3,3,3,3,2,2].
```

Equivalently:

- every core vertex has internal degree at least two;
- at least four core vertices have internal degree three;
- with nine edges all six have degree three; and
- with eight edges exactly four have degree three and two have degree two.

There are exactly ten labeled critical masks: `K3,3` and its nine possible
single-edge deletions.

## Relation to `f(G)=4`

The earlier `CornerStructure` certificate proves that if the six-core is an
induced-bipartite witness and `f(G)=4`, every five-vertex core deletion is
cyclic.  In a bipartite graph on sides `2+3` or `3+2`, a cycle must be the
four-edge rectangle encoded here.  The new module additionally constructs an
explicit four-cycle from every such rectangle, so the encoded obstruction has
its intended graph-theoretic meaning.

The reverse translation from an arbitrary Mathlib `IsCycle` in a labeled
five-card to the rectangle coordinates is not composed with
`CornerStructure` in this module.  The exact finite matrix classification is
kernel checked, but claiming a single end-to-end graph theorem before that
interface lemma is written would overstate this checkpoint.

## Why this improves the residue route

The star and split-graph countermodels from v25 defeat statements involving
only one maximum degree.  They do not reproduce this internal multiplicity:
the hypothetical corner carries four or six simultaneously saturated core
vertices, with at most one missing cross-edge.

This gives the residue branch a substantially sharper input.  A next lemma
should combine these six internal lower bounds with the already proved dense
outside attachments.  Each aligned outside row contributes additional degree
to several of the same core vertices, so the descending global profile may
acquire a forced prefix rather than merely a large first entry.

## Lean audit

The new module was checked with the repository-pinned Lean 4.27 toolchain,
warnings promoted to errors, and a 60-second process cap:

```text
ELAN_TOOLCHAIN=leanprover/lean4:v4.27.0 \
LEAN_PATH=/tmp/c5k4-59-v26-fast.FgYBev:/tmp/c5k4-59-v25-final.lDLoc5:/tmp \
timeout 60s lake env lean \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  -DwarningAsError=true \
  -o /tmp/c5k4-59-v26-fast.FgYBev/GraphConjecture59CoreProfileMultiplicity.olean \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture59CoreProfileMultiplicity.lean
```

Result: exit code 0 in under 11 seconds.  The finite classification uses ordinary
kernel reduction with `decide`, not native computation.  The certificate has
no proof holes or custom axioms.

WOWII #59 is already externally disproved; this is theorem extraction, not a
new counterexample or release candidate.
