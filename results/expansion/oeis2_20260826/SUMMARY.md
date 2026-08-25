# SUMMARY — oeis2 lane, 2026-08-26

**Lane:** OEIS only. Pinned upstream commit `2411d22e`. Inventory:
`open_targets_oeis_erdos_20260815.json` (OEIS corpus, previously_touched=false,
yield-ordered by finite_signals per METHOD_V1_6 §A1).

**Headline: 21 targets audited to full gate discipline, 0 crossings, 0 novel
claims filed.** One status-sync candidate (A102722 ~ (1−γ)n provable from
Dirichlet's divisor asymptotic) was independently derived here and then killed
by the novelty gate — KitaKen1's PR #4971 with a Lean proof was already merged
upstream on 2026-08-16. Five bounded brackets extend known computational
verification ranges; two unclaimed repair opportunities recorded.

| Target | Class | One-line result | Gates |
|---|---|---|---|
| A110835 | HOLD | Sierpiński a(n)≥n faithful; 52 terms reproduced by 2 code paths; no violation | a,b,c,d |
| A102722 | STATUS-SYNC (prior art) | asymptotic follows from Dirichlet divisor estimate; already merged upstream as PR #4971 | a,c,d(killed) |
| A000041 (41) | HOLD | Sun's perfect-power partition conjecture verbatim; still open per 2025–26 literature | a,b,d |
| A101779 | HOLD | least-k prime AP definition + conjecture faithful; head hand-checked | a,b,d |
| A056777 | HOLD | McCranie quadruple conjecture faithful; Lean converses correctly conditional; verified to 10^12 at source | a,b,d |
| A109227 | HOLD | indicator-string encoding pinned by OEIS %e matches Lean incl. zero-drop; open question faithful | a,b,d |
| A107247 | HOLD + repair opp. | nonacci offset subtlety resolved in Lean's favour; all 9 sorried textbook claims verified twice; next prime > n=699 (bracket) | a,b,c,d |
| A113257 | HOLD_BOUNDED | Q1 no prime 3≤n≤95 (certificates+BPSW); Q2 no square 3≤n≤2500, each by explicit QR obstruction | a,b,c,d |
| A081091 | HOLD | Wagstaff 3-bits infinitude faithful | a,b,d |
| A116150 | HOLD_BOUNDED | five claimed primes verified; no prime for 432≤n<4860 (bracket, ~2300-digit terms) | a,b,c,d |
| A067720 | HOLD_BOUNDED | k=8 sole composite-(k+1) member in [1,60000] by 2 independent implementations; b-file to 1548870 consistent | a,b,c,d |
| A110475 | HOLD_BOUNDED | exceptional set {1..7,9,11} exact up to 10^6; two of this lane's own bugs caught by cross-checking | a,b,c,d |
| A113213 | HOLD | O(n³) not finitely falsifiable; definition+sentinel faithful | a,b,d |
| A001146 | HOLD_BOUNDED | Hasler characterization: exhaustive scan to 2·10^7 finds only 16,256,65536 | a,b,c,d |
| A108129 | HOLD | Riesel 509203-minimality encoded verbatim (Browkin–Schinzel half proved; ∀ half open) | a,b,d |
| A117027 | HOLD | determinant formula matches %F/%E exactly; cumulative-ratio reading confirmed against OEIS table | a,b,d |
| A103885 | HOLD | m=1 instance solved exactly over ℚ (P ∝ 5x²−5x+1, Q ∝ 55x²−34x+3, zeros in range); lane-own slip retracted | a,b,c,d |
| A063880 | HOLD_BOUNDED + obs. | mod-216, unique-primitive-108, decomposition all hold to 2·10^5; recorded: `exists_primitive_of_a` is research-solved-with-sorry | a,b,c,d |
| A167604 | HOLD | Chua subset-product = minFac over divisors proven equivalent (distinct-prime Euclid argument) | a,b,d |
| A228828 | HOLD | infinitude of n²+π(n) primes faithful; closed upstream PR #3393 consistent | a,b,d |
| A111114 | HOLD | ∃ᶠ encoding of "infinitely many decreases" correct; audit-only shape | a,b,d |

## Contamination / skip record

Excluded from fresh claims after duplicate-surface pre-flight (gate d):
KitaKen1 repo coverage of inventory entries 100474, 105751, 211417, 112521,
102371, 114831, 103425, 112970, 108306 (PR #4957 merged), 100478, plus merged
PR #4971 (A102722); campaign post-freeze work on A110854 (#4983), A108864
(#4985), A237271 (#4987); A306477 triaged out (source-verified to 1.2·10^12;
closed PR #3397).

## Method notes

- The verification layer earned its keep twice: the A110475 cross-check caught
  two bugs in this lane's own primary implementation that had produced a false
  counterexample set {15,21,27}, and the A103885 check caught a coefficient-
  ordering slip that had produced an apparent violation of Bala's polynomials.
- Both incidents are preserved in the reports; neither reached any claim.
- All scripts committed alongside reports; every bracket is reproducible under
  the 60-second cap.
