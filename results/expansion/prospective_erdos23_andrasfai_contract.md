# Frozen prospective trial: Andrásfai successors of the Erdős 23 equality wall

Frozen: **2026-08-13 UTC**, before the database gate and before any development
graph or quotient cut was evaluated.

## Target and source lock

- Upstream: `google-deepmind/formal-conjectures` at
  `d16e05aded22b8c467a0a27c14b2311f53185006`.
- Source: `FormalConjectures/ErdosProblems/23.lean`, blob
  `346d29667313a32382bbf42b87588d53bb208400`.
- Live declaration: `Erdos23.erdos_23`, tagged
  `@[category research open]`.
- Exact statement: a triangle-free graph on `5*n` vertices can be made
  bipartite by deleting at most `n^2` edges.

The source separately records the 5-vertex and 25-vertex cases as solved.
Neither order is a development parameter below. This is a major human
conjecture and no numerical output is a public claim.

## Equality wall and frozen transformation

The uniform independent-set blow-up of `C5` is tight. Write `A_k` for the
Andrásfai graph on `3*k-1` cyclic vertices, with two vertices adjacent exactly
when their difference is congruent to `1 mod 3` (up to sign). Then `A_2=C5`.

The sole transformation is the canonical Andrásfai successor

```text
A_2 = C5  ->  A_k, k in {3,4,5,6},
```

followed by replacing every quotient vertex by an independent bag of size
five. This preserves triangle-freeness and the dense three-chromatic cyclic
geometry while changing the quotient globally. Development orders are
`40,55,70,85`, strictly outside both finite orders explicitly marked solved in
the source. No edge surgery, voltage, nonuniform weight, padding, random graph,
or adaptive parameter is permitted.

## Frozen prediction

The `A_3` successor may retain enough odd-cycle edge burden that its five-fold
blow-up approaches or crosses the Erdős wall. Later successors may instead
move inward because their larger cyclic quotients offer more cut flexibility.
The exact signed slack is

```text
R(G) = (|V(G)|/5)^2 - (|E(G)| - maxcut(G)),
```

and a negative value is a candidate.

## Exact quotient reduction

For a uniform independent blow-up `Q[bar K_5]`, some maximum cut assigns every
false-twin bag wholly to one side: with all other bags fixed, the cut objective
is linear in the number of vertices of that bag placed on one side. Therefore

```text
beta_edge(Q[bar K_5]) = 25 * beta_edge(Q).
```

The primary evaluator must nevertheless emit a full lifted cut and replay it
on the development graph. Quotient maximum cuts are computed by exhaustive
binary enumeration with one quotient vertex fixed; at most `2^16` assignments
occur for the frozen largest quotient.

## Mandatory database gate

Before constructing any development graph:

1. reproduce the current source/status/blob above;
2. evaluate every connected triangle-free Graph Atlas graph on exactly five
   vertices and require edge bipartization at most one;
3. reproduce exact equality on balanced `C5` independent blow-ups with bag
   sizes one through five;
4. verify Petersen at order ten and divisible-order complete-bipartite controls;
5. independently replay every cut, deleted-edge set, triangle-free predicate,
   order divisor, and bound arithmetic.

Any unexplained control failure stops the lane as `DB_SANITY_REJECT`.

## Execution, evidence, and verdicts

- Append, flush, and `fsync` the gate and each of the four development rows.
- Every operating-system process is capped at 60 seconds.
- A crossing requires a separate implementation to enumerate quotient cuts,
  direct triangle search, lifted-witness replay, and a current literature/status
  audit before it can be classified beyond `CANDIDATE_ADVERSARIAL`.
- Verdicts: `DB_SANITY_REJECT`, `CANDIDATE_ADVERSARIAL`, `HOLD_BOUNDED`, or
  `INCONCLUSIVE`.

No commit, push, release, issue, pull request, or other public action is
authorized.

