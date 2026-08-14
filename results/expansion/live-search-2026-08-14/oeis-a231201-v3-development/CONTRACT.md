# OEIS A231201 v3 constructor-only DEVELOPMENT freeze

This is a contaminated, bounded construction diagnostic. It is not held-out
evidence, a conjecture result, or an authorization to promote any emitted
object. It inherits the immutable source/database gate from v2.2 but stops
before every target-verification stage.

## Why v3 stops at construction

Run `31812806288` showed that six proposals covering 192 sampled exponents
each missed the cheap contiguous seed almost immediately: the least missed
exponents in cells `0_0,0_1,0_2,1_0,1_1,1_2` were respectively
`3,5,29,6,6,22`. Sending those proposals into the explicit periodic checker
created 13.1--18.1 million partial states before an honest deadline.

More importantly, the finite full-period cover used by v1--v2.2 is now a
theorem-shadow direction, not a justified search objective. For a fresh prime
`q` and current modulus `M`, put
`d = ord_q(2) / gcd(M, ord_q(2))`. Each live congruence class has exactly
`q*d` lifts at the new combined modulus, split into `d` fibers. Within each
fiber `2^x (mod q)` is constant while `x (mod q)` is bijective, so exactly one
of the `q` lifts is forbidden by a selected value and exactly `d*(q-1)` lifts
survive. Thus a nonempty live class cannot be eliminated at a fresh prime.
V3 therefore does not run, wrap, or reinterpret the old full-period checker.
A future target phase would need a separately frozen exact backend for the
bounded condition `1 <= x < n`.

## Frozen construction diagnostic

All three inherited construction arms remain in the matrix. The two full-seed
arms retain their v2.1 Python-3.9-compatible implementations. The
`SMALL_BASIS_CEGAR` arm begins rounds 0, 1, and 2 with exactly 192, 256, and 320
active low-discrepancy rows, so round 1 cannot repeat v2.2's identical
192-row master.

After every feasible small-basis solve, v3 exactly scans all active exponents
in `1..4096` in increasing order. If a miss exists, it records the complete
proposal, its SHA-256, the exact least missed exponent, and a hash-bound basis
delta, then adds that exponent and re-solves inside the same 48-second search
budget. A proposal file can be written only when no active seed exponent is
missed. The terminal status is
`FULL_SEED_PROPOSAL_EMITTED_DIAGNOSTIC`; there is no promotion status.

Every proposal and terminal binds the inherited manifest, the v3 manifest,
the exact gate, campaign identity, basis, semantic proposal digest, and
artifact digest. Both explicitly set `diagnostic_only=true`,
`target_promotion_authorized=false`, and
`mathematical_result_claimed=false`. The independent artifact checker rejects
any other trust-boundary encoding and replays every least-escape delta.

## Caps and stop rule

Construction has 48 seconds of search inside a 54-second internal budget and
the standing 60-second external process-group cap with six-second TERM-to-KILL
grace. Artifact verification is separately capped at 60 seconds. The source
gate retains its own 54/60 discipline.

V3 is nonresumable and runs each `(arm,cell,round)` independently. A cap,
unknown solver status, basis infeasibility, or full-seed proposal is only a
diagnostic observation. None may be upgraded to a bounded `x<n` certificate,
periodic exhaustion, or an A231201 result.
