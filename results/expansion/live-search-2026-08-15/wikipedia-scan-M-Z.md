# Wikipedia collection audit — names M–Z (plus digit/symbol) — 2026-08-15

**Scope.** `corpus == "Wikipedia"` entries of
`results/expansion/open_targets_other_corpora_20260815.json` whose `name` does
not begin with a–l (case-insensitive). **51 files**, 206,201 bytes total. None
begin with a digit or symbol.

**Upstream pin.** `638da20efd8eeeed2993fc2550fc596dc90c1ce8`
(`2026-08-15 09:23:12 +0000`, "Mark OEIS A105565 as solved (#4958)"), read
read-only via `git show upstream/main:<path>`. Per-file blob SHAs recorded in
`scratchpad/mz/_index.json` and reproduced in the depth sections below.

**Method.** METHOD_V1_6 §A4 (triage all before depth), §A2 (P0 pre-flight),
§A5 (append after every target), §A6 (four-coordinate status). Hard cap 60 s per
computation; every timeout recorded as a bracket, never as a hold.

**Framing.** These are famous named conjectures. A finite refutation of one of
them is essentially certainly a bug in this audit, not a discovery. The vein
being worked is formalization faithfulness: does the Lean declaration say what
its own cited Wikipedia article says?

---

## 1. Triage (all 51, one line each)

Legend for the certificate column:
`FIN` finitely settleable/falsifiable in principle at reachable scale ·
`FIN-HARD` finite but out of reach of a 60 s budget ·
`INF` infinitary/asymptotic/real-analytic/cardinal — no finite certificate ·
`TERM` the open hole is an `answer(sorry)` in **term** position asking for an
unknown constant, so it cannot be closed by a witness or refuted by a finite check.

