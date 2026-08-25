# Discretization-cliff paper release preflight checklist

Date: **2026-08-26 UTC**. Prepared by the final-verification research agent;
every check below was executed today against the working tree unless marked
`TODO-ORCHESTRATOR`.

This is a **paper release**, not a single-counterexample release. It deviates
from the `UPSTREAM_PROTOCOL.md` rule "one release covers one WoW II problem"
(§Release format) by covering the whole case study (WOWII 63, 85, 64, 309 plus
the corpus sweep). Sections are adapted honestly rather than forced into the
counterexample template; the deviation requires explicit orchestrator sign-off
(recorded as a pending row below). No upstream issue or PR is proposed or
authorized by this checklist — GitHub releases only.

## 1. Verification result (gate: must pass)

- [x] `paper/discretization-cliff/verify_paper_claims.py`: **PASS, exit 0**,
      end-to-end, on 2026-08-26. Full output saved to
      `paper/discretization-cliff/VERIFY_RUN_2026-08-26.log`. Re-derives every
      closed form of Sections 4–5 for m = 1..6, Corollary 3.3 for
      C5/C7/C9, the C5[K4] carrier profile, and all eight retro-kill RHS values
      (exact arithmetic only).
- [x] `scripts/family_sweep.py`: **PASS** — reproduces Table 1's 63/85/64
      columns exactly (holds m ≤ 3; violated m ≥ 4; RHS values 3,4,4,5,6 /
      3,4,4,5,5 / 2,2,4,5,5).
- [x] `scripts/verify_wowii_64.py`: **PASS** (0.016 s).
- [x] `scripts/verify_wowii_309.py`: **PASS** (0.080 s) — 989/994 applicable
      order-3..7 graphs, 0 violations, 36 equalities, six RHS readings all fail.
- [x] Independent tally of `results/{open,refuted,proved}_sweep/*.jsonl`
      reproduces Section 7 exactly: open 220 = 167 holds + 47 n/a + 6 violated;
      refuted 139 = 101 + 29 n/a + 8 violated (+1 `VIOLATED_SOME_READINGS`,
      #77); proved 163 = 98 holds + 19 TIGHT + 45 n/a + 1 anomaly. Violated IDs
      = {24,25,46,49,52,54,55,56} (+77); TIGHT IDs = exactly the paper's 19-item
      list {4,7,15,16,18,37,57,68,89,94,99,173,382a,409a,411,420a,451,452,458}.
- [x] Adversarial read of `main.tex` (1136 lines): every numeric claim traced to
      script output or raw JSONL; theorem quantifiers checked (Lemma 3.1 both
      directions incl. m ≥ 2 converse hypothesis; Thm 3.2(i)–(iv) chain and the
      squeeze in (iv); Cor 3.3 valid for r ≥ 1 including r = 1, since K₂ is a
      tree and bipartite; Prop 3.5 correctly assumes diam(H) ≥ 2 via
      connected + non-complete + k ≥ 3; Thms 5.1–5.4 threshold arithmetic
      re-derived by hand — m ∈ {2,3} equality sets and the 309 margin
      (2m−5)(m−1)/2 all confirmed). No quantifier slips found.
- [x] Conjecture transcriptions 63/85/64/309 compared verbatim against
      `data/wowii-conjectures.json`: statements, page markers (`O`), dates
      (Mar 25 2004, Apr 04 2004, Mar 25 2004, Mar 1 2007), section names, and
      the deliberately preserved unbalanced brackets of #64 all match.
- [x] LaTeX toolchain: **absent locally** (`which pdflatex tectonic latexmk` —
      nothing found). Non-blocking: `main.pdf` is present and NOTES.md records
      the drafting-time build (pdflatex ×3, 0 errors / 0 warnings / 14 pp);
      rebuild in CI or on ai-vps before tagging.

## 2. Discrepancies found (all minor; none blocks release)

1. **Editorial, recommend fixing before tag:** §6 remark "On the database
   boundary" says "all 995 connected graphs of order **at most 7**". 995 is the
   count for orders **2–7**; order 1..7 totals 996. §7.1 states the range
   correctly ("order 2 ≤ n ≤ 7"). One-phrase fix in main.tex (~line 720), then
   rebuild the PDF.
2. **Known-open, intentional:** the `[CITATION NEEDED]` marker remains in the
   same remark, per NOTES.md §3 (Graffiti.pc database horizon unverifiable).
   Orchestrator decides: resolve with a DIMACS-source citation or ship as-is.
   Either way it is honest flagging, not an error.
3. **Pending gate item:** the paper asserts sorry-free Lean certificates exist
   for all four refutations; the files
   `lean/GraphConjecture{63,85,64,309}.lean` exist, but NOTES.md records that
   `lake build` was **not** re-run at drafting time. Run the warning-as-error
   build + axiom audit (rows in §5) before release.
4. **Bibliography nit:** TxGraffiti arXiv v1 title is "Automated conjecturing
   with TxGraffiti"; the bibliography cites the AMAI journal title "Automated
   conjecturing in mathematics with TxGraffiti" (journal DOI
   10.1007/s10472-026-10005-5 was verified at drafting time per NOTES.md §3).
   Keep if the journal title is confirmed; otherwise align with arXiv.
   Everything else in the bibliography re-checked today: both Gebendorfer
   Zenodo DOIs resolve via DataCite with matching titles/year and day-level
   dates (309 → 2026-07-25 = zenodo.21553295; 64 → 2026-07-26 =
   zenodo.21595503); arXiv 2409.19379 / 2411.09158 / 2507.17780 / 2605.13171
   all resolve with correct titles, dates, and author lists (incl. all 11
   Formal Conjectures authors in order); EJC 15 (2008) #R33 returns HTTP 200;
   Geller–Stahl (10.1016/0095-8956(75)90076-3) and Fajtlowicz
   (10.1016/0012-365X(88)90199-9) DOIs resolve through doi.org.

