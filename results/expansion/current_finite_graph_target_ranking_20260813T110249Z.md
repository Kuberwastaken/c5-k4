# Current finite-graph target ranking (selection only)

Audit time: **2026-08-13T11:02:49Z**
Disposition: **RANKED, NOT SELECTED, NOT EVALUATED**

This is a source and coverage pass for a possible next Method round. It does
not freeze a family, authorize a constructor, or evaluate a development-family
member.

## Version and scope lock

- Method repository: `c5-k4` at `d14466d7e58b2556344a1dc10d71e8b0a0b8b9ae`
  when the final coverage refresh began. `METHOD.md` is v0.8 and
  `OVERARCHING_PLAN.md` requires a separate frozen contract before any new
  development row.
- Local `formal-conjectures` checkout: branch `prove-wowii-438b`, commit
  `9a1636c4030039f70cf78b866c216d8b6c5f35b0`.
- Current upstream `main`: `d16e05aded22b8c467a0a27c14b2311f53185006`
  (`git ls-remote` and an isolated depth-one clone). The local checkout was not
  treated as current because its commit differs from remote main.
- Operational finite-graph rule: an open declaration is included when its
  source module contains `SimpleGraph`, matching the conservative dependency
  rule of `formal_conjectures.md`. This includes fixed-value and existential
  graph questions and excludes non-graph declarations which merely share AMS
  category 5.
- Deterministic manifest: **79 open declarations in 57 modules**; the extracted
  manifest has SHA-256
  `327628efe4f4e8e96a1e92e16cf1fbe8d45c068c2b88274539e193c403102bd2`.

The current remote manifest is the earlier 77-declaration manifest plus the
two Dean-cycle declarations. No later finite-graph open declaration was found.

## Exact current manifest

Line numbers are from upstream commit `d16e05ad`.

