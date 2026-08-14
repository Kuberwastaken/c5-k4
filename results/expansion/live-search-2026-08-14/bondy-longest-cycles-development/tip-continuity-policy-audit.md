# Bondy tip-continuity policy audit

**Audit date:** 2026-08-14 UTC

**Disposition:** `GO_REVISE`

**Blob-only alternative:** `STRICT_STOP`

This is a read-only policy and mathematical-source audit. It does not alter
the v2 gate or freeze, authorize a retry or activation, dispatch a workflow,
evaluate a target row, or authorize publication or any other public action.

## Decision

Replacing the v2 requirement that live upstream `main` equal the pinned
whole-repository commit is safe only if v3 also requires both descendant
history continuity and semantic-dependency continuity.

An unchanged target blob is necessary but is not sufficient in general. Lean
source bytes can retain the same spelling while denoting a different
proposition if an imported definition, notation, instance, macro, attribute,
or dependency revision changes. Therefore:

- target-blob equality alone is `STRICT_STOP`;
- target-blob equality plus the ten v3 requirements below is `GO_REVISE`;
- any actual target, import-closure, or toolchain change remains a strict stop
  pending a new source and semantic audit.

The current `b5ac...2411` delta is safe under that revised rule because it is
linear descendant history and does not touch the Bondy target, its
in-repository import closure, or dependency/toolchain pins.

## Exact upstream identities and delta

The frozen upstream identity is:

- commit `b5acb0ff13e38084105b7fe020ba0d59c1925bc5`;
- root tree `4f6c9bd17fdfdc264f54b26862ce768743da5d63`.

The observed live upstream identity is:

- commit `2411d22e1bd550d050d0eac6c1fb379a76a3e7c5`;
- root tree `f6b52f1d3f63b365d6f8c405623d5f7a4e674efc`.

The GitHub comparison reports `status=ahead`, `ahead_by=2`, `behind_by=0`,
and the following linear history:

1. `a2a45c07539a519aa264f7780a8cd2a1a5f46e3e`, parent
   `b5acb0ff13e38084105b7fe020ba0d59c1925bc5`, tree
   `7a07d9fed38752621063ed78591565f1f08dbbd9`:
   - modifies `AUTHORS` by adding one author;
   - adds `FormalConjectures/ErdosProblems/506.lean`.
2. `2411d22e1bd550d050d0eac6c1fb379a76a3e7c5`, parent
   `a2a45c07539a519aa264f7780a8cd2a1a5f46e3e`, tree
   `f6b52f1d3f63b365d6f8c405623d5f7a4e674efc`:
   - modifies only
     `FormalConjectures/WrittenOnTheWallII/GraphConjecture59.lean`, changing
     WOWII 59 from `research open` to `research solved` and expressing its
     negative answer as `answer(False)`.

No other path appears in the comparison. In particular, no Bondy file,
shared utility file, package manifest, dependency lock, or Lean toolchain file
changed.

## Bondy target and import relevance

The target path is
`FormalConjectures/Arxiv/2606.03696/BondyLongestCycles.lean`.
At both the pinned and live commits it has:

- Git blob SHA-1 `c4c5cb1983936860d5a4a7208b3f04bd201290d4`;
- raw-file SHA-256
  `562fbbb0ec47041a61017bb85ec0c7e9aa6fc98cf132be3022268a7dc60e9004`;
- byte-for-byte equality under a direct raw-file comparison.

The file directly imports only `FormalConjecturesUtil`. That shared module in
turn publicly imports Mathlib, `FormalConjecturesForMathlib`,
`FormalConjecturesUtil.Answer`, and the repository linter modules. None of
those files, their recursively imported in-repository dependencies, or the
external dependency/toolchain pins appears in the delta.

The import direction matters. Both the new Erdős 506 module and the changed
WOWII 59 module import `FormalConjecturesUtil`; the Bondy module does not
import either of them. They are sibling consumers of the shared utility, not
dependencies of Bondy. Lean does not load sibling modules merely because
they exist in the same repository. The `AUTHORS` change is non-semantic.

Consequently, the two upstream commits cannot alter the parsed or elaborated
meaning of the Bondy declaration through its import graph. They can change
whole-repository identity and unrelated database contents, which is why v2
failed, but they do not change this target's source, status, or semantics.

## Exact v3 requirements

1. **Historical anchor.** Preserve the existing pinned commit, root tree,
   target path, target blob, raw target SHA-256, and primary-paper SHA-256.
   Verify the commit object exists, its root tree is exactly the frozen tree,
   and the pinned tree entry at the target path is exactly the frozen blob.

2. **Live identity and ancestry.** Resolve and record the live `main` commit
   and its root tree. Require the frozen commit to be an ancestor of live
   `main`, equivalently that the merge base is the frozen commit and the
   history is not rewritten or divergent. Do not require the live commit or
   live root tree to equal the frozen values.

3. **Complete delta.** Fetch the relevant Git objects and compute a complete
   local Git diff from the frozen commit to the resolved live commit. Do not
   rely solely on GitHub Compare's file-list limits. Record every commit and
   changed path deterministically.

4. **Live target identity.** Resolve the live target tree entry and require
   its object type, mode, blob SHA-1, raw byte count, and raw SHA-256 to equal
   the frozen target. Fetch and compare both the pinned and live raw bytes;
   do not infer equality merely from a path or API metadata field.

5. **Semantic closure continuity.** Freeze the recursively resolved
   in-repository import closure of the Bondy module and require every closure
   path's live blob to equal its pinned blob. Also freeze and compare
   `lean-toolchain`, `lakefile.*`, `lake-manifest.json`, and every external
   dependency revision needed to elaborate the target. A closure or toolchain
   delta cannot be waived automatically even when the target blob is equal.

