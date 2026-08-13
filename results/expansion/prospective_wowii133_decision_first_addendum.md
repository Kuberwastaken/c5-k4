# Frozen addendum: WOWII #133 decision-first path-suppression trial

Frozen: 2026-08-13 UTC, before candidate evaluation

Parent trial: `prospective_wowii133_alt_geometry_contract.md`

## Target and decision rule

The reading is unchanged.  For a connected simple C4-free graph `G`, set

```text
T133(G) = radius(G) + floor(average_v alpha(G[N(v)])).
```

The statement holds on `G` as soon as an induced path on `T133(G)` vertices
is exhibited.  The primary oracle therefore performs endpoint-extension DFS
and stops on the first target-length witness.  It does **not** optimize the
path length on a hold candidate.

Only if exhaustive target search reports that no target-length path exists
may the evaluator compute the exact maximum induced-path order.  A crossing
requires that exact value, a second descending-subset verifier, and the source,
status, and novelty audit from the parent contract.  A timeout is unresolved.

## Frozen prediction

The alternate-geometry trial showed that sparse subdivisions and pendant
attachments create rather than suppress clean path extensions.  This trial
instead adds global C4-safe chords, deletes path-supporting vertices from
dense polarity graphs, and amalgamates dense C4-free blocks.  These operations
are intended to destroy long induced paths while keeping `radius + floor(l)`
as high as possible.

## Frozen construction families

No subdivision, pendant attachment, voltage cover, or degree switch is used.

1. **Orthogonal polarity graphs.**  For prime `q in {3,5,7}`, use the graph on
   normalized points of `PG(2,q)` in which distinct points are adjacent when
   their dot product is zero.  Remove loops.  Evaluate the base and every
   nonisomorphic deletion of one vertex or two vertices represented by the
   deterministic signatures `(degree, eccentricity, local alpha)` and pair
   distance/signatures.  Deletions are capped at 24 representatives per `q`.
2. **Witness-blocking chord closure.**  Start from `C_n` for
   `8 <= n <= 30`.  At each of at most 16 rounds, find the deterministic first
   target-length induced path.  Among nonconsecutive pairs on that witness,
   retain additions which preserve simplicity, connectedness, C4-freeness,
   and do not lower `T133`.  Add the edge maximizing the new `T133`, then
   radius, then `floor(l)`, with graph6 as final tie-break.  Evaluate the base
   and every accepted intermediate graph.  Stop when no admissible blocker
   exists.
3. **Dense block amalgams.**  Take two through four copies of either the
   Petersen graph or the `q=3` polarity graph and identify one deterministic
   minimum-label vertex from every copy.  Evaluate both the common-hub
   amalgam and a chain amalgam identifying consecutive copies at distinct
   minimum-label vertices.  Exact C4 filtering is mandatory.

Exact graph6 duplicates are removed globally.  Candidate order is capped at
80 and the trial at 600 distinct candidates.  No family may be added after
this addendum is frozen.

## Gate, resources, and logging

- Before discovery, run every connected Graph Atlas graph of orders 2--7 and
  the named controls from the parent contract through both the target oracle
  and the existing exact evaluator.  Their hold/crossing decisions must agree;
  every exact residual must be nonnegative.  Otherwise stop `GATE_FAIL`.
- Every operating-system process is capped at 60 seconds.
- Each target decision receives at most 5 seconds; exact fallback at most 20
  seconds; each batch at most 55 seconds.
- Exact C4, radius, local neighborhood independence, target, graph6, decision
  witness/states, and elapsed time are appended immediately to
  `results/expansion/prospective_wowii133_decision_first_ledger.jsonl`.
- Every crossing candidate is independently checked by descending vertex
  subsets before any claim.

Verdicts are `GATE_FAIL`, `CROSSING_VERIFIED`, `HOLD_BOUNDED`,
`HOLD_WITH_TIMEOUTS`, and `NO_APPLICABLE_CANDIDATES`.

## Public action

This lane may write only its local evaluator, append-only ledger, and result
report.  It may not commit, push, release, open an issue, open a PR, or take
any other public action.
