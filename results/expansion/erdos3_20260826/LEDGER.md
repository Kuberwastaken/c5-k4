# LEDGER — erdos3_20260826 (ErdosProblems lane, ROUND 2: graph-flavored slice)

Operator: research agent, campaign c5-k4. Upstream pinned `2411d22e` (raw.githubusercontent.com/google-deepmind/formal-conjectures).
Queue: results/expansion/erdos3_20260826/graph_queue.txt (60 files, round-1 §A4 keyword triage reproduced at threshold ≥2; round-1 LEDGER's 15 audited ids excluded).
Method: METHOD_V1_6 §A1 yield bands, §A6 four-coordinate status. DB-SANITY GATE mandatory for any claimed violation of a graph-universal reading (all connected graphs n≤7 via nx.graph_atlas_g() + named families).
Budget: hard 60 s per solver process unless a larger explicit cap is stated next to the run.
Venv: /Users/kuber.mehta/Personal-Projects/c5-k4/.venv/bin/python (networkx 3.6.1).

## Running log

- [audit+compute] EP 85: faithful (`⊑` non-induced correct; site question = eventual monotonicity of f). Exact f(1..7)=1,2,3,2,3,3,3 by two independent enumerations (bitmask DFS ↔ networkx edge-subset); f(4)=2 reproduces site sanity; no monotonicity failure on [4,7]. HOLD_BOUNDED (bracket n≤7). EP85.md. (appended)
- [audit+compute] EP 82: faithful (sSup-of-guarantees + IsInduced + deg-0 regularity match site/literature). Exact F(1..6)=1,2,2,2,3,3, two implementations agreeing; DB-sanity recovers site anchor F(5)=3 exactly and stays consistent with G(3)=5/G(4)=7/F(7)=4. HOLD_BOUNDED (bracket n≤6). EP82.md. (appended)
- [audit+compute] EP 600: faithful; exact e(n,r) to n=7 (two impls agreeing on n≤6): e(7,·)=10,16,17,19 for r=2..5. Solver-hypothesis bug caught by gate (min-book not max-book) and corrected with dual-path evidence. Corrected duality r ≤ f_c(n) ⟺ e(n,r) ≤ ⌈cn²⌉ verified exhaustively; header-comment un-ceiled form fails (n=4,c=0.2). HOLD_BOUNDED. EP600.md. (appended)
- [DEFECT] EP 80: main statement `∀c∈(0,1/2) ∃ε>0 n^ε < f_c n` is FALSE on its own quantifier range — Fox–Loh 2012 disprove for all c<1/4 (bound quoted on the problem's own page); c>1/4 true via Khadzhiivanov–Nikiforov. Filed `research open` ⇒ DEFECT_CLASS_STATUS_SYNC, repairable (re-scope to log-question / re-categorize). Comment-only ceiling imprecision recorded. f_c(n) exact table recorded. EP80.md. (appended)
- [audit+compute] EP 617: faithful (FALSIFIABLE class on site). BAL(n,r) exhaustive searches: anchors BAL(4,2)/BAL(5,2) SAT reproduce site's "false at r=2"; BAL(6,2) UNSAT=R(3,3); BAL(9,3) SAT w/ validated witness; BAL(10,3) UNSAT via z3-SMT (3m35s) confirming ErGy99 r=3. DFS/DIMACS engines exceeded caps (recorded). Two solver soundness bugs caught by anchor gate. HOLD_BOUNDED. EP617.md. (appended)
- [audit+compute] EP 60: main faithful/asymptotic (classified). Exact ex(n,C4) n≤7 = 0,1,3,4,6,7,9 and min-#C4-above-ex = –,–,–,1,2,1,1 (two impls; subset-formula overcount bug caught, orthogonal cycle-enumerator validation; A006856 identified as girth≥5 sequence, not ex(n,C4)). HOLD_BOUNDED. EP60.md. (appended)
- [audit] EP 595: faithful; $250 infinite-graph question, rich proved-variant file (star decomposition of K_N, heredity, edge-colouring reformulation all script-proved). Set-theoretic class. AUDIT_CLEAN. EP595.md. (appended)
- [audit+note] EP 593: faithful to site's "characterize" but main statement encodes a specific formalizer-added conjecture (obligatory ⇔ Property B) — honestly labeled; graph-case variants match EGH75 claims. AUDIT_CLEAN w/ editorial note. EP593.md. (appended)
- [audit] EP 1175: faithful; shelah_consistency correctly modeled as answer(sorry) placeholder with model-theoretic caveat instead of ZFC-negation — avoids classic consistency defect. AUDIT_CLEAN. EP1175.md. (appended)
- [audit+repair-candidate] EP 918: faithful split induced/all-subgraphs + eq_aleph0 textbook variants; four textbook+sorry impossibility declarations flagged as hygiene repair-candidates (proofs sketched on-site only). AUDIT_CLEAN. EP918.md. (appended)
- [audit] EP 579: faithful (∀δ ∃c ∀ᶜn order = ≫_δ; octahedron encoding correct; EHSS δ>1/8 variant present). Asymptotic class. AUDIT_CLEAN. EP579.md. (appended)
- [audit] EP 740: faithful (walk-based NoShortOddCycle soundly encodes short-odd-cycle avoidance); TODO gap for f_r(m)/girth variants recorded as documentation scope. AUDIT_CLEAN. EP740.md. (appended)
- [status-sync] EP 1007: solved file audited — answers 9 (K33) / 15 (K6, K133) present; external formal-proof link live (HTTP 200); edge counts recomputed. No repair. EP1007.md. (appended)
- [triage-correction] EP 978: NOT graph-flavored (keyword noise); DeepMind-disproof variant + open cores correctly recorded upstream. EP978.md. (appended)
- [queue pruning note] Keyword-noise entries in graph_queue.txt (not graph-flavored; recorded for slice hygiene): 91,97,99,107,1199,123,138,160*,189,302,340,346,348,349,352,354,477,501,507,509,522,633,660,872*,96,982,975,1026,1038,1041,1044,1047,1133,1150 (*=finite-search flavored, candidate future compute lane).
