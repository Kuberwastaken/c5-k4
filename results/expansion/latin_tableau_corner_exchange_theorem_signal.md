# Latin Tableau corner-exchange theorem signal

**Classification:** `THEOREM_SIGNAL`; no further size sweep  
**Input:** independently verified order-15 bottom-corner trial

Let `A_k(lambda)` be the maximum number of cells covered by `k` disjoint
stable sets, equivalently `k` matchings in the Ferrers bipartite graph. Delete
the bottommost corner `x` to obtain `lambda^-` and set

```text
Delta_k = A_k(lambda) - A_k(lambda^-).
```

Deletion changes every optimum by at most one, so `Delta_k` is zero or one.
Split the Ferrers min-cut candidates into:

- `P_k`, the minimum among cuts covering `x`;
- `Q_k`, the minimum among cuts leaving `x` in the uncovered rectangle.

The exact identities are

```text
A_k(lambda)   = min(P_k, Q_k)
A_k(lambda^-) = min(P_k, Q_k - 1),
```

and hence

```text
Delta_k = 1  iff  Q_k <= P_k.
```

Thus the corner affects `A_k` exactly when an optimal `k`-cut leaves it
uncovered.

For the CDS class-size profiles `d_k=A_k-A_(k-1)`, telescoping gives

```text
d_k(lambda) - d_k(lambda^-) = Delta_k - Delta_(k-1).
```

Direct corner insertion has the right profile precisely when `Delta` is a
single threshold `0,...,0,1,...,1`. If the threshold begins at color `c`, the
profile difference is the basis vector `e_c`; a child CDS coloring transfers
when color `c` is absent from the new cell's row and column.

## The four order-15 exceptions

| parent | `Delta` | parent profile minus child profile |
|---|---|---|
| `(7,3,3,1,1)` | `0,1,0,1,1,1,1` | `e_2-e_3+e_4` |
| `(5,5,2,1,1,1)` | `0,0,0,1,0,1` | `e_4-e_5+e_6` |
| `(4,4,4,2,1)` | `0,0,1,0,1` | `e_3-e_4+e_5` |
| `(4,4,4,1,1,1)` | `0,0,1,0,0,1` | `e_3-e_4+e_6` |

Each is exactly one redistribution plus one new-color insertion—not an
arbitrary failure. The min-cut winner's treatment of the deleted corner
switches, making `Delta` nonmonotone.

## Exchange lemma

A useful restricted lemma is:

> If a child CDS coloring has a `b`-majority alternating component in the union
> of color matchings `M_a union M_b`, and color `c` avoids the new corner's row
> and column, swap `a,b` on that component and color the corner `c`. The result
> realizes profile change `e_a-e_b+e_c`.

The following pieces should be direct Lean targets:

1. deletion changes `A_k` by at most one;
2. the profile/`Delta` telescoping identity;
3. threshold `Delta` iff the profile difference is one basis vector;
4. direct proper-coloring corner extension;
5. the two-color alternating-component swap;
6. composition into an `e_a-e_b+e_c` extension certificate.

The genuine combinatorial work is formalizing the Ferrers union-of-matchings
min-cut theorem and proving that an exchange-ready CDS coloring exists. An
arbitrary child coloring need not expose the needed two-color path, so the
remaining result likely needs a multicolor augmenting-trail theorem.

The first four algebra/coloring components are now extracted in
`lean/LatinTableauCornerExchange.lean`. At exact upstream commit
`7a38c469ec329d0c97c068e03c58834f61628e7e`, the module passes

```text
timeout 60s lake env lean -DwarningAsError=true \
  lean/LatinTableauCornerExchange.lean
```

It formalizes the profile/`Delta` telescoping identity, the `{-1,0,1}`
coordinate bound from binary `Delta`, the threshold-to-basis-vector step,
generic proper-coloring extension across one new vertex, and the actual
`SimpleGraph.indepNumK` deletion inequality

```text
indepNumK(G-v,k) <= indepNumK(G,k) <= indepNumK(G-v,k)+1.
```

The last theorem discharges the binary-`Delta` assumption at the API used by
the conjecture. The module intentionally does not assert the Ferrers min-cut
formulas or existence of the required exchange-ready component.

The next honest lane is the restricted **one-defect nesting theorem**:

> Under corner deletion, when the profile difference is `e_a-e_b+e_c`, give
> sufficient active-corner/min-cut conditions for a CDS coloring with the
> required exchange and color-`c` endpoint slack.

This target explains the four exceptions without claiming the full Latin
Tableau conjecture. No additional order sweep, counterexample claim, issue,
PR, or release is authorized by this signal.
