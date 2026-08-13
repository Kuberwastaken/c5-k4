# Prospective current-DeepMind WOWII 34 trial: bounded hold

## Verdict

`HOLD_BOUNDED` under the contract frozen before evaluation.

No counterexample was found among 215 predeclared constructions of order at
most 24.  There were no induced-path timeouts.  Independent sanity evaluation
also found no crossing among all 994 connected Atlas graphs through order
seven or the 28 standard database graphs.

No public action or novelty claim is warranted.

## Reading clarification

The current Lean inequality is

```text
ceil(distavg(G, center(G)) + distavg(G, maxDegreeVertices(G)))
  <= largestInducedPathOrder(G).
```

Two textual ambiguities were frozen away before search:

- `M` is the maximum-degree vertex set, not the periphery;
- the imported `path G` is the order of a largest induced path, despite the
  conjecture module's prose mistakenly calling it a floor of average distance.

The declaration is tagged `research solved` behind `answer(sorry)`, but the
answer direction is not recorded.  This trial therefore tests the universally
quantified inequality only; it makes no claim about open status.

## Construction sweep

The frozen lanes produced 215 nonisomorphic-by-WL-signature graphs:

- nonuniform clique blowups of paths, cycles, theta-like and complete-bipartite
  bases;
- clique/independent diameter layers with consecutive and alternating
  distance-two joins;
- portal-edge and two-by-two portal joins between clique blocks;
- strong and lexicographic products of small paths, cycles, cliques, and
  related cages.

All graphs were connected and had order at most 24.  Distances and averages
were computed exactly using integer all-pairs distances and `Fraction`; the
ceiling was applied only after exact addition.

Largest induced path was computed exactly by a chord-aware DFS.  A state
contains an induced path's vertex set and one endpoint; a new endpoint is
allowed only when adjacent to the old endpoint and nonadjacent to every earlier
path vertex.  State memoization is sound because those two pieces of data
determine all legal extensions.  The sweep explored 315,686 states/calls in
1.30 seconds, with no timeout.

Exact slack distribution, where

```text
slack = largestInducedPathOrder - ceil(distance sum),
```

was:

| slack | graphs |
|---:|---:|
| 1 | 16 |
| 2 | 91 |
| 3 | 34 |
| 4 | 29 |
| 5 | 22 |
| 6 | 14 |
| 7 | 5 |
| 8 | 1 |
| 9 | 3 |

There were no equality cases and no negative slack.  The closest constructions
had slack one: shortcut-rich three-layer substitutions and small strong/
lexicographic blowups typically had induced path order three against ceiling
two.

## Independent database sanity

The sanity checker did not reuse the discovery path DFS.  For every vertex
subset, it characterized an induced path by checking that the induced subgraph
is connected, has `|S|-1` edges, and has maximum degree at most two.  Searching
subsets from largest to smallest gives the exact maximum.

Results:

```text
994 connected Atlas graphs, orders 3--7: 0 crossings, 0 equality cases
28 standard sanity graphs:             0 crossings, minimum slack 1
```

The standard set comprised `C5--C9`, `P7`, Petersen, `K3,3`, `K7`, stars of
orders three through eight, and complete bipartite graphs `K(a,b)` for
`2 <= a <= 5`, `a <= b <= 6`.

Exact `Fraction` averages were recomputed independently in both sanity runs.

## Reproduction

```text
timeout 60s /home/ec2-user/.venvs/wowii/bin/python \
  scripts/prospective_wowii34_discovery.py
```

The script also passes `py_compile`.  Every invoked process remained below the
60-second cap.

## Interpretation

The proposed mechanism did push the two distance averages upward while dense
substitution kept induced paths short, but not enough to cross.  The same
layering that makes vertices far from the center or maximum-degree set also
provides a geodesic whose one-representative-per-layer vertices form an induced
path.  Chord additions shorten that path, but they simultaneously reduce the
set-distance averages.

That coupled response explains the persistent positive slack and suggests a
theorem shadow: shortest paths from remote layers naturally furnish induced
paths long enough to cover the rounded distance sum.  A future trial should be
frozen around a genuinely different mechanism rather than further tuning these
dense layered families.
