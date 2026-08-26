# SUMMARY — erdos3_20260826 ErdosProblems lane ROUND 2 (graph-flavored slice)

Method: METHOD_V1_6 §A1/§A6; upstream pinned `2411d22e`; DB-SANITY GATE enforced on every
claimed violation (none survived — every "violation" was a solver bug caught by the gate).
Scope: 60-file graph-flavored queue reproduced from round-1 §A4 triage (graph_queue.txt);
round-1 LEDGER's 15 ids skipped. 14 full audits below (6 deep-with-computation, 6
read/classify, 2 status/triage).

## Results table

| Target | Class | One-line result | Gates passed |
|---|---|---|---|
| EP 85 | HOLD_BOUNDED | faithful; exact f(1..7)=1,2,3,2,3,3,3 (two impls); site anchor f(4)=2 reproduced; monotonicity holds on [4,7] | source recovery, dual enumeration, site-anchor recovery |
| EP 82 | HOLD_BOUNDED | faithful; exact F(1..6)=1,2,2,2,3,3 (two impls); F(5)=3 site anchor reproduced; consistent with published G(3)=5, G(4)=7, F(7)=4 | source recovery, dual enumeration, DB-sanity |
| EP 600 | HOLD_BOUNDED | faithful; exact e(n,r) to n=7; hypothesis-reading bug (min-book not max-book) caught by cross-path; corrected duality r ≤ f_c(n) iff e(n,r) <= ceil(c n^2), verified exhaustively | source recovery, two impls agreeing, duality check |
| EP 80 | DEFECT: STATUS_SYNC | main claim (forall c in (0,1/2) exists eps: n^eps < f_c(n)) is FALSE for all c < 1/4 per Fox-Loh 2012 — quoted on the problem's own page — yet filed research open; c>1/4 true via KhN79; log variant genuinely open; header duality comment needs ceiling | literature recovery from own source page, exact f_c(n) tables |
| EP 617 | HOLD_BOUNDED | faithful (site class FALSIFIABLE); BAL anchors reproduce site claims (false at r=2; R(3,3)=6 UNSAT); BAL(9,3)=SAT explicit validated witness; BAL(10,3)=UNSAT via z3-SMT 3m35s confirming ErGy99 r=3; DFS/DIMACS engines exceeded caps (recorded honestly) | three solver engines agreeing on anchors; witness re-validation; DB-sanity |
| EP 60 | HOLD_BOUNDED | main faithful/asymptotic; exact ex(n,C4) n<=7 and min-C4-above-ex = 1 at n in {4,6,7} (single-C4 witnesses cycle-enumerator-validated); A006856 identified as girth>=5 sequence (contamination warning recorded) | two impls after subset-formula overcount bug caught; orthogonal validation |
| EP 595 | AUDIT_CLEAN | faithful; unusually strong upstream file with script-proved variants (star decomposition of K_N, heredity, edge-colouring reformulation) | source recovery |
| EP 593 | AUDIT_CLEAN + editorial note | faithful to site "characterize", but main encodes a formalizer-added conjecture (obligatory <-> Property B), honestly labeled | source recovery |
| EP 1175 | AUDIT_CLEAN | faithful; shelah_consistency correctly an answer(sorry) placeholder w/ model-theoretic caveat (no consistency-as-negation defect) | source recovery |
| EP 918 | AUDIT_CLEAN + repair-candidate | faithful induced/all-subgraphs split; four textbook+sorry impossibility declarations flagged as hygiene repair-candidates | source recovery |
| EP 579 | AUDIT_CLEAN | faithful quantifier order (= much-greater-than_delta); octahedron encoding correct; EHSS partial result present | source recovery |
| EP 740 | AUDIT_CLEAN | faithful walk-based NoShortOddCycle encoding sound; TODO gap for f_r(m)/girth variants = documentation scope | source recovery |
| EP 1007 | STATUS_NOTE | solved file correct: 9 = K33, 15 = K6/K133 (recomputed); external formal-proof link live | link check, recomputation |
| EP 978 | TRIAGE CORRECTION | not graph-flavored (keyword noise); DeepMind-disproof trail correctly recorded upstream | docstring-level check |

## Headline

**1 crossing: EP80 status-sync defect (main statement known false on its own quantifier
range — repairable by re-scoping to the log question or restricting c).** 0 statement-level
formalization defects otherwise. Repair-candidates/hygiene: EP918 textbook-sorry quartet,
EP80 header-comment ceiling. Data/brackets recorded for 85/82/600/60/617. Queue pruned:
~34 keyword-noise files reclassified out of the graph slice (ledger note).

## Solver-bug postmortem (campaign arsenal value)

The DB-SANITY gate earned its keep twice in one day:
1. EP617 search returned SAT regardless of outcome (return placement) AND used AND-NOT undo
   after idempotent OR updates (must snapshot-restore). The (4,2)/(5,2)/(6,2) anchors caught
   both immediately.
2. EP600/60 hypothesis/count formulas (min-book vs max-book; 4-subset edge-count vs pairwise
   common-neighbors) were both caught by dual-path disagreement before any number shipped.

## Artifacts

LEDGER.md (append-only), per-problem .md x14, graph_queue.txt, solvers/ (ep85_f,
ep85_indep, ep82_F, ep82_indep, ep600_ep80_joint, ep600_ep80_indep, ep617_balanced,
ep617_c.c, ep617_z3, ep617_smt, ep60_twocopies, ep60_indep). All numeric claims carry their
caps: enumeration caps stated per run; z3/SMT timeouts recorded where they occurred.
