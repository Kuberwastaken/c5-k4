# Other-collections lane — upstream filings, 2026-08-15

Authorization: explicit, this campaign turn, for upstream issues **and** PRs on the
GreensOpenProblems / Arxiv / Paper / Books scan. Source of truth:
[`../live-search-2026-08-15/CONFIRMED_LEDGER.md`](../live-search-2026-08-15/CONFIRMED_LEDGER.md)
§ "Other collections lane (2026-08-15)", derivations in
[`../live-search-2026-08-15/other-corpora-scan.md`](../live-search-2026-08-15/other-corpora-scan.md).

## Pins and identity

| item | value |
|---|---|
| upstream `main` at write time | `638da20efd8eeeed2993fc2550fc596dc90c1ce8` (2026-08-15 09:23:12Z, "Mark OEIS A105565 as solved (#4958)") — confirmed live via `gh api …/commits` at write time, unchanged from the scan pin |
| c5-k4 commit used for immutable links | `aa598efc894f2ab9628ccd8019b41318f20111ac` (on `origin/main`; both linked blobs HTTP 200) |
| git identity | Kuber Mehta \<kuberhob@gmail.com\>, GitHub `Kuberwastaken` |
| Lean | Mathlib v4.27.0, toolchain `leanprover/lean4:v4.27.0` |

## Results

