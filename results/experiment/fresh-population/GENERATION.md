# Generation record — fresh conjecture population

**Produced:** 2026-08-15 UTC, after
[`../PREREGISTRATION.md`](../PREREGISTRATION.md) was committed and before any arm
was run.
**Artifact:** [`population.json`](population.json) — 30 frozen targets.
**Code:** [`../../../scripts/gen/`](../../../scripts/gen/).

This is the *generation* stage of the three-arm test recommended in
[`../../review/INDEPENDENT_REVIEW_2026-08-15.md`](../../review/INDEPENDENT_REVIEW_2026-08-15.md)
§4. The point of generating a population from scratch is that these conjectures
did not exist before this run, so no arm can have prior knowledge of them.

---

## 1. What was and was not tested — the contamination contract

**Tested:** every candidate inequality was evaluated on every member of `D`
(all 12,112 connected graphs on `2 <= n <= 8`) and on nothing else.

**Not tested — no candidate inequality was ever evaluated on any of these:**
C₅[K_m] for any `m`, T(n) = L(Kₙ), Petersen, Kneser, Paley, complete
multipartite, cocktail-party, prisms, Möbius–Kantor, complete bipartite, stars,
brooms, double stars, hypercubes, circulants, grids, random graphs, any
complement of the above, any graph on `n >= 9`, or any graph named anywhere in
this repository. There is no random search, no local search, no named-family
catalogue and no counterexample hunt anywhere in `scripts/gen/`.

**The one place graphs outside `D` appear at all:**
[`check_invariants.py`](../../../scripts/gen/check_invariants.py) and
[`check_target_budget.py`](../../../scripts/gen/check_target_budget.py) run the
invariant code on generic stress structures (paths, cycles, grids, hypercubes,
circulants, complete multipartite, seeded random graphs) to measure **how long an
invariant takes**. They print timings only. There is no code path in either
script by which a candidate inequality could be evaluated, and no invariant
*value* for a non-`D` graph is printed, stored or compared. The runtime figures
in §7 are their entire output.

**Candidates discarded because they were accidentally learned to be false outside
`D`: none.** No such event occurred, because no such evaluation occurred.

---

## 2. The database `D`

| `n` | connected graphs | source |
|---|---|---|
| 2 | 1 | `networkx.graph_atlas_g()` |
| 3 | 2 | `networkx.graph_atlas_g()` |
| 4 | 6 | `networkx.graph_atlas_g()` |
| 5 | 21 | `networkx.graph_atlas_g()` |
| 6 | 112 | `networkx.graph_atlas_g()` |
| 7 | 853 | `networkx.graph_atlas_g()` |
| 8 | 11,117 | generated here (below) |
| **total** | **12,112** | |

Every count matches OEIS A001349 (connected graphs on `n` nodes) exactly; the
build asserts this. SHA-256 of the graph6 database file is recorded in
`population.json` under `database.sha256_graph6_file`.

**`n = 8` was feasible and was done.** No `geng`/`nauty` is available in this
environment, so [`graph_db.py`](../../../scripts/gen/graph_db.py) generates the
8-vertex graphs itself: every 8-vertex graph has a vertex-deleted subgraph on 7
vertices, so extending *all* 1,044 graphs on 7 vertices by one vertex over all
2⁷ neighbourhoods is exhaustive. The 119,980 connected candidates are then
reduced modulo isomorphism by bucketing on a cheap invariant certificate and
running exact VF2 (`networkx.is_isomorphic`) inside each bucket — so correctness
does not depend on the certificate being complete. Result: exactly 11,117, the
known value. Build time ≈ 50 s; the database is cached as an 84 kB graph6 file.

`K_1` is excluded: no edges, no neighbourhoods, so `deg_avg`, `lambda(v)`,
`girth`, `disp` and the domination invariants are 0 or undefined on it, and
Graffiti-lineage databases do not contain it. Every emitted statement is
therefore quantified over **connected graphs with `n >= 2`** and says so in its
own text.

