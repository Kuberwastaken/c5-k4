# Erdős 375 / Grimm S-unit Hall family: DEVELOPMENT preflight

**Audit date:** 2026-08-14 UTC  
**Disposition:** `STRICT_STOP_DUPLICATE_AND_NO_CROSSING_REACHABILITY`  
**Evaluation state:** `NOT_EVALUATED`  
**Authorization:** none

This directory is deliberately separate from the held-out arithmetic audit.
It asks only whether one proposed DEVELOPMENT construction is source-clean and
can reach its obstruction wall before any target instance is evaluated. No
integer `n`, composite block, exponent box, target residual, matching, or
candidate was enumerated. No broad `n` scan, workflow, freeze, dispatch,
release, issue, pull request, or other public action is authorized.

## Immutable target identity

The GitHub commits and contents APIs resolved the target to:

```text
repository  google-deepmind/formal-conjectures
commit      2411d22e1bd550d050d0eac6c1fb379a76a3e7c5
tree        f6b52f1d3f63b365d6f8c405623d5f7a4e674efc
commit date 2026-08-14T19:16:38Z
path        FormalConjectures/ErdosProblems/375.lean
blob        e68e24b79463a32b5c61c101fef737bd86d0cc97
bytes       4217
SHA-256     59e7516bf4dd5cf3e7eabbfcfc8f13f9cfda33446fd2f5c844cf36edd3bd2c7c
declaration Erdos375.erdos_375
status      research open
```

