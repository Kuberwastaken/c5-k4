# Graph Brain / CONJECTURING alpha upper-bound sweep

## Scope, sources, and protocol

This lane covers exactly the **139** author-posted upper bounds in
`corpora/graphbrain_open_alpha.json`.  The primary machine-readable source is
the Graph Brain Project's author-project GitHub issue #421, and invariant
semantics are taken from the accompanying
`math1um/objects-invariants-properties` Sage source.  The primary paper is
Bushaw–Larson–Van Cleemput et al., *Automated Conjecturing VII: The Graph Brain
Project & Big Mathematics* (arXiv:1801.01814v1).  The paper says the project had
520 stored graphs rather than claiming an exhaustive all-connected-through-10
database; its Figure 14 entries were additionally tested on all connected
graphs through order 10 and random graphs through order 100.  I therefore state
database coverage entry by entry and do not silently promote the paper's test
description.

For every source-faithful, defined expression I test the campaign arsenal and
useful extensions `C5[K_m]`, `C7[K_m]`, triangular graphs `T(q)=L(K_q)`, and
complete graphs when the formula exposes a threshold.  Any apparent violation
must pass the identical-reading DB-sanity gate on every connected nonempty
Graph Atlas graph through order 7 plus named calibration graphs, be independently
recomputed, and receive a status/novelty check.  Trigonometric functions use
radians.  A `1e-6` guard protects floating integer/floor/ceiling boundaries.
Every ILP solve is capped at 60 seconds.  An absent or irrecoverable invariant
definition is `SKIP_UNDEFINED`, never guessed.

## Frozen manifest

The exact lane manifest is:

