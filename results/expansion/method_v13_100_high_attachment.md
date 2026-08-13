# Method v0.13 — WOWII 100 high-attachment aggregate

Date: 2026-08-13  
Outcome: `CONDITIONAL_THEOREM`  
Formal artifact: `lean/GraphConjecture100HighAttachment.lean`

## Scope and reading warning

This is proof extraction in the existing WOWII 100 lane, not a held-out trial
or a counterexample/release candidate. The upstream prose discusses complement
diameter, while the Lean theorem uses `degreeL2Norm Gᶜ`. This work addresses
only that exact Lean expression.

## Two-outside coordinate model

Let `S` be a maximum independent set of size `a`, and let two distinct outside
vertices have complement-attachment counts `t,u` into `S`. If each is a
`G`-neighbor of at least one member of `S`, then `t,u <= a-1`. The two
nonattachment sets give

```text
L >= max(a-t,a-u) = a-min(t,u).
```

Counting both outside vertices gives the aggregate energy target

```text
q^2 >= a(a-1)^2 + (2a-1)(t+u) + t^2 + u^2.      (E2)
```

The first term is the complement clique on `S`; every attachment raises the
degree-square contribution at its endpoint by at least `2a-1`; and the two
outside vertices contribute `t^2+u^2`.

## Exact bounded optimization

The formal optimizer proves that for every

```text
8 <= a <= 11,  t+1 <= a,  u+1 <= a,
```

the strict residual square inequality holds:

```text
(2a-4+2 min(t,u))^2
  < a(a-1)^2 + (2a-1)(t+u) + t^2 + u^2.
```

The worst exact margins, attained at `t=u=a-1`, are:

| `a` | worst squared margin |
|---:|---:|
| 8 | 24 |
| 9 | 76 |
| 10 | 158 |
| 11 | 276 |

Thus the two-witness package is uniformly sufficient throughout `a=8..11`.

For `a=4..7`, the analogous worst margins are `-4,-12,-14,-4`. The Lean file
contains an exact negative audit showing this same package is not uniform
there. This is a limitation of the lower-bound package, not a graph
counterexample.

## What is formally closed

The Lean file deliberately exposes (E2) as
`TwoOutsideEnergyCertificate`; it is a proposition, not an axiom. The theorem
`conjecture100_of_two_outside_energy_certificate` proves the exact upstream
degree-norm conclusion from:

- `8 <= a <= 11`;
- both attachment counts at most `a-1`;
- the two explicit local-independence bounds;
- the explicit aggregate energy certificate (E2).

This is a verified conditional structural slice. It is not yet an
unconditional closure of `alpha=8..11`: the remaining graph-theoretic bridge
is to construct two suitable distinct outside witnesses from connectedness
and derive (E2) inside Lean. A first direct formalization of that incidence
sum was abandoned because its subtype and finite-sum proof became
disproportionately large; the obligation is kept visible rather than hidden.

## Verification

With local dependency oleans in `/tmp/c5k4-proof100-high`, the target was
checked by:

```bash
LEAN_PATH=/tmp/c5k4-proof100-high timeout 60s lake env lean \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture100HighAttachment.lean
```

The checker completed within the 60-second shell cap with no diagnostics. The
artifact contains no `native_decide`, `sorry`, `admit`, custom axiom, or
diagnostic command. The finite optimizer has an explicit heartbeat allowance
but remains bounded by the mandatory wall-clock cap.

## Next obligation

The exact high-value target is now narrow:

1. prove that connectedness supplies two distinct outside cross-edge
   witnesses whenever the one-witness v0.12 threshold does not already apply;
2. formalize the incidence identity behind (E2), preferably as a reusable sum
   over attachment multiplicities rather than four adjacency case splits;
3. instantiate the conditional theorem to close `alpha=8..11` unconditionally.

The lower range `alpha=4..7` will require either three or more outside
witnesses or a sharper structural constraint; two witnesses alone are
provably insufficient in the worst coordinate cases.