| source | open declaration(s) |
|---|---|
| `Arxiv/2107.00295/IndependentDomination.lean` | `independentDominationEven` (35), `independentDominationOdd` (48) |
| `Arxiv/2605.02731/DeanCycles.lean` | `dean_conjecture` (46), `dean_conjecture.variants.five` (56) |
| `Arxiv/2607.06396/AlonTarsi.lean` | `alon_tarsi_short_cycle_cover` (51) |
| `ErdosProblems/1068.lean` | `erdos_1068` (34) |
| `ErdosProblems/108.lean` | `erdos_108` (36) |
| `ErdosProblems/1175.lean` | `erdos_1175` (49), `erdos_1175.variants.threshold_formulation` (87) |
| `ErdosProblems/1176.lean` | `erdos_1176` (37) |
| `ErdosProblems/128.lean` | `erdos_128` (34) |
| `ErdosProblems/184.lean` | `erdos_184` (55), `erdos_184.variants.covering` (100) |
| `ErdosProblems/23.lean` | `erdos_23` (102) |
| `ErdosProblems/508.lean` | `HadwigerNelsonProblem` (45) |
| `ErdosProblems/566.lean` | `erdos_566` (40) |
| `ErdosProblems/567.lean` | `erdos_567.parts.i` (57), `.parts.ii` (66), `.parts.iii` (75) |
| `ErdosProblems/579.lean` | `erdos_579` (51) |
| `ErdosProblems/593.lean` | `erdos_593` (49), `.variants.obligatory_implies_two_colorable` (63), `.variants.two_colorable_implies_obligatory` (80) |
| `ErdosProblems/595.lean` | `erdos_595` (51) |
| `ErdosProblems/596.lean` | `erdos_596` (50), `.variants.K4_K3_exceptional_iff` (97) |
| `ErdosProblems/60.lean` | `erdos_60` (38) |
| `ErdosProblems/600.lean` | `erdos_600.parts.i` (49), `.parts.ii` (58) |
| `ErdosProblems/61.lean` | `erdos_61` (46) |
| `ErdosProblems/628.lean` | `erdos_628` (43) |
| `ErdosProblems/64.lean` | `erdos_64` (32) |
| `ErdosProblems/74.lean` | `erdos_74` (122), `.variants.sqrt` (132) |
| `ErdosProblems/740.lean` | `erdos_740` (39) |
| `ErdosProblems/742.lean` | `erdos_742` (55) |
| `ErdosProblems/75.lean` | `erdos_75` (36) |
| `ErdosProblems/80.lean` | `erdos_80` (72), `.variants.log` (81) |
| `ErdosProblems/82.lean` | `erdos_82` (50) |
| `ErdosProblems/835.lean` | `erdos_835` (48), `.variants.johnson` (63), `johnson_chromaticNumber` (158) |
| `ErdosProblems/85.lean` | `erdos_85` (41) |
| `ErdosProblems/918.lean` | `erdos_918.parts.i` (38), `.parts.ii` (46), `.variants.all_subgraphs.parts.i` (56), `.parts.ii` (64) |
| `ErdosProblems/944.lean` | `erdos_944` (44), `.variants.dirac_conjecture` (55), `.k_eq_four` (97) |
| `Paper/KotzigConjecture.lean` | `kotzig_conjecture` (43) |
| `Paper/LatinTableau.lean` | `LatinTableauConjecture` (44) |
| `Paper/ReedOmegaDeltaChi.lean` | `reed_omega_delta_chi_conjecture` (38), `_for_finite_graphs` (52), `reed_conjecture_Delta_6_omega_2` (64) |
| `Paper/RingelConjecture.lean` | `ringel_conjecture` (42) |
| `Wikipedia/Conway99Graph.lean` | `conway99Graph` (64) |
| `Wikipedia/DiameterSimpleFiniteGroups.lean` | `babai_seress_conjecture_alternating` (153), `babai_seress_conjecture` (165) |
| `Wikipedia/GracefulLabeling.lean` | `graceful_tree_conjecture` (74) |
| `Wikipedia/PebblingNumberConjecture.lean` | `pebbling_number_conjecture` (131) |
| `Wikipedia/RamseyNumbers.lean` | `ramsey_number_five_five` (92) |
| `Wikipedia/SidorenkoConjecture.lean` | `sidorenko_conjecture` (56) |
| `Wikipedia/SnakeInTheBox.lean` | `snake_dim_nine` (98) |
| `WrittenOnTheWallII/160.lean` | `conjecture160` (69) |
| `WrittenOnTheWallII/GraphConjecture100.lean` | `conjecture100` (76) |
| `WrittenOnTheWallII/GraphConjecture133.lean` | `conjecture133` (48) |
| `WrittenOnTheWallII/GraphConjecture141.lean` | `conjecture141` (42) |
| `WrittenOnTheWallII/GraphConjecture145.lean` | `conjecture145` (76) |
| `WrittenOnTheWallII/GraphConjecture146.lean` | `conjecture146` (60) |
| `WrittenOnTheWallII/GraphConjecture19.lean` | `conjecture19` (43) |
| `WrittenOnTheWallII/GraphConjecture198a.lean` | `conjecture198a` (41) |
| `WrittenOnTheWallII/GraphConjecture200.lean` | `conjecture200` (42) |
| `WrittenOnTheWallII/GraphConjecture291.lean` | `conjecture291` (109) |
| `WrittenOnTheWallII/GraphConjecture314.lean` | `conjecture314` (68) |
| `WrittenOnTheWallII/GraphConjecture40.lean` | `conjecture40` (41) |
| `WrittenOnTheWallII/GraphConjecture59.lean` | `conjecture59` (44) |
| `WrittenOnTheWallII/GraphConjecture61.lean` | `conjecture61` (43) |

## Coverage subtraction

The following current-manifest clusters are removed before ranking because
`c5-k4` contains an actual family evaluation, a frozen trial already in
execution, or a theorem/prior-art closure—not merely a manifest mention:

- independent domination (2 declarations): multiple private-leaf lanes;
- Dean `k=5` (2): arsenal and complete two-switch trials, then Dirac closure;
- Alon--Tarsi (1): a Petersen-splice switch contract and ledger already existed
  at this audit timestamp, so it is no longer a prospective next-round target;
- Reed (3): carrier equality evaluation and five prospective transformation
  lanes, including a proved claw-free-domain stop;
- Erdős 23, 64, 128, and 742 (4): each has target-specific prospective records;
- all 14 current WOWII declarations (14): all were in the complete sweep and
  each cluster has later target-specific trial, proof, status, or prior-art
  records.

