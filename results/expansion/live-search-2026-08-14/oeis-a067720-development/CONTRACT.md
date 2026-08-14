# OEIS A067720 composite-successor profile DEVELOPMENT freeze

**State:** frozen harness, not evaluated, not dispatched

**Target:** `OeisA67720.prime_add_one_of_a` at
`google-deepmind/formal-conjectures@05ea0345d09375efac830fac93bf083b654e317e`

This is a development-set trial under `METHOD.md`. It is not held out. This
contract freezes the complete construction before any non-control target
residual is evaluated. A later run may end in a bounded zero, a cap prefix, a
gate failure, or one finite candidate. None of those outcomes may change the
catalogues below.

## Literal certificate

Put `s=k+1` and `m=k^2+1=s^2-2s+2`. The declaration is false exactly when
there is a `k != 8` such that

```text
R(k) = phi(m) - k*phi(s) = 0
```

and `s` is composite. A candidate certificate contains `k,s,m`, ordered
complete prime factorizations of both endpoints, the two exact totient
products, `R=0`, a proper prime divisor of `s`, and proof that `k` is neither
the known exception nor a source-table row. Deterministic 64-bit primality and
integer products independently replay every factor. One witness suffices.

The reading is `UNAMBIGUOUS`. There is no answer placeholder, eventual
quantifier, or unbounded auxiliary certificate.

## Source, status, novelty, and database-sanity gate

The workflow checks out an exact 40-hex campaign commit. Before construction
it downloads and verifies:

1. the pinned Lean module and its live-`main` copy;
2. the OEIS source at exact `oeisdata` commit
   `8872fa543438401edd424a57b67ad5e0737bebfb`;
3. the exact 10,000-row b-file through `(10000,1548870)`; and
4. a fresh authenticated GitHub audit of upstream/local exact searches and
   every open upstream PR changed-file list (including rename source paths),
   and every page of local releases through a short final page.

The live gate binds the exact four search strings, completeness flags, result
counts, and known item roles. It fails on upstream-head drift,
source/status/hash drift, a new search result outside the frozen known items,
any target-path PR (including a renamed-away source path) other than the
exact pinned non-resolving #4198/#4688 tuples, any head/content/classification
drift in those tuples, or any local issue/PR/release match. The
source gate independently checks every b-file row. It proves exact equality,
proves both endpoints prime on all 9,999 nonexceptional rows, and replays
`9=3^2`, `65=5*13`, `phi(65)=48=8*phi(9)` on the sole exception. Thus the
entire source table is both a database-sanity control and an exclusion set.

The ingestion PR 1878 is required to remain merged at its frozen merge commit;
the unrelated issue 1456 must remain closed and non-PR. Open PR 4198 is bound
by head and file hash as a stale
normalization whose target remains literally open with `sorry`; open PR 4688
is similarly bound as module/import maintenance with an unchanged target.
Batch history 4450 does not resolve the theorem. Any head, content, status, or
classification change stops the lane for manual review; the contract is never
weakened.

## Theorem subtraction and wall

The module already proves that prime `k+1` and prime `k^2+1` imply `R=0`.
Those rows are theorem-baseline controls, not candidates. The OEIS table has
one composite-successor wall point, `k=8`. The separating coordinate is
therefore not magnitude or a longer prefix: it is the ordered exponent profile
of composite `s`, coupled through the rigid translation to a factored `m`.

The search is a two-profile meet-in-the-middle construction. It never scans
flat `k` values and never factors an arbitrary translated endpoint. A residual
is evaluated only after the exact integer `m=s^2-2s+2` occurs in the frozen
endpoint-factor catalogue, so both complete factorizations precede evaluation.

## Immutable catalogues

All primes are indexed from one in increasing order.

- `s <= 2,000,000,001`; equivalently `k <= 2,000,000,000`.
- Successor primes are the first 512 primes.
- `SUCCESSOR_PROFILE_SURGERY` owns exactly `s=q^e`, `e=2..12`.
- `TOTIENT_RATIO_WALL` owns exactly `s=q^e r^f`, `q<r`, for exponent pairs
  `(1,1),(1,2),(2,1),(2,2),(1,3),(3,1)`.
- Endpoint primes are the first 768 primes.
- The endpoint catalogue contains `p^a`, `a=1..16`, and `p^a t^b`, `p<t`,
  with the same six exponent pairs, subject to
  `m <= 2,000,000,000^2+1`.

The arms are disjoint by the number of distinct successor primes. Canonical
profile order is signature, prime ranks, then exponents. The zero-based
canonical successor ordinal belongs to `ordinal mod 24`; there are 24 shards.
The source rows and `k=8` are controls even if their coordinates recur.

A target-free pre-freeze benchmark constructs only the endpoint catalogue: it
contains exactly 1,771,382 entries and has canonical stream SHA-256
`36fde67d9061e145ad13433ee3970b389a1b89fec68383d05d86cc5ec66aba9f`.
It completed locally in 11.50 seconds under the separately frozen 48-second
catalogue-only cap, without performing a translation lookup or residual
evaluation. The successor-only streams contain 824 and 269,943 eligible
profiles respectively; their counts and hashes are pinned in `manifest.json`.

No prime rank, exponent, value ceiling, signature, factor backend, arm, shard,
or translation rule may be added after a result. An extension is a new trial.

## Output and stop discipline

Every worker has a 48-second in-process horizon, a 54-second external process
cap, and a separate 60-second independent verifier cap. The workflow itself
also carries finite job timeouts. No ILP or unbounded child process exists.

Each worker creates a new append-only JSONL ledger and fsyncs a hash-chained
checkpoint every 128 constructed successor profiles, plus its initial and
final prefix. A candidate is written by fsync-and-rename as the atomic state
commit; no ledger write follows it. The terminal binds the ledger byte hash,
row-chain tail, exact visited prefix, stop counts, gate attestation, arm,
shard, and campaign commit. Valid terminal reasons are
`DOMAIN_EXHAUSTED`, `CAP_PREFIX`, `CERTIFICATE_FOUND`, and `WORKER_ERROR`.
External timeout without a verifiable terminal is retained as an incomplete
artifact and cannot be called a bounded zero.

The independent verifier separately generates the prime/profile catalogues,
replays the exact prefix and stop partition, checks domain exhaustion, and
recomputes every candidate product, primality predicate, totient, residual,
proper divisor, source exclusion, and coordinate ownership. Probable primes,
unmatched ratios, incomplete profiles, and a bare residual are never
certificates.

## Frozen interpretation of outcomes

- first new exact equality: `CERTIFICATE_FOUND`, pending all independent and
  publication gates;
- exact shard completion without equality: contributes only to
  `HOLD_BOUNDED` after all 48 shards independently replay;
- deadline: `CAP_PREFIX`, never exhaustion;
- control/source hit: logged as `KNOWN_EXCEPTION_CONTROL` or
  `CATALOGUE_CONTROL` and never promoted;
- source/status/duplicate drift: `GATE_FAIL` before construction;
- any implementation/contract mismatch: `PROTOCOL_DEVIATION`, with artifacts
  preserved.

This freeze authorizes no issue, pull request, release, README claim, tag, or
publication.
