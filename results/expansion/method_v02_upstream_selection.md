# Method v0.2 Trial H: upstream target selection

Selection frozen: **2026-08-12 UTC**

This is a selection report, not a construction search. No transformation named
below was evaluated while preparing this file.

## Source and evidence lock

- Upstream repository: `google-deepmind/formal-conjectures`
- Exact upstream baseline: `547f309edcc2069c1f61c2465729031c10385540`
- Operational corpus: 79 open declarations in 57 modules, as fixed in
  `method_v01_upstream_manifest.md`
- Previous exact evaluations: `formal_conjectures.md`, `family_forest.md`,
  `open_sweep/*.jsonl`, and the checked-in family profiles
- Method rule: select at most two clusters having either equality on at least
  two nonisomorphic graphs, or residual one together with a catalogue
  transformation that targets a specific residual coordinate

The previous upstream refresh found only one new cluster, Dean's `k = 5`
cycle-divisibility conjecture. It remains low priority: it has no numerical
wall, and all admissible campaign graphs already contain a 5-cycle.

## Signed residuals

For WOWII 61 use

```text
R61(G) = f(G) - residue(G) - ceil(diam(G) / 3).
```

For WOWII 133 use

```text
R133(G) = path(G) - radius(G) - floor(l(G))^cC4(G),
```

where `cC4(G) = 1` exactly when `G` has no (not necessarily induced)
4-cycle. In both cases a negative residual is a counterexample.

For Boolean or conditional statements below, the table records the exact
applicable margin or the reason a signed residual is not meaningful.

## Exact applicable-target ranking

The 23 declarations that the upstream sweep classified as concretely
evaluable are completely disposed of here. Closest values are inherited only
from exact computations already committed before this selection.

| upstream cluster | declarations | closest exact evidence | selection |
|---|---:|---|---|
| independent domination | 2 | Petersen odd-case polynomial slack 48; every ILP optimal | exclude: no equality/unit wall |
| Reed omega-delta-chi, universal and finite | 2 | residual `omega + Delta + 2 - 2 chi = 0` on every odd `C5[K_m]`, including nonisomorphic `C5[K3]` and `C5[K5]` | exclude: equality qualifies, but no transformation is known that raises chromatic number while holding both clique number and maximum degree; this is a longstanding human conjecture, not a bounded method-fit trial |
| Reed `Delta = 6`, `omega = 2` | 1 | no arsenal member satisfies both hypotheses | exclude: not applicable |
| Erdős 23 | 1 | `comp(C5[K4])` needs exactly 16 deletions, equal to `20^2/25`; upstream itself records the full uniform `C5` independent-blow-up equality family | exclude: the Lean declaration is an `answer(sorry) ↔ ...` question rather than a direct universal theorem to flip with one witness, and weighted `C5` blow-ups have an immediate minimum-edge-orbit compensation |
| Erdős 64 | 1 | every eligible arsenal graph has a power-of-two cycle (Petersen has an 8-cycle) | exclude: Boolean safe-side result, no wall coordinate |
| Erdős 128 | 1 | the two triangle-free controls meet the density threshold only at equality, so the strict premise is false | exclude: vacuous boundary, not a conclusion wall |
| Erdős 742 | 1 | applicable controls have margins 20 and 10 edges; dense candidate families cease to be diameter-two-critical after one edge deletion | exclude: no equality/unit wall and transformation breaks the hypothesis |
| WOWII 19 | 1 | residual zero on 17 nonisomorphic complete/mixed blob graphs | exclude: structural ladder `b >= l(v)+1+alpha(G-N[v])` blocks the obvious eccentricity move, and an upstream proof/status PR is already active |
| WOWII 40 | 1 | minimum residual 1 at `C5[K2]` | exclude: cycle blow-ups are traceable; leaf/false-twin additions raise `f` at least as quickly as the ceiling of `p+b`, so no separating move is presently specified |
| WOWII 59 | 1 | minimum residual 1 at `C5[K2]` | exclude: competing upstream disproofs already exist, and `residue <= alpha` blocks the campaign blow-up direction |
| **WOWII 61** | **1** | **`C5[K2]`: `f=4`, `residue=2`, `diam=2`, hence `R61=1`** | **include: a degree-preserving 2-switch fixes the Havel--Hakimi residue while it can move diameter across a ceiling boundary** |
| **WOWII 133** | **1** | **exact equality on nonisomorphic `C5` and Petersen: respectively `4=2+2` and `5=2+3`** | **include: graph covers/lifts can preserve degree and C4-freeness while changing radius and longest induced path** |
| WOWII 141 | 1 | minimum residual 1 on `comp(C5[K3])` | exclude: the star at a maximum-local-independence vertex supplies the observed `tree >= lambda_max+1` compensation |
| WOWII 145 | 1 | carrier residual at least 3.5 under the surviving set-eccentricity reading | exclude: no close wall; an upstream solution PR is active |
| WOWII 146 | 1 | minimum residual 4 in the family sweep under the source-faithful set-eccentricity reading | exclude: no close wall; competing proof/status PRs are active |
| WOWII 160 | 1 | official C4-subgraph characteristic makes the carrier residual 15 | exclude: the apparent induced-C4 violation is definitionally invalid; proof/status work is active upstream |
| WOWII 198a | 1 | carrier satisfies the premise at equality and is traceable | exclude: equality is in an implication premise, not a false conclusion; a proof PR is active |
| WOWII 200 | 1 | carrier fails the equality hypothesis | exclude: not applicable; an upstream disproof already exists |
| WOWII 291 | 1 | carrier margin 34 | exclude: no wall and active statement/counterexample work upstream |
| WOWII 314 | 1 | carrier is not triangle-free, so the implication is vacuous | exclude: not applicable; competing solution PRs are active |

