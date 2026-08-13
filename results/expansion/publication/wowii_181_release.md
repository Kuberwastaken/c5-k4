# WOWII 181 formalized-reading project-release checklist

Date: **2026-08-13 UTC**

## Eligibility, reading, and novelty

- Scope: Written on the Wall II in the frozen represented corpus.
- Complete disproof only of the explicitly formalized square-degree reading:
  degrees of `B(G^2)` are measured in `G^2`.
- `T(7)` is not a counterexample when the same vertices' degrees are measured
  back in `G`; that reading holds with slack nine. The qualification must be in
  the release title and first summary paragraph.
- Source, definitions, both readings, live status, literature, project public
  history, upstream issue/PR history, and priority were audited at commit
  `eaaf8b70036eb65c47942b57a31322492ff5b9d5`.
- No earlier independent resolution was located; claim only apparently
  unrecorded before this project's public 2026-08-12 commit/issue.
- Existing upstream #4905/#4907 are this project's own public history.
- No local/remote `wowii-181-v1` tag or c5-k4 release exists.
- No new upstream issue, PR, or comment will be opened.

## Durable artifacts

- Complete no-`sorry` Lean certificate:
  `3bfa33d7470055a9a11d9ffde29186245dc3a329`.
- Independent exact verifier:
  `8f4bad087fa543ac9b2eac7622241c0bbbac5e56`.
- Reading/status/priority audit:
  `eaaf8b70036eb65c47942b57a31322492ff5b9d5`.
- Verifier: pass in 5.584 seconds under hard 60-second cap; exact `T(7)`
  invariants and all 995 connected Atlas controls under both readings.
- Lean warning-as-error elaboration: pass under 60 seconds.
- Trust assumptions: `propext`, `Classical.choice`, `Lean.ofReduceBool`,
  `Lean.trustCompiler`, and `Quot.sound`; no `sorryAx` or project axiom.
- Every planned immutable certificate/verifier/audit/method link returned HTTP
  200 and was opened/read.

## Planned release

- Tag: `wowii-181-v1`.
- Title: `WOWII Conjecture 181 (formalized square-degree reading): counterexample and formal certificate`.
- Canonical body with the alternate-reading non-counterexample prominently
  disclosed; no binary assets.

## Release lock

Resolved with `git rev-parse` to
`f71a0d28b59907b8b9ee9f534d6ad7d5cdf8a528`. The annotated tag must
dereference to exactly that preflight snapshot.
