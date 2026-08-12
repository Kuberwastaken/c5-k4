# Breakthroughmaxxing target cross-sweep

Date: 2026-08-12. Discovery source: the tracked documentation in the
read-only checkout `/Users/kuber.mehta/Projects/breakthroughmaxxing`.

## Protocol and scope

This pass asks whether the existing `c5-k4` arsenal also refutes explicit
universal graph statements independently catalogued by the
`breakthroughmaxxing` campaign. It applies the four handoff gates: exact
hypotheses and conventions, the connected Graph Atlas database through order
7 plus named controls, an independent recomputation of every apparent
violation, and a current-status/novelty check. Spectral comparisons use a
`1e-6` guard and any optimization call is capped at 60 seconds.

The source checkout is used read-only. Temporary computations live under
`/tmp`. This report is appended one audited statement at a time.

## Corpus cross-check

The discovery checkout has 13,683 tracked files. Its high-yield inventories
are `01-scope/legendary-weakspot-scout-2026-07-24/RANKED_TARGETS.md`,
`01-scope/false-sibling-transfer-2026-07-24/README.md`,
`01-scope/recent-object-ammunition-2026-07-24/{CANDIDATES,RANKING}.md`, and
`07-marlin/STRATEGY.md`. The 11,048-file `07-marlin` tree is mostly completed
run artifacts rather than additional conjecture statements.

All numbered WoW-I and WoW-II targets appearing in that checkout are already
covered by this repository's complete 587-entry and 522-entry sweeps. The
AutoGraphiX and TxGraffiti/Optimist lists are also already complete here. They
are excluded rather than double-counted.

## Ranked manifest

| rank | statement | why it can use this arsenal | initial state |
|---:|---|---|---|
| 1 | Dean cycle divisibility (`delta(G) >= k >= 3` gives a cycle of length divisible by `k`; only `k=5` open in the source lock) | direct exact cycle predicate; dense carrier family and triangular graphs admit `k=5` | queued |
| 2 | graphical multiplicative Merino--Welsh (`max(alpha_acyclic, alpha_totally_cyclic) >= tau`) | direct deletion/contraction evaluation on the smaller arsenal members; false matroid sibling | queued |
| 3 | Erdős--Gyárfás power-of-two cycle conjecture | direct cycle predicate on every arsenal graph with minimum degree at least 3 | queued |
| 4 | Reed's chromatic bound | `chi`, `Delta`, and `omega` are already core arsenal invariants; the carrier is known to sit near this wall | queued |
| 5 | Total Coloring Conjecture (`chi'' <= Delta+2`) | finite coloring certificate; evaluate manageable arsenal members with a 60-second cap | queued |
| 6 | Erdős--Nešetřil strong chromatic-index bound | finite coloring predicate on squared line graphs | queued |
| 7 | Tutte's nowhere-zero 5-flow conjecture | applies to bridgeless arsenal graphs and has an exact modular-flow predicate | queued |
| 8 | Lovász vertex-transitive Hamilton-path conjecture | every main arsenal member is vertex-transitive; Hamilton paths are direct certificates | queued |
| 9 | Hadwiger's clique-minor conjecture | carrier chromatic numbers exceed the proved small-colour cases, while explicit branch-set certificates are finite | queued |
| 10 | Fan--Raspaud three-perfect-matching conjecture | exactly three named arsenal controls are bridgeless cubic graphs | queued |
| 11 | Petersen-colouring conjecture | same three bridgeless cubic controls; edge-map certificates are finite | queued |
| 12 | Dominating Cycle Conjecture | the cubic controls are admissible; a cycle is a direct certificate | queued |

Other ranked source targets are not admissible for these fixed objects
(trees, digraphs, planar cubic graphs, polytopes, hypergraphs, Latin squares,
matroids not represented by a campaign graph, or algebraic objects), or they
are existence/non-uniqueness questions for which a single arsenal graph cannot
be a counterexample. Ordinary Cycle Double Cover is excluded because the
source's July 2026 audit marks it resolved.

## Evaluations

### 1. Dean cycle divisibility — HOLD

