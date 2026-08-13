import assert from 'node:assert/strict'
import crypto from 'node:crypto'
import fs from 'node:fs/promises'
import os from 'node:os'
import path from 'node:path'
import test from 'node:test'
import { fileURLToPath } from 'node:url'

import {
  INVOCATION_CONTRACT,
  LEGACY_CHAIN,
  assertUnlocked,
  canonicalJson,
  fetchOfficialResponses,
  profileFromC0,
  verifyRelayPair,
  writeExclusiveArtifact
} from '../fetch-and-verify-v12.mjs'

const here = path.dirname(fileURLToPath(import.meta.url))
const infoRaw = await fs.readFile(path.join(here, 'fixtures/legacy-round-1-info.json'), 'utf8')
const beaconRaw = await fs.readFile(path.join(here, 'fixtures/legacy-round-1-beacon.json'), 'utf8')
const info = JSON.parse(infoRaw)
const beacon = JSON.parse(beaconRaw)

function c0 () {
  return {
    schema_version: 'c5k4-c0-randomness-contract-1.2',
    phase: 'C0_FROZEN',
    chronology: {
      p0_artifact_commit: '1'.repeat(40),
      p0_attestation_commit: '2'.repeat(40),
      p0_published_at_utc: '2020-07-22T15:00:00Z',
      s0_acquired_at_utc: '2020-07-22T15:05:00Z',
      c0_artifact_commit: '3'.repeat(40),
      c0_attestation_commit: null,
      c0_published_at_utc: '2020-07-22T15:10:00Z'
    },
    published_at_utc: '2020-07-22T15:10:00Z',
    pool_file_sha256: '5'.repeat(64),
    quota_feasibility_sha256: '6'.repeat(64),
    randomness: {
      source: 'League of Entropy drand',
      chain_hash: LEGACY_CHAIN.chainHash,
      round: 1,
      round_closes_at_utc: '2020-07-22T15:17:30Z',
      value: null
    }
  }
}

function receipt (value) {
  const result = {
    schema_version: 'c5k4-c0-validation-receipt-1.2',
    c0t: { path: 'results/c0t.json', file_sha256: crypto.createHash('sha256').update(JSON.stringify(value)).digest('hex') },
    c0_artifact_commit: '3'.repeat(40),
    c0_attestation_commit: '4'.repeat(40),
    direct_nonmerge_parent_verified: true,
    committed_bytes_verified: true,
    c0_published_at_utc: value.chronology.c0_published_at_utc,
    future_round_close_at_utc: value.randomness.round_closes_at_utc
  }
  result.receipt_sha256 = crypto.createHash('sha256').update(canonicalJson(result)).digest('hex')
  return result
}

function validatedProfile (value = c0(), validation = null) {
  return profileFromC0(value, validation || receipt(value), JSON.stringify(value))
}

function pair () {
  return LEGACY_CHAIN.relays.map(url => ({
    url,
    infoRaw,
    beaconRaw,
    info: structuredClone(info),
    beacon: structuredClone(beacon)
  }))
}

test('publishes an exact P0-bindable invocation contract', () => {
  assert.deepEqual(INVOCATION_CONTRACT, {
    schema_version: 'c5k4-drand-fetch-invocation-contract-1.2',
    argv: ['--c0-contract', 'FILE', '--c0-validation-receipt', 'FILE', '--output', 'NEW_FILE'],
    network_after_contract_and_unlock_only: true,
    relay_count: 2,
    output_create_mode: 'EXCLUSIVE_NO_OVERWRITE'
  })
})

test('derives the dynamic round only from a valid future C0 contract', () => {
  const profile = validatedProfile()
  assert.equal(profile.round, 1)
  assert.equal(profile.roundClosesAtUtc, '2020-07-22T15:17:30Z')
  assert.equal(profile.chainHash, LEGACY_CHAIN.chainHash)
})

