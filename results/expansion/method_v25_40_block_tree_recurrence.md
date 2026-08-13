# WOWII 40 v0.25: one-vertex block-tree rank recurrence

## Outcome

The exact include/exclude formulas now feed a single block-tree composition
rank.  Define the two branch values by

```text
I = withinIncluding(L,c) + withinIncluding(R,c)
E = within(L.erase c) + within(R.erase c) + 1,
```

and set `blockTreeForestRank = max I E`.  The formalization proves

```text
largestInducedForestSize(G) + 1 = blockTreeForestRank
```

and, using `|L| + |R| = |V(G)| + 1`, derives the exact recurrence

```text
feedbackDeletion(G) + blockTreeForestRank = |L| + |R|.
```

Equivalently, feedback deletion is the complement of the composed state rank
inside the sum of the two side orders.  This is a genuine one-node block-tree
composition theorem: both include and exclude states are consumed, and the
maximum selects the globally optimal branch.

The file then reduces the bipartite `2*tau+1` target exactly to

```text
2 * (|L| + |R| - blockTreeForestRank) + 1
  <= linearForestRank(G).
```

Under that one remaining state inequality, WOWII 40 follows.  The next honest
bridge for recursive induction is to identify `forestOrderWithin G A` (and
its include-cut analogue) with the corresponding invariants of the induced
subtype graph; after that, leaf-block rank increments can be attached to this
state recurrence without ambient/subtype bookkeeping gaps.

## Verification

All 19 modules in the dependency chain were built in topological order into
the fresh `mktemp` directory
`/Users/kuber.mehta/Projects/scratch/c5k4_40_recurrence_final.xfdi2V`.
Every invocation used a fresh explicit olean output,
`-DwarningAsError=true`, and a 60-second process cap; all returned exit code
zero.  The new source contains no `native_decide`, `sorry`, `admit`, `#print`,
or custom axiom.
