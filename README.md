# C₅[K₄]

![C5[K4] — five K4 blobs on a cycle, complete join between adjacent blobs](assets/c5k4.png)

**One 20-vertex graph that became a counterexample-discovery program.**

C₅[K₄] is the lexicographic product of the 5-cycle with the complete graph K₄:
blow every vertex of a pentagon into a K₄ clique and join adjacent blobs
completely. It has 20 vertices, 110 edges, and it is 11-regular,
vertex-transitive, and diameter 2.

I found it on **2026-07-23** while systematically hunting through
E. DeLaViña's *Written on the Wall II* (WOWII / Graffiti.pc) conjecture
list, as a counterexample to Conjecture 85 — and it turned out to be a much
bigger deal than that. This repository maps, exhaustively, **everything in
the WOWII universe that this single graph closes**: I evaluated all 522
transcribed conjectures (220 open, 139 refuted, 163 proved/other) against
it, adversarially re-verified every violation, and cross-checked every
claim against the current literature and the
[google-deepmind/formal-conjectures](https://github.com/google-deepmind/formal-conjectures) race.

I then turned the same arsenal outward. On 2026-08-12 I completed durable,
entry-by-entry sweeps of **409 open Written on the Wall I conjectures**, **71
AutoGraphiX targets**, and the **16 evaluable open/generated TxGraffiti
records**. That expansion found two additional gate-surviving disproofs in
WoW I: #191 and #889. AutoGraphiX produced no claimable kill. The TxGraffiti
arsenal sweep produced no new kill, but a follow-up status audit found that its
harmonic-index conjecture had already been refuted externally; the sweep's
other curated apparent violation is a printed-statement erratum, not new
mathematics.

A further sweep covered all **228 independence-number bounds** still listed
as open in Graph Brain issue #421, all **178 resolved/annotated WoW I rows**,
all **94 WoW I source-recovery rows**, the current finite-graph declarations
in `google-deepmind/formal-conjectures`, and 12 nonduplicate major human
conjectures. It found one especially clean, apparently unrecorded
open-as-posted disproof: Graph Brain upper-081 is false on C₅[K₄], on a
9-vertex windmill, and on two infinite families.

## From one carrier to a discovery procedure

The project no longer stops at asking which published inequalities are
violated by `C₅[K₄]`. Its more general follow-up uses graphs that are exactly
tight as **local maps of conjecture space**:

1. find a graph or family on an equality wall;
2. identify the invariant that prevents it from crossing that wall;
3. move to a purpose-built family that changes that invariant while preserving
   the rest of the extremal structure;
4. require the candidate to pass the historical database-sanity gate,
   independent exact recomputation, source recovery, and a no-`sorry` Lean
   certificate.

That procedure has now produced three prospective structural transfers and one
prospective theorem recovery, not merely retrospective explanations of the
original four kills:

| Tightness map | Obstruction exposed | Deliberate separating family | New crossing |
|---|---|---|---|
| `C₅[K_m]` on the `L_s+b` frontier | `α=λ_max` prevents #181 from crossing | triangular graphs `T(n)` | #181 under the formalized square-degree reading |
| diameter-two equality wall around #176 | the selected square-degree vertices cannot separate in the original metric | two triangles joined by a long path (`D_L`) | #176, then adjacent #172 |
| regular clique blow-ups in the independent-domination cluster | center geometry and the Caro--Wei correction move together | nonuniform `P₇` clique blow-ups | #430a |
| repeated equality in #438b | matching edges seem able to evade both induced-subgraph corrections | low-degree false-twin layer | no crossing: the attempted separation yields a stronger arbitrary-subset theorem proving #438b |

The `P₇` crossing is especially important: it is the second instance in a
substantially different conjecture cluster of the same prospective pattern

`tight carrier → isolate obstruction → separate invariant → new counterexample`.

That is the expanding claim of this repository. `C₅[K₄]` remains the seed and
the best diagnostic carrier, but the research object is now the repeatable
navigation of tightness walls into new graph families. Direct carrier kills,
spawned counterexamples, retro-kills, and interpretation-dependent statements
remain counted separately below.

The development record also publishes its zeroes. Method v0.2 found no
crossing for #382e after 212,502 wall-directed substitutions, all connected
order-eight graphs, and 20,000 unrestricted-weight samples; and no crossing
for #61 across 968 nonisomorphic degree-preserving switch realizations. Both
end as bounded holds with sharply stated theorem signals, not inflated truth
claims. See [`method_v02_382e.md`](results/expansion/method_v02_382e.md) and
[`method_v02_61.md`](results/expansion/method_v02_61.md).

The programme-level roadmap is [`OVERARCHING_PLAN.md`](OVERARCHING_PLAN.md),
and the full versioned development protocol is [`METHOD.md`](METHOD.md). They fix
the residual-wall workflow, theorem-shadow taxonomy, transformation catalogue,
verification gates, outcome ledger, and the boundary between the current
`formal-conjectures` development set and a future genuinely held-out test.

### Versioned project releases

New apparently-unclaimed results are now published as one-problem releases in
this repository, after committed novelty, verifier, Lean, trust, immutable-link,
and tag-target gates. No new `formal-conjectures` issue or PR is opened by this
workflow.

- [WOWII 172: barbell-family counterexample and formal certificate](https://github.com/Kuberwastaken/c5-k4/releases/tag/wowii-172-v1)
- [WOWII 176: barbell-family counterexample and formal certificate](https://github.com/Kuberwastaken/c5-k4/releases/tag/wowii-176-v1)
- [WOWII 430a: nonuniform path-blow-up counterexample and formal certificate](https://github.com/Kuberwastaken/c5-k4/releases/tag/wowii-430a-v1)
- [WOWII 181: formalized square-degree reading counterexample and formal certificate](https://github.com/Kuberwastaken/c5-k4/releases/tag/wowii-181-v1)

Known externally claimed results such as WOWII 64 and 309 remain fully
formalized and credited in the repository, but are not republished as
apparently-unclaimed releases.

## The kills

Among the 220 WOWII conjectures that were still open in July 2026, C₅[K₄]
refutes **four**:

| # | Conjecture (DeLaViña's statement) | On C₅[K₄] | First refuted |
|---|---|---|---|
| **63** | f(G) ≥ ⌈(min dist_even(v) + b(G) + 1)/3⌉ | f = 4 < 5 = ⌈(9+4+1)/3⌉ | [me, 2026-07-23](https://github.com/google-deepmind/formal-conjectures/pull/4592) — this graph |
| **85** | tree(G) ≥ ⌈√(1 + 2·min dist_even(v))⌉ | tree = 4 < 5 = ⌈√19⌉ | [me, 2026-07-23](https://github.com/google-deepmind/formal-conjectures/pull/4592) — this graph |
| **64** | f(G) ≥ ⌈√(α(G)·(1 + n mod Δ))⌉ | f = 4 < 5 = ⌈√(2·(1+9))⌉ | [Gebendorfer, 2026-07-26](https://doi.org/10.5281/zenodo.21595503) — **this graph** (crediting my 63/85 certificate), + an 18-vertex minimum |
| **309** | γ_t(G) ≤ ½[max_v{dist_even(v) − even_horizontal(v)} + min_{e∈E(Ḡ)}\|N_Ḡ(e)\|] | γ_t = 3 > −3/2 = ½(−19 + 16) | [Gebendorfer, 2026-07-25](https://doi.org/10.5281/zenodo.21553295) — **this graph's family** C₅[K_k], k ≥ 3 (crediting the carrier) |

Here f, b, tree are the largest induced forest / bipartite subgraph / tree
(all equal **4** on C₅[K₄] — certified exhaustively over all 15,504
5-subsets, twice, by independent code paths); dist_even(v) = 9 for every
vertex (self counted); even_horizontal(v) = 28 for every vertex (the two
far blobs induce a K₈); γ_t = 3; and every complement edge has
|N_Ḡ(e)| = 16.

The two conjectures killed by Jonas J. Gebendorfer both explicitly ride
this carrier: his 309 note calls it "a new application of the carrier"
from my 63/85 disproof, and his 64 note states "the earlier certificate
has priority for this graph." I found one graph, once — and it is now four
dead conjectures across two independent research efforts.

The #64 kill is verified to an unusual standard: the parse is pinned by
the page's own `printDefinitions` links (def 32 = "n mod Δ"), the claimed
reading has **zero violations across all 995 connected graphs on ≤ 7
vertices** plus paths, cycles, complete multipartite graphs, Petersen,
hypercubes, Kneser graphs and C₅[K₂]/C₅[K₃] — and it is exactly tight on
DeLaViña's own K₃+3×K₁₂ refutation graph from the same page section. It
fails only on the C₅[K_m ≥ 4] cliff. That is the signature of a faithful
machine conjecture meeting the one graph its database never contained.
Complete no-`sorry` Lean certificates for both 64 and 309 are committed in
[`lean/`](lean/), with Gebendorfer's prior disproofs credited explicitly.

### Why it kills them: the discretization cliff

Graffiti.pc verified its conjectures against a finite graph database
(roughly n ≤ 11). C₅[K₄] lives exactly past the edge of that database on a
**rounding cliff**: its induced-substructure invariants are pinned at 4
(any 5 vertices either meet a blob twice — creating a stranded component or
a triangle — or induce the pentagon C₅, which is a cycle), while the
distance-parity terms in the bounds keep growing with the blob size. The
whole family C₅[K_m] shows the cliff sharply
([`scripts/family_sweep.py`](scripts/family_sweep.py)):

| m | n | f=b=tree | min dist_even | C63 RHS | C85 RHS | C64 RHS | verdicts |
|---|---|---|---|---|---|---|---|
| 1 | 5 | 4 | 3 | 3 | 3 | 2 | all hold |
| 2 | 10 | 4 | 5 | 4 | 4 | 2 | all hold |
| 3 | 15 | 4 | 7 | **4** | **4** | **4** | all hold, **all exactly tight** |
| 4 | 20 | 4 | 9 | 5 | 5 | 5 | **63, 85, 64 all violated** |
| 5 | 25 | 4 | 11 | 6 | 5 | 5 | all violated |

Analytically (m ≥ 4): f = b = tree = 4, α = 2, dist_even = 2m+1, and
n mod Δ = 5m mod (3m−1) = 2m+1, so all three right-hand sides exceed 4
forever. **Three conjectures, one family, equality at m = 3 and violation
at every m ≥ 4.** For 309 the cliff is even steeper: the family kills it
for every k ≥ 3, with plain C₅ sitting at exact equality (3 ≤ 3).

### The fifth kill — spawned by the carrier, executed by T(7)

The family sweep of the L_s + b lower-bound group (conjectures 174–186)
found the blow-ups **saturate that frontier without ever crossing it** —
exactly tight on up to 23 of 30 family members per conjecture. But the
saturation did two things. First, it **pinned the reading** of Conjecture
181 (`L_s + b ≥ α + deg_avg(B(G²))`): of its two gate-surviving parses,
only the deg_avg-measured-in-G² one is exactly tight on this carrier, and
Graffiti.pc's tightness discipline doesn't emit slack-8 bounds. Second,
it exposed the lever the blow-ups can't pull: the whole family has
α = λ_max, and violating 181 needs **α > λ_max**.

Feed that lever to a graph with tiny cliques and big independence — the
**triangular graph T(7) = L(K₇)**, the strongly regular (21,10,5,4)
graph — and 181 dies: diameter 2 makes G² = K₂₁ (deg_avg = 20), and
exhaustive computation (every relevant subset, twice, by independent
code) gives α = 3, b = 6, γ_c = 5 so L_s = 16. **LHS = 16 + 6 = 22 <
23 = 3 + 20 = RHS.** The triangular graphs T(n) for n ≥ 7 are an
infinite family of counterexamples with unboundedly growing margin
(closed forms: α = ⌊n/2⌋, b = n or n−1, L_s = n(n−1)/2 − n + 2...,
confirmed exhaustively through T(11)). The violation is
**reading-dependent** (the in-G parse of deg_avg holds with slack 9) and
is documented as such. The complete no-`sorry` Lean certificate is
[`lean/GraphConjecture181.lean`](lean/GraphConjecture181.lean); the upstream
submission is tracked in [formal-conjectures issue #4905](https://github.com/google-deepmind/formal-conjectures/issues/4905)
and [draft PR #4907](https://github.com/google-deepmind/formal-conjectures/pull/4907).

One graph killed four conjectures; its tightness frontier then aimed the
next shot. Full analysis: [`results/family_forest.md`](results/family_forest.md).

### Two more WoW I kills

The expansion into Fajtlowicz and DeLaViña's earlier *Written on the Wall I*
corpus produced two candidates that survived the same four-step protocol:
exact statement recovery, a complete applicable small-graph database gate,
independent recomputation, and a targeted novelty check.

| # | Conjecture | Counterexample | Exact failure |
|---|---|---|---|
| **191** | If `sum Odd ≤ sum Even`, minimum deficiency ≤ \|E\|/ω | `T(7) = L(K₇)` | `20 > 105/6`; in fact every `T(n)`, `n ≥ 7`, fails |
| **889** | A connected regular triangle-free graph has a blue clique on `w/4` vertices | complement of `C₅[K₄]` | blue clique number `1 < 8/4 = 2` |

Both disproofs have complete no-`sorry` Lean certificates:
[`#191`](lean/GraphConjecture191.lean) and
[`#889`](lean/GraphConjecture889.lean).

The first is another T(n) lever: for `T(n)`, minimum deficiency is
`(n−2)(n−3)` while `|E|/ω = n(n−2)/2`. The second uses the complement of the
carrier, which is connected, 8-regular, triangle-free, and diameter 2; every
vertex therefore has `w=8`, while the #822 blue graph has no edges.

The complete per-entry audits are
[`results/expansion/wow1_part1.md`](results/expansion/wow1_part1.md) and
[`results/expansion/wow1_part2.md`](results/expansion/wow1_part2.md).

### A second structural transfer: WOWII 176

The sharpness follow-up also found a new infinite counterexample family to
WOWII 176. Join distinguished vertices of two triangles by a path of `L`
edges. The family pins `L_s=4`, has `b=L+3`, and separates the two
maximum-degree vertices of its square by distance `L-2` back in the original
graph. Thus `L_s+b=L+7<2L+3=n+dist_min(M^2)` for every `L>=5`.
For `L>=7` it also violates the alternative reading that measures the distance
inside `G^2`, so this is not dependent on the notation ambiguity. The complete
source audit, structural derivation, database gate, and exact verifier are in
[`wowii_176_disproof.md`](results/expansion/wowii_176_disproof.md). The
no-`sorry` Lean certificate is [`GraphConjecture176.lean`](lean/GraphConjecture176.lean);
the upstream submission is [issue #4910](https://github.com/google-deepmind/formal-conjectures/issues/4910)
and [PR #4911](https://github.com/google-deepmind/formal-conjectures/pull/4911).

The same family also closes nearby WOWII 172: its periphery vertices have
degree 2, so 172 reduces to the false requirement `4>=L-1`. It fails under the
published reading for `L>=6` and under both readings for `L>=9`; details are in
[`wowii_172_disproof.md`](results/expansion/wowii_172_disproof.md). Its
no-`sorry` Lean certificate is [`GraphConjecture172.lean`](lean/GraphConjecture172.lean);
the upstream submission is [issue #4908](https://github.com/google-deepmind/formal-conjectures/issues/4908)
and [PR #4909](https://github.com/google-deepmind/formal-conjectures/pull/4909).

### Crossing a different wall: WOWII 430a

The same procedure succeeds in a substantially different independent-
domination cluster. A nonuniform `P7` clique blow-up with blob orders
`(1,4,12,19,12,4,1)` has `i=3`, center-neighborhood independence 2, and
`CW=51123/25585<2`; hence 430a falsely asserts `3<=2`. Uniform scaling gives
an infinite family. This is the clean second example of
`tight wall -> identify obstruction -> separate the controlling invariant ->
cross`: eccentricity asymmetry shrinks the center term while dense cliques pin
the Caro--Wei correction below its integer cliff. Full audit:
[`wowii_430a_disproof.md`](results/expansion/wowii_430a_disproof.md). The
no-`sorry` Lean certificate is [`GraphConjecture430a.lean`](lean/GraphConjecture430a.lean);
the upstream submission is [issue #4912](https://github.com/google-deepmind/formal-conjectures/issues/4912)
and [PR #4913](https://github.com/google-deepmind/formal-conjectures/pull/4913).

### A Graph Brain kill — and an order-9 witness

The complete 228-entry Graph Brain sweep found one source-faithful result
that survives the full protocol and appears not to have been recorded before.
Upper-081, still present in the author's open issue, asserts

```text
independence_number(G) <= 2*diameter(G)/(edge_connectivity(G)-vertex_connectivity(G)).
```

On C₅[K₄], `(alpha, diameter, edge connectivity, vertex connectivity) =
(2, 2, 11, 8)`, so the asserted upper bound is `4/3 < 2`, an exact failure by
`2/3`. More generally, C₅[K_m] has right side `4/(m-1)`: it is tight at
`m=3` and false for every `m>=4`.

There is an even smaller structural witness. Take two K₅s sharing exactly
one vertex (order 9, graph6 `H~}CKMF`). It has `(alpha,D,lambda,kappa) =
(2,2,4,1)`, hence the same false right side `4/3`. For the windmill made from
`t` copies of K_s sharing one hub, the values are `alpha=t`, `D=2`,
`lambda=s-1`, and `kappa=1`; the bound fails whenever `t(s-2)>4`.

All 995 nontrivial connected Graph Atlas graphs through order 7 pass under
the author's evaluator semantics (58 have a nonzero denominator; zero is
mapped to `+Infinity`). The exact statement, invariant definitions,
independent recomputation, named controls, source/status search, and
machine-readable certificate are in
[`results/expansion/graphbrain_upper.md`](results/expansion/graphbrain_upper.md)
and [`certificates/graphbrain-alpha-upper-081/`](certificates/graphbrain-alpha-upper-081/).
A no-`sorry` Lean draft formalizes the source semantics and proves the exact
invariant-tuple reduction in
[`GraphBrainAlphaUpper081.lean`](lean/GraphBrainAlphaUpper081.lean); proving
the four concrete windmill equalities awaits a connectivity API absent from
the current mathlib snapshot.
The claim here is deliberately narrow: **apparently unrecorded and open as
posted**, not proof of absolute bibliographic priority.

### Further reach found by the exhaustive follow-up

- The other 227 Graph Brain bounds produced eight gate-surviving
  open-as-posted retro-kills: lower-033, 055, 061, 071, 082, 087 and
  upper-066, 069. Simple witnesses make these stale falsehoods rather than
  serious novelty claims. The two complete ledgers contain exact verdicts
  for all 89 lower and 139 upper bounds.
- The complement family `H_m = complement(C5[K_m])`, `m>=3`, is a connected
  infinite counterexample family to already-refuted WoW I #724. On `H_m`,
  the asserted left side is `3m-2` while `alpha=2m`; C₅[K₄]'s complement
  gives `10>8`. The historical source recorded only disconnected `2C5`, so
  this connected family appears to be new evidence for an old refutation.
- Six more resolved WoW I rows (#23, 29, 55, 124, 166, 188) acquire
  additional carrier-family witnesses. No proved theorem was contradicted;
  row #207 instead exposes a metadata defect because its stored statement
  duplicates proved row #43.
- The current formal-conjectures sweep and 12-target human-conjecture sweep
  found no additional disproof. They did prove a useful sharpness identity:
  `chi(C5[K_m]) = ceil(5m/2) = ceil((Delta+1+omega)/2)`, so the family meets
  Reed's bound exactly for every `m`.

Full records: [`graphbrain_lower.md`](results/expansion/graphbrain_lower.md),
[`wow1_resolved_part1.md`](results/expansion/wow1_resolved_part1.md),
[`wow1_resolved_part2.md`](results/expansion/wow1_resolved_part2.md),
[`formal_conjectures.md`](results/expansion/formal_conjectures.md), and
[`breakthrough_targets.md`](results/expansion/breakthrough_targets.md).

### It would have killed eight more

Sweeping the 139 WOWII conjectures that were *already refuted* by others:
C₅[K₄] is also a counterexample to **24, 25, 46, 49, 52, 54, 55, 56**
(and to 77 under the member-eccentricity reading) — almost all of them in
the same forest-number/bipartite-number section, where dense-regular
correction terms (n mod Δ, dist_even, complement length) blow past
f = b = 4. Had this graph been in anyone's database, it would have
pre-empted eight-plus refutations. Numbers per conjecture in
[`results/refuted_sweep/`](results/refuted_sweep/).

## Where it is exactly tight (sharpness gallery)

Beyond the kills, C₅[K₄] achieves **zero-slack equality** in a striking
number of still-open WOWII bounds — it is an extremal witness for:

| # | Bound | Value on C₅[K₄] |
|---|---|---|
| 19 | b ≥ ⌊avg ecc + max λ(v)⌋ | 4 = ⌊2 + 2⌋ |
| 174 | L_s + b ≥ n + max λ(v) − 1 | 21 = 20 + 2 − 1 |
| 176 | L_s + b ≥ (bound) | 21 = 21 |
| 183, 184, 185 | L_s + b families | 21 = 21 |
| 382e | γ₂ ≤ maxine + γ | 4 = 2 + 2 |
| 401b | γ₂ ≤ ⌊3·Tdist_max / freq[T_max(v)]⌋ | 4 = ⌊81/20⌋ |
| 422b | i(G) ≤ α(G[M]) + γ(∅)² | 2 = 2 + 0 |
| 430a | i(G) ≤ α(G[N(C)]) + 2⌊CW − 1⌋ | 2 = 2 + 0 |
| 438b | α₂ ≤ a(G) + a(G[V−H₂]) + \|E(G[H₂])\| | 4 = 2 + 2 + 0; now proved by a stronger arbitrary-subset theorem ([PR #4916](https://github.com/google-deepmind/formal-conjectures/pull/4916)) |

It is just as tight against the **proved** part of the corpus — a
zero-slack witness of theorems 4, 7, 15, 16, 18, 37, 57, 68, 89, 94, 99,
173, 382a, 409a, 411, 420a, 451, 452, and 458 (e.g. L_s = 17 =
min|N(ē)| − 1; b = 4 = 2·rad = 2α; α = 2 = b − λ_min; and α₂ = 4 = 2α
pinned simultaneously by three different theorems), and of already-refuted
bounds 219, 289 (γ_t = p + ⌈b/2⌉ = 3), 424, and 430b. Two curios from the sweep: for refuted
traceability conjectures the graph can never be a witness (it is
Hamiltonian, so their conclusions hold), and the literal transcription of
**proved theorem 97** (α ≤ λ_max **−** δ(Ḡ)) is falsified by C₅[K₄] — and
by C₅ and Petersen — so the published minus sign must be a plus lost in
the Symbol-font transcription; the corrected bound α ≤ λ_max + δ(Ḡ) is
provable and holds here with slack 8.

(Readings and exact numbers per conjecture in
[`results/open_sweep/`](results/open_sweep/).) A graph this tight against
this many independent bounds is exactly the profile of a database-edge
extremal object — Graffiti.pc "knew" this territory to m = 3 and
conjectured right up against it.

## What it does *not* close (the honest part)

The sweep's whole point is knowing where the graph's reach ends:

- **305, 308, 310** (the other γ_t bounds): hold with slack 5+ — the
  carrier does not touch them.
- The **well-total-dominated characterizations (314–328)**: C₅[K₄] is *not*
  well-total-dominated (minimal TDS {0,1,8,9} of size 4 > γ_t = 3), but
  every antecedent fails on it, so all escape vacuously. Closest call: 314,
  saved only by the graph's 260 triangles.
- All tree-hypothesis sections (γ_t-of-trees, 34x, 35x–38x, 404–407) and
  bipartite-hypothesis conjectures: not applicable — the graph is neither.
- **412f and 448b** appear violated under the literal statement — and I
  audited the live page (2026-08-12): the transcription is
  verbatim-faithful, so the weirdness is on DeLaViña's page itself. But
  the literal statements are also violated by K₄ (412f, under DeLaViña's
  own note that |H| = 0 for regular graphs of degree > n/2) and by every
  Kₙ (448b) — graphs certainly in Graffiti.pc's database, which the
  program checked before emitting conjectures. The published wording is
  therefore presumed corrupted between Graffiti.pc's output and the page;
  a "kill" of a page typo is empty, so these are **not** claimed. The
  adversarial verification went further: as published, 412f is violated
  by 62% of all connected graphs on ≤ 7 vertices (K₃ included) and 448b
  by C₄ itself, while every sane repair of either statement is satisfied
  by C₅[K₄]. (Verbatim page quotes in
  [`results/transcription_audit.md`](results/transcription_audit.md),
  full adversarial analysis in
  [`results/verification.md`](results/verification.md).)
- **Transcription-audit bonus**: the July community parse of the page
  missed three open conjectures entirely (136, 137, 138 — the path(G)
  sub-list, hidden by split HTML id cells). I recovered and evaluated
  them: none violated; **137 is yet another exact tie**
  (path = 4 = 4/p(Ḡ), the complement being Hamiltonian). The audit also
  found the page itself moved on 2026-08-06: ten conjectures listed as
  open in July are now marked resolved by others (proved: 141, 146, 178,
  198a; refuted: 103, 174, 200, 209, 291, 300, and 391) — the WOWII race
  is that fast right now.

Everything else among the 220 open WOWII conjectures: holds, with margins
recorded per-conjecture in the sweep data. The later expansion reports keep
`SKIP_OCR`, non-applicable, and database-rejected readings explicit rather
than silently turning damaged statements into claims.

## Where this weapon points next

The kill signature, stated precisely: on C₅-blowups the **hereditary
induced invariants are pinned at tiny constants** (α = 2, f = b = tree =
induced path = 4, λ(v) = 2, γ_t = 3 — growing the blobs adds zero
independent structure) **while density and distance terms grow freely**
(Δ = 3m−1, dist_even = 2m+1, n mod Δ = 2m+1), and vertex-transitivity +
regularity + diameter 2 **collapse the set machinery** (center =
periphery = M = A = V, G² = Kₙ, H = ∅, maxine = α). Any conjecture that
lower-bounds a pinned invariant by a growing term, or feeds a collapsed
set into a correction term, is in the kill zone.

The corollary that guides targeting: this graph murders
**machine-generated conjectures with finite verification databases** —
no automated conjecturer's database ever contained a dense
vertex-transitive diameter-2 graph past n ≈ 15 — but it is nearly
useless against human conjectures, because humans sanity-check dense
regular graphs instinctively. Ranked targets:

1. **WOWII — full carrier sweep complete; structural follow-up active** (this
   repo, as of 2026-08-12): open sweep (223 incl. 3 recovered), refuted sweep
   (139), proved QA (163), both family sweeps (30+ members), transcription
   audit, and adversarial verification all reported. The original carrier
   score is 4 direct kills + spawned 181 + 8 retro-kills. Follow-up navigation
   of its tightness walls has now additionally disproved 172, 176, and 430a,
   with purpose-built families, and proved the formerly open 438b by a
   stronger universal inequality. The carrier family itself cannot cross the remaining walls —
   it sits at exact equality on them (window-argument proofs in
   [`results/family_domination.md`](results/family_domination.md)).
   For the diameter-two `L_s+b` cluster 176/182--185, that equality is now
   explained exactly: every statement collapses to the already-proved WOWII
   173 baseline `L_s+b>=n+1` (DeLaViña--Waller 2008), so this common-wall
   search is impossible rather than merely unsuccessful. See
   [`wowii_173_wall.md`](results/expansion/wowii_173_wall.md).
   Three more entries (401b, 412f, 448b) are corrupt as published
   (violated by stars/K₄/C₄ inside Graffiti.pc's own database) and can
   only be hunted from DeLaViña's original output: the Wayback follow-up
   reached the earliest available captures (2010 for 401b/412f, 2016 for
   448b) and found the same corrupt wording already present there.
2. **Written on the Wall I — swept**: all 409 eligible open/unannotated
   records, all 178 resolved/annotated records, and all 94 rows carrying a
   source/OCR gap now have durable audits. I found #191 and #889 plus the
   connected #724 retro-family; damaged definitions and unrecoverable source
   text remain explicit rather than guessed. Every lane has zero missing,
   extra, or duplicate IDs.
3. **AutoGraphiX — swept**: all 71 targets now have verdicts. Forty-five
   hold on the arsenal, 24 remain unreadable/missing-definition, one is
   inapplicable and already proved, and the only apparent violation fails
   the small-graph gate. Full audit:
   [`results/expansion/agx.md`](results/expansion/agx.md).
4. **TxGraffiti / Optimist — swept**: all 16 evaluable open/generated
   records were checked. The arsenal itself yields no new kill; the printed
   `Z`/γ_t cubic statement is an erratum that K₃,₃ exposes, and the raw
   Optimist equality is trivially false. The μ*/H inequality is strict on
   C₅[K₄] (`9 < 10`), but is already externally false: the friendship graph
   `F4` has `μ*=4 > 18/5=H`. Full audit and status correction:
   [`txgraffiti.md`](results/expansion/txgraffiti.md),
   [`txgraffiti_status_followup.md`](results/expansion/txgraffiti_status_followup.md).
5. **Graph Brain / CONJECTURING — swept**: all 228 open-as-posted alpha
   bounds now have exact ledgers. Upper-081 is the one apparently unrecorded
   source-faithful kill; eight more are conservatively recorded as retro-kills,
   48 upper bounds fail the small-graph gate, and 19 already have
   counterexamples in the author's own source.
6. **google-deepmind/formal-conjectures beyond WOWII — swept at current
   upstream**: 77 current open finite-graph declarations were classified;
   23 were concretely applicable and none failed. Twelve major human
   conjectures likewise produced no kill.

Where it is useless, equally worth knowing: asymptotic/extremal
statements, anything with tree/bipartite/triangle-free/planar/sparse
hypotheses (the graph is none of these), and human structural
conjectures.

## The graph, in numbers

All values exact, computed by [`scripts/profile_c5k4.py`](scripts/profile_c5k4.py)
and cross-checked analytically ([`data/profile.json`](data/profile.json)):

| invariant | value | invariant | value |
|---|---|---|---|
| n, m | 20, 110 | degree | 11-regular, vertex-transitive |
| diameter, radius | 2, 2 | girth | 3 (260 triangles; T(v) = 39) |
| α (independence) | **2** | ω (clique) | 8 (two adjacent blobs) |
| f, b, tree, induced path | **4, 4, 4, 4** | induced circumference | 5 |
| γ, γ_t, γ_i, γ₂, γ_c | 2, 3, 2, 4, 3 | L_s (max spanning-tree leaves) | 17 |
| μ (matching) | 10 (perfect) | path cover p | 1 (Hamiltonian) |
| dist_even(v), dist_odd(v) | 9, 11 (every v) | even/odd horizontal(v) | 28, 39 (every v) |
| residue, annihilation | 2, 10 | maxine | 2 |
| κ (connectivity) | 8 | Tdist(v) | 27 (every v) |
| λ(v) (local independence) | 2 (every v) | critical independence α′ | 0 (H = ∅) |
| well-total-dominated | **no** | G² | K₂₀ |
| complement | connected, 8-regular, triangle-free, diameter 2 (blown-up C₅) | | |

## Reproduce

```sh
python3 -m venv .venv && .venv/bin/pip install networkx pulp matplotlib
.venv/bin/python scripts/profile_c5k4.py     # full certified invariant profile
.venv/bin/python scripts/family_sweep.py     # the C5[K_m] cliff table
.venv/bin/python scripts/render.py           # the README image
```

The full sweep data lives in [`results/`](results/) (one JSONL verdict per
conjecture, with every reading of every ambiguous statement evaluated), the
WOWII transcription in [`data/wowii-conjectures.json`](data/wowii-conjectures.json),
and DeLaViña's verbatim invariant definitions (recovered from her
`wowIIdefs.js` via the Wayback Machine) in
[`data/INVARIANT-GLOSSARY.md`](data/INVARIANT-GLOSSARY.md).

## References

- E. DeLaViña, [*Written on the Wall II — Conjectures of Graffiti.pc*](http://cms.dt.uh.edu/faculty/delavinae/research/wowII/)
- **Conjectures 63 & 85 (mine)** — [wowii-63-85-counterexample](https://github.com/Kuberwastaken/wowii-63-85-counterexample):
  my complete Lean 4 proofs (no `sorry`, no custom axioms), independent
  verifiers, and the counterexample certificates.
  Upstream: [formal-conjectures PR #4592](https://github.com/google-deepmind/formal-conjectures/pull/4592),
  [issue #4590](https://github.com/google-deepmind/formal-conjectures/issues/4590).
- **Conjecture 181 (spawned by the carrier)** — complete Lean 4 certificate
  [`GraphConjecture181.lean`](lean/GraphConjecture181.lean).
  Upstream: [formal-conjectures draft PR #4907](https://github.com/google-deepmind/formal-conjectures/pull/4907),
  [issue #4905](https://github.com/google-deepmind/formal-conjectures/issues/4905).
- **Conjecture 309** — J. J. Gebendorfer, *An Infinite Family of
  Counterexamples to Written on the Wall II Conjecture 309*, Zenodo,
  2026-07-25. [doi:10.5281/zenodo.21553295](https://doi.org/10.5281/zenodo.21553295)
- **Conjecture 64** — J. J. Gebendorfer, *Clique Blow-ups of the 5-Cycle and
  WOWII Conjecture 64*, Zenodo, 2026-07-26.
  [doi:10.5281/zenodo.21595503](https://doi.org/10.5281/zenodo.21595503)
- Discovery pipeline — [breakthroughmaxxing](https://github.com/Kuberwastaken/breakthroughmaxxing)
  (`04-wowii/`): my ranked open-target list whose construction surfaced
  this graph, plus hunt engines and calibration.

## Provenance

I ran the 2026-08-12 exhaustive campaign as a parallel agentic pipeline
across Claude Code and Codex: evaluation agents covered the original 522
WOWII records and every expansion lane, every VIOLATED verdict was
independently re-derived by an adversarial verifier instructed to *save*
the conjecture, plus literature and repo-race sweeps. Transcriptions of
DeLaViña's statements are inherently lossy; every kill claimed above
survives all plausible readings, and every reading-sensitive case is
documented in the sweep data rather than claimed.
