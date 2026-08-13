# Erdős 92 formal-transfer audit

**Classification:** retrospective theorem-transfer benchmark  
**DeepMind commit:** `7a38c469ec329d0c97c068e03c58834f61628e7e`  
**Canonical status commit:** `66dfe4860f73d94ecb1b09b99990a67272b6d16a`

The canonical Erdős Problems database records problem 92 as **disproved** via
problem 90, but DeepMind still contains two `research open` declarations and no
formal solution. This is a status lag and formalization opportunity, not a new
mathematical discovery.

## Exact scope

`FormalConjectures/ErdosProblems/92.lean` contains:

- a weak bound `f(n) <= n^(o(n))`;
- a stronger eventual bound `f(n) <= n^(c / log log n)`.

The official implication from problem 90 uses point sets with polynomially
many unit distances. A graph with sufficiently large average degree has a
nonempty induced core of large minimum degree; all neighbors in the unit-
distance graph are equidistant from their center. The core therefore supplies
a value in `possible_f_values`, giving a fixed-power lower bound for `f` along
an unbounded sequence. That contradicts both proposed subpower upper bounds.

## Duplicate and proof audit

- Merged PR 660 added the statement only.
- Merged PR 4411 proves only `possible_f_values_BddAbove`.
- Closed PR 2973 is an unrelated Pach-Sharir upper-bound stub and proves
  neither declaration.
- No live issue, PR, or exact public formal proof of problem 92 was found.
- Public repository `kim-em/erdos-unit-distance` contains a sorry-free result
  strong enough to feed the **strong** 92 negation, but not the fixed-power
  lower bound needed for the **weak** negation. Its fixed-power statement still
  has a `sorry`, and it uses a newer Lean/toolchain than formal-conjectures.
- DeepMind problem 90's polynomial lower bound also remains unproved in Lean.

## Checked Lean bridge

A 73-line scratch module compiled under the current formal-conjectures
toolchain, establishing the local pieces without changing the repository:

- twice the unordered unit-distance count equals the ordered count;
- membership in `possible_f_values n` implies the value is at most `f n`;
- the finite unit-distance graph on a point set;
- its vertex degree equals the unit-neighbor filter cardinality;
- a unit-distance class is bounded by `maxEquidistantPointsAt`;
- a uniform local unit-degree bound yields membership in
  `possible_f_values`.

## Smallest honest remaining ladder

1. Extract an extremal point set attaining `maxUnitDistances` from the bounded
   natural-number `sSup`.
2. Relate the graph edge count exactly to `unitDistancePairsCount`.
3. Prove the finite peeling lemma that sufficient average degree yields a
   nonempty induced subgraph of prescribed minimum degree.
4. Transport that minimum degree into `possible_f_values` and hence `f`.
5. Complete the power/floor bookkeeping for an unbounded fixed-power lower
   sequence.
6. Prove the two real-asymptotic contradictions.

A conditional theorem

```text
Erdos90.polynomial_lower_bound -> not weak_RHS and not strong_RHS
```

is a realistic bounded formalization project. A fully sorry-free proof of the
weak variant is not currently bounded because its problem-90 fixed-power input
is itself unformalized. The strong variant may be approachable by porting the
external uniform-constant result, but that is integration and formal theorem
work rather than this campaign's finite counterexample loop.

Primary outcome: `STATUS_SYNC` plus a reusable conditional proof architecture.
No solution claim, release, issue, or PR is authorized from this audit.
