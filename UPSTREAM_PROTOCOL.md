# DeepMind `formal-conjectures` publication protocol

**Standing rule:** every public issue and PR from this campaign follows the
WOWII 172/176 layout. This is a release gate, not optional guidance.

Canonical exemplars:

- issue [#4908](https://github.com/google-deepmind/formal-conjectures/issues/4908)
  and PR [#4909](https://github.com/google-deepmind/formal-conjectures/pull/4909)
  for WOWII 172;
- issue [#4910](https://github.com/google-deepmind/formal-conjectures/issues/4910)
  and PR [#4911](https://github.com/google-deepmind/formal-conjectures/pull/4911)
  for WOWII 176.

## Scope gate

Before any public write, all answers below must be yes:

1. Is this an existing problem from a collection already represented in
   `google-deepmind/formal-conjectures`?
2. For this campaign, is it Written on the Wall **II**, not WoW I or Graph
   Brain?
3. Does the current upstream repository not already contain the file,
   declaration, issue, or focused PR?
4. Has the primary source/status and every plausible reading been audited?
5. Is the claimed result complete rather than a conditional arithmetic core,
   bounded hold, theorem signal, or source erratum?

If any answer is no, stop the publication path. Keep the work local and label
its actual status.

## Artifact gate

The public workflow starts only after `c5-k4` contains sequential commits for:

1. the source/readings/status audit;
2. the exact discovery or paper proof report;
3. an independent verifier where computation is material;
4. the complete no-`sorry` Lean certificate;
5. a warning-as-error build and axiom audit.

The complete proof belongs in `c5-k4`. The upstream problem file follows the
172/176 benchmark layout: concise source-faithful definitions and statement,
`answer(True/False)`, `@[category research solved, AMS 5]`, an immutable
`formal_proof using lean4` link, and repository-standard `by sorry`. Do not
copy a long executable certificate into the benchmark PR unless a maintainer
explicitly asks for it.

## Immutable-link gate

Never type or infer a full commit hash from a short hash. Obtain it with:

```bash
git rev-parse <commit>
```

Before public use, verify every immutable link:

```bash
curl -sS -o /dev/null -w '%{http_code}\n' -L '<url>'
```

The result must be HTTP 200. Open/read the linked file content as a second
check. Prefer a precise line anchor only after confirming it resolves; a valid
whole-file blob link is better than a stale line range.

Record the full resolved SHA and URL in the local publication checklist.

## Issue order and format

Create the issue first. One issue covers one WoW II problem. Its title is:

```text
Formalize the disproof of WOWII Conjecture N
Formalize the proof of WOWII Conjecture N
```

Use these sections in this order:

1. `## Summary` — exact source-faithful formula and status.
2. `## Counterexample` or `## Proof idea` — exact witness values or rigorous
   argument, including the final numerical contradiction when applicable.
3. `## Relationship to the C₅[K₄] campaign` — prospective wall-navigation
   path, without inflated novelty claims.
4. Immutable discovery/proof report and broader method links.
5. `## Complete formal certificate` — verified immutable no-`sorry` Lean URL,
   warning-clean result, and exact trust assumptions.
6. `## Reading note` or `## Source/status note` — ambiguities, conventions,
   historical priority, and known earlier results.
7. `## AI assistance disclosure` — same responsibility wording as 172/176.

After creation, read the rendered issue back via GitHub and verify every link.

## Branch and PR format

Only after the issue exists:

1. branch from the exact current `upstream/main`;
2. add one problem file for one conjecture;
3. run the target `lake --wfail build`;
4. commit only that file at the logical checkpoint;
5. push the one branch;
6. open one non-draft PR that closes the issue.

PR title:

```text
WrittenOnTheWallII: disprove conjecture N
WrittenOnTheWallII: prove conjecture N
```

PR body sections, matching 172/176:

1. `## Summary` — exact statement, compact witness/proof data, and
   `Closes #ISSUE`.
2. `## Follow-up discovery pattern` — how the carrier/tight wall led here,
   with immutable method and detailed-result links.
3. `## Formal proof` — verified immutable certificate and audit link, with
   exact trust assumptions.
4. `## Reading note` or `## Source/status note`.
5. `## Verification` — target build and external warning-as-error command.
6. `## AI assistance disclosure`.

After creation, read back the PR body/files/base/head. Confirm exactly one
problem file, `main` as base, the intended fork branch as head, and all links
HTTP 200. Then monitor CI. A transient infrastructure failure is reported as
such; it never changes the mathematical status.

## Public-write preflight checklist

Each future submission must add and commit a short checklist under
`results/expansion/publication/` before the issue is created. It records:

- upstream SHA and eligible collection;
- exact duplicate-search queries and results;
- source URL/status/readings;
- local report/proof/verifier commits;
- complete Lean build command/result and trust assumptions;
- full SHA from `git rev-parse`;
- HTTP-200 checks for every planned URL;
- proposed issue title and PR title;
- confirmation that the issue and PR bodies were generated from the canonical
  section order above.

No checklist, no public write.
