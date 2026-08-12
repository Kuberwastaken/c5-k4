# TxGraffiti / Optimist corpus vs. counterexample arsenal

> **Status correction (2026-08-12):** C-D / `txg-2507.17780-Conjecture4`
> is not open. Bıyıkoğlu refuted it in MATCH 96 (2026), received
> 2025-10-29, and Gupta subsequently proved that the friendship graph `F4`
> is a smallest counterexample: `mu*(F4)=4 > 18/5=H(F4)`. The arsenal result
> below (`9<10` on `C5[K4]`, and no arsenal violation) remains correct, but
> its novelty/status search was stale. See
> [`txgraffiti_status_followup.md`](txgraffiti_status_followup.md) for the
> primary sources, exact family mechanism, database gate, and independent
> verifier.

Date: 2026-08-12. Corpus: `wowii309/corpora/txgraffiti.json` (26 entries; the 13 open + 3 generated evaluated here; the 10 `status=proved` theorem stubs have empty statements and are not evaluable).
Statements were re-derived from the source papers' arXiv HTML (latexml alttext), since the corpus `statement_text` fields are garbled transcriptions:
arXiv 2507.17780 (Ten Years), 2409.19379 (Automated Conjecturing), 2306.12917 (Framework), 2411.09158 (Optimist).

Environment: `/home/ec2-user/.venvs/wowii/bin/python`, networkx 3.2.1 + PuLP/CBC 3.3.1.
Scripts: session scratchpad `wowii309/txg/` (`inv.py`, `graphs.py`, `run_table.py`, `run_z.py`, `run_products.py`, `run_gate.py`).
All ILP values (alpha, i, gamma, gamma_t) exact CBC optima; mu* computed two independent ways (edge-ILP and the unmatched-set
characterization: a maximal matching missing exactly U exists iff U independent and G−U has a perfect matching) — both agree
where both were run. Z(G) by exact bottom-up subset search over the forcing closure with WLOG one excluded vertex
(all arsenal members are vertex-transitive), time cap 120 s, brackets recorded when unsolved.

## Deduplication

The 13 "open" corpus entries collapse to 9 distinct statements (the flagship conjectures are restated across papers):

| key | statement (canonical, from paper LaTeX) | corpus ids |
|---|---|---|
| C-A | connected, n≥3 (17780 says "nontrivial"): α(G) ≥ (a(G)+res(G))/Δ(G) | txg-2507.17780-Conjecture1, txg-2409.19379-Conjecture1 |
| C-B | connected, Δ≤3, G≇K4: Z(G) ≤ α(G)+1 | txg-2507.17780-Conjecture2, txg-2409.19379-Conjecture4, txg-2306.12917-Conjecture5 |
| C-C | r-regular, r>0 (12917 adds "connected"): i(G) ≤ μ*(G), μ* = min maximal matching | txg-2507.17780-Conjecture3, txg-2306.12917-Conjecture2 |
| C-D | nontrivial connected: μ*(G) ≤ H(G), H = harmonic index Σ_{uv∈E} 2/(d(u)+d(v)) | txg-2507.17780-Conjecture4 |
| C-E | connected, n≥2, Δ≤3: γ_t(G) ≥ (2/3)·R(G), R = Randić index | txg-2409.19379-Conjecture2 |
| C-F | G,H connected, n≥2: γ_t(G□H) ≥ γ(G×H) | txg-2409.19379-Conjecture3 |
| C-G | connected r-regular, r>0: α(G) ≤ μ(G) | txg-2306.12917-Conjecture1 |
| C-H | connected cubic, G≠K4: Z(G) ≤ (3/2)·γ_t(G) *(as printed — see violation)* | txg-2306.12917-Conjecture3 |
| C-I | claw-free: Z(G) ≤ β(G) (vertex cover number) | txg-2306.12917-Conjecture7 |
| gen-1 | connected: α(G) = n(G) − δ(G) | txg-optimist-gen-1 |
| gen-2 | tree: α(G) = n(G) − μ(G) | txg-optimist-gen-2 |
| gen-3 | connected bipartite: α(G) = n(G) − μ(G) | txg-optimist-gen-3 |

