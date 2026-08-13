# Method v0.9 — WOWII 100 connected finite residue

Date: 2026-08-13  
Outcome: `PARTIAL_THEOREM`  
Formal artifact: `lean/GraphConjecture100FiniteRange.lean`

## Scope and reading

This is a continuation of the already-developed WOWII 100 proof lane, not a
held-out trial and not a counterexample/release candidate.

The upstream module's prose discusses the diameter of the complement, while
its theorem expression actually contains `degreeL2Norm Gᶜ`. This extraction
continues to follow the exact Lean expression. Nothing here should be cited as
a result about the prose diameter reading.

Method v0.8 proved the exact residual equivalence

```text
a <= ceil((L + q/2)/2)  <->  4(a-1) < 2L + q,
```

where `a = alpha(G)`, `L = max_v indepNeighborsCard(G,v)`, and
`q = degreeL2Norm(Gᶜ)`, together with

```text
sqrt(a(a-1)^2) <= q.
```

The unconditional energy term closed `a >= 17`. This lane asks how far the
connectedness hypotheses push the finite residue.

## The forced local correction

If both `G` and `Gᶜ` are connected on a nontrivial finite vertex type, then
`G` is connected and noncomplete. Choose an edge `xz` of `Gᶜ`; this is a
nonedge of `G`. A shortest `G`-walk from `x` to `z` has length at least two,
and its first three vertices form an induced path

```text
u -- v -- w,   with u not adjacent to w.
```

Thus `{u,w}` is an independent two-set in the open neighborhood of `v`, so

```text
L >= 2.
```

The Lean proof uses Mathlib's shortest-walk lemma
`Walk.exists_adj_adj_not_adj_ne`; the independent pair is then constructed
explicitly in the subtype `G.neighborSet v` and compared with that induced
graph's `indepNum`.

This universal lower bound is sharp as a local statement: connected
noncomplete graphs can have maximum local independence exactly two. Any
further improvement must therefore use additional information, such as the
specified value of `alpha(G)`, rather than connectedness alone.

## Exact finite arithmetic

Substituting `2L >= 4` and the complement-energy bound reduces the sufficient
condition to

```text
4(a-1) - 4 < sqrt(a(a-1)^2).
```

The exact squared margins for the unresolved finite values are:

| `a` | left after correction | energy squared | `energy - left^2` | forced? |
|---:|---:|---:|---:|:---|
| 2 | 0 | 2 | 2 | yes |
| 3 | 4 | 12 | -4 | no |
| 4 | 8 | 36 | -28 | no |
| 5 | 12 | 80 | -64 | no |
| 6 | 16 | 150 | -106 | no |
| 7 | 20 | 252 | -148 | no |
| 8 | 24 | 392 | -184 | no |
| 9 | 28 | 576 | -208 | no |
| 10 | 32 | 810 | -214 | no |
| 11 | 36 | 1100 | -196 | no |
| 12 | 40 | 1452 | -148 | no |
| 13 | 44 | 1872 | -64 | no |
| 14 | 48 | 2366 | 62 | yes |
| 15 | 52 | 2940 | 236 | yes |
| 16 | 56 | 3600 | 464 | yes |

The negative rows mean only that these two universal lower bounds do not force
the conjecture; they are not counterexamples or evidence of failure.

For `a=14` and `a=15`, Lean checks the exact strict squared inequalities. For
`a>=16`, it proves

```text
4(a-1) <= sqrt(a(a-1)^2)
```

from `(a-16)(a-1)^2 >= 0`, after which the local correction supplies strict
slack. The isolated `a=2` case follows because the corrected residual is zero
and the energy term is positive.

## Formal result

The strongest final class proved in this lane is:

```text
G.Connected -> Gᶜ.Connected ->
(alpha(G) = 2 or 14 <= alpha(G)) ->
alpha(G) <= ceil((L + degreeL2Norm(Gᶜ)/2)/2).
```

The file also retains the simpler `alpha(G) >= 14` theorem as a direct API
rung. It imports the v0.8 extraction but does not invoke the upstream open
theorem or its `sorry`.

New no-`sorry` declarations:

- `two_le_indepNeighborsCard_of_induced_path`;
- `two_le_max_indepNeighborsCard`;
- `four_mul_sub_four_lt_sqrt_energy_of_ge_fourteen`;
- `four_mul_sub_four_lt_sqrt_energy_of_eq_two`;
- `conjecture100_of_connected_of_indepNum_ge_fourteen`;
- `conjecture100_of_connected_of_indepNum_eq_two_or_ge_fourteen`.

## Verification

The dependency and continuation were compiled under a temporary module path:

```bash
tmpdir=$(mktemp -d)
timeout 60s lake env lean \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  -DwarningAsError=true \
  -o "$tmpdir/GraphConjecture100Extraction.olean" \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture100Extraction.lean
LEAN_PATH="$tmpdir:${LEAN_PATH:-}" timeout 60s lake env lean \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture100FiniteRange.lean
rm -r "$tmpdir"
```

Result: exit code 0. The continuation contains no `sorry`, `admit`, custom
axiom, or diagnostic command. Each subprocess stayed under 60 seconds.

## Remaining range

Under the exact upstream connectedness assumptions, the present proof chain
now leaves only

```text
3 <= alpha(G) <= 13.
```

The next honest move is not to squeeze the sharp universal `L>=2` bound. It is
to derive a joint constraint among `alpha(G)`, complement degree energy, and
local independence in this middle range. The near misses at `a=3` and `a=13`
are the first rational targets: the current squared deficits are only `4` and
`64`, respectively.
