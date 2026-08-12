# Current formal-conjectures graph cross-sweep

Date: 2026-08-12. Upstream source: `google-deepmind/formal-conjectures`
`main` at `c9052e8577118ed0ada54462bd4ef1f3beff37d6`, fetched directly from
GitHub at the start of this pass. The source checkout is read-only.

## Protocol and scope

This pass asks whether the campaign arsenal refutes any statement that upstream
currently labels `@[category research open]` and that involves mathlib's
`SimpleGraph` through a theorem parameter, a locally defined graph, or a helper
defined in the same source module. This conservative module-level dependency
rule deliberately includes fixed-value and existential questions so aliases do
not disappear from the manifest. It does not claim that every item can be
falsified by plugging in one finite graph.

Every concretely evaluable universal statement is subjected to the handoff's
four gates: exact formal hypotheses and conventions; applicable connected
Graph Atlas graphs through order 7 plus named controls; an independent
recomputation for an apparent violation; and a current-status/novelty check.
Hard optimization calls are capped at 60 seconds.

## Exact upstream manifest

The operational corpus contains **77 open declarations in 56 source modules**.
Line numbers below refer to upstream commit `c9052e8`.

| source module | open declaration(s) |
|---|---|
| `FormalConjectures/Arxiv/2107.00295/IndependentDomination.lean` | `independentDominationEven` (L34), `independentDominationOdd` (L47) |
| `FormalConjectures/Arxiv/2607.06396/AlonTarsi.lean` | `alon_tarsi_short_cycle_cover` (L50) |
| `FormalConjectures/ErdosProblems/1068.lean` | `erdos_1068` (L33) |
| `FormalConjectures/ErdosProblems/108.lean` | `erdos_108` (L35) |
| `FormalConjectures/ErdosProblems/1175.lean` | `erdos_1175` (L48), `erdos_1175.variants.threshold_formulation` (L86) |
| `FormalConjectures/ErdosProblems/1176.lean` | `erdos_1176` (L36) |
| `FormalConjectures/ErdosProblems/128.lean` | `erdos_128` (L33) |
| `FormalConjectures/ErdosProblems/184.lean` | `erdos_184` (L54), `erdos_184.variants.covering` (L99) |
| `FormalConjectures/ErdosProblems/23.lean` | `erdos_23` (L101) |
| `FormalConjectures/ErdosProblems/508.lean` | `HadwigerNelsonProblem` (L44) |
| `FormalConjectures/ErdosProblems/566.lean` | `erdos_566` (L39) |
| `FormalConjectures/ErdosProblems/567.lean` | `erdos_567.parts.i` (L56), `erdos_567.parts.ii` (L65), `erdos_567.parts.iii` (L74) |
| `FormalConjectures/ErdosProblems/579.lean` | `erdos_579` (L50) |
| `FormalConjectures/ErdosProblems/593.lean` | `erdos_593` (L48), `erdos_593.variants.obligatory_implies_two_colorable` (L62), `erdos_593.variants.two_colorable_implies_obligatory` (L79) |
| `FormalConjectures/ErdosProblems/595.lean` | `erdos_595` (L50) |
| `FormalConjectures/ErdosProblems/596.lean` | `erdos_596` (L49), `erdos_596.variants.K4_K3_exceptional_iff` (L96) |
| `FormalConjectures/ErdosProblems/60.lean` | `erdos_60` (L37) |
| `FormalConjectures/ErdosProblems/600.lean` | `erdos_600.parts.i` (L48), `erdos_600.parts.ii` (L57) |
| `FormalConjectures/ErdosProblems/61.lean` | `erdos_61` (L45) |
| `FormalConjectures/ErdosProblems/628.lean` | `erdos_628` (L42) |
| `FormalConjectures/ErdosProblems/64.lean` | `erdos_64` (L31) |
| `FormalConjectures/ErdosProblems/74.lean` | `erdos_74` (L121), `erdos_74.variants.sqrt` (L131) |
| `FormalConjectures/ErdosProblems/740.lean` | `erdos_740` (L38) |
| `FormalConjectures/ErdosProblems/742.lean` | `erdos_742` (L54) |
| `FormalConjectures/ErdosProblems/75.lean` | `erdos_75` (L35) |
| `FormalConjectures/ErdosProblems/80.lean` | `erdos_80` (L71), `erdos_80.variants.log` (L80) |
| `FormalConjectures/ErdosProblems/82.lean` | `erdos_82` (L49) |
| `FormalConjectures/ErdosProblems/835.lean` | `erdos_835` (L47), `erdos_835.variants.johnson` (L62), `johnson_chromaticNumber` (L157) |
| `FormalConjectures/ErdosProblems/85.lean` | `erdos_85` (L40) |
| `FormalConjectures/ErdosProblems/918.lean` | `erdos_918.parts.i` (L37), `erdos_918.parts.ii` (L45), `erdos_918.variants.all_subgraphs.parts.i` (L55), `erdos_918.variants.all_subgraphs.parts.ii` (L63) |
| `FormalConjectures/ErdosProblems/944.lean` | `erdos_944` (L43), `erdos_944.variants.dirac_conjecture` (L54), `erdos_944.variants.dirac_conjecture.k_eq_four` (L96) |
| `FormalConjectures/Paper/KotzigConjecture.lean` | `kotzig_conjecture` (L42) |
| `FormalConjectures/Paper/LatinTableau.lean` | `LatinTableauConjecture` (L43) |
| `FormalConjectures/Paper/ReedOmegaDeltaChi.lean` | `reed_omega_delta_chi_conjecture` (L37), `reed_omega_delta_chi_conjecture_for_finite_graphs` (L51), `reed_conjecture_Δ_6_ω_2` (L63) |
| `FormalConjectures/Paper/RingelConjecture.lean` | `ringel_conjecture` (L41) |
| `FormalConjectures/Wikipedia/Conway99Graph.lean` | `conway99Graph` (L63) |
| `FormalConjectures/Wikipedia/DiameterSimpleFiniteGroups.lean` | `babai_seress_conjecture_alternating` (L152), `babai_seress_conjecture` (L164) |
| `FormalConjectures/Wikipedia/GracefulLabeling.lean` | `graceful_tree_conjecture` (L73) |
| `FormalConjectures/Wikipedia/PebblingNumberConjecture.lean` | `pebbling_number_conjecture` (L130) |
| `FormalConjectures/Wikipedia/RamseyNumbers.lean` | `ramsey_number_five_five` (L91) |
| `FormalConjectures/Wikipedia/SidorenkoConjecture.lean` | `sidorenko_conjecture` (L55) |
| `FormalConjectures/Wikipedia/SnakeInTheBox.lean` | `snake_dim_nine` (L97) |
| `FormalConjectures/WrittenOnTheWallII/160.lean` | `conjecture160` (L68) |
| `FormalConjectures/WrittenOnTheWallII/GraphConjecture100.lean` | `conjecture100` (L75) |
| `FormalConjectures/WrittenOnTheWallII/GraphConjecture133.lean` | `conjecture133` (L47) |
| `FormalConjectures/WrittenOnTheWallII/GraphConjecture141.lean` | `conjecture141` (L41) |
| `FormalConjectures/WrittenOnTheWallII/GraphConjecture145.lean` | `conjecture145` (L75) |
| `FormalConjectures/WrittenOnTheWallII/GraphConjecture146.lean` | `conjecture146` (L59) |
| `FormalConjectures/WrittenOnTheWallII/GraphConjecture19.lean` | `conjecture19` (L42) |
| `FormalConjectures/WrittenOnTheWallII/GraphConjecture198a.lean` | `conjecture198a` (L40) |
| `FormalConjectures/WrittenOnTheWallII/GraphConjecture200.lean` | `conjecture200` (L41) |
| `FormalConjectures/WrittenOnTheWallII/GraphConjecture291.lean` | `conjecture291` (L108) |
| `FormalConjectures/WrittenOnTheWallII/GraphConjecture314.lean` | `conjecture314` (L67) |
| `FormalConjectures/WrittenOnTheWallII/GraphConjecture40.lean` | `conjecture40` (L40) |
| `FormalConjectures/WrittenOnTheWallII/GraphConjecture59.lean` | `conjecture59` (L43) |
| `FormalConjectures/WrittenOnTheWallII/GraphConjecture61.lean` | `conjecture61` (L42) |