`graphbrain-alpha-upper-001`, `graphbrain-alpha-upper-002`, `graphbrain-alpha-upper-003`, `graphbrain-alpha-upper-004`, `graphbrain-alpha-upper-005`, `graphbrain-alpha-upper-006`, `graphbrain-alpha-upper-007`, `graphbrain-alpha-upper-008`, `graphbrain-alpha-upper-009`, `graphbrain-alpha-upper-010`, `graphbrain-alpha-upper-011`, `graphbrain-alpha-upper-012`, `graphbrain-alpha-upper-013`, `graphbrain-alpha-upper-014`, `graphbrain-alpha-upper-015`, `graphbrain-alpha-upper-016`, `graphbrain-alpha-upper-017`, `graphbrain-alpha-upper-018`, `graphbrain-alpha-upper-019`, `graphbrain-alpha-upper-020`, `graphbrain-alpha-upper-021`, `graphbrain-alpha-upper-022`, `graphbrain-alpha-upper-023`, `graphbrain-alpha-upper-024`, `graphbrain-alpha-upper-025`, `graphbrain-alpha-upper-026`, `graphbrain-alpha-upper-027`, `graphbrain-alpha-upper-028`, `graphbrain-alpha-upper-029`, `graphbrain-alpha-upper-030`, `graphbrain-alpha-upper-031`, `graphbrain-alpha-upper-032`, `graphbrain-alpha-upper-033`, `graphbrain-alpha-upper-034`, `graphbrain-alpha-upper-035`, `graphbrain-alpha-upper-036`, `graphbrain-alpha-upper-037`, `graphbrain-alpha-upper-038`, `graphbrain-alpha-upper-039`, `graphbrain-alpha-upper-040`, `graphbrain-alpha-upper-041`, `graphbrain-alpha-upper-042`, `graphbrain-alpha-upper-043`, `graphbrain-alpha-upper-044`, `graphbrain-alpha-upper-045`, `graphbrain-alpha-upper-046`, `graphbrain-alpha-upper-047`, `graphbrain-alpha-upper-048`, `graphbrain-alpha-upper-049`, `graphbrain-alpha-upper-050`, `graphbrain-alpha-upper-051`, `graphbrain-alpha-upper-052`, `graphbrain-alpha-upper-053`, `graphbrain-alpha-upper-054`, `graphbrain-alpha-upper-055`, `graphbrain-alpha-upper-056`, `graphbrain-alpha-upper-057`, `graphbrain-alpha-upper-058`, `graphbrain-alpha-upper-059`, `graphbrain-alpha-upper-060`, `graphbrain-alpha-upper-061`, `graphbrain-alpha-upper-062`, `graphbrain-alpha-upper-063`, `graphbrain-alpha-upper-064`, `graphbrain-alpha-upper-065`, `graphbrain-alpha-upper-066`, `graphbrain-alpha-upper-067`, `graphbrain-alpha-upper-068`, `graphbrain-alpha-upper-069`, `graphbrain-alpha-upper-070`, `graphbrain-alpha-upper-071`, `graphbrain-alpha-upper-072`, `graphbrain-alpha-upper-073`, `graphbrain-alpha-upper-074`, `graphbrain-alpha-upper-075`, `graphbrain-alpha-upper-076`, `graphbrain-alpha-upper-077`, `graphbrain-alpha-upper-078`, `graphbrain-alpha-upper-079`, `graphbrain-alpha-upper-080`, `graphbrain-alpha-upper-081`, `graphbrain-alpha-upper-082`, `graphbrain-alpha-upper-083`, `graphbrain-alpha-upper-084`, `graphbrain-alpha-upper-085`, `graphbrain-alpha-upper-086`, `graphbrain-alpha-upper-087`, `graphbrain-alpha-upper-088`, `graphbrain-alpha-upper-089`, `graphbrain-alpha-upper-090`, `graphbrain-alpha-upper-091`, `graphbrain-alpha-upper-092`, `graphbrain-alpha-upper-093`, `graphbrain-alpha-upper-094`, `graphbrain-alpha-upper-095`, `graphbrain-alpha-upper-096`, `graphbrain-alpha-upper-097`, `graphbrain-alpha-upper-098`, `graphbrain-alpha-upper-099`, `graphbrain-alpha-upper-100`, `graphbrain-alpha-upper-101`, `graphbrain-alpha-upper-102`, `graphbrain-alpha-upper-103`, `graphbrain-alpha-upper-104`, `graphbrain-alpha-upper-105`, `graphbrain-alpha-upper-106`, `graphbrain-alpha-upper-107`, `graphbrain-alpha-upper-108`, `graphbrain-alpha-upper-109`, `graphbrain-alpha-upper-110`, `graphbrain-alpha-upper-111`, `graphbrain-alpha-upper-112`, `graphbrain-alpha-upper-113`, `graphbrain-alpha-upper-114`, `graphbrain-alpha-upper-115`, `graphbrain-alpha-upper-116`, `graphbrain-alpha-upper-117`, `graphbrain-alpha-upper-118`, `graphbrain-alpha-upper-119`, `graphbrain-alpha-upper-120`, `graphbrain-alpha-upper-121`, `graphbrain-alpha-upper-122`, `graphbrain-alpha-upper-123`, `graphbrain-alpha-upper-124`, `graphbrain-alpha-upper-125`, `graphbrain-alpha-upper-126`, `graphbrain-alpha-upper-127`, `graphbrain-alpha-upper-128`, `graphbrain-alpha-upper-129`, `graphbrain-alpha-upper-130`, `graphbrain-alpha-upper-131`, `graphbrain-alpha-upper-132`, `graphbrain-alpha-upper-133`, `graphbrain-alpha-upper-134`, `graphbrain-alpha-upper-135`, `graphbrain-alpha-upper-136`, `graphbrain-alpha-upper-137`, `graphbrain-alpha-upper-138`, `graphbrain-alpha-upper-139`.

Manifest audit: 139 unique IDs, no missing or extra IDs relative to the frozen
corpus selection `id.startswith("graphbrain-alpha-upper-")`.

## Incremental verdict ledger

### graphbrain-alpha-upper-001 — HOLD_ARSENAL

> `independence_number(x) <= e^(maximum(max_even_minus_even_horizontal(x), 1/2*max_degree(x)))`

The author-project implementation defines `max_even_minus_even_horizontal` as
the maximum, over vertices, of the number of even-distance vertices minus the
number of edges they induce, with an initial maximum of zero.  The exact
author reading holds on all 996 connected nonempty Graph Atlas graphs through
order 7 and on the named and campaign-family controls.  In particular the
carrier has `alpha=2`, `max_even_minus_even_horizontal=0`, and `Delta=11`, so
the right side is `exp(11/2)`, far above 2.  No numerical boundary is close.

### graphbrain-alpha-upper-066 — CANDIDATE_KILL

> `independence_number(x) <= e^cosh(average_distance(x)) - tan(sigma_2(x))`

