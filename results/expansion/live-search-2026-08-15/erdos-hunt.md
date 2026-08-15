# Erdős Problems finite-counterexample hunt — live search 2026-08-15

---

# HANDOFF STATE (written 2026-08-15, agent replaced mid-run)

## Triage — COMPLETE

All **603** `@[category research open]` declarations in the **364** untouched
`ErdosProblems` files were extracted from upstream `2411d22e` and classified.
The full table is below (section "Triage counts" → the 603-row table).
**Do not redo this.** Result: **575 NOT_FINITELY_REFUTABLE, 28
CANDIDATE_FOR_DEPTH** (in 25 files).

The 28 candidates, by file:
`10` (granville_soundararajan_odd), `11` (×3: erdos_11, not_four_dvd,
two_pow_two), `189` (parallelogram), `241` (generalization), `242` (erdos_242),
`274` (herzog_schonheim), `324` (quintic), `349`
(complete_for_alpha_in_Ioo_one_to_goldenRatio), `364` (erdos_364), `406`
(one_two), `409` (sigma_termination), `477` (×2: X_pow_three, monomial), `535`
(sunflower_strong), `617` (erdos_617), `677` (erdos_677), `779` (erdos_779),
`931` (exists_prime), `952` (erdos_952), `982` (erdos_982), `1041` (erdos_1041),
`1044` (fixed_degree), `1055` (selfridge_limit), `1084`
(triangular_optimal_d2), `1113` (filaseta_finch_kozek), `1135` (erdos_1135).

## Depth — COMPLETED (written up in full below, sections D1–D4 plus D5–D9 here)

| target | verdict | one line |
|---|---|---|
| 931 `exists_prime` | `HOLD_BOUNDED` | 161,590,323 tuples over all prime-free runs ≤ 3·10^5, 0 hits |
| 10 `granville_soundararajan_odd` | `HOLD_BOUNDED` | all n ≤ 2·10^7, 0 failures; Grechuk fixture reproduced |
| 11 (×3) | `HOLD_BOUNDED` | all n ≤ 5·10^7, 0 failures incl. the n ≡ 2 (mod 4) class |
| 677 `erdos_677` | `HOLD_BOUNDED` | dict sweep n,m ≤ 2·10^5 k ≤ 12 + complete-in-m divisor-run n ≤ 40 k ≤ 24, 0 hits |
| 364 `erdos_364` | `HOLD_BOUNDED` | 680,331 powerful numbers ≤ 10^11, 0 triples (16 pairs as control) |
| 406 `one_two` | `HOLD_BOUNDED` | 2^m base-3 digits ⊆ {1,2} only for m ∈ {0,1,2,3,4,15} up to m = 4000 |
| 324 `quintic` | `HOLD_BOUNDED` | 1,124,250 sums a^5+b^5, a<b<1500, 0 collisions |
| 1084 `triangular_optimal_d2` | **`STATUS_SYNC` (finding, not a counterexample)** | see D8 |
| 409 `sigma_termination` | **`CERTIFICATE_SHAPE_FAIL` (triage correction)** | see D9 |

## Depth — MID-WAY when stopped: **Erdős 242** (the one live thread)

`Erdos242.erdos_242 : ∀ n, 2 < n → ∃ x y z, 1 ≤ x ∧ x < y ∧ y < z ∧ (4/n:ℚ) = 1/x+1/y+1/z`

What is established:
* Source (erdosproblems.com/242, status **FALSIFIABLE**) states the **distinct**
  `1 ≤ x < y < z` version verbatim, so the Lean is source-faithful — there is
  **no** formalization divergence to exploit here.
* Source notes: verified for all `n ≤ 10^18` [MiDu25]; "It suffices to prove
  this when n is prime." So a small counterexample is already excluded by prior
  art — expected verdict is `HOLD_BOUNDED` / prior-art stop.
* Run `verify_erdos_misc.py es242 3000`: phase 1 (capped search, `ycap=20000`,
  400k-op budget per n, x descending) covered `n = 3..2901` and left **178
  unresolved** n (budget/cap exhausted, NOT failures). Phase 2 (exhaustive
  per-n search) then hit the 52 s cap and checked **none** of them.
* **UNVERIFIED:** those 178 n. They are almost certainly fine (they are only
  "not settled within the phase-1 cap"), but the exhaustive pass was never run.
  Next agent: run `es242` phase 2 alone on the unresolved list, or raise
  `ycap`. The exhaustive routine `es242_solve(n)` with `ycap=None, budget=None`
  is complete: `x ∈ (n/4, 3n/4]`, then `y ∈ (q/p, 2q/p]` where
  `p/q = 4/n − 1/x` reduced, `z = qy/(py−q)`.

## Depth — NOT STARTED

* **779 `erdos_779`** (Deaconescu). Script mode `d779` is written and untested.
  Source: "Does there always exist some prime p with p_n < p < P such that P+p
  is prime?" Site status **FALSIFIABLE**; Deaconescu verified n ≤ 1000; Cambie:
  "the chances of failing are ridiculously small". Lean index-shift
  (`range (n+1)`, `hn : n ≥ 1`) matches source `n > 1` — **no divergence**.
  Note: a *finite refutation* is only possible for tiny n (all p < P must be
  ruled out), so realistically this is `CONSTRUCTION_ONLY` in practice.
* **982**, **274**, **617**, **1113**, **1135**, **1055**, **535**, **477**,
  **952**, **1041**, **1044**, **349**, **241**, **189** — see the "residual
  candidate dispositions" table below; all are strict stops or prior-art stops
  and were deliberately deprioritised.

## Time-savers for the next agent

1. **erdosproblems.com fetch.** Plain `curl` with the *default* UA gets a
   Cloudflare 403. `curl -H 'User-Agent: Mozilla/5.0 …'` returns **HTTP 200** —
   no browser needed. The `browse` skill is **unusable on this box** (its
   `browser-manager.ts` hardcodes `headless: false`, no X server; it
   mis-reports the failure as "No available port in range 9400-9409").
   Best endpoints:
   * `https://www.erdosproblems.com/latex/<id>` — canonical LaTeX; `<div
     id="content">` = statement, `<div class="problem-additional-text">` =
     notes + references.
   * `https://www.erdosproblems.com/<id>` — `<div id="prize">` = status line
     (`OPEN` / `FALSIFIABLE` / `VERIFIABLE` / `SOLVED` / prize).
   * **No JSON API** (`/api/problems/<id>` → Flask 404).
   * `teorth/erdosproblems` exists (`data/problems.yaml`) but carries only
     metadata (status/formal_status/formalized/tags/prize), **no statements**.
   * **Already fetched for 26 ids** (10, 11, 137, 189, 241, 242, 274, 324, 349,
     364, 406, 409, 477, 535, 617, 677, 779, 931, 952, 982, 1041, 1044, 1055,
     1084, 1113, 1135) and cached at
     `/tmp/claude-1000/-Users-kuber-mehta-Projects-scratch/21f73cfa-6e97-457f-8bb8-ae31d911cc43/scratchpad/erdos_sources.json`
     (may be wiped with the session — re-fetch is ~2 min).
