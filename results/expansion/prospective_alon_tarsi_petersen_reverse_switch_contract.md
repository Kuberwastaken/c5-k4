# Frozen prospective trial: Alon--Tarsi reverse Petersen-splice switches

Date frozen: **2026-08-13 UTC**.  No candidate below was evaluated before this
contract and its zero-evaluation ledger row were written.  This is a distinct
trial from the timed-out forward-orientation run; that audit remains intact.

## Target and exact orientation

At live upstream commit `d16e05aded22b8c467a0a27c14b2311f53185006`,
`FormalConjectures/Arxiv/2607.06396/AlonTarsi.lean` lines 50--56 states that
every finite simple bridgeless graph has a cycle cover of total length at most
`(7/5)|E|`.  Immutable source:
<https://github.com/google-deepmind/formal-conjectures/blob/d16e05aded22b8c467a0a27c14b2311f53185006/FormalConjectures/Arxiv/2607.06396/AlonTarsi.lean#L50-L56>.

Writing `tau(G)` for the exact minimum cover length, a counterexample requires
`5*tau(G) > 7*|E(G)|`.

## Labelled equality carrier and one frozen rule

Use two standard labelled Petersen graphs on `0..9` and `10..19`.  Delete
`(0,1)` and `(10,11)` and add join edges `p=(0,10)` and `q=(1,11)`.
This simple connected cubic bridgeless carrier has `|E|=30` and exact
`tau=42`, so it lies on the wall.

Enumerate every internal edge `e=(u,v)`, `u<v`, lexicographically, excluding
`p`, `q`, and edges incident with `0` or `10`.  Apply exactly the reverse
orientation

```text
delete (0,10), (u,v); add (0,v), (10,u).
```

Discard collisions, loops, disconnected children, and children with a bridge.
The two-switch preserves degrees and `|E|`; the right side remains 42.  The
directional prediction is that breaking the equality decomposition can raise
`tau` from 42 to 43, which would cross by five cleared units.

All retained labelled children are the complete frozen family.  Exact graph
isomorphism may partition them before optimization because `tau` and every
premise are isomorphism invariants.  The lexicographically first child in each
class is solved; each labelled member is still written individually with its
representative ID.  This performance rule is frozen specifically to remain
inside the 60-second cap and is not a graph-family filter.

## Gates, oracle, and stops

The SciPy/HiGHS binary set-cover ILP over all canonical simple cycles must
reproduce `tau(C3,C4,C5)=(3,4,5)`, Petersen `tau=21`, and carrier `tau=42`.
Edge-mask dynamic programming independently checks the first four values.
The previously frozen database gate is rerun on every connected nonempty
bridgeless Graph Atlas graph through order six; ILP and DP must agree and no
graph may cross.

An apparent crossing is independently recomputed by the separate
branch-and-bound set-cover oracle.  Any non-optimal status, gate disagreement,
oracle mismatch, or external timeout stops the trial.  The whole process is
capped at 60 seconds.  No adaptive expansion and no public or git action is
authorized.
