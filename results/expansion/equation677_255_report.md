# Equation 677 to 255 finite selector

**Outcome:** `TIMEOUT_BRACKET_AFTER_EXACT_UNSAT_PREFIX`  
**Evidence split:** development, retrospectively packaged  
**Formal Conjectures base:** `7a38c469ec329d0c97c068e03c58834f61628e7e`  
**Equational Theories base:** `9836b9b39dd39dd36dc0a20375ed95f3db6f0eac`

## Why this target belongs in the method loop

The declaration has the correct finite-certificate shape. One finite magma
satisfying Equation 677 but not Equation 255 would settle the negative side,
and its complete operation table is independently replayable. This is not an
Erdős entry and does not use the graph-invariant residual machinery; it is a
useful non-graph test of Method v1's certificate gate and evidence discipline.

The primary project describes the finite implication as its main remaining
open question. DeepMind has formalized exactly that implication as
`EquationalTheories_677_255.Finite.Equation677_implies_Equation255`, still with
category `research open`. Searches found public benchmark copies but no proof,
finite counterexample, merged solution, open competing solution, or release
covering the exact declaration.

## Encoding audit

For each order `n`, variables assert `i*j=k`. The SAT instance enforces a total
single-valued operation, Equation 677, and failure of Equation 255 at label
zero. Requiring each left translation to be a permutation is a derived finite
consequence of Equation 677, not a heuristic restriction: for fixed `y`, the
law explicitly writes every `x` as `y*z`, so left multiplication by `y` is
surjective and hence bijective on a finite set.

The distinguished failing label is also exact. Any countermodel failing at
some element can be transported along a bijection that sends that element to
zero.

The order-five affine control `x*y=2x-y mod 5` passes both identities and has
canonical compact-table SHA-256
`ba5b9d7a0e32276244edbb11261116fb48bf961fcd8ceea29704d3a56f4d029b`.

## Preserved result

| order | solver verdict | wall time | preserved CNF metadata |
|---:|---|---:|---|
| 5 | UNSAT | 0.016 s | post-run deterministic reconstruction: 125 variables; 3,700 clauses; `1dacee07a7849f1da3f6ae131a3bc0def7492009adbd2054bc8fb126459ff720` |
| 6 | UNSAT | 0.63 s | post-run deterministic reconstruction: 216 variables; 8,964 clauses; `ba715f197714752045d0c977da9a9a7a2cb85f64da6e7de6faf67deb59aca7d6` |
| 7 | UNSAT | 26.37 s | post-run deterministic reconstruction: 343 variables; 19,012 clauses; `7cae8d0041a0e7f77a009379049394455f99fb4f849cbc658bdaeb614e1391c2` |
| 8 | timeout / no verdict | 60.00 s | 512 variables; 36,544 clauses; `1168924d7cf6682c3e7bb947ba51ff935fc0ffbead4fa4a4f15723f3648cd99c` |

Thus no finite countermodel exists at orders five through seven under the exact
encoding. Order eight is unknown; the 60-second timeout gives neither SAT nor
UNSAT evidence. There is no counterexample, proof, Lean artifact, release, or
public action to claim.

The hashes for orders five through seven are not misrepresented as original
solver output: they were reconstructed later from the frozen clause order,
without rerunning a solver. This strengthens artifact identification, not the
UNSAT outcome evidence. There is no automatic GitHub Actions solver workflow
because an unattended push-triggered order-eight rerun would violate the
frozen no-retuning contract.

## Method signal

This is a calibrated zero rather than a discovery. It demonstrates three
useful method behaviors outside graph theory:

1. the certificate-shape gate admits the target for the right reason;
2. a theorem-derived constraint can shrink SAT without changing the model
   class;
3. a timeout remains visibly separate from an exact bounded hold.

The exact four-order trial is closed. Any future attempt needs a new contract,
its own evidence split, and an independently motivated structural restriction
or proof idea; it may not be reported as a continuation of this UNSAT prefix.
