# OEIS A108081 shifted word-count development result

**Outcome:** `HOLD_BOUNDED` at word length `n=14`  
**Evidence split:** development, not held-out  
**Frozen upstream:** `google-deepmind/formal-conjectures@7a38c469ec329d0c97c068e03c58834f61628e7e`  
**Declaration:** `OeisA108081.count_words_in_x_is_a_shifted`

The one-step extension beyond the new `n=13` equality control does not cross
the conjecture's wall. The complete distinct-word closure at length 14 has

```text
Set.ncard (xN 14) = 16,438,345 = a 13.
```

An independently encoded implementation reproduced the same count. This is a
finite equality check only: it neither proves the universal statement nor
authorizes a counterexample claim, Lean disproof, release, issue, or PR.

## Why the enumeration is exact

`XWord.base` has length one. Every non-base derivation ends in exactly one of
`step_left` or `step_right`, whose two parent words have positive lengths that
sum to the child's length. Consequently, for fixed `n`, iterating every split
`i + j = n` with `1 <= i,j < n`, every word in the already-complete sets
`xN i` and `xN j`, and both constructors gives all and only length-`n`
`XWord`s. Hash-set deduplication then computes `Set.ncard` rather than the
number of derivations.

The primary implementation stores 14 signed coordinates. All coordinates at
length `n <= 14` lie in `[-(n-1), n-1]`, so `int8_t` is exact. Its sequence
function is a literal bounded translation of Lean's

```text
sum k in range (n+1), (n+k-1).choose k * fib (n-k+1),
```

including natural-number truncated subtraction. The independent audit instead
packs each coordinate into five bits and compares against fixed sequence
values. Five bits with offset 16 cover the admitted coordinate range. Thus the
second implementation changes the word representation, hash, and expected-
value path while preserving the root closure.

## Evidence accounting

The original machine-readable contract was frozen as development evidence
during the completed read-only trial. It is not a preregistered or held-out
contract. Its stop rule was followed: evaluate exactly through `n=14`, report
the result, and do not extend to `n=15`. No `n=14` computation was rerun while
packaging these artifacts.

The pre-contract pilot established the equality controls through `n=13` but
its exact source snapshot was superseded by the one-line loop-bound extension
to `n=14`. The pilot binary and raw evidence remain identified by digest; it is
used only as calibration evidence. The primary `n=14` source snapshot is
preserved exactly, as is the independently written packed audit.

| row | exact count | expected | result | wall | peak RSS |
|---|---:|---:|---|---:|---:|
| calibration `n=1..13` | through 4,227,273 | all equal | pass | 4.58 s | 239,748 KiB |
| primary `n=14` | 16,438,345 | 16,438,345 | equality | 21.04 s | 917,248 KiB |
| packed audit `n=14` | 16,438,345 | 16,438,345 | equality | 23.16 s | 1,263,448 KiB |

All three processes exited zero under the 60-second cap.

## Artifact digests

| artifact | SHA-256 |
|---|---|
| `oeis108081_n14_contract.json` | `ae00b4a53f2a390b06962b5bf4a277b6a8c9564d3bf992f5b824fdd46fd1884e` |
| `prospective_oeis108081_exact.cpp` | `4e60de1a12a2ae846a5bd60ddb5c889341313d27875c8337252ef3b5b79217ce` |
| historical primary `n=14` binary | `e1dec83c21991677b152ea74c40b0ef9961694d18a8bb23f73eb092304e5bb55` |
| `oeis108081_primary_n14.out` | `60987e1c36118366edd40528bf9eec64dd28d7ebc4fa08b10525ff0e6b46501f` |
| `oeis108081_primary_n14_resources.txt` | `bc1f7abab2902ebb611bcd6d106f6590d820ea600e11e6912a31dbd9b2a30eee` |
| `prospective_oeis108081_packed_audit.cpp` | `88f473aeba5ab107f852031c9b78fff6fd42b4fd503a68b450d9757f29850a2a` |
| historical packed-audit binary | `b07677955359054388a8be3dce73cadb0a06545f1b4f8f46c3317206471adf57` |
| `oeis108081_packed_audit_n14.out` | `5dfe413152dea20750fa8fd36faa948e5bd00e5e35ef2049e43d4644069aa119` |
| `oeis108081_packed_audit_n14_resources.txt` | `77d03d9649b4a3275aff3a9d5c8d6d2cfd6dc6554ea01a1cfc7c248dd6a455a9` |
| historical pre-contract pilot binary | `bace07830b23bc7321bcaef8b7057f39b94e6fd553e914e057affcdd2ff4365d` |
| `oeis108081_primary_precontract_n13.out` | `e6e47f2b0f76a7ee99b712a1b147e44dfb4365d16e5a0968cebea3434194ea67` |
| `oeis108081_primary_precontract_n13_resources.txt` | `8a534992f946df20ed13f3965312a7268ba4e84b7dec1f6df9394687cf15955b` |

## Method interpretation

This was the intended inexpensive one-off test: use the first equality control
immediately beyond the source's reported range as the carrier, then apply one
more exact recursive extension. The result is a useful calibrated zero. The
wall persists at `n=14`, and the next brute-force row is deliberately outside
this contract. Any future work should first extract structural compression or
a symbolic recurrence; merely spending more memory on `n=15` would not be a
new method step.
