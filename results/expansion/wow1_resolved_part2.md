# WoW I resolved/annotated sweep — ids >= 450

This durable lane covers exactly the 56 records in `corpora/graffiti_wow.json`
whose numeric WoW identifier is at least 450 and whose status does not begin
with `open` or `unannotated`.  It asks a deliberately retrospective question:
which already-proved, already-refuted, or otherwise annotated claims are also
met, made sharp, or refuted by the campaign arsenal?

Every usable statement is read with its inherited section hypothesis and is
tested on `C5[K_m]` for `m in {2,3,4,5,6,8}`, `C7[K3]`, `C9[K3]`,
`T(n)=L(K_n)` for `n in {7,8,9}`, and the complement of `C5[K4]`, with
named comparison graphs where applicable.  A candidate is not called a
retro-kill unless it passes the four handoff gates: the applicable connected
Atlas graphs through order 7 plus named graphs, every plausible reading,
independent recomputation, and a literature/novelty check.  Spectral tests use
a `1e-6` guard.  No ILP run may exceed 60 seconds.  OCR damage and hypotheses
that exclude the entire arsenal are recorded rather than repaired by guesswork.

Verdict labels distinguish `HOLD`, `TIGHT`, `RETRO_KILL`, `NOT_APPLICABLE`,
`SKIP_OCR`, and `DB_REJECTED` (a literal reading already fails Graffiti-era
sanity graphs and therefore cannot support a mathematical claim).

## wow-577 — NOT_APPLICABLE

**Status:** proved (WoW annotation). The primary statement is restricted to
trees. No campaign-arsenal member is a tree, so this lane supplies no
admissible witness. The OCR phrase `inverse Dual Degree` is not guessed at.

## wow-584 — NOT_APPLICABLE

**Status:** proved (Aouchiche--Hansen survey). The recovered statement,
`lambda_max(L) <= 2 + alpha`, is explicitly for trees. Every arsenal graph
contains cycles, so none is applicable. (The OCR `<` represents the source's
non-strict comparison convention.)

## wow-596 — SKIP_OCR

**Status:** refuted (WoW annotation). The normalized row has lost its
comparison sign: `radius maximal frequency of mid-Degree`. The surrounding
definition describes a derived Havel--Hakimi sequence, but the predicate is
still absent. No reading is invented and no arsenal verdict is claimed.

## wow-599 — HOLD

**Status:** refuted (WoW annotation). The inherited 595--605 triangle-free
hypothesis leaves only `complement(C5[K4])` in the arsenal. It has
`n-alpha=12`, while `chi(G)+chi(bar G)=3+10=13`, so the source bound
holds. Exact colorings supply the two values independently; no retro-kill.

## wow-601 — HOLD

**Status:** refuted (WoW annotation). Under the same triangle-free section
hypothesis, `complement(C5[K4])` gives `chi=3` and average distance `30/19`,
so `3 <= 20/(30/19)=38/3`. Exact distance counts and an independent shortest-
path calculation agree. No candidate reaches a gate.

## wow-636 — HOLD

**Status:** proved (Aouchiche--Hansen survey). In the 634--654 section the
hypothesis is `chi(bar G)=n-matching`. The complement carrier satisfies it:
`chi(C5[K4])=10=20-10`. Its `|E|/alpha=80/8=10`, below
`lambda_max(L)=10+2sqrt(5)=14.47213595...`; the guarded numerical spectrum
and complement closed form agree.

## wow-637 — HOLD

**Status:** refuted (WoW annotation). On the only arsenal member meeting the
634--654 hypothesis, `complement(C5[K4])`, `|E|/alpha=10`, while the sum of
positive adjacency eigenvalues is `8+2(sqrt(5)-1)=10+2sqrt(5)`.
Direct diagonalization agrees beyond the `1e-6` guard. It is not a retro-witness.

## wow-648 — NOT_APPLICABLE

