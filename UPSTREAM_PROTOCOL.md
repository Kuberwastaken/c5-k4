# Public-result publication protocol

**Standing rule:** treat `google-deepmind/formal-conjectures` as read-only
unless the user explicitly authorizes a new upstream submission in the current
campaign turn.  Explicit authorization permits only results that pass every
gate below.  A matching open, closed, or merged issue, PR, declaration, or
commit disqualifies a duplicate submission; reuse or leave the existing record
alone as appropriate.  Independently publish newly validated, apparently
unclaimed counterexamples as versioned releases of `Kuberwastaken/c5-k4`.

Existing upstream PRs may be monitored and repaired in response to CI or
review.  Without current explicit authorization, this does not authorize a new
upstream issue, PR, comment, or review action.

Canonical exemplars:

- issue [#4908](https://github.com/google-deepmind/formal-conjectures/issues/4908)
  and PR [#4909](https://github.com/google-deepmind/formal-conjectures/pull/4909)
  for WOWII 172;
- issue [#4910](https://github.com/google-deepmind/formal-conjectures/issues/4910)
  and PR [#4911](https://github.com/google-deepmind/formal-conjectures/pull/4911)
  for WOWII 176.

## Upstream issue and PR format

When an upstream submission is explicitly authorized, one issue and one PR
cover one problem.  The issue uses, in order: `Summary`, `Counterexample` or
`Proof`, `Relationship to the C5[K4] campaign`, immutable audit/verifier/proof
links, `Source/status note`, and `AI assistance disclosure`.  The PR uses, in
order: `Summary`, the closing issue reference, `Follow-up discovery pattern`,
`Formal proof`, `Source/status note`, `Verification`, and `AI assistance
disclosure`.  Attribution and ambiguity caveats remain prominent in both.

## Scope and novelty gate

Before any public write, all answers below must be yes:

1. Is this an existing problem from the campaign's frozen
   `formal-conjectures`-represented scope?
2. For this campaign, is it Written on the Wall **II**, not WoW I or Graph
   Brain?
3. Has the primary source/status and every plausible reading been audited?
4. Is the result complete rather than a conditional arithmetic core, bounded
   hold, theorem signal, or source erratum?
5. Is it apparently unclaimed after checking literature, the current upstream
   repository, its issue/PR history, and this project's own commits, tags, and
   releases?
6. Is the proposed tag/version absent from both local and remote tags?

If any answer is no, stop the publication path. Keep the work local and label
its actual status.

## Artifact gate

The public workflow starts only after `c5-k4` contains sequential commits for:

1. the source/readings/status audit;
2. the exact discovery or paper proof report;
3. an independent verifier where computation is material;
4. the complete no-`sorry` Lean certificate;
5. a warning-as-error build and axiom audit.

The complete proof, verifier, source audit, and result report all belong in
`c5-k4` before a release is drafted.

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

## Release format

One release covers one WoW II problem. Its tag and title are:

```text
wowii-N-v1
WOWII Conjecture N: counterexample and formal certificate
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

Create the release from the exact audited commit, not from a moving branch.
After creation, read the rendered release and its target commit back through
GitHub, verify every link, and confirm that the tag resolves to the intended
commit. Do not upload generated binaries when the committed source,
certificate, and verifier are the actual durable artifacts.

## Public-write preflight checklist

Each future release must add and commit a short checklist under
`results/expansion/publication/` before the release is created. It records:

- upstream SHA and eligible collection;
- exact duplicate-search queries and results;
- source URL/status/readings;
- local report/proof/verifier commits;
- complete Lean build command/result and trust assumptions;
- full SHA from `git rev-parse`;
- HTTP-200 checks for every planned URL;
- proposed tag and release title;
- confirmation that the release body uses the canonical section order above;
- confirmation whether an upstream issue/PR is explicitly authorized and, if
  so, that no matching open, closed, or merged record exists.

No checklist, no release.
