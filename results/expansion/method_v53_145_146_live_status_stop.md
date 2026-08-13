# WOWII 145/146 live status gate

Date: **2026-08-13 UTC**

Strict outcome: **KNOWN_PROOF_DOMAIN**.  The correlated cluster stopped before
any transformation was frozen or evaluated.

## Live source state

The audit was performed first, as required, against current
`google-deepmind/formal-conjectures` main commit
`d16e05aded22b8c467a0a27c14b2311f53185006`.

Both source files still display `@[category research open]` and contain
`sorry` on main:

| target | current source blob |
|---|---|
| WOWII 145 | `1a6956440fa676d53df639fea44cd599171d9c68` |
| WOWII 146 | `e900a462229967b91a0621c62c1d4f64b8b45743` |

That branch metadata is not the complete live status.  Both exact statements
already have complete proof submissions under review.

## Existing proof domain

### WOWII 145

[PR #4520](https://github.com/google-deepmind/formal-conjectures/pull/4520)
is open, non-draft, and has a successful upstream project build.  It marks the
unchanged statement solved and links the immutable proof
[`WOW145/145.lean`](https://github.com/DomTheDeveloper/crl/blob/2ee448baa80c98f0c8b9a0c1c3d9421200f99aa5/math/wowii145/WOW145/145.lean).

The linked blob is
`b87364b75f0c0e69ff458054bd23fe564a1c43d0`, 5,601 bytes.  Direct inspection
finds theorem `WOW145.conjecture145_proved` with the same connectedness,
positive complement-local-independence, and integral inequality as current
upstream.  It contains no `sorry`, `admit`, or `native_decide` token.  The
proof handles local-independence minimum at least two by the diametral induced
path bound.  Its minimum-one extremal branch invokes the independently checked
WOWII 146 exceptional theorem.

Thus the proof domain is the entire current universal premise, not merely a
family containing the campaign's equality seeds.

### WOWII 146

[PR #4505](https://github.com/google-deepmind/formal-conjectures/pull/4505)
is open, non-draft, CI-green, and received collaborator approval on
2026-08-11.  Its immutable linked proof is
[`GraphConjecture146Proof.lean`](https://github.com/Mapika/formal-conjectures/blob/60a80606e38cb743326b70defe2cfe55f5b9fc1f/FormalConjectures/WrittenOnTheWallII/GraphConjecture146Proof.lean).

The linked blob is
`49e8bb5460690af2d82cf5c5551b050e5db6d377`, 23,792 bytes.  Direct inspection
finds theorem `conjecture146_core` with the unchanged connectedness,
positive-square-radius premise, and exact upstream conclusion.  It contains
no `sorry`, `admit`, or `native_decide` token.  The proof covers the full
universal domain by a periphery-geodesic tree bound plus the square-radius-one,
diameter-four exceptional case.

A second CI-green solved-status submission,
[PR #4540](https://github.com/google-deepmind/formal-conjectures/pull/4540),
independently links another complete proof.  It is corroboration, not a second
result.

## Stop decision

Main-branch `research open` metadata is lagging live review state.  The exact
unchanged universal targets are already inside complete Lean proof domains;
the #146 proof has additionally passed maintainer review.  A search over a new
equality-seed transformation could neither produce a valid counterexample nor
count as prospective discovery evidence unless those proofs were first shown
invalid.  This audit found no such defect.

Accordingly:

- no transformation was selected or frozen;
- no database gate or development computation was run;
- zero candidates were evaluated;
- #145/#146 remain one correlated cluster, with zero new successes;
- the earlier factor-free equality rows remain calibration and theorem-wall
  evidence only.

No commit, release, issue, PR, or other public action was made.
