# Method v0.2 development Wave 2: frozen manifest

Frozen: **2026-08-12 UTC**
Method predecessor: `0287c2eb53eaa29cc2e11aabfc9ba58f5e5ae12e`
Wave 1 completion: `c3d0a49`
WOWII transcription: `data/wowii-conjectures.json` at this manifest commit
Upstream baseline: `google-deepmind/formal-conjectures` `547f309e`

This manifest is committed before any Wave 2 construction result is evaluated.
All targets are development-set statements already published in their source
corpora. Nothing here will later be counted as held-out evidence.

## Lessons imported from Wave 1

- Gate conditional branches separately.
- Derive quotient/family necessary conditions before optimizing weights.
- Treat persistent unit slack plus a structural reduction as a theorem signal.
- A surgery that repeatedly reaches equality needs a new core geometry, not a
  silently enlarged edge-edit budget.
- Continue publishing zeroes, errata, ambiguity, and theorem signals alongside
  disproofs.

Every exact optimization call remains capped at 60 seconds. Results are written
incrementally to one report per cluster and independently recomputed before any
novelty or disproof claim.

## Trial F: WOWII 382e

Source statement:

```text
For every connected graph of order greater than two,
gamma_2(G) <= Maxine(G) + gamma(G).
```

The source's `Maxine` is an algorithmic greedy maximum-degree-deletion output,
not ordinary independence. Both the deterministic source reading and the best
tie-choice reading passed the existing control gate. Uniform `C5` clique
blow-ups and two nonuniform carrier variants attain `4 = 2 + 2`.

Pre-evaluation obstruction: cycle-clique blow-ups make two-domination obey a
four-vertex window while both domination and Maxine remain two; reweighting the
same quotient cannot raise the left side alone.

Pre-evaluation prediction: false-twin bundles or a small clique-substitution
over a non-cycle quotient may force an additional two-dominator while leaving
ordinary domination at two and allowing the greedy deletion process to finish
with two survivors. The primary test is whether this separation can occur for
both frozen Maxine readings.

Frozen bounds:

- connected quotient graphs through order eight;
- positive false-twin and clique substitutions of total order at most 60;
- structured double-hub, theta, and short-path cores before generic quotients;
- exact two-domination and domination, with each solve capped at 60 seconds;
- immediate stop if a quotient-level necessary inequality prunes all weights.

## Trial G: WOWII 438b

Source statement:

```text
alpha_2(G) <= alpha(G) + alpha(G[V-H_2]) + |E(G[H_2])|,
```

where `H_2` is the set of vertices of degree at most two. It passed the existing
control gate and is tight on several odd-cycle clique blow-ups and nonuniform
carrier variants.

Pre-evaluation theorem baseline: every induced maximum-degree-one subgraph is
bipartite, so `alpha_2(G) <= 2 alpha(G)`. A crossing therefore must exploit a
nonempty `H_2` for which `alpha(G[V-H_2])` is substantially smaller than
`alpha(G)`, without paying the induced-edge correction.

Pre-evaluation prediction: attach an independent low-degree layer to a dense
core so that many `H_2` vertices enter a 2-independent set while a common core
neighborhood suppresses `alpha(G[V-H_2])`. Pendant matchings are expected to be
compensated by `alpha(G)` or `|E(G[H_2])|`; shared-neighborhood false twins are
the intended separating transformation.

Frozen bounds:

- dense cores through order eight;
- low-degree false-twin layers of size at most 24 and total order at most 48;
- every attachment orbit with one or two core neighbors;
- exact `alpha`, `alpha_2`, and induced terms, each solve capped at 60 seconds;
- a proof that the correction compensates the construction is a valid theorem
  signal and terminates that subfamily.

## Trial H: current upstream declarations

Re-rank the 79 open declarations / 57 modules locked in
`method_v01_upstream_manifest.md`, but only after computing an exact
arsenal/family residual table for concretely evaluable graph statements. Select
at most two clusters with equality on at least two nonisomorphic graphs or a
one-unit residual and a transformation-catalogue match.

The selection report must be committed before either selected construction is
evaluated. Dean's `k=5` cluster remains low priority because it has no numerical
wall and the existing arsenal readily supplies 5-cycles.

## Internal certificate queue (not an upstream queue or method trial)

The already-certified WoW I 191 and 889 disproofs, plus Graph Brain upper-081,
are internal `c5-k4` certificate work rather than Wave 2 discovery evidence.
They are outside the collections represented by `formal-conjectures` and must
not be submitted there. Audit source fidelity and logical completeness for the
local record only; if a certificate proves merely an arithmetic implication
from externally supplied invariant values, record that limitation instead of
overstating formal coverage.
