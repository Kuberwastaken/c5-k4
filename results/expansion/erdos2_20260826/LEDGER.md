# LEDGER — erdos2_20260826 (ErdosProblems lane)

Operator: research agent, campaign c5-k4, method frozen METHOD_V1_6 §A1/§A6.
Upstream pinned commit: `2411d22e` (google-deepmind/formal-conjectures); mathlib rev 0df444a3 (v4.33.1).
Inventory: results/expansion/open_targets_oeis_erdos_20260815.json — 364 untouched ErdosProblems entries auditable (9 previously touched excluded).
Local mirror lacked ErdosProblems/; all audited files fetched from raw.githubusercontent.com at pinned sha into /tmp/erdos2/lean (364/364 fetched, byte-checks on 647 vs main identical).
Budget: hard 60 s per solver process (enforced with alarm-based wrapper). Append-only ledger; one markdown per audited problem.

Triage (§A4): keyword scan → 58/364 graph-flavored; concrete-numeral scan over all answer(sorry) blocks → 44 candidates ranked; deep work ordered by band (1 faithfulness defects > 2 finite refutation > 3 retro/status-sync), per A1.

## Running log

- [audit] EP 61,70,74,75,108,141,193,398,506 read/classified → asymptotic/cardinal class, not bounded-evaluable; faithful. COMPACT_AUDITS.md. (appended)
- [audit+compute] EP 647: ⨆-parse defect hypothesis REJECTED by internal typecheck evidence (ciSup_le unification) — statement faithful; three-path exact search to 5·10⁶ empty above n=24; DB-sanity recovers {24}. **Duplicate gate: open issue #5021 (Millennium Research, kernel-checked exclusion to 10⁸ + literature to 9.17·10¹⁸) ⇒ STOP_DUPLICATE_PRIOR_ART, row downgraded to retro-confirmation.** EP647.md. (appended)
- [audit+compute] EP 931: faithful; solution censuses for (k₁,k₂) ∈ {(3,3),(4,4)} exact and plateauing (16 resp. 5 solutions, max n₂ = 58562 inside numbers ≤ 1.5·10⁶); independent sympy path reproduces all ≤ 3000 solutions identically; searcher reproduces upstream AlphaProof witness (10,3,0,13) exactly after catching an off-by-one via that gate. HOLD_BOUNDED. EP931.md. (appended)
- [audit+compute] EP 288: |I₂|=1 variant enumerated exactly to 400: six sporadic solutions incl. the source example [3,6]+{20}; single-interval sanity matches Kürschák. HOLD_BOUNDED data record. EP288.md. (appended)
- [structural stop] EP 1212: diagonal-jog automaton idea for an explicit ray written down; stopped at Phase 0 because pinned file already carries 2026 partial-result cores naming a "no-periodic-certificate theorem" — prior-art domain (v0.9 local theorem-domain audit). STOP_PRIOR_ART_DOMAIN. EP1212.md. (appended)
- [status-sync] EP 944: Skottová–Steiner arXiv:2508.08703 resolves k ≥ 5 ∀ r; open core is k=4 (Dirac). Declaration status correctly open; no sync action; degeneracy (∅ critical set) checked non-vacuous. STATUS_NOTE. EP944.md. (appended)
- [faithfulness audit] EP 723: degenerate order-1 plane excluded by Mathlib `one_lt_order`; IsPrimePow safe. AUDIT_CLEAN. EP723.md. (appended)

## Scorekeeping summary

Audited first pass: 15 problems (4 deep-with-computation, 11 read/classified/status-audited).
Crossings: 0. Defects found requiring upstream repair: 0 (one candidate parse-defect on 647 investigated and rejected with evidence).
Prior-art stops: 2 (EP 647 issue #5021; EP 1212 periodic-certificate domain in-file).
Holds/brackets recorded: EP 931 census brackets (exact, complete to 1.5·10⁶ for two k-pairs);
EP 288 enumeration to 400; EP 647 bracket superseded by #5021's larger kernel-checked bracket.
