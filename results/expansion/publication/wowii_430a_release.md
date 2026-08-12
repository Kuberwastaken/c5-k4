# WOWII 430a project-release checklist

Date: **2026-08-12 UTC**

## Eligibility and novelty

- Scope: Written on the Wall II in the frozen represented corpus.
- Complete source-faithful disproof under both open/closed center-neighborhood
  readings.
- Exact formula, concept, literature, live source, upstream history, and
  GitHub searches found no earlier resolution; the relevant 2011 paper was
  read in full. Claim only **apparently unrecorded**.
- Existing upstream #4912/#4913 are this project's own earlier submission.
- No local/remote `wowii-430a-v1` tag or project release exists.
- No new upstream issue, PR, or comment will be opened.

## Durable artifacts

- Result, source/readings audit, two-verifier evidence, and novelty record:
  `8d48fbdf45301afb57f9d4d5627f5b984f385089`.
- Complete no-`sorry` Lean certificate:
  `85fff48cdd7cc1f743802320fdc94db14d1f841e`.
- Independent verifier: pass under 60 seconds; 992 Atlas and 24 named controls,
  exact `n=53`, `m=875`, `i=3`, center-neighborhood independence `2`, and
  `CW=51123/25585<2`.
- Lean warning-as-error elaboration: pass under 60 seconds.
- Trust assumptions: `propext`, `Classical.choice`, `Lean.ofReduceBool`,
  `Lean.trustCompiler`, and `Quot.sound`; no `sorryAx` or project axiom.

## Planned release

- Tag: `wowii-430a-v1`.
- Title: `WOWII Conjecture 430a: counterexample and formal certificate`.
- Canonical body order; no generated binary assets.

## Release lock

Resolved with `git rev-parse` to
`d187206a7328cbaf1e595cee2e178eb86076ec29`. The annotated tag must dereference
to exactly that preflight snapshot.