2. **Dead-end declaration shapes** (don't re-triage these): `answer(sorry)`
   anywhere (486 of 603 declarations!) — the declaration is a hole with no
   truth value, so it cannot be falsified by a finite object even when its
   right-hand side is a decidable `∀`. Same for `Set.Infinite` / `Set.Finite` /
   `Cardinal` conclusions, `Filter.atTop` / `∀ᶠ`, densities, `∃ c > 0, ∀ …`.
3. **The supplied `finite_signals` ranking is misleading.** It is a file-level
   lexical score. Erdős 470 ranks #2 only because of a big `decide` block in a
   *textbook* proof; 18, 36, 602, 509, 1049, 1063 likewise. Every open
   declaration in all of those is an `answer(sorry)` hole or asymptotic. Rank
   from the declaration text, not the file.
4. **Reusable extraction scripts** (scratchpad, may be wiped):
   `extract.py` (pulls every `@[category research open]` block + docstring from
   the upstream tree), `triage.py` (flag regexes), `write_triage.py` (renders
   the table). The upstream tree snapshot was made with
   `git -C /Users/kuber.mehta/Projects/formal-conjectures archive 2411d22e FormalConjectures/ErdosProblems | tar -x -C <dir>`
   (the `c5-k4/upstream/formal-conjectures` checkout is a stub containing only
   one WOWII file — do not use it).
5. **Committed verifier scripts** (in this directory, safe to reuse):
   * `verify_erdos931_exists_prime.py <limit>`
   * `verify_erdos10_erdos11.py {erdos10|erdos10_grechuk|erdos11} <limit>`
   * `verify_erdos677_lcm_interval.py <nmax> <kmax>`
   * `verify_erdos_misc.py {es242|q324|p364|d406|d779} <arg>`
6. **Useful semantics facts established** (don't re-derive):
   * `sumPrimeAndTwoPows k` membership ⟺ `∃ prime p ≤ n, popcount(n−p) ≤ k`
     (multiset of ≤k exponents ⟺ binary popcount ≤ k). Validated against the
     repo's own `research solved` fact `1117175146 ∉ sumPrimeAndTwoPows 3`.
   * `lcmInterval n k = (Finset.Ioc n (n+k)).lcm id = lcm{n+1,…,n+k}`
     (`FormalConjecturesForMathlib/Algebra/GCDMonoid/Finset.lean:27`).
   * `EuclideanGeometry.IsConvexPolygon` (`FormalConjecturesForMathlib/Geometry/2d.lean:153`)
     `= IsCcwConvexPolygon p ∨ IsCcwConvexPolygon (p ∘ Neg.neg)`, i.e. **strict**
     convexity (all oriented-angle signs = 1) — no three collinear vertices, so
     there is no degenerate-configuration hole in Erdős 982.
   * `Nat.Squarefree 0 = False`, `Squarefree 1 = True`.
7. **No upstream write of any kind was made.** No issue, PR, comment, or fork
   push. `gh` was used only for read queries.

## Residual candidate dispositions (deprioritised, with reasons)

| decl | disposition | reason |
|---|---|---|
| 409 `sigma_termination` | `CERTIFICATE_SHAPE_FAIL` | **triage correction:** `σ(n)−1 > n` strictly for every composite `n>1` and `= n` exactly at primes, so the orbit is strictly increasing until it halts — no cycle can exist, hence the negation "∃n ∀i ¬Prime" has no finite certificate. Reclassify as NOT_FINITELY_REFUTABLE. |
| 982 `erdos_982` | deprioritised | source status FALSIFIABLE and the proved lower bound is only `(13/36+1/22701)n`, so a counterexample is genuinely possible — but it needs an exact algebraic-coordinate convex polygon where **every** vertex has `< ⌊n/2⌋` distinct distances. Regular n-gon is exactly tight. Lean `n / 2` is ℕ-division = `⌊n/2⌋`, faithful. Real lane, out of this budget. |
| 274 `herzog_schonheim` | prior-art stop | Herzog–Schönheim; `ExactCovering` is a genuine coset partition with `1 < #ι`; enormous existing verification. Note `1 < ENat.card G` admits infinite `G`, where `Subgroup.index = 0` for infinite index, so any two infinite-index parts already satisfy the conclusion. |
| 617 `erdos_617` | prior-art stop | METHOD v1.0 already closed this lane: standalone public artifacts claim computer-assisted proofs for `r = 5..11`; refutation would need `r ≥ 12`, i.e. a 12-colouring of `K_145`. |
| 1113 `filaseta_finch_kozek` | `CERTIFICATE_SHAPE_FAIL` | refutation needs a Sierpiński number proved to have **no** finite covering set — not a finite artifact. |
| 1135 `erdos_1135` | prior-art stop | Collatz; verified past `2^68`. |
| 1055 `selfridge_limit` | `CERTIFICATE_SHAPE_FAIL` | `∃ M, ∀ r …` — global constant; refutation must rule out every `M`. (Regex missed it because the binder is `∃ M,` with no `:`/`>`; **fix the GLOBAL_CONST regex** if re-running triage.) |
| 535 `sunflower_strong` | `CERTIFICATE_SHAPE_FAIL` | `∃ c_r > 0, ∀ k, ∀ A …` — same; regex missed it because of the underscore in `c_r`. |
| 477 `X_pow_three`, `monomial` | `CERTIFICATE_SHAPE_FAIL` | `∀ A : Set ℤ, ∃ z, …` — refutation needs a specific **infinite** set `A`. |
| 952, 1041 | `CONSTRUCTION_ONLY` | purely existential; a bounded search can prove but never disprove. |
| 1044 `fixed_degree`, 349, 241, 189 | `CERTIFICATE_SHAPE_FAIL` / real-analytic | `IsLeast` over ℂ[X]/ℝ objects, `IsGoodPair` over ℝ², Bose–Chowla asymptotics, and a `¬ Erdos189For` whose negation is a full ∀-statement over ℝ² colourings. |

## Two flagged formalization defects (neither is a counterexample)

1. **Erdős 1084 `triangular_optimal_d2`** — see D8. Docstring says
   `f_2(3n²+3n+1) < 9n²+3n`; the source says Erdős speculated `= 9n²+3n`; and
   the source records **Harborth [Ha74b] proved it**, with the general formula
   `f_2(n) = ⌊3n − √(12n−3)⌋`. So (a) the docstring's `<` is a transcription
   error and is *provably false* (the triangular lattice attains `9n²+3n`), and
   (b) the declaration is labelled `@[category research open]` although the
   canonical source records it as proved. `STATUS_SYNC` / metadata defect.
2. **Erdős 931 `exists_prime`** — prose says "a prime **between** `n₁` and
   `n₂`", Lean says `n₁ ≤ p ∧ p ≤ n₂` (closed). A weakening, so conservative;
   it makes the conclusion trivial whenever `n₁ ≤ 2`, which is how the repo's
   own AlphaProof witness `(k₁,k₂,n₁,n₂) = (10,3,0,13)` discharges it.


**Corpus:** `google-deepmind/formal-conjectures` at upstream commit
`2411d22e1bd550d050d0eac6c1fb379a76a3e7c5` (2026-08-14 19:16:38 +0000,
"Disprove WOWII 59 (#4574)"), tree `FormalConjectures/ErdosProblems/`.

**Target list:** `results/expansion/open_targets_oeis_erdos_20260815.json`,
entries with `corpus == "ErdosProblems"` and `previously_touched == false`
(364 files). Those files carry **603** `@[category research open]`
declarations; the declaration, not the file, is the unit of triage.

**Governing protocol:** `METHOD.md` Phase 0A (certificate-shape gate) and the
60-second hard wall-clock cap on every computation. Exact arithmetic only
(`/home/ec2-user/.venvs/wowii/bin/python`, integer/`fractions.Fraction`).

**Publication:** none. No upstream issue, PR, or comment was opened. Local
records only.

## Triage rule actually applied

A declaration is `CANDIDATE_FOR_DEPTH` only if its **literal negation is one
finite, replayable object**. Everything else is `NOT_FINITELY_REFUTABLE`, i.e.
a strict stop under METHOD G0 / Phase 0A. The disqualifying shapes, in
precedence order:

1. `answer(sorry)` anywhere in the statement — the declaration is a hole with
   no truth value, so no finite object can falsify it (`answer_placeholder`).
2. asymptotic / eventual quantifier: `Filter.atTop`, `∀ᶠ`, `∃ᶠ`, `Tendsto`,
   big-O / little-o, `limsup`, `liminf`.
3. infinitary conclusion: `Set.Infinite`, `Set.Finite`, `Cardinal`, `ℵ₀`.
4. density statements.
5. analytic objects: `∑'`, integrals, derivatives.
6. existentially quantified global constant (`∃ c > 0, ∀ …`).
7. `∀ ε > 0` statements.

## Triage counts

| bucket | declarations | files |
|---|---|---|
| total open declarations scanned | 603 | 364 |
| `NOT_FINITELY_REFUTABLE` | 575 | — |
| `CANDIDATE_FOR_DEPTH` | 28 | 25 |

Breakdown of disqualifying flags (a declaration may carry several):
`answer(sorry)` 486, asymptotic 282, infinitary 113, global-constant 71,
density 41, ∀ε 20, analytic 14.

**Note on the supplied `finite_signals` ranking.** It is a lexical score over
the whole file and is not reliable at declaration level. Erdős 470 ranks #2
(42) only because its *textbook* `smallest_weird_eq_70` proof is a large
`decide` block; both of its open declarations are `answer(sorry)` holes.
Erdős 18, 36, 602, 509, 1049, 1063 likewise rank high on file-level lexical
signal while every open declaration in them is an `answer(sorry)` hole or an
asymptotic/density statement. The candidate set below was therefore rebuilt
from the declaration texts.

| Erdős # | declaration | verdict | reason |
|---|---|---|---|
| 1 | `erdos_1` | NOT_FINITELY_REFUTABLE | existentially quantified global constant: negation must rule out every constant |
| 1 | `erdos_1.variants.real` | NOT_FINITELY_REFUTABLE | existentially quantified global constant: negation must rule out every constant |
| 3 | `erdos_3` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC,ANALYTIC] |
| 5 | `erdos_5` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 5 | `erdos_5.variants.dense` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 5 | `erdos_5.variants.limit_point_set` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 7 | `erdos_7` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+GLOBAL_CONST] |
| 9 | `erdos_9` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+DENSITY] |
| 10 | `erdos_10` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 10 | `erdos_10.variants.granville_soundararajan_odd` | CANDIDATE_FOR_DEPTH | literal statement is a universal/decidable-body claim whose negation is one finite object |
| 10 | `erdos_10.variants.grechuk` | NOT_FINITELY_REFUTABLE | infinite-cardinality conclusion (Set.Infinite / Set.Finite / Cardinal): negation is a global nonexistence or infinitude proof |
| 11 | `erdos_11` | CANDIDATE_FOR_DEPTH | literal statement is a universal/decidable-body claim whose negation is one finite object |
| 11 | `erdos_11.variants.not_four_dvd` | CANDIDATE_FOR_DEPTH | literal statement is a universal/decidable-body claim whose negation is one finite object |
| 11 | `erdos_11.variants.two_pow_two` | CANDIDATE_FOR_DEPTH | literal statement is a universal/decidable-body claim whose negation is one finite object |
| 12 | `erdos_12.parts.iii` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ANALYTIC] |
| 13 | `erdos_13.variants.general` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+GLOBAL_CONST] |
| 14 | `erdos_14.parts.i` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+EPSILON] |
| 14 | `erdos_14.parts.ii` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 15 | `erdos_15` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ANALYTIC] |
| 17 | `erdos_17` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 18 | `erdos_18a` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC,GLOBAL_CONST] |
| 18 | `erdos_18b` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC,EPSILON] |
| 18 | `erdos_18c` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC,GLOBAL_CONST] |
| 20 | `erdos_20` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+GLOBAL_CONST] |
| 25 | `erdos_25` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+DENSITY] |
| 28 | `erdos_28` | NOT_FINITELY_REFUTABLE | asymptotic/eventual quantifier (atTop / ∀ᶠ / Tendsto / big-O / limsup): negation needs an infinite family + rate [+INFINITARY] |
| 30 | `erdos_30` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 32 | `erdos_32` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 32 | `erdos_32.variants.log_bound` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 33 | `erdos_33` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 36 | `erdos_36` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 36 | `erdos_36.variants.lower` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC,GLOBAL_CONST] |
| 36 | `erdos_36.variants.upper` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC,GLOBAL_CONST] |
| 39 | `erdos_39` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC,INFINITARY] |
| 40 | `erdos_40` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 41 | `erdos_41` | NOT_FINITELY_REFUTABLE | asymptotic/eventual quantifier (atTop / ∀ᶠ / Tendsto / big-O / limsup): negation needs an infinite family + rate [+INFINITARY] |
| 44 | `erdos_44` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 44 | `erdos_44.variants.empty_start` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 50 | `erdos_50` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 51 | `erdos_51` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC,INFINITARY] |
| 52 | `erdos_52` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+GLOBAL_CONST] |
| 60 | `erdos_60` | NOT_FINITELY_REFUTABLE | asymptotic/eventual quantifier (atTop / ∀ᶠ / Tendsto / big-O / limsup): negation needs an infinite family + rate [+GLOBAL_CONST] |
| 61 | `erdos_61` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+GLOBAL_CONST] |
| 66 | `erdos_66` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 68 | `erdos_68` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ANALYTIC] |
| 70 | `erdos_70` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 70 | `omega_one` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 70 | `omega_times_two_four` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 74 | `erdos_74` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 74 | `erdos_74.variants.sqrt` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 75 | `erdos_75` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC,INFINITARY,EPSILON] |
| 80 | `erdos_80` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC,GLOBAL_CONST] |
| 80 | `erdos_80.variants.log` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 82 | `erdos_82` | NOT_FINITELY_REFUTABLE | asymptotic/eventual quantifier (atTop / ∀ᶠ / Tendsto / big-O / limsup): negation needs an infinite family + rate |
| 85 | `erdos_85` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 89 | `erdos_89` | NOT_FINITELY_REFUTABLE | asymptotic/eventual quantifier (atTop / ∀ᶠ / Tendsto / big-O / limsup): negation needs an infinite family + rate |
| 91 | `erdos_91` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 94 | `erdos_94.variants.regular_ngon` | NOT_FINITELY_REFUTABLE | asymptotic/eventual quantifier (atTop / ∀ᶠ / Tendsto / big-O / limsup): negation needs an infinite family + rate |
| 96 | `erdos_96` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 97 | `erdos_97` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 97 | `erdos_97.variants.k_equidistant` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 98 | `erdos_98` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 99 | `erdos_99` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 100 | `erdos_100` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC,GLOBAL_CONST] |
| 100 | `erdos_100.variants.strong` | NOT_FINITELY_REFUTABLE | asymptotic/eventual quantifier (atTop / ∀ᶠ / Tendsto / big-O / limsup): negation needs an infinite family + rate |
| 101 | `erdos_101` | NOT_FINITELY_REFUTABLE | asymptotic/eventual quantifier (atTop / ∀ᶠ / Tendsto / big-O / limsup): negation needs an infinite family + rate |
| 105 | `erdos_105.variants.sub_four` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 107 | `erdos_107` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 108 | `erdos_108` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 120 | `erdos_120` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 123 | `erdos_123.variants.powers_2_3_5_snug` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC,EPSILON] |
| 124 | `erdos124.ne_zero` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 125 | `erdos_125.variants.positive_upper_density` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+DENSITY] |
| 125 | `erdos_125.variants.zero_density` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+DENSITY] |
| 125 | `erdos_125.variants.zero_lower_positive_upper_density` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+DENSITY] |
| 126 | `erdos_126` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 126 | `erdos_126.variants.isLittleO` | NOT_FINITELY_REFUTABLE | asymptotic/eventual quantifier (atTop / ∀ᶠ / Tendsto / big-O / limsup): negation needs an infinite family + rate |
| 137 | `erdos_137` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 137 | `erdos_137.variants.multiple_powerful_factors` | NOT_FINITELY_REFUTABLE | asymptotic/eventual quantifier (atTop / ∀ᶠ / Tendsto / big-O / limsup): negation needs an infinite family + rate |
| 138 | `erdos_138` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 138 | `erdos_138.variants.dvd_two_pow` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 138 | `erdos_138.variants.quotient` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 141 | `erdos_141` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 141 | `erdos_141.variants.eleven` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 141 | `erdos_141.variants.infinite_general_case` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 141 | `erdos_141.variants.infinite_three` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 142 | `erdos_142` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 142 | `erdos_142.variants.lower` | NOT_FINITELY_REFUTABLE | asymptotic/eventual quantifier (atTop / ∀ᶠ / Tendsto / big-O / limsup): negation needs an infinite family + rate |
| 142 | `erdos_142.variants.three` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 142 | `erdos_142.variants.upper` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 143 | `erdos_143.parts.i` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 143 | `erdos_143.parts.ii` | NOT_FINITELY_REFUTABLE | analytic object (tsum / integral / derivative): no finite replayable certificate |
| 145 | `erdos_145` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 153 | `erdos_153` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 155 | `erdos_155` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 156 | `erdos_156` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 158 | `erdos_158` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC,INFINITARY] |
| 160 | `erdos_160.better_lower` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 160 | `erdos_160.better_upper` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 168 | `erdos_168.parts.i` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 168 | `erdos_168.parts.ii` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 170 | `erdos170` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 172 | `erdos_172` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 188 | `erdos_188` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 189 | `erdos_189.variants.parallelogram` | CANDIDATE_FOR_DEPTH | literal statement is a universal/decidable-body claim whose negation is one finite object |
| 193 | `erdos_193` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 195 | `erdos_195` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 196 | `erdos_196` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 197 | `erdos_197` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 200 | `erdos_200` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 203 | `erdos_203` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 205 | `erdos_205.variants.odd_counterexamples` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 208 | `erdos_208.parts.i` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC,EPSILON] |
| 208 | `erdos_208.parts.ii` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC,GLOBAL_CONST] |
| 208 | `erdos_208.variants.log_bound` | NOT_FINITELY_REFUTABLE | asymptotic/eventual quantifier (atTop / ∀ᶠ / Tendsto / big-O / limsup): negation needs an infinite family + rate |
| 212 | `erdos_212` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 213 | `erdos_213` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 218 | `erdos_218.variants.ge` | NOT_FINITELY_REFUTABLE | density statement: negation needs an asymptotic rate, not a finite artifact |
| 218 | `erdos_218.variants.infinite_equal_prime_gap` | NOT_FINITELY_REFUTABLE | infinite-cardinality conclusion (Set.Infinite / Set.Finite / Cardinal): negation is a global nonexistence or infinitude proof |
| 218 | `erdos_218.variants.le` | NOT_FINITELY_REFUTABLE | density statement: negation needs an asymptotic rate, not a finite artifact |
| 233 | `erdos_233` | NOT_FINITELY_REFUTABLE | asymptotic/eventual quantifier (atTop / ∀ᶠ / Tendsto / big-O / limsup): negation needs an infinite family + rate |
| 234 | `erdos_234` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+DENSITY] |
| 236 | `erdos_236` | NOT_FINITELY_REFUTABLE | asymptotic/eventual quantifier (atTop / ∀ᶠ / Tendsto / big-O / limsup): negation needs an infinite family + rate |
| 238 | `erdos_238` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 241 | `erdos_241` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 241 | `erdos_241.variants.generalization` | CANDIDATE_FOR_DEPTH | literal statement is a universal/decidable-body claim whose negation is one finite object |
| 242 | `erdos_242` | CANDIDATE_FOR_DEPTH | literal statement is a universal/decidable-body claim whose negation is one finite object |
| 242 | `erdos_242.variants.schinzel_generalization` | NOT_FINITELY_REFUTABLE | asymptotic/eventual quantifier (atTop / ∀ᶠ / Tendsto / big-O / limsup): negation needs an infinite family + rate |
| 243 | `erdos_243` | NOT_FINITELY_REFUTABLE | asymptotic/eventual quantifier (atTop / ∀ᶠ / Tendsto / big-O / limsup): negation needs an infinite family + rate [+ANALYTIC] |
| 244 | `erdos_244` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+DENSITY] |
| 247 | `erdos_247` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC,ANALYTIC] |
| 249 | `erdos_249` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ANALYTIC] |
| 251 | `erdos_251` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ANALYTIC] |
| 252 | `erdos_252` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 252 | `erdos_252.variants.k_ge_five` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 257 | `erdos_257` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY,ANALYTIC] |
| 260 | `erdos_260` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 263 | `erdos_263.parts.i` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 263 | `erdos_263.parts.ii` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 264 | `erdos_264.parts.ii` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 267 | `erdos_267.variants.generalisation_ratio_limit_to_infinity` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC,ANALYTIC] |
| 269 | `erdos_269.variants.irrational` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 269 | `erdos_269.variants.rational` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 272 | `erdos_272` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 272 | `erdos_272.variants.szabo_strong` | NOT_FINITELY_REFUTABLE | asymptotic/eventual quantifier (atTop / ∀ᶠ / Tendsto / big-O / limsup): negation needs an infinite family + rate |
| 273 | `erdos_273` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+GLOBAL_CONST] |
| 274 | `erdos_274` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 274 | `herzog_schonheim` | CANDIDATE_FOR_DEPTH | literal statement is a universal/decidable-body claim whose negation is one finite object |
| 276 | `erdos_276` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 279 | `erdos_279` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+GLOBAL_CONST] |
| 282 | `erdos_282` | NOT_FINITELY_REFUTABLE | asymptotic/eventual quantifier (atTop / ∀ᶠ / Tendsto / big-O / limsup): negation needs an infinite family + rate |
| 282 | `erdos_282.variants.general` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 282 | `erdos_282.variants.graham` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 282 | `erdos_282.variants.sq` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 287 | `erdos_287` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 287 | `erdos_287.variants.prime_conjecture` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+GLOBAL_CONST] |
| 288 | `erdos_288` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 288 | `erdos_288.variants.exists_k_gt_2` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 288 | `erdos_288.variants.i2_card_eq_1` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 288 | `erdos_288.variants.k_intervals` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 289 | `erdos_289` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 291 | `erdos_291.parts.i` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 291 | `erdos_291.variants.shiu_heuristic_asymptotic` | NOT_FINITELY_REFUTABLE | asymptotic/eventual quantifier (atTop / ∀ᶠ / Tendsto / big-O / limsup): negation needs an infinite family + rate |
| 291 | `erdos_291.variants.shiu_heuristic_density_zero` | NOT_FINITELY_REFUTABLE | asymptotic/eventual quantifier (atTop / ∀ᶠ / Tendsto / big-O / limsup): negation needs an infinite family + rate [+DENSITY] |
| 295 | `erdos_295` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 302 | `erdos_302.parts.i` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 304 | `upper_bound` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 306 | `erdos_306` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 307 | `erdos_307` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 307 | `erdos_307.variants.coprime_one_notMem` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 312 | `erdos_312` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+GLOBAL_CONST] |
| 313 | `erdos_313` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 313 | `erdos_313.variants.primary_pseudoperfect_are_infinite` | NOT_FINITELY_REFUTABLE | infinite-cardinality conclusion (Set.Infinite / Set.Finite / Cardinal): negation is a global nonexistence or infinitude proof |
| 317 | `erdos_317` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+GLOBAL_CONST] |
| 317 | `erdos_317.variants.claim2` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 319 | `erdos_319` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+GLOBAL_CONST] |
| 319 | `erdos_319.variants.isBigO` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC,GLOBAL_CONST] |
| 319 | `erdos_319.variants.isLittleO` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC,GLOBAL_CONST] |
| 319 | `erdos_319.variants.isTheta` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC,GLOBAL_CONST] |
| 321 | `erdos_321` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 321 | `erdos_321.variants.isBigO` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 321 | `erdos_321.variants.isLittleO` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 321 | `erdos_321.variants.isTheta` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 323 | `erdos_323.parts.i` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC,EPSILON] |
| 323 | `erdos_323.parts.ii` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 323 | `erdos_323.variants.k_gt_2` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 324 | `erdos_324` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 324 | `erdos_324.variants.quintic` | CANDIDATE_FOR_DEPTH | literal statement is a universal/decidable-body claim whose negation is one finite object |
| 325 | `erdos_325` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 325 | `erdos_325.variants.weaker` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC,EPSILON] |
| 326 | `erdos_326` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 329 | `erdos_329` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+DENSITY] |
| 329 | `erdos_329.variants.converse_implication` | NOT_FINITELY_REFUTABLE | density statement: negation needs an asymptotic rate, not a finite artifact |
| 331 | `erdos_331.variants.ruzsa` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC,INFINITARY] |
| 332 | `erdos_332` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 337 | `erdos_337.variants.ruzsa_turjanyi` | NOT_FINITELY_REFUTABLE | asymptotic/eventual quantifier (atTop / ∀ᶠ / Tendsto / big-O / limsup): negation needs an infinite family + rate |
| 340 | `erdos_340` | NOT_FINITELY_REFUTABLE | asymptotic/eventual quantifier (atTop / ∀ᶠ / Tendsto / big-O / limsup): negation needs an infinite family + rate |
| 340 | `erdos_340.variants._33_mem_sub` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 340 | `erdos_340.variants.co_density_zero_sub` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+DENSITY] |
| 340 | `erdos_340.variants.cofinite_sub` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 340 | `erdos_340.variants.isTheta` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 340 | `erdos_340.variants.sub_hasPosDensity` | NOT_FINITELY_REFUTABLE | density statement: negation needs an asymptotic rate, not a finite artifact |
| 341 | `erdos_341` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 342 | `erdos_342.parts.i` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 342 | `erdos_342.parts.ii` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 342 | `erdos_342.parts.iii` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+DENSITY] |
| 346 | `erdos_346` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC,INFINITARY] |
| 348 | `erdos_348` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 349 | `complete_for_alpha_in_Ioo_one_to_goldenRatio` | CANDIDATE_FOR_DEPTH | literal statement is a universal/decidable-body claim whose negation is one finite object |
| 349 | `erdos_349` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 349 | `erdos_349.variants.floor_3_halves_even` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 349 | `erdos_349.variants.floor_3_halves_odd` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 352 | `erdos_352` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+GLOBAL_CONST] |
| 354 | `erdos_354.parts.i` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 354 | `erdos_354.parts.ii` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 357 | `erdos_357.parts.i` | NOT_FINITELY_REFUTABLE | asymptotic/eventual quantifier (atTop / ∀ᶠ / Tendsto / big-O / limsup): negation needs an infinite family + rate |
| 357 | `erdos_357.parts.ii.bigO_version` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 357 | `erdos_357.parts.ii.bigO_version_symm` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 357 | `erdos_357.parts.ii.bigTheta_version` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 357 | `erdos_357.parts.ii.littleO_version` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 357 | `erdos_357.parts.ii.littleO_version_symm` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 357 | `erdos_357.variants.hegyvari` | NOT_FINITELY_REFUTABLE | asymptotic/eventual quantifier (atTop / ∀ᶠ / Tendsto / big-O / limsup): negation needs an infinite family + rate |
| 357 | `erdos_357.variants.infinite_set_density` | NOT_FINITELY_REFUTABLE | density statement: negation needs an asymptotic rate, not a finite artifact |
| 357 | `erdos_357.variants.infinite_set_sum` | NOT_FINITELY_REFUTABLE | analytic object (tsum / integral / derivative): no finite replayable certificate |
| 357 | `erdos_357.variants.monotone.parts.i` | NOT_FINITELY_REFUTABLE | asymptotic/eventual quantifier (atTop / ∀ᶠ / Tendsto / big-O / limsup): negation needs an infinite family + rate |
| 357 | `erdos_357.variants.monotone.parts.ii.bigO_version` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 357 | `erdos_357.variants.monotone.parts.ii.bigO_version_symm` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 357 | `erdos_357.variants.monotone.parts.ii.bigTheta_version` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 357 | `erdos_357.variants.monotone.parts.ii.littleO_version` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 357 | `erdos_357.variants.monotone.parts.ii.littleO_version_symm` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 358 | `erdos_358.variants.one_le` | NOT_FINITELY_REFUTABLE | asymptotic/eventual quantifier (atTop / ∀ᶠ / Tendsto / big-O / limsup): negation needs an infinite family + rate |
| 358 | `erdos_358.variants.prime_set` | NOT_FINITELY_REFUTABLE | asymptotic/eventual quantifier (atTop / ∀ᶠ / Tendsto / big-O / limsup): negation needs an infinite family + rate |
| 358 | `erdos_358.variants.prime_set_density_representation` | NOT_FINITELY_REFUTABLE | density statement: negation needs an asymptotic rate, not a finite artifact |
| 359 | `erdos_359.parts.i` | NOT_FINITELY_REFUTABLE | asymptotic/eventual quantifier (atTop / ∀ᶠ / Tendsto / big-O / limsup): negation needs an infinite family + rate |
| 359 | `erdos_359.parts.ii` | NOT_FINITELY_REFUTABLE | asymptotic/eventual quantifier (atTop / ∀ᶠ / Tendsto / big-O / limsup): negation needs an infinite family + rate |
| 359 | `erdos_359.variants.isGoodFor_1_asymptotic` | NOT_FINITELY_REFUTABLE | asymptotic/eventual quantifier (atTop / ∀ᶠ / Tendsto / big-O / limsup): negation needs an infinite family + rate |
| 361 | `erdos_361` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 361 | `erdos_361.asymptotic` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 364 | `erdos_364` | CANDIDATE_FOR_DEPTH | literal statement is a universal/decidable-body claim whose negation is one finite object |
| 364 | `erdos_364.variants.strong` | NOT_FINITELY_REFUTABLE | existentially quantified global constant: negation must rule out every constant |
| 366 | `erdos_366` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 366 | `erdos_366.variants.three_two` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 366 | `erdos_366.variants.weaker` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 371 | `erdos_371` | NOT_FINITELY_REFUTABLE | density statement: negation needs an asymptotic rate, not a finite artifact |
| 376 | `erdos_376` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 377 | `erdos_377` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+GLOBAL_CONST] |
| 383 | `erdos_383` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 385 | `erdos_385.parts.i` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 385 | `erdos_385.parts.ii` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 385 | `erdos_385.variants.lb` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 386 | `erdos_386` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 386 | `erdos_386.variants.forall` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 386 | `erdos_386.variants.two` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 387 | `erdos_387.variants.schinzel` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 389 | `erdos_389` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 390 | `erdos_390` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 394 | `erdos_394.variants.factorial_gap_conjecture` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 394 | `erdos_394.variants.hall_conjecture` | NOT_FINITELY_REFUTABLE | asymptotic/eventual quantifier (atTop / ∀ᶠ / Tendsto / big-O / limsup): negation needs an infinite family + rate |
| 396 | `erdos_396` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 398 | `erdos_398` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 400 | `erdos_400.parts.i` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC,GLOBAL_CONST] |
| 400 | `erdos_400.parts.ii` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC,GLOBAL_CONST,EPSILON] |
| 406 | `erdos_406` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 406 | `erdos_406.variants.one_two` | CANDIDATE_FOR_DEPTH | literal statement is a universal/decidable-body claim whose negation is one finite object |
| 409 | `erdos_409.parts.i` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 409 | `erdos_409.parts.i.isBigO` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 409 | `erdos_409.parts.i.isLittleO` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 409 | `erdos_409.parts.i.isTheta` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 409 | `erdos_409.parts.ii` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 409 | `erdos_409.parts.iii` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+DENSITY] |
| 409 | `erdos_409.variants.sigma` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 409 | `erdos_409.variants.sigma_isBigO` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 409 | `erdos_409.variants.sigma_isLittleO` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 409 | `erdos_409.variants.sigma_isTheta` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 409 | `erdos_409.variants.sigma_prime_termination` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 409 | `erdos_409.variants.sigma_termination` | CANDIDATE_FOR_DEPTH | literal statement is a universal/decidable-body claim whose negation is one finite object |
| 410 | `erdos_410` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 412 | `erdos_412` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 413 | `erdos_413.parts.i` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 413 | `erdos_413.parts.ii` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY,GLOBAL_CONST] |
| 413 | `erdos_413.variants.bigOmega` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 414 | `erdos_414` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 416 | `erdos_416.parts.i` | NOT_FINITELY_REFUTABLE | asymptotic/eventual quantifier (atTop / ∀ᶠ / Tendsto / big-O / limsup): negation needs an infinite family + rate |
| 416 | `erdos_416.parts.ii` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 417 | `erdos_417.parts.i` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 417 | `erdos_417.parts.ii` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 418 | `erdos_418.variants.density` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+DENSITY] |
| 421 | `erdos_421` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+DENSITY] |
| 422 | `erdos_422` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 422 | `erdos_422.variants.eventually_const` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 422 | `erdos_422.variants.growth_rate` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 422 | `erdos_422.variants.surjective` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 424 | `erdos_424` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+DENSITY] |
| 428 | `erdos_428` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC,DENSITY] |
| 445 | `erdos_445` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 450 | `erdos_450` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC,EPSILON] |
| 454 | `erdos_454` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 455 | `erdos_455` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 456 | `erdos_456.parts.i` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 456 | `erdos_456.parts.ii` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 456 | `erdos_456.parts.iii` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 457 | `erdos_457.variants.one_sub` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC,GLOBAL_CONST] |
| 457 | `erdos_457.variants.qnk` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY,GLOBAL_CONST] |
| 458 | `erdos_458` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 463 | `erdos_463` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 470 | `erdos_470.parts.i` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 470 | `erdos_470.parts.ii` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 477 | `erdos_477` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 477 | `erdos_477.variants.X_pow_three` | CANDIDATE_FOR_DEPTH | literal statement is a universal/decidable-body claim whose negation is one finite object |
| 477 | `erdos_477.variants.monomial` | CANDIDATE_FOR_DEPTH | literal statement is a universal/decidable-body claim whose negation is one finite object |
| 479 | `erdos_479` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 486 | `erdos_486` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+DENSITY] |
| 488 | `erdos_488` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 495 | `erdos_495` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 501 | `erdos_501` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 503 | `erdos_503` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 506 | `erdos_506` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 506 | `erdos_506.variants.small_n` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 507 | `erdos_507.equivalent` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 507 | `erdos_507.lower` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 507 | `erdos_507.upper` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 508 | `HadwigerNelsonProblem` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 509 | `erdos_509` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 510 | `erdos_510` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC,GLOBAL_CONST] |
| 513 | `erdos_513` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 516 | `erdos_516.variants.limsup_ratio_eq_one_of_hasFejerGaps` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 517 | `erdos_517` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 520 | `erdos_520` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC,GLOBAL_CONST] |
| 522 | `erdos_522` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 522 | `erdos_522.variants.zero_one` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 535 | `erdos_535` | NOT_FINITELY_REFUTABLE | asymptotic/eventual quantifier (atTop / ∀ᶠ / Tendsto / big-O / limsup): negation needs an infinite family + rate [+GLOBAL_CONST] |
| 535 | `erdos_535.variants.first_open_case` | NOT_FINITELY_REFUTABLE | asymptotic/eventual quantifier (atTop / ∀ᶠ / Tendsto / big-O / limsup): negation needs an infinite family + rate [+GLOBAL_CONST] |
| 535 | `erdos_535.variants.sunflower_strong` | CANDIDATE_FOR_DEPTH | literal statement is a universal/decidable-body claim whose negation is one finite object |
| 536 | `erdos_536` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 538 | `erdos_538` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC,GLOBAL_CONST] |
| 539 | `erdos_539` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 539 | `erdos_539.variants.isBigO_sq` | NOT_FINITELY_REFUTABLE | asymptotic/eventual quantifier (atTop / ∀ᶠ / Tendsto / big-O / limsup): negation needs an infinite family + rate |
| 539 | `erdos_539.variants.sq` | NOT_FINITELY_REFUTABLE | asymptotic/eventual quantifier (atTop / ∀ᶠ / Tendsto / big-O / limsup): negation needs an infinite family + rate |
| 562 | `erdos_562` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 564 | `erdos_564` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC,GLOBAL_CONST] |
| 566 | `erdos_566` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+GLOBAL_CONST] |
| 567 | `erdos_567.parts.i` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 567 | `erdos_567.parts.ii` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 567 | `erdos_567.parts.iii` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 579 | `erdos_579` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC,GLOBAL_CONST] |
| 592 | `erdos_592` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 593 | `erdos_593` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 593 | `erdos_593.variants.obligatory_implies_two_colorable` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 593 | `erdos_593.variants.two_colorable_implies_obligatory` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 595 | `erdos_595` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 596 | `erdos_596` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 596 | `erdos_596.variants.K4_K3_exceptional_iff` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 598 | `erdos_598` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+GLOBAL_CONST] |
| 600 | `erdos_600.parts.i` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 600 | `erdos_600.parts.ii` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 602 | `erdos_602` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 617 | `erdos_617` | CANDIDATE_FOR_DEPTH | literal statement is a universal/decidable-body claim whose negation is one finite object |
| 623 | `erdos_623` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 624 | `erdos_624` | NOT_FINITELY_REFUTABLE | asymptotic/eventual quantifier (atTop / ∀ᶠ / Tendsto / big-O / limsup): negation needs an infinite family + rate |
| 633 | `erdos_633` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 647 | `erdos_647` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 647 | `erdos_647.variants.infinite` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 647 | `erdos_647.variants.lim` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 649 | `erdos_649.variants.tong_question` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 653 | `erdos_653` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 655 | `erdos_655.variants.general_position` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC,GLOBAL_CONST] |
| 660 | `erdos_660` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC,EPSILON] |
| 660 | `erdos_660.variants.Er75f` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC,GLOBAL_CONST] |
| 672 | `erdos_672` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 677 | `erdos_677` | CANDIDATE_FOR_DEPTH | literal statement is a universal/decidable-body claim whose negation is one finite object |
| 680 | `erdos_680.parts.i` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 680 | `erdos_680.parts.ii` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC,GLOBAL_CONST,EPSILON] |
| 681 | `erdos_681` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 683 | `erdos_683` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+GLOBAL_CONST] |
| 683 | `erdos_683.variant.exp_sqrt` | NOT_FINITELY_REFUTABLE | existentially quantified global constant: negation must rule out every constant |
| 686 | `erdos_686` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 686 | `erdos_686.variants.four` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 686 | `erdos_686.variants.square` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 686 | `erdos_686.variants.twenty_five` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 688 | `erdos_688.parts.i.lower_bound` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 688 | `erdos_688.parts.i.upper_bound` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 688 | `erdos_688.parts.ii` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 689 | `erdos_689` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 692 | `erdos_692.parts.ii` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 694 | `erdos_694.variants.carmichael` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 695 | `erdos_695` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 695 | `erdos_695.variants.upperBound` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 699 | `erdos_699` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 699 | `erdos_szekeres_strengthening` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 700 | `erdos_700.parts.i` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 700 | `erdos_700.parts.ii` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 700 | `erdos_700.parts.iii` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+GLOBAL_CONST] |
| 701 | `erdos_701` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 723 | `erdos_723` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 723 | `erdos_723.variants.eq_12` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 726 | `erdos_726` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 727 | `erdos_727` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 727 | `erdos_727.variants.k_2` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 730 | `erdos_730` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 740 | `erdos_740` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 741 | `erdos_741.variants.lower` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+DENSITY] |
| 749 | `erdos_749` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+DENSITY,EPSILON] |
| 757 | `erdos_757` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 769 | `erdos_769.variants.growth_rate` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC,GLOBAL_CONST] |
| 770 | `erdos_770.parts.i` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+DENSITY] |
| 770 | `erdos_770.parts.ii` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 770 | `erdos_770.parts.iii` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC,EPSILON] |
| 770 | `erdos_770.variants.three` | NOT_FINITELY_REFUTABLE | infinite-cardinality conclusion (Set.Infinite / Set.Finite / Cardinal): negation is a global nonexistence or infinitude proof |
| 774 | `erdos_774` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 779 | `erdos_779` | CANDIDATE_FOR_DEPTH | literal statement is a universal/decidable-body claim whose negation is one finite object |
| 785 | `erdos_785.variants.chen_conjecture` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC,INFINITARY] |
| 786 | `erdos_786.parts.i` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+DENSITY,EPSILON] |
| 786 | `erdos_786.parts.ii` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 789 | `erdos_789` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 789 | `erdos_789.variants.cube_root_linearithmic` | NOT_FINITELY_REFUTABLE | asymptotic/eventual quantifier (atTop / ∀ᶠ / Tendsto / big-O / limsup): negation needs an infinite family + rate |
| 789 | `erdos_789.variants.isBigO_cube_root_linearithmic` | NOT_FINITELY_REFUTABLE | asymptotic/eventual quantifier (atTop / ∀ᶠ / Tendsto / big-O / limsup): negation needs an infinite family + rate |
| 789 | `erdos_789.variants.sq` | NOT_FINITELY_REFUTABLE | asymptotic/eventual quantifier (atTop / ∀ᶠ / Tendsto / big-O / limsup): negation needs an infinite family + rate |
| 789 | `erdos_789.variants.sq_isBigO` | NOT_FINITELY_REFUTABLE | asymptotic/eventual quantifier (atTop / ∀ᶠ / Tendsto / big-O / limsup): negation needs an infinite family + rate |
| 812 | `erdos_812.parts.i` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC,GLOBAL_CONST] |
| 812 | `erdos_812.parts.ii` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 817 | `erdos_817` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 821 | `erdos_821` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY,EPSILON] |
| 826 | `erdos_826` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY,GLOBAL_CONST] |
| 828 | `erdos_828` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 828 | `erdos_828.variants.lehmer_conjecture` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 829 | `erdos_829` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC,GLOBAL_CONST] |
| 830 | `erdos_830.parts.i` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 830 | `erdos_830.parts.ii` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 849 | `erdos_849` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 850 | `erdos_850` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 853 | `erdos_853.parts.i` | NOT_FINITELY_REFUTABLE | asymptotic/eventual quantifier (atTop / ∀ᶠ / Tendsto / big-O / limsup): negation needs an infinite family + rate |
| 853 | `erdos_853.parts.ii` | NOT_FINITELY_REFUTABLE | asymptotic/eventual quantifier (atTop / ∀ᶠ / Tendsto / big-O / limsup): negation needs an infinite family + rate |
| 855 | `erdos_855` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 857 | `erdos_857` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 859 | `erdos_859` | NOT_FINITELY_REFUTABLE | asymptotic/eventual quantifier (atTop / ∀ᶠ / Tendsto / big-O / limsup): negation needs an infinite family + rate [+DENSITY,GLOBAL_CONST] |
| 865 | `erdos_865.variants.sos` | NOT_FINITELY_REFUTABLE | asymptotic/eventual quantifier (atTop / ∀ᶠ / Tendsto / big-O / limsup): negation needs an infinite family + rate |
| 872 | `erdos_872.parts.i` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC,GLOBAL_CONST] |
| 872 | `erdos_872.parts.ii` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC,EPSILON] |
| 872 | `erdos_872.variants.prime_question` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 873 | `erdos_873` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 881 | `erdos_881` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 885 | `erdos_885` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 886 | `erdos_886` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC,GLOBAL_CONST,EPSILON] |
| 887 | `erdos_887.parts.i` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 887 | `erdos_887.parts.ii` | NOT_FINITELY_REFUTABLE | asymptotic/eventual quantifier (atTop / ∀ᶠ / Tendsto / big-O / limsup): negation needs an infinite family + rate |
| 887 | `erdos_887.variants.rosenfeld_4` | NOT_FINITELY_REFUTABLE | infinite-cardinality conclusion (Set.Infinite / Set.Finite / Cardinal): negation is a global nonexistence or infinitude proof [+GLOBAL_CONST] |
| 889 | `erdos_889` | NOT_FINITELY_REFUTABLE | asymptotic/eventual quantifier (atTop / ∀ᶠ / Tendsto / big-O / limsup): negation needs an infinite family + rate |
| 889 | `erdos_889.variants.V1_eq_1_finite` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 889 | `erdos_889.variants.general` | NOT_FINITELY_REFUTABLE | asymptotic/eventual quantifier (atTop / ∀ᶠ / Tendsto / big-O / limsup): negation needs an infinite family + rate |
| 889 | `erdos_889.variants.v1_eq_1_finite` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 890 | `erdos_890.parts.a` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 890 | `erdos_890.parts.b` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 891 | `erdos_891` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 891 | `erdos_891.variants.case_k_2` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 891 | `erdos_891.variants.weisenberg` | NOT_FINITELY_REFUTABLE | asymptotic/eventual quantifier (atTop / ∀ᶠ / Tendsto / big-O / limsup): negation needs an infinite family + rate |
| 893 | `erdos_893` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 897 | `erdos_897.variants.parts.i` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 897 | `erdos_897.variants.parts.ii` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 906 | `erdos_906` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 912 | `erdos_912` | NOT_FINITELY_REFUTABLE | asymptotic/eventual quantifier (atTop / ∀ᶠ / Tendsto / big-O / limsup): negation needs an infinite family + rate [+GLOBAL_CONST] |
| 912 | `erdos_912.variants.tao` | NOT_FINITELY_REFUTABLE | asymptotic/eventual quantifier (atTop / ∀ᶠ / Tendsto / big-O / limsup): negation needs an infinite family + rate |
| 913 | `erdos_913` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 913 | `erdos_913.variants.infinite_many_8p_sq_add_one_primes` | NOT_FINITELY_REFUTABLE | infinite-cardinality conclusion (Set.Infinite / Set.Finite / Cardinal): negation is a global nonexistence or infinitude proof |
| 918 | `erdos_918.parts.i` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 918 | `erdos_918.parts.ii` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 918 | `erdos_918.variants.all_subgraphs.parts.i` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 918 | `erdos_918.variants.all_subgraphs.parts.ii` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 930 | `erdos_930` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 931 | `erdos_931` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 931 | `erdos_931.variants.additional_condition` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 931 | `erdos_931.variants.exists_prime` | CANDIDATE_FOR_DEPTH | literal statement is a universal/decidable-body claim whose negation is one finite object |
| 932 | `erdos_932` | NOT_FINITELY_REFUTABLE | infinite-cardinality conclusion (Set.Infinite / Set.Finite / Cardinal): negation is a global nonexistence or infinitude proof |
| 933 | `erdos_933` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 936 | `erdos_936.variants.factorial_add_one` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 936 | `erdos_936.variants.factorial_sub_one` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 936 | `erdos_936.variants.two_pow_add_one` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 936 | `erdos_936.variants.two_pow_sub_one` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 938 | `erdos_938` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 939 | `erdos_939` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 939 | `erdos_939.variants.infinite` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 939 | `erdos_939.variants.triples` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 940 | `erdos_940` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+DENSITY] |
| 940 | `erdos_940.variants.large_integers` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 940 | `erdos_940.variants.three_cubes` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+DENSITY] |
| 942 | `erdos_942` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC,INFINITARY,GLOBAL_CONST] |
| 943 | `erdos_943` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 944 | `erdos_944` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 944 | `erdos_944.variants.dirac_conjecture` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 944 | `erdos_944.variants.dirac_conjecture.k_eq_four` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 945 | `erdos_945` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 945 | `erdos_945.variants.constant` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 949 | `erdos_949` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 950 | `erdos_950.parts.i` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 950 | `erdos_950.parts.ii` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 950 | `erdos_950.parts.iii` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 950 | `erdos_950.variants.sum_primes` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 950 | `erdos_950.variants.weaker_pi` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC,EPSILON] |
| 951 | `erdos_951` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 952 | `erdos_952` | CANDIDATE_FOR_DEPTH | literal statement is a universal/decidable-body claim whose negation is one finite object |
| 955 | `erdos_955` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+DENSITY] |
| 959 | `erdos_959` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 961 | `erdos_961` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC,GLOBAL_CONST] |
| 962 | `erdos_962` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC,GLOBAL_CONST] |
| 967 | `erdos_967.variants.finite` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 967 | `erdos_967.variants.two_three_five` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 968 | `erdos_968` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+DENSITY] |
| 968 | `erdos_968.variants.infinite_decreasingTriples` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 968 | `erdos_968.variants.infinite_increasingTriples` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 971 | `erdos_971` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC,GLOBAL_CONST] |
| 972 | `erdos_972` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 973 | `erdos_973` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+GLOBAL_CONST] |
| 975 | `erdos_975` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC,GLOBAL_CONST] |
| 978 | `erdos_978.parts.ii` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 978 | `erdos_978.parts.iii` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 979 | `erdos_979` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 982 | `erdos_982` | CANDIDATE_FOR_DEPTH | literal statement is a universal/decidable-body claim whose negation is one finite object |
| 985 | `erdos_985` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 996 | `erdos_996` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC,ANALYTIC,GLOBAL_CONST] |
| 1002 | `erdos_1002` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 1003 | `erdos_1003` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 1003 | `erdos_1003.variants.Icc` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 1004 | `erdos_1004` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 1038 | `erdos_1038.parts.i` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 1041 | `erdos_1041` | CANDIDATE_FOR_DEPTH | literal statement is a universal/decidable-body claim whose negation is one finite object |
| 1044 | `erdos_1044.variants.fixed_degree` | CANDIDATE_FOR_DEPTH | literal statement is a universal/decidable-body claim whose negation is one finite object |
| 1047 | `erdos_1047.variants.max_non_convex_components` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 1049 | `erdos_1049` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ANALYTIC] |
| 1052 | `erdos_1052` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 1054 | `erdos_1054.parts.i` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 1054 | `erdos_1054.parts.ii` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC,DENSITY] |
| 1054 | `erdos_1054.parts.iii` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC,DENSITY] |
| 1055 | `erdos_1055` | NOT_FINITELY_REFUTABLE | infinite-cardinality conclusion (Set.Infinite / Set.Finite / Cardinal): negation is a global nonexistence or infinitude proof |
| 1055 | `erdos_1055.variants.erdos_limit` | NOT_FINITELY_REFUTABLE | asymptotic/eventual quantifier (atTop / ∀ᶠ / Tendsto / big-O / limsup): negation needs an infinite family + rate |
| 1055 | `erdos_1055.variants.selfridge_limit` | CANDIDATE_FOR_DEPTH | literal statement is a universal/decidable-body claim whose negation is one finite object |
| 1056 | `erdos_1056` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 1056 | `erdos_1056.variants.noll_simmons` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 1057 | `erdos_1057` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 1057 | `erdos_1057.variants.pomerance` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 1059 | `erdos_1059` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 1060 | `erdos_1060.parts.i` | NOT_FINITELY_REFUTABLE | asymptotic/eventual quantifier (atTop / ∀ᶠ / Tendsto / big-O / limsup): negation needs an infinite family + rate |
| 1060 | `erdos_1060.parts.ii` | NOT_FINITELY_REFUTABLE | asymptotic/eventual quantifier (atTop / ∀ᶠ / Tendsto / big-O / limsup): negation needs an infinite family + rate [+GLOBAL_CONST] |
| 1061 | `erdos_1061` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC,GLOBAL_CONST] |
| 1062 | `erdos_1062.parts.ii` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 1063 | `erdos_1063.better_upper` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 1065 | `erdos_1065.parts.i` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 1065 | `erdos_1065.parts.ii` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 1068 | `erdos_1068` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 1072 | `erdos_1072.parts.i` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 1072 | `erdos_1072.parts.ii` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC,DENSITY] |
| 1072 | `erdos_1072.variants.littleo` | NOT_FINITELY_REFUTABLE | asymptotic/eventual quantifier (atTop / ∀ᶠ / Tendsto / big-O / limsup): negation needs an infinite family + rate |
| 1073 | `erdos_1073` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 1074 | `erdos_1074.parts.i` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+DENSITY] |
| 1074 | `erdos_1074.parts.ii` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+DENSITY] |
| 1074 | `erdos_1074.parts.iii` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+DENSITY] |
| 1074 | `erdos_1074.parts.iv` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+DENSITY] |
| 1074 | `erdos_1074.variants.EHSNumbers_one_half` | NOT_FINITELY_REFUTABLE | density statement: negation needs an asymptotic rate, not a finite artifact |
| 1082 | `erdos_1082.parts.i` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 1084 | `erdos_1084.variants.triangular_optimal_d2` | CANDIDATE_FOR_DEPTH | literal statement is a universal/decidable-body claim whose negation is one finite object |
| 1085 | `erdos_1085.variants.upper_d3` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 1093 | `erdos_1093.parts.i` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 1093 | `erdos_1093.parts.ii` | NOT_FINITELY_REFUTABLE | infinite-cardinality conclusion (Set.Infinite / Set.Finite / Cardinal): negation is a global nonexistence or infinitude proof |
| 1094 | `erdos_1094` | NOT_FINITELY_REFUTABLE | infinite-cardinality conclusion (Set.Infinite / Set.Finite / Cardinal): negation is a global nonexistence or infinitude proof |
| 1095 | `erdos_1095.variants.log_equivalent` | NOT_FINITELY_REFUTABLE | asymptotic/eventual quantifier (atTop / ∀ᶠ / Tendsto / big-O / limsup): negation needs an infinite family + rate |
| 1095 | `erdos_1095.variants.lower_conjecture` | NOT_FINITELY_REFUTABLE | asymptotic/eventual quantifier (atTop / ∀ᶠ / Tendsto / big-O / limsup): negation needs an infinite family + rate [+GLOBAL_CONST] |
| 1095 | `erdos_1095.variants.upper_conjecture` | NOT_FINITELY_REFUTABLE | asymptotic/eventual quantifier (atTop / ∀ᶠ / Tendsto / big-O / limsup): negation needs an infinite family + rate |
| 1101 | `erdos_1101.parts.i` | NOT_FINITELY_REFUTABLE | asymptotic/eventual quantifier (atTop / ∀ᶠ / Tendsto / big-O / limsup): negation needs an infinite family + rate |
| 1101 | `erdos_1101.parts.ii` | NOT_FINITELY_REFUTABLE | asymptotic/eventual quantifier (atTop / ∀ᶠ / Tendsto / big-O / limsup): negation needs an infinite family + rate |
| 1106 | `erdos_1106.parts.i` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 1106 | `erdos_1106.parts.ii` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 1107 | `erdos_1107` | NOT_FINITELY_REFUTABLE | asymptotic/eventual quantifier (atTop / ∀ᶠ / Tendsto / big-O / limsup): negation needs an infinite family + rate |
| 1108 | `erdos_1108.parts.i` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 1108 | `erdos_1108.parts.ii` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 1109 | `erdos_1109` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+EPSILON] |
| 1109 | `erdos_1109.variants.polylog` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+GLOBAL_CONST] |
| 1110 | `erdos_1110` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 1113 | `erdos_1113` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 1113 | `erdos_1113.variants.filaseta_finch_kozek` | CANDIDATE_FOR_DEPTH | literal statement is a universal/decidable-body claim whose negation is one finite object |
| 1133 | `erdos_1133` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC,GLOBAL_CONST] |
| 1135 | `erdos_1135` | CANDIDATE_FOR_DEPTH | literal statement is a universal/decidable-body claim whose negation is one finite object |
| 1137 | `erdos_1137` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 1139 | `erdos_1139` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 1142 | `erdos_1142` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 1145 | `erdos_1145` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 1146 | `erdos_1146` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 1150 | `erdos_1150` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC,GLOBAL_CONST] |
| 1167 | `binary_colors` | NOT_FINITELY_REFUTABLE | infinite-cardinality conclusion (Set.Infinite / Set.Finite / Cardinal): negation is a global nonexistence or infinitude proof |
| 1167 | `erdos_1167` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 1167 | `finite_targets` | NOT_FINITELY_REFUTABLE | infinite-cardinality conclusion (Set.Infinite / Set.Finite / Cardinal): negation is a global nonexistence or infinitude proof |
| 1167 | `infinite_targets` | NOT_FINITELY_REFUTABLE | infinite-cardinality conclusion (Set.Infinite / Set.Finite / Cardinal): negation is a global nonexistence or infinitude proof |
| 1167 | `r_eq_two` | NOT_FINITELY_REFUTABLE | infinite-cardinality conclusion (Set.Infinite / Set.Finite / Cardinal): negation is a global nonexistence or infinitude proof |
| 1175 | `erdos_1175` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 1175 | `erdos_1175.variants.threshold_formulation` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 1176 | `erdos_1176` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 1192 | `erdos_1192` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 1199 | `erdos_1199` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 1201 | `erdos_1201` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC,EPSILON] |
| 1203 | `erdos_1203` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |
| 1209 | `erdos_1209.parts.iii.b` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) |
| 1209 | `erdos_1209.parts.iii.c` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 1209 | `erdos_1209.parts.iii.d` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+INFINITARY] |
| 1210 | `erdos_1210` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+GLOBAL_CONST] |
| 1210 | `erdos_1210.variants.er80_correction` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+GLOBAL_CONST] |
| 1212 | `erdos_1212` | NOT_FINITELY_REFUTABLE | answer(sorry) hole: literal declaration has no truth value a finite object can falsify (METHOD Phase 0A answer_placeholder=true) [+ASYMPTOTIC] |


