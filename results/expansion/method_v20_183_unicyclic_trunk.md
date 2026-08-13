# Method v0.20: #183 cycle-breaking trunks

## Structural audit

“Unicyclic” alone is not the right one-vertex deletion hypothesis.  If the
chosen cycle vertex is also a cut vertex carrying an attached tree, deleting it
disconnects that attachment.  The exact obstruction is therefore a cycle
vertex whose deletion is disconnected.

The corrected structural condition is `IsGoodCycleBreak H q`:

- `H-q` is connected;
- `H-q` is bipartite; and
- `q` has a neighbor in `H-q`.

For an odd cycle, every vertex is good.  More generally this covers a
unicyclic graph whenever the selected cycle-breaking vertex is not needed to
connect an attached branch and deleting it breaks the only odd cycle.

## Formal result and obstruction

Lean proves that `D=V-{q}` is connected dominating and induced bipartite, with
exact order `|D|+1=|V|`.  However, this is **not** a valid final local package:
the ambient branch must additionally contain its attachment neighbor of `x`.

Lean proves the attachment is outside the flattened trunk and hence

```text
|attachmentBranch| = |D|+1 = |V|.
```

For a genuinely nonbipartite component, every induced-bipartite witness is
proper and has order `<|V|`.  Therefore the local budget is impossible.  This
is formalized as `oneDeletion_budget_impossible`.

Thus even a good non-cut cycle-breaking vertex is one unit too expensive.  A
successful nonbipartite construction must use a connected dominating trunk
omitting at least two vertices while its bipartite witness omits at most one,
or exploit a different branch that avoids paying a separate attachment.

## Verification

The strict command was:

```bash
LEAN_PATH=/tmp/c5k4_183_attachment_selection_v1 timeout 60s lake env lean \
  -DwarningAsError=true \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture183UnicyclicTrunk.lean
```

Result: exit code `0` in 6.5 seconds.  The module contains no `native_decide`,
`sorry`, `admit`, `#print`, or custom axiom declaration.
