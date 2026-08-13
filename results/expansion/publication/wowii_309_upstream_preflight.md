# WOWII 309 upstream issue/PR preflight

Date: **2026-08-13 UTC**

## Authorization and scope

- The user explicitly authorized cross-verified DeepMind issues and PRs in the
  current turn.
- The target is Written on the Wall II Conjecture 309, a collection accepted by
  `google-deepmind/formal-conjectures`.
- The contribution is a formalization of Gebendorfer's already-published
  disproof, not a novelty or first-priority claim.
- One issue and one PR will cover this problem.

## Upstream and duplicate lock

- Upstream repository: `google-deepmind/formal-conjectures`.
- Base branch: `main`.
- Audited base SHA: `d16e05aded22b8c467a0a27c14b2311f53185006`.
- Proposed head: `Kuberwastaken:formalize-wowii-309`.
- Current upstream has no
  `FormalConjectures/WrittenOnTheWallII/GraphConjecture309.lean` and no path
  history for that filename.
- GitHub issue/PR history was searched, including closed and merged records,
  with `"WOWII 309"`, `"Conjecture 309" "Written on the Wall"`, and
  `"GraphConjecture309"`. No matching record exists. Numeric issue #309 is the
  unrelated Erdős Problem 80.
- The fork has no existing `formalize-wowii-309` PR.

## Source, status, and priority

- Complete WOWII list:
  `http://cms.uhd.edu/faculty/delavinae/research/wowII/all.html` (HTTP 200).
- Source-maintained status: `O`.
- Mathematical status: false by Jonas J. Gebendorfer, *An Infinite Family of
  Counterexamples to Written on the Wall II, Conjecture 309*, published
  2026-07-25, DOI `10.5281/zenodo.21553295` (HTTP 200).
- The planned text credits Gebendorfer and makes no new-disproof claim.
- The exact complement-neighborhood reading, the undefined complete-graph
  minimum, and six nearby conventions are recorded in the status audit.

## Durable artifacts

- Complete certificate:
  `c9daf0f594d6d5b264c6cd54dc9eec488cb64741/lean/GraphConjecture309.lean`
  (HTTP 200).
- Source/status/priority audit:
  `05c3546ca8aa64ecb0a3b8ba456b56b07ba61b12/results/expansion/wowii_309_status_audit.md`
  (HTTP 200).
- Exact verifier:
  `57f2826673b2b5b5d3695947900537f9b959b3de/scripts/verify_wowii_309.py`
  (HTTP 200).
- Proposed upstream file:
  `FormalConjectures/WrittenOnTheWallII/GraphConjecture309.lean`.

## Verification

- `python3 scripts/verify_wowii_309.py`: PASS in 0.214 seconds, below the
  60-second cap; six readings fail on the witness; 989/994 Atlas controls are
  applicable, with zero violations.
- External certificate against current upstream:
  `lake env lean -DwarningAsError=true ../c5-k4/lean/GraphConjecture309.lean`:
  PASS.
- `#print axioms` for the external theorem reports only `propext`,
  `Classical.choice`, `Lean.ofReduceBool`, `Lean.trustCompiler`, and
  `Quot.sound`; no `sorryAx` or project-specific axiom.
- Proposed upstream module:
  `lake --wfail build FormalConjectures.WrittenOnTheWallII.GraphConjecture309`:
  PASS (8,053 jobs).
- Clean GitHub Actions validation:
  `https://github.com/Kuberwastaken/c5-k4/actions/runs/31704036464`:
  PASS. The run checked out exact upstream SHA
  `d16e05aded22b8c467a0a27c14b2311f53185006`, overlaid the staged candidate,
  passed the exact verifier, built `FormalConjecturesUtil`, compiled the
  external certificate warning-clean, generated aggregate modules, built the
  candidate dependency closure, and completed the full upstream
  warning-as-error corpus build.

## Planned public records

- Issue title: `Formalize the disproof of WOWII Conjecture 309`.
- PR title: `WrittenOnTheWallII: disprove conjecture 309`.
- The issue and PR bodies follow the 172/176 section order and include immutable
  certificate, audit, verifier, source-status, attribution, and AI-assistance
  disclosures.
- WOWII 64 is excluded because issue #4917 is already closed. Releases 172,
  176, 181, and 430a are excluded because each already has an open issue and
  PR. Existing/open/closed records will not be duplicated.
