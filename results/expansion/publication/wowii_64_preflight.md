# WOWII 64 upstream publication preflight

Date: **2026-08-12 UTC**

This is the mandatory public-write gate from `UPSTREAM_PROTOCOL.md`. The
submission will follow the issue/PR layout of WOWII 172 and 176 exactly and
will claim only a Lean formalization of an already-published disproof.

## Scope and upstream lock

- Eligible collection: Written on the Wall **II**.
- Repository: `google-deepmind/formal-conjectures`.
- Current upstream `main`: `547f309edcc2069c1f61c2465729031c10385540`.
- `FormalConjectures/WrittenOnTheWallII/GraphConjecture64.lean`: absent.
- Focused declaration, issue, or PR: absent.
- Exact duplicate queries rerun immediately before this checklist:
  `GraphConjecture64`, `"Conjecture 64"`, `"WOWII 64"`, and
  `"WOWII Conjecture 64"` across the upstream tree, issues, and PRs.
  Numeric-only issue/PR 64 hits were unrelated.

## Source, reading, status, and priority

- Primary source: the live WOWII `all.html`, `open.html`, and definition 32.
- Source marker: `O`, dated 25 March 2004.
- Natural reading:
  `f(G) >= ceil(sqrt(alpha(G) * (1 + (n mod Delta(G)))))`.
- `%` is natural-number remainder before coercion to the reals.
- Jonas J. Gebendorfer published the Conjecture 64 disproof, a smaller
  18-vertex witness, and an infinite family on 2026-07-26, DOI
  `10.5281/zenodo.21595503`. The public submission will credit that priority
  prominently and will not claim a new or first disproof.
- Durable source/status/priority audit:
  `41d71ec2729ea9a00440653f5e89359bf3c57aae`.

## Local artifacts and verification

- Complete no-`sorry` Lean certificate:
  `8c0a76079e5c7153bdc2dd6d97a9821ee25b2620`,
  `lean/GraphConjecture64.lean`.
- Independent exact verifier and audit:
  `41d71ec2729ea9a00440653f5e89359bf3c57aae`.
- Verifier command: `timeout 60s python3 scripts/verify_wowii_64.py`.
- Verifier result: pass in under 0.1 seconds; all 1,140 triples and 15,504
  five-subsets exhausted; `n=20`, `Delta=11`, `alpha=2`, `f=4`, natural
  `20 % 11=9`, and conjectured RHS `5`.
- Lean command:
  `lake env lean -DwarningAsError=true lean/GraphConjecture64.lean` — pass.
- Trust assumptions: `propext`, `Classical.choice`, `Lean.ofReduceBool`,
  `Lean.trustCompiler`, and `Quot.sound`; no `sorryAx` or project-specific
  axiom.

All full SHAs above were obtained with `git rev-parse`, not inferred from
abbreviated hashes.

## Immutable links

Each link returned HTTP 200 under `curl -L` and was opened/read to confirm its
contents:

- complete certificate:
  <https://github.com/Kuberwastaken/c5-k4/blob/8c0a76079e5c7153bdc2dd6d97a9821ee25b2620/lean/GraphConjecture64.lean>;
- source/status/priority audit:
  <https://github.com/Kuberwastaken/c5-k4/blob/41d71ec2729ea9a00440653f5e89359bf3c57aae/results/expansion/wowii_64_status_audit.md>;
- independent verifier:
  <https://github.com/Kuberwastaken/c5-k4/blob/41d71ec2729ea9a00440653f5e89359bf3c57aae/scripts/verify_wowii_64.py>;
- Method v0.3:
  <https://github.com/Kuberwastaken/c5-k4/blob/b001771f367e1de30099e9afee34157b73a47dd5/METHOD.md>.

## Canonical public layout

- Issue title: `Formalize the disproof of WOWII Conjecture 64`.
- PR title: `WrittenOnTheWallII: disprove conjecture 64`.
- Issue sections, in order: Summary; Counterexample; Relationship to the
  C5[K4] campaign; immutable result/method links; Complete formal certificate;
  Source/status note; AI assistance disclosure.
- PR sections, in order: Summary; Follow-up discovery pattern; Formal proof;
  Source/status note; Verification; AI assistance disclosure.
- Branch will start at the exact upstream SHA above, contain one problem file,
  use the repository-standard `by sorry`, close the issue, and target `main`.
- After each public write, the rendered body, URLs, files, base, head, and CI
  state will be read back before continuing.

No public write is authorized until this checklist commit is pushed.
