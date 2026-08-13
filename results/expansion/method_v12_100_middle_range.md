# Method v0.12 — WOWII 100 parameterized middle range

Date: 2026-08-13  
Outcome: `PARTIAL_THEOREM`  
Formal artifact: `lean/GraphConjecture100MiddleRange.lean`

## Scope and reading warning

This is proof extraction inside the existing WOWII 100 development lane. It
is not a held-out discovery, counterexample, or release candidate.

The upstream module prose discusses the diameter of the complement, while its
Lean theorem expression uses `degreeL2Norm Gᶜ`. Every result below follows the
exact Lean expression. None should be presented as resolving the distinct
diameter reading.

## General attachment theorem

Let `S` be any nonempty independent set, let `a=|S|`, and let `y` be outside
`S`. Define

```text
T = {s in S | Gᶜ.Adj y s},
t = |T|.
```

The new parameterized Lean theorem proves both sides of the shared tradeoff:

```text
indepNeighborsCard(G,y) >= a-t,

sum_v degree_Gᶜ(v)^2
  >= (a-1)^2(a-t) + a^2 t + t^2.
```

The proof is fully structural:

- the `a-t` nonattachments are independent `G`-neighbors of `y`;
- every vertex of `S` has the other `a-1` vertices as complement neighbors;
- each attached vertex has the additional complement neighbor `y`;
- `degree_Gᶜ(y)>=t`.

This generalizes the fixed `a=13` argument from method v0.11.

## Residual optimization

The exact ceiling residual is

```text
4(a-1) < 2L + q.
```

After substituting the parameterized bounds, it suffices that

```text
(2a-4+2t)^2 < (a-1)^2(a-t) + a^2t + t^2.       (1)
```

The difference between the right and left sides is

```text
D(a,t) = a^3 - 6a^2 + 17a - 16 + (15-6a)t - 3t^2.
```

For `a>=12`, the chosen outside vertex can be taken as a `G`-neighbor of a
vertex in `S`, so at least one member of `S` is a nonattachment and
`t<=a-1`. The exact decomposition

```text
D(a,t)
 = [(a-12)^3 + 21(a-12)^2 + 116(a-12) + 62]
   + 3(a-1-t)(3a+t-6)
```

is strictly positive throughout that range.

This is the unconditional symbolic range. Lean proves it without enumerating
values of either parameter.

## New unconditional closure

The final graph theorem states:

```text
G.Connected -> 12 <= alpha(G) ->
alpha(G) <= ceil((L + degreeL2Norm(Gᶜ)/2)/2).
```

Connectedness of `Gᶜ` is unnecessary. Relative to v0.11, the genuinely new
closed value is

```text
alpha(G)=12.
```

Values 13 and above were already closed by earlier rungs, though the new
symbolic theorem subsumes them with one proof.

## Finite conditional cases below 12

For `4<=a<=11`, inequality (1) is not uniform over all `t<=a-1`. Exact finite
arithmetic gives the following sufficient attachment ranges:

| `a` | attachment counts formally certified |
|---:|:---|
| 4 | `t <= 1` |
| 5 | `t <= 2` |
| 6 | `t <= 2` |
| 7 | `t <= 3` |
| 8 | `t <= 5` |
| 9 | `t <= 6` |
| 10 | `t <= 8` |
| 11 | `t <= 9` |

These are conditional structural slices, not unconditional resolutions of
the corresponding independence numbers. The Lean lemma `finite_middle_margin`
certifies every row by exact finite interval cases. It is kept separate from
the symbolic `a>=12` theorem so enumeration is not disguised as a general
argument.

The first excluded counts really do defeat this lower-bound package. For
example, at `(a,t)=(11,10)`, the squared margin is `-34`; at `(10,9)` it is
`-94`. This does not refute the conjecture. It shows only that more graph
structure is required when an outside vertex has nearly all of `S` as
complement neighbors.

## Formal declarations

The warning-clean no-`sorry` file adds:

- `attachment_tradeoff`;
- `symbolic_margin_of_twelve_le`;
- `finite_middle_margin`;
- `conjecture100_of_connected_of_twelve_le_indepNum`.

The final theorem has the exact upstream degree-norm conclusion and does not
invoke the upstream open theorem or its `sorry`.

## Verification

The four earlier local modules were compiled into a temporary module path,
then the new file was checked with warnings promoted to errors:

```bash
LEAN_PATH=/tmp/c5k4-proof100-middle timeout 60s lake env lean \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture100MiddleRange.lean
```

Result: exit code 0 in 9.7 seconds. The artifact contains no `sorry`, `admit`,
custom axiom, or diagnostic command. Every subprocess stayed below the
60-second campaign cap.

## Updated residue

Combining v0.9--v0.12 closes the exact Lean reading for

```text
alpha(G) in {2,3} or alpha(G)>=12
```

under the upstream connectedness hypotheses. The remaining unconditional
independence range is now

```text
4 <= alpha(G) <= 11.
```

The conditional table identifies the next obstruction precisely: the only
unresolved configurations are high-attachment outside vertices. Their many
complement attachments raise energy, but not quite as quickly as the current
residual after the local term shrinks. The next proof should use additional
vertices or connectedness to show that either some outside vertex has a lower
attachment count, or multiple outside vertices contribute enough extra
complement energy to close the high-attachment cases.
