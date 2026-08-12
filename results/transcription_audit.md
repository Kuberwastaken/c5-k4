# WOWII Transcription Completeness Audit

Date: 2026-08-12.
JSON audited: `/Users/kuber.mehta/Projects/breakthroughmaxxing/04-wowii/conjectures.json` (522 entries = 521 unique ids; `434a` + `434a-dup2` are the two page variants of 434a). Parsed July 2026.
Page source: LIVE fetch (2026-08-12) of `cms.dt.uh.edu/faculty/delavinae/research/wowII/` — files `all.html`, `open.html`, `resolved.htm`, `menu.htm`, `wowIIdefs.js` (in `../` of this results dir). `menu.htm` states **"last update 8/6/26"** — the page was edited AFTER the July parse. Wayback CDX enumerated to `../cdx.txt` (125 URLs) but not needed: live page is fresher than any snapshot.

Parsing notes: rows extracted as (marker td, id td, statement td); id cells sometimes split across tags (`<a name="conj31"><b>1</b></a><b>31.&nbsp;</b>`) and some rows use uppercase `<TD>/<B>` — both handled. Symbol-font mapping applied (a=α, d=δ, D=Δ, l=λ, m=μ, r=ρ, g=γ, £=≤; overline = complement).

Row counts parsed: `all.html` 528 rows / 527 unique ids; `open.html` 227 / 221; `resolved.htm` 317 / 307. **Page union: 531 unique ids** vs 521 in JSON.

---

## (a) Ids on the page but MISSING from the JSON — 10

| id | page marker | where | statement (decoded) | verdict |
|----|------|-------|-----------|---------|
| **136** | **O (open)** | all.html + open.html | If G is a simple connected graph, then path(G) ≥ (1+girth)/Δ(R) | **genuinely missing open conjecture** |
| **137** | **O (open)** | all.html + open.html | If G is a simple connected graph, then path(G) ≥ 4/p(Ḡ) | **genuinely missing open conjecture** |
| **138** | **O (open)** | all.html + open.html | If G is a simple connected graph, then path(G) ≥ (2+u(G))\*dist_min(M(G²)) | **genuinely missing open conjecture** |
| 131 | E | all.html + resolved.htm | If G is a simple connected graph, then path(G) ≥ circumference − 1 | missing, resolved (E) |
| 135 | T | all.html + resolved.htm | If G is a simple connected graph, then path(G) ≥ girth/δ(G) (July 12 2005, B. Waller) | missing, proved |
| 139 | F | all.html + resolved.htm | If G is a simple connected graph, then path(G) ≥ u(G)\*(1+2\*dist_avg(C)) (counterexample = the one for 105) | missing, refuted |
| 98 | F | resolved.htm ONLY (absent from all.html) | If G is a simple connected graph, then α(G) ≤ maximum of dist_even(v) + FLOOR[p(G)/2] (April 21 2004; refuted DeLaVina May 2004, ceconj98.gif) | missing, refuted |
| 384 | T | resolved.htm only | = JSON **384a** verbatim (γ₂ ≤ FLOOR(n − k_v/2)) | unlettered duplicate of 384a — no new content |
| 386 | T | resolved.htm only | = JSON **386a** verbatim (γ₂ ≤ n − max{\|N(u)∩N(v)\|}) | duplicate of 386a (note: resolved.htm marks it T, all.html marks 386a E) |
| 389 | F | resolved.htm only | = JSON **389b** (γ₂ ≤ q\*\|M\| + α(G[A])) | duplicate of 389b — no new content |

Root cause for 131/135–139: on `all.html` these six ids are written split across two `<b>` tags with an anchor between (`<b>1</b></a><b>35.</b>`); a naive parser reads "1". 132/133/134 don't have the split and were captured. 98 was missed because it appears only on `resolved.htm`, never on `all.html`.

So the only *material* misses are **98 (F), 131 (E), 135 (T), 136 (O), 137 (O), 138 (O), 139 (F)** — and of these, three are OPEN: **136, 137, 138**.

## (b) Ids in the JSON but not on the page — NONE

Every one of the 521 JSON ids appears on the current page. (Page numbering gaps 13, 16, 17, 42, 50, 67, 117, 220–225 etc. are gaps on the page itself, absent from JSON too — consistent.)

## (c) Status disagreements — 10 flips + 1 page-internal conflict

