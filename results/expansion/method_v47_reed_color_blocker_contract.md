# Frozen prospective trial: one-vertex color blocker on C5[K3]

Frozen: **2026-08-13 UTC, before transformed chromatic evaluation**

## Target and conservatism

The target is the current finite declaration in
`FormalConjectures/Paper/ReedOmegaDeltaChi.lean`:

`2 * chromaticNumber(G) <= cliqueNum(G) + maxDegree(G) + 2`.

This is Reed's major human open conjecture. A numerical crossing is only an
audit trigger, never a public disproof claim. There is no authorization for a
commit, push, release, issue, PR, or other public action.

The starting carrier is the exact odd equality case `C5[K3]`, with
`(chi, omega, Delta) = (8, 6, 8)` and doubled slack zero.

## Frozen operation

Let the five three-vertex clique bags be

`Bi = {(i,0), (i,1), (i,2)}`, for `i in Z/5Z`,

with complete joins between consecutive bags. Add one new vertex `x`, and no
other vertex or edge. Its neighborhood is frozen as

`S = B0 union {(1,0),(1,1),(4,0),(4,1),(2,0),(3,0)}`.

Thus `x` has exactly nine neighbors. No alternative deletion, replacement,
rotation, second gadget, or adaptive neighborhood is permitted.

## Pre-evaluation coordinate prediction

This neighborhood is the minimal symmetric perturbation considered here of
the closed-neighborhood color blocker `N[(0,0)]`. One vertex is omitted from
each adjacent bag and replaced by one vertex from each distance-two bag. The
purpose is to destroy the new seven-clique and the claw-free true-twin
structure while retaining a plausible eight-color blocker.

The frozen structural predictions are:

- `Delta = 9`: `x` has degree 9; selected carrier vertices rise from 8 to 9;
- `omega = 6`: carrier six-cliques remain, while `G[S]` has clique number 5,
  so a clique containing `x` has size at most 6;
- `8 <= chi <= 9`: the graph contains `C5[K3]`, and giving `x` a fresh color
  gives a nine-coloring;
- an induced claw is predicted with center `(0,0)` and leaves
  `x`, `(1,2)`, `(4,2)`.

Consequently the only unknown coordinate is `chi`. If `chi=9`, the frozen
graph has slack `6+9+2-18 = -1`; if `chi=8`, it has slack `1`.

## Mandatory sequence

1. Re-run the 995-graph connected Atlas sanity gate with exact witnesses and
   require zero violations.
2. Audit the current source/status and known theorem domains. In particular,
   verify that the explicit claw takes the graph outside the King--Reed
   claw-free theorem. Stop on any known proof class or status ambiguity.
3. Construct only the frozen graph and verify its adjacency digest.
4. Compute exact `chi` by deterministic DSATUR/fixed-`k` search, exact `omega`
   by clique branch-and-bound, `Delta` directly, and the explicit claw.
5. Independently recompute any crossing with a separately implemented
   fixed-`k` search and exhaustive clique-subset enumeration, then stop for a
   fresh bibliographic and theorem-class audit.

Every subprocess has a hard 60-second cap. Results are appended incrementally
to the JSONL ledger.
