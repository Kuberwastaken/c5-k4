# C₅[K₄]

![C5[K4] — five K4 blobs on a cycle, complete join between adjacent blobs](assets/c5k4.png)

**One 20-vertex graph that keeps killing conjectures.**

C₅[K₄] is the lexicographic product of the 5-cycle with the complete graph K₄:
blow every vertex of a pentagon into a K₄ clique and join adjacent blobs
completely. It has 20 vertices, 110 edges, and it is 11-regular,
vertex-transitive, and diameter 2.

It was found on **2026-07-23** during a systematic hunt through E. DeLaViña's
*Written on the Wall II* (WOWII / Graffiti.pc) conjecture list, as a
counterexample to Conjecture 85 — and it turned out to be a much bigger deal
than that. This repository maps, exhaustively, **everything in the WOWII
universe that this single graph closes**: all 522 transcribed conjectures
(220 open, 139 refuted, 163 proved/other) were evaluated against it, every
violation adversarially re-verified, and every claim cross-checked against
the current literature and the
[google-deepmind/formal-conjectures](https://github.com/google-deepmind/formal-conjectures) race.

## The kills

Among the 220 WOWII conjectures that were still open in July 2026, C₅[K₄]
refutes **four**:

| # | Conjecture (DeLaViña's statement) | On C₅[K₄] | First refuted |
|---|---|---|---|
| **63** | f(G) ≥ ⌈(min dist_even(v) + b(G) + 1)/3⌉ | f = 4 < 5 = ⌈(9+4+1)/3⌉ | [Kuberwastaken, 2026-07-23](https://github.com/google-deepmind/formal-conjectures/pull/4592) — this graph |
| **85** | tree(G) ≥ ⌈√(1 + 2·min dist_even(v))⌉ | tree = 4 < 5 = ⌈√19⌉ | [Kuberwastaken, 2026-07-23](https://github.com/google-deepmind/formal-conjectures/pull/4592) — this graph |
| **64** | f(G) ≥ ⌈√(α(G)·(1 + n mod Δ))⌉ | f = 4 < 5 = ⌈√(2·(1+9))⌉ | [Gebendorfer, 2026-07-26](https://doi.org/10.5281/zenodo.21595503) — **this graph** (with credit to the 63/85 certificate), + an 18-vertex minimum |
| **309** | γ_t(G) ≤ ½[max_v{dist_even(v) − even_horizontal(v)} + min_{e∈E(Ḡ)}\|N_Ḡ(e)\|] | γ_t = 3 > −3/2 = ½(−19 + 16) | [Gebendorfer, 2026-07-25](https://doi.org/10.5281/zenodo.21553295) — **this graph's family** C₅[K_k], k ≥ 3 (with credit to the carrier) |

Here f, b, tree are the largest induced forest / bipartite subgraph / tree
(all equal **4** on C₅[K₄] — certified exhaustively over all 15,504
5-subsets, twice, by independent code paths); dist_even(v) = 9 for every
vertex (self counted); even_horizontal(v) = 28 for every vertex (the two
far blobs induce a K₈); γ_t = 3; and every complement edge has
|N_Ḡ(e)| = 16.

The two conjectures killed by Jonas J. Gebendorfer both explicitly ride
this carrier: the 309 note calls it "a new application of the carrier"
from the 63/85 disproof, and the 64 note states "the earlier certificate
has priority for this graph." One graph, found once, now four dead
conjectures across two research groups. **Conjectures 64 and 309 are still
unclaimed in formal-conjectures** (no files, PRs, or issues as of
2026-08-12) — Lean formulations in the house style are drafted in
[`lean/`](lean/).

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
| 438b | α₂ ≤ a(G) + a(G[V−H₂]) + \|E(G[H₂])\| | 4 = 2 + 2 + 0 |

It is just as tight against the **proved** part of the corpus — a
zero-slack witness of theorems 4, 7, 15, 16, 18, 37, 57, 68, 89, 94, 99,
and 173 (e.g. L_s = 17 = min|N(ē)| − 1; b = 4 = 2·rad = 2α;
α = 2 = b − λ_min), and of already-refuted bounds 219, 289 (γ_t = p +
⌈b/2⌉ = 3), 424, and 430b. Two curios from the sweep: for refuted
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
- **412f and 448b** appear violated under the literal transcription, but the
  literal transcription is also violated by K₄ (412f, under DeLaViña's own
  H-convention note) and by every Kₙ (448b) — graphs certainly in
  Graffiti.pc's database. These are transcription/interpretation artifacts
  until the original page wording says otherwise; they are **not** claimed
  as kills. (Verification details in [`results/`](results/).)

Everything else among the 220 open conjectures: holds, with margins
recorded per-conjecture in the sweep data.

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
- **Conjectures 63 & 85** — [Kuberwastaken/wowii-63-85-counterexample](https://github.com/Kuberwastaken/wowii-63-85-counterexample):
  complete Lean 4 proofs (no `sorry`, no custom axioms), independent
  verifiers, and the counterexample certificates.
  Upstream: [formal-conjectures PR #4592](https://github.com/google-deepmind/formal-conjectures/pull/4592),
  [issue #4590](https://github.com/google-deepmind/formal-conjectures/issues/4590).
- **Conjecture 309** — J. J. Gebendorfer, *An Infinite Family of
  Counterexamples to Written on the Wall II Conjecture 309*, Zenodo,
  2026-07-25. [doi:10.5281/zenodo.21553295](https://doi.org/10.5281/zenodo.21553295)
- **Conjecture 64** — J. J. Gebendorfer, *Clique Blow-ups of the 5-Cycle and
  WOWII Conjecture 64*, Zenodo, 2026-07-26.
  [doi:10.5281/zenodo.21595503](https://doi.org/10.5281/zenodo.21595503)
- Discovery pipeline — [Kuberwastaken/breakthroughmaxxing](https://github.com/Kuberwastaken/breakthroughmaxxing)
  (`04-wowii/`): the ranked open-target list whose construction surfaced
  this graph, plus hunt engines and calibration.

## Provenance

The 2026-08-12 exhaustive sweep (all 522 conjectures × this one graph) was
run as a parallel agentic pipeline (Claude Code): 10 evaluation agents over
the open/refuted/proved partitions, every VIOLATED verdict independently
re-derived by an adversarial verifier instructed to *save* the conjecture,
plus literature and repo-race sweeps. Transcriptions of DeLaViña's
statements are inherently lossy; every kill claimed above survives all
plausible readings, and every reading-sensitive case is documented in the
sweep data rather than claimed.
