# Wave 2 live automata search — 2026-08-14

## Outcome

**`ZERO_BOUNDED`; no candidate and no novelty claim.**  The search continued
the current research-open declaration
`CernyConjecture.cerny_conjecture`.  At order 13, a literal negative witness
would be a synchronizing DFA whose exact shortest reset-word length is greater
than `(13 - 1)^2 = 144`.  Three independently capped 60-second arms scored
25,331 new automata by exact breadth-first search of the 8,191 nonempty state
subsets.  Every row synchronized; the largest exact reset length was 144.

This wave used the structural move exposed by the first wave rather than
replaying its mostly nonsynchronizing random family.  The permutation letter
was frozen to the 13-cycle `a(i)=i+1 mod 13`.  Every other letter had the form

```text
b(i) = p(i)              if i != src
b(src) = p(dst),         src != dst,
```

where `p` is a permutation.  Thus `b` always has rank 12.  This parameterizes
the full class of rank-12 transformations on 13 states (up to the two choices
of which member of the doubleton fibre is called `src`).  It also retains the
prime-cycle synchronization geometry absent from the first wave's arbitrary
permutation arm.  Synchronization was not merely assumed: the exact BFS found
a singleton in every emitted row.

Claude's Cycles was excluded before target selection because PR #4935
preempts that lane.

## Status and literal gate

The worktree began on `main` with one unrelated untracked file,
`lean/SnakeInTheBoxNine191.lean`; it was not read, changed, or included in any
command.  The requested report path did not exist.

Live remote reads resolved `google-deepmind/formal-conjectures/main` to
`b33d8678a28118c95d8d4f60b11faaf39ccff1e6`.  The raw current
`FormalConjectures/Wikipedia/CernyConjecture.lean` had SHA-256
`a370ccc0e20edf6c2d7af7aa8638a224a47dfdbe28125fbdf8f78ab3deb0cd12`,
identical to the first-wave copy.  An all-state GitHub search found only merged
statement PR [#3906](https://github.com/google-deepmind/formal-conjectures/pull/3906)
and its closed statement issue
[#3905](https://github.com/google-deepmind/formal-conjectures/issues/3905);
it found no proof, disproof, or competing Černý candidate.

As in Wave 1, the Lean declaration is an `answer(sorry) <->` statement.  A
finite automaton above the bound would settle the intended universal right
side negatively, but would not alone falsify the biconditional until the
answer placeholder is fixed.

## Frozen verifier and controls

For each transition vector `b`, the verifier began at the full 13-state subset
and performed ordinary BFS under the exact subset images of `a` and `b`.  The
first singleton depth is therefore the shortest reset length, not the length
of a heuristic word.  A row with no reachable singleton would fail the
synchronizing premise rather than count as a hold.

Each arm ran in its own child process with a parent-enforced hard wall of 60.0
seconds and an internal serialization deadline of 59.15 seconds.  The parent
received a final arm receipt at 59.160--59.170 seconds in all three cases and
did not need its final hard kill.  Search code was supplied on standard input;
it left no repository artifact.  Every arm independently replayed the
standard `C_n`, `n=3,...,13`, control and obtained exactly

```text
4, 9, 16, 25, 36, 49, 64, 81, 100, 121, 144.
```

Best-row replay also reconstructed a reset word and reached a singleton after
discovering 8,179 subset states.  Flushed best events and periodic count
checkpoints were emitted during the live processes, so an interruption would
have retained incremental evidence.

## Equal-budget arms

| arm | frozen search | realized exact work | result |
|---|---|---:|---|
| `CATALOGUE` | Lexicographic affine permutations `p(i)=u*i+v mod 13`, `u=1,...,12`, `v=0,...,12`, followed by every ordered `src != dst`.  The frozen catalogue contains 24,336 rows. | 13,479-row prefix in 59.166 s; 13,479 synchronized.  Checkpoints at 2,000-row increments reached 12,000 rows at 52.315 s. | Zero crossings.  Maximum 144, attained 13 times in the realized prefix.  The prefix is incomplete under the cap, so this is not a complete-catalogue zero. |
| `GENERIC` | Seed `2026081402`; independent uniform random permutation `p`, uniform `src`, and uniform distinct `dst`, continuing to the cap. | 11,751 rows in 59.160 s; 11,751 synchronized.  Checkpoints: 5,000 rows at 25.217 s and 10,000 at 50.788 s. | Zero crossings.  Maximum 54, uniquely first reached at row index 4,907. |
| `WALL_NAVIGATION` | Seed `2026081403`; start at the standard tight `C13` defect and propose one permutation-output swap or a change of `src`/`dst`.  Every move remains permutation-plus-one-merge and hence rank 12.  Exact-score hill climbing retained nonworsening moves with rare downhill moves. | 101 distinct rows in 59.156 s; 101 synchronized. | Zero crossings.  It rediscovered length 144 after 16 evaluations, then its duplicate filter/local neighborhood stalled.  This is an algorithmic stall, not 60 seconds of independent evidence. |

The catalogue's first tight row was

```text
b = (1,1,2,3,4,5,6,7,8,9,10,11,12),  L = 144.
```

Its exact length histogram near the top began
`144:13, 133:26, 122:26, 111:26, 100:26, 89:26` in the realized prefix.
The generic best was

```text
b = (6,10,8,9,1,7,0,3,4,2,11,5,6),  L = 54,
```

from permutation `(6,10,8,9,1,7,0,3,4,2,11,5,12)` with `src=12` and
`dst=0`.  Its SHA-256-derived row digest was `fd7c1c47e940107f`.

The wall best was the standard defect

```text
b = (0,1,2,3,4,5,6,7,8,9,10,11,0),  L = 144.
```

For both tight orientations the reconstructed word had the expected form
`b (a^12 b)^11`, of total length 144.

## Increment over Wave 1

The first-wave generic arm used an arbitrary permutation letter plus a
rank-12 merge and spent 1,833 of 2,000 rows (91.65%) proving that the premise
was false.  This wave instead kept the full 13-cycle and moved all additional
permutation structure into the defect letter.  The result was
25,331/25,331 synchronizing rows across the three arms.  This is a genuine
search-efficiency improvement and validates the new structural move, but it
did not improve the extremal residual: the structured catalogue and wall arm
only returned to Černý equality, while the generic arm remained 90 steps
below it.

The affine catalogue also extends the first-wave identity-permutation ladder:
many nonidentity affine transformations remain exactly scorable and
synchronizing, but no realized row exceeded the standard orbit.  The evidence
does not justify a theorem claim because only 13,479 of 24,336 catalogue rows
fit the cap and the full permutation space is vastly larger.

## Disposition

No candidate-specific verification or novelty release gate was activated.
The honest terminal label is `ZERO_BOUNDED`, with the catalogue explicitly
marked as a timeout prefix and the wall arm explicitly marked as a
duplicate-neighborhood stall.

If this lane is continued, the next wall engine should enumerate a fixed
radius without replacement or maintain a beam of several high-length states;
the present single-state walker spent almost all of its nominal budget on
duplicate proposals.  The rank-12/13-cycle parameterization should be kept:
it eliminated premise-false waste and supplies finite literal BFS
certificates for every row.
