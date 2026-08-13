# Phase 0 contract: R(5,5) cyclic-orbit flip

Date frozen: **2026-08-13 UTC**

Status: **PHASE_0_ONLY**.  This document and its zero-development ledger row
were persisted without constructing or evaluating any development child.
There is no authorization here for a candidate run, git action, release,
issue, PR, or other public action.

## Exact current DeepMind declaration

Live upstream `main` was audited at commit
`d16e05aded22b8c467a0a27c14b2311f53185006`.  The source blob is
`41b81b68621b270892a3b0f238302b4823a99e4b`:

<https://github.com/google-deepmind/formal-conjectures/blob/d16e05aded22b8c467a0a27c14b2311f53185006/FormalConjectures/Wikipedia/RamseyNumbers.lean#L86-L112>

The open declaration is the fixed-value question

```lean
@[category research open, AMS 5]
theorem ramsey_number_five_five :
    R(5, 5) = answer(sorry) := by
  sorry
```

Here `R(k,l)` is the least `n` for which every `SimpleGraph (Fin n)`
fails `G.CliqueFree k ∧ (Gᶜ).CliqueFree l`.  Thus a single supplied graph does
not settle the `answer(sorry)` declaration.  It can test and possibly improve
the lower bound only.

The same module records, as `research solved` but still with `sorry`:

- `ramsey_number_five_five_lower_bound`: an existential `(5,5)`-Ramsey graph
  on 42 vertices, giving `43 ≤ R(5,5)`;
- `ramsey_number_five_five_upper_bound`: `IsGraphRamsey 46 5 5`.

## Local theorem/API inventory and formal boundary

The module supplies:

- `IsGraphRamsey n k l`;
- monotonicity `IsGraphRamsey.succ`;
- complement symmetry `IsGraphRamsey.symm`;
- `graphRamseyNumber` as a natural-number `sInf`;
- the two bound statements above.

The local `FormalConjecturesForMathlib/Combinatorics/Ramsey.lean` and
`Ramsey/Diagonal.lean` files develop `hypergraphRamsey`, including a general
diagonal upper bound, but the audited tree contains no proved bridge identifying
that definition with this module's `graphRamseyNumber`.  It also contains no
machine-checked 42-vertex Exoo witness.  Consequently, a future successful
trial should first state the source-shaped strengthening

```lean
∃ G : SimpleGraph (Fin 43), G.CliqueFree 5 ∧ (Gᶜ).CliqueFree 5
```

and separately supply the missing order-to-lower-bound bridge if a numerical
`44 ≤ R(5,5)` theorem is desired.

## Live status and literature gate

The scoped DeepMind GitHub audit found:

- open intake issue #2364;
- merged formalization PR #2436;
- closed, unmerged duplicate PR #3409;
- no issue or PR claiming an exact value, improved lower bound, or formal proof
  of either current bound.

The rigorous bounds found in the cited primary literature remain

```text
43 ≤ R(5,5) ≤ 46.
```

The lower bound comes from Exoo's 42-vertex coloring.  Ge--Jayasooriya--Qiu--
Sun--Yuan, arXiv:2212.12630v3, gives a detailed verification and explicitly
studies near-miss colorings on 43 vertices.  Angeltveit--McKay,
arXiv:2409.15709v2, proves the upper bound 46 by independent large
computations.  The 2025 quantum-diagnostics preprint arXiv:2508.16699v2
heuristically identifies 45; its abstract does not give a rigorous bound or
change the status used here.

This gate must be refreshed before any development run.  Discovery stops if a
rigorous 43-vertex `(5,5)`-Ramsey graph, an improved upper bound, or the exact
value has appeared.

## Frozen near-wall carrier

Use the 43-vertex cyclic coloring `Cyclic(43)` from Definition 1.1 of
arXiv:2212.12630v3.  Vertices are `Z/43Z`; the undirected cyclic distance of
`a,b` is the unique `d ∈ {1,...,21}` congruent to `±(a-b) mod 43`.
The red graph has distance set

```text
R = {1,2,7,10,12,13,14,16,18,20,21};
```

the remaining distances

```text
B = {3,4,5,6,8,9,11,15,17,19}
```

form its complement.

The cited paper proves that this coloring has exactly 43 red `K5`s, namely the
cyclic translates of

```text
{0,1,2,22,23},
```

and no blue `K5`.  This is the near-equality wall: only one color prevents it
from being a 43-vertex lower-bound witness.

## One bounded symmetric operation

For each and only each

```text
d ∈ {1,2,20,21},
```

form `G_d` by recoloring the entire cyclic edge orbit of distance `d` from red
to blue.  Equivalently, delete from the red graph all 43 edges
`{x,x+d}` for `x ∈ Z/43Z`.  No other distance class, partial orbit, second
flip, local repair, relabeling, or adaptive expansion is allowed.

This operation is method-valid and directionally explicit:

- it preserves all 43 vertices and full cyclic symmetry;
- every known red `K5` contains an edge of each of the four frozen distances,
  so each child is predicted to have red clique number at most four;
- moving a full red orbit into blue is predicted to increase only the blue
  clique coordinate; the exact question is whether it reaches five;
- if some child has both `ω(G_d) ≤ 4` and `ω(G_dᶜ) ≤ 4`, it is an exact
  43-vertex Ramsey graph and strengthens the lower bound to 44.

The family has exactly four labelled candidates.  It tests the lower-bound
side only.  A single symmetric construction cannot certify the universal
46- or 45-vertex upper-bound side.

## Mandatory exact gates and certificates for a later phase

No gate below has been executed in Phase 0.  If Phase 1 is separately
authorized, it must:

1. reconstruct `Cyclic(43)` from the two frozen distance sets and reproduce
   exactly 43 red `K5`s and zero blue `K5`s;
2. verify the literature's 42-vertex Exoo graph if and only if its complete 16
   edge recoloring list is independently transcribed and hashed;
3. enumerate all `binom(43,5)=962598` five-subsets for each `G_d`, recording
   exact red and blue `K5` counts plus the lexicographically first witness in
   either nonzero color;
4. independently recompute any double-zero result using separate exact
   Bron--Kerbosch maximum-clique searches on `G_d` and `G_dᶜ`;
5. store the canonical adjacency hash, distance set, counts, witnesses, and
   independent clique bounds incrementally in a new development ledger.

A claimable lower-bound candidate requires both exhaustive subset counts to be
zero and both independent maximum-clique computations to return at most four.
Every process is capped at 60 seconds.  Any source mismatch, timeout, oracle
disagreement, or prior-art hit is an immediate stop.  The family ends after the
four frozen orbit flips regardless of outcome.
