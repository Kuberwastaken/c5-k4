# A231201 pre-freeze correction: the prime 2

The preflight's notation `C(q,a)={r : r-2^r=a (mod q)}` is sound for odd
`q`, but its canonical representative `r=0` is not sound for `q=2`.
Although `o_2=1` and `m_2=2`, `2^0=1 (mod 2)` while `2^x=0 (mod 2)` for
every positive even `x`. Thus canonical evaluation at `r=0` would falsely
claim that one residue covers all positive even exponents.

This freeze supersedes the preflight design before any target evaluation. For every
periodic class it evaluates `2^x` at the least positive representative:
`x=r` when `r>0`, and `x=m_q` when `r=0`. For every prime in the unchanged
55-prime universe this is equivalent to evaluating any positive exponent in
that class. The preflight's `x=0` seed is removed: `x=0` is outside the source
domain and an extra constraint there could exclude an otherwise valid cover.
The operative seed is exactly `x=1,...,4096`.

The correction changes neither the prime set, assignment variables, nor the
finite assignment universe. Constructor tests prove the positive-exponent
equivalence for `q=2` and all odd frozen primes. The freeze verifier requires
this document and the matching manifest fields.

The preflight also proposed recomputing all 10,000 b-file counts under forty
60-second caps. That entails roughly fifty million large primality decisions
and was not calibrated as feasible. This freeze instead content-locks and
parses every row, exactly recomputes the complete prefix `n=1,...,72` in eight
contiguous 9-row shards, and replays the named source/Lean controls, the prior
private vendored L327 control, and the public covering receipts. The resulting
gate makes the narrower claim recorded in the
manifest; every tested integer is within a proved deterministic Miller--Rabin
range, and it never claims that all 10,000 counts were independently replayed.
