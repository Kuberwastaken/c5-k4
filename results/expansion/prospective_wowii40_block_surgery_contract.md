# Frozen prospective trial: current DeepMind WOWII 40 block surgery

Frozen: 2026-08-13 UTC, before evaluating any development graph.

## Database and status gate

The local WOWII corpus entry and the current upstream Lean source agree on:

```text
f(G) >= ceil((p(G) + b(G) + 1) / 2)
```

for a connected nontrivial simple graph, where `f` is maximum induced-forest
order, `p` is the minimum number of vertex-disjoint paths covering every
vertex, and `b` is maximum induced-bipartite order.  The WOWII page marker is
`O`; the current DeepMind declaration is `@[category research open]` with a
`sorry` proof.  The source note records only the proved `p(G)=1` case.

Repository and web/GitHub searches performed before construction found no
recorded #40 counterexample, issue, or pull request.  This is a bounded
prospective search, not yet a novelty claim; any crossing must receive a
fresh source/status/priority audit before being described as new.

## Frozen mechanism

Search outside the prior cactus proof-extraction lane by replacing blocks or
ears nonuniformly so that induced cycles overlap enough to depress `f`, while
the graph remains largely bipartite and fragmented enough to increase `b`
and path-cover number `p`.

## Frozen construction lanes

1. **Block substitutions:** start from paths or small block trees and replace
   selected vertices by independent or complete bipartite blocks; join along
   portals, matchings, or complete bipartite interfaces.
2. **Ear surgeries:** attach ears of lengths 2--5 between nonuniform portal
   pairs in a base cycle, theta graph, or two-block core; optionally replace
   one internal ear vertex by twins.
3. **Nonuniform bipartite block trees:** glue `K(a,b)` blocks at alternating
   left/right cut vertices, with block sizes `2 <= a,b <= 5`, depth at most
   four, nonconstant block sizes, and optional pendant two-edge ears.
4. **One-off mutations:** for every generated graph, add or delete at most two
   interface edges, or split one cut vertex into adjacent/nonadjacent twins.

No family may be added after seeing development results.  Enumeration is
deterministic with seed `4020260813` used only for fixed subsampling.

## Frozen budget and exact evaluation

- At most 1,200 connected graphs, order 3--18.
- At most 60 seconds per process and per exact invariant solve.
- `f` and `b`: exhaustive descending vertex-subset search with explicit
  witnesses; a first witness proves the maximum because all larger subsets
  have already been exhausted.
- `p`: exact subset dynamic programming.  First enumerate every subset whose
  induced ambient graph admits a spanning path (including singletons), then
  minimize the number of disjoint such subsets partitioning the full vertex
  set.  Emit the path-cover vertex orders.
- Any timeout is `INCONCLUSIVE`, never a crossing.
- Log every evaluated graph incrementally before aggregate interpretation.
- Retain all strict crossings and all cases with slack
  `f - ceil((p+b+1)/2) <= 1`.

## Mandatory sanity and crossing gates

Before accepting a strict crossing:

1. independently recompute `f`, `b`, and `p` by a second implementation;
2. emit graph6, edge list, forest/bipartite witnesses, path-cover paths, and
   exhaustive search counts;
3. evaluate every connected Atlas graph through order seven plus standard
   paths, cycles, complete graphs, complete bipartite graphs, Petersen, and
   the historical `C5[K4]` control;
4. reject any formal reading contradicted by the sanity database;
5. rerun the source/status/novelty audit, including current upstream code,
   issues, PRs, and the original WOWII record;
6. append the complete evidence to the ledger before alerting the parent.

No commit, push, release, issue, PR, or other public action is authorized.

## Frozen verdicts

- `CANDIDATE`: strict crossing surviving every mandatory gate.
- `HOLD_BOUNDED`: no crossing within the frozen constructions and budget.
- `INCONCLUSIVE`: any retained candidate whose exact solve times out.
