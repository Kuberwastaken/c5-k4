# Method v0.11 — WOWII 100 at independence thirteen

Date: 2026-08-13  
Outcome: `PARTIAL_THEOREM`  
Formal artifact: `lean/GraphConjecture100AlphaThirteen.lean`

## Scope and exact reading

This is proof extraction from the existing WOWII 100 development lane, not a
held-out trial and not a counterexample or release candidate.

The upstream module's prose discusses the diameter of the complement, but the
Lean theorem expression uses `degreeL2Norm Gᶜ`. This file follows the Lean
expression exactly. Its result must not be presented as a theorem about the
different prose reading.

Earlier stages reduced the formalized inequality to

```text
4(alpha(G)-1) < 2L + q,
```

where

```text
L = max_v indepNeighborsCard(G,v),
q = degreeL2Norm(Gᶜ).
```

At `alpha(G)=13`, the target is `48 < 2L+q`. The separate universal bounds
`L>=2` and `q>=sqrt(1872)` miss this target. The correct move is to preserve
their dependence on the same outside vertex.

## Attachment parameter

Let `S` be a maximum independent set of size 13 and let `y` be outside `S`.
Define

```text
T = {s in S | y is adjacent to s in Gᶜ},
t = |T|.
```

Because `y` is outside `S`, every nonattachment in `S \ T` is adjacent to `y`
in `G`. Those `13-t` vertices remain independent, so they occur as an
independent subset of the open neighborhood of `y`:

```text
L >= indepNeighborsCard(G,y) >= 13-t.
```

On the complement-energy side, every vertex of `S` has the other twelve
vertices of `S` as complement neighbors. Each of the `t` attached vertices has
the additional neighbor `y`, and `degree_Gᶜ(y)>=t`. Hence

```text
q^2 >= 144(13-t) + 169t + t^2
     = 1872 + 25t + t^2.
```

Both inequalities are formalized for an arbitrary independent 13-set and an
arbitrary outside vertex; maximality is needed only to instantiate a set of
the desired size.

## Exact optimization

It remains to prove, for `0<=t<=13`,

```text
48 < 2(13-t) + sqrt(1872+25t+t^2),
```

or equivalently

```text
22+2t < sqrt(1872+25t+t^2).
```

After squaring, the positive margin is

```text
1872+25t+t^2 - (22+2t)^2
  = 1388 - 63t - 3t^2
  = 62 + (13-t)(102+3t) > 0.
```

This identity closes the entire attachment range uniformly; no case split or
numerical approximation is used.

## Stronger connectedness result

To obtain an outside vertex, choose `s in S`. Connectedness of `G` supplies a
`G`-neighbor `y` of `s`, and independence forces `y` outside `S`. The tradeoff
then closes the exact residual.

Therefore the formal theorem at `alpha(G)=13` requires only `G.Connected`.
Connectedness of `Gᶜ`, although present in the upstream conjecture, is not
needed for this slice.

The warning-clean no-`sorry` declarations are:

- `card_le_indepNeighborsCard_of_indep_neighbor_subset`;
- `alpha_thirteen_attachment_tradeoff`;
- `twenty_two_add_two_mul_lt_sqrt_tradeoff`;
- `conjecture100_of_connected_of_indepNum_eq_thirteen`.

The final theorem has the exact upstream degree-norm conclusion:

```text
G.Connected -> alpha(G)=13 ->
alpha(G) <= ceil((L + degreeL2Norm(Gᶜ)/2)/2).
```

It does not invoke the upstream open theorem or its `sorry`.

## Verification

The three earlier local modules were compiled into a temporary module path,
then the new continuation was checked with warnings promoted to errors:

```bash
LEAN_PATH=/tmp/c5k4-proof100-alpha13 timeout 60s lake env lean \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture100AlphaThirteen.lean
```

Result: exit code 0 in 9.8 seconds. The file contains no `sorry`, `admit`,
custom axiom, or diagnostic command. Every subprocess remained below the
60-second campaign cap. The temporary dependency directory can be discarded;
it contains generated oleans only.

## Updated residue and next wall

Combining v0.9--v0.11 closes

```text
alpha(G) in {2,3,13} or alpha(G)>=14.
```

The connected residue is now

```text
4 <= alpha(G) <= 12.
```

The attachment calculation is not special to 13 except for its constants.
For a maximum independent `a`-set and an outside vertex with `t` complement
attachments, the same proof pattern gives

```text
L >= a-t,
q^2 >= a(a-1)^2 + (2a-1)t + t^2.
```

The next useful extraction is to formalize that parameterized theorem once and
solve exactly which remaining values `4<=a<=12` it closes, instead of
duplicating a separate fixed-cardinality argument for each value.
