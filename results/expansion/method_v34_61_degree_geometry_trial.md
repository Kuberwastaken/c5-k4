# Method v0.34: WOWII 61 prospective degree-geometry trial

## Outcome

The frozen trial returns **`HOLD_BOUNDED`**.  It found neither:

- a graphical degree-sequence pair refuting the residual no-overshoot bridge;
  nor
- a connected graph violating current DeepMind WOWII 61.

The persistent signal is now sharper: prove no residual overshoot first for a
single graphical majorizing edge transfer, then compose such transfers.  The
trial deliberately stressed the Havel--Hakimi threshold through nonthreshold
defects, unequal blowups, joins, and realization switches, but the scalar gap
never crossed its initial ceiling.

The frozen protocol and append-only record are:

- `results/expansion/prospective_wowii61_degree_geometry_contract.md`;
- `results/expansion/prospective_wowii61_degree_geometry_ledger.jsonl`.

No public action or novelty claim was made.

## Source and novelty gate

The target was the exact theorem at upstream commit
`9a1636c4030039f70cf78b866c216d8b6c5f35b0`:

```text
largestInducedForestSize(G)
  >= residue(G) + ceil(diameter(G)/3).
```

The source file SHA-256 was
`54620e7b70a9a98eaaf7ce10154f533046b9f6d36fa276c8923c1a7301a7e091`.
It remained `research open`.  Target-specific GitHub searches before and after
the trial found no competing solution or counterexample claim.  This status
audit did not relax the rule that only an independently certified strict
crossing could become a candidate.

## Database sanity came first

Before any development-family graph was tested, an independent evaluator ran
on 1,069 controls: all connected nontrivial Graph Atlas graphs through order
seven plus the frozen named families.

There were no violations.  The exact WOWII 61 residual histogram was:

| residual | 0 | 1 | 2 | 3 | 4 | 5 |
|---:|---:|---:|---:|---:|---:|---:|
| graphs | 185 | 583 | 285 | 10 | 5 | 1 |

The evaluator independently constructed the full descending Havel--Hakimi
trajectory, computed the residue and diameter, and exhaustively found a
maximum induced forest.

## Degree-sequence experiment

The prospective construction lanes generated 8,748 structured connected
graphs and 2,064 distinct graphical degree sequences of orders three through
eighteen.  They included:

- split and bipartite chain graphs;
- one-edge nonthreshold/Ferrers defects;
- joins;
- independent and clique unequal blowups;
- alternating blowups; and
- graphical one-edge majorizing transfers.

The run checked 8,516 transformation-linked pairs first and then continued to
100,000 distinct prefix-comparable pairs.  For every pair it retained the
complete Havel--Hakimi states and tested

```text
gap(k) <= gap(0)
```

at every common admissible depth.  No residual overshoot occurred.

This result specifically survives the threshold-count geometry isolated in
v0.33.  The constructed defects move entries across the decrement boundary
and change the counts of `e+1` inside the laid-off prefix and `e` outside it;
nevertheless the combined trajectory never produced an unfunded head
reversal.

## Exact graph realizations

From the structured catalog, 660 representative graphs received exact
forest/residue/diameter evaluation.  The realization lane then checked 350
additional nonisomorphic connected graphs at switch depths one through three:

| switch depth | 1 | 2 | 3 |
|---:|---:|---:|---:|
| graphs | 150 | 182 | 18 |

There were no timeouts and no violations.  Across all 1,010 development
realizations:

| residual | 0 | 1 | 2 | 3 | 4 | 5 | 6 |
|---:|---:|---:|---:|---:|---:|---:|---:|
| graphs | 268 | 343 | 270 | 72 | 40 | 15 | 2 |

The largest diameter reached was five.  On the equality wall, the familiar
compensation remained exact: examples with degree sequence
`[3,2,2,2,2,1]`, residue three, and diameter four had induced-forest order
five, giving `5 - 3 - 2 = 0`.

## Independent recomputation

Every one of the 268 equality-wall realizations was recomputed by a second
implementation using:

- a separately written Havel--Hakimi state loop;
- explicit all-source BFS for diameter; and
- deletion-order subset enumeration with an independent forest predicate.

All 268 residues, diameters, and maximum induced-forest orders agreed.  There
were zero mismatches.

## Theorem signal

The most economical next theorem is no longer a broad successor-majorization
claim.  It is the local generator statement:

> A graphical edge transfer that moves one degree unit from a lower entry to
> a higher entry, and therefore increases weak prefix order, cannot make the
> signed Havel--Hakimi residual gap overshoot its initial value.

Such unit transfers are the natural generators of majorization.  A proof that
also keeps the intermediate sequences graphical would allow composition to
the full no-overshoot bridge.  The 8,516 direct transformation pairs are
prospective bounded evidence for exactly this formulation.

The graph-side experiment gives the complementary signal: degree-preserving
2-switches can move diameter, but every observed move toward the next
`ceil(diameter/3)` boundary supplied the needed induced-forest vertex.  Thus
the useful next step is theorem extraction around unit-transfer monotonicity
and diameter-path forest augmentation, not a wider unfocused search.

## Scope

This bounded hold is not a proof of WOWII 61.  Orders above eighteen,
unrepresented graphical-transfer chains, and realization classes outside the
frozen construction lanes remain open.  It does, however, eliminate the
predeclared structured attempts to break both the list bridge and the graph
inequality, with exact witnesses, independent equality-wall recomputation,
and no silent timeouts.

