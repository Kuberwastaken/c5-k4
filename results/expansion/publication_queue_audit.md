# Scope audit: WoW I 191, WoW I 889, and Graph Brain upper-081

Date: 2026-08-12

## Scope correction

These three items are **not** an upstream `formal-conjectures` publication
queue. That repository's campaign collection is Written on the Wall II; it
does not cover Written on the Wall I or Graph Brain. Complete local Lean
certificates remain useful `c5-k4` artifacts, but source recovery and technical
formalizability do not authorize introducing a new upstream corpus.

An upstream WoW I 191 issue was opened in error as #4914, then immediately
closed with this correction. No PR was opened, and the fork branch was deleted.

This is a publication-readiness audit, not a discovery trial. It checks the
three items frozen in the Method v0.2 Wave 2 publication queue against the
current `google-deepmind/formal-conjectures` layout, GitHub issues and pull
requests, the primary-source links, and the actual logical coverage of the
local Lean files.

## Audit baseline

- `c5-k4` audited at `3ae6df52debfc22e4ed86f75d46446961b3e15a3`.
- `formal-conjectures` upstream baseline audited at
  `547f309edcc2069c1f61c2465729031c10385540`.
- The upstream repository has a `WrittenOnTheWallII/` collection but no
  `WrittenOnTheWallI/` or Graph Brain collection.
- Exact GitHub searches of the upstream repository found no issue, pull
  request, or indexed file for `GraphConjecture191`, `GraphConjecture889`,
  `GraphBrainAlphaUpper081`, the two distinctive WoW I inequalities, the
  Graph Brain source URL, or `edge_con`. A global exact-expression search and
  a search of `Kuberwastaken/c5-k4` issues and pull requests likewise found no
  matching submission. Numeric-only searches return unrelated issue numbers
  and are not evidence of duplicates.
