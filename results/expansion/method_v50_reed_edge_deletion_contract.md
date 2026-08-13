# Frozen prospective trial: all one-edge deletions from the v49 Reed graph

Frozen: **2026-08-13 UTC, before any deletion-graph computation**

## Recorded starting point

The v49 first-feasible hard-claw blocker graph has 18 vertices, 89 edges, and
exact coordinates

`(chi, omega, Delta) = (9, 7, 10)`,

so its doubled Reed slack is `7+10+2-18 = 1`. It contains the explicit induced
claw `[0,15,5,14]` and passed the recorded static theorem-domain audit.

## Frozen deletion menu

The eligible menu is **every edge of the recorded v49 graph**, sorted as
canonical integer pairs `(min(u,v),max(u,v))` in lexicographic order. For each
of the 89 menu entries, delete exactly that one edge and make no other change.

There is deliberately no ranking by newly computed maximum cliques, degree
ties, coloring witnesses, or deletion outcomes. No two-edge deletion,
replacement edge, reordered retry, or adaptive extension is permitted.

## Predicted coordinate movement

Deleting one edge gives the unconditional ranges

- `chi in {8,9}`;
- `omega in {6,7}`;
- `Delta in {9,10}`.

The starting value is `omega+Delta=17`. A strict Reed crossing requires

`2*chi > omega+Delta+2`.

Thus a menu row can cross only if it preserves `chi=9` and simultaneously
reaches `omega+Delta<=15`; equivalently, the single deletion must lower the
sum of the clique number and maximum degree by at least two. A one-unit drop
only reaches equality slack zero.

## Mandatory protocol

1. Re-run the exact 995-graph connected Atlas sanity gate before evaluating
   any deletion graph; require zero violations.
2. Reconstruct the v49 graph from its frozen neighborhoods and require its
   graph6 digest and exact coordinates to match the recorded values.
3. Enumerate the full 89-edge menu before evaluating its first row and record
   a canonical menu digest.
4. Evaluate rows in lexicographic order with exact DSATUR `chi`, exact clique
   branch-and-bound `omega`, direct `Delta`, and retained witnesses.
5. On the first numerical crossing, stop immediately for adversarial theorem
   and bibliographic escalation. It is not a disproof claim.
6. If no crossing occurs, independently recompute every distinct closest
   coordinate profile represented in the menu using separate fixed-order
   coloring and exhaustive clique-subset routines.

Every subprocess has a hard 60-second cap. Results are appended incrementally
to the JSONL ledger. Reed's conjecture is a major human open problem. No
commit, push, release, issue, PR, or other public action is authorized.
