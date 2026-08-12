# WOWII Conjecture 309 — target paper + 2025–2026 WOWII/Graffiti.pc literature sweep

Compiled 2026-08-12. All raw source files in `../` (this scratchpad): `wowii309.pdf` + `wowii309.md` (full text of target paper), `all.html` / `wowIIdefs.js` (DeLaVina's WOWII source page), Zenodo JSON, companion-note PDFs/MDs.

## TARGET PAPER

**"An Infinite Family of Counterexamples to Written on the Wall II, Conjecture 309"**

### (a) Author and dates
- Sole author: **Jonas J. Gebendorfer** ("Jonas Jakob Gebendorfer" in metadata).
- Original venue: **Zenodo**, publication date **25 July 2026** (DataCite record created 2026-07-25T10:54:38Z). File: `WOWII_309_counterexample_note.pdf` (224,662 bytes).
- The ResearchGate page (publication id 410896849) is a **mirror upload**. RG is unreachable from every vector tried (see "access log" below); its exact upload date is not directly recoverable, but is ≥ 2026-07-25. The author's other RG mirrors carry DataCite dates 2026-07-31 (Conj 64 note, Conj 364 note) and 2026-08-09 (Conj 145 proof), so the RG 309 upload almost certainly falls in that late-July/early-August 2026 window.
- Acknowledges AI assistance: "OpenAI Codex assisted with candidate screening, exact finite computation, source and notation auditing, adversarial checking, and preparation of the reproducibility package and initial manuscript draft."

### (b) Statement of WOWII Conjecture 309 as given in the paper
For every simple connected graph G with n(G) > 2:

γ_t(G) ≤ B(G) := (1/2) [ max_{v∈V(G)} { d_e(v) − h_e(v) } + min_{e∈E(Ḡ)} |N_Ḡ(e)| ]

with the paper's literal definitions:
- d_e(v) = |{x ∈ V(G) : d_G(v,x) is even}| — **includes v itself** (distance 0 is even). This is WOWII "dist_even(v)".
- h_e(v) = |{xy ∈ E(G) : d_G(v,x) = d_G(v,y) and this common distance is even}| — WOWII "even horizontal(v)".
- **N_Ḡ(e) interpretation (the ambiguous term):** the paper takes e to be an **edge of the complement graph Ḡ** (i.e. a non-adjacent pair x,y of G) and the neighborhood computed **in Ḡ**: |N_Ḡ(e)| = |N_Ḡ(x) ∪ N_Ḡ(y)|, quoting WOWII definition entry 28 ("Let e=(u,v) such that u and v are adjacent in the graph. The neighborhood of e is the set of vertices adjacent to at least one of u or v") composed with entry 31 (complement). So: *neighborhood of an edge of the complement, in the complement* — equivalently the neighborhood-in-Ḡ of a non-edge of G. NOT "neighborhood of a non-edge computed in G".
- The paper explicitly audited this: "A source snapshot retrieved on 25 July 2026 was checked at the DOM level so that the overline on G in the edge-neighborhood term was not lost. The same statement, date, and status occur in an independently retained 2010 snapshot."
- Independently verified here against DeLaVina's live page (`cms.uhd.edu/faculty/delavinae/research/wowII/all.html`): row 309 is status **O** (open), dated **Mar. 1, 2007**, and the raw HTML for the last term is `|N<sub><span style="text-decoration: overline">G</span></sub>(e)|` — i.e. N with subscript G-overline. Its "definitions" link calls `printDefinitions(94, 10, 93, 28, 31)` = {γ_t, dist_even, even horizontal, neighborhood-of-an-edge, complement}. This matches the paper's reading exactly.
- Robustness remark in the paper: excluding v from d_e(v) (7→6 for k=3) or excluding endpoints from N(e) (12→10) still leaves the bound violated; "Neither convention repairs the conjecture."

### (c) The counterexample family
- **G_k = C₅[K_k], the lexicographic product of the 5-cycle with a k-clique ("clique blow-ups / blown-up 5-cycles"), for every k ≥ 3.** Five fibers F_0..F_4, each a k-clique, consecutive fibers completely joined.
- Closed forms proved: γ_t(G_k) = 3; max_v{d_e(v) − h_e(v)} = 2k+1 − k(2k−1) = −2k² + 3k + 1 (vertex-transitive, constant); Ḡ_k ≅ C₅[K̄_k]; min_{e∈E(Ḡ)} |N_Ḡ(e)| = 4k (four fibers).
- So B(G_k) = (−2k² + 7k + 1)/2 and B(G_k) − 3 = −(2k−5)(k−1)/2 < 0 for k ≥ 3.
- **First member: C₅[K₃], n = 15**, 8-regular, 60 edges; the conjecture there asserts 3 ≤ 2. graph6 code: `N~~ww{^?wF_^wFwF{Bw`. Concrete table: d_e(v)=7, h_e(v)=15, min|N_Ḡ(e)|=12, B=2. Exhaustive verifier output: #TDS₁=0, #TDS₂=0, #TDS₃=135.
- **C₅[K₄] (n = 20) is in the family** (k = 4), but the paper's smallest witness is k = 3. The paper explicitly credits the carrier: "The blow-up carrier C₅[K_m] was used publicly on 23 July 2026 to disprove the distinct WOWII Conjectures 63 and 85 [2]. That report does not discuss Conjecture 309, even-horizontal edges, or total domination. The present calculation is a new application of the carrier and already works for m = 3." Reference [2] = **Kuberwastaken, "Complete formal certification for the disproofs of WOWII Conjectures 63 and 85", GitHub issue #4590 (google-deepmind/formal-conjectures), 23 July 2026.**
- A dependency-free Python verifier (`verify_wowii_309.py`, stdlib only) accompanies the note. "No claim of order-minimality is made for the 15-vertex witness."

### (d) Other WOWII conjectures and the same family
- **Within the 309 note: none.** It resolves only 309 and mentions no other conjecture falling to the family except crediting the prior 63/85 disproof (Kuberwastaken's C₅[K₄], via issue #4590). **305, 308, and 310 are not mentioned at all.**
- Same author, companion note (26 July 2026): "Clique Blow-ups of the 5-Cycle and WOWII Conjecture 64" — **Conjecture 64 also falls to this carrier**: notes the prior Kuberwastaken C₅[K₄] certificate (n=20) already refutes 64 ("the earlier certificate has priority for this graph"), then gives a smaller 18-vertex counterexample B(4,4,3,4,3) (nonuniform blow-up), an infinite family, and proves 18 is order-minimal (and dihedral-unique) within positive C₅-clique-blow-ups.
- Status on DeLaVina's site as scraped 2026-08-12: **305 = O (open), 308 = O, 309 = O, 310 = O**; 306 = T (proved 2007), 307 = F, 311 = F (2007 counterexamples). No 2025–26 paper/preprint claiming 305, 308, or 310 was found anywhere in the sweep.
- For reference, site statements (γ_t = total domination number, same N_Ḡ(e) notation): 305: γ_t ≤ CEIL[(2/3)·max|N_Ḡ(e)|]; 308: γ_t ≤ (1/2)[maxine(G) + min|N_Ḡ(e)|]; 310: γ_t ≤ CEIL[1 + Tdist_min(v)/3]. 63 (O): f(G) ≥ CEIL[(min dist_even(v) + b(G) + 1)/3] (Mar 25 2004); 85 (O): tree(G) ≥ CEIL[sqrt(1 + 2·min dist_even(v))] (Apr 04 2004). (Site status letters lag reality; the maintainer has not updated them.)

### (e) DOI / mirrors
- **DOI: 10.5281/zenodo.21553295** (version); concept DOI 10.5281/zenodo.21553294. https://zenodo.org/records/21553295
- **No arXiv version exists** (arXiv API full-metadata search for "written on the wall": 0 hits as of 2026-08-12).
- ResearchGate mirror id 410896849 has **no RG-minted DOI** (no 10.13140 record in DataCite for the 309 title).
- The RG URL has **never been captured by the Wayback Machine** (CDX query empty), and the title is unindexed by Google, Bing, and Google Scholar (0 hits each).

### RG access log (all 403/blocked)
Attempted: direct curl (VPS, 403), WebFetch (403), r.jina.ai (DataDome CAPTCHA), headless Chromium on VPS via browse daemon (DataDome "Access restricted", Ray ID a29e35894bb594dd), curl and headless Chrome from the Mac's residential IP (DataDome JS challenge), Wayback CDX (no captures), Save-Page-Now (form flow, not pursued after Zenodo original was found). The Zenodo original made RG access unnecessary.

---

## SECONDARY SWEEP: 2025–2026 papers/preprints on WOWII / Graffiti.pc conjectures

All items below are 2026; nothing from 2025 was found. Everything traces to a burst starting ~21 July 2026 (the google-deepmind/formal-conjectures repo added WOWII batches in April–June 2026; PRs #3795 merged 2026-04-20, #3820 merged 2026-06-08).

### Papers / preprints (Zenodo, arXiv, ResearchGate)
| Date (first) | Conjecture(s) | Direction | Author | Venue / DOI |
|---|---|---|---|---|
| 2026-07-21 | WOWII 198a | proof (self-labeled "candidate proof", v0.1) | Ben Cohen | Zenodo 10.5281/zenodo.21481944 — "Average Eccentricity, Induced Bipartite Subgraphs, and Hamiltonian Paths" |
| 2026-07-22 | WOWII 194 | **disproof** (3-parameter infinite family; 18-vertex first member, Lean 4 verified) | Cameron Beeley | Zenodo 10.5281/zenodo.21498586 (+21498167/8) — "Infinite Counterexamples to WOWII Conjecture 194" |
| 2026-07-23 | WOWII 63, 85 | **disproof** (C₅[K₄], n=20; Lean 4 certificates) | Kuberwastaken | GitHub repo `Kuberwastaken/wowii-63-85-counterexample` + formal-conjectures issue #4590 / PR #4592 (no Zenodo/arXiv paper found) |
| 2026-07-25 | **WOWII 309** | **disproof** (C₅[K_k], k≥3; this sweep's target) | Jonas J. Gebendorfer | Zenodo 10.5281/zenodo.21553295; RG mirror id 410896849 |
| 2026-07-25 | WOWII 322 | proof + transcription correction (formal-conjectures entry omits the complement) | Jonas J. Gebendorfer | Zenodo 10.5281/zenodo.21553981 |
| 2026-07-25 | (related) claw-free bipartite–forest gap | — | Jonas J. Gebendorfer | Zenodo 10.5281/zenodo.21573353 — "The Bipartite–Forest Gap Is Unbounded in Claw-Free Graphs" |
| 2026-07-26 | WOWII 64 | **disproof** (via C₅[K₄] w/ credit to Kuberwastaken; new 18-vertex minimum B(4,4,3,4,3); infinite family) | Jonas J. Gebendorfer | Zenodo 10.5281/zenodo.21595503; RG DOI 10.13140/rg.2.2.21931.20008 (2026-07-31) |
| 2026-07-26 | Graffiti.pc 364 | formulation/status note | Jonas J. Gebendorfer | Zenodo 10.5281/zenodo.21592318; RG DOI 10.13140/rg.2.2.28642.08646 |
| 2026-07-27 | WOWII 141 | proof | Jun Qing | Zenodo 10.5281/zenodo.21621181 — "Extending an Induced Star Along a Geodesic" |
| 2026-07-27 | WOWII 387 | proof | Jun Qing | Zenodo 10.5281/zenodo.21621226 + arXiv 2607.27246 |
| 2026-07-27 | WOWII 314 | proof ("Triangle-Free P5-Free Graphs Are Well-Totally-Dominated") | Jun Qing | Zenodo 10.5281/zenodo.21622564 |
| 2026-07-27 | WOWII (Graffiti.pc) 2 | proof (L_s(G) ≥ 2(I_avg(G)−1); tight on balanced complete bipartite) | Yanmohan Wang, Tianyue Dai, Rui Tong | arXiv 2607.24020 |
| 2026-07-28 | WOWII 315, 317, 322 | proofs / structural resolutions (batch; 317 gets sharp WTD(2) classification, sole exception graph Ḡ ≅ C₄ ∪ (n−4)K₁ which fails the hypothesis, so the implication holds) | Jonas J. Gebendorfer | Zenodo 10.5281/zenodo.21650036 — "Three Well-Total-Domination Conjectures…" |
| 2026-08-02 | WOWII 316 | proof (≤3 non-pendant vertices forced; checked all 996 connected graphs to n=7) | Cavan Cohoes | Zenodo 10.5281/zenodo.21754513 |
| 2026-08-02 | WOWII 141, 142, 143 | proofs (Lean 4 ancillary files) | Alper Ferudun | arXiv 2608.01396 |
| 2026-08-03 | WOWII 40 (f ≥ ⌈(p+b+1)/2⌉) | **partial**: equivalent deficiency form ℓ+o ≥ 2τ+1; bipartite case reduced to 2 open lemmas; verified n ≤ 11 | Chris Ozols | Zenodo 10.5281/zenodo.21778700 |
| 2026-08-09 | WOWII 145 | proof | Jonas J. Gebendorfer | RG DOI 10.13140/rg.2.2.25953.47209 — "Peripheral Eccentricity and Local Independence in the Complement" (RG-only; page 403s) |

### Repo-level resolutions in google-deepmind/formal-conjectures (no standalone paper located)
Merged:
- **103 disproved** — CinnamonRolls1 — PR #4482, merged 2026-07-25 (11-vertex counterexample).
- **109 disproved** — marked via PR #4494 (DomTheDeveloper), merged 2026-07-21 (disproof PR #4493 closed unmerged).
- **143 marked solved** — PR #4442 (DomTheDeveloper), merged 2026-07-21; **142 marked solved** — PR #4457 (AlperTheKing), merged 2026-08-11 (paper = Ferudun arXiv 2608.01396).
- **65 disproved** — SamuelSchlesinger — PR #4514, merged 2026-08-06.
- **194 disproved** — anagnorisis2peripeteia — PR #4542, merged 2026-08-07 (paper = Beeley).
- **2 marked solved** — kingcharlezz — PR #4565, merged 2026-08-06 (paper = Wang–Dai–Tong).
- **217 marked solved (external Lean proof)** — KitaKen1 — PR #4656, merged 2026-08-04.
- 160 source fix — PR #4443 merged 2026-07-26; 22 and 34 statement fixes merged Apr–May 2026.

Open claims (as of 2026-08-12):
- 36 disproof certification (anagnorisis2peripeteia, PRs #4570/#4572 — "known disproof").
- 58 false with 31-vertex counterexample (hypnopump, PR #4634).
- 59 disproof, 18-vertex witness (anagnorisis2peripeteia, PRs #4573/#4574/#4582/#4583).
- 63 & 85 disproof (Kuberwastaken, PR #4592, closes #4590).
- 100 misformalization report (issue #4502); 19 solved (akakabrian #4559); 141+143 proofs (AlperTheKing #4454); 145 solved (DomTheDeveloper #4520); 146 solved (Mapika #4540); 160 source-corrected proof (anagnorisis2peripeteia #4569/#4575/#4576); 198a solved (lukekabbash #4597, paper = Cohen); 200 disproof (infinityscroll #4500); 209 disproof (infinityscroll #4508); 291 hypothesis fix (#4509); 314 solved (DomTheDeveloper #4496, paper = Qing); 322 corrected-form solved (#4497 closed); 40 status note (#4702, paper = Ozols).

### Not claimed by anyone (relevant to the 309 family)
WOWII **305, 308, 310** — no paper, preprint, or formal-conjectures PR claims them; all still "O" on DeLaVina's page. Both 305 and 308 use the same min/max |N_Ḡ(e)| term; 308 additionally uses maxine(G); 310 uses Tdist_min. (Not evaluated here whether C₅[K_k] violates them.)

### Search-index status of the target paper (2026-08-12)
- Google (via WebSearch): exact title 0 hits; Bing: 0 hits; Google Scholar: 0 hits for "Written on the Wall II Conjecture 309"; Wayback: never archived; local SearXNG: engines mangle quoted phrases, no hits. Discovery path that worked: **DataCite API** (`api.datacite.org/dois?query="Conjecture 309"`) → Zenodo record → PDF.
