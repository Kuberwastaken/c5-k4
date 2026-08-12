# Graph Brain alpha lower-bound sweep

Audit date: **2026-08-12**. Primary manifest:
`corpora/graphbrain_open_alpha.json`, preserving author-project issue #421.
This ledger covers all **89** `graphbrain-alpha-lower-*` lines exactly once.

## Method and invariant semantics

Statements are quoted exactly from the issue-derived corpus. Evaluation uses
the campaign arsenal and the required DB-sanity gate: all 995 nontrivial
connected graphs in `networkx.graph_atlas_g()` (orders 2--7), plus cycles,
paths, Petersen, complete, star, and complete-bipartite controls. Expressions
outside their real domain or containing a zero denominator are not silently
extended. Trigonometric functions use radians, matching the author code.

Crucially, Graph Brain's primary `src/Invariants/invariants.sage` defines
`max_even_minus_even_horizontal` with an accumulator initialized to zero. It
returns `max(0, |Even(v)|-|E(G[Even(v)])|)` on a connected component. Thus it
is **0**, not the WoW-style signed value -19, on `C5[K4]`. Every entry below
uses the author implementation. This source check prevents a false apparent
violation of lower-078.

Verdicts mean: `HOLD_ARSENAL` (no arsenal violation); `HOLD_TIGHT` (an arsenal
equality); `RETRO_KILL` (the open-as-posted line has a gate-surviving
counterexample, without a novelty claim); `DB_REJECTED` (an apparent arsenal
violation is already present in the required small database); and
`SKIP_UNDEFINED` (the expression is not real/defined on a relevant graph and
the source supplies no totalization).

## Entry ledger

#### graphbrain-alpha-lower-001 — `HOLD_TIGHT`
`independence_number(x) >= minimum(girth(x), floor(lovasz_theta(x)))`. Equality on `C5[K4]`: `2=min(3,2)`.

#### graphbrain-alpha-lower-002 — `HOLD_TIGHT`
`independence_number(x) >= diameter(x)/different_degrees(x)`. Equality on the carrier: `2=2/1`.

#### graphbrain-alpha-lower-003 — `HOLD_TIGHT`
`independence_number(x) >= minimum(diameter(x), lovasz_theta(x))`. Equality on the carrier: `2=min(2,sqrt(5))`.

#### graphbrain-alpha-lower-004 — `HOLD_ARSENAL`
`independence_number(x) >= maximum(max_even_minus_even_horizontal(x),1/2*lovasz_theta(x))`. Author-clamped MEEH is zero on the carrier; RHS `sqrt(5)/2`.

#### graphbrain-alpha-lower-005 — `HOLD_ARSENAL`
`independence_number(x) >= maximum(critical_independence_number(x),1/2*lovasz_theta(x))`. No arsenal violation under the author implementation.

#### graphbrain-alpha-lower-006 — `HOLD_TIGHT`
`independence_number(x) >= maximum(residue(x), 1/2*lovasz_theta(x))`. Carrier equality at residue `2`.

#### graphbrain-alpha-lower-007 — `HOLD_ARSENAL`
`independence_number(x) >= floor(lovasz_theta(x))/vertex_con(x)`. Carrier RHS `2/8`.

#### graphbrain-alpha-lower-008 — `HOLD_TIGHT`
`independence_number(x) >= 2*floor(arccosh(lovasz_theta(x)))`. Carrier RHS `2`.

#### graphbrain-alpha-lower-009 — `HOLD_ARSENAL`
`independence_number(x) >= floor(arccosh(lovasz_theta(x)))^2`. Carrier RHS `1`.

#### graphbrain-alpha-lower-010 — `HOLD_ARSENAL`
`independence_number(x) >= minimum(floor(lovasz_theta(x)), max_even_minus_even_horizontal(x) + 1)`. Carrier RHS `1` using author MEEH `0`.

#### graphbrain-alpha-lower-011 — `HOLD_ARSENAL`
`independence_number(x) >= minimum(card_periphery(x), lovasz_theta(x)/card_center(x))`. Carrier RHS `sqrt(5)/20`.

#### graphbrain-alpha-lower-012 — `HOLD_ARSENAL`
`independence_number(x) >= floor(lovasz_theta(x))sin(gutman_energy(x))`. The implicit product reading used by the source was checked; no arsenal violation.

#### graphbrain-alpha-lower-013 — `HOLD_ARSENAL`
`independence_number(x) >= ceil(lovasz_theta(x)) - radius(x)`. Carrier RHS `1`.

