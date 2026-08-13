# Method v34: WOWII #59 deficient-column degree prefix

Date: 2026-08-13

Local certificate: `lean/GraphConjecture59DeficientColumnDegreePrefix.lean`

## Outcome

This checkpoint refines the v31 deficient-column DNF and converts the named
ambient degree bounds into an actual order-statistic coordinate of the full
graph's descending degree sequence.

## Six exact deficient-column patterns

Write the four unknown frame incidences of the deficient column endpoint `t`
in order `(u,c,v,p)`.  The conjunction

```text
t hits at least two of {u,v,p}
and t hits at least two of {u,c,v}
```

has exactly six disjoint Boolean realizations:

```text
0111, 1010, 1011, 1101, 1110, 1111.
```

Lean proves this exact classification in
`two_covers_iff_exact_six_patterns`.

Only `1010` realizes the minimum frame contribution: `t` sees both path
endpoints but misses the center and `p`.  Since `t` also sees the core
vertices `b,d` and the already forced vertex `q`, this is the only branch in
which the current data merely gives

```text
degree(t) >= 5.
```

Every other pattern supplies at least three frame neighbors and therefore
forces

```text
degree(t) >= 6.
```

This is certified by `degree_six_or_minimal_pattern`; it is not a numerical
inference from a mask.

## Ambient aligned-row degrees

The unique deficient aligned row `a` has its two surviving internal-core
neighbors and the four distinct outside neighbors `u,c,v,p`.  The other
aligned row `b` has all three internal-core neighbors and the same four
outside neighbors.  Lean packages the required nodup data and proves

```text
degree(a) >= 6,
degree(b) >= 7.
```

This closes the ambient-degree bookkeeping gap left explicit in v31.

## Actual descending prefix

The module defines `descendingThresholdCount G k` as the number of entries
at least `k` in the repository's actual `descendingDegreeSequence G`.
It proves from first principles that sorting preserves this count and that it
equals the cardinality of the corresponding high-degree vertex set.

Combining the named bounds from the current closure gives the exact threshold
prefix

```text
at least 2 degree entries >= 8,
at least 3 degree entries >= 7,
at least 5 degree entries >= 6,
at least 6 degree entries >= 5.
```

Equivalently, the first six sorted degrees dominate

```text
[8,8,7,6,6,5].
```

The two degree-eight entries are the saturated third row and `q`; the
degree-seven entry is the nondeficient aligned row; the next two degree-six
entries are the deficient aligned row and one nondeficient column; and `t`
supplies the sixth entry.

Outside the single minimal `1010` attachment pattern, `t` also has degree at
least six, so the stronger prefix is

```text
[8,8,7,6,6,6].
```

`forcedPrefix_and_sixth_degree_or_minimal` records precisely this dichotomy.
The theorem is deliberately parameterized by the named ambient bounds so it
composes without depending on the simultaneously developed v32 module.

## Residue verdict

This is a genuine ambient sorted-degree statement, but it still does not by
itself contradict residue three.  Lean reuses the existing fourteen-vertex
split graph and proves simultaneously that it satisfies a stronger version
of the threshold prefix and has Havel--Hakimi residue exactly three.

Thus the valid remaining profile is:

```text
minimal branch:    prefix [8,8,7,6,6,5] plus exact pattern 1010;
all other branches: prefix [8,8,7,6,6,6] plus one of five exact patterns.
```

Any contradiction must use the adjacency structure carried by those
patterns, the v33 exact eleven-vertex residue computation, or restrictions on
additional ambient vertices.  Scalar prefix dominance alone is formally
closed as a route.

## Lean audit

The v31 opposite-column dependency was rebuilt in 7.71 seconds.  The new
module passed under the pinned Lean 4.27 toolchain, warnings as errors, and
the required 60-second process cap:

```text
ELAN_TOOLCHAIN=leanprover/lean4:v4.27.0 \
LEAN_PATH=/tmp/c5k4-59-v32-prefix:/tmp/c5k4-59-v31-opposite:\
/tmp/c5k4-59-v30-audit.0hp4f0:/tmp/c5k4-59-v30-synthesis:\
/tmp/c5k4-59-v29-audit.BoHebr:/tmp/c5k4-59-v27-audit.Q5a01Z:/tmp \
timeout 60s lake env lean \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture59DeficientColumnDegreePrefix.lean
```

Result: exit code 0 in 14.02 seconds.  The source contains no proof holes,
native evaluation shortcut, custom axioms, or diagnostic print commands.

WOWII #59 is already externally disproved.  This is theorem extraction, not
a new counterexample or release candidate.
