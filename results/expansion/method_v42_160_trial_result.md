# Prospective WOWII 160 trial result

Date: **2026-08-13 UTC**

Outcome: **bounded hold — no crossing survived the frozen search or Atlas
sanity gate.** No novelty claim or public action is warranted.

## Frozen search result

The trial evaluated the precommitted block-graph, friendship/windmill,
constrained triangle-cactus, and one-move C4-free surgery grammar without
adaptive expansion:

- 144 distinct generated representatives;
- 89 connected C4-free representatives with exact profiles;
- 0 crossings of `Ls < maxL + maxT`;
- 51 exact equality cases.

The high equality rate confirms that these families inhabit the intended wall,
but this bounded grammar supplied no direction across it. This is a negative
prospective result, not evidence that the inequality holds outside the tested
scope.

## Atlas and named-control sanity

All 995 connected unlabeled Atlas graphs of orders 2 through 7 were checked.
Of these, 90 are C4-free; none crosses the wall and 74 are exactly tight.

Named controls also behaved as expected:

| Graph | `Ls` | `maxL` | `maxT` | RHS | Result |
|---|---:|---:|---:|---:|---|
| `K3` | 2 | 1 | 1 | 2 | tight |
| claw | 3 | 3 | 0 | 3 | tight |
| friendship `F2` | 4 | 2 | 2 | 4 | tight |
| `P5` | 2 | 2 | 0 | 2 | tight |
| `C5` | 2 | 2 | 0 | 2 | tight |

`C4` was correctly rejected from the active branch because the statement's
four-cycle condition concerns a simple four-cycle, not only an induced one.

## Independent recomputation

The nontrivial tight control `F2` was recomputed independently of the connected
dominating-set evaluator. Direct enumeration found all 9 spanning trees and a
maximum of 4 leaves. Separate neighborhood calculations gave local
independence values `[2,1,1,1,1]`, triangle counts `[2,1,1,1,1]`, and confirmed
C4-freeness. Hence `Ls = 4 = 2 + 2`.

## Current-status gate

The current upstream module still carries the research/open metadata and a
`sorry`, but this is not an unclaimed target:

- source-correction PR #4443 merged on 2026-07-26;
- proof-proposal issues #4569 and #4575 remain open;
- PR #4576 remains open and unmerged and links two complete independent Lean
  proofs.

Therefore even a future counterexample would require renewed statement and
priority review; this run has no release or novelty path.

## Interpretation

The useful signal is the prevalence of equality: 51/89 frozen-family profiles
and 74/90 C4-free Atlas profiles lie on the wall. The precommitted local
surgeries did not decouple the two neighborhood terms from maximum spanning-
tree leaves. Further work should only resume under a newly frozen mechanism
that supplies a genuinely different degree of freedom, rather than enlarging
this grammar after observing the outcome.
