# OEIS A111291 formalization-endpoint release checklist

Date: **2026-08-14 UTC**

## Eligibility and classification

- Scope: the exact `research open` declaration merged at
  `google-deepmind/formal-conjectures@b33d8678a28118c95d8d4f60b11faaf39ccff1e6`.
- Complete literal disproof at the real input `x=3/2`.
- Classified as a **real-domain formalization/endpoint erratum**, not a
  disproof of the intended integer or eventual refactorable-number bound and
  not counted as a mathematical kill.
- PR #4450 introduced the declaration on 2026-08-13.  Searches for `111291`
  and `refactorable` found no issue, PR, review comment, or later commit in the
  upstream repository on 2026-08-14.
- No local/remote `oeis-111291-formalization-v1` tag or release exists.
- No upstream issue, PR, or comment will be opened under the current policy.

## Durable artifacts

- Source/status/classification audit and exact argument: `892826d`.
- Independent exact/counting verifier and integer calibration: `892826d`.
- Complete no-`sorry` Lean certificate: `892826d`.
- Lean 4.27.0 warning-as-error elaboration: pass in 7.04 seconds at the frozen
  upstream commit.
- Exhaustive integer calibration: zero failures for `2 <= x <= 1,000,000`;
  the smallest sampled slack is approximately `0.20136` at `x=7`.

## Planned release

- Tag: `oeis-111291-formalization-v1`.
- Title: `OEIS A111291: real-domain counterexample to the merged declaration`.
- The endpoint-erratum classification must appear in the opening paragraph.
- No generated binary assets.

## Release lock

The annotated tag dereferences locally and remotely to
`ae4c77d2c130944eb2e660dab9fd47da25a27ec9`.  The tag object is
`d5570d673248e693ffb39aede194f9f64956a3bf`.

## Publication readback

- Release:
  <https://github.com/Kuberwastaken/c5-k4/releases/tag/oeis-111291-formalization-v1>.
- GitHub confirms the qualified title, non-draft and non-prerelease state,
  publication at `2026-08-14T06:38:21Z`, and zero binary assets.
- The audit, Lean proof, independent verifier, frozen upstream module, and
  authoritative OEIS b-file links all returned HTTP 200.
- The opening explicitly classifies the finding as an endpoint erratum and
  excludes it from the mathematical-kill count.
