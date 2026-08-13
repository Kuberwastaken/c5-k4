# WOWII 40 prospective rooted-biclique bouquet trial

## Outcome

`HOLD_BOUNDED`.

This trial prospectively inverted the obstruction learned from the line-graph
experiment. Before constructing any development graph, it froze a rooted
balanced-biclique bouquet operation intended to preserve cycle burden while
destroying Hamiltonicity and increasing minimum path-cover number.

The exact database gate passed. Eighteen admissible transformed equality seeds
were then evaluated exactly, with zero crossings and zero timeouts.

## Frozen mechanism

Each equality seed received several copies of `K_(r,r)` sharing a single
deterministically selected maximum-degree root. The petal configurations were
frozen as `(q,r)=(3,2),(4,2),(2,3)`. A simple path can use the shared cut vertex
to connect at most two petals, so increasing `q` creates unavoidable path-cover
fragmentation. Every petal is cyclic and bipartite, simultaneously maintaining
feedback burden and a large induced-bipartite coordinate.

This is a rooted star bouquet, not the prior path-shaped biclique block tree,
block substitution, ear surgery, bounded mutation, or line graph.

## Exact results

- sanity controls: 1,031, with zero crossings;
- distinct admissible bouquets: 18, orders 13 through 18;
- predeclared order-cap exclusions: 12;
- exact path-cover range: 2 through 6;
- slack distribution: `{2: 5, 3: 7, 4: 4, 5: 2}`;
- residual range: `R=6` through `R=11`;
- timeouts: zero.

The path-cover computation maximized the number of edges in a spanning linear
forest using binary edge variables, degree-at-most-two constraints, and exact
iterative cycle cuts. Since `p=n-|E(F)|` for a maximum spanning linear forest,
the optimum gives the exact minimum path-cover number. Each emitted path
partition was checked directly. Induced-forest and induced-bipartite maxima
were computed by exhaustive descending subset search, with returned witnesses
also checked directly.

The deterministic output fingerprint is
`84cc6df3ce07c815d55db53c3336fdba474570e660d61633b5e19b2bd334f3e3`.

## What the negative result teaches

The transformation succeeded at its immediate goal: unlike the line graphs,
the bouquets were not Hamiltonian and had path-cover numbers as high as six.
But each bipartite petal supplied too many vertices that could coexist in an
induced forest. Maximum induced-forest order consequently grew faster than the
right side, and every output moved well away from equality.

The obstruction is now sharper than “avoid Hamiltonicity.” A future gadget
must combine path-cover fragmentation with cross-petal edges or another global
compatibility constraint that prevents most new vertices from appearing
together in an induced forest. That would be a new trial and must be frozen
separately rather than added to this result.

No crossing occurred, so no source/novelty audit was triggered. No commit,
push, release, issue, PR, or other public action was taken.