## 3. Scope, novelty, and duplicate gates (UPSTREAM_PROTOCOL §Scope)

- [x] Eligible collection: Written on the Wall **II** (not WoW I / Graph Brain).
- [x] Proposed tag `discretization-cliff-v1` is absent from local tags
      (`git tag -l | grep -i cliff` → empty) and remote tags
      (`gh api repos/Kuberwastaken/c5-k4/tags` → no match) as of 2026-08-26.
- [x] This is a release of campaign-native work (the mechanism paper); the four
      refutations' priority picture is already recorded: 63/85 first killed by
      C5[K4] in July 2026 (this campaign); 64/309 independently by Gebendorfer
      with credit to the earlier certificate — the paper credits him in-line,
      in the acknowledgements, and in the bibliography.
- [ ] **TODO-ORCHESTRATOR**: re-run duplicate searches immediately before
      publishing: `discretization-cliff`, `C5[K_m]` WOWII, across GitHub
      releases/tags and the web; confirm no prior release of this paper.
- [ ] **TODO-ORCHESTRATOR (sign-off)**: approve the one-release-many-conjectures
      deviation documented in the preamble.

## 4. Immutable-link slots

Full SHAs may NOT be guessed. Obtain each with `git rev-parse <commit>` after
the final commits (the checklist itself and the verify log must be committed
first, so the links can resolve), then fill in and run the HTTP-200 check.
The release must be cut from that exact audited commit, not a moving branch.

| Artifact | Path | Full SHA (git rev-parse) | HTTP 200 (`curl -sS -o /dev/null -w '%{http_code}' -L`) |
|---|---|---|---|
| Paper source | `paper/discretization-cliff/main.tex` | TODO-ORCHESTRATOR | ☐ pending |
| Compiled paper | `paper/discretization-cliff/main.pdf` | TODO-ORCHESTRATOR | ☐ pending |
| Drafting notes | `paper/discretization-cliff/NOTES.md` | TODO-ORCHESTRATOR | ☐ pending |
| Claim verifier | `paper/discretization-cliff/verify_paper_claims.py` | TODO-ORCHESTRATOR | ☐ pending |
| Verify run log (today) | `paper/discretization-cliff/VERIFY_RUN_2026-08-26.log` | TODO-ORCHESTRATOR | ☐ pending |
| Family sweep script | `scripts/family_sweep.py` | TODO-ORCHESTRATOR | ☐ pending |
| Verifier #64 | `scripts/verify_wowii_64.py` | TODO-ORCHESTRATOR | ☐ pending |
| Verifier #309 | `scripts/verify_wowii_309.py` | TODO-ORCHESTRATOR | ☐ pending |
| Lean certificate 63 | `lean/GraphConjecture63.lean` | TODO-ORCHESTRATOR | ☐ pending |
| Lean certificate 85 | `lean/GraphConjecture85.lean` | TODO-ORCHESTRATOR | ☐ pending |
| Lean certificate 64 | `lean/GraphConjecture64.lean` | TODO-ORCHESTRATOR | ☐ pending |
| Lean certificate 309 | `lean/GraphConjecture309.lean` | TODO-ORCHESTRATOR | ☐ pending |
| Corpus transcriptions | `data/wowii-conjectures.json` | TODO-ORCHESTRATOR | ☐ pending |
| Sweep verdicts | `results/open_sweep/`, `results/refuted_sweep/`, `results/proved_sweep/` | TODO-ORCHESTRATOR | ☐ pending |
| Carrier profile artefact | `data/profile.json` | TODO-ORCHESTRATOR | ☐ pending |

