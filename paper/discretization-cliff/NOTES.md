# Drafting notes — `paper/discretization-cliff/main.tex`

Draft written 2026-08-15. Target scope fixed by
`results/review/INDEPENDENT_REVIEW_2026-08-15.md` §6: the discretization-cliff case study, and
nothing broader. This file records exactly what is proved, what is asserted on the strength of
computation, where citations are unverified, and where a referee will push.

**Build status:** compiles cleanly. `pdflatex` 3 passes, **0 errors, 0 warnings, 0 overfull
boxes, 14 pages** (article, 10pt, a4paper, 1in margins). `microtype` is not installed on this
box, so the `\usepackage` is wrapped in `\IfFileExists`; it will load on a full TeX install
without changing the page count materially. Figure is `../../assets/c5k4.png` (386 KB, the
existing repo asset — no new figure assets were created).

---

## 1. What is proved rigorously (complete proofs in the paper)

| # | Statement | Status |
|---|---|---|
| Lemma 3.1 | Blob profile lemma: if `G[S]` is triangle-free in `H[K_m]` then `s_i ≤ 2`; `s_i = 2` forces `s_j = 0` for all `j ∈ N_H(i)`; `G[S] ≅ \|A\|K₂ ⊔ H[B]`; and every admissible `(A,B)` is realised when `m ≥ 2` | **Proved.** Elementary, complete, both directions. |
| Thm 3.2(i) | `α(H[K_m]) = α(H)` | **Proved.** Two lines, both directions. |
| Thm 3.2(ii) | `path ≤ tree ≤ f ≤ b ≤ 2α(H)` on `H[K_m]`, independent of `m` | **Proved.** The chain is class inclusion; `b ≤ 2α` is the elementary bound composed with (i). |
| Thm 3.2(iii)(iv) | `F(H) ≤ F(H[K_m])`; if `path(H) = 2α(H)` then all four numbers equal `2α(H)` for every `m ≥ 1` | **Proved.** |
| Cor 3.3 | `C_{2r+1}[K_m]`: `α = r`, `path = tree = f = b = 2r`, all `m ≥ 1` | **Proved** from 3.2. Independently checked computationally for `k ∈ {5,7,9}`. |
| Prop 3.4 | Exact `F(H[K_m])` profile formula for any hereditary triangle-free class; constancy in `m ≥ 2`; `≤ 2α(H)` when the class is bipartite | **Proved.** |
| Prop 3.5 | Growth: `n = km`, regularity, `ω(H[K_m]) = m·ω(H)`, `diam(H[K_m]) = diam(H)`, the `dist_even` formula | **Proved.** |
| Prop 3.6 | Cliff principle (pinned vs. divergent term; last surviving member is an equality case when the term lands on the pinned value) | **Proved**, but it is nearly a tautology. Its role is framing, and the paper says so. |
| Prop 4.1 | `C₅[K_m]`: `n`, `\|E\|`, regularity, vertex-transitivity, `diam = rad = 2`, `α = 2`, `ω = 2m`, `γ = 2`, `γ_t = 3`, `γ_c = 3`, `L_s = 5m−3`, `λ(v) = 2` | **Proved.** The three domination numbers are proved by the blob-covering argument, not asserted from the sweep. |
| Prop 4.2 | `dist_even = 2m+1`, `even_horizontal = m(2m−1)`, `Ḡ ≅ C₅[K̄_m]` (2m-regular, triangle-free, diam 2), `min\|N_Ḡ(e)\| = 4m`, `n mod Δ = 2m+1` for `m ≥ 3` (with the `m = 1, 2` exceptions stated) | **Proved.** |
| Thms 5.1–5.4 | The four conjecture right-hand sides in closed form, with exact thresholds and exact equality indices | **Proved.** Each is a short computation from Props 4.1–4.2. |