This subtracts **26 declarations**. The remaining **53 declarations** are not
all method-suitable: many are asymptotic, infinite-cardinal, fixed-value, or
non-graph-object questions. A prior manifest-only classification is not
treated as an attempt; otherwise no candidate could emerge from the audited
but unevaluated remainder.

## Ranking method

Each factor is scored 0--3: exact tight/equality seed availability (`S`),
interpretable invariant obstruction (`O`), bounded exact evaluability (`E`),
and novelty/proof-domain safety (`N`, where 3 is lower risk). Scores are
selection heuristics, not evidence about truth. Ties are ordered by fit to the
residual-wall method and by whether the open declaration is a direct universal
statement rather than an `answer(sorry)` wrapper.

| rank | untouched current cluster | S | O | E | N | total | selection rationale |
|---:|---|---:|---:|---:|---:|---:|---|
| 1 | Erdős 184 cycle/edge decomposition (2 declarations) | 3 | 3 | 2 | 1 | 9 | Trees force `n-1` one-edge pieces in the covering formulation, an exact cap seed. Cycle rank and the number of edges left outside chosen cycles give a literal obstruction, and bounded cycle enumeration plus exact set-cover ILP is available. Risk: the main declaration is asymptotic and the covering variant is an answer-valued historical question, so Phase 0 must freeze which direction is being tested. |
| 2 | graceful/Kotzig/Ringel tree-labeling and decomposition cluster (3 declarations) | 3 | 3 | 2 | 0 | 8 | Every witness is an exact difference-set or edge-partition certificate; the missing modular difference is an interpretable obstruction. Small trees admit bounded SAT/exact-cover evaluation. These declarations are one cluster because graceful/cyclic embeddings feed the stronger decomposition statements. Severe prior-art and proof-domain risk keeps it below Erdős 184. |
| 3 | graph pebbling product inequality (1 declaration) | 2 | 2 | 2 | 1 | 7 | The source proves the exact complete-graph pebbling number, supplying calibrated factors. Distance-weight and reachability bottlenecks are interpretable, and fixed small products have finite exact state-space evaluation. State explosion and many known product classes require a strict proof-domain gate. |
| 4 | Sidorenko homomorphism-density inequality (1 declaration) | 3 | 2 | 3 | 0 | 8 | The source contains exact equality at `K2` and solved `K2,2`/tree domains; all finite-host residuals are exact rationals from homomorphism counts. The controlling obstruction is correlation/degree nonuniformity. It ranks below pebbling despite the larger raw score because the useful seeds lie in theorem-closed pattern classes and the novelty/proof-domain risk is maximal. |
| 5 | Erdős--Lovász Tihany partition, Erdős 628 (1 declaration) | 1 | 3 | 2 | 1 | 7 | The obstruction is clean: chromatic-critical mass must split across complementary induced subgraphs. Exact coloring and exhaustive vertex bipartitions are bounded on small candidates. The source already closes `k=5,a=b=3`, quasi-line graphs, and independence number two; no exact open-domain equality seed is yet recorded, so this is a reserve lane rather than the first trial. |

### Ranked-out near misses

- Conway's 99-graph has an exact nine-vertex analogue and crisp common-neighbor
  equations, but the jump to 99 vertices is not boundedly evaluable in the
  Method sense without first supplying an algebraic quotient.
- Snake-in-the-box dimension nine has an exact lower-bound witness length 190,
  but the open object is a fixed optimum rather than a residual wall and a
  complete exact upper-bound evaluation is too large.
- Ramsey `R(5,5)`, Hadwiger--Nelson, and the Erdős 567/596/835/944 fixed-value
  clusters similarly lack a bounded wall-crossing trial from the present
  campaign arsenal.
- Infinite-cardinal and asymptotic clusters remain outside bounded
  counterexample-family evaluation unless a finite obstruction theorem is
  first derived.

## Recommendation and stop

The next selector should begin with **Erdős 184**, but only after a new,
separate source contract resolves the `answer(sorry)` direction and chooses
either the covering statement or a finite obstruction to the asymptotic
statement. No graph family is selected here. If that Phase-0 reading cannot be
made unambiguous, advance to the graceful/Kotzig/Ringel cluster rather than
evaluating an interpretation-dependent family.

No development family was evaluated; no existing result was edited; no
commit, push, issue, PR, release, or other public action was performed.
