# Reed v49 deletion closure: theorem-shadow closes all edge pruning

Date: **2026-08-13 UTC**

Status: **completed theorem-shadow; no graph menu, crossing, or public claim**

## Fresh declaration and database gate

The current DeepMind source blob for
`FormalConjectures/Paper/ReedOmegaDeltaChi.lean` remains
`526ca28f41ba9e18646d53ac8cf995cb771fa51a`.  Its finite declaration remains
tagged `research open` and states

`2 * chromaticNumber ≤ cliqueNum + maxDegree + 2`.

The fresh exact Atlas gate again found zero violations among all 995 connected
graphs of orders 2--7.

## Frozen-base replay

The v49 graph reconstructed with the required digest
`d662f7a28227f590393b86cda3834a51805ae6a55f93def531b23f6f00f5a7da`
and exact profile `(n,m,χ,ω,Δ,slack)=(18,89,9,7,10,1)`.  Its 89-edge menu
again had digest
`dfeeba767e53dc19e02bbfe77c77db367e47e3ad18866b73a4a4db75c17bd9e8`.

No transformed graph was evaluated in v51.  The input certificate is the
completed v50 table: every one of those 89 singleton deletions has exact
chromatic number eight.

## The stronger consequence

Let `S` be any deletion set containing a genuine base edge `e`.  Then

`G \ S ≤ G \ {e}`.

The right-hand graph is eight-colorable by its v50 certificate.  A coloring
of a graph is also a coloring of every spanning subgraph, so `G \ S` is
eight-colorable as well.  This holds regardless of how many additional edges
are deleted.

The general implication is formalized in
`lean/ReedEdgeDeletionClosure.lean`, including the chromatic-number corollary.
It elaborates with warnings treated as errors under the 60-second cap and
uses no `native_decide`, `sorry`, or custom axiom.

## Method verdict

The proposed next move is **not another bounded deletion trial**.  The v50
result already closes the entire nonempty edge-deletion closure of v49, not
just its singleton layer.  Every genuine pruning loses the ninth color, so no
such operation can preserve `χ=9` while reducing `ω` or `Δ`.

This is the method-valid stopping result for the v49/v50 neighborhood.  Any
future Reed experiment must leave this operation class and preregister a
genuinely different construction with a prospective coordinate law; adaptive
multi-edge deletion and enlargement of the same blocker CNF are excluded.