---

# Depth targets

Every computation below ran under an explicit `timeout 60` wall-clock cap with
exact integer / `Fraction` arithmetic. Source statements were pulled from
`https://www.erdosproblems.com/latex/<id>` (the LaTeX view of the canonical
page; plain `curl` with a browser User-Agent returns HTTP 200 — the Cloudflare
403 only affects the default curl UA) and from the `<div id="prize">` status
line on `https://www.erdosproblems.com/<id>`. The site's own metadata repo
`teorth/erdosproblems` (`data/problems.yaml`) carries status/prize/tags but no
statements; it was used for the four status coordinates. There is no JSON API
(`/api/problems/<id>` is a Flask 404).

Verifier scripts are committed alongside this file:
`verify_erdos931_exists_prime.py`, `verify_erdos10_erdos11.py`,
`verify_erdos677_lcm_interval.py`, `verify_erdos_misc.py`.

## D1 — Erdős 931, `erdos_931.variants.exists_prime`

**Lean (upstream 2411d22e, `FormalConjectures/ErdosProblems/931.lean:71`)**

```lean
theorem erdos_931.variants.exists_prime (k₁ k₂ n₁ n₂ : ℕ) (h₁ : k₂ ≤ k₁) (h₂ : 3 ≤ k₂)
    (h₃ : n₁ + k₁ ≤ n₂) (h₄ : (∏ i ∈ Finset.Icc 1 k₁, (n₁ + i)).primeFactors =
      (∏ j ∈ Finset.Icc 1 k₂, (n₂ + j)).primeFactors) :
    ∃ (p : ℕ), p.Prime ∧ n₁ ≤ p ∧ p ≤ n₂
```

