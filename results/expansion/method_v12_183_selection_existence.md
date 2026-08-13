# Method v0.12: #183 attachment-selection existence

## Interface audit

The v0.11 `AttachmentSelectionInput` requests attachment edges for every
connected component of `G-N(x)`, although its finite list `C` intentionally
contains only the non-root components.  The omitted component containing `x`
is isolated in `G-N(x)` and has no valid attachment through an edge incident
with `x`.  Thus that universal quantification is too broad and cannot serve as
the target of a general existence theorem.

This pass introduces `SelectedAttachmentData`, whose root and attachment edge
conditions are indexed by membership in `C`.  It also records explicitly that
the root component is excluded.

## Existence theorem

Lean proves a general boundary-crossing lemma for walks: a walk starting
outside a set and ending inside it contains an edge crossing into the set.

Apply this to the ambient support of a connected component of `G-N(x)`.  For a
component other than the one containing `x`, ambient connectedness supplies a
walk from `x` into the component.  At the first crossing edge `p-r`, the outside
endpoint `p` must be adjacent to `x`; otherwise `p` itself belongs to
`G-N(x)`, and the edge `p-r` would put it in the same outside component,
contradicting that the edge crosses the support boundary.

Finite classical choice then constructs simultaneously one pair `(p,r)` for
every non-root outside component.  The endpoint is the concrete definition

```text
selectedAttachmentDataOfConnected (G) (hconnected) (x) :
  SelectedAttachmentData G x
```

No claw-free assumption is needed for existence.  Claw-freeness enters later
to prove injectivity of the chosen attachment vertices, as in v0.11.

## Remaining repair

The v0.11 domination/connectivity fold should next be ported from its
over-quantified input to `SelectedAttachmentData` extended with trunks only on
members of `C`.  The corrected nontrivial trunk principle then applies to
non-singleton components, while singleton components receive their own exact
one-vertex payment.

## Verification

After compiling the parent modules into a temporary module directory, the
strict child command was:

```bash
LEAN_PATH=/tmp/c5k4_183_attachment_selection_v1 timeout 60s lake env lean \
  -DwarningAsError=true \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture183SelectionExistence.lean
```

Result: exit code `0` in 8.8 seconds.  The module contains no `sorry`, `admit`,
`#print`, or custom axiom declaration.
