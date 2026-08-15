# Bondy next-coordinate strict stop

- Classification: `STRICT_STOP_G3_WRONG_SIGN`
- Stage reached: target-free constructor reachability (`G2`)
- Stage failed: signed invariant separation (`G3`)
- Circumference, `q_4`, or proposed-target calls: `0`
- Search workflow, candidate, release, issue, or pull request: none

## Status continuity

The read-only status recheck retained upstream commit
`2411d22e1bd550d050d0eac6c1fb379a76a3e7c5` and exact target blob
`c4c5cb1983936860d5a4a7208b3f04bd201290d4`. No open pull request touched
`FormalConjectures/Arxiv/2606.03696/BondyLongestCycles.lean`; exact searches
still returned only the merged ingestion pull request #4879. This audit did
not authorize or perform a target evaluation.

## A legal target-free wall family

For integers

```text
r >= 5,
r + 1 <= c <= 2r - 4,
r + 2c < 108,
```

consider

```text
G(r,c) = K_r join (c K_2).
```

Write `n = r + 2c`. Every peripheral vertex has degree `r+1`, so

```text
delta(G) = r + 1
n + 12 <= 5 delta(G)  iff  c <= 2r - 4.
```

The graph is at least 4-connected, lies below the order-108 theorem range,
and has an induced claw. Its peripheral path-cover obstruction is also
symbolic: `c K_2` needs `c` paths, but a cycle through the universal `K_r`
separator can traverse at most `r` peripheral path components. Since `c>r`,
the graph is non-Hamiltonian. For example, `(r,c)=(7,9)` gives
`n=25` and `delta=8=ceil(37/5)`.

This is a genuine `G2` reachability result. It is not a target crossing.
Every maximum packing uses `r` of the `K_2` lobes and leaves only isolated
`K_2` lobes, so its uncovered graph has no four-vertex path.

## Why the natural leakage surgery has the wrong sign

Joining two peripheral `K_2` lobes by one edge creates a `P_4`, but it also
reduces their path-cover cost from two paths to one. A maximum packing values
that new lobe at four covered vertices instead of two and therefore absorbs
the `P_4`; the untouched `K_2` lobes remain outside. The construction changes
the intended invariant in the wrong direction.

The obstruction extends to the full universal-separator/disconnected-lobe
class. Let

```text
G = K_r join F,
```

where `F` is nonempty and has more than `r` connected lobes. Put
`m=|V(F)|` and define `d=delta(F)` exactly—the minimum of the lobe minimum
degrees. More than `r` lobes give the intended path-cover obstruction, while
each lobe has at least `d+1` vertices, hence

```text
m >= (r+1)(d+1).
```

Bondy's degree premise for the join gives

```text
m <= 4r + 5d - 12.
```

Combining them yields

```text
r(d-3) <= 4d-13.
```

For `r>=4`, this is impossible when `d>=3`, so every legal construction in
this class has `d<=2` and therefore `m<=4r-2`.

Now suppose a maximum packing by at most `r` vertex-disjoint peripheral paths
left a simple four-vertex path. It must use all `r` available paths; otherwise
the omitted path could be added. Every used path must contain at least four
vertices; otherwise replacing it with the omitted path would cover more.
The packing and omitted path would force

```text
m >= 4r + 4,
```

contradicting `m<=4r-2`. Thus this entire construction class cannot leave a
four-vertex path outside a maximum packing while satisfying the premise.

The packing statement is exactly the longest-cycle statement needed here.
Let `q_r(F)` be the maximum number of peripheral vertices coverable by at
most `r` pairwise vertex-disjoint nonempty paths. For `r>=4` and nonempty
`F`,

```text
circ(K_r join F) = r + q_r(F).
```

Indeed, if a cycle uses `1<=s<=r` hubs, deleting them leaves at most `s`
peripheral paths, so its length is at most `s+q_s(F)<=s+q_r(F)`, strictly
less than `r+q_r(F)` when `s<r`. If it uses no hub, breaking one cycle edge
gives a peripheral path, so its length is at most `q_r(F)`. Conversely,
stitch an optimal collection of at most `r` peripheral paths through distinct
universal hubs and insert all unused clique vertices consecutively into a
connecting segment. Hence every longest cycle uses all `r` hubs and its
peripheral vertices form a maximum `r`-path packing. The contradiction from
the omitted four-vertex path therefore rules out the required longest-cycle
complement, not merely a proxy statistic.

## Stop and next admissible coordinate

Fixed universal separators, endpoint cliques, disconnected lobes, and the
obvious multiport surgery are retired for this target. No honest
non-universal multiport parameterization with a proved leakage bound passed
`G3`, so the empirical-selector protocol requires a strict stop rather than a
dispatch.

Together with the
[`C4`-factor Hamiltonicity theorem](c4-factor-hamiltonicity-theorem.md), this
narrows the next admissible Bondy coordinate substantially: it must both break
the compatible-Euler factorization and avoid a universal separator whose
packing economics force every four-vertex lobe into a longest-cycle packing.
That is a design requirement for a future arm, not permission to evaluate a
new target.