## Evaluation log

Results are appended below one statement (or one inseparable variant family)
at a time. A statement excluded from fixed-graph evaluation still receives an
explicit reason in the completion audit.

### `independentDominationEven` and `independentDominationOdd` — HOLD

The hypotheses require only positive minimum degree and select the formula by
the parity of the maximum degree. I solved the exact minimum independent
dominating-set ILP for every arsenal graph (binary vertex variables,
independence constraints on edges, closed-neighborhood domination constraints,
CBC capped at 60 seconds). All solves were optimal. The closest arsenal member
was Petersen, with odd-case slack
`(3^2+3)10 - (3+1)(3+3)3 = 48`; the complement of `C5[K4]` had even-case
slack `560`. The carrier had odd-case slack `2144`; `T(7)` had even-case
slack `1752`. All other tested slacks were larger. No candidate violation was
generated, so the small-graph and independent-recompute gates were not
triggered.

### Reed's three open declarations — HOLD / NOT APPLICABLE

For both the unrestricted and finite formulations I evaluated the exact slack
`omega + Delta + 2 - 2 chi`. For `C5[K_m]`, the closed forms
`chi = ceil(5m/2)`, `Delta = 3m-1`, and `omega = 2m` give slack `1` for even
`m` and `0` for odd `m`. Thus the odd members are equality witnesses, not
counterexamples. The slacks for `C7[K3]`, `C9[K3]`, `T(7)`, `T(8)`, `T(9)`,
`comp(C5[K4])`, and Petersen are respectively `2, 2, 4, 7, 6, 6, 1`.
Chromatic numbers were checked both from the standard multicoloring/edge-
coloring formulas and by an independent exact coloring search on the tractable
members. None of the arsenal graphs has the special hypotheses
`Delta = 6` and `omega = 2`, so `reed_conjecture_Delta_6_omega_2` is not
applicable. There is no violation to pass to the database gate.

