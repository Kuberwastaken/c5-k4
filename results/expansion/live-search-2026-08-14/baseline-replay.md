# Baseline replay / calibration — 2026-08-14

Status: **empirical calibration only; not a Method v1.1 confirmatory run**  
Run window: **2026-08-14T06:09:36Z–06:13Z**  
Outcome: **no candidate crossing**

## Scope and target sample

This replay asked a deliberately practical question: what do the best existing
catalogue-like search scripts and a literal implementation of the frozen
generic graph grammar find in one real 8×60-second budget on a small sample of
currently open DeepMind declarations?

The sample was selected before running the arms from the current finite-graph
inventory and existing executable coverage. It is not random and is not a
benchmark sample. The inclusion rule was: current upstream `research open`
declaration, exact finite evaluator already present, and one representative of
three materially different evaluator costs.

| target | upstream declaration | reason for inclusion | exact objective |
|---|---|---|---|
| WOWII 19 | `WrittenOnTheWallII/GraphConjecture19.lean:conjecture19` | induced-subset optimization plus metric term; strongest existing dense catalogue | `R19 = b - maxLocalAlpha - floor(avgEcc)`; crossing iff `R19 < 0` |
| WOWII 160 | `WrittenOnTheWallII/160.lean:conjecture160` | spanning-tree/connected-domination evaluator and an active structural hypothesis | on C4-free graphs, `R160 = Ls - maxL - maxT`; crossing iff negative |
| WOWII 198a | `WrittenOnTheWallII/GraphConjecture198a.lean:conjecture198a` | implication with rare antecedent and Hamiltonian-path decision | among connected nontraceable graphs, `R198a = b*n - (2*n + sumEcc)`; crossing iff nonpositive |

Live upstream was read without modifying either repository. At upstream `main`
`b33d8678a28118c95d8d4f60b11faaf39ccff1e6` (queried 2026-08-14), all three
files still contain `@[category research open, AMS 5]` and `sorry`. They are
open declarations but poor novelty targets: proof PRs #4559 (19), #4576 (160),
and #4597 (198a) are all still open and unmerged. Thus a crossing would have
required a priority/proof reconciliation even before a novelty claim.

Excluded from all commands: `lean/SnakeInTheBoxNine191.lean`.

## Frozen references and what was actually replayed

Method v1.1 says CATALOGUE and GENERIC each receive eight process trees capped
at 60 seconds, but it does not ship an evaluator-independent baseline search
driver. The later frozen library remains a prose/data contract. The relevant
digests at replay time were:

```text
d39552027fc9f0ffec2281920843bf4bd107a2a02dd1bb058c26ab06f2a2fbbd  results/benchmark/v1.4-protocol/baseline-library.json
7fde0ed75b9bbb1cc1d8dc4406d51d4f6ca83607b6f7318c3fd55100ed210068  scripts/run_benchmark_v11_job.py
3a00a57d7c456f660c03bf7a6173153ed456be652eeadcc7a2d9fdc3c1d65836  scripts/method_v44_19_dense_trial.py
0fe2240da4fdc176dd44e81ddad387d536d69522e5c424bb1df036249287a63a  scripts/method_v42_160_trial.py
11d03341751135c9944eeaa22ee19b8e5594b016ebb756e54bf64739043b7b95  scripts/method_v41_198a_trial.py
```

Consequently the labels below are operational:

- **CATALOGUE-like** means replaying the strongest existing deterministic
  named/family enumeration for that evaluator. These scripts contain
  target-specific families and therefore are not valid isolated CATALOGUE
  arms under Method v1.1.
- **GENERIC calibration** means eight deterministic process trees using only
  uniform `G(n,p)` proposals and untargeted single-edge add/delete mutations,
  with no residual or controlling-term input. This follows two entries of the
  frozen graph grammar, but the missing production driver forced an inline
  harness, so it too is not a confirmatory frozen arm.

## Invocations and budgets

Python was `/home/ec2-user/.venvs/wowii/bin/python`. Every process was wrapped
externally as:

```text
timeout --signal=TERM --kill-after=5s 60s /usr/bin/time \
  -f 'RESOURCE wall=%e user=%U sys=%S rss_kb=%M exit=%x' -- <argv>
```

Catalogue-like invocations (one existing deterministic script per target):

```text
python scripts/method_v44_19_dense_trial.py family
python scripts/method_v42_160_trial.py
python scripts/method_v41_198a_trial.py
```

The generic invocation was the same inline Python program with arguments
`<target> <process-index>` for process indices 0–7. Its exact schedule was:

1. seed = first 64 bits, big endian, of
   `SHA256("baseline-replay|" + target + "|" + process_index)`;
2. round-robin orders 8–11 (19), 7–10 (160), and 8–14 (198a);
3. round-robin probabilities 0.18, 0.32, 0.50, 0.68;
4. alternate a fresh `nx.gnp_random_graph` proposal with a uniformly chosen
   single-edge toggle of the last graph in the same `(n,p)` stream;