The pinning proof the task asked to be written properly is Theorem 3.2. Note that the argument
in the README ("2 in a blob strands a component or makes a triangle; ≤ 1 per blob gives an
induced C₅") is **not** the argument used. The written proof is shorter and airtight:

```
path ≤ tree ≤ f ≤ b ≤ 2α   (class inclusions + the elementary b ≤ 2α)
α(C₅[K_m]) = α(C₅) = 2      (one vertex per blob; blob indices independent in C₅)
⇒ all four ≤ 4
one vertex in each of B₀,B₁,B₃,B₄ induces P₄  ⇒ all four ≥ 4.
```

The README's blob-counting argument is retained in spirit as Lemma 3.1 + Prop 3.4, where it does
real work (it gives the exact value for arbitrary `H` and proves stabilisation in `m`).

## 2. What is computation, not proof

These are stated in the paper as computational results with a named script or data file, and are
**not** claimed as theorems:

1. **Corpus tallies** (Section 7): 522 records = 220 open + 139 refuted + 163 proved; open
   verdicts 167 holds / 47 n-a / 6 violated; refuted 101 / 29 / 8 (+1 reading-dependent);
   proved 98 holds + 19 tight / 45 n-a / 1 anomaly. These are tallies of the `verdict` fields
   in `results/{open,refuted,proved}_sweep/*.jsonl`, re-derived for this draft.
2. **The eight retro-kill right-hand sides** (Table 3). The LHS/RHS values at `m = 4` come from
   `results/refuted_sweep/`; I re-derived all eight independently in
   `verify_paper_claims.py` and they match exactly (5, 8, 6, 8, 6, 6, 15, 5 against LHS 4). The
   paper asserts these grow in `m` via Prop 3.5, which covers `dist_even`, `n mod Δ`,
   `deg_avg(Ḡ)` and `length(Ḡ)`; it does **not** give per-conjecture closed forms in `m`, only
   the identification of the growing term. A referee could reasonably ask for those closed
   forms; they are easy but were left out for length.
3. **The sharpness lists** (19 proved / 12 open / 4 refuted / conjecture 137). Read off the
   sweep files and `results/family_forest.md`. See §4 below for a caveat on the count.
4. **The database-sanity gate figures**: 995 connected graphs of order ≤ 7 for 63/85/64;
   989 of 994 applicable with 0 violations and 36 equalities for 309. The latter is printed by
   `scripts/verify_wowii_309.py`, which I ran (passes, 0.22 s). `scripts/verify_wowii_64.py`
   also ran and passes (0.04 s). `scripts/family_sweep.py` ran and reproduces Table 1's
   63/85/64 columns exactly.
5. **`scripts/profile_c5k4.py` does not run in this environment** — it imports `pulp`, which is
   not installed here. `data/profile.json` is the committed artefact and every profile value the
   paper actually uses was independently recomputed in `verify_paper_claims.py`. The paper says
   this in the reproducibility section rather than implying the script was run.

New file added alongside the paper: **`verify_paper_claims.py`** (self-contained, exact
arithmetic, `networkx` only). It re-derives every closed form in Sections 4–5 for `m = 1..6`,
the odd-cycle pinning for `C₅/C₇/C₉`, the carrier profile, and the eight retro-kill RHS values.
It passes end-to-end (runtime ≈ 70 s on 1 core). This was added because the task requires every numerical
claim to be reproducible from a named script and no existing repo script covers the general-`m`
309 closed form or the odd-cycle corollary.

## 3. `[CITATION NEEDED]` markers and citation verification

**One `[CITATION NEEDED]` remains in the text**, in the "On the database boundary" remark at the
end of Section 6:

> the exact contents of the database used for the 2004–2007 WOWII runs are not published, as far
> as we can determine **[CITATION NEEDED]**.

Reason: the repo's README asserts "Graffiti.pc verified its conjectures against a finite graph
database (roughly n ≤ 11)". **I could not verify the `n ≤ 11` figure anywhere.** It appears
nowhere in the repo with a source, and DeLaViña's own Graffiti.pc paper is unreachable from this
host (`cms.dt.uh.edu` times out over HTTP and refuses HTTPS; WebFetch upgrades to HTTPS and
fails). The paper therefore **does not use the `n ≤ 11` claim at all**. It states instead a
verifiable lower bound on where the failure begins (all 995 connected graphs of order ≤ 7 satisfy
the conjectures) and explicitly disclaims knowledge of `n₀`. Before submission, someone with
access should either (a) find the database description in DeLaViña, *Graffiti.pc: A Variant of
Graffiti*, DIMACS 69, pp. 71–79, or in *Some History of the Development of Graffiti*, DIMACS 69,
pp. 81–118, and cite it; or (b) leave the disclaimer as written. Do **not** reinstate "n ≤ 11"
without a source.

**Citations verified against primary/authoritative sources during drafting:**

| Reference | Verified | How |
|---|---|---|
| Fajtlowicz, *On conjectures of Graffiti*, Discrete Math. **72** (1988) 113–118 | ✅ | DOI 10.1016/0012-365X(88)90199-9; ACM DL + Semantic Scholar agree on volume/pages/year |
| DeLaViña, *Graffiti.pc: A Variant of Graffiti*, DIMACS **69** (2005) 71–79 | ✅ | DIMACS Vol. 69 official table of contents, page 71 |
| DeLaViña, *Some History of the Development of Graffiti*, DIMACS **69** (2005) 81–118 | ✅ | Same TOC (starts p. 81; next item starts p. 119) |
| Larson, *A Survey of Research in Automated Mathematical Conjecture-Making*, DIMACS **69** (2005) 297–318 | ✅ | Same TOC (starts p. 297; next item starts p. 319) |
| Larson & Van Cleemput, *Automated conjecturing I*, Artificial Intelligence **231** (2016) 17–38 | ✅ | ScienceDirect S0004370215001575 |
| Caporossi & Hansen, *VNS for extremal graphs. 1. The AutoGraphiX system*, Discrete Math. **212** (2000) 29–44 | ✅ | DOI 10.1016/S0012-365X(99)00206-X |
| Aouchiche & Hansen, *A survey of automated conjectures in spectral graph theory*, LAA **432** (2010) 2293–2322 | ✅ | ScienceDirect S0024379509003061; MR2599861 |
| Davila, *Automated conjecturing in mathematics with TxGraffiti*, Ann. Math. Artif. Intell. (2026); arXiv:2409.19379 | ✅ | arXiv abstract page: journal DOI 10.1007/s10472-026-10005-5, v2 2026-05-11 |
| Davila, *The Optimist: Towards Fully Automated Graph Theory Research*, arXiv:2411.09158 | ✅ | arXiv abstract page, 2024-11-14, sole author |
| Davila, Brimkov & Pepper, *In Reverie Together*, arXiv:2507.17780 | ✅ | arXiv abstract page, 2025-07-23; **no journal ref** — cited as preprint |
| DeLaViña & Waller, *Spanning trees with many leaves and average distance*, EJC **15** (2008) #R33 | ✅ | combinatorics.org record v15i1r33 |
| Firsching et al., *Formal Conjectures*, arXiv:2605.13171 (2026) + the GitHub repo | ✅ | repo README citation block + arXiv abstract page (11 authors, listed in full) |
| Geller & Stahl, *The chromatic number and other functions of the lexicographic product*, JCTB **19** (1975) 87–95 | ⚠️ mostly | Volume/issue/pages/year confirmed via ScienceDirect 0095895675900763. The abstract explicitly lists "point independence number" among the functions treated, which is what the paper cites it for — but **I did not read the paper**, so the exact form of the independence-number statement there is unconfirmed. The paper hedges ("one of the functions treated by"). |
| Gebendorfer, Zenodo DOIs 10.5281/zenodo.21595503 (Conj. 64) and 10.5281/zenodo.21553295 (Conj. 309) | ✅ | Verified in `results/literature.md`, which records the DataCite metadata, dates, and quoted text. I did not re-fetch the PDFs; the closed forms quoted there match my independent derivations exactly. |
| DeLaViña, *Written on the Wall II* page + `wowIIdefs.js` | ⚠️ | The live site is **unreachable from this host** (curl times out). Cited as a page with a stated snapshot date (2026-08-12) plus archived captures. The transcription, statuses, and dates in the paper come from `data/wowii-conjectures.json`, `data/INVARIANT-GLOSSARY.md` and `results/transcription_audit.md`, all of which record their own provenance. |

**No reference in the bibliography was invented, and no page number was guessed.** Every page
range came from an authoritative TOC or publisher record.

## 4. Numbers where I departed from, or tightened, the README

- The task brief said "~40 tight". **The defensible count is ≈ 36**, and the paper says "roughly
  three dozen": 19 proved theorems (verdict `TIGHT` in `results/proved_sweep/`), 12 open
  conjectures at zero slack under *gate-surviving* readings, 4 already-refuted bounds, plus
  conjecture 137. A naive parse of the sweep files finds zero-slack readings for 17 open records,
  but four of those (133, 142, 144, 146) are tight only under readings the database-sanity gate
  **discarded**, and one (401b) is corrupt as published. The paper excludes all five.
- The brief said "f = b = tree = 4 for m ≥ 2". The correct statement is **for every m ≥ 1**;
  `C₅` itself has `f = b = tree = path = 4`. The cliff table in the README already shows this.
- The brief said "n mod Δ = 2m+1". True **only for m ≥ 3** (`m=1` gives 1, `m=2` gives 0). The
  paper states the exceptions; they matter because they are why conjecture 64's RHS is 2, not 4,
  at `m = 1, 2`.
- README says "Graffiti.pc verified its conjectures against a finite graph database (roughly
  n ≤ 11)" — dropped, see §3.
