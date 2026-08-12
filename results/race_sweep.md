# WOWII claim map — google-deepmind/formal-conjectures — swept 2026-08-12

Main HEAD at sweep time: `37f41a80` (2026-08-12). Directory: `FormalConjectures/WrittenOnTheWallII/` — 46 conjecture files (45 `GraphConjectureNN.lean` + `160.lean`), plus `README.md`, `Test.lean`.

Status read from `@[category research open|solved]` + `answer(...)` in each file on main (raw fetch 2026-08-12).
"solved-true" = `research solved`, statement affirmed (no `answer(False)`); "solved-false" = `research solved` + `answer(False)`.
Note: nearly all statements carry a placeholder `sorry` in-repo (repo convention); `fp` = has `formal_proof` attribute linking an external Lean proof.

## Table: conjecture -> status

| WOWII # | On main | Status | Pending PRs / claims |
|---|---|---|---|
| 1 | yes | solved-true (fp) | — |
| 2 | yes | solved-true (3x fp) | — |
| 3 | yes | solved-true | — |
| 4 | yes | solved-true | — |
| 5 | yes | solved-true | — |
| 6 | yes | solved-true | — |
| 7 | yes | solved-true | — |
| 13 | yes | solved-true | — |
| 16 | yes | solved-true | — |
| 17 | yes | solved-true | PR #4161 mo271 (open, adds formal_proof link) |
| 18 | yes | solved-true (fixed by #4602 08-03) | — |
| 19 | yes | **OPEN** | PR #4559 akakabrian (open, mark solved); PR #1511 henrykmichalewski (open since Jan, K3 test) |
| 20 | yes | solved-true | — |
| 23 | yes | solved-false (answer(False)) | — |
| 24 | no | not in repo | import-as-open in batch PR #3796 (open, conflicted) |
| 31 | yes | solved-true | PR #4567 anagnorisis2peripeteia (open, fix path def/source); PR #4658 KitaKen1 (open, docs proof link); issue #4566 |
| 32 | yes | solved-false | — |
| 33 | yes | solved-false | — |
| 34 | yes | research solved but `answer(sorry)` (direction unresolved in-repo) | issue #3808 (open, statement dispute B vs M) |
| 36 | yes | solved-false | PR #4572 anagnorisis2peripeteia (open, certify disproof in-repo); issue #4570 |
| 40 | yes | **OPEN** | issue #4702 cozuya (open, status note: partial reduction, verified to n=11; no PR) |
| 58 | yes | solved-false (fp) | PR #4634 hypnopump (open, smaller 31-vertex counterexample) |
| 59 | yes | **OPEN** | **competing disproofs**: PR #4574 QDKStorm (open, disprove); PR #4583 anagnorisis2peripeteia (open, certify disproof, 18-vertex witness); issues #4573, #4582 |
| 61 | yes | **OPEN** | — |
| 63 | **no** | not in repo | **PR #4592 Kuberwastaken (open, disprove via C5[K4], answer(False), fp links)** + issue #4590; also import-as-open in batch PR #3796 |
| 65 | yes | solved-false (merged #4514, 08-06) | — |
| 72 | no | not in repo | import-as-open in batch PR #3796 |
| 84 | no | not in repo | import-as-open in batch PR #3796 |
| 85 | **no** | not in repo | **PR #4592 Kuberwastaken (open, disprove, same C5[K4] witness)** + issue #4590; also import-as-open in batch PR #3796 |
| 91 | no | not in repo | import-as-open in batch PR #3796 |
| 96 | no | not in repo | import in batch PR #3796; also referenced in #3821 GraphDistOdd |
| 100 | yes | **OPEN** | PR #4504 anagnorisis2peripeteia (open, fix: graph length is not diameter); PR #4515 DomTheDeveloper (open, mark solved); issue #4502; PR #4513 closed-unmerged |
| 101 | yes | solved-true | — |
| 103 | yes | solved-false (merged #4482, 07-25) | — |
| 109 | yes | solved-false (merged #4495, 07-26) | — |
| 133 | yes | **OPEN** | — |
| 141 | yes | **OPEN** | PR #4454 AlperTheKing (open, prove 141+143) |
| 142 | yes | solved-true (fp; merged #4457, 08-11) | — |
| 143 | yes | solved-true (fp) | PR #4454 also re-proves 143 |
| 144 | yes | solved-true (fp; merged #4696, 08-04) | — |
| 145 | yes | **OPEN** | PR #4520 DomTheDeveloper (open, solve) |
| 146 | yes | **OPEN** | PR #4505 akakabrian (open, formalize+prove); PR #4540 Mapika (open, mark solved) — competing |
| 160 | yes (file `160.lean`) | **OPEN** (source-corrected by #4443, 07-26) | PR #4576 anagnorisis2peripeteia (open, mark solved); issues #4575 (anagnorisis proof proposal), #4569 (vulnix0x4 proposed proof) — competing |
| 194 | yes | solved-false (fp; merged #4542, 08-07) | — |
| 198a | yes | **OPEN** | PR #4597 lukekabbash (open, mark solved); issue #4596 |
| 200 | yes | **OPEN** | PR #4500 infinityscroll (open, **disprove**); issue #4499 |
| 209 | no | not in repo | PR #4508 infinityscroll (open, disprove); issue #4507; referenced in #3821 GraphFrequencyMaxL |
| 217 | yes | solved-true (fp; merged #4656, 08-04) | — |
| 284 | no | not in repo | PR #4557 SamPetkov (open, formalize as solved — disproved by Hoffman–Singleton); issue #4556 |
| 291 | yes | **OPEN** | PR #4510 anagnorisis2peripeteia (open, fix: remove extra order hypothesis); issue #4562 vulnix0x4 (open, **counterexample claim**, no PR yet); issue #4509 |
| 305 | no | **not in repo — zero PRs/issues mention it** | unclaimed |
| 309 | no | **not in repo — zero PRs/issues mention it** (only search hit is a "+309" diffstat in a #3820 comment) | unclaimed |
| 310 | no | **not in repo — zero PRs/issues mention it** | unclaimed |
| 314 | yes | **OPEN** | **competing solve claims**: PR #4455 glyaea (open, mark solved); PR #4496 DomTheDeveloper (open, mark solved) |
| 315 | yes | solved-true (fp) | — |
| 316 | yes | solved-true (fp; merged #4426, 08-07 — statement was corrected after 2026-05/06 P5-counterexample disproof claims #4107/#4133/#4134) | — |
| 322 | yes | solved-true (fp, in-repo proof, no sorry; merged #4430, 08-05) | — |
| 327 | yes | solved-false (fp) | — |
| 384b | no | **not in repo — zero PRs/issues mention it** ("384b" search: 0 results) | unclaimed |
| 189, 199 | no | not in repo | import-as-open in batch PR #3796 |

Fully proved in-repo (no sorry anywhere in file): 65, 103, 322. All other research statements carry the conventional placeholder `sorry`.

## Chronological WOWII PRs/issues since 2026-07-01 (by creation date)

| Date | # | Type | Author | Target | Direction | Outcome |
|---|---|---|---|---|---|---|
| 07-12 | 4423 | issue | changjonathanc | 160 | misformalization report | closed (fixed by #4443) |
| 07-13 | 4426 | PR | KitaKen1 | 316 | prove (mark solved, ext. proof) | **merged 08-07** |
| 07-14 | 4430 | PR | SamuelSchlesinger | 322 | prove | **merged 08-05** |
| 07-14 | 4431 | PR | SamuelSchlesinger | 316 | prove | closed unmerged |
| 07-16 | 4441 | PR | DomTheDeveloper | 65 | mark solved (true) | closed unmerged (65 later disproved) |
| 07-16 | 4442 | PR | DomTheDeveloper | 143 | mark solved | API says merged 07-21, but commit absent from current main history; 143's `research solved` flip appears on main inside #4563 (07-23) |
| 07-16 | 4443 | PR | DomTheDeveloper | 160 | fix C4-free characteristic | **merged 07-26** |
| 07-18 | 4454 | PR | AlperTheKing | 141, 143 | prove | open |
| 07-18 | 4455 | PR | glyaea | 314 | mark solved | open |
| 07-18 | 4457 | PR | AlperTheKing | 142 | mark solved | **merged 08-11** |
| 07-20 | 4481 | issue | CinnamonRolls1 | 103 | counterexample | closed |
| 07-20 | 4482 | PR | CinnamonRolls1 | 103 | disprove | **merged 07-25** |
| 07-21 | 4493 | PR | chelokot | 109 | disprove | closed unmerged (dup of #4495) |
| 07-21 | 4494 | PR | DomTheDeveloper | 109 | mark disproved | API says merged 07-21; commit not in current main history (109 disproof landed via #4495) |
| 07-21 | 4495 | PR | chelokot | 109 | disprove | **merged 07-26** |
| 07-21 | 4496 | PR | DomTheDeveloper | 314 | mark solved | open |
| 07-21 | 4497 | PR | DomTheDeveloper | 322 | mark solved | closed unmerged |
| 07-21 | 4499 | issue | infinityscroll | 200 | counterexample | open |
| 07-21 | 4500 | PR | infinityscroll | 200 | disprove | open |
| 07-21 | 4502 | issue | anagnorisis2peripeteia | 100 | misformalization | open |
| 07-21 | 4504 | PR | anagnorisis2peripeteia | 100 | fix definition | open |
| 07-21 | 4505 | PR | akakabrian | 146 | formalize+prove | open |
| 07-21 | 4507 | issue | infinityscroll | 209 | counterexample | open |
| 07-21 | 4508 | PR | infinityscroll | 209 | disprove (import+disprove) | open |
| 07-21 | 4509 | issue | anagnorisis2peripeteia | 291 | fix statement | open |
| 07-21 | 4510 | PR | anagnorisis2peripeteia | 291 | fix statement | open |
| 07-21 | 4513 | PR | DomTheDeveloper | 100 | mark solved | closed unmerged |
| 07-21 | 4514 | PR | SamuelSchlesinger | 65 | disprove | **merged 08-06** |
| 07-21 | 4515 | PR | DomTheDeveloper | 100 | mark solved | open |
| 07-21 | 4520 | PR | DomTheDeveloper | 145 | solve | open |
| 07-22 | 4540 | PR | Mapika | 146 | mark solved | open |
| 07-22 | 4541 | issue | anagnorisis2peripeteia | 194 | disproof | closed |
| 07-22 | 4542 | PR | anagnorisis2peripeteia | 194 | disprove | **merged 08-07** |
| 07-22 | 4556 | issue | SamPetkov | 284 | import-as-solved-false | open |
| 07-22 | 4557 | PR | SamPetkov | 284 | import-as-solved (disproved, Hoffman–Singleton) | open |
| 07-23 | 4559 | PR | akakabrian | 19 | mark solved | open |
| 07-23 | 4562 | issue | vulnix0x4 | 291 | counterexample claim | open |
| 07-23 | 4564 | issue | kingcharlezz | 2 | mark solved | closed |
| 07-23 | 4565 | PR | kingcharlezz | 2 | mark solved | **merged 08-06** |
| 07-23 | 4566 | issue | anagnorisis2peripeteia | 31 | fix statement | open |
| 07-23 | 4567 | PR | anagnorisis2peripeteia | 31 | fix statement | open |
| 07-23 | 4569 | issue | vulnix0x4 | 160 | proposed proof | open |
| 07-23 | 4570 | issue | anagnorisis2peripeteia | 36 | formalize counterexample | open |
| 07-23 | 4572 | PR | anagnorisis2peripeteia | 36 | certify disproof in-repo | open |
| 07-23 | 4573 | issue | QDKStorm | 59 | counterexample | open |
| 07-23 | 4574 | PR | QDKStorm | 59 | disprove | open |
| 07-23 | 4575 | issue | anagnorisis2peripeteia | 160 | proof, propose mark solved | open |
| 07-23 | 4576 | PR | anagnorisis2peripeteia | 160 | mark solved | open |
| 07-23 | 4582 | issue | anagnorisis2peripeteia | 59 | disproof certification | open |
| 07-23 | 4583 | PR | anagnorisis2peripeteia | 59 | certify disproof (18-vertex witness) | open |
| 07-23 | 4590 | issue | Kuberwastaken | 63, 85 | disproof certification | open |
| 07-23 | 4592 | PR | Kuberwastaken | 63, 85 | disprove (C5[K4]) | open |
| 07-23 | 4596 | issue | lukekabbash | 198a | proof | open |
| 07-23 | 4597 | PR | lukekabbash | 198a | mark solved | open |
| 07-24 | 4601 | issue | anagnorisis2peripeteia | 18 | misformalization | closed |
| 07-24 | 4602 | PR | anagnorisis2peripeteia | 18 | fix statement | **merged 08-03** |
| 07-24 | 4611 | PR | MiskinAleksandr23 | 1 | add formal proof link | **merged 07-25** |
| 07-24 | 4612 | issue | MiskinAleksandr23 | 1 | proof | closed |
| 07-26 | 4634 | PR | hypnopump | 58 | smaller counterexample (already false) | open |
| 07-27 | 4654 | PR | KitaKen1 | 2 | third formal proof | **merged 08-08** |
| 07-28 | 4656 | PR | KitaKen1 | 217 | mark solved (ext. proof) | **merged 08-04** |
| 07-28 | 4658 | PR | KitaKen1 | 31 | docs proof link | open |
| 07-30 | 4667 | issue | anagnorisis2peripeteia | 217 | request mark solved | closed |
| 07-30 | 4668 | PR | anagnorisis2peripeteia | 217 | mark solved | closed unmerged (lost to #4656) |
| 08-02 | 4686 | PR | MrBrain295 | 322 | prove | closed unmerged |
| 08-02 | 4687 | PR | MrBrain295 | 65 | prove (wrong direction — 65 is false) | closed unmerged |
| 08-02 | 4688 | PR | felixpernegger | repo-wide | modulize FormalConjectures/ | open |
| 08-03 | 4695 | issue | beowulf127 | 144 | proof | closed |
| 08-03 | 4696 | PR | beowulf127 | 144 | solve | **merged 08-04** |
| 08-03 | 4702 | issue | cozuya | 40 | status note (partial, n<=11 verified) | open |
| 08-04 | 4747 | issue | williamjblair | repo-wide | 53 test/API statements lack sorry-free proofs | open |
| 08-07 | 4819 | issue | williamjblair | repo-wide | category attrs on `example` recorded nowhere | open |

Older still-open WOWII items (pre-July): PR #3796 henrykmichalewski (2026-04-17, batch 2 import-as-open: 23, 24, 63, 72, 84, 85, 91, 96, 189, 199 — conflicted); PR #3821 henrykmichalewski (2026-04-22, 27 invariant-named files, no numbered conjectures except refs to 96, 209); PR #4111 henrykmichalewski (2026-05-29, draft placeholders: boxicity/crossingNumber/thickness); PR #1511 henrykmichalewski (2026-01-06, K3 verification for 19); PR #4161 mo271 (2026-05-31, formal_proof for 17); PR #3676 mo271 (Test.lean tests); issue #3808 (34 statement dispute).

Merges landed on main since the 2026-07-23 sweep: #4602 (18 fix, 08-03), #4656 (217 solved, 08-04), #4696 (144 solved, 08-04), #4430 (322 proved, 08-05), #4565 (2 solved, 08-06), #4514 (65 disproved, 08-06), #4426 (316 solved, 08-07), #4542 (194 disproved, 08-07), #4654 (2 third proof, 08-08), #4457 (142 solved, 08-11); plus #4482 (103, 07-25), #4611 (1 link, 07-25), #4443 (160 fix, 07-26), #4495 (109, 07-26) just before/at that sweep.

Anomaly note: PRs #4442 (143) and #4494 (109) report `merged: true` (2026-07-21) in the GitHub API with merge_commit_shas `35707f05...` / `76ad865f...`, but neither commit exists in current upstream/main history; 143's solved status entered main inside #4563 (07-23 LaTeX-linter commit) and 109's disproof re-landed via #4495.
