# Sidorenko homomorphism-density declaration — Phase 0 source/status contract

Frozen: **2026-08-13 UTC**
Scope: **Phase 0 only; no pattern/host pair was evaluated**

## Exact current source

- Repository: `google-deepmind/formal-conjectures`.
- Refreshed commit: `d16e05aded22b8c467a0a27c14b2311f53185006`.
- File: `FormalConjectures/Wikipedia/SidorenkoConjecture.lean`.
- File blob: `872b7fc20702f8ea0b5e40a3b7062648d1aeb153`.
- File SHA-256: `0dc7172a28c2bc3257bb2c2aefea00b9446a1ee90d89a40eefa17c368e9f4c4d`.
- Declaration: `SidorenkoConjecture.sidorenko_conjecture`.
- Category: `@[category research open, AMS 5]`.
- Immutable source URL:
  `https://github.com/google-deepmind/formal-conjectures/blob/d16e05aded22b8c467a0a27c14b2311f53185006/FormalConjectures/Wikipedia/SidorenkoConjecture.lean#L55-L62`.
- Imported density definition blob:
  `de362e1c823f812e5a5a9907be80cc6f4af3ba1e`.

The current Lean declaration is

```text
forall finite simple H and G with a nonempty host vertex type,
  H.IsBipartite ->
  homDensity K2 G ^ |E(H)| <= homDensity H G.
```

The quantifier orientation is exact:

- `H` is the finite bipartite **pattern**;
- `G` is the arbitrary finite nonempty **host**;
- `homDensity H G = homCount H G / |V(G)|^|V(H)|`;
- `homCount H G` counts all graph homomorphisms, not injective copies.

Classification: **`UNAMBIGUOUS`**. The declaration agrees with the standard
finite homomorphism-density formulation. There is no competing source reading
analogous to the WOWII 181 degree-location ambiguity.

For `h = |V(H)|`, `e = |E(H)|`, `N = |V(G)|`,
`M = homCount H G`, and `D = homCount K2 G`, the Lean inequality is equivalent
because `N > 0` to the exact integer residual

```text
R_H(G) = M * N^(2*e) - D^e * N^h >= 0.
```

This is the only residual orientation authorized by this audit. Negative is a
candidate counterexample; zero is equality.

## Current-source theorem inventory

The source itself records the following solved pattern domains:

- `K2`, with a sorry-free equality proof;
- `K2,2 = C4`, with a sorry-free Cauchy--Schwarz proof;
- trees, marked `research solved` from Sidorenko's theorem (the general Lean
  proof remains a `sorry`, while the subsingleton base case is closed).

Open PR #4845 adds declarations for complete bipartite graphs, even cycles,
paths, stars, and necessity of bipartiteness. The complete-bipartite,
even-cycle, and path declarations are marked solved but still contain `sorry`;
the star and non-bipartite-necessity declarations are proved in Lean. Open PR
#4603 adds the graphon statement and solved declarations for tree, even-cycle,
and complete-bipartite pattern domains. Neither PR claims the general
conjecture.

## Local project-history and theorem gate

Pre-audit project commit:
`8bf2be41c06dae79bc88f8303b774999c80d7ca3`.

The complete local worktree and history were searched for the exact terms

```text
Sidorenko
sidorenko
homDensity
homCount
```

using `rg` over the repository and `git log --all -G` over all refs. The only
history hits are the current-manifest selection and ranking commits
`e225d78`, `2c30971`, `c156ddf`, and `daef974`. The only current files are the
source sweep and target-ranking reports. There is no local Sidorenko theorem,
Lean certificate, homomorphism-count evaluator, pattern/host result row,
branch, tag, or release.

The ranking report already states the operative obstruction: exact equality
examples in the project lie in theorem-closed pattern classes, while a finite
counterexample requires varying both the pattern and host. No existing c5-k4
carrier result supplies a Sidorenko residual.

## Live issue and PR gate

Read-only GitHub searches on 2026-08-13 found:

- PR #4845, **open**, mergeable but blocked, updated 2026-08-10:
  `https://github.com/google-deepmind/formal-conjectures/pull/4845`;
- PR #4603, **open**, mergeable but blocked, updated 2026-08-03:
  `https://github.com/google-deepmind/formal-conjectures/pull/4603`;
