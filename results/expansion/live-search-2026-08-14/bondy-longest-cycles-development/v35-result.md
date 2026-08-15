# Bondy v3.5 enabled result

- Classification: `VERIFIED_FROZEN_DOMAIN_EXHAUSTION`
- Exact freeze commit: `3be87c143b41f455346087786b02faa12ca548df`
- Disabled gate run: `31857412193` (`success`)
- Enabled run: `31857501706` (`success`)
- Terminal: `DOMAIN_EXHAUSTED`
- Constructor rows: `96 / 96`
- Applicable nonisomorphic rows: `22`
- Target rows completed: `22 / 22`
- Candidates: `0`
- Release: none

## Scope and provenance

V3.5 is a target-informed, contaminated `DEVELOPMENT` continuation of the
v3.4 `CAP_PREFIX`. It restarts from row zero and preserves the exact same
96-row constructor grammar, order, theorem subtraction, duplicate rules,
target predicate, and 48/54/60-second caps. Its only algorithm change is a
bounded positive-only Hamiltonian-path witness search before the unchanged
endpoint path-cover DP. A miss is inconclusive and falls through to that DP;
only a replayable spanning path can reject early.

The separately dispatched disabled run passed the immutable v3.5 freeze, all
69 target-free tests, exact source control, independent C++ compilation, and
the complete live continuity gate. Its canonical attestation has 18/18 checks
true. All three open-pull surfaces contain exactly 275 identities/bindings,
and the exact target collision set is empty.

```text
disabled artifact id      9239477316
disabled archive digest   sha256:788edf29164c8de2a0cd90b6736d96102c4824578497952b5096a521e9aae4f2
disabled attestation      sha256:32fc56ca81e9aa88fd6a627895d8a63c78a67a85ef503e6341167ade325f3124
```

The enabled run repeated the gate at the same immutable commit. Its fresh
post-target safeguard has 7/7 checks true: upstream main, the exact target
blob and declaration, all status identities, and the complete changed-file
binding surface remained unchanged, with no exact target-path collision.

## Exhausted frozen result

The target process serialized every one of the 96 constructor rows. Exact
ordinary-isomorphism filtering classified 74 as duplicates and retained 22
applicable rows at indices

```text
0, 2, 3, 5, 6, 8, 12, 15, 18, 21, 23, 33, 35, 48, 50, 51, 53, 54, 60, 62, 63, 65.
```

All 22 applicable rows completed target evaluation. Each produced a canonical
20-vertex spanning path after exactly 20 deterministic DFS expansions and was
classified

```text
HAMILTONIAN_PATH_UPPER_REJECTED
X = []
pc(H) = 1
candidate = false
```

The independent verifier reconstructed every peripheral graph, replayed every
path edge-by-edge, checked canonical reversal and exact vertex coverage, and
replayed the full constructor/duplicate ledger. The 120-record chain ends at
`24a7ed9a418b8eb5145069b7c0ad4100a5f2cc46e61bdd15f8ced454f80bbba1`.
Both the workflow verifier and a second local verifier returned
`TERMINAL_VERIFIED / DOMAIN_EXHAUSTED`.

This is a complete bounded zero for the frozen 96-row balanced-rewiring
grammar. It is not evidence that the Bondy declaration is true outside that
grammar, and it is not a counterexample, release, issue, or pull request.

## Enabled evidence

```text
artifact id     9239509231
artifact name   bondy-longest-cycles-development-v35-enabled-evidence
archive digest  sha256:ec031e084968ca090ae2815070abdcc8b61e7860f38d133eeb07aa323896a090
manifest        sha256:2a4432487c6bb7752ec5fbbb41b300a7257ee67d4514355fd84168f4aa18f62f
ledger          sha256:e640ce495ad6be29b89b60ab444790c5fa2fdf16ae80afc13082d309325889fd
source gate     sha256:8f2ec1265c569d9f9e3bca01b0585cb71ef53506b9d2817e74cf771d63926614
post safeguard sha256:080a7061edb6e7ba55f0414ab5ea811cb4b208304b40d377cf335c1d390bfff5
terminal        sha256:abdde8ad5483a280091f64e42895533dd0d91b0f18667f2dedb4b516a756ce88
verification    sha256:88ed00d6521e5c4b02cfa54d2dcb27d9eead1d55a35de0e5b1d62a7fadffa8b6
```

The enabled evidence manifest binds all five required files. Independent
recomputation found zero byte-count or digest mismatches.

## Method consequence

The v3.4 observation led to a certificate-preserving evaluator improvement,
and the next immutable run converted a 22-row prefix into exact exhaustion of
the unchanged 96-row domain. Scientifically, the result retires this balanced
rewiring catalogue and exposes a strong local theorem signal: every one of its
22 nonisomorphic applicable peripheral graphs is traceable. Any next Bondy arm
must introduce a prospectively justified structural coordinate that can
destroy traceability; merely expanding this catalogue or rerunning the same
grammar is prohibited by the stop rule.