**Source (erdosproblems.com/931, status `OPEN`)** — "Erdős was unable to prove
that if the two products have the same factors then there must exist a prime
between $n_1$ and $n_2$."

**Word-by-word divergence.** The prose says "a prime *between* $n_1$ and
$n_2$"; the Lean uses the **closed** interval `n₁ ≤ p ∧ p ≤ n₂`. This is a
*weakening* (it also accepts `p = n₁` and `p = n₂`), so it makes the
declaration harder, not easier, to refute. It also makes the declaration
trivially true whenever `n₁ ≤ 2 ≤ n₂` — which is exactly what happens on the
repo's own proved witness `erdos_931.variants.additional_condition_nonempty`
(`k₁,k₂,n₁,n₂ = 10,3,0,13`, i.e. `10! = 2^8·3^4·5^2·7` vs
`14·15·16 = 2^5·3·5·7`, both with prime support `{2,3,5,7}`): the conclusion is
discharged by `p = 2`. Same for Tijdeman's example `19,20,21,22` /
`54,55,56,57` (`n₁=18, k₁=4, n₂=53, k₂=4`, common support `{2,3,5,7,11,19}`),
discharged by `p = 19`.

**Negation shape (finite).** A counterexample is one tuple `(k₁,k₂,n₁,n₂)` with
`3 ≤ k₂ ≤ k₁`, `n₁+k₁ ≤ n₂`, equal prime supports, and **no prime in the closed
interval `[n₁,n₂]`**. Since `n₂ - n₁ ≥ k₁ ≥ k₂ ≥ 3`, the interval `[n₁,n₂]`
must sit inside a maximal prime-free run of span `≥ 3`. That reduces the search
to an exhaustive enumeration over prime-free runs.