`n = 9` was not attempted — it is outside the task's `n <= 8` specification. For
the record: 261,080 connected graphs, ≈3.2 M extension candidates; with this
pure-Python isomorphism rejection it would cost an estimated 1.5–2 h end to end
rather than the ~2 min the whole `n <= 8` pipeline takes.

---

## 3. Invariant vocabulary

**49 invariants computed, 47 used for emission.** All values are exact `int` or
`Fraction` — no floating-point value enters any statement. Definitions follow
[`data/INVARIANT-GLOSSARY.md`](../../../data/INVARIANT-GLOSSARY.md) (DeLaViña's
WOWII definitions database), extending
[`scripts/profile_c5k4.py`](../../../scripts/profile_c5k4.py).

| group | invariants |
|---|---|
| order, size, degrees | `n`, `m`, `Delta`, `delta`, `sigma_2`, `Sigma_2`, `dd`, `f_1`, `deg_avg` |
| degree-sequence machinery | `res` (residue), `A` (annihilation), `SW` (Szekeres–Wilf = degeneracy), `CW` (Caro–Wei) |
| distance | `diam`, `rad`, `girth`, `ecc_avg`, `dist_even_min`, `dist_even_max`, `Tdist_min`, `Tdist_max`, `dist_avg` |
| connectivity, counting | `kappa`, `cutv`, `t` (triangles), `disp_min`, `disp_max`, `disp_avg` |
| spectral | `floor(lambda_1)`, `ceil(lambda_1)` |
| independence, clique, colouring, matching | `alpha`, `omega`, `chi`, `mu`, `lambda_max`, `lambda_min`, `lambda_avg` |
| domination | `gamma`, `gamma_t`, `gamma_2`, `gamma_i` |
| induced-order | `f` (forest number), `b` (bipartite number) — **computed but not emitted, see below** |
| 0/1 characteristic functions | `chi_bipartite`, `chi_K3free`, `chi_C4free`, `chi_clawfree`, `chi_regular`, `chi_tree` |

### Conventions pinned here

* **`girth`** = number of vertices of a shortest cycle, and **`n + 1` if `G` is
  acyclic**. Any cycle in an `n`-vertex graph has at most `n` vertices, so inside
  the universe of quantification `n+1` behaves exactly like `+inf` while keeping
  every statement finite-checkable. (No target in the final 30 uses `girth`.)
* **`dist_even(v)`** counts `v` itself (distance 0 is even), matching
  `scripts/profile_c5k4.py` and the WOWII page examples.
* **`floor(lambda_1)` / `ceil(lambda_1)`** are computed **exactly**, with no
  eigenvalue arithmetic: `lambda_1 < k` iff `kI − A` is positive definite iff
  every leading principal minor of `kI − A` is positive (Sylvester), and those
  minors are integer determinants (Bareiss). The spectral radius itself is
  irrational in general and is deliberately never used as a value.

### Excluded from the vocabulary

* **`maxine`** — the greedy "delete a maximum-degree vertex" process is
  tie-break dependent, so it is not an isomorphism invariant and cannot appear in
  a well-defined universal statement.
* **`p(G)` (path covering number), `path(G)` (longest induced path), `tree(G)`
  (largest induced tree), `L_s`/`gamma_c` (max-leaf spanning tree / connected
  domination), `alpha'` (critical independence)** — no exact solver here decides
  them inside the cap at `n = 30..40` (no ILP solver is installed).

### Excluded from *emission* on measured runtime: `f` and `b`

`f` (largest induced forest) and `b` (largest induced bipartite subgraph) are
computed on `D` and cross-checked, but **no emitted statement may use them.**
Measured with the branch-and-bound solvers here (branch on a short (odd) cycle,
bounded by a disjoint cycle packing, seeded greedily):

| graph | n | m | `b` | `f` |
|---|---|---|---|---|
| G(30, 0.3) | 30 | 138 | 0.70 s | 4.66 s |
| G(30, 0.5) | 30 | 216 | 2.93 s | 13.52 s |
| G(40, 0.15) | 40 | 127 | 17.96 s | **> 20 s** |
| G(40, 0.3) | 40 | 230 | **> 20 s** | **> 20 s** |
| G(40, 0.5) | 40 | 389 | **> 20 s** | **> 20 s** |
| 5×8 grid | 40 | 67 | 0.00 s | **> 12 s** |

