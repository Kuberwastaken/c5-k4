# LEDGER — oeis4 lane (OEIS ROUND 4), 2026-08-26

Pinned upstream commit: `2411d22e` (google-deepmind/formal-conjectures).
Inventory: results/expansion/open_targets_oeis_erdos_20260815.json, corpus=OEIS,
previously_touched=false, minus rounds 2-3 audited sets and both contamination
lists (round-2: KitaKen1 repos 100474, 105751, 211417, 112521, 102371, 114831,
103425, 112970, 108306, 100478 + PR #4971/A102722 + post-freeze 110854, 108864,
237271 + triaged 306477; round-3: A105801, A113249-family).
Lane rules: 60 s hard cap per solver/search process; exact arithmetic where feasible;
independent recomputation via second code path; novelty check before claims.
SPECIAL FOCUS this round: asymptotic/inequality-type declarations — per-term
checkable relations computed exactly; genuinely asymptotic claims get numeric
evidence labelled HOLD_NUMERIC only. One wrong term = CROSSING.
No git commands from this agent.

Pre-flight notes:
- All 16 remaining uncovered inventory entries fetched fresh from
  raw.githubusercontent.com at pinned commit into upstream_cache/
  (UA: OpenAI File Downloader, XaiImageApiFetch/1.0; transient connection resets
  retried sequentially - 16/16 ok).
- OEIS pages (fmt=text internal format) to oeis_pages/, b-files to bfiles/
  (curl -L following oeis.org redirect to /A<pad>/b<pad>.txt).
- Remaining pool is EXACTLY these 16 entries: 105720, 108569, 103151, 108081,
  105565, 108211, 109908, 109909, 108866, 115257, 114137, 113019, 109074,
  111291, 11545 (A011545), 231201. Target >=15 => audit all 16.

## Contamination pre-flight (gate d)

(to be appended per-target below)

## Entries

1. [2026-08-26] A113019 — AUDITED -> DECLARATION_DEFECT (classification false),
   claim killed DUPLICATE_PRIOR_ART. Exhaustive (d,r)-enumeration (complete, no
   bound): fixed points EXACTLY {1, 32, 387420489=9^9}; brute scan n<=1e7
   agrees in range. Lean RHS "fixed points = {1,32}" false at n=387420489;
   matches OEIS %C added by Kenta Kitamura 2026-08-14. NOVELTY KILLED:
   KitaKen1 PR google-deepmind/formal-conjectures#4953 (disproof) MERGED
   2026-08-20 > pin => defect live at pin, filing would duplicate. Value-add
   recorded: complete-set repair via finite table. Report a113019.md;
   scripts/a113019_fixedpoints.py; a113019_run1.log.