**Search (`verify_erdos931_exists_prime.py 300000`, 54.2 s).**
All 20,028 maximal prime-free runs of span ≥ 3 with `n₁ ≤ 300000` (max span 84,
i.e. the largest admissible `k₁` in range is 84); for every `(n₁,n₂)` inside a
run and every `3 ≤ k₂ ≤ k₁ ≤ n₂-n₁`: **161,590,323 tuples tested, 0 satisfy
`h₄`**. No premise-satisfying tuple with a prime-free interval exists in that
range at all — the binding constraint is `h₄`, not the prime.

**Verdict:** `HOLD_BOUNDED`. No counterexample; the interval-endpoint
divergence (`between` vs `≤ … ≤`) is a real but *conservative* formalization
difference and is recorded as a `STATUS_SYNC`-class note, not a defect that
could be exploited.

## D2 — Erdős 10, `erdos_10.variants.granville_soundararajan_odd`

**Lean (`10.lean:59`)**

```lean
theorem erdos_10.variants.granville_soundararajan_odd :
    {n : ℕ | Odd n ∧ 1 < n} ⊆ sumPrimeAndTwoPows 3 ∧
      {n : ℕ | Even n ∧ n ≠ 0} ⊆ sumPrimeAndTwoPows 4
```

with `sumPrimeAndTwoPows k = { p + (pows.map (2 ^ ·)).sum | p.Prime, pows : Multiset ℕ, pows.card ≤ k }`.