A statement that cannot be *decided* inside the 60 s cap is unscorable for every
arm, so it must not be emitted. This is a real cost: `f` and `b` were central to
the campaign's own C₅[K_m] case study, and the population is therefore not a
re-run of its home ground (see §10(e)).

---

## 4. Emission rules

A candidate is `t REL E` where `t` is a **target invariant**, `REL` is `<=` or
`>=`, and `E` is a right-hand side built by one of the template tables.

**Targets (14, both directions each):** `alpha`, `omega`, `chi`, `mu`, `gamma`,
`gamma_t`, `gamma_2`, `gamma_i`, `res`, `A`, `diam`, `rad`, `kappa`,
`lambda_max`. (`f` and `b` were on the target list and were removed with the rest
of their use, §3.) The order/size parameters and the 0/1 characteristic
functions appear only on the right, which is how Graffiti uses them.

**Templates (51).** Small integer coefficients, sums and differences of two
invariants, and — the shapes that carry the discretisation — ceilings and floors
of halves, thirds and invariant/invariant ratios.

| kind | count | shapes (`c` a small integer constant) |
|---|---|---|
| unary | 31 | `x+c`, `2x+c`, `3x+c`, `ceil(x/2)+c`, `floor(x/2)+c`, `ceil(x/3)+c`, `floor(x/3)+c` |
| binary, symmetric | 7 | `x+y+c`, `ceil((x+y)/2)+c`, `floor((x+y)/2)+c` |
| binary, asymmetric | 13 | `x−y+c`, `ceil((x−y)/2)+c`, `floor((x−y)/2)+c`, `2x−y+c`, `ceil(x/2)+y`, `floor(x/2)+y`, `ceil(x/y)`, `floor(x/y)` |

`ceil(x/y)` and `floor(x/y)` are built **only** over denominators provably `>= 1`
on every connected graph with `n >= 2` (38 of the 47; `f_1`, `cutv`, `t` and the
six characteristic functions are excluded because each vanishes somewhere). No
emitted statement can therefore be undefined anywhere in its own universe of
quantification — which matters, because an undefined statement is not finitely
refutable.

**Filters.** A candidate is kept iff all of:

| | rule | rationale |
|---|---|---|
| F1 | **zero counterexamples over all of `D`** | this is what makes it a conjecture rather than a refuted guess |
| F2 | **sharp**: equality attained on at least one member of `D` | Graffiti's Dalmatian significance criterion; also the tightness data the wall arm is entitled to |
| F3 | **not an identity**: equality does *not* hold on all of `D` | an identity on the whole database is a definitional relation, not a conjecture |
| F4 | the right-hand side is **non-constant** on `D` | a constant bound expresses no relation between invariants |
| F5 | the right-hand side does **not** mention the target | rules out `alpha <= alpha + 1` |

**Finite-universality (brief, step 3) is structural, not a filter.** Every
emitted statement reads "for every connected graph `G` with `n(G) >= 2`,
`<inequality between computable invariants of G>`". No asymptotics, no
quantifiers over families, no non-computable terms, no hypotheses — so a single
explicit graph refutes any of them. Nothing was dropped at this step because
nothing of another shape can be generated.

---

## 5. Counts at each stage

| stage | count |
|---|---|
| database `D` | **12,112** graphs |
| invariants computed / emitted | 49 / **47** |
| target invariants × directions | 14 × 2 = 28 |
| distinct right-hand-side expressions enumerated | **36,302** |
| … rejected, constant on `D` (F4) | 406 |
| (candidate, target) pairs rejected, target on the right (F5) | 13,228 |
| **candidate statements evaluated against all of `D`** | **195,759** |
| … rejected, counterexample in `D` (F1) | 20,990 |
| … rejected, not sharp (F2) | 79,510 |
| … rejected, identity on `D` (F3) | 0 |
| **survivors of F1–F5** | **95,259** |
| after dedup D-S (identical slack vector) | 87,057 |
| after dedup D-C (structural cluster) | **20,926** |
| after dedup D-D (Dalmatian domination) | **1,611** |
| **selected into the frozen population** | **30** |

