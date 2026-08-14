# Method v1.5 P0A → P0T → A0 offline publication contract

Status: repository-only contract. It performs no network request, Git push,
cloud mutation, key generation, or signature issuance. Following these steps is
not evidence that any step occurred.

## Frozen chronology

1. Before P0A, obtain the hashes of at least two independently controlled
   Ed25519 authority public keys and the domain-separated policy/template
   digest for `benchmark-attestable-ami-authority-binding-v1.5`. This is not the
   live AMI binding: the later live binding must bind the exact A0 commit, tree,
   and artifact and therefore cannot be hashed into A0 without a cycle.
2. In an offline clone, create P0A with `build_benchmark_v15_p0_a0.py p0a`.
   The component list must equal the closed ten-file P0/A0 implementation and
   test set plus the five frozen AMI policy components. Components are read
   from one exact base commit, sorted, target-audited, and bound by Git blob
   IDs, SHA-256 digests, and a canonical closure digest. The publication
   verifier independently repeats this audit from the base commit bytes.
3. Commit only `results/benchmark/v1.5-p0-a0/P0A.json`. P0A's sole parent must
   be the exact embedded base commit. Publish only by a normal non-force push
   to the dedicated `method-v1.5-p0` branch.
4. An independent read-only observer captures the successful first attempt of
   the pinned GitHub Actions workflow with `--stage actions-observation`, exact
   commit, artifact kind, and server run ID. The verifier replays the live run,
   workflow-run listing, and canonical public ref through GitHub's API; requires
   the exact repository name and numeric ID, workflow path and committed blob,
   push event, branch/ref, head SHA, unique first attempt, successful
   conclusion, and ordered server times; and recomputes raw-response and
   bounded-projection digests. The listing query is pinned to exact `head_sha`,
   every page implied by the bounded server `total_count` is fetched, and
   uniqueness is decided only after full pagination. Do not place API tokens, raw responses, logs,
   secrets, or target data in the receipt.
5. Create P0T with `build_benchmark_v15_p0_a0.py p0t`. The builder live-replays
   the independent P0A observation and cannot synthesize a receipt. Commit only
   P0T as the sole-parent child of exact P0A; publish normally; then independently
   capture P0T's first-attempt Actions receipt by the same procedure. P0A and
   P0T must have distinct runs and P0A completion must precede P0T creation;
   batching both commits into one push cannot satisfy the contract.
6. Create A0 with `build_benchmark_v15_p0_a0.py a0-draft` only as a local
   validation preview. **Do not commit or publish the draft.** The repository
   builder always emits
   `NONAUTHORITATIVE_DRAFT_AWAITING_EXTERNAL_NITROTPM_KEY_AND_SIGNATURES`, and
   the publication validator rejects that status at a Git commit.

## Fail-closed activation ceremony

The draft A0 is not a publication or activation boundary. It must be discarded,
not upgraded in a later child commit. Only after all of the following facts
independently exist may the external ceremony assemble authoritative A0 bytes:

- a controlled-host Ed25519 verification-key hash whose private key was
  generated and remains sealed under the frozen NitroTPM PCR policy;
- the exact P0A-frozen AMI authority-binding policy/template digest;
- an external NitroTPM key-generation attestation digest for that sealed key
  (not the post-A0 live authority binding);
- at least the P0A-frozen threshold of distinct Ed25519 signatures over
  `b"c5k4-method-v1.5-a0-authority-signature-1.0\0" ||
  bytes.fromhex(a0_payload_sha256)`; and
- offline public-key bytes whose SHA-256 values match the exact authority
  roster frozen in P0A.

The authoritative artifact also contains `a0_authorized_at_utc`. It is inside
the threshold-signed activation payload and must follow the authenticated P0T
publication completion; Git author/committer time is never chronology evidence.

The repository builder intentionally has no authoritative-A0 command. An
independent ceremony may assemble the authoritative artifact only after those
facts exist. It must commit that authoritative A0 directly as the one-path,
sole-parent child of exact P0T; there is no committed draft and therefore no
sibling, rewrite, or draft-upgrade commit. Validate it offline with:

```text
python3 scripts/verify_benchmark_v15_p0_a0_publication.py \
  --stage a0 --commit <exact-a0-commit> --require-authoritative \
  --authority-keys <offline-public-keys.json>
```

After the A0 observer run completes, capture it with `--stage
actions-observation --artifact-kind A0`. Produce the downstream closed identity
projection with `--stage a0 --print-identity`, the same offline authority keys,
and `--publication-receipt <a0-publication-receipt.json>`.

The offline key file has the closed form
`{"schema":"c5k4-method-v1.5-offline-a0-authority-keys-1.0","keys":[...]}`
and is verification input, not a repository artifact. The validator performs
only read-only GitHub replay and never accepts caller-supplied authority keys unless their raw-byte
hashes match P0A's frozen roster. Missing, duplicate, substituted, or invalid
keys/signatures fail closed.

Post-A0 live verifiers must call `validated_a0_identity(...)` or the CLI with
`--print-identity`, the offline keys, and an independently captured A0
publication receipt. A0 uses the same first-attempt observer workflow, but its
workflow job performs only the closed structural publication gate; the later
identity validation performs the actual threshold signature verification and
live API replay of the embedded P0A receipt, embedded P0T receipt, and external
A0 publication receipt. Chronology uses only those replayed GitHub server
projections plus threshold-signed A0 authorization time; self-rehashed embedded
timestamps are not authority. That projection is derived from Git, not caller coordinates,
and binds the exact A0 commit, root tree, artifact bytes/canonical digest,
P0A-frozen authority-roster root, AMI policy/template digest, external harness
key hash, NitroTPM key-generation attestation/policy, signed authority time,
and GitHub-server A0 publication completion time. Downstream AMI/bootstrap
chronology uses the later publication completion boundary.

## Prohibitions

No force push, history rewrite, merge commit, multi-path stage commit, API
mutation by the builder or validator, credential publication, target identity, statement
text, ranking, semantic analysis, entropy, selection, or locally fabricated
operational claim is permitted. P0A, P0T, and draft A0 grant no P1, U1,
checkpoint, candidate, or experimental authority.
