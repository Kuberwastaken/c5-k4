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

---

## Source pin for GreensOpenProblems

Green, Ben, *100 open problems*, `https://people.maths.ox.ac.uk/greenbj/papers/open-problems.pdf`
— fetched 2026-08-15, HTTP 200, 839,479 bytes, 62 pages, `pdf_type: text_based`,
0 pages needing OCR, embedded pdfTeX creation date **2026-01-30**. Converted with
pdf-inspector; markdown at `scratchpad/green-open-problems.md`, `pdftotext -layout`
cross-check at `scratchpad/green-op-layout.txt`. All quotations below are from
that file.

## Read-only Lean apparatus (no `lake build`)

The repo checkout has `.lake` prebuilt (7.2 GB) but only three project oleans are
present (`FormalConjecturesUtil`, `FormalConjecturesForMathlib`, one OEIS module) —
no `FormalConjectures/GreensOpenProblems/*.olean`. So the Green declarations
themselves cannot be imported. What *can* be run is

```
LEAN_PATH="$(cat scratchpad/LEANPATH.txt)" lean -Dpp.unicode.fun=true \
  -DautoImplicit=false -DrelaxedAutoImplicit=false -Dwarn.sorry=false <probe.lean>
```

with `import FormalConjecturesUtil`, reproducing the relevant statement *shapes*
against real Mathlib. Two probes were run; both are recorded below with their
results. Elapsed ~2 min each. `lake build` was **not** run; nothing was committed.

---

## Depth results

### D1. `Books/UniformDistributionOfSequences/Equidistribution.lean` — `isEquidistributedModuloOne_transcendental_three_halves_pow` — **COUNTEREXAMPLE (formalization)**

**Declaration, verbatim** (blob `f8d8f31c92894545b28e0b2c124241adeaea50c0`):

```lean
/-- For any transcendental number `x`, the sequence `x * (3 / 2) ^ n` is
equidistributed modulo 1. -/
@[category research open, AMS 11]
theorem isEquidistributedModuloOne_transcendental_three_halves_pow (x : ℝ)
    (hx : Transcendental ℚ x) :
    IsEquidistributedModuloOne (fun n ↦ x * (3 / 2 : ℝ) ^ n) := by
  sorry
```

**Definition it unfolds to** (`FormalConjecturesForMathlib/Analysis/Equidistribution/ModOne.lean`):

```lean
def IsEquidistributed (a b : ℝ) (s : ℕ → ℝ) : Prop :=
  ∀ c d, c ≤ d → Set.Icc c d ⊆ Set.Icc a b →
  Filter.atTop.Tendsto (fun n => ((Finset.range n).filter
    fun m => s m ∈ Set.Icc c d).card / (n : ℝ)) (𝓝 <| (d - c) / (b - a))

def IsEquidistributedModuloOne (s : ℕ → ℝ) : Prop :=
  IsEquidistributed 0 1 (fun n => Int.fract (s n))
```

so the claim is: for **every** transcendental `x` and every `0 ≤ c ≤ d ≤ 1`,
`#{m < N : fract (x·(3/2)^m) ∈ [c,d]} / N → d − c`.

**Source divergence.** The file's own header cites Kuipers–Niederreiter,
*Uniform Distribution of Sequences*, Ch. 1 Cor. 4.2, which says `(xⁿ)` is
equidistributed mod 1 **for almost all `x > 1`**, and then quotes the book saying
the `(3/2)ⁿ` case is *unknown*. The declaration replaces "almost all" by "all
transcendental". That is the METHOD band-1 shape (`∀` where the source says
"almost all").

**Provenance.** Added by PR **#3609** (Ralf Stephan, 2026-04-13,
commit `ba885891`), an 8-line diff that appends the declaration with no source
citation and the commit message "This would help in the decidability question of
some halting problems ;-)". Nothing else in the file's history touches it.

**Refutation.** Set `λ = 3/2`, `c = 1/10`, `G = 8`. Build nested closed intervals
`I₀ ⊇ I₁ ⊇ …`, `I_j` of length `c·λ^{−jG}`, such that `ξ ∈ I_j ⟹ fract(ξ λ^{iG}) ∈ [0,c]`
for `i ≤ j`. Induction step: the image of `I_j` under `ξ ↦ ξ λ^{(j+1)G}` is an
interval of length `c·λ^G = 6561/2560 = 2.562891…`. Since `2.5629 ≥ 2 + c = 2.1`,
that image contains **two** full blocks `[k, k+c]`, `k ∈ ℤ`; pull either back.

- Two choices per level ⇒ an injection `{0,1}^ℕ ↪ ℝ` (the two level-`j+1`
  intervals are disjoint because `c < 1`), so the solution set has cardinality
  `2^ℵ₀`. Algebraic numbers are countable, hence **some solution `x` is
  transcendental**.
- For any such `x`, `#{n < N : fract(x λⁿ) ∈ [0,c]} ≥ ⌊N/G⌋`, so
  `liminf ≥ 1/G = 0.125 > 0.1 = d − c`. The required limit is `0.1`. Equidistribution
  fails at `(c,d) = (0, 1/10)`.

**Computation** (exact `Fraction` arithmetic, no floats in the decision path;
`scratchpad/verify_equidist_transcendental.py`, 45 levels, < 1 s):

```
image-interval length c*lambda^G = 6561/2560 = 2.562891
  need >= 1+c = 1.1000 for one choice   -> True
  need >= 2+c = 2.1000 for two choices  -> True
branch all-0: x ~ 1.01549955161749250   interval length 4.047e-65
  violations among n = 0,8,...,360: []
branch mixed: x ~ 1.05363479177655939
  violations: []          x0 != x1: True
over n < 360: hits in [0,1/10] = 111  (density 0.3083), controlled = 45
```

Both branches satisfy every constraint exactly; the empirical density 0.3083 is
well above the guaranteed 0.125, itself above the required 0.1.

**METHOD §A6 classification.** Coordinates (3) and (4): the declaration is
**unfaithful to its own cited source** and **literally false**. Coordinate (1) is
untouched — whether `((3/2)ⁿ)` itself is equidistributed mod 1 (the sibling
`isEquidistributedModuloOne_three_halves_pow`) remains open, and nothing here bears
on it. This is a *formalization* counterexample, not a mathematical one.

**Duplicate status.** `gh search issues/prs` on
`isEquidistributedModuloOne_transcendental`, `transcendental_three_halves`,
`UniformDistributionOfSequences`: **0 hits** on the declaration name. The only PRs
touching this file are #3152/#2628 (both on
`isAccumulationPoint_three_halves_pow_infinite`) and #3609 (the one that
introduced the defect). Not in #4896/#4923/#4927 (re-checked below). **Apparently novel.**

### D2. `GreensOpenProblems/19.lean` — `green_19.lower`, `green_19.upper` — **MIS-TAGGED `research open`**

Both open declarations in the file:

```lean
/-- [Ma21] showed that $3.13 \leq C$. -/
@[category research open, AMS 5 11]
theorem green_19.lower : C >= 3.13 := by sorry

/-- [Ma21] showed that $C \leq 4$. -/
@[category research open, AMS 5 11]
theorem green_19.upper : C <= 4 := by sorry
```

Green's Problem 19 is tagged **"(Solved)"** in the source, and its comments read
verbatim:

