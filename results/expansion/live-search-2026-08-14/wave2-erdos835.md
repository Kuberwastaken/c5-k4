# Wave 2 live search: Erdős 835 at `k=10`

Started: 2026-08-14 UTC  
Scope: actual complement-quotiented witness search; no repository file other
than this incremental log was edited.  The engine was built in `/tmp`.

## Live source and repository gate (before spend)

Commands:

```text
git remote -v
git branch --show-current
git status --short
gh pr status
git ls-remote https://github.com/google-deepmind/formal-conjectures.git HEAD
gh pr list --repo google-deepmind/formal-conjectures --state open --search '835' --limit 100 --json number,title,state,url,updatedAt,headRefName
gh pr list --repo google-deepmind/formal-conjectures --state all --search '835' --limit 100 --json number,title,state,url,updatedAt,headRefName
gh api 'repos/google-deepmind/formal-conjectures/commits?path=FormalConjectures/ErdosProblems/835.lean&per_page=10'
```

Observed before any search:

- local repository: `origin=https://github.com/Kuberwastaken/c5-k4.git`, branch
  `main`, no associated/open authored PR; the pre-existing untracked
  `lean/SnakeInTheBoxNine191.lean` was left untouched;
- upstream HEAD: `b33d8678a28118c95d8d4f60b11faaf39ccff1e6`;
- no open upstream PR matched `835`;
- direct solution PRs #2548 and #3073 remain closed; introducing PR #1428 is
  merged.  The latest commits touching `835.lean` are refactors, most recently
  `c252a41054125b5fd9c8356e2137cd9b55337657` (2026-07-16), not a solution.

Disposition at the gate: **VERIFIABLE/open**.

## Frozen quotient and literal objective

Let a variable be an unordered complement pair `{B,[20]\\B}` of 10-sets.
There are `C(20,10)/2 = 92,378` variables.  For every 9-set `T`, its eleven
extensions `T∪{x}` give eleven complement-pair variables, constrained to have
all eleven colors.  There are `C(20,9) = 167,960` such constraints, and every
variable occurs in exactly 20 constraints.

This is the complement-closed large-set formulation: a color class covers
each 9-set exactly once, hence is an `S(9,10,20)`; all eleven classes partition
the complement pairs.  A full solution has exactly `92,378/11 = 8,398`
complement pairs in each color.

The literal residual is

```text
sum_T (11 - number of distinct colors on the eleven extensions of T).
```

Residual zero is exactly the requested coloring.  Each final state is replayed
against every one of the 167,960 constraints; a zero would additionally print
`candidate=1` and `exact_check=1`.

Frozen arms (no result sharing):

1. `CATALOGUE`: complement-symmetric modular moment/product families;
2. `GENERIC`: unconstrained complement-pair min-conflict recoloring;
3. `WALL_LARGE_SET`: balanced initialization with exactly 8,398 variables of
   every color, followed only by two-color swaps, so the necessary large-set
   class sizes hold throughout.

Build and identification:

```text
g++ -O3 -march=native -std=c++20 /tmp/erdos835_wave2.cpp -o /tmp/erdos835_wave2
sha256sum /tmp/erdos835_wave2.cpp /tmp/erdos835_wave2
```

The final source/binary hashes and the three capped command transcripts are
recorded below after the frozen runs.

## Native controls

Command:

```text
/usr/bin/time -f 'elapsed=%e maxrss_kb=%M' /tmp/erdos835_wave2 controls
```

Output:

```text
CONTROL k=2 variables=3 constraints=4 residual=0 rainbow=4 verified=1 hash=a940e14f3a8f72be
CONTROL k=3 J(6,3)_4colorable=0 dsatur_nodes=257 verified_negative=1
elapsed=0.00 maxrss_kb=3504
```

Thus the complement-quotient evaluator accepts the standard positive `k=2`
factorization, while an exact DSATUR traversal independently rejects a
four-coloring of `J(6,3)`.

## Engine calibration and audit trail

Two short development calibrations were run before freezing the optimized
incremental updater.  They are not included in the equal-cap comparison:

```text
timeout ... 8s /tmp/erdos835_wave2 generic 8351001 5
RESULT ... moves=13032 accepted=10348 residual=595687 rainbow=63 exact_check=1
elapsed=5.11 maxrss_kb=35984

timeout ... 8s /tmp/erdos835_wave2 wall 8351002 5
RESULT ... moves=4337 accepted=2028 residual=638488 rainbow=34 exact_check=1 balanced=1
elapsed=5.08 maxrss_kb=37012
```

After replacing a full residual recount on every recolor with an incremental
update, the 3-second checks were:

