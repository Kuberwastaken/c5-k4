# Independent review — 2026-08-15

**Reviewer:** external, no stake in the project, instructed to be adversarial.
**Scope read:** `README.md` (all 1,619 lines), `OVERARCHING_PLAN.md`, `METHOD.md`,
`METHOD_V1_6.md`, `METHOD_V1_1..V1_5` records, `UPSTREAM_PROTOCOL.md`, `HANDOFF.md`,
`results/expansion/live-search-2026-08-15/CONFIRMED_LEDGER.md` and
`candidate-verification.md`, `results/expansion/publication/` (both defect-fix batch
records, the KitaKen1 analysis), `results/benchmark/v1.4-f0a/`, wide samples of
`results/expansion/live-search-2026-08-14/` (128 entries, including the Bondy v3.x
invalid-run chain, the A231201 v1–v3 chain, `empirical-loop.md`, and the Graffiti³
C2/C13 results), plus spot-verification of the upstream Lean text for A110854 and
A108864 against the local `formal-conjectures` checkout and independent arithmetic
re-checks of the A108864 witness (8925 = 3·5²·7·17, σ = 17856, deviation 6) and the
A110854 parity argument.

**Context that frames everything below:** the entire git history is four days old —
2,049 commits from 2026-08-12 to 2026-08-15 (1,077 / 613 / 291 / 68 per day). The
campaign itself is ~3.5 weeks old (first kill 2026-07-23). `results/` is 319 MB and
998 files under `results/expansion/` alone; there are 8 protocol documents and 6+
METHOD versions, all written inside those four days. This is machine-generated
throughput regulated by machine-generated process. That is not a criticism by
itself — but it means every judgment below has to ask whether an artifact exists
because the mathematics needed it or because the pipeline emits artifacts at a
fixed rate regardless.

---

## Verdict in one paragraph

This repository contains one genuinely good piece of mathematics-adjacent research
(the C₅[K_m] discretization-cliff case study), one honest and currently productive
QA operation (the formal-corpus faithfulness audit), and one research claim
(prospective tightness navigation) whose evidence base is far thinner than the
program built around it. The small print of the repo is almost always honest; the
large print consistently outruns it. The verification discipline is real and is the
best thing here — it caught six wrong claims in a single day. But six METHOD
versions, five benchmark protocol versions with zero completed measurements, and a
planned KMS/Object-Lock/OIDC evidence chain are process in search of a result. The
single highest-value act available is cheap and has been avoidable-avoided:
actually run the three-arm test on a fresh, uncontaminated population, once, and
let the headline claim live or die.

---

## 1. Is the headline research claim actually supported?

**No — not at the standard the repo itself set. The honest count is n≈4
developmental, n≈1 under frozen protocol, and n=0 held-out.** Broken down:

**Genuine design-before-evaluation crossings (developmental, adaptive era, one
corpus):** three events.

1. **WOWII 181** via T(7)=L(K₇): the `L_s+b` saturation identified `α=λ_max` as the
   obstruction; T(n) was chosen because it achieves `α>λ_max`; evaluation followed.
   Genuinely prospective in the weak sense. Reading-dependent (deg_avg-in-G² parse
   only), and the repo says so.
2. **WOWII 176 → 172** via the barbell family D_L (one event, two conjectures —
   172 fell as an adjacency of the same family, not a second prediction).
3. **WOWII 430a** via the nonuniform P₇ clique blow-up.

All three date to the adaptive 08-12/13 window, before the frozen-contract regime
was operative. They are design-then-test, but not preregistered, and they are
correlated: one corpus (WOWII), one generator (Graffiti.pc), overlapping invariant
families.

**Frozen-regime crossings attributable to wall navigation:** one, with an asterisk
that swallows it. **Graffiti³ Conjecture 2** (DS(11,12)) was found by the frozen
wall-navigation arm in 85 evaluations — and *independently by the plain catalogue
arm in 99 evaluations* (`graffiti3-conjecture2-result.md`). A 25-vertex double star
is exactly what enumerating small trees finds. As measured, the marginal value of
navigation over brute force in the one frozen success is zero.

