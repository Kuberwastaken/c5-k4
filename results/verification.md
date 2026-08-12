# Adversarial verification: C5[K4] vs WOWII #64, #412f, #448b

Verifier session 2026-08-12. Role: try to SAVE each conjecture; kill stands only if no defensible
reading survives. All computations exact, run under /home/ec2-user/.venvs/wowii/bin/python
(networkx 3.2.1 + pulp/CBC). Scripts in
/tmp/claude-1000/-Users-kuber-mehta-Projects-scratch/21f73cfa-6e97-457f-8bb8-ae31d911cc43/scratchpad/wowii309/
(core.py, c64_atlas.py, c412f.py, h_lib.py, c412f_variants.py, c448_atlas.py, solvers.py).

**Ground truth obtained**: DeLaVina's original page recovered from the Wayback Machine
(fetched via `ssh mac` because the VPS IP was rate-limited):
`http://web.archive.org/web/20161109113252id_/http://cms.uhd.edu:80/faculty/delavinae/research/wowII/all.html`
(796,423 bytes, saved at `.../scratchpad/wowii309/wb/all_2016.html`) plus the site's definitions
database `wowIIdefs.js` (capture 20220130133625, 122 defEntries, saved at `.../wb/wowIIdefs.js`).
Every claim below about "the page" is from these captures.

## Graph facts (all recomputed from scratch)

C5[K4]: n=20, 110 edges, connected, 11-regular (Δ=δ=11).
- α = 2 (max clique of complement, exhaustive; also α(G[H])=α(G)α(H) for lex product).
- f = 4. Exhaustive: **none of the C(20,5)=15504 5-subsets induces a forest**; (0,1,8,9) induces
  2K2. Forests are hereditary, so no larger subset can induce one. f=4 exactly.
- μ = 10 (perfect matching; nx.max_weight_matching).
- P (pendants) = ∅.
- α₂ (2-independence = dissociation) = 4. Exhaustive: no 5-subset induces max degree ≤ 1;
  (0,1,8,9) does. Hereditary ⇒ α₂ = 4 exactly.
- Hamiltonian cycle 0,1,…,19,0 exists ⇒ path covering number p(G) = 1.
- Independent sets: ∅ (diff 0), 20 singletons (|S|−|N(S)| = 1−11 = −10), 80 nonadjacent pairs
  (2−18 = −16). Max of |S|−|N(S)| over independent sets = 0, attained ONLY by ∅.
  ⇒ H (union of maximum critical independent sets, empty set allowed) = ∅, |H| = 0.
  Under a nonempty-sets-only convention: max = −10 attained by all 20 singletons ⇒ H = V, |H| = 20.
- Spectral radius = 11 (regular).

All numbers claimed by the earlier analysis reproduce exactly.

---

## #64 — VERDICT: KILL_CONFIRMED

Page text (verbatim, capture 2016; unbalanced brackets are on the page itself):
`f(G) ≥ CEIL[(sqrt[α(G) * (1 + (n mod Δ(G))] ]`, marker O, note "Mar 25, 2004",
section "2nd run on Lower bounds on the forest number". The conjectures.json transcription is
character-faithful to the page.

**Decisive**: the page's definitions link for #64 is `printDefinitions(41,5,32,16,0)`:
def 41 = f(G) (forest number), def 5 = α(G), **def 32 = "n modulus maximum degree: for Δ(G) ≥ 2,
n mod Δ(G) is the remainder upon division of n by Δ(G)"**, def 16 = CEIL.
So "n mod Δ(G)" is an atomic invariant of the conjecture; Δ(C5[K4]) = 11 ≥ 2 so it is defined,
and equals 20 mod 11 = 9.

