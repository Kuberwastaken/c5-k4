# Alon--Tarsi Petersen-splice switch trials

Date: **2026-08-13 UTC**

Verdict: **HOLD_BOUNDED**.  No counterexample was found.  The forward trial
timed out after six retained candidates and is explicitly incomplete; the
separately frozen reverse-orientation trial completed its entire family.

## Exact current target and status

At live upstream `main` commit
`d16e05aded22b8c467a0a27c14b2311f53185006`, the declaration
`alon_tarsi_short_cycle_cover` remains `@[category research open]` with a
`sorry` in
`FormalConjectures/Arxiv/2607.06396/AlonTarsi.lean`, lines 50--56:

<https://github.com/google-deepmind/formal-conjectures/blob/d16e05aded22b8c467a0a27c14b2311f53185006/FormalConjectures/Arxiv/2607.06396/AlonTarsi.lean#L50-L56>

It says every finite simple bridgeless graph has a multiset of simple cycles
covering every edge with total length at most `(7/5)|E|`.  Thus a disproof
requires the exact minimum cycle-cover length `tau` to satisfy
`5*tau > 7|E|`.

The live GitHub audit found only the merged formalization PR #4850 and its
closed intake issue #4813.  Neither is a proof or counterexample report.  The
primary arXiv source `2607.06396v1`, Conjecture 4, states the same conjecture.
No prior-art counterexample or active solution claim was found by the scoped
repository search.

## Database and exactness gate

Both frozen trials reproduced:

- `tau(C3)=3`, `tau(C4)=4`, `tau(C5)=5`;
- `tau(Petersen)=21=(7/5)*15`;
- `tau(H)=42=(7/5)*30` for the two-Petersen splice carrier;
- zero crossings among all 75 connected, nonempty, bridgeless Graph Atlas
  graphs through order six.

The primary evaluator canonically enumerated all undirected simple cycles and
solved the minimum weighted edge-cover binary ILP with SciPy/HiGHS.  A separate
full edge-mask dynamic program agreed on every Atlas graph and the Petersen
graph.  An explicit Petersen optimum consists of cycles of lengths `6,5,5,5`.
For the splice carrier the two Petersen-side contractions give the independent
lower bound 42, matching the ILP upper bound.

## Forward-orientation trial: timed out honestly

The first contract froze switches

```text
(0,10),(u,v) -> (0,u),(10,v).
```

Its external 60-second process cap expired after the gate and six retained
children.  The append-only ledger preserves the completed results:

- two children had `tau=42`, exact equality;
- four children had `tau=41`, cleared residual `-5`;
- zero crossings appeared before timeout.

The implementation then stopped; the remaining frozen family was not silently
treated as evaluated.  A pre-gate Python-compatibility error (`zip` lacking the
newer `strict` keyword) is also recorded.  Removing that keyword did not alter
the graph family, mathematics, or evaluated data.

## Reverse-orientation trial: complete bounded hold

A second contract was frozen, with its zero-evaluation ledger row persisted,
before evaluating the genuinely distinct reverse orientation

```text
(0,10),(u,v) -> (0,v),(10,u).
```

It retained all **18** labelled children.  Exact graph isomorphism partitioned
them into **four** classes before optimization; every labelled child is still
logged with its representative.  The complete run finished in **33.312039
seconds**, below the 60-second cap.

Results:

- **16** labelled children had `tau=41`, hence
  `5*tau-7|E| = 205-210 = -5`;
- **2** labelled children, `reverse_switch_11_12` and
  `reverse_switch_11_16`, had `tau=42`, exact equality;
- **0** children had positive residual;
- every retained child was rechecked simple, connected, cubic, and bridgeless;
- every HiGHS solve reported proven optimality.

Because there was no apparent crossing, the contract's independent
branch-and-bound crossing oracle was correctly not triggered.

## Interpretation

The Petersen graph and its two-edge sum are real exact/near-equality carriers,
so this is a suitable held-out test of invariant-wall navigation outside the
previous induced-subgraph inequalities.  The predicted crossing did not occur:
the one local degree-preserving operation either preserved the `7/5` wall or
moved one unit to the safe side.  The negative result is method-valid evidence,
not support for claiming the conjecture proved.

The completed reverse lane suggests that this specific cross-edge two-switch
has a compensation mechanism: breaking the visible Petersen decomposition
creates shorter alternative cycles quickly enough to reduce `tau` to 41 in
most isomorphism classes.  Any future trial would require a separately frozen
operation that suppresses those alternative cycles; no further family was
started here.

No commit, push, release, issue, PR, or other public action was performed.
