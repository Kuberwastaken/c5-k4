# Frozen prospective trial: Dean `k = 5` two-switch cycle-spectrum surgery

Frozen: **2026-08-13 UTC**, before the database gate and before any
transformed graph was generated.

## Target and source lock

- Upstream: `google-deepmind/formal-conjectures` at
  `d16e05aded22b8c467a0a27c14b2311f53185006`.
- Source: `FormalConjectures/Arxiv/2605.02731/DeanCycles.lean`, blob
  `4a65620a7ff37a6d3f005f6db3705e26d793b3cf`.
- Live declaration: `dean_conjecture.variants.five`, tagged
  `@[category research open]`.
- Exact finite statement: if `5 <= G.minDegree`, then `G.cycleLengths`
  contains some `m` divisible by five.

This is one mathematical target, not two trials: the general `dean_conjecture`
and its `variants.five` declaration share the only open case.

## Prior-evidence and novelty lock

The repository's earlier fixed-arsenal pass is only `HOLD_BOUNDED`: every
eligible named graph had a 5-cycle. There is no prior prospective Dean
transformation lane in the repository. This trial is development evidence and
authorizes no issue, pull request, release, commit, or novelty claim.

## Equality control and frozen coordinate move

The base is `C5[K2]`, labelled `(i,a)` as integer `2*i+a`. Vertices in one
two-vertex blob are adjacent, and consecutive blobs of the five-cycle are
completely joined. It is 5-regular, so it meets the hypothesis at equality,
and it has a cycle of the least possible positive length divisible by five.

A simple-graph 2-switch replaces disjoint edges `{a,b},{c,d}` by one of the
other perfect matchings on the same four vertices when both replacement pairs
are nonedges. It preserves every vertex degree, hence preserves
`minDegree = 5`, while directly changing the cycle spectrum. This is the one
frozen transformation; no vertex additions, edge additions/deletions outside
the switch, adaptive gadgets, or random families are allowed.

## Frozen prediction

One or two 2-switches may remove all cycles whose length is divisible by five
while retaining the hypothesis exactly. Since every development graph has
order ten, the only forbidden lengths are 5 and 10. A graph with neither is a
candidate counterexample. Persistent survival of a 5- or 10-cycle throughout
the complete frozen neighborhood is `HOLD_BOUNDED`, not a theorem claim.

## Mandatory database gate

Before generating any switched graph:

1. parse and record the exact current source/status above;
2. evaluate every connected Graph Atlas graph through order seven;
3. for every graph satisfying `minDegree >= 5`, find and replay a simple cycle
   whose length is divisible by five;
4. reproduce `minDegree = 5` and explicit 5- and 10-cycle witnesses on the
   base `C5[K2]`;
5. independently replay each gate witness by checking vertex distinctness,
   closure, edge incidence, and length divisibility.

Any unexplained eligible gate failure stops the trial as `DB_SANITY_REJECT`.

## Frozen development budget and enumeration

- Enumerate every valid labelled 2-switch from `C5[K2]`, in lexicographic
  edge/replacement order.
- From every unique labelled depth-one graph, enumerate every valid second
  switch in the same order.
- Remove identical labelled edge sets at each depth. Report exact isomorphism
  class counts separately; isomorphism quotienting must not determine which
  graphs are evaluated.
- For every unique labelled graph, compute minimum degree and exhaustively
  search simple cycles of lengths 5 and 10. Append and flush a JSONL record at
  least every 100 graphs and on every new best cycle profile.
- Every operating-system process is capped at 60 seconds. No ILP is required.

## Verdict taxonomy

- `DB_SANITY_REJECT`: the source/reading/control gate fails.
- `CANDIDATE`: an eligible development graph has neither a 5-cycle nor a
  10-cycle; it still requires a fresh independent implementation and a current
  literature/status audit.
- `CROSSING_VERIFIED`: a candidate survives both checks. This remains an
  internal result and triggers no public action here.
- `HOLD_BOUNDED`: the gate passes and every graph in the frozen neighborhood
  has a 5- or 10-cycle.
- `INCONCLUSIVE`: a cap, count mismatch, witness replay, exactness, or audit
  failure prevents a complete classification.

