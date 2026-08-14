# Graffiti³ energy Conjecture 3: DOI-qualified source/status attestation

Status: **MULTI_READING; LITERAL READING DEVELOPMENT-ELIGIBLE**

Audit date: 2026-08-14 UTC

This record concerns only Conjecture 3 on page 9 of Randy Davila,
*Graffiti³: Compact Theory Libraries for Automated Mathematical Discovery*,
Research Square `rs-8493329/v1`, DOI
[`10.21203/rs.3.rs-8493329/v1`](https://doi.org/10.21203/rs.3.rs-8493329/v1).
It must be called **Graffiti³ energy C3** or identified by this DOI. It is not
the older TxGraffiti product Conjecture 3 (`gamma_t(G square H) >= gamma(G x H)`),
which has a separate active campaign in this repository.

## Printed statement

For a nontrivial connected planar graph of diameter at most three, the paper
prints

```text
round(Energy(G)) >= 3 * sum_{uv in E(G)} 1/sqrt(d2(u)*d2(v)).
```

The preceding prose defines `d2(u)` as the number of vertices within distance
at most two of `u`. The literal graph-distance reading includes `u`, since
`dist(u,u)=0`. The paper does not specify how exact half-integer energies are
rounded.

## Source lock

- Research Square PDF SHA-256:
  `9758ec4530febf62bbcee35bd5804d2dda9e226a0878b082a25eaf1c7e4a9f7a`.
- Current author repository audited at
  `RandyRDavila/TxGraffiti2@e37126da53b84150d142a5d61202b61f78521fcc`.
- Published `expressive_graph_data.csv` Git blob:
  `bc52f0bb8314b3047091863d1931b05fb3024479`.
- Downloaded CSV SHA-256:
  `4f455fbfe1149c2ca952b429c7ca9d9c1aae192309fbb642be2b12a345526e97`.
- The CSV has 335 rows; 97 are flagged connected, planar, and diameter at
  most three. Its scalar columns contain zero reported violations and nine
  equality row ids: `19,33,52,65,75,159,172,174,263`.

## Reading reconciliation and database gate

The table values reveal a source/implementation split. On every diameter-two
row, its `reciprocal_randic_index_2_degree` behaves as though the center were
removed from the radius-two ball. Under that reading:

- `K2` has rounded energy `2`, while the right side is `3`;
- `K3` has rounded energy `4`, while the right side is `9/2`.

Both graphs satisfy every printed hypothesis and are unavoidable historical
controls. The center-excluding reading is therefore `DB_REJECTED`; the nine
published equality rows are calibration evidence for that implementation,
not equality evidence for the literal statement.

The literal closed-ball reading passes all 995 connected Graph Atlas graphs
of orders two through seven with the standing `1e-6` spectral guard. It has no
Atlas equality; its least gap is `1/2` on `K2`. Development search may proceed
only against this literal reading. Every candidate must also report the
rejected reading, and must isolate energy strictly inside one rounding shelf,
so both half-up and ties-to-even conventions return the same integer.

## Current status and duplicate audit

The v1 preprint calls the inequality sharp on its evidence base and supplies
no proof. Searches on 2026-08-14 covered:

- exact fragments of the displayed formula and the full planar/diameter
  hypothesis;
- `"TxGraffiti" graph energy planar diameter`, `d2(u)d2(v)`, the DOI, and
  Conjecture 3 together with graph energy;
- general web and scholarly results;
- GitHub code, commits, issues, and pull requests;
- every branch-visible issue in `RandyRDavila/TxGraffiti2`;
- `google-deepmind/formal-conjectures`;
- this repository's full history, tags, and releases.

No proof, counterexample, erratum, or exact competing claim was found. This is
a dated negative search, not a priority guarantee. Novelty must be rerun after
any candidate and before any public claim.

## Scope

This statement is not represented in `formal-conjectures`. It is an external
DEVELOPMENT lane and cannot enter the current formal-conjectures method
denominator without an explicit scope change. No upstream issue or pull
request is authorized by this freeze.
