# Wikipedia corpus scan, names A–L — open-declaration audit

## HANDOFF STATE

- **Lane**: `formal-conjectures` Wikipedia collection, open declarations whose
  file `name` starts A–L (case-insensitive). Share file:
  `results/expansion/open_targets_other_corpora_20260815.json`, `corpus=="Wikipedia"`.
- **Upstream pin**: `638da20efd8eeeed2993fc2550fc596dc90c1ce8`
  (`2026-08-15 09:23:12 +0000`, "Mark OEIS A105565 as solved (#4958)").
  All declarations read via `git show upstream/main:<path>`. Per-file blob SHAs
  recorded in the triage table.
- **Budget**: 60 s hard cap per computation (METHOD §A2.4). Timeouts are
  brackets, never holds.
- **Status**: triage complete (80/80). Depth pass complete on ranked head.
- **Nothing written upstream.** No issue, PR or comment opened.

### Candidate summary (details below)

| # | Target | Class | Status |
|---|---|---|---|
| C1 | `EllipticCurveRank.RatEllipticCurve.rank_height_count_asymptotic` | **finitely FALSE as written** (`H = 2`, any `r ∈ [1,20]`) | confirmed, 2 code paths |
| C2 | `BoundedBurnsideProblem.bounded_burnside_problem` | status mis-tag: `research open` on a 1968-settled question | confirmed |
| C3 | `HardyLittlewood.first_hardy_littlewood_conjecture` | `=O` where the docstring/source says `∼`; also missing distinctness of offsets | confirmed |
| C4 | `DedekindNumber.M_eq` | `answer(sorry)` hole closable by a witness the same file already supplies | confirmed |
| C5 | `FeitThompsonPrimeConjecture.feit_thompson_primes` | one half of the source statement (direction + `p < q`) | confirmed |
| C6 | `Koethe.KotherConjecture.variants.matrixOver_KotherRadical` | hypothesis `{I}`/`hI` unused by the conclusion | confirmed (low severity) |
| C7 | `BetrothedNumbers.same_parity_betrothed` | missing `m ≠ n`; conflates with the quasiperfect-number problem | confirmed (low severity) |
| C8 | `Dickson.polignac_conjecture` | drops "consecutive" from de Polignac | confirmed (low severity) |

Negative results (checked, no defect found) are listed at the bottom so they are
not re-worked.

---

## 1. Triage pass (METHOD §A4)

80 targets, one line each. `FIN` = a finite artifact could settle or falsify the
open declaration as written. `INC` = certificate-shape-incompatible (asymptotic /
infinitary / cardinal / real-analytic / requires an object no bounded search
reaches). `DECL` = the interesting surface is the declaration text itself
(faithfulness), independent of whether the mathematics is finite.

