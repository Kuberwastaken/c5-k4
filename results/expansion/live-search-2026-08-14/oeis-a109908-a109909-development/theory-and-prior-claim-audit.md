# A109908/A109909 theory and prior-claim audit

**Audit date:** 2026-08-14 UTC  
**Disposition:** `PUBLIC_PROOF_CLAIM_AUDITED_INVALID`  
**Target state:** `TARGET_NOT_EVALUATED`

This is an independent mathematical, source-status, and certificate-shape
audit. It does not evaluate a candidate or residue profile, report a bounded
search, or authorize a release. The joint lane may be frozen only after a fresh
public race check records no newer proof or counterexample.

## Exact pinned declarations

The audited upstream pin is
[`google-deepmind/formal-conjectures@6c0950bec7743f5098c0196c6aee7b22c1ec8005`](https://github.com/google-deepmind/formal-conjectures/commit/6c0950bec7743f5098c0196c6aee7b22c1ec8005).

| declaration | path | Git blob | SHA-256 | literal definition |
|---|---|---|---|---|
| `OeisA109908.conjecture` | `FormalConjectures/OEIS/109908.lean` | `79f24ed3f20108f908be7144915e4bc81faedad4` | `518c786ad769b81fb2495c0edf6d496205d304aa4fcca064ad94e5c0224afc96` | the supremum of prime values `k * (n - k) - 1` for `k` in `Finset.Icc 1 (n / 2)` is positive for every `n > 3` |
| `OeisA109909.conjecture` | `FormalConjectures/OEIS/109909.lean` | `f4328ad6def541b625aa9cb287cb898bb1431753` | `bb91d62d701549ae907e5f35a81c1c9bb0ba5ff4d7a5446eae643a0e5cf6ba47` | the number of distinct prime values `k * (n - k) - 1` for `k` in `Finset.Ico 1 n` is positive for every `n > 3` |

Both declarations remain literally tagged `@[category research open]` with
`sorry` at that pin. Exact all-state GitHub issue and pull-request searches for
`109908`, `OeisA109908`, `109909`, and `OeisA109909` returned no resolving item.
The only path commit is merged statement-import PR #4450.

## Natural-number semantics and the shared half-range

Put

```text
F_n(k) = k * (n - k) - 1
```

with every operation interpreted in `Nat`, as in the Lean source. On the target
domain `n > 3` and `1 <= k < n`, both factors are positive and
`k * (n - k) >= n - 1 >= 3` at the endpoints. Consequently the final natural
subtraction does not truncate: it is the ordinary nonnegative integer
`k(n-k)-1`. Modular algebra may only be invoked after recording this domain
fact.

For every `1 <= k < n`, let

```text
r = min(k, n-k).
```

Then `1 <= r <= floor(n/2)`. Moreover `n - (n - k) = k`, because `k <= n`,
and commutativity of multiplication gives

```text
F_n(n-k) = (n-k) * k - 1 = F_n(k).
```

Therefore `F_n(r)=F_n(k)`. Conversely, every
`1 <= r <= floor(n/2)` belongs to `Finset.Ico 1 n` when `n>3`. The two
`Finset.image`s hence have exactly the same underlying value set; the full
range merely duplicates symmetric values.

Filtering that common finite set by `Nat.Prime` is empty exactly when no value
is prime. For A109908, `Finset.sup id` of the empty natural-number finset is
zero, while every member of a nonempty prime finset is positive. For A109909,
`Finset.card` is positive exactly when the filtered finset is nonempty. Thus,
for every `n>3`, the two formal positivity predicates are extensionally
equivalent. A single counterexample refutes both declarations, but it is one
correlated mathematical finding, not two independent discoveries.

## Modular-cover lemma and mandatory caveats

Fix `n>3`, `1 <= k <= floor(n/2)`, and a modulus `q>1`. Let `u` be an inverse
of `k` modulo `q`, equivalently

```text
gcd(k,q) = 1  and  k*u = 1 (mod q).
```

Since the natural subtraction is safe on this domain,

```text
q | F_n(k)
<-> k(n-k) = 1 (mod q)
<-> n-k = u (mod q)
<-> n = k+u (mod q).
```

The reverse implication follows by multiplying `n = k+u (mod q)` by `k`.
The forward implication itself forces `gcd(k,q)=1`: any common divisor of
`k` and `q` would divide both `k(n-k)` and `k(n-k)-1`, hence one. However, a
constructor using the congruence in the forward direction must check
invertibility before computing `u`.

The modulus need not be prime. If prime moduli are used, a fixed choice of
`n mod q` covers at most the two roots of

```text
k^2 - n*k + 1 = 0 (mod q).
```

They are paired by inversion. More explicitly, two units `k,l` prescribe the
same residue `k+k^(-1) = l+l^(-1) (mod q)` exactly when

```text
(k-l)(k*l-1) = 0 (mod q).
```

Thus a profile chooses one compatible residue for `n` per modulus; it cannot
assign unrelated residues to different `k` values using the same modulus.

Divisibility alone is not a compositeness certificate. A covering divisor must
satisfy

```text
1 < q < F_n(k).
```

In particular, `q = F_n(k)` is compatible with `F_n(k)` being prime. On the
half-range `F_n` is strictly increasing and `F_n(1)=n-2`, so the convenient
global sufficient check `q<n-2` makes every covering divisor proper. A final
certificate may instead check properness separately for each represented
`k`.

Finally, let `D` be a fixed finite divisor universe and
`Q = lcm {q | q in D}`. If `Q<=n/2`, the representative `k=Q` is divisible
by every `q in D`, so

```text
F_n(Q) = -1 (mod q)
```

for every such `q`. Therefore it is uncovered by the entire frozen universe.
A complete `D`-cover of the literal half-interval necessarily has `Q>n/2`.
This is a mandatory self-consistency gate, and is a simpler exact form of the
finite-periodic-cover obstruction.

## What a complete counterexample certificate must contain

A replayable joint certificate must include:

1. the exact decimal integer `n`, its byte-level serialization/hash, and a
   check of `n>3` and, for novelty, `n>10^9`;
2. the pinned declaration identities and an executable proof/replay of the
   full-range-to-half-range reduction above;
3. complete coverage of every integer `1 <= k <= floor(n/2)`;
4. for every covered class, an exact divisor `q` and checks of
   `q | F_n(k)` and `1<q<F_n(k)`, or an equivalent factor pair with both
   factors greater than one;
5. exact coverage evidence proving that no `k` is omitted, including endpoint
   and overlap handling; and
6. an independent arbitrary-precision replay that recomputes every expression
   and never trusts probable-prime output, constructor state, or an incomplete
   factorization.

Because novelty forces `n>10^9`, a flat per-`k` ledger has at least 500
million rows. It is operationally incompatible with the project's 60-second
cap and current storage discipline. The freeze must therefore specify a
compact exact cover certificate: `n`, the divisor/modulus list, its covered
residue classes, properness bounds, and a finite-prefix coverage proof that an
independent checker can replay without enumerating or storing half a billion
records. A residue trie, recursively certified CRT partition, or comparably
exact interval-cover representation is acceptable; a claimed least-uncovered
index without its proof is not. Any representative left outside the compact
cover must carry its own exact proper factor.

## Direct prior proof claim

The live A109909 record links:

> Pengcheng Niu and Junli Zhang, *On Two Conjectures of A. Murthy* (2024),
> DOI [`10.13140/RG.2.2.16430.11848`](https://doi.org/10.13140/RG.2.2.16430.11848).

The same preprint is linked from A034693. Its Theorem 1.2 states that every
integer `n>3` can be written `n=a+b` with positive integers `a,b` such that
`ab-1` is prime. Taking `k=a` makes this exactly the A109909 existential, and
the proved half-range symmetry would also establish A109908. It therefore had
to be audited as a potentially preempting result, not treated as a merely
related citation.

The DOI metadata identifies the work as an **unpublished preprint**, with no
journal/container. The DOI was registered on 2024-09-04. The authoritative
OEIS A109909 record was updated on 2024-09-29 and still says “Conjecture” and
“verified up to `10^9`”; A109908 was updated on 2025-10-06 and says the same.
The current DeepMind declarations also remain research-open. These facts do
not by themselves refute the paper, but show that its theorem claim has not
been incorporated as an accepted resolution by either maintained source.

## Decisive failure in the preprint's proof

Section 3 reduces Theorem 1.2 to the Lagrange-multiplier argument in Section 2.
In that argument the real constraint set is defined by

```text
g = sum x_i^2 + sum y_i^2 + sum u_j^2 - pi(D)*z = 0
h = sum (x_i^2+x_i) + sum y_i^2 + sum (u_j^2+u_j)
    - pi(D) - l - l1 = 0,
```

and the objective is

```text
f = sum (y_i^2+y_i).
```

After obtaining `lambda=0`, the paper's `mu=0` stationary branch has
`y_i=-1/2`, with the `x_i` and `u_j` unrestricted by the stationarity
equations. It computes `f=-l/4`, calls this a negative global maximum, and
uses it to bound the designated point. That classification does not follow
from stationarity and is explicitly false on the paper's own constraint set.

Indeed, put every `y_i=-1/2` and define

```text
C = pi(D) + 3*l/4 + l1 > 0.
```

Set all `x_i,u_j` except one `x_1` to zero and choose

```text
x_1 = (-1 + sqrt(1+4*C))/2,
```

so `x_1^2+x_1=C`. Then `h=0`. Since `pi(D)>0`, choosing

```text
z = (x_1^2 + l/4) / pi(D)
```

also gives `g=0`. This is an explicit feasible point on the `mu=0` branch
with `f=-l/4<0`. It is only one feasible critical stratum, not a global upper
bound. The paper's separate `mu != 0` branch is asserted to have positive
objective value, which itself prevents the negative branch from being the
global maximum. Conversely, a positive stationary branch cannot be declared
the global minimum because the feasible branch just constructed has negative
objective value.

The missing global-extremum comparison is exactly the step needed to infer the
sign of `f` at the integer point representing the prime partition. Section 3's
instruction to treat the remainder “as in Section 2” inherits this failure.
Accordingly, this preprint does **not** establish Theorem 1.2, A109909, or
A109908.

## Gate decision

The direct theorem claim is neither ignorable nor a valid prior theorem stop.
It is classified:

```text
PUBLIC_PROOF_CLAIM_AUDITED_INVALID
```

The proposed modular finite-prefix lane remains mathematically eligible, but
only after a fresh race check and a corrected immutable freeze incorporating
all range, invertibility, proper-divisor, `Q>n/2`, compact-certificate, and
60-second replay requirements above. Until that freeze exists, the state is:

```text
TARGET_NOT_EVALUATED
```
