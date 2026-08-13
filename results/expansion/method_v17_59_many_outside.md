# Method v0.17: WOWII 59 many dense outside rows

Date: 2026-08-13

## Scope

This pass replaces brute-force growth in the number of outside vertices with a
structural extremal-set lemma. WOWII 59 is already externally disproved; this
is proof extraction around the hypothetical low-residue corner, not a novelty
or held-out claim.

## The proposed common-incidence lemma is false

The first tempting statement was:

```text
four dense attachment rows on a three-vertex color class
must all share one core vertex.
```

This is false. Let the first three rows be the three two-subsets

```text
{0,1}, {0,2}, {1,2}
```

and repeat any one of them as the fourth row. Their four-way intersection is
empty.

This obstruction is not an artifact of graph realizability; it is already a
sharp counterexample at the incidence-family level.

## Exact finite guide

There are exactly four subsets of a fixed three-set having order at least two:
the three two-subsets and the full three-set. All `4^4=256` ordered quadruples
were checked under the candidate replacement:

```text
some two rows repeat,
or some three rows have nonempty common intersection.
```

There were zero counterexamples. The check completed in under 0.2 seconds and
was used only to select the theorem; the Lean proof is symbolic.

## Sharp four-row theorem

Let `A,B,C,D` be subsets of a three-set `U`, each of cardinality at least two.
Then exactly the following weak alternative is forced:

1. two of `A,B,C,D` are equal; or
2. one of the four triples has nonempty common intersection.

The proof begins with the v0.16 classification of `A,B,C`.

- If they share a vertex, the aligned-triple outcome already holds.
- Otherwise they are three pairwise-distinct two-subsets.
- If `D` has order three, it equals `U`, and the nonempty intersection of
  `A` and `B` gives an aligned triple with `D`.
- If `D` has order two and differs from all three earlier rows, then
  `{A,B,C,D}` would be four distinct members of `U.powersetCard 2`. But

```text
|U.powersetCard 2| = choose(3,2) = 3,
```

which is impossible.

This theorem is sharp: the rotating-complement counterexample with a repeated
row realizes the repetition branch without any four-way common attachment.

## Consequence for arbitrarily many outside vertices

Any family of at least four exchange-resistant outside rows contains a
four-row subfamily. On each core color side, that subfamily therefore has:

- a repeated colored attachment row; or
- three outside vertices aligned on one common core neighbor.

The alternatives may differ between the two color sides. The theorem does not
yet guarantee that the same triple aligns on both sides, nor that a full
two-sided attachment row repeats. Those synchronization questions are the
remaining graph-theoretic obstruction.

## Formal artifact

[`lean/GraphConjecture59ManyOutside.lean`](../../lean/GraphConjecture59ManyOutside.lean)
defines `RepeatedOrTripleAligned` and proves:

1. the generic four-subset theorem above;
2. its specialization to four dense attachment rows on either color side of a
   `3+3` bipartite core.

The contradiction in the final case is certified through Mathlib's exact
`powersetCard` cardinality theorem, not enumeration or native evaluation.

## Verification

After compiling the warning-clean v0.8-v0.16 dependencies into temporary
`.olean` files, the module was checked with

```text
LEAN_PATH=/tmp lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture59ManyOutside.lean
```

It completed in 6.3 seconds with no warnings or errors. The file contains no
`sorry`, `admit`, custom axiom, `native_decide`, or imported upstream
conjecture proof.

## Next structural bridge

The many-outside problem is now finite at the incidence-type level. On each
side, rows are drawn from four types, and every four rows force repetition or
triple alignment. The useful next theorem should synchronize the two sides:

1. encode a full dense row as a pair of four-valued side types;
2. use repeated/aligned side information to force either a repeated full row
   or a triple with controlled attachment incidence on both sides;
3. combine that synchronized pattern with the outside adjacency graph to
   produce `f>=5`, `b>=7`, or the residue-at-most-two potential observed in the
   exact one-, two-, and three-outside audits.

Seventeen outside vertices force repetition of a full two-sided row by the
ordinary pigeonhole principle because there are only `4*4=16` full row types;
stronger intersection structure should lower that threshold substantially.
The current theorem supplies the sidewise input but does not claim such a
synchronized threshold yet.

## Outcome

`SHARP_MANY_ROW_REPETITION_OR_ALIGNMENT_THEOREM`.

The naive four-way-common-neighbor conjecture is formally rejected by an exact
incidence counterexample. Its sharp replacement is proved: every four dense
rows repeat on that color side or contain an aligned triple.
