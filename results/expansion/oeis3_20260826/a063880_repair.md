# A063880 — round-2 opportunity DEVELOPED: partial repair + wrong-tag finding

**Class: PARTIAL REPAIR CANDIDATE + STATUS-SYNC (tag overstatement).
Gates: a ✓, b ✓, c ✓ (exact, 281 terms ≤ 100000), d ✓.**

## The two recorded items (from round 2)

1. `a_of_primitive_mul_squarefree` — category **textbook**, body `sorry`.
2. `exists_primitive_of_a {n} (h : A n) : ∃ m s, IsPrimitiveTerm m ∧
   Squarefree s ∧ m.Coprime s ∧ n = m * s` — category **research solved**,
   body `sorry`.

## Item 1 is PROVABLE in one line → complete repair candidate

For q prime with q ∤ n:
- σ(n·q) = σ(n)(q+1)
- usigma(n·q) = usigma(n)(1+q^1) = usigma(n)(q+1)

(unitary divisors of n·q split as U(n) ⊔ q·U(n)). Hence
σ(nq)/usigma(nq) = σ(n)/usigma(n), so A(n) ⟹ A(n·q); iterate over the primes
of the squarefree s. In Lean: unfold `usigma` over `unitaryDivisors`, use
`Finset.prod_union`/multiplicativity of `ArithmeticFunction.sigma` on coprime
factors. **Closable; no sorry needed.**

## Item 2: research-solved tag is NOT justified by what can be proven

Mathematical analysis (`scripts/a063880_kernel.py`, log `a063880_run2.log`):

- For ANY n there is always a structural decomposition n = m·s with s
  squarefree, gcd(m,s)=1 (m := powerful kernel ∏ p^max(e_p,2)-part). The real
  CONTENT of exists_primitive_of_a is therefore: **the powerful kernel of a
  term is again a (primitive) term**, plus minimality of that primitive.
- This does NOT follow from A's definition by pure logic: removing an
  exponent-1 prime multiplies the ratio σ/usigma by (1+q^e)^{-1}(q+1) ≠ 1 in
  general; nothing forces the ratio back to exactly 2.
- Empirically TRUE here: all **281 terms ≤ 100000** satisfy both the
  min-divisor decomposition shape AND the powerful-kernel-is-a-term property;
  unique primitive = 108; closure spot-checks (30 random term×prime pairs) all
  consistent.

OEIS page (%I #39 Aug 31 2024) states "All the other terms are of the form m*s,
where m is primitive (powerful) and s is a squarefree number coprime to m"
as a %C fact, but its sibling comments hedge computationally ("Numbers SO FAR
are all ≡108 mod 216 [confirmed up to 10^7]", "The only primitive term BELOW
10^18 is 108"). The Lean tag `research solved` imports OEIS's fact-tone for a
statement whose published evidence is bounded computation.

## Verdict

- Item 1: fillable now (proof above).
- Item 2: **wrong-tag candidate** — honest category is research-open (or
  conditional on the unproven structure claim). At minimum the file should not
  carry both `research solved` and a `sorry` while its own `unique_primitive_108`
  and `mod_216_of_a` are open.