On `C5[K10]`, every vertex has degree 29 and `sigma_2=58`.  Of the
`C(50,2)=1225` unordered pairs, 725 are adjacent and 500 have distance two,
so average distance is `69/49`.  In radians the right side is
`exp(cosh(69/49))-tan(58)=0.396963134787592... < alpha=2`.

The identical expression has no violation among all 996 connected nonempty
Graph Atlas graphs through order 7 on which it is defined, nor on Petersen,
`K3,3`, the cube, or Heawood.  (The author code gives `sigma_2=Infinity` on a
complete graph, so those domain-error cases are not evaluated.)  A second
formula-only implementation reproduces the counts and margin `1.603036865...`,
far from the `1e-6` guard.  Searches of the author repository, issue history,
and exact formula found the posting but no pre-existing counterexample.  This
is a candidate new disproof; an executable certificate is prepared separately.

### graphbrain-alpha-upper-069 — RETRO_KILL

> `independence_number(x) <= (10^different_degrees(x) - min_common_neighbors(x))^2`

`C5[K9]` has one distinct degree and minimum common-neighbor count 9, so
the right side is `1 < alpha=2`.  This is not a novelty candidate: the simpler
`K12` has `alpha=1`, one distinct degree, and minimum common-neighbor count 10,
giving right side zero.  Exact integer recomputation agrees.

### graphbrain-alpha-upper-081 — CANDIDATE_KILL

> `independence_number(x) <= 2*diameter(x)/(edge_con(x) - vertex_con(x))`

For `C5[K_m]`, `alpha=2`, diameter is 2, edge connectivity is its degree
`3m-1`, and vertex connectivity is `2m`.  The right side is therefore
`4/(m-1)`: equality at `m=3`, but `4/3 < 2` at `C5[K4]`, with violations for
every `m>=4`.

The identical author reading has no violation among all 996 connected
nonempty Graph Atlas graphs through order 7 for which its denominator is
nonzero, nor on the named controls.  NetworkX connectivity algorithms and a
separate structural calculation independently give
`(alpha,diameter,edge_con,vertex_con)=(2,2,11,8)` and exact margin `2/3`.
Author-repository, issue-history, exact-formula, and broader invariant searches
found no pre-existing counterexample.  This is a candidate new disproof; an
executable certificate is prepared separately.

### graphbrain-alpha-upper-042 — HOLD_ARSENAL

> `independence_number(x) <= diameter(x)^ceil(1/2*max_degree(x))`

The source-faithful expression has no violation on all 996 connected nonempty Graph Atlas graphs through order 7 where defined, the named controls, or the campaign families and threshold complete graphs.  Real-valued comparisons obey the `1e-6` guard.  This is an arsenal hold, not a proof.


### graphbrain-alpha-upper-041 — HOLD_ARSENAL

> `independence_number(x) <= (girth(x)^sigma_2(x) - card_periphery(x))^2`

The source-faithful expression has no violation on all 996 connected nonempty Graph Atlas graphs through order 7 where defined, the named controls, or the campaign families and threshold complete graphs.  Real-valued comparisons obey the `1e-6` guard.  This is an arsenal hold, not a proof.


### graphbrain-alpha-upper-040 — DB_REJECTED

> `independence_number(x) <= ceil(sqrt(average_distance(x))^order(x))`

The identical author-project reading already fails the mandatory small-graph gate on connected Graph Atlas graph `atlas:@`: `alpha=1` while the right side is `0`.  It is therefore a database-inconsistent/as-posted falsehood, not a new campaign counterexample.  The result was independently recomputed from the author invariant definitions; undefined domain cases were excluded.


### graphbrain-alpha-upper-039 — HOLD_ARSENAL

> `independence_number(x) <= maximum(max_even_minus_even_horizontal(x), matching_number(x) - 1)^different_degrees(x)`

The source-faithful expression has no violation on all 996 connected nonempty Graph Atlas graphs through order 7 where defined, the named controls, or the campaign families and threshold complete graphs.  Real-valued comparisons obey the `1e-6` guard.  This is an arsenal hold, not a proof.


### graphbrain-alpha-upper-038 — HOLD_ARSENAL

> `independence_number(x) <= maximum(max_degree(x), e^min_degree(x)/density(x))`

