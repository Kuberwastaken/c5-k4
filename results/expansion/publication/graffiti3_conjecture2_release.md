# Graffiti³ Conjecture 2 release checklist

Date: **2026-08-14 UTC**

## Eligibility and classification

- Exact source statement and `d₂` convention recovered from the primary PDF.
- Connected 25-vertex tree `DS(11,12)` independently verifies
  `RGA²<23=alpha` with a rational-square certificate.
- Balanced `DS(k,k)` supplies an infinite family for every `k>=12`.
- Corrected frozen run `31789142496` has three valid artifact manifests and
  three replayable ledger chains; two arms reached the same canonical graph.
- First run `31788835531` is excluded because its internal JSON hash chain was
  not replayable. Its chronology is preserved rather than silently replaced.
- Public source/status/prior-art audit through 2026-08-14 found no earlier
  resolution or claim.
- No local tag, remote tag, or GitHub release named
  `graffiti3-conjecture2-double-star-v1` exists at preflight.
- No upstream issue, pull request, or comment will be opened under the current
  repository-only publication policy.

## Durable artifacts

- Verified mathematical result and chronology: `c936765`.
- Complete arithmetic-only Lean certificate: `88fd614`.
- Independent exact verifier: `66d3b1a`.
- Corrected GitHub Actions replay: `31789142496`.
- Lean warning-as-error CI: run `31790179797` passed against pinned upstream
  commit `942fb149e782a56c2719c543ab58e093f733acb4`.

## Planned release

- Tag: `graffiti3-conjecture2-double-star-v1`.
- Title: `Graffiti³ Conjecture 2: double-star counterexamples`.
- Target: the final README/certificate commit after CI passes.
- Non-draft, non-prerelease, no generated binary assets.
- The body must retain the notation caveat, rejected-run chronology, formal
  scope limitation, dated priority qualification, and AI disclosure.

## Release lock

Release published and read back successfully:

- URL: `https://github.com/Kuberwastaken/c5-k4/releases/tag/graffiti3-conjecture2-double-star-v1`
- annotated tag object: `ba51d7bc7da5b0b372225363394b4cdf9387af30`
- peeled target commit: `332ec3dcbf74469754e53e09b22eb82977ff8507`
- published: `2026-08-14T10:02:37Z`
- draft/prerelease: `false` / `false`
- every immutable artifact link in the release body returned HTTP 200 at
  readback.