> *Comments.* Mandache [220] showed that 3.13 ⩽ *C* ⩽ 4 (and so in particular *C*
> cannot be 3, a fact noted earlier by Qing Chu [70] …).
> *Update 2019.* This question has been resolved by Fox, Sah, Sawhney, Stoner, and
> Zhao [125], showing that **C = 4**.

So both declarations are (a) proved in the literature — their **own docstrings say
"[Ma21] showed that"** — and (b) immediate corollaries of the same file's
`green_19 : C = 4`, which the file itself tags `research solved`. A `research open`
declaration that is a one-line corollary of a `research solved` declaration sitting
eight lines above it is a tagging defect, not a mathematical one.

**Classification (§A6).** Coordinate (2)/(3) only. Nothing false; nothing about the
mathematics. Band 3 (status sync). The genuinely open sibling — the *squares*
configuration `(x,y), (x,y+d), (x+d,y), (x+d,y+d)`, for which Green says "it is not
even clear that C exists" — is **not** in the file.

### D3. `GreensOpenProblems/40.lean` — `green_40.variants.all_n` — **`atTop` on `ℝ≥0∞` does not mean "tends to ∞"**

```lean
/-- Does $f(r) \to \infty$? [Gr24]-/
theorem green_40 : answer(sorry) ↔ Tendsto f atTop (𝓝 ⊤)
...
/-- Does $f_{\text{all}}(r) \to \infty$? [Gr24] -/
theorem green_40.variants.all_n : answer(sorry) ↔ Tendsto f_all atTop atTop
```

`f, f_all : ℕ → ℝ≥0∞`. The two docstrings ask the same kind of question and the two
statements use different target filters. **Machine-checked** (probe
`scratchpad/probe/ProbeGreens.lean`, `lean` exit 0, no errors):

```lean
theorem atTop_ennreal_eq : (atTop : Filter ℝ≥0∞) = pure ⊤ := by
  rw [(isTop_top (α := ℝ≥0∞)).atTop_eq]
  have : Set.Ici (⊤ : ℝ≥0∞) = {⊤} := by
    ext x; simp only [Set.mem_Ici, Set.mem_singleton_iff, top_le_iff]
  rw [this, principal_singleton]

theorem tendsto_atTop_ennreal_iff {α : Type*} (l : Filter α) (g : α → ℝ≥0∞) :
    Tendsto g l (atTop : Filter ℝ≥0∞) ↔ ∀ᶠ x in l, g x = ⊤ := by
  rw [atTop_ennreal_eq, tendsto_pure]
```

`ℝ≥0∞` has a greatest element, so `atTop = ⨅ a, 𝓟 (Ici a) ≤ 𝓟 (Ici ⊤) = pure ⊤`.
Hence `green_40.variants.all_n` asserts **`f_all r = ⊤` for all sufficiently large `r`**
— a strictly stronger and different claim from `f_all r → ∞`, which is what the
docstring asks and what `green_40` (correctly, via `𝓝 ⊤`) states. The probe also
confirms the implication runs one way only (`tendsto_nhds_of_eventually_eq`).

Green's own text for Problem 40 asks "Does *f*(*r*) → ∞?" and notes the non-linear
variant "*f̃*(2) = 1 is known [289], but *f̃*(*r*) → ∞ still possible" — i.e. the
intended reading throughout is the topological one.

**Classification.** Coordinate (4) only: the declaration says something other than
what it means to say. Not false — merely much stronger than the source question.

### D4. `GreensOpenProblems` — a cluster of degenerate `answer(sorry)` holes

The `answer(sorry)` elaborator (`FormalConjecturesUtil/Answer.lean`) is documented
as "providing an answer is not just finding any way to replace `answer(sorry)`", and
in `AnswerSetting.withAuxiliary` it turns the answer into a **top-level auxiliary
definition** `<decl>._answer` — so a legitimate answer must be a **closed** term.
The `AnswerLinter` only catches the one shape `theorem foo (args) : answer(sorry) ↔ …`;
it does not see any of the following.

**(a) Closed by reflexivity — the `isTheta_refl` shape already in the ledger (Erdős 142).**

| Declaration | Statement | Closing term |
|---|---|---|
| `green_25` | `{k : ℕ → ℕ \| ∀ᶠ N in atTop, Property25 (k N) N} = answer(sorry)` | the left-hand set itself; `rfl` |
| `green_51` | `answer(sorry) = guaranteedMaxCosetDim` | `guaranteedMaxCosetDim`; `rfl` |
| `green_27.equivalent` | `(answer(sorry) : ℕ → ℝ) ~[primesAtTop] m` | `m`; `IsEquivalent.refl` |
| `green_37_theta` | `(fun N ↦ (m N k : ℝ)) =Θ[atTop] answer(sorry)` | same function; `isTheta_refl` |
| `green_37_bigO` | `(fun N ↦ (m N k : ℝ)) =O[atTop] answer(sorry)` | same function; `isBigO_refl` |

Machine-checked (same probe, exit 0):

```lean
theorem g27_refl {α : Type*} (l : Filter α) (m : α → ℝ) : m ~[l] m := IsEquivalent.refl
theorem g37_theta_refl {α : Type*} (l : Filter α) (m : α → ℝ) : m =Θ[l] m := isTheta_refl _ _
theorem g37_bigO_refl {α : Type*} (l : Filter α) (m : α → ℝ) : m =O[l] m := isBigO_refl _ _
```

For `green_25` and `green_51` the closing term is closed (no bound variables in
scope), so these two are the strongest: an intended-hard "what is the answer"
question discharged by `rfl`. For `green_37_theta`/`_bigO` the closing term mentions
the theorem's own binder `k`, which puts them in class (b) as well.

**(b) No closed answer exists — false as literally stated.** In each of these the
`answer(sorry)` sits *inside* a binder, so the only terms that could work mention
that binder and are therefore not closed; with a closed answer the statement is
false because the quantity being pinned is non-constant.

| Declaration | Shape | Why no constant works |
|---|---|---|
| `green_24` | `∀ n, max013AffineTranslates n = answer(sorry)` (answer `: ℕ`, under `∀ n`) | `max013AffineTranslates 0 = 0` (only `A = ∅`), and at `n = 3` the set `A = {0,1,3}` already gives one translate, so the value is not constant |
| `green_16` | `(N : ℕ) : ∃ A ⊆ Icc 1 N, SolutionFree A ∧ A.card = answer(sorry) ∧ MaximalFor …` | the maximum is `1` at `N = 1` and `≥ 3` at `N ≥ 3` (any set of `< 4` elements is `SolutionFree`, since `[x,y,z,w].Nodup` needs four distinct elements) |
| `green_37` | `(N k : ℕ) : IsLeast {m \| …} (answer(sorry))` (answer `: ℕ`) | `m N k` varies in both arguments |
| `green_37_asymptotic` | `(k : ℕ) : ∀ᶠ N, (m N k : ℝ) = (answer(sorry) : ℕ → ℝ) N` | one `ℕ → ℝ` cannot equal `m · k` for every `k` |
| `green_41` | `∃ C > 0, ∃ ε₀ > 0, ∀ ε ∈ Ioc 0 ε₀, let ans := (answer(sorry) : ℝ); (minCopies ε : ℝ) ≤ ans ∧ ans < exp exp exp (ε^(-C))` | `ans` is a **single real** under `∀ ε`; `minCopies ε ≥ 1/(2ε) → ∞` as `ε → 0⁺` (each rotated pyjama set has planar density `2ε`, so `n` of them cover only `2εn`), so no constant is an upper bound |

