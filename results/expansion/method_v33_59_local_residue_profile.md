# Method v33: WOWII #59 exact local residue profile

Date: 2026-08-13

Local certificate: `lean/GraphConjecture59LocalResidueProfile.lean`

## Exact completion audit

After the v31-v32 propagation, the only untracked edges in the named
eleven-vertex frame are the twelve incidences

```text
{r,s,t} x {u,c,v,p}.
```

The module encodes these as a mask in `Fin 4096`. All other edges and
nonedges are fixed by the `K3,3-e` core, the aligned outside path, the full
fan, and the proved saturation of `d,q`.

The mask is restricted by exactly the two previously formalized conditions:

1. v31's exact deficient-column DNF

   ```text
   (t-u and t-v)
   or (t-u and t-c and t-p)
   or (t-c and t-v and t-p);
   ```

2. v32's four pointwise covers

   ```text
   r-z or s-z, for z = u,c,v,p.
   ```

Of the 4096 raw masks, an independent exhaustive enumerator finds 486 that
satisfy both conditions and 51 distinct descending degree profiles. The Lean
module records all 51 profiles and proves by ordinary kernel reduction that
each has

```text
Havel--Hakimi residue = 2.
```

No `native_decide` is used.

The attempted single kernel reduction quantifying directly over all 4096
masks exceeded the mandatory 60-second process cap. Accordingly, the present
certificate deliberately separates the two audit layers:

- exact mask-to-profile enumeration: external exhaustive computation;
- residue-two verification of every resulting profile: Lean theorem
  `every_admissible_profile_has_residue_two`.

The direct mask-to-profile inclusion remains to be decomposed into smaller
Lean cases; it is not claimed as kernel-certified in this checkpoint.

## What this does and does not close

This is the first full-profile residue audit of the local propagation. The
enumeration says the combined incidence constraints force residue two on the
complete named frame, and Lean certifies the residue computation for every
profile produced. The hypothetical WOWII #59 corner requires ambient residue
three.

It is not yet an ambient contradiction. Havel--Hakimi residue is not monotone
under taking induced subgraphs, and the hypothetical graph may contain
vertices outside these eleven names. Such vertices change both the degrees
of the named vertices and the recursive reduction. Therefore the valid next
interface is one of:

- prove that no additional vertices remain;
- prove an extension-stability theorem preserving residue at most two for
  vertices satisfying the earlier unused-pool cover; or
- use an additional outside vertex to create another explicit five-forest.

The third route is the most local and avoids assuming a false residue
monotonicity principle. The exact local result nevertheless identifies the
right invariant: any ambient residue-three survivor must obtain its extra
residue entirely from vertices outside the named eleven-vertex frame.

## Verification

Lean checked all 51 listed residue reductions in 31.79 seconds against the
same clean dependency directory, with warnings promoted to errors and the
mandatory 60-second process cap. The module uses explicit coordinate formulas
and ordinary kernel reduction only; it contains no `sorry`, `admit`, `axiom`,
or `native_decide`.