### `erdos_64` (power-of-two cycle) — HOLD

Every arsenal graph with minimum degree at least three except Petersen contains
an explicit 4-cycle (`2^2`). For example, `comp(C5[K4])` contains
`0-4-1-5-0`, and a common-neighbor search produced 4-cycles in every
`C5[K_m]`, `C7[K3]`, `C9[K3]`, and `T(n)` member. Petersen has no 4-cycle but
does contain an 8-cycle. The latter was checked by a separate simple-cycle
enumeration. Thus all eligible arsenal graphs satisfy the statement.

### `erdos_23` (triangle-free bipartization) — HOLD, tight

Only `comp(C5[K4])` and Petersen are triangle-free members whose orders are
multiples of five. The former is exactly the independent-part blow-up of
`C5` with part size four: its maximum cut has 64 of 80 edges, so exactly
`16 = 4^2` deletions suffice and are necessary. Petersen's exact maximum cut
has 12 of 15 edges, so only `3 <= 2^2` deletions are needed. A second method
enumerated all bipartitions (fixing one vertex's side) and obtained the same
max-cut values. No violation survives.

### `erdos_128` (dense large induced subgraphs force a triangle) — HOLD/vacuous

Graphs in the arsenal that contain triangles satisfy the conclusion. For the
two triangle-free candidates, the premise fails exactly: among subsets meeting
Lean's condition `2|V'|+1 >= |V|`, `comp(C5[K4])` has a 10-vertex subset with
8 edges, not strictly more than `20^2/50 = 8`; Petersen has a 5-vertex subset
with 2 edges, not strictly more than `10^2/50 = 2`. The first minimum was
independently obtained both by subset enumeration and by minimizing
`sum x_i x_(i+1)` over five part occupancies `0 <= x_i <= 4`.

### `erdos_742` (Murty--Simon) — HOLD / mostly not applicable

Deleting a single edge leaves diameter two for every dense blow-up and every
triangular graph, so those objects fail diameter-2-criticality. Both applicable
arsenal members satisfy the bound: `comp(C5[K4])` is diameter-2-critical with
`80 <= 20^2/4 = 100`, and Petersen is diameter-2-critical with
`15 <= 10^2/4 = 25`. Criticality was checked by deleting every edge and
recomputing all-pairs distances; a separate structural check uses that each
edge is the unique length-one route for its endpoints and has no common
neighbor in these triangle-free diameter-two graphs.

### Previously completed WoW-II declarations — no additional kill

The 14 upstream WoW-II declarations in this manifest were already evaluated
source-faithfully in the campaign's complete 522-entry sweep. The present
arsenal verdicts are: HOLD for 19, 40, 59, 61, 100, 133, 141, 145, 146,
160, 198a, and 291; NOT APPLICABLE for 200; and vacuous HOLD for 314 because
the carrier is not triangle-free (the complement is triangle-free but has a
larger induced path and is not well-totally-dominated candidate under the
conjunction). The broader family sweep had already exposed only WoW-II 181,
which upstream has not formalized. No declaration in the current upstream
WoW-II subset is newly disproved here.