The source-faithful expression has no violation on all 996 connected nonempty Graph Atlas graphs through order 7 where defined, the named controls, or the campaign families and threshold complete graphs.  Real-valued comparisons obey the `1e-6` guard.  This is an arsenal hold, not a proof.


### graphbrain-alpha-upper-037 — HOLD_ARSENAL

> `independence_number(x) <= (girth(x)^card_center(x))^card_periphery(x)`

The source-faithful expression has no violation on all 996 connected nonempty Graph Atlas graphs through order 7 where defined, the named controls, or the campaign families and threshold complete graphs.  Real-valued comparisons obey the `1e-6` guard.  This is an arsenal hold, not a proof.


### graphbrain-alpha-upper-036 — HOLD_ARSENAL

> `independence_number(x) <= -card_center(x) + girth(x) + size(x)`

The source-faithful expression has no violation on all 996 connected nonempty Graph Atlas graphs through order 7 where defined, the named controls, or the campaign families and threshold complete graphs.  Real-valued comparisons obey the `1e-6` guard.  This is an arsenal hold, not a proof.


### graphbrain-alpha-upper-035 — HOLD_ARSENAL

> `independence_number(x) <= maximum(2*max_even_minus_even_horizontal(x), maximum(max_degree(x), card_center(x)))`

The source-faithful expression has no violation on all 996 connected nonempty Graph Atlas graphs through order 7 where defined, the named controls, or the campaign families and threshold complete graphs.  Real-valued comparisons obey the `1e-6` guard.  This is an arsenal hold, not a proof.


### graphbrain-alpha-upper-034 — HOLD_ARSENAL

> `independence_number(x) <= girth(x)^max_degree(x) + card_center(x)`

The source-faithful expression has no violation on all 996 connected nonempty Graph Atlas graphs through order 7 where defined, the named controls, or the campaign families and threshold complete graphs.  Real-valued comparisons obey the `1e-6` guard.  This is an arsenal hold, not a proof.


### graphbrain-alpha-upper-033 — HOLD_ARSENAL

> `independence_number(x) <= card_periphery(x)^different_degrees(x) + max_even_minus_even_horizontal(x)`

The source-faithful expression has no violation on all 996 connected nonempty Graph Atlas graphs through order 7 where defined, the named controls, or the campaign families and threshold complete graphs.  Real-valued comparisons obey the `1e-6` guard.  This is an arsenal hold, not a proof.


### graphbrain-alpha-upper-032 — HOLD_ARSENAL

> `independence_number(x) <= degree_sum(x)/minimum(different_degrees(x), number_of_triangles(x))`

The source-faithful expression has no violation on all 996 connected nonempty Graph Atlas graphs through order 7 where defined, the named controls, or the campaign families and threshold complete graphs.  Real-valued comparisons obey the `1e-6` guard.  This is an arsenal hold, not a proof.


### graphbrain-alpha-upper-031 — DB_REJECTED

> `independence_number(x) <= order(x)^order_automorphism_group(x) - ceil(average_degree(x))`

The identical author-project reading already fails the mandatory small-graph gate on connected Graph Atlas graph `atlas:FjtWO`: `alpha=4` while the right side is `3`.  It is therefore a database-inconsistent/as-posted falsehood, not a new campaign counterexample.  The result was independently recomputed from the author invariant definitions; undefined domain cases were excluded.


### graphbrain-alpha-upper-030 — DB_REJECTED

> `independence_number(x) <= cosh(-number_of_triangles(x) + order(x))*max_degree(x)`

The identical author-project reading already fails the mandatory small-graph gate on connected Graph Atlas graph `atlas:@`: `alpha=1` while the right side is `0`.  It is therefore a database-inconsistent/as-posted falsehood, not a new campaign counterexample.  The result was independently recomputed from the author invariant definitions; undefined domain cases were excluded.


### graphbrain-alpha-upper-029 — DB_REJECTED

> `independence_number(x) <= max_degree(x)^card_center(x) + 2*diameter(x)`

The identical author-project reading already fails the mandatory small-graph gate on connected Graph Atlas graph `atlas:@`: `alpha=1` while the right side is `0`.  It is therefore a database-inconsistent/as-posted falsehood, not a new campaign counterexample.  The result was independently recomputed from the author invariant definitions; undefined domain cases were excluded.


