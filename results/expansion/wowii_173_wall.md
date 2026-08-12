# Why the diameter-two `L_s+b` common wall cannot be crossed

Audit date: **2026-08-12**. This closes the proposed search for a diameter-two
graph with `b(G) <= gamma_c(G)` as mathematically impossible. It also explains
the repeated exact equality of `C5[K_m]`, `T(n)`, and other dense
diameter-two graphs on WOWII 176 and 182--185.

## The wall is already a proved baseline

WOWII 173, immediately preceding this run of conjectures, is marked proved:

```text
L_s(G) + b(G) >= n(G) + 1
```

for every nontrivial connected graph. This is Theorem 4 of Ermelinda DeLaViña
and Bill Waller,
[*Spanning Trees with Many Leaves and Average Distance*](https://www.combinatorics.org/ojs/index.php/eljc/article/download/v15i1r33/pdf),
Electronic Journal of Combinatorics 15 (2008), #R33. Their proof constructs a
connected dominating set of order at most `b-1`; equivalently, using
`L_s=n-gamma_c`, `b(G) >= gamma_c(G)+1`.

Odd cycles show the theorem is sharp. The paper explicitly leaves the
characterization of equality as an open problem.

## Why five later conjectures coincide on diameter-two graphs

If `diam(G)=2`, then `G^2=K_n`. Consequently, under the standard readings
already fixed by the database gate:

- 176 has right side `n + dist_min(M^2) = n+1`;
- 182 has `Delta(B(G^2)) + diam(G) = (n-1)+2 = n+1`;
- 183 has `Delta(G^2) + 2 rad(G^2) = (n-1)+2 = n+1`;
- 184 has `Delta(G^2) + 2 dist_avg(B(G^2),V(G^2)) = n+1`;
- 185 has `Delta(G^2) + 2 dist_avg(G^2) = n+1`.

Thus all five reduce exactly to the proved 173 baseline. Searching the
diameter-two class for `b<=gamma_c` can never refute them.

This should not be described as reverse-engineering an unknown theorem. The
historical layout makes the relationship explicit: 173 is the proved baseline
and the following entries are machine-generated attempted strengthenings whose
correction terms happen to collapse back to the baseline on diameter-two
graphs.

## What the equality data is still good for

- It validates the source reading and invariant implementations.
- It identifies `C5[K_m]` and `T(n)` as members of the sharpness locus of a
  known theorem.
- It points to the paper's stated open problem: characterize equality in
  `L_s+b>=n+1`.
- It prunes an entire search lane before expensive ILP work.

To hunt 176 or 182--185, one must leave diameter two and make the entry's
square-graph correction exceed the 173 baseline while keeping `L_s+b` near
equality. That is a different search problem; the common-wall attack itself is
closed.

## Independent computational audit

[`scripts/verify_wowii_173_wall.py`](../../scripts/verify_wowii_173_wall.py)
exhaustively recomputes `b` and `gamma_c` on all connected Graph Atlas graphs
of orders 2 through 7, then independently builds graph squares and checks the
diameter-two reductions in exact arithmetic. It uses no ILP and no floating
point comparisons. The audit is a consistency check, not the proof; the proof
is the cited 2008 theorem.
