# Method v0.2 Trial H1: WOWII 61

Trial frozen in `method_v02_upstream_selection.md`: **2026-08-12 UTC**

This report is an incremental construction-search record. A negative residual
means a counterexample; an empty bounded search is not a truth claim.

## Phase 0: source and reading lock

- Upstream: `google-deepmind/formal-conjectures` at
  `547f309edcc2069c1f61c2465729031c10385540`.
- Module: `FormalConjectures/WrittenOnTheWallII/GraphConjecture61.lean`.
- Declaration: `WrittenOnTheWallII.GraphConjecture61.conjecture61`, category
  `research open`.
- Recovered corpus row: `data/wowii-conjectures.json`, id 61, section
  "2nd run on Lower bounds on the forest number of simple connected graphs".
- Historical marker: `O`, dated March 25, 2004.
- The exact upstream file has SHA-256
  `54620e7b70a9a98eaaf7ce10154f533046b9f6d36fa276c8923c1a7301a7e091`.
- GitHub search found no issue and no target-specific PR for
  `GraphConjecture61` or `Conjecture 61`. The broad open module-reorganization
  PR #4688 is not mathematical work on this declaration.

The source and Lean statement agree without a competing parse:

```text
f(G) >= residue(G) + ceil(diameter(G) / 3)
```

Here `f` is the maximum order of an induced forest, `residue` is the number
of zero terms left by the nonincreasing Havel--Hakimi reduction, and diameter
is the ordinary connected-graph diameter. Define

```text
R61(G) = f(G) - residue(G) - ceil(diameter(G)/3).
```

Status before construction: `UNAMBIGUOUS`.

## Frozen implementation details

The database gate and switch trial use `scripts/method_v02_61_search.py`.
All integer arithmetic is exact. The induced-forest optimizer enumerates
vertex subsets in decreasing order and checks acyclicity; every individual
solve is protected by a 60-second alarm. A second implementation is reserved
for any candidate.

The control universe is fixed before switch evaluation:

- every connected Graph Atlas graph on two through seven vertices (matching
  upstream's `Nontrivial` typeclass);
- `C5`--`C9`, `P7`, Petersen, `K3,3`, `K7`, stars through order 12, and
  complete bipartite graphs through order 12;
- `C5[K2]`, the named unit-slack starting point from Trial H1.

Every nonisomorphic control having exact residual one or two is a
declared switch base. For each base, the search enumerates every connected
graph reachable by at most four two-switches. Each unordered pair of disjoint
edges and both reconnections are considered; invalid, disconnected, duplicate,
and isomorphic outputs are removed. This is the meaning of "canonical
two-switches" in this trial. Degree sequence, and hence residue, is fixed in
each component.

For the highly symmetric 5-regular order-10 component, labelled generation
creates an avoidable duplicate explosion. The implementation instead uses
nauty `geng` to construct the complete connected unlabelled regular class,
builds its quotient two-switch graph exactly, and retains the representatives
at switch distance at most four. This is the same declared search with a
canonical labeller, not a change of bounds.

The extension stratum through order 20 remains conditional: it is entered
only if an order-at-most-12 base reaches equality after a nontrivial switch.
Results are appended to `method_v02_61_search.jsonl` after the gate and after
every completed base/stratum.

## Phase 1: database-sanity gate

**PASS.** The gate evaluated 1,023 distinct applicable controls: all 995
connected nontrivial Atlas graphs through order seven plus the nonisomorphic
named/family controls. There were zero violations. The exact residual
histogram was:

| `R61` | 0 | 1 | 2 | 3 | 4 | 5 |
|---:|---:|---:|---:|---:|---:|---:|
| controls | 156 | 574 | 279 | 8 | 5 | 1 |

This both validates the source-faithful reading and selects 853 named
low-slack controls. Collapsing identical degree sequences gives 228 switch
components.

## Bounded switch result

Outcome: **`HOLD_BOUNDED` with a theorem signal.**

The exact search evaluated 968 nonisomorphic connected realizations at switch
distance at most four from the 228 selected degree-sequence components. There
were no timeouts and no negative residuals:

| exact quantity | value |
|---|---:|
| graphs evaluated | 968 |
| `R61 = 0` | 36 |
| `R61 = 1` | 592 |
| `R61 = 2` | 337 |
| `R61 = 3` | 3 |
| maximum diameter reached | 6 |
| negative residuals | 0 |
| timed-out forest solves | 0 |

The diameter distribution was 448, 417, 92, 10, and 1 graphs at diameters
2, 3, 4, 5, and 6 respectively. No searched graph reached diameter seven.
Every diameter-four graph that lowered the ceiling-adjusted margin to the wall
also admitted the compensating extra forest vertex. For example, `EhU?` has

```text
degree sequence = (3,2,2,2,2,1)
residue = 3, diameter = 4, f = 5
R61 = 5 - 3 - 2 = 0.
```

### Principal `C5[K2]` test

Nauty enumerates 60 connected unlabelled 5-regular graphs of order ten. The
quotient switch graph places 57 of them within four switches of `C5[K2]`, in
layers `1,3,16,28,9`. Every one has diameter two. Their residual histogram is

```text
R61=1: 2 graphs; R61=2: 52 graphs; R61=3: 3 graphs.
```

Thus the predicted coordinate separation does not begin on the declared dense
unit-slack carrier: the fixed degree sequence itself pins diameter at two
through almost the entire realization class, and no graph in the bounded
component reaches equality.

### Conditional extension stratum

Eighteen small degree-sequence components did reach equality after a
nontrivial switch, so the frozen trigger fires literally. They are all order
six or seven controls already exhaustively covered by the Graph Atlas. There
is no corresponding larger base of the same degree sequence to extend through
order 20; changing order necessarily changes the degree sequence and would no
longer be the frozen two-switch experiment. Consequently the extension adds
no graphs rather than silently introducing an unfrozen family.

### Interpretation

The intended move worked only halfway: Havel--Hakimi residue was pinned
exactly, and diameter sometimes crossed from at most three to four, but the
largest induced forest rose by the same unit. Across this exact bounded
universe the persistent compensation is

```text
every three additional distance layers force an additional induced-forest
vertex relative to the fixed residue.
```

This is the theorem signal preregistered in Trial H1. It is not a proof of
WOWII 61. A future trial should first seek a structural relation between
Havel--Hakimi residue, a diameter path, and induced-forest augmentation rather
than widening the switch depth.

The append-only machine record is `method_v02_61_search.jsonl`. The complete
run took 13.84 seconds; all individual exact optimizations remained far below
the 60-second cap.