External URLs cited by the release body (spot-check before publishing):
Zenodo `10.5281/zenodo.21595503` and `10.5281/zenodo.21553295` (verified via
DataCite API today), the WOWII page URL (currently redirects/dead from this
host — the paper cites snapshot provenance instead, keep that framing),
`https://github.com/google-deepmind/formal-conjectures`.

## 5. Lean build + axiom audit (pending)

- [ ] **TODO-ORCHESTRATOR**: `lake env lean -DwarningAsError=true
      lean/GraphConjecture63.lean` (and 85/64/309) — record pass/fail.
- [ ] **TODO-ORCHESTRATOR**: `#print axioms` audit per certificate — expect
      only `propext`, `Classical.choice`, `Lean.ofReduceBool`,
      `Lean.trustCompiler`, `Quot.sound`; no `sorryAx`.

## 6. Proposed tag and title

```text
tag:   discretization-cliff-v1
title: The discretization cliff: clique blow-ups of C5 and a predictable failure mode of database-verified conjecture generators
```

## 7. Release body draft (section-ordered; adapt freely, do not reorder)

### Summary

This release publishes the campaign's paper, *"The discretization cliff:
clique blow-ups of the 5-cycle and a predictable failure mode of
database-verified conjecture generators"* (14 pp., compiles cleanly; PDF and
LaTeX source included). The paper isolates a structural regime in which the
database-plus-sharpness filter of Graffiti-lineage conjecture generators is
systematically uninformative: along a clique blow-up H[K_m], every
hereditary-bipartite induced-subgraph number (path, tree, forest, bipartite)
is pinned — bounded by 2α(H) for all m and constant in m for m ≥ 2 (Theorem
3.2, Proposition 3.4) — while the vocabulary's growing terms (n, Δ,
dist_even, even horizontal, n mod Δ, …) scale with m. Any bound that combines
a pinned term with a growing term therefore fails past an exact threshold, and
its last surviving member attains equality — precisely the sharpness signal a
Dalmatian-style heuristic rewards. For H = C₅ the paper proves α(C₅[K_m]) = 2
and path = tree = f = b = 4 for every m ≥ 1, derives closed forms for the
growing side, and shows four WOWII conjectures open in July 2026 — numbers 63,
85, 64 and 309 — fall at exact thresholds (63, 85, 64 attained with equality
at m = 3, violated for all m ≥ 4; 309 attained with equality at m = 1,
violated for all m ≥ 3). An exhaustive evaluation of all 522 transcribed WOWII
records against C₅[K₄] locates the same mechanism eight more times among
already-refuted conjectures and exhibits the carrier as a zero-slack witness
for roughly three dozen further statements, 19 of them proved theorems of the
corpus. The paper states explicitly what it does not claim: it is a mechanism
and a diagnostic, not a counterexample engine, and no prospective use of
tightness data is claimed.

### Statement of results

All proved in the paper with complete proofs; every numeric claim re-derived
by `verify_paper_claims.py` (run log linked below, PASS end-to-end on
2026-08-26):

- Pinning (Thm 3.2, Cor 3.3): α(H[K_m]) = α(H); path ≤ tree ≤ f ≤ b ≤ 2α(H)
  independent of m; if path(H) = 2α(H) then all four equal 2α(H) for every
  m ≥ 1 — hence C_{2r+1}[K_m] pins all four at 2r for every m ≥ 1, r ≥ 1.
- Exact profile formula and stabilisation (Lemma 3.1, Prop 3.4) for any
  hereditary triangle-free class, m ≥ 2.
- Growth (Prop 3.5) and the cliff principle (Prop 3.6), including the last
  clause: the last surviving member of a pinned/growing pair is an equality
  case.
- C₅[K_m] closed forms (Props 4.1–4.2): n = 5m, |E| = 5m(3m−1)/2,
  (3m−1)-regular, diam = rad = 2, α = 2, ω = 2m, γ = 2, γ_t = 3, γ_c = 3,
  L_s = 5m−3, λ(v) = 2, dist_even = 2m+1, even_horizontal = m(2m−1),
  min|N_Ḡ(e)| = 4m, n mod Δ = 2m+1 for m ≥ 3.
