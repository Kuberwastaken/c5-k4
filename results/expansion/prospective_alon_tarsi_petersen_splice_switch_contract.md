# Frozen prospective trial: Alon--Tarsi Petersen-splice switches

Date frozen: **2026-08-13 UTC**

This contract was written before any graph in the switch family was evaluated.
The trial is read-only with respect to DeepMind and has no issue, PR, release,
commit, or push authorization.

## Exact live target

Upstream commit: `d16e05aded22b8c467a0a27c14b2311f53185006`.

Source:
`FormalConjectures/Arxiv/2607.06396/AlonTarsi.lean`, lines 50--56,
immutable blob:
<https://github.com/google-deepmind/formal-conjectures/blob/d16e05aded22b8c467a0a27c14b2311f53185006/FormalConjectures/Arxiv/2607.06396/AlonTarsi.lean#L50-L56>.

For every finite simple bridgeless graph `G`, there should be a multiset of
simple cycles covering every edge whose total length `tau(G)` is at most
`(7/5) |E(G)|`.  The cleared crossing condition is

```text
5 * tau(G) > 7 * |E(G)|.
```

The conjecture is existential.  Consequently `tau(G)` means the exact minimum
over all cycle covers, not the length of a merely supplied cover.

## Equality obstruction and labelled carrier

The standard NetworkX Petersen graph has labelled edge set

```text
(0,1) (0,4) (0,5) (1,2) (1,6)
(2,3) (2,7) (3,4) (3,8) (4,9)
(5,7) (5,8) (6,8) (6,9) (7,9).
```

Exact cycle enumeration and edge-mask dynamic programming give
`tau(P)=21=(7/5)*15`.  An explicit optimum has cycle lengths `6,5,5,5`.

The larger equality carrier `H` is the labelled two-edge sum of two Petersen
copies `A={0,...,9}` and `B={10,...,19}`:

1. delete portal edges `a=(0,1)` and `b=(10,11)`;
2. add join edges `p=(0,10)` and `q=(1,11)`.

Roles are frozen as follows: `p` is the switched join edge, `q` is the fixed
join edge, endpoints `0,10` are the switched portals, endpoints `1,11` are the
fixed portals, and every other edge is an internal edge.  `H` is simple,
connected, cubic, bridgeless, has 30 edges, and exact minimum `tau(H)=42`.
The independent lower-bound oracle contracts every crossing cycle back across
the deleted portal edge in each Petersen copy, producing two Petersen covers
of the same total length; hence every cover of `H` has length at least 42.

## One frozen transformation rule

Enumerate the internal edges `e=(u,v)` of `H` lexicographically with `u<v`,
excluding edges incident to either switched portal `0` or `10`.  For each edge,
perform exactly the orientation

```text
delete p=(0,10) and e=(u,v)
add    (0,u) and (10,v).
```

Discard the child if either new edge already exists, if a loop is created, or
if the child is disconnected or has a bridge.  Do not try the reverse
orientation `(0,v),(10,u)`, relabel candidates, tune a switch after observing
results, or expand the family.

This is method-valid because the two-switch preserves vertex degrees and the
edge count.  The conjectured right side therefore remains exactly 42 while
the operation breaks the two-edge-cut decomposition that realizes equality.
The directional prediction is `tau: 42 -> 43` for at least one retained child;
`tau=43` is already a strict crossing because `5*43=215>210=7*30`.

## Exact evaluator, sanity gate, and independent oracle

The evaluator must enumerate all undirected simple cycles canonically by their
edge sets and solve the resulting minimum-weight edge-cover binary ILP with
SciPy/HiGHS.  Every solver call must report optimality.  Repeated copies of one
cycle can be omitted because they cannot cover a new edge.

Before discovery it must reproduce:

- `tau(C3)=3`, `tau(C4)=4`, `tau(C5)=5`;
- `tau(Petersen)=21`, independently by full edge-mask dynamic programming;
- `tau(H)=42`, with the independent Petersen-decomposition lower bound above;
- all connected, nonempty, bridgeless Graph Atlas graphs through order six
  satisfy `5*tau <= 7*|E|`.

Any apparent crossing must be recomputed by an independent branch-and-bound
set-cover solver over the separately enumerated canonical cycles.  It is not a
candidate unless both exact solvers return the same `tau`, the graph is again
verified simple/connected/bridgeless, and the cleared integer inequality is
strict.

## Bounds and stop rules

- One external process cap: **60 seconds**.
- Exactly the switch family above; no adaptive expansion.
- Append one JSON object to the ledger after the gate and after every retained
  candidate, including solver status and cleared residual
  `5*tau-7|E|`.
- Stop immediately on a timeout, non-optimal solver status, oracle mismatch,
  source/status ambiguity, or prior-art hit.
- A crossing triggers independent recomputation and reporting only.  It does
  not authorize any public claim or repository release.