- PR #4016, closed, the original finite formalization;
- PR #4224, closed, the correction adding a nonempty host;
- no open issue or PR claiming a proof or counterexample to the current general
  finite declaration.

These are status/proof-domain records only. No public action was taken.

## Primary-literature proof-domain gate

The full conjecture remains open. The 2025 paper on even subdivisions still
describes it as very open, and the specifically audited small open pattern is
the ten-vertex cubic bipartite graph

```text
H_M = K_{5,5} minus C10.
```

Lee--Schuelke explicitly identify this pattern as an open Sidorenko case while
proving that it is not weakly norming:
`https://arxiv.org/abs/1910.08454`. It has bipartition
`A={a0,...,a4}`, `B={b0,...,b4}` and, with indices modulo five, the exact edge
set

```text
ai--b(i+1), ai--b(i+2), ai--b(i+3)  for i=0,...,4.
```

Thus `|V(H_M)|=10`, `|E(H_M)|=15`, and every vertex has degree three. A 2025
open-problem update continues to call its Cayley-host case the simplest unknown
instance, so no later resolution was located:
`https://people.maths.ox.ac.uk/greenbj/papers/open-problems.pdf`.

The proof-domain audit also checked these primary sources:

- a universal vertex complete to the opposite part and an approximate theorem
  for all patterns: `https://arxiv.org/abs/1004.4236`;
- tree-decomposable families, certain subdivisions including clique
  subdivisions, and Cartesian products with even cycles:
  `https://arxiv.org/abs/1510.06533`;
- weakly norming/reflection-graph families:
  `https://arxiv.org/abs/1611.05784`;
- degree-divisibility blow-ups and a Sidorenko blow-up of every bipartite
  pattern: `https://arxiv.org/abs/1809.01259`;
- generalized-theta substitutions and further subdivision families:
  `https://arxiv.org/abs/2408.03491`;
- locally quasirandom/constant graphons:
  `https://arxiv.org/abs/1004.3026`.

This list is an exclusion gate for the obvious seeds and transformations, not
a claim to be an exhaustive survey of every known Sidorenko class.

## Equality/near-wall seed audit

`H_M` supplies an exact open-domain **pattern**, but the repository supplies no
nondegenerate finite host on which its residual is known to be zero or near
zero.

The equality candidates available without a new host evaluation were rejected:

1. Any nonempty zero-edge host gives `D=M=0` for every pattern with an edge, so
   `R_H(G)=0`. This is a degenerate zero-density identity, not an
   invariant-coordinate wall. Adding its first edge moves immediately away
   from the zero-density boundary and supplies no frozen near-wall evidence.
2. A constant graphon gives equality for every pattern, but it is not a finite
   host in the current Lean declaration. Finite quasirandom approximants are
   only near equality after an actual calculation, which Phase 0 forbids; the
   local neighborhood of the constant graphon is also a proved positive domain.
3. Balanced host blow-ups preserve every homomorphism density exactly and hence
   preserve the residual sign. They cannot create a crossing direction from a
   known safe seed.
4. The source's exact `K2`, `K2,2`, and tree equality/sharpness cases vary the
   pattern inside already proved domains and therefore cannot be used as
   open-domain evidence.

No exact, nondegenerate, open-pattern finite-host equality or certified
near-wall pair remains after these exclusions. Selecting an edge toggle,
two-block perturbation, or host blow-up now would either start from the
degenerate zero-density identity or require evaluating candidate hosts before
the family was frozen.

## Phase 0 disposition

**`STRICT_STOP_NO_NONDEGENERATE_OPEN_DOMAIN_WALL`**.

The source, reading, residual, live status, local theorem inventory, proved
domains, and exact open pattern `H_M` are settled. The required second half of
the freeze is not: no nondegenerate finite-host equality/near-wall seed exists
in the current evidence, so no bounded host transformation is authorized.

There are deliberately no development rows. A future Sidorenko lane must begin
with a separate Phase 0 contract that brings an independently sourced exact
finite-host wall for `H_M` (or another certified open pattern); it may not use
exploratory host evaluations to choose that wall retrospectively.

No commit, push, issue, PR, release, or other public action is authorized by
this contract.
