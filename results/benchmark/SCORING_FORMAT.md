# Method v1.1 ledger-derived scoring format

`scripts/score_benchmark_v11.py` is the sole aggregate-score constructor. It
accepts a `COMPLETE` Method v1.1 manifest, validates that manifest and every
content-addressed hash chain with `lint_benchmark_v11.py`, and emits canonical
JSON. It does not accept precomputed score fields.

Run:

```sh
python3 scripts/score_benchmark_v11.py results/benchmark/<manifest>.json
```

All quantities used in exact calculations must be JSON integers or rational
strings such as `"17/20"` or `"0.35"`. JSON floating-point numbers are
rejected by the scorer. Output ratios are reduced rational strings.

## Score events

Ordinary job rows keep the base ledger fields documented by the manifest
linter. Exactly one terminal score event is added to the appropriate row under
`score_event`. Fields are closed: omissions and additional keys fail scoring.

Every runnable cluster has one terminal row in each discovery arm:

```json
{
  "score_event": {
    "kind": "ARM_TERMINAL",
    "status": "COMPLETE",
    "objective": {
      "residual_orientation": "SAFE_NONNEGATIVE",
      "signed_residual": "-3/4",
      "frozen_control_residual": "1"
    },
    "controlling_term": null
  }
}
```

The objective exactly implements the frozen scoring rule. For a residual whose
safe side is nonnegative, gain is `max(0, -signed_residual) / control_scale`;
for a residual whose safe side is nonpositive, it is
`max(0, signed_residual) / control_scale`, where the scorer derives
`control_scale = max(1, abs(frozen_control_residual))` exactly.
For `TIMEOUT` and `PROTOCOL_INVALID`, `objective` must be null and the scorer
assigns zero gain. A completed `WALL_NAVIGATION` event instead has:

```json
"controlling_term": {"forecast_sign": 1, "observed_delta": "3/5"}
```

The preregistered forecast sign is nonzero. The two baseline arms must use
null. An incomplete wall arm also uses null and is excluded because it has no
exact evaluation.

Every cluster has exactly one `SHARED_ANALYSIS` terminal event:

```json
{
  "score_event": {
    "kind": "CLUSTER_TERMINAL",
    "terminal_outcome": "ZERO_COMPLETE",
    "theorem_yield": "0",
    "theorem_evidence": "NONE",
    "theorem_evidence_sha256": null,
    "independent_countermodel_check": false,
    "crossing_candidate_sha256": null,
    "crossing_class": "NONE"
  }
}
```

Theorem yield is exactly `0`, `1/2`, or `1`. A half point requires `SIGNAL`, a
true independent-countermodel flag, and an evidence digest. One point requires
`PROVED` and an evidence digest. Zero permits `NONE` or `RETROSPECTIVE` and no
digest.

A `CROSS` terminal supplies the candidate digest and one of `NOVEL`, `RETRO`,
`AMBIGUOUS`, or `STATUS_PREEMPTED`. It is accepted only when the ledger also
contains exactly two rows with distinct process IDs of this form, both using
the candidate digest as their base `carrier_sha256`:

```json
{
  "arm": "INDEPENDENT_VERIFICATION",
  "score_event": {
    "kind": "INDEPENDENT_VERIFICATION_TERMINAL",
    "candidate_sha256": "<64 hex digits>",
    "result": "VERIFIED"
  }
}
```

## Derived metrics and gates

The scorer derives both multiclass mean Brier scores and skills against the
single frozen development prior. A complete score requires both forecasts for
all twelve clusters. To interpret the protocol's singular positive-skill
requirement conservatively, `PREDICTIVE_SUPPORT` requires both skills to be
positive.

For each arm it reports mean and total normalized gain, exact observed CPU,
gain per CPU-second, and timeout/protocol-invalid counts and rates. Wall versus
each baseline is paired by cluster. Controlling-term accuracy uses the frozen
denominator of preregistered nonzero directions having exact evaluations.

The theorem table reports exact total/mean yield and evidence-class counts.
Crossings stay separated by novelty/status class. `PREDICTIVE_SUPPORT` is true
only when both Brier skills are positive, wall mean gain strictly beats each
baseline, wall paired wins are at least losses against each baseline, and sign
accuracy is at least `7/10`. `DISCOVERY_SUPPORT` additionally requires a
twice-verified crossing whose frozen intervention forecast assigns strictly
more probability to `CROSS` than to `ZERO_COMPLETE`.

Any failed manifest/ledger validation, missing or duplicate terminal record,
inconsistent terminal outcome, unsupported evidence credit, or incomplete
verification aborts scoring. No partial support label is emitted.