| # | file | open decl(s) | certificate | one-line triage reason |
|---|---|---|---|---|
| 1 | SquarePacking | 5 × `IsLeast … answer(sorry)` | TERM | the hole is the unknown optimal side/radius; packings are real-geometric |
| 2 | SierpinskiNumber | `selfridge_conjecture`, `prime_sierpinski_problem`, `extended_sierpinski_problem` | INF | `IsSierpinskiNumber` quantifies `∀ n` over all exponents; no finite certificate either way |
| 3 | Taxicab | `taxicab_for_5_2_2`, `taxicab_for_5_2_n` | FIN (positive side only) | a witness `a⁵+b⁵=c⁵+d⁵` would settle it; definitional parse worth checking |
| 4 | Mersenne | `new_mersenne_conjecture`, `.variants.prime`, `infinitely_many_mersenne_primes`, `catalans_mersenne_conjecture` | FIN (NMC per-`p`) / INF (rest) | NMC is a per-`p` finite predicate; Catalan/infinitude are infinitary |
| 5 | MagicSquares | `exists_magic_square_squares`, `exists_semi_magic_square_cubes` | FIN (positive side) | both are pure existence over ℕ⁹; a witness settles `answer := True` |
| 6 | MoserWorm | `mosers_worm_problem`, `convex_mosers_worm_problem` | TERM | GLB of areas of universal covers; unknown real constant |
| 7 | PerfectNumbers | `infinitely_many_perfect`, `infinitely_many_even_perfect`, `odd_perfect_number_conjecture` | INF | infinitude / odd-perfect lower bound is 10^1500 |
| 8 | SolitaryNumber | `is_ten_solitary`, `infinite_club_exists` | FIN-HARD | a friend of 10 is known to exceed 10^30 |
| 9 | SidorenkoConjecture | `sidorenko_conjecture` | FIN-HARD | quantified over all finite bipartite `H` and all finite `G`; check `IsBipartite` |
| 10 | ScholzConjecture | `scholz_conjecture` | FIN-HARD | ℓ(2^n−1) needs addition-chain search, superexponential past n≈20 |
| 11 | SumOfThreeCubes | `isSumOfThreeCubes_iff_mod_9` | INF | the hard direction is a non-existence statement about all integers |
| 12 | PowerfulNumbersDensity | `error_term_improvement` | INF | big-O error-exponent question |
| 13 | PrimeTriplets | `prime_triplets` | INF | infinitude of a prime constellation |
| 14 | PrimesAndPerfectSquares | `infinite_prime_sq_add_one` | INF | Landau problem 4, infinitude |
| 15 | QuasiperfectNumbers | `exists_quasiperfect` | FIN-HARD | quasiperfect n must be an odd square > 10^35 |
| 16 | RamseyNumbers | `ramsey_number_five_five` | TERM | asks for the value of R(5,5); bracket 43..46 is upstream already |
| 17 | RationalDistanceProblem | `rational_distance_problem` | FIN (positive side) | a rational-distance point would be an explicit witness |
| 18 | SnakeInTheBox | `snake_dim_nine` | TERM | asks for the unknown value of the dim-9 snake |
| 19 | TwinPrimes | `twin_primes` | INF | infinitude |
| 20 | UnionClosed | `union_closed`, `.variants.cardinality_even_of_union_closed_tight` | FIN (variant) | the tightness variant is a finite search over union-closed families |
| 21 | PebblingNumberConjecture | `pebbling_number_conjecture` | FIN-HARD | Graham's product conjecture; π(G) is itself PSPACE-flavoured |
| 22 | Mandelbrot | `MLC`, `MLC_general_exponent`, `density_of_hyperbolicity` ×2, `volume_frontier_*` ×2 | INF | complex-analytic / measure-theoretic |
| 23 | MovingSofa | `volume_eq_sofaConstant_iff_congruent_gerversSofa` | INF | uniqueness of Gerver's sofa, real-geometric |
| 24 | Sendov | `sendov_conjecture` | INF | all complex polynomials of each degree |
| 25 | RegularPrimes | `regularprime_conjecture` | INF | infinitude of regular primes |
| 26 | RudinsConjecture | `rudins_conjecture`, `rudins_conjecture_strong`, `rudins_conjecture_unique` | FIN (strong/unique, per N) | `Q N 24 1 = Qmax N` and the q=24 uniqueness are decidable for each N |
| 27 | Selfridge | `selfridge_conjecture` (PSW), `selfridge_seq_conjecture` | FIN-HARD | PSW counterexample > 2^64; Fermat-factor monotonicity needs F₁₂ |
| 28 | MeanValueProblem | `mean_value_problem` | INF | Smale K=1; all complex polynomials |
| 29 | SparseRuler | `wichmann_conjecture` | FIN-HARD | needs exhaustive perfect-ruler enumeration at ≥15 marks |
| 30 | RamanujanTau | `lehmer_ramanujan_tau` | FIN-HARD | τ(n)≠0 verified past 10^15; check the `∏'` junk-value risk |
| 31 | SurjunctiveGroup | `gottschalk_surjunctivity_conjecture` | INF | all groups, all finite alphabets |
| 32 | Mahler32 | `mahler_conjecture` | INF | real number with a condition on all n; check `IsZNumber` |
| 33 | NormalityOfPi | `pi_normal_base_ten` | INF | normality |
| 34 | Oppermann | `.parts.i`, `.parts.ii`, `oppermann_conjecture` | FIN (verification only) | per-x finite check; a counterexample needs a prime gap far beyond reach |
| 35 | Pell | `infinite_pellNumber_primes` | INF | infinitude |
| 36 | PierceBirkhoff | `pierce_birkhoff_conjecture` | INF | real semialgebraic geometry |
| 37 | PierpontPrime | `infinitely_many_pierpont_primes` | INF | infinitude |
| 38 | PollocksConjecture | `pollock_tetrahedral`, `.salzer_levine` | FIN | both have finitely checkable content at reachable scale |
| 39 | RiemannZetaValues | `irrational_five/seven/nine/eleven/odd` | INF | irrationality |
| 40 | Schanuel | `schanuel_conjecture` | INF | transcendence degree |
| 41 | Schinzel | `schinzel_conjecture` | INF | infinitude of simultaneous prime values |
| 42 | Singmaster | `singmaster` | INF | uniform bound over all t |
| 43 | SteinerSystem | `large_steiner_systems` (a `def`) | FIN (positive side) | an explicit S(t,k,n) with 5<t<10, n<200 would close it |
| 44 | Superperfectnumbers | `twoFivePerfect` | FIN | σ(σ(n))=5n is a direct finite search |
| 45 | Toronto | `DiscreteTopology.of_t2_of_torontoSpace` | INF | topological, all cardinalities |
| 46 | Transcendental | 16 open decls | INF (15) / FIN-HARD (1) | transcendence; `pi_pow_pi_pow_pi_pow_pi_not_integer` is finite but astronomically so |
| 47 | VaughtConjecture | `vaught_conjecture` | INF | cardinal arithmetic / model theory |
| 48 | WallSunSun | `exists_isWallSunSunPrime`, `infinite_isWallSunSunPrime`, `infinite_isWallSunSunPrime_of_disc_eq` | FIN (existence, positive side) | L_p ≡ 1 mod p² is a direct search; searched to 1.4·10^17 upstream |
| 49 | WilsonPrime | `infinitely_many_wilson_primes` | INF | infinitude |
| 50 | WolstenholmePrime | `wolstenholme_prime_infinite` | INF | infinitude |
| 51 | WoodalPrimes | `infinitely_many_woodall_primes` | INF | infinitude |

**Triage counts.** FIN 11 · FIN-HARD 9 · INF 26 · TERM 5.
(Files can carry several open declarations; the class shown is the strongest
available for that file.)

**Ranked depth head** (finite-settleable first, then highest suspicion of a
definitional divergence):
Superperfectnumbers · MagicSquares · PollocksConjecture · UnionClosed ·
RudinsConjecture · WallSunSun · Oppermann · Mahler32 · SierpinskiNumber ·
Taxicab · Mersenne · Selfridge · SnakeInTheBox · Toronto · SparseRuler.

---

## HANDOFF STATE

- Triage: **complete** (51/51).
- Depth: in progress. See §2 below for per-target verdicts appended as they land.
