# WOWII 176 project-release checklist

Date: **2026-08-12 UTC**

## Eligibility and novelty

- Scope: Written on the Wall II in the frozen represented corpus.
- Complete disproof: `D_7` violates both plausible distance readings.
- Targeted source, formula, conjecture-number, literature, upstream history,
  and GitHub searches found no earlier resolution. Claim only **apparently
  unrecorded**, not absolute priority.
- Existing upstream #4910/#4911 are this project's own earlier submission.
- No local/remote `wowii-176-v1` tag or c5-k4 release exists.
- No new upstream issue, PR, or comment will be opened.

## Durable artifacts

- Result, source/readings audit, verifier, and novelty record:
  `9bfc0586e7afcf3708aea5fe878346d72e266196`.
- Complete no-`sorry` Lean certificate:
  `b0ba2b9206176b4fc30bd633de206ac230b4e01f`.
- Exact verifier: pass under 60 seconds; 995 connected Atlas controls, exact
  family formulas for `D_L`, `L=5..12`, and both readings crossed by `D_7`.
- Lean warning-as-error elaboration: pass under 60 seconds.
- Trust assumptions: `propext`, `Classical.choice`, `Lean.ofReduceBool`,
  `Lean.trustCompiler`, and `Quot.sound`; no `sorryAx` or project axiom.

## Planned release

- Tag: `wowii-176-v1`.
- Title: `WOWII Conjecture 176: counterexample and formal certificate`.
- Body order follows the project release protocol.
- No generated binary assets.

## Release lock

Resolved with `git rev-parse` to
`51faa868b85ce5069e4017dfa97845772435229a`. The annotated tag must dereference
to exactly that preflight snapshot.
