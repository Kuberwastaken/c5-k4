# Status-sync recheck — seven CONTESTED findings resolved against live sources

**Date:** 2026-08-26
**Re-checks:** results/expansion/live-search-2026-08-15/CONFIRMED_LEDGER.md, §"Status-sync findings"
(the seven rows under the ⚠ CONTESTED banner).
**Why contested then:** erdosproblems.com returned Cloudflare 403 to every lane on
2026-08-15 and the offline mirror (`teorth/erdosproblems@data/problems.yaml`) still
recorded all seven as open.
**Method today:** live HTTPS fetches of https://www.erdosproblems.com/&lt;id&gt; (curl,
UA `OpenAI File Downloader, XaiImageApiFetch/1.0`, HTTP 200 for all six — the 403
did not recur), OEIS `fmt=text` export, GitHub API for
`google-deepmind/formal-conjectures` (default branch **main**, last push
2026-08-25T21:08Z) at both current HEAD and ledger pin `2411d22e`, plus targeted
websearch corroboration. Local mirror at
`upstream/formal-conjectures/FormalConjectures/ErdosProblems/` does not exist on
this checkout (only `FormalConjectures/WrittenOnTheWallII/` is populated), so all
Lean citations below are raw/API fetches from the canonical repo.

**Pin-drift check (defects still present TODAY):** files 36, 44, 60, 1084, 1106
are **byte-identical** between pin `2411d22e` and current main. File 1054 differs
only inside the unrelated `textbook` proofs `f_undefined_at_2/3`
(`by_contra!`/`lia` refactors from chore PRs #5074/#3691/#4025/#5109, Aug 23–24);
`.parts.i` itself untouched. No post-2026-08-15 commit repairs any of the seven
defects.

---

## 1. Erdős 1084 `triangular_optimal_d2` — CONFIRMED_LIVE

**Claim:** Harborth (1974) proved the declared `=` form, so the docstring's `<`
plus the `research open` tag are wrong.

**Live evidence**
- https://www.erdosproblems.com/1084 (HTTP 200 2026-08-26; page states "last edited
  08 February 2026"): remarks read — *"he speculated that the triangular lattice is
  exactly the best possible, and in particular f₂(3n²+3n+1)=9n²+3n. Harborth
  [Ha74b] proved this, and more generally f₂(n)=⌊3n−√(12n−3)⌋ for all n≥2."*
- Nuance recorded honestly: the page's overall status chip still says OPEN —
  correct, because the *general* problem "estimate f_d(n)" (f₃ etc.) remains open.
  But the *declared instance* is exactly what the live page records Harborth as
  having proved, so the variant's tag is wrong regardless of the chip.

**Upstream today:** `FormalConjectures/ErdosProblems/1084.lean` @ main (blob
`159a640c`), lines 61–68:
```
/-- Erdős conjectured … in particular that $f_2(3n^2 + 3n + 1) < 9n^2 + 3n$. … -/
@[category research open, AMS 52]
theorem erdos_1084.variants.triangular_optimal_d2 :
    f 2 (3 * n ^ 2 + 3 * n + 1) = 9 * n ^ 2 + 3 * n := by sorry
```
Docstring writes `<` where both the code and the live source say `=`; tag is
`research open`. Commit history for this path: nothing substantive after #4433
(2026-07-16 refactor) — the defect predates and survives 2026-08-15.

## 2. Erdős 1106 `.parts.i` — CONFIRMED_LIVE

**Claim:** settled (F(n) → ∞ follows), yet tagged open.

**Live evidence**
- https://www.erdosproblems.com/1106 (HTTP 200 2026-08-26; edited 16 November 2025):
  *"Schinzel noted in the Oberwolfach problem book that F(n)→∞ follows from the
  asymptotic formula for p(n) and a result of Tijdeman [Ti73]. … Schinzel and
  Wirsing [ScWi87] have proved F(n) ≫ log n."* F(n) ≫ log n ⇒ F(n) → ∞, i.e. part
  (i) is settled by literature the site itself cites. Part (ii) (F(n) > n
  eventually) stays open, which is consistent with the page's OPEN chip.

**Upstream today:** `1106.lean` @ main (blob `dd77edbc`), lines 32–39:
`@[category research open]` on `erdos_1106.parts.i : answer(sorry) ↔ Tendsto …
atTop atTop`. Byte-identical to pin; last non-chore touch 2026-03-01 (#2416).

## 3. Erdős 1054 `.parts.i` — CONFIRMED_LIVE

**Claim:** the site records Tao's disproof of the strong claim.

**Live evidence**
- https://www.erdosproblems.com/1054 (HTTP 200 2026-08-26; edited 06 December 2025):
  *"The strong claim that f(n)=o(n) was disproved by Tao in the comments to [468],
  in which he proves that the upper density of {n : f(n) ≤ δn} is ≪ δ²."* The
  page's comment-activity box reads "A claimed solution has been posted".
  `.parts.i` in the Lean file is precisely the strong claim.

**Upstream today:** `1054.lean` @ main (blob `1a4b4a78`), lines 37–41:
`@[category research open]` on `erdos_1054.parts.i : answer(sorry) ↔ f =o[atTop]
(id : ℕ → ℝ)`. Still open-tagged although its RHS is now recorded as disproved.
Pin→master diff touches only `f_undefined_at_*` proof style (chores of Aug 23–24).

## 4. Erdős 36 `.variants.upper` — CONFIRMED_LIVE

**Claim:** site now records c < 0.380876 while the declaration asks c <
0.380926853433087.

**Live evidence**
- https://www.erdosproblems.com/36 (HTTP 200 2026-08-26; edited 23 January 2026):
  *"The current records are 0.379005 < c < 0.380876, the lower bound due to White
  [Wh22] and the upper bound due to the TTT-Discover LLM [YKLBMWKCZGS26],
  improving slightly on earlier bounds due to AlphaEvolve [GGTW25] and Haugland
  [Ha16]."*
- Independent corroboration: Wikipedia "Minimum overlap problem" table (Haugland
  2016 → 0.380926…, AlphaEvolve 2025 → 0.380924…, TTT-Discover 2026 → 0.380876…,
  SimpleTES 2026 → 0.380868…); TTT-Discover paper arXiv:2601.16175 (§4.1.1, Fig. 2:
  600-piece step function certifying 0.380876); the site's own forum thread
  /forum/discuss/36 (dated 2026-01-23) noting the page was updated for it.
- The stale-mirror objection is dead: the live page's edit date (2026-01-23 era
  update) precedes and explains why an offline snapshot could lag.

**Upstream today:** `36.lean` @ main (blob `1b33c95a`), lines 353–359:
```
/-- Find a better upper bound! -/
@[category research open, AMS 5 11]
theorem erdos_36.variants.upper :
    ∃ (c : ℝ), c < 0.380926853433087 ∧ atTop.limsup MinOverlapQuotient ≤ c ∧
      c = answer(sorry) := by sorry
```
The threshold is exactly Haugland 2016; the file carries no variant for
AlphaEvolve's 0.380924 or TTT-Discover's 0.380876. Byte-identical to pin (last
touches: #4751 Aug 6 proved M₂–M₅ tests; #4948 Aug 14 balanced delimiters).

## 5. Erdős 44 `.variants.empty_start` — CONFIRMED_LIVE

**Claim:** identical to Singer (1938).

**Live evidence**
- https://www.erdosproblems.com/44 (HTTP 200 2026-08-26; edited 09 January 2026):
  statement matches the Lean docstring (extend Sidon A ⊆ {1..N} to size ≥
  (1−ε)M^{1/2} inside {1..M}); page OPEN.
- https://www.erdosproblems.com/30 (HTTP 200 2026-08-26): *"Singer [Si38] was the
  first to show that h(N) ≥ (1−o(1))N^{1/2} for all N"* — where h(N) is the
  maximum size of a Sidon subset of {1,…,N}. Setting A := ∅ in EP 44 collapses it
  to exactly "∃ Sidon A ⊆ {1..M}, (1−ε)√M ≤ |A| eventually for every ε > 0",
  which is precisely h(M) ≥ (1−ε)√M — Singer's theorem as the corpus itself
  records it, live, on the sibling page. (Precision note: "identical to Singer"
  is exact given the page's ∀N phrasing; no extra interval argument is needed.)

**Upstream today:** `44.lean` @ main (blob `5d9fe5eb`), lines 91–97:
`@[category research open]` on `erdos_44.variants.empty_start : answer(sorry) ↔
∀ᵉ (ε > 0), ∀ᶠ M in atTop, ∃ᵉ A ⊆ Icc 1 M, IsSidon A ∧ (1 − ε) * sqrt M ≤ A.card`.
Byte-identical to pin; last substantive touch #4880 (Aug 12, textbook statements
elsewhere in the file).

## 6. Erdős 60 `.variants.two_copies` — CONFIRMED_LIVE

**Claim:** mis-tagged `research solved`; site records no proof.

**Live evidence**
- https://www.erdosproblems.com/60 (HTTP 200 2026-08-26; edited 18 November 2025):
  status OPEN; *"Conjectured by Erdős and Simonovits, who could not even prove
  that at least 2 copies of C₄ are guaranteed."* Comment activity: none;
  "0 claimed proofs for this problem". Only partial result recorded is He–Ma–Yang
  for n = q²+q+1, q even.

**Upstream today:** `60.lean` @ main (blob `5fd36d9a`), lines 60–69:
```
/-- Erdős and Simonovits conjectured that at least 2 copies of $C_4$ are guaranteed. -/
@[category research solved, AMS 5]
theorem erdos_60.variants.two_copies : … 2 ≤ { H' : G.Subgraph | … }.ncard := by sorry
```
Tagged **solved** for a statement the live site records as a conjecture with zero
claimed proofs — wrong in the expensive direction. File introduced by #4311
(committed 2026-08-03), unchanged since; existed at audit time, survives today.

## 7. OEIS A357513 — CONFIRMED_LIVE

**Claim:** proved by Kutal, Jul 2026, with a Lean formalization; not tracked
upstream.

**Live evidence**
- OEIS https://oeis.org/search?q=id:A357513&fmt=text (fetched 2026-08-26; entry
  version **#28, Jul 22 2026**):
  - `%C`: *"This conjecture is now proved; see Links. The exceptional primes are
    exactly the primes p for which p − 1 divides 2m + 4 and p does not divide
    2m + 7. … Every exceptional prime satisfies p ≤ 2m + 5. — Ondrej Kutal, Jul 18
    2026"* (generalized m-parameter conjecture, proved).
  - `%F`: *"The above conjecture is true. See Links for proof. — Moritz
    Firsching, Jan 29 2026"*.
  - `%H` links: (a) Firsching's AlphaProof formalization into
    `google-deepmind/formal-conjectures@879bf008…/OEIS/357513.lean` (Jan 2026);
    (b) *"Ondrej Kutal, A proof of the generalized conjecture, with Lean
    formalization, github.com/TheSil/A357513_conjecture, Jul 2026."*
- https://api.github.com/repos/TheSil/A357513_conjecture: created **2026-07-18**,
  pushed 2026-07-18; contains `Proof.lean` (51,901 B), `proof.tex`, `proof.pdf`,
  `lakefile.lean` — a real Lean formalization, not a stub.

**Upstream today:** `FormalConjectures/OEIS/357513.lean` @ main (blob `2fe8eb90`)
exists (added Apr 1 by #1924; last touched Aug 14 by delimiter-balance #4948):
- `a357513_supercongruence` (m=1 instance) is already `@[category research
  solved]` citing AlphaProof commit `9c7f21e7`;
- **`general_supercongruence` (m-parameter) is still `@[category research open]`
  with `sorry`** (lines 91–98) — exactly the statement OEIS now records as proved
  by Kutal;
- GitHub issue/PR search `repo:google-deepmind/formal-conjectures 357513` returns
  **one hit**, closed infra PR #4841 (linter enablement) — **no issue or PR tracks
  Kutal's proof**.

**Verdict note:** the original wording "not tracked upstream" needs one
refinement — the *file* was already upstream before the finding (so the finding
was never "file missing"), and its m=1 theorem was already marked solved via
AlphaProof. What remains true and untracked is the Kutal development: the
general supercongruence's `research open` tag is stale against OEIS's Jul 18 2026
"now proved", with zero upstream reference to the proof or formalization.

---

## Roll-up

| # | Target | 2026-08-15 | 2026-08-26 verdict | Key live fact |
|---|---|---|---|---|
| 1 | Erdős 1084 `triangular_optimal_d2` | CONTESTED | **CONFIRMED_LIVE** | Site records Harborth [Ha74b] proved the declared equality; Lean docstring `<` + `research open` unchanged |
| 2 | Erdős 1106 `.parts.i` | CONTESTED | **CONFIRMED_LIVE** | Site: Schinzel–Wirsing [ScWi87] prove F(n) ≫ log n ⇒ part (i) settled; Lean still open |
| 3 | Erdős 1054 `.parts.i` | CONTESTED | **CONFIRMED_LIVE** | Site: "strong claim f(n)=o(n) was disproved by Tao"; Lean still open |
| 4 | Erdős 36 `.variants.upper` | CONTESTED | **CONFIRMED_LIVE** | Site record c < 0.380876 (TTT-Discover, Jan 2026); Lean asks c < 0.380926853433087 |
| 5 | Erdős 44 `.variants.empty_start` | CONTESTED | **CONFIRMED_LIVE** | Site EP30: Singer [Si38] h(N) ≥ (1−o(1))√N for all N = the empty-start variant |
| 6 | Erdős 60 `.variants.two_copies` | CONTESTED | **CONFIRMED_LIVE** | Site: conjecture, "could not even prove at least 2 copies", 0 claimed proofs; Lean tagged solved |
| 7 | OEIS A357513 | CONTESTED | **CONFIRMED_LIVE** (wording refined) | OEIS #28 (Jul 22 2026): "now proved", Kutal Jul 18 2026 + Lean repo TheSil/A357513_conjecture; upstream `general_supercongruence` still open/sorry, 0 tracking issues |

No item resolved REFUTED, CONFIRMED_BUT_FIXED_UPSTREAM, or STILL_CONTESTED.
The offline-mirror objection is resolved in every case: the live site (and OEIS)
today carries the disproof/proof/new-record content the audit claimed, with page
edit dates (Nov 2025 – Feb 2026, entry Jul 2026) showing the mirror was the stale
side. All seven defects remain present on `google-deepmind/formal-conjectures@main`
as of 2026-08-26 (pin-drift check above).
