# Method v0.8 — WOWII 100 complement-energy extraction

Date: 2026-08-13  
Outcome: `PARTIAL_THEOREM`  
Formal artifact: `lean/GraphConjecture100Extraction.lean`

## Scope

This is proof extraction from a statement already present in the current
`formal-conjectures` development set. It is not a held-out discovery trial and
does not add a counterexample or release candidate.

The exact upstream Lean conclusion is

```text
alpha(G) <= ceil((max_v indepNeighborsCard(G,v)
                 + (1/2) * degreeL2Norm(complement G)) / 2).
```

There is a material prose/code discrepancy in the upstream module: its
docstring discusses the diameter of the complement, but the theorem expression
uses `degreeL2Norm Gᶜ`. The proof here follows the Lean expression exactly and
does not silently substitute the prose reading.

## Exact residual wall

Writing

```text
a = alpha(G),
L = max_v indepNeighborsCard(G,v),
q = degreeL2Norm(complement G),
```

integrality of `a` turns the ceiling conclusion into the exact equivalence

```text
a <= ceil((L + q/2)/2)  <->  4(a - 1) < 2L + q.
```

This is formalized as `conjecture100_iff_residual`, with an immediately usable
one-way wrapper `conjecture100_of_residual`.

## Graph-theoretic extraction

If `S` is independent in `G`, then it is a clique in `Gᶜ`. Hence every vertex
of `S` has complement degree at least `|S|-1`, giving

```text
|S| (|S|-1)^2 <= sum_v degree(Gᶜ,v)^2.
```

The Lean development proves this first for an explicit independent set and
then instantiates a maximum independent set:

```text
sqrt(a (a-1)^2) <= degreeL2Norm(Gᶜ).
```

For `a >= 17`,

```text
4(a-1) < sqrt(a (a-1)^2),
```

so the norm term alone crosses the exact residual wall; the nonnegative local
term `2L` is not needed. Therefore the exact formalized WOWII 100 inequality
holds for every finite graph with independence number at least 17.
Connectivity of either graph is unnecessary for this specialization.

The threshold is the natural cutoff for this norm-only argument: at `a=16`,
the two displayed quantities are both `60`. The positive local term may still
close that boundary and smaller values, but that requires additional analysis.

## Formal trust result

The file proves, without importing or invoking the upstream conjecture theorem:

- `card_sub_one_le_compl_degree_of_indep`;
- `independent_set_compl_degree_energy`;
- `sqrt_indep_energy_le_degreeL2Norm_compl`;
- `conjecture100_iff_residual`;
- `conjecture100_of_residual`;
- `four_mul_indep_sub_one_lt_sqrt_energy`;
- `conjecture100_of_indepNum_ge_seventeen`.

Verification command:

```bash
timeout 60s lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture100Extraction.lean
```

Result: exit code 0. The artifact contains no `sorry`, `admit`, or custom
axiom. Every subprocess remained under the campaign's 60-second cap.

## Remaining obligation

This closes the entire `alpha(G) >= 17` regime of the formalized statement.
The open residue is finite in the independence coordinate:

```text
2 <= alpha(G) <= 16
```

under the upstream connectedness assumptions (the endpoint lower bound follows
from connectedness of the complement). The next useful rung is to combine the
positive `2L` correction with sharper complement degree constraints in that
range, rather than re-proving the already closed high-independence case.
