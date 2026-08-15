# OEIS A110854 — upstream submission record

Target: `google-deepmind/formal-conjectures`, `FormalConjectures/OEIS/110854.lean`,
declaration `conjecture` (`@[category research open, AMS 11]`).

Classification: `NEW_FORMALIZED_READING_DISPROOF`. The **formalized statement**
is false. The **OEIS question** (does `{|a(n)|}` cover A004275?) is untouched
and remains open.

Date: 2026-08-15. Submitter identity: `Kuber Mehta <kuberhob@gmail.com>`.

---

## 1. Result

Declaration under audit:

```lean
noncomputable def a (n : ℕ) : ℤ :=
  let p (k : ℕ) : ℤ := (Nat.nth Nat.Prime (k - 1)).cast
  if n = 0 then 0
  else p (2 * n + 2) - p (2 * n + 1) - p (2 * n) + p (2 * n - 1)

@[category research open, AMS 11]
theorem conjecture :
  ∀ d > 0, (∃ p1 p2 : ℕ, p1.Prime ∧ p2.Prime ∧ d = (p1 - p2 : ℤ).natAbs) →
  ∃ n > 0, d = (a n).natAbs
```

Counterexample `d = 3`:

- hypothesis holds — `3 > 0`, `p1 = 5`, `p2 = 2` prime, `(5 - 2 : ℤ).natAbs = 3`;
- `a 1 = 7 - 5 - 3 + 2 = 1`;
- for `n ≥ 2` the indices `2n-1, 2n, 2n+1, 2n+2` are all `≥ 3`, so all four
  primes are odd, and `odd - odd - odd + odd` is even;
- hence `{(a n).natAbs : n > 0} ⊆ {1} ∪ 2ℕ`, and `3` is in neither.

Further witnesses: every `d = p - 2` with `p` an odd prime `> 3`, i.e.
`d = 5, 9, 11, 15, 17, 21, 27, 29, 35, …`.

Root cause: the only A110854 comment asks "Do the absolute values cover
A004275?", and A004275 is "1 together with the nonnegative even numbers". The
formalization replaced that hypothesis by "`d` is an absolute difference of two
primes", which is strictly weaker, making the declaration strictly stronger than
its source. The file docstring's claim "A004275 is the set of all differences
between two prime numbers" is incorrect and is the likely origin of the defect.

---

## 2. Duplicate gate — PASS

Re-run immediately before the write, 2026-08-15, against upstream HEAD
`638da20efd8eeeed2993fc2550fc596dc90c1ce8` ("Mark OEIS A105565 as solved (#4958)").

| Query | Scope | Result |
|---|---|---|
| `gh search issues "110854" --include-prs` | open+closed+merged | 1 hit: PR #4450 (merged, the AutoOeis batch that created the file) |
| `gh search prs "110854"` | open+closed+merged | same single hit, #4450 |
| `gh search issues "A110854" --include-prs` | all | 0 hits |
| `gh search issues "A004275" --include-prs` | all | 0 hits |
| `gh search issues "OeisA110854" --include-prs` | all | 0 hits |
| `gh search issues "110854.lean" --include-prs` | all | 1 hit, #4450 |
| `git log upstream/main -- FormalConjectures/OEIS/110854.lean` | file history | single commit `d7032450` (#4450) |

Tracker issues read in full: **#4896** (Tracking: possible misformalizations
found in statement audits), **#4923** (Possible misformalizations II), **#4927**
(Open statements with known solutions). None mentions A110854, A004275, or this
file.

