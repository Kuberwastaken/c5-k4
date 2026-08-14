# GitHub Actions scientific-shard audit

Date: **2026-08-14 UTC**

Scope: read-only audit of `Kuberwastaken/c5-k4` Actions settings, retained
artifacts/caches, recent runs, frozen-job workflows, and the Method v1.5 live
search runtime.  This audit does not dispatch a workflow or make a discovery
claim.

## Current repository state

- The repository is public. Standard GitHub-hosted Actions minutes are free for
  public repositories.
- Actions are enabled, all actions are allowed, and the default workflow token
  permission is read-only.
- Artifact/log retention is configured at 90 days, the maximum for a public
  repository. Individual scientific artifacts should request a shorter period.
- Three retained artifacts occupy 50,370 bytes. Five dependency caches occupy
  67,697,552 bytes. Storage is not presently a constraint.
- Recent relevant runs are serial validation/Lean jobs. No large search matrix
  was active during this audit.

GitHub's current documented ceilings relevant to this repository are:

- 40 concurrent standard GitHub-hosted jobs for GitHub Pro;
- 256 jobs in one matrix;
- six hours per hosted job;
- 1 GB of included artifact storage for GitHub Pro; and
- 10 GB of default dependency-cache storage per repository.

The account-level cache-limit API returned HTTP 402 while the ordinary cache
inventory remained readable. The reusable design therefore assumes the
documented default and does not require cache writes. A 32-job maximum leaves
eight nominal Pro slots for validation, Lean, and unrelated repositories owned
by the same account.

## Existing workflow findings

The v1.1-v1.4 frozen-job workflows have strong commit pinning, clean-checkout
checks, immutable artifact upload, and content addressing. They execute one
cluster/mode/arm per manual dispatch rather than a bounded multi-shard matrix.

`catchup-exact-minimax.yml` demonstrates a small two-job matrix and always
uploads each row. Its `TIMEOUT_OR_EXTERNAL_TERMINATION` classification groups
exit codes 124, 137, and 143, so the artifact does not distinguish the wrapper's
deadline from an external cancellation or kill.

The live-search runtime has durable, fsynced, hash-chained JSONL prefixes and an
actual process-group deadline. Its worker-owned `COMPLETED` summary only proves
normal worker return, however. It does not bind an assigned finite range or
prove iterator exhaustion. The phase-three TxGraffiti report correctly treats
those results as bounded prefixes.

Top-level deterministic concurrency groups are also unsuitable for repeated
scientific dispatches: GitHub permits only one running and one pending member
of a concurrency group, and a newer pending run replaces the older pending
run. A scientific campaign should either use a single matrix dispatch or avoid
such a group so queued evidence is not silently displaced.

## Reusable contract added by this audit

The uncommitted files below provide an isolated generic implementation:

- `.github/workflows/scientific-shard-campaign.yml`
- `scripts/run_scientific_shard_campaign.py`
- `scripts/test_run_scientific_shard_campaign.py`

The workflow accepts only an exact 40-hex commit, a repository-relative frozen
manifest, and a bounded `max_parallel` choice. The manifest supplies at most
256 disjoint half-open ranges, exact domain digests, argv vectors (never shell
strings), and a runner deadline of at most 60 seconds. The GitHub job receives
separate setup and artifact-upload slack; it does not broaden the scientific
process cap.

Each matrix worker writes incremental output only below its own directory. The
runner separately writes `runner-terminal.json` with one of:

- `DOMAIN_EXHAUSTED`: accepted only after a canonical worker attestation bound
  to the commit, domain digest, shard range, and full expected state count;
- `CANDIDATE_FOUND`: a candidate stop, not an exhaustion claim;
- `DEADLINE_PREFIX`: assigned only when the runner itself observes its timeout
  and terminates the worker process group;
- `WORKER_INCOMPLETE`: zero exit without an attestation;
- `INVALID_WORKER_ATTESTATION`; or
- `WORKER_FAILURE`.

Every shard record is content-addressed and uploaded even when classification
fails. The final job downloads the small terminal records and writes a campaign
index. It emits campaign-level `DOMAIN_EXHAUSTED` only if every expected shard
is present and exhausted. Missing artifacts, invalid results, and any deadline
remain explicit non-exhaustive outcomes.

No dependency cache is written per shard. This avoids a 32-way cache upload
race and cache churn. Campaign-specific numerical libraries and exact tools
(especially the frozen `labelg`) must be provisioned reproducibly before this
generic workflow is dispatched. The current TxGraffiti phase-four worker uses
a different terminal schema and needs an adapter; it must not be pointed at
this workflow unchanged.

## Recommended operating envelope

1. Freeze the finite canonical worklist first and hash each disjoint partition.
2. Commit the manifest, worker, dependency lock/tool digest, and this runner in
   the same exact campaign commit.
3. Start with `max_parallel=24`; increase to 32 only when no other large account
   workload needs the headroom.
4. Keep shard artifacts at 30 days and promote only candidate certificates or
   final aggregate evidence into Git. Do not use Actions cache as evidence.
5. Treat `DEADLINE_PREFIX` as a valid retained prefix that may seed a new frozen
   continuation manifest, never as a zero or an exhausted search.
6. Require a separate exact replay/certificate lane before publishing a
   candidate as a release.

Official limit references:

- <https://docs.github.com/en/actions/reference/limits>
- <https://docs.github.com/en/actions/concepts/billing-and-usage>
- <https://docs.github.com/en/actions/reference/workflows-and-actions/dependency-caching>
- <https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/run-job-variations>
