# Prospective WOWII #133 Heawood edge-contraction report

Date: 2026-08-13 UTC
Status: `HOLD_BOUNDED`; no counterexample candidate

## Wall and frozen move

The closest genuinely new-family point in the earlier #133 search was the
Heawood graph, equivalently the Levi graph of `PG(2,2)`:

```text
maximum induced path = 7
radius = 3
floor(average local independence) = 3
residual = 7 - 3 - 3 = 1.
```

Because Heawood is cubic and triangle-free, every local independence value is
three.  The trial froze one-edge contraction before evaluation.  This minor
operation was meant to compress path-supporting adjacency while retaining
the floor-three correction: the contracted graph is triangle-free with
`n=13,m=20`, so its average local independence is exactly `40/13`.

Girth six proves that a one-edge contraction creates no C4: any new triangle
or C4 through the contracted vertex would lift to a cycle of order at most
five, while any C4 avoiding it was already present.  This transformation is
distinct from the previously tested covers, switches, subdivisions,
pendants, polarity deletions, and cycle chords.  The preregistered details are
in
[`prospective_wowii133_edge_contraction_contract.md`](prospective_wowii133_edge_contraction_contract.md).

## Database gate

The decision-first oracle and the existing exact evaluator agreed on all
1,014 controls: every connected Graph Atlas graph of orders two through seven
plus the established named controls.  There were zero disagreements and zero
timeouts.  The two independently constructed input graphs were then exactly
recomputed and both reproduced `(path,radius,floor(l),R)=(7,3,3,1)`.

## Decision-first result

The 21 edge contractions of each input produced 42 raw graphs but only one
isomorphism class, as expected from Heawood edge transitivity.  Its exact
decision coordinates are

```text
n = 13, m = 20, graph6 = LhcIGCP_GGc@_P
C4 = absent
radius = 2
average local independence = 40/13
floor(local average) = 3
target = radius + floor(local average) = 5.
```

The target oracle immediately found the induced path

```text
[0, 1, 2, 11, 10].
```

That certificate was independently validated.  Under the frozen protocol it
decides the conjecture on this graph, so exact maximum induced-path
optimization was correctly not run.

## Obstruction learned

The contraction preserved the desired floor-three local correction but did
not preserve the other side of the wall: the radius fell from three to two.
The target therefore fell from six to five, and a five-vertex induced path is
immediate.  Edge contraction couples path compression to metric compression
too tightly on the Heawood geometry.  Any next Heawood-local separator must
keep radius three while suppressing all six-vertex induced paths; repeating
edge contraction is not supported.

The append-only evidence is in
[`prospective_wowii133_edge_contraction_ledger.jsonl`](prospective_wowii133_edge_contraction_ledger.jsonl),
and the reproducible runner is
[`scripts/prospective_wowii133_edge_contraction.py`](../../scripts/prospective_wowii133_edge_contraction.py).

No commit, push, release, issue, PR, or other public action was performed.