#### graphbrain-alpha-lower-014 — `HOLD_ARSENAL`
`independence_number(x) >= ceil(lovasz_theta(x)) - girth(x)`. Carrier RHS `0`.

#### graphbrain-alpha-lower-015 — `HOLD_ARSENAL`
`independence_number(x) >= ceil(lovasz_theta(x)) - welsh_powell(x)`. No arsenal violation.

#### graphbrain-alpha-lower-016 — `HOLD_ARSENAL`
`independence_number(x) >= max_degree(x) - sigma_2(x) - 1`. Carrier RHS `11-22-1=-12`.

#### graphbrain-alpha-lower-017 — `HOLD_ARSENAL`
`independence_number(x) >= 1/2*card_negative_eigenvalues(x) - max_common_neighbors(x)`. No arsenal violation.

#### graphbrain-alpha-lower-018 — `HOLD_ARSENAL`
`independence_number(x) >= minimum(inverse_degree(x), floor(lovasz_theta(x)))`. Carrier RHS `min(20/11,2)=20/11`.

#### graphbrain-alpha-lower-019 — `HOLD_TIGHT`
`independence_number(x) >= ceil(card_independence_irreducible_part(x)/szekeres_wilf(x))`. Author decomposition gives carrier RHS `ceil(20/12)=2`.

#### graphbrain-alpha-lower-020 — `HOLD_ARSENAL`
`independence_number(x) >= -card_center(x) + floor(lovasz_theta(x))`. Carrier RHS `-18`.

#### graphbrain-alpha-lower-021 — `HOLD_TIGHT`
`independence_number(x) >= ceil(card_center(x)/szekeres_wilf(x))`. Carrier RHS `ceil(20/12)=2`.

#### graphbrain-alpha-lower-022 — `HOLD_ARSENAL`
`independence_number(x) >= 1/2*card_periphery(x) - sigma_2(x)`. Carrier RHS `10-22=-12`.

#### graphbrain-alpha-lower-023 — `HOLD_ARSENAL`
`independence_number(x) >= (degree_sum(x) - order_automorphism_group(x))/10^max_common_neighbors(x)`. No arsenal violation; symmetry makes the carrier RHS negative.

#### graphbrain-alpha-lower-024 — `HOLD_ARSENAL`
`independence_number(x) >= floor(log(size(x))) - order_automorphism_group(x)`. No arsenal violation using natural log and exact automorphism orders.

#### graphbrain-alpha-lower-025 — `HOLD_ARSENAL`
`independence_number(x) >= ceil(arcsinh(order(x) - sigma_2(x)))`. Carrier RHS `ceil(asinh(-2))=-1`.

#### graphbrain-alpha-lower-026 — `HOLD_ARSENAL`
`independence_number(x) >= 1/2*matching_number(x) - 1/2*min_degree(x)`. Carrier RHS `-1/2`.

#### graphbrain-alpha-lower-027 — `HOLD_ARSENAL`
`independence_number(x) >= -(girth(x) - radius(x))*card_pendants(x)`. Carrier RHS `0`.

#### graphbrain-alpha-lower-028 — `HOLD_ARSENAL`
`independence_number(x) >= minimum(girth(x), max_degree(x) - szekeres_wilf(x))`. Carrier RHS `min(3,-1)=-1`.

#### graphbrain-alpha-lower-029 — `HOLD_ARSENAL`
`independence_number(x) >= 2*different_degrees(x) - 2*szekeres_wilf(x)`. Carrier RHS `-22`.

#### graphbrain-alpha-lower-030 — `HOLD_ARSENAL`
`independence_number(x) >= minimum(matching_number(x), girth(x) - max_common_neighbors(x))`. No arsenal violation.

#### graphbrain-alpha-lower-031 — `HOLD_ARSENAL`
`independence_number(x) >= minimum(10^number_of_triangles(x), card_pendants(x) + 1)`. Carrier RHS `1`.

#### graphbrain-alpha-lower-032 — `HOLD_ARSENAL`
`independence_number(x) >= order(x)/card_periphery(x) - card_center(x)`. Carrier RHS `1-20=-19`.

#### graphbrain-alpha-lower-033 — `RETRO_KILL`
`independence_number(x) >= -girth(x) + minimum(min_degree(x), tan(average_distance(x)))`. On `C5[K3]`, average distance is exactly `10/7`, so RHS `-3+tan(10/7)=3.9836453508... > 2=alpha`. All 995 connected Atlas controls and 43 named controls pass; independent executable certificate below.

#### graphbrain-alpha-lower-034 — `HOLD_ARSENAL`
`independence_number(x) >= floor(tan(order(x) - szekeres_wilf(x)))`. No arsenal violation.