All 10 flips are in one direction: **JSON says open, current page says resolved** — every one carries a dated note of **July 20 – Aug 6, 2026** (i.e., resolved after the July parse; the July parse was correct at the time):

| id | page now | resolved by / note |
|----|----------|--------------------|
| 103 | F | July 20 2026, Chinmayan Pradeep (ChatGPT-assisted counterexample; triangle + 4 leaves on each of two triangle vertices, α=9 > bound 8). NOTE: 103 still physically listed on open.html but with marker F there too. |
| 141 | T | Aug 4 2026 DeLaVina proof, inspired by July 28 2026 AI-assisted sketch by Maeda Akihiro |
| 146 | T | July 21 2026 Brain Akaka human-readable proof (AI-collaborative) |
| 174 | F | July 23 2026 Apple Lamps counterexample (n=11), found with ChatGPT 5.6 Sol |
| 178 | T | July 23 2026 Austin Stubbs proof |
| 198a | T | July 22 2026 Ben Cohen (WSJ), AI-model proof, doi:10.5281/zenodo.21481944 |
| 200 | F | July 21 2026 Jitendra Prajapati, 11-vertex counterexample g6 `J??FFBRq}N_` |
| 209 | F | July 21 2026 Jitendra Prajapati, family K_m-based counterexamples (m ≥ 7) |
| 291 | F | July 23 2026 Zyad Tamimi, 12-vertex counterexample (γt=4, bound 3) |
| 300 | F | July 26 2026 William Weishuhn (CU Boulder), family with arbitrarily large violation; Codex-assisted verification |

Page-internal conflict: **391** is marker **O on open.html** but **F on resolved.htm** (July 24 2026 Ishan Chordia 7-vertex tree counterexample: γ₂=5 > p+1+μ+|E| = 4). JSON says open. Effectively refuted.

