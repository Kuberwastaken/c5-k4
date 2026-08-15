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
- **Status**: triage complete (80/80). Depth pass complete on the ranked head
  (8 faithfulness targets + 3 reachable finite targets). Lane finished.
- **Blob re-pin, 2026-08-15T21:48Z**: `upstream/main` unchanged at `638da20e`; all
  six candidate-file blobs re-verified identical to the values recorded in §1.
- **Duplicate re-check, 2026-08-15T21:48Z** (surface moves in hours — KitaKen1 /
  williamjblair active): `gh` search on `rank_height_count_asymptotic`,
  `twentyone_le_rank`, `FirstHardyLittlewoodConjectureFor`, `M_eq_kisielewiczFormula`,
  `matrixOver_KotherRadical`, `same_parity_betrothed`, `polignac_conjecture`,
  `four_dim_euler_brick_existence` → **0 hits each**; `idoneal_numbers_completeness`
  → #4314 (closed, unrelated: proving `knownIdonealNumbers_are_idoneal`). The newest
  20 issues/PRs (#4982–#4993, created since 2026-08-14) are all Erdős/OEIS — no
  Wikipedia-collection entry. **Re-run this check immediately before any write.**
- **Nothing written upstream.** No issue, PR or comment opened. `lake build` not run;
  no `git commit` from this lane.
- **Next action if resumed**: C1 is release-shaped (finite witness, two code paths,
  novel, strong provenance). C3/C4/C6/C7/C8 are issue-shaped faithfulness reports.
  C2 is dead (claimed by #4518/#4519).

### Candidate summary (details below)

| # | Target | Class (METHOD §A6) | Duplicate status |
|---|---|---|---|
| **C1** | `EllipticCurveRank.RatEllipticCurve.rank_height_count_asymptotic` | **formalization counterexample** — declaration is finitely FALSE (`H = 2`, every `r ∈ [1,20]`); underlying PPVW heuristic untouched | **novel** (0 hits) |
| C2 | `BoundedBurnsideProblem.bounded_burnside_problem` | status mis-tag: `research open` on a 1968-settled question | **DUPLICATE** — issue #4518 + PR #4519, both open since 2026-07-21 |
| C3 | `HardyLittlewood.first_hardy_littlewood_conjecture` | declaration weaker than source: `=O` where Wikipedia writes `∼`; plus offsets not required distinct | **novel** (0 hits) |
| C4 | `DedekindNumber.M_eq` | `answer(sorry)` hole closed by a witness the *same PR* added one declaration above | **partially claimed** — issue #3490 (CLOSED) raised the concern; the fix PR #3895 left the hole and supplied the witness |
| C5 | `FeitThompsonPrimeConjecture.feit_thompson_primes` | **REFUTED** — see §4.1, the omitted half is trivial by size | n/a |
| C6 | `Koethe.KotherConjecture.variants.matrixOver_KotherRadical` | spurious (unused, satisfiable) hypothesis `{I}`/`hI` + garbled docstring | **novel** (0 hits) |
| C7 | `BetrothedNumbers.same_parity_betrothed` | missing `m ≠ n`; satisfiable by a quasiperfect number, a *different* open problem | **novel** (0 hits) |
| C8 | `Dickson.polignac_conjecture` | drops "consecutive" from de Polignac; `k = 0` instance is Euclid's theorem | **novel for this declaration**; adjacent WIP issue #4673 |

Negative results (checked, no defect found) are in §4 so they are not re-worked.

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
| 38 | EulerBrick `6fe862750f7b` | **FIN** | `four_dim_euler_brick_existence` is settled by one integer 4-tuple; searched exhaustively to 10^5 (see §3.3) |
| 39 | EulerSumOfPowers `f555756690cb` | INC | `k ≥ 6` case; no counterexample known, search space huge |
| 40 | Exponentials `98f53a6305de` | INC | transcendence |
| 41 | FactorialPrime `46a394021071` | INC | `Set.Infinite`; def avoids ℕ-subtraction via `n! = p + 1` ✔ |
| 42 | FeitThompsonPrimeConjecture `923cea516d71` | ~~DECL~~ | flagged (one of two ordered directions vs Wikipedia) then **REFUTED** in §4.1 — the omitted half is trivial by size |
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
`DECL`-flagged (faithfulness surface) 8 at triage, of which 7 survived depth
(C5 refuted in §4.1). Depth was spent on the 8 `DECL` targets plus the 3 reachable
`FIN` targets.

---

## 2. Depth — confirmed candidates

### C1 — `EllipticCurveRank.RatEllipticCurve.rank_height_count_asymptotic` is FALSE as written

**File** `FormalConjectures/Wikipedia/EllipticCurveRank.lean`, blob `63b538269af3`.
**Declaration, verbatim:**

```lean
/-- [PPVW2016] 8.2(b): for 1 ≤ r ≤ 20, the number of elliptic curves over ℚ with rank `r` and
naïve height at most `H` is asymptotically `H ^ ((21 - r) / 24 + o(1))`. … -/
@[category research open, AMS 11 14]
theorem rank_height_count_asymptotic (r : ℕ) (h₁ : 1 ≤ r) (h₂ : r ≤ 20) :
    ∃ f : ℕ → ℝ, atTop.Tendsto f (𝓝 0) ∧
      ∀ H : ℕ, 1 < H → {E ∈ heightLE H | r ≤ E.rank}.ncard = (H : ℝ) ^ ((21 - r) / 24 + f H) := by
  sorry
```

Supporting definitions in the same file:

```lean
structure RatEllipticCurve : Type where
  A : ℤ
  B : ℤ
  reduced (p : ℕ) : p.Prime → ¬ ((p ^ 4 : ℤ) ∣ A ∧ (p ^ 6 : ℤ) ∣ B)
  Δ_ne_zero : 4 * A ^ 3 + 27 * B ^ 2 ≠ 0

def naiveHeight (E : RatEllipticCurve) : ℕ := max (4 * E.A.natAbs ^ 3) (27 * E.B.natAbs ^ 2)
def heightLE (H : ℕ) : Set RatEllipticCurve := {E : RatEllipticCurve | E.naiveHeight ≤ H}
```

**The defect.** The statement asserts an *exact equality* for **every** `H > 1`, not
an asymptotic. But `heightLE H` is empty for `H ≤ 3`:

- `naiveHeight E ≤ 3` forces `4·|A|³ ≤ 3` and `27·B² ≤ 3`, hence `A = 0` and `B = 0`;
- `(A, B) = (0, 0)` is excluded twice over — by `Δ_ne_zero` (`4·0 + 27·0 = 0`) and by
  `reduced` (every prime `p` has `p⁴ ∣ 0` and `p⁶ ∣ 0`).

So `{E ∈ heightLE 2 | r ≤ E.rank} = ∅` and its `ncard` is `0`.
The right-hand side is `Real.rpow`: the exponent is `(21 - r)/24 + f H : ℝ` because
`f : ℕ → ℝ`, so `(2 : ℝ) ^ (…)` is `Real.rpow 2 (…) > 0` for *every* real exponent
(`Real.rpow_pos_of_pos`, base `2 > 0`). Therefore `0 = (2:ℝ)^(…)` is false **for every
choice of `f`**, so the `∃ f` cannot be satisfied.

**Witness (minimal).** `H = 2`, any `r` with `1 ≤ r ≤ 20`. `H = 3` works identically.

**Two independent code paths** (`scratchpad/wiki/comp1.py`, `comp5.py`):

| path | method | result |
|---|---|---|
| A | brute-force enumeration of all `(A,B) ∈ [-10,10]²` applying `Δ_ne_zero`, `reduced` and `naiveHeight ≤ H` | `\|heightLE H\| = 0` for `H = 0,1,2,3`; first non-empty is `H = 4` with `{(1,0), (-1,0)}` |
| B | interval argument on `max(4\|A\|³, 27B²) ≤ 3` alone, then the two exclusion clauses | only candidate `(0,0)`; excluded by both `Δ_ne_zero` and `reduced` |

Both also confirm `heightLE H = {(±1, 0)}` for `4 ≤ H ≤ 26` (curves `y² = x³ ± x`,
both of rank 0), so the filtered set stays empty for `r ≥ 1` well past `H = 4`; the
`H = 2` witness is chosen because it needs no rank computation at all.

**Provenance — the guard was added deliberately and stops one step short.** PR
[#252](https://github.com/google-deepmind/formal-conjectures/pull/252),
titled *"fix(EllipticCurveRank): corner cases and a sanity check"*, rewrote exactly
this declaration:

```diff
-    ∃ f : ℕ+ → ℝ, atTop.Tendsto f (𝓝 0) ∧
-      ∀ H : ℕ+, {E ∈ heightLE H | r ≤ E.rank}.ncard = (H : ℝ) ^ ((21 - r) / 24 + f H)
+    ∃ f : ℕ → ℝ, atTop.Tendsto f (𝓝 0) ∧
+      ∀ H : ℕ, 1 < H → {E ∈ heightLE H | r ≤ E.rank}.ncard = (H : ℝ) ^ ((21 - r) / 24 + f H)
```

The `1 < H` guard was introduced *to handle this class of corner case* (at `H = 1`,
`(1:ℝ)^x = 1 ≠ 0`), but the set is empty until `H = 4`, so `H = 2, 3` remain. The
sibling declaration `twentyone_le_rank_height_count_asymptotic`, edited in the same
diff, uses `≤` instead of `=` and is therefore immune (`0 ≤` positive).

**Classification (METHOD §A6).** (1) the PPVW 8.2(b) heuristic is untouched; (2) no
formal solution exists; (3) the declaration is unfaithful to its source — the source
is an asymptotic, the Lean is a pointwise identity starting at `H = 2`; (4) the
declaration literally asserts something false. This is a **formalization
counterexample**, explicitly *not* a claim about elliptic-curve rank distributions.

**Suggested repair** (not filed): guard with `∀ᶠ H in atTop` (or `∃ H₀, ∀ H ≥ H₀`)
instead of `1 < H`, matching the `o(1)` in the docstring.

**Duplicate check, 2026-08-15.** `gh` issue+PR search for `rank_height_count_asymptotic`
→ 0 hits. `heightLE` → 1 hit, PR #252 (above, does not report the residual defect).
`EllipticCurveRank` → issues #3596 (missing docstrings), #4685 (Millennium WIP); PRs
#4422, #4355, #3536, #252, #3125, #2601, #3532 — none touching this. Absent from
trackers #4896, #4923, #4927. Full open-issue title sweep (722 open issues,
295 open PRs) shows no elliptic-curve entry. **Novel.**

---

### C2 — `BoundedBurnsideProblem.bounded_burnside_problem` — DUPLICATE, already claimed

```lean
@[category research open, AMS 20]
theorem bounded_burnside_problem :
    answer(sorry) ↔ ∀ (G : Type) [Group G] (fin_gen : Group.FG G)
      (n : ℕ) (hn : n > 0) (bounded : ∀ g : G, g^n = 1), Finite G := by
  sorry
```

The universal proposition on the right has been known to be **false** since
Novikov–Adian (1968): Wikipedia's cited section states *"for every odd number n with
n > 4381, there exist infinite, finitely generated groups of exponent n"*, and Adian
later reduced the bound to 665. The correct shape is the one the repo already uses in
`Fuglede.variants.dim_3_or_higher` (`answer(False)` + `research solved`).

**Duplicate status: CLAIMED.** Issue
[#4518](https://github.com/google-deepmind/formal-conjectures/issues/4518)
*"Wikipedia/BoundedBurnsideProblem: record the known negative answer"* (opened
2026-07-21, still open) quotes the identical declaration and proposes exactly
`answer(False)` + `research solved`; PR
[#4519](https://github.com/google-deepmind/formal-conjectures/pull/4519) implements it
and is still open. **Stop — no independent artifact available here.** Recorded so the
lane does not re-derive it.

---

### C3 — `HardyLittlewood.first_hardy_littlewood_conjecture` states `=O` where the source states `∼`

**File** `FormalConjectures/Wikipedia/HardyLittlewood.lean`, blob `1f4439a73541`.

```lean
def FirstHardyLittlewoodConjectureFor {k : ℕ} (m : Fin k.succ → ℕ) : Prop :=
  let C : ℝ :=
      2 ^ k * ∏' (q : { q : ℕ // q.Prime ∧ 3 ≤ q}),
        (1 - (Nat.numResidues q m : ℝ) / q) / (1 - 1 / q) ^ k.succ
    let π_P : ℕ → ℝ := fun n => (Nat.primeTupleCounting m n : ℝ)
    π_P =O[atTop] fun n => C * ∫ t in (2)..n, 1 / t.log ^ k.succ
```

whose own docstring ends

> Then $\pi_P(n)\sim C_P\int_2^n\frac{dt}{\log^{k+1}t}$.

and Wikipedia's *First Hardy–Littlewood conjecture* states, verbatim, the asymptotic
relation `π_P(n) ∼ C_P ∫₂ⁿ dt/log^{k+1} t` with
`C_P = 2^k ∏_{q ≥ 3 prime} [1 − w(q; m₁,…,m_k)/q] / [(1 − 1/q)^(k+1)]`.

**Defect 1 — `∼` replaced by `=O`.** `f =O[atTop] g` is a one-sided bound with an
arbitrary implied constant; `f ∼ g` is `f/g → 1`. The Lean therefore drops the entire
main-term content of the conjecture. Worse, for the intended inputs the surviving
half is a *classical theorem*: for a fixed admissible tuple with distinct offsets the
Brun/Selberg sieve gives `π_P(n) ≪_k 𝔖 · n/(log n)^{k+1}`, and `=O` permits any
constant. So the declaration retains only a provable upper bound, not the open
conjecture.

**The constant itself is right** — independently checked. For the twin tuple
`m = ![0,1]` (`k = 1`, `w(q) = 2` for `q ≥ 3`) the Lean's `C` evaluates to

```
2^1 · ∏_{3 ≤ q < 2·10⁶} (1 − 2/q)/(1 − 1/q)²  =  1.320324
2·C₂ (twin prime constant)                     =  1.320323632…
```

The `2^k` prefactor is exactly the missing `q = 2` Euler factor
`(1 − w(2)/2)/(1 − 1/2)^{k+1} = 2^k` (all offsets `2·m i` are even, so `w(2) = 1`),
and using residues of `m i` rather than `2·m i` is harmless because `×2` is a
bijection mod every odd `q`. No defect in `C`.

**Defect 2 — offsets are not required distinct.** The declaration is `∀ m`, and `m`
may repeat: `k = 2`, `m = ![0, 1, 1]` satisfies `m 0 = 0` and `∀ i ≠ 0, 0 < m i`. Then

- `IsPrimeConstellation m p ⟺ p` and `p+2` both prime; admissibility holds for every
  `q` (the range has ≤ 2 elements), so `π_P(n) = π₂(n)`, the twin-prime count;
- `Nat.numResidues q m = |{0,1}| = 2` for `q ≥ 3`, so each Euler factor is
  `(q−2)q²/(q−1)³ = 1 + (q²−3q+1)/(q−1)³ ≈ 1 + 1/q`;
- the product therefore **diverges**: partial products over `3 ≤ q ≤ Q` are
  `1.628 (Q=10)`, `2.776 (10²)`, `4.081 (10³)`, `5.422 (10⁴)`, `6.771 (10⁵)`,
  `8.122 (10⁶)` — so the family is not `Multipliable` in ℝ and Mathlib's `tprod`
  returns its junk value `1`, giving `C = 2² · 1 = 4`;
- the RHS is then `≍ n/(log n)³` while `π₂(n) ≍ n/(log n)²` under the twin-prime
  conjecture, so `π_P =O[atTop] RHS` **fails**.

This is a *conditional* falsity (it needs a lower bound on twin primes, which is
itself open), so it is recorded as a hypothesis gap — the source's `m_i` are the
offsets of a constellation and are implicitly distinct — not as a counterexample.

**Classification.** Defect 1 is a clean (3)/(4) divergence: the declaration says
something strictly weaker than, and provable independently of, the conjecture it
names. Defect 2 is a missing non-degeneracy hypothesis (METHOD §A3.1 shape).

**Duplicate check, 2026-08-15.** `gh` content search `hardy littlewood` → #4990,
#136, #104, #4724, #1248, #195, #2492, #1772 — none about `=O` vs `∼` in this file
(#2492 is the solved Richards incompatibility). `FirstHardyLittlewood` → 0 hits.
Absent from #4896/#4923/#4927. File `git log` shows no statement-level edit since
creation (only docstring/space/classical-reasoning chores). **Novel.**

---

### C4 — `DedekindNumber.M_eq`: the fix PR supplied the witness that closes the hole

```lean
/-- Kisielewicz (1988) proved the following arithmetic formula … -/
@[category research solved, AMS 5 6]
theorem M_eq_kisielewiczFormula : M = kisielewiczFormula := by
  sorry

/--
  No closed-form expression that allows efficient computation of Dedekind numbers is
  currently known.
-/
@[category research open, AMS 5 6]
theorem M_eq : M = answer(sorry) := by
  sorry
```

`M_eq` is closed by `answer := M` (`rfl`), and — more pointedly — by
`answer := kisielewiczFormula`, at which point `M_eq` **is literally the statement of
`M_eq_kisielewiczFormula`, the `research solved` declaration immediately above it in
the same file**. The docstring's actual content ("no *efficiently computable* closed
form") is not expressible as an equation and is not captured by the declaration at all.

**Provenance.** Issue
[#3490](https://github.com/google-deepmind/formal-conjectures/issues/3490)
*"Dedekind Numbers Closed Form"* (2026-03-09, closed 2026-04-29) raised precisely this:
*"This makes me wonder if the Dedekind Numbers aren't just trivially solvable anyway,
at least when formalized with answer(sorry), as one can just provide the arithmetic
formula expression for n = 10 with a proof that it equals M(10)."* Commenter
`franzhusch` reinforced it. The resolving PR
[#3895](https://github.com/google-deepmind/formal-conjectures/pull/3895) — diff read in
full — **renamed** `DedekindNumbers` to `M_eq`, reworded the docstring, and *added*
`kisielewiczFormula` together with `M_eq_kisielewiczFormula`. The `answer(sorry)` hole
survived, and the same PR put the closing witness one declaration above it.

`Dedekind_10 : M 10 = answer(sorry)` is the repo's standard "determine the value"
idiom and is **not** flagged: its answer is a genuinely unknown constant.

**Classification.** (4)-only: the declaration asserts something trivially true; the
mathematics (the value of `M(10)`) is untouched.

**Duplicate status: PARTIALLY CLAIMED.** #3490 and #3513 are closed; the residual
defect in `M_eq` is not tracked, and Dedekind appears in neither the "Exact
self-answers" nor "Reflexive asymptotic answers" section of #4923, nor in "Already
implied in the repository" in #4927 — where it belongs alongside Green 19.

---

### C6 — `Koethe.KotherConjecture.variants.matrixOver_KotherRadical`: spurious hypothesis + wrong docstring

```lean
open scoped Classical in
/-- The **Köthe conjecture**: for any positive integer `n`, the Köthe radical of `R` is the matrix ideal `M_2(Nil*(R))`. -/
@[category research open, AMS 16]
theorem KotherConjecture.variants.matrixOver_KotherRadical
    {I : TwoSidedIdeal R} (hI : IsNil I) (n : Type*) [Fintype n] :
    matrix n (Nil* R) = Nil* (Matrix n n R) := by
  sorry
```

- `I` and `hI` **do not occur in the conclusion**. `I` is implicit and unconstrained,
  so it can only ever be supplied by hand. The hypothesis is *satisfiable*
  (`I = ⊥` is nil), so this is a spurious hypothesis, not a vacuity — the declaration
  is logically equivalent to the hypothesis-free version. Severity: low.
- The docstring is garbled twice: it writes "the Köthe radical of `R`" where the code
  (correctly) says `Nil*(M_n(R))`, and "`M_2`" where the code uses an arbitrary
  `Fintype n`. Wikipedia's equivalent formulation 6 reads *"For any ring R, the upper
  nilradical of M_n(R) is the set of matrices with entries from the upper nilradical
  of R for every positive integer n"* — which the **code** matches exactly.
- `n : Type*` `[Fintype n]` admits `n = Empty`; both sides then live in the trivial
  ring and are equal, so no degeneracy.

The sibling declarations `.general_matrix` and `.two_by_two_matrix` do use `hI`
correctly.

**Duplicate check.** `matrixOver_KotherRadical` → 0 issue/PR hits; `Kothe`/`Koethe` →
#202 (tracking list), #2994 (solved Amitsur). `git log` on the file shows only
formatting/chore commits since creation. **Novel.**

---

### C7 — `BetrothedNumbers.same_parity_betrothed` omits `m ≠ n`

```lean
@[mk_iff]
structure IsBetrothed (m n : ℕ) : Prop where
  left  : σ 1 m = m + n + 1
  right : σ 1 n = m + n + 1

/-- **Same parity betrothed numbers conjecture.** Do there exist betrothed numbers
$(m, n)$ where both have the same parity …? -/
@[category research open, AMS 11]
theorem same_parity_betrothed :
    answer(sorry) ↔ ∃ m n : ℕ, IsBetrothed m n ∧ (Even m ↔ Even n) := by
  sorry
```

Taking `m = n` gives `IsBetrothed n n ⟺ σ(n) = 2n + 1` — the definition of a
**quasiperfect number** — and `Even n ↔ Even n` is trivially true. So the declaration
is satisfied by any quasiperfect number, which is a *different* open problem (none is
known; any quasiperfect number is an odd square exceeding 10³⁵), whereas Wikipedia's
open question is about betrothed **pairs**: *"All known pairs of betrothed numbers have
opposite parity. Any pair of the same parity must exceed 10¹³."*

The sibling declaration in the same file does enforce distinctness
(`{p : ℕ × ℕ | p.1 < p.2 ∧ IsBetrothed p.1 p.2}`), which is direct evidence the
omission is unintentional.

**Computation** (`σ` sieve to `5·10⁶`, 22.8 s, within cap): no `n ≤ 5·10⁶` with
`σ(n) = 2n+1`; 35 betrothed pairs `m < n ≤ 5·10⁶` — `(48,75), (140,195), (1050,1925),
(1575,1648), (2024,2295), (5775,6128), (8892,16587), (9504,20735), (62744,75495),
(186615,206504), …` — **all of opposite parity**, matching the literature. So no
finite witness either way; the defect is that the two open problems are conflated.

**Duplicate check.** `betrothed` → #2246, #2243 (the feature request that created this
declaration), #2264 (its PR); all closed, none reporting the missing `m ≠ n`. **Novel.**

---

### C8 — `Dickson.polignac_conjecture` is not de Polignac's conjecture

```lean
/--
**Polignac's conjecture**
For any integer $k$ there are infinitely many primes $p$ such that $p + 2k$ is prime.
-/
@[category research open, AMS 11]
theorem polignac_conjecture (k : ℕ) :
    Infinite {p : ℕ | p.Prime ∧ (p + 2 * k).Prime} := by
  sorry
```

Wikipedia: *"For any positive even number n, there are infinitely many prime gaps of
size n. In other words: There are infinitely many cases of two **consecutive** prime
numbers with difference n."* (the 1849 source: *"la différence de deux nombres premiers
**consécutifs**"*).

Two divergences:

1. **"consecutive" is dropped.** The Lean statement is the generalised twin-prime
   statement (`p` and `p+2k` both prime), which is strictly weaker than de Polignac and
   is what actually follows from Dickson's conjecture — the file's own framing ("Special
   cases" of Dickson). The name and docstring nevertheless claim de Polignac.
2. **`k = 0` is admitted**, where the statement degenerates to
   `Infinite {p | p.Prime ∧ p.Prime}` = the infinitude of primes, a theorem. The source
   requires `n` a *positive* even number.

Both are declaration-level; nothing about the mathematics is claimed. A one-token
repair for (2) is `(k : ℕ) (hk : 0 < k)`; (1) needs the consecutiveness clause or a
rename to the generalised-twin-prime statement.

**Duplicate check.** `Polignac` → issue #4673 (OPEN, WIP: *"Polignac's conjecture
(consecutive prime gaps)"* — a contributor is preparing a separate, consecutive-aware
formalization) and PR #4684 (closed). Neither reports the defect in the *existing*
`Dickson.polignac_conjecture`. **Novel for this declaration, adjacent work in flight —
re-check before any write.**

---

## 3. Depth — finite checks that closed with no defect (brackets)

### 3.3 `EulerBrick.four_dim_euler_brick_existence` — no 4-D Euler brick to 10⁵

```lean
def IsEulerHyperBrick (n : ℕ) (sides : Fin n → ℕ+) : Prop :=
  Pairwise fun i j ↦ IsSquare ((sides i)^2 + (sides j)^2)

@[category research open, AMS 11]
theorem four_dim_euler_brick_existence :
    answer(sorry) ↔ ∃ sides : Fin 4 → ℕ+, IsEulerHyperBrick 4 sides := by sorry
```

A witness is four positive integers whose six pairwise sums of squares are all squares
— i.e. a `K₄` in the "Pythagorean pair" graph. Searched exhaustively:

| bound on sides | `K₃` (3-D Euler bricks) | `K₄` (4-D) | time |
|---|---|---|---|
| 4 000 | 54 | **0** | 0.0 s |
| 20 000 | 320 | **0** | 0.0 s |
| 100 000 | 1 714 | **0** | 0.3 s |

Second code path: the fast generator (primitive triples `(m²−n², 2mn)` scaled) was
verified **edge-for-edge identical** to an `O(N²) isqrt` brute force at `N = 2000`, and
its `K₃` count at `N = 4000` (54) matches the brute-force count from the independent
first script. Smallest `K₃` reproduced as `(44, 117, 240)`, the classical Euler brick.

`HOLD_BOUNDED`, bracket at `min side > 100 000`. Note Wikipedia's *Euler brick* article
— the declaration's cited reference — contains **no** higher-dimensional material at
all; the file's only support for the 4-D and `n`-D declarations is a
math.stackexchange link. Recorded as a weak sourcing observation, not a defect.

### 3.6 `Idoneal.idoneal_numbers_completeness` — the 65-number list is exactly right to 10⁶

```lean
def IsIdoneal (n : ℕ) : Prop :=
  0 < n ∧ ¬ ∃ a b c : ℕ, 0 < a ∧ a < b ∧ b < c ∧ n = a * b + b * c + a * c
@[category research open, AMS 11]
theorem idoneal_numbers_completeness :
    answer(sorry) ↔ ∀ n : ℕ, IsIdoneal n → n ∈ knownIdonealNumbers := by sorry
```

Sieved all `n` not representable as `ab + bc + ca` with `0 < a < b < c`:

- `n ≤ 10⁵`: 65 non-representable values, **set-equal** to `knownIdonealNumbers`
  (2.4 s, within cap). 0 extra, 0 missing.
- `n ≤ 10⁶`: still exactly 65, still set-equal (79.9 s — **over the 60 s cap**, so
  recorded as an over-budget extension, not as in-budget evidence).

No finite counterexample; the encoding is faithful. `HOLD_BOUNDED`, bracket at
`n > 10⁵` (in-budget) / `n > 10⁶` (over-budget).

### 3.9 `Buchi.buchi_problem_M5` — no non-trivial length-5 Büchi sequence in the searched box

`IsBuchi 5` fails iff some `(x, a) ∈ ℤ²` with `a ≠ 0` makes `(x+n)² + a` a square for
`n = 0,…,4`. Parametrising `a = z₀² − x²`, searched `x ∈ [−3000, 3000]`,
`z₀ ∈ [0, 6000]`: **0 solutions** (22.9 s). The file's own `¬IsBuchi 4` witness
`(x, a) = (246, −60480)` lies inside this box and was re-derived by the same code
(`6², 23², 32², 39²`), confirming the search is correctly wired. `HOLD_BOUNDED`.

### 3.10 Gilbreath and Goormaghtigh brackets

- `Gilbreath.gilbreath_conjecture (k : ℕ+) : d k 0 = 1` — verified `d^k(0) = 1` for
  **all `k = 1..5000`** (1.1 s). The Lean recursion coerces into ℤ before `Int.natAbs`,
  so it is a genuine absolute difference, not ℕ-truncated subtraction. `HOLD_BOUNDED`.
- `Goormaghtigh.goormaghtigh_conjecture` — enumerated every repunit with ≥ 3 digits in
  every base ≥ 2 up to `10¹³`: the **only** two values with representations in two
  distinct bases are `31 = 11111₂ = 111₅` and `8191 = 1111111111111₂ = 111₉₀` (2.3 s),
  exactly the declaration's conclusion. `HOLD_BOUNDED`, bracket at `N > 10¹³`.

### 3.11 `LychrelNumbers` — docstring direction (recorded, not a declaration defect)

The module docstring says *"One commonly stated conjectural direction is that there are
no Lychrel numbers in base 10."* Wikipedia's article states the opposite expectation:
no Lychrel number has been *proved* to exist, but 196 and others are *believed* to be
Lychrel. Because both declarations are `answer(sorry) ↔ P` (questions, not assertions),
the declarations themselves are unaffected; only the prose misleads. Not raised as a
candidate.

---

## 4. Refuted candidates (checked, no defect — do not re-raise)

### 4.1 `FeitThompsonPrimeConjecture.feit_thompson_primes` — the restriction is harmless

```lean
theorem feit_thompson_primes (p q : ℕ) (hp : p.Prime) (hq : q.Prime) (h : p < q) :
    ¬ (q ^ p - 1) / (q - 1) ∣ (p ^ q - 1) / (p - 1)
```

Wikipedia quantifies over *all* distinct primes and asserts
`¬ ((p^q − 1)/(p − 1) ∣ (q^p − 1)/(q − 1))`, i.e. **both** ordered directions per
unordered pair. The Lean fixes `p < q` and asserts only one of them. The omitted
direction is trivially true: writing `A_{x,y} = (x^y − 1)/(x − 1)`, for `2 ≤ p < q` we
have `(q−1)/log q > (p−1)/log p` (the map `x ↦ (x−1)/log x` is increasing on `[2,∞)`),
hence `p^{q−1} > q^{p−1}` and therefore `A_{p,q} > A_{q,p} > 0`, so a divisibility
`A_{p,q} ∣ A_{q,p}` is impossible for size reasons. The Lean thus keeps exactly the
non-trivial half (`smaller ∤ larger`; e.g. `p=2, q=3` gives `¬(4 ∣ 7)`). ℕ-division is
exact on both sides (`x − 1 ∣ x^y − 1`). **No defect.**

### 4.2 Other checks that came back clean

- **`AmicableNumbers.opposite_parity_amicable`** — `Even a ↔ Odd b` is exactly
  "opposite parity" (all four parity cases enumerated), and opposite parity already
  forces `a ≠ b`. No missing-hypothesis defect.
- **`BalancedPrimes.balanced_primes`** — `(pₙ + pₙ₊₂) / 2` is ℕ-division, but for
  `n ≥ 1` both primes are odd so the sum is even and the division exact; at `n = 0` the
  floor `7/2 = 3` coincidentally equals `p₁`. No defect.
- **`BrocardConjecture`** — `hn : 1 ≤ n` with 0-indexed `Nat.nth` corresponds exactly to
  the source's 1-indexed `n ≥ 2`; `n = 1` gives 5 primes in `(9, 25)`. No off-by-one.
- **`Bunyakovsky` / `Dickson`** — `BunyakovskyCondition f := 1 ≤ f.degree ∧ Irreducible f
  ∧ 0 < f.leadingCoeff` (read from `FormalConjecturesForMathlib/Algebra/Polynomial/Basic.lean`).
  The `1 ≤ degree` clause closes the constant-polynomial loophole; `degree = 1 ∧
  Irreducible` in Dickson forces primitivity, matching `gcd(aᵢ,bᵢ) = 1`. No defect.
- **`CernyConjecture`** — `Fintype.card σ - 1` is ℕ-subtraction, but it only truncates at
  `card σ = 0`, where `IsSynchronizing` is unsatisfiable (`∃ p : σ` fails). No defect.
- **`CongruentNumber`** — `congruentNumber` omits `0 < a, 0 < b`, but `(a,b) ↦ (|a|,|b|)`
  preserves `a²+b²=c²` and `ab`, so the definition is unchanged for `n ≥ 1`. Tunnell
  parities hand-checked at `n = 1` (fails, correct) and `n = 5` (holds, correct).
- **`GaussCircleProblem.error_isBigO`** — `∃ o → 0, E =O r^{1/2 + o(r)}` is exactly
  `limsup log|E(r)|/log r ≤ 1/2`. Faithful.
- **`Kakeya`, `KomlosConjecture`, `LonelyRunnerConjecture`, `LittlewoodConjecture`,
  `LehmerTotient`, `LegendreConjecture`, `GoldbachConjecture`, `Grimm`,
  `GracefulLabeling`, `Firoozbakht`, `FactorialPrime`, `FermatCatalanConjecture`,
  `Fermat`, `Irrational`, `LanderParkinAndSelfridgeConjecture`, `Lemoine`** — statements
  read against their sources word by word; no divergence found. Details of the
  non-obvious ones: `GracefulLabeling` uses a `Finset` image where the source uses a
  multiset, which is sound because `|edgeFinset| = |Icc 1 m| = m` forces injectivity;
  `LehmerMahlerMeasureProblem`'s `∃ μ, ∀ f, μ > 1 ∧ …` is equivalent to
  `∃ μ > 1, ∀ f, …` since `ℤ[X]` is nonempty.
- **`JacobianConjecture`** (out of scope — `research solved` — checked as an anchor).
  Recomputed both maps with an exact-rational multivariate polynomial implementation:
  `det J(G) = 1` and `G(1,0,1) = G(0,3,-71) = (1,3,0)`; `det J(F) = −2` and
  `F(0,0,−1/4) = F(1,−3/2,13/2) = (−1/4,0,0)`. The repo's `research solved`
  `answer(False)` for the general Jacobian conjecture is backed by a genuine
  counterexample. The open `jacobian_conjecture_two_variables` is untouched by it.

