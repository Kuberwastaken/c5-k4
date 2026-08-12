# WOWII 438b upstream preflight and remediation record

Date: **2026-08-12 UTC**

This checklist was added after issue #4915 and PR #4916 were already opened.
Those public writes predate the standing protocol in `UPSTREAM_PROTOCOL.md`.
The record therefore serves both as a complete preflight reconstruction and as
the required remediation gate before editing the open PR into canonical
172/176 form.

## Scope and upstream lock

- Eligible collection: Written on the Wall **II**.
- Upstream repository: `google-deepmind/formal-conjectures`.
- Base SHA when the branch was created:
  `547f309edcc2069c1f61c2465729031c10385540`.
- Existing upstream file/declaration at that SHA: none.
- Existing focused issue/PR before this submission: none.

Duplicate searches used exact terms `GraphConjecture438b`, `Conjecture 438b`,
and the distinctive `alpha_2` / `H_2` formula against upstream issues, PRs,
and files. Numeric-only GitHub hits were rejected as unrelated.

## Source, status, and priority

- Primary WOWII entry: one occurrence under upper bounds on 2-independence,
  marked `O`, dated January 2012.
- Source reading: unambiguous.
- `alpha_2`: maximum order of an induced maximum-degree-at-most-one subgraph.
- `H_2`: vertices of degree at most two.
- Scraped duplicate/matching-section metadata: extraction artifact, not a
  second primary-source statement.
- Durable audit commit: `841ab20`.
- Priority qualification: the arbitrary-subset strengthening follows from the
  published 2022 bound `diss(G) <= alpha(G) + nu_s(G)` plus an elementary
  induced-matching split. Claim only a complete Lean proof/formalization of a
  source-listed-open entry; do not claim a novel mathematical theorem.

## Local mathematical and formal artifacts

- Method trial/proof report commit: `57eda7b`.
- Complete no-`sorry` Lean certificate commit:
  `e62f216625438bc099707e466d2825ab483717a4`.
- Certificate path: `lean/GraphConjecture438b.lean`.
- Warning gate:
  `lake env lean -DwarningAsError=true lean/GraphConjecture438b.lean` — pass.
- Trust assumptions: `propext`, `Classical.choice`, `Quot.sound`.
- Forbidden assumptions: no `sorryAx`, native-decision trust, or
  project-specific axiom.
- Independent audit: 144,923 arbitrary-subset Atlas cases, 992 source cases,
  10 named controls, and 66 structured cases.

The full SHA above was obtained with `git rev-parse e62f216`, not inferred from
the abbreviation.

## Immutable-link checks

Both planned public links returned HTTP 200 under `curl -L` and were opened to
confirm their contents:

- complete external proof:
  <https://github.com/Kuberwastaken/c5-k4/blob/e62f216625438bc099707e466d2825ab483717a4/lean/GraphConjecture438b.lean>;
- status/priority audit:
  <https://github.com/Kuberwastaken/c5-k4/blob/841ab20/results/expansion/wowii_438b_status_audit.md>.

## Canonical public layout

- Issue title: `Formalize the proof of WOWII Conjecture 438b`.
- PR title: `WrittenOnTheWallII: prove conjecture 438b`.
- Issue: [#4915](https://github.com/google-deepmind/formal-conjectures/issues/4915).
- PR: [#4916](https://github.com/google-deepmind/formal-conjectures/pull/4916).
- Base: `main`.
- Head: `Kuberwastaken:prove-wowii-438b`.
- Scope: one new problem file.

Remediation required after this commit:

1. slim the upstream problem file to source-faithful definitions and statement
   with repository-standard `by sorry`;
2. retain the complete proof only at the verified immutable external link;
3. use the 172/176 PR section order;
4. explicitly include the 2022 priority qualification;
5. rerun the target `lake --wfail build`;
6. read back issue/PR/files/base/head and recheck every link.
