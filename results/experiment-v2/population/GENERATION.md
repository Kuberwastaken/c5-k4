# Generation record — v2 fresh conjecture population

**Produced:** 2026-08-16 UTC, after [`../DESIGN.md`](../DESIGN.md) was committed
and before any v2 arm was run.
**Artifact:** [`population.json`](population.json) — 30 frozen targets.
**Code:** [`../../../scripts/gen2/`](../../../scripts/gen2/).

This is the generation stage of **experiment v2**, whose preregistered question is
narrower than v1's:

> **H1-v2:** on conjectures whose statements involve hereditary induced
> invariants (`f`, `b`, `tree`, `path`, `alpha`), does tightness navigation find
> crossings that generic search misses?

[`../../experiment/RESULTS.md`](../../experiment/RESULTS.md) — v1's near-null
result, wall-unique 1/30 — **stands and is not reinterpreted here**. v1's own
`GENERATION.md` pre-committed that "a null result cannot be blamed on that vein",
and that commitment binds: v2 is a different and smaller question, not a rerun.

Three things had to change, and did:

| | v1 | v2 |
|---|---|---|
| database `D` | connected graphs `n <= 8`, **12,112** | connected graphs `n <= 9`, **273,192** |
| `f`, `b` | computed, **forbidden in emission** (runtime) | emitted |
| `tree`, `path` | **absent from the vocabulary** | emitted |
| restriction | none | **every target uses a hereditary induced invariant** |
| invariant validation | two backends **sharing one polynomial core** | two backends sharing **no code**, checked on all 273,192 |

---

## 1. What was and was not tested — the contamination contract

**Tested:** every candidate inequality was evaluated on every member of `D2`
(all 273,192 connected graphs on `2 <= n <= 9`) and on **nothing else**.

**Not tested — no candidate inequality was ever evaluated on any of these:**
`C5[K_m]` for any `m`, `T(n) = L(K_n)`, Petersen, Kneser, Paley, complete
multipartite, cocktail-party, prisms, Möbius–Kantor, complete bipartite, stars,
brooms, double stars, hypercubes, circulants, grids, random graphs, any
complement of the above, **any graph on `n >= 10`**, or any graph named anywhere
in this repository. There is no random search, no local search, no named-family
catalogue and no counterexample hunt anywhere in `scripts/gen2/`.

**Candidates discarded because they were accidentally learned to be false outside
`D2`: none.** No such event occurred, because no such evaluation occurred.

**The one place graphs outside `D2` appear at all:**
[`bench_hereditary.py`](../../../scripts/gen2/bench_hereditary.py) runs the
hereditary solvers on generic stress structures (paths, cycles, stars, wheels,
complete graphs, balanced binary trees, grids, two circulant families, complete
bipartite, complete multipartite, `Q5`, and seeded `G(n,p)` at
`p = 0.15, 0.3, 0.5, 0.7`) at `n = 10..40`. It prints **timings and
agreement flags only**: no invariant *value* of a non-`D2` graph is printed,
stored, returned or compared with anything except a second implementation of the
same invariant on the same graph, and there is no code path in that file by which
a candidate inequality could be evaluated. It was run **before** any candidate
existed. §5 is its entire output.

**Instruments not read.** `results/experiment/arm-*.json|md`,
`scripts/exp/catalogue.py` and `scripts/exp/wall_*.py` were not opened at any
point during generation. The only v1 artifacts consulted were
`results/experiment/RESULTS.md`, `METHOD_V1_7.md`, `scripts/gen/` and its cached
`data/`, all of which the task directs the generator to reuse. See also honesty
caveat (h) on process-table visibility.

---

## 2. The database `D2` and its exact boundary

**`D2` = every connected graph on `2 <= n <= 9` vertices, up to isomorphism.
It is complete through `n = 9`; no fallback and no partial layer was needed.**

| `n` | connected graphs | A001349 | ok |
|---|---|---|---|
| 2 | 1 | 1 | ✓ |
| 3 | 2 | 2 | ✓ |
| 4 | 6 | 6 | ✓ |
| 5 | 21 | 21 | ✓ |
| 6 | 112 | 112 | ✓ |
| 7 | 853 | 853 | ✓ |
| 8 | 11,117 | 11,117 | ✓ |
| 9 | **261,080** | 261,080 | ✓ |
| **total** | **273,192** | | |

**Boundary, stated exactly:** `D2` contains every connected graph with
`2 <= n(G) <= 9` and nothing else. `K_1` is excluded, as in v1: with no edges and
no neighbourhoods, `deg_avg`, `lambda(v)`, `girth`, `disp` and the domination
invariants are 0 or undefined on it, and Graffiti-lineage databases do not
contain it. Every emitted statement is therefore quantified over **connected
graphs with `n >= 2`** and says so in its own text. No graph on `n >= 10` is in
`D2`, and none was evaluated.

