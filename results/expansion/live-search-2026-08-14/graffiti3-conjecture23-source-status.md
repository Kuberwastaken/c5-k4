# Graffiti³ Conjecture 23: source and public-status attestation

**Audit date:** 2026-08-14 UTC  
**Disposition:** source-listed open; no public resolution located; DEVELOPMENT only

## Primary source lock

Randy Davila, *Graffiti³: Compact Theory Libraries for Automated Mathematical
Discovery*, Research Square version 1, DOI
[`10.21203/rs.3.rs-8493329/v1`](https://doi.org/10.21203/rs.3.rs-8493329/v1),
Conjecture 23 on PDF page 33, states:

```text
If G is a finite p-group, then

  k(G) <= (1/2)|G/G'| + (1/4)|G| + (1/2)|Z(G)|.
```

Here `k(G)` is the number of conjugacy classes, `G'` is the derived subgroup,
and `Z(G)` is the center. The downloaded PDF has SHA-256
`9758ec4530febf62bbcee35bd5804d2dda9e226a0878b082a25eaf1c7e4a9f7a`.
Crossref dates version 1 to 2026-01-19. The Research Square version-2 URL
currently returns `Resource not found`; no later source revision was located.

The source says that Appendix C lists conjectures which remained interesting
or not easily falsifiable after the paper's adversarial checks. Its group
snapshot contains every SmallGroup of order at most 128. Conjecture 23 is
therefore treated as a source-listed open, snapshot-true statement, not as a
theorem or a formally reviewed declaration.

## Dated duplicate and status search

The 2026-08-14 audit searched the exact formula, title, DOI, `Conjecture 23`,
the invariant quartet, and equivalent commuting-probability language across:

- general and scholarly web indexes;
- GitHub code, commits, issues, and pull requests;
- every visible issue/branch of `RandyRDavila/TxGraffiti2` at
  `e37126da53b84150d142a5d61202b61f78521fcc`;
- `google-deepmind/formal-conjectures` at
  `9a1636c4030039f70cf78b866c216d8b6c5f35b0`;
- this repository's history, tags, releases, and live-search reports.

No proof, counterexample, erratum, or exact competing claim was found.
OpenAlex reported zero citations for the source record at the audit time.
This is a dated negative search, not an assertion of absolute priority; it
must be repeated after any candidate and before publication.

Graffiti³ Conjecture 23 is **not represented in DeepMind's repository**. This
lane must never be described as a DeepMind or Written on the Wall I target.

## Exact finite resolution shape

Multiply the proposed inequality by four and define

```text
W(G) = 2|G/G'| + |G| + 2|Z(G)| - 4k(G).
```

The conjecture says `W(G) >= 0`. One finite multiplication table of prime-power
order with independently certified center, derived subgroup, abelianization,
and conjugacy-class partition and with `W(G) < 0` is a complete disproof.

