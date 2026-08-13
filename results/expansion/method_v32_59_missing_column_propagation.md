# Method v32: WOWII #59 nondeficient-column propagation

Date: 2026-08-13

Local certificate: `lean/GraphConjecture59MissingColumnPropagation.lean`

## Scope relative to v31

This module imports `GraphConjecture59OppositeColumnClosure` and does not
repeat its deficient-column results. In particular, v31 already proves
`q-t`, both two-of-three covers at `t`, their exact three-pattern DNF, and
`degree(t) >= 5`.

The v32 contribution is the complementary all-column information.

## Matrix extraction and all-column closure

At the exact matrix level, a unique missing edge in aligned row `a` selects
a column `t` in which the other distinct rows `b,d` are present. This
connects `OneMissingCoreEdgeAtRow` to the graph-level deficient-column
notation used in v31.

More generally, if `q` missed any opposite-core vertex `x`, then

```text
{a,b,d,x,q}
```

would be a five-forest. Begin with the independent aligned-core triple,
add `x` with arbitrary incidences to that triple, and then add `q`, which
can see only `d` among the preceding vertices. Thus `q` is complete to all
three opposite-core columns, not only to the deficient column from v31.

Together with the saturated outside rectangle, the eight certified neighbors

```text
u,c,v,p,d,r,s,t
```

give `degree(q) >= 8`.

## Joint cover by the nondeficient columns

Let `r,s` be the two columns other than the deficient column `t`. For every
frame vertex `z` among `u,c,v,p`, at least one of `r-z,s-z` is an edge.
Otherwise

```text
{a,r,s,t,z}
```

is a five-forest. The possible edge `t-z` is harmless: build from independent
`{r,s}`, add `a`, then `z`, then `t` as successive leaf extensions.

Four pointwise covers imply by pigeonhole that one of `r,s` hits at least
two of the four frame vertices. Each already has the four certified neighbors
`a,b,d,q`, so Lean proves

```text
degree(r) >= 6 or degree(s) >= 6.
```

The combined v31-v32 named degree prefix is therefore

```text
degree(d) >= 8,
degree(q) >= 8,
degree(nondeficient aligned row) >= 7,
degree(deficient aligned row) >= 6,
degree(t) >= 5,
degree(r) >= 6 or degree(s) >= 6.
```

The next question is whether this many simultaneous large entries constrain
the Havel--Hakimi residue, rather than merely one isolated degree. That audit
must account for the ambient order and every untracked outside vertex; the
local prefix alone must not be silently identified with the complete degree
sequence.
