# Existing upstream PR maintenance audit

Checked: **2026-08-13 01:02 UTC**

Scope: read-only maintenance check of the five already-open campaign pull
requests in `google-deepmind/formal-conjectures`. This is not authorization to
open another upstream issue or pull request; new discoveries follow the
project-release protocol.

| PR | campaign result | state | review | project build | other required checks |
|---:|---|---|---|---|---|
| [#4907](https://github.com/google-deepmind/formal-conjectures/pull/4907) | WOWII 181, qualified formalized reading | open, non-draft | required | success | success |
| [#4909](https://github.com/google-deepmind/formal-conjectures/pull/4909) | WOWII 172 | open, non-draft | required | success | success |
| [#4911](https://github.com/google-deepmind/formal-conjectures/pull/4911) | WOWII 176 | open, non-draft | required | success | success |
| [#4913](https://github.com/google-deepmind/formal-conjectures/pull/4913) | WOWII 430a | open, non-draft | required | success | success |
| [#4916](https://github.com/google-deepmind/formal-conjectures/pull/4916) | WOWII 438b stronger theorem | open, non-draft | required | success | success |

`Test scripts`, `check-copyright`, `check-changes`, `scan-pr`, `labeler`, and
`cla/google` report success on every row. Skipped deployment/security-output
jobs are workflow skips, not failures. There are no review comments or failing
checks requiring a campaign write at this checkpoint, so no comment, commit,
push, rerun, or upstream edit was made.