Open PR sweep over recent OEIS-touching PRs (#4946–#4972 plus #4450, #4953,
#4963): none touches `FormalConjectures/OEIS/110854.lean`. PR #4964, the
mid-run arrival that motivated re-checking, is A103425 and unrelated.

Verdict: **novel, apparently unclaimed.** Submission proceeded.

---

## 3. Artifacts (immutable, all HTTP 200 verified)

c5-k4 commit: `e4e95c3e3adda9dd91cd3e077ec30b0fccb543f9`
(branch `catchup-parity-packed-freeze`, pushed).

| Artifact | URL |
|---|---|
| Source audit + witness derivation | https://github.com/Kuberwastaken/c5-k4/blob/e4e95c3e3adda9dd91cd3e077ec30b0fccb543f9/results/expansion/live-search-2026-08-15/oeis-hunt-part1.md#L203-L272 |
| Ledger entry | https://github.com/Kuberwastaken/c5-k4/blob/e4e95c3e3adda9dd91cd3e077ec30b0fccb543f9/results/expansion/live-search-2026-08-15/CONFIRMED_LEDGER.md#L29 |
| Independent verifier (sieve) | https://github.com/Kuberwastaken/c5-k4/blob/e4e95c3e3adda9dd91cd3e077ec30b0fccb543f9/results/expansion/live-search-2026-08-15/scripts/part1/c110854.py#L1-L24 |
| No-`sorry` Lean certificate | https://github.com/Kuberwastaken/c5-k4/blob/e4e95c3e3adda9dd91cd3e077ec30b0fccb543f9/lean/OeisA110854Disproof.lean#L1-L163 |

Verifier output (primes to `4·10⁶`): `a(1..12) = [1, 0, 0, 4, 0, -4, 4, -4, 2,
2, 0, -2]` matching the published DATA exactly; the only `n > 0` with `a n` odd
is `n = 1`; no `n` in range with `|a n| = 3`; the set of odd `|a n|` values is
`{1}`.

---

## 4. Upstream issue — POSTED

https://github.com/google-deepmind/formal-conjectures/issues/4982

Title: `OEIS A110854: conjecture is false as formalized (d = 3); the A004275 question is untouched`

Body archived at `oeis_110854_issue_body.md` in this directory. Sections follow
`UPSTREAM_PROTOCOL.md`: Summary, Counterexample, Relationship to the C₅[K₄]
campaign, Independent verifier, Complete formal certificate, Source/status note,
AI assistance disclosure.

---

## 5. Lean branch — READY, NOT PUSHED

Branch `disprove-oeis-110854` in `/Users/kuber.mehta/Projects/formal-conjectures`,
based on upstream/main `638da20e`. Single commit
`7b3f3d7605959915b06b12f540bf027c589ed0e2`, author `Kuber Mehta
<kuberhob@gmail.com>`, no co-author trailer.

Committed from a `git worktree` at
`<scratchpad>/fc-110854` because a sibling agent session held the main checkout
on branch `fix-oeis-108864-encoding` with an active `lake build`.

The change:

1. `conjecture` → `@[category research solved, AMS 11]`, `answer(False) ↔ …`,
   with a complete in-repo proof (no `formal_proof` link, nothing external);
2. three new `@[category API, AMS 11]` lemmas — `odd_nth_prime`, `a_add_two`,
   `even_a`;
3. docstring corrected (A004275 is *not* the set of prime differences) and the
   counterexample recorded;
4. new `conjecture.variants.oeis_question`, `@[category research open, AMS 11]`,
   `answer(sorry) ↔ ∀ d : ℕ, (d = 1 ∨ Even d) → ∃ n > 0, d = (a n).natAbs`,
   preserving the actual OEIS question in the file.

### Build status — honest

`lake --wfail build 'FormalConjectures.OEIS.«110854»'` was **NOT** run to
completion, and no such claim is made anywhere in the issue or the PR body.

Reason: `FormalConjecturesUtil` does `public import Mathlib`, so the module
requires all 7516 Mathlib modules. The local cache held ~1500 built oleans, the
box had ~2 GB free disk against the ~8–12 GB a full source build needs, and a
sibling agent session was concurrently building the same package tree in the
same working directory. A baseline build was started and killed after it was
found to be racing with the sibling process on identical olean output paths.

What **was** run, on the exact committed file content, transformed mechanically
(no hand transcription):

```
lean -DwarningAsError=true   # Lean 4.27.0, Mathlib v4.27.0, LEAN_PATH over the
                             # existing package oleans; read-only, no lake
```

with `answer(False)` → `False` and the `@[category …]` attributes stripped, both
of which require `FormalConjecturesUtil`. Result: **exit 0, warning-clean**, and

```
'OeisA110854.conjecture'     depends on axioms: [propext, Classical.choice, Quot.sound]
'OeisA110854.even_a'         depends on axioms: [propext, Classical.choice, Quot.sound]
'OeisA110854.a_add_two'      depends on axioms: [propext, Classical.choice, Quot.sound]
'OeisA110854.odd_nth_prime'  depends on axioms: [propext, Classical.choice, Quot.sound]
```

No `sorryAx`, no `native_decide`, no project-specific axiom. `answer(False)`
elaborates to `False`, so the proposition proved is exactly the upstream
statement.

Separately, `conjecture.variants.oeis_question` was elaborated with
`answer(sorry)` → `(sorry : Prop)` and type-checks with the intended statement,
emitting only the expected `declaration uses 'sorry'` warning.

Not exercised by any of the above, and therefore still unverified:

- the `answer()` elaborator itself and the `@[category …]`/`AMS` attribute
  elaboration;
- the repository's own linters (AMSLinter, AnswerLinter, CategoryDocstringLinter,
  LatexDocstringLinter, NamespaceLinter, …), though the file was checked by hand
  against each linter's rule — no line exceeds 100 characters, no trailing
  whitespace, docstrings use `$ … $` and contain no `\[ \]` or `\( \)`, AMS tags
  are single-valued, and no `answer(…) ↔` theorem carries binders before the
  colon;
- the full-project build.

Per `UPSTREAM_PROTOCOL.md` and the standing instruction, the branch is therefore
left **unpushed** pending a real `lake --wfail build` on a machine with adequate
disk.

---

## 6. PR — NOT OPENED

Deliberately left for review. Body archived at `oeis_110854_pr_body.md` in this
directory. Exact command, to be run after pushing the branch and after a real
`lake --wfail build` passes:

```bash
cd /Users/kuber.mehta/Projects/formal-conjectures
git push -u origin disprove-oeis-110854
gh pr create \
  --repo google-deepmind/formal-conjectures \
  --base main \
  --head Kuberwastaken:disprove-oeis-110854 \
  --title "OEIS A110854: disprove the formalized conjecture, restate the OEIS question" \
  --body-file results/expansion/publication/oeis_110854_pr_body.md
```

(the `--body-file` path is relative to the `c5-k4` checkout; use the absolute
path `/Users/kuber.mehta/Projects/c5-k4/results/expansion/publication/oeis_110854_pr_body.md`).

The PR body closes the issue with `Fixes #4982.`

---

## 7. Environment note

Disk on `ai-vps` fell from 6.8 GB to ~2.0 GB free during this session, driven by
the sibling lane's from-source Mathlib build in
`/Users/kuber.mehta/Projects/formal-conjectures/.lake`. A full Mathlib source
build there will exhaust the disk. `lake exe cache get` (oleans only, no `.c`
IR) is the cheaper route, but even that is tight at the current free space.
