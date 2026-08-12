# WOWII 172 project-release checklist

Date: **2026-08-12 UTC**

## Eligibility and novelty

- Scope: Written on the Wall II, already represented in the frozen
  `formal-conjectures` corpus.
- Result: complete counterexample, not a bounded hold or interpretation-only
  arithmetic core.
- Primary and alternate distance readings were audited; `D_9` violates both.
- Targeted exact-statement, formula, conjecture-number, literature, upstream
  tree/history, and GitHub searches found no earlier resolution. The claim is
  only **apparently unrecorded**, not absolute priority.
- Existing public upstream issue/PR #4908/#4909 are this project's own earlier
  submission, not an external priority conflict.
- `gh release list`, local tags, and remote tags contain no WOWII 172 release.
- No new upstream issue, PR, or comment will be opened.

## Durable artifacts

- Result/source audit and expanded verifier commit:
  `bf10abe232b96d98db895a879d25a1343ccd5c77`.
- Complete no-`sorry` Lean certificate commit:
  `a948106ad2d2a5d291b6b99575fe78bf373e7e02`.
- `timeout 60s python3 scripts/verify_wowii_176.py`: pass; 995 connected Atlas
  graphs satisfy both readings, and exact `D_L` formulas hold for `L=5..12`.
- `timeout 60s lake env lean -DwarningAsError=true
  lean/GraphConjecture172.lean`: pass.
- Trust assumptions: `propext`, `Classical.choice`, `Lean.ofReduceBool`,
  `Lean.trustCompiler`, and `Quot.sound`; no `sorryAx` or project-specific
  axiom.

## Planned release

- Tag: `wowii-172-v1`.
- Title: `WOWII Conjecture 172: counterexample and formal certificate`.
- Target: the release-lock commit recorded below.
- Body order: Summary; Counterexample; Relationship to the C5[K4] campaign;
  immutable artifacts; Complete formal certificate; Reading/priority note; AI
  assistance disclosure.
- No generated binary assets; the committed proof, report, and verifier are
  the durable artifacts.

## Release lock

Resolved target commit from `git rev-parse`:
`64abb3ce00e6ac34ac8358baa9798511d0ca8ec0`. The tag must resolve to exactly
that commit; this follow-up record is intentionally not included in the tagged
snapshot so the target can be recorded without a self-referential hash.
