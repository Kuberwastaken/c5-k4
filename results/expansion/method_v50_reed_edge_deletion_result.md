# Reed v49 edge-deletion trial: uniformly edge-critical, no crossing

Date: **2026-08-13 UTC**

Status: **completed; 89 exact evaluations, no crossing, no public claim**

## Frozen menu

The starting graph was the v49 first-feasible hard-claw graph, with

`(chi, omega, Delta) = (9,7,10)` and doubled Reed slack 1.

Before computing any deletion outcome, the trial froze every one of its 89
edges as the complete eligible menu. Each row deletes exactly one edge, in
lexicographic endpoint order. No edge ranking, two-edge deletion, or adaptive
choice was allowed.

The reconstructed base matched the recorded graph digest and coordinates.
The canonical menu digest is

`dfeeba767e53dc19e02bbfe77c77db367e47e3ad18866b73a4a4db75c17bd9e8`.

The fresh Atlas gate again found zero Reed violations among all 995 connected
graphs of orders 2--7.

## Exact result

All **89/89** deletion graphs have exactly the same coordinate profile:

`(chi, omega, Delta) = (8,7,10)`.

Therefore every row has doubled Reed slack

`7+10+2-16 = 3`.

There are no crossings and no equality rows. Rather than preserving the ninth
color while reducing the right-hand side, every possible single-edge deletion
immediately makes the graph eight-colorable while leaving both `omega` and
`Delta` unchanged.

The v49 graph is consequently edge-critical for its ninth color: deletion of
any edge lowers its chromatic number.

## Independent verification

There is only one distinct closest coordinate profile. For its canonical
representative, deletion of edge `(0,1)`, a separately implemented
static-order search:

- rejected seven colors in 2,117 states;
- found an eight-coloring in 19 states;
- supplied coloring
  `[5,5,0,1,2,6,0,3,4,1,2,5,3,4,6,6,7,7]`.

Exhaustive enumeration of all `2^18` vertex subsets independently found the
seven-clique `[6,7,8,9,10,11,17]`; direct recomputation gave maximum degree
ten.

## Interpretation

The v49 slack-one graph is not amenable to local edge pruning. Its ninth color
is supported globally enough that every edge is essential, while its large
clique and maximum-degree coordinates have enough redundancy to survive every
single deletion. The attempted coordinate move therefore goes in precisely
the wrong direction: the doubled left side falls by two and the right side
does not move.

Any further deletion experiment would require a new preregistered multi-edge
menu and should account for this observed edge-criticality. It is not an
adaptive continuation of the completed one-edge trial.
