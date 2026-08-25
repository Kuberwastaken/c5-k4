# LEDGER — oeis2 lane, 2026-08-26

Pinned upstream commit: `2411d22e` (google-deepmind/formal-conjectures).
Inventory: results/expansion/open_targets_oeis_erdos_20260815.json, corpus=OEIS,
previously_touched=false, ordered by finite_signals desc (METHOD_V1_6 §A1).
Lane rules: 60 s hard cap per solver/search process; exact arithmetic where feasible;
independent recomputation via second code path; novelty check before claims.
No git commands from this agent.

Pre-flight notes:
- Local mirror /Users/kuber.mehta/Personal-Projects/c5-k4/upstream/formal-conjectures exists
  but contains NO FormalConjectures/OEIS directory (only WrittenOnTheWallII), so all target
  files are fetched from raw.githubusercontent.com at commit 2411d22e into
  upstream_cache/ via fetch_upstream.py (UA: OpenAI File Downloader, XaiImageApiFetch/1.0).
- Campaign post-freeze prior work on inventory entries flagged previously_touched=false
  (CONTRIBUTIONS.md): A110854 (PR #4983 crossing), A108864 (PR #4985 repair),
  A237271 (PR #4987 merged repair). These three are excluded from fresh discovery claims;
  recorded below as SKIP_PRIOR_CAMPAIGN_WORK unless audited for unfixed residue.

## Entries

1. [2026-08-26] A110835 (finite_signals 43) — AUDITED → HOLD.
   Faithful declaration; source quote matches verbatim; two independent code
   paths reproduce published terms n=1..52 exactly; a(n)>=n holds in range.
   Report: a110835.md. No defect, no crossing.
2. [2026-08-26] A102722 (finite_signals 10) — STATUS-SYNC derived independently
   (sum{n/k} = nH_n - Dirichlet divisor summatory = (1-gamma)n + O(sqrt n)),
   verified exact to n=300 + mpmath at n=1e3/1e4 vs b-file. NOVELTY GATE KILLED:
   KitaKen1 PR google-deepmind/formal-conjectures#4971 "Mark OEIS A102722
   asymptotic as solved", MERGED 2026-08-16. Class: DUPLICATE_PRIOR_ART.
   Scripts: a102722_primary.py, a102722_independent.py.
3. [2026-08-26] Contamination sweep (duplicate-surface pre-flight): KitaKen1
   GitHub repos cover inventory entries 100474, 105751, 211417, 112521, 102371,
   114831, 103425, 112970, 108306, 100478 (repo names listed in
   results/expansion/publication/kitaken1-activity-analysis.md and live API).
   These are excluded from fresh claims pending explicit upstream PR/issue
   confirmation per target. Campaign post-freeze work excludes 110854, 108864,
   237271. Remaining clean head: 108129, 117027, 107247, 41, 101779, 306477,
   113257, 109905, 116150, 81091, 103885, 113213, 67720, 109227, 110475,
   111114, 1146, 228828, 63880, 167604.

## Entries (batch 2, 2026-08-26)

6. A000041 (41.lean) — HOLD. Sun perfect-power partition conjecture verbatim;
   still open (Merca-Ono-Tsai 2025, Ono 2025 confirm cases only). a41.md.
7. A101779 — HOLD. Definition and "k always exists" conjecture faithful;
   test terms hand-checked. a101779.md.
8. A056777 — HOLD. McCranie prime-quadruple conjecture faithful, verified to
   1e12 at OEIS; Lean converses correctly conditional. Cosmetic module-title
   artifact noted. a056777.md.
9. A109227 — HOLD. Primality-indicator strings; leading-zero convention pinned
   by %e matches Lean; open question faithfully encoded. a109227.md.
10. A107247 — HOLD + REPAIR_OPPORTUNITY. Nonacci sum-of-squares definition
    reproduces published terms exactly (offset subtlety verified);
    `known_prime_and_semiprimes` (textbook+sorry): all 9 conjuncts verified by
    two independent factorization paths; next-prime bracket n>699.
    a107247.md.
11. A113257 — HOLD_BOUNDED. Q1: no prime for 3<=n<=95 (parity+divisibility
    certificates; survivors BPSW); cap inside n=106 PRP (~20k digits).
    Q2: no square for 3<=n<=2500; every exclusion an explicit QR obstruction
    (survivor n=1914 killed mod 113). a113257.md.
12. A081091 — HOLD. Wagstaff three-1-bits infinitude; faithful. a081091.md.
13. A116150 — HOLD_BOUNDED. Claimed primes a(11),a(17),a(71),a(91),a(431)
    all verified; no prime for 432<=n<4860 (bracket). a116150.md.
14. A067720 — HOLD_BOUNDED. Only member with composite k+1 is k=8 in [1,60000]
    (two independent implementations incl. own Pollard rho/Miller-Rabin);
    published b-file to 1548870 consistent. a067720.md.
15. A110475 — HOLD_BOUNDED. Unrepresentable set == {1..7,9,11} exactly up to
    1e6 (bitset path) and 2e5 (trial-division path); two of this lane's own
    implementation bugs caught and fixed via cross-checking (documented).
    a110475.md.
16. A113213 — HOLD. O(n^3) claim not finitely falsifiable; definition faithful
    incl. a(1)=0 sentinel. a113213.md.
17. A001146 — HOLD_BOUNDED. Hasler k^4-1 | 2^k-1 characterization: exhaustive
    exact scan to 2e7 finds only 16,256,65536. a001146.md.
18. A108129 — HOLD. Riesel 509203-minimality verbatim faithful. a108129.md.
19. A117027 — HOLD. Determinant formula matches %F/%E exactly; ratio-limit
    formalization faithful to Bala-style comment. a117027.md.
20. A103885 — HOLD. m=1 instance of recurrence-polynomial conjecture solved
    exactly over Q: unique P ∝ 5x^2-5x+1, Q ∝ 55x^2-34x+3, zero-location OK.
    An apparent violation was this lane's own coefficient-ordering slip,
    retracted here per protocol. a103885.md.
21. A063880 — HOLD_BOUNDED + observation. All members ≡108 mod 216 to 2e5;
    only primitive = 108; decomposition property holds throughout.
    Recorded (unclaimed): `exists_primitive_of_a` marked research-solved with
    sorry body. a063880.md.
22. A167604 — HOLD. Chua subset-product min-fac reformulation proven equivalent
    (distinct-prime terms ⇒ divisors = subset products). a167604.md.
23. A228828 — HOLD. Infinite-sequence conjecture faithful; PR #3393 closed
    upstream, consistent. a228828.md.
24. A111114 — HOLD. floor(prime(n)/pi(n)) decreases-infinitely-often;
    ∃ᶠ encoding correct; audit-only shape. a111114.md.
25. A306477 — SKIP_TRIAGE. Sun 2-4-6-8 conjecture verified to 1.2e12 at source
    (Baruch 2019); closed upstream PR #3397 claimed a solution. No finite lane.

## Lane outcome

0 crossings, 0 new repair/status claims filed upstream, 21 full audits,
1 status-sync calibration (prior art), 2 recorded unclaimed repair
opportunities, 5 bounded brackets extending known verification ranges.
Contamination pre-flight excluded 11 KitaKen1-covered entries and 3
campaign-post-freeze entries from claims (see entry 3).