2. [2026-08-26] A109074 — AUDITED -> DECLARATION_DEFECT x2 + COMPLETE REPAIR
   CANDIDATE; claim killed PRIOR_ART (issue #5024 open 2026-08-18). (i) Lean
   `b` is A001764 (=C(3n,n)/(2n+1), verified n<=60), NOT A005156; (ii) Lean
   statement frac n = b(n+1)/b(n) FALSE at n=1 (1 vs 3); (iii) OEIS comment's
   own shift wrong too: true relation frac n = A005156(n)/A005156(n-1), exact
   n=1..66 AND symbolic — immediate theorem of Kuperberg-proved
   Razumov-Stroganov product formula => sorry closable after fixing refs.
   Numerators match b-file head. Report a109074.md;
   scripts/a109074_identity{,_v2}.py; a109074_run{1,2}.log.
3. [2026-08-26] A111291 — AUDITED -> DECLARATION_DEFECT (inequality false as
   formalized); claim killed PRIOR_ART (itemized in issue #4923 open
   2026-08-13). For EVERY real x in (1,2): LHS=count(1)=1 < x/(2 log x)
   (since x-2log x>0 always); explicit x=1.5, 1.1, 1.001. BOUNDED BRACKET:
   independent linear-sieve tau to 1e7 reproduces b-file heads n<=7 EXACTLY;
   zero violations count(m)>=m/(2 ln m) for integer m in [2,1e7], and also
   zero right-endpoint worst-case violations => repaired statement viable.
   Repair sketch recorded (integer version / explicit threshold). Report
   a111291.md; scripts/a111291_refactorable.py; a111291_run1.log.
4. [2026-08-26] A108211 — AUDITED -> HOLD_BOUNDED + STATUS-SYNC (claim killed
   DUPLICATE_PRIOR_ART: PR #5027 MERGED 2026-08-24 proves the floor formula).
   Kimberling floor identity verified PER-TERM: rigorous rational log2
   enclosure (width 7e-37) confirms n=1..400 exactly over Q; mpmath dps=60
   clean to n=10121 under cap; margins shrink ~1/(16n^4), asymptotic sketch
   matches upstream proof approach. At-pin sorry/status-sync noted. Report
   a108211.md; scripts/a108211_floor.py; a108211_run1.log.
5. [2026-08-26] A105565 — AUDITED -> HOLD_NUMERIC + STATUS-SYNC (claim killed
   DUPLICATE_PRIOR_ART: PR #4958 MERGED 2026-08-15 marks solved). Lean maxK=
   5n+10 filter verified SAFE n<=299 (def faithful). Exact fib digit-counts
   match OEIS %S head + b-file 120 terms; independent Iverson formula path
   matches n=2..3000 (zero mismatches); inequality beta-2<S(n)-alpha*n<
   beta-1 holds n<=3000, min margins 2.06e-5 / 6.61e-4. Infinitary =>
   numeric label only. Report a105565.md; scripts/a105565_fibdigits.py;
   a105565_run1.log.
6. [2026-08-26] A105720 — AUDITED -> HOLD_BOUNDED. Square classification
   "only(?) n=3,6,4072": all three reproduced exactly (36=6^2, 169=13^2,
   247590225=15735^2); hunt n<=20000 finds NO further square (bracket
   extended); heads + prime-at-n list match %S/%C; two paths (numpy sieve
   sliding window vs sympy.primerange). Report a105720.md;
   scripts/a105720_squares.py; a105720_run1.log.
7. [2026-08-26] A108569 — AUDITED -> HOLD_BOUNDED. phi(k)=phi(k+phi(k)):
   384 terms k<=1e6; ONLY odd term is 1 => conjecture clean in range; heads
   match %S(20)+b-file(30); sympy totient recheck zero mismatches; sample
   cross-scan zero misses. Report a108569.md; scripts/a108569_phi.py;
   a108569_run1.log.
8. [2026-08-26] A103151 — AUDITED -> HOLD_BOUNDED + OEIS-edit observation.
   Levy/Lemoine-type counts: full counts match b-file EXACTLY (60 terms);
   existence scan clean to n=1.5e6 ("stronger than Goldbach" wording is
   source-side, faithfully copied - recorded as OEIS-edit candidate, not a
   Lean defect). Reports a103151.md; scripts/a103151_lemoine.py;
   a103151_run1.log.
9. [2026-08-26] A109908 + A109909 — AUDITED -> HOLD_BOUNDED x2. Existence
   scan zero violations n=4..5e5 (OEIS reports 1e9); b-files of BOTH
   sequences reproduced exactly (60 terms each); max>0 <=> count>=1
   consistency n<=2000. Joint report a109908_909.md;
   scripts/a109908_909_knp.py; a109908_909_run1.log.
10. [2026-08-26] A108866 — AUDITED -> HOLD_BOUNDED. Ordowski congruence
    num(-2/n+Sum 2^k/k) == 0 mod n^2 <=> prime: BOTH directions clean to
    n=4000 (one wrong term would be crossing); sequence head matches b-file
    16 terms; Fraction path vs lcm common-denominator path agree on samples.
    Report a108866.md; scripts/a108866_wolstenholme.py; a108866_run1.log.
11. [2026-08-26] A115257 — AUDITED -> HOLD_BOUNDED. Sun irreducibility of
    P_n/Q_n: ZERO reducible cases n<=95 (sympy factor_list) + independent
    Rabin GF(p) certificates 77/80 (3 trivial degree-1 / covered by path 1);
    head sums match. Report a115257.md; scripts/a115257_irred.py;
    a115257_run{1,2,3}.log.
12. [2026-08-26] A114137 — AUDITED -> HOLD_NUMERIC x2. Semiprime gaps above
    2^n: head n=0..12 matches b-file exactly; scan to n=141 (cap): gap=1
    occurs 24x (2^n+1 odd semiprime); 25 distinct gap values; 11 odd values
    <=69 unwitnessed. Both conjectures infinitary => numeric labels only.
    Report a114137.md; scripts/a114137_semiprimegap.py; a114137_run1.log.
13. [2026-08-26] A11545 (A011545) — AUDITED -> HOLD_NUMERIC x2. Haken no-
    square conjecture: no square term n<=6000 (mpmath dps 6260 + exact
    isqrt); collision-interval containment NONE n<=1200, closest approach
    n=761 slack 1.6e-7; b-file head matches floor(pi*10^n). Infinitary =>
    numeric labels. Report a11545.md; scripts/a11545_pi.py; a11545_run1.log.
14. [2026-08-26] A231201 — AUDITED -> HOLD_BOUNDED. Sun $1000 witnesses:
    ALL n in [2,1129] witnessed by TWO paths (y-first/sympy-BPSW vs x-desc/
    own Miller-Rabin, cross-asserted), cap at 1130; all six Lean test
    witnesses verified; representation-count head matches %S exactly.
    Report a231201.md; scripts/a231201_sun.py; a231201_run1.log.
15. [2026-08-26] A108081 — AUDITED -> HOLD_BOUNDED (strong support). Word
    closure enumerated exhaustively by levels: |X_n| = a(n-1) EXACTLY for
    n=2..9 (beyond file's own tests); Barry formula == main binomial
    formula n<=40; head matches b-file. Report a108081.md;
    scripts/a108081_words.py; a108081_run1.log.

## Lane outcome (final)

16/16 remaining uncovered inventory entries audited to full gate discipline
(target was >=15). Findings: 3 declaration defects (A113019 fixed-point
classification false - third fixed point 9^9=387420489, complete-set proof;
A109074 double misformalization + sorry closable after repair; A111291
inequality false on (1,2)) - ALL THREE killed as PRIOR_ART (#4953 merged,
#5024/#4923 open respectively) => 0 novel claims filed. 1 status-sync pair
(A108211, A105565 both proven upstream post-pin, #5027/#4958). 11 clean
HOLD/HOLD_BOUNDED/HOLD_NUMERIC audits with brackets extended (notably
A103151 to n=1.5e6 existence; A105720 square-hunt to n=20000; A109908/909
to n=5e5; A108569 odd-term hunt to k=1e6).
