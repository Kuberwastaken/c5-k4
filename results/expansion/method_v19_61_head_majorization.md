# Method v0.19: WOWII 61 head-majorization extremal boundary

Date: **2026-08-13 UTC**

Outcome: **the proposed incident-edge extremal characterization of cumulative
Havel--Hakimi heads is false, first at order five.**  A five-vertex path has
degree sequence

```text
[2,2,2,1,1].
```

Its first two canonical eliminated heads sum to three, while two vertices of
the path are incident to all four edges.

Lean kernel-certifies both finite quantities and proves the corrected exact
functional:

```text
2 * cumulativeHeadSum(k,s) = cumulative degree sum removed in k steps
```

for every explicitly admissible canonical history.

This does not prove cumulative-head monotonicity under graphical weak
majorization and does not prove WOWII 61.

## Frozen scope

- New certificate only: `lean/GraphConjecture61HeadMajorization.lean`.
- New report only:
  `results/expansion/method_v19_61_head_majorization.md`.
- No existing file was edited.  No commit, push, release, issue, PR, or other
  public action was made.
- Every subprocess was capped at 60 seconds.

## Candidate tested

The proposed route was to characterize

```text
cumulativeHeadSum(k, degreeSequence(G))
```

as the maximum number of graph edges incident to a set of `k` vertices.  Such
an identity would have converted the remaining sequence theorem into a familiar
extremal graph functional.

Exact enumeration tested every labeled simple graph by increasing order and
every relevant `k`.  The identity holds through order four.  Its first failure
is the five-vertex path.

## First obstruction

For the path with edges

```text
01, 12, 23, 34,
```

the degree sequence is `[2,2,2,1,1]`.  Canonical Havel--Hakimi reduction begins

```text
[2,2,2,1,1] -> [1,1,1,1],
```

so the first two eliminated heads are `2` and `1`, with sum three.

But vertices `1` and `3` jointly touch every path edge:

```text
01 touches 1
12 touches 1
23 touches 3
34 touches 3.
```

Thus a two-vertex set is incident to four edges, strictly more than the
canonical head sum three.

Lean proves the canonical successor using `mergeSort_eq_self` and a kernel-
checked pairwise-order proof.  It represents the four path edges as a concrete
finite list, filters by incidence with vertices `1` and `3`, and kernel-checks
that all four remain.  The final theorem proves `3 < 4`.

No native evaluator, custom axiom, or unproved graph-library computation is
used.

## Stronger extremal repair also fails

A natural reaction is to minimize the maximum incident-edge count over all
graph realizations of the degree sequence.  Exact realization enumeration
also refutes that variant at order five:

```text
degree sequence [3,3,3,3,2]
k = 2
canonical cumulative head sum = 5
minimum, over realizations, of maximum two-vertex incidence = 6.
```

Therefore cumulative canonical heads are not captured by either the maximum
incident count in a fixed realization or the minimum of that maximum across
all realizations.

This second bounded result is reported as search evidence only; the Lean file
formalizes the first and simpler fixed-realization obstruction.

## Corrected functional

The certificate returns to the property canonical reduction actually controls.
For an admissible step with head `d`, it proves

```text
stepLoss = 2d.
```

It then defines complete admissible histories and proves by ordinary structural
induction

```text
2 * cumulativeHeadSum(k,s) = cumulativeStepLoss(k,s).
```

This is the exact corrected functional.  It is realization-independent and
depends only on the canonical degree-sequence trajectory.  Unlike the false
incident-edge proposal, it does not silently optimize over arbitrary vertex
sets that the Havel--Hakimi trajectory never selected.

## Why the extremal idea failed

Havel--Hakimi chooses a current maximum degree and constructs one admissible
canonical residual sequence.  It does not choose the `k` original vertices
maximizing jointly covered edges.

In the path obstruction, choosing an endpoint-independent pair of internal
vertices covers all four edges.  Canonical elimination spends its first head
of degree two and then sees only head one in the residual sequence.  Joint
coverage in the original graph can exploit edges distributed across two
vertices in a way the sequential residual maximum does not reproduce.

The discrepancy is structural, not an implementation detail or a choice of
tie-breaking among equal initial degrees.

## Remaining theorem

The desired statement remains the sequence-level implication

```text
graphical s and t
weak degree-prefix dominance s over t
------------------------------------------------
cumulativeHeadSum(k,t) <= cumulativeHeadSum(k,s)
```

for every canonical prefix `k`, with zero padding after a trajectory terminates.

The incident-edge extremal shortcut cannot prove it.  The surviving exact
functional rewrites the goal as monotonicity of cumulative canonical degree-
sum removal, which is the same residual-gap theorem isolated earlier.

The next non-equivalent route should study Havel--Hakimi as an operator on
majorization lattices, possibly through a variational formula expressed solely
in degree-sequence prefixes.  Any formula involving arbitrary original-graph
vertex sets must account for the order-five path obstruction.

## Bounded evidence and claim limit

The earlier complete audit still reports no failure of cumulative-head
monotonicity itself among 105,582,418 graphical weak-majorization pairs through
order ten.  That evidence motivated testing an extremal characterization but
is not used by the Lean proof and is not promoted to a theorem.

The negative extremal result is exact and independent of the positive bounded
audit: the characterization fails even though the desired monotonicity may
still hold.

## Verification

From the pinned `formal-conjectures` checkout:

```bash
timeout 60s lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture61HeadMajorization.lean
```

Result: **PASS** in approximately seven seconds.  The source contains no
unfinished proof, custom axiom, native evaluator, or external oracle.

## Verdict

The first proposed extremal characterization is decisively false at order
five, and minimizing over realizations does not repair it.  Cumulative
Havel--Hakimi heads measure canonical sequential degree removal, not maximum
joint edge coverage by original vertices.  The exact corrected functional is
twice cumulative heads equals cumulative removed degree sum; proving its
majorization monotonicity remains the genuine problem.