Readings evaluated on C5[K4] (α=2, m = n mod Δ = 9):
| reading | RHS | f=4 vs RHS |
|---|---|---|
| R1 `ceil(sqrt(α·(1+m)))` (natural parse) | ceil(√20)=5 | **VIOLATED** |
| R2 `ceil(sqrt(α)·(1+m))` | 15 | violated, but reading refuted (646/995 atlas violations) |
| R3 `ceil(sqrt(α+m))` | 4 | holds — but requires deleting the page's `* (1` tokens; not a bracket placement |
| R4 `ceil(sqrt(α·((1+n) mod Δ)))` | 5 | **VIOLATED** (the only other bracket-defensible parse) |
| R5 `ceil(sqrt((α·(1+n)) mod Δ))` | 3 | holds — but moves `mod` outside the def-32 atom; excluded by def link |
| R6 `ceil(sqrt(α))+m` | 11 | violated, but reading refuted (39 atlas violations) |
| Δ mod n variant | ceil(√24)=5 | violated; reading refuted anyway (fails K5: RHS 3 > f 2) |
| n mod δ | δ=Δ=11, identical | violated |

The def-32 atom + the `*` on the page pin the formula to R1 (R4 is the only other completion of
the missing bracket, and it also gives 5). Every "saving" reading (R3, R5, Δ mod n) requires
altering tokens that are demonstrably on the page or contradicts the definitions link, and Δ mod n
is additionally false on K5.

