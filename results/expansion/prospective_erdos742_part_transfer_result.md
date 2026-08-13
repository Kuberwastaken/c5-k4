# Erdős 742 part transfer: premise preserved, equality breaks safely

Date: **2026-08-13 UTC**

Status: **`KNOWN_PROOF_DOMAIN`; zero prospective candidate evaluations**

## Methodology correction

METHOD v0.8 requires a known-proof-domain stop before development profiling.
The frozen contract itself recorded Fan's theorem for every order at most 24,
and the proposed graph has order 10. The primary trial outcome is therefore

`KNOWN_PROOF_DOMAIN`, with `candidate_evaluations=0`.

The `K4,6` computation described below occurred after the point where the lane
should have stopped. It is retained transparently as reproducible
**post-stop calibration**, but is excluded from prospective evidence and from
hold/crossing scorekeeping. The append-only ledger preserves the earlier rows
and adds an explicit taxonomy override rather than silently rewriting history.

## Frozen transformation

The current DeepMind target is the Murty--Simon diameter-2-critical edge
bound. The exact carrier `K5,5` has 25 edges and attains
`floor(10^2/4)=25`.

Before evaluation, the trial froze one canonical transfer of a vertex between
the bipartition classes, rebuilding the complete cross edges. This produces
exactly `K4,6`. No other imbalance or edge surgery was tested.

This order lies within Fan's proved `n<=24` range. Under METHOD v0.8 that fact
terminates the prospective lane before the transformation is profiled.

## Database sanity gate

The exact gate identified 21 connected diameter-2-critical Atlas graphs of
orders 3--7. It replayed 156 singleton-edge deletion diameters and found zero
Murty--Simon violations.

Named controls reproduced:

| graph | edges | bound | slack |
|---|---:|---:|---:|
| `K2,2` | 4 | 4 | 0 |
| `K2,3` | 6 | 6 | 0 |
| `K3,3` | 9 | 9 | 0 |
| `K5,5` | 25 | 25 | 0 |
| Petersen | 15 | 25 | 10 |

## Excluded post-stop calibration

The preserved computation for `K4,6` has:

- order 10;
- 24 edges;
- diameter exactly 2;
- diameter-2-criticality verified on all 24 edges;
- bound 25;
- safe-side slack 1.

For every edge deletion, the full graph diameter becomes 3 and the deleted
endpoints have distance exactly 3.

The canonical graph digest is
`d9599a3adeed2c4b2f046fd31765cd6cb2c47fc2a956e417a11802b6a9e6e6a6`.

## Independent calibration audit and interpretation

The independent verifier reconstructed the two stable parts of sizes four and
six, checked every one of the 24 cross edges and the absence of internal
edges, recomputed the edge count as `4*6=24`, and replayed endpoint distance
three after deleting each cross edge.

As a mathematical calibration, this is a clean premise-preserving wall move.
Transferring one vertex keeps
diameter-2-criticality intact but replaces the balanced product `5*5` by
`4*6`, decreasing the edge coordinate by exactly one while leaving the
order-based bound fixed. The equality manifold is therefore precisely the
balanced bipartition; the first imbalance moves to slack one.

It is not a prospective trial result because the graph is inside a known proof
domain. For scorekeeping the lane contributes one `KNOWN_PROOF_DOMAIN` stop,
zero candidate evaluations, zero holds, and zero crossings.

No WoW I source, random search, ambiguity, timeout, commit, release, or public
action occurred.