Source-lock statement: every graph of minimum degree at least `k >= 3` has a
cycle whose length is divisible by `k`; the discovery source records `k=5` as
the only open case on 2026-07-25. Every arsenal graph with minimum degree at
least five has an explicit 5-cycle. This includes all `C5[K_m]` members,
`C7[K3]`, `C9[K3]`, `T(7..9)`, and `comp(C5[K4])`. Representative vertex
cycles in the campaign's integer labelling are:

- `C5[K4]`: `(0,19,18,17,16)`;
- `T(7)`: `(0,18,20,16,17)` in NetworkX's deterministic relabelling;
- `comp(C5[K4])`: `(0,15,7,19,11)`.

A bounded simple-path DFS found each cycle and a separate edge-by-edge replay
checked distinct vertices, closure, and all five edges. The carrier therefore
does not disprove Dean's conjecture. No optimization or floating-point
comparison is involved.

### 2. Graphical multiplicative Merino--Welsh — BOUNDED HOLD

Exact source-lock statement for a connected bridgeless graph is
`alpha(G) * alpha*(G) >= tau(G)^2`, where the three quantities count acyclic
orientations, totally cyclic orientations, and spanning trees. The 2026 source
audit still lists the graphical statement as open; the 2024 counterexamples
are nongraphic matroids and therefore do not settle this target.

An exact subset-rank specialization of the Tutte polynomial evaluated the
small named controls and the smallest carrier-family member. Matrix-tree
Bareiss elimination independently supplied `tau`:

| graph | `alpha` | `alpha*` | `tau` | multiplicative slack |
|---|---:|---:|---:|---:|
| `K4` | 24 | 24 | 16 | 320 |
| `K3,3` | 230 | 102 | 81 | 16,899 |
| Petersen | 16,680 | 1,920 | 2,000 | 28,025,600 |
| `C5[K2]` | 183,360 | 17,099,904 | 311,040 | 3,038,692,515,840 |

The `C5[K2]` product is about `32.409` times `tau^2`, nowhere near the
boundary. Exact general Tutte evaluation is exponential in the edge count, so
the denser family members were not mislabeled as tested. This admissible
bounded screen finds no disproof and supplies no candidate requiring the
database or novelty gates.

### 3. Erdos--Gyarfas power-of-two cycles — HOLD

The source-lock statement requires every finite simple graph of minimum degree
at least three to contain a simple cycle of length `2^j` for some `j >= 2`.
Every applicable arsenal member has such a cycle. All carrier-family,
triangular, complement-carrier, `K4`, and `K3,3` instances already contain a
4-cycle. Petersen, the only arsenal graph without one, contains the explicit
8-cycle `(0,5,8,6,9,7,2,1)`.

The same bounded path enumerator used for the Dean check searched lengths
`4,8,16,32` in increasing order; a separate replay checked vertex uniqueness,
edge incidence, closure, and the power-of-two length. The source inventory's
2026 frontier starts beyond 17 vertices generally and beyond 29 for cubic
graphs, but the 20--40 vertex carrier objects are not near misses: all except
Petersen fail immediately at length four. No disproof is present.

### 4. Reed's chromatic bound — HOLD (carrier family is sharp)

The target is `chi(G) <= ceil((Delta(G)+1+omega(G))/2)`. Exact maximum-clique
enumeration and replayed proper-colouring certificates establish the bound on
the entire arsenal. The informative cases are the clique blow-ups:

| family | certified colouring | Reed RHS | verdict |
|---|---:|---:|---|
| `C5[K_m]`, `m=2,3,4,5,6,8` | `ceil(5m/2)` | `ceil(5m/2)` | equality |
| `C7[K3]` | 7 | 8 | strict |
| `C9[K3]` | 7 | 8 | strict |
| `T(7),T(8),T(9)` | at most 8, 7, 10 | 9, 10, 12 | strict |
| `comp(C5[K4])` | 3 | 6 | strict |
| Petersen, `K3,3`, `K4` | 3, 2, 4 | 3, 3, 4 | hold |

