# OEIS A056777 DEVELOPMENT search contract

This is a contaminated, duplicate-aware development lane. It is not a benchmark
sample, novelty claim, proof, disproof, or publication path. The immutable source
is `google-deepmind/formal-conjectures` commit
`6b37c6ede7ccdee80826b8399a80ec010771d5d4`, declaration
`OeisA56777.comesFromPrimeQuadruple_of_a`, still marked `research open` at freeze
time. OEIS reports verification through `10^12`; this lane starts at
`10^12 + 1` and does not treat the 166-row b-file as exhaustive evidence.

## Method wall and exact escape partition

If both `n = ab` and `n+12 = cd` are squarefree semiprimes, with each pair in
increasing order, the sigma equality and `cd-ab=12` imply `a+b=c+d`.
Writing `c=a+x` and `d=b-x` gives `x((b-a)-x)=12`. Odd-prime parity eliminates
the factor pairs giving gaps 13 and 7. The remaining gap is 8; ordered factors
`c<=d` eliminate the order-swapping shift 6, leaving shift 2.
Thus the primes are `p,p+2,p+6,p+8` and `n=p(p+8)`. Small factors are checked
exactly by the same identity. A counterexample must therefore lie in one of the
broad escape strata: `n` nonsquarefree or `n` squarefree with at least three prime
factors. Indeed define `K(x)=sigma(x)+phi(x)-2x`. The two target equalities imply
`K(n+12)=K(n)`. Exact prime-factor algebra gives `K(x)=2` iff `x` is a product
of two distinct primes and `K(x)=1` iff `x` is a prime square (for `x>1`). Hence squarefree-semiprime `n` forces the same
shape for `n+12`, and the ordered gap argument above forces the known quadruple.
Likewise `n=p^2` would force `n+12=q^2`, but `(q-p)(q+p)=12` has no prime
solution, so prime squares are theorem-pruned without target evaluation.

The executable arms below are deliberately non-exhaustive, finite constructive
slices within those broad strata (they do not cover repeated shapes with two
repeated bases or three or more distinct primes, or squarefree shapes with four
or more prime factors):

1. `REPEATED_POWER_SURGERY`: canonical `n=p^e q`, `e>=2`, from frozen
   smallest-prime ranks, exponent ranks, and cofactor-prime offsets.
2. `SQUAREFREE_THREE_BLOCK`: canonical `n=p q r`, `p<q<r`, from frozen
   disjoint smallest/middle/terminal prime-rank blocks.
3. `PURE_PRIME_POWER`: every canonical `n=p^e` in the frozen value interval,
   with prime base and `3<=e<=floor(log_2(10^14))=46`; squares are theorem-pruned
   above. Prime bases make the representation unique. This completely covers the
   pure-prime-power subshape omitted by `p^e q` surgery.

Each arm constructs `n` from its prime-factor certificate before phi/sigma are
evaluated, and factors `n+12` exactly. The search uses deterministic Miller--Rabin
plus deterministic Brent factorization; the independent verifier uses a separately
implemented Floyd factorizer and rebuilds every visited tuple prefix. Shards own
smallest-prime coordinates modulo 24. Each completed tuple records the strict
lexicographic best-so-far wall metrics `|K(n+12)-K(n)|` and
`|phi(n+12)-phi(n)-12| + |sigma(n+12)-sigma(n)-12|`. The bounds describe finite tuple domains, not an
exhaustive integer interval; `DOMAIN_EXHAUSTED` claims only tuple-domain exhaustion.
All searched values (including `n+12`) are below `2^64`; this is the stated domain
of the fixed seven-base deterministic Miller--Rabin test used by both implementations.

## Failure and evidence rules

- Search stops internally at 48 seconds; the shell kills it at 54 seconds; the
  independent verifier is killed at 60 seconds.
- JSONL progress is hash-chained and fsynced every 128 visits. Terminal JSON is
  atomically written and bound to the ledger and immutable gate.
- Factorization and arithmetic are computed in locals. `SIGALRM` is blocked only
  while a fully computed tuple, optional certificate, and checkpoint are committed,
  so a deadline can never expose a half-counted tuple. Unexpected exceptions emit
  `WORKER_ERROR` with a typed, hashed message and fail the job; they are never
  mislabeled as a deadline prefix.
- A certificate is only an exact witness to the Lean declaration if the separate
  verifier re-factors both integers, recomputes phi and sigma, confirms the arm,
  and proves no prime-quadruple witness exists.
- A certificate-verifier failure fails the job. No workflow step promotes,
  publishes, comments on, dispatches to, or modifies upstream.