**Source.** `geng -c n` from **nauty 2.8.8** (McKay–Piperno), built from the
nauty source bundled in the `pynauty` 2.8.8.1 sdist (`pip install pynauty` fails
on this box for want of `Python.h`; the bundled nauty itself compiles cleanly).
`geng` emits exactly one representative of each isomorphism class. Build time for
the whole of `D2`: **0.17 s**.

**The database does not depend on trusting `geng`.**
[`graph_db2.py --verify`](../../../scripts/gen2/graph_db2.py) proves it complete
by an independent route and passes on every check:

```
count  n=2..9              all match OEIS A001349
shape  all connected + graph6 round-trip: ok
iso    distinct canonical forms: 273192 / 273192  ok
cover  extensions of n=2 -> 3       candidates -> 2      classes; n=3 has 2;      EQUAL (complete)
cover  extensions of n=3 -> 14      candidates -> 6      classes; n=4 has 6;      EQUAL (complete)
cover  extensions of n=4 -> 90      candidates -> 21     classes; n=5 has 21;     EQUAL (complete)
cover  extensions of n=5 -> 651     candidates -> 112    classes; n=6 has 112;    EQUAL (complete)
cover  extensions of n=6 -> 7056    candidates -> 853    classes; n=7 has 853;    EQUAL (complete)
cover  extensions of n=7 -> 108331  candidates -> 11117  classes; n=8 has 11117;  EQUAL (complete)
cover  extensions of n=8 -> 2834835 candidates -> 261080 classes; n=9 has 261080; EQUAL (complete)
v1     n<=8 agrees with scripts/gen/data/connected_n2_n8.g6 (12112 vs 12112): ok
```

The `cover` argument: every connected graph on `n+1` vertices has a non-cut
vertex, so deleting it leaves a *connected* graph on `n` vertices. Extending
every connected `n`-vertex graph by one new vertex over all `2^n - 1` non-empty
neighbourhoods therefore produces every connected `(n+1)`-vertex graph at least
once. Canonicalising those 2,834,835 extensions and comparing the resulting set
of classes with `geng`'s output gives set equality at every level. The `n <= 8`
part additionally reproduces v1's database, which was built by a completely
different route (networkx atlas + one-vertex extension + VF2).

`sha256(data/connected_n2_n9.g6)` =
`b827d6a3e9dd0fdd01753a17c5c1090453b43a25c2f31b3c5f8f41f3dc136365`, recorded in
`population.json` under `database.sha256_graph6_file`. The file is 2.1 MB and is
the durable artifact; the two invariant-matrix caches (5.0 MB each) are
regenerable and are git-ignored.

---

## 3. Invariant vocabulary

**51 invariants computed, 51 emitted. Nothing is excluded for runtime.** All
values are exact `int` or `Fraction`; no floating-point value enters any quantity
a conjecture depends on. Definitions follow
[`data/INVARIANT-GLOSSARY.md`](../../../data/INVARIANT-GLOSSARY.md) (DeLaViña's
WOWII definitions database).

| group | invariants |
|---|---|
| order, size, degrees | `n`, `m`, `Delta`, `delta`, `sigma_2`, `Sigma_2`, `dd`, `f_1`, `deg_avg` |
| degree-sequence machinery | `res`, `A`, `SW`, `CW` |
| distance | `diam`, `rad`, `girth`, `ecc_avg`, `dist_even_min`, `dist_even_max`, `Tdist_min`, `Tdist_max`, `dist_avg` |
| connectivity, counting | `kappa`, `cutv`, `t`, `disp_min`, `disp_max`, `disp_avg` |
| spectral | `floor(lambda_1)`, `ceil(lambda_1)` |
| clique, colouring, matching, local independence | `omega`, `chi`, `mu`, `lambda_max`, `lambda_min`, `lambda_avg` |
| domination | `gamma`, `gamma_t`, `gamma_2`, `gamma_i` |
| **hereditary induced** | **`alpha`, `f`, `b`, `tree`, `path`** |
| 0/1 characteristic functions | `chi_bipartite`, `chi_K3free`, `chi_C4free`, `chi_clawfree`, `chi_regular`, `chi_tree` |

### The hereditary block, which is the point of v2

* **`alpha`** independence number — order of a largest induced edgeless subgraph
* **`f`** forest number — order of a largest induced forest
* **`b`** bipartite number — order of a largest induced bipartite subgraph
* **`tree`** tree number — order of a largest induced tree
* **`path`** path number — order (vertex count) of a largest induced path