5. reject disconnected graphs, then apply the target's existing exact
   evaluator; stop proposing at 55 monotonic seconds so serialization can
   finish below the external 60-second cap.

The eight seeds, in process order, were:

```text
19:   4678307548621680437, 11520549151215336246, 1386049066027439404,
      3689018560019607464, 2406987866943941853, 7765388005174956741,
      1782640792302878504, 14377824879952165689
160:  513527607019527148, 6018369670473558360, 16915851087807544660,
      10606713344240494172, 8447453265375252737, 10396629046585438472,
      5626744870319413017, 14540007560805201172
198a: 17682376699837393436, 1289079071982621128, 10767664877635871905,
      8293056615456373898, 4041069049623637908, 1688880077031319001,
      1175878202809999204, 9296547989175337007
```

Each generic target therefore received the protocol-shaped budget of eight
60-second process caps (480 wall/CPU-second upper bound). Processes actually
proposed for 55 seconds. The catalogue-like replay used one 60-second process
per target because the existing scripts are single-process programs and
repeat deterministically; running eight identical copies would add no search
coverage.

## Outcomes

### Catalogue-like replay

| target | exit / resources | generated and evaluated | crossing | closest useful signal |
|---|---|---:|---:|---|
| 19 | exit 0; 51.34 s wall, 48.66 s user, 136,100 KiB RSS | 8,000 generated; first 2,000 exact | 0 | 481 equality objects; minimum `R19=0` |
| 160 | exit 0; 3.33 s wall, 3.09 s user, 36,868 KiB RSS | 144 generated; 89 connected C4-free exact | 0 | 51 equality objects; minimum `R160=0` |
| 198a | exit 0; 47.68 s wall, 45.07 s user, 68,620 KiB RSS | 343 generated; 79 connected nontraceable exact | 0 | claw misses antecedent by `1/4`: `16 > 15` after multiplying by `n` |

These reproduce the recorded expansion reports byte-for-semantics: no new
result appeared. They also show radically unequal useful work under the same
nominal cap: 2,000 profiles, 89 profiles, and 79 rare-antecedent profiles.

### Generic calibration, eight process trees per target

| target | total proposals | connected / post-first-filter count | crossings | best score | measured resources summed over 8 trees |
|---|---:|---:|---:|---:|---|
| 19 | 38,177 | 31,297 connected exact profiles | 0 | `R19=0` | 443.51 s wall; 224.46 s user; 1.11 s system |
| 160 | 151,702 | 121,338 connected profiles before C4-free rejection | 0 | best scored C4-free `R160=0` | 445.84 s wall; 247.23 s user; 1.18 s system |
| 198a | 14,262 | 1,170 connected nontraceable exact profiles | 0 | `R198a=5`, i.e. antecedent miss `5/8` | 443.64 s wall; 308.13 s user; 1.43 s system |

All 24 generic processes exited zero. Observed per-process elapsed ranges were
55.00–55.08 s (19), 55.00–55.00 s (160), and 55.00–55.15 s (198a). No external
timeout fired.

Best generic witnesses were near-wall controls, not candidates:

- 19: graph6 `G[xf__`, `n=8,m=13`, `b=6`, `maxLocalAlpha=3`,
  `floor(avgEcc)=3`, hence exact equality `6=3+3`.
- 160: graph6 `FPOJ?`, `n=7,m=6`, C4-free, `Ls=3`, `maxL=3`,
  `maxT=0`, hence exact equality.
- 198a: graph6 `GN?SCS`, `n=8,m=9`, nontraceable, `b=6`,
  `sumEcc=27`; the required cross-product is `48 <= 43`, so it misses by
  5 (equivalently `5/8` before multiplying by `n`). The catalogue claw is
  substantially closer.

No candidate triggered independent verification or a candidate-specific
upstream audit.

## What the baselines find and miss

1. **Equality is easy; directional escape is not.** Both arms repeatedly hit
   exact equality for 19 and 160. Generic random search did not improve on the
   deterministic catalogue minimum in either case.
2. **Rare antecedents dominate implication searches.** Only 1,170/14,262
   generic 198a proposals (8.2%) were connected and nontraceable, and none was
   as close as the four-vertex claw already in the catalogue. Uniform random
   graphs mostly spend exact-evaluator budget on traceable objects.
3. **Named small controls matter.** The catalogue beats 440 seconds of generic
   wall budget on 198a because it includes the claw. This is precisely the
   benefit a canonical catalogue should preserve.
4. **The current catalogue-like programs are actually intervention searches.**
   The 19 script enumerates line graphs, complements, blow-ups, joins, and
   perturbations; 160 enumerates a target-designed C4-free block/cactus
   grammar; 198a enumerates target-designed blow-ups and sparse cuts. Their
   negative results cannot be used as isolated CATALOGUE-arm observations.
5. **Random throughput is not comparable across targets.** Proposal counts
   differ by more than 10× and useful filtered counts by more than 100×. Raw
   graph count is therefore a misleading equal-budget metric; CPU-normalized
   evaluated-object and hypothesis-survivor counts are required alongside
   objective gain.