For `C5[K_m]`, each colour class meets at most two nonadjacent blobs, proving
the matching lower bound `chi >= ceil(5m/2)`; explicit cyclic colour-set
assignments attain it. Thus the original carrier is exactly sharp
(`chi=10`, RHS `10`) rather than a counterexample. Every stored colouring was
separately replayed across all edges. There is no numerical or optimization
ambiguity and no violation to promote through the novelty gate.

### 5. Total Coloring Conjecture — HOLD where solved; four capped UNKNOWN

The exact predicate is a proper colouring of the total graph (original
vertices and edges, with incidence and adjacency conflicts) using at most
`Delta+2` colours. A binary feasibility model fixed the `Delta+1`-vertex
incidence clique at vertex zero to canonical colours, used one thread, and
capped every CBC call at 60 seconds. Returned assignments were replayed
directly against every conflict edge.

| verdict | arsenal members |
|---|---|
| certificate found | `K4`, `K3,3`, Petersen, `C5[K2]`, `C5[K3]`, `C5[K4]`, `C7[K3]`, `C9[K3]`, `T(7)`, `comp(C5[K4])` |
| 60-second UNKNOWN | `C5[K5]`, `C5[K6]`, `T(8)`, `T(9)` |
| process cap before verdict | `C5[K8]` |

For the carrier itself the replayed 13-colouring has class sizes
`10,10,10,10,10,9,11,10,10,10,10,10,10`; its total graph has 130 vertices.
The complement carrier has a replayed 10-colouring of its 100-vertex total
graph. The UNKNOWN rows are neither positive nor negative evidence. Thus the
main carrier does not disprove Total Coloring, and this bounded pass exposes no
candidate counterexample.

### 6. Erdos--Nesetril strong chromatic-index bound — HOLD

The conjectured bound is `5 Delta^2/4` for even `Delta` and
`(5 Delta^2-2 Delta+1)/4` for odd `Delta`. For eleven arsenal graphs,
including every `C5[K_m]` member and the original carrier, the number of edges
itself is no larger than the bound, so assigning a distinct colour to every
edge is already a formal certificate. The only nontrivial rows were coloured
on `L(G)^2` and replayed conflict-by-conflict:

| graph | `Delta` | edges | bound | certificate colours |
|---|---:|---:|---:|---:|
| `C7[K3]` | 8 | 84 | 80 | 42 |
| `C9[K3]` | 8 | 108 | 80 | 36 |
| `T(9)` | 14 | 252 | 245 | 94 |
| Petersen | 3 | 15 | 10 | 5 |

In particular `C5[K4]` has only 110 edges against a bound of 146, while its
complement has 80 edges against a bound of exactly 80. All cases hold with
large or elementary margins; no 60-second optimization was needed.

### 7. Tutte nowhere-zero 5-flow — HOLD

Every arsenal member is bridgeless, so every one meets the conjecture's exact
hypothesis. Orienting each edge from its lower to higher integer endpoint, a
spanning-tree construction assigned nonzero values in `Z/5Z` to the chords
and solved the tree-edge values by leaf elimination. A distinct replay then
checked that every edge value lies in `{1,2,3,4}` and that signed incident
values sum to zero modulo five at every vertex.

All 15 arsenal graphs received exact witnesses, from 6 assigned values on
`K4` through 460 on `C5[K8]`. For `C5[K4]`, the value multiplicities
`(1,2,3,4) = (32,28,21,29)` cover all 110 edges; the complement carrier has
counts `(24,15,21,20)` across its 80 edges. Petersen also holds, with counts
`(3,4,4,4)`. These are positive flow certificates, so none of the objects can
disprove Tutte's conjecture.

### 8. Lovasz vertex-transitive Hamilton paths — HOLD

Every main arsenal member is vertex-transitive by construction: cyclic blob
rotations and within-blob permutations cover the blow-ups, permutations of
`K_n` act transitively on the vertices of `T(n)=L(K_n)`, and the named controls
are standard vertex-transitive graphs. Each is connected. A deterministic
backtracking search produced a spanning path for all 15 graphs, followed by a
separate check of vertex coverage, uniqueness, and every consecutive edge.

Representative certificates are:

- `C5[K4]`:
  `(0,2,17,16,19,1,18,3,4,5,6,7,9,8,10,11,14,12,13,15)`;
