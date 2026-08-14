# OEIS A109074 formalization-erratum release checklist

Date: **2026-08-14 UTC**

## Eligibility and classification

- Scope: the exact `research open` declaration merged at
  `google-deepmind/formal-conjectures@b33d8678a28118c95d8d4f60b11faaf39ccff1e6`.
- Complete literal disproof at the stated lower endpoint `n=1`.
- Classified as a **formalization/source erratum**, not a disproof of the
  corrected number-theory identity and not counted as a mathematical kill.
- The printed A109074 ratio has a one-step index shift, and the Lean module's
  local `b` is independently not the referenced A005156 sequence.
- PR #4450 introduced the declaration on 2026-08-13.  Repository-wide issue
  and PR search for `109074` returned no records on 2026-08-14.
- No local/remote `oeis-109074-formalization-v1` tag or project release exists.
- No upstream issue, PR, or comment will be opened under the current campaign
  policy.

## Durable artifacts

- Source/status/classification audit and exact arithmetic: `65859c4`.
- Independent executable verifier: `65859c4`.
- Complete no-`sorry` Lean certificate: `65859c4`.
- Verifier result: `frac 1 = 1`, `b 1 = 1`, `b 2 = 3`, hence formal RHS `3`.
- Lean 4.27.0 warning-as-error elaboration: pass in 5.81 seconds at the frozen
  upstream commit.

## Planned release

- Tag: `oeis-109074-formalization-v1`.
- Title: `OEIS A109074: counterexample to the merged formal declaration`.
- The erratum classification must appear in the opening paragraph.
- No generated binary assets.

## Release lock and publication readback

Pending creation of the preflight commit and release.  A follow-up commit will
record the exact tag target, GitHub readback, and immutable-link checks.