**Status:** refuted (WoW annotation). This is existential: it predicts graphs
in the 634--654 class with `chi(bar G)/alpha >= average_distance`, rather than
a universal bound that an arsenal graph could falsify. The eligible complement
carrier is not a witness to the existential claim (`10/8 < 30/19`); that fact
is not a disproof.

## wow-649 — NOT_APPLICABLE

**Status:** refuted (Aouchiche--Hansen survey). This is likewise an existential
prediction, now comparing `chi(bar G)/alpha` to the range of positive
eigenvalues. Failure of an individual arsenal graph to witness existence cannot
refute it, and no new mathematical verdict is assigned.

## wow-706 — HOLD

**Status:** proved (Aouchiche--Hansen survey). Every arsenal member satisfies
`matching <= sum(positive adjacency eigenvalues)`. For the carrier the values
are `10` and `13+4sqrt(5)`; for its complement they are `10` and
`10+2sqrt(5)`. Direct maximum matchings and guarded diagonalization agree.

## wow-711 — HOLD

**Status:** refuted (Aouchiche--Hansen survey). Every arsenal graph is regular,
so vertex deficiency is constant and its range is zero. The adjacency spectral
range is strictly positive on every member, hence the bound holds under both
range conventions. No candidate gate is triggered.

## wow-713 — HOLD

**Status:** proved (Aouchiche--Hansen survey). Direct guarded spectra give a
nonpositive-eigenvalue mean whose negation is well below the Randić index on
every arsenal member. Independently, regularity gives `R=|E|/d=n/2` exactly;
the spectral side never approaches that value within `1e-6`.

## wow-715 — HOLD

**Status:** refuted (Aouchiche--Hansen survey). Reading `scope` as spectral
range, all arsenal members satisfy the comparison. On the carrier the
nonpositive range is below mean high degree `11`; on the complement it is
`2sqrt(5)+2 < 8`. Guarded eigenspectra reproduce the closed-form checks.

## wow-720 — NOT_APPLICABLE

**Status:** proved (Aouchiche--Hansen survey). The statement is restricted to
heliotropic plants (equality in Cvetkovic's nonnegative-eigenvalue independence
bound). None of the arsenal graphs meets that equality: the carrier has
`alpha=2` versus three nonnegative eigenvalues, and the complement has `8`
versus `18`; triangular graphs also fail.

## wow-721 — NOT_APPLICABLE

**Status:** refuted (WoW annotation). The antecedent is that `G` is a perfect
plant, as defined in the preceding discussion. No arsenal member satisfies that
special equality condition, so the campaign cannot supply a retro-counterexample.

## wow-722 — SKIP_OCR

**Status:** refuted (Aouchiche--Hansen survey). The row depends on the
`frequency of mode` of a largest-eigenvalue eigenvector, with normalization,
choice, and tie behavior absent from the isolated record. It is a Graffiti
try-out rather than a well-defined invariant; no reading is guessed.

## wow-723 — DB_REJECTED

**Status:** refuted (Aouchiche--Hansen survey). The literal reading is
`n_nonnegative(A) - sum_{lambda_i(L)>0} 1/lambda_i(L) <= alpha`. It appears to
fail on `T(7)` and the complement carrier, but also fails on 27 nontrivial
connected Atlas graphs through order 7. An independent eigensolver reproduces
those failures, so this reading cannot yield a campaign retro-kill.

## wow-724 — RETRO_KILL (new connected infinite family)

**Status:** already refuted (WoW annotation). The primary scan, p.109, gives

`n_nonnegative(A) - lambda_max(A) + smallest_nonnegative(A) <= alpha`.

It says Brewster, Dinneen, and Faber found only the disconnected graph `2C5`
in their search. Let `H_m = complement(C5[K_m])`. For every `m >= 1`,

