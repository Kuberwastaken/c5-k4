# Prospective WOWII 19: independent structural lane

## Outcome

`HOLD_BOUNDED`.

The database-sanity reading passed, but none of the 269 graphs in the frozen
development set crossed current DeepMind WOWII 19. Every retained near-wall
result has exact rational eccentricity data, a local-independence witness, and
an exact maximum induced-bipartite witness. There were no unresolved solves.

This is a negative prospective trial. It is not a disproof, release candidate,
or public claim.

## Frozen question

The trial tested

```text
b(G) >= floor(average_v eccentricity(v)
              + max_v alpha(G[N(v)]))
```

on structural families deliberately separate from the existing #19 proof
ladder: odd-cycle block trees, nonuniform clique/cycle substitutions, and
bounded edge/endpoint surgeries. The complete contract was written before any
database or development graph was evaluated; see
`prospective_wowii19_new_contract.md`.

## Gate results

| Gate | Exact evaluations | Crossings | Tight | Timeouts |
|---|---:|---:|---:|---:|
| Connected Graph Atlas, orders 2--7 | 995 | 0 | 599 | 0 |
| Frozen standard named graphs | 28 | 0 | 13 | 0 |
| Frozen base constructions | 74 | 0 | 19 retained at equality | 0 |
| Deterministic one-surgery constructions | 195 | 0 | 37 retained at equality | 0 |

The base sweep retained 38 graphs at slack at most two: 19 at zero, 9 at one,
and 10 at two. The surgery sweep retained 108: 37 at zero, 42 at one, and 29
at two. A strict crossing would necessarily have been retained, so its absence
is not an artifact of output filtering.

## Exactness and timeout closure

The primary induced-bipartite computation enumerates deletion sets in
increasing cardinality. For larger dense substitutions, a bounded exact MILP
fallback uses two binaries per vertex: one records retention and the other a
two-color. Each retained edge is constrained to have opposite colors, and the
objective maximizes the number retained. Successful solves require the solver
to report an optimum at zero MIP gap, after which the returned induced graph is
independently checked as bipartite.

This fallback closed every initial enumeration timeout. Both final processes
finished within the frozen 60-second process cap, and each fallback solve used
a 10-second cap. The final classification therefore is not `INCONCLUSIVE`.

Representative exact equality certificates are recorded in the JSONL ledger.
For example, graph6 `Ds{` has average eccentricity `8/5`, maximum local
independence 3 witnessed in the neighborhood of vertex 0, right side 4, and
maximum induced-bipartite order 4 witnessed by vertices `[1,2,3,4]`.

## Status and novelty gate

The locally checked current source is
`FormalConjectures/WrittenOnTheWallII/GraphConjecture19.lean`, tagged
`research open`. Because the frozen trial produced no strict crossing, the
mandatory issue/PR/literature novelty audit was not triggered. No commit,
push, release, issue, PR, or other public action was taken.

## Interpretation

The trial found many points on the wall, but the chosen odd-cycle packing and
local-neighborhood separation did not move through it. This is useful negative
evidence for the method evaluation: a prospectively frozen family can generate
substantial tightness without manufacturing a claimed discovery.

Any next #19 trial should be frozen separately and should add a genuinely new
coordinate, rather than expanding these same substitutions after seeing this
result. One plausible direction is a controlled product or lift that changes
average eccentricity without allowing the induced-bipartite witness to absorb
the same added vertices; that direction is not part of this completed trial.
