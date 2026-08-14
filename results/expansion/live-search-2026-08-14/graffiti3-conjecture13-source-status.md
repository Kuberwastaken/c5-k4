# Graffiti³ Conjecture 13: source/status attestation

Date: 2026-08-14 UTC. Status: **source-listed open; DEVELOPMENT only**.

Randy Davila, *Graffiti³: Compact Theory Libraries for Automated Mathematical
Discovery*, Research Square v1, DOI `10.21203/rs.3.rs-8493329/v1`, prints on
PDF page 24:

```text
Fix a base b >= 2 (empirically b=2). If phi(n) <= (9/19)n,
then n is not a Fermat pseudoprime to base b.
```

The layout places `9` above `19`; the exact premise is `19*phi(n) <= 9*n`.
The PDF SHA-256 is
`9758ec4530febf62bbcee35bd5804d2dda9e226a0878b082a25eaf1c7e4a9f7a`.
The paper reports its integer snapshot through `2*10^6`; target evaluation is
therefore restricted to `n>2,000,000`.

The 2026-08-14 audit searched the exact coefficient/formula, DOI/title,
Conjecture 13, totient-ratio variants, Fermat-pseudoprime literature, GitHub,
the author repository, `formal-conjectures`, and this repository's history and
releases. It found no proof, counterexample, erratum, or competing exact claim.
The statement is not in DeepMind's repository. This is a dated negative search,
not absolute priority, and must be repeated after a candidate.

For base two, one finite disproof certificate is a composite odd `n>2,000,000`
with a complete prime factorization, `pow(2,n-1,n)=1`, and
`19*phi(n)<=9*n`.
