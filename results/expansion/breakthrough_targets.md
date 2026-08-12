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

