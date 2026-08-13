# Prospective WOWII 291 trial: bounded hold

## Verdict

`HOLD_BOUNDED` under the contract frozen before evaluation in
`prospective_wowii291_contract.md`.

No counterexample to the current DeepMind statement was found among 66 frozen
base constructions or 19,583 distinct degree-preserving surgery graphs.  The
independent database-sanity pass also found no crossing among all 994 connected
Atlas graphs of orders three through seven or the 28 predeclared standard
sanity graphs.

This is a prospective negative result, not evidence that WOWII 291 is proved.
No public action or novelty claim is warranted.

## Evaluated mechanism

The frozen search tested three predeclared lanes:

1. nonuniform paths of clique blocks;
2. regularized paths and cycles of sparse portal-connected clique blocks;
3. connected degree-preserving two-switch surgeries of the first two lanes.

For each graph the discovery code computed:

- the full descending degree sequence;
- the canonical Havel--Hakimi trace and first zero/empty step, counted from
  zero exactly as in the current Lean declaration;
- every vertex triangle-incidence count and the frequency of its minimum;
- a total-dominating-set certificate.

The fast total-domination phase starts from all vertices and deletes vertices
while retaining total domination under several deterministic orders.  Every
evaluated graph produced a witness of size at most

```text
k_zero + freqMinTriangles.
```

Such a witness is already an exact certificate that the graph is not a
crossing, so no ILP escalation was required.  There were no CBC timeouts.

## Results

| lane | evaluated | strict crossings | exact near-wall retained | timeouts |
|---|---:|---:|---:|---:|
| nonuniform clique-block paths | included below | 0 | 0 | 0 |
| regularized sparse clique blocks | **66 base total** | 0 | 0 | 0 |
| degree-preserving two-switch surgery | **19,583** | 0 | 0 | 0 |

The surgery run remained below the frozen 20,000-graph cap.  It used seed
`29120260813` and at most 400 lexicographically generated, deterministically
shuffled valid switches per eligible seed.  Since a two-switch preserves the
degree sequence, every child retained its parent's Havel--Hakimi zero step;
the lane varied triangle-frequency and total-domination geometry around that
fixed term.

None approached the wall closely enough to require exact ILP evaluation.
Structurally, portal-connected clique blocks make total domination moderately
large, but they also create a minimum triangle-incidence class large enough to
cover it.  Two-switch surgery moves the triangle classes, yet the graphs still
admit small explicit total-dominating sets.

## Database-sanity gate

An independent code path recomputed the current reading on every connected
NetworkX Atlas graph of orders three through seven:

```text
994 checked, 0 crossings.
```

Total domination was computed by exhaustive subset enumeration, not the
discovery ILP or deletion heuristic.  The Havel--Hakimi zero step was also
implemented independently.

The same independent checker evaluated 28 standard graphs:

- `C5` through `C9`;
- `P7`, Petersen, `K3,3`, and `K7`;
- stars of orders three through eight;
- complete bipartite `K(a,b)` for `2 <= a <= 5` and `a <= b <= 6`.

Again there were zero crossings.

One transient sanity command incorrectly iterated the keys of NetworkX's
triangle-count dictionary rather than its values, making every triangle-free
graph appear to have frequency one and spuriously printing `P7`.  The error was
recognized immediately because triangle-free graphs must have minimum
frequency equal to their order.  That output was discarded, the independent
command was corrected, and the append-only ledger records the correction.

## Reproduction

Discovery entry point:

```text
/home/ec2-user/.venvs/wowii/bin/python \
  scripts/prospective_wowii291_discovery.py --lane base

/home/ec2-user/.venvs/wowii/bin/python \
  scripts/prospective_wowii291_discovery.py --lane surgery --surgery-limit 400
```

Both were executed under external 60-second process caps.  The base run took
1.14 seconds.  The final surgery run took 13.47 seconds.

## Research interpretation

The frozen hypothesis was directionally sensible but did not cross the
conjecture.  Clique blocks increase total domination only by creating many
locally similar vertices, and that same similarity inflates the frequency of
the minimum triangle count.  Degree-preserving surgery did not separate those
coordinates enough.

A future prospective trial should therefore avoid further tuning of this
frozen family.  A genuinely new mechanism would need unique or very
low-frequency triangle signatures at many domination-forcing gadgets, without
allowing one portal vertex to dominate an entire gadget.  Such a trial should
be frozen separately before evaluation.