* `alpha(H_m)=2m` and `lambda_max(H_m)=2m`;
* the spectrum has three positive eigenvalues, `5m-5` zero eigenvalues, and
  two negative eigenvalues, hence `n_nonnegative=5m-2`;
* the smallest nonnegative eigenvalue is zero.

Thus the left side is `3m-2`, exceeding `2m` exactly when `m >= 3`. In
particular the connected, regular, triangle-free carrier complement `H_4`
gives `18-8+0=10 > 8`. Direct NumPy diagonalization independently reproduces
the spectrum and value. The mandatory gate found zero violations of the
non-strict statement among all connected Atlas graphs through order 7 and all
named calibration graphs (complete graphs and Petersen are ties). Targeted
searches recovered the historical `2C5` note but no publication of this
connected infinite family. This is a provisionally novel retro-family, not a
new disproof of an open conjecture.

## wow-725 — SKIP_OCR

**Status:** refuted (Aouchiche--Hansen survey). The statement uses reciprocals
of coordinates of `Maxine`, an eigenvector try-out whose scaling, zero
coordinates, and basis choice are not specified. No invariant reading can be
certified from the record.

## wow-728 — NOT_APPLICABLE

**Status:** proved (WoW annotation). This concerns Euclidean distance matrices
of distinct planar point configurations, not graph-distance matrices. The
campaign arsenal supplies no planar configuration realizing the required
object, so graph substitution would change the statement.

## wow-729 — NOT_APPLICABLE

**Status:** annotated refuted in corpus metadata, though the quoted inequality
is the standard nonnegative-matrix row-sum bound. Its objects are planar point
configurations and their Euclidean distance matrices. No arsenal graph is an
admissible instance; the metadata tension is recorded without inventing one.

## wow-732 — NOT_APPLICABLE

**Status:** refuted (WoW annotation). The antecedent requires the visibility
graph of a polygon together with the polygon's Euclidean distance matrix.
Arsenal graphs have no supplied polygon realization, and the eigenvector
component count is explicitly a nonunique try-out.

## wow-739 — NOT_APPLICABLE

**Status:** proved (WoW annotation). This is a Euclidean triangle area identity,
not a graph conjecture. No campaign object supplies the required angle
bisectors, side distances, or perimeter.

## wow-747 — HOLD

**Status:** proved (WoW annotation). Reading the source glyph as the order `b`
of a largest induced bipartite subgraph, the bound is
`average_distance <= b/2`. The carrier gives `27/19 <= 4/2`, using the
certified value `b=4`; exact unordered distance counts independently agree.
The remainder of the arsenal also holds.

## wow-748 — HOLD

**Status:** proved (WoW annotation). Every campaign graph is Hamiltonian, so
the minimum, over starting vertices, of longest-path length is `n-1`.
Consequently `chi(G) <= 1+p=n` holds immediately. Explicit Hamiltonian cycles
and exact colorings provide independent checks.

## wow-750 — HOLD

**Status:** refuted (WoW annotation). On each vertex-transitive diameter-two
arsenal graph, the odd-distance count is its degree while horizontal edges
within the distance layers make `max d(v)-min h(v)` no larger than `alpha`.
For the carrier, `d=11` and `h=67`, so the proposed lower bound is negative.
Direct layer construction agrees.

## wow-751 — HOLD

**Status:** annotated refuted despite the accompanying text giving a proof.
Every regular arsenal graph has zero cut vertices, reducing the inequality to
`alpha <= n`. NetworkX articulation points and the explicit connectivity of
each family independently give `c=0`.

## wow-758 — SKIP_OCR

**Status:** refuted (WoW annotation). The record defines a slowest expanding
sequence and expansion coefficients but truncates immediately after
`Conjecture: the smallest expanding coefficient of a connected graph`.
Neither comparison nor right-hand side survives, so no predicate is guessed.

## wow-764 — SKIP_OCR

