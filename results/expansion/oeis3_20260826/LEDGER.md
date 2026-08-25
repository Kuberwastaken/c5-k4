# LEDGER — oeis3 lane (ROUND 3), 2026-08-26

Pinned upstream commit: `2411d22e` (google-deepmind/formal-conjectures).
Inventory: results/expansion/open_targets_oeis_erdos_20260815.json, corpus=OEIS,
previously_touched=false, minus round-2 audited set and contamination list.
Lane rules: 60 s hard cap per solver/search process; exact arithmetic where feasible;
independent recomputation via second code path; novelty check before claims.
No git commands from this agent.

Pre-flight notes:
- All target .lean files fetched fresh from raw.githubusercontent.com at pinned commit
  into upstream_cache/ (39 files; UA per protocol).
- OEIS pages fetched to oeis_pages/ (%I edit stamps recorded per target);
  b-files to bfiles/. Python SSL to oeis.org failed (cert chain) -> curl fallback.
- Inventory id -> canonical A-number: zero-pad to 6 (id 1157 -> A001157,
  id 34693 -> A034693, id 37274 -> A037274, id 945 -> A000945); each report cites
  the A-number from the file's own reference line.
- Contamination pre-flight (gate d): KitaKen1 repos cover A105801 and the
  A113249 square-term family (=> A113250/113252/113255) as of 2026-08-15 pushes;
  excluded from fresh discovery claims.

## Entries

1. [2026-08-26] A113271 — AUDITED -> DECLARATION_DEFECT (docstring) + HOLD_BOUNDED.
   OEIS %C and Lean docstring assert "smallest primes ... a(5) = 543"; actual
   a(5) = 135457 = 7*37*523 (composite), and 543 = 3*181 is neither prime nor a
   term. Two code paths reproduce published %S/%T head n=0..7 exactly. Next-prime
   bracket: a(5)..a(11) all composite (BPSW; a(11) has 309 digits) => sInf >= 12
   if it exists. NOVELTY: no upstream issue/PR, no KitaKen1 repo, no web hit.
   Report a113271.md; scripts/a113271_terms.py; logs a113271_run1.log.
2. [2026-08-26] A102847 — AUDITED -> DECLARATION_DEFECT (docstring, two claims) +
   HOLD_BOUNDED. OEIS %C/Lean docstring: (i) "a(6) has 4 prime factors" — false,
   Omega(a6) = 6 (19*43*59*313*6091*570379); (ii) "a(7) = 41 * 811^2 * ..." —
   that product is exactly a(8) (off-by-one); true a(7) =
   3*353*609933336530249*4253659619248673. b-file confirms our terms. Bracket:
   a(5)..a(19) composite (independent BPSW re-verification of Russ Cox's 2006
   note through what was then a(20)-unknown). NOVELTY: none found upstream.
   Report a102847.md; scripts/a102847_factors.py; a102847_run1.log/run2.log.
3. [2026-08-26] A100434 — AUDITED -> CROSSING (already reported upstream;
   class DUPLICATE_PRIOR_ART). All three sorried "conjectures"
   (c+d=b, e+f=b, g+a=b) are FALSE as formalized: counterexample at n=0
   (c0+d0 = 3 vs b0 = c1 = -3; e0+f0 = 3; g0+a0 = 3) and at every even n.
   conjecture3 additionally contradicts the same file's PROVEN lemma
   `a_even : a(2n) = -c(2n+1)` (g(2n)=0 => LHS = -b(2n)). True content:
   three-way identity c(n)+d(n) = e(n)+f(n) = g(n)+a(n) holds for ALL n>=0
   (verified to n=100), and (c+d)(n) = (-1)^(n+1) * b(n). Prior art:
   google-deepmind/formal-conjectures#4560 (PR closed unmerged 2026-07-25),
   #5025 "[Misformalization] ... sign error in b ..." (issue closed completed
   2026-08-24, i.e. after pin 2411d22e — defect still present AT PIN).
   Report a100434.md; scripts/a100434_dement.py; a100434_run1.log/run2.log.