### graphbrain-alpha-upper-028 — HOLD_ARSENAL

> `independence_number(x) <= 10^arctan(different_degrees(x)) + 1/min_common_neighbors(x)`

The source-faithful expression has no violation on all 996 connected nonempty Graph Atlas graphs through order 7 where defined, the named controls, or the campaign families and threshold complete graphs.  Real-valued comparisons obey the `1e-6` guard.  This is an arsenal hold, not a proof.


### graphbrain-alpha-upper-027 — HOLD_ARSENAL

> `independence_number(x) <= 10^(number_of_triangles(x) + order_automorphism_group(x))`

The source-faithful expression has no violation on all 996 connected nonempty Graph Atlas graphs through order 7 where defined, the named controls, or the campaign families and threshold complete graphs.  Real-valued comparisons obey the `1e-6` guard.  This is an arsenal hold, not a proof.


### graphbrain-alpha-upper-026 — DB_REJECTED

> `independence_number(x) <= floor(degree_sum(x)/sigma_2(x))`

The identical author-project reading already fails the mandatory small-graph gate on connected Graph Atlas graph `atlas:@`: `alpha=1` while the right side is `0`.  It is therefore a database-inconsistent/as-posted falsehood, not a new campaign counterexample.  The result was independently recomputed from the author invariant definitions; undefined domain cases were excluded.


### graphbrain-alpha-upper-025 — DB_REJECTED

> `independence_number(x) <= 2*diameter(x)^2 + max_degree(x)`

The identical author-project reading already fails the mandatory small-graph gate on connected Graph Atlas graph `atlas:@`: `alpha=1` while the right side is `0`.  It is therefore a database-inconsistent/as-posted falsehood, not a new campaign counterexample.  The result was recomputed from the author invariant definitions; any undefined domain cases were excluded rather than coerced.


### graphbrain-alpha-upper-024 — HOLD_ARSENAL

> `independence_number(x) <= 10^cosh(-card_periphery(x) + matching_number(x))`

The source-faithful expression has no violation on all 996 connected nonempty Graph Atlas graphs through order 7 where it is defined, the named controls, or the campaign families and threshold complete graphs.  Exact arithmetic was used where available; real-valued comparisons obey the `1e-6` guard.  This is only an arsenal hold, not a proof.


### graphbrain-alpha-upper-023 — DB_REJECTED

> `independence_number(x) <= floor(sigma_2(x)^(1/density(x)))`

The identical author-project reading already fails the mandatory small-graph gate on connected Graph Atlas graph `atlas:Fn{GO`: `alpha=4` while the right side is `3`.  It is therefore a database-inconsistent/as-posted falsehood, not a new campaign counterexample.  The result was recomputed from the author invariant definitions; any undefined domain cases were excluded rather than coerced.


### graphbrain-alpha-upper-022 — DB_REJECTED

> `independence_number(x) <= 2*diameter(x)/min_common_neighbors(x) + max_common_neighbors(x)`

The identical author-project reading already fails the mandatory small-graph gate on connected Graph Atlas graph `atlas:@`: `alpha=1` while the right side is `0`.  It is therefore a database-inconsistent/as-posted falsehood, not a new campaign counterexample.  The result was recomputed from the author invariant definitions; any undefined domain cases were excluded rather than coerced.


### graphbrain-alpha-upper-021 — DB_REJECTED

> `independence_number(x) <= maximum(min_degree(x), e^(order(x) - sigma_2(x)))`

The identical author-project reading already fails the mandatory small-graph gate on connected Graph Atlas graph `atlas:@`: `alpha=1` while the right side is `0`.  It is therefore a database-inconsistent/as-posted falsehood, not a new campaign counterexample.  The result was recomputed from the author invariant definitions; any undefined domain cases were excluded rather than coerced.


### graphbrain-alpha-upper-020 — DB_REJECTED

> `independence_number(x) <= girth(x)^floor(average_distance(x)/density(x))`

The identical author-project reading already fails the mandatory small-graph gate on connected Graph Atlas graph `atlas:FF~ww`: `alpha=4` while the right side is `3`.  It is therefore a database-inconsistent/as-posted falsehood, not a new campaign counterexample.  The result was recomputed from the author invariant definitions; any undefined domain cases were excluded rather than coerced.