- The Graph Brain source issue
  [math1um/objects-invariants-properties#421](https://github.com/math1um/objects-invariants-properties/issues/421)
  is still open. It was created on 2017-09-07, last updated on 2018-06-26,
  and contains the upper-081 expression in its sole comment.
- The WoW I source URL currently used by both Lean modules resolves correctly,
  by HTTP redirect, to the immutable 2007 Wayback capture. A submission should
  link that final capture directly:
  <https://web.archive.org/web/20070824041950id_/http://www.math.uh.edu/~clarson/wow-july2004.ps>.
- Static scans found no `sorry`, `admit`, `axiom`, `opaque`, or unsafe
  declaration in any of the three local modules. `GraphConjecture191.lean`
  deliberately ends with `#print axioms conjecture191`; this is diagnostic,
  not a custom axiom.
- The pruned shared Lake package link was replaced with a local dependency
  tree at the locked upstream revisions. `lake exe cache get` and
  `lake build FormalConjecturesUtil` then completed successfully (8,057 jobs).
  Fresh `lake env lean -DwarningAsError=true` elaboration passed for all three
  modules. Conjecture 191's `#print axioms` reports only `propext`,
  `Classical.choice`, `Lean.ofReduceBool`, `Lean.trustCompiler`, and
  `Quot.sound`; there is no `sorryAx` or project-specific axiom.
- All executable certificate tests passed in this audit: 3/3 for WoW I 191,
  3/3 for WoW I 889, and 5/5 for Graph Brain upper-081.

## Decision table

| Item | Local Lean coverage | Source/status | Duplicate audit | Decision |
|---|---|---|---|---|
| WoW I 191 | Complete, witness-bearing formal disproof | Source-faithful after visual correction of OCR `<` to printed `<=`; unannotated in the 2004 register | No duplicate local submission | Keep in `c5-k4`; out of upstream scope |
| WoW I 889 | Complete, witness-bearing formal disproof | Source-faithful reading using #822's blue-edge definition; unannotated in the 2004 register | No duplicate local submission | Keep in `c5-k4`; out of upstream scope |
| Graph Brain upper-081 | Conditional arithmetic reduction only | Exact expression remains in an open author-project issue; division-by-zero behavior is a formalization choice | No duplicate local submission | Complete locally if useful; out of upstream scope |

## WoW I Conjecture 191

### What the Lean file proves

[`lean/GraphConjecture191.lean`](../../lean/GraphConjecture191.lean) is a full
formal disproof, not merely an arithmetic certificate. It defines the vertex
deficiency and distance-parity quantities, constructs
`T(7) = L(K_7)` as a finite simple graph, and formally proves:

- connectivity;
- the section hypothesis `sum Odd <= sum Even`;
- minimum vertex deficiency `20`;
- edge count `105`;
- clique number `6`; and
- the contradiction `20 <= 105 / 6`.

The theorem concludes the complete source-level universal statement as
`answer(False)`. The proof has no placeholder or custom axiom. Its immutable
external-proof link should be:

<https://github.com/Kuberwastaken/c5-k4/blob/9247f5c60ca1787cac941a40ead5cfe65522e51d/lean/GraphConjecture191.lean>

The independent exact certificate suite passed all three tests. It also checks
the closed forms and the exact `T(q)` threshold, although the Lean theorem only
needs `T(7)`.

### Source and status caution

The OCR corpus row has `<`, while visual inspection of page 70 of the primary
scan gives `<=`; the Lean theorem correctly follows the scan. The section
heading, rather than the conjecture sentence itself, supplies the parity
hypothesis. The entry has no resolution annotation in the July 2004 register,
and the searches above found no later GitHub resolution. It should therefore
be described as an unannotated, provisionally novel disproof rather than as
independently proven to have remained open continuously since 2004.

### Local artifact disposition

Keep the complete certificate at `lean/GraphConjecture191.lean`. It is outside
the DeepMind repository's WoW II collection and must not receive an upstream
issue or PR. Any independent publication should preserve the primary-scan
correction and inherited section hypothesis prominently.

## WoW I Conjecture 889

### What the Lean file proves

[`lean/GraphConjecture889.lean`](../../lean/GraphConjecture889.lean) is also a
full formal disproof. It specializes conjecture #822's color convention to
triangle-free graphs, constructs the four-fold independent blow-up of `C_5`
(equivalently `complement(C_5[K_4])`), and formally proves:

- connectivity;
- 8-regularity;
- triangle-freeness;
- maximum odd-distance count `8`;
- an empty blue graph, hence blue clique number `1`; and
- the contradiction `8 / 4 <= 1`.

The theorem concludes the full universal statement as `answer(False)`, with
no placeholder or custom axiom. Its immutable external-proof link should be:

<https://github.com/Kuberwastaken/c5-k4/blob/25ec2145bbad0b46f0e25eaca9e03300d242b5a5/lean/GraphConjecture889.lean>

All three independent certificate tests passed.

### Source and status caution

The formalization correctly uses #822: a nonedge is blue exactly when adding
it preserves triangle-freeness, equivalently when its endpoints have no common
neighbor. The phrase "a blue clique with w/4 vertices" is represented as an
at-least inequality over the reals; for this witness `w/4 = 2`, so there is no
rounding ambiguity. The entry is unannotated in the source and no exact later
resolution was found, so the same provisionally-novel wording as for #191 is
appropriate.

### Local artifact disposition

Keep the complete certificate at `lean/GraphConjecture889.lean`. It is outside
the DeepMind repository's WoW II collection and must not receive an upstream
issue or PR. Any independent publication should preserve the #822
cross-reference and explain the real-valued rendering of `w/4`.

## Graph Brain alpha upper bound 081

### What the Lean file proves—and does not prove

[`lean/GraphBrainAlphaUpper081.lean`](../../lean/GraphBrainAlphaUpper081.lean)
provides finite definitions of edge and vertex connectivity and proves the
arithmetic fact that any graph with invariant tuple
`(alpha, diameter, lambda, kappa) = (2, 2, 4, 1)` violates the bound. It also
proves that supplying a connected order-nine graph with those four equalities
would refute the universal statement.

It does **not** construct the order-nine windmill in Lean or prove any of those
four equalities for it. Therefore
`upper081Statement_false_of_windmill_certificate` is a conditional theorem,
not a Lean proof that upper-081 is false. The Python certificate and all five
tests do verify the witness and database gate, but they do not fill this Lean
gap. No `formal_proof using lean4` claim should be made yet.

The source expression is in the sole comment on the still-open author-project
issue. Use the exact comment anchor, not the issue top:

<https://github.com/math1um/objects-invariants-properties/issues/421#issuecomment-327846086>

### Local artifact disposition after completion

Complete the local `c5-k4` certificate only if it remains useful to this
project. Graph Brain is outside the DeepMind campaign scope and must not
receive an upstream issue or PR.

### Blocking work

1. Define the nine-vertex windmill (two `K_5` copies sharing one hub) in Lean.
2. Prove `indepNum = 2` and `diam = 2` for that concrete graph.
3. Prove `edgeConnectivity = 4` and `vertexConnectivity = 1` for the concrete
   graph under the exact finite definitions in the module.
4. Derive an unconditional theorem `answer(False) ↔ upper081Statement` (or an
   equivalent unconditional negation), and only then label the file a full
   Lean disproof.
5. Ask reviewers to confirm the formalization of the source evaluator's
   division-by-zero behavior. The posted expression alone does not document
   this semantic convention, even though it does not affect the windmill
   witness because `4 - 1` is positive.
6. The fresh warning-as-error build now passes; retain it as a regression gate
   while completing the concrete witness.

Until those steps are complete, upper-081 remains an exact computational
counterexample report rather than a complete local Lean disproof.

## Upstream disposition

No WoW I or Graph Brain issue or PR should be opened in
`google-deepmind/formal-conjectures`. The active upstream queue is restricted
to WoW II and other collections already present there.