All five are **orders** (vertex counts). A single vertex is a tree and a path, so
on a connected graph with `n >= 2` all five are `>= 1` and `f, b, tree, path >= 2`.
This is the convention under which the campaign's own `C5[K_m]` case study reads
`f = b = tree = 4`.

v1 computed `f` and `b` but forbade their use on measured runtime, and never had
`tree` or `path` at all. §5 shows the measurements that make the v2 choice
defensible: the cost is managed by capping **evaluation order** and by branch and
bound with early exit, not by dropping the invariants.

### Other conventions pinned here

* **`girth`** = number of vertices of a shortest cycle, and **`n + 1` if `G` is
  acyclic**. Any cycle of an `n`-vertex graph has at most `n` vertices, so inside
  the universe of quantification `n+1` behaves exactly like `+inf` while keeping
  every statement finitely checkable.
* **`dist_even(v)`** counts `v` itself (distance 0 is even).
* **`gamma_2`**: every vertex outside the set has at least two neighbours in it; a
  vertex settles its own constraint by being selected.
* **`floor(lambda_1)` / `ceil(lambda_1)`** are computed exactly, with no
  eigenvalue arithmetic, by two unrelated methods — see §4.

### Still excluded from the vocabulary

* **`maxine`** — the greedy "delete a maximum-degree vertex" process is tie-break
  dependent, so it is not an isomorphism invariant and cannot appear in a
  well-defined universal statement.
* **`p(G)` (path covering number), `L_s`/`gamma_c` (max-leaf spanning tree /
  connected domination), `alpha'` (critical independence)** — no exact solver here
  decides them and no ILP solver is installed. Note that v1's exclusion list also
  contained `path` and `tree`; both are now in, with exact solvers (§5).

---

## 4. R4 — cross-validation of every invariant before freezing

METHOD v1.7 **R4** requires every invariant to be validated against a second
independent implementation over the whole database *before* the population is
frozen. The v1 defect it was written for was `ceil(lambda_1)`, and the reason it
escaped is structural: **v1's two backends shared one `_poly_part`**, so every
polynomial invariant — the spectral bracket included — was implemented once and
"cross-checked" against itself.

**In v2 the two backends share no code.**

| | backend **A** | backend **B** |
|---|---|---|
| graph representation | own graph6 decoder → bit-masks, **no networkx at all** | networkx objects |
| polynomial invariants | own bit-mask BFS / pop-count code | networkx (`eccentricity`, `core_number`, `articulation_points`, `triangles`, `node_connectivity`, `all_pairs_shortest_path_length`, `max_weight_matching`, `is_tree`, `is_bipartite`) |
| spectral bracket | Sylvester leading-minor definiteness of `kI − A` (Bareiss, integer), plus a positive-**semi**definiteness test | exact integer characteristic polynomial by Newton's identities, then Taylor positivity of all derivatives |
| `chi` | DSATUR branch and bound | independent-set cover DP over all `2^n` subsets |
| `alpha`, `omega`, `f`, `b`, `tree`, `path`, `gamma*`, `lambda*` | exhaustive `2^n` subset scan in decreasing (or increasing) size with early exit | the branch-and-bound solvers an arm would run at `n = 20..40` |

The per-invariant pairing is recorded machine-readably in
`invariants2.CROSSCHECK_PATHS` and copied into
`scripts/gen2/data/crossval_ok.json`.

### Result

```
== R4 cross-validation: backend A vs backend B on all 273192 members ==
   51 of 51 invariants:  0 mismatches
TOTAL MISMATCHES: 0  ->  PASS
```

`generate2.py` refuses to run unless `data/crossval_ok.json` exists, records
`passed: true`, and carries the same database sha256 — so the population
**cannot** be frozen ahead of the check.

### Bugs the check caught, pre-freeze

**One real bug, found and fixed before anything was frozen.**

| invariant | disagreement | which side was wrong | cause |
|---|---|---|---|
| `res` (residue) | **55,204 of 273,192** members | backend **B** | the counting-array Havel–Hakimi demoted a vertex from degree `d` to `d−1` and then met it again at level `d−1` inside the *same* step, demoting it twice |

Backend A implements the textbook process directly (pop the largest degree,
decrement the next `d` largest, re-sort) and was confirmed correct by hand on the
first disagreeing members (`DEk`, degree sequence `[3,3,2,1,1]`: HH gives
`[2,1,1,0] → [0,0,0]`, residue 3; B returned 2). Backend B's residue was
rewritten to park demotions in a separate buffer and fold them back only at the
end of the step; the whole backend-B matrix was then **recomputed from scratch**
and the cross-check re-run, giving 0 mismatches. Nothing was frozen in between.

### Regression witness: v1's `ceil(lambda_1)` rule, re-run on `D2`