This table counts `2+2+1+1+1+1+1+14 = 23` declarations. The two Reed universal
declarations are one mathematical target but remain separately counted to
match the upstream manifest.

## Frozen Trial H1: WOWII 61

### Obstruction and intended separating move

The Havel--Hakimi residue depends only on the degree sequence. A
degree-preserving 2-switch therefore holds `residue(G)` exactly fixed while
potentially changing both diameter and largest induced forest size. This is a
clean coordinate separation unavailable to vertex blow-ups.

Starting from the unit-slack control `C5[K2]`, moving the diameter from 2 to
the interval 4--6 raises `ceil(diam/3)` by one and reaches equality if `f`
stays 4. Reaching diameter at least 7 raises it by two and crosses the wall if
`f` stays 4. These are predictions, not observed outcomes.

### Frozen prediction

Among graphs degree-sequence-equivalent to a dense unit-slack control, a short
sequence of 2-switches may increase `ceil(diam/3)` faster than it increases
`f`. The strongest prospective signature is

```text
residue unchanged, diam >= 7, largest induced forest <= 4.
```

A persistent rule that every three added distance layers force at least one
additional induced-forest vertex is a theorem signal and is a valid negative
outcome.

### Frozen bounds

- bases: every prior exact unit- or two-unit-slack control for 61, beginning
  with `C5[K2]`, plus connected degree-sequence controls through order 12;
- all connected graphs reachable by at most four canonical 2-switches, with
  isomorphic duplicates removed;
- an extension stratum through order 20 only for a base that reaches equality
  within the four-switch stratum;
- exact Havel--Hakimi residue and diameter; exact induced-forest optimization,
  each individual solve capped at 60 seconds;
- stop a degree sequence immediately if an independently checked structural
  lower bound proves `R61 >= 0` for its entire switch class.

## Frozen Trial H2: WOWII 133

### Obstruction and intended separating move

The C4-present branch is provably safe because it reduces to
`path(G) >= radius(G)+1`, which follows from a diameter path. Only the C4-free
branch is live. On a triangle-free graph, every vertex neighborhood is
independent, so a regular C4-free graph has `floor(l(G)) = degree(G)` and the
wall becomes

```text
path(G) >= radius(G) + degree(G).
```

`C5` and Petersen are nonisomorphic equality controls. A graph covering lift
of a girth-at-least-five base preserves degree and the absence of 4-cycles,
while radius and maximum induced-path order can move separately. This targets
the only live branch without changing the local-independence coordinate.

### Frozen prediction

A connected lift of an equality control may raise radius while adding fewer
vertices to a maximum induced path, producing `R133 < 0`. Conversely, if every
such lift admits an induced path of order at least `radius+degree`, the
persistent wall should be promoted to a theorem-shadow investigation rather
than widened into an unstructured graph search.

### Frozen bounds

- exact connected 2-lifts of `C5` and Petersen, quotienting sign assignments
  by vertex switching and automorphisms where available;
- connected cubic C4-free controls through order 24 generated independently
  of the lift representation;
- at most two degree-preserving 2-switches from each control, retaining only
  connected C4-free outputs;
- exact radius and exact longest induced path, with each optimization capped
  at 60 seconds;
- named prior safe-side controls (McGee, Pappus, Desargues, Dodecahedron,
  Kneser `(7,3)`, and Hoffman--Singleton) remain calibration data and are not
  counted as new trials.

## Remaining 54 declarations: unchanged exclusions

Every declaration excluded from fixed-graph residual evaluation in the exact
upstream manifest remains excluded. They are recorded here so Trial H has no
silent omissions.

- **Asymptotic or uniform-over-orders (13):** Erdős 60, 61, 74 (two
  declarations), 80 (two), 82, 85, 108, 566, 579, and 600 (two).
- **Infinite-cardinal graph assertions (11):** Erdős 75, 1068, 1175 (two),
  1176, 595, 740, and 918 (four).
- **Existential or fixed-value questions (18):** Erdős 508, 567 (three), 593
  (three), 596 (two), 835 (three), 944 (three), Conway's 99-graph, Ramsey
  `R(5,5)`, and snake dimension nine.
- **Construction/decomposition universals requiring unbounded auxiliary
  search (8):** Alon--Tarsi short-cycle cover, Erdős 184 (two), Erdős 628,
  graceful labeling, Kotzig, Ringel, and graph pebbling.
- **Pattern-as-variable inequality (1):** Sidorenko's conjecture.
- **Non-arsenal objects encoded through graph helpers (3):** Latin tableaux
  and the two diameter-of-finite-simple-groups declarations.

The counts sum to `13+11+18+8+1+3 = 54`. Together with the 23 concretely
ranked declarations and the two declarations in the already-low-priority Dean
cluster, this accounts for all 79 open declarations at the locked upstream
SHA.

## Selection outcome

Trial H selects exactly two direct upstream targets:

1. WOWII 61: unit residual plus a degree-sequence-preserving transformation;
2. WOWII 133: two nonisomorphic equality controls plus a C4-safe covering
   transformation.

Neither proposed transformation has been evaluated in this report. Any later
result must be written incrementally to a separate report, retain the 60-second
per-solve cap, and pass the database and independent-recomputation gates before
a disproof claim.