`green_41` is the sharpest of these because the same file already contains the
correct form eight lines below — `green_41.variants.exists_better_bound` puts the
bound under `∃ ans : ℝ` *inside* the `∀ ε`. The main statement simply has the
quantifier in the wrong place.

**(c) The hole carries no information at all.**

`green_35.lower`:

```lean
let lb : ℝ≥0∞ → ℝ≥0∞ := answer(sorry)
(∀ p, 1 < p → lb p ≤ c p) ∧ (ENNReal.ofReal (Real.sqrt (4 / 7)) < c 2 ∨ 0.64 < c ∞)
```

The second conjunct does not mention `lb`. Taking `lb := 0` makes the first
conjunct unconditionally true in `ℝ≥0∞` (machine-checked:
`theorem g35_lower_first_conjunct (c : ℝ≥0∞ → ℝ≥0∞) : ∀ p : ℝ≥0∞, 1 < p → (0 : ℝ≥0∞ → ℝ≥0∞) p ≤ c p := fun p _ => by simp`),
so the declaration is *equivalent to the bare disjunction* and the "answer" is
decorative.

`green_35.upper` is the same shape one step weaker: machine-checked

```lean
theorem g35_upper_shape (c : ℝ≥0∞ → ℝ≥0∞) (h : c ⊤ < 0.7505) :
    ∃ ub : ℝ≥0∞ → ℝ≥0∞, (∀ p : ℝ≥0∞, 1 < p → c p ≤ ub p) ∧ ub ⊤ < 0.7505 :=
  ⟨fun p => if p = ⊤ then c ⊤ else ⊤, …⟩
```

so `green_35.upper` ⟺ `c ∞ < 0.7505`, with `ub` free to be `⊤` everywhere else.

**(d) Green 35 upper is additionally superseded.** Green's own Update 2025 for
Problem 35 reads verbatim: "An AI-based approach [313] has slightly improved the
upper bound of Matolcsi and Vinuesa to *c*_∞ ⩽ **0.75026**." Since `0.75026 < 0.7505`,
`green_35.upper` is answerable from the literature the corpus already cites, while
the file records only `variants.c_inf_upper : c ∞ ≤ 0.7505` as best known. Band-3
status sync.

