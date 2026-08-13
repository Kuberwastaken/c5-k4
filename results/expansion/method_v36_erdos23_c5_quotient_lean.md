# Erdős 23 weighted `C5` quotient Lean extraction

## Result

The computational identity for nonuniform independent-set blow-ups of `C5`
is

```text
beta_edge = min_i |A_i| |A_(i+1)|.
```

The new Lean module extracts its two reusable quotient kernels.

First, it proves the exact local false-twin rounding inequality.  If `x` of
the `n` vertices in one bag lie on one cut side and the already-fixed neighbor
assignments give aggregate coefficients `l,r`, then

```text
x*r + (n-x)*l <= max(n*r,n*l).
```

Thus one of the two whole-bag placements is never worse than the current split
placement.  Repeating this certificate bag by bag is the standard optimum-cut
normalization argument.

Second, it defines the symbolic monochromatic-interface cost of a Boolean
coloring of a weighted five-cycle and proves both directions of the exact
identity:

- every coloring pays at least the minimum interface weight;
- each interface has an explicit coloring making it the unique
  monochromatic interface, so the minimum is attained.

The product-weight corollary substitutes `|A_i||A_(i+1)|` directly.

## Honest API boundary

The file does not claim a full theorem about `SimpleGraph` cuts.  The current
repository has a uniform `blowupC5` definition but no nonuniform weighted
blow-up structure carrying its five bags, edge partition, and arbitrary-cut
counts.  Building that layer would be much larger than the combinatorial
extraction.  Instead the Lean result supplies exactly the arithmetic theorem
and the local rounding certificate that such a graph-level adapter must use.

The explicit five colorings also formalize the constructive upper bound:
deleting a chosen interface leaves the quotient path, hence the blow-up is
bipartite.  The final graph-lifting sentence remains an adapter obligation,
not a hidden premise of the arithmetic theorem.

## Verification

From the pinned local `formal-conjectures` environment:

```text
timeout 55s lake env lean -DwarningAsError=true \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  /Users/kuber.mehta/Projects/c5-k4/lean/Erdos23C5BlowupQuotient.lean
```

The command exited zero in 6.4 seconds with no output.  The module contains no
`sorry`, `admit`, custom `axiom`, or native decision procedure.
Fresh `.olean` compilation followed by `#print axioms` reports only Lean's
standard `propext`, `Classical.choice`, and `Quot.sound` foundations for the
exact weighted-cycle theorem, the bag-rounding lemma, and the product-weight
corollary.

No commit, push, release, issue, PR, or other public action was performed.
