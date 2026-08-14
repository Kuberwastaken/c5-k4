# Live automata/game/process search — 2026-08-14

## Scope and terminal outcome

**Lane outcome: `ZERO_BOUNDED`; no candidate and no novelty claim.** Three
currently open finite-certificate question clusters were searched:

1. `CernyConjecture.cerny_conjecture`, where one finite synchronizing DFA
   whose shortest reset word is longer than `(n-1)^2` falsifies the intended
   positive side;
2. `OeisA37274.home_prime_conjecture`, where one finite nonprime cycle of the
   prime-factor-splicing process literally refutes the universal declaration;
3. `Erdos872.erdos_872.variants.prime_question`, where one finite maximal
   primitive subset of `{2,...,n}` with cardinality below `pi(n)` falsifies the
   right side of the encoded question.

The completed Cerny two-cycle and dihedral-factorization families, Catch-Up
`N=23/24` trial, and Latin Tableau order-15 trial were not rerun. Lychrel 196
and the asymptotic clauses of Erdős 872 were excluded because a bounded
failure to terminate or a finite game-value row cannot certify their
negations.

There is an important literal-formal qualification. The Cerny declaration is
`answer(sorry) <-> universal_bound`, and the Erdős 872 variant is
`answer(sorry) <-> universal_maximal_set_bound`; a finite counterexample would
settle the intended right side negatively but would not by itself prove the
Lean biconditional false without fixing the answer placeholder. The Home Prime
declaration has no answer placeholder and is directly universal. No crossing
was found under either interpretation.

## Literal statements and current upstream status

