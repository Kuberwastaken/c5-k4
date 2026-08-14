# Bondy upstream-drift and versioned-repin audit

**Audit date:** 2026-08-14 UTC

**Scope:** read-only audit of the drift from the immutable Bondy DEVELOPMENT
freeze to the then-current `google-deepmind/formal-conjectures` `main`. This
audit did not activate or evaluate the target, alter the frozen experiment,
dispatch work, or create any upstream/public action.

**Verdict:** `REPIN_SAFE_VERSIONED` (`UNRELATED_DRIFT`), not `STRICT_STOP`.

The old freeze must continue to fail closed when run against a different
commit or tree. The evidence below supports a new, explicitly versioned
superseding freeze pinned to the audited current commit; it does not authorize
an in-place mutation or reinterpretation of the existing freeze.

## Exact upstream identity and complete delta

The frozen upstream identity is:

- commit
  [`5a5af706fa5bef3f09606554d393c9170d2b27e8`](https://github.com/google-deepmind/formal-conjectures/commit/5a5af706fa5bef3f09606554d393c9170d2b27e8);
- tree `0ef534e06d27e22e68e4cfd5081f2a5e28ebe73a`;
- author and committer time `2026-08-14T18:36:16Z`;
- parent `8781428a922a53914450550218bf14be703d8d69`.

Authenticated GitHub REST and an independent `git ls-remote` resolved
`refs/heads/main` to the following identity. The final `ls-remote` observation
was at `2026-08-14T21:52:56Z`:

- commit
  [`b5acb0ff13e38084105b7fe020ba0d59c1925bc5`](https://github.com/google-deepmind/formal-conjectures/commit/b5acb0ff13e38084105b7fe020ba0d59c1925bc5);
- tree `4f6c9bd17fdfdc264f54b26862ce768743da5d63`;
- author and committer time `2026-08-14T18:36:29Z`;
- sole parent `5a5af706fa5bef3f09606554d393c9170d2b27e8`.

The GitHub
[`5a5af706...b5acb0ff` comparison](https://github.com/google-deepmind/formal-conjectures/compare/5a5af706fa5bef3f09606554d393c9170d2b27e8...b5acb0ff13e38084105b7fe020ba0d59c1925bc5)
reported `status=ahead`, `ahead_by=1`, `behind_by=0`,
`total_commits=1`, and merge base exactly the frozen commit. Its complete
commit/path delta was:

| Commit | Time | Subject | Changed path | Status | Blob | Additions | Deletions |
| --- | --- | --- | --- | --- | --- | ---: | ---: |
| `b5acb0ff13e38084105b7fe020ba0d59c1925bc5` | `2026-08-14T18:36:29Z` | `feat(ErdosProblems): resolve three Erdős 539 exponent variants (#4869)` | `FormalConjectures/ErdosProblems/539.lean` | modified | `5546c7ec89cb801295ab72a1ec82985b83feed11` | 23 | 9 |

There were no other commits or paths in the comparison. In particular, the
delta does not touch `FormalConjectures/Arxiv/2606.03696/` or any shared
utility imported by the target file.

## Target blob and formal-status invariance

The audited target is
[`FormalConjectures/Arxiv/2606.03696/BondyLongestCycles.lean`](https://github.com/google-deepmind/formal-conjectures/blob/b5acb0ff13e38084105b7fe020ba0d59c1925bc5/FormalConjectures/Arxiv/2606.03696/BondyLongestCycles.lean).
Direct raw downloads at the frozen and current commits compared byte-for-byte
equal. Both have:

- size: `4786` bytes;
- Git blob SHA-1: `c4c5cb1983936860d5a4a7208b3f04bd201290d4`;
- raw SHA-256:
  `562fbbb0ec47041a61017bb85ec0c7e9aa6fc98cf132be3022268a7dc60e9004`.

The declaration shape is therefore also byte-identical:

- line 56: `@[category research open, AMS 5]`;
- line 57: `theorem bondy_conjecture :`;
- line 58: `answer(sorry) ↔ ...`;
- line 64: the main theorem body remains `sorry`.

The file contains five proof-body `sorry` lines, at lines 64, 76, 87, 98,
and 112. There are six lexical `sorry` tokens when the opaque
`answer(sorry)` placeholder is included. Thus neither the main target's
`research open` category, its proof placeholder, nor the answer wrapper has
changed.

The target-path history on current `main` still begins with the ingestion
merge
[`8781428a922a53914450550218bf14be703d8d69`](https://github.com/google-deepmind/formal-conjectures/commit/8781428a922a53914450550218bf14be703d8d69),
committed at `2026-08-14T18:34:32Z`. No later path commit was returned.

## Current issue, PR, and exact-search evidence

The status/search snapshot below was collected at
`2026-08-14T21:47:20Z` through authenticated GitHub REST:

- ingestion issue
  [#4858](https://github.com/google-deepmind/formal-conjectures/issues/4858)
  is an issue, not a pull request; it is `closed` with
  `state_reason=completed`, `closed_at=2026-08-14T20:25:51Z`;
- ingestion PR
  [#4879](https://github.com/google-deepmind/formal-conjectures/pull/4879)
  is non-draft, `closed`, and merged at
  `2026-08-14T20:25:50Z`; its merge commit is
  `8781428a922a53914450550218bf14be703d8d69` and GitHub reported two
  changed files.

All three frozen issue-search requests returned
`incomplete_results=false`, with these exact result-number sets:

| Exact query | Result set |
| --- | --- |
| `repo:google-deepmind/formal-conjectures "bondy_conjecture"` | `[4879]` |
| `repo:google-deepmind/formal-conjectures "BondyLongestCycles"` | `[]` |
| `repo:google-deepmind/formal-conjectures "2606.03696"` | `[4879]` |

A broader repository issue search for `"longest cycles" in:title,body`
returned only #4858 and #4879, both closed. A still broader `Bondy`
title/body search also returned unrelated historical material and open PR
[#4451](https://github.com/google-deepmind/formal-conjectures/pull/4451).
That PR concerns an Erdős cycle-versus-clique Ramsey problem and its sole
changed path is `FormalConjectures/ErdosProblems/551.lean`; it does not touch
the Bondy target.

## Complete open-PR changed-file audit

A canonical open-PR identity snapshot was taken before the changed-file scan
at `2026-08-14T21:48:53Z` and repeated after it at
`2026-08-14T21:51:10Z`. Both brackets had:

- `main=b5acb0ff13e38084105b7fe020ba0d59c1925bc5`;
- exactly `274` open pull requests;
- audit identity-stream SHA-256
  `49187b03ac0dadd24eb2314f32baec4c34cae5135d9d07d19e7b4022325435ae`.

The identity stream bound, in PR-number order, each PR's number, title,
draft flag, `updated_at`, head SHA/ref/repository, and base
SHA/ref/repository. The before and after streams were byte-equal.

Using 24 concurrent workers, all `274` open PR changed-file lists were fetched
with full REST pagination. The scan completed at
`2026-08-14T21:51:03Z` with:

- processed: `274`;
- fetch/pagination failures: `0`;
- PRs whose changed paths include
  `FormalConjectures/Arxiv/2606.03696/BondyLongestCycles.lean`: `0`.

This is direct changed-path evidence; it does not depend on PR titles or
GitHub text-search indexing.

## Standalone and literature checks

The frozen standalone repository query
`"Bondy" "longest cycles" counterexample` returned `total_count=0` and
`incomplete_results=false`. Additional bounded GitHub searches returned:

- repository search `BondyLongestCycles`: zero;
- repository search `2606.03696 counterexample`: zero;
- global issue/PR search `"BondyLongestCycles"`: zero;
- global issue/PR search `"2606.03696" counterexample`: zero;
- global issue/PR search `"Bondy longest cycles" counterexample`: zero.

A repository search for the much broader term `bondy_conjecture` had one
result, but it was a different Bondy/Malkevitch pancyclicity conjecture and
not this longest-cycle target. General web searches likewise found the
primary paper and older or different Bondy conjectures, but no claimed
counterexample or resolution of this exact target. These are bounded search
results, not a claim of logically exhaustive absence across the entire web.

The primary source remains
[`arXiv:2606.03696v1`](https://arxiv.org/abs/2606.03696), by Jie Ma, Bo Ning,
and Ziyuan Zhao, published and last updated at
`2026-06-02T14:17:06Z`. The arXiv record continues to state that the
conjecture is known for `k ≤ 3`, remains open for `k ≥ 4`, and is proved
for sufficiently large graphs. The paper gives the explicit large-order
bound `n_k = 5k^2 + 7k`. It separately supplies a counterexample to a Voss
conjecture; that is not a counterexample to the Bondy conjecture audited
here.

The bytes served by both the versioned and current PDF URLs matched the
frozen primary-source SHA-256:

`56213cd6384cc2111864d67150c41e1426608c59b1b009c6752acab9be3487fb`.

## Gate interpretation and repin decision

The existing contract states that any live upstream drift is `GATE_FAIL` and
that there is no repin inside that trial. That behavior remains correct: the
old immutable gate must fail because `main` no longer equals its frozen
commit/tree, even though the target itself is unchanged.

The audited drift is nevertheless unrelated to the target and preserves all
target blob, raw-content, category, `sorry`, answer-wrapper, issue/PR,
exact-search, open-PR-touch, standalone-search, and primary-source facts.
Accordingly:

- there is no evidence-based `STRICT_STOP` trigger in this upstream delta;
- a **new versioned freeze** may repin the upstream commit to
  `b5acb0ff13e38084105b7fe020ba0d59c1925bc5` and tree to
  `4f6c9bd17fdfdc264f54b26862ce768743da5d63`;
- the target blob, target raw SHA-256, and primary PDF SHA-256 remain the
  frozen values above;
- the superseding freeze must rerun its own immutable verification and live
  gate at its eventual review/use time, because `main`, PRs, and search
  results are temporally mutable.

This audit authorizes no target execution, activation, publication, issue,
pull request, or other public action.