## Runner and search defects exposed

1. **There is no production CATALOGUE or GENERIC search executable.**
   `run_benchmark_v11_job.py` explicitly says it is only an orchestration
   layer. `baseline-library.json` defines families and operation grammar in
   prose but supplies no canonical encoder, size ceiling, evaluator adapter,
   seed scheduler, or result schema. A content-addressed contract can launch a
   command, but the repository currently has no command that realizes these
   two arms for an arbitrary selected graph target.
2. **Existing “best” scripts violate baseline isolation.** They encode
   target-specific families selected from wall reasoning. Reusing them under a
   CATALOGUE label would leak intervention information and invalidate the arm.
3. **Canonicalization is not sound or shared.** The 160 script deduplicates on
   `(n,m,WL-hash)`, which can merge nonisomorphic graphs. The 198a script uses
   only WL hash. The 19 script adds a graph6 encoding after integer relabeling,
   but that encoding is labeling-dependent rather than an isomorphism
   canonical form. None implements the frozen “reject duplicate canonical
   encodings without replacement-budget credit” rule.
4. **Output is buffered until termination.** The catalogue scripts print their
   scientific result only at the end. The 19 and 198a runs used 51.34 and
   47.68 of 60 seconds and had zero stdout while running. A timeout, wrapper
   overhead, or slightly slower host would preserve no evaluated prefix and no
   best-so-far row. The inline generic harness had the same defect.
5. **Useful-work counters are inconsistent.** In this replay the 160 generic
   harness counted connected graphs before C4-free rejection; the existing
   scripts variously report generated, exact, nontraceable, or active-branch
   counts. A shared schema must distinguish `proposed`, `canonical_unique`,
   `hypothesis_survivor`, `exact_evaluated`, and `objective_scored`.
6. **The generic schedule is underspecified for implementation.** “Round-robin
   increasing encoded size” does not freeze graph order ceilings, density
   schedule, mutation parent policy, restart policy, or allocation among the
   four graph operations. Those choices can change results by orders of
   magnitude while still sounding compliant.
7. **The exact evaluators are the bottleneck and have no cost-aware static
   allocation.** 19 spends descending subset enumeration twice; 160 enumerates
   connected dominating sets; 198a combines Hamiltonian subset DP with induced
   bipartite deletion. Equal time is enforced, but the frozen contracts need a
   pre-result schedule of size bands suited to evaluator complexity or most
   large proposals will never be reached.
8. **The runner records execution, not scientific semantics.** It does not
   validate result JSON, canonical candidate identities, proposal counts,
   objective direction, hypothesis filtering, incremental checkpoints, or the
   requirement to continue after a crossing. A zero-exit process that emits no
   parseable result is not rejected as a scientific orchestration failure.

## Concrete improvements before a live baseline campaign

1. Add one versioned graph baseline driver with subcommands `catalogue` and
   `generic`, a shared evaluator plug-in interface, canonical graph labeling
   (nauty/Traces or an equivalently exact method), and JSONL output.
2. Freeze per-target order ceilings and the complete generic allocation table:
   sizes, densities, operation proportions, mutation-parent/restart policy,
   and eight seeds. Store these as data, not prose.
3. Emit an append-only row after every fixed number of exact evaluations and
   flush it. Include elapsed/user CPU, all five useful-work counters, canonical
   graph digest, exact residual, and best-so-far digest. A 60-second kill must
   leave a valid prefix.
4. Add a result linter to the runner. Require a terminal summary or a valid
   timeout prefix; independently recompute counts/digests; reject malformed or
   empty zero-exit output; enforce that all eight trees ran and that no process
   silently changed evaluator semantics.
5. Separate named catalogue families from target-designed constructions. For
   this sample, paths/cycles/complete/bipartite/stars/wheels/Petersen/line
   graphs of complete graphs and the fixed cycle blow-ups may enter CATALOGUE;
   dense complement/join perturbations, C4-free cactus grammars, and sparse-cut
   blowups remain wall/intervention material unless they were frozen globally
   before target selection.
6. Report both CPU-normalized residual gain and CPU-normalized
   hypothesis-survivor throughput. For implication targets such as 198a, add a
   frozen generic rejection/conditioning rule that remains target-wall-blind
   (for example, generate from a globally fixed nontraceable catalogue) rather
   than spending most proposals on objects that fail the conclusion test.
7. Put a two-second serialization/checkpoint reserve inside every 60-second
   process contract and test the kill path. The external cap remains exactly
   60 seconds; the worker deadline should be monotonic and earlier.

## Calibration verdict

The empirical result is a three-way **baseline bounded hold**, with exact
equality signals for 19 and 160 and no candidate for 198a. More importantly,
the replay shows that the present repository cannot yet execute the frozen
CATALOGUE/GENERIC distinction faithfully: it has a strong execution envelope
and several exact target evaluators, but no shared canonical baseline search
runtime joining the two. The next useful work is therefore the baseline driver
and result contract above, not another target-specific family replay.