4. [2026-08-26] A107247 — REPAIR DEVELOPED (round-2 opportunity) ->
   COMPLETE FORMALIZATION-REPAIR CANDIDATE. Third independent code path
   (sliding-window nonacci + trial-division certification) verifies all 9
   conjuncts of `known_prime_and_semiprimes`; witness table emitted
   (a(17) = 37*9419; a(27) = 71*5045088967, both factors prime). Mathlib API
   identified: Nat.IsSemiprime = IsAlmostPrime 2 (Ω=2),
   Nat.Prime.mul_isAlmostPrime_two gives the proof skeleton; a-value equalities
   via equation-lemma unfolding + norm_num. Report a107247_repair.md;
   scripts/a107247_third_path.py; a107247_run3.log.
5. [2026-08-26] A108301 — AUDITED -> COMPLETE FORMALIZATION-REPAIR CANDIDATE
   (textbook-sorry `primes_in_a`, discovered this round). Digit sums of Fermat
   numbers computed by two paths: a(0)=3, a(1)=5, a(5)=59, a(6)=89, a(7)=167,
   a(11)=2741 — all prime (each conjunct verifies); context composites a(2..4),
   a(8), a(9) recorded. Hunt: no further prime digit-sum for n<=25. Proof
   closable by decide/norm_num after digits unfolding. Report a108301.md;
   scripts/a108301_digitsums.py; a108301_run1.log, a108301_run2.log.
6. [2026-08-26] A063880 — ROUND-2 OPPORTUNITY DEVELOPED -> PARTIAL REPAIR +
   STATUS-SYNC FINDING. (i) `a_of_primitive_mul_squarefree` (textbook, sorry) is
   PROVABLE in one line: for q prime, q∤n, sigma(nq) = sigma(n)(q+1) and
   usigma(nq) = usigma(n)(q+1), so A(n) => A(nq); iterate over primes of s.
   (ii) `exists_primitive_of_a` carries category research-solved but is NOT
   derivable from the file's own definitions/lemmas; its nontrivial content is
   "the powerful kernel of every term is again a primitive term". Verified here
   for all 281 terms <= 100000 (kernel property AND min-divisor decomposition
   shape), only primitive term 108 — but OEIS's own wording ("terms so far",
   "below 10^18") shows the evidence is computational. Tag overstates what is
   established: honest status is open-or-conditional => STATUS-SYNC finding
   (wrong-tag candidate), not a fillable sorry. Report a063880_repair.md;
   scripts/a063880_kernel.py; a063880_run2.log.
7. [2026-08-26] A357513 — AUDITED -> HOLD + STATUS-SYNC note. Supercongruence
   a(p-1) == 0 mod p^4 verified EXACTLY (Fractions path + fully modular path)
   for all primes 3 <= p <= 59 with sole exception p = 7 (residue 1715 mod 2401;
   cross-checked as unit-multiple agreement between paths). Negative control:
   no composite n < 30 vanishes mod n^2. general_supercongruence spot-check:
   exception sets depend on m (m=0,2 fail at p=3,5; m=3 fails at p=3,11) --
   consistent with "finite exceptions depending on m". Tag research-solved is
   JUSTIFIED: attribute points to real commit 9c7f21e7 ("AlphaProof proof",
   2026-01-15, modifies FormalConjectures/OEIS/357513.lean); sorry body at pin
   is a porting artifact. Report a357513.md; scripts/a357513_supercongruence.py.
8. [2026-08-26] A114362 — AUDITED -> HOLD_BOUNDED + STATUS-SYNC (prior art).
   Numerators via Bernoulli formula match b-file head (2, 2, 6, 691, 7234,
   523833, ...) and Lean tests. conjecture2 residual/(11^-n) stays in
   [0.78, 0.94] for n = 5..30 (mpmath dps=60), consistent with O(11^-n).
   STATUS-SYNC: upstream PR #5028 "prove conjecture2 (Ordowski's asymptotic
   expansion)" closed AFTER pin -> any claim would be duplicate; recorded only.
   Report a114362.md; scripts/a114362_zeta.py.