test('rejects circular C0T identity and unbound validation receipts', () => {
  const circular = c0()
  circular.chronology.c0_attestation_commit = '4'.repeat(40)
  assert.throws(() => validatedProfile(circular), /cannot contain its own commit/)
  const value = c0()
  const tampered = receipt(value)
  tampered.direct_nonmerge_parent_verified = false
  assert.throws(() => profileFromC0(value, tampered, JSON.stringify(value)), /(digest does not replay|does not bind)/)
})

test('rejects a populated value, nonfuture close, or wrong legacy chain before I/O', () => {
  const populated = c0()
  populated.randomness.value = '00'.repeat(32)
  assert.throws(() => validatedProfile(populated), /must be null/)
  const nonfuture = c0()
  nonfuture.chronology.c0_published_at_utc = nonfuture.randomness.round_closes_at_utc
  nonfuture.published_at_utc = nonfuture.randomness.round_closes_at_utc
  const nonfutureReceipt = receipt(nonfuture)
  nonfutureReceipt.c0_published_at_utc = nonfuture.randomness.round_closes_at_utc
  assert.throws(() => validatedProfile(nonfuture, nonfutureReceipt), /not future/)
  const wrongChain = c0()
  wrongChain.randomness.chain_hash = '0'.repeat(64)
  assert.throws(() => validatedProfile(wrongChain), /not legacy mainnet/)
})

test('refuses network access before unlock', async () => {
  const profile = validatedProfile()
  let calls = 0
  const fetcher = async () => { calls += 1; return '{}' }
  await assert.rejects(
    fetchOfficialResponses(profile, fetcher, new Date('2020-07-22T15:17:29.999Z')),
    /network disabled/
  )
  assert.equal(calls, 0)
  assert.throws(() => assertUnlocked(profile, new Date('2020-07-22T15:17:29.999Z')), /network disabled/)
})

test('accepts an offline two-relay historical vector with BLS and hash verification', async () => {
  const profile = validatedProfile()
  const artifact = await verifyRelayPair(pair(), profile, new Date('2020-07-22T15:17:31Z'))
  assert.equal(artifact.randomness, beacon.randomness)
  assert.equal(artifact.round, 1)
  assert.equal(artifact.c0_binding.artifact_commit, '3'.repeat(40))
  assert.equal(artifact.verification.bls_signature, true)
  assert.equal(artifact.signature_sha256, beacon.randomness)
  assert.equal(
    artifact.beacon_canonical_sha256,
    '2ce7f1f6db69f0ad91d0dd35dfbfa538de6212d6d421d5165eb108c2b0de52c3'
  )
})

test('rejects relay substitution, disagreement, and wrong round', async () => {
  const profile = validatedProfile()
  const substituted = pair()
  substituted[1].url = 'https://example.invalid'
  await assert.rejects(verifyRelayPair(substituted, profile, new Date('2020-07-22T15:17:31Z')), /URL is not/)
  const disagreement = pair()
  disagreement[1].beacon.previous_signature = `00${disagreement[1].beacon.previous_signature.slice(2)}`
  await assert.rejects(verifyRelayPair(disagreement, profile, new Date('2020-07-22T15:17:31Z')), /(BLS verification failed|beacon mismatch)/)
  const wrongRound = pair()
  wrongRound[0].beacon.round = 2
  await assert.rejects(verifyRelayPair(wrongRound, profile, new Date('2020-07-22T15:17:31Z')), /returned round/)
})

test('exclusive artifact writing refuses to overwrite evidence', async () => {
  const directory = await fs.mkdtemp(path.join(os.tmpdir(), 'c5k4-drand-v12-'))
  const output = path.join(directory, 'beacon.json')
  try {
    await writeExclusiveArtifact(output, { frozen: true })
    await assert.rejects(writeExclusiveArtifact(output, { frozen: false }), error => error.code === 'EEXIST')
    assert.deepEqual(JSON.parse(await fs.readFile(output, 'utf8')), { frozen: true })
  } finally {
    await fs.rm(directory, { recursive: true })
  }
})
