# WOWII counterexample release-backlog audit

Date: **2026-08-13 UTC**

## Scope

This is a conservative audit of completed counterexample work in the
`c5-k4` repository that could plausibly belong in the one-problem GitHub
release workflow.

The scope is restricted to **Written on the Wall II and graph-conjecture work
covered by the formal-conjectures campaign**. Written on the Wall I and Graph
Brain are excluded. The audit compares `README.md`, `HANDOFF.md`, the durable
reports and ledgers in `results/expansion/`, the local release tags, the Lean
and executable certificates, and the git history.

The release gate used here is intentionally strict. A result is not ready if
it is already claimed publicly, already has a project release, is only a
retro-kill, depends on a corrupt or ambiguous source statement, is a theorem
or theorem signal rather than a counterexample, or lacks complete exact and
formal verification.

## Result

**There is no unreleased, apparently-unclaimed, release-ready counterexample
in the audited scope.**

The four current one-problem releases and their local tag targets are:

| release | tag target |
|---|---|
| WOWII 172 | `wowii-172-v1` -> `64abb3ce00e6ac34ac8358baa9798511d0ca8ec0` |
| WOWII 176 | `wowii-176-v1` -> `51faa868b85ce5069e4017dfa97845772435229a` |
| WOWII 181, qualified square-degree reading | `wowii-181-v1` -> `f71a0d28b59907b8b9ee9f534d6ad7d5cdf8a528` |
| WOWII 430a | `wowii-430a-v1` -> `d187206a7328cbaf1e595cee2e178eb86076ec29` |

## Ranked unreleased completed results

The table ranks the mathematically completed but unreleased WOWII disproofs by
proximity to the release gate. Every row is disqualified by an existing
priority or public-completion record.

| rank | conjecture | witness | evidence files | exact-verifier status | novelty / reading caveat | release readiness |
|---:|---|---|---|---|---|---|
| 1 | 63 | `C5[K4]` | `results/open_sweep/batch0.jsonl`; `data/profile.json`; `lean/GraphConjecture63.lean`; `README.md` | The open-sweep row records exact exhaustive checks of `f=4`, `b=4`, and both even-distance conventions. The local formal-conjectures-style file is a benchmark stub whose annotation links the complete external no-`sorry` certificate. | Kuber publicly claimed this result on 2026-07-23; formal-conjectures PR #4592 merged it, and the dedicated `wowii-63-85-counterexample` repository already publishes the complete certificate. | **Not backlog: already publicly completed by this campaign.** |
| 2 | 85 | `C5[K4]` | `results/open_sweep/batch0.jsonl`; `data/profile.json`; `lean/GraphConjecture85.lean`; `README.md` | The open-sweep row records an exact exhaustive induced-tree bound and both even-distance conventions. The local benchmark stub links the complete external no-`sorry` certificate. | Kuber publicly claimed this result with 63; it was merged by formal-conjectures PR #4592 and is already published in the dedicated certificate repository. | **Not backlog: already publicly completed by this campaign.** |
| 3 | 64 | `C5[K4]` | `results/expansion/wowii_64_status_audit.md`; `results/verification.md`; `results/expansion/publication/wowii_64_preflight.md`; `scripts/verify_wowii_64.py`; `lean/GraphConjecture64.lean` | Fresh bounded replay on 2026-08-13 passed in 0.039 seconds: all 1,140 triples and 15,504 five-subsets were exhausted, proving `alpha=2`, `f=4`, and `4<5`. The preflight records a warning-clean no-`sorry` Lean build and trust audit. | Jonas J. Gebendorfer published the disproof, a smaller 18-vertex witness, and an infinite family on 2026-07-26, while crediting the earlier carrier work. | **Ineligible: externally claimed; do not release as apparently unclaimed.** |
| 4 | 309 | `C5[K4]`; externally recorded family `C5[K_k]`, `k>=3` | `results/expansion/wowii_309_status_audit.md`; `results/literature.md`; `scripts/verify_wowii_309.py`; `lean/GraphConjecture309.lean` | Fresh bounded replay on 2026-08-13 passed in 0.217 seconds. All six nearby readings fail on the witness; the chosen source reading gives `3<=-3/2`. The Atlas sanity gate evaluated 989 of 994 connected order-3-through-7 controls, with five complete graphs undefined and zero violations. | Jonas J. Gebendorfer published the family disproof on 2026-07-25. The local Lean work is a later formal certification, not a new resolution. | **Ineligible: externally claimed; do not release as apparently unclaimed.** |

## Additional exclusions

- **Already released:** WOWII 172, 176, 181, and 430a have individual project
  releases and matching local tags. The 181 release is explicitly limited to
  the formalized square-degree reading; the alternate in-`G` reading holds on
  `T(7)` and remains prominent in the release audit.
- **Already publicly completed by this campaign:** WOWII 63 and 85 are merged
  upstream and have a dedicated external certificate repository. A second
  project release would not be an unreleased discovery.
- **Known external priority:** WOWII 64 and 309 have complete local exact and
  Lean certificates, but Gebendorfer's dated publications already record the
  mathematical disproofs. They are formalizations of known results.
- **Retro-kills:** WOWII 24, 25, 46, 49, 52, 54, 55, and 56, plus 77 under one
  reading, were already refuted by others. The carrier reproducing those
  failures is valuable structural evidence but not a novel release claim.
  WOWII 174 likewise has an existing counterexample record.
- **Corrupt or unusable source statements:** 401b fails the mandatory
  small-graph sanity gate under both recorded readings. The literal 412f and
  448b statements are already contradicted by elementary database graphs such
  as `K3`/`K4` and `C4`; the durable audits classify them as corrupt or
  transcription-garbled rather than claimable counterexamples. The printed
  proved-theorem 97 minus sign is an erratum, not an open-conjecture kill.
- **Gate-refuted family readings:** apparent violations such as the 255/256
  endpoint-excluding readings fail the database-sanity gate and are not
  candidates.
- **Theorems rather than counterexamples:** 438b has a complete stronger
  arbitrary-subset proof and an upstream proof/formalization record. It does
  not belong in the counterexample release queue.
- **Incomplete theorem lanes:** 133 has a corrected cubic specialization and
  compiled local bridges, not a completed disproof or full formal proof of the
  original statement. The 183 work remains a narrowed theorem signal with no
  counterexample and no complete proof.
- **Bounded holds:** the 61, 382e, 422b, 430c/434c, and 184/185 trials found no
  gate-surviving crossing. A bounded hold or theorem signal is not a release.
- **Current formal-conjectures cross-sweep:**
  `results/expansion/formal_conjectures.md` classifies all 77 declarations in
  its locked manifest and records no new gate-surviving violation.

## Conclusion

The release backlog is **empty** under the current policy. The next release
must come from a new result that survives source recovery, all plausible
readings, the database-sanity gate, independent exact recomputation, current
novelty checking, complete warning-clean formal certification, and the
one-problem release preflight. None of the completed but unreleased WOWII
artifacts presently satisfies the novelty gate.
