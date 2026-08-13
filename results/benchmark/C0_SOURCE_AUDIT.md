# Method v1.1 C0 source-discovery audit

This audit records the source boundary used for the semantics-blind
contamination scan. It was fixed before entropy selection and without reading
candidate statements. The pinned declaration registry is
`google-deepmind/formal-conjectures` commit
`7a38c469ec329d0c97c068e03c58834f61628e7e`, tree
`daa36d0d9e82133dfd83488d89594d92b4940fb7`.

## Included histories

- the complete reachable Git histories of `c5-k4`, `breakthroughmaxxing`,
  `conway99-c3-orbits-lean`, `formal-conjectures-counterexamples`, `reimann`,
  `subagentmaxxing`, `wanless-778-lean`,
  `wowii-63-85-counterexample`, and `zeta-23-lean`;
- the complete current `c5-k4` worktree, including untracked research files;
- commits in the local `formal-conjectures` fork not reachable from any
  `refs/remotes/upstream/` ref;
- the unversioned `permanental-dominance-n4` and research `scratch` trees;
- format-aware natural-language turns from the `codex/` and `claude/` trees at
  exact synchronized `ai-chats` commit
  `e1a0fc9da99979ee34619608a0b28fb93d144497`;
- the complete c5-k4 GitHub release metadata snapshot acquired before C0.

The separate `formal-conjectures-wowii309` checkout is a clean linked worktree
of the included formal-conjectures Git common directory. Its committed branch
is therefore covered by the user-only delta rather than duplicated as a tree.

Every configured source completed. The exact observed scan-unit counts and
corpus hashes are:

| Source | Units | Corpus SHA-256 | Raw malformed rows |
|---|---:|---|---:|
| `git:c5-k4-campaign` | 8199 | `6bad8a76c76e7dab533028c9cad04cc495bd0204d659062780040215ffc03b16` | 0 |
| `git:breakthroughmaxxing` | 27019 | `2ba7015dd212acf179152143826fc274778f12f7ae15b9dc2e71011fc07528a3` | 0 |
| `git:conway99-c3-orbits-lean` | 19 | `7632b13496b1e8f2bd47a2839a050d14f5a59c959de4e15bcdbffb24a94951b1` | 0 |
| `git:formal-conjectures-counterexamples` | 7 | `af66e6dfe37c62c81dee6015a29af1b7baa8fb3058b96df245bb0b5976faf7c2` | 0 |
| `git:reimann` | 733 | `dd960d6e3d94c8861046c1f2f6a16530155e572e5e928c54f4ac31f187ba0c2c` | 0 |
| `git:subagentmaxxing` | 67 | `a76fe25273e9dcf85a1651259f200c457a1ad50bd094b4919d5ae6441a73409b` | 0 |
| `git:wanless-778-lean` | 35 | `052b6798e10549a36a99280e21bf990be638de50fb3b11ef2e8cff1829a7c14d` | 0 |
| `git:wowii-63-85-counterexample` | 27 | `17bbca978428eb8cd688c42601614c491fad9670f6ac988ba3d5c0640f093157` | 0 |
| `git:zeta-23-lean` | 683 | `c04cff3a9c6c738c4acaa3dd77c12e722cc257f34801af0a098e4b2eb5bd68bf` | 0 |
| `git:formal-conjectures-user-delta` | 55 | `f48821cb16d1d20758ad9dd1aa2e0fecac47714a056f99f5923cb544b4bd4fd7` | 0 |
| `tree:unversioned-permanental-dominance` | 14 | `9ba267f632970f8f0910f3752d427dece7d567592acfea72bdca149742507c01` | 0 |
| `tree:research-scratch` | 236 | `eca5ea01352a232c774fde7cc64fcc92bd578eb1bd18c39cedc0f69447fb24a3` | 0 |
| `sessions:codex` | 30076 | `fece9d3e3b9a0066879d835ceceae7d929cdb0627ff75137929873dde9162865` | 562 |
| `sessions:claude` | 34626 | `7de49c5b5adf029ed96d5039074558c86349b80ac7e844c658dd4792539e1c84` | 599 |
| `releases:c5-k4` | 4 | `7980a092091c6614d7a63d29e081599e1f9e6634b169b675cbf3ed47ca302a7b` | 0 |

## Deliberate non-research exclusions

Repository discovery also found product/application, personal-site, résumé,
and marketing repositories. They were excluded by repository purpose rather
than candidate identity: `claurst`, `cookie`, `grok-build`, `hive`,
`kuberwastaken.github.io`, `linkedin-forensics`, `megaphone`, `resume`, and
`sira-router`. The active `marketing-outbound` tree and services were neither
read nor altered. Logo-only directories and command-placeholder directories
were likewise outside the research-history boundary.

## Conservative recovery and exemptions

Tool outputs are excluded from parseable session rows because registry dumps
are not evidence of semantic consideration. Malformed synchronized JSONL rows
are searched as exact raw text instead: 562 Codex rows and 599 Claude rows.
Their locator/unit-hash digests are recorded in the inventory, and all 15
configured sources completed.

Only three exact raw-file hashes are exempted from the campaign worktree: the
machine-generated open inventory, provisional cluster pool, and syntax-only
classifier. The exemption is byte-exact and does not cover mixed method prose,
research notes, scripts, proofs, or any other worktree unit.

## Result

The registry contains 729 conservative source-module clusters. The scan marks
281 exposed and 448 unexposed. Combining this with syntax-only eligibility
leaves 250 eligible clusters:

- `GRAPH_SCALAR_INEQUALITY`: 0;
- `GRAPH_STRUCTURAL_PROPERTY`: 0;
- `FINITE_ALGEBRA_EQUATIONAL`: 7;
- `AUTOMATA_GAME_PROCESS`: 1;
- `FINITE_COMBINATORIAL`: 242.

The frozen quotas therefore cannot be filled. Under the no-backfill rule, this
pool supports `NO_ELIGIBLE_BENCHMARK`; it must not proceed to C1 selection by
relaxing contamination or changing strata.

The final inventory's internal canonical hash is
`1981fa17203ecc8be92ddd6b742971b077c840d09968c0e0898993ac73623f69`;
its file hash is
`fe74bbb0fc976101fa2ecba105eb0713fb9bea2122967778fc013bda95d1fe4c`.
The contamination-applied pool file hash is
`66053635704287dcfa78cb0529ff00871fac19b0e3ce329cdde94cfa2f161ef1`.

One diagnostic run accidentally saw the prior inventory output inside the
campaign worktree and therefore over-excluded every cluster. That diagnostic
was moved outside the repository and is not the frozen result. The final scan
started with both inventory and overlay destinations absent; only its 281/448
split and the hashes above are authoritative.