Generation wall clock: 30 s, on top of ~50 s to build `D` and ~31 s to compute
the invariant matrix (both cached).

---

## 6. Deduplication and selection rules

Graffiti-lineage generators emit large numbers of algebraically equivalent
restatements. Three rules, in this order:

**D-S — identical behaviour on `D`.** Two candidates with the same target, the
same direction, and the *same slack vector over all 12,112 graphs* are one
statement wearing two hats — e.g. `mu <= floor(m/deg_avg)` and `mu <= floor(n/2)`
(identical because `deg_avg = 2m/n`), or any bound plus a correction term that is
identically zero on `D`. One representative survives: the **simplest surface
form** — fewest invariant symbols, then shortest rendering, then lexicographic.
Simplicity is used here and only here, where the alternatives are provably the
same statement on `D`, so the choice is cosmetic. `95,259 → 87,057`.

**D-C — structural cluster.** Cluster = `(target, direction, set of invariant
symbols used)`. This is the "structural cluster" of the brief: everything built
from the same invariants, about the same target, in the same direction collapses
to one representative. `87,057 → 20,926`.

**D-D — Dalmatian domination.** Within each `(target, direction)`, drop any
representative that some other representative beats or ties **on every member of
`D`** — uniformly no stronger, so it carries no information the other does not.
This is Fajtlowicz's own significance filter and it removes the long tails of
weakened variants. `20,926 → 1,611`.

**Selection to 30.** Primary criterion, as specified: **maximise the diversity of
invariant sets.** Greedy maximin — repeatedly take the candidate whose invariant
set has the largest minimum Jaccard distance to everything already selected —
under quotas of at most 3 targets per left-hand-side invariant and at most 2 per
`(left-hand side, direction)`, so no single invariant can own the population.

**Ties are broken by a deterministic coin**, `blake2b(salt ‖ statement)`, not by
any property of the mathematics. This is deliberate, and it is the single most
consequential methodological choice in this file:

> Ranking candidates by **how often they are tight** promotes near-identities.
> The first version of this run did exactly that and returned a population led by
> `kappa <= delta`, `chi >= omega`, `b >= f`, `mu <= floor(n/2)` — textbook
> theorems. Switching the preference to **simplicity** promoted *the same*
> textbook theorems from the other side (`alpha <= n - mu`, `A >= mu`,
> `gamma_i <= gamma_2`, `diam >= ecc_avg`). Both are thumbs on the scale, and
> ranking by tightness in particular would be optimising for the mechanism under
> test. A coin is not. `blake2b` is stable across runs and machines (unlike
> Python's salted `hash`), so the population stays reproducible.

Both discarded variants are recoverable from the git history of
`scripts/gen/generate.py`; nothing was tuned by looking at how refutable the
results were, because refutability outside `D` was never measured.

---

## 7. Runtime — is every target actually checkable?

Yes — **worst case 3.93 s**, against a 60 s cap.

Measured by [`check_target_budget.py`](../../../scripts/gen/check_target_budget.py)
over 31 generic stress graphs on 20–40 vertices (paths, cycles, a 5×8 grid, `Q5`,
two circulants, complete multipartite, `K_{20,20}`, a wheel, a binary tree,
`K_30`, `K_40`, and 17 seeded `G(n,p)` graphs at `n = 20..40`,
`p = 0.15..0.7`). Each NP-hard invariant is timed separately with a 12 s
per-block cap. Timings only — no inequality is evaluated on any of these graphs.

**Worst observed cost per block, over all 31 stress graphs:**

| block | worst | | block | worst |
|---|---|---|---|---|
| polynomial block (all 30 poly invariants) | 0.56 s | | `gamma` | 0.02 s |
| `alpha` | < 0.01 s | | `gamma_t` | 0.03 s |
| `omega` | < 0.01 s | | `gamma_2` | 2.36 s |
| `chi` | 1.00 s | | `gamma_i` | 0.03 s |
| `lambda_*` (all `n` neighbourhoods) | 0.01 s | | | |
| `f` (**not emitted**) | > 12 s on 15 of 31 | | `b` (**not emitted**) | > 12 s on 9 of 31 |

**Worst-case cost of deciding each frozen target** (polynomial block plus the
NP-hard invariants it actually names):

| cost | targets |
|---|---|
| 0.56–0.61 s | FP-001, FP-003, FP-004, FP-005, FP-008, FP-009, FP-011, FP-015, FP-016, FP-017, FP-018, FP-019, FP-020, FP-021, FP-022, FP-024, FP-025, FP-026, FP-027, FP-028, FP-029, FP-030 |
| 1.56 s | FP-002, FP-006 |
| 2.91–2.94 s | FP-007, FP-010, FP-012, FP-013, FP-014 |
| 3.93 s | FP-023 |

**Over the 60 s budget: none.** The two blocks that do blow the cap, `f` and `b`,
are exactly the two excluded from emission (§3), which is why they were excluded.

---

## 8. Verification

[`verify_population.py`](../../../scripts/gen/verify_population.py) re-derives
every claim in `population.json` through a code path that shares nothing with the
generator's sweep: invariants recomputed from the graphs rather than read from
the cache, and the statements evaluated from their JSON ASTs in `Fraction`
arithmetic rather than in scaled `int64` numpy. For all 30 targets over all
12,112 graphs it checks: zero counterexamples; the recorded min and max slack;
the recorded equality count and its breakdown by `n`; that every recorded graph6
witness really attains equality; and that the relation string renders from the
recorded AST.

    full-D re-verification done in 46s
    backend cross-check on 300 graphs x 30 targets: 0 mismatches
    PASS: all 30 targets reproduce exactly on an independent code path.

[`check_invariants.py`](../../../scripts/gen/check_invariants.py) additionally
cross-checks the two invariant backends — exhaustive `2^n` subset enumeration
versus branch-and-bound with no subset enumeration — on deterministic samples of
`D`: **0 disagreements on 1,500 graphs**. A third path (networkx
`max_weight_clique`, `diameter`, `radius`, naive `itertools` domination and
induced-forest search, and a float eigenvalue check bracketing
`floor(lambda_1)`/`ceil(lambda_1)`) agreed on a 250-graph sample.

Three real bugs were caught this way and fixed before the population was frozen:
an invalid independent-set bound (an independent-set partition used where a
clique cover is required), duplicate branching in the domination solver, and a
`gamma_2` infeasibility test that forgot a vertex can 2-dominate itself by being
selected. The last one produced wrong values on 215 of 1,500 sampled graphs and
would have silently corrupted every `gamma_2` target.

---

## 9. What is in the population

30 targets, all of the form "for every connected graph `G` with `n(G) >= 2`,
`<inequality>`":

* **13 distinct left-hand-side invariants**; **42 of the 47** emission-vocabulary
  invariants appear somewhere.
* 20 lower bounds, 10 upper bounds.
* **22 of 30 contain a ceiling or a floor** — the discretisation the mechanism
  under test is about; **7** contain an invariant/invariant ratio; **6** carry a
  0/1 characteristic function as a correction term; 13 distinct templates are
  represented.
* Every target names exactly two right-hand-side invariants (three including the
  target).
* Equality witnesses in `D`: fewest 2, median 249, most 10,407. **29 of 30 are
  tight on at least one graph at `n = 8`**, the database edge; the exception is
  `FP-004`, tight only at `n = 2` and `n = 3`.

Recorded per target in `population.json`: `id`, the exact `statement`, the
machine-readable `expr` AST, `target_invariant`, `direction`, `template`,
`template_operands`, `invariants_used` with their definitions,
`min_slack_over_D`, `max_slack_over_D`, `counterexamples_in_D`,
`equality_count_in_D`, `equality_by_order_n`, up to 300
`equality_witnesses_graph6` (largest `n` first, i.e. the database edge first,
with a truncation flag), and the full `slack_histogram_over_D`.

---

## 10. Honesty caveats

Recorded now so they cannot be rationalised later.

**(a) `min_slack_over_D` is 0 for all 30, by construction.** Filter F2 requires
sharpness, so the field does not discriminate; the informative fields are
`equality_count_in_D`, `equality_by_order_n` and `slack_histogram_over_D`.
Sharpness is Graffiti's own Dalmatian criterion and dropping it would make the
generator unfaithful — but it does mean **every target hands the wall arm usable
tightness data**. That is the most favourable *fair* setting for the hypothesis
and the analysis should say so.

**(b) The population contains statements that are classical theorems, and the
generator cannot tell.** This is a real property of Graffiti-style generation,
not a defect of this run — Fajtlowicz's own output rediscovered known results
constantly. Reading the final 30 by hand *after* generation, the following look
provable in a line or two from standard facts. This is advisory only:

| id | statement | why it is probably not open |
|---|---|---|
| FP-003 | `alpha >= lambda_max - cutv` | `lambda_max <= alpha` (a maximum independent set in `N(v)` is independent in `G`); `cutv >= 0` |
| FP-006 | `chi >= ceil((omega - chi_regular)/2) + 1` | implied by `chi >= omega` |
| FP-018 | `gamma_t >= floor(gamma/disp_min)` | `disp_min >= 1`, so the right side is at most `gamma <= gamma_t` |
| FP-019 | `kappa <= floor(t/2) + floor(lambda_1)` | `kappa <= delta <= floor(lambda_1)` and `t >= 0` |
| FP-024 | `mu <= ceil((n - chi_tree)/2)` | implied by `mu <= floor(n/2)` in both parities |
| FP-028 | `res <= alpha + CW - 1` | `res <= alpha` (Favaron–Mahéo–Saclé) and `CW >= n/(1+Delta) >= 1` |

**These six were NOT removed.** Removing them would be hand-curation of a
population the preregistration requires to be mechanical and frozen, and the
judgement above is mine, made after the fact from classical knowledge — never
from any evaluation outside `D`. The consequence should be stated in the results:
the effective denominator may be closer to **24** than to 30, and the
preregistered endpoint requires ≥ 20 scored targets. If the analysis scores only
the non-theorem subset it must say so explicitly and report both numbers.

**(c) The reverse risk is unmeasured.** Nothing here estimates how many of the
remaining ~24 are refutable *at all* within a 20–40 vertex budget. A population
where no arm refutes anything is the preregistration's own named failure mode
("the experiment failed to test the hypothesis") and remains a live possibility.

**(d) `D` stops at `n = 8`, smaller than the historical Graffiti databases.**
Graffiti.pc verified against roughly `n <= 11`. Conjectures surviving an
exhaustive `n <= 8` sweep are therefore *easier* to refute than the WOWII
conjectures the campaign has been working on — the database edge here is at 8
vertices, not 11. This cuts both ways: it should raise every arm's hit rate, and
it makes the comparison *between* arms the only thing worth reading, not the
absolute counts.

**(e) The vocabulary is missing the invariants that carried the original case
study.** `L_s` (max-leaf spanning tree) and `tree` (induced tree number) were the
key terms in the WOWII 181 and C₅[K_m] work; `f` and `b` were the pinned
hereditary invariants in the cliff analysis. All four are absent here, three for
lack of a solver and two (`f`, `b`) on measured runtime (§3). The population is
therefore not a re-run of the campaign's home ground — which is the point of a
held-out test — but it also means neither a null nor a positive result can be
attributed to that specific vein.

**(f) The template grammar is narrower than Graffiti's.** Two operands per
right-hand side, integer coefficients up to 3, constants in `[-3, 3]`, and one
level of ceiling/floor. Graffiti emits deeper expressions. This bounds what the
population can contain and is a limit on generality, not on validity.

**(g) Reproducibility — verified, not asserted.** No randomness at any stage;
every tie-break is a fixed `blake2b` hash or lexicographic. `python3
scripts/gen/generate.py` was run twice and the two `population.json` files are
**byte identical** (`sha256sum -c`: OK). The `D` graph6 file is content-hashed
into the population under `database.sha256_graph6_file`. The generator prints its
wall-clock time to stdout but deliberately keeps it *out* of the artifact — a
timing field was in the first version and was the sole reason two runs differed.