v1 declared `lambda_1` an integer whenever `det(floor(lambda_1)·I − A) == 0`,
which fires whenever *any* eigenvalue equals `floor(lambda_1)`. Replaying that
rule over `D2`:

```
v1's rule is wrong on 96 of 273192 members of D2  (by order: n=5:1, 6:1, 7:2, 8:15, 9:77)
restricted to n <= 8 (v1's database D): 19 wrong of 12,112 — v1's own post-hoc audit
                                        found 19 (REPRODUCED)
```

The `19` reproduces v1's own figure exactly, which is a check on *this* report as
much as on v1.

### Third path: v1's generator itself, on the slice both databases share

v1's cached invariant matrix (a third, older codebase) was matched to `D2`'s
`n <= 8` slice by canonical form and compared:

```
== third path: v1's generator (scripts/gen) on the shared n <= 8 slice ==
spec_ceil      19   <-- v1 defect
48 of the 49 shared invariants agree everywhere; disagreements only on: ['spec_ceil']
```

So on the 12,112 graphs the two experiments share, **three independent
implementations agree on 48 of 49 shared invariants**, and the single
disagreement is exactly the v1 defect that METHOD v1.7 R4 was written about,
on exactly the 19 graphs v1 identified.

---

## 5. The hereditary invariants: exactness and measured runtime

### Exactness

Two separate bodies of evidence.

**(i) All of `D2`.** The exhaustive `2^n` scan (backend A) and the
branch-and-bound solver (backend B) agree on `alpha`, `f`, `b`, `tree` and `path`
on **every one of the 273,192 members** — part of the §4 zero-mismatch result.

**(ii) Stress graphs at `n = 10, 12, 14, 16, 18, 20`.** Up to twelve generic
structures per order — path, cycle, `2 × n/2` grid, complete, complete bipartite,
complete multipartite, circulant `C_n(1,3)`, wheel, and seeded `G(n,p)` at
`p = 0.15, 0.30, 0.50, 0.70`; the complete multipartite construction is skipped
at orders not divisible by 5, so the counts are 12, 11, 11, 11, 11, 12 — each
solved both ways:

```
RESULT: 340 agreements, 0 disagreements, 0 not finished inside the cap
```

**Every one of the five solvers is therefore verified exact to `n = 20`**, with
no case left unresolved, on top of exhaustive agreement over the whole database.

### Measured per-graph runtime — the data the arms' budgets come from

CPU seconds per graph, cap 60 s CPU, over the stress list of §1 (15 graphs at
`n = 20` and `n = 30`, 16 at `n = 40`). CPU time rather than wall time because
this box was running other agent sessions concurrently; see caveat (h).

The lists are *centred* on 20/30/40 rather than exactly at them: the balanced
binary tree has `2^(h+1) - 1` vertices (15 in the `n = 20` group, 31 in the
`n = 30` and `n = 40` groups) and `Q5` has 32 in the `n = 40` group. All four
deviating entries are **smaller** than the nominal order and all are sparse, so
they can only make the reported medians optimistic; none of them is among the
graphs that blow the cap, so the over-cap counts are unaffected.

| `n` | invariant | median | p90 | worst | over 60 s |
|---|---|---|---|---|---|
| 20 | `alpha` | 0.000 | 0.000 | 0.000 | 0/15 |
| 20 | `f` | 0.026 | 1.204 | 2.854 | 0/15 |
| 20 | `b` | 0.010 | 0.055 | 0.077 | 0/15 |
| 20 | `tree` | 0.029 | 0.159 | 0.434 | 0/15 |
| 20 | `path` | 0.006 | 0.037 | 0.041 | 0/15 |
| 30 | `alpha` | 0.000 | 0.006 | 0.009 | 0/15 |
| 30 | `f` | 0.485 | 18.456 | > 60 | **1/15** |
| 30 | `b` | 0.010 | 2.124 | 3.238 | 0/15 |
| 30 | `tree` | 1.107 | 20.459 | > 60 | **1/15** |
| 30 | `path` | 0.013 | 0.595 | 0.728 | 0/15 |
| 40 | `alpha` | 0.000 | 0.009 | 0.010 | 0/16 |
| 40 | `f` | > 60 | > 60 | > 60 | **8/16** |
| 40 | `b` | 0.036 | > 60 | > 60 | **3/16** |
| 40 | `tree` | > 60 | > 60 | > 60 | **8/16** |
| 40 | `path` | 0.078 | 7.477 | 8.557 | 0/16 |

**What this licenses, stated as an evaluation-order cap rather than an
exclusion** — which is the difference between v1's response and v2's:

