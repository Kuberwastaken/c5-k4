# Method v0.10 — WOWII 100 independence-three near miss

Date: 2026-08-13  
Outcome: `PARTIAL_THEOREM`  
Formal artifact: `lean/GraphConjecture100NearMiss.lean`

## Scope and exact reading

This is a proof-extraction continuation for a statement already in the
development set. It is not a held-out trial, counterexample, or release
candidate.

The upstream module prose describes a complement-diameter term, but its Lean
theorem uses `degreeL2Norm Gᶜ`. This file proves only the exact Lean reading.

The previous two stages established

```text
a <= ceil((L + q/2)/2)  <->  4(a-1) < 2L + q,
L >= 2,
q >= sqrt(a(a-1)^2),
```

for connected `G` and `Gᶜ`, with the latter two inequalities coming from an
induced `P3` and a maximum independent set, respectively.

At `a=3`, these universal bounds give only

```text
8 < 4 + sqrt(12),
```

which is false. The exact norm deficit is small: it is enough to sharpen
`q > 4`.

## Joint structural correction

Let `S` be a maximum independent triple in `G`. In `Gᶜ`, `S` is a triangle,
so its three vertices initially contribute at least

```text
3 * 2^2 = 12
```

to the squared-degree sum.

The triple is a proper subset. Formally, choose `s in S`. Connectedness of `G`
gives a `G`-neighbor `z` of `s`; independence of `S` forces `z` outside `S`.
Connectedness of `Gᶜ` then supplies a walk from `s` to `z`. The first boundary
dart of that walk is a complement edge `ay` with `a in S` and `y outside S`.

That one crossing edge strengthens the degree contributions to

```text
degree_Gᶜ(a) >= 3,
degree_Gᶜ(y) >= 1,
degree_Gᶜ(v) >= 2 for the other two v in S.
```

Therefore

```text
sum_v degree_Gᶜ(v)^2 >= 3^2 + 2*2^2 + 1^2 = 18,
q >= sqrt(18) > 4.
```

Substituting `a=3`, `L>=2`, and `q>4` into the exact residual gives

```text
8 < 2L + q,
```

which proves the exact formalized conjecture at independence number three.

## Formal result

The warning-clean no-`sorry` development proves:

- `eighteen_le_compl_energy_of_indep_triple_crossing`;
- `eighteen_le_compl_energy_of_connected_indepNum_three`;
- `four_lt_degreeL2Norm_compl_of_connected_indepNum_three`;
- `conjecture100_of_connected_of_indepNum_eq_three`.

The last theorem has the exact upstream conclusion and hypotheses:

```text
G.Connected -> Gᶜ.Connected -> alpha(G)=3 ->
alpha(G) <= ceil((L + degreeL2Norm(Gᶜ)/2)/2).
```

It imports the earlier extraction modules but never invokes the upstream open
theorem or its `sorry`.

## Verification

The two local dependencies were compiled into a temporary module directory,
then the continuation was checked with warnings promoted to errors:

```bash
tmpdir=$(mktemp -d)
timeout 60s lake env lean -R /Users/kuber.mehta/Projects/c5-k4/lean \
  -DwarningAsError=true \
  -o "$tmpdir/GraphConjecture100Extraction.olean" \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture100Extraction.lean
LEAN_PATH="$tmpdir:${LEAN_PATH:-}" timeout 60s lake env lean \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  -DwarningAsError=true \
  -o "$tmpdir/GraphConjecture100FiniteRange.olean" \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture100FiniteRange.lean
LEAN_PATH="$tmpdir:${LEAN_PATH:-}" timeout 60s lake env lean \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture100NearMiss.lean
rm -r "$tmpdir"
```

Result: exit code 0. There are no `sorry`, `admit`, custom axioms, or
diagnostic commands. Every subprocess remained below 60 seconds.

## Updated residue

Combining v0.9 and v0.10 closes

```text
alpha(G) in {2,3} or alpha(G) >= 14.
```

The exact connected residue is now

```text
4 <= alpha(G) <= 13.
```

The `alpha=13` near miss cannot be closed by merely repeating the one-crossing
energy argument: one attachment raises the crude squared energy from `1872`
to only `1898`, while the energy-only corrected target is `1936`. The next
joint argument should exploit the complementary tradeoff: a vertex outside a
large independent set that has few complement attachments has many neighbors
inside it in `G`, which directly raises `L`. This energy/local-independence
tradeoff is the appropriate next wall, rather than counting complement energy
alone.