**(e) Closed by a choice function.** `green_4` (`let S : ∀ n, Set (alternatingGroup (Fin n)) := answer(sorry); MaximalFor (ProdFree …) Set.ncard (S n)`),
`green_5.variants.sl_two` (same shape over `SL(2, ZMod p)`), `green_5`
(`IsLUB {α | …} answer(sorry)` — the set contains every `α ≤ 0` because any
non-identity element is a one-element product-free set, and is bounded above by 1,
so `sSup` closes it), `green_21.variants.fox_kleitman_sharp`
(`IsGreatest {c | ∃ a, ¬RadoCondition a ∧ minColours a = c} answer(sorry)` —
non-empty and bounded by 24 via the file's own `fox_kleitman`). Weaker than (a)–(c):
the closing term exists but is not one token.

### D5. `GreensOpenProblems/72.lean` — `green_72`, `NoKInLine` — asserted in the direction the source doubts

Green's Problem 72, verbatim: "What is the largest subset of the grid [*N*]² with no
three points in a line? **In particular, for *N* sufficiently large is it impossible
to have a set of size 2*N* with this property?**" and, in the comments,
"[167] shows one can have (3/2 + *o*(1))*N* points for arbitrary *N*, **and my
personal suspicion is that this is optimal**."

The Lean asserts the opposite as a bare theorem:

```lean
def NoKInLineFor (k : ℕ) (N : ℕ) : Prop := AllowedSetSize k N = (k - 1) * N

@[category research open, AMS 5 52]
theorem NoKInLine {k : ℕ} {N : ℕ} (hk : 2 < k) (h : k ≤ N) : NoKInLineFor k N := by sorry

@[category research open, AMS 5 52]
theorem green_72 {N : ℕ} (hN : 3 ≤ N) : NoKInLineFor 3 N := by sorry
```

i.e. "`2N` points **are** achievable for every `N ≥ 3`" — the statement Green asks
whether one can *rule out*, and whose negation he suspects. This is the Erdős 952
shape from the ledger ("source asks a question and quotes the author saying the
answer is almost certainly negative; the Lean asserts the positive direction as a
bare `theorem`"). The correctly-hedged form is present in the same file as
`green_72.variants.eventually : answer(sorry) ↔ ∀ᶠ N in atTop, NoKInLineFor 3 N`.

Secondary, same file: the module docstring asks "Given `N > 2` and more than `2*N`
points on an `N × N`-grid, are there 3 of the points on a common line?" — that is the
`≤` half, which the file itself proves as the `textbook` lemma `allowedSetSize_le`
by pigeonhole. The module docstring therefore advertises a question the file already
answers, while the declarations state the other half.

### D6. Checked and cleared (negative results, recorded so they are not re-raised)

- **`GreensOpenProblems/50.lean` `10 • A`.** Hypothesis: `10 • A` might elaborate to
  `Finset.smulFinset` (pointwise scaling), which in characteristic 2 sends `10 • x`
  to `0`, collapsing `10 • A` to `{0}` and making `green_50` trivially false. The
  file's own docstring invites the suspicion by calling it "pointwise scalar
  multiplication". **Refuted by type-check** against real Mathlib:
  `10 • A` elaborates to `Finset.nsmul`, the iterated sumset. Decisive `#eval`s:
  `(10 • (univ : Finset (Fin 1 → ZMod 2))).card = 2` (scaling would give `1`),
  `(2 • univ).card = 2`, `(10 • {0}).card = 1`. `green_50` is faithful; Green's text
  ("Does 10*A* contain a coset of some subspace of dimension at least
  *n* − *O*(log(1/*α*))?") matches word for word.
- **`Other/VCDimConvex.lean` — no internal contradiction.** Hypothesis: at `n = 0`
  the `research solved` lemma `exists_convex_rn_add_two_vc_n_forall_not_hasAddVCNDimAtMost`
  asserts a convex set in `ℝ²` of infinite `VC₀` dimension, contradicting
  `hasAddVCDimAtMost_three_of_convex_r2`. **Refuted by unfolding**
  `HasAddVCNDimAtMost A n d := ∀ x y, ¬ ∀ i s, y s + ∑ k, x k (i k) ∈ A ↔ i ∈ s`
  (`FormalConjecturesForMathlib/Combinatorics/Additive/VCDim.lean`): at `n = 0` the
  index type `Fin 0 → Fin (d+1)` is a singleton, so the condition reduces to
  `A ≠ ∅ ∧ A ≠ univ`, independent of `d`; any proper non-empty convex set witnesses
  it. `VC₁` does coincide with `VC`, so the `n = 1` instance is the genuine
  "convex set in `ℝ³` of infinite VC dimension". No defect.
- **`Other/EquationalTheories_677_255.lean` — correctly tagged, genuinely open.**
  Verified against the ETP: arXiv **2512.07087** states verbatim "we were unable to
  obtain either a human-readable or formalized proof or disproof of the implication
  E677 ⊧_fin E255 … This is the last remaining implication (up to duality) for
  finite magmas to be resolved", and the explorer's data bundle
  (`implications.js`, `last_updated` **2026-08-14T02:20:58Z**) still carries
  "The implication to Equation 255 for finite models **remains open**". The
  infinite-magma case *is* resolved false (greedy / free-677-magma construction),
  matching the file's `research solved` tag on `Equation677_not_implies_Equation255`.
  No finite counterexample is reachable: 1796 known finite 677-magmas up to order
  983 all satisfy 255, and orders 2, 3, 4, 6, 8, 10 admit no 677-magma at all.
- **`Books/…/Problem10_8.lean`, `Mathoverflow/17560.lean`, `Mathoverflow/34145.lean`,
  `Mathoverflow/21003.lean`, `Mathoverflow/434111.lean`, `Other/BeaverMathOlympiad.lean`,
  `Kourovka/1_40.lean`, `GreensOpenProblems/42.lean`** — each carried a specific
  suspicion (trivial-truth loophole, `ℕ`-subtraction, cover-vs-pack inequivalence,
  dot-notation misresolution, indexing drift, `ℕ` vs `ℤ` conclusion, Engel-side
  convention, Cohn–Elkies `2^d` normalisation). All eight checked out; details in
  the triage tables above. In particular Green 42's `f 0 / fHat f 0 = bound` is
  correct precisely because the file fixes minimum distance `r = 2`, making
  Cohn–Elkies' `(r/2)^d` factor equal to 1, and the four `bound` values
  (`1/2`, `√3/6`, `1/16`, `1`) are the optimal centre densities in dimensions
  1, 2, 8, 24.

---

## HANDOFF STATE (updated)

- Triage complete: Millenium 4, Kourovka 4, Subsets 2, Other 3, Books 8,
  Mathoverflow 10, GreensOpenProblems 50, Arxiv 8 of 24 = **89/131**.
- Remaining to triage: Arxiv 16, Paper 23, OpenQuantumProblems 3 = 42.
- Depth done: D1–D6 above.
- Open computational threads: none running.
- Still to do: duplicate sweep against trackers #4896/#4923/#4927 for the D4
  cluster; Green 12 (Möbius-ladder Sidorenko) bounded search; Green 14
  `W_3_20_lower`…`W_3_39_lower` source check; Arxiv 2107.00295 regular-vs-maxDegree
  check.
- Nothing written upstream. No `lake build`. No commits.

---

## Triage — pass 2 (Arxiv 24, Paper 23, OpenQuantumProblems 3)

### Arxiv (24) — the finite head

| Path | Open decls | Verdict |
|---|---|---|
| `Arxiv/2501.03234/ArithmeticSumS.lean` | `conjecture_1_1`, `4_1`, `4_2`, `4_3`, `4_4` | **FIN — computed, see D7.** `S(k)` is an exact double sum over `1 ≤ h, j < k`. |
| `Arxiv/2607.05739/TanArctanSum.lean` | `tan_arctan_sum_not_integer` | **FIN — computed, see D8.** `IsIntegerValue n := A n ∣ B n` with `A, B` the real/imaginary parts of `∏(1+ik)` in `ℤ[i]`; exact integer arithmetic. |
| `Arxiv/1601.03081/UniqueCrystalComponents.lean` | `crystals_components_unique` | **FIN — computed, see D9.** Counterexample is one odd `n` with two admissible factorisations. |
| `Arxiv/2606.03696/BondyLongestCycles.lean` | `bondy_conjecture` | FIN. **Already worked by this campaign** — METHOD_V1_6 §A3 uses "the Bondy exceptional-lobe coordinate" as its worked example of a surgery that dies on a sign check (joining two peripheral `K₂` lobes creates the intended `P₄` but drops the lobe pair's path-cover cost from two to one). Not re-opened. Statement re-checked and faithful: `k*(k-1)` elaborates in `ℝ` (no `ℕ`-truncation), the `+ 1 ≤ k` encoding of "at most `k-1` vertices" is documented, and `variants.one` is vacuous exactly because Dirac forces a Hamiltonian cycle. |
| `Arxiv/2605.02731/DeanCycles.lean` | `dean_conjecture`, `.variants.five` | FIN. `k = 5` is the only open case (the file says so and lists the other cases as solved). Counterexample is one finite graph with `minDegree ≥ 5` and no cycle length divisible by 5; needs a graph generator (no `nauty` on this box). The `m = 0` trivial-truth loophole is closed by the file's own docstring reasoning (a cycle has length ≥ 3). |
| `Arxiv/2604.08040/Conjecture5_5.lean` | `solvable_of_cyc_lt` | FIN, blocked on tooling. Counterexample is a finite non-solvable `G` with `cyc(G) < 2^{π(G)+2}`. `cyc` re-derived by hand for `A₅`: `1 + 15 + 10 + 6 = 32`, matching the file's `cyc_alternatingGroup_five`, and `2^{3+2} = 32`, so `A₅` misses by exactly one — as the file states. Checked the obvious neighbours by hand: `SL(2,5)` has `cyc = 49`, `PSL(2,7)` has `cyc = 79`, both `> 32`; and `cyc(A₅ × C_p) = 64 = 2^{4+2}` for a new prime `p`, again exactly on the boundary. No counterexample without a small-groups library (GAP absent). |
| `Arxiv/2607.05349/MicroscopicWeighting.lean` | `microscopic_weighting_iff_finite_concentration` | FIN. Certificate is a finite metric space where the gauging exists but `(Z t)⁻¹ 1` fails to converge as `t → 0⁺`. Fresh 2026 conjecture. Good hygiene: the file documents that `Matrix.inv` is `0` on singular matrices and why `Nonempty` is load-bearing. Not attempted. |
| `Arxiv/2107.00295/IndependentDomination.lean` | `independentDominationEven`, `independentDominationOdd` | **CANDIDATE — see D10.** Source is *On independent domination of **regular** graphs*; the Lean drops regularity and substitutes `G.maxDegree`. |
| `Arxiv/2607.06396/AlonTarsi.lean` | `alon_tarsi_short_cycle_cover` | FIN but tight. The Petersen graph attains `7/5` exactly (15 edges, shortest cycle cover 21), so any counterexample must beat the known extremal example. Statement faithful (`Multiset` allows repeats; `IsCycleCover` is per-edge). OUT-practical. |
| `Arxiv/2402.13202/CirculantHadamard.lean` | `circulant_hadamard_conjecture` | FIN, verified in the literature past `10^11`. OUT-practical. |
| `Arxiv/0912.2382/CurlingNumberConjecture.lean` | `curling_number_conjecture` | FIN. `k S = sSup {k | ∃ X Y, Y ≠ [] ∧ S = X ++ (replicate k Y).flatten}` — bounded by `|S|` since `Y ≠ []`, so the `sSup` is not junk; `k = 0` and `k = 1` are always attainable. Faithful. Chaffin–Sloane searched far beyond reach. OUT-practical. |
| `Arxiv/2107.12475/CollatzLike.lean` | `CollatzLike` | FIN per `n`; equivalent to BB(15) hardness, verified enormously far. Re-derived the file's own test: `2^8 = 256 = 3^5 + 3^2 + 3 + 1`, base-3 digits `1,0,1,1,0,1`, no `2` ✓. OUT-practical. |
| `Arxiv/2607.08366/MinModulus.lean` | `min_modulus` | FIN for small `n` (`minModulus 3 = 6`, `minModulus 4 = 12`, `minModulus 5 = 28`; exhaustive at `n ≤ 5` is feasible). Good hygiene: the file documents why `0 < N` is needed (`ZMod 0 = ℤ` would make `{1,2}` valid). Not attempted. |
| `Arxiv/1102.4662/AtiyahSutcliffe.lean` | `conjecture_one` | FIN numerically (a determinant in `n` points). The unnormalised `directionLift` is justified in-file by scaling invariance, and the north-pole branch `(1,0)` is the correct projective limit of `((v₀+iv₁)/(‖v‖−v₂), 1)`. Verified numerically by others to `n ≈ 40`. OUT-practical. |
| `Arxiv/2104.00502/BarkerSequence.lean` | `barker_conjecture` | FIN. `aperiodicAutocorrelation` via `zipWith` truncation is exactly `∑ᵢ aᵢaᵢ₊ₖ` ✓. Odd lengths `> 13` ruled out unconditionally; even lengths ruled out past `4·10^33`. OUT-practical. |
| `Arxiv/1104.1579/CunninghamChain.lean` | `infinitely_many_firstKind_chains`, `..._secondKind_...` | OUT (infinitary). Definitions re-checked against the file's two tests (`2 → 2,5,11,23,47,95` length 5; `7 → 7,13,25` length 2) ✓. |
| `Arxiv/2605.12342/Conjecture1.lean` | `conjecture_1` | FIN per `(m,n)` but needs generation-rank computation in `S_m × S_n`. The file documents the `(2,2)` exception carefully (rank 1 vs 2-generation). Not attempted. |
| `Arxiv/2209.04540/…`, `2607.03582/…`, `math.0110202/…`, `2303.01089/…`, `2504.17644/…`, `2208.14736/…` | 3 + 1 + 1 + 1 + 1 + 1 | OUT (spectral sets, convex geometry, Banach spaces, ergodic theory, homogeneous spaces, affine algebraic geometry). |

### Paper (23)

| Path | Open decls | Verdict |
|---|---|---|
| `Paper/LatinSquare.lean` | 7 | **CANDIDATE — see D11.** Two distinct defects; note PR #4965 (theebayuser, opened 2026-08-15) is currently editing this file. |
| `Paper/VoronovskajaTypeFormula.lean` | 4 | **CANDIDATE — see D12.** The `answer` is scoped under `α`, `f`, `x`, and the constant-`f` instance forces it to `0`. |
| `Paper/ReedOmegaDeltaChi.lean` | 3 | FAITH-low. `2*χ ≤ ω + Δ + 2` correctly encodes `χ ≤ ⌈(ω+Δ+1)/2⌉`. But the file mixes `ecliqueNum`/`emaxDegree` (in `ℕ∞`) in the first two statements with `cliqueNum` (in `ℕ`) plus `emaxDegree` in `reed_conjecture_Δ_6_ω_2` — an internal inconsistency, and `cliqueNum` on a type with unbounded cliques takes the junk value `0`. Harmless here because `Δ = 6` caps clique size, but it is a real unit mismatch. FIN in principle (a triangle-free `Δ=6` graph with `χ = 6`). |
| `Paper/Kurepa.lean` | 3 (`kurepa_conjecture`, `.variants.prime`, `.variants.gcd`) | FIN, verified in the literature past `2^34`. The file proves both reductions (prime, gcd) in full, which is unusually strong evidence of faithfulness. OUT-practical. |
| `Paper/Chvatal.lean` | 1 | FIN. Checked the two degenerate families: `F = ∅` and `F = {∅}` both satisfy the conclusion (`Intersecting {∅}` is **false**, so the only subfamily to bound is `∅`). Faithful. Verified in the literature for small ground sets. |
| `Paper/ConjugacyClassSizes.lean` | 1 | FIN, blocked on tooling (needs a finite-group library). Faithful. |
| `Paper/CasasAlvero.lean` | 1 | Status-sync candidate, **already self-documented**: the file's own header says "The conjecture is now claimed to be proven in this paper: [Soham Ghosh, arXiv:2501.09272]" while the declaration stays `research open`. Since the file itself records the claim, an upstream report adds little. |
| `Paper/StrongSensitivityConjecture.lean` | 1 | FIN for `n ≤ 4` by brute force; the best known separation is `bs ≥ (2/3)s²`, so no small counterexample exists. OUT-practical. |
| `Paper/PrimeTuples.lean` | 1 | Checked hard for a defect and found none. The `n = 0` escape in the admissibility hypothesis (`∏ bᵢ = 1 ⟹ p ∤ 1` for every `p`) is *also* present in Dickson's own formulation, and every degenerate form I tried (`aᵢn` with `aᵢ > 1`; proportional forms; `n, n+2, n+4`) is correctly excluded by admissibility at some prime. `b : Fin k → ℕ` narrows the source's integer `bᵢ` to non-negative, which loses generality but introduces no falsity. |
| `Paper/Dubner.lean` | 1 | FIN. `IsTwinPrime p := p.Prime ∧ ((p−2).Prime ∨ (p+2).Prime)`; the `ℕ`-truncation at `p = 2` gives `0`, which is not prime, matching the file's test `¬IsTwinPrime 2` ✓. Faithful. The `4208` threshold is Dubner's own computational bound. |
| `Paper/CatchUpConjecture.lean` | 1 | FIN per `N` (a combinatorial game value), but the game tree grows fast. Not attempted. |
| `Paper/KotzigConjecture.lean`, `Paper/RingelConjecture.lean`, `Paper/LatinTableau.lean` | 1 + 1 + 1 | FIN per tree / per Young diagram; all are famous open decomposition/colouring conjectures. OUT-practical. |
| `Paper/DeGiorgi.lean` | 6 | OUT (PDE rigidity, dimensions 4–8). |
| `Paper/Homogenous.lean` | 5 | OUT (compact homogeneous spaces, cardinal bounds). Minor: quantifies over `Type` rather than `Type*`. |
| `Paper/WeakTiling.lean` | 3 | OUT (measure-theoretic tiling). |
| `Paper/WeaklyFirstCountable.lean` | 3 | OUT (cardinal). Correctly separates the ZFC-only existence (open) from the CH construction (`research solved`, Yakovlev). |
| `Paper/ZagierMZV.lean` | 1 | OUT. `zagierDim` and the weight-0/weight-1 base cases all check out against the file's own tests. |
| `Paper/MonochromaticQuantumGraph.lean` | 34 | OUT-practical. Each is `answer(sorry) ↔ ¬∃ W : WeightsN N D ℂ, EqSystemN N D W` — a polynomial-system solvability question over `ℂ`. Certificate-compatible in principle (Gröbner / numerical algebraic geometry) but this is an active DeepMind prover-agent benchmark file with in-file `formal_proof` links; heavily worked upstream. |
| `Paper/HartshorneConjecture.lean`, `Paper/CardinalityLindelof.lean`, `Paper/FusibleNumber.lean`, `Paper/CatchUpConjecture.lean` | 1 each | OUT (schemes; cardinal — and note the `CardinalityLindelof` docstring's own TODO says such a space exists "under additional axioms (consistent with ZFC)", i.e. the bare `∃` may be independent of ZFC; fusible numbers, where the file itself enumerates four deliberate deviations from Conjecture 7.1). |

### OpenQuantumProblems (3) — all OUT-practical

| Path | Open decls | Verdict |
|---|---|---|
| `OpenQuantumProblems/13.lean` | 12 | Maximal MUB counts in dimensions 6, 10, 12, 14, 15 and the general `d`. **Well-formed**: the general statement is `IsMaxMUBCount d ((answer(sorry) : ℕ → ℕ) d)` — the answer is a *function* applied to `d`, exactly the shape `green_41` and `VoronovskajaTypeFormula` get wrong. Good counter-example to have on file. |
| `OpenQuantumProblems/23.lean` | 12 | SIC-POVM existence in fixed dimensions. Certificate is an exact algebraic construction; only numerical solutions are known in the listed dimensions. |
| `OpenQuantumProblems/35.lean` | 16 | AME-state existence. Already on upstream's radar: issue #4927 lists `OpenQuantumProblems/35`. |

**Triage totals: 131/131 complete.** By collection —
GreensOpenProblems 50, Arxiv 24, Paper 23, Mathoverflow 10, Books 8,
Kourovka 4, Millenium 4, OpenQuantumProblems 3, Other 3, Subsets 2.
FIN (finite certificate shape) 48 · FAITH-only 21 · OUT 62.

---

## Depth results, continued

### D7. `Arxiv/2501.03234/ArithmeticSumS.lean` — **HOLD_BOUNDED, thresholds confirmed sharp**

`S'(h,k) = ∑_{j=1}^{k-1} (−1)^{j+1+⌊hj/k⌋}`, `S(k) = ∑_{h=1}^{k-1} S'(h,k)`.
Four open declarations: `0 < S k` (odd prime `k`); `k < S k` (`k > 5`);
`2k < S k` (`k > 233`); `3k < S k` (`k > 3119`).

Two implementations sharing no code path — a pure-Python double loop
(`scratchpad/verify_arxiv_finite.py`) and a vectorised NumPy outer-product
(`scratchpad/verify_S_threshold.py`) — agree on `k = 3, 5, 7, 11, 101, 233, 239, 401`,
and both reproduce the file's own test `S_fst_10 = [0,0,1,2,5,4,7,10,11,8]` exactly.

```
swept odd primes k ≤ 5987 (two paths; 40 s + 215 s)
  conjecture_1_1 violations (S k ≤ 0)  : []
  conjecture_4_1 violations (S k ≤ k)  : []
  conjecture_4_2 violations (S k ≤ 2k) : []
  conjecture_4_3 violations (S k ≤ 3k, k > 3119) : []
threshold sharpness
  last odd prime with S(k) ≤ 1k  = 5      (file threshold k > 5)     ✓ sharp
  last odd prime with S(k) ≤ 2k  = 233    (file threshold k > 233)   ✓ sharp
  last odd prime with S(k) ≤ 3k  = 3119   (file threshold k > 3119)  ✓ sharp
  k=3109 S=14588 3k= 9327  S>3k ✓        k=3119 S= 9194 3k= 9357  S>3k ✗
  k=3121 S=15128 3k= 9363  S>3k ✓        k=3137 S=12280 3k= 9411  S>3k ✓
  k=3163 S=14382 3k= 9489  S>3k ✓
```

All three thresholds are **exactly** the last failing prime — the strongest possible
positive check on the corpus's constants and on my implementation. No defect.
`HOLD_BOUNDED`; bracket at `k > 5987`.

### D8. `Arxiv/2607.05739/TanArctanSum.lean` — **HOLD_BOUNDED, range extended 40×**

`Zₙ = ∏_{k=1}^n (1+ik)` by exact integer recursion `(a,b) ↦ (a − b·n, b + a·n)`.

```
swept n = 1..119,503  (25 s, exact ℤ arithmetic)
  n with A n = 0                : []          (file's docstring only claims n ≤ 3000)
  n with A n ∣ B n (xₙ integer) : [(1,1), (2,−3), (3,0), (4,4)]
  violations for n ≥ 5          : []
```

The four integer values reproduce the file's `x_values` test
(`x 1 = 1, x 2 = −3, x 3 = 0, x 4 = 4`) exactly. Conjecture verified to
`n = 119,503`, versus the `n ≤ 3000` the file records. No defect. Bracket at `n > 119,503`.

### D9. `Arxiv/1601.03081/UniqueCrystalComponents.lean` — **HOLD_BOUNDED**

```
swept odd n = 3..1,922,151  (40 s)
  crystals found: 115
  crystals with more than one component pair (counterexamples): []
  sample: (35,5,7) (119,7,17) (279,9,31) (527,17,31) (539,11,49) (923,13,71)
          (1455,15,97) (1519,31,49) (2159,17,127) (2759,31,89) (3059,19,161) (3479,49,71)
```

`(35,5,7)` reproduces the file's own test `isCrystalWithComponents_35_5_7` ✓.
No defect. Bracket at odd `n > 1,922,151`.

### D10. `Arxiv/2107.00295/IndependentDomination.lean` — **CANDIDATE: regularity hypothesis dropped**

```lean
/-- **Conjecture 1.6 (Even case).**
For a nonempty isolate-free graph $G$ on $n$ vertices,
if $D$ is even, then $(D + 2)^2 \cdot i(G) \leq (D^2 + 4) \cdot n$. -/
@[category research open, AMS 5]
theorem independentDominationEven (hIso : 0 < G.minDegree) (hEven : Even G.maxDegree) :
    let D := G.maxDegree
    let i := G.indepDominationNumber
    let n := Fintype.card V
    (D + 2)^2 * i ≤ (D^2 + 4) * n
```

The cited source is Cho–Choi–Park, **"On independent domination of *regular* graphs"**
(arXiv:2107.00295). The Lean replaces "`D`-regular" with "isolate-free, `D := G.maxDegree`",
which is a strictly stronger claim: every `D`-regular graph is isolate-free with
`maxDegree = D`, but not conversely.

**Duplicate status — the interesting part.** `gh` search on `IndependentDomination`,
`Cho`, `regularity`: **0 hits** for the regularity mismatch. But two upstream artifacts
propagate the same reading:
- the repo's own formalization request, closed issue **#227** (mo271, 2025-06-13,
  "arxiv 2107.00295: upper bound on independent domination number for isolate-free
  graphs"), states Conjecture 1.6 in the isolate-free/maximum-degree form;
- PR **#1373** (merged 2025-12-10) implemented it that way with no reviewer objection;
- tracker **#4927** (KitaKen1, 2026-08-13) lists both declarations, but only to claim
  they are *solved* ("Corollary 1.3 of arXiv:2202.09594 proves both displayed bounds →
  mark solved") — which, if the regularity hypothesis is genuinely missing, would mark
  as solved a statement stronger than the cited corollary.

**Status: unverified.** I did not fetch arXiv:2107.00295 to confirm the exact wording of
Conjecture 1.6, and the `≤ n/2` heuristic below suggests the non-regular reading may still
be true, so this is a *fidelity* flag, not a falsity claim. Hand-probes found no
counterexample: disjoint `K₂`'s give `i/n = 1/2` at `D = 1`; paths and cycles give
`i/n ≤ 1/2` at `D = 2`; `K_{m,m}` gives `i/n = 1/2`. The asserted ratios are
`(D²+4)/(D+2)² ≥ 1/2` (equality only at `D = 2`) and
`(D²+3)/((D+1)(D+3)) ≥ 1/2` (equality at `D = 1, 3`), so both statements would follow
from `i(G) ≤ n/2` for isolate-free graphs. **Next step for whoever picks this up: read
Conjecture 1.6 in the paper and check whether it says "`k`-regular".**

### D11. `Paper/LatinSquare.lean` — two defects

**(i) `molsExistenceProblem` is closed by `rfl`.**

```lean
@[category research open, AMS 5]
theorem molsExistenceProblem : answer(sorry) = {n : ℕ | HasCompleteMOLS n} := by sorry
```

`answer := {n : ℕ | HasCompleteMOLS n}` is a closed term and the goal becomes `rfl`.
Identical shape to `green_25` and `green_51`. The intended question — "determine exactly
which orders `n` admit a complete set of MOLS", i.e. for which `n` an affine plane exists —
is entirely outside what the declaration asks.

**(ii) `answer(sorry)` outside a free section variable makes `answer := False` unreachable.**

The file opens with `variable {n : ℕ}`, and then:

```lean
theorem oddOrderLatinSquareTransversal : answer(sorry) ↔
    Odd n → ∀ (L : LatinSquare n), ∃ σ, IsTransversal L σ

theorem latinSquareNearTransversal : answer(sorry) ↔
    ∀ (L : LatinSquare n), ∃ ρ σ, IsNearTransversal L ρ σ
```

`n` is auto-bound as an implicit argument, so each reads `∀ {n}, answer ↔ P n` with a
single `answer` outside the `∀ n`. Consequences:

- For `oddOrderLatinSquareTransversal`, `P n` is *true* whenever `n` is even (`Odd n` is
  false), which forces `answer = True`; `answer := False` is then unprovable **whether or
  not the conjecture holds**. The `answer(sorry) ↔ …` idiom exists precisely to let a
  solver record either verdict, and here one verdict is unreachable.
- For `latinSquareNearTransversal` the same scoping means the declaration is provable only
  if `P n` has the *same* truth value for every `n`. If the near-transversal conjecture
  held for some orders and failed for others, **no** value of `answer` would make it
  provable.

This is the exact failure the repo's own `AnswerLinter` warns about
("Move the quantifiers outward … likely the intention was
`theorem foo : answer(sorry) ↔ ∀ᵉ (bar : ℕ) …`"), but the linter's `contains_early_args`
inspects explicit binders in the `declSig` and does not fire on a `variable`-introduced
implicit.

**Also in this file:** `oddOrderLeq9LatinSquareTransversal` is tagged `research solved`
yet still carries an unfilled `answer(sorry)` — the answer should be `answer(True)`.

**Concurrency warning:** PR **#4965** (theebayuser, opened 2026-08-15, "fix: replace
`answer(sorry)` with `answer(True)` in solved statements") is currently editing
`Paper/LatinSquare.lean` **and** `GreensOpenProblems/14.lean`. Re-check this file's blob
immediately before any write.

### D12. `Paper/VoronovskajaTypeFormula.lean` — **CANDIDATE: mis-scoped answer forces the limit to 0**

```lean
@[category research open, AMS 26 40 47]
theorem voronovskaja_theorem.bezier_bernstein_operators
    (α : ℝ) (hα_pos : 0 < α) (hα : α ≠ 1)
    (f : ℝ → ℝ) (x : ℝ) (hx : x ∈ I)
    (hf : ContDiffOn ℝ 2 f I) :
    Tendsto (fun n : ℕ => Real.sqrt n * (bezierBernstein n α f x - f x)) atTop
      (𝓝 answer(sorry)) := by
  sorry
```

`answer(sorry) : ℝ` sits under the binders `α`, `f`, `x`, so a legitimate (closed) answer
is a single real constant, the same for every `α`, `f` and `x`. Two consequences:

1. **The answer is forced to `0`.** Take `f` constant, `f ≡ c` — it is `ContDiffOn ℝ 2` on
   `I`, so it is in scope. Then
   `bezierBernstein n α f x = ∑_{k=0}^n c·(J_{n,k}(x)^α − J_{n,k+1}(x)^α)`
   telescopes to `c·(J_{n,0}(x)^α − J_{n,n+1}(x)^α)`. Now `J_{n,0}(x) = ∑_{j=0}^n p_{n,j}(x) = 1`
   by the binomial theorem, and `bernsteinTail n (n+1)` sums over `Finset.Icc (n+1) n = ∅`,
   so it is the zero polynomial and `0 ^ α = 0` for `α > 0`. Hence the bracket is `c`, the
   sequence is identically `0`, and uniqueness of limits in `ℝ` pins `answer = 0`.
2. **With `answer = 0` the declaration then asserts that
   `√n·(B_{n,α}f(x) − f(x)) → 0` for every `C²` function `f`** — which contradicts the
   file's own "Known Results" section: *"Numerical experiments indicate that for `α ≠ 1`
   the quantity `√n (B_{n,α} f(x) − f(x))` may converge to a **non-zero** limit."*

So the declaration is either false or vacuous, and in neither reading does it ask the
source's question, which is explicitly *"determine an explicit expression for it in terms
of `f`, `x`, and `α`"*.

The same mis-scoping recurs twice more in the file:
`variants.eventually_smooth` binds `let limitFormula : (ℝ → ℝ) → ℝ → ℝ := answer(sorry)`
under `α` (so the formula cannot depend on `α`), and `variants.answer_smoothness` binds
`let p : ℕ × ((ℝ → ℝ) → ℝ → ℝ) := answer(sorry)` under `α` likewise. Only
`variants.eventually_smooth.limit_exists`, which uses `∃ L` **inside** all the binders,
is correctly formed — and `OpenQuantumProblems/13.lean`'s
`IsMaxMUBCount d ((answer(sorry) : ℕ → ℕ) d)` shows the idiom done right elsewhere in the
corpus.

**Duplicate status:** `gh` search on `Voronovskaja`, `bezier`, `bernstein`: not covered by
#4896 / #4923 / #4927, which contain no `Paper/VoronovskajaTypeFormula` entry.
**Apparently novel.** (Caveat: I did not run a dedicated `gh` query on the string
"Voronovskaja"; the sweep covered the trackers and the Green/Books surface. Re-check
before any write.)

---

## Duplicate sweep — results

Offline `gh` sweep of the three live trackers plus targeted issue/PR searches
(read-only; nothing opened, edited or commented).

**Tracker contents.**
- **#4896** (KitaKen1, 2026-08-12, label `misformalization`) — mostly Erdős; only two
  GreensOpenProblems entries: **Green 72** ("apparent reversal of the intended
  conclusion") and Green 21 `fox_kleitman_modular`. **No `Books/` paths.**
- **#4923** (KitaKen1, 2026-08-13) — names the *reflexive asymptotic answer* pattern
  (`isBigO_refl` on Erdős 422, `isTheta_refl` on Erdős 539 and 789) but lists **zero**
  GreensOpenProblems and zero Books items.
- **#4927** (KitaKen1, 2026-08-13, "Open statements with known solutions") — OEIS A287616;
  **Green 3**; **Green 31** (two upper bounds); **OpenQuantumProblems/35**;
  **Arxiv/2107.00295** (as *solved*, not as unfaithful); Mathoverflow/31809;
  **Green 19 `lower` and `upper`**; Erdős 272.

Also relevant: meta-issues **#33** (Paul-Lez, 2025-05-27, "`answer(sorry)` and asymptotic
problems") and **#1407** ("Lint against `answer(sorry)` related errors") state the
reflexivity problem generically and are still open — so the *pattern* is known upstream
while the specific instances below are not.

| Finding | Duplicate status |
|---|---|
| D2 `green_19.lower` / `.upper` mis-tagged | **DUPLICATE.** #4927 verbatim: "Green 19 — `lower` and `upper` — the same file already has the solved theorem `C = 4` → mark both solved." **Drop.** |
| D5 `green_72` asserted in the wrong direction | **DUPLICATE.** PR **#4941** (williamjblair, 2026-08-13) "GreensOpenProblems/72: ask Green's question rather than assert its opposite", plus #4896. |
| D5 `NoKInLine` (same claim at `k = 3`) | **Not covered.** #4941 says explicitly: "**Left alone.** `NoKInLine` contains the same claim at `k = 3`. GK2025 proves it for `k > 10^37`, so the range is a maintainer's call." Weak novelty — deliberately deferred, not missed. |
| D4(a) `green_37_bigO` | **PARTIAL.** PR **#4943** (KitaKen1, 2026-08-13) replaces `answer(sorry)` with `answer(fun N : ℕ ↦ (N : ℝ))` on `green_37_bigO` and `green_37_littleO`, framed as marking solved. It states it "leaves `green_37`, `green_37_asymptotic`, and `green_37_theta` open". |
| D4(a) `green_25`, `green_51`, `green_27.equivalent`, `green_37_theta` | **NOVEL.** 0 hits each. |
| D4(b) `green_24`, `green_16`, `green_37`, `green_37_asymptotic`, `green_41` | **NOVEL.** 0 hits. |
| D4(c) `green_35.lower` (zero-function hole) and (d) `green_35.upper` superseded by `c_∞ ≤ 0.75026` | **NOVEL.** 0 hits on `green_35`; only PRs #1866 and #3547, both cosmetic/feature. |
| D3 `green_40.variants.all_n` (`atTop` on `ℝ≥0∞`) | **NOVEL.** 0 hits on `green_40`, `f_all`, `ENNReal`, `Tendsto atTop atTop`. |
| D1 `isEquidistributedModuloOne_transcendental_three_halves_pow` | **NOVEL.** 0 hits. The only issue naming that module is #4747, and it names a *different* declaration (`isAccumulationPoint_three_halves_pow_exists`). No `Books/` item appears in any of the three trackers. |
| D10 `Arxiv/2107.00295` regularity | **NOVEL as a fidelity claim.** #4927 lists the same two declarations but only asserts they are solved. |
| D11 `Paper/LatinSquare` | **NOVEL**, but PR #4965 is live on the file *today*. |
| D12 `Paper/VoronovskajaTypeFormula` | **NOVEL** (not in any tracker). |
| Green 14 `W_3_20_lower` … `W_3_39_lower` | **DUPLICATE — checked before spending a SAT run.** Issue **#4854** (KitaKen1, 2026-08-10, "Green Problem 14: AKS14 lower bounds are misclassified as open"), PR **#4584**, PR **#4965**. Saved the planned certificate search. |
| `Subsets/FC100OpenSet1` docstring/count mismatch | 0 hits, but the mismatch is almost certainly just drift as listed problems get solved — the `#eval verifyCategoryCounts` is the maintained artifact. Low value; not pursued. |

**Timing risk.** Open-issue counts on this surface right now: 8 labelled
`misformalization`, 19 matching "misformalization" in full text, 8 matching "vacuous",
20 matching "answer(sorry)". In the last three days KitaKen1 touched GreensOpenProblems
four times (PRs #4943, #4887; issues #4927, #4896) and williamjblair twice (PRs #4941,
#4948); **neither has touched `Books/` at all**. A third contributor, theebayuser, opened
PR #4965 on 2026-08-15 against `GreensOpenProblems/14.lean` and `Paper/LatinSquare.lean`.
Re-check every blob immediately before any write.

**Search caveat recorded for the next lane:** GitHub tokenizes underscores, so
`gh search issues "green_19"` returns 0 hits even though #4927 covers it (it writes
"Green 19"). Every underscore-form "0 hits" above was re-run as a spaced phrase.

---

## HANDOFF STATE (final)

- **Triage: COMPLETE, 131/131.** FIN 48 · FAITH-only 21 · OUT 62.
- **Depth: D1–D12 complete.** Three computational holds (D7, D8, D9) with brackets
  recorded; two hypotheses raised and refuted (Green 50 `10 • A`, VCDimConvex `n = 0`).
- **Live candidates, novel, in priority order:**
  1. `Books/UniformDistributionOfSequences/Equidistribution.lean`
     `isEquidistributedModuloOne_transcendental_three_halves_pow` — false; Cantor-set
     construction verified in exact rational arithmetic. **Books is untouched by every
     upstream auditor.**
  2. `Paper/VoronovskajaTypeFormula.lean` `bezier_bernstein_operators` (+2 variants) —
     answer forced to `0` by the constant-`f` instance, contradicting the file's own
     "Known Results" note.
  3. `GreensOpenProblems` degenerate-`answer` cluster: `green_25`, `green_51`,
     `green_27.equivalent` (reflexive); `green_24`, `green_16`, `green_37`,
     `green_37_asymptotic`, `green_37_theta`, `green_41` (mis-scoped);
     `green_35.lower`/`.upper` (content-free hole; `.upper` also superseded by
     `c_∞ ≤ 0.75026` from Green's own Update 2025).
  4. `GreensOpenProblems/40.lean` `variants.all_n` — `atTop` on `ℝ≥0∞` means
     "eventually `⊤`". Machine-checked.
  5. `Paper/LatinSquare.lean` — `molsExistenceProblem` closed by `rfl`;
     `oddOrderLatinSquareTransversal` / `latinSquareNearTransversal` have the answer hole
     outside a free section variable. **PR #4965 is live on this file.**
  6. `Arxiv/2107.00295/IndependentDomination.lean` — regularity hypothesis apparently
     dropped. **Needs the paper read before it is claimed.**
- **Dropped as duplicates:** Green 19 (#4927), Green 72 `green_72` (#4941/#4896),
  Green 14 lower bounds (#4854/#4584/#4965), `green_37_bigO` (#4943, partial).
- **Not attempted, recorded as available inventory:** Green 12 (Möbius-ladder
  `K_{5,5}\C₁₀` Sidorenko instance — the transfer-tensor contraction over `y ∈ G⁵`
  makes `|G| ≤ 27` reachable in NumPy); Dean `k = 5`; Arxiv 2604.08040 (needs GAP);
  Arxiv 2607.05349; Kourovka 19.25 and 20.76 (both need a small-groups library);
  Dubner (cheap twin-prime sieve, not run).
- Nothing written upstream. No `lake build`. No `git commit`.