| targets | invariants named | decidable inside 60 s CPU | count |
|---|---|---|---|
| `FP2-008 011 012 013 015 017 021 023 027 028 029 030` | name `f` or `tree` | to **`n = 30`** (dense random graphs at `n = 40` blow the cap) | 12 |
| `FP2-005 006 007 010 024` | name `b`, not `f`/`tree` | to `n = 30` comfortably; at `n = 40`, 3 of 16 stress graphs blow the cap | 5 |
| the other 13 | `alpha`/`path` only, or no hereditary term beyond `alpha` | to **`n = 40`** | 13 |

The over-cap cases are all dense: `G(n, 0.3..0.7)`, `K_n` and the complete
multipartite graphs. Sparse and structured graphs at `n = 40` are decided in
well under a second. An arm looking for a counterexample to one of the 12
`f`/`tree` targets should be budgeted at order `<= 30`, or at order `<= 40` on
sparse constructions, and told so — that is exactly the number the design asked
to be set from data instead of guessed.

---

## 6. Emission rules

A candidate is `t REL E`, `REL` in `{<=, >=}`, `E` from the template tables.
**The grammar is unchanged from v1**: small integer coefficients, sums and
differences of two invariants, and ceilings/floors of halves, thirds and
invariant/invariant ratios.

**Targets (18, both directions each):** `alpha`, `omega`, `chi`, `mu`, `gamma`,
`gamma_t`, `gamma_2`, `gamma_i`, **`f`, `b`, `tree`, `path`**, `res`, `A`,
`diam`, `rad`, `kappa`, `lambda_max`. Order/size parameters and the 0/1
characteristic functions appear only on the right, as Graffiti uses them. v1 had
the same list minus `tree` and `path` and with `f`, `b` removed for runtime.

**Templates (51, identical to v1):** 31 unary (`x+c`, `2x+c`, `3x+c`,
`ceil(x/2)+c`, `floor(x/2)+c`, `ceil(x/3)+c`, `floor(x/3)+c`), 7 binary symmetric
(`x+y+c`, `ceil((x+y)/2)+c`, `floor((x+y)/2)+c`), 13 binary asymmetric (`x−y+c`,
`ceil((x−y)/2)+c`, `floor((x−y)/2)+c`, `2x−y+c`, `ceil(x/2)+y`, `floor(x/2)+y`,
`ceil(x/y)`, `floor(x/y)`).

`ceil(x/y)` and `floor(x/y)` are built only over denominators provably `>= 1` on
every connected graph with `n >= 2` — **42 of the 51** (`tree` and `path` join the
list; `f_1`, `cutv`, `t` and the six characteristic functions stay out because
each vanishes somewhere). `generate2.py` re-asserts positivity of all 42 columns
over all of `D2` at run time rather than trusting the argument. No emitted
statement can be undefined anywhere in its own universe of quantification.

Exactness of the scaled sweep: every `Fraction`-valued invariant on `n <= 9` has
a denominator dividing `SCALE = lcm(1..9) = 2520`, and the loader asserts this
graph by graph, so the `int64` sweep is an exact representation, not a rounding.

**Filters.** A candidate is kept iff all of:

| | rule | rationale |
|---|---|---|
| F1 | **zero counterexamples over all of `D2`** | this is what makes it a conjecture rather than a refuted guess |
| F2 | **sharp**: equality attained on at least one member of `D2` | Graffiti's Dalmatian significance criterion; also the tightness data the wall arm is entitled to |
| F3 | **not an identity**: equality does not hold on all of `D2` | an identity is a definitional relation, not a conjecture |
| F4 | the right-hand side is **non-constant** on `D2` | a constant bound expresses no relation between invariants |
| F5 | the right-hand side does **not** mention the target | rules out `alpha <= alpha + 1` |
| **F6** | **the statement uses at least one of `alpha`, `f`, `b`, `tree`, `path`** | **new in v2: the population's defining restriction** |

