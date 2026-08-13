# Read-only upstream and release maintenance audit

Date: **2026-08-13 02:18 UTC**

Scope: existing `google-deepmind/formal-conjectures` pull requests
[#4907](https://github.com/google-deepmind/formal-conjectures/pull/4907),
[#4909](https://github.com/google-deepmind/formal-conjectures/pull/4909),
[#4911](https://github.com/google-deepmind/formal-conjectures/pull/4911),
[#4913](https://github.com/google-deepmind/formal-conjectures/pull/4913), and
[#4916](https://github.com/google-deepmind/formal-conjectures/pull/4916), plus
the one-problem releases and annotated tags in `Kuberwastaken/c5-k4`.

This was a read-only maintenance audit. It created no issue, pull request,
review, comment, release, tag, branch, commit, or push, and it did not modify
any existing external object.

## Audit method

Current pull-request metadata, check runs, reviews, review comments, issue
comments, file counts, and mergeability were read with `gh` from the canonical
base repository. Required checks were queried separately with `gh pr checks
--required`. Release objects, annotated-tag objects, and remote tag refs were
read from the GitHub API. Local annotated tags were dereferenced with Git and
compared to the remote tag targets. Every immutable `c5-k4/blob/<sha>/...` URL
present in the five PR bodies or four release bodies was fetched with redirects
enabled and checked for HTTP 200.

Repository state at the start of the audit was `main` at
`ac9b2f5` (`docs: refresh theorem extraction frontier`), matching
`origin/main`.

## Pull-request state

| PR | subject | state | mergeability | checks | review state | discussion blocker |
|---|---|---|---|---|---|---|
| [#4907](https://github.com/google-deepmind/formal-conjectures/pull/4907) | WOWII 181, formalized square-degree disproof | open, non-draft, unmerged | GitHub reports mergeable; merge state `blocked` | all required checks pass | `REVIEW_REQUIRED`; zero submitted reviews and zero review comments | none; one author issue comment contains no requested change |
| [#4909](https://github.com/google-deepmind/formal-conjectures/pull/4909) | WOWII 172 disproof | open, non-draft, unmerged | GitHub reports mergeable; merge state `blocked` | all required checks pass | `REVIEW_REQUIRED`; zero submitted reviews and zero review comments | none |
| [#4911](https://github.com/google-deepmind/formal-conjectures/pull/4911) | WOWII 176 disproof | open, non-draft, unmerged | GitHub reports mergeable; merge state `blocked` | all required checks pass | `REVIEW_REQUIRED`; zero submitted reviews and zero review comments | none |
| [#4913](https://github.com/google-deepmind/formal-conjectures/pull/4913) | WOWII 430a disproof | open, non-draft, unmerged | GitHub reports mergeable; merge state `blocked` | all required checks pass | `REVIEW_REQUIRED`; zero submitted reviews and zero review comments | none |
| [#4916](https://github.com/google-deepmind/formal-conjectures/pull/4916) | WOWII 438b proof/formalization | open, non-draft, unmerged | GitHub reports mergeable; merge state `blocked` | all required checks pass | `REVIEW_REQUIRED`; zero submitted reviews and zero review comments | none |

All five PRs have the `written-on-the-wall-ii` label, target `main`, and change
exactly one problem file. No reviewer or review team is explicitly requested on
any PR. The required checks reported by GitHub are:

- `Build project`: pass;
- `check-copyright`: pass;
- `cla/google`: pass.

The broader rollups also show successful test-script, change-scan, security,
and labeler jobs. Deployment and auxiliary Zizmor jobs are skipped by workflow
design rather than failed. There is no pending, cancelled, timed-out, or failed
check in the current rollup.

The only current blocker visible through the API is branch-policy review:
`reviewDecision=REVIEW_REQUIRED` together with `mergeStateStatus=BLOCKED`.
Because every required check passes, each head is reported mergeable, and no
review thread exists, there is no code, CI, CLA, copyright, merge-conflict, or
addressable review-comment blocker at this checkpoint. Maintainer approval is
the outstanding external action.

## Pull-request artifact links

Every complete-certificate, method, README, source-audit, verifier, and
priority-audit blob URL in the five PR bodies currently resolves with HTTP
200. This includes the complete no-`sorry` certificates for WOWII 181, 172,
176, 430a, and 438b and the supporting immutable audit links.

The WOWII 181 qualification remains present in both the PR title/body and its
artifact trail: the submitted result is explicitly the square-degree reading,
not the alternate reading that measures the selected vertices' degrees back in
the original graph. The WOWII 438b body also retains its priority limitation:
it claims a complete Lean formalization of the source-listed-open entry, not a
novel mathematical theorem.

## Project releases and annotated tags

GitHub currently lists exactly four `c5-k4` releases:

| release | publication state | annotated-tag target | local/remote agreement | release page |
|---|---|---|---|---|
| `wowii-172-v1` | published; non-draft; non-prerelease; zero assets | `64abb3ce00e6ac34ac8358baa9798511d0ca8ec0` | exact | HTTP 200 |
| `wowii-176-v1` | published; non-draft; non-prerelease; zero assets | `51faa868b85ce5069e4017dfa97845772435229a` | exact | HTTP 200 |
| `wowii-181-v1` | published; non-draft; non-prerelease; zero assets | `f71a0d28b59907b8b9ee9f534d6ad7d5cdf8a528` | exact | HTTP 200 |
| `wowii-430a-v1` | published; non-draft; non-prerelease; zero assets | `d187206a7328cbaf1e595cee2e178eb86076ec29` | exact | HTTP 200 |

All four refs point to annotated tag objects, not lightweight tags. Each local
tag dereferences to the same commit as the corresponding remote annotated tag.
The targets match the locked commits recorded in the existing release
checklists and release-backlog audit.

Across the five PR bodies and four release bodies there are **27 unique
immutable `c5-k4` blob URLs**. All 27 returned HTTP 200 under `curl -L`. The
four release pages also returned HTTP 200. No release has generated binary
assets, and no extra local or remote one-problem release tag was found.

## Newly committed local theorem work

The commits after the prior release-backlog checkpoint add genuine theorem and
proof-extraction progress, but no new release-eligible counterexample:

- WOWII 61 now has realization-aware graphical-transfer and recursive-potential
  infrastructure. The decisive residue monotonicity/Maxine bridge and the
  original conjecture remain open.
- WOWII 133 now has the maximum-degree-one independence formula, the C4-free
  local-average identity, matching-neighborhood machinery, and a
  triangle-incidence bridge. The remaining induced-path inequality and full
  source conjecture are not proved or disproved.
- WOWII 183 now has a universal outside-neighborhood budget theorem and a
  component-parity formulation of the attachment obligation. The compatible
  attachment existence step remains unproved; the exact auxiliary
  counterfamilies continue to satisfy WOWII 183 rather than refute it.
- WOWII 438b remains a completed stronger theorem with an existing upstream
  proof/formalization PR, but it is a theorem rather than a counterexample.

Under the standing **one-problem, counterexample-only** project-release rule,
none of these theorem artifacts is release-eligible. A reusable lemma, stronger
theorem, theorem signal, auxiliary-lemma counterexample, or partial
formalization does not enter the counterexample release queue. No newly
committed local artifact supplies a new source-faithful, apparently unclaimed,
independently verified, warning-clean counterexample with a completed release
preflight.

## Disposition

1. Keep all five upstream PRs unchanged. They are open, green, mergeable, and
   awaiting maintainer review; there is no review comment to address.
2. Keep the four existing releases and tags unchanged. Their locked targets,
   metadata, release pages, and immutable artifact links remain valid.
3. Do not create a project release for the new WOWII 61, 133, 183, or 438b
   theorem work under the counterexample-only rule.
4. The one-problem counterexample release backlog remains empty at this
   checkpoint.
