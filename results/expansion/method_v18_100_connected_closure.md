# Method v18: WOWII #100 connected closure

## Consolidated result

The exact upstream Lean statement is now proved for every finite, nontrivial,
connected graph:

```text
theorem conjecture100_of_connected
    (G : SimpleGraph V) [DecidableRel G.Adj] [Nontrivial V]
    (hG : G.Connected) :
    let maxL := (Finset.univ.image (indepNeighborsCard G)).max' (by simp)
    (G.indepNum : ℝ) <=
      ceil (((maxL : ℝ) + (1/2) * degreeL2Norm Gᶜ) / 2)
```

No complement-connectedness hypothesis remains.

This is a closure of the formalized `degreeL2Norm Gᶜ` reading only.  The
historical prose describes a complement-diameter quantity instead.  Nothing
in this module claims that the two readings coincide or that this theorem
settles the prose statement.

## Precise audit of the former ranges

Before this consolidation, the modules established:

| independence number | earlier route |
|---|---|
| `alpha=1` | not isolated |
| `alpha=2` | connected `G` and connected `Gᶜ` |
| `alpha=3` | connected `G` and connected `Gᶜ` |
| `4<=alpha<=7` | connected `G`, v17 |
| `8<=alpha<=11` | connected `G`, v15 |
| `alpha>=12` | connected `G`, v12 |

The extra complement-connectedness assumptions at `alpha=2,3` came from the
earlier induced-path/energy route.  They are not intrinsic to the formalized
inequality.

## Removing the low-alpha hypotheses

### The range `2 <= alpha <= 11`

The v17 cross-witness classification works verbatim throughout this larger
range:

1. a unique cross witness has zero complement attachment;
2. two exhaustive witnesses have disjoint complement-attachment sets, hence
   `t+u<=alpha`;
3. three distinct witnesses supply the graph-level triple incidence energy.

This file reruns the exact coordinate optimizers over `2<=alpha<=11`:

- the two-witness package is strict under `t+u<=alpha`;
- the three-witness package is strict for all `t,u,v<=alpha-1`;
- the zero-attachment one-witness package is strict.

The three-coordinate proof reduces to `m=min(t,min(u,v))`, checks the bounded
`(alpha,m)` grid, and uses monotonicity for the remaining coordinates.  It
does not enumerate graphs.

Consequently `alpha=2` and `alpha=3` now follow from connectedness alone, and
the same theorem subsumes the v17 and v15 middle ranges.

### The row `alpha=1`

Every vertex in a nontrivial connected graph has a neighbor.  A singleton
neighbor is an independent subset of its open neighborhood, so

```text
maxL >= 1.
```

For `alpha=1`, the residual left side is zero, while the local contribution is
positive and `degreeL2Norm Gᶜ` is nonnegative.  This directly proves the row;
no structural description of independence-one graphs is required.

### The range `alpha>=12`

The final theorem invokes the existing v12 symbolic connected-graph theorem.

## Formal artifact

```text
lean/GraphConjecture100ConnectedClosure.lean
```

Principal declarations:

- `two_attachment_margin_two_to_three_of_sum_le` (now deliberately covering
  the expanded `2<=alpha<=11` box despite the legacy local name);
- `three_attachment_margin_two_to_three` (same expanded box);
- the one-, two-, and three-witness exact conclusion lemmas;
- `conjecture100_of_connected_of_indepNum_two_to_eleven`;
- `one_le_max_indepNeighborsCard_of_connected`;
- `conjecture100_of_connected_of_indepNum_one`;
- `conjecture100_of_connected`.

The legacy helper names reflect the original low-row target but their theorem
signatures explicitly state `2<=alpha<=11`; users should rely on the types.

## Verification

```bash
LEAN_PATH=/tmp/c5k4-proof100-three timeout 60s lake env lean \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture100ConnectedClosure.lean
```

Result: exit code 0, no diagnostics, within the 60-second process cap
(approximately 56 seconds on the working machine).  The file contains no
`sorry`, `admit`, `native_decide`, or custom axiom.

## Final scope

There is no remaining independence-number gap for the exact upstream Lean
formula under the finite, nontrivial, connected hypotheses.  The only caveat
is semantic and remains prominent: the verified square-degree-norm formula is
not the complement-diameter expression printed in the historical prose.
