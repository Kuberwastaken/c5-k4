# SUMMARY — oeis3 lane (OEIS ROUND 3), 2026-08-26

**Lane:** OEIS only. Pinned upstream commit `2411d22e`. Inventory:
`open_targets_oeis_erdos_20260815.json` (OEIS corpus, previously_touched=false),
minus round-2 audited set (21) and round-2 contamination list.

**Headline: 34 targets audited to gate discipline (target was >=15), 0 new
crossings filed, 2 novel declaration-defect findings (A113271, A102847), both
repair opportunities from round 2 developed to completion or verdict, plus one
new repair candidate discovered en route (A108301). One apparent crossing
(A100434) killed by the novelty gate — already reported upstream post-pin.**

| Target | Class | Result | Gates |
|---|---|---|---|
| A113271 | DEFECT (docstring) + HOLD_BOUNDED | %C/docstring claim "a(5)=543 prime" false: a(5)=135457=7·37·523; no prime n=5..11 (sInf≥12) | a,b,c,d |
| A102847 | DEFECT (docstring) + HOLD_BOUNDED | "a(6) has 4 prime factors" false (Ω=6); claimed a(7) factorization is actually a(8)'s (off-by-one); composite n=5..19 re-verified | a,b,c,d |
| A100434 | DUPLICATE_PRIOR_ART (confirmed crossing) | all three sorried identities false at every even n as formalized (n=0: c+d=3≠b=−3); conj3 contradicts file's own a_even; true form: c+d=e+f=g+a ∀n — upstream #4560/#5025 closed it 2026-08-24 (post-pin) | a,b,c,d(killed) |
| A107247 | REPAIR CANDIDATE (complete) | all 9 textbook-sorry conjuncts verified via third path; witness table + Mathlib IsSemiprime=IsAlmostPrime 2 proof plan | a,b,c,d |
| A108301 | REPAIR CANDIDATE (complete, new find) | six Fermat digit sums prime (3,5,59,89,167,2741), two paths; decide-closable; none further n≤25 | a,b,c,d |
| A063880 | PARTIAL REPAIR + WRONG-TAG finding | closure lemma provable in one line (σ(nq)=σ(n)(q+1)=usigma shift); exists_primitive_of_a NOT derivable from own defs (kernel property), 281 terms ≤1e5 verify shape; research-solved tag overstates | a,b,c,d |
| A357513 | HOLD + status-sync note | supercongruence exact for primes 3..59, exception p=7 confirmed (residue 1715); AlphaProof commit 9c7f21e7 real → sorry at pin is porting artifact | a,b,c,d |
| A114362 | HOLD_BOUNDED + prior art | numerators match b-file; conj2 residual/(11⁻ⁿ) ∈ [0.78,0.94] n≤30; conj2 PROVEN upstream #5028 post-pin → duplicate | a,b,c,d(killed) |
| A109905 | HOLD_BOUNDED | zeros exactly {1,6,30,54} through n<19000 | a,b,c,d |
| A113258 | HOLD_BOUNDED | no perfect power after 125 through n=11 (a(11): 1.09M digits) | a,b,c,d |
| A113609 | HOLD_BOUNDED | only pair (25,27) below 2·10⁶; none q≥10⁶ | a,b,c,d |
| A113010 | HOLD_BOUNDED | fixed points exactly {1,32} to 2·10⁶ | a,b,c,d |
| A114216 | HOLD_BOUNDED | last a(n)=1 at n=33900 confirmed to 60000 | a,b,c,d |
| A100800 | HOLD_BOUNDED | multiple-hit for all n≤5000 (strictly increasing iterates noted) | a,b,c,d |
| A100475 | HOLD | head matches b-file; all 120 starts escape table pre-loop (question not finitely decidable) | a,b,c,d |
| A109671 | HOLD | b-file head exact incl. prev=mid edge semantics | a,b,c,d |
| A110566 | HOLD | a(n)=gcd(S_n,L_n) simplification proved+used; head matches; coverage bounded | a,b,c,d |
| A109845 | HOLD_BOUNDED | lcm-recurrence ≡ polynomial recurrence n≤16 (provable); primes a(1..5); composite to n=15 | a,b,c,d |
| A104320 | HOLD_BOUNDED | ternary-zero claim intact n≤4000 (disproof hunt negative) | a,b,c,d |
| A001157 (inv 1157) | HOLD_BOUNDED | Sun fractional-parts clean k=2..7, n≤60000 | a,b,c,d |
| A115366 | HOLD_BOUNDED | ratios 1.7801 / 1.7769 at n=5,6 inside [1.77,1.78] | a,b,c,d |
| A034693 (inv 34693) | HOLD + solved-claim verified | n=19 counterexample exact (k≤9 all composite, bound 9.8364); exists_k clean ≤5000; stronger ≤20000 | a,b,c,d |
| A232174 | HOLD_BOUNDED | witnesses for all n≤800 | a,b,c,d |
| A280831 | HOLD_BOUNDED | witnesses for all n≤800 (reproduces file's own 41²,216² witnesses) | a,b,c,d |
| A281976 | HOLD_BOUNDED | witnesses for all n≤300 | a,b,c,d |
| A287616 | HOLD_BOUNDED | witnesses for all n≤3000 (upstream #4927 tracks known-solution status) | a,b,c,d |
| A303656 | HOLD_BOUNDED | witnesses for all n≤5000 | a,b,c,d |
| A308734 | HOLD_BOUNDED | witnesses for all n≤8000 | a,b,c,d |
| A103662 | HOLD_BOUNDED | head ✓; no zeroless base ≤20000 for n=40 | a,b,c,d |
| A037274 | HOLD_BOUNDED | home primes reached ∀ n∈[2,48]; 49 open (consistent) | a,b,c,d |
| A000945 | HOLD | first 12 EM terms reproduced by exact factorization | a,b,c,d |
| A239957 | HOLD | exact-form vs residue readings agree on all 430 primes <3000 | a,b,c,d |
| A105020 | HOLD_BOUNDED | Lean strong reading: 773 applicable pairs in first 300k terms, zero violations; stale %C example indices noted | a,b,c,d |
| A105210 | HOLD_BOUNDED | five starts pairwise disjoint below 2·10⁶ | a,b,c,d |
| A113250/52/55 | HOLD_BOUNDED ×3, SKIP_CLAIMS | squares verified ≤ index 200; KitaKen1 A113249-family repo covers ⇒ excluded from claims | a,b,c,d(✗) |
| A105801 | SKIP_CONTAMINATION | KitaKen1 oeis-a105801-lean | — |

## Status-sync quick pass (all audited entries)

- **A063880**: `exists_primitive_of_a` tagged research-solved; content not
  derivable from own defs; OEIS evidence computational ("so far", "below
  10^18") → wrong-tag candidate recorded.
- **A357513**: research-solved tag JUSTIFIED (AlphaProof commit verified);
  sorry body is AutoOeis porting artifact.
- **A100434 / A114362**: both already resolved/discussed upstream POST-pin —
  at-pin defects remain live at 2411d22e.
- **OEIS-side staleness (candidates for OEIS edit suggestions)**: A113271 %C
  ("a(5)=543"), A102847 %C ("a(6) has 4 factors"; a(7)/a(8) mixup), A105020 %C
  example indices.
- All other pages' current status consistent with their declarations' tags.

## Method notes

- The verification layer earned its keep again: v1 scripts produced two false
  alarms that cross-checking caught BEFORE any claim (A280831 dropped z-factor;
  Sun batch v1 strict inequalities), plus one genuine path-agreement subtlety
  (A357513 p=7 residue differs by unit factor between paths — resolved).
- Python SSL failures to oeis.org worked around with curl (UA per protocol);
  b-file URL pattern is bAxxxxxx.txt lowercase-b + padded number.
- All scripts + run logs committed under scripts/ and lane root; every bracket
  reproducible under the 60-second cap.

## Lane outcome

0 new crossings filed · 2 novel declaration-defects (unclaimed, documented) ·
3 repair candidates developed (A107247, A108301, A063880-item1) · 1 wrong-tag
finding (A063880-item2) · 2 duplicate/prior-art kills (A100434, A114362-conj2)
· 26 bounded brackets extending verification ranges · 34 full audits +
3 contamination-limited audits + 1 skip.
