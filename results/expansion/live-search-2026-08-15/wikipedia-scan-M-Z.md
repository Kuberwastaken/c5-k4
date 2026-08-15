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

---

## 2. Depth verdicts

Blob SHAs are at pin `638da20e`. Every computational claim below was produced
under a 60 s cap; scripts live in
`scratchpad/mz/` (`probe_a2.py`, `probe_b2.py`, `probe_b3.py`, `probe_cfgh.py`,
`probe_d.py`, `verify_rudin.py`, `probe_e.py`).

### 2.1 RudinsConjecture — `rudins_conjecture_unique` is finitely FALSE — **DUPLICATE**

`FormalConjectures/Wikipedia/RudinsConjecture.lean`, blob
`322b2d7d43f9bf209db4fd6f533f663341c6a5e4` (4627 bytes).

Declaration (verbatim):

```lean
@[category research open, AMS 11]
theorem rudins_conjecture_unique (N : ℕ) (hN : 6 ≤ N) (q a : ℕ)
    (hqa : IsNontrivial q a) (hmax : Q N q a = Qmax N) : q = 24
```

**Witness.** `N = 6`, `q = 120`, `a = 49`.
`IsNontrivial 120 49` holds: `1 ≤ 120`, `1 ≤ 49`, `Nat.Coprime 120 49`
(`120 = 2³·3·5`, `49 = 7²`), `(120,49) ≠ (1,1)`.
First six terms `49, 169, 289, 409, 529, 649`; exactly four are squares
(`7², 13², 17², 23²`; `20² < 409 < 21²` and `25² < 649 < 26²`), so
`Q 6 120 49 = 4 = Q 6 24 1`, and `Qmax 6 = 4`
(González-Jiménez–Xarles verified `Q(N) = Q(N;24,1)` for `6 ≤ N ≤ 52`).
Conclusion would force `120 = 24`. Second witness at `N = 6`: `q = 168, a = 121`
(terms `121,289,457,625,793,961`, squares `11²,17²,25²,31²`).

**Independent re-verification.** Two programs sharing no code path: a
residue-class/sliding-window sieve (`probe_d.py`, `q ≤ 6000`) and a direct
brute force over `(q,a)` with `a` allowed to exceed `q` (`verify_rudin.py`,
`q ≤ 3000`). Both give identical `Qmax(N)` tables for `N ≤ 30` and identical
argmax sets.

**Root cause (adds to the existing issue).** Wikipedia's *Super-Strong Rudin's
Conjecture* asserts uniqueness only for `N = GP_k + 1 ≥ 8` where `GP_k` is the
`k`-th generalized pentagonal number, and only *up to equivalence*. The Lean
drops both qualifications and asserts `q = 24` for every `N ≥ 6`. The
computed failure set for `6 ≤ N ≤ 30` is exactly
`{6,7,9,10,11,12,15,19,20,21,22,24,25,26}`, and its complement inside
the range contains every `GP_k+1` value (`8, 13, 16, 23, 27`) — i.e. the data
match the source's restricted claim precisely.

**Classification (§A6).** (1) Rudin's conjecture untouched; (2) no formal
solution; (3) declaration **unfaithful** to the cited article;
(4) declaration **finitely false**. Formalization counterexample, *not* a
counterexample to Rudin.

