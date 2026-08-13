# Method v0.4: WOWII 133 induced-path prepend bridge

Status: **PROVED LOCALLY / NO SORRY**

Date: **2026-08-13 UTC**

Local artifact: `lean/GraphConjecture133Cubic.lean`

This bounded follow-up proves only the representation lemma recommended by
`method_v04_133_extension_bridge.md`.  It does not select a neighbor using
cubicity, use C4-freeness, or claim the one-vertex geodesic extension needed by
the cubic specialization.

## Compiled theorem

```lean
lemma isInducedPath_cons_of_adj_head_of_not_adj_tail {G : SimpleGraph V}
    {a b : V} {xs : List V} (hpath : G.isInducedPath (b :: xs))
    (hab : G.Adj a b) (hafresh : a ∉ b :: xs)
    (hclean : ∀ x ∈ xs, ¬G.Adj a x) :
    G.isInducedPath (a :: b :: xs)
```

The hypotheses isolate exactly the representation obligations for a clean
prepend:

- `b :: xs` is already an induced path;
- the new vertex `a` is adjacent to the old head `b`;
- `a` is fresh, so the enlarged list remains duplicate-free; and
- `a` has no edge to any later vertex in `xs`.

No finiteness, decidable-equality, or nonemptiness assumption is used by the
lemma.

## Proof structure

The nodup component follows by one `List.nodup_cons` decomposition.  For the
indexed adjacency biconditional, the proof eliminates both indices with
`Fin.cases`.

1. At indices zero and zero, graph looplessness gives nonadjacency.
2. At indices zero and one (and symmetrically one and zero), `hab` supplies the
   unique new consecutive edge.
3. At index zero versus an index at least two (and symmetrically), `hclean`
   rules out adjacency and arithmetic rules out consecutiveness.
4. When both indices are positive, removing the leading vertex reduces the
   goal to the complete biconditional in `hpath`.

Thus the theorem establishes the repository-local `isInducedPath` predicate
itself, not a weaker chordlessness condition.

## Verification

Every build and source-search command was capped at 60 seconds.  Final build:

```text
timeout 60s lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture133Cubic.lean
```

Result: exit status `0`.  A temporary `#print axioms` audit reported only
`propext`, `Classical.choice`, and `Quot.sound`; it did not report `sorryAx` or
any project-specific axiom.  The checked source contains no `sorry`, `admit`,
or custom `axiom`.

## Next boundary

The list-representation half of the one-extension step is now closed.  A later
task may select an off-geodesic neighbor `a` of the radius-geodesic head and
prove the freshness and no-later-contact hypotheses needed by this lemma.
That cubic/C4-free selection argument is intentionally outside this task.
