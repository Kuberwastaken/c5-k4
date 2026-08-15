# Erdős Problems finite-counterexample hunt — live search 2026-08-15

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