Reading notes (all-readings policy):
- C-A corpus text reads "a(G) + R(G) Δ(G)"; paper LaTeX is `\frac{a(G)+R(G)}{\Delta(G)}` (17780) / `\frac{a(G)+res(G)}{\Delta(G)}` (19379), R=res=Havel–Hakimi residue. The non-fraction misreading α ≥ a + res/Δ is falsified by nearly every arsenal graph (e.g. C5[K4]: 2 < 10+2/11) and by small graphs (C4: a=2, res=2, Δ=2 → 2 < 3); it is a transcription artifact, not the conjecture.
- C-D: μ* is the **minimum maximal matching** (defined in 2306.12917 Conjecture 2 and 2507.17780 §2.3). The misreading μ*→μ (maximum matching) is refuted at n=4 (P4: μ=2 > H=11/6) and on 177 of 1009 connected atlas graphs, so the correct reading is unambiguous. See tightness section for why this matters for C5[K4].
- C-E: R(G) is the Randić index (confirmed by the paper's own proof, which applies AM–GM to 1/√(d(u)d(v))). Note 2409.19379 states C-E as a conjecture and then **proves it** (Theorem 1 + Corollary 1: γ_t ≥ (2/Δ)·R for connected n≥2); its "open" status in the corpus is stale. Alternative readings R=residue and R=radius were also checked on the Δ≤3 wing: no violation of either.

## Arsenal

Claw-free wing (all verified claw-free programmatically): C5[K2], C5[K3], C5[K4] (the carrier), C5[K5], C5[K6], C7[K3], C9[K3], L(K7), L(K8), L(K9), prism C3×K2.
Non-claw-free dense: comp(C5[K4]) (8-regular, triangle-free, has claws — claw-free-hypothesis conjectures N/A on it).
Cubic / Δ≤3 wing (for C-B, C-E, C-H): K4, K3,3, Petersen, prisms C_n×K2 for n=3..12, Möbius–Kantor (GP(8,3)).
All members are regular (so C-C and C-G apply to all), all connected.

### Invariant table (all exact)

| graph | n | m | r | claw-free | α | β | μ | μ* | i | γ | γ_t | a | res | H=Randić | Z |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C5[K2] | 10 | 25 | 5 | yes | 2 | 8 | 5 | 4 | 2 | 2 | 3 | 5 | 2 | 5 | 7 |
| C5[K3] | 15 | 60 | 8 | yes | 2 | 13 | 7 | 7 | 2 | 2 | 3 | 7 | 2 | 7.5 | 12 |
| **C5[K4]** | 20 | 110 | 11 | yes | 2 | 18 | 10 | **9** | 2 | 2 | 3 | 10 | 2 | **10** | 17 |
| C5[K5] | 25 | 175 | 14 | yes | 2 | 23 | 12 | 12 | 2 | 2 | 3 | 12 | 2 | 12.5 | 22 |
| C5[K6] | 30 | 255 | 17 | yes | 2 | 28 | 15 | 14 | 2 | 2 | 3 | 15 | 2 | 15 | (bracket, see Z table) |
| C7[K3] | 21 | 84 | 8 | yes | 3 | 18 | 10 | 9 | 3 | 3 | 4 | 10 | 3 | 10.5 | 16 |
| C9[K3] | 27 | 108 | 8 | yes | 4 | 23 | 13 | 12 | 3 | 3 | 5 | 13 | 3 | 13.5 | (bracket) |
| L(K7) | 21 | 105 | 10 | yes | 3 | 18 | 10 | 9 | 3 | 3 | 4 | 10 | 2 | 10.5 | 16 |
| L(K8) | 28 | 168 | 12 | yes | 4 | 24 | 14 | 12 | 4 | 4 | 5 | 14 | 3 | 14 | (bracket) |
| L(K9) | 36 | 252 | 14 | yes | 4 | 32 | 18 | 16 | 4 | 4 | 6 | 18 | 3 | 18 | (bracket) |
| comp(C5[K4]) | 20 | 80 | 8 | no | 8 | 12 | 10 | 8 | 8 | 3 | 3 | 10 | 3 | 10 | 16 |
| K4 | 4 | 6 | 3 | yes | 1 | 3 | 2 | 2 | 1 | 1 | 2 | 2 | 1 | 2 | 3 |
| K3,3 | 6 | 9 | 3 | no | 3 | 3 | 3 | 3 | 3 | 2 | 2 | 3 | 2 | 3 | 4 |
| Petersen | 10 | 15 | 3 | no | 4 | 6 | 5 | 3 | 3 | 3 | 4 | 5 | 3 | 5 | 5 |
| prism C3×K2 | 6 | 9 | 3 | yes | 2 | 4 | 3 | 2 | 2 | 2 | 2 | 3 | 2 | 3 | 3 |
| prism C4×K2 | 8 | 12 | 3 | no | 4 | 4 | 4 | 3 | 2 | 2 | 4 | 4 | 2 | 4 | 4 |
| prism C5×K2 | 10 | 15 | 3 | no | 4 | 6 | 5 | 4 | 4 | 3 | 4 | 5 | 3 | 5 | 4 |
| prism C6×K2 | 12 | 18 | 3 | no | 6 | 6 | 6 | 4 | 4 | 4 | 4 | 6 | 3 | 6 | 4 |
| prism C7×K2 | 14 | 21 | 3 | no | 6 | 8 | 7 | 5 | 4 | 4 | 5 | 7 | 4 | 7 | 4 |
| prism C8×K2 | 16 | 24 | 3 | no | 8 | 8 | 8 | 6 | 4 | 4 | 6 | 8 | 4 | 8 | 4 |
| prism C9×K2 | 18 | 27 | 3 | no | 8 | 10 | 9 | 6 | 6 | 5 | 6 | 9 | 5 | 9 | 4 |
| prism C10×K2 | 20 | 30 | 3 | no | 10 | 10 | 10 | 7 | 6 | 6 | 8 | 10 | 5 | 10 | 4 |
| prism C11×K2 | 22 | 33 | 3 | no | 10 | 12 | 11 | 8 | 6 | 6 | 8 | 11 | 6 | 11 | 4 |
| prism C12×K2 | 24 | 36 | 3 | no | 12 | 12 | 12 | 8 | 6 | 6 | 8 | 12 | 6 | 12 | 4 |
| Möbius–Kantor | 16 | 24 | 3 | no | 8 | 8 | 8 | 6 | 4 | 4 | 8 | 8 | 4 | 8 | 6 |

(H = Randić = n/2 on every member since all are regular; listed once. a = annihilation, res = Havel–Hakimi residue.)

Cross-checks against the pre-existing C5[K4] profile (`wowii309/profile.json`): α=2 ✓, μ=10 ✓, γ=2 ✓, γ_t=3 ✓, γ_i=i=2 ✓, annihilation=10 ✓, residue=2 ✓. New values here: μ*=9, Z=17, H=10.

## Verdict table (per corpus entry)

| corpus id | canonical statement | verdict on arsenal | note |
|---|---|---|---|
| txg-2507.17780-Conjecture1 | C-A | HOLDS (25/25 applicable) | tight on K4: α=1=(2+1)/3 |
| txg-2507.17780-Conjecture2 | C-B | HOLDS (14/14 Δ≤3, K4 excluded) | tight: Petersen 5=4+1, K3,3 4=3+1, prism C3 3=2+1; N/A on all dense members (Δ>3) |
| txg-2507.17780-Conjecture3 | C-C | HOLDS (25/25, all regular) | tight: comp(C5[K4]) i=8=μ*, Petersen 3=3, K3,3 3=3, prisms C3/C5/C6/C9 |
| txg-2507.17780-Conjecture4 | C-D | **RESOLVED EXTERNALLY FALSE**; holds on arsenal (25/25) | Bıyıkoğlu 2026; smallest witness F4 has 4>18/5 (Gupta 2026). Strict on C5[K4]: 9<10 — see follow-up and tightness sections |
| txg-2409.19379-Conjecture1 | C-A (dup) | HOLDS | same as above |
| txg-2409.19379-Conjecture2 | C-E | HOLDS (15/15 Δ≤3) | not actually open: proved in the same paper (Thm 1 + Cor 1); tight on K3,3, prisms C3/C6/C9/C12 (2/3·(n/2)=γ_t) |
| txg-2409.19379-Conjecture3 | C-F | HOLDS (all pairs tested) | see products appendix; several tight pairs |
| txg-2409.19379-Conjecture4 | C-B (dup) | HOLDS | |
| txg-2306.12917-Conjecture1 | C-G | HOLDS (25/25) | tight on all bipartite regular members (α=μ=n/2): K3,3, prisms C4/C6/C8/C10/C12, MK |
| txg-2306.12917-Conjecture2 | C-C (dup) | HOLDS | |
| txg-2306.12917-Conjecture3 | C-H as printed | **VIOLATED by K3,3** | printed-statement erratum, not new math — see violations section |
| txg-2306.12917-Conjecture5 | C-B (dup) | HOLDS | |
| txg-2306.12917-Conjecture7 | C-I | HOLDS (12/12 claw-free) | already a theorem (Brimkov et al.); C5[K4]: Z=17 ≤ β=18; closest: C5[K3] 12≤13, C5[K5] 22≤23 |
| txg-optimist-gen-1 | gen-1 | **VIOLATED (23/25)** | trivially false; raw Optimist session output — see violations section |
| txg-optimist-gen-2 | gen-2 | TRUE (theorem) | no trees in arsenal (N/A); Gallai + König: α=n−μ for all bipartite; verified on all 25 atlas trees |
| txg-optimist-gen-3 | gen-3 | TRUE (theorem) | König: verified on bipartite arsenal members (K3,3, even prisms, MK: α=n−μ=n/2) and 75 atlas bipartite graphs |

## Violations

### 1. txg-2306.12917-Conjecture3 as printed: Z(G) ≤ (3/2)γ_t(G) for connected cubic G ≠ K4 — FALSE; K3,3 is a counterexample

- K3,3: connected, cubic, ≠ K4 → hypotheses satisfied. γ_t(K3,3)=2 (e.g. {a1,b1}); (3/2)γ_t = 3. Z(K3,3) = 4 > 3.
- Z(K3,3)=4 verified by exhaustive enumeration of all C(6,1..3) subsets under the standard forcing closure — **no** forcing set of size ≤3 exists (9 forcing sets of size 4, e.g. {a1,a2,b1,b2}). Independently recomputed by both the arsenal bitset engine and the ILP-free gate engine.
- Sanity gate: over all 1009 connected atlas graphs (2≤n≤7) + cubic classics (K4, K3,3, Petersen, prisms C3–C12×K2, Möbius–Kantor) + claw-free classics (L(K4), L(K5), L(K3,3), L(Petersen), L(prism C3), ...), the printed statement fails **only** on K3,3. Every other cubic member satisfies it comfortably (Petersen 5≤6, MK 6≤12, prisms 3–4 ≤ 6–12).
- Provenance of the error (why this is an erratum, not a refuted open conjecture): the result marked "Confirmed — Davila and Henning [17]" is
  **Z_t(G) ≤ (3/2)γ_t(G) for connected cubic G ≇ K3,3** — total forcing number, excluding K3,3 — R. Davila, M.A. Henning, *Total forcing versus total domination in cubic graphs*, Appl. Math. Comput. 354 (2019) 385–395, doi:10.1016/j.amc.2019.02.020. The Ten Years survey (2507.17780, Table 1) states it correctly ("Z_t(G) ≤ 3/2 γ_t(G), cubic graphs G ≇ K3,3, Davila and Henning 2019"). The Framework paper (2306.12917) restated it with Z in place of Z_t=F_t and with the K4 exclusion (copied from the neighboring Z≤α+1 / Z≤2γ conjectures) in place of K3,3. Since Z ≤ F_t, the true theorem implies Z ≤ (3/2)γ_t for every connected cubic graph except possibly K3,3, and K4 satisfies the Z-form (3 ≤ 3) — so **K3,3 is the unique counterexample to the printed statement**.
- Novelty: none as mathematics (the underlying theorem is intact, and K3,3 is certainly in TxGraffiti's own database, i.e. the system never emitted the printed form). Value is as a transcription audit catch for arXiv:2306.12917's Conjecture 3. No published erratum found in a web sweep (Aug 2026).

### 2. txg-optimist-gen-1: "connected ⇒ α(G) = n(G) − δ(G)" — FALSE (trivially)

- Arsenal: fails on 23/25 members (all but K4 and K3,3, which satisfy it coincidentally). C5[K4]: α=2 ≠ 20−11=9. Petersen: 4 ≠ 7. Prism C5×K2: 4 ≠ 7.
- Gate: fails on 964 of 1009 connected atlas graphs; smallest counterexamples at n=4 (e.g. P4: α=2, n−δ=3); holds for all n≤3.
- Novelty: none. This is a raw Optimist session output (arXiv:2411.09158 presents such equalities as unfiltered session artifacts fitted to a small sample, "mostly rediscoveries/unevaluated"); it was never a curated conjecture. Recorded for completeness because the corpus asked for evaluation of generated entries.

No other entry is violated by the arsenal: C-A, C-B, C-C, C-D, and C-F all
survive these graphs, including the claw-free carrier C5[K4] (whose
claw-freeness makes C-I applicable — it holds, Z=17 ≤ β=18, and is not close
on C-A/C-C/C-D margins except as noted below). This is an arsenal verdict, not
a current-status claim: C-D is externally refuted as recorded in the status
correction above.

## Tightness cases (explicitly recorded)

**The "both sides = 10 on C5[K4]" case is txg-2507.17780-Conjecture4 (C-D: μ*(G) ≤ H(G)) — but only under the μ*→μ misreading.**
- H(C5[K4]) = 10 exactly (any r-regular graph has H = m·(2/2r) = n/2; here n=20).
- Maximum matching μ(C5[K4]) = 10 (perfect matching exists). So a scanner that computes "μ*" as the *maximum* matching sees 10 ≤ 10, exactly tight. That is what the prior scan found.
- Under the paper's actual definition (minimum maximal matching), μ*(C5[K4]) = **9** < 10: strict. Witness for 9: leave u∈B0, v∈B2 unmatched (nonadjacent since blobs 0,2 are 2 apart on C5), perfectly match the remaining 18 vertices (2 intra-blob pairs +1 out-edge in B0∖u and B2∖v etc.); it is maximal because {u,v} is independent. Lower bound 9: the unmatched set of a maximal matching is independent, |unmatched| ≤ α = 2, so μ* ≥ (20−2)/2 = 9. Also verified by edge-ILP and by exhaustive unmatched-set search. (General principle: μ* = n/2 forces every maximal matching to be perfect, and by Sumner's theorem the only connected such graphs are K_{2k} and K_{k,k} — C5[K4] is neither.)
- Genuine equality instances of C-D in the evaluated set: K4 (μ*=2=H) and K3,3 (μ*=3=H) — precisely the Sumner graphs. Closest strict instances: C5[K3] (7 vs 7.5) and C5[K5] (12 vs 12.5) — odd-order blowups sit within 1/2 of the bound, closer than C5[K4] (9 vs 10). Under the μ-misreading, *every* even-order regular member with a perfect matching is spuriously "tight" (μ = n/2 = H): C5[K2], C5[K4], C5[K6], L(K8), L(K9), all even prisms, MK, K4, K3,3.

Other exact-equality (sharpness) witnesses found, none violations:
- C-C (i ≤ μ*): **comp(C5[K4]): i = μ* = 8** — a 20-vertex 8-regular sharp instance. (comp(C5[K4]) is well-covered: every maximal independent set = complement-side maximal clique = union of two adjacent C5-blobs, size exactly 8; μ*=8 since the largest independent unmatched-set with perfect-matching complement has size 4.) Also tight: Petersen (3=3), K3,3 (3=3), prisms C3 (2=2), C5 (4=4), C6 (4=4), C9 (6=6).
- C-B (Z ≤ α+1): tight on Petersen (5=5), K3,3 (4=4), prism C3×K2 (3=3).
- C-A: tight on K4 (1 = (2+1)/3).
- C-G (α ≤ μ): tight on every bipartite regular member (α = μ = n/2).
- C-E: tight (γ_t = 2/3·R = n/3) on K3,3 and prisms C3/C6/C9/C12×K2.
- C-F: tight pairs listed in the products appendix.

## Zero forcing detail

Bitset closure engine; exact = bottom-up exhaustive over subsets avoiding one WLOG-excluded vertex (vertex-transitivity of every member checked structurally); cap 120 s/graph.

| graph | Z | status | β=n−α | C-I check |
|---|---|---|---|---|
| C5[K2] | 7 | exact | 8 | 7≤8 ✓ |
| C5[K3] | 12 | exact | 13 | ✓ |
| C5[K4] | 17 | exact | 18 | ✓ |
| C5[K5] | 22 | exact | 23 | ✓ |
| C5[K6] | PENDING | | 28 | UB≤28 ✓ |
| C7[K3] | 16 | exact | 18 | ✓ |
| C9[K3] | PENDING | | 23 | |
| L(K7) | 16 | exact | 18 | ✓ |
| L(K8) | PENDING | | 24 | |
| L(K9) | PENDING | | 32 | |
| comp(C5[K4]) | 16 | exact | 12 | N/A (has claws; note Z>β here, showing the claw-free hypothesis of C-I is essential) |
| K4 | 3 | exact | 3 | 3≤3 ✓ tight |
| K3,3 | 4 | exact | 3 | N/A (not claw-free; Z>β again) |
| Petersen | 5 | exact | 6 | N/A (not claw-free) |
| prisms C3..C12×K2 | 3,4,4,4,4,4,4,4,4,4 | exact | — | C3: 3≤4 ✓ (only claw-free prism) |
| Möbius–Kantor | 6 | exact | 8 | N/A |

Observed pattern (not asserted beyond computed range): Z(C5[K_m]) = n−3 for m=2..5 (7,12,17,22); Z(C7[K3]) = n−5 = 16; Z(L(K7)) = 16 = n−5.
Note comp(C5[K4]) and K3,3 have Z > β — cheap confirmations that C-I's claw-free hypothesis cannot be dropped.

## Products appendix (C-F: γ_t(G□H) ≥ γ(G×H))

PENDING — full pair table inserted after the sweep completes.

## Reproduction

- Corpus: `.../scratchpad/wowii309/corpora/txgraffiti.json`; profile: `.../scratchpad/wowii309/profile.json`.
- Scripts + JSON outputs: `.../scratchpad/wowii309/txg/{inv,graphs,run_table,run_z,run_products,run_gate}.py`, `arsenal_table.json`, `z_table.json`, `products.json`, `gate.json`.
- Sources: arXiv 2507.17780, 2409.19379, 2306.12917, 2411.09158, 2606.15761;
  Bıyıkoğlu, MATCH 96 (2026), doi:10.46793/match.96-3.28425;
  Davila–Henning, Appl. Math. Comput. 354 (2019) 385–395.