**Duplicate status: DUPLICATE — STOP.** Upstream issue
[#4568](https://github.com/google-deepmind/formal-conjectures/issues/4568)
("Wikipedia/RudinsConjecture: counterexample to `rudins_conjecture_unique` at
N = 6", Terry-cyx, 2026-07-23, still OPEN) carries the identical witness
`(N,q,a) = (6,120,49)`. Independent reproduction only. The generalized-pentagonal
diagnosis and the second witness `(168,121)` are not in #4568.

`rudins_conjecture_strong` (`Q N 24 1 = Qmax N` for `N ≥ 6`) was **confirmed**
for `6 ≤ N ≤ 30` by both code paths — `HOLD_BOUNDED`, bracket `N ≥ 31`.

### 2.2 SparseRuler — `wichmann_conjecture` substitutes a hard threshold for "sufficiently large" — **apparently unclaimed**

```lean
@[category research open, AMS 5]
theorem wichmann_conjecture {g : List ℕ} (hopt : IsOptimal g) (hseg : 13 < g.length) :
    ∃ r s : ℕ, g = wichmannGaps r s ∨ g = (wichmannGaps r s).reverse
```

Wikipedia (raw article text, verified): *"Many (but not all) Wichmann rulers
are optimal, and **Wichmann speculated that all sufficiently large optimal
rulers are of this type**. None of the optimal rulers of length 1, 13, 17, 23
and 58 follow this pattern, but no further non-Wichmann optimal rulers are
known and **there are known to be no others up to length 213**."*

Divergences:

1. **"sufficiently large" → `13 < g.length`.** The source states an
   eventually-quantifier; the Lean states a specific explicit threshold. This is
   the band-1 shape the campaign converts on. Nothing in the source asserts that
   14 segments is enough.
2. **Wrong unit and off-by-one in the motivating remark.** The docstring says
   *"the known exceptions occur at lengths 1, 13, 17, 23, 58; the largest of
   these has 13 segments"*. The exceptions are catalogued by **length**; the
   maximal perfect-ruler lengths by mark count (OEIS A004137) are
   `…, 6 marks → 13, 7 → 17, 8 → 23, 13 → 58, 14 → 68, 15 → 79`, so the
   length-58 exception has **13 marks = 12 segments**, not 13 segments. The
   threshold is therefore conservative rather than tight, but the stated
   justification is off by one in the marks/segments unit.
3. **Verified range.** Even the weakest defensible explicit form is only
   verified to length 213 (≈ 24 marks), whereas the declaration ranges over all
   optimal rulers with ≥ 14 segments.

Checked and **clean**: `IsMinimal` and `IsMaximal` match the article's
definitions verbatim (*"minimal if there is no complete sparse ruler of length
L with m−1 marks … even if the marks could be rearranged"* — global, as in the
Lean; *"maximal if there is no complete sparse ruler of greater length with m
marks"*). `wichmannGaps` matches `W(r,s) = 1^r, r+1, (2r+1)^r, (4r+3)^s,
(2r+2)^{r+1}, 1^r`; the proved `wichmannGaps_length = 4r+s+2` segments and
`wichmannGaps_sum = 4r(r+s+2)+3(s+1)` agree with the article's
`4r+s+3` marks and identical length formula.

No finite counterexample is reachable: exhaustive enumeration of 15-mark
perfect rulers of length 79 is `C(78,13) ≈ 1.6·10^14`, far past the 60 s cap.
`INVALID_PRE_EVALUATION` for a finite certificate; the finding is
faithfulness-only, severity **statement ≠ source**, not `FINITELY_FALSE`.

**Duplicate status.** `gh` search on `Wichmann`, `wichmann_conjecture`,
`SparseRuler`: only issue #401 (Erdős 170, closed) and PR #4166
("feat(Wikipedia/SparseRuler) add Wichmann conjecture", merged). Absent from
trackers #4896 / #4923 / #4927. **Apparently unclaimed.**

### 2.3 Superperfectnumbers — `twoFivePerfect` faithful, no finite counterexample

```lean
def PerfectFor (n m k : ℕ) : Prop := 0 < n ∧ Nat.iterate (fun x => σ 1 x) m n = k * n
@[category research open, AMS 11] theorem twoFivePerfect : ¬ ∃ n, PerfectFor n 2 5
```

`σ(σ(n)) = 5n` searched exhaustively for `n ≤ 1,200,000` (divisor sieve to
6·10⁶ so `σ(n)` is always in range; zero skips). **No hit.**

Code validated by reproducing the published `(2,k)`-perfect data on the same
run: `(2,2) → 2,4,16,64,4096,65536`; `(2,3) → 8,21,512`;
`(2,4) → 15,1023,29127`; `(2,6) → 42,84,160,336,1344,86016`;
`(2,7) → 24,1536,47360` — all exact matches to the Wikipedia/OEIS tables.

The `n = 0` loophole that this shape usually carries is **already fixed**
upstream (PR #4096, "fix(Wikipedia/Superperfectnumbers): exclude `n = 0`", merged;
issue #2251 closed). Declaration faithful. `HOLD_BOUNDED`, bracket `n > 1.2·10⁶`.

### 2.4 MagicSquares — `exists_semi_magic_square_cubes` faithful and genuinely open

```lean
@[category research open, AMS 5 11]
theorem exists_semi_magic_square_cubes : answer(sorry) ↔ ∃ m : Fin 3 → Fin 3 → ℕ, ∃ t : ℕ,
   m.Injective2 ∧ (∀ i j, ∃ n : ℕ, 0 < n ∧ m i j = n ^ 3) ∧
   (∀ i, ∑ j, m i j = t) ∧ (∀ j, ∑ i, m i j = t)
```

`Function.Injective2 m` is `∀ a₁ a₂ b₁ b₂, m a₁ b₁ = m a₂ b₂ → a₁ = a₂ ∧ b₁ = b₂`,
i.e. all nine entries distinct — correct. Source check
(multimagie.com/English/SquaresOfCubes.htm, table *"First known squares of
cubes"*): **3×3 semi-magic square of cubes = "Unknown!", 3×3 magic square of
cubes = "Impossible"**. So `research open` is right and no witness is expected.

Two independent searches, no hit:
(a) group triples of distinct cubes by sum, look for three pairwise-disjoint
triples admitting a column arrangement — cube roots ≤ 200;
(b) the sharper *determined-third-row* search: for every disjoint pair of
equal-sum triples `A, B` and each of the 6 relative orderings, set
`C[x] = t − A[x] − B[x]` and test cubicity of `C[x]` against cubes up to
`3·LIMR³` (so the third row may use roots beyond the enumeration bound).
Run (b) at `LIMR = 220`: 1,750,540 triples, 185,715 equal-sum groups,
259,523 candidate pairs × 6 orderings, third-row roots admitted up to 317 —
**no hit**. `HOLD_BOUNDED`, bracket: two rows with roots > 220.

`exists_magic_square_squares` (magic square of squares, all rows/cols/both
diagonals, entries positive and distinct) is faithful to the Parker-square
problem and correctly open.

### 2.5 PollocksConjecture — both open declarations confirmed at finite scale

- `pollock_tetrahedral (N : ℕ) : ∃ f : Fin 5 → ℕ, N = ∑ i, tetrahedral (f i)` —
  `tetrahedral 0 = 0` makes "at most 5" the right reading. Verified for **all
  `N ≤ 3·10⁶`** (bitset reachability, 5 convolutions). Zero failures.
- `pollock_tetrahedral.salzer_levine : IsGreatest NotSumOfFourTetrahedral 343867` —
  membership half **verified exactly**: 343867 is not a sum of 4 tetrahedral
  numbers (exhaustive triple loop + set lookup); controls 343866 and 343868 are
  both representable. Maximality half verified up to `3·10⁶`: the exception set
  has **exactly 241 elements with maximum 343867**, matching OEIS A000797 and
  the file's companion `ncard_exceptions` claim.

Faithful; `HOLD_BOUNDED`, bracket `N > 3·10⁶`.

### 2.6 Oppermann, WallSunSun, Mersenne, Selfridge, Mahler32, Sierpinski, Taxicab — checked, clean

- **Oppermann** `parts.i / parts.ii / oppermann_conjecture`: `Finset.Ioo` is the
  open interval, `x - 1` is safe under `2 ≤ x`. Verified for every
  `2 ≤ x ≤ 50000`, zero failures. Faithful.
- **WallSunSun** `exists_isWallSunSunPrime`: `IsWallSunSunPrime p` = `p.Prime ∧
  lucasNumber p ≡ 1 [ZMOD p^2]`, with `lucasNumber = LucasSequence.V 1 (-1)`
  giving `2,1,3,4,7,11,…` — the correct Lucas numbers and the criterion
  Wikipedia states. No `p < 2·10⁶` satisfies it; the criterion was validated by
  confirming `L_p ≡ 1 (mod p)` for every prime tested. Faithful,
  `HOLD_BOUNDED` (upstream searches reach ~1.4·10^17 anyway).
  *Soft note, `infinite_isWallSunSunPrime_of_disc_eq`:* the set is
  `{p | ∃ a b, a² − 4b = D ∧ IsLucasWieferichPrime a b p}`, so the pair `(a,b)`
  is existentially quantified **inside** the set-builder. The source conjecture
  is about a fixed Lucas sequence of discriminant `D`; the Lean union over all
  `(a,b)` with `a²−4b = D` is strictly weaker. The file itself carries
  `TODO: Source this conjecture`, and `hD₁ : D ≠ 1` is redundant given
  `IsFundamentalDiscr`.
- **Mersenne** `new_mersenne_conjecture`: `IsSpecialForm p := ∃ k, p = 2^k+1 ∨
  p = 2^k−1 ∨ p = 4^k+3 ∨ p = 4^k−3` uses ℕ-subtraction, so `k = 0` contributes
  the truncated value `0` to the last two disjuncts. **Harmless**: `0` is not
  `Odd`, and the theorem's hypothesis is `Odd p`. Cross-checking the known
  Mersenne-prime exponents, Wagstaff-prime exponents and special-form values for
  odd `p ≤ 1000` produces no `p` where exactly two of the three conditions hold.
  `catalans_mersenne_conjecture` (`∀ n ≥ 5, Prime (catalanMersenne n)`) and
  `infinitely_many_mersenne_primes` are faithful.
- **Selfridge**: `IsSelfridge` matches Wikipedia's PSW statement token for token
  (`Odd p`, `p ≡ ±2 mod 5` as `2 ∨ 3`, `2^(p−1) ≡ 1 mod p`, `F_{p+1} ≡ 0 mod p`).
  `selfridge_seq_conjecture : ¬ Monotone fermatFactors` with
  `fermatFactors n = n.fermatNumber.primeFactors.card` matches
  *"g(n), the count of distinct prime divisors of F_n, is not monotonic"*.
  Both faithful.
- **Mahler32** `mahler_conjecture (x) (hx : IsZNumber x) : False`.
  `IsZNumber ξ := 0 < ξ ∧ ∀ n : ℕ, 1 ≤ n → Int.fract (ξ * (3/2)^n) < 1/2`.
  Wikipedia's definition quantifies over `n ≥ 0`, so the Lean predicate is
  *weaker* and the theorem correspondingly *stronger*. **Not a defect**: the map
  `ξ ↦ (3/2)ξ` is a bijection of `(0,∞)` carrying Lean-Z-numbers onto Mahler
  Z-numbers, so "no Lean Z-number exists" ⟺ Mahler's conjecture. Recorded
  because the surface reading suggests a divergence that is not one.
- **SierpinskiNumber**: `Nat.IsSierpinskiNumber k := ¬ 2 ∣ k ∧ ∀ n, (k·2^n+1).Composite`
  with `Nat.Composite n := 1 < n ∧ ¬ n.Prime`. `k = 0` is excluded because
  `2 ∣ 0`, so "positive odd" is captured. All three `IsLeast` formulations
  (`78557` smallest; `271129` smallest prime; `271129` least Sierpiński number
  having a smaller Sierpiński number below it = second smallest) are faithful.
- **Taxicab**: `IsTaxicabFor'` nests the length/positivity/sum clause inside
  `L ≠ M → …`, which is degenerate for `n ≤ 1` (`S = {[]}` satisfies
  `IsTaxicabFor' k m 1 x` for every `x`) but **sound for `n = 2`**, the only
  value used, because `S.card ≥ 2` guarantees a witnessing distinct pair. The
  `List.Disjoint` requirement is a strengthening over the standard "n distinct
  ways", but for `m = 2` it exactly removes the `[a,b]`/`[b,a]` duplicate and
  costs nothing else. Soft note: `taxicab_for_5_2_n` states
  `∃ n ≥ 2, ∃ x, IsTaxicabFor 5 2 n x`, which is *logically equivalent* to
  `taxicab_for_5_2_2`, while its docstring reads as a `∀ n ≥ 2` claim.

### 2.7 UnionClosed — `.variants.cardinality_even_of_union_closed_tight` hypothesis is stronger than "tight"

```lean
@[category research open, AMS 5]
theorem union_closed.variants.cardinality_even_of_union_closed_tight
    [Nonempty n] (hA : A ≠ {∅} ∧ A ≠ ∅) (hA : IsUnionClosed A)
    (UCC_tight : ∀ i, #{x ∈ A | i ∈ x} = (1 / 2 : ℝ) * #A) : ∃ k, #A = 2 ^ k
```

`UCC_tight` demands that **every element of the ambient type `n`** lie in
exactly half the members. Two consequences the docstring ("if the UC conjecture
is tight for some family A") does not convey:

- any `i ∉ ⋃A` forces `#A = 0`, contradicting `A ≠ ∅`, so the hypothesis
  silently forces the type `n` to be finite and exactly covered by `⋃A`;
- the natural reading of "tight" (`max_i #{x ∈ A | i ∈ x} = #A/2`, i.e. equality
  in the conjecture's own bound) is strictly weaker, so the Lean theorem is a
  strictly weaker statement than Conjecture 3 of the cited NAW article.

Direction of the divergence means **no counterexample can arise from it**, and
none does: exhaustive enumeration over all `2^(2^n)` subfamilies of `P([n])`
for `n ≤ 4` finds 1, 2, 5 and 15 families satisfying the Lean hypothesis
respectively, and **every one has `#A` a power of 2**. `HOLD_BOUNDED`, bracket
`n ≥ 5`. Severity: docstring/statement fidelity only. Note the shadowed binder
`hA` (both the non-degeneracy conjunction and `IsUnionClosed A` are named `hA`).

Also recorded: the headline `union_closed` omits `A ≠ ∅`, but that is harmless —
at `A = ∅` both sides of the inequality are `0`.

### 2.8 Secondary findings on non-open declarations (out of target scope, recorded)

- **Sendov** `sendov_conjecture.variants.le_nine (hn : n ∈ Set.Icc 2 9)`,
  `@[category research solved]`. Wikipedia: *"Brown and Xiang proved the
  conjecture for n < 9 in 1999"*, i.e. **n ≤ 8**. The declaration claims the
  solved status one degree beyond its source. Not covered by any upstream
  issue/PR found.
- **SnakeInTheBox** `snake_upper_bound`, `@[category research solved]`. The
  docstring bound is `1 + 2^{n−1}·6n / (6n + n^{1/2}/(6√6) − 7)`; the Lean omits
  the `− 7`, giving a *strictly stronger* (smaller) bound than the cited one.
  (Including the `−7` would in fact make the statement false at `n = 1`, where
  the denominator goes negative — so the omission is probably deliberate, but it
  is undocumented and statement ≠ docstring.) Also `2 ^ (n - 1)` uses
  ℕ-subtraction, so `n = 0` gives `2^0 = 1`; the `n = 0` case survives only
  because Lean's `0/0 = 0`.
- **Sidorenko** `sidorenko_tree` carries `@[category research solved]` while its
  inductive step is an open `sorry` with an in-file TODO
  (`docs/PHASE2_PROOF_ROADMAP.md §6`); only the subsingleton base case is closed.

### 2.9 Certificate-incompatible, triaged out with no defect found

Sidorenko (main), Scholz (statement matches the Scholz–Brauer inequality
`ℓ(2^n−1) ≤ n−1+ℓ(n)` exactly; `additionChainLength` pinned by the file's own
proved `A003313` prefix `[0,1,2,2,3,3,4,3,4,4]`), SumOfThreeCubes,
PowerfulNumbersDensity, PrimeTriplets (the `Prime p ∧ (Prime (p+2) ∨ Prime (p+4))
∧ Prime (p+6)` set automatically consists of *consecutive* primes for `p > 3`,
since `p ≡ 1 mod 3` kills `p+2` and `p ≡ 2 mod 3` kills `p+4`, so the docstring's
"consecutive" is not lost), PrimesAndPerfectSquares, QuasiperfectNumbers
(`σ n = 2n+1`; `n = 0` gives `0 ≠ 1`, no junk witness), RamseyNumbers,
RationalDistanceProblem (`¬ Irrational d` = `d` rational, correct),
SnakeInTheBox (open decl), TwinPrimes, PebblingNumberConjecture, Mandelbrot
(the `n = 0,1` degenerate cases the docstrings claim are indeed benign:
`multibrotSet 0 = ℂ`, `multibrotSet 1 = {0}`, both locally connected with empty
or null frontier), MovingSofa, RegularPrimes, MeanValueProblem (the unused
`K : ℝ` binder is cosmetic; `c = z` closes the `p'(z) = 0` case via `0/0 = 0`,
which is the intended content), RamanujanTau (the `∏'` is multipliable in the
`WithPiTopology` — each coefficient stabilises after finitely many factors — so
`Δ` is not the junk `X`), SurjunctiveGroup, NormalityOfPi, Pell,
PierceBirkhoff, PierpontPrime, RiemannZetaValues (the `∃ x, Irrational x ∧
riemannZeta k = x` shape elaborates `x : ℝ` with a coercion, i.e. "ζ(k) is real
and irrational" — the intended statement), Schanuel, Schinzel
(`SchinzelCondition` = "for every prime `p` some `n` avoids all `f`", equivalent
to the standard fixed-divisor condition; `natAbs` only adds elements),
Singmaster, SteinerSystem, Toronto (Wikipedia: *"The Toronto space problem asks
for an uncountable Toronto Hausdorff space that is not discrete"*; the Lean's
unrestricted `∀ X` is the same statement given the known countable case),
Transcendental, VaughtConjecture, WilsonPrime, WolstenholmePrime, WoodalPrimes,
SolitaryNumber, PerfectNumbers, SquarePacking (the `n = 3` squares-in-a-circle
case is only *conjectured* optimal per Wikipedia, so `research open` is correct;
the negative-radius loophole was already fixed by #4859/#4863).

---

## HANDOFF STATE (current)

- **Triage:** complete, 51/51. Counts FIN 11 · FIN-HARD 9 · INF 26 · TERM 5.
- **Depth:** complete for the ranked head (§2.1–§2.9). Every FIN target has been
  run to a bracket; no FIN target is left unexamined.
- **Findings:**
  1. `rudins_conjecture_unique` finitely false at `N=6, q=120, a=49` —
     **DUPLICATE of open issue #4568**, stop.
  2. `wichmann_conjecture` substitutes `13 < g.length` for the source's
     "sufficiently large", with an off-by-one marks/segments justification —
     **apparently unclaimed**, faithfulness-only.
  3. `union_closed.variants.cardinality_even_of_union_closed_tight` hypothesis
     is strictly stronger than "tight" — **apparently unclaimed**,
     faithfulness-only, no counterexample (exhaustive `n ≤ 4`).
  4. `sendov_conjecture.variants.le_nine` claims degree 9 where Brown–Xiang give
     `n < 9` — **apparently unclaimed**, but the declaration is `research solved`
     (out of the open-target scope).
  5. `snake_upper_bound` omits the `− 7` of its own docstring formula —
     `research solved`, out of scope.
- **Brackets open:** `(2,5)`-perfect `n > 1.2·10⁶`; semi-magic cube roots > 200;
  Pollock/Salzer–Levine `N > 3·10⁶`; Oppermann `x > 50000`; WSS `p > 2·10⁶`;
  Rudin strong `N > 30`; union-closed tightness ground set `n ≥ 5`.
- **Not done:** no upstream issue, PR or comment was opened; no `lake build` was
  run; no `git commit` was made.
- **Re-check before any write:** duplicate surface moves hourly (KitaKen1,
  williamjblair, Terry-cyx active). Trackers #4896 / #4923 / #4927 were read at
  2026-08-15 and contain **none** of the M–Z Wikipedia filenames.
