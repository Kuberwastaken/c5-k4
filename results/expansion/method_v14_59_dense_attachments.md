# Method v0.14: WOWII 59 dense attachment patterns

Date: 2026-08-13

## Scope

This pass analyzes the exchange-resistant regime left by v0.13 for an explicit
`3+3` bipartite six-core. WOWII 59 is already externally disproved; this is
structural proof extraction, not a novelty or held-out claim.

## Fixed finite pattern audit

Two six-vertex cores were evaluated:

1. `K3,3` on color classes `{0,1,2}` and `{3,4,5}`;
2. `K3,3` minus edge `(0,3)` on the same classes.

An outside vertex `6` was joined to every attachment pattern with two or three
neighbors in each color class. The scope is complete for this regime:

```text
core: K3,3 or K3,3-e
left attachment count: 2 or 3
right attachment count: 2 or 3
all labelled choices within each count
total rows: 32
```

Every row was evaluated exactly by descending subset enumeration for the
largest induced forest and by Havel--Hakimi reduction of its seven-vertex
degree sequence. The process completed in 0.4 seconds.

### Results

- All 16 `K3,3` attachment rows have `f=4` on the induced seven-vertex graph.
- Of the 16 `K3,3-e` rows, four `2+2` patterns have `f=5`; the other 12 have
  `f=4`.
- Every one of all 32 seven-vertex induced graphs has Havel--Hakimi residue
  exactly two.

The four forest-producing `K3,3-e` patterns are exactly those where the two
attachments on one side avoid one endpoint of the missing edge while the two
on the other side include the corresponding missing-edge endpoint in the
complementary orientation. Explicit five-vertex forest witnesses were found in
each case.

These are exact facts about the induced seven-vertex graphs. They do **not**
prove that a larger ambient graph has residue two: outside vertices alter the
whole degree sequence. The 28 `f=4` survivors also show that forest-five alone
cannot eliminate the dense regime.

## Formal classification

[`lean/GraphConjecture59DenseAttachments.lean`](../../lean/GraphConjecture59DenseAttachments.lean)
formalizes the complete count-level classification without relying on the
finite audit.

For an outside vertex `x`, fixed core coloring `c`, and color `k`, define

```text
A_k(x) = {y in S : x~y and c(y)=k}.
```

The file proves:

1. `A_k(x)` is contained in the corresponding core color class;
2. `A_0(x)` and `A_1(x)` partition the full attachment set by cardinality;
3. if each core color class has order three and exchange resistance gives
   `|A_k(x)|>=2`, then each count is exactly two or three;
4. the total attachment count determines the complete pattern:

```text
total 4  ->  2+2
total 5  ->  2+3 or 3+2
total 6  ->  3+3
```

and the total necessarily lies between four and six.

This formally closes the count classification requested after v0.13. The
remaining distinctions are positional: which vertices inside a side are the
nonattachments, especially relative to the missing edge of `K3,3-e`.

## Verification

After compiling the warning-clean v0.8-v0.13 dependencies into temporary
`.olean` files, the module was checked with

```text
LEAN_PATH=/tmp lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture59DenseAttachments.lean
```

It completed in 6.7 seconds with no warnings or errors. The file contains no
`sorry`, `admit`, custom axiom, `native_decide`, or imported upstream
conjecture proof.

## Interpretation

The finite audit gives two useful negatives:

- the full dense regime is not killed by a five-vertex forest argument;
- nevertheless, the entire one-outside-vertex extension continues to have
  residue two in every exact pattern.

That second signal suggests the remaining global issue is not local core
geometry but accumulation across multiple outside vertices. A universal proof
must control how several dense mixed-parity attachment rows interact in the
ambient Havel--Hakimi sequence.

The most promising next split is:

1. formalize the four positional `K3,3-e` patterns that immediately force a
   five-vertex forest;
2. for the 28 survivors, study pairs of outside vertices and show that either
   their attachment rows admit a larger bipartite exchange or their combined
   degree contribution preserves a residue-at-most-two potential.

## Outcome

`EXACT_DENSE_PATTERN_CLASSIFICATION`.

The count regime is fully formalized; four positional patterns are exactly
forest-excluded by computation; and all 32 one-vertex extensions have induced
residue two. Universal ambient residue exclusion remains open.