#### graphbrain-alpha-lower-035 — `HOLD_ARSENAL`
`independence_number(x) >= ceil(tan(min_degree(x))) - order_automorphism_group(x)`. No arsenal violation using exact automorphism orders.

#### graphbrain-alpha-lower-036 — `HOLD_ARSENAL`
`independence_number(x) >= minimum(different_degrees(x), -card_cut_vertices(x) + diameter(x))`. Carrier RHS `1`.

#### graphbrain-alpha-lower-037 — `HOLD_ARSENAL`
`independence_number(x) >= (different_degrees(x) - szekeres_wilf(x))*min_degree(x)`. Carrier RHS is negative.

#### graphbrain-alpha-lower-038 — `HOLD_TIGHT`
`independence_number(x) >= ceil(2*matching_number(x)/szekeres_wilf(x))`. Carrier RHS `ceil(20/12)=2`.

#### graphbrain-alpha-lower-039 — `HOLD_ARSENAL`
`independence_number(x) >= minimum(max_common_neighbors(x), tan(order(x) + 1))`. No arsenal violation.

#### graphbrain-alpha-lower-040 — `HOLD_ARSENAL`
`independence_number(x) >= log(density(x))^(-max_common_neighbors(x) + szekeres_wilf(x))`. Evaluated on real-defined arsenal instances; no violation.

#### graphbrain-alpha-lower-041 — `HOLD_ARSENAL`
`independence_number(x) >= 2*different_degrees(x)/sigma_2(x)`. Carrier RHS `1/11`.

#### graphbrain-alpha-lower-042 — `HOLD_ARSENAL`
`independence_number(x) >= -10^min_degree(x) + matching_number(x)`. Carrier RHS is negative.

#### graphbrain-alpha-lower-043 — `HOLD_ARSENAL`
`independence_number(x) >= minimum(different_degrees(x), 2*card_cut_vertices(x))`. Carrier RHS `0`.

#### graphbrain-alpha-lower-044 — `HOLD_ARSENAL`
`independence_number(x) >= matching_number(x) - max_degree(x) - szekeres_wilf(x)`. Carrier RHS `-13`.

#### graphbrain-alpha-lower-045 — `HOLD_ARSENAL`
`independence_number(x) >= tan(max_even_minus_even_horizontal(x)*order(x))/sigma_2(x)`. Carrier RHS `0` under author MEEH.

#### graphbrain-alpha-lower-046 — `HOLD_ARSENAL`
`independence_number(x) >= (max_common_neighbors(x) - min_degree(x))/order_automorphism_group(x)`. No arsenal violation.

#### graphbrain-alpha-lower-047 — `HOLD_ARSENAL`
`independence_number(x) >= card_cut_vertices(x) + card_pendants(x) - matching_number(x)`. Carrier RHS `-10`.

#### graphbrain-alpha-lower-048 — `HOLD_ARSENAL`
`independence_number(x) >= -girth(x)^card_periphery(x) + matching_number(x)`. Carrier RHS is negative.

#### graphbrain-alpha-lower-049 — `HOLD_ARSENAL`
`independence_number(x) >= -10^max_common_neighbors(x) + matching_number(x)`. Carrier RHS is negative.

#### graphbrain-alpha-lower-050 — `HOLD_ARSENAL`
`independence_number(x) >= minimum(different_degrees(x), order(x)/sigma_2(x))`. Carrier RHS `10/11`.

#### graphbrain-alpha-lower-051 — `HOLD_ARSENAL`
`independence_number(x) >= -2*card_center(x) - girth(x) + matching_number(x)`. Carrier RHS `-33`.

#### graphbrain-alpha-lower-052 — `HOLD_ARSENAL`
`independence_number(x) >= minimum(order_automorphism_group(x), -max_common_neighbors(x) + min_degree(x))`. Carrier RHS `1`.

#### graphbrain-alpha-lower-053 — `HOLD_ARSENAL`
`independence_number(x) >= floor(arctanh(sin(number_of_triangles(x))))`. Radian evaluation yields no arsenal violation.

#### graphbrain-alpha-lower-054 — `HOLD_ARSENAL`
`independence_number(x) >= different_degrees(x)/sqrt(density(x)) - max_degree(x)`. No arsenal violation.

#### graphbrain-alpha-lower-055 — `RETRO_KILL`
`independence_number(x) >= minimum(radius(x)^2, 1/2*min_common_neighbors(x))`. On `C5[K5]`, RHS `min(4,5/2)=5/2 > 2=alpha`. The author definition takes the minimum common-neighbor count over every distinct vertex pair. The full required gate passes.

