# Method v31: WOWII #59 opposite-column closure

Date: 2026-08-13

Local certificate: `lean/GraphConjecture59OppositeColumnClosure.lean`

## Outcome

The v30 three-core closure forces the surviving all-three/full-fan branch to
have a complete third row `d`.  Therefore, in the `K3,3-e` case, the unique
missing core edge joins one aligned row—call it `a`—to an opposite-side core
vertex `t`.

This checkpoint uses that opposite endpoint.  Three different five-vertex
sets give three independent constraints.

### 1. The missing column endpoint must see `q`

If `t-q` were absent, the five-set

```text
{a,b,d,t,q}
```

could be constructed as successive leaf extensions along `q-d-t-b`, with
`a` isolated.  It would be an induced forest, contradicting `f(G)=4`.
Therefore Lean proves `t-q`.

### 2. The aligned-star exchange

The set `{a,t,u,v,p}` starts with the independent triple `{u,v,p}` and adds
the aligned vertex `a`.  Since `a-t` is the missing core edge, adding `t`
preserves acyclicity whenever `t` has at most one neighbor among `{u,v,p}`.
Thus survival forces

```text
t hits at least two of {u,v,p}.
```

### 3. The outside-path exchange

Build the path `u-c-v`, add `t`, and finally add `p`, which avoids the entire
outside path.  This remains a forest whenever `t` has at most one neighbor
on the path.  Hence survival also forces

```text
t hits at least two of {u,c,v}.
```

The theorem `opposite_column_forced_profile` certifies all three conclusions
from the actual graph hypotheses and three order-five cardinality witnesses.

## Exact remaining attachment patterns

The conjunction of the two covers simplifies exactly to

```text
(t-u and t-v)
or (t-u and t-c and t-p)
or (t-c and t-v and t-p).
```

Lean proves this equivalence in
`two_opposite_covers_iff_exact_patterns`.  Together with forced `t-q`, this
is the exact new core/frame neighborhood restriction on the endpoint of the
missing edge.

It is stronger than a scalar degree statement because it identifies which
edges must coexist.  In particular, `t` has its two surviving internal-core
neighbors `b,d`, the forced neighbor `q`, and at least two of `{u,v,p}`.
Given distinctness, Lean proves

```text
5 <= degree(t).
```

## Degree-prefix consequence and boundary

Combining this rung with v30 gives the prospective named degree prefix

```text
degree(d) >= 8,
degree(nondeficient aligned row) >= 7,
degree(deficient aligned row) >= 6,
degree(t) >= 5.
```

The new module kernel-certifies the `t >= 5` component.  The `d >= 8`
component is already certified in `GraphConjecture59ThreeCoreClosure`; the
two aligned-row ambient-degree conversions remain bookkeeping work requiring
their four distinct outside neighbors to be packaged explicitly.

This degree prefix still does not imply residue below three on its own.  The
repository's earlier split-graph model already warns that high degrees and
residue three can coexist.  The useful advance is the exact adjacency DNF,
which supplies three sharply bounded branches for the next forest exchange.

The most promising next move is branchwise:

1. if `t-u` and `t-v`, exploit the resulting rectangle against the path
   center `c`;
2. if `t-u,t-c,t-p`, use the missed endpoint `v` as the next leaf candidate;
3. symmetrically, if `t-c,t-v,t-p`, use `u`.

## Lean audit

`GraphConjecture59CoreCoverSynthesis` was rebuilt to an olean in 20.44
seconds.  The new module then passed with the pinned Lean 4.27 toolchain,
warnings as errors, and the 60-second process cap:

```text
ELAN_TOOLCHAIN=leanprover/lean4:v4.27.0 \
LEAN_PATH=/tmp/c5k4-59-v31-opposite:/tmp/c5k4-59-v30-audit.0hp4f0:\
/tmp/c5k4-59-v30-synthesis:/tmp/c5k4-59-v29-audit.BoHebr:\
/tmp/c5k4-59-v27-audit.Q5a01Z:/tmp \
timeout 60s lake env lean \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture59OppositeColumnClosure.lean
```

Result: exit code 0 in 7.70 seconds.  The source contains no proof holes,
native evaluation shortcut, custom axioms, or diagnostic print commands.

WOWII #59 is already externally disproved.  This is theorem extraction, not
a new counterexample or release candidate.
