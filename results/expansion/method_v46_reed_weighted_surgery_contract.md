# Frozen prospective trial: finite Reed bound from weighted C5 clique blow-ups

Frozen: **2026-08-13 UTC, before database or transformed-graph evaluation**

## Exact current statement and status

The current finite declaration in
`FormalConjectures/Paper/ReedOmegaDeltaChi.lean` is

`2 * chromaticNumber(G) <= cliqueNum(G) + maxDegree(G) + 2`

for every finite simple graph with decidable adjacency. The same module also
contains an unrestricted extended-natural formulation and the open special
case `Delta=6`, `omega=2`. All three remain tagged `research open` on upstream
`main`. GitHub issue #159 remains open; the only matching PR, #1264, is the
closed/merged import of the statements, not a proof.

This is Reed's longstanding human conjecture. The novelty gate is deliberately
stronger than for machine-generated corpora.

## Known-domain stop

King and Reed, *Claw-Free Graphs, Skeletal Graphs, and a Stronger Conjecture on
omega, Delta, and chi*, Journal of Graph Theory (2014), DOI
`10.1002/jgt.21797`, proves Reed's conjecture for all claw-free graphs.

Every nonuniform clique blow-up `C5[K_(w0,...,w4)]` is claw-free: a neighborhood
has at most two mutually nonadjacent side-blob directions, while vertices in
the center blob are adjacent to the whole neighborhood. Therefore unmodified
weighted blow-ups are calibration/equality walls only and are not development
candidates.

After surgery, claw-freeness is checked before chi/omega optimization. Any
claw-free output is stopped as `KNOWN_PROOF_DOMAIN`. Any numerical crossing is
only a gated candidate and triggers a fresh theorem-class/bibliographic audit;
it is not a disproof claim.

## Mandatory database sanity gate

Before any transformed-family row:

1. exhaust all 995 connected unlabeled Atlas graphs of orders 2--7;
2. compute exact `chi`, `omega`, and `Delta`, retaining coloring, clique, and
   maximum-degree witnesses;
3. require zero violations and reproduce named controls `K_n`, odd cycles,
   Petersen, and uniform `C5[K_m]` equality/slack formulas.

Any gate violation or invariant mismatch stops the trial as `AMBIGUOUS`.

## Frozen weighted equality bases

- weights `(w0,...,w4)` with each `wi in {1,...,6}` and total order at most 24;
- quotient by the dihedral action on the five positions using the
  lexicographically minimum rotation/reflection;
- construct cliques inside bags and complete joins only between consecutive
  cycle bags;
- retain only bases with exact slack
  `omega + Delta + 2 - 2*chi = 0`;
- cap at 2,000 equality bases in lexicographic canonical order.

## Frozen one-edge surgery

For each retained base and each of the five unordered distance-two blob pairs,
add exactly one edge between the canonical first vertex of each blob. Vertices
inside a blob are symmetric before surgery, so this represents the full
one-edge interblob-addition orbit for that blob pair.

This move directly tests the desired coordinate separation: it can forbid one
color reuse across nonadjacent blobs, potentially raising `chi` by one, while
raising `Delta` by only one and ideally leaving `omega` unchanged.

Caps: 10,000 generated surgeries and 4,000 claw-containing exact profiles.
No edge deletion, second edge, adaptive weight extension, or alternative
quotient is allowed.

## Exact invariants and certificates

- `chi`: exact DSATUR/backtracking optimization; retain a proper coloring and
  certify infeasibility for every smaller color count searched;
- `omega`: exact Bron--Kerbosch maximum clique with a clique witness and
  exhaustive bound;
- `Delta`: direct degrees with a maximizing vertex;
- claw gate: explicit induced `K1,3` witness for every evaluated surgery;
- crossing rule: `omega + Delta + 2 - 2*chi < 0`.

Any crossing is independently recomputed by a separately implemented
fixed-`k` coloring search and exhaustive clique-subset enumeration, then halted
for proof-domain review. Every subprocess has a hard 60-second cap.

No commit, push, release, issue, PR, or other public action is authorized.