#### graphbrain-alpha-lower-056 — `HOLD_TIGHT`
`independence_number(x) >= minimum(card_periphery(x), diameter(x)/different_degrees(x))`. Carrier equality at `2`.

#### graphbrain-alpha-lower-057 — `HOLD_ARSENAL`
`independence_number(x) >= -(card_periphery(x) - matching_number(x))/different_degrees(x)`. Carrier RHS `-10`.

#### graphbrain-alpha-lower-058 — `HOLD_ARSENAL`
`independence_number(x) >= (card_center(x) - 2*matching_number(x))*diameter(x)`. Carrier RHS `0`.

#### graphbrain-alpha-lower-059 — `HOLD_ARSENAL`
`independence_number(x) >= -card_center(x) + matching_number(x) - max_degree(x)`. Carrier RHS `-21`.

#### graphbrain-alpha-lower-060 — `HOLD_ARSENAL`
`independence_number(x) >= minimum(tan(size(x)), -card_center(x) + matching_number(x))`. Carrier second branch is `-10`.

#### graphbrain-alpha-lower-061 — `RETRO_KILL`
`independence_number(x) >= minimum(szekeres_wilf(x), -average_degree(x) + matching_number(x))`. On `C9[K3]`, RHS `min(9,-8+13)=5 > 4=alpha`. The full required gate passes.

#### graphbrain-alpha-lower-062 — `HOLD_ARSENAL`
`independence_number(x) >= card_periphery(x)/min_degree(x) - order_automorphism_group(x)`. No arsenal violation.

#### graphbrain-alpha-lower-063 — `SKIP_UNDEFINED`
`independence_number(x) >= minimum(max_degree(x), matching_number(x)/max_common_neighbors(x))`. The denominator is zero on connected source-domain graphs (for example paths), and the source gives no totalization.

#### graphbrain-alpha-lower-064 — `HOLD_ARSENAL`
`independence_number(x) >= minimum(different_degrees(x), 1/cos(card_center(x)))`. Carrier RHS is at most `1`.

#### graphbrain-alpha-lower-065 — `SKIP_UNDEFINED`
`independence_number(x) >= -card_periphery(x)/max_even_minus_even_horizontal(x) + different_degrees(x)`. Author MEEH is zero on the carrier and many controls; no zero-denominator convention is supplied.

#### graphbrain-alpha-lower-066 — `HOLD_ARSENAL`
`independence_number(x) >= minimum(max_degree(x), card_cut_vertices(x)/tan(average_degree(x)))`. Carrier RHS `0`.

#### graphbrain-alpha-lower-067 — `HOLD_ARSENAL`
`independence_number(x) >= 1/2*card_cut_vertices(x) + max_even_minus_even_horizontal(x) - radius(x)`. Carrier RHS `-2`.

#### graphbrain-alpha-lower-068 — `DB_REJECTED`
`independence_number(x) >= minimum(tan(degree_sum(x)), -max_common_neighbors(x) + max_degree(x))`. `T(9)` appears to fail (`4 < 4.35675...`), but connected six-vertex Atlas graphs `EtaG` and `Ehfw` already fail the same literal radian reading. This is not a campaign kill.

#### graphbrain-alpha-lower-069 — `HOLD_ARSENAL`
`independence_number(x) >= floor(tan(min_common_neighbors(x))/density(x))`. No arsenal violation.

#### graphbrain-alpha-lower-070 — `HOLD_ARSENAL`
`independence_number(x) >= -order_automorphism_group(x) + tan(diameter(x) + number_of_triangles(x))`. No arsenal violation using exact automorphism orders.

#### graphbrain-alpha-lower-071 — `RETRO_KILL`
`independence_number(x) >= floor(2*tan(matching_number(x)) - 2)`. Reverified existing certificate: `C7[K4]` has `alpha=3`, matching number `14`, and RHS `12`; all order-at-most-10 graphs pass.

#### graphbrain-alpha-lower-072 — `HOLD_ARSENAL`
`independence_number(x) >= minimum(card_center(x), card_cut_vertices(x)/sin(matching_number(x)))`. Carrier RHS `0`.

#### graphbrain-alpha-lower-073 — `HOLD_ARSENAL`
`independence_number(x) >= minimum(szekeres_wilf(x), tan(2*average_distance(x)))`. No arsenal violation.

#### graphbrain-alpha-lower-074 — `HOLD_ARSENAL`
`independence_number(x) >= ceil(log(average_distance(x)))^vertex_con(x)`. Carrier RHS `1`.

