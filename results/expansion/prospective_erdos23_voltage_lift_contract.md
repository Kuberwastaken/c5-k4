# Frozen prospective trial: connected voltage 2-lifts for Erdős 23

Frozen: 2026-08-13 UTC, before database-gate or lift evaluation.

## Current source, status, and arithmetic

The checked declaration is `Erdos23.erdos_23` in
`FormalConjectures/ErdosProblems/23.lean`, current local upstream commit
`ee4aaef5655f8aa4a29d59391a822f398891a2b3`. It is tagged `research open` and
asks whether every triangle-free graph on `5*n` vertices has edge
bipartization number at most `n^2`.

The base is the balanced independent-set `C5` blow-up `B_m` with five parts of
size `m`. It has order `5m` and is the equality wall. Every two-sheet lift has
order `10m = 5*(2m)`, so the exact Erdős bound for a lifted graph is `(2m)^2 =
4m^2`. Frozen sheet/base sizes are `m=2,3,4`, giving orders `20,30,40` and
bounds `16,36,64`.

## Frozen voltage family

For each base edge between `(i,a)` and `(i+1,b)`, assign voltage
`sigma(i,a,b)` in `F_2`. Its lift has vertices `(i,a,s)`, `s in F_2`, and
edges

```text
(i,a,s) -- (i+1,b,s xor sigma(i,a,b)).
```

The frozen nonseparable voltage templates are:

1. `diagonal`: `[a=b]` on masked interfaces;
2. `bilinear`: `(a mod 2)*(b mod 2)` on masked interfaces;
3. `circulant0`: `[(a-b) mod m = 0]` on masked interfaces;
4. `circulant01`: `[(a-b) mod m in {0,1}]` on masked interfaces.

For each template, use every nonzero five-bit interface mask, canonicalized
under the dihedral action on the base cycle. Voltage zero is used on unmasked
interfaces. Canonically deduplicate isomorphic lifted graphs. Retain only
connected lifts; disconnected/switching-trivial outcomes are calibration
rejections, not development results.

This global edge-cover transformation is genuinely outside the completed
nonuniform part-size and one-edge-surgery families. No voltage template or
post-lift mutation may be added after results are observed.

## Frozen limits and exactness

- at most 100 distinct connected lifts;
- orders exactly 20, 30, or 40;
- every process at most 60 seconds;
- every maximum-cut MILP at most 10 seconds, zero MIP gap;
- direct triangle enumeration and connectivity check;
- explicit cut partition, kept crossing edges, and deleted same-side edges;
- direct replay that the kept graph is bipartite and arithmetic uses `n/5`.

## Gate order

Before constructing a development lift, repeat the exact 33-graph divisibility-
correct sanity gate from the completed Erdős 23 trial. Add two lift controls at
each `m`: all-zero voltage (two disconnected base copies) and uniform odd
interface voltage (a connected but bipartite lift). The reading is rejected if
any control contradicts its known value.

## Adversarial crossing protocol

This is a major human conjecture. Any apparent strict crossing must be stopped
and attacked before reporting:

1. independently recompute maximum cut with a separately implemented exact
   branch-and-bound or quotient-state enumeration;
2. relabel randomly and solve again;
3. reconstruct the lift from its voltage table and independently verify
   connectedness, triangle-freeness, order divisibility, and every witness;
4. audit the current source, issues/PRs, literature, and known extremal graph
   catalogues;
5. classify only as `CANDIDATE_ADVERSARIAL`, never as a public disproof.

Other outcomes are `DB_SANITY_REJECT`, `HOLD_BOUNDED`, and `INCONCLUSIVE`.
No commit, push, release, issue, PR, or other public action is authorized.
