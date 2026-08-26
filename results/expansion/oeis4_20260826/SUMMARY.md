# SUMMARY — oeis4 lane (OEIS ROUND 4), 2026-08-26

**Lane:** OEIS only. Pinned upstream commit `2411d22e`. Inventory:
`open_targets_oeis_erdos_20260815.json` (OEIS corpus, previously_touched=false),
minus rounds 2–3 audited sets and both KitaKen1 contamination lists. The
uncovered pool was EXACTLY 16 entries; all 16 audited to full gate discipline
(target ≥15).

**Headline: 16 full audits, 0 new claims filed — the three genuine defects
found this round were each killed by the novelty gate as PRIOR_ART, and two
more targets were proven upstream post-pin (status-sync). One complete repair
candidate developed (A109074). Inequality-type special focus executed with
rigorous rational enclosures where feasible.**

| Target | Class | Result | Gates |
|---|---|---|---|
| A113019 | DEFECT + DUP_PRIOR_ART (#4953) | fixed points EXACTLY {1,32,9^9=387420489} by COMPLETE finite enumeration; Lean "{1,32}" false at n=387420489; matches OEIS %C Kitamura Aug 14 2026; KitaKen1 PR #4953 merged 08-20 | a,b,c,d(✗) |
| A109074 | DEFECT ×2 + REPAIR (complete) + PRIOR_ART (#5024/#4923) | Lean `b` is A001764 not A005156; statement false at n=1 (1≠3); OEIS's own shift wrong: true relation frac n = A005156(n)/A005156(n−1) is a THEOREM of Kuperberg-proved Razumov–Stroganov product formula → sorry closable after fixing refs/shift | a,b,c,d(killed) |
| A111291 | DEFECT + PRIOR_ART (#4923) | inequality false for EVERY real x∈(1,2) (x−2lnx>0 ⇒ RHS>1=LHS); integer points clean to 10^7 (counts reproduce b-file exactly) incl. right-endpoint worst case → repaired statement viable; itemized upstream already | a,b,c,d(killed) |
| A108211 | HOLD_BOUNDED + STATUS-SYNC (dup #5027) | Kimberling floor formula verified per-term: rigorous rational log2 enclosure (width 7e-37) n=1..400 exact over ℚ; mpmath clean to n=10121; proven upstream PR #5027 merged 08-24 | a,b,c,d(killed) |
| A105565 | HOLD_NUMERIC + STATUS-SYNC (dup #4958) | Lean maxK=5n+10 filter SAFE n≤299; Iverson formula zero mismatches n≤3000; β−2<S(n)−αn<β−1 holds n≤3000, min margins 2.06e-5/6.61e-4; solved upstream 08-15 | a,b,c,d(killed) |
| A105720 | HOLD_BOUNDED | squares in n≤20000 are EXACTLY {3,6,4072} (36=6²,169=13²,247590225=15735²) — "(?)" bracket extended; heads + prime list match; two paths | a,b,c,d |
| A108569 | HOLD_BOUNDED | φ(k)=φ(k+φ(k)): 384 terms ≤1e6, only odd term is 1; heads match %S+b-file; sympy recheck + sample cross-scan clean | a,b,c,d |
| A103151 | HOLD_BOUNDED + OEIS-edit obs. | counts match b-file EXACTLY (60 terms); existence scan clean to n=1.5e6; "stronger than Goldbach" wording is source-side (Levy/Lemoine type) → OEIS-edit candidate only | a,b,c,d |
| A109908 | HOLD_BOUNDED | greatest prime k(n−k)−1 >0 for ALL n=4..5·10^5 (early-exit + exhaustive fallback) | a,b,c,d |
| A109909 | HOLD_BOUNDED | count version: b-file reproduced exactly (60 terms); sup>0 ⟺ count≥1 consistency perfect n≤2000 | a,b,c,d |
| A108866 | HOLD_BOUNDED | Ordowski congruence iff-prime: BOTH directions clean to n=4000; head matches b-file 16 terms; Fraction vs lcm-denominator paths agree | a,b,c,d |
| A115257 | HOLD_BOUNDED | Sun irreducibility P_n/Q_n: ZERO reducible cases n≤95 (factor_list) + independent Rabin GF(p) certificates 77/80 (rest trivial/covered) | a,b,c,d |
| A114137 | HOLD_NUMERIC ×2 | semiprime gaps above 2^n: gap=1 occurs 24× by n=141; 25 distinct gaps; 11 odd values ≤69 unwitnessed; infinitary → numeric only | a,b,c,d |
| A11545 (A011545) | HOLD_NUMERIC ×2 | Haken no-square: NONE n≤6000; collision interval containment NONE n≤1200 (closest approach n=761, slack 1.6e-7) | a,b,c,d |
| A231201 | HOLD_BOUNDED | Sun $1000: witnesses for ALL n∈[2,1129] via two paths/two oracles (sympy BPSW vs own MR, cross-asserted); rep-count head matches %S | a,b,c,d |
| A108081 | HOLD_BOUNDED (strong support) | word closure enumerated exhaustively: \|X_n\|=a(n−1) EXACTLY for n=2..9 (beyond file tests); Barry≡main formula n≤40 | a,b,c,d |

## Novelty / contamination record

- Pre-flight GitHub issue/PR sweep for all 16 A-numbers (search API, pinned UA).
- Claims filed: **NONE** — every defect/priority opportunity was pre-existing:
  - #4953 (merged 2026-08-20) covers the A113019 disproof;
  - #5024 (open) + checklist item in #4923 (open) cover both A109074 defects;
  - #4923 (open) covers the A111291 boundary defect;
  - #5027 (merged 2026-08-24) proves A108211; #4958 (merged 2026-08-15)
    solves A105565.
- No target overlapped the round-2/3 KitaKen1 repo lists (verified).

## Value-add beyond prior art

- A113019: complete finite (d,r)-table proof that {1,32,387420489} is the
  FULL fixed-point set (prior art shows one counterexample only).
- A109074: corrected identity PROVEN symbolically via Razumov–Stroganov
  (Kuperberg) — turns the misformalized "conjecture" into a theorem; exact fix
  sketch recorded.
- A111291: integer-point verification to 10^7 + monotone right-endpoint
  reduction = the evidence needed for #4923's proposed "sufficiently large"
  restatement.
- A105565: proved the flagged maxK filter safe (n≤299 exhaustive).
- A108081: independent word-enumeration extends Xia's check from length 3
  to length 9.

## Method notes

- Verification layer caught this lane twice BEFORE any verdict: A109074 v1
  used a wrong guessed A005156 product formula (replaced by OEIS-fetched
  b-file ground truth + symbolic proof), and harness bugs in A115257
  (exponent/degree confusion), A114137 (candidate parity), A108866 (path-2
  algebra, comparison length) were all caught by cross-path disagreement and
  fixed before classification. Logs preserve final runs.
- oeis.org requires `-L` for b-files (`b<pad>.txt` → `/A<pad>/b<pad>.txt`);
  raw.githubusercontent bursts reset connections → sequential retries.
- All scripts + logs under lane root; every bracket reproducible under the
  60-second cap. Venv: .venv/bin/python (sympy 1.14.0, mpmath, numpy).

## Lane outcome

16 full audits · 3 declaration defects (all prior-art-killed, documented with
fix sketches) · 1 complete formalization-repair candidate (A109074) ·
2 status-sync pairs (A108211, A105565) · 11 clean holds with brackets extended
· 0 new crossings claimed · 0 novel claims filed.