| # | Finding | Gate outcome | Artifact | Verification status |
|---|---|---|---|---|
| 1 | `Books/…/Equidistribution.lean` `isEquidistributedModuloOne_transcendental_three_halves_pow` — false as written (`∀` transcendental where the cited source says "almost all") | **CLEAR.** 0 issues on the declaration; only issue naming the module is #4747 (different declaration). Open PRs on the file: #4004 (docstring LaTeX), #4428 (touches only `isAccumulationPoint_iff_exists_subsequence_tendsto`), #4198/#4688 (module chores) — none repairs it. Absent from #4896/#4923/#4927 | issue [#5003](https://github.com/google-deepmind/formal-conjectures/issues/5003), PR [#5004](https://github.com/google-deepmind/formal-conjectures/pull/5004) | Counterexample **re-derived independently** this turn (fresh script, exact `Fraction` arithmetic, 60 levels, three branches, zero violations; `c·λ^G = 6561/2560 ≥ 2+c` exact). Replacement statement **type-checked** against real Mathlib (`lean -DwarningAsError=true`, exit 0). **`lake build` NOT run** (disk); stated in the PR |
| 2 | GreensOpenProblems degenerate-`answer` cluster | **CLEAR** for the six reported; **three items deliberately dropped** (see below) | issue [#5005](https://github.com/google-deepmind/formal-conjectures/issues/5005) | `green_24`, `green_16`, `green_37`, `green_37_asymptotic`: **full Lean disproofs of the closed-answer reading**, definitions copied verbatim from `638da20e`, `lean -DwarningAsError=true`, exit 0, no `sorry`. `green_41`: **argued only** (planar-density bound `minCopies ε ≥ 1/(2ε)`), stated as such in the issue. `green_35.lower`/`.upper` shape lemmas machine-checked. `green_35.upper` status sync **verified against the live source** (Green's PDF fetched today, HTTP 200, 839,479 bytes, MD5 `b82b1358949e0e09db84ca3ba1f5e4bd`; Update 2025 gives `c∞ ⩽ 0.75026 < 0.7505`) |
| 3 | `green_40.variants.all_n` — `(atTop : Filter ℝ≥0∞) = pure ⊤` | **CLEAR.** 0 issues; only PRs on the file are #3947 (introducing), #4312 (notation), #4419 (formal-proof link on `f_tilde_le_f`) | issue [#5006](https://github.com/google-deepmind/formal-conjectures/issues/5006), PR [#5007](https://github.com/google-deepmind/formal-conjectures/pull/5007) | `atTop_ennreal_eq`, `tendsto_atTop_ennreal_iff`, one-way implication: **machine-proved**, exit 0. Replacement shape type-checked. **`lake build` NOT run** |
| 4 | `Paper/VoronovskajaTypeFormula` `bezier_bernstein_operators` (+2 variants) — answer scoped under `α`, `f`, `x`; constant `f` forces it to `0` | **CLEAR as a defect report**, but **contested territory**: two *open* PRs on the same declaration — #4646 (KitaKen1, marks it `research solved` with an external formal proof of `μ(α)√(x(1−x))f′(x)`, leaving `answer(sorry)` in place) and #4432 (SamuelSchlesinger, records the same formula in the docstring). Neither reports the scoping defect; both propose an answer the slot cannot hold. Issue cross-references both and takes no position on their mathematics | issue [#5008](https://github.com/google-deepmind/formal-conjectures/issues/5008) — **no PR** (either open PR would conflict) | `bernsteinTail_zero`, `bernsteinTail_succ_self`, `bezierBernstein_const`, `answer_forced_zero`: **machine-proved** from verbatim definitions, exit 0, no `sorry`. Independent corroboration: PR #4432 proves the same `bezierBernstein_const` |
| 5 | `green_35.upper` status sync (`ub ∞ < 0.7505` vs Green's `c∞ ⩽ 0.75026`) | **CLEAR.** Folded into #5005 Part B rather than filed separately | issue [#5005](https://github.com/google-deepmind/formal-conjectures/issues/5005) Part B | **Live source reached this turn** (unlike the erdosproblems.com batch): PDF fetched HTTP 200, converted with pdf-inspector, Problem 35 comments quoted verbatim, reference [313] identified as the AlphaEvolve white paper. Recorded honestly that AlphaEvolve's bound was not independently re-verified |
| 6 | `Paper/LatinSquare.lean` | **RE-GATED IMMEDIATELY BEFORE WRITE.** PR #4965 (open, `updated 2026-08-15T07:25:11Z`) touches the file but its diff changes **only** `oddOrderLeq9LatinSquareTransversal` (`answer(sorry)` → `answer(True)`). The two reported declarations are untouched | issue [#5009](https://github.com/google-deepmind/formal-conjectures/issues/5009) — **no PR** (#4965 would conflict) | `answer_forced_true` machine-proved. **New finding this turn:** the `AnswerLinter` fires on an explicit `declSig` binder but is **silent** on a `variable`-introduced one — demonstrated by a two-declaration probe whose output is quoted in the issue |

### Dropped, and why

| Item | Reason |
|---|---|
| `green_25`, `green_51`, `green_27.equivalent` (reflexive `rfl` / `IsEquivalent.refl` closures) | **Not a bug by the repo's own policy.** `CONTRIBUTING.md` § "Problems that require answers" gives *literally this shape* (`{n : ℕ \| P n} = answer(sorry)`) as its example and says "one can provide trivial answers that aren't mathematically interesting … outside of the scope of this repository". Maintainer meta-issue #33 tracks it as a design question. All three **were verified closable** (`greens_reflexive_answer_probe.lean`, `with_auxiliary` mode, exit 0) — they are simply not reportable. #5005 says so explicitly, to show the policy was read rather than missed |
| `green_37_theta` | The reflexive witness `fun N ↦ (m N k : ℝ)` mentions the binder `k`, so it is *not* a closed-answer reflexivity; and I could not rule out a single closed function serving every `k` up to `Θ`. No claim made |
| `green_37_bigO`, `green_37_littleO` | PR #4943 (KitaKen1, open) |
| `molsExistenceProblem` (`rfl`) | Same CONTRIBUTING out-of-scope note as the reflexive trio; stated in #5009 |
| Green 19, `green_72`, Green 14 `W_3_*_lower` | Duplicates recorded in the scan (#4927, #4941/#4896, #4854/#4584) — not re-checked in depth this turn, not filed |
| `Arxiv/2107.00295` regularity | Ledger flags it **unverified** (arXiv:2107.00295 not read). Out of scope for this turn; not filed |

## Duplicate gate — method

Ran **immediately before each write**:

1. Full offline corpus snapshot: `gh issue list --state all --limit 6000` → **1747 issues**;
   `gh pr list --state all --limit 6000 --json …,files` → **3237 PRs with per-PR file lists**.
   Regex-matched on declaration name, **spaced** problem name (GitHub tokenises underscores, so
   `green_19` returns 0 hits while #4927 writes "Green 19"), and changed file path.
2. Read #4896, #4923, #4927 in full. None lists any Books, Paper, or the reported Green items.
   Also read #33 and #1407 (the maintainer meta-issues on `answer(sorry)` semantics) — they
   state the *pattern* generically; the instances are unreported.
3. Read the diffs of every open PR touching a target file: #4646, #4432 (Voronovskaja), #4965
   (LatinSquare), #4943 (Green 37), #4549 (Green 27), #4004, #4198, #4428, #4688 (chores).
4. Re-listed everything updated since 2026-08-14 immediately before the first write; nothing
   collided.
5. `git fetch upstream` + `gh api …/commits`: live head **unchanged** at `638da20e`.

## Read-only Lean apparatus

No `lake build` (checkout `.lake` is 7.2 GB, 5.9 GB free; only `FormalConjecturesUtil` and
`FormalConjecturesForMathlib` oleans exist — no `GreensOpenProblems`, `Books` or `Paper` oleans).
Method: copy the target declarations' **definitions verbatim** from `git show upstream/main:<path>`
into a standalone file importing `FormalConjecturesUtil`, then

```
PATH="$HOME/.elan/bin:$PATH" LEAN_PATH="$(cat LEANPATH.txt)" \
  lean -Dpp.unicode.fun=true -DautoImplicit=false -DrelaxedAutoImplicit=false \
       -Dwarn.sorry=false -DwarningAsError=true probe.lean
```

This checks the mathematics against the real Mathlib definitions. It does **not** check that the
upstream files still build; both PRs say so in their Verification sections and ask for CI.

Probes committed alongside this file:

| file | contents | result |
|---|---|---|
| `answer_elaborator_scope_probe.lean` | `with_auxiliary` accepts a closed answer and rejects a binder-dependent one (`(kernel) declaration has free variables '<decl>._answer'`); AnswerLinter fires on `declSig` binders, silent on `variable` binders | as described |
| `greens_answer_scope_probe.lean` | `green_24_no_closed_answer`, `green_16_no_closed_answer`, `green_37_no_closed_answer`, `green_37_asymptotic_no_closed_answer` | exit 0, no `sorry` |
| `greens_reflexive_answer_probe.lean` | `green_25`/`green_51`/`green_27.equivalent` closed by `rfl`/`IsEquivalent.refl` under `with_auxiliary` (verified, **not filed**) | exit 0 |
| `green40_ennreal_atTop_probe.lean` | `atTop = pure ⊤` on `ℝ≥0∞`; `green_35.lower`/`.upper` shape lemmas | exit 0 |
| `voronovskaja_answer_probe.lean` | `bezierBernstein_const`, `answer_forced_zero` | exit 0 |
| `equidistribution_cantor_verify.py` | nested-interval construction in exact `Fraction` arithmetic | 60 levels, 0 violations |

## Link gate

All 15 distinct URLs used in the five issue bodies and two PR bodies returned **HTTP 200**
(`curl -sS -o /dev/null -w '%{http_code}' -L`), including every upstream blob line-anchor at
`638da20e` and both c5-k4 blobs at `aa598ef`.

## Worktree hygiene

Both PRs were prepared in dedicated `git worktree`s off `upstream/main`
(`fix-books-equidistribution-transcendental`, `fix-green-40-all-n-nhds-top`), pushed to the
`Kuberwastaken/formal-conjectures` fork, and the worktrees removed. The shared checkout at
`/Users/kuber.mehta/Projects/formal-conjectures` was never modified (still on
`disprove-oeis-110854`, clean). No `git commit` in `c5-k4`.

## Honest limits

- **No `lake build` anywhere.** Both PRs disclose it and ask for CI.
- **`green_41` is argued, not machine-checked.** The `minCopies ε ≥ 1/(2ε)` density bound is
  standard but was not formalised; the issue says so in place.
- **Kuipers–Niederreiter was not consulted directly.** The "almost all" attribution in #5003 is
  taken from the file's own module docstring. The counterexample does not depend on it.
- **The "almost all" repair was not pursued.** #5003/#5004 convert the false assertion into the
  `answer(sorry) ↔ …` question form (the #4941 idiom) rather than substituting the
  measure-theoretic statement, because that statement is classical and would need a
  `research solved` tag plus a citation I could not pin down (whether the relevant
  Kuipers–Niederreiter theorem covers `(x·θⁿ)` for fixed `θ`, as opposed to `(xⁿ)`).
- **AlphaEvolve's `c∞ ⩽ 0.75026` was not independently verified**, only Green's record of it.
- **The Voronovskaja and LatinSquare issues carry no PR** because open PRs by other contributors
  are live on both files.