6. **Exact declaration shape.** Require exactly one target declaration with
   the exact name `bondy_conjecture`, the exact
   `@[category research open, AMS 5]` attribute, the exact
   `answer(sorry) ↔` wrapper, and the frozen `by sorry` placeholder shape.
   Reject a solved category, `answer(False)`, missing or replaced `sorry`, a
   duplicate declaration, or parse failure. These checks are defense in depth
   in addition to full target-byte equality.

7. **Complete open-PR bindings.** In both brackets, enumerate every page of
   current open pull requests and every page of changed files for each pull
   request. Bind canonical full PR identities to complete, sorted changed-path
   lists and hashes. Require equality of the full bindings before and after,
   not merely equality of PR numbers or identities. Require no open PR to
   touch the target, its semantic import closure, or toolchain/lock files.

8. **Full bracketed live surface.** Each bracket must include the live main
   commit and tree, live target identity and bytes, known issue #4858, known
   PR #4879, the exact three frozen issue-search result sets, the standalone
   repository search, and the complete open-PR bindings. Require canonical
   before/after byte equality for the whole snapshot.

9. **Independent source and contamination controls.** Preserve the exact
   primary PDF hash, exact known issue/PR state and merge identity, exact
   allowed search result sets, zero standalone-repository hits, and exact
   local-contamination history. Any newly discovered resolution or duplicate
   remains disqualifying even when the source files are unchanged.

10. **Versioned fail-closed handoff.** Emit a canonical v3 attestation that
    records the pinned identity, live identity, ancestry proof, full delta,
    closure bindings, complete live surfaces, and every Boolean check. Update
    the immutable freeze verifier and target-execution lock together so the
    candidate process accepts only the exact reviewed v3 schema and refuses a
    v1, v2, incomplete, noncanonical, or mismatched attestation.

## Strict-stop conditions

The v3 gate must stop before target evaluation on any of the following:

- the frozen commit, root tree, target entry, blob, raw bytes, or paper hash
  is unavailable or mismatched;
- live `main` is missing, moves during the bracket, is not descended from the
  frozen commit, or reflects rewritten/divergent history;
- complete commit or changed-path enumeration cannot be proved, including
  truncation, pagination ambiguity, duplicate identities, timeouts, rate
  limiting, or any API/Git error;
- the live target is absent, renamed, not a regular blob, mode-changed, or
  differs in blob, byte count, raw SHA-256, or raw bytes;
- any in-repository semantic-closure file or any Lean/Mathlib toolchain,
  package, or lock revision differs from the pin;
- semantic closure resolution is incomplete or ambiguous;
- the exact category, open status, theorem name, `answer(sorry) ↔` wrapper,
  unique declaration count, or `sorry` placeholder shape drifts;
- any open PR touches the target, semantic closure, or dependency/toolchain
  pins;
- before/after snapshots or full PR file bindings differ;
- issue #4858, PR #4879, an allowed issue-search set, standalone-repository
  count, primary-source identity, or local-contamination history differs;
- the v3 attestation is absent, noncanonical, incomplete, wrong-schema, or
  inconsistent with the checked-out campaign commit.

Unrelated descendant changes may pass only after they are completely
enumerated and shown not to intersect the target, semantic closure, or frozen
status/duplicate surfaces. A strict stop caused by a genuine dependency
change can be cleared only by a fresh semantic audit and an explicitly
reviewed new freeze; it is not an automatic repin.

## Invalid run 31845837185

GitHub Actions metadata for workflow run `31845837185` records:

- workflow: `Bondy longest cycles DEVELOPMENT v2 (disabled by default)`;
- checked-out head: `dfcc6675517fc67898a39f34d1c2af1b54a8e19a`;
- `target-free-preflight`: `failure`;
- the failed step: `Recheck source, open status, duplicates, and primary hash`;
- `candidate-search`: `skipped`, with an empty step list.

The workflow places the only target process in `candidate-search`, after its
own exact live gate. The executed preflight job contains only freeze checks,
target-free constructor tests, the fixed source-control replay, compilation
of the independent replay binary without candidate execution, and the live
source/status gate. Because the prerequisite preflight failed, GitHub skipped
the entire dependent candidate job before checkout or any target step.

It follows mechanically that run `31845837185` evaluated zero target rows and
emitted zero candidate, terminal, ledger, verification, or uploaded target
artifacts. Commit `c13d9f3` records the same classification as
`INVALID_PRE_EVALUATION_SOURCE_DRIFT`, with candidate job skipped, target rows
`0`, target artifacts `0`, and target results `0`. The run is not mathematical
evidence.

## Rate-limit caveat and authorization boundary

The run-time record states that the v2 gate failed solely on the exact-main
check after observing live prefix `2411d22e`; the other v2 checks, including
the complete 274-open-PR changed-file scan and bracket stability, passed in
that run. A later independent audit attempt reconfirmed the commit delta and
target raw-byte identity, but a fresh full-surface gate attempt received a
GitHub HTTP 403 rate-limit response while fetching open-PR changed paths and
correctly emitted no attestation.

Therefore this document supports only the policy conclusion `GO_REVISE`. It
does not certify that the dynamic issue/search/repository/open-PR surface is
still unchanged at a later instant. Any future activation must wait for API
availability and obtain a new, complete, stable, passing v3 bracket. Rate
limiting, missing output, or partial enumeration is itself a strict stop.
