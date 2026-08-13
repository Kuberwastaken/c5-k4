# Černý C13 defect-one dihedral factorization

**Classification:** development, `HOLD_BOUNDED`  
**Frozen family:** `C13_dihedral_factorization_v1`  
**Manifest SHA-256:** `b3d79bb0e1dba995ec13d208113a2425ada47ca832d77c77bac503b9ebafe7c2`

This follow-up addresses the exact failure of the preceding two-cycle surgery:
it preserves a rank-12 defect-one contraction letter. It is a separately frozen
development family, not a retuning of the closed defect-two trial.

## Frozen family

On `Q=Z/13Z`, for each predeclared phase `t=0,...,5`, use

```text
b(12)=0, with b fixing 0,...,11;
r_t(i)=t-i mod 13;
s_t(i)=t+1-i mod 13.
```

Both `r_t` and `s_t` are involutions with one fixed point and six
transpositions, so no individual letter is circular or one-cluster. Their
composition is the original 13-cycle. The standard `C13` shortest word has 132
cycle letters and 12 contractions; replacing each cycle letter by `rs` gives a
legal word of length 276. Thus the frozen nominal sign-potential was favorable:

```text
delta L = +132; delta(144-L) = -132.
```

The explicit opposing risk was that making both factors separately available
would create shortcuts not present in the composite cycle.

Canonical carrier hashes for phases zero through five were:

```text
8dddb3fb775cb61df82d213b3a55f2afee676f24ac9ee9ccd98384bd9583e95e
4de0dd41139b5119b8fbbb5b16d24a2d81fc2cc7cecae07feb38e7837e30ef6e
dc3034c9f5d12c824e30a90f83b2b5ab12048f49a722749cbe75fc924d3ef026
f1552e9466e01153d2096c0acf96bfab14cd0a6563304d8ee23c9b8c9dcfdb65
8617d5614f49e67de0446c92cca659224cf721413fed06e8ee361832311f4429
219c68557deb17166c0c375d049daf783a34e613813e2c014513542c679c4cfd
```

## Exact result

The standard `C3,...,C12` calibration again reproduced `(n-1)^2` exactly.
Every phase has shortest reset length 32 and residual `144-32=112`.

| phase | shortest reset word |
|---:|---|
| 0 | `bsrbsrbsrbsrbsrbsrbsrbsrbsrbsbrb` |
| 1 | `bsrbsrbsrbsrbsrbsrbsrbsrbsbrbsrb` |
| 2 | `bsrbsrbsrbsrbsrbsrbsrbsbrbsrbsrb` |
| 3 | `bsrbsrbsrbsrbsrbsrbsbrbsrbsrbsrb` |
| 4 | `bsrbsrbsrbsrbsrbsbrbsrbsrbsrbsrb` |
| 5 | `bsrbsrbsrbsrbsbrbsrbsrbsrbsrbsrb` |

Each word uses 12 `b`, 10 `r`, and 10 `s` letters. Forward subset BFS and an
independent reverse BFS over all 8,191 nonempty subsets agree on every minimum,
and direct replay reaches a singleton. Total computation was 0.485 seconds,
below the 60-second cap.

## Status, overlap, and conclusion

The exact DeepMind declaration remains open; issue 3905 and merged PR 3906 are
statement-only. MathHandoff commit
`00998a194d2441a4ae677ad3c9a8bfd81f42abd7` covers an open distinguished
two-cycle-letter program but no matching dihedral factorization was found.
Broader permutation-letter plus rank-`n-1` theory exists, so this result is
development evidence rather than an independent held-out test.

The negative shortcut dominates the nominal dilation: relative to the legal
276-letter factorized word, the true optimum improves by 244 steps. The exact
method lesson is:

> Factoring a slow circular generator into separately accessible short
> generators does not preserve its synchronization obstruction.

This family is closed. A future transformation must not expose factors of a
known slow generator as independent shortcut letters. No counterexample,
formal disproof, issue, PR, or release is authorized.