**Finite-universality is structural, not a filter.** Every emitted statement reads
"for every connected graph `G` with `n(G) >= 2`, `<inequality between computable
invariants of G>`" — no asymptotics, no quantifiers over families, no
non-computable terms, no hypotheses, so a single explicit graph refutes any of
them. Nothing was dropped at this step because nothing of another shape can be
generated.

---

## 7. Counts at every stage

| stage | count |
|---|---|
| database `D2` | **273,192** graphs |
| invariants computed / emitted | 51 / **51** (v1: 49 / 47) |
| target invariants × directions | 18 × 2 = 36 |
| distinct right-hand-side expressions enumerated | **42,756** |
| … rejected, constant on `D2` (F4) | 521 |
| (expression, target) pairs rejected, target on the right (F5) | 59,146 |
| (expression, target) pairs rejected, **no hereditary invariant (F6)** | **855,580** |
| … rejected by the deterministic stride pre-filter (a counterexample on 1 graph in 37) | 448,054 |
| **candidate statements evaluated against all of `D2`** | **157,680** |
| … rejected, counterexample in `D2` (F1) | 29,027 |
| … rejected, not sharp (F2) | 81,630 |
| … rejected, identity on `D2` (F3) | 0 |
| **survivors of F1–F6** | **47,023** |
| after dedup D-S (identical slack vector over `D2`) | 44,599 |
| after dedup D-C (structural cluster) | **12,219** |
| after dedup D-D (Dalmatian domination) | **1,298** |
| **selected into the frozen population** | **30** |

The pre-filter is an optimisation, not a filter: it only ever rejects candidates
that a full `D2` sweep would also reject (it finds a counterexample among a fixed
1-in-37 stride sample of the database's fixed order). The `f1_counterexample`
count is therefore conditional on having survived it; the two rows together are
the true F1 rejection count.

Generation wall clock: **668 s**, on top of 356 s to build the backend-A
invariant matrix, 1,064 s for backend B, and 0.17 s to build `D2` itself.

---

## 8. Deduplication and selection

Unchanged in substance from v1; only the implementation differs, because a slack
vector over `D2` is 2.2 MB and v1's approach of holding one per cluster would need
~27 GB.

**D-S — identical behaviour on `D2`.** Same target, same direction, same slack
vector over all 273,192 graphs: one statement wearing two hats. One
representative survives, the simplest surface form (fewest invariant symbols,
then shortest rendering, then lexicographic). Simplicity is used here and only
here, where the alternatives are provably the same statement on `D2`, so the
choice is cosmetic. `47,023 → 44,599`.

**D-C — structural cluster.** Cluster = `(target, direction, set of invariant
symbols used)`; everything built from the same invariants, about the same target,
in the same direction collapses to one representative, chosen by the coin below.
`44,599 → 12,219`.

**D-D — Dalmatian domination.** Within each `(target, direction)`, drop any
representative that another beats or ties on **every** member of `D2` — uniformly
no stronger, so it carries no information the other does not. `12,219 → 1,298`.
Implemented as a two-stage test: a domination is first refuted on a fixed 1-in-25
stride sample (sound, because a domination failing on a subset fails on the whole)
and only confirmed on full 273,192-entry vectors when the sample does not refute
it.

**Selection to 30.** Primary criterion, as specified: **maximise the diversity of
invariant sets** — greedy maximin on Jaccard distance between invariant sets,
under quotas of at most 3 targets per left-hand-side invariant and at most 2 per
`(left-hand side, direction)`.

**Ties are broken by a deterministic coin**, `blake2b(salt ‖ statement)`, not by
any property of the mathematics — the same choice v1 made and for the same
reason:

> Ranking candidates by **how often they are tight** promotes near-identities and
> would be optimising for the mechanism under test. Ranking by **simplicity**
> promotes the same textbook theorems from the other side. Both are thumbs on the
> scale. A coin is not. `blake2b` is stable across runs and machines, so the
> population stays reproducible.

**No thumb was placed on the hereditary distribution.** The selector is v1's,
unmodified; F6 is the only v2-specific rule, and it is a hard structural filter
applied before any ranking. The distribution in §9 is what the unmodified
selector produced.

---

## 9. Verification of the frozen population

[`verify_population2.py`](../../../scripts/gen2/verify_population2.py) re-derives
every claim in `population.json` on a code path that shares nothing with the
generator's sweep: **backend B's** invariant values (networkx + branch and bound +
characteristic polynomial) instead of backend A's, and the JSON `expr` AST
evaluated in exact `Fraction` arithmetic by `expressions2.evaluate` instead of the
scaled-`int64` numpy template functions. For all 30 targets over all 273,192
graphs it checks: zero counterexamples; the recorded min and max slack; the
recorded equality count and its breakdown by order; that every recorded graph6
witness really attains equality; and that the `relation` string renders from the
recorded AST.

```
render: all 30 relation strings reproduce from their ASTs
PASS: all 30 targets reproduce exactly on an independent code path
      (backend B values, Fraction AST evaluation, all 273192 graphs).
