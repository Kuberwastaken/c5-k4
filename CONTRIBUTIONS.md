# Contributions ledger

Every genuine contribution this campaign has produced, with its current status
and its honest class. Maintained as the single source of truth; update it in the
same commit as the contribution.

**Classes are not interchangeable** (METHOD_V1_6 §A6). A formalization defect is
a statement about what a Lean declaration asserts. A crossing is a finite
witness that makes a declaration false. A mathematical counterexample refutes
the underlying question. Only the last is a claim about mathematics, and this
campaign has produced those only against machine-generated conjecture lists.

Last updated: 2026-08-15.

## A. Merged upstream (google-deepmind/formal-conjectures)

| Date | PR | Contribution | Class |
|---|---|---|---|
| 2026-08-12 | [#4592](https://github.com/google-deepmind/formal-conjectures/pull/4592) | Disprove WOWII 63 and 85 via C₅[K₄] | mathematical counterexample (machine-generated conjecture) |
| 2026-08-09 | [#4605](https://github.com/google-deepmind/formal-conjectures/pull/4605) | Green 31: formalise binary Sidon sums | formalization repair |

## B. Open upstream PRs

Sixteen open as of 2026-08-15; none reviewed yet.

| PR | Contribution | Class | CI |
|---|---|---|---|
| [#4907](https://github.com/google-deepmind/formal-conjectures/pull/4907) | WOWII 181 disproof (via T(n)) | counterexample | pass |
| [#4909](https://github.com/google-deepmind/formal-conjectures/pull/4909) | WOWII 172 disproof | counterexample | pass |
| [#4911](https://github.com/google-deepmind/formal-conjectures/pull/4911) | WOWII 176 disproof | counterexample | pass |
| [#4913](https://github.com/google-deepmind/formal-conjectures/pull/4913) | WOWII 430a disproof | counterexample | pass |
| [#4916](https://github.com/google-deepmind/formal-conjectures/pull/4916) | WOWII 438b proof | theorem | pass |
| [#4932](https://github.com/google-deepmind/formal-conjectures/pull/4932) | WOWII 309 disproof | counterexample | pass |
| [#4983](https://github.com/google-deepmind/formal-conjectures/pull/4983) | OEIS A110854 disproof (d = 3) | crossing | pass |
| [#4985](https://github.com/google-deepmind/formal-conjectures/pull/4985) | OEIS A108864 encoding repair (A109883) | formalization repair | pass |
| [#4986](https://github.com/google-deepmind/formal-conjectures/pull/4986) | Erdős 1093 `smoothNumbers (k+1)` | formalization repair | building |
| [#4987](https://github.com/google-deepmind/formal-conjectures/pull/4987) | OEIS A237271 `IsCarmichael` hypothesis | formalization repair | building |
| [#4988](https://github.com/google-deepmind/formal-conjectures/pull/4988) | Erdős 1055 `IsOfClass` exactness | formalization repair | building |
| [#4989](https://github.com/google-deepmind/formal-conjectures/pull/4989) | Erdős 33 lower-bound form | formalization repair | pass |
| [#4990](https://github.com/google-deepmind/formal-conjectures/pull/4990) | Erdős 15 conditional convergence | formalization repair | pass |
| [#4991](https://github.com/google-deepmind/formal-conjectures/pull/4991) | Erdős 477 two-sided index set | formalization repair | pass |
| [#4992](https://github.com/google-deepmind/formal-conjectures/pull/4992) | Erdős 952 `answer(sorry) ↔` | formalization repair | pass |
| [#4993](https://github.com/google-deepmind/formal-conjectures/pull/4993) | Erdős 40 decision form | formalization repair | building |

## C. Upstream issues filed

[#4974](https://github.com/google-deepmind/formal-conjectures/issues/4974) A237271 ·
[#4975](https://github.com/google-deepmind/formal-conjectures/issues/4975) Erdős 1093 ·
[#4976](https://github.com/google-deepmind/formal-conjectures/issues/4976) Erdős 1055 ·
[#4977](https://github.com/google-deepmind/formal-conjectures/issues/4977) Erdős 40 ·
[#4978](https://github.com/google-deepmind/formal-conjectures/issues/4978) Erdős 33 ·
[#4979](https://github.com/google-deepmind/formal-conjectures/issues/4979) Erdős 15 ·
[#4980](https://github.com/google-deepmind/formal-conjectures/issues/4980) Erdős 477 ·
[#4981](https://github.com/google-deepmind/formal-conjectures/issues/4981) Erdős 952 ·
[#4982](https://github.com/google-deepmind/formal-conjectures/issues/4982) A110854 ·
[#4984](https://github.com/google-deepmind/formal-conjectures/issues/4984) A108864 ·
plus a comment on [#4922](https://github.com/google-deepmind/formal-conjectures/issues/4922) (Erdős 142).

## D. Releases (github.com/Kuberwastaken/c5-k4/releases)

| Tag | Contribution |
|---|---|
| `wowii-172-v1`, `wowii-176-v1`, `wowii-181-v1`, `wowii-430a-v1` | WOWII counterexamples with formal certificates |
| `graffiti3-conjecture2-double-star-v1` | Graffiti³ Conjecture 2 counterexample family `DS(k,k)`, `k ≥ 12` |
| `graffiti3-conjecture13-pseudoprime-v1` | Graffiti³ Conjecture 13 counterexample `n = 81,722,145` |
| `oeis-109074-formalization-v1`, `oeis-111291-formalization-v1`, `oeis-113019-fixed-points-v1` | OEIS formalization counterexamples |
| `bateman-horn-count-endpoint-v1` | Bateman–Horn counting helper endpoint |
| `method-v1.4-terminal` | method snapshot (not a result) |

## E. Corrections issued (we published, then refuted ourselves)

Kept deliberately visible; this is the campaign's error record, and its rate is
itself a finding.

| Date | What we claimed | What is actually true |
|---|---|---|
| 2026-08-15 | Issue #4978: `A = ℕ` trivially witnesses Erdős 33 `one_mem_lowerBounds` | The `limsup` elaborates in `ℝ`, not `EReal`; for `A = ℕ` it is the junk `0` from `Real.sInf_empty`, so `1 < 0` fails. Correction comment posted on the issue; defect reclassified as a name/docstring-fidelity + junk-value issue |
| 2026-08-15 | Issue #4977's own suggested repair (`IsGreatest {G \| Erdos40ForSet G}`) | That shape is closable in two `fun`s, because `Erdos40ForSet` is pointwise hence downward- and union-closed. PR #4993 implements a decision form instead |
| 2026-08-15 | Erdős 1084 "finitely false as stated" | The `<` is only in the docstring; the declaration asserts `=`, which is Harborth's theorem |
| 2026-08-15 | Erdős 931 "closed interval trivialises the conclusion" | 280 premise-satisfying tuples show zero disagreement between readings; the quoted source sentence is not on the live page |
| 2026-08-15 | Bondy C₄-factor Hamiltonicity as a project theorem | Already published: Boyd & Sebő, IPCO 2017 / Math. Prog. 186 (2021), Lemma 2, same proof |
| 2026-08-15 | Ledger: seven status-sync findings | Live source unreachable; the offline mirror records all seven as still open. Marked CONTESTED, held back from upstream |

## F. Not contributions (recorded to prevent recounting)

- **401b, 412f, 448b** — the published WOWII wording is corrupt (violated by stars, K₃, C₄ inside Graffiti.pc's own database). Killing a typo is not a result.
- **C₃/C₃ sharpness** for the C₄-factor theorem — assembles Harary–Nash-Williams with well-known facts; routine.
- **Graph Brain upper-081, WoW I #191 and #889** — outside the programme's declared scope (`OVERARCHING_PLAN.md`), so they do not count toward the methodological record even though they are verified.
