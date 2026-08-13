# Method v0.4 WOWII 179 trial

Status: **TIMEOUT_BRACKET — DATABASE GATE DID NOT PASS**

The trial used the target, residual, controls, family, bounds, and stop rules
frozen at commit `2265037bef0d806995c4f0d3c4a01ae9d2270f43`. It did not evaluate
the private-neighborhood split-clique grid.

## Mandatory database gate

The primary gate wrote 1,042 consecutive `OK` graph records (indices 0--1041)
before `T(7)` at index 1042 reached the internal 55-second deadline. The
timeout was durably recorded as `TIMEOUT_BRACKET`; the coordinator then wrote
`gate_stop` and did not run the remaining 14 controls. No cap was enlarged and
the timed-out graph was not rerun.

Among the 1,042 completed primary rows:

- all certificates validated in-process;
- every exact identity `R179 = T173 - Q179` held;
- all `T173` values were nonnegative;
- all required completed complete/star controls had residual zero;
- there were zero crossings and zero non-timeout gate failures;
- the residual range was 0 through 14, with 470 zero rows;
- the slowest completed row was `C5[K8]` at 23.449572 seconds.

The order-two control follows the source convention frozen in the selection:
`L_s(K2)=1`, represented by a rooted spanning-tree leaf certificate. This is
the convention required for the selection's asserted `K_n` equality for every
`n>=2`.

Every graph was a fresh externally supervised process under GNU `timeout 60s`.
The worker installed a 55-second alarm and passed a 55-second limit to each
HiGHS optimization. Rows were appended and `fsync`ed individually to
`method_v04_179_trial.jsonl`.

## Independent replay

The independent verifier first checked each serialized spanning tree,
induced-bipartite set, dominating set, and neighborhood independent set. It
then recomputed the optima with CBC/PuLP. In particular, it used minimum
connected domination for `L_s`, whereas discovery used a direct maximum-leaf
spanning-tree formulation.

Rows 0--1037 (1,038 rows) passed certificate validation and exact independent
recomputation. The independent process for `C5[K5]` at index 1038 then reached
its own internal 55-second deadline and was recorded as `TIMEOUT_BRACKET`.
The independent replay stopped without a rerun. Thus this report does not
claim independent agreement for primary rows 1038--1041.

## Pre-grid family identity

During the gate, before any prospective-family graph was evaluated, a
structural derivation settled the direction of the frozen family. This is
recorded as `PRE-GRID_FAMILY_IDENTITY`, not as a completed trial outcome.

For `H(p; a)` let `A=sum_i a_i` and `M=max_i a_i`. Then:

```text
gamma_c = s,       L_s = p+A-s,
b = A+2,           Delta = p-1+M,
gamma = s,         lambda_max = M+1.
```

For connected domination, every active private block forces its hub into a
connected dominating set: including private vertices without their hub cannot
connect them to the rest of the set. The `s` active hubs themselves form a
connected dominating set. Hence `gamma_c=s` and `L_s=p+A-s`.

All private vertices together with any two hubs induce a bipartite graph, so
`b>=A+2`; three hubs induce a triangle, while omitting hubs cannot improve on
retaining all `A` private vertices, so `b=A+2`. For ordinary domination,
omitting an active hub requires selecting its entire positive private block;
minimizing this choice gives `gamma=s`. A largest active hub has degree
`p-1+M`, and its neighborhood contains an independent set consisting of its
`M` private vertices and one other hub; no larger neighborhood independent set
is possible. Thus `lambda_max=M+1`.

Substitution gives

```text
R179(H(p;a)) = 2*(A-M-(s-1)) >= 0,
```

because all nonmaximum block sizes are positive integers. Equality holds
exactly when every nonmaximum block has size one. This proof covers the frozen
grid (indeed, the whole declared positive-block family), but the mandatory
gate timeout prevents classifying the trial itself as a theorem shadow or
bounded hold.

## Outcome and artifacts

Primary outcome: `TIMEOUT_BRACKET`. The gate did not pass, so there are exactly
zero `grid` rows. No theorem, counterexample, novelty, minimality, upstream, or
release claim follows.

Artifacts:

- `scripts/method_v04_179_trial.py`: frozen manifest, per-graph worker, exact
  primary solvers, incremental coordinator, and gate lock;
- `scripts/verify_method_v04_179_trial.py`: independent certificate and
  CBC/PuLP ledger verifier;
- `results/expansion/method_v04_179_trial.jsonl`: primary incremental ledger;
- `results/expansion/method_v04_179_trial.verify.jsonl`: independent replay.

No process from this trial remained alive after the stopped primary and
independent runs. No commit, push, tag, release, issue, pull request, web
search, upstream write, or README change was performed.