9. [2026-08-26] A109905 — AUDITED -> HOLD_BOUNDED. Definition reproduces Lean
   tests; zero set of a(n) is exactly {1,6,30,54} for n <= 19000 (55 s cap).
   Faithful to OEIS comment. Report a109905.md; scripts/a109905_zeros.py.
10. [2026-08-26] A113258 — AUDITED -> HOLD_BOUNDED. Head matches; sympy
    perfect_power finds NO perfect power for 5 <= n <= 11 (a(11) has 1,092,378
    digits). Report a113258.md; scripts/a113258_powers.py; run2-run4 logs.
11. [2026-08-26] A113609 — AUDITED -> HOLD_BOUNDED. Both-nonprime prime-power
    pairs (q,q+2): only (25,27) for q <= 2,000,000; none with q >= 10^6 =>
    Lean conjecture (existence q >= 10^6) remains open, bracket extended.
    Report a113609.md; scripts/a113609_pairs.py.
12. [2026-08-26] A113010 — AUDITED -> HOLD_BOUNDED. Fixed points of
    d(n)^s(n): exactly {1, 32} for n <= 2,000,000. Report a113010.md.
13. [2026-08-26] A114216 — AUDITED -> HOLD_BOUNDED. a(33900) = 1 confirmed;
    last index with a(n)=1 is 33900 among n <= 60000; head matches tests/b-file.
    Report a114216.md; scripts/a114216_lastone.py.
14. [2026-08-26] A100800 — AUDITED -> HOLD_BOUNDED. Iterates of f(n)=n+digitsum(n)
    reach a multiple of n for every n <= 5000 (cap 200000 iterations; iteration
    strictly increases so 'no-hit' is only ever a cap, recorded honestly).
    Report a100800.md; scripts/a100800_iterate.py.
15. [2026-08-26] A100475 — AUDITED -> HOLD (bounded observations). Main-sequence
    head matches b-file; trajectories from all 120 small starts leave the
    computable prime-table range before looping; no cycle found (question not
    finitely decidable for escaping trajectories). Report a100475.md.
16. [2026-08-26] A109671 — AUDITED -> HOLD. Implementation matches b-file head
    exactly; parity/sign choice (prev>mid ? prev-mid : prev+mid) is the unique
    positive solution of |x - a(2n-1)| = a(n). Surjectivity: 2945 distinct
    values in n <= 4e6, small values like 916 not yet seen (bounded obs.).
    Report a109671.md; scripts/a109671_surjective.py.
17. [2026-08-26] A110566 — AUDITED -> HOLD. Key simplification proved+used:
    a(n) = gcd(S_n, L_n) where H_n = S_n/L_n, L_n = lcm(1..n); head matches
    b-file (1,1,1,1,1,3,3,3); odd-value coverage bounded (many odds < 1000 not
    yet seen at n <= 20000; conjecture remains open per Jianing Song 2022).
    Report a110566.md; scripts/a110566_odds.py.
18. [2026-08-26] A109845 — AUDITED -> HOLD_BOUNDED. lcm-recurrence == polynomial
    recurrence verified n = 1..16 (provable: consecutive terms coprime, so
    lcm(previous)*t relation collapses); primes a(1..5) = 2,3,5,31,929; a(6..15)
    composite (digit cap). Report a109845.md; scripts/a109845_primes.py.
19. [2026-08-26] A104320 — AUDITED -> HOLD_BOUNDED. Sloane ternary-zero claim
    a(n) > 0 for n > 15: scanned n <= 4000, ZERO violations (disproof hunt
    negative). Report a104320.md; scripts/a104320_ternary.py.
20. [2026-08-26] A001157 (inv. id 1157) — AUDITED -> HOLD_BOUNDED. Sun's
    fractional-parts conjecture: no collision for k = 2..7 across n <= 60000
    (exact Fractions). Page still lists it as conjecture => tags faithful.
    Report a001157.md; scripts/a001157_fractional.py.