**Source (erdosproblems.com/10, status `OPEN`)** — "Granville and Soundararajan
have conjectured that at most 3 powers of 2 suffice for all odd integers, and
hence at most 4 powers of 2 suffice for all even integers."

**Exact semantics used.** A multiset of at most `k` exponents sums to a number
of binary popcount `≤ k`, and conversely every number of popcount `≤ k` is such
a sum. Hence
`n ∈ sumPrimeAndTwoPows k ⟺ ∃ prime p ≤ n with popcount(n − p) ≤ k`
(the empty multiset gives `popcount 0 = 0`, i.e. `n` itself prime).

**Semantics calibration against a `research solved` sibling.** The same file
asserts `erdos_10.variants.grechuk_example : 1117175146 ∉ sumPrimeAndTwoPows 3`.
The popcount characterisation reproduces this exactly: enumerating **all**
`d ≥ 0` with `popcount d ≤ 3` and `d ≤ 1117175144`, no `1117175146 − d` is
prime. Semantics fixture PASSES.

**Search (`verify_erdos10_erdos11.py erdos10 20000000`, 43.3 s).**
Every `2 ≤ n ≤ 20,000,000`: odd `n` tested against popcount ≤ 3, even `n`
against popcount ≤ 4. **0 odd failures, 0 even failures.**