**Explicitly not transfers, by the repo's own admission:**

- **Graffiti³ Conjecture 13**: "the preregistered separating family stayed safe and
  the catalogue arm found the crossing … **not** a fifth successful wall-navigation
  transfer" (README). Correctly not counted. Good.
- **A113019** (`n = d^r` reduction): the one clean prospective arm win outside
  graphs (`empirical-loop.md`: "Wall navigation won decisively once"). But this is
  a necessary-form reduction — a completely standard technique — not tightness
  transfer. It supports "structured coordinates beat flat search," which nobody
  disputes, not the specific equality-wall claim.
- The README's phrase "**four prospective structural transfers and two prospective
  theorem recoveries**" over-counts: two of its six table rows are no-crossings
  (438b, Bondy), and the Bondy "theorem recovery" is Boyd–Sebő 2017 Lemma 2, i.e. a
  known result recovered — the repo's own prior-art file reclassified it
  `KNOWN_RESULT_RECOVERED`. Counting a rediscovery as a "prospective theorem
  recovery" in the headline table while correcting it three paragraphs later is
  exactly the large-print/small-print pattern.

**The denominator.** I count roughly **80 frozen prospective decisions** across
v0.2 → 2026-08-15 (v0.2: 2; first portfolio: 6; live-core: 4; cross-corpus: ~7;
v0.8: 9; post-v0.8: 6; v0.9/v1.0 rotations: ~10; 2026-08-14 arithmetic rotation:
23 strict stops; txgraffiti-cc ×4, product ×2, energy, C23, solvable, min-modulus,
tan-arctan, G3 ×2: ~11; 08-15: EP982 + triage). Crossings under that regime: the
one asterisked G3-C2. Everywhere the method has been applied under its own
discipline, and everywhere outside its home corpus, it has produced bounded zeros.
`empirical-loop.md` says it plainly: "most other live wall arms produced equality,
bounded zeroes, or worse residuals than the generic baseline," and for Erdős 835
"the unconstrained generic arm was still 14,799 better."