### graphbrain-alpha-upper-019 — DB_REJECTED

> `independence_number(x) <= (average_degree(x)*order_automorphism_group(x))^(diameter(x) - 1)`

The identical author-project reading already fails the mandatory small-graph gate on connected Graph Atlas graph `atlas:Fhf_g`: `alpha=3` while the right side is `2.857142857142857`.  It is therefore a database-inconsistent/as-posted falsehood, not a new campaign counterexample.  The result was recomputed from the author invariant definitions; any undefined domain cases were excluded rather than coerced.


### graphbrain-alpha-upper-018 — HOLD_ARSENAL

> `-independence_number(x) <= maximum(number_of_triangles(x), 1/min_common_neighbors(x))`

The source-faithful expression has no violation on all 996 connected nonempty Graph Atlas graphs through order 7 where it is defined, the named controls, or the campaign families and threshold complete graphs.  Exact arithmetic was used where available; real-valued comparisons obey the `1e-6` guard.  This is only an arsenal hold, not a proof.


### graphbrain-alpha-upper-017 — HOLD_ARSENAL

> `independence_number(x) <= sinh(maximum(max_even_minus_even_horizontal(x), 1/2*matching_number(x)))`

The source-faithful expression has no violation on all 996 connected nonempty Graph Atlas graphs through order 7 where it is defined, the named controls, or the campaign families and threshold complete graphs.  Exact arithmetic was used where available; real-valued comparisons obey the `1e-6` guard.  This is only an arsenal hold, not a proof.


### graphbrain-alpha-upper-016 — DB_REJECTED

> `independence_number(x) <= maximum(max_common_neighbors(x), 10^(order(x) - sigma_2(x)))`

The identical author-project reading already fails the mandatory small-graph gate on connected Graph Atlas graph `atlas:@`: `alpha=1` while the right side is `0`.  It is therefore a database-inconsistent/as-posted falsehood, not a new campaign counterexample.  The result was recomputed from the author invariant definitions; any undefined domain cases were excluded rather than coerced.


### graphbrain-alpha-upper-015 — HOLD_ARSENAL

> `independence_number(x) <= 10^sigma_2(x) - card_periphery(x)`

The source-faithful expression has no violation on all 996 connected nonempty Graph Atlas graphs through order 7 where it is defined, the named controls, or the campaign families and threshold complete graphs.  Exact arithmetic was used where available; real-valued comparisons obey the `1e-6` guard.  This is only an arsenal hold, not a proof.


### graphbrain-alpha-upper-014 — HOLD_ARSENAL

> `independence_number(x) <= max_even_minus_even_horizontal(x)^2 + matching_number(x)`

The source-faithful expression has no violation on all 996 connected nonempty Graph Atlas graphs through order 7 where it is defined, the named controls, or the campaign families and threshold complete graphs.  Exact arithmetic was used where available; real-valued comparisons obey the `1e-6` guard.  This is only an arsenal hold, not a proof.


### graphbrain-alpha-upper-013 — HOLD_ARSENAL

> `independence_number(x) <= 10^card_center(x) + max_even_minus_even_horizontal(x)`

The source-faithful expression has no violation on all 996 connected nonempty Graph Atlas graphs through order 7 where it is defined, the named controls, or the campaign families and threshold complete graphs.  Exact arithmetic was used where available; real-valued comparisons obey the `1e-6` guard.  This is only an arsenal hold, not a proof.


### graphbrain-alpha-upper-012 — HOLD_ARSENAL

> `independence_number(x) <= maximum(max_degree(x)^2, max_even_minus_even_horizontal(x) + min_degree(x))`

The source-faithful expression has no violation on all 996 connected nonempty Graph Atlas graphs through order 7 where it is defined, the named controls, or the campaign families and threshold complete graphs.  Exact arithmetic was used where available; real-valued comparisons obey the `1e-6` guard.  This is only an arsenal hold, not a proof.


### graphbrain-alpha-upper-011 — DB_REJECTED

> `independence_number(x) <= maximum(vertex_con(x), e^(order(x) - sigma_2(x)))`

The identical author-project reading already fails the mandatory small-graph gate on connected Graph Atlas graph `atlas:@`: `alpha=1` while the right side is `0`.  It is therefore a database-inconsistent/as-posted falsehood, not a new campaign counterexample.  The result was recomputed from the author invariant definitions; any undefined domain cases were excluded rather than coerced.


