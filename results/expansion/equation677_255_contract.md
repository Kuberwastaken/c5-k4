# Finite Equation 677 implies Equation 255: development contract

This is a post-run transcription of the exact read-only selector that was
evaluated on 2026-08-13. It is **development evidence**, not a Git-preregistered
or held-out trial. No order, timeout, solver, clause, or result was adapted
after the first output.

## Exact target and certificate shape

At `google-deepmind/formal-conjectures@7a38c469`, the declaration
`EquationalTheories_677_255.Finite.Equation677_implies_Equation255` asks whether
every finite magma satisfying

```text
Equation 677: y * (x * ((y * x) * y)) = x
```

also satisfies

```text
Equation 255: ((x * x) * x) * x = x.
```

Its literal finite negation is one finite operation table satisfying Equation
677 and failing Equation 255 at some element. Such a table, plus exhaustive
evaluation of the two identities, is a complete finite counterexample
certificate. The Boolean residual is `R(M)=1` when the implication holds and
`R(M)=0` when it fails; the crossing condition is `R(M)=0`.

The upstream file has Git blob SHA-1
`f5641e3da7b811dca952f00b6fddc3ed3700d0a4` and raw-file SHA-256
`ce01a0a4c994dfd82b8f14295be7f6c97c8be6e59f5367015c299f95a750f6d5`.

## Calibration control

Use the labelled order-five affine magma

```json
[[0,4,3,2,1],[2,1,0,4,3],[4,3,2,1,0],[1,0,4,3,2],[3,2,1,0,4]]
```

serialized exactly as the compact JSON literal above, with no trailing
newline. Its SHA-256 is
`ba5b9d7a0e32276244edbb11261116fb48bf961fcd8ceea29704d3a56f4d029b`.
It is `x*y=2x-y mod 5`; direct affine simplification proves both Equation 677
and Equation 255. This is a safe control, not a counterexample candidate.

## Frozen development domain

Search all operation tables of orders `n=5,6,7,8`, in that order. Use the
exact-one table encoding, then add the valid redundant fact that each left
translation is a permutation. This fact follows because Equation 677 makes
every left translation surjective, and a surjection of a finite set is
bijective.

The compact frozen-domain manifest has SHA-256
`15fd8ad1101782b8dbdc1051e6cccf2bbbd1a1571a2504b9347061fa5597ed70`.

Encode Equation 677 directly. Negate Equation 255 at the distinguished label
`x=0`; this loses no countermodel because any failing element can be relabelled
to zero. Preserve the loop and clause order in
`scripts/prospective_equation677_255_sat.py`. Use PySAT 1.9.dev7 with
`cadical195`, an internal 60-second interrupt, and no solver continuation.

The CNF digest serialization is the UTF-8 encoding of clauses joined by `\n`,
with literals separated by one space and with no DIMACS header or trailing
newline. The reconstruction script has SHA-256
`636bc6c53fb9e4d99a98f8d9419e5b5baa58da691cb6bbf55d3359aa82299066`.

## Evidence boundary

The completed selector retained these outcome results and no stronger outcome
record:

- `n=5`: UNSAT in 0.016 seconds;
- `n=6`: UNSAT in 0.63 seconds;
- `n=7`: UNSAT in 26.37 seconds;
- `n=8`: 512 variables, 36,544 clauses, CNF SHA-256
  `1168924d7cf6682c3e7bb947ba51ff935fc0ffbead4fa4a4f15723f3648cd99c`,
  and no verdict before the exact 60-second cap.

The clause counts and CNF hashes for `n=5,6,7` were not retained by the
original solve. A separate deterministic post-run reconstruction, without a
solver call, produced:

| order | variables | clauses | reconstructed CNF SHA-256 |
|---:|---:|---:|---|
| 5 | 125 | 3,700 | `1dacee07a7849f1da3f6ae131a3bc0def7492009adbd2054bc8fb126459ff720` |
| 6 | 216 | 8,964 | `ba715f197714752045d0c977da9a9a7a2cb85f64da6e7de6faf67deb59aca7d6` |
| 7 | 343 | 19,012 | `7cae8d0041a0e7f77a009379049394455f99fb4f849cbc658bdaeb614e1391c2` |

Those three hashes are labelled `POST_RUN_DETERMINISTIC_RECONSTRUCTION` in the
ledger; they do not pretend that the original solver stdout contained them.
No SAT solve was repeated. The independently reconstructed `n=8` digest
matched the one retained before its solve. The `n=8` timeout is a resource
bracket, never an UNSAT or hold claim.

No new order, restart, solver, timeout extension, clause strengthening, or
parameter retuning belongs to this trial. In particular, do not launch `n=8`
from an automatic push workflow. An explicitly authorized future replay is:

```text
python3 -m pip install --user 'python-sat==1.9.dev7'
timeout 60s python3 scripts/prospective_equation677_255_sat.py --n 8 --cap-seconds 60
```

## Status and overlap

The Equational Theories project at commit
`9836b9b39dd39dd36dc0a20375ed95f3db6f0eac` calls this finite implication the
main remaining open question and the “last survivor.” The formal-conjectures
declaration remains `research open`. Exact repository, all-state issue/PR, and
public code searches found benchmark mirrors and proofs of the *infinite*
non-implication, but no formal solution or finite countermodel for this exact
declaration. The ICARM Equation 677 Database likewise reports that every known
finite example satisfies Equation 255.
