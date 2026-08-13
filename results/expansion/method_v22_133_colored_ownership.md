# Method v0.22: WOWII 133 colored ownership counterprofile

Date: **2026-08-13 UTC**

Outcome: **the smallest branch-colored incidence model still realizes the
fully collapsed aggregate profile while satisfying target capacities and the
v0.20 parent--target non-incidence rule.**  Therefore branch labels plus that
non-incidence rule do not eliminate the `(0,0,9)` profile.

This is an exact finite incidence countermodel to the proposed proof layer.  It
is not a simple graph, not a counterexample to WOWII 133, and not evidence that
all omitted graph constraints can be realized simultaneously.

## Frozen scope

- New certificate only: `lean/GraphConjecture133ColoredOwnership.lean`.
- New report only:
  `results/expansion/method_v22_133_colored_ownership.md`.
- Parent inputs:
  `lean/GraphConjecture133SharedThirdBlockers.lean` and
  `lean/GraphConjecture133MultiplicityCharge.lean`.
- No existing file was edited.  No commit, push, release, issue, PR, or other
  public action was made.
- Every subprocess was capped at 60 seconds.

## Smallest colored model

The finite types are deliberately minimal:

```text
3 branches
3 parent slots per branch
9 distinct third vertices
5 early targets.
```

Each third vertex `z` is owned in every branch by parent slot `z mod 3`.
Consequently:

- every third vertex has exactly one parent in each branch;
- every colored parent owns exactly three third vertices;
- every branch carries nine incidences;
- the three branches carry all 27 incidences.

Lean proves each statement over the explicit finite types.  Nine vertices are
minimal because multiplicity is at most three and `27 <= 3 * distinct` forces
`distinct >= 9`.

Thus this is the smallest possible realization of the aggregate `(0,0,9)`
profile even after branch ownership is retained.

## Blocker targets and capacities

The nine third vertices are assigned cyclically to five targets.  Their loads
are

```text
2,2,2,2,1.
```

The target-capacity vector is

```text
3,2,2,2,2,
```

matching the earlier endpoint/interior outside-slot calculation.  Lean proves
every target load is within capacity and that exactly nine of the eleven total
slots are used.

This assignment is not optimized to create a contradiction; it demonstrates
that target colors and capacities alone leave slack.

## Parent--target non-incidence

The v0.20 graph theorem says that when a shared third vertex is blocked by a
target, none of its owning second parents may contact that target.

The colored incidence model takes the parent--target contact relation to be
empty.  Hence for every third vertex, every branch, and its unique owning
parent,

```text
parent does not contact blockerTarget(third).
```

Lean proves this universally.  The complete theorem
`colored_ownership_counterprofile` packages simultaneously:

1. unique parent ownership in every branch;
2. three third incidences per colored parent;
3. all blocker target capacities;
4. blocker/owning-parent non-incidence.

All four constraints coexist in the smallest nine-vertex profile.

## Genuine graph constraints versus scalar assumptions

The source constraints have different status and the certificate keeps that
distinction explicit.

Genuine graph-derived constraints already proved in earlier Lean files:

- one parent per branch for a shared third vertex;
- same-parent third choices are disjoint;
- a blocker target cannot contact any owning parent;
- multiplicity is at most three because there are three branches;
- target outside-neighbor capacities are three or two.

Abstract incidence/scalar choices in this new model:

- ownership is assigned by modular arithmetic rather than graph adjacency;
- blocker targets are assigned cyclically;
- the parent--target contact relation is chosen empty;
- no adjacency is supplied among first choices, second parents, third vertices,
  geodesic vertices, or unused fourth neighbors;
- triangle-freeness, C4-freeness, four-regularity, connectivity, and metric
  distances are not modeled as graph predicates here.

Accordingly, the model refutes only the claim that the retained colored
ownership, capacity, and non-incidence data already contradict `(0,0,9)`.

## What constraint is still missing

The empty parent--target relation makes the currently formalized non-incidence
rule cost-free.  A graph-level contradiction must force some positive incidence
elsewhere.  Candidate sources are:

1. four-regular degree completion for the nine second parents;
2. connectivity or distance constraints requiring their remaining edges to
   land in the early-target/branch system;
3. C4-free restrictions between different saturated third vertices sharing
   parent-slot patterns;
4. adjacency requirements for the unused neighbor of multiplicity-two
   vertices in the other six aggregate profiles.

The counterprofile therefore identifies the next useful theorem shape: a
positive lower bound on parent--target or cross-owner contacts forced by degree
completion.  Additional prohibitions alone cannot eliminate a model that sets
all optional contacts to false.

## Verification

From the pinned `formal-conjectures` checkout:

```bash
timeout 60s lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture133ColoredOwnership.lean
```

Result: **PASS** in approximately eight seconds.  The source contains no
unfinished proof, custom axiom, native evaluator, or external oracle.  All
finite checks use kernel reduction through `decide`.

## Verdict

The smallest colored ownership model exposes rather than eliminates the
aggregate counterprofile.  Nine triple-owned blockers can be balanced evenly
over all parents and targets while satisfying every retained non-incidence
rule.  The next graph theorem must force a positive contact through degree or
metric completion; more scalar capacity accounting or optional non-incidence
constraints will not suffice.