### graphbrain-alpha-upper-010 — DB_REJECTED

> `independence_number(x) <= (max_even_minus_even_horizontal(x) + 1)*matching_number(x)`

The identical author-project reading already fails the mandatory small-graph gate on connected Graph Atlas graph `atlas:@`: `alpha=1` while the right side is `0`.  It is therefore a database-inconsistent/as-posted falsehood, not a new campaign counterexample.  The result was recomputed from the author invariant definitions; any undefined domain cases were excluded rather than coerced.


### graphbrain-alpha-upper-009 — DB_REJECTED

> `independence_number(x) <= floor(arctan(girth(x))^size(x))`

The identical author-project reading already fails the mandatory small-graph gate on connected Graph Atlas graph `atlas:E?Fw`: `alpha=4` while the right side is `3`.  It is therefore a database-inconsistent/as-posted falsehood, not a new campaign counterexample.  The result was recomputed from the author invariant definitions; any undefined domain cases were excluded rather than coerced.


### graphbrain-alpha-upper-008 — HOLD_ARSENAL

> `independence_number(x) <= ceil(e^(order(x)/min_degree(x)))`

The source-faithful expression has no violation on all 996 connected nonempty Graph Atlas graphs through order 7 where it is defined, the named controls, or the campaign families and threshold complete graphs.  Exact arithmetic was used where available; real-valued comparisons obey the `1e-6` guard.  This is only an arsenal hold, not a proof.


### graphbrain-alpha-upper-007 — RETRO_KILL_AUTHOR_SOURCE

> `independence_number(x) <= (2*girth(x))^card_periphery(x)`

The author project's own current graph-object source contains a graph explicitly labeled as a counterexample to this exact formula.  This independently establishes that the still-open issue line is stale.  The campaign therefore records a retro-kill, not a novelty claim; the author-source status takes precedence over arsenal behavior.


### graphbrain-alpha-upper-006 — HOLD_ARSENAL

> `independence_number(x) <= (card_periphery(x) + diameter(x))^(max_even_minus_even_horizontal(x) + 1)`

The source-faithful expression has no violation on all 996 connected nonempty Graph Atlas graphs through order 7 where it is defined, the named controls, or the campaign families and threshold complete graphs.  Exact arithmetic was used where available; real-valued comparisons obey the `1e-6` guard.  This is only an arsenal hold, not a proof.


### graphbrain-alpha-upper-005 — HOLD_ARSENAL

> `independence_number(x) <= (max_degree(x) + max_even_minus_even_horizontal(x))^2 - matching_number(x)`

The source-faithful expression has no violation on all 996 connected nonempty Graph Atlas graphs through order 7 where it is defined, the named controls, or the campaign families and threshold complete graphs.  Exact arithmetic was used where available; real-valued comparisons obey the `1e-6` guard.  This is only an arsenal hold, not a proof.


### graphbrain-alpha-upper-004 — HOLD_ARSENAL

> `independence_number(x) <= ceil(e^girth(x)) + max_even_minus_even_horizontal(x)`

The source-faithful expression has no violation on all 996 connected nonempty Graph Atlas graphs through order 7 where it is defined, the named controls, or the campaign families and threshold complete graphs.  Exact arithmetic was used where available; real-valued comparisons obey the `1e-6` guard.  This is only an arsenal hold, not a proof.


### graphbrain-alpha-upper-003 — RETRO_KILL_AUTHOR_SOURCE

> `independence_number(x) <= max_even_minus_even_horizontal(x) + sinh(max_degree(x) - 1)`

The author project's own current graph-object source contains a graph explicitly labeled as a counterexample to this exact formula.  This independently establishes that the still-open issue line is stale.  The campaign therefore records a retro-kill, not a novelty claim; the author-source status takes precedence over arsenal behavior.


### graphbrain-alpha-upper-002 — RETRO_KILL_AUTHOR_SOURCE

> `independence_number(x) <= floor(10^sqrt(average_distance(x)))`

The author project's own current graph-object source contains a graph explicitly labeled as a counterexample to this exact formula.  This independently establishes that the still-open issue line is stale.  The campaign therefore records a retro-kill, not a novelty claim; the author-source status takes precedence over arsenal behavior.
