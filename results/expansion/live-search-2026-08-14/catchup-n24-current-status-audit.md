# Catch-Up `N=24` current-status and novelty audit

**Disposition:** `READ_ONLY_NOT_SELECTED_NOT_EVALUATED`  
**Audit captured:** `2026-08-14T19:25:08Z`  
**Novelty gate:** `PASS_BOUNDED_N24_COMPUTATION_ONLY`

This is a source/status/novelty audit. It does not select the target, evaluate
`N=24`, change the search contract, authorize a public claim, or report a
mathematical result.

## Decisive conclusion

No exact public value or exact public strategy certificate for
`Catch-Up({1, ..., 24})` was located in the official formal-conjectures record,
the primary literature, or the relevant public code/results checked in this
audit. An exact `N=24` computation therefore passes the novelty gate as a
**bounded computation**.

That gate is deliberately narrower than the universal conjecture:

- an exact `draw` at `N=24` would be a new bounded confirmation only;
- an exact `win` or `loss` at `N=24` would refute the universal conjecture,
  subject to independent semantic and certificate replay;
- a timeout or heuristic/MCTS result is neither outcome;
- no result authorizes a universal proof claim unless the theorem for every
  admissible `N` is actually proved.

Negative novelty searches cannot prove global nonexistence. The conclusion is
the strict result of the official-source, primary-literature, and public-code
audit below as of the capture timestamp.

## Exact current formal declaration

At capture time, `google-deepmind/formal-conjectures` `main` was:

- commit [`6c0950bec7743f5098c0196c6aee7b22c1ec8005`](https://github.com/google-deepmind/formal-conjectures/commit/6c0950bec7743f5098c0196c6aee7b22c1ec8005),
  committed `2026-08-14T16:42:13Z`;
- tree `5af0d2a3a319ee2458f8cd061db7c49aeba1b35e`;
- declaration file
  [`FormalConjectures/Paper/CatchUpConjecture.lean`](https://github.com/google-deepmind/formal-conjectures/blob/6c0950bec7743f5098c0196c6aee7b22c1ec8005/FormalConjectures/Paper/CatchUpConjecture.lean);
- Git blob `ce8251a228ea79a6b2f8414e9eb6b5291a640677`;
- raw-file SHA-256
  `7e940f2e37a1794e98fc21454096429da13243669a432b9239743aaf46f1d3c0`.

The exact declaration remains tagged `@[category research open, AMS 11 91]`
and its proof body is `sorry`:

```lean
theorem value_of_even_mul_succ_self_div_two
    (N : ℕ) (h_even : Even (N * (N + 1) / 2)) :
    value (.Icc 1 N) = .draw := by
  sorry
```

This statement is universal in `N`. Since
`24 * (24 + 1) / 2 = 300` is even, `N=24` is one covered instance. Computing
that instance as a draw does not prove the universal statement; computing it
as non-draw supplies the existential witness needed to refute it.

## Primary-literature status

The primary paper is A. Isaksen, M. Ismail, S. J. Brams, and A. Nealen,
*Catch-Up: A Game in Which the Lead Alternates* (2015):

- [author-hosted PDF](https://www.nealen.net/papers/catch-up-a-game-in-which-the-lead-alternates-2015.pdf),
  SHA-256
  `93745c0b55856343ec0c91cfd26bea9cdda167b612e9841d8a5d23c05aba38cb`;
- [MPRA archival record](https://mpra.ub.uni-muenchen.de/108784/), deposited
  `2021-07-15`.

The paper makes two materially different claims:

1. It reports **exact minimax game values through `N=20`** using alpha-beta
   pruning and transposition tables.
2. It reports that Monte Carlo tree search explored `N=23,24,27,28` and found
   no contradiction.

The second claim is heuristic search evidence. It is not an exact `N=24` game
value, a proof that `N=24` is a draw, or an exhaustive strategy certificate.
It therefore does not preempt an exact bounded computation.

A later relevant public source, David Feng's May 2024 College of Staten Island
honors thesis, *Analysis of All the End Game Possibilities in Catch-up*, also
describes the exact-computation frontier as `N=20` and studies positions with
three or four remaining pieces. It does not report an exact `N=24` value:

- [thesis PDF](https://www.math.csi.cuny.edu/Undergraduate/HonorsTheses/2024-feng.pdf),
  SHA-256
  `0aa294c0a1daa9819abb25fee75ddfb734c23fd93c8699bee03ab96ae139cb2f`.

## Official GitHub status and duplicate audit

The formal declaration entered the repository through
[`google-deepmind/formal-conjectures#1325`](https://github.com/google-deepmind/formal-conjectures/pull/1325):

- created `2025-12-02T23:29:40Z`;
- merged `2025-12-22T18:17:12Z`;
- merge commit `d0e60263f9b7302410993db4fa381c85adef7f3a`.

The only current Catch-Up-specific development proposal found was
[`#4834`](https://github.com/google-deepmind/formal-conjectures/issues/4834),
opened `2026-08-07T21:41:05Z` and still open at capture time. Its body
explicitly says that the proposed normalized API claims no new conjecture
case or reduction theorem and excludes exact-search scripts and certificates.
It therefore does not preempt `N=24`.

The audit searched open and closed official issues and pull requests for
`Catch-Up`, `CatchUp`, `CatchUpConjecture`, and `N=24`, and searched public
GitHub code for the exact theorem name plus Catch-Up/`N=24` combinations. No
exact `N=24` value, proof, or strategy certificate was found. Public
FormalConjectures-Bench entries are challenge scaffolding: their bundled
`solve.sh` reports that no licence-reviewed `Target.lean` solution is present.
They are not solutions or bounded computations.

## Existing c5-k4 computation

The prior c5-k4 run is also not an `N=24` result:

- [GitHub Actions run `31721869656`](https://github.com/Kuberwastaken/c5-k4/actions/runs/31721869656);
- [`catchup_n23_n24_report.md`](../catchup_n23_n24_report.md).

That run computed an exact draw for `N=23` after `95,451,689` memo states and
`50.786 s`. The isolated `N=24` job reached at least `112,000,000` memo states
and `985,908,066` calls, then exited at the fixed `60 s` cap without emitting a
result row. Its status is `TIMEOUT_BRACKET`, not draw, win, or loss.

## Gate and disposition rules

The status/novelty gate is **PASS for one exact bounded `N=24` computation**.
It is not a target selection and no evaluation occurred during this audit.

If a later authorized run returns:

| Exact outcome | Required disposition |
|---|---|
| `draw` | Record as a new bounded confirmation. Do not call it a proof of the universal theorem, a disproof, or a conjecture release. |
| `win` or `loss` | Treat as a counterexample candidate only until the exact recurrence, source semantics, and a complete winning-strategy DAG/certificate replay independently. Then perform a fresh same-day duplicate/status audit before any claim. |
| timeout, OOM, partial table, heuristic/MCTS indication | Record only the resource bracket or heuristic evidence. Make no mathematical outcome claim. |

Any future evaluation must freeze the exact source blob, reproduce the
published values through `N=20`, preserve the project's process cap and
incremental-output rules, and distinguish optimized solver output from an
independent semantic replay.