```text
timeout ... 7s /tmp/erdos835_wave2 generic 8351001 3
RESULT ... moves=98730 accepted=47282 residual=464339 rainbow=634 exact_check=1
elapsed=3.09 maxrss_kb=35852

timeout ... 7s /tmp/erdos835_wave2 wall 8351002 3
RESULT ... moves=258338 accepted=47823 residual=509741 rainbow=268 exact_check=1 balanced=1
elapsed=3.13 maxrss_kb=37008
```

A first equal-cap launch used seeds `8352001`, `8352002`, `8352003` and the
same commands as below.  All three process trees reached their caps, but the
calling orchestration discarded their final stdout after yielding early.
Those attempts are **UNSCORED_TELEMETRY_LOSS**: no residual or candidate claim
is made from them.  Process inspection confirmed that the exact three capped
commands ran to termination before the scored relaunch.  No state was shared
with the relaunch.

Final frozen engine hashes:

```text
9441efe15301c51197580f9d7958a157060cbaa6ac063ed55ee57e683c84f475  /tmp/erdos835_wave2.cpp
6a289d206a2daadfe96eafdf68befe963fb500bfc4f7e6b480cec5953988d270  /tmp/erdos835_wave2
```

## Equal hard-cap comparison

Each arm was an independent process with an external hard cap of 60 seconds
and an internal 58-second reporting budget:

```text
/usr/bin/time -f 'elapsed=%e maxrss_kb=%M exit=%x' timeout --signal=TERM --kill-after=1s 60s /tmp/erdos835_wave2 catalogue 8352101 58
/usr/bin/time -f 'elapsed=%e maxrss_kb=%M exit=%x' timeout --signal=TERM --kill-after=1s 60s /tmp/erdos835_wave2 generic   8352102 58
/usr/bin/time -f 'elapsed=%e maxrss_kb=%M exit=%x' timeout --signal=TERM --kill-after=1s 60s /tmp/erdos835_wave2 wall      8352103 58
```

Exact outputs:

```text
RESULT arm=CATALOGUE seed=8352101 seconds=58 evals=3168 residual=798650 rainbow=0 hash=9e903947fa0ebbfe candidate=0 exact_check=1
elapsed=58.17 maxrss_kb=36224 exit=0

RESULT arm=GENERIC seed=8352102 seconds=58 moves=65805402 accepted=96469 restarts=0 residual=369820 rainbow=2660 hash=38ef186462d0c3e3 candidate=0 exact_check=1 balanced=0
elapsed=58.11 maxrss_kb=36468 exit=0

RESULT arm=WALL_LARGE_SET seed=8352103 seconds=58 moves=23115436 accepted=186746 restarts=0 residual=384619 rainbow=2240 hash=7e6cc2b876effc6f candidate=0 exact_check=1 balanced=1
elapsed=58.23 maxrss_kb=37388 exit=0
```

| arm | seed | work | literal residual | rainbow constraints | exact replay | verdict |
|---|---:|---:|---:|---:|---:|---|
| `CATALOGUE` | 8352101 | 3,168 complete formulas | 798,650 | 0 | pass | `NO_CANDIDATE` |
| `GENERIC` | 8352102 | 65,805,402 moves | **369,820** | **2,660** | pass | `NO_CANDIDATE` |
| `WALL_LARGE_SET` | 8352103 | 23,115,436 swaps | 384,619 | 2,240 | pass; balanced | `NO_CANDIDATE` |

The large-set wall beats the catalogue by 414,031 residual units but trails
generic recoloring by 14,799.  Its important additional certificate is
`balanced=1`: every color has the exact required 8,398 complement-pair blocks.
The generic arm's lower residual does not enforce that global exact-cover
count during search (although residual zero would force it automatically).

## Literal witness disposition

All `k=10` states use one variable for a complement pair, so complement
equality is structural rather than checked probabilistically.  For every
scored terminal state the engine rebuilt the number of represented colors in
all 167,960 rows and reproduced the incremental residual (`exact_check=1`).
No state had residual zero, so there is no coloring to serialize or submit to
an independent candidate verifier.  Claimable candidates: **zero**.  These
bounded failures are not evidence of nonexistence.

## Completion recheck

Completed: 2026-08-14T06:41:00Z.

```text
git ls-remote https://github.com/google-deepmind/formal-conjectures.git HEAD
b33d8678a28118c95d8d4f60b11faaf39ccff1e6  HEAD

gh pr list --repo google-deepmind/formal-conjectures --state open --search '835' --limit 100 --json number,title,url,updatedAt
[]
```

The source status did not change during spend.  No issue, PR, comment, commit,
push, release, or other outward mutation was performed.
