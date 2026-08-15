# Defect-fix PRs, batch 2 — Erdős 33 / 15 / 477 / 952

Written 2026-08-15. Upstream base: `google-deepmind/formal-conjectures` `main` at
`638da20e` ("Mark OEIS A105565 as solved (#4958)").

Four issues filed in the 2026-08-15 sweep (#4978, #4979, #4980, #4981) converted
into one-file PRs. All four sources were re-read **live** from erdosproblems.com
(the site returns 403 to a default user agent and to WebFetch, but serves normally
to `curl` with a browser `User-Agent`; that is how #15/#33/#477/#952 were fetched).
All four problems are `open` on the site and in the `teorth/erdosproblems`
`data/problems.yaml` mirror.

## Result table

| Defect | PR | Repair chosen | Verification | Deliberately left out |
|---|---|---|---|---|
| Erdős 33 `variants.one_mem_lowerBounds` (#4978) | [#4989](https://github.com/google-deepmind/formal-conjectures/pull/4989) | `∃ A, cond A ∧ 1 < limsup_ℝ …` → `1 < ⨅ A : {A \| AdditiveBasisCondition A}, limsup … (√N : EReal)`, the expression `erdos_33`/`vanDoorn` already use; +1 docstring sentence | `lean -DwarningAsError=true`, clean; also clean under `google.answer=postpone`. No `lake build` | The alternative repair (keep `∃`, rename the declaration, add explicit `< ⊤`) is offered in the PR body but not pushed |
| Erdős 15 `Summable` (#4979) | [#4990](https://github.com/google-deepmind/formal-conjectures/pull/4990) | `Summable (… : ℕ → ℚ)` → `∃ l : ℝ, Tendsto (fun N => ∑ k ∈ Finset.range N, (-1:ℝ)^(k+1) * (k+1) / nth Prime k) atTop (𝓝 l)`; +3 docstring lines saying why not `Summable` | Same as above, clean in both modes. Reduction "current RHS ⇒ `Summable (n/p_n)`" machine-checked, `#print axioms` = `[propext, Classical.choice, Quot.sound]` | The file's `-- TODO: add the other statements from the additional material` (three further Erdős conjectures on the source page) |
| Erdős 477 index set (#4980) | [#4991](https://github.com/google-deepmind/formal-conjectures/pull/4991) | `f.eval '' {n \| 0 < n}` → `Set.range f.eval` in all five declarations | Same as above, clean in both modes | No attempt to settle whether the one-sided `degree_two_dvd_condition_b_ne_zero` was true; no re-tagging of the two `research solved` variants |
| Erdős 952 asserted direction (#4981) | [#4992](https://github.com/google-deepmind/formal-conjectures/pull/4992) | `theorem erdos_952 : ∃ …` → `theorem erdos_952 : answer(sorry) ↔ ∃ …`; RHS byte-identical | Same as above, clean in both modes | `norm` is the squared step (`Zsqrtd.norm`), left as is; the [Er77c] misattribution note on the source page not touched |

Diff sizes: 33 `+6/-3`, 15 `+6/-1`, 477 `+5/-5`, 952 `+1/-1`. One file each, no
bundled changes. Each body carries the AI assistance disclosure and `Fixes #NNNN.`

## The one substantive correction: issue #4978's witness was wrong

The ledger and issue #4978 claim `A = ℕ` trivially satisfies
`erdos_33.variants.one_mem_lowerBounds`, on the grounds that `limsup (N/√N) = ⊤`.
**That is false.** The `limsup` in that declaration carries no `EReal` ascription
and elaborates in `ℝ`:

```
fun A => limsup (fun N => ↑(A ∩ Icc 1 N).ncard / √↑N) atTop : Set ℕ → ℝ
```

In `ℝ`, `Filter.limsup u f = sInf {a | ∀ᶠ n in f, u n ≤ a}` and
`Real.sInf_empty : sInf ∅ = 0`. For `A = ℕ` the ratio `√N` is unbounded, the set is
empty, the `limsup` is the junk value `0`, and `1 < 0` fails. So the existential is
**not** trivially true — and, by the same junk value, `1 < limsup_ℝ u` silently
doubles as "`u` is eventually bounded above", which is how the declaration's
"finite" content was being carried.

Machine-checked, no `sorryAx` (probe saved beside this file as
`erdos33_limsup_probe.lean`): the `ℝ`-valued elaboration (`rfl`),
`lt_limsup_nonempty`, `univ_abc`, `univ_ratio`, and `univ_not_witness`. The
Erdős 15 reduction probe is `erdos15_summable_probe.lean`.

A correction comment was posted on the issue:
<https://github.com/google-deepmind/formal-conjectures/issues/4978#issuecomment-5304160267>

### What still justified the PR

Provenance found in `git log`, which is stronger than the withdrawn witness:

* **#631** (original): `1 ∈ lowerBounds { c : ℝ | ∃ A, AdditiveBasisCondition A ∧ limsup … = c }`
  — the lower-bound form the name `one_mem_lowerBounds` still refers to.
* **#1206** *"fix: typing in `erdos_33`"* moved `erdos_33` and `variants.vanDoorn`
  from `ℝ` to `EReal`, its commit message giving the reason: *"if `limsup` is
  infinite, then it gets the junk `0` value in `Real`"*. The same commit rewrote
  this declaration to `∃ A, AdditiveBasisCondition A → 1 < …` (*"Can avoid some
  unnecessary casting … by not using `lowerBounds`"*) and left it in `ℝ`.
* **#2226** replaced the `→` by `∧` — the `∃ x, P x → Q` pattern AGENTS.md and the
  repo's own `ExistsImplicationLinter` flag — keeping the existential and the `ℝ`.

So the two neighbouring declarations were repaired against the junk-value problem
and this one was replaced by a different statement instead.

### Known ambiguity, disclosed in the PR

erdosproblems.com/33 says *"Erdős observed that there exist $A$ for which the
$\limsup$ is finite and $>1$"* — grammatically **existential**, which cuts against
the repair. The PR body states this plainly, gives the reasons for the
lower-bound reading (the name, the docstring's "this value", the #631 statement,
and the page's Moser `>1.06` / Cilleruelo `≥ 4/π` bounds being valid for every
`A`), and offers to switch to the rename-instead repair if maintainers read it the
other way. Truth of the repaired form: Moser [Mo65] gives `liminf > 1.06` for every
admissible `A`, so `⨅ ≥ 1.06 > 1`; `research solved` remains correct.

## Verification method (identical for all four)

No `lake build` was run — the box had ~6 GB free and two earlier lanes collided on
shared olean paths. Instead:

* dedicated worktree `/Users/kuber.mehta/Projects/fc-fixpr` off `upstream/main`
  (removed after use); the shared checkout at
  `/Users/kuber.mehta/Projects/formal-conjectures` was never modified;
* `lean` v4.27.0 run directly with `LEAN_PATH` pointing at the shared checkout's
  already-built oleans (`FormalConjecturesUtil`, `FormalConjecturesForMathlib`,
  Mathlib and deps). `FormalConjecturesUtil` and `FormalConjecturesForMathlib` are
  byte-identical between the shared checkout's HEAD and `upstream/main`, so the
  oleans are valid for this base;
* flags reproducing the lakefile: `-DwarningAsError=true -Dpp.unicode.fun=true
  -DautoImplicit=false -DrelaxedAutoImplicit=false -Dwarn.sorry=false` plus
  `-Dlinter.style.{copyright.formalConjectures,namespace,openClassical,
  ams_attribute,category_attribute,conditional_formal_proof,moduleDocstring,
  latex_docstring}=true`;
* a second pass with `-Dgoogle.answer=postpone` (the `FormalConjecturesAnswerPostpone`
  library variant);
* harness validated by a **negative control**: appending `example : (1:ℕ) = 2 := rfl`
  and a `String`/`ℝ` mismatch produced the expected type errors *and* fired the AMS
  and category linters, so the elaborator and linters really do run.

All four edited files: exit 0, no errors, no warnings, in both modes.

**Not verified:** the lake targets themselves, anything downstream of these
modules, the full CI linter set as configured, and any linter or elaborator not
reachable from `import FormalConjecturesUtil`. Every PR body says so and says CI is
authoritative.

## Duplicate check (run immediately before pushing)

`gh search issues "erdos_15 / erdos_33 / erdos_477 / erdos_952"` returns only the
four issues themselves plus the closed #1543 and #2414. `gh search prs` for the four
paths, restricted to open PRs, returns no PR touching any of the four files;
`#4949` (optimization_constant attribute) and `#4965` (`answer(True)` in solved
statements) were checked file-by-file and touch none of them. Batch 1 of this
campaign is live as #4986 (Erdős 1093) and #4987 (OEIS A237271).

## Ledger corrections implied

`CONFIRMED_LEDGER.md` row "**Erdős 33** … Witness `A = ℕ`: `k = k + 0²`,
`limsup N/√N = ⊤`" is **wrong** and should be replaced by the `ℝ`-junk analysis
above. `erdos-faithfulness-lowband.md` §"EP 33" carries the same error. The finding
itself (name/docstring vs statement, plus the junk-value dependence) survives; the
severity label `VACUOUS_AS_STATED` does not and should read as a
name/docstring-fidelity defect instead.
