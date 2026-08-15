# KitaKen1 — activity analysis (google-deepmind/formal-conjectures)

**Subject:** GitHub user `KitaKen1` — <https://github.com/KitaKen1>
**Analysis date:** 2026-08-15 (data pulled ~20:00Z)
**Method:** `gh api` over `search/issues`, `repos/.../issues`, `repos/.../pulls`, `users/KitaKen1/{repos,events/public}`. Read-only; no interaction of any kind.

---

## 0. Identity card

| Field | Value |
|---|---|
| Login | `KitaKen1` (id 114803503) |
| Real name (self-declared in PR bodies) | **Kenta Kitamura** |
| Bio | `Kenta Kitamura / Intellectual Moonshine` |
| Account created | **2022-10-01** |
| Public repos | **63** |
| Followers / following | 5 / 0 |
| Company / blog / location / email | all empty |
| Org affiliation | **Not** a public member of `google-deepmind` (HTTP 404) |
| `author_association` on all 53 FC items | **`CONTRIBUTOR`** (never MEMBER/COLLABORATOR) |

**Inference:** an unaffiliated outside contributor, not a DeepMind employee and not a repo collaborator. The account predates this work by three years but shows essentially no math activity before 2026-05.

---

## 1. Volume and timeline

### Totals in `google-deepmind/formal-conjectures`

