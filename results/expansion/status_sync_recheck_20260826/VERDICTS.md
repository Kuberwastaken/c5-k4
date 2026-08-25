# VERDICTS — status-sync recheck, 2026-08-26

Companion to `RECHECK.md` (full citations there). Resolves the seven CONTESTED
rows of `results/expansion/live-search-2026-08-15/CONFIRMED_LEDGER.md`.

| # | Target | Verdict | Defect still on `formal-conjectures@main` (2026-08-26)? | Primary live source (fetched 2026-08-26) |
|---|---|---|---|---|
| 1 | Erdős 1084 `triangular_optimal_d2` | **CONFIRMED_LIVE** | Yes — docstring `<`, tag `research open`; byte-identical to pin | erdosproblems.com/1084 (ed. 08 Feb 2026): "Harborth [Ha74b] proved this" |
| 2 | Erdős 1106 `.parts.i` | **CONFIRMED_LIVE** | Yes — open-tagged; identical to pin | erdosproblems.com/1106 (ed. 16 Nov 2025): Schinzel–Wirsing F(n) ≫ log n ⇒ F(n)→∞ settled |
| 3 | Erdős 1054 `.parts.i` | **CONFIRMED_LIVE** | Yes — open-tagged; only unrelated chore diffs since pin | erdosproblems.com/1054 (ed. 06 Dec 2025): f(n)=o(n) "disproved by Tao" |
| 4 | Erdős 36 `.variants.upper` | **CONFIRMED_LIVE** | Yes — threshold still 0.380926853433087; identical to pin | erdosproblems.com/36 (ed. 23 Jan 2026): record c < 0.380876 (TTT-Discover); corr. arXiv:2601.16175, Wikipedia |
| 5 | Erdős 44 `.variants.empty_start` | **CONFIRMED_LIVE** | Yes — open-tagged; identical to pin | erdosproblems.com/30 (live): Singer [Si38] h(N) ≥ (1−o(1))√N for all N = empty-start case |
| 6 | Erdős 60 `.variants.two_copies` | **CONFIRMED_LIVE** | Yes — tag `research solved` with `sorry`; unchanged since #4311 (Aug 3) | erdosproblems.com/60 (ed. 18 Nov 2025): conjecture, 0 claimed proofs |
| 7 | OEIS A357513 | **CONFIRMED_LIVE** (wording refined) | Yes — `general_supercongruence` open/sorry; m=1 already solved via AlphaProof; no issue/PR cites Kutal | oeis.org A357513 entry #28 (22 Jul 2026): "now proved", Kutal 18 Jul 2026 + Lean repo TheSil/A357513_conjecture |

Score: 7 × CONFIRMED_LIVE · 0 × CONFIRMED_BUT_FIXED_UPSTREAM · 0 × REFUTED · 0 × STILL_CONTESTED.

Resolution of the original objection: the live site and OEIS were reachable today
(HTTP 200 throughout; no Cloudflare block), and their edit/entry dates show the
offline mirror was the stale side in all seven cases.