| # | name / blob | verdict | one-line reason |
|---|---|---|---|
| 1 | ABC `584f7ed8f07e` | INC | three `Set.Finite` statements about all coprime triples; no finite certificate either way |
| 2 | AgohGiuga `e26d7e8f20a0` | INC | `agoh_giuga` / `.variants.giuga` are ∀ over all `p ≥ 2` with Bernoulli/power-sum congruence; counterexample provably ≥ 13000 digits |
| 3 | Agrawal `e67c165f3e98` | INC | ∀ over all `(n,r)` coprime; Lenstra–Pomerance heuristic counterexamples are far out of reach |
| 4 | AlgebraicNormality `26b0bfed7f1b` | INC | normality of algebraic irrationals; real-analytic, no finite witness |
| 5 | AlmostPerfectNumbers `386be0ef02f5` | INC | `∃ n` almost perfect non-power-of-2; equivalent to a search with no known bound. Def `1 + σ n = 2n` checked: powers of 2 satisfy it, so the ∃ is non-trivial |
| 6 | AmicableNumbers `742d53acd7e6` | INC | three ∃/Infinite statements; `Even a ↔ Odd b` **is** exactly opposite parity (checked all four parity cases) — no defect |
| 7 | Andrica `179b354a3116` | INC | ∀ n inequality on √p; 0-indexing of `Nat.nth` checked correct |
| 8 | ArtinPrimitiveRootsConjecture `8088dd5616cf` | INC | four open density statements; `HasDensity` is asymptotic |
| 9 | BalancedPrimes `95c0f29b03c0` | INC | two `Set.Infinite` statements. ℕ-division `(pₙ+pₙ₊₂)/2` is exact for n ≥ 1 (both odd); n = 0 gives 7/2 = 3 = p₁ so the floor is harmless |
| 10 | BatemanHornConjecture `10af1913a99f` | INC | `~[atTop]` asymptotic |
| 11 | BealConjecture `f7171e5a6c84` | INC | ∀ over all solutions of `A^x+B^y=C^z`; no finite certificate |
| 12 | BeckFialaConjecture `a3f2fc22c341` | INC | `∃ C` universal constant over all set systems |
| 13 | BetrothedNumbers `f74baaf21ab0` | **DECL** | `same_parity_betrothed` omits `m ≠ n`, unlike the sibling `infinitely_many_betrothed` which uses `p.1 < p.2` → C7 |
| 14 | BingBorsuk `6d1207bac676` | INC | topology over all metrizable homogeneous ANRs |
| 15 | Bloch `c0f42556dbb5` | INC | exact values of the Bloch/Landau constants; real-analytic |
| 16 | BoundedBurnsideProblem `a65e2d7b6fa6` | **DECL** | tagged `research open`, but the bounded Burnside problem is settled (Novikov–Adian 1968) → C2 |
| 17 | Brennanconjecture `aef5765bbf4f` | INC | integral means spectrum; real-analytic |
| 18 | BrocardConjecture `e83f06c2bae3` | INC | ∀ n; `hn : 1 ≤ n` with 0-indexed `Nat.nth` = "n ≥ 2" 1-indexed, checked correct |
| 19 | Buchi `93cc5a20c334` | FIN (weak) | `buchi_problem_M5 : IsBuchi 5` is refutable by one integer pair `(x,a)`; searched, nothing (see §3.9) |
| 20 | Bunyakovsky `7692947227b1` | INC | infinitude of prime values. `BunyakovskyCondition` verified to include `1 ≤ degree` so no constant-polynomial loophole |
| 21 | BusyBeaver `2f9fcea33b93` | INC | `BB 6 = answer(sorry)`; the value is a well-known unknown, hole is the repo's standard "determine the value" idiom |
| 22 | CarmichaelTotient `2598d9a81866` | INC | counterexample provably ≥ 10^(10^10) (Ford) |
| 23 | Catalan `8eeb7e66d320` | INC | Pillai finiteness + Lebesgue–Nagell; ℕ-subtraction is harmless because `c > 0` forces the untruncated branch |
| 24 | CernyConjecture `f1ba46e9b04e` | INC | ∀ DFA; `card σ - 1` ℕ-subtraction only bites at `card σ = 0`, where `IsSynchronizing` is unsatisfiable |
| 25 | ClassNumberProblem `881975dfa513` | INC | `Set.Infinite` of real quadratic fields with class number one |
| 26 | CollatzConjecture `dc64f6d61029` | INC | ∀ n; faithful |
| 27 | CongruentNumber `4263fc68e738` | INC | two Tunnell converses (BSD-conditional). Missing positivity on `a,b` is harmless: `(a,b) ↦ (\|a\|,\|b\|)` preserves both clauses |
| 28 | conjecture_1_3_to_2_3 `50f3e30eae43` | INC | ∀ finite posets; the ratio is genuine ℚ division (expected type ℚ), `total_ext` is pinned to the linear extensions |
| 29 | Conway99Graph `abd92022eabc` | FIN (unreachable) | a witness is a `srg(99,14,1,2)`; search space astronomically large, finding one would be famous |
| 30 | DedekindNumber `b0a540bf7dee` | **DECL** | `M_eq : M = answer(sorry)` — the same file proves `M = kisielewiczFormula`, so the hole has a supplied closing witness → C4 |
| 31 | DeterminantalConjecture `1e1c977fbf07` | INC | convex-hull containment over all normal matrices; known for n ≤ 3 |
| 32 | DiameterSimpleFiniteGroups `fa136e65ff0b` | INC | `∃ C` polynomial/polylog diameter bounds |
| 33 | Dickson `baa7bbf5259f` | **DECL** | `polignac_conjecture` drops the "consecutive primes" clause of de Polignac → C8. Dickson itself faithful (`degree = 1 ∧ BunyakovskyCondition` ⇒ primitive linear) |
| 34 | ElliottHalberstamConjecture `9918cefc80ea` | INC | ∀θ<1 averaged error bound |
| 35 | EllipticCurveRank `63b538269af3` | **FIN** | `rank_height_count_asymptotic` asserts an exact equality for **every** `H > 1`, but `heightLE 2 = ∅` → C1 |
| 36 | ErdosMoser `06d844fd2101` | INC | counterexample provably ≥ 10^(10^9) |
| 37 | Euclid `b635df0f8d81` | INC | primality/squarefreeness of `p_n# + 1`; `Euclid n` def checked correct (`1 + ∏_{i<n} pᵢ`) |
| 38 | EulerBrick `6fe862750f7b` | **FIN** | `four_dim_euler_brick_existence` is settled by one integer 4-tuple; searched to 20000 (see §3.3) |
| 39 | EulerSumOfPowers `f555756690cb` | INC | `k ≥ 6` case; no counterexample known, search space huge |
| 40 | Exponentials `98f53a6305de` | INC | transcendence |
| 41 | FactorialPrime `46a394021071` | INC | `Set.Infinite`; def avoids ℕ-subtraction via `n! = p + 1` ✔ |
| 42 | FeitThompsonPrimeConjecture `923cea516d71` | **DECL** | asserts only one of the two ordered directions Wikipedia quantifies over → C5 |
| 43 | Fermat `3ca015d4f658` | INC | four Fermat-number questions; all four are exactly Wikipedia's "Open questions" list |
| 44 | FermatCatalanConjecture `1c84be41b9f8` | INC | `Set.Finite`; image-set construction correctly implements "distinct triplets of values" |
| 45 | FibonacciPrimes `e19501750d05` | INC | `Set.Infinite` |
| 46 | Firoozbakht `d7a383868718` | INC | ∀ n; indexing checked (`firoozbakhtSeq n = p_{n+1}^{1/(n+1)}` 1-indexed) |
| 47 | FlintCooksonHills `c348671456d0` | INC | `Summable`; terms are positive so Mathlib's absolute `Summable` is not a trap here |
| 48 | FortuneConjecture `b47b4a64f311` | FIN (unreachable) | one composite Fortunate number would settle it; extensively searched in the literature |
| 49 | Fuglede `99d0ce2a1879` | INC | measure-theoretic spectral sets in ℝ¹/ℝ² |
| 50 | GapConjecture `b833a7c165ae` | INC | growth asymptotics |
| 51 | GaussCircleProblem `544850589d84` | INC | `=O` with an `o(1)` exponent; verified equivalent to `limsup log\|E\|/log r ≤ 1/2` |
| 52 | Gilbreath `1a0729ab41f8` | FIN (unreachable) | `d k 0 = 1` for one `k` would refute; `Int.natAbs` coercion is genuine (not ℕ-truncated). Verified for k ≤ 5000 (§3.10) |
| 53 | GoldbachConjecture `08feda554254` | INC | ∀ even n |
| 54 | Goormaghtigh `807537c74b7a` | FIN (unreachable) | one third repunit coincidence refutes; verified none to 10^13 (§3.10) |
| 55 | GracefulLabeling `0de8bcd4e17e` | FIN (unreachable) | one non-graceful tree refutes; verified to ~35 vertices in the literature. Finset-image encoding is sound (card forces injectivity) |
| 56 | Grimm `aa697e2849e2` | FIN (unreachable) | one bad run of composites refutes; verified far beyond reach |
| 57 | Hadamard `180b7a22d9ae` | FIN (unreachable) | `«167»` needs an explicit 668×668 Hadamard matrix — that is the open problem itself |
| 58 | Hall `8393f34b1fe0` | INC | `∃ C` over all `(x,y)`; x = 0 edge case checked benign (`0^(1/2) = 0`) |
| 59 | HardyLittlewood `1f4439a73541` | **DECL** | `=O` where the docstring says `∼`; and offsets `m` are not required distinct → C3 |
| 60 | IdonealCompleteness `bed775bd6882` | **FIN** | one `n ∉ knownIdonealNumbers` with no `ab+bc+ca` representation refutes; searched to 10^6 (§3.6) |
| 61 | InscribedSquare `d928c7eb85ec` | INC | Jordan curves; `IsRectangle` with `ratio 1` |
| 62 | InvariantSubspaceProblem `ccd6415b1d4e` | INC | separable Hilbert space operators |
| 63 | InverseGalois `ec5611e8d8e4` | FIN (unreachable) | a witness is a Galois realization over ℚ; not a bounded search |
| 64 | Irrational `afd6f7a8d7a2` | INC | nine irrationality/algebraic-independence questions |
| 65 | JacobianConjecture `a3c471555a2b` | INC | the open one is the 2-variable case over all char-0 fields |
| 66 | JugglerConjecture `aac98059e739` | INC | ∀ n; rpow-floor step function faithful |
| 67 | Kakeya `454d93aa5af2` | INC | Hausdorff dimension |
| 68 | Kaplansky `305c8d2fc403` | INC | group-algebra statements over all torsion-free groups |
| 69 | Koethe `9e7494604f4c` | **DECL** | `matrixOver_KotherRadical` carries an unused hypothesis pair `{I}`/`hI` → C6 |
| 70 | KomlosConjecture `cd17e10dde4c` | INC | `∃ K` universal constant |
| 71 | KummerVandiver `efde8b36bd17` | FIN (unreachable) | one prime `p` with `p ∣ h⁺` refutes; verified past 2·10^9 in the literature |
| 72 | LanderParkinAndSelfridgeConjecture `355dbcaf8b51` | INC | ∀ k,n,m; the `n+m ≤ 3` cases collapse to FLT so no cheap witness |
| 73 | LegendreConjecture `9295ed4ece2a` | FIN (unreachable) | one prime-free square interval refutes; verified far beyond reach |
| 74 | LehmerMahlerMeasureProblem `3dbb26ea352c` | INC | `∃ μ` over all of ℤ[X]. `∃ μ, ∀ f, μ > 1 ∧ …` is equivalent to `∃ μ > 1, ∀ f, …` (ℤ[X] nonempty) — ugly, not wrong |
| 75 | LehmerTotient `c149ba84ba9c` | FIN (unreachable) | one composite `n` with `φ(n) ∣ n−1` settles it; verified past 10^30 |
| 76 | LeinsterGroup `c6e37b9af421` | INC | unboundedness of Leinster-group orders; entangled with infinitude of perfect numbers |
| 77 | Lemoine `e7346fd76454` | FIN (unreachable) | one odd `n` with no `p+2q` refutes; verified far beyond reach |
| 78 | LittlewoodConjecture `aa66c7f9c855` | INC | `liminf` |
| 79 | LonelyRunnerConjecture `a47a8b42132a` | INC | ∀ real speed tuples; `1/n` is real division, `n ≤ 1` edge cases benign |
| 80 | LychrelNumbers `9d125a117636` | FIN (unreachable) | `IsLychrel10 196` — the open case itself; the *docstring* mis-states the community's expected direction (noted, §3.11) |

**Counts.** 80 triaged. `FIN` 13 (of which 3 reachable: EllipticCurveRank,
EulerBrick 4-D, Idoneal; 10 unreachable-in-practice). `INC` 59.
`DECL`-flagged (faithfulness surface) 8. Depth was spent on the 8 `DECL` targets
plus the 3 reachable `FIN` targets.

---

*(depth sections appended below, one per target, as they complete)*