#### graphbrain-alpha-lower-075 — `HOLD_ARSENAL`
`independence_number(x) >= -max_degree(x)^2 - card_center(x) + card_periphery(x)`. Carrier RHS `-121`.

#### graphbrain-alpha-lower-076 — `HOLD_ARSENAL`
`independence_number(x) >= different_degrees(x)*tan(max_even_minus_even_horizontal(x)) - girth(x)`. Carrier RHS `-3`.

#### graphbrain-alpha-lower-077 — `DB_REJECTED`
`independence_number(x) >= arcsinh(floor(tan(sqrt(average_distance(x)))))`. `C9[K3]` appears to fail (`4 < 4.3042...`), but seven connected Atlas graphs of orders 6--7 already fail; the reading is rejected.

#### graphbrain-alpha-lower-078 — `HOLD_ARSENAL`
`independence_number(x) >= (matching_number(x) - max_even_minus_even_horizontal(x))^2/max_degree(x)^2`. Carrier RHS is `100/121 < 2`, because author MEEH is clamped to `0`. Using the WoW signed value `-19` would falsely produce `841/121`; that is not this source's invariant.

#### graphbrain-alpha-lower-079 — `HOLD_ARSENAL`
`independence_number(x) >= tan(floor(tan(log(density(x)))))`. No arsenal violation.

#### graphbrain-alpha-lower-080 — `HOLD_ARSENAL`
`independence_number(x) >= -girth(x)^max_degree(x) + 2*max_even_minus_even_horizontal(x)`. Carrier RHS is negative.

#### graphbrain-alpha-lower-081 — `HOLD_ARSENAL`
`independence_number(x) >= minimum(vertex_con(x), 1/(max_degree(x) - number_of_triangles(x)))`. No violation on defined arsenal instances; zero-denominator instances are not interpreted.

#### graphbrain-alpha-lower-082 — `RETRO_KILL`
`independence_number(x) >= floor(log(tan(order(x))^2)/log(10))`. Reverified existing certificate: `K11` has `alpha=1` and RHS `4`; all nontrivial connected graphs through order 10 pass.

#### graphbrain-alpha-lower-083 — `HOLD_ARSENAL`
`independence_number(x) >= tan(matching_number(x)/girth(x))/max_degree(x)`. No arsenal violation.

#### graphbrain-alpha-lower-084 — `HOLD_ARSENAL`
`independence_number(x) >= tan(max_even_minus_even_horizontal(x)*radius(x) + 1)`. Carrier RHS `tan(1)=1.5574... < 2`.

#### graphbrain-alpha-lower-085 — `HOLD_ARSENAL`
`independence_number(x) >= arcsinh(tan(e^sin(average_distance(x))))`. No arsenal violation on real-defined instances.

#### graphbrain-alpha-lower-086 — `HOLD_ARSENAL`
`independence_number(x) >= card_center(x)^minimum(card_cut_vertices(x), cos(order(x)))`. No arsenal violation.

#### graphbrain-alpha-lower-087 — `RETRO_KILL`
`independence_number(x) >= minimum(2*girth(x), matching_number(x) - max_degree(x))`. On `C9[K3]`, RHS `min(6,13-8)=5 > 4=alpha`. The full required gate passes.

#### graphbrain-alpha-lower-088 — `HOLD_ARSENAL`
`independence_number(x) >= tan(size(x) + szekeres_wilf(x))/order_automorphism_group(x)`. No arsenal violation using exact automorphism orders.

#### graphbrain-alpha-lower-089 — `HOLD_ARSENAL`
`independence_number(x) >= max_even_minus_even_horizontal(x)*tan(diameter(x)) - order_automorphism_group(x)`. No arsenal violation.

## Completion audit

Exact corpus-ID comparison confirms **89/89** lower entries appear above,
with no missing or duplicate ID. Verdict counts: **70 `HOLD_ARSENAL`, 9
`HOLD_TIGHT`, 6 `RETRO_KILL`, 2 `DB_REJECTED`, and 2 `SKIP_UNDEFINED`**.
The six retro-kills are 033, 055, 061, 071, 082, and 087. Entries 071 and
082 reuse their earlier standalone certificates; the four newly exposed
lines are independently executable in
`certificates/graphbrain-alpha-lower-033-055-061-087/`.

The primary issue remains open-as-posted and contains no follow-up resolution
comments. Exact-statement searches found no substantive indexed refutation of
033, 055, 061, or 087. That negative search is not proof of novelty, so all
six remain conservatively labeled `RETRO_KILL`, not “new open conjecture
kills.”
