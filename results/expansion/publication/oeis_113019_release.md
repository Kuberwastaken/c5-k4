# OEIS A113019 fixed-point release checklist

Date: **2026-08-14 UTC**

## Eligibility and classification

- Scope: the intended fixed-point question in A113019 and the exact RHS of
  the `research open` declaration at
  `google-deepmind/formal-conjectures@b33d8678a28118c95d8d4f60b11faaf39ccff1e6`.
- Exact new witness: `387420489 = 9^9` has nine digits and digital root nine.
- Complete reduction shows the literal function's fixed points are exactly
  `1`, `32`, and `387420489`.
- Classified as **intended question answered / source correction candidate**,
  not a refutation of the opaque `answer(sorry)` biconditional.
- Current OEIS still asks whether any fixed point beyond `1,32` exists.
  Dated GitHub and web searches found no prior A113019 report containing this
  witness; claim only apparently unrecorded as of 2026-08-14.
- No local/remote `oeis-113019-fixed-points-v1` tag or release exists.
- No upstream issue, PR, or comment will be opened under the current policy.

## Durable artifacts

- Three-arm derivation, source/status audit, and independent replay: `ebd82bb`.
- Dedicated result/classification audit: `7bc2a0c`.
- Independent exhaustive fixed-point verifier: `7bc2a0c`.
- Complete no-`sorry` Lean witness: `7bc2a0c`.
- Lean 4.27.0 warning-as-error elaboration: pass in 6.12 seconds at the frozen
  upstream commit.

## Planned release

- Tag: `oeis-113019-fixed-points-v1`.
- Title: `OEIS A113019: the third and final fixed point is 9^9`.
- The opening must distinguish the intended answer from the opaque formal
  wrapper and qualify the priority search.
- No generated binary assets.

## Release lock

The annotated tag dereferences locally and remotely to
`23187774664723186f9e6d63c3b8af71912b8957`.  The tag object is
`29421fbb19aeb1feee519510c7175b9e4783723b`.

## Publication readback

- Release:
  <https://github.com/Kuberwastaken/c5-k4/releases/tag/oeis-113019-fixed-points-v1>.
- GitHub confirms the intended title, non-draft and non-prerelease state,
  publication at `2026-08-14T06:47:54Z`, and zero binary assets.
- Every immutable GitHub artifact link returned HTTP 200.
- OEIS's Cloudflare layer returned HTTP 403 to the automated page readback;
  the source content and status had already been independently audited, and
  this transport response is not recorded as a mathematical verification.
- The release distinguishes the intended source answer from the opaque
  `answer(sorry)` wrapper and qualifies bibliographic priority.
