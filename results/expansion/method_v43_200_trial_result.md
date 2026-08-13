# WOWII 200 prospective lane: PRIOR_ART_STOP

Date: **2026-08-13 UTC**

Final status: **PRIOR_ART_STOP**

The mandatory database/status gate confirmed an existing counterexample before
any Atlas graph or development-family graph was evaluated. Candidate count is
therefore exactly zero, as required by the frozen contract.

## Exact statement audited

Current upstream
`FormalConjectures/WrittenOnTheWallII/GraphConjecture200.lean` says that a
finite nontrivial connected simple graph satisfying

`(largestInducedTreeSize G : ℝ) = ⌈1 + averageIndepNeighbors G⌉`

has a Hamiltonian path (formalized as a Hamiltonian walk). The local term is
the average of the independence numbers of open neighborhoods. This is the
reading used by the existing counterexample certificate.

The module on upstream `main` still has `@[category research open]` and a
`sorry`; that metadata lag does not make the target unclaimed.

## Prior art confirmed

- The locally preserved live-page audit records #200 as false on 2026-07-21,
  attributed to Jitendra Prajapati, with the 11-vertex encoding
  `J??FFBRq}N_`.
- [Issue #4499](https://github.com/google-deepmind/formal-conjectures/issues/4499)
  is open and has stated the infinite counterexample family since
  2026-07-21 11:03 UTC.
- [PR #4500](https://github.com/google-deepmind/formal-conjectures/pull/4500)
  is open and unmerged. Its commit `f2fd6bdce15e95a6e3506eff6689f6ffc661f18d`
  changes #200 to false and documents the same family and minimum witness.
- The PR links a complete standalone Lean file at commit
  `9dd290db402c49922fa42793e4a7cfb802daf5c1`. Inspection confirms lemmas for
  connectivity, local-independence sum `24`, average `24/11`, largest induced
  tree order `4`, the exact ceiling equality, and nontraceability from three
  distinct pendant vertices.

For the smallest member, `ceil(1 + 24/11) = 4`, matching the certified induced
tree number. Three leaves cannot all be endpoints of one Hamiltonian path.

## Stop-rule accounting

| Stage | Count |
|---|---:|
| Development-family candidates generated | 0 |
| Development-family exact profiles | 0 |
| Atlas profiles | 0 |
| New candidates | 0 |

Atlas was deliberately not run: the frozen contract makes the prior-art audit
the first database gate and prohibits downstream evaluation once a prior
counterexample is confirmed. No commit, push, release, issue, PR, or public
state change was made.
