# WoW I #724: a connected infinite retro-counterexample family

This certificate records a new family of witnesses to an **already-refuted**
conjecture. It is not a priority claim for refuting an open problem.

## Primary statement and historical status

Page 109 of Fajtlowicz's July 2004 *Written on the Wall* says:

> 724. the number of nonnegative eigenvalues - largest eigenvalue + smallest
> nonnegative eigenvalue <= independence.

The same source credits Tony L. Brewster, Michael J. Dinneen, and Vance Faber
and says the only counterexample their search found was the disjoint union of
two copies of `C5`.

## Connected family

For `m >= 1`, set

`H_m = complement(C5[K_m])`.

Equivalently, replace each vertex of a 5-cycle by an independent `m`-set and
join sets whose cycle positions are nonadjacent. This is a connected,
`2m`-regular, triangle-free graph on `5m` vertices.

Its adjacency spectrum is

```text
2m                                      multiplicity 1
((sqrt(5)-1)m/2)                       multiplicity 2
0                                      multiplicity 5m-5
-((sqrt(5)+1)m/2)                      multiplicity 2
```

There are therefore `5m-2` nonnegative eigenvalues. For `m >= 2`, zero occurs,
the largest eigenvalue is `2m`, and the smallest nonnegative eigenvalue is zero.
Moreover, `alpha(H_m)=2m`: two nonadjacent cycle blobs form an independent
set, while an independent set cannot meet more than two base positions.

For the relevant range `m >= 2`, WoW #724's two sides are consequently

```text
LHS = (5m-2) - 2m + 0 = 3m-2
RHS = alpha(H_m) = 2m.
```

The inequality fails exactly for `m >= 3`. The campaign carrier case `m=4`
is concrete: `10 > 8`.

## Verification

Run:

```bash
/home/ec2-user/.venvs/wowii/bin/python verify.py
```

The verifier constructs `H_m`, recomputes spectra and independence numbers,
checks the closed forms for `m=1..8`, and runs the mandatory database-sanity
gate over every connected nonempty NetworkX Atlas graph through order 7 plus
the named calibration graphs. Spectral comparisons use a `1e-6` guard.

Targeted searches on 2026-08-12 found the primary historical `2C5` report but
no prior appearance of this connected infinite family; novelty is therefore
provisional.
