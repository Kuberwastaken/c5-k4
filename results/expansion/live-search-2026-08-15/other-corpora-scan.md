# Other-corpora audit — non-Wikipedia collections, 2026-08-15

**Scope:** the 131 entries of
`results/expansion/open_targets_other_corpora_20260815.json` whose `corpus` is
**not** `Wikipedia`. Ten collections: GreensOpenProblems (50), Arxiv (24),
Paper (23), Mathoverflow (10), Books (8), Kourovka (4), Millenium (4),
OpenQuantumProblems (3), Other (3), Subsets (2).

**Upstream pin:** `638da20efd8eeeed2993fc2550fc596dc90c1ce8` (2026-08-15 09:23:12
+0000), the same head the OEIS/Erdős lane re-verified against. All file text
read via `git show upstream/main:<path>`; per-file blob SHAs recorded in
`scratchpad/manifest.json`.

**Method:** METHOD_V1_6 §A4 (triage all before depth), §A2 (P0 pre-flight),
§A5 (append after every target), §A6 (four-coordinate status).

---

## HANDOFF STATE

- Triage: IN PROGRESS. Complete for Millenium (4), Kourovka (4), Subsets (2),
  Other (3), Books (8), Mathoverflow (10) = 31/131.
- Depth: not started.
- Candidates so far: 1 strong (Books/UniformDistributionOfSequences —
  `isEquidistributedModuloOne_transcendental_three_halves_pow`), unverified.
- Nothing written upstream. No `lake build` run. No commits.

---

## Triage — pass 1

Legend: **FIN** = finite-settleable or finitely falsifiable in principle;
**FAITH** = faithfulness/vacuity check is the live vein; **OUT** =
certificate-shape-incompatible (asymptotic / infinitary / cardinal / analytic)
and no faithfulness handle.

### Millenium (4) — triaged OUT as a block

Clay Millennium problems. Every open declaration quantifies over
infinite-dimensional function spaces, manifolds, complexity classes over
infinite language sets, or the analytic continuation of an L-function. There is
no finite artifact whose evaluation can make any of them false, and the
canonical statements are pinned by Clay's own PDFs (which each file cites), so
the faithfulness vein is also thin. Concretely:

| Path | Open decls | Reason |
|---|---|---|
| `Millenium/NavierStokes.lean` | 4 (A/B/C/D) | PDE existence + smoothness on `ℝ³`/`ℝ³/ℤ³`; witness would be a `C^∞` velocity field. OUT. Statement tracks Fefferman's conditions (1)–(11) with per-condition docstrings; the errata (periodic pressure) is explicitly handled. |
| `Millenium/Poincare.lean` | 2 (`smooth_dimension_four`, `smooth_other_cases`) | Smooth Poincaré in dim 4 and Wang's Conjecture 1.17. Manifold-valued. OUT. |
| `Millenium/PvsNP.lean` | 2 (`P_ne_NP`, `NP_ne_coNP`) | Equality of sets of `List Bool → Bool`. OUT. |
| `Millenium/RiemannHypothesis.lean` | 2 (`riemannHypothesis`, `generalized_riemann_hypothesis`) | Analytic. OUT. Note the file already documents (and avoids) the `dedekindZeta` junk-value trap that would have made a naive ERH provably false — the defect shape this campaign hunts is here *pre-empted* by the authors. |

No further work planned on Millenium.

### Kourovka (4)

| Path | Decl | Verdict |
|---|---|---|
| `Kourovka/19_25.lean` | `kourovka.«19.25»` | **FIN — top of queue.** `∀ G H finite groups, |G| = |H| → ∑_{g} φ(ord g) = ∑_{h} φ(ord h) → IsSimpleGroup G → IsSimpleGroup H`. A counterexample is a *pair of finite groups*: entirely finite, exhaustively searchable at small order. |
| `Kourovka/20_76.lean` | `kourovka.«20.76»` | **FIN.** Pyber: finite `p`-group, all abelian normal subgroups of order `≤ p^k` ⟹ all abelian subgroups of order `≤ p^{2k}`. Counterexample is one finite `p`-group. Needs a small-group library. |
| `Kourovka/1_40.lean` | `kourovka.«1.40»` | OUT/FAITH. Engel groups; a counterexample is infinite (the Fitting analogue fails only in infinite groups). Faithfulness of `IsEngelElement` checked: `engelCommutator x y n = [x, _n y]`, `∀ x, ∃ n` — matches Robinson's *left* Engel element, as the docstring claims. `H ⊔ K = ⊤` is the correct rendering of `G = HK` for normal `H, K`. No defect found. |
| `Kourovka/1_74.lean` | `kourovka.«1.74»` | OUT / status-sync. Existence of a topologizable Tarski monster. Infinite witness. The file's own docstring concedes it formalizes a "natural test case" rather than Problem 1.74 ("describe all minimal topological groups") — a self-declared narrowing, not a hidden defect. Worth one literature check against Ol'shanskii's non-topologizable group. |

