# Archived workflows

Workflows here are **inactive** — GitHub Actions only reads
`.github/workflows/`. They are kept in-tree rather than deleted so the research
trail stays intact (their past runs also remain visible in the Actions tab).

Archived 2026-08-15:

| File | Why |
|---|---|
| `method-v11-frozen-job.yml` | superseded by v1.5 / v1.6 |
| `method-v12-frozen-job.yml`, `method-v12-validation.yml` | superseded |
| `method-v13-frozen-job.yml`, `method-v13-validation.yml` | superseded |
| `method-v14-frozen-job.yml`, `method-v14-validation.yml` | superseded; the v1.4 release is tagged `method-v1.4-terminal` |
| `oeis-a231201-v2-development.yml`, `-v21-`, `-v22-` | three redundant revisions of one target; the `-v3-` job remains active |
| `oeis-a056777-v2-development.yml` | target lane stopped (see `live-search-2026-08-14/oeis-a056777-v3-reachability/preflight.md`) |

Restoring one is a `git mv` back into `.github/workflows/`.

## Standing note on workflow count

Even after this pass there are 36 active workflow files, most of them one-shot
"development" jobs for a single target. That is a lot of surface for the number
of results it has produced, and it is a live question in the 2026-08-15
independent review (`results/review/`). Prefer reusing a parameterised job over
adding another per-target file.
