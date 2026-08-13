# Erdős 64 Petersen `Z3` lift: pre-freeze source/status audit

Audited: **2026-08-13 UTC**, before family freeze or evaluation

## Live source and status

The canonical current source is
`google-deepmind/formal-conjectures`,
`FormalConjectures/ErdosProblems/64.lean`, blob
`22b941b2c65cb361e185dc9a49eb4d5c340aa950`.  It is tagged
`@[category research open, AMS 5]` and asks whether every finite graph of
minimum degree at least three has a cycle of length `2^k`, `k >= 2`.
Repository searches found no open issue or PR mentioning Erdős 64 or that
source path.

The live Erdős Problems page also marks problem 64 `Open` and was last edited
10 April 2026.  It records the high-average-degree theorem of Liu--Montgomery
and restricted-family results, not a solution at minimum degree three.

## Prior art and stop decision

The pre-freeze literature search included the original computational line,
recent structural work, Petersen-cover literature, and explicit searches for
Petersen `Z3` lifts without 4-, 8-, or 16-cycles.

- Markström's 2004 exhaustive computation generated cubic graphs on fewer
  than 29 vertices and found no counterexample.  Later sources summarize the
  boundary as at least 30 vertices.  A three-sheet Petersen lift has exactly
  30 vertices, so this does **not** subsume the frozen domain.
- Carr (arXiv:2605.22844) states that the conjecture remains open, gives
  structural restrictions on minimal counterexamples, and does not exclude
  arbitrary cubic order-30 covers.
- Restricted positive results found cover planar, cubic claw-free,
  3-connected cubic planar, `P8`-free, `P10`-free, diameter-two, and
  sufficiently high average-degree graphs.  None covers every cyclic
  three-sheet lift of Petersen.
- A current 60-vertex lower bound concerns **cubic bipartite**
  counterexamples.  Petersen is nonbipartite and no claim that all its
  three-covers are bipartite is available, so this is not a domain stop.
- Existing literature classifies some elementary abelian covers of Petersen
  that lift automorphism groups, but the search found no result asserting a
  power-of-two cycle in every cyclic three-cover and no matching
  counterexample claim.

Verdict: **LIVE_OPEN_AND_DOMAIN_NOT_COVERED**.  The family may be frozen and
evaluated.  This is only authorization under the prospective protocol; it is
not evidence that a crossing exists.

## Prediction correction before freeze

The mechanism must be phrased conditionally.  A base cycle with nonzero total
`Z3` voltage lifts to a cycle three times as long, but a globally nonzero
assignment need not give nonzero voltage to every base 8-cycle.  The exact
family is therefore retained as a legitimate test, while the stronger phrase
“nonzero voltage sends base 8-cycles to length 24” is not used as a universal
claim.

No public action was taken.

