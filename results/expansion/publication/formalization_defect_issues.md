# Upstream formalization-defect issues — 2026-08-15

Authorization: explicit, this campaign turn, for upstream **issues only** (no PRs,
no releases). Every item below is a **formalization defect** — a statement about
what a Lean declaration in `google-deepmind/formal-conjectures` asserts. **None is
a counterexample to the underlying mathematics**; in several cases the literal
declaration is trivially *true*. This is recorded explicitly in each issue body.

Source of truth: `../live-search-2026-08-15/CONFIRMED_LEDGER.md`.

## Pins and identity

| item | value |
|---|---|
| upstream `main` at write time | `638da20efd8eeeed2993fc2550fc596dc90c1ce8` (2026-08-15 09:23:12Z, "Mark OEIS A105565 as solved (#4958)") |
| ledger pin (superseded, re-verified against current main) | `2411d22e1bd550d050d0eac6c1fb379a76a3e7c5` |
| `c5-k4` audit commit used for immutable links | `214325f5962530512b32f31e9e3f63648496f886` (branch `catchup-parity-packed-freeze`, already on origin) |
| git identity | Kuber Mehta <kuberhob@gmail.com>, GitHub `Kuberwastaken` |

## Duplicate gate — method

The GitHub search API rate-limited after ~20 queries, so the gate was run
**offline against a full corpus snapshot**: `gh issue list --state all --limit 6000`
(**1734 issues**) and `gh pr list --state all --limit 6000 --json …,files`
(**3226 PRs, with per-PR file lists**), then regex-matched on title, body **and**
changed file path. Script: `scratchpad/dupgate.py` (session-local).

Additionally, for every item:

- read #4896, #4923, #4927 in full (the three live audit trackers) — none lists
  any of items 1–8;
- read #4922 in full for item 9;
- `git log` / `git show` on each target file at current `upstream/main`;
- checked every **open** PR whose file list touches a target file. Only four do —
  #4688 and #4198 (module/import chores; no statement hunks), #4004 and #4003
  (docstring LaTeX normalisation). None repairs any defect reported here.
- re-listed issues and PRs updated since 2026-08-14 immediately before writing;
  nothing new collides.

Timing note: PR **#4964** (A103425) landed mid-run on 2026-08-15 on a target the
OEIS lane was triaging, confirming the surface moves daily. Items 1–3 were posted
first, before drafting 4–8, to reduce that exposure.

## Re-verification performed this turn

Every declaration was re-read **verbatim at `638da20e`**, not at the ledger pin.
All eight are unchanged from the ledger's transcription.

Independent recomputation (`scratchpad/reverify.py`, own code path):

- **A237271** — `a(n)` reproduces the OEIS **b-file** exactly for `n = 1..2000`
  (the encoding is faithful; the defect is only in the hypothesis). No `k ≤ 20000`
  satisfies the Lean hypothesis. Carmichael `k ≤ 20000`: `561, 1105, 1729, 2465,
  2821, 6601, 8911, 10585, 15841` with `a(k) = 5,6,4,6,6,6,7,7,8`, **min 4 ≥ 3**,
  so the OEIS observation is *not* refuted.
- **1093** — `C(7,3)`: 1 vs 0; `C(23,5)`: 1 vs 0; `C(47,11)`: 4 vs 3 under
  `p ≤ k` vs `p < k`. All three eligible (`2k ≤ n`, no prime `≤ k` divides the
  coefficient). Separating values `6`, `20`, `44`; all have `k` prime.
- **1055** — least prime with `IsOfClass r`: `2, 2, 37, 73, 1021` vs A005113
  `2, 13, 37, 73, 1021`. Mismatch **only at `r = 2`**. The 16 primes `< 500` where
  `IsOfClass 2` disagrees with "class exactly 2" are exactly the class-1 primes.

Link gate: all 12 planned URLs (3 c5-k4 audit blobs, 9 upstream blob anchors)
returned **HTTP 200** and the line ranges were read back and confirmed to frame the
intended declarations.

## Results