- `comp(C5[K4])`:
  `(0,12,3,8,2,11,1,15,4,14,7,13,5,17,10,19,9,16,6,18)`;
- Petersen: `(0,4,3,2,1,6,9,7,5,8)`.

These positive certificates rule out every arsenal object as a counterexample
to the Hamilton-path conjecture. (They do not address the false Hamilton-cycle
strengthening catalogued in the source.)

### 9. Hadwiger clique minors — HOLD

Hadwiger requires a `K_chi(G)` minor. Exact proper-colouring values/certificates
from the Reed evaluation were paired with explicit disjoint connected branch
sets; a separate verifier checked connectedness of every set and at least one
cross-edge for every pair.

The carrier family has a uniform, stronger certificate. In `C5[K_m]`, take
the `m` singleton vertices of blob 4, `m` disjoint edges pairing blobs 2--3,
and `m` disjoint edges pairing blobs 0--1. These `3m` branch sets are pairwise
adjacent, hence give a `K_(3m)` minor, while `chi=ceil(5m/2) <= 3m`. For the
original carrier this is a `K12` minor against `chi=10`.

The remaining nontrivial certificates include:

- `C7[K3]`, `chi=7`: `{0},{1},{2},{3,6},{4,7},{5,8},{9,12,15,18}`;
- `C9[K3]`, `chi=7`: `{0},{1},{2},{3,6,9,12},{4,7,10,13},`
  `{5,8,11,14},{15,18,21,24}`;
- `T(7)`, `chi=7`: `{18,20},{17,19},{15,16},{12,13},{7,10},{6,9},{5,11}`;
- `T(9)`, `chi=9`: nine replayed two-vertex branch sets.

`T(8)`, the complement carrier, Petersen, `K3,3`, and `K4` likewise have
replayed clique-minor certificates of the required order. Thus even the
arsenal's above-theorem chromatic cases satisfy Hadwiger; there is no new
disproof.

### 10. Fan--Raspaud perfect matchings — HOLD on all applicable controls

The conjecture asks every bridgeless cubic graph to have three perfect
matchings with empty common intersection. Exactly three arsenal members meet
the cubic hypothesis: `K4`, `K3,3`, and Petersen. Exhaustive recursive matching
enumeration finds respectively 3, 6, and 6 perfect matchings. Each graph has a
certified triple with empty intersection.

For Petersen, one such triple is

1. `{12,34,68,79,05}`;
2. `{04,58,23,79,16}`;
3. `{38,27,49,05,16}`,

where `uv` denotes edge `{u,v}`. An independent replay checks that each row
covers every vertex exactly once, contains only graph edges, and that no edge
appears in all three rows. The dense carrier family is not cubic and is
correctly marked not applicable; every applicable control holds.

### 11. Petersen colouring — HOLD on all applicable controls

Under the source convention, a Petersen colouring maps each edge of a
bridgeless cubic graph to an edge of Petersen so that the three incident edges
at every source vertex map to the three incident edges at some Petersen
vertex. Petersen itself has the identity map. Both `K4` and `K3,3` have
replayed proper 3-edge-colourings; map their three colour classes bijectively
to the three edges incident at any fixed Petersen vertex. Every source vertex
sees all three colours, so this is immediately a valid Petersen edge map.

These are the only cubic arsenal members. Direct replay checks cubicity,
bridgelessness, the proper three-edge-colour partitions, and the local
incident-edge condition. All applicable controls hold; the higher-degree
carrier graphs cannot test this conjecture.

### 12. Dominating Cycle Conjecture — HOLD on all applicable controls

The source states that every cyclically 4-edge-connected cubic graph has a
dominating cycle. `K4` and `K3,3` are Hamiltonian, so their Hamilton cycles
dominate every edge. Petersen has the 9-cycle
`(0,5,8,6,9,7,2,3,4)`; its sole outside vertex is `1`, hence the complement of
the cycle is independent and the cycle is dominating.

A separate replay checks simplicity and closure of each cycle and verifies
that no edge has both endpoints outside it. Thus all applicable arsenal
controls hold. The higher-degree carrier graphs do not satisfy the cubic
hypothesis and cannot disprove this statement.

