# Bondy v3.4 enabled result

- Classification: `VERIFIED_CAP_PREFIX`
- Exact freeze commit: `657a3bc64f2a2fa844a80a0c238e166331af7230`
- Disabled gate run: `31855812545` (`success`)
- Enabled run: `31855904650` (`success`)
- Terminal: `CAP_PREFIX`
- Constructor rows reached: `22 / 96`
- Applicable rows reached: `10`
- Target rows completed: `9`
- Candidates: `0`
- Release: none

## Gate and activation

The separately dispatched disabled run passed the immutable v3.4 freeze,
64 target-free tests, exact source control, independent replay compilation,
and the complete live continuity gate. Its canonical attestation has 18/18
checks true. The single full changed-file catalogue, its two identity
surfaces, and their totals all contain exactly 274 open pull requests. The
exact target collision set is empty. Live upstream remained at commit
`2411d22e1bd550d050d0eac6c1fb379a76a3e7c5`, tree
`f6b52f1d3f63b365d6f8c405623d5f7a4e674efc`.

The disabled artifact is:

```text
id             9238992983
name           bondy-longest-cycles-development-v34-gate-evidence
archive digest sha256:1a7ab6231eaedc9f5e5d605275618d2c0848855ff007f69f7c8e2a2cee43a505
attestation    sha256:3f196c673a8d697adf784ced93d022a6c694e591ad205354e8fcc05a3e9248cd
```

After that artifact was independently checked, the rotated repository secret
was configured and one enabled run was dispatched at the same immutable
commit. Its pre-target gate passed again. The fresh post-target safeguard has
7/7 checks true, including an unchanged complete PR binding surface, unchanged
main/target/declaration, and no exact target collision.

## Exact capped observation

The target process ran for 49 seconds under the frozen 48/54/60-second
boundaries. It serialized 22 constructor rows: 10 were applicable and 12 were
ordinary-isomorphic duplicates. Nine applicable rows completed the endpoint
path-cover DP before finalization; the tenth applicable row was constructed
but not evaluated.

All nine completed rows have the same exact rejection shape:

```text
classification = Q4_UPPER_BOUND_REJECTED
candidate = false
X = []
pc(H - X) = pc(H) = 1
```

Thus each completed peripheral graph `H` itself has a spanning path, which is
already enough to reject that row. Individual evaluations took 5.015--5.294
seconds. No completed row reached a candidate certificate.

The canonical terminal records `applicable=10`, `evaluated=9`, ledger head
`64ea4f24fe298f7d4c2171379da73065ace468effa1790a376a2133c8587820c`,
and status `CAP_PREFIX`. The independent verifier replayed all 33 ledger rows
and returned `TERMINAL_VERIFIED`; a second local replay reproduced that
verdict. `CAP_PREFIX` is not a bounded hold, domain exhaustion, counterexample,
or evidence for the universal statement.

## Enabled evidence

```text
artifact id     9239036406
artifact name   bondy-longest-cycles-development-v34-enabled-evidence
archive digest  sha256:b1aa0593b7d71df18a55fc9bdab2a92382092ec829fbe90fa2558ce333b05604
manifest        sha256:fc691931d7572aaf1ea7ea76e78edd47ede76b4cb4a1c79fbcd85ad870d57ae7
ledger          sha256:f9ac2cecc2974653eaf73f4acd583b561dcf6cac5e3e1b9c8b3319fa2f49e9e3
source gate     sha256:9d67b5adb79c3b441b2c2dc553129af814ce6fe88df88b619531f9dd714d6f73
post safeguard sha256:bbb004f3abece13c52a769275b57dee5108325c0c02f390dc9a8f3bc647fab85
terminal        sha256:7323560ba83452362294272088afe57a0e6eb2a8f9c289bb2111bb5c6c1bc247
verification    sha256:79b735acf5b35811e0ea730c5d706a313c67a9a2bfbb16a7402be9c46ebb667b
```

The enabled evidence manifest binds all five required files; independent
recomputation found zero byte-count or SHA-256 mismatches.

## Cancelled dispatch receipt

Run `31855803325` was cancelled immediately because its disabled dispatch
carried an incorrect campaign input string. Cancellation reached it during
checkout: every freeze, gate, target, verifier, and evidence step was skipped,
and GitHub reports zero artifacts. It is
`INVALID_DISPATCH_INPUT_CANCELLED`, not an attempted scientific run.

## Standing and next diagnostic

This run produces no release. Its useful information is algorithmic and
structural: the first nine applicable rows were rejected by the cheapest
possible deletion set, `X=[]`, but the frozen evaluator still built the full
endpoint table before exposing that fact. A future version may consider an
independently replayable exact spanning-path prefilter while preserving the
same 96-row grammar and all caps. That change requires a new audit and freeze;
the present prefix cannot be silently extended or relabelled.