**Verdict:** `HOLD_BOUNDED`. Note the parent problem's source statement says
"every **large** integer", but this particular declaration is the
Granville–Soundararajan variant, which the source does state without a
largeness caveat ("for all odd integers"), so there is no all-vs-eventually
divergence to exploit here.

## D3 — Erdős 11, `erdos_11`, `.variants.not_four_dvd`, `.variants.two_pow_two`

**Lean (`11.lean:28,38,47`)** — three universally quantified declarations:
`∀ n, Odd n → 1 < n → ∃ k l, Squarefree k ∧ n = k + 2^l`; the same with
hypothesis `¬ 4 ∣ n` (so it also covers every `n ≡ 2 (mod 4)`); and the
two-powers version.

**Source (erdosproblems.com/11, status `OPEN`)** — "Is every **large** odd
integer $n$ the sum of a squarefree number and a power of 2?"

**Word-by-word divergence — this is the target shape.** The source says
*large*; the Lean quantifies over **all** odd `n > 1`. The unrestricted version
is exactly the kind of statement that is often finitely false. It is not,
however, exploitable here: the source notes record that Odlyzko checked to
`10^7` and Hercher [He24b] verified **all** odd integers up to `2^50 ≈
1.12·10^15`, so the "large" gap is already closed numerically far beyond any
reachable search.

The `not_four_dvd` variant is the genuinely wider one: it adds every
`n ≡ 2 (mod 4)`, a residue class the cited verifications (stated for *odd*
integers) do not cover.

**Search (`verify_erdos10_erdos11.py erdos11 50000000`, 27.3 s).** Exact
squarefree sieve (`Squarefree 0 = False`, `Squarefree 1 = True`, matching
Mathlib). Every `2 ≤ n ≤ 50,000,000` with `n` odd or `n ≢ 0 (mod 4)`:
**0 failures for `erdos_11`, 0 for `not_four_dvd` (including all `n ≡ 2 mod 4`),
0 for `two_pow_two`.**

**Verdict:** `HOLD_BOUNDED` on all three. The `n ≡ 2 (mod 4)` class — the part
not covered by the published odd-integer verifications — is clean to `5·10^7`.

## D4 — Erdős 677, `erdos_677`

**Lean (`677.lean:41`)**

```lean
theorem erdos_677 :
    ∀ (m n k : ℕ), k > 0 → m ≥ n + k → lcmInterval m k ≠ lcmInterval n k
```

`lcmInterval n k = (Finset.Ioc n (n+k)).lcm id = lcm{n+1,…,n+k}`
(`FormalConjecturesForMathlib/Algebra/GCDMonoid/Finset.lean:27`).

**Source (erdosproblems.com/677, status `OPEN`)** — "Is it true that for all
$m\geq n+k$, $M(n,k)\neq M(m,k)$?" The Lean matches the source exactly
(including the free `k > 0`). Source notes: "The Thue–Siegel theorem implies
that, for fixed $k$, there are only **finitely many** $m,n$ such that $m\geq
n+k$ and $M(n,k)=M(m,k)$" — i.e. the source itself leaves room for a finite
counterexample set. The two solutions Erdős knew, `M(4,3)=M(13,2)` and
`M(3,4)=M(19,2)`, use **different** `k` on the two sides and are therefore not
counterexamples to this declaration; they are reproduced verbatim by the repo's
own `@[category test] lcmInterval_eq_example1` and are used here as calibration
fixtures (both check out: 210 and 420).

**Two independent search paths, both zero.**

1. Collision-dictionary search: for `k = 1..12` and `n = 0..200,000`, hash every
   `lcmInterval n k` and flag equal values with index gap `≥ k`.
   **0 counterexamples** (3.8 s). Equal values *do* occur — e.g.
   `lcmInterval 9 10 = lcmInterval 12 10 = 232792560` — but always with gap
   `< k`; the largest observed gap is 3 (at `k = 10`), never reaching `k`.
2. Complete-in-`m` divisor-run search: `m+1,…,m+k` must **all divide**
   `V = lcmInterval n k`, so they are a run of `k` consecutive divisors of `V`.
   Factoring `V` and enumerating its divisors settles **every** `m` at once,
   not just `m ≤ 200,000`. Run for `n = 0..40`, `k = 3..24`:
   **0 counterexamples** (43.8 s).

