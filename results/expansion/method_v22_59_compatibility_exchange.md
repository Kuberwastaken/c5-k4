# Method v22: WOWII #59 compatibility exchange

Date: 2026-08-13

Local certificate: `lean/GraphConjecture59CompatibilityExchange.lean`

## Outcome

The v21 seven-vertex witness reduces the remaining existence problem to two
finite selection questions.  This checkpoint proves the exact exchange
criterion and identifies the minimal obstruction when it fails.

For candidate pools `P` and `Q`, define

```text
blockedOutside(P) = {p in P | p~x or p~y or p~z},
blockedCore(Q)    = {q in Q | q~a or q~b}.
```

If each blocker set is a proper subset of its pool and the pools are
disjoint, Lean selects distinct vertices `p,q` satisfying

```text
p !~ x,y,z,
q !~ a,b.
```

These are exactly the `OppositeSideCompatible` hypotheses from v21.

## Formal selection lemmas

`exists_outside_side_candidate_of_blocked_lt` proves

```text
|blockedOutside(P)| < |P|
  ==> exists p in P avoiding x,y,z.
```

`exists_core_side_candidate_of_blocked_lt` proves the analogous two-target
selection for `Q`.

`exists_opposite_side_compatible_pair` combines both selections.  Disjoint
pools guarantee `p != q`; no graph-specific distinctness assumption is hidden
in the proof.

Once the candidate pools are also disjoint from the aligned five-set, the
result plugs directly into `seven_le_b_of_aligned_compatible_extensions` from
v21 and yields `b(G)>=7`.

## Exact minimal obstruction

`outside_selection_fails_iff_all_blocked` proves the equivalence

```text
no p in P avoids all of x,y,z
  <->
every p in P hits at least one of x,y,z.
```

Thus failure is not an amorphous global phenomenon: the outside triple covers
the entire candidate pool by its three neighborhoods.  The core-side failure
is the symmetric two-neighborhood cover by `a,b`.

## Relation to the dense-row hypotheses

The established dense-row assumptions control how outside vertices attach to
the `3+3` bipartite core.  They do **not**, by themselves, provide either
strict blocker-cardinality inequality above.  Indeed, density pushes toward
neighborhood covers rather than away from them.

Consequently it would be unsound to claim unconditional compatible `p,q`
existence from the current row hypotheses.  The exact remaining alternatives
are now:

1. one candidate survives each cover, giving `b>=7` by v21;
2. one of the covers is complete.

The complete-cover case is the precise local obstruction that must force the
forest or residue exit.  A useful next lemma should translate a full
three-neighborhood cover of `P`, or a full two-neighborhood cover of `Q`, into
a degree-sequence lower bound or an acyclic exchange witness.

## Lean audit

The new module and its direct v21 dependency were checked in a fresh local
chain with warnings promoted to errors:

```text
LEAN_PATH=/tmp/c5k4-59-v22-audit \
  timeout 60s lake env lean \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture59CompatibilityExchange.lean
```

Result: exit code 0 in 7.9 seconds.

The file contains no native computation, proof holes, or custom axioms.
WOWII 59 is already externally disproved; this is theorem extraction, not a
new counterexample or release candidate.
