# Method v30: WOWII #59 three-core closure

Date: 2026-08-13

Local certificate: `lean/GraphConjecture59ThreeCoreClosure.lean`

## Missed attachments are now impossible

The end-to-end `3+3` core relabeling supplies a genuine third vertex `d` on
the same color side as the aligned pair `a,b`. If `q` misses a path vertex
`w`, then

```text
{a,b,d} is independent,
q avoids a,b,w,
and d-q is unrestricted.
```

Consequently `{a,b,d,w,q}` is always a forest: add `w` to the independent
core triple, then add `q`, which has at most the single old neighbor `d`.
This contradicts `f(G)=4`.

Lean composes this witness directly with
`exists_relabeling_with_exact_core_profile`. Therefore both remaining
missed-vertex patterns from v28 are eliminated completely:

* center plus exactly one endpoint;
* both endpoints but not the center.

The v29 cover condition is no longer needed for those cases.

## Saturated all-three/full-fan closure

Only the all-three/full-fan rectangle survives. In this case the same
five-set argument forces, for the third same-side core vertex `d`,

```text
d-q, d-u, d-c, d-v, and d-p.
```

Moreover, if any opposite-side core vertex `t` missed `d`, then
`{a,b,d,t,q}` would be a five-forest. Hence `d` must be complete to the
opposite three-vertex core side as well.

Thus the saturated third core has at least eight distinct neighbors:

```text
u, c, v, p, q, and the three opposite-core vertices.
```

Lean provides the explicit degree conclusion `8 <= degree(d)` once those
eight distinct neighbors are instantiated.

## Profile and residue consequence

The eight-edge `K3,3-e` profile is not eliminated outright, but its missing
core edge cannot be incident with `d`; the deficient same-side vertex must be
one of `a,b`. In the nine-edge profile, `d` is already internally cubic.

No residue contradiction follows from the degree lower bound alone. The repo
already contains exact countermodels showing that residue three can coexist
with very high degree. The useful output of this rung is structural: every
non-all-three case is closed, and the sole saturated case forces a completely
specified high-degree third core row.

## Verification

The entire 29-module dependency closure from `GraphConjecture40Baseline`
through both parent branches and this module was rebuilt into the fresh
directory `/tmp/c5k4-59-v30-audit.0hp4f0`. The final module passed with
`-DwarningAsError=true`; every Lean invocation was independently capped at
60 seconds. The new source contains no `sorry`, `admit`, `axiom`, or
`native_decide`.