21. [2026-08-26] A115366 — AUDITED -> HOLD_BOUNDED. Counts reproduce Lean tests
    (9, 50, 313); ratios a(n)/pi(10^n) = 1.7801 (n=5), 1.7769 (n=6) — inside
    [1.77, 1.78]. Report a115366.md; scripts/a115366_ratio.py.
22. [2026-08-26] A034693 (inv. id 34693) — AUDITED -> HOLD + SOLVED-CLAIM
    VERIFIED. The `research solved` counterexample (exponent 0.74 fails at
    n=19): numeric bound 9.8364 => k in 0..9, and 19k+1 composite for ALL
    k = 0..9 (k=0 gives 1, non-prime) — Lean's interval_cases proof logic
    sound. exists_k clean to n = 5000; stronger k < 1+n^(3/4) clean to
    n = 20000. Competing Big-O conjectures noted as intentional pair.
    Report a034693.md; scripts/a034693_leastk.py.
23. [2026-08-26] Sun prize-conjecture family — AUDITED -> HOLD_BOUNDED x6
    (witness searches): A232174 complete for n <= 800; A280831 for n <= 800
    (witnesses reproduce Lean's own a_7=(1,1,1,2)->41^2 and a_95->216^2);
    A281976 for n <= 300; A287616 for n <= 3000; A303656 for n <= 5000;
    A308734 for n <= 8000. No counterexamples. Reports sun_232174.md etc.;
    scripts/sun_batch1.py, sun_batch2.py (+ a280831 log).
24. [2026-08-26] A103662 — AUDITED -> HOLD_BOUNDED. Head matches b-file; n=40:
    no zeroless base b <= 20000 (Lean variant conjecture intact); zeroless
    bases exist for n <= 20 (bracket list). Report a103662.md.
25. [2026-08-26] A037274 — AUDITED -> HOLD_BOUNDED. Home primes reached for ALL
    n in [2,48]; n=49 unresolved (consistent with famous open case);
    25 -> 55 -> 511 -> 773 verified. Report a037274.md.
26. [2026-08-26] A000945 — AUDITED -> HOLD. Euclid-Mullin first 12 terms
    reproduced by exact factorization (matches published incl. 38709183810571);
    Lean a_1..a_7 tests pass. Report a000945.md.
27. [2026-08-26] A239957 — AUDITED -> HOLD (readings pinned). Lean's exact-form
    reading (g = k^2+1 < p literally) vs residue reading: BOTH witnessed for
    all 430 primes < 3000 — readings do not diverge in range; declaration
    faithful either way; Sun prize status unchanged. Report a239957.md.
28. [2026-08-26] A105020 — AUDITED -> HOLD_BOUNDED. Lean reading requires the
    semiprime interior for EVERY occurrence-pair (a(i)=2n+1, a(i+n+1)=2n+3):
    773 applicable pairs within first 300000 terms, zero violations. Note:
    Hiebl's %C example indices (a(7)=7, a(11)=9) are stale under current
    published ordering (a(6)=7, a(10)=10th-term 9) — value-content correct.
    Report a105020.md; scripts/a105020_hiebl.py.
29. [2026-08-26] A105210 — AUDITED -> HOLD_BOUNDED. Five Cormier-Selfridge
    starts pairwise disjoint below 2,000,000 (all five sequences generated past
    2e6; heads match Lean tests). Report a105210.md.
30. [2026-08-26] A113250 / A113252 / A113255 — AUDITED -> HOLD_BOUNDED x3 BUT
    SKIP_CLAIMS (contamination: KitaKen1 repo oeis-a113249-family-square-terms-
    lean, pushed 2026-08-15). Odd-index terms perfect squares to index 200 for
    all three recurrences. Report a113250_family.md.
31. [2026-08-26] A105801 — SKIP_CONTAMINATION (KitaKen1 oeis-a105801-lean,
    pushed 2026-08-15). Not audited for claims.