**Status:** refuted (WoW annotation). The claim depends on zeros at a vertex
across a chosen complete eigenbasis. Repeated eigenspaces make that basis
nonunique, as the source itself notes, and the OCR alternates `m(v)` and
`p(v)`. No invariant reading survives.

## wow-771 — HOLD

**Status:** refuted (WoW annotation). The hypothesis is cubic. No primary
carrier-family graph is cubic; the named Petersen calibration graph is, and
gives `alpha=4 = n_nonnegative-diameter=6-2`. A guarded eigenspectrum and
exact independent-set search agree.

## wow-774 — HOLD

**Status:** proved (Aouchiche--Hansen survey). For the applicable cubic named
graph Petersen, only its eigenvalue `3` is strictly greater than one, while
`alpha=4`. No primary arsenal family member is cubic, and the calibration
case holds with wide slack.

## wow-776 — HOLD

**Status:** refuted (Aouchiche--Hansen survey). On the applicable cubic
calibration graph Petersen, the positive adjacency eigenvalue sum is `8`, so
the bound reads `alpha=4 >= -1+8/2=3`. Exact spectrum and independent maximum
independent-set enumeration agree.

## wow-777 — SKIP_OCR

**Status:** refuted (WoW annotation). This record preserves definitions of
counter-independent sets and jets but truncates before a complete conjectured
comparison. The definitions are useful for #778; they do not themselves form a
falsifiable row.

## wow-778 — HOLD

**Status:** proved (WoW annotation). Exhaustive subset search gives jet number
`2` on every `C5[K_m]` and on the complement carrier, versus respectively
three positive eigenvalues. It gives jet numbers `3,3,4` on `T(7),T(8),T(9)`
versus `7,8,9`. A separate neighborhood-complement predicate reproduces each
jet, so `jet <= n_positive` holds throughout.

## wow-783 — NOT_APPLICABLE

**Status:** refuted (WoW annotation). This concerns arithmetic-progression
graphs on intervals of primes. None of the campaign graphs is supplied with
the required prime labeling, and testing an arbitrary isomorphic graph would
erase the number-theoretic hypothesis.

## wow-785 — NOT_APPLICABLE

**Status:** refuted (WoW annotation). The graph is specifically `AP[10,n]`
from #783; no arsenal member has that construction. The OCR also collapses the
Laplacian symbol and right side to `d <= -1+1`, so it is unusable independently.

## wow-790 — NOT_APPLICABLE

**Status:** refuted (WoW annotation). The claim is restricted to critical
Ramsey triangle-free graphs `R(3,a+1)`. Although the complement carrier is
regular and triangle-free, it is not certified as a largest critical Ramsey
graph of its independence order; no arsenal member meets the antecedent.

## wow-792 — HOLD

**Status:** proved (Aouchiche--Hansen survey). All arsenal graphs satisfy
`alpha(G) <= 1+lambda_max(bar G)`. The carrier gives `2 <= 9`; its complement
gives `8 <= 12`. Direct complement diagonalization and the closed-form
spectra agree beyond the `1e-6` guard.

## wow-800 — HOLD

**Status:** proved (Aouchiche--Hansen survey). The source says the inequality
is valid for all graphs: `alpha(G) <= 1+n_nonpositive(bar G)`. Guarded
complement spectra verify it throughout the arsenal; the carrier gives
`2 <= 18`, and its complement gives `8 <= 18`.

## wow-822 — NOT_APPLICABLE

**Status:** refuted (WoW annotation). This row introduces red/blue graphs for
an arbitrary graph property and states a class-level Ramseyan prediction. It
does not specify one fixed property and one universal numerical inequality
that a single arsenal graph could refute.

## wow-823 — NOT_APPLICABLE

**Status:** refuted (WoW annotation). The primary-page context says the red and
blue graphs here are taken with respect to a fixed chromatic number. The corpus
does not preserve that parameter, and substituting the later triangle-free
distance-two coloring makes C5 itself fail the database gate. No such
context-changing reading is claimed.