### Subsets (2)

| Path | Verdict |
|---|---|
| `Subsets/FC100OpenSet1.lean` | **FAITH — checkable, mechanical.** Docstring: "A random subset of 100 open research problems, drawn uniformly at random from all problems with the `category research open` tag." The file's own `#eval verifyCategoryCounts` then asserts `("research open", 92), ("research solved", 8)`. Docstring and assertion contradict each other on 8 of the 100 members. Verify by reading the live category tag of each of the 100 names. |
| `Subsets/FC100SolvedSet1.lean` | OK. Docstring says "without the `research open` tag (solved, test, API, etc.)"; counts `test 34 / research solved 50 / API 9 / textbook 7 = 100` are consistent with it. No defect. |

### Other (3)

| Path | Decl | Verdict |
|---|---|---|
| `Other/EquationalTheories_677_255.lean` | `Finite.Equation677_not_implies_Equation255`, `Finite.Equation677_implies_Equation255` | **FIN / status-sync — high priority.** Asterix (677) vs Obelix (255) on *finite* magmas; the two open declarations are exact negations of each other. Witness would be one finite magma. Upstream ETP has searched this hard; the live question is whether ETP has since resolved it (status-sync). |
| `Other/BeaverMathOlympiad.lean` | `problem_1`, `problem_2_antihydra`, `.variants.set`, `problem_5`, `problem_8` | FIN-in-principle, low. Each is an explicit integer recursion; the open ones are Busy-Beaver halting reformulations that bbchallenge has iterated far past anything reachable in 60 s. Docstring/Lean recurrences re-derived term-by-term for #1 (10 terms), #4 (9 terms), #5 and #8 (8 terms each) — **all match**, and every `ℕ`-subtraction is guarded by its own `if`. No formalization defect. |
| `Other/VCDimConvex.lean` | `hasAddVCNDimAtMost_two_one_of_convex_r3`, `exists_hasAddVCNDimAtMost_n_of_convex_rn_add_one`, `hasAddVCNDimAtMost_n_one_of_convex_rn_add_one` | FAITH. Needs the repo's `HasAddVCNDimAtMost` definition. Specific check queued: at `n = 0` the `research solved` lemma `exists_convex_rn_add_two_vc_n_...` asserts a convex set in `ℝ²` with **infinite** `VC₀` dimension, while `hasAddVCDimAtMost_three_of_convex_r2` asserts every convex set in `ℝ²` has VC dimension `≤ 3`. If `VC₀ = VC` these two contradict. |

### Books (8)

| Path | Decl | Verdict |
|---|---|---|
| `Books/UniformDistributionOfSequences/Equidistribution.lean` | `isEquidistributedModuloOne_transcendental_three_halves_pow` | **CANDIDATE — depth target #1.** Asserts `∀ x transcendental, (x·(3/2)ⁿ) is equidistributed mod 1`. The cited source (Kuipers–Niederreiter Ch. 1 Cor. 4.2) says *almost all* `x > 1`, and the file's own header quotes the book saying the `(3/2)ⁿ` case is unknown. `∀` where the source says "almost all" is the METHOD band-1 defect shape. Refutation sketch (nested-interval / Cantor construction) below. |
| same | `isEquidistributedModuloOne_three_halves_pow` | OUT. The genuine open problem (`x = 1`). |
| same | `isAccumulationPoint_three_halves_pow` | FAITH-low. `answer(sorry)` hole whose answer is a *real number*: "find an accumulation point of `{(3/2)ⁿ}`". No degenerate witness found — `IsAccumulationPoint x s := x ∈ closure (range s \ {x})` and the range is an infinite set of distinct reals, so no self-referential collapse. Separately: `isAccumulationPoint_iff_exists_subsequence_tendsto` is a `def` (not `theorem`), carries no `category` attribute, is proved by `sorry`, and its name says "iff" while it states one direction only. Cosmetic. |
| `Books/BugeaudDistributionModuloOne/IntDistanceDistribution.lean` | `problem_10_1`, `10_2`, `10_3`, `waldschmidt` | OUT. Limits/`Tendsto`/`∃c ∀n` bounds on `‖eⁿ‖`. Re-read against Bugeaud Ch. 10: `1 < |α|` correctly excludes the trivial `|α| < 1` case the docstring names, and the `n ≥ 2` start on `waldschmidt` is documented and necessary. No defect. |
| `Books/BugeaudDistributionModuloOne/Problem10_4.lean` | `spectrum_xi_alpha_pow_countable` | OUT (countability of a spectrum). |
| `Books/BugeaudDistributionModuloOne/Problem10_5.lean` | `problem_10_5`, `problem_10_5_moreover` | OUT (lacunary sequences in a number field). The `.._of_moreover` bridge is fully proved, which is evidence the two are correctly related. |
| `Books/BugeaudDistributionModuloOne/Problem10_6.lean` | `problem_10_6_variant_1`, `_variant_2` | OUT (Hausdorff dimension / density mod 1). |
| `Books/BugeaudDistributionModuloOne/Problem10_7.lean` | `problem_10_7` | OUT (arbitrarily large non-Pisot `α`). |
| `Books/BugeaudDistributionModuloOne/Problem10_8.lean` | `problem_10_8` | OUT. `p`-adic Littlewood. Checked for a trivial-truth loophole: for rational `ξ` the set contains `0` outright, but for irrational `ξ` every element is `> 0`, so the `sInf = 0` claim is the real conjecture. Faithful. |
| `Books/BugeaudDistributionModuloOne/Problem10_9.lean` | `problem_10_9` | OUT. Delegates to `Mahler32.mahler_conjecture` via `type_of%`, so no independent statement to diverge. |