**Verdict:** `HOLD_BOUNDED`. Path 2 is a genuine all-`m` closure on the
low-`(n,k)` corner; path 1 is a bounded two-sided sweep.

## D5 — Erdős 364, `erdos_364`

**Lean (`364.lean:30`)** `¬ ∃ (n : ℕ), Powerful n ∧ Powerful (n+1) ∧ Powerful (n+2)`.
**Source (erdosproblems.com/364, status `VERIFIABLE` — "Open, but could be proved
with a finite example")** — "Are there any triples of consecutive positive
integers all of which are powerful?" Lean is source-faithful. Note the Lean
polarity: the *declaration* asserts non-existence, so a finite triple would
refute the declaration and simultaneously answer the source question "yes".

**Search (`verify_erdos_misc.py p364 100000000000`, 1.0 s).** Generated all
680,331 powerful numbers `≤ 10^11` as `a²b³` (plus `0`, which is `Powerful` in
Mathlib since every prime divides `0` and `p² ∣ 0`). **0 triples.** Control:
**16 consecutive powerful pairs** in range, consistent with Mahler's
infinitude via `x² = 8y² + 1`, so the generator is not silently empty.

**Verdict:** `HOLD_BOUNDED` and prior-art stop — OEIS A076445 already excludes
`n < 7.38·10^28`.

## D6 — Erdős 406, `erdos_406.variants.one_two`

**Lean (`406.lean:41`)** `IsGreatest { n | n.isPowerOfTwo ∧ Nat.digits 3 n ⊆ [1,2] } (2^15)`.
**Source (erdosproblems.com/406, status `OPEN`)** — "If we only allow the digits
1 and 2 then `2^15` seems to be the largest such power of 2." Faithful.

**Negation shape (finite).** `IsGreatest S a = a ∈ S ∧ ∀ b ∈ S, b ≤ a`. Two
finite refutation routes: (i) `2^15 ∉ S`, or (ii) some `2^m > 2^15` in `S`.

**Search (`verify_erdos_misc.py d406 4000`, 3.7 s).**
* Membership: base-3 digits of `2^15 = 32768` (little-endian) are
  `[2,2,1,1,2,2,2,2,1,1]` — all in `{1,2}`. `2^15 ∈ S` **confirmed**.
* Upper bound: for `0 ≤ m ≤ 4000`, `2^m` has all base-3 digits in `{1,2}`
  exactly for `m ∈ {0,1,2,3,4,15}`. **No `2^m > 2^15` in `S`.**
* Companion calibration for the sibling `erdos_406` (`digits ⊆ {0,1}`):
  `m ∈ {0,2,8}`, i.e. `1, 4, 256` — reproduces the source note "The only
  examples seem to be 1, 4 = 1+3, and 256 = 1+3+3²+3⁵" exactly.

**Verdict:** `HOLD_BOUNDED` and prior-art stop — Saye [Sa22] already computed
that `2^n` contains **every** ternary digit for `16 ≤ n ≤ 5.9·10^21`, which
settles both digit-restricted sets far beyond any reachable search.

## D7 — Erdős 324, `erdos_324.variants.quintic`

**Lean (`324.lean:39`)** `{(a, b) : ℕ × ℕ | a < b}.InjOn fun (a, b) => a ^ 5 + b ^ 5`.
**Source (erdosproblems.com/324, status `OPEN`)** — "Probably `f(x)=x^5` should
work"; the Lander–Parkin–Selfridge conjecture would imply it for all `n ≥ 5`.
Faithful. Negation = one pair of distinct pairs `(a,b) ≠ (c,d)`, `a<b`, `c<d`,
with `a^5+b^5 = c^5+d^5` — a finite witness.

**Search (`verify_erdos_misc.py q324 1500`, 0.9 s).** All `0 ≤ a < b < 1500`:
**1,124,250 sums, 0 collisions.**

**Verdict:** `HOLD_BOUNDED`. (Prior art: no equal sum of two fifth powers is
known at all; published searches go far beyond this bound. The bounded run is
calibration, not new evidence.)

## D8 — Erdős 1084, `erdos_1084.variants.triangular_optimal_d2` — `STATUS_SYNC`

**Lean (`1084.lean`, with `variable {n : ℕ}` at file scope, so `n` is
auto-bound universally)**

```lean
/-- Erdős conjectured that the triangular lattice is best possible in 2D, in particular that
$f_2(3n^2 + 3n + 1) < 9n^2 + 3n$.
Note: in [Er75f] is read $9n^2 + 6n$, but this seems to be a typo. -/
@[category research open, AMS 52]
theorem erdos_1084.variants.triangular_optimal_d2 :
    f 2 (3 * n ^ 2 + 3 * n + 1) = 9 * n ^ 2 + 3 * n
```

**Source (erdosproblems.com/1084, status `OPEN` for the parent estimate)** —
"In [Er75f] he speculated that the triangular lattice is exactly the best
possible, and in particular `f_2(3n²+3n+1) = 9n²+3n`. **Harborth [Ha74b] proved
this**, and more generally `f_2(n) = ⌊3n − √(12n−3)⌋` for all `n ≥ 2`."

**Two defects, neither exploitable as a counterexample.**
1. The Lean **docstring** states the conjecture with a strict `<`. The source
   states it with `=`. The `<` version is *false*: the triangular-lattice patch
   with `3n²+3n+1` points attains exactly `9n²+3n` unit distances (`n = 1`:
   7 points, 12 unit pairs = `9·1+3·1`), so `f_2(3n²+3n+1) < 9n²+3n` fails at
   every `n ≥ 1`. The Lean *statement* uses `=` and is the correct reading, so
   the defect is confined to the docstring.
2. The declaration is `@[category research open]`, but the canonical source
   records it as **proved by Harborth (1974)**. Cross-check of Harborth's
   closed form at the relevant arguments:
   `3(3n²+3n+1) − √(12(3n²+3n+1) − 3) = 9n²+9n+3 − √((6n+3)²) = 9n²+9n+3 − (6n+3) = 9n²+3n` ✓,
   and the auto-bound `n = 0` case is `f 2 1 = 0 = 9·0+3·0` ✓.

**Verdict:** `STATUS_SYNC` — the exact declaration appears to be a theorem of
Harborth mis-labelled `research open`, plus a docstring transcription error
(`<` for `=`). **Not** a counterexample. No upstream action taken.

## D9 — Erdős 409, `erdos_409.variants.sigma_termination` — triage correction

**Lean (`409.lean:130`)** `∀ n, n > 1 → ∃ i, ((σ 1 · - 1)^[i] n).Prime`, with
the file's own note "this is open — it is not clear that the σ iteration always
terminates, since it is non-decreasing".

Initially triaged `CANDIDATE_FOR_DEPTH` because a **cycle** in the orbit would
be a finite refutation certificate. That is impossible: for composite `n > 1`,
`σ(n) ≥ 1 + d + n` for some proper divisor `d > 1`, so `σ(n) − 1 > n`; and for
prime `n`, `σ(n) − 1 = n` and the orbit is already at a prime. Hence the orbit
is **strictly increasing until it halts** and can never cycle. The literal
negation is `∃ n > 1, ∀ i, ¬ Prime(…)`, which has no finite certificate.

**Verdict:** `CERTIFICATE_SHAPE_FAIL` — reclassify as NOT_FINITELY_REFUTABLE.
(ℕ-subtraction is also harmless here: `σ 1 0 = 0` and `0 - 1 = 0` in ℕ, but no
`n > 1` can reach `1`, since `σ(n) − 1 = 1` forces `σ(n) = 2`, i.e. `n = 1`.)

## D10 — Erdős 242, `erdos_242` — **INCOMPLETE / UNVERIFIED**

**Lean (`242.lean:32`)**

```lean
theorem erdos_242 (n : ℕ) (hn : 2 < n) :
    ∃ x y z : ℕ, 1 ≤ x ∧ x < y ∧ y < z ∧ (4 / n : ℚ) = 1 / x + 1 / y + 1 / z
```

**Source (erdosproblems.com/242, status `FALSIFIABLE` — "Open, but could be
disproved with a finite counterexample")** — "For every `n>2` there exist
**distinct** integers `1 ≤ x < y < z` such that `4/n = 1/x + 1/y + 1/z`."
**No divergence:** the source itself carries the strict `x < y < z`, and the
Lean division is rational (`(4/n : ℚ)`), not ℕ-division. Erdős–Straus.

**Prior art that closes the exploitable window:** verified for all `n ≤ 10^18`
[MiDu25]; it suffices to prove it for prime `n`; Mordell/Terzi reduce the
exceptions to explicit congruence classes.

**State of the run (`verify_erdos_misc.py es242 3000`, hit the 52 s cap).**
Phase 1 (per-`n` capped search: `x` descending over `(n/4, 3n/4]`, `y` capped
at 20,000, 400,000-op budget) covered `n = 3..2901` and left **178 `n`
unresolved by the cap**. Phase 2 (the exhaustive per-`n` routine) then hit the
cap having checked **none** of them.

**Verdict: NONE — UNVERIFIED.** 0 counterexamples were found, but 178 values of
`n ≤ 2901` were never settled exhaustively. This is a `TIMEOUT_BRACKET`, not a
hold. The exhaustive routine is `es242_solve(n, ycap=None, budget=None)` in
`verify_erdos_misc.py`: `x ∈ (⌊n/4⌋, ⌊3n/4⌋]`; with `p/q = 4/n − 1/x` in lowest
terms, `y` ranges over `(q/p, 2q/p]` and `z = qy/(py − q)` must be an integer
`> y`. Next agent: rerun phase 2 alone over the unresolved list.

## D11 — Erdős 779, `erdos_779` — NOT STARTED

Script mode `verify_erdos_misc.py d779 <nmax>` is written but **never
executed**. Source (status `FALSIFIABLE`): "Let `n > 1` and `p_1 < … < p_n` the
first `n` primes, `P = ∏ p_i`. Does there always exist some prime `p` with
`p_n < p < P` such that `P + p` is prime?" The Lean uses
`P := ∏ i ∈ range (n+1), nth Nat.Prime i` with `hn : n ≥ 1`, i.e. the first
`n+1` primes and `nth Nat.Prime n` as the largest — the index shift the
docstring documents. **This matches the source exactly; no divergence.**
Deaconescu verified `n ≤ 1000`; Cambie's heuristic puts the failure chance at
`≪ exp(-n^{-cn})`. A *finite refutation* would require ruling out every prime
`p < P`, which is infeasible beyond `n ≈ 3`, so this is effectively
`CONSTRUCTION_ONLY`.