**Held-out evidence: zero, structurally.** Method v1.1 → `NO_ELIGIBLE_BENCHMARK`;
v1.2 → `PROTOCOL_INVALID`; v1.3 → `PROTOCOL_INVALID`; v1.4 → the sole completed
registry build found **0 of 728 clusters eligible** (`v1.4-f0a/`); v1.5 is
"PRE-P1 and non-operational." Five protocol versions, zero measurements. The
maturity milestone in `OVERARCHING_PLAN.md` ("multiple prospective successes in
distinct invariant clusters") has not been met by the plan's own definition.

So: the claim is a live hypothesis with one good case study, currently
accumulating *dis*confirming data in its extended domain (0/23 on 08-14), and it
has never faced the test the repo has spent five protocol versions describing.

---

## 2. Is the process proportionate to the results?

**The verification layer is rigor. The benchmark/freeze apparatus is displacement.
They need to be judged separately.**

**Keep, unambiguously:** the adversarial verification lane (it overturned 6 claims
in one day — see §7 — and is the only thing standing between this pipeline and
publishing garbage); the DB-sanity gate (caught 4 corrupt WOWII statements); exact
recomputation by independent code paths; the no-`sorry` Lean gate for actual
counterexample claims; the CONTESTED hold-back of the seven status-sync rows when
the live source was unreachable (that was the single best judgment call in the
08-15 ledger); METHOD_V1_6 §A2/A3 pre-flight and sign checks (cheap, and validated
3/3 on EP982).

**Cut, specifically:**

1. **The entire Method v1.5 cloud activation chain** — Object Lock/KMS/IAM,
   TLS/OIDC signing, custody receipts, the 24-tree Linux isolation adapter. This is
   evidence infrastructure scaled for a clinical trial, wrapped around an
   experiment that has never selected a single target. v1.4 already shipped a
   101,190,589-byte provenance inventory through Git LFS **for a run that measured
   nothing**. A held-out test needs a tagged commit, a hash, a frozen script, and a
   public timestamp. That is one page, not five protocol documents.
2. **The Bondy v3.x continuity-gate saga** — six gate versions (v3 → v3.5), five
   invalid runs failing on GitHub REST response shapes, PR-snapshot timeouts, and
   toolchain-prefix models, to evaluate 96 graphs that were then closed
   symbolically by a lemma published in 2017. METHOD_V1_6's own accounting: 6 of
   the 23 stops on 08-14 were `INVALID_PRE_EVALUATION_*` — "full setup cost, zero
   mathematical information." When the gate has more versions than the target has
   evaluations, the gate has become the project.
3. **METHOD version proliferation** — v0.1 through v1.6 plus a separate empirical
   selector, versioned faster than evidence accumulates (ten versions in four
   days). Fold into one METHOD.md with a changelog. A method that changes daily is
   not yet a method; it is a lab notebook wearing a standards document's clothes.
4. **One-problem GitHub releases for formalization defects.** The 08-15 ledger
   itself says the right artifact for defect findings is an upstream issue. The
   release machinery (tag gates, immutable-link gates, readback confirmation) is
   appropriate for the four real counterexample releases and theater for the rest.
5. **The 1,619-line README.** It is a run journal impersonating a front page, and
   it is where the claim inflation lives (§1). 150 lines of README; move the
   journal to a RESULTS index.

The tell for displacement is simple: over 08-13→08-15, the ratio of
infrastructure-iteration commits to new mathematical facts is enormous, and the
repo's own yield table (METHOD_V1_6 §A1) shows the published results came
"overwhelmingly from a vein the 2026-08-14 lane was not working" — i.e., the
apparatus was pointed away from the yield for a full day and the response was to
write a seventh method document rather than ask why the apparatus keeps growing.

---

## 3. Which program is worth continuing?

**(b), the corpus audit, is what actually works today — but it is QA labour on a
depleting, contested vein, and it should be run as such: hard, fast, and with an
explicit end date. (a) is the only research claim, and it deserves exactly one
decisive test before any further investment.**

Evidence that (b) is real: 2 verified formalization counterexamples (A110854 d=3;
A108864 n=67 — both spot-checked by this review against the upstream Lean text and
independently re-derived arithmetic), 9 defect filings with minimal witnesses and
suggested repairs, provenance forensics of genuine quality (Erdős 1093's bug
introduced by a review suggestion on PR #1328; Erdős 477's docstring/code
contradiction from #1242 vs #1510).

Evidence that (b) depletes: the complete triage of all 603 open ErdosProblems
declarations classified **575 as not finitely refutable**; after the first two
crossings, 19 depth targets and 61 OEIS files produced **zero** more. The vein
substantially emptied within one day of mining it. And it is contested:
KitaKen1 entered OEIS on 08-13 and is consuming ~11 targets/day at 2.4–4.8 h merge
latency; williamjblair has 50 merged PRs since 08-01; this project has **0 merged
of 8** (its own `kitaken1-activity-analysis.md`, §7). Upstream PR #4964 took
A103425 mid-triage on 08-15. Worse for the long run: the defect classes are
patternable, mo271 is already writing linters, and every class this project or
KitaKen1 documents publicly makes the next automated sweep cheaper for everyone —
(b) is self-extinguishing by design.

Is (b) a research program? No. It is excellent QA with one paper-shaped residue
(§6). Does it deplete the project? Yes, doubly: it consumes the verification
lane's scarce capacity (the actual bottleneck, §7), and it feeds the racing
incentive that produced today's two post-publication retractions.

---

## 4. The single highest-value next thing

**Run the preregistered three-arm test on a freshly generated conjecture
population, within two weeks, at one-page-protocol weight.** v1.4 proved the
locally accumulated corpus can never serve as held-out (0/728). v1.5's answer —
wait for future upstream cohorts under cloud-custody infrastructure — is the
expensive road to the same place. There is a cheap road:

- **Population:** machine-generated graph-invariant conjectures that did not exist
  at freeze time. Two admissible sources, in order of preference: (1) run a public
  generator (TxGraffiti/Optimist is public and runnable) against its own standard
  database to emit a fresh batch of conjectures on the project's invariant
  vocabulary; (2) the next public release from an active generator lineage
  (Graffiti³-style) or any `formal-conjectures` graph cohort merged after the
  freeze commit. Source (1) is unlimited and contamination-proof by construction.
- **Freeze protocol:** one commit, publicly tagged before the population exists,
  containing: the three arm implementations, the invariant library, the catalogue
  database, per-target budget, the analysis script, and this success criterion
  verbatim. Population is generated/fetched only after the tag is pushed. Reuse
  v1.4's S0 exclusion replay to certify no target overlaps any prior repo file.
- **Sampling:** all eligible finite-universal conjectures from the batch, capped
  at 30 by public randomness if more. Eligibility by the existing Phase 0A
  resolution-card rules, applied mechanically.
- **Arms, equal budget (1 CPU-hour/target each):** (1) *catalogue* — fixed
  ≤10-vertex atlas plus ~50 named families, no adaptation; (2) *generic* — random
  construction search; (3) *wall navigation* — the METHOD pipeline: find equality
  witnesses, extract the obstruction identity, build the separating family.
- **Primary endpoint:** unique crossings — counterexamples found by arm 3 and
  missed by both baselines within budget.
- **Success criterion (state before running):** arm 3 produces ≥3 unique crossings
  across ≥20 evaluable targets AND total arm-3 crossings ≥ total arm-1 crossings.
- **Falsification:** arm-3 uniques ≤ arm-1 uniques, or zero arm-3 uniques. Publish
  the result either way, one run, no retries, no post-hoc re-scoring. A
  falsification here means the honest summary of this project becomes "one graph,
  one cliff, one good paper" — which is fine, and citable.

Everything needed already exists in the repo except the willingness to run it at
this weight. Estimated cost: days.

---

## 5. What should be abandoned

Named, in descending order of savings:

1. **Method v1.5 benchmark infrastructure** (the whole activation chain:
   Object Lock/KMS/IAM, TLS/OIDC, custody receipts, P1A/P1T/P1R). Superseded by §4.
2. **The Bondy lane** — already `DOMAIN_EXHAUSTED` + theorem-closed + prior-arted;
   also its v3.x gate framework as a pattern. Do not port it to the next arm.
3. **A231201 and the OEIS residue-cover/CP-SAT genre.** Six versions produced, in
   the repo's own words, "negligible evidence about either conjecture or the
   search method." The periodic-cover impossibility theorem was the one real
   output and it says *stop*. It is currently "paused"; make it terminal.
4. **Arithmetic "wall navigation" generally** (A063880, A067720, A108569,
   A105720-class lanes). The mechanism behind the graph successes — pinned
   hereditary invariants vs. freely growing correction terms past a finite
   verification horizon — has no analogue in these targets; "equality wall" there
   means only "the known solution is the known solution." Twelve consecutive
   bounded zeros are the data. Band-1 auditing of these files is fine; band-4
   surgery on them is vocabulary transplanted without the mechanism.
5. **Competitor dossier maintenance.** The KitaKen1 analysis was worth doing
   once — its packaging delta (§7 of that file) is genuinely actionable. Standing
   surveillance of another contributor's daily cadence is displacement, and the
   race framing it feeds caused measurable harm today (§7).
6. **Per-defect GitHub releases; the 1,619-line README; `graphify-out/` in-repo;
   worktree-sync commit noise.** Hygiene, not strategy.
7. **The daily METHOD version.** Freeze METHOD until after the §4 test; the next
   version number should be earned by that result.

Explicitly *not* abandoned: WOWII/Graffiti³ finite-refutation work (band 2 —
still the best per-unit yield), the verification lane, the Lean certificate gates,
and maintenance of the 16-odd open upstream PRs until decided.

---

## 6. Is there a genuinely novel intellectual contribution?

**Yes — one, plus a half.**

**The one: the discretization-cliff case study.** A single vertex-transitive
20-vertex graph family where hereditary induced invariants pin at constants
(α=2, f=b=tree=4) while distance/parity/density terms grow linearly, producing
*simultaneous exact equality at m=3 and violation at every m≥4* across many
independent machine-generated bounds — with the analytic explanation, the
exhaustive verification that the generator's own database satisfies every claimed
reading, and the demonstrated transfer anecdotes (181 via T(n); 176/172 via
barbells; 430a via nonuniform blow-ups). This is a precise, replicated mechanism
for *why* finite-database conjecture generators fail just past their verification
horizon, and "equality at the database edge is the signature of an impending
cliff" is a portable, testable heuristic. Nobody has written this up properly.
**Where:** a 10–15 page paper for the automated-conjecturing community —
Experimental Mathematics, Discrete Applied Mathematics, or the venues the
Graffiti/TxGraffiti lineage publishes in — with the transfers honestly labelled
n≈4 developmental. **For whom:** Davila, Larson, DeLaViña's community on the
generation side; the formal-conjectures/benchmark-curation community on the
evaluation side.

**The half: formal-corpus defect forensics.** The four-coordinate status
discipline (METHOD_V1_6 §A6) and the provenance work (a review suggestion
injecting the 1093 threshold bug; the 477 two-PR docstring/code divergence; the
A108864 index-set root-cause via re-implementing A109883) are craft of real
quality — but the defect *taxonomy* (vacuous hypotheses, junk-value carriers,
reflexive answers) is contemporaneously and publicly shared with KitaKen1's
trackers #4896/#4923, so there is no priority claim on the genre. Worth a short
experience-report at an AITP/ITP-adjacent workshop on QA of AI-populated formal
corpora; not more.

**The tightness-navigation method itself is not yet a contribution.** It is a
hypothesis with one good case study and a pending test.

---

## 7. Failure modes the project cannot see about itself

The 6-overturned-claims day is the key datum. The six: Erdős 1084 ("finitely
false as stated" — actually a docstring-only defect over a true Harborth
theorem), Erdős 931 ("closed interval trivialises" — refuted by 280/280
premise-satisfying tuples), the EP982 false crossing (R=−2 from a degenerate
orbit collapse violating the declaration's own injectivity hypothesis), a
float-guard miscount in the same lane, and — **after publication** — issue
#4978's witness (the `A = ℕ` limsup elaborates in ℝ and junk-values to 0, so the
claimed trivialisation is false) and issue #4977's suggested repair (the
`IsGreatest` wrapper is itself closable in two `fun`s). What this implies:

1. **The generation lane's interior error rate is ~40%+.** Five inherited
   candidates went to adversarial review; two died. Of eight published issues,
   one needed a retraction comment and one a repair-of-the-repair within hours.
   Any ledger line that has not been adversarially replayed should carry roughly
   that prior — which means the many "confirmed" rows in older lanes that
   predate the permanent verification lane are softer than the repo treats them.
2. **Claims amplify as they travel inward.** `candidate-verification.md`
   documents it precisely: the 1084 lane report said docstring-only; the summary
   handed to the next lane said "FINITELY FALSE AS STATED." The same gradient —
   accurate small print, inflated large print — is visible between the README's
   headline table and its own corrections three paragraphs later (§1). A
   pipeline that summarizes itself repeatedly will Chinese-whisper its own
   results; nothing in the current process re-checks *summaries* against
   *sources*, only claims against mathematics.
3. **The race framing caused today's retractions.** The ledger's timing-risk
   section instructs "treat any delay before writing as a real risk of losing
   priority." Eight issues were then filed same-day; two needed public
   correction. The competitor analysis and the retractions sit in the same
   directory, written the same day, and no document connects them. The
   verification lane is permanent; the *pacing* decision that overwhelms it is
   never examined.
4. **Verification is the bottleneck and generation sets the cadence.** That is
   the wrong coupling and it will not fix itself, because throughput is the
   pipeline's implicit fitness function — visible in the outcome taxonomy
   ("bounded zero," "strict stop," "theorem shadow") that converts every
   non-result into a countable, commit-worthy product. 23 stops in a day reads
   internally as discipline; it is zero yield plus 23 units of ledger.
5. **Infrastructure sunk-cost loops.** Bondy v3→v3.5, A231201 v1→v3, benchmark
   v1.1→v1.5: when a run fails, the apparatus gets a new version; whether the
   *target* still deserves apparatus is asked late or never.
6. **No external mathematical contact with the actual claim.** Every validation
   is internal (own verifiers, own Lean certs) or upstream-mechanical (defect
   PRs). Gebendorfer engaged the *carrier*; maintainers engage the *defects*.
   No mathematician has ever looked at the navigation claim. For a project whose
   stated completion condition is auditability, the absence of a single outside
   auditor of the central claim after 2,050 commits is the largest unexamined
   risk.
7. **Scope migration under yield pressure.** The 08-15 "operator-directed"
   amendment pointed the queue at OEIS/Erdős, where band-1 auditing pays daily
   and band-4 navigation has produced twelve straight zeros. The program is
   becoming its own bug hunt while retaining the research program's vocabulary.
   Unchecked, in a month the claim will be something the repo *says* while the
   audit is what it *does* — and the claim will have expired untested rather
   than falsified.

---

## 8. Is there a credible path to a real discovery program?

**Numbers, then reasoning.**

- P(the §4 preregistered test, run fairly on a fresh machine-generated graph
  corpus, shows the wall arm materially beating both baselines): **~25–30%.**
- P(this line ever produces a counterexample or theorem that mathematicians
  outside the automated-conjecturing niche care about): **~5%.**
- P(the corpus-audit lane still yields ≥1 publishable defect/week in 3 months):
  **~20%** (depletion measured on 08-15 + two faster competitors + upstream
  linters closing the classes).

Reasoning for the 25–30%: the mechanism is real but narrow. It operates exactly
when a generator's verification database undersamples a family direction that
tightness data points along — the C₅[K_m] cliff is a bona fide instance, and
machine corpora are soft enough that the regime plausibly recurs. Against it: the
only frozen-era success was matched by its own brute-force baseline at comparable
cost; `empirical-loop.md` records generic arms beating wall arms where they
competed; the natural competing hypothesis — "machine conjecture corpora are so
under-verified that *any* systematic search kills at this rate, and tightness
adds mainly narrative" — is consistent with every observation to date, including
Gebendorfer independently killing two conjectures with the same carrier within
days of its publication.

So: **today this is a well-run bug hunt with one genuinely good idea and an
aspirational framing.** The path to a discovery program exists and is short — it
runs through the §4 test and the §6 paper, in that order — but the current
trajectory (more method versions, more infrastructure, deeper into arithmetic
QA) walks past it. The failure mode to fear is not falsification; it is the
claim quietly expiring untested underneath an ever-better-documented audit
operation.

---

## Strongest single recommendation

**Freeze METHOD, cancel the v1.5 infrastructure, and run the fresh-generation
three-arm test (§4) within two weeks at one-page-protocol weight — then write
the discretization-cliff paper with whatever the test returns.** If the wall arm
wins, the program has its first real evidence and the paper has a spine. If it
loses, the honest product is still substantial: one graph, one cliff mechanism,
four developmental transfers, two formalization counterexamples, and the best
verification discipline in this niche. Either outcome beats a seventh method
version.