Pinned source:
[`375.lean`](https://github.com/google-deepmind/formal-conjectures/blob/2411d22e1bd550d050d0eac6c1fb379a76a3e7c5/FormalConjectures/ErdosProblems/375.lean).

The proposition says that every block `n+1,...,n+k` of composites admits an
injective choice of prime divisors, one per position. The theorem is
answer-wrapped:

```text
answer(sorry) <-> Erdos375Prop
```

Therefore a finite obstruction refutes `Erdos375Prop`; any later resolution
claim would also need to handle the repository's answer-wrapper convention
exactly rather than merely report a failed matching.

## Public status and race audit

The independent problem database at pinned `teorth/erdosproblems` commit
`3cbe2cffad0267952de3523089549009ea6fe5dc` lists Problem 375 as
`FALSIFIABLE Open`, says there are no partial or complete solutions claimed in
its comments, and records Laishram--Shorey's verification for every `k` and
`n <= 1.9 * 10^10`.

Exact DeepMind issue and pull-request searches for `erdos_375`, `Erdos 375`,
and `Grimm` found no mathematical resolution claim. Merged PR #1497 introduced
the Erdős module; older PRs #175 and #261 concern the Wikipedia formalization
and a statement correction. Two open PRs touch the exact path:

- #4428, a repository-wide version bump;
- #4004, repository-wide docstring formatting.

Neither claims to solve the target, but any later activation would have to
repeat the exact-path changed-file audit and stop on semantic or status drift.
A non-peer-reviewed public computation additionally claims verification
through `10^11`; it is treated as a conservative source boundary, not as a
certified theorem and not as novelty evidence.

The local v1.4 registry already contains this cluster with identity

```text
fabf45dc5c7de91bcbfdf2bdc43a4df11eb464f7ca27baaa4108450a32ac3976
```

and records `semantic_exposure: true`, `unknown_exposure: true`, and
`eligible: false`. This preflight adds further semantic exposure. The lane is
DEVELOPMENT only and can never be described as held out.

## Exact obstruction coordinate

For a finite composite block `B={n+1,...,n+k}`, form the bipartite graph

```text
left vertices  I = {1,...,k}
right vertices all primes dividing at least one n+i
edge (i,p)     exactly when p divides n+i.
```

Hall's theorem gives the exact residual for every subset `S` of positions:

```text
H(S) = |N(S)| - |S|.
```

The conjectured matching exists exactly when `H(S) >= 0` for every `S`.
The equality wall is `H(S)=0`; a literal obstruction requires one subset with
`H(S)<0`, in addition to the full block's composite premise.

The proposed sufficient construction chooses a finite prime set `P` and a
position subset `S` such that

```text
every n+i for i in S is P-smooth, and |P| < |S|.
```

Then `N(S)` is contained in `P`, so `H(S) <= |P|-|S| < 0`. This implication is
exact and target-independent. It certifies the sign only **if** such a subset
is reached inside an all-composite consecutive block.

## Duplicate gate: failed

The primary source

```text
Shanta Laishram and M. Ram Murty,
Grimm's Conjecture and Smooth Numbers,
arXiv:1306.0765v1 (2013).
```

was downloaded from arXiv for this audit. Its PDF receipt is:

```text
SHA-256          70fd0c5704d23aa7f4066b036e3ce81974af1688ee56465b1e33328e33740586
pages            17
classification   text_based
confidence       1.0
pages needing OCR []
encoding issues  false
```

Lemma 2.4 states that if a short interval contains more `y`-smooth numbers
than there are primes at most `y`, then the interval has no prime
representation. Its proof is precisely the pigeonhole/Hall-neighborhood
mechanism: all selected numbers draw prime divisors from a support set too
small to assign distinctly.

The proposed `P`-smooth/S-unit family is a specialization of that published
transfer, not an independently new wall geometry. Replacing the scalar smooth
bound `p <= y` by an explicit finite support `P`, or spelling the same
pigeonhole argument as a Hall residual, does not clear the duplicate gate.

## Target-free crossing-reachability preflight

The remaining question is whether an unoccupied parametrized family reaches
the wall without looking at a Grimm instance. Write selected terms as

```text
n + i = product over p in P of p^(e[i,p]),
```

with exact offset equations

```text
product_p p^(e[i,p]) - product_p p^(e[j,p]) = i-j.
```

Three target-free facts are available:

1. If the equations have positive composite solutions for more positions than
   primes, the Hall residual is strictly negative.
2. Adjacent selected positions must have disjoint nonempty prime supports,
   because consecutive integers are coprime.
3. For arbitrary selected positions, every common prime divisor must divide
   their offset difference, since
   `gcd(n+i,n+j)` divides `|i-j|`.

These facts prune exponent/support patterns, but none supplies existence.
Chinese-remainder constructions can make a finite interval composite by
assigning divisors positionwise; they do not also make a Hall-deficient subset
use fewer primes than positions. Conversely, an S-unit difference solution
does not by itself make every intervening block position composite. No theorem
or independently sourced construction was found that joins those two
requirements outside the published verification boundary.

The tempting finite proposal `k in {3,4}`, `|P|=k-1`, bounded prime supports,
and bounded exponent vectors therefore fails before enumeration:

- a bounded exponent box has no target-free proof that it contains any
  consecutive solution;
- a found solution would itself expose a target instance, so reachability
  cannot be inferred retrospectively from target output;
- fixed small `k` lies in the direction of the known
  Ramachandra--Shorey--Tijdeman theorem (`k` below a constant multiple of
  `(log n/log log n)^3`), not in a demonstrated crossing regime; and
- the smooth-number obstruction is already the published source mechanism.

Thus the logical transfer is valid but **crossing reachability is not
established**. The method requires a strict stop before constructing or testing
any `(n,k)`.

## Strict-stop conditions reached

```text
source_status_open                     true
exact_path_resolution_claim            false
heldout_eligible                       false
published_same_wall_transfer           true
target_free_negative_sign_implication  true
target_free_family_realizability       false
full_composite_block_reachability       false
target_instances_read                  0
candidate                              null
workflow_dispatched                    false
```

Final disposition:

```text
STRICT_STOP_DUPLICATE_AND_NO_CROSSING_REACHABILITY
```

This lane may reopen only with both (a) a source-distinct construction not
subsumed by the published smooth-number pigeonhole mechanism and (b) a proof,
derived without inspecting Grimm target output, that its frozen parameter
domain contains an all-composite consecutive block with a Hall-deficient
subset beyond every accepted public boundary. Merely enlarging prime or
exponent caps is forbidden.

