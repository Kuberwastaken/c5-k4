# Method v0.30: unconditional WOWII #141 closure through girth eleven

Date: 2026-08-13
Status: original conjecture closed for every connected graph of girth at most eleven

## Result

[`lean/GraphConjecture141GirthElevenClosure.lean`](../../lean/GraphConjecture141GirthElevenClosure.lean)
feeds the v0.29 radius-three exclusion into the existing three-tail assembly.
It proves the original WOWII #141 inequality unconditionally in the girth-ten
and girth-eleven range and combines this with v0.19 to close every connected
graph of girth at most eleven.

The exported endpoint is:

```lean
theorem conjecture141_of_girth_le_eleven
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hconn : G.Connected) (hgirth : G.girth ≤ 11) :
    (G.girth / 2 : ℤ) - 1 +
        ((Finset.univ.sup (indepNeighborsCard G) : ℕ) : ℤ) ≤
      (largestInducedTreeSize G : ℤ)
```

## Four-edge prefix

At a vertex maximizing local independence, v0.29 supplies a vertex at
distance at least four.  Connectedness and the shortest-path extraction from
v0.21 then give a chordless prefix

```text
v -- u -- x -- y -- z.
```

The existing `secondLeafDataOfPrefix` construction uses `v-u-x-y` to build a
maximum local star with the verified two-vertex tail `x-y`.

## Third-leaf attachment

It remains to show that `z` is a leaf in the induced graph retained by the
two-tail certificate.  The shortest-path prefix already records

```text
z not adjacent to v, u, or x,
```

and its five-vertex cardinality certificate gives all required vertex
inequalities.

If `z` had an additional neighbor `a` in `N(v)`, then

```text
v -- u -- x -- y -- z -- a -- v
```

would be a simple cycle of length six.  Girth at least ten excludes this.
Thus among the retained star and tail vertices, `z` is adjacent exactly to
`y`.  This constructs `ThirdLeafData`, and the pre-existing leaf-extension
theorem supplies an induced tree with

```text
max local independence + 4
```

vertices.  Since `girth / 2 ≤ 5` for girth ten or eleven, this is exactly the
arithmetic needed by the original conjecture.

## Scope

This rung closes an exact original-conjecture range; it is not merely another
structural reduction.  The remaining unchecked values, if the project
continues upward by the same direct tail strategy, begin at girth twelve and
require one more retained vertex beyond maximum local independence.

## Verification

The complete recursive #141 chain, from `GraphConjecture141Extraction`
through `GraphConjecture141GirthElevenClosure`, was compiled from source into
a fresh temporary directory.  Each invocation used:

```bash
LEAN_PATH=<fresh-audit-directory> timeout 60s lake env lean \
  -DwarningAsError=true \
  -o <fresh-audit-directory>/<MODULE>.olean \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  /Users/kuber.mehta/Projects/c5-k4/lean/<MODULE>.lean
```

Every process was individually capped at 60 seconds.  The new module contains
no `sorry`, `admit`, `native_decide`, `#print`, or custom axiom declaration.