The GitHub API resolved current upstream `main` to
[`b33d8678a28118c95d8d4f60b11faaf39ccff1e6`](https://github.com/google-deepmind/formal-conjectures/commit/b33d8678a28118c95d8d4f60b11faaf39ccff1e6).
The three raw files at that commit are byte-identical to the local search
copies, with SHA-256 digests:

| declaration file | SHA-256 | current category |
|---|---|---|
| `Wikipedia/CernyConjecture.lean` | `a370ccc0e20edf6c2d7af7aa8638a224a47dfdbe28125fbdf8f78ab3deb0cd12` | `research open` |
| `OEIS/37274.lean` | `1af7d2502660a77f7897ef608007d56d6409e68f058cae1967a84308dde19a5a` | `research open` |
| `ErdosProblems/872.lean` | `ed850b66ee339066d794a53a9e36f1ba98f168f5c8caa4e57c4fc7e5a272d7b4` | `research open` |

The exact predicates used were the formal ones: full-subset power-automaton
reachability for Cerny; sorted prime factors with multiplicity concatenated in
decimal for A037274; and pairwise divisibility incomparability plus maximality
inside `Finset.Icc 2 n` for Erdős 872.

All-state upstream issue/PR searches found only the statement work. Cerny PR
[#3906](https://github.com/google-deepmind/formal-conjectures/pull/3906)
merged on 2026-06-01; Home Prime PR
[#4794](https://github.com/google-deepmind/formal-conjectures/pull/4794)
merged on 2026-08-09; and Erdős 872 PR
[#4226](https://github.com/google-deepmind/formal-conjectures/pull/4226)
merged on 2026-07-02. Their matching issues #3905, #4788, and #994 are closed
because formalization merged, while the declarations remain marked open. No
upstream proof/disproof PR or competing candidate was found for the searched
statements.

## Process accounting

Every subprocess was externally wrapped in `timeout 60s`; every CBC invocation
also had an internal limit of at most ten seconds and one thread. Search code
was supplied on standard input and left no repository artifact. The only
durable output is this report.

Three exploratory Home Prime attempts produced no usable terminal row: two
Pollard-rho catalogue processes (planned ranges `2..5000` and `2..1000`) and a
20,000-seed generic process ended without serialized output. They are counted
as inconclusive orchestration/resource zeroes, not silently included in the
successful denominators. An earlier Erdős catalogue launch failed immediately
because `sympy` was absent from the selected virtual environment; the exact
replacement used an internal primality test and completed. No process exceeded
the 60-second cap.

## Target 1: Cerny finite automata

The state set was `Z/13Z`. Reset length was computed exactly by BFS from the
full 13-state subset to the first singleton in the complete nonempty power
automaton. Thus a synchronizing row has an exact optimum, not merely a found
word. The defect letter in all searched rank-preserving rows had rank 12.

| arm | frozen search | realized work | hits / zeroes |
|---|---|---|---|
| `CATALOGUE` | Standard `C_n` for `n=3..13`, then all 156 ordered single merges `b(src)=dst` with the standard 13-cycle letter. | One process, about 13 s. The controls reproduced `4,9,...,144=(n-1)^2`. All 156 C13 rows synchronized. | Zero crossings. Reset lengths were exactly `23,34,45,...,144`, with 13 rows at each length. The 13 adjacent merges were the only length-144 rows. `ZERO_COMPLETE` for this catalogue. |
| `GENERIC` | Seed `2026081401`; 2,000 independent rows, each a uniform random permutation letter plus an independently uniform ordered rank-12 merge. | One process, 22.503 s; 167 synchronizing and 1,833 nonsynchronizing rows. | Zero crossings. Maximum length 144; the best row was index 120 with permutation `(5,6,12,4,9,3,7,10,0,2,8,1,11)` and merge `10 -> 8`. Since the permutation maps `10 -> 8`, this is a relabelled adjacent-merge tight catalogue case, not a new extremal type. |
| `WALL_NAVIGATION` | Keep `b(12)=0`; exhaust all 78 swaps of two outputs of the standard cycle permutation. This is a defect-preserving letter surgery: rank 12 is unchanged while the permutation cycle structure is broken. | One process, about 3.6 s; all 78 rows exhausted. | Seventy-seven rows were nonsynchronizing. The sole synchronizing row, swapping outputs 0 and 12, had reset length 23 and residual `144-23=121`. Zero crossings. |

The shortcut-risk check was explicit. Adding accessible factors or locally
splitting the slow cycle can only expose new subset paths; the earlier
dihedral trial showed that risk empirically, and this exhaustive swap family
shows the stronger failure mode: loss of synchronization in 77 rows and a
121-step shortcut in the survivor. Every synchronizing wall row was strictly
shorter than C13.

**Theorem signal, not theorem:** if cyclic distance from the merged source to
its image is indexed `d=1,...,12`, the complete catalogue obeys
`L=11d+12`. Proving this exact ladder would explain both the unique tight
adjacent-merge orbit and the uniform 11-step loss per displacement. The
generic arm also reveals a practical improvement: prefilter permutation-plus-
merge rows for synchronization or strong pair reachability, since 91.65% of
the random budget was spent certifying nonsynchronization.

## Target 2: Home Prime / A037274

All completed factorizations used exact trial division. A row was declared
resolved only upon exact primality; a repeated nonprime value would have been
a literal cycle candidate. Values beyond the frozen magnitude threshold, or
trajectories beyond the step threshold, were brackets rather than holds.

| arm | frozen search | realized work | hits / zeroes |
|---|---|---|---|
| `CATALOGUE` | Every start `2..10000`; at most 40 splice steps; bracket before factoring a nonprime value above `10^10`. | One process, natural completion in about 12 s; 9,999 starts. | 6,639 reached a prime, 3,360 brackets, zero repeated nonprime states. Longest resolved start was 2950: 13 steps, ending at prime 33,261,510,817. |
| `GENERIC` | Seed `3727420260814`; 2,000 uniform starts from `10001..1000000`; at most 30 steps; magnitude threshold `10^9`. | One process, 2.8 s. | 858 reached a prime, 1,142 brackets, zero cycles. Longest resolved sample was 253713: seven steps, ending at prime 13,173,273,343. |
| `WALL_NAVIGATION` | All one-decimal-digit mutations of the catalogue's longest resolved composite start 2950, retaining only composite starts. | One process, 0.6 s; 33 distinct rows; at most 50 steps; threshold `10^12`. | 25 reached a prime, eight brackets, zero cycles. Longest resolved mutation was 2952 at nine steps; the shortest resolved in one step. |

The wall move did not preserve trajectory difficulty: all resolved mutations
shortened the 13-step base trajectory, sometimes to one step. This is the
process analogue of shortcut risk. The eight brackets are not theorem
evidence; they are factoring-policy stops at 13--14 decimal digits.

There is no positive theorem signal beyond the bounded no-cycle observation.
The actionable improvement is certificate-aware factorization: use a bounded
ECM/Pollard pipeline that serializes every completed prime factor with a
primality certificate, and checkpoint before the cap. That would convert the
three no-output exploratory processes and many magnitude brackets into honest
rows without confusing hard factorization with a long dynamical orbit.

## Target 3: Erdős 872 maximal primitive sets

For each `n`, the exact wall model minimized `sum x_v` subject to

```text
x_a + x_b <= 1                  whenever a divides b,
x_v + sum_{u comparable to v} x_u >= 1   for every v in {2,...,n}.
```

The first constraint makes the selected set primitive; the second is exactly
maximality. Every emitted witness was independently replayed for both
properties before comparing its cardinality with the exact elementary prime
count.

| arm | frozen search | realized work | hits / zeroes |
|---|---|---|---|
| `CATALOGUE` | Solve the binary model exactly for every `n=2..120`. | One process, 6.3 s; 119 optimal rows. | In every row the minimum cardinality equalled `pi(n)`. Zero negative answers; complete zero for this range. |
| `GENERIC` | Seed `87220260814`; 4,000 random-order greedy maximal-antichain constructions at each `n` in `64,96,128,160,200,256,320`. | One process, about 11 s; 28,000 maximal primitive sets. | Zero sets below `pi(n)`. Best residuals `|A|-pi(n)` were `0,0,0,2,3,3,19`. |
| `WALL_NAVIGATION` | Exact minimum independent-dominating-set state surgery at `n=128,160,200,240,300`, directly allowing prime representatives to be exchanged for composite divisibility states. | One process, 1.0 s; all five CBC models optimal (individual solves 0.042--0.143 s). | Objectives `31,37,46,52,62`, exactly `pi(n)` in every case. All five witnesses independently passed primitive and maximal checks. Zero crossings. |

**Theorem signal, not theorem:** every one of the 124 exact optimum rows has
minimum size exactly `pi(n)`. This is directly aligned with the open right
side rather than a loose numerical correlation. The next useful step is not a
larger blind MILP range; it is an injection or charging lemma showing that a
maximal antichain in the divisibility poset must carry at least one unit for
each prime at most `n`. A proof must handle composite selected elements that
simultaneously dominate multiples of several primes; the finite equality does
not remove that obstruction.

## Overall observations

Across the successful denominators, the lane evaluated 2,234 Cerny automata,
11,999 Home Prime starts plus 33 wall mutations, 119 exact small game states,
28,000 generic maximal primitive sets, and five larger exact game states. It
found zero counterexample candidates and therefore activated no candidate-
specific independent verification or novelty release gate.

The strongest method lesson is that preserving a visible defect is
insufficient. In the automata lane the rank-12 defect survived but the slow
subset geometry did not; in the number-process lane a one-digit neighborhood
mostly created shorter routes. The game lane behaved differently: exact state
surgery repeatedly returned to the prime wall, producing a genuine theorem
signal. Future wall navigation should therefore freeze and test the shortcut
mechanism itself—pair-compression distance for automata, trajectory-prefix
overlap for digit processes, and a prime-charge obstruction for the primitive
game—rather than treating the nominal defect as the whole invariant.
