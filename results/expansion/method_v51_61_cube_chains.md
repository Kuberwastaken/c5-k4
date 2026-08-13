# Method v0.51: WOWII 61 serial cube chains

## Outcome and strict protocol classification

The strict trial verdict is **`INCONCLUSIVE_PROTOCOL_DEVIATION`**. The initial
summary's `HOLD_BOUNDED` label is superseded.

An independent final audit found that the cube-gate graph6 string `Gl_XIS`
decodes to a labelling with `distance(0,7)=2`, while the gate simultaneously
claimed labelled root zero and port seven were distance three. Every actual
development cube block instead has labelled edge-set graph6 `Gl_YPK` and does
have `distance(0,7)=3`. Graph6 serialization changed vertex labels, but the
gate omitted a labelled edge list that would distinguish the abstract graph
certificate from its labelled root/port coordinates.

The contract's strict gate rule therefore makes the run inconclusive. No
correction or rerun is presented as part of this frozen trial.

Conditionally on the actual labelled `Gl_YPK` construction in the development
records, all 832 graphs satisfy WOWII 61 with residual at least seven. Repeated
cubes grow residue from nine to thirty-six, but maximum induced-forest order
grows too quickly for the diameter ceiling to compensate.

The family is closed. No length range, attachment rule, or coordinate was
changed after evaluation, and no release or other public action was taken.

Artifacts:

- `results/expansion/prospective_wowii61_cube_chain_contract.md`;
- `results/expansion/prospective_wowii61_cube_chain_ledger.jsonl`;
- `results/expansion/prospective_wowii61_cube_chain_records.jsonl`;
- `scripts/prospective_wowii61_cube_chain.py`;
- `scripts/verify_wowii61_cube_chain.py`.

## Frozen construction

The trial carried forward—but did not alter—the independently certified cube
coordinate from v0.50:

```text
Q3 order                  8
root-to-antipode distance 3
maximum induced forest    5
feedback loss              3
```

For every diametral pair of each of the three order-twelve neutral bases, the
trial attached a serial cube chain of length `a` to one end and length `b` to
the other, for every ordered `(a,b)` in `[1,8]^2`. Cube antipodes were joined
to the next cube roots through bridges. The bases have 3, 4, and 6 diametral
pairs, so the frozen universe contains

```text
(3 + 4 + 6) * 8^2 = 832
```

labelled graphs.

## Gates and graph6-label discrepancy

The database gate replayed 1,030 controls with no violation or timeout:

| residual | 0 | 1 | 2 | 3 | 4 | 5 |
|---:|---:|---:|---:|---:|---:|---:|
| graphs | 159 | 574 | 281 | 10 | 5 | 1 |

The cube evaluator internally checked the intended fixed labelling:

- order 8 and size 12;
- root-to-port distance and root eccentricity 3;
- the stored five-vertex induced-forest witness; and
- all 28 six-vertex subsets, none of which induces a forest.

Thus the exact maximum induced-forest order is five. However, the gate wrote
the isomorphic string `Gl_XIS`, whose decoded labels place vertex seven at
distance two from vertex zero. The actual intended labelled cube is `Gl_YPK`.
Because the gate did not store its labelled edge list, those gate fields are
literally inconsistent. Every base otherwise recomputed to residue eight,
diameter four, maximum induced forest ten, and residual zero.

## Frozen coordinate proof

Every inter-block edge is a bridge. A chain with `t` cubes contributes exactly
`5t` vertices to a maximum induced forest. The far port is four distance units
per block from the attachment: three through the cube and one joining bridge.
For chain lengths `(a,b)`, therefore,

```text
forest(T)   = 10 + 5(a+b),
diameter(T) = 4(a+b+1).
```

Every record contains the ten-vertex base witness plus the translated
five-vertex witness in every cube. The matching upper certificate sums the
exact base bound ten and the exact cube bound five across bridge-separated
blocks.

## Conditional downstream results

All 832 constructions completed without a timeout or certificate mismatch.
Their outcome depends only on the total cube count `s=a+b`, not on the base,
diametral pair, or split between the two sides:

| `s` | graphs | residue | diameter | forest | residual |
|---:|---:|---:|---:|---:|---:|
| 2 | 13 | 9 | 12 | 20 | 7 |
| 3 | 26 | 11 | 16 | 25 | 8 |
| 4 | 39 | 13 | 20 | 30 | 10 |
| 5 | 52 | 15 | 24 | 35 | 12 |
| 6 | 65 | 17 | 28 | 40 | 13 |
| 7 | 78 | 18 | 32 | 45 | 16 |
| 8 | 91 | 20 | 36 | 50 | 18 |
| 9 | 104 | 22 | 40 | 55 | 19 |
| 10 | 91 | 24 | 44 | 60 | 21 |
| 11 | 78 | 26 | 48 | 65 | 23 |
| 12 | 65 | 28 | 52 | 70 | 24 |
| 13 | 52 | 30 | 56 | 75 | 26 |
| 14 | 39 | 32 | 60 | 80 | 28 |
| 15 | 26 | 34 | 64 | 85 | 29 |
| 16 | 13 | 36 | 68 | 90 | 31 |

There are no negative, tight, or residual-one graphs. The closest case is the
shortest chain pair `(1,1)`, already seven units safe. Slack then generally
increases with chain length.

## Independent replay

A separately written verifier reconstructed all 832 labelled graphs and
independently checked:

- graph6 isomorphism against each edge list;
- every canonical cube block and joining bridge;
- full Havel--Hakimi trajectories and residues;
- all-source BFS diameters and the coordinate formula;
- explicit induced-forest witnesses and blockwise exact upper bounds; and
- thresholds and final residuals.

It returned 832 agreements, minimum residual seven, zero candidates, and zero
downstream mismatches for the actual labelled blocks. A separate final auditor
reconstructed every family key and repeated the full calculation without
importing either trial script. It confirmed all 832 stored graph6 values are
abstractly isomorphic to their edge lists, although none preserves those
labels exactly.

This validates the conditional mathematics but does not repair the frozen
gate or restore a protocol-exact `HOLD_BOUNDED` verdict.

## Interpretation

The corrected cube coordinate is real and useful: each sparse cubic block
forces three feedback deletions, and serial repetition raises residue steadily.
But per added cube the dominant asymptotics are approximately

```text
forest:          +5
residue:         about +2
diameter ceiling about +4/3.
```

The right side therefore gains only about `10/3` against five new forest
vertices, so the gap widens rather than closes. Conditionally, the cube's
one-extra feedback loss does not cross the residue wall under the actual
serial root-to-antipode construction. Strictly, the prospective trial remains
inconclusive because its cube gate did not preserve the labelled coordinate it
claimed to certify.
