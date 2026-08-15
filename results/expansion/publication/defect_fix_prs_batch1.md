# Defect-fix PRs, batch 1 — OEIS A237271 / Erdős 1093 / 1055 / 40

Written 2026-08-15. Upstream base: `google-deepmind/formal-conjectures` `main` at
`638da20e` ("Mark OEIS A105565 as solved (#4958)").

Four issues filed in the 2026-08-15 sweep (#4974, #4975, #4976, #4977) converted
into one-file PRs, each closing its issue with `Fixes #NNNN.`

Sources were re-read **live** for all four: erdosproblems.com/1093, /1055, /40 and
oeis.org/A002997, /A005113, /A237271, via the headless-Chromium `browse` daemon
(curl and WebFetch both get Cloudflare 403 from both hosts; the daemon's ports
9400–9409 were all occupied by leaked servers, so a dedicated instance was run on
port 9779 under `Xvfb :99`). All four problems are `open` on their source pages.

## Result table

| Defect | PR | Repair chosen | Verification | Deliberately left out |
|---|---|---|---|---|
| OEIS A237271 `observation_carmichael` (#4974) | [#4987](https://github.com/google-deepmind/formal-conjectures/pull/4987) | `(hk : ¬k.Prime ∧ 1 < k ∧ ∀ a : ZMod k, a ≠ 0 → a^(k-1) = 1)` → `(hk : IsCarmichael k)`, the repo's own predicate in `FormalConjecturesForMathlib/NumberTheory/Carmichael.lean` (no new import: `FormalConjecturesUtil` re-exports it); +3 docstring lines quoting A002997 | Type-check clean in both `answer` modes. **Machine-checked** that the old hypothesis is unsatisfiable for every `k`: `old_hyp_unsatisfiable`, `#print axioms` = `[propext, Classical.choice, Quot.sound]` | The issue's suggested inline `∀ a : ZMod k, IsUnit a → …` (rejected: AGENTS.md says reuse an existing definition; would leave two unconnected spellings of "Carmichael"). No `#print axioms isCarmichael_561` — that olean was not built |
| Erdős 1093 `deficiency` (#4975) | [#4986](https://github.com/google-deepmind/formal-conjectures/pull/4986) | `smoothNumbers k` → `smoothNumbers (k + 1)` (one token); +4 docstring lines carrying the source's "divisible only by primes $\le k$" and naming the `< m` convention | Type-check clean in both modes. All 23 catalogue entries recomputed with exact integer arithmetic: **23/23** under `≤ k`, **20/23** under `< k`; the 3 that change are exactly C(7,3) 1→0, C(23,5) 1→0, C(47,11) 4→3, all with `k` prime, all satisfying `2k ≤ n` and the "no prime `p ≤ k` divides `C(n,k)`" side condition | A `test` lemma pinning `deficiency 7 3 = 1` — `deficiency` is `noncomputable`, so it needs a decidable restructuring. Offered in the PR body |
| Erdős 1055 `IsOfClass` (#4976) | [#4988](https://github.com/google-deepmind/formal-conjectures/pull/4988) | Added `(∀ (m : ℕ+) (hm : m ≤ n), ¬ H m hm p) ∧` as the first conjunct of the successor case, making the class exact; +5 docstring lines | Type-check clean in both modes. Both definitions transcribed from the recursor's defining equations into an independent implementation and compared against the sources' class function: over every prime `< 200000` and `r ∈ 1..7` the current definition disagrees with "class exactly `r`" on **35** `(p,r)` pairs (all `r = 2`, all class-1 primes), the repaired one on **0**. `p r` reproduces A005113 `2,13,37,73,1021,2917` for `r = 1..6` | Unfolding lemmas for `IsOfClass` and a `test` pinning `p 2 = 13`. Both offered in the body. The alternative one-clause repair `¬((p+1).primeFactors ⊆ {2,3})` (sufficient, but fixes the symptom at `n=1` rather than stating exactness) |
| Erdős 40 `erdos_40` (#4977) | [#4993](https://github.com/google-deepmind/formal-conjectures/pull/4993) | `Erdos40ForSet answer(sorry)` → `answer(sorry) ↔ ∃ g : ℕ → ℝ, Tendsto g atTop atTop ∧ Erdos40For g`; +5 docstring lines | Type-check clean in both modes; `variants.implies_erdos_28` still compiles. **Machine-checked** that four candidate shapes are trivially closable, each `#print axioms` = `[propext, Classical.choice, Quot.sound]` | **The fix the issue itself suggested.** See below |

Diff sizes: A237271 `+4/-3`, 1093 `+6/-2`, 1055 `+8/-1`, 40 `+8/-2`. One file each,
no bundled changes. Every body carries the AI assistance disclosure and `Fixes
#NNNN.`

## The one substantive correction: issue #4977's suggested fix is also trivial

Issue #4977 proposed repairing `erdos_40` with an extremality wrapper,
`IsGreatest {G : Set (ℕ → ℝ) | Erdos40ForSet G} answer(sorry)`. That was checked
before writing the diff, and **it is closable in two `fun`s**:

```lean
theorem isGreatest_trivial :
    IsGreatest {G : Set (ℕ → ℝ) | Erdos40ForSet G}
      {g : ℕ → ℝ | Tendsto g atTop atTop → Erdos40For g} :=
  ⟨fun _ hg h => hg h, fun _ hG _ hgG => hG _ hgG⟩
-- depends on axioms: [propext, Classical.choice, Quot.sound]
```

The reason is structural, not incidental: `Erdos40ForSet G` is a *pointwise*
property of the members of `G`, so it is downward closed and closed under unions,
and its greatest element is definitionally `{g | Tendsto g atTop atTop → Erdos40For
g}`. The same objection kills every "determine the class" shape — including
`{g | Tendsto g atTop atTop ∧ Erdos40For g} = answer(sorry)`, closed by `rfl`,
which is the reflexive-`answer` pattern already collected upstream in #4923.
Implementing the issue's suggestion would have replaced one trivial hole with
another.

The maximal instantiation is not a candidate either: `Erdos40ForSet .univ` is
**false**. The file's own `variants.implies_erdos_28` instantiates it at
`g = fun N ↦ √N`, and `Erdos40For (fun N ↦ √N)` fails for `A = {2^k}`: there
`√N / g N = 1 = O(|A ∩ [1,N]|)` since `|A ∩ [1,N]| = ⌊log₂ N⌋ + 1`, while
`sumRep A n ≤ 2` for every `n`, so the `limsup` is `2`, not `⊤`. So
`variants.implies_erdos_28` is a true implication with an unsatisfiable hypothesis.
This was **not** formalised and is **not** in the diff; it is recorded in the PR
body as an out-of-scope observation, and it is the reason the `.univ` reading was
rejected.

What was implemented instead is the decision form of the source's question ("is
there any such `g` at all?"). It is faithful to how the source describes the
problem's content — "establishing this for any function `g(N)→∞` would imply a
positive solution to [28]" — and it is at least as hard as Erdős Problem 28, hence
open. It is weaker than the full characterisation, and the PR body says so
explicitly: since `Erdos40For` is antitone in `g`, the admissible class is downward
closed and any Lean rendering of "determine that class" is closed by writing the
class down. If a concrete conjectured threshold is ever recorded on the problem
page, `Erdos40ForSet {g | …}` with that threshold named would be strictly better.

## Verification method (identical for all four)

`lake build` was **not** run (shared checkout, ~6 GB free, two earlier lanes
collided racing identical olean paths). Instead each file was elaborated read-only
against the existing package oleans:

```
LEAN_PATH=<repo>/.lake/build/lib/lean:<each package>/.lake/build/lib/lean
lean -DwarningAsError=true -Dpp.unicode.fun=true -DautoImplicit=false \
     -DrelaxedAutoImplicit=false -Dwarn.sorry=false \
     -Dlinter.style.copyright.formalConjectures=true -Dlinter.style.namespace=true \
     -Dlinter.style.openClassical=true -Dlinter.style.ams_attribute=true \
     -Dlinter.style.category_attribute=true \
     -Dlinter.style.conditional_formal_proof=true \
     -Dlinter.style.moduleDocstring=true -Dlinter.style.latex_docstring=true \
     <file>
```

— i.e. exactly the `leanOptions` the `FormalConjectures` library declares in
`lakefile.toml`, plus `warningAsError`. Every file was also run with
`-Dgoogle.answer=postpone` (the `FormalConjecturesAnswerPostpone` library's mode).
No transformation of `answer(…)` or of `@[category …]` was needed: with
`FormalConjecturesUtil`'s olean on `LEAN_PATH` both elaborate normally.

Two **negative controls** confirm the linters are actually live in this
configuration, rather than silently absent:

- reordering the `AMS` tags → `error: The AMS tags should be ordered as AMS 5 11`;
- deleting a `@[category …]` attribute → `error: Missing problem category
  attribute` and `error: Missing AMS attribute`.

`FormalConjectures/ErdosProblems/40.lean` imports `FormalConjectures.ErdosProblems.«28»`,
whose olean was not built; it was compiled once with `lean -o` into a scratch
directory outside the shared tree, never into `<repo>/.lake`.

Limits stated in every PR body: no `lake build`, so the full build (downstream
modules, the test driver, `decide`-based elaboration elsewhere) was not exercised;
CI is the authoritative check.

## Not verified, and said so

- **1055**: the semantic check is a transcription of `PNat.caseStrongInductionOn`'s
  defining equations, not a Lean evaluation. `IsOfClass` cannot be evaluated inside
  Lean at all: it is built on well-founded recursion, `IsOfClass 1 2` is not
  definitionally `(3 : ℕ).primeFactors ⊆ {2,3}`, `rfl` fails and
  `simp [IsOfClass, PNat.caseStrongInductionOn, PNat.strongInductionOn]` loops to
  `maximum recursion depth`. The file provides no unfolding lemmas.
- **A237271**: `isCarmichael_561` is cited as an existing declaration in
  `FormalConjectures/Wikipedia/AgohGiuga.lean`, not as a proof I checked — that
  module's olean was not available, so no `#print axioms` was run on it.
- **40**: the `Erdos40ForSet .univ` falsity argument is a paper argument.

## Duplicate gate

Re-run immediately before each push, on the identifier and on open PRs touching the
file: `237271` / `observation_carmichael` → 0 PRs; `1093` / `smoothNumbers` → only
merged #1328, #1532 and closed solve-attempts; `IsOfClass` → only the introducing
#1197; `erdos_40` / `Erdos40ForSet` → only two closed solve-attempts. The one open
PR that matched on the string `1055` (#3588, Ramsey formalisations) was checked
file-by-file and touches none of the four files. All four issues were still `OPEN`
and unassigned at push time.

## PRs

| Issue | PR |
|---|---|
| [#4974](https://github.com/google-deepmind/formal-conjectures/issues/4974) OEIS A237271 | [#4987](https://github.com/google-deepmind/formal-conjectures/pull/4987) |
| [#4975](https://github.com/google-deepmind/formal-conjectures/issues/4975) Erdős 1093 | [#4986](https://github.com/google-deepmind/formal-conjectures/pull/4986) |
| [#4976](https://github.com/google-deepmind/formal-conjectures/issues/4976) Erdős 1055 | [#4988](https://github.com/google-deepmind/formal-conjectures/pull/4988) |
| [#4977](https://github.com/google-deepmind/formal-conjectures/issues/4977) Erdős 40 | [#4993](https://github.com/google-deepmind/formal-conjectures/pull/4993) |

All four `OPEN` and `MERGEABLE` at time of writing. Work was done in a dedicated
`git worktree` off `upstream/main`, removed afterwards; the shared checkout at
`/Users/kuber.mehta/Projects/formal-conjectures` was never modified.