| Metric | Count |
|---|---|
| Total items (issues + PRs) | **53** |
| Pull requests | **38** |
| — merged | **15** |
| — closed unmerged | **2** (both Feb 2026, superseded by their own #2177) |
| — still open | **21** |
| Issues | **15** |
| — closed | 4 |
| — open | 11 |
| Merge rate, all PRs | **39.5%** |
| Merge rate, *decided* PRs (merged ÷ (merged + closed-unmerged)) | **88.2%** |

Period: **2026-01-30 → 2026-08-15** (~6.5 months), but see the cadence — it is not uniform.

### Cadence — a dormant start, then a hard burst

| Month | Items opened |
|---|---|
| 2026-01 | 2 |
| 2026-02 | 3 |
| 2026-03 | 0 |
| 2026-04 | 0 |
| 2026-05 | 0 |
| 2026-06 | 0 |
| 2026-07 | 10 |
| **2026-08 (to the 15th)** | **38** |

Per-day, August:

```
2026-08-01  ##      2
2026-08-03  #       1
2026-08-10  #####   5
2026-08-11  #####   5
2026-08-12  #####   5
2026-08-13  ####### 7
2026-08-14  ##      2
2026-08-15  ####### ####  11
```

**This is a burst, not a sustained baseline.** 38 of 53 items (72%) land in the last 15 days; 30 of 53 (57%) in the last 6 days. There is a five-month total gap (Mar–Jun 2026) with zero activity in this repo.

### Corroborating signal — personal artifact repos

Every finding gets its own dedicated public repo. Repo creation dates track the same curve:

| Month | Repos created |
|---|---|
| 2024-06 | 2 (unrelated — brain-organoid topics) |
| 2026-02 | 1 (`formal-conjectures` fork) |
| 2026-05 | 7 |
| 2026-06 | 11 |
| 2026-07 | 13 |
| **2026-08** | **29** |

**11 repos created on 2026-08-15 alone**, all OEIS:
`oeis-a100478-eventual-periodicity`, `oeis-a105801-lean`, `oeis-a112970-formal-conjectures`, `oeis-a113249-family-square-terms-lean`, `oeis-a103425-prime-free`, `erdos-357-additional-targets`, `oeis-a114831-asymptotic`, `oeis-a102371`, `oeis-102722-asymptotic`, `oeis-108306`, `oeis-a112521-formal-conjectures`.

### Relative standing (since 2026-08-01)

| User | PRs | merged | Issues |
|---|---|---|---|
| `williamjblair` | **66** | **50** | 17 |
| `KitaKen1` | 25 | 10 | 13 |
| `mo271` (maintainer) | 14 | 6 | 20 |
| `Kuberwastaken` (us) | 8 | 0 | 18 |
| `bocowgill` | 4 | 1 | 3 |

**KitaKen1 is prolific but is *not* the highest-volume contributor.** `williamjblair` is running ~2.6× their PR volume with a 76% merge rate. Noted as a separate competitor worth its own analysis.

---

## 2. Composition

### By kind (n=53)

| Kind | Count | Share |
|---|---|---|
| Proof + status flip (`research open` → `research solved`) | 29 | 55% |
| Misformalization / defect reports | 6 | 11% |
| Disproofs / counterexamples | 5 | 9% |
| Tracker / meta issues | 2 | 4% |
| Other (statement additions, proposals, status syncs) | 11 | 21% |

**The dominant mode is not defect-hunting — it is solving.** 55% of their output is "I proved the open target; flip it to solved." The misformalization tracker issues that made them visible to us are a *minority* of their work (11%).

### By corpus (primary corpus per title)

| Corpus | Items |
|---|---|
| Erdős Problems | 12 |
| **OEIS** | **12** |
| Arxiv / Paper | 5 |
| WOWII | 4 |
| Green's Open Problems | 3 |
| MathOverflow | 2 |
| Wikipedia | 2 |
| Other (quantum graphs, weak tiling, Lonely Runner, optimization) | 13 |

**Critical trend:** OEIS is a *recent pivot*. Their first OEIS item is #4924 on **2026-08-13**. All 12 OEIS items are from the last 3 days. They are moving into the OEIS corpus right now, at ~11 targets/day.

### Representative sample read in full (12 items)

| # | Type | Shape of the finding |
|---|---|---|
| #4924 | PR, **merged** | OEIS A237271 `conjecture_4`/`conjecture_5`: parity at square and hexagonal indices. Genuine proof, external repo, kernel-checked. |
| #4953 | PR, open | OEIS A113019 disproof: OEIS asks "n=1 and 32 are fixed points. Are there any others?" — finds `387420489 = 9^9` as a third fixed point. `answer(sorry)` → `answer(False)`. |
| #4964 | PR, open | OEIS A103425: proves prime-free weighted Tribonacci exists via the **constant sequence** `x(n)=4`. A degenerate-witness solve. |
| #4892 | Issue, open | Erdős 319 `isBigO`: docstring asks for *simplest* `g`, Lean only checks *some* upper bound. `g(N)=N` works trivially. |
| #4919 | Issue, open | Erdős 688 `upper_bound`: `answer(sorry)` accepts any comparison function; `fun _ ↦ 1` closes it. Does not prove `ε = o(1)`. |
| #4922 | Issue, open | Erdős 142 `variants.upper`: admits trivial linear answer `N`. *(We commented on this issue at 2026-08-15T19:27 with two further `=Θ` reflexive instances in the same file.)* |
| #4867 | Issue, closed | Erdős 80: both open statements quantify over all `c > 0`; at `c = 2` you'd need `2n²` edges but max is `n(n-1)/2`, so `f 2 n = 0` and both are `False`. |
| #4851 | Issue, closed | Wikipedia/MovingSofa: uniqueness quantifies over *every* planar set, not just moving sofas. "Remove one point from `gerversSofa`" breaks it. |
| #4859 | Issue, closed | Wikipedia/SquarePacking: `Circle (r : ℝ)` defined via `r ^ 2` admits negative radii, so no least radius exists. Affects 2 of 5 open declarations. |
| #4854 | Issue, open | Green 14: 20 AKS14 lower bounds labelled `research open`/"Conjectured" but the paper presents them as established with Appendix A certificates. Pure status-sync finding. |
| #4855 | Issue, open | Erdős 973: solved negatively by Luo–Yang–Zhu (arXiv:2607.22017); should be `answer(False)` + `research solved`. Literature-sync finding. |
| #4657 | PR, open | Convex additive-VC₂ bound in ℝ³: six-halfspace counterexample, replaces the theorem with its negation. Notes a prior attempt in a fork "whose Lean CI did not pass". |

**Shape summary:** the defect findings are overwhelmingly *type-level and quantifier-level*, not deep mathematics — negative radii admitted by `r^2`, unrestricted `∀ c > 0`, `answer(sorry)` holes that accept the left-hand side, vacuous hypotheses over empty fibres. The proofs, by contrast, are real Lean developments.

---

## 3. Method

### 3a. They disclose AI assistance on essentially every item

This is stated explicitly and consistently. Verbatim examples:

> **AI Usage Disclosure:** This formalization was assisted by ChatGPT 5.6 sol and Codex GPT 5.6 sol with xhigh reasoning.
> — #4954, #4957, #4959 (and near-identical text on most OEIS PRs)

> **AI Usage Disclosure:** This formalization was developed with assistance from OpenAI Codex, using GPT-5.6 sol.
> — #4953, #4967

> **AI Usage Disclosure:** This formalization and PR preparation were assisted by OpenAI Codex.
> — #4964

> The proof and write-up were prepared with AI assistance, as disclosed in the external repository README.
> — #4426

On the *tracker* issues the disclosure is different and more revealing:

> ## Caveat
> This list was organized with **AI assistance from my long working notes** and may contain transcription or interpretation errors.
> — #4923

> This list was organized with AI assistance from long working notes and may contain transcription or interpretation errors. Please treat the entries as **triage leads** until each one has been checked against the source and current Lean statement.
> — #4896

> This list was prepared with AI assistance and may contain mistakes.
> — #4927

**Inference:** the pipeline is *human working notes → LLM organization → issue text*, not *LLM scan → issue text*. The phrase "my long working notes" implies the finding happens upstream of the AI step; the AI is doing write-up and triage formatting. That is a materially different claim from "a script found these."

### 3b. No tooling is described — but the findings are visibly pattern-clustered

They **never** describe a script, scanner, linter, or automated sweep. There is no mention of grep, regex, CI hooks, or a query harness anywhere in their 53 items. The single "linter" reference in their threads is **not theirs** — mo271 wrote it:

> @KitaKen1 wrote a linter to catch the thing I'm complaining about here automatically: #4962
> — mo271 on #4953

(PR #4962 `feat(FormalConjecturesUtil): linter against sorry-free formal_proof` — `author = mo271`. This is mo271 telling KitaKen1 "*I* wrote a linter", not the reverse.)

However, #4923 is organised *by defect pattern*, which is exactly what a systematic scan would produce:

- **"Exact self-answers"** — Erdős 33, 329, 348, 409(iii). Pattern: *the entire unknown expression can be copied into `answer`, so the theorem closes by `rfl`.*
- **"Reflexive asymptotic answers"** — Erdős 422, 539, 789. Pattern: *the target function itself can be used as the Big-O/Big-Θ answer; `isBigO_refl`/`isTheta_refl` then closes the theorem.*
- **"Degenerate witness"** — OEIS A211417. Pattern: *choose `D = 0`; every integer divides zero.*

Quoting the Erdős 422 entry in full, as the cleanest specimen:

> **Problem:** the target function itself can be used as the Big-O answer; `isBigO_refl` then closes the theorem. **Likely fix:** require an independently specified comparison scale or restrict the permitted answer family.

**Inference (marked as inference):** the *clustering by Lean tactic* (`rfl`, `isBigO_refl`, `isTheta_refl`) rather than by mathematical topic strongly suggests the search key is a syntactic/type-level property of the declaration — the kind of thing found by pattern-matching `answer(sorry)` against the statement's own left-hand side. Whether that matching is done by a script or by a human reading files with LLM help, the record does not say. They claim the latter.

### 3c. The actual production loop, from the event stream

Their public event stream shows a tight, repeatable pipeline. Example, OEIS A112521 on 2026-08-15:

```
13:48:20  CreateEvent      KitaKen1/oeis-a112521-formal-conjectures   (new artifact repo)
13:50:36  PushEvent        KitaKen1/oeis-a112521-formal-conjectures   (Lean proof + Lean4Web variant)
13:56:42  CreateEvent      KitaKen1/formal-conjectures                (branch on their fork)
13:58:47  PushEvent        KitaKen1/formal-conjectures                (the one-line status flip)
13:59:39  PullRequestEvent google-deepmind/formal-conjectures opened
```

**Eleven minutes, cold start to open PR.** A second instance the same morning (`oeis-a114831-asymptotic`, 10:10:37 → PR at 10:20:50) took ten minutes.

### 3d. Why the PRs are so cheap to review — the key structural trick

The upstream diffs are *tiny*, because all the mathematics lives in the external artifact repo and the PR only flips a category and adds a `formal_proof` link:

| PR | Diff | Files |
|---|---|---|
| #4957 | +3 / −1 | 1 |
| #4959 | +3 / −1 | 1 |
| #4853 | +3 / −2 | 1 |
| #4954 | +4 / −2 | 1 |
| #4924 | +6 / −2 | 1 |
| #4960 | +9 / −3 | 1 |
| #4963 | +9 / −3 | 3 |
| #4887 | +12 / −2 | 1 |
| #4869 | +23 / −9 | 1 |

Median merged diff is roughly **+9 / −3 in a single file.** This is deliberate and it directly conforms to the repo's stated scope, which the welcome bot states on every PR:

> This repository is mainly for formalised _statements_. Proofs longer than about 25-50 lines are usually out of scope; longer proofs are welcome to be included/linked via the `formal_proof` mechanism.

Each PR body carries a fixed template: the exact target theorem in a fenced block, a **commit-pinned** permalink with an `#L` line range, the repo link, a Lean4Web live link, an axiom audit line, and the AI disclosure. Example (#4924):

> `#print axioms` reports only `propext`, `Classical.choice`, and `Quot.sound`; there is no `sorryAx` in either proof.

**This is the single most transferable thing they do that we do not.** They pre-empt every question a reviewer could ask — is it pinned, does it match character-for-character, does it use `native_decide`, what are the axioms — inside the PR body, before review starts.

---

## 4. Overlap with our targets

### OEIS

| Our target | Their status | Verdict |
|---|---|---|
| **A237271** | PR **#4924, MERGED 2026-08-13** — `conjecture_4`, `conjecture_5` | **NEAR-MISS, same file.** They took the *parity at square and hexagonal indices* targets. Our target is `observation_carmichael` (vacuous-hypothesis defect), a **different declaration**. Our ledger already records it as "Novel… absent from #4896/#4923/#4927". Not lost — but they are now inside this file. |
| **A110854** | **No hit** anywhere in their 53 items | Clear |
| **A108864** | **No hit** anywhere in their 53 items | Clear |

### Erdős

| Our target | Their status | Verdict |
|---|---|---|
| **33** | Listed in **#4923** (2026-08-13) — the file's *headline* self-answer (infimum/limsup copied into `answer`, closes by `rfl`) | **NEAR-MISS, same file.** Our target is `.variants.one_mem_lowerBounds` (states `1 < limsup` while the name/docstring claim a lower bound). Different declaration. Our ledger already flags this correctly. |
| **142** | Issue **#4922** (2026-08-13) — `variants.upper` admits trivial linear answer `N` | **COLLISION — they were first on the file by 2 days.** We commented on their issue 2026-08-15T19:27 adding `erdos_142` and `variants.three`, both `=Θ` against unconstrained `answer(sorry)`, closable by `Asymptotics.isTheta_refl`. Our contribution is a genuine extension: #4923 records the reflexive-asymptotic pattern for Erdős 422/539/789 but **not** for 142. |
| 1093, 1055, 40, 15, 477, 952, 1084, 931, 242, 274, 982 | **No hit** | Clear — 11 of 13 Erdős targets untouched |

### WOWII

They have touched WOWII **four times**: Graph Conjectures **316** (#4426, merged), **2** (#4654, merged), **217** (#4656, merged), **31** (#4658, open).

Against our set (63, 85, 172, 176, 181, 309, 430a, 438b): **zero overlap.** No hit on any of our eight numbers.

### Overlap verdict

**One true collision (Erdős 142, they were first), two same-file near-misses (A237271, Erdős 33) where our declarations are distinct and still novel, and no contact at all on 11/13 Erdős targets, 2/3 OEIS targets, or any of our 8 WOWII targets.**

The live risk is not what they have taken — it is the **direction of travel**. They entered OEIS on 2026-08-13 and are consuming ~11 OEIS targets/day with a 2.4–4.8h merge latency. A110854 and A108864 are clear *today*; that is not a durable state.

---

## 5. Reception

### Maintainers merge them fast, and the latency is collapsing

| PR | Latency to merge | Merged by |
|---|---|---|
| #2177 (Feb) | 2140.8 h | Paul-Lez |
| #4426 (Jul 13) | 590.8 h | mo271 |
| #4654 | 275.3 h | mo271 |
| #4644 | 197.7 h | mo271 |
| #4656 | 173.4 h | Danie-I |
| #4869 | 87.4 h | mo271 |
| #4872 | 82.4 h | mo271 |
| #4887 | 11.9 h | mo271 |
| #4853 | 10.6 h | mo271 |
| #4954 | 8.9 h | mo271 |
| #4957 | 4.8 h | mo271 |
| #4959 | 4.8 h | mo271 |
| #4960 | 4.1 h | mo271 |
| #4963 | 3.6 h | mo271 |
| **#4924 (A237271)** | **2.4 h** | mo271 |

**Median 11.9 h. 13 of 15 merges by `mo271`.** The July items sat for 1–3 weeks; the 2026-08-15 OEIS batch merged in 2.4–4.8 hours. They have built reviewer trust, and `mo271` is now effectively fast-pathing them.

### Tone is positive, with substantive technical engagement

> Thanks for the contribution and congrats on solving the problem!
> — mo271, #4646

> Great work, I checked three of the in-repo leads and all are correct.
> — williamjblair, #4896

> Thanks for the contribution! The CI is only failing because one of the theorems is in the list `FC100OpenSet1`… Should be easy to fix by changing `94` to 93
> — mo271, #4659

### Pushback exists, and it is about *statement fidelity*, not volume

There is **no pushback on volume or quality anywhere in the record.** The criticism that does appear is precise and mathematical:

> on first sight looks like a potential misformalisation?
> — mo271 on #4890 (Erdős 319 linear upper bound) — i.e. the maintainer suspects the *statement*, not the proof. KitaKen1 then filed #4892 himself documenting exactly that.

> Even though it is not explicitely metnioned in the OEIS, perhaps it can be assumed that the intention here was to look for a **non-constant** sequence? Perhaps this can be added as a second conjecture marked `research open` next to the now `research solved` version without that requirement?
> — mo271 on #4964 (A103425) — pushback on a degenerate constant-sequence witness.

> Let's move it to the docstring. Can we quote the 2025 update verbatim?
> — mo271, #4887

> @KitaKen1 can you add a few words about the informal proof here (in the docstring)
> — mo271, #4646

> That would be great. Also let's mention Shashi456's formalization in some place!
> — mo271, #4853

### What the project wants — decisive signals

1. **Attribution and provenance matter.** Repeated requests to credit prior formalizers and quote sources verbatim in docstrings.
2. **Docstrings must carry the informal content.** Twice asked to move justification into the docstring rather than leaving it in the PR description.
3. **Original formalizers get consulted before a "solved" flip.** On #4704: *"since @aditya-ramabadran suggested to add those problems and @Sfgangloff formalised them, perhaps they have some opinion on if this is indeed solving problem 4.3"*. On #4646 and #4659 similarly (`@shamEiNew`, `@MarioKrenn6240`).
4. **Degenerate witnesses get converted into a new open statement rather than rejected** (#4964). The project's instinct is to *preserve the mathematical question* by splitting it, not to refuse the trivial solve.
5. **Independent verification is welcomed and is happening.** `williamjblair` builds their linked repos and reports axiom footprints, link pinning, and character-identity of statements — unprompted, on at least 8 of their PRs.

---

## 6. Anything else notable

### They coordinate publicly on Zulip — and that is where the audit started

> The initial audit was discussed on Zulip:
> <https://leanprover.zulipchat.com/#narrow/channel/524981-Formal-conjectures/topic/Possible.20misformalizations/with/616080167>
> — #4896

> This contribution was discussed in the Formal Conjectures Zulip stream, where opening a PR and using the `formal_proof` attribute was recommended.
> — #4426

**The `#Formal-conjectures` Zulip channel (524981) is an unmonitored intelligence channel for us.** Their method was socialised there *before* it appeared as GitHub issues, and the maintainers told them how to package contributions. We are not reading it.

### A priority dispute already happened — and the norm is publication date

`anagnorisis2peripeteia` on #4656:

> Congratulations, @KitaKen1 — this is a fine result. I completed an independent Lean proof of the same statement on July 30 and was preparing to propose marking it solved (#4667/#4668) before finding this PR; **your work was public two days earlier, on July 28, so I have closed mine in its favor. Priority is clearly yours.**

**The operative norm in this community is "first public artifact wins."** Not first to solve, not first to merge — first *public*. This is why the per-problem artifact repo matters: it timestamps the claim the moment it is pushed, minutes before the PR.

### Adjacent activity beyond this repo

- 62 issues/PRs authored across all of GitHub vs 53 here — **~85% of their entire GitHub output is this one repo.** They are a specialist.
- Three `lean-eval-*` repos (Aug 1–6): `lean-eval-two-plus-two` ("submitted as a pipeline test"), `lean-eval-conway-schneeberger-fifteen`, `lean-eval-pi-succ-sphere-n-mulequiv-zmod-two`. They are participating in a separate **LeanEval** benchmark/submission programme.
- Repos referencing external collaboration: `erdosproblems` ("A community database for the problems on the erdosproblems.com site"), `finite-simple-groups-lean`.
- No blog, no Twitter, no personal site, no email. Only the bio string "Intellectual Moonshine".

### On #4644, an outside expert independently corroborated — and partially corrected — them

`alreadydone` (the MathOverflow question's author) on #4644:

> (Update: the 735-line file on Lean Web editor does look valid), but coincidentally Patricia Purtill emailed me on July 24 with a solution in collaboration with GPT-5.6, which I formalized with Aristotle, so **it's fair to mark this as formally solved**. … The Weierstrass curve @KitaKen1 uses is **singular (not elliptic)**, and the construction is probably a slight tweak while essentially the same.

Note the wider context: multiple independent parties are solving these with frontier LLMs plus Lean simultaneously. This is a crowded race, not a two-horse one.

---

## 7. What they do that we do not — actionable delta

1. **One public artifact repo per finding, pushed *before* the PR.** Timestamps priority under the community's own "first public wins" norm. Costs them ~2 minutes.
2. **Keep the upstream diff at ~+9/−3 in one file.** The proof lives outside; the PR is a category flip plus a `formal_proof` link. Directly matches the repo's stated 25–50-line scope limit.
3. **Commit-pinned permalinks with `#L` line ranges** to the exact theorem — not `main`. Reviewers verify character-identity in seconds; `williamjblair` explicitly checks this and once flagged a 7-char short SHA as a nit.
4. **Axiom audit stated in the PR body**, every time: *"`#print axioms` reports only `propext`, `Classical.choice`, and `Quot.sound`; there is no `sorryAx`."*
5. **A Lean4Web live link** so a reviewer can check without cloning.
6. **Explicit AI-usage disclosure** — this has drawn zero friction and plausibly buys goodwill.
7. **Separate the defect report from the fix.** They file the issue (#4892) *and* the PR (#4890) and cross-link them, so the maintainer can accept the finding independently of the proposed repair.
8. **Volume against a fast-merging reviewer.** They found that `mo271` fast-paths well-packaged OEIS status flips, and they are exploiting that lane at ~11/day.

Our record for comparison: **8 PRs, 0 merged, 18 issues since 2026-08-01.** Their conversion is the gap, and the packaging above is most of the explanation.

---

## Appendix A — complete item list

| # | Type | State | Created | Merged | Title |
|---|---|---|---|---|---|
| 1935 | ISSUE | closed | 2026-01-30 | | Statement: Improved asymptotic lower bound for the Lonely Runner Conjecture (Tao, 2017) |
| 1941 | ISSUE | open | 2026-01-31 | | Proposal: Classification and Tagging for Original Conjectures, Milestones, and SOTA Bounds |
| 2171 | PR | closed | 2026-02-05 | | Update LonelyRunnerConjecture.lean |
| 2176 | PR | closed | 2026-02-06 | | Kita ken1 patch 1 |
| 2177 | PR | closed | 2026-02-06 | **MERGED** | Add Tao (2017) variant statement for Lonely Runner |
| 4426 | PR | closed | 2026-07-13 | **MERGED** | feat(WrittenOnTheWallII): mark Graph Conjecture 316 as solved |
| 4644 | PR | closed | 2026-07-27 | **MERGED** | feat(Mathoverflow/507128): mark as formally solved |
| 4646 | PR | open | 2026-07-27 | | feat(Paper): mark Bézier–Bernstein Voronovskaja problem solved |
| 4654 | PR | closed | 2026-07-27 | **MERGED** | WrittenOnTheWallII: add a third formal proof for Graph Conjecture 2 |
| 4656 | PR | closed | 2026-07-28 | **MERGED** | Mark WOWII Graph Conjecture 217 as solved by an external Lean proof |
| 4657 | PR | open | 2026-07-28 | | disprove(Other): convex additive-VC₂ bound in ℝ³ |
| 4658 | PR | open | 2026-07-28 | | docs(WrittenOnTheWallII/31): link a Lean proof of Chung's induced-path bound |
| 4659 | PR | open | 2026-07-29 | | feat(Paper/MonochromaticQuantumGraph): solve all-even integer cases |
| 4661 | PR | open | 2026-07-29 | | feat(Paper/MonochromaticQuantumGraph): solve three sharp high-color cases |
| 4664 | PR | open | 2026-07-30 | | feat(Paper/MonochromaticQuantumGraph): solve N = 6, D = 4 over C |
| 4680 | ISSUE | open | 2026-08-01 | | Ehrhart's volume conjecture |
| 4681 | ISSUE | open | 2026-08-01 | | Quantum parallel repetition for finite two-player games |
| 4704 | PR | open | 2026-08-03 | | Mark Weak Tiling Problem 4.3 as solved |
| 4851 | ISSUE | closed | 2026-08-10 | | Misformalization in Wikipedia/MovingSofa |
| 4853 | PR | closed | 2026-08-10 | **MERGED** | feat(ErdosProblems): mark Erdős 42 constructive variant as solved |
| 4854 | ISSUE | open | 2026-08-10 | | Green Problem 14: AKS14 lower bounds are misclassified as open |
| 4855 | ISSUE | open | 2026-08-10 | | Erdős Problem 973 has a negative answer |
| 4859 | ISSUE | closed | 2026-08-10 | | Wikipedia/SquarePacking: least-radius statements are false because negative radii are allowed |
| 4867 | ISSUE | closed | 2026-08-11 | | Erdős Problem 80: both open statements are false for c = 2 |
| 4868 | PR | open | 2026-08-11 | | feat(Arxiv): mark Fernandes conjecture 1 as solved |
| 4869 | PR | closed | 2026-08-11 | **MERGED** | feat(ErdosProblems): resolve three Erdős 539 exponent variants |
| 4872 | PR | closed | 2026-08-11 | **MERGED** | Mark MathOverflow 10799 Kahn-Kalai variant as solved |
| 4875 | PR | open | 2026-08-11 | | Mark Arxiv 2607.05349 microscopic weighting conjecture as solved |
| 4887 | PR | closed | 2026-08-12 | **MERGED** | Mark Green's Open Problem 52 logarithmic variant as solved |
| 4888 | PR | open | 2026-08-12 | | Mark Erdős Problem 692 Part II target as solved |
| 4890 | PR | open | 2026-08-12 | | feat(ErdosProblems/319): prove the linear upper bound |
| 4892 | ISSUE | open | 2026-08-12 | | Erdős 319 `isBigO` variant admits a tautological answer |
| 4896 | ISSUE | open | 2026-08-12 | | **Tracking: possible misformalizations found in statement audits** |
| 4918 | PR | open | 2026-08-13 | | Mark Erdős Problem 357 lower Big-O variant as solved |
| 4919 | ISSUE | open | 2026-08-13 | | Erdős 688 upper_bound admits the trivial constant answer 1 |
| 4922 | ISSUE | open | 2026-08-13 | | **Erdős 142 variants.upper admits the trivial linear answer N** |
| 4923 | ISSUE | open | 2026-08-13 | | **Possible misformalizations II** |
| 4924 | PR | closed | 2026-08-13 | **MERGED** | **Mark OEIS A237271 parity conjectures as solved** |
| 4927 | ISSUE | open | 2026-08-13 | | Open statements with known solutions |
| 4943 | PR | open | 2026-08-13 | | Mark qualitative upper bounds for Green 37 as solved |
| 4944 | PR | open | 2026-08-14 | | Mark Erdős Problem 361 asymptotic variant as solved |
| 4953 | PR | open | 2026-08-14 | | disprove(OEIS): resolve A113019 fixed-point conjecture |
| 4954 | PR | closed | 2026-08-15 | **MERGED** | Mark OEIS A100478 as solved |
| 4957 | PR | closed | 2026-08-15 | **MERGED** | Mark OEIS A108306 as solved |
| 4959 | PR | closed | 2026-08-15 | **MERGED** | Mark OEIS A105801 as solved |
| 4960 | PR | closed | 2026-08-15 | **MERGED** | Mark OEIS A112970 conjectures as solved |
| 4963 | PR | closed | 2026-08-15 | **MERGED** | Mark OEIS A113250, A113252, and A113255 as solved |
| 4964 | PR | open | 2026-08-15 | | Mark OEIS A103425 as solved |
| 4967 | PR | open | 2026-08-15 | | Mark three Erdős 357 growth targets as solved |
| 4969 | PR | open | 2026-08-15 | | Mark OEIS A114831 asymptotic conjecture as solved |
| 4970 | PR | open | 2026-08-15 | | Mark OEIS A102371 as solved |
| 4971 | PR | open | 2026-08-15 | | Mark OEIS A102722 asymptotic as solved |
| 4972 | PR | open | 2026-08-15 | | Mark OEIS A112521 as solved |

## Appendix B — full text of the two tracker issues

Reproduced verbatim in the raw pull; the defect taxonomy from #4923 is the operationally important part and is quoted in §3b above. #4896's categories are:

- **Source / statement mismatches** (8 items): Optimization Constant C1a, Erdős 996, 697, 887, 918, 1167, 757, Green 72
- **Boundary cases / vacuous wrappers** (4 items): Erdős 940 *(fixed by PR #4933)*, 694, 939, Green 21
- **Interpretation / `answer` semantics** (2 items): Erdős 357 weak-monotone, self-answer patterns in Erdős 195/188/1047
- **Existing tracking**: Erdős 80 (#4867), 319 (#4892), 769 (#4806)
- **Open-PR blockers** (4 items): PR #4660, #4866, #4258 (Erdős 1208), #3588 (Erdős 190)