JSON-side deliberate overrides (page still says O; NOT transcription errors — these come from the Lean formal-conjectures repo / this project's own counterexamples): 34 (unclear), 58, 91, 109, 327, 430b (refuted), 143, 315 (proved).

Statement-text check: fuzzy diff of all 521 shared ids found **zero** statements below 0.82 similarity — no material transcription drift anywhere.

## (d) Section-header counts

Only two section headers on `all.html` carry T/F/O counts, and both are stale historical stamps:

- "Lower bounds for Total Domination γt **(50 T 8 F 20 O 22)**" — internally sums 8+20+22=50 ✓, but the section NOW holds 53 rows (ids 226–278): T 7, R 2, E 1, F 25, O 17, O* 1.
- "Upper bounds for Total Domination γt. **(34 T 9 F 12 O 14- 2/19/09)**" — internally sums 9+12+14=**35 ≠ 34** (off-by-one on the page itself), and the section NOW holds 51 rows (ids 279–329): O 26, F 14, T 7, R 4.

Menu.htm totals are likewise stale: Dalmatians (488), open (204), resolved (284), Sophie (52, T 20 F 10), resolvedT (149) — vs the actual current union of 531 unique ids, 220 O-marked unique ids on open.html, 307 unique on resolved.htm. Header/menu counts cannot be used for validation; row-level parsing is authoritative.

---

## Verbatim page wording of the 5 suspect ids

(Symbol-font glyphs decoded in braces; everything else literal, including the page's own typos.)

**448b** (all.html, marker O):
> Let G be a connected graph on n > 3 vertices. Then {α}<sub>2</sub>(G) {≤} |V-A| + |E(G[N(S)])| + {ρ}(G), where A is the set of vertices of minimum degree and S is the set of support vertices in G.

Raw: `<font face="Symbol">a<sub>2</sub></font>(G)<font face="Symbol">Â£ </font>...|V-A| + |E(G[N(S)])| + <font face="Symbol">r</font>(G)` — the `Â£` is Symbol-font `£` = ≤. **JSON matches exactly** (α_2 ≤ |V−A| + |E(G[N(S)])| + ρ(G)).

**412f** (open.html/all.html, marker O):
> Let G be a connected graph on n > 2 vertices, P the set of pendant vertices and H the union of all maximum critical independent sets of G. Then |H| ≥ {μ}(G[V-N(P)]), and if G is also bipartite then, then |H| ≥ number of components of G[V-N(P] + {μ}(G[V-N(P)]).

The doubled "then, then" and the unbalanced "G[V-N(P]" are **on the page itself**. **JSON matches exactly**, typos preserved.

**412d** (marker O):
> Let G be a connected bipartite graph on n > 2 vertices and H the union of all maximum critical independent sets of G. Then |H| ≥ γ<sub>T</sub>(G).

Page writes the subscript as capital T (`&gamma;<sub>T</sub>`). **JSON matches** (γ_T, formula gamma_t).

**97** (marker T):
> If G is a simple connected graph, then {α}(G) ≤ maximum of {λ}(v) - {δ}(<span overline>G</span>)

i.e. α(G) ≤ max λ(v) − δ(Ḡ), with δ taken of the **complement** (overline G on the page). **JSON matches** (`δ( bar(G) )`).

**64** (marker O):
> If G is a simple connected graph, then f(G) ≥ CEIL[(sqrt[{α}(G) * (1 + (n mod {Δ}(G))] ]

The brackets are unbalanced **on the page itself** (`CEIL[(sqrt[ ... (1 + (n mod Δ(G))] ]`). **JSON matches exactly**, unbalanced brackets preserved. Most natural reading: f(G) ≥ CEIL[ sqrt( α(G) · (1 + (n mod Δ(G))) ) ].

Conclusion: none of the 5 suspected transcription issues is a transcription issue — every quirk is verbatim on DeLaVina's page.

---

## New evaluations on C5[K4] — the 3 missing OPEN conjectures

Graph: C5[K4], 20 vertices, 5 K4-blobs on a cycle, complete join between adjacent blobs. Certified profile `../profile.json`: n=20, 11-regular, girth 3, α=2, radius=diameter=2 (every vertex central), radial circle per center = 8 vertices, G² = K20, 80 maximum independent sets, path(G) (largest **induced** path order, wowIIdefs def 35) = 4, complement = C5[4K1] (connected, Hamiltonian — explicit Ham path re-verified with networkx this session ⇒ path covering number p(Ḡ) = 1).

**Conjecture 136**: path(G) ≥ (1+girth)/Δ(R). Def 76: Δ(R) = max degree over vertices on radial circles (radial circle = vertices at distance radius from a center).
- Δ(R) = 11 (graph regular). RHS = (1+3)/11 = 4/11 ≈ 0.364. LHS = 4. **4 ≥ 4/11 — HOLDS** (huge slack).

**Conjecture 137**: path(G) ≥ 4/p(Ḡ). Def 12: p = path covering number; def 31: Ḡ = complement.
- p(Ḡ) = 1 (complement traceable, explicit Hamiltonian path verified). RHS = 4/1 = 4. LHS = 4. **4 ≥ 4 — HOLDS WITH EQUALITY.** C5[K4] is a tight (sharp) example, not a counterexample.

**Conjecture 138**: path(G) ≥ (2+u(G))·dist_min(M(G²)). Def 74: u(G)=1 iff G has a unique maximum independent set, else 0; def 19: M = set of max-degree vertices, dist_min(M) = min distance between them; def 75: G² = square.
- u(G) = 0 (80 maximum independent sets). G² = K20 ⇒ M(G²) = all 20 vertices ⇒ dist_min = 1 (distinct vertices; adjacent pairs exist — same value whether distance is measured in G or G²). RHS = (2+0)·1 = 2. LHS = 4. **4 ≥ 2 — HOLDS.** All alternate readings also hold (even u=1 would give 3 ≤ 4).

**No new C5[K4] violations found.** (137 is tight — equality, not violation.)

The other missing ids (98 F, 131 E, 135 T, 139 F, and duplicates 384/386/389) are resolved on the page; no evaluation needed.

---

## Bottom line

1. The July parse missed exactly **7 real conjectures** (98, 131, 135, 136, 137, 138, 139) plus 3 unlettered duplicate listings (384=384a, 386=386a, 389=389b). The only missed OPEN ones are **136, 137, 138** (path(G) lower bounds); none is violated by C5[K4]; 137 is met with equality.
2. Zero statement-text transcription errors across all 521 shared ids; the 5 "suspect" wordings (448b, 412f, 412d, 97, 64) are verbatim-faithful — the oddities (≤ as Symbol £, "then, then", unbalanced brackets in 64/412f) are DeLaVina's own.
3. The page moved after the parse (updated 8/6/26): **10 JSON-open conjectures are now resolved on the page** (T: 141, 146, 178, 198a; F: 103, 174, 200, 209, 291, 300), all July 20–Aug 6 2026, nearly all AI-assisted; plus **391** refuted (July 24 2026) though still listed on open.html with marker O.
