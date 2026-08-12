# WoW I source-recovery sweep — numeric ids below 450

## Method and progress

This lane revisits every below-450 row reported with a `SKIP_OCR` component in
`results/expansion/wow1_part1.md`.  The source is the canonical July 2004
*Written on the Wall* scan.  `pdf-inspector --detect` classified the 216-page
PDF as text-based, but its embedded font mapping produces unusable extracted
text; therefore every relevant statement is read from a rasterized image of
the original page and not reconstructed from the damaged transcription.

Recovered statements are evaluated against the complete HANDOFF arsenal.  Any
apparent violation must pass the identical-reading DB-sanity gate (all connected
nonempty Graph Atlas graphs through order 7 and all named calibration graphs),
independent recomputation, and a novelty search.  Exact arithmetic is used for
combinatorial and distance quantities, spectral comparisons have a `1e-6`
guard, and any ILP solve is capped at 60 seconds.  Entries remain `SKIP_OCR`
when the scan itself does not define a historical program-dependent invariant.

Progress is committed and pushed one recovered row at a time.

### wow-86 — SKIP_SOURCE

> variance of coordinates of a maximal clique maximum of Even.

The primary scan (printed p.43, PDF p.43) confirms that the comparison operator
is absent in the source itself, between “clique” and “maximum”.  This is not an
OCR loss: the July 2004 document preserves a damaged original entry.  Supplying
`<=` would be editorial conjecture rather than source recovery.  The row remains
unevaluable.

### wow-96(2) — NOT_AN_ENTRY

The scan (printed p.45) shows `William Staton. April 88.` is the attribution and
date completing conjecture 97, which begins immediately above it on the same
page.  The OCR parser incorrectly created a second row numbered 96.  There is no
statement to evaluate.

### wow-123 — DB_REJECTED

> size/2 <= the rank of the gravity matrix.

The scan (printed p.52) recovers the operator exactly; `size` is the number of
edges in WoW I.  Thus the literal source statement is not an OCR problem.  It
fails the mandatory database gate already on `K7`: `|E|/2 = 21/2 > 7`, while
the gravity matrix has rank 7.  The carrier similarly gives `55 > 20`.
Consequently this is a bad-as-printed/database-inconsistent entry, not a new
counterexample.

### wow-133 — HOLD

> Sum of reciprocals of components of twister <= harmonic.

Printed p.51 defines the twister component of a vertex lying on a cycle as the
length of its shortest containing cycle; printed p.65 confirms the operator.
Every arsenal graph is vertex-transitive and every vertex lies on a triangle,
so the left side is `n/3`.  For a regular graph the harmonic index is
`|E|/d = n/2`; hence `n/3 <= n/2` throughout.  No candidate violation arises.

### wow-135 — HOLD

> chromatic number / clique <= independence of D2.

Printed p.51 defines `D2(G)` on the same vertex set, with adjacency exactly at
distance 2 in `G`; printed p.65 confirms the bound.  Direct evaluation against
every arsenal graph holds.  For the carrier, `D2` is the complement's five-part
distance-two graph and has independence number 12, whereas `chi/omega=10/8`.
For each diameter-two triangular graph `T(q)`, `D2` is its complement and the
left side is at most the obvious clique-sized independent set.  No violation
approaches a numerical guard.

### wow-155 — SKIP_DEFINITION

> mean of autocoordinates of Maxine of D2 <= the matching number.

The scan (printed p.67) confirms the exact statement and operator, and p.51
defines both Maxine and `D2`.  It never defines **autocoordinates**, however;
neither the document nor targeted searches recover a mathematical definition.
Moreover Maxine explicitly depends on vertex tie-breaking.  Evaluating a guessed
coordinate convention would violate the all-readings rule, so this stays skipped.

### wow-156 — SKIP_DEFINITION

> mean of autocoordinates of Maxine of D2 <= the chromatic number.

Printed p.67 confirms this companion to 155.  The source defines Maxine and
`D2` but not autocoordinates, so the same representation-dependent definition
gap prevents a faithful evaluation.  The OCR's trailing `x * x` is not present
in the source and was only page ornament/noise.

### wow-161 — SKIP_DEFINITION

> The maximum of autocoordinates of Maxine of the complement of G <= the
> average transmission of the distance matrix.