- README's sharpness table lists 174 as an open conjecture the carrier is tight on;
  `results/transcription_audit.md` records that 174 was **refuted by a third party on
  2026-07-23** (11-vertex counterexample). The paper flags 174, 438b, 176, 181 and 430a as
  having changed status since the sweep.
- The 309 closed form `(−2m²+7m+1)/2` is derived independently in the paper and matches
  Gebendorfer's published form recorded in `results/literature.md`; it is also verified
  computationally for `m = 1..6`.

## 5. What was deliberately excluded (per the review's boundary)

- **No prospective-navigation claim.** Section 8 contains one labelled `Observation`
  (T(7) = L(K₇) vs. WOWII 181) presented as "a single suggestive follow-up", immediately
  followed by the disconfirming evidence: dozens of frozen-protocol applications with
  essentially no crossings a catalogue baseline did not also find, and the competing hypothesis
  that machine corpora are simply under-verified. The paper states that the preregistered
  three-arm test has **not** been run.
- No mention of the formal-corpus defect-forensics programme (the review's "half a
  contribution"), the METHOD version series, the benchmark v1.x protocol chain, the Bondy /
  A231201 / OEIS lanes, or the Graffiti³ results. None of it belongs in this paper.
- The 176 / 172 / 430a transfers are mentioned only as status changes in the sharpness list, not
  as evidence for a method.
- No submission, posting, release, or `git commit` was performed. `lake build` was not run.

## 6. What a referee will attack, in descending order of danger

1. **"Theorem 3.2 is trivial."** The upper bound `b ≤ 2α` is elementary and `α(H[K_m]) = α(H)`
   is classical; composing them is a two-line argument. This is the single most likely referee
   complaint and it is partly correct. Mitigations already in the draft: the paper says so
   explicitly in a remark; the non-trivial content is relocated to Lemma 3.1 / Prop 3.4 (exact
   value for arbitrary `H`, stabilisation in `m`, structural description `|A|K₂ ⊔ H[B]`) and to
   the identification of condition `path(H) = 2α(H)`. If a referee still objects, the honest
   response is that the paper's contribution is the *diagnosis*, not the lemma.
2. **"The mechanism is obvious once stated."** Also partly correct, and the paper leans into it
   ("Proposition 3.6 is nearly a tautology; its role is framing"). The defence is empirical: the
   mechanism accounts for 4 open kills + 8 retro-kills + ~36 sharpness cases in one corpus, and
   nobody had written it down. A referee unpersuaded by "nobody wrote it down" is a real risk.
3. **Transcription reliability.** Every claim is a claim about a *reading* of a lossily-encoded
   HTML page whose live copy is currently unreachable, whose author edited it mid-study, and
   four of whose entries are demonstrably corrupt. Section 7.3 states this plainly and Section 8
   repeats it, but a strict referee could demand a verbatim archival appendix (page captures,
   `wowIIdefs.js` excerpts, and the reading-enumeration table) before accepting any refutation
   claim. **Recommendation: add such an appendix before submission.** It is a paste job — the
   material exists in `results/transcription_audit.md` and `data/INVARIANT-GLOSSARY.md`.
4. **Priority / attribution on 64 and 309.** Gebendorfer published both refutations
   (2026-07-25 and -26) crediting the earlier 63/85 certificate for the carrier. The paper
   credits him in the acknowledgements and in-line, and presents Theorems 5.3–5.4 as independent
   re-derivations needed for the uniform statement. A referee may still want this made even more
   prominent, e.g. in the abstract. Consider it.
5. **"Section 7 is a lab report, not a theorem."** The corpus section is the weakest part
   mathematically. It is retained because the review identified it as the empirical backbone of
   the mechanism claim, and because its honest defects (4 corrupt entries, 3 conjectures the
   community parse missed, a mid-study page edit) are themselves findings about corpus quality.
   A referee at *Experimental Mathematics* should be fine with it; a referee at *Discrete
   Applied Mathematics* may ask for it to be compressed to a table.
6. **The `n mod Δ` reading of Conjecture 64.** The page text has unbalanced brackets. The
   defence — the page's own `printDefinitions(41,5,32,16,0)` link declares `n mod Δ` an atomic
   invariant (definition 32) — is strong but relies on an archived JS file. This should go in
   the archival appendix (item 3).
7. **`even horizontal` convention.** The paper notes that the two candidate readings ("same even
   distance" vs. "both endpoints at even distance") coincide on this family and that all six
   convention combinations still refute 309. That is verified by `scripts/verify_wowii_309.py`.
   Low risk, but a referee will check it.
8. **Venue fit.** See §7.

## 7. Publishability assessment (honest)

**Publishable, with work, at *Experimental Mathematics*.** The paper has: a fully-proved
structural mechanism; exact closed forms for a named family; four refutations of published open
conjectures (two of them first-published here, two independently); an exhaustive corpus
evaluation with its defects disclosed; and a reproducibility trail. That is a real paper. The
weakness is that the central lemma is easy; the value is diagnostic and empirical, which is
exactly what *Experimental Mathematics* exists for.

- ***Experimental Mathematics*** — best fit. The "computational evidence about a mathematical
  phenomenon, with proofs where proofs are available" format is precisely this paper.
- ***Discrete Applied Mathematics*** — plausible but a worse fit; DAM will read the theorems as
  slight and may want the corpus material cut, which removes the point.
- ***MATCH Commun. Math. Comput. Chem.*** — the AutoGraphiX/VNS line publishes there; a real
  option if the framing shifts towards "failure modes of automated conjecturing".
- **A workshop (AITP / conjecturing-adjacent)** — would take it as-is, but under-sells it.

**Before submission, in priority order:** (a) add the archival appendix (item 6.3); (b) resolve
or permanently accept the `[CITATION NEEDED]` on the Graffiti.pc database description; (c)
decide whether to give per-conjecture closed forms for the eight retro-kills; (d) confirm the
author line, affiliation and correspondence address (currently `Kuber Mehta`, taken from the
repository's git identity — **verify this is how the author wants to be named**); (e) have
someone check Geller–Stahl's actual statement of the independence-number identity, or replace
the citation with a self-contained one-line proof (it is already proved in Theorem 3.2(i), so
the citation could simply be dropped).

**What would make it substantially stronger, but is out of scope here:** running the
preregistered three-arm experiment the review's §4 describes and reporting the result either
way. If the wall arm wins, this paper gains a method section. If it loses, this paper is still
the honest product — and Section 8 already says so.