```

**Reproducibility — verified, not asserted.** No randomness at any stage; every
tie-break is a fixed `blake2b` hash or lexicographic. `generate2.py` was run twice
and the two `population.json` files are byte identical
(`sha256 20368346da027b579b3de756c3bacf8e18171c840d8a146e7e1e08649c48c745`). As in
v1, wall-clock timings are printed to stdout and deliberately kept **out** of the
artifact.

---

## 10. What is in the population

30 targets, all of the form "for every connected graph `G` with `n(G) >= 2`,
`<inequality>`".

**Hereditary content — the reason this population exists:**

| invariant | targets using it | share |
|---|---|---|
| `f` | 8 | 27% |
| `alpha` | 7 | 23% |
| `path` | 7 | 23% |
| `b` | 5 | 17% |
| `tree` | 5 | 17% |
| **at least one of `f`, `b`, `tree`, `path`** | **23** | **77%** |
| only `alpha` among the hereditary five | 7 | 23% |
| a hereditary invariant as the **left-hand side** | 12 | 40% |

Every one of the 30 satisfies F6 by construction.

**Shape:** 16 distinct left-hand-side invariants; 33 of the 51 vocabulary
invariants appear somewhere; 22 lower bounds and 8 upper bounds; 16 distinct
templates; **16 of 30 contain a ceiling or a floor** and 4 contain an
invariant/invariant ratio; every target names exactly two right-hand-side
invariants (three including the target).

**Tightness:** equality witnesses in `D2` — fewest 1, median 92, most 46,990.
`min_slack_over_D = 0` for all 30 (see caveat (a)); `max_slack_over_D` ranges 3 to
14. **29 of 30 are tight on at least one graph at `n = 9`**, the database edge;
the exception is `FP2-011` (`f >= ceil(f_1/2) + CW`), tight only on `K_2`.

| id | statement | hereditary invariants |
|---|---|---|
| FP2-001 | `alpha <= floor((Tdist_max - disp_max)/2) + 1` | alpha |
| FP2-002 | `alpha >= f_1 + disp_min - 2` | alpha |
| FP2-003 | `alpha >= floor((res + lambda_max)/2)` | alpha |
| FP2-004 | `A >= alpha - dist_even_min + 1` | alpha |
| FP2-005 | `A >= ceil((b - dist_avg)/2)` | b |
| FP2-006 | `b >= 2*rad - cutv` | b |
| FP2-007 | `b >= ceil(lambda_avg/2) + ecc_avg` | b |
| FP2-008 | `chi >= f - tree` | f, tree |
| FP2-009 | `chi >= gamma_2 - alpha` | alpha |
| FP2-010 | `diam >= floor((b - Delta)/2)` | b |
| FP2-011 | `f >= ceil(f_1/2) + CW` | f |
| FP2-012 | `f >= ceil(n/SW)` | f |
| FP2-013 | `gamma <= f - cutv + 2` | f |
| FP2-014 | `gamma >= dist_even_min - path + 1` | path |
| FP2-015 | `gamma_2 <= ceil((A + tree)/2) + 1` | tree |
| FP2-016 | `gamma_i >= 2*rad - path + 1` | path |
| FP2-017 | `gamma_t <= floor((f + dist_avg)/2) + 1` | f |
| FP2-018 | `gamma_t >= 2*rad - alpha` | alpha |
| FP2-019 | `lambda_max >= floor(dist_even_max/path)` | path |
| FP2-020 | `mu <= ceil(path/2) + girth` | path |
| FP2-021 | `mu <= floor((f + deg_avg)/2) + 1` | f |
| FP2-022 | `omega >= ceil(diam/alpha)` | alpha |
| FP2-023 | `omega >= dist_even_max - f + 1` | f |
| FP2-024 | `path <= b - f_1 + 2` | b, path |
| FP2-025 | `path >= 2*dist_avg - ecc_avg + 1` | path |
| FP2-026 | `path >= floor(disp_min/2) + diam` | path |
| FP2-027 | `res <= f - rad + 1` | f |
| FP2-028 | `res >= dist_even_min - tree + 2` | tree |
| FP2-029 | `tree >= ceil(n/omega)` | tree |
| FP2-030 | `tree >= floor((disp_max + ecc_avg)/2) + 1` | tree |

Recorded per target in `population.json`: `id`, the exact `statement`, the
machine-readable `expr` AST with `rel`/`lhs`/`rhs`, `target_invariant`,
`direction`, `template`, `template_operands`, `invariants_used`,
`hereditary_invariants_used`, `invariant_definitions`, `min_slack_over_D`,
`max_slack_over_D`, `counterexamples_in_D`, `equality_count_in_D`,
`equality_by_order_n`, up to 300 `equality_witnesses_graph6` (largest `n` first,
i.e. the database edge first, with a truncation flag), and the full
`slack_histogram_over_D`. Field names are v1's unchanged; `D` in them denotes
`D2`, and the file says so in its `note`.

---

## 11. Honesty caveats

Recorded now so they cannot be rationalised later.

**(a) `min_slack_over_D` is 0 for all 30, by construction.** Filter F2 requires
sharpness, so the field does not discriminate; the informative fields are
`equality_count_in_D`, `equality_by_order_n` and `slack_histogram_over_D`.
Sharpness is Graffiti's own Dalmatian criterion and dropping it would make the
generator unfaithful — but it does mean **every target hands the wall arm usable
tightness data**, exactly as in v1. That is the most favourable *fair* setting for
the hypothesis and the analysis should say so.

**(b) The population contains statements that are classical theorems, and the
generator cannot tell.** This is a property of Graffiti-style generation, not a
defect of this run. Reading the 30 by hand *after* generation, several look
provable in a line or two from standard facts — for instance `FP2-029`
(`tree >= ceil(n/omega)`) and `FP2-012` (`f >= ceil(n/SW)`) are colouring-style
counting bounds, `FP2-008` (`chi >= f - tree`) is weak because `f - tree` is
small, and `FP2-011` (`f >= ceil(f_1/2) + CW`) is tight only on `K_2`. **None was
removed.** Removing them would be hand-curation of a population the design
requires to be mechanical and frozen, and the judgement is mine, made after the
fact from classical knowledge — never from any evaluation outside `D2`. The
consequence should be stated in the results: the effective denominator may be
smaller than 30, and the preregistered endpoint requires >= 20 scored targets. An
analysis that scores only a subset must say so and report both numbers.

**(c) The reverse risk is unmeasured.** Nothing here estimates how many of the 30
are refutable *at all* within a 20–40 vertex budget. A population where no arm
refutes anything is the preregistration's own named failure mode and remains a
live possibility — and it is *more* likely here than in v1, because `D2` is 22.6×
larger and one vertex deeper, which is the whole point of the change.

**(d) The `n = 9` edge is harder than v1's but still short of Graffiti's.**
Graffiti.pc verified against roughly `n <= 11`. Conjectures surviving an
exhaustive `n <= 9` sweep are still easier to refute than the WOWII conjectures
the campaign works on. This cuts both ways and makes the comparison *between*
arms the only thing worth reading, not the absolute counts.

**(e) Two of the five hereditary invariants cannot be decided at `n = 40` on dense
graphs.** §5 is explicit: `f` and `tree` blow the 60 s cap on 8 of 16 stress
graphs at `n = 40`, and `b` on 3 of 16. v1's response to this was to delete the
invariants; v2's is to cap the evaluation order at 30 for the 12 targets that
name `f` or `tree` and to report the measurement. That is a real restriction on
where those 12 targets can be refuted, and any arm that is budget-limited to
`n <= 30` on 12 of 30 targets is not on an equal footing with one working at
`n <= 40` on the other 18. This must be carried into the arm design (R3) and into
the analysis.

**(f) `L_s` (max-leaf spanning tree) is still missing.** It was one of the key
terms in the WOWII 181 and `C5[K_m]` work and there is still no exact solver for
it here. `f`, `b` and `tree` — the pinned hereditary invariants of the cliff
analysis — are now present, so the v1 caveat that "the vocabulary is missing the
invariants that carried the original case study" is *partly* repaired, not fully.

**(g) The template grammar is narrower than Graffiti's.** Two operands per
right-hand side, integer coefficients up to 3, constants in `[-3, 3]`, one level
of ceiling/floor. Unchanged from v1 by design, and a limit on generality, not on
validity.

**(h) Process-table visibility during generation (R2-adjacent).** This box ran
other agent sessions throughout. A concurrent **v1** arm run
(`scripts/exp/generic/search.py`) was visible in `ps` output while the v2
generator was being built; its command lines named v1 target ids (`FP-0xx`) and
nothing about v2. No arm file was read, no v1 arm information entered the v2
pipeline, and the v2 population did not exist in any form until after those
observations. It is recorded because R2 makes process-table visibility an
integrity matter, not because a leak is suspected. The same contention is why §5
reports **CPU** time rather than wall time.

**(i) The database depends on nauty for its construction, though not for its
correctness.** `geng` produced the graphs; the count check against A001349, the
distinct-canonical-form check, and the independent one-vertex-extension coverage
proof (§2) are what establish that `D2` is exactly the set claimed. Re-running
`graph_db2.py --rebuild` needs `geng` on `PATH`; the frozen `connected_n2_n9.g6`
and its sha256 are what the population is actually pinned to.

**(j) `alpha` alone satisfies F6 for 7 of the 30 targets.** The design names
`alpha` among the hereditary induced invariants, so those 7 are within the
preregistered restriction — but `alpha` was already in v1's vocabulary, so those
7 targets are not, on their own, new ground. The 23 that name `f`, `b`, `tree` or
`path` are. Any claim that v2 tested the mechanism on terrain v1 could not
represent should use **23**, not 30, as its denominator.