The full inequality is clean on printed p.68.  It repairs the truncated OCR but
not the absent definition of autocoordinates or Maxine's tie-order dependence.
No faithful numerical reading can be assigned from the source.

### wow-175 — SKIP_DEFINITION

> mean of autocoordinates of Maxine of D2 <= n / average distance.

Printed p.69 supplies the missing right side and confirms that the heading for
connected graphs begins only at 176, so 175 has the previous unrestricted
context.  Autocoordinates remain undefined in the primary document and Maxine
is tie-order dependent; the recovered formula therefore cannot be evaluated
without inventing the left-hand invariant.

### wow-181 — SKIP_DEFINITION

> The range of resolution of Maxine <= maximum of E.

Printed p.69 confirms this is inside the connected-graph section with
`sum(D) <= sum(E)`.  The source defines Maxine but nowhere defines its
“resolution”; it is also explicitly tie-order dependent.  The section condition
does select `T(7..9)` and the carrier complement, but no recoverable left-hand
quantity exists to test on them.

### wow-182 — SKIP_DEFINITION

> The mean of autocoordinates of Maxine of the complement of G <=
> size / average distance.

Printed p.69 confirms the complete inequality and inherited connected
`sum(D) <= sum(E)` condition.  The source does not define autocoordinates; no
faithful value can be assigned to the left side, so it remains skipped.

### wow-183 — SKIP_DEFINITION

> The length of autocoordinates of Maxine of the complement of G <= the
> mean transmission of the distance matrix.

Printed p.69 confirms the complete statement and inherited connected
`sum(D) <= sum(E)` condition.  Autocoordinates are never defined in the source;
“length” cannot repair that missing base object, so no evaluation is possible.

### wow-184 — SKIP_DEFINITION

> The maximum of autocoordinates of Maxine of the complement of G <=
> n - the matching number.

Printed p.69 confirms the full statement under connected `sum(D) <= sum(E)`.
The historical program invariant autocoordinates is absent from the glossary
and Maxine is tie-order dependent, so the source is still insufficient for a
faithful test.

### wow-204 — SKIP_DEFINITION

> The length of autocoordinates of Maxine of D2 <= the mean transmission
> of the distance matrix.

Printed p.71 recovers the full statement under connected `sum(E) <= sum(D)`.
Autocoordinates are absent from the source glossary, so the left-hand vector and
therefore its length cannot be evaluated faithfully.

### wow-212 — RETRO_REFUTED

> Inverse coordinates of Maxine <= n/2.

Printed p.72 confirms the inequality and the inherited triangle-free hypothesis.
The row itself gives `P5` as a counterexample for a suitable vertex order and asks
for a representation-independent example.  This is a historically recorded
refutation, not a new target; Maxine's order dependence is explicit.

### wow-213 — DB_REJECTED

> size/2 <= Randic.

Printed p.73 confirms the operator and inherited triangle-free hypothesis; no
radical was lost.  With WoW `size=|E|`, the literal bound fails database graphs,
including `K3,3`: `|E|/2=9/2 > R=3`.  The carrier complement also fails
`40 > 10`.  It is therefore source-faithful but database-inconsistent.

### wow-228 — SKIP_DEFINITION

> mean of coordinates of resolution of Maxine <= size/2.

Printed p.74 confirms the exact statement under the regular-graph hypothesis.
The source does not define “resolution of Maxine”, and Maxine's tie choices are
representation dependent.  Recovery does not supply an evaluable invariant.

### wow-229 — SKIP_DEFINITION

> maximum of coordinates of resolution of Maxine <= the matching number.

Printed p.74 confirms the exact regular-graph statement.  “Resolution of Maxine”
remains undefined in the source, so its coordinate maximum cannot be tested
without inventing a historical program convention.

### wow-230 — SKIP_DEFINITION

> minimum of autocoordinates of resolution of Maxine of the complement
> of G <= n / independence.

Printed p.74 recovers the full regular-graph statement.  Both autocoordinates and
resolution of Maxine lack source definitions, so no faithful reading survives.

### wow-232 — DB_REJECTED

> size/2 <= n - independence.

Printed p.74 confirms the exact regular-graph statement.  Under the established
edge-count meaning of size, it fails the database gate on `K7`:
`|E|/2=21/2 > 6=n-alpha`.  The carrier also fails `55 > 18`.  No exponent
or radical was lost; the source itself is inconsistent with the test database.