| # | target | gate outcome | result |
|---|---|---|---|
| 1 | OEIS A237271 `observation_carmichael` | **CLEAR** — 0 issue hits; only PR #4924 (merged) touches the file, and it changes `conjecture_4`/`conjecture_5` only. Absent from #4896/#4923/#4927 | [#4974](https://github.com/google-deepmind/formal-conjectures/issues/4974) |
| 2 | Erdős 1093 `deficiency` | **CLEAR** — `smoothNumbers` matches only PR #1668 and the introducing PR #1328; no issue/PR raises the `<`/`≤` threshold | [#4975](https://github.com/google-deepmind/formal-conjectures/issues/4975) |
| 3 | Erdős 1055 `IsOfClass` | **CLEAR** — `IsOfClass` matches only the introducing PR #1197; `A005113` 0 hits; definition never revised | [#4976](https://github.com/google-deepmind/formal-conjectures/issues/4976) |
| 4 | Erdős 40 `erdos_40` | **CLEAR** — `Erdos40ForSet` 0 hits; only closed bot PRs on `variants.known_result` | [#4977](https://github.com/google-deepmind/formal-conjectures/issues/4977) |
| 5 | Erdős 33 `.variants.one_mem_lowerBounds` | **CLEAR** — `one_mem_lowerBounds` 0 hits. #4923's Erdős 33 bullet covers the *headline* `answer`-hole self-answer only; issue states this distinction explicitly and does not re-report the headline | [#4978](https://github.com/google-deepmind/formal-conjectures/issues/4978) |
| 6 | Erdős 15 `erdos_15` | **CLEAR** — no issue/PR on the `Summable` reading. #4896's "PR #4660 `tsum` without `Summable`" is the opposite defect | [#4979](https://github.com/google-deepmind/formal-conjectures/issues/4979) |
| 7 | Erdős 477 index set | **CLEAR** — no issue/PR raises the `{n \| 0 < n}` divergence | [#4980](https://github.com/google-deepmind/formal-conjectures/issues/4980) |
| 8 | Erdős 952 asserted direction | **CLEAR** — only #1031 (closed intake) and #2978 (closed bot proof) | [#4981](https://github.com/google-deepmind/formal-conjectures/issues/4981) |
| 9 | Erdős 142 headline + `.variants.three` | **PARTIAL DUPLICATE** — #4922 (open) covers `.variants.upper`; #4923 lists the pattern for EP 422/539/789 but not EP 142. Handled as a comment, per instruction, not a new issue | [comment on #4922](https://github.com/google-deepmind/formal-conjectures/issues/4922#issuecomment-5303863018) |
| — | status syncs (1084, 1106, 1054, 36, 44, 60, A357513) | **DROPPED — verification gate, not duplicate gate** (see below) | not posted |

### Provenance recovered while writing (new, in the issue bodies)

- **1093**: PR #1328's first commit defined `IsKSmooth k n := ∀ p, p.Prime → p ∣ n → p ≤ k`
  correctly; a review suggestion replaced it with `smoothNumbers k`. The `≤`→`<`
  change was never discussed; later fixes #1489 and #1532 did not touch it.
- **477**: the file originally used `Set.range f.eval`. #1242 replaced it with
  `f.eval '' {n | 0 < n}` **and** changed the docstring to `n > 0`. #1510 then
  re-synced the docstring to the site's `b ∈ {f(n) : n∈ℤ}` — explicitly "update to
  the new statement from erdosproblems.com/477" — while carrying the one-sided
  index set into every declaration it added. That is why docstring and code now
  contradict each other inside the same declaration.

## Why the status-sync bundle was dropped

The bundle's premise is "the declaration lags its **source**", so each item needs
the live primary source. erdosproblems.com was **not reachable** from this host
this turn:

- `curl` and WebFetch both receive the Cloudflare interstitial / HTTP 403;
- the headless-browser skill could not bind a port (9400–9409) in this sandbox;
- WebFetch is blocked from `web.archive.org`.

The offline mirror `teorth/erdosproblems@data/problems.yaml` (the community
database behind the site) still records **all** of 15, 33, 36, 40, 44, 60, 142,
477, 952, 1054, 1055, 1084, 1093, 1106 as `status: open`, which **contradicts**
several ledger claims (e.g. 1054 "site records Tao's disproof", 36 "site now
records `c < 0.380876`"). Either the mirror lags the site or the ledger entries
need re-reading; both possibilities require the live page to settle.

Posting an unverified "this is already solved" claim upstream is the costly
direction of error, so the bundle is held. It is **not** blocked by duplicates:
the offline corpus scan found no dedicated issue for any of the seven, and #4952
("Erdős Problem 506: status mismatch") shows individual status-mismatch issues are
welcome. Re-run when erdosproblems.com is reachable.

One partial exception worth noting for the re-run: `erdos_60.variants.two_copies`
is tagged `research solved` while its own docstring says Erdős and Simonovits
**conjectured** it, and unlike its sibling `variants.he_ma_yang` it carries no
citation. That inconsistency is visible in-repo, but confirming it is a *mis-tag*
still needs the site.

## Notes

- Labels could not be applied: `AddLabelsToLabelable` requires repository write
  access (HTTP 403 for an outside contributor). Maintainers apply the
  `misformalization` label. All bodies follow the repo's
  `misformlization_report.md` section shape, extended with the
  `UPSTREAM_PROTOCOL.md` order (Summary → Proof → Suggested fix → campaign
  relationship + immutable links → Source/status note → AI assistance disclosure).
- Every issue carries an explicit sentence that the underlying mathematical
  question is unaffected, and an AI assistance disclosure.
- No PRs were opened in this lane. No release was drafted; none of these findings
  is release-eligible under `UPSTREAM_PROTOCOL.md`, which is for counterexamples.

## Upstream submissions, 2026-08-15

- **A110854** — issue [#4982](https://github.com/google-deepmind/formal-conjectures/issues/4982), PR [#4983](https://github.com/google-deepmind/formal-conjectures/pull/4983) (`answer(False)` with a complete in-repo proof, plus `conjecture.variants.oeis_question` preserving the real OEIS question). Build note: a full `lake build` was NOT run (the box lacked disk for a from-source Mathlib build); the file was type-checked with `lean -DwarningAsError=true` against existing package oleans, exit 0, axioms `[propext, Classical.choice, Quot.sound]`, no `sorryAx`. CI is the authoritative check.
- **Eight formalization-defect issues** [#4974–#4981](https://github.com/google-deepmind/formal-conjectures/issues/4974) plus a comment on #4922.

- **A108864** — issue [#4984](https://github.com/google-deepmind/formal-conjectures/issues/4984), PR [#4985](https://github.com/google-deepmind/formal-conjectures/pull/4985). Repair shape (b) chosen: fix the encoding to A109883 and keep the declaration `research open`, per AGENTS.md ("if they disagree, the Lean is incorrect") and precedent PR #4933; option (a) `answer(False)` would have recorded a refutation of a conjecture that has not been refuted. Build: `lake --wfail build` exit 0, warning-clean, 8055/8055 (after `lake exe cache get`).

## Review round: PR #4986 (Erdős 1093) — corpus-wide `smoothNumbers` audit

mo271: *"We should check if the same mistake has been made in other places where
`smoothNumbers` are used!"* Audited at upstream `main`.

**Result: 1093 is the only instance.**

| Location | Uses | Verdict |
|---|---|---|
| `ErdosProblems/961.lean` | `Nat.smoothNumbers (k + 1)` | **Correct.** `< k+1` is `≤ k`, so `∉ smoothNumbers (k+1)` = "has a prime factor `> k`", matching the source ("integer divisible by a prime `> k`"). Already compensates for the Mathlib convention |
| `ErdosProblems/369.lean` | `∀ p ∈ primeFactors, (p:ℝ) ≤ n^ε` | Bound written directly; no convention involved |
| `ErdosProblems/648.lean` | largest prime factor | different notion |
| `ErdosProblems/851.lean` | `primeFactors.card ≤ r` | *number* of prime factors, different notion |
| `Millenium/Poincare.lean` | `SmoothConjectureFor` | differential topology, unrelated |

**One prose nit reported, not a defect**: 961's `sylvester_schur` docstring says
"divisible by a prime greater than $k$, i.e. not $(k+1)$-smooth". Under the
standard convention ($k$-smooth = every prime factor $\le k$) that should read
"not $k$-smooth". The Lean is correct; only the sentence is loose. Offered as a
one-word fix pending the maintainer's preference — not pushed unasked into a
file outside the PR's scope.

[Reply](https://github.com/google-deepmind/formal-conjectures/pull/4986#issuecomment-5307907971)