- Four cliffs (Thms 5.1–5.4) with exact thresholds and equality indices as in
  the Summary; Table 1 of the paper is printed by `scripts/family_sweep.py`.
- Corpus sweep (Section 7): 220 open / 139 refuted-by-others / 163 proved
  records evaluated against C₅[K₄] under reading enumeration, a
  database-sanity gate over the 995 connected graphs of order 2 ≤ n ≤ 7,
  DeLaViña's own recovered invariant definitions, and adversarial
  re-verification of every violation; four corrupt entries disclosed and
  excluded rather than counted.

Priority note: WOWII 64 and 309 were independently refuted by J. J. Gebendorfer
(Zenodo DOI 10.5281/zenodo.21595503, 2026-07-26; DOI 10.5281/zenodo.21553295,
2026-07-25) using this campaign's carrier family, credited to the earlier
63/85 certificate. The paper credits this prominently and presents its own
derivations as independent re-derivations needed for the uniform statement of
the mechanism.

### Relationship to the C5[K4] campaign

This paper is the case-study write-up the campaign's review identified as its
most novel contribution: it explains, in one mechanism, why a single
20-vertex graph and its siblings cleared four open conjectures at once, and
why the generator's own verification procedure could not have flagged the
danger. The carrier, the sweep data, the transcription audit, and the four
Lean certificates all live in this repository; the paper is their
synthesis. Per the campaign's limitations discipline, the paper claims no
prospective wall-navigation method and reports the negative experience with
tightness-directed search alongside the single suggestive instance (T(7) vs.
WOWII 181).

### Complete formal certificate

There is **no Lean certificate for this release as a whole**, and none is
needed: this release is a paper whose mathematical content is either proved in
the text (Sections 3–6) or reported as computation with named scripts and
committed data artifacts (Section 7). Certificates attach to the four
individual refutations, not to the paper: sorry-free Lean 4 certificates for
WOWII 63, 85, 64 and 309 exist in `lean/GraphConjecture{63,85,64,309}.lean`
(build command, result, and axiom audit to be re-recorded at release time —
see checklist §5). The claim verifier
`paper/discretization-cliff/verify_paper_claims.py` is exact-arithmetic,
exhaustive-enumerative, depends only on networkx, and exits 0 iff every closed
form asserted in the paper checks out; today's run is archived alongside it.

### Source and provenance note

Primary source: DeLaViña's *Written on the Wall II* page (live site currently
unreachable from the campaign hosts); the corpus used here is the page as it
stood on 2026-08-12, transcribed into 522 machine-readable records with
verbatim statements, status markers, dates, and sections, cross-checked
against archived captures of 2010, 2016 and 2022 and against DeLaViña's own
recovered definition database (`wowIIdefs.js`, capture of 2022-01-30). The
page was edited mid-study on 2026-08-06 (ten conjectures moved open →
resolved); the transcription audit documents this, the three conjectures the
July 2026 community parse missed (136–138), and the four corrupt entries
(412f, 448b, 401b, Theorem 97) that are disclosed and excluded rather than
counted. Every claim above is a claim about a reading of a lossily-encoded
source; readings are enumerated and gated, and residual transcription risk is
stated in the paper rather than hidden.

### AI assistance disclosure

OpenAI Codex and delegated coding agents assisted with source transcription
and auditing, literature verification, proof drafting, independent
verification scripts, and preparation of this release. The submitter reviewed
the paper, the verification log, the attribution, and this release, and takes
responsibility for the publication.

## 8. Final pre-publish sequence (orchestrator)

1. Commit this checklist and `paper/discretization-cliff/VERIFY_RUN_2026-08-26.log`.
2. Decide discrepancy items §2.1 (fix "at most 7" → "of order 2 to 7", rebuild
   PDF off-box) and §2.2 ([CITATION NEEDED]: resolve or ship).
3. Fill §4 SHAs via `git rev-parse`; run all HTTP-200 checks; open each link.
4. Record §5 Lean build + axiom audit results.
5. Re-run duplicate search (§3) and confirm tag absence once more.
6. Create the release from the audited commit; read back the rendered release,
   verify every link, and confirm the tag resolves to the intended commit.

**Verdict at time of writing: NOTHING BLOCKS RELEASE.** Two editorial items
(§2.1, §2.2) and two pending-gate rows (§4 hashes/HTTP, §5 Lean audit) must be
closed by the orchestrator before tagging.
