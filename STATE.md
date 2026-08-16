# Where this project stands — 2026-08-16

Read this first when picking the work back up. It is the situation report, not
a summary of achievements; `CONTRIBUTIONS.md` is the ledger and `README.md` is
the story.

Nothing is running. No agents, no background loops, no watchers. The working
tree is clean and everything is pushed (main, 2,094 commits).

## The one-paragraph version

The C₅[K₄] carrier work is real and largely finished. The corpus-audit lane is
productive and **six PRs are now merged upstream**. The research claim the
project is named for — that tightness structure *prospectively* designs
counterexamples — was put to its first preregistered test and came back at
**wall-unique = 1 of 30**, which is close to null. A v2 population that fixes
v1's two blamable weaknesses is frozen and ready, but its arms have not run,
and there is an unresolved question of whether running it is a fair narrower
test or moving the goalposts. That question is the main open decision.

## What is settled

- **63 and 85** disproved via C₅[K₄], merged upstream (#4592). Four more merges
  landed 2026-08-16 (#4987, #4988, #4992, #4999) plus the earlier #4605.
- **16 PRs still open** upstream, all CI-green or building; **22 issues** filed.
- The **discretization-cliff paper** is drafted at `paper/discretization-cliff/`
  — 14 pages, compiles, with `verify_paper_claims.py` re-deriving every numeric
  claim. It proves more than the original brief: `C_{2r+1}[K_m]` pins
  path/tree/f/b at `2r` for **every** `m ≥ 1`, not just C₅. Both independent
  reviews called this the one genuinely novel contribution. **It is not
  submitted anywhere.**
- **Method frozen at v1.7**, which contains only repairs the experiment forced.
  No v1.8 without new evidence.

## The experiment, and what it means

`results/experiment/` — protocol tagged before the population existed, population
tagged before the arms ran, adjudicator committed before any arm reported.

```
catalogue (8)  ⊆  generic (14)  ⊆  wall (15)
```

The wall arm found everything the controls found and exactly one target more.
Verdict INCONCLUSIVE by the letter (falsification needed wall-unique ≤ 0), but
nobody should read the label as encouraging. Two caveats were tested rather than
assumed: the control later ran ~16 more hours and converted 14 brackets **all
into HELDs, none into CROSSEDs**, so the "budget-starved control" excuse is
dead and the single margin is real; and the disclosed contamination risk (E2)
biases *against* the method, so it cannot explain the result away.

Findings worth keeping regardless: the G3-lite sign check stopped 691 of 756
trials (91%) — a good filter even if navigation has no discovery value — and it
has a real bug, that step-function residuals read `dR = 0` across adjacent
members, which silently kills families that do cross.

## The open decision

**Should experiment v2 run?** `results/experiment-v2/` has a frozen population:
`D₂` complete through **n = 9 (273,192 graphs**, versus v1's 12,112), all 30
targets carrying hereditary induced invariants (`f`, `b`, `tree`, `path`, `α`) —
the vein v1 excluded on runtime grounds and therefore could not test. R4
cross-validation ran over the whole database and caught a bug pre-freeze.

The argument for: v1 could not test the mechanism it was about.

The argument against, which is serious: **v1's own generator pre-committed in
writing that a null "cannot be blamed" on the missing invariants.** v2 is
therefore designed as an explicitly *narrower* hypothesis (does navigation win
*where its mechanism applies*), and a positive v2 licenses only that bounded
claim, never H1 as originally stated. Whether that is legitimate or
goalpost-moving is a judgement call that has not been made.

A second independent Fable review was launched to rule on exactly this and was
**killed before finishing** — no verdict exists. Re-running it is cheap and is
probably the right first move.

## Honest liabilities

- **Nine corrections are logged** in `CONFIRMED_LEDGER.md`, two of them issued
  after we had already published the claim upstream. The interior error rate on
  single-pass findings is roughly 40%. The adversarial verification layer is the
  only reason the published record is trustworthy — do not drop it to go faster.
- **Seven status-sync findings are marked CONTESTED**, held back because the live
  source was unreachable and an offline mirror disagreed. They need re-checking
  against erdosproblems.com before anyone claims them.
- The first review's numbers: P(fresh test vindicates the wall arm) 25–30%,
  P(result mathematicians outside the niche care about) **5%**. The experiment
  has since come in near-null, which should move the first number down.

## Live threads with maintainers

- **#4986** (Erdős 1093) — replied with a corpus-wide `smoothNumbers` audit;
  1093 is the only instance, 961 already compensates correctly. Offered a
  one-word docstring nit in 961; awaiting his preference.
- **#5004** (Books/Equidistribution) — argued the ∀-form is *known false* (de
  Mathan; Pollington) so it should be `answer(False)` + `research solved` rather
  than `answer(sorry)`. Citations verified and ready. **Awaiting mo271's
  decision; the switch is deliberately not pushed.**
- **#4991** (Erdős 477) — docstring synced to the source's renamed variables.

## Infrastructure

25 active workflows, all parsing, all with valid triggers and no missing script
references. 22 archived under `.github/workflows-archive/`. A latent landmine
was fixed on 2026-08-16: `erdos-resolution-shape-audit.yml` invoked a
`campaign/` path that has never existed in this repo and would have failed on
main the first time anyone edited the script it watches.

Disk: **5.9 GB free (91% used)**. The big win was `git gc` on the ai-chats
archive (5.0 GB → 1.5 GB). **The `chats-to-git` cron is still paused and should
stay paused** until its re-blobbing bug is fixed — it was re-committing an 82 MB
rollout every five minutes. `agent-wt/` (2.6 GB) is marketing-outbound's active
worktrees; leave it alone.

## If you want the shortest path to value

1. Re-run the second independent review; let it rule on v2.
2. If it says run v2, run the arms **sequentially and isolated** (METHOD v1.7
   R2) — concurrent arms caused the contamination event.
3. Regardless of v2: the cliff paper is the most likely thing here to matter to
   anyone outside this repo, and it is sitting finished and unsubmitted.
