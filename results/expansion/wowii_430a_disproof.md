# WOWII 430a: a second invariant-separation counterexample family

Date: **2026-08-12**. Verdict: **DISPROVED**, source-faithful and apparently
unrecorded after source recovery, the database gate, two independent exact
verifiers, and targeted novelty searches.

WOWII 430a, still marked open on the live page, states that for a connected
graph on more than three vertices with center `C`,

```text
i(G) <= alpha(G[N(C)]) + 2 floor(CW(G)-1),
```

where `i` is independent domination and
`CW(G)=sum_v 1/(deg(v)+1)`. Both the open-neighborhood and closed-neighborhood
readings were audited.

## Construction and exact failure

Replace the seven vertices of `P7` by cliques of orders

```text
(1,4,12,19,12,4,1)
```

and completely join consecutive cliques. The resulting graph has 53 vertices
and 875 edges. Exact values are

```text
center = the middle K19,
alpha(G[N(C)]) = 2                 (open or closed reading),
i(G) = 3,
CW(G) = 51123/25585 = 2 - 47/25585 < 2.
```

Therefore `floor(CW-1)=0` and the conjecture claims `3<=2`.

Uniformly scaling every clique order by an integer `t>=1` preserves the
quotient graph and therefore `i=3` and `alpha(G[N(C)])=2`. For a vertex in
blob `j`, `deg+1=s_{j-1}+s_j+s_{j+1}`; scaling all blob sizes multiplies both
the number of vertices and this denominator by `t`, so every blob's total
Caro--Wei contribution is unchanged. It therefore gives an infinite
counterexample family.

The mechanism is the requested second structural transfer. Dense regular
carriers make `C=V`, causing the center-neighborhood term to absorb `i`. The
nonuniform path blow-up introduces controlled eccentricity asymmetry: it pins
the center to one middle clique and keeps its neighborhood independence at 2,
while the seven-clique quotient forces every independent dominating set to use
three separated blobs. Large adjacent cliques keep `CW` just below the integer
cliff at 2, deleting the correction term entirely.

## Verification and novelty

[`scripts/verify_wowii_430a.py`](../../scripts/verify_wowii_430a.py) uses
exact `Fraction` arithmetic and enumerates all maximal independent sets through
maximal cliques of the complement. It checks both neighborhood readings on all
992 applicable connected atlas graphs of orders 4--7 plus the campaign's named
controls. An independent verifier enumerated all 724 maximal independent sets
of the 53-vertex graph and separately recomputed the neighborhood independence
number. A 154,143,080-vector exact search found no positive-integer `P7`
clique-blowup witness below order 53; this proves minimality only within that
construction class.

The live source (updated 2026-08-06) still marks 430a open. Exact-formula,
concept, GitHub, and bibliographic searches found no resolution. The 2011
DeLaViña--Pepper--Waller paper on Graffiti.pc independent domination was also
read in full and does not cover 430a. The novelty claim is therefore
**apparently unrecorded**, not proof of absolute priority.
