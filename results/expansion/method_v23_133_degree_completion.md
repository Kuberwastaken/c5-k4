# Method v0.23: WOWII 133 degree-four completion boundary

Date: **2026-08-13 UTC**

Outcome: **the smallest genuine degree-completion lemma does not force a
positive parent--target contact.  It proves the opposite.**  In a four-regular
graph, each second parent already has four known neighbors:

```text
one first-choice vertex + three third-choice vertices.
```

Those vertices exhaust its neighborhood.  Any additional early target contact
is impossible.  A multiplicity-three blocked third vertex is likewise
saturated by its three owning parents and blocker target.

Therefore four-regular degree completion reinforces the empty parent--target
relation used by the v0.22 colored incidence counterprofile.  It cannot be the
missing contradiction.

This is a genuine `SimpleGraph` theorem, not a scalar incidence assumption.  It
does not construct a complete graph realizing the entire colored profile and
does not prove or disprove WOWII 133.

## Frozen scope

- New certificate only: `lean/GraphConjecture133DegreeCompletion.lean`.
- New report only:
  `results/expansion/method_v23_133_degree_completion.md`.
- Parent evidence:
  `lean/GraphConjecture133ThirdLayerCapacity.lean`,
  `lean/GraphConjecture133SharedThirdBlockers.lean`, and
  `lean/GraphConjecture133ColoredOwnership.lean`.
- No existing file was edited.  No commit, push, release, issue, PR, or other
  public action was made.
- Every subprocess was capped at 60 seconds.

## Generic neighborhood exhaustion

The certificate proves the graph-level theorem:

```text
G is 4-regular
a,b,c,d are pairwise distinct
v is adjacent to a,b,c,d
--------------------------------
neighborFinset(v) = {a,b,c,d}.
```

The proof is exact finite-set cardinality reasoning.  The four known vertices
form a subset of the neighbor set.  Pairwise distinctness gives their set card
four; regularity gives the neighbor set card four.  The subset is therefore an
equality.

The companion theorem excludes every fifth candidate `x` distinct from all
four known neighbors:

```text
not G.Adj v x.
```

No triangle-free, C4-free, connectedness, or metric premise is required.

## Second-parent completion

Within one first-choice branch, a second parent `p` has:

```text
p -- first
p -- z1
p -- z2
p -- z3.
```

The earlier graph modules prove that a four-regular parent has exactly three
third choices and that the relevant choices are distinct in the C4-free
configuration.  Once these four explicit neighbors are supplied, the new Lean
theorem gives

```text
neighborFinset(p) = {first,z1,z2,z3}.
```

Consequently, every early target distinct from those vertices satisfies

```text
p not adjacent target.
```

This non-incidence is now a direct consequence of degree completion, stronger
than the v0.20 triangle-free blocker-specific prohibition.

## Triple-blocker completion

A blocked third vertex of multiplicity three has exactly the four known
neighbors

```text
p1,p2,p3,target.
```

Under their explicit pairwise distinctness and adjacencies, Lean proves

```text
neighborFinset(z) = {p1,p2,p3,target}.
```

Thus the saturation statement used informally in v0.20 and v0.21 is now a
kernel-checked graph theorem.  Such a vertex has no unused edge through which a
new degree-completion contact could be forced.

## Why positive-contact forcing fails

The v0.22 incidence model deliberately set all parent--target contacts to
false.  One possible next move was to argue that four-regularity requires some
of those missing contacts in order to complete degrees.

The new theorem refutes that move at the local graph level:

- each second parent is already degree-saturated;
- each multiplicity-three blocker is already degree-saturated;
- an extra contact at either endpoint would violate four-regularity.

So degree completion does not merely permit the empty-contact choice; wherever
the four listed neighbors are genuine and distinct, it forces that choice.

This is an exact negative result about a proposed proof strategy, not a graph
counterexample to the conjecture.

## What remains unmodeled

The certificate does not assert that the entire 27-incidence colored profile
embeds in one connected triangle-free C4-free four-regular graph with the
required geodesic distances.  A complete realization must still satisfy:

1. compatibility among all nine saturated parent neighborhoods;
2. compatibility among the nine saturated triple-blocker neighborhoods;
3. first-choice and geodesic vertex degrees;
4. global simplicity, triangle-freeness, C4-freeness, connectedness, and metric
   placement;
5. equality constraints when vertices from different colored roles coincide.

The new result isolates where a contradiction can still arise: not from adding
an optional parent--target edge, but from incompatibility among the already
forced saturated neighborhoods or from the global metric structure.

## Next graph theorem

The most focused next target is a compatibility theorem for two saturated
parents or two saturated triple blockers.  For example, if their known
neighborhoods overlap in a forbidden pattern, C4-freeness may force equality or
disjointness that the modular v0.22 ownership design violates.

A useful finite formulation would retain two parent slots, their first-choice
colors, and their three owned third vertices, then classify the allowable
intersection sizes under C4-freeness.  Same-branch intersections are already
zero; the missing constraint concerns parents from different branches whose
third sets overlap through the triple-owned vertices.

## Genuine graph facts versus abstract data

Genuine graph theorems in this rung:

- neighbor-set exhaustion from four-regularity;
- no fifth adjacency after four distinct known neighbors;
- parent saturation;
- multiplicity-three blocker saturation.

Still abstract or conditional:

- the modular ownership assignment from v0.22;
- simultaneous realization of all local neighborhoods;
- target assignments and metric labels;
- pairwise distinctness across every local specialization, supplied explicitly
  rather than derived globally.

The report therefore does not call the v0.22 object a graph-level countermodel.
It says only that the first genuine completion lemma points in the same
non-incidence direction.

## Verification

From the pinned `formal-conjectures` checkout:

```bash
timeout 60s lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture133DegreeCompletion.lean
```

Result: **PASS** in approximately seven seconds.  The source contains no
unfinished proof, custom axiom, native evaluator, or external oracle.

## Verdict

The degree-completion route to a forced positive contact is closed.  Every
second parent and every blocked triple-owned third vertex is locally saturated,
so extra parent--target contacts are impossible.  Any elimination of the
colored `(0,0,9)` profile must come from cross-neighborhood compatibility or
global metric constraints, not unused degree capacity.