Sanity of R1 (claimed reading) — holds with **0 violations on all 995 connected graphs with
2 ≤ n ≤ 7** (networkx atlas, f and α brute force), and on: paths, cycles C3–C12, K2–K10,
K_{m,m}, K_{m,m+1}, stars, wheels, Q3 (f=5 ≥ 4), Q4 (f=12 ≥ 3), Petersen (f=7 ≥ 3),
K_{2,2,2} (3 ≥ 3 tight), K_{3,3,3} (4 ≥ 4 tight), grid 3×3, Kneser(7,2) (f ≥ α=6 ≥ 4),
C5[K2] (4 ≥ 2), C5[K3] (4 ≥ 4 tight), C7[K3] (6 ≥ 5), C7[K4] (6 ≥ 5).
Strongest single check: DeLaVina's own dense refutation graph from the same page section
(K3 with a K12 attached at each triangle vertex, used by her in Mar 2004 to kill #45/#46, hence
in the DB before the 2nd run that produced #64): n=36, Δ=13, α=3, f=6 (ILP);
R1 = ceil(√33) = 6 — **holds with equality**. A Dalmatian-heuristic conjecture being tight on a
database graph is exactly the expected signature of a correctly transcribed machine conjecture.

Failure profile: R1 fails only on the C5[K_m] cliff (C5[K4]: 4 < 5; C5[K5]: n=25, Δ=14,
m=11, f=4 < 5) where α collapses to 2 while n mod Δ spikes. This is the "holds on standard
graphs, fails on the cliff" signature the task defines as a credible kill.

**#64 kill stands. f=4 < 5 = ceil(sqrt(2·(1+9))). No defensible saving reading exists.**

---

## #412f — VERDICT: KILL TECHNICALLY TRUE UNDER THE AUTHOR'S STATED CONVENTION, BUT WORTHLESS —
## K3 is already a counterexample; under the only convention that makes the conjecture sane, C5[K4] complies (SAVED)

Page text (verbatim, capture 2016): "Let G be a connected graph on n > 2 vertices, P the set of
pendant vertices and H the union of all maximum critical independent sets of G. Then
|H| ≥ μ(G[V-N(P)]), and if G is also bipartite then, then |H| ≥ number of components of
G[V-N(P] + μ(G[V-N(P)])." Marker O, June 2010. Definitions link `printDefinitions(105,100,46,2,0)`:
105 = critical independence number α′ ("critical independent set S is independent with
|S|−|N(S)| ≥ |U|−|N(U)| for any independent subset U" — U includes ∅), 100 = G[S], 46 = N(S),
2 = μ. Transcription faithful; there is no defEntry for H itself anywhere in the 122 definitions.

The 410a quote IS verbatim on the page (410a comment cell): "For regular graphs of degree
greater than n/2, |H| = 0 and so the only open question is: if G is k-regular with k ≤ n/2, then
|H| ≤ |E(G[D_e])|?" — this pins DeLaVina's own convention: the empty set counts, and for
regular graphs of degree > n/2 (C5[K4]: 11 > 10) H = ∅.

On C5[K4]: P = ∅ ⇒ V−N(P) = V ⇒ RHS = μ(G) = 10; |H| = 0 < 10. Violation reproduces.

**Why the kill is worthless — the same convention kills K3.** For ANY connected regular graph, no
nonempty independent S has |S| ≥ |N(S)| unless the graph is bipartite-regular-splittable; for
degree > n/2 it is provably impossible. So under the author's convention:
- K3 (n=3 > 2, hypothesis satisfied): |H| = 0 < μ = 1. Smallest possible counterexample.
- K4, K5, K6, C5, K_{2,2,2}, wheel6, C5[K2], C5[K3], Petersen (H=∅ by direct computation),
  all violate. Atlas sweep: **614 of 994 connected graphs with 3 ≤ n ≤ 7 violate 412f under the
  empty-set convention** (first: K3). A statement false on 62% of all small connected graphs was
  never a live conjecture; C5[K4] is roughly the six-hundredth counterexample by size, not a find.
- Even under the H-nonempty rescue convention, 224/994 atlas graphs still violate, including
  convention-independent ones: g6 `E~AG` (K4 + pendant path attached, n=6, edges
  (0,1)(0,2)(0,3)(0,5)(1,2)(1,3)(2,3)(4,5)): pendant P={4}, every convention gives H = {4}
  (the pendant singleton uniquely attains max diff 0 among nonempty sets, ∅ ties at 0),
  |H| = 1 < μ(G[V−N(P)]) = μ(K4 ∪ K1) = 2. So the published statement is false at n=6 with NO
  convention dispute — the June 2010 page statement cannot be what Graffiti.pc verified against
  its database (the α₂/H-era sections were actively human-vetted: 447 carries a "Feb. 2013, DPW
  see a counterexample" note while 412f stayed O).

Saving readings tried on C5[K4]:
1. H from nonempty critical sets only ⇒ H = all 20 singleton-attainers ⇒ |H| = 20 ≥ 10. SAVED.
   (But contradicts the author's verbatim 410a note, and the statement still dies on `E~AG`.)
2. "Maximum critical independent set" = maximum independent set that is critical ⇒ none ⇒ H=∅,
   same as empty convention (683/994 atlas violations — worse).
3. Union of ALL critical sets (not just maximum ones): identical here (∅ only); 614 violations.
4. RHS reparses: μ(G[V−N[P]]) — identical for P=∅ (10). "μ(G)[V−N(P)]" is not well-formed.
5. RHS with N(P)-shape like sibling 412a ("|H| ≥ c_L(G[N(P)])", noted "easily true since
   P ⊆ H"): |H| ≥ μ(G[N(P)]) has **0 violations on the whole atlas under both conventions** and
   gives RHS = μ(G[∅]) = 0 ≤ |H| on C5[K4] — SAVED. This is the only μ-variant that makes 412f
   sane, suggesting the page's "V−" in the first part is the author's own slip (the bipartite
   part with V−N(P) is fine: 0 atlas violations).
6. Hypothesis rescue "P ≠ ∅ implied": then C5[K4] is out of scope entirely — SAVED vacuously.

Every route ends the same way: either the conjecture is read so that C5[K4] complies, or it is
read so that K3/E~AG already refute it trivially. **C5[K4] is not a meaningful counterexample to
412f under any reading. Do not claim this kill.**

---

## #448b — VERDICT: TRANSCRIPTION_GARBLED (garble is on DeLaVina's page itself); kill worthless — C4 already violates the published text; every sane repair is satisfied by C5[K4]

Page text (verbatim, capture 2016): "Let G be a connected graph on n > 3 vertices. Then
α₂(G) ≤ |V-A| + |E(G[N(S)])| + ρ(G), where A is the set of vertices of minimum degree and S is
the set of support vertices in G." Marker O, Jan. 2012. The conjectures.json transcription is
faithful — including the where-clause.

**ρ is pinned by the page**: the definitions links of BOTH 448a and 448b are
`printDefinitions(118,12,100,0,0)`: def 118 = α_k (k-independent set = induced max degree
≤ k−1), **def 12 = p(G), "the minimum number of vertex disjoint paths needed to cover the
vertices"**, def 100 = G[S]. Sibling 455 (same Jan 2012 run) also glosses ρ(·) as "the path
covering number" in its where-clause. So ρ(G) = path covering number; ρ(C5[K4]) = 1 (Ham path).

As published on C5[K4]: A = V (regular) ⇒ |V−A| = 0; no leaves ⇒ S = ∅ ⇒ |E(G[N(S)])| = 0;
RHS = 1 < α₂ = 4. Violation reproduces. BUT as published it is equally violated by:
- C4 (n=4 > 3): α₂ = 2 > 0+0+1 = 1. Minimal counterexample.
- C5: 2 > 1. K4: 2 > 1. Petersen: α₂ = 6 > 1. Every connected regular graph with a Hamiltonian
  path and n > 3. Atlas sweep: **62 of 992 connected graphs with 4 ≤ n ≤ 7 violate the published
  statement** (first: C4 `Cl`, K4 `C~`).
Contrast: sibling 448a as published has **0 violations on the same 992 atlas graphs** (its
|H_{n/2}| term = n on dense regular graphs). The garble is localized to 448b, on the page itself.
A Graffiti.pc output tested on any database containing C4/C5 could not be this statement; the
section was human-vetted (447 refuted Feb 2013) while 448b stayed O — the published line is a
hand-typing slip (all conjectures were hand-typed FrontPage HTML), not the machine conjecture.

Alternative ρ-meanings tried (to save the published text): p(G), radius, diameter, residue,
packing number, domination number, matching number, spectral radius, longest-path order,
p(G[N(S)]) replacing the last two terms — **every one has 4-or-5-vertex atlas counterexamples**
(p: 62 violations incl. C4; rad: 47; diam: 28; residue: 20 incl. K4; packing: 60; γ: 46; μ: 13;
spectral radius fails Petersen: 6 > 3). No reading of ρ saves the published formula, because for
regular graphs the first two terms vanish and α₂(C_n) = ⌊2n/3⌋ outruns every candidate.

Reconstruction: replacing the first term |V\A| by |V\S| (the shape used by neighboring
conjectures 446 and 450, which read "α₂ ≤ pN(A) + |V\S|" and "α₂ ≤ pN(A₂) + |V\S| + pN(V\H₃)")
gives `α₂(G) ≤ |V\S| + |E(G[N(S)])| + ρ(G)` with **0 violations on all 992 atlas graphs**.
(For calibration on stars K_{1,9}: as published RHS = |V\A| + 0 + p = 1+0+8 = 9 = α₂, tight;
repaired RHS = 9+0+8 = 17, loose but valid.) Either way, on C5[K4] the
repaired statement gives RHS = 20+0+1 = 21 ≥ 4 — **no violation**. Any repair that survives
small graphs must have a term ≳ n on regular graphs, so C5[K4] (α₂ = 4 ≤ 20) can never violate
a sane repair.

**Corrected-statement verdict: exact intended statement not recoverable from the page (candidate:
A→S typo as above, satisfied by C5[K4]); the published text is refuted by C4, so a C5[K4] "kill"
of 448b is meaningless. Do not claim.**

---

## Bottom line

| conj | verdict | C5[K4] numbers | minimal counterexample to the literal text |
|---|---|---|---|
| 64 | **KILL_CONFIRMED** | f=4 < 5 = ceil(sqrt(α(1+(n mod Δ)))) = ceil(√(2·10)); def-link pins the parse; 0 atlas violations otherwise; tight on DeLaVina's own K3+3×K12 | C5[K4] (n=20) is genuinely the interesting object; C5[K5] also violates (4 < 5) |
| 412f | **NOT A USABLE KILL** (author-convention violation is trivial: K3; sane conventions/readings are satisfied by C5[K4]) | |H|=0 vs μ=10 under her 410a convention; |H|=20 ≥ 10 under nonempty convention; RHS=0 under the only atlas-clean μ-variant | K3 (n=3); convention-free counterexample `E~AG` (n=6) |
| 448b | **TRANSCRIPTION_GARBLED at source; not a usable kill** | α₂=4 > 1 as published, but RHS ≥ 21 under any atlas-clean repair | C4 (n=4) |

Recommended claim: **only #64**. If staking the C5[K4] graph, #64 is a clean, exhaustively
verified counterexample to an open, correctly-transcribed, 22-year-old Graffiti.pc conjecture.
Presenting 412f/448b as additional kills would not survive review: their literal statements are
already falsified by K3 and C4 respectively, i.e., the published texts are defective, not the
mathematics of C5[K4].