### Mathoverflow (10)

| Path | Decl | Verdict |
|---|---|---|
| `Mathoverflow/339137.lean` | `mathoverflow_339137` | **FIN — depth queue.** Monic `P, Q ∈ ℝ[X]` with non-negative coefficients and `PQ` a 0–1 polynomial ⟹ `P, Q` are 0–1. A counterexample is a finite pair of real polynomials, so the certificate shape *is* compatible. Same problem as `Green28`. |
| `Mathoverflow/75792.lean` | `complexity_two_pow` | FIN-in-principle, OUT in practice. `‖2ⁿ‖ = 2n`; integer complexity is verified past `10^12` by Iraids et al. Definitions re-checked (`Reachable` upward-closed via `·.mul .one`; `complexity` = `Nat.find`) — faithful. |
| `Mathoverflow/34145.lean` | `rectangles_cover_unit_square`, `rectangles_pack_unit_square` | OUT (infinitely many rectangles). Checked the cover form for a "rectangles may stick out / may overlap" loophole: total area is exactly 1 (`tsum_area_eq_one`, proved in-file), so any cover forces an essentially-exact tiling and the two forms are genuinely equivalent. Faithful. |
| `Mathoverflow/235893.lean` | `mathoverflow_235893` | OUT (connected bijections of `ℝⁿ`). |
| `Mathoverflow/1973.lean` | `mathoverflow_1973` | OUT (complex structure on `S⁶`). |
| `Mathoverflow/21003.lean` | `mathoverflow_21003` | OUT (polynomial bijection `ℚ² → ℚ`). `f.eval x` resolves to `MvPolynomial.eval x f`, so the map is `(Fin 2 → ℚ) → ℚ`. Faithful. |
| `Mathoverflow/17560.lean` | `mathoverflow_17560` | OUT (four-exponentials-strength). Checked the `∃ m : ℕ, x = m` conclusion against the source's "x must be an integer": `2^x = m` with `m : ℕ` forces `m ≥ 1` hence `x ≥ 0`, so `ℕ` loses nothing. Faithful. |
| `Mathoverflow/347178.lean` | `.variants.bounded_only` | OUT-low. Both sibling variants are `research solved` with `answer(False)` and a linked formal proof; the open one adds two-sided boundedness. |
| `Mathoverflow/31809.lean` | `mathoverflow_31809` | OUT + minor FAITH note. Docstring asks "*does there exist* a pretriangulated category that is not triangulated"; the formalized proposition is the `∀`-form "every pretriangulated category is triangulated", i.e. the negation. `answer` therefore inverts the docstring's question. Same shape as Erdős 952 in the ledger but much weaker (no assertion is made in the wrong direction — the `answer(sorry)` hole absorbs it). |
| `Mathoverflow/434111.lean` | `restricted_prime_number_theorem`, `.variants.even_subsequence` | OUT (asymptotic `~`). Verified `S n` reproduces A013916 (`S k` prime at `k = 1,2,4,6,…`) and that the `.even_subsequence` variant correctly carries Meštrović's `S_{2m}` indexing with the matching `m/log m` (not `m/(2 log m)`) normalisation. Faithful. |
