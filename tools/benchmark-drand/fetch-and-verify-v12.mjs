#!/usr/bin/env node

/** Offline-testable, C0-driven public-randomness retrieval for Method v1.2. */

import crypto from 'node:crypto'
import fs from 'node:fs/promises'
import path from 'node:path'
import process from 'node:process'
import { fileURLToPath } from 'node:url'
import { fetchBeacon } from 'drand-client'

export const C0_SCHEMA_VERSION = 'c5k4-c0-randomness-contract-1.2'
export const ARTIFACT_SCHEMA_VERSION = 'c5k4-drand-randomness-artifact-1'
export const INVOCATION_CONTRACT = Object.freeze({
  schema_version: 'c5k4-drand-fetch-invocation-contract-1.2',
  argv: Object.freeze(['--c0-contract', 'FILE', '--c0-validation-receipt', 'FILE', '--output', 'NEW_FILE']),
  network_after_contract_and_unlock_only: true,
  relay_count: 2,
  output_create_mode: 'EXCLUSIVE_NO_OVERWRITE'
})
export const LEGACY_CHAIN = Object.freeze({
  source: 'League of Entropy drand',
  chainHash: '8990e7a9aaed2ffed73dbd7092123d6f289930540d7651336225dc172e51b2ce',
  publicKey: '868f005eb8e6e4ca0a47c8a77ceaa5309a47978a7c71bc5cce96366b5d7a569937c529eeda66c7293784a9402801af31',
  schemeID: 'pedersen-bls-chained',
  genesisTime: 1595431050,
  periodSeconds: 30,
  relays: Object.freeze(['https://api.drand.sh', 'https://api2.drand.sh'])
})

function sha256Hex (bytes) {
  return crypto.createHash('sha256').update(bytes).digest('hex')
}

function canonicalize (value) {
  if (Array.isArray(value)) return value.map(canonicalize)
  if (value !== null && typeof value === 'object') {
    return Object.fromEntries(Object.keys(value).sort().map(key => [key, canonicalize(value[key])]))
  }
  return value
}

export function canonicalJson (value) {
  return JSON.stringify(canonicalize(value))
}

function exactHex (value, length, where) {
  if (typeof value !== 'string' || value.length !== length || !/^[0-9a-f]+$/.test(value)) {
    throw new Error(`${where} must be exactly ${length} lowercase hexadecimal characters`)
  }
}

function utcMillis (value, where) {
  if (typeof value !== 'string' || !value.endsWith('Z')) throw new Error(`${where} must be an RFC 3339 UTC timestamp ending in Z`)
  const millis = Date.parse(value)
  if (!Number.isFinite(millis)) throw new Error(`${where} is not a valid timestamp`)
  return millis
}

/** Validate the frozen contract fully before callers are allowed to do I/O. */
export function profileFromC0 (c0, receipt, c0Raw) {
  if (c0 === null || typeof c0 !== 'object' || Array.isArray(c0)) throw new Error('C0 contract must be an object')
  if (c0.schema_version !== C0_SCHEMA_VERSION) throw new Error(`C0 schema_version must be ${C0_SCHEMA_VERSION}`)
  if (c0.phase !== 'C0_FROZEN') throw new Error('C0 phase must be C0_FROZEN')
  const chronology = c0.chronology
  if (chronology === null || typeof chronology !== 'object' || Array.isArray(chronology)) throw new Error('C0 chronology must be an object')
  const commitKeys = ['p0_artifact_commit', 'p0_attestation_commit', 'c0_artifact_commit']
  const chronologyKeys = [...commitKeys, 'c0_attestation_commit', 'p0_published_at_utc', 's0_acquired_at_utc', 'c0_published_at_utc'].sort()
  if (canonicalJson(Object.keys(chronology).sort()) !== canonicalJson(chronologyKeys)) throw new Error('C0 chronology has missing or unknown fields')
  for (const key of commitKeys) exactHex(chronology[key], 40, `C0 chronology.${key}`)
  if (chronology.c0_attestation_commit !== null) throw new Error('C0T cannot contain its own commit identity')
  if (receipt === null || typeof receipt !== 'object' || Array.isArray(receipt) || receipt.schema_version !== 'c5k4-c0-validation-receipt-1.2') throw new Error('valid C0 validation receipt is required')
  if (typeof c0Raw !== 'string' || receipt.c0t?.file_sha256 !== sha256Hex(Buffer.from(c0Raw, 'utf8'))) throw new Error('C0 validation receipt does not bind exact C0T bytes')
  const unsignedReceipt = Object.fromEntries(Object.entries(receipt).filter(([key]) => key !== 'receipt_sha256'))
  if (receipt.receipt_sha256 !== sha256Hex(Buffer.from(canonicalJson(unsignedReceipt), 'utf8'))) throw new Error('C0 validation receipt digest does not replay')
  exactHex(receipt.c0_attestation_commit, 40, 'validated external C0T commit')
  if (receipt.c0_artifact_commit !== chronology.c0_artifact_commit || receipt.direct_nonmerge_parent_verified !== true || receipt.committed_bytes_verified !== true || receipt.c0_published_at_utc !== chronology.c0_published_at_utc || receipt.future_round_close_at_utc !== c0.randomness.round_closes_at_utc) throw new Error('C0 validation receipt does not bind ancestry, bytes, and publication')
  const p0 = utcMillis(chronology.p0_published_at_utc, 'C0 chronology.p0_published_at_utc')
  const s0 = utcMillis(chronology.s0_acquired_at_utc, 'C0 chronology.s0_acquired_at_utc')
  const c0Published = utcMillis(chronology.c0_published_at_utc, 'C0 chronology.c0_published_at_utc')
  if (!(p0 < s0 && s0 < c0Published)) throw new Error('C0 chronology must satisfy P0T publication < S0 < C0T publication')
  if (c0.published_at_utc !== chronology.c0_published_at_utc) throw new Error('C0 publication timestamps disagree')
  exactHex(c0.pool_file_sha256, 64, 'C0 pool_file_sha256')
  exactHex(c0.quota_feasibility_sha256, 64, 'C0 quota_feasibility_sha256')

  const randomness = c0.randomness
  if (randomness === null || typeof randomness !== 'object' || Array.isArray(randomness)) throw new Error('C0 randomness must be an object')
  const expectedKeys = ['chain_hash', 'round', 'round_closes_at_utc', 'source', 'value']
  if (canonicalJson(Object.keys(randomness).sort()) !== canonicalJson(expectedKeys)) throw new Error('C0 randomness has missing or unknown fields')
  if (randomness.source !== LEGACY_CHAIN.source) throw new Error('C0 randomness source is not the frozen League of Entropy source')
  if (randomness.chain_hash !== LEGACY_CHAIN.chainHash) throw new Error('C0 randomness chain is not legacy mainnet')
  if (!Number.isSafeInteger(randomness.round) || randomness.round < 1) throw new Error('C0 randomness round must be a positive safe integer')
  if (randomness.value !== null) throw new Error('C0 randomness value must be null before retrieval')
  const closes = utcMillis(randomness.round_closes_at_utc, 'C0 randomness.round_closes_at_utc')
  if (closes <= c0Published) throw new Error('C0 randomness round is not future relative to publication')
  const derivedClose = (LEGACY_CHAIN.genesisTime + (randomness.round - 1) * LEGACY_CHAIN.periodSeconds) * 1000
  if (closes !== derivedClose) throw new Error('C0 round close does not match legacy-chain genesis, period, and round')
  return Object.freeze({
    ...LEGACY_CHAIN,
    round: randomness.round,
    roundClosesAtUtc: randomness.round_closes_at_utc,
    c0PublishedAtUtc: c0.published_at_utc,
    c0ArtifactCommit: chronology.c0_artifact_commit,
    c0AttestationCommit: receipt.c0_attestation_commit
  })
}

export function assertUnlocked (profile, now = new Date()) {
  if (now.getTime() < Date.parse(profile.roundClosesAtUtc)) {
    throw new Error(`network disabled until ${profile.roundClosesAtUtc}`)
  }
}

function validateInfo (info, profile, where) {
  if (info === null || typeof info !== 'object' || Array.isArray(info)) throw new Error(`${where} info is not an object`)
  const expected = {
    public_key: profile.publicKey,
    period: profile.periodSeconds,
    genesis_time: profile.genesisTime,
    hash: profile.chainHash,
    schemeID: profile.schemeID
  }
  for (const [key, value] of Object.entries(expected)) {
    if (info[key] !== value) throw new Error(`${where} info.${key} disagrees with the frozen legacy chain`)
  }
}

function validateBeaconShape (beacon, profile, where) {
  if (beacon === null || typeof beacon !== 'object' || Array.isArray(beacon)) throw new Error(`${where} beacon is not an object`)
  if (beacon.round !== profile.round) throw new Error(`${where} returned round ${beacon.round}, expected ${profile.round}`)
  exactHex(beacon.randomness, 64, `${where} randomness`)
  exactHex(beacon.signature, 192, `${where} signature`)
  exactHex(beacon.previous_signature, beacon.round === 1 ? 64 : 192, `${where} previous_signature`)
  if (beacon.randomness !== sha256Hex(Buffer.from(beacon.signature, 'hex'))) throw new Error(`${where} randomness is not SHA256(signature)`)
}

async function verifyBls (info, beacon, profile, where) {
  const options = {
    disableBeaconVerification: false,
    noCache: true,
    chainVerificationParams: { chainHash: profile.chainHash, publicKey: profile.publicKey }
  }
  const chain = { baseUrl: `offline:${where}`, info: async () => info }
  const client = {
    options,
    chain: () => chain,
    latest: async () => beacon,
    get: async round => {
      if (round !== profile.round) throw new Error(`${where} verifier requested an unexpected round`)
      return beacon
    }
  }
  try {
    await fetchBeacon(client, profile.round)
  } catch (error) {
    throw new Error(`${where} BLS verification failed: ${error.message}`)
  }
}

export async function verifyRelayPair (responses, profile, retrievedAt = new Date()) {
  if (!Array.isArray(responses) || responses.length !== 2) throw new Error('exactly two relay responses are required')
  if (retrievedAt.getTime() < Date.parse(profile.roundClosesAtUtc)) throw new Error('retrieval timestamp precedes the frozen round close')
  for (let index = 0; index < responses.length; index += 1) {
    const response = responses[index]
    const where = `relay ${index + 1}`
    if (response.url !== profile.relays[index]) throw new Error(`${where} URL is not the frozen official relay`)
    validateInfo(response.info, profile, where)
    validateBeaconShape(response.beacon, profile, where)
    await verifyBls(response.info, response.beacon, profile, where)
  }
  if (canonicalJson(responses[0].info) !== canonicalJson(responses[1].info)) throw new Error('official relay chain-info mismatch')
  if (canonicalJson(responses[0].beacon) !== canonicalJson(responses[1].beacon)) throw new Error('official relay beacon mismatch')

  const beacon = canonicalize(responses[0].beacon)
  return {
    schema_version: ARTIFACT_SCHEMA_VERSION,
    c0_binding: {
      artifact_commit: profile.c0ArtifactCommit,
      attestation_commit: profile.c0AttestationCommit,
      published_at_utc: profile.c0PublishedAtUtc
    },
    retrieval: {
      source: profile.source,
      retrieved_at_utc: retrievedAt.toISOString(),
      relays: responses.map(response => ({
        url: response.url,
        info_raw: response.infoRaw,
        info_raw_sha256: sha256Hex(Buffer.from(response.infoRaw, 'utf8')),
        beacon_raw: response.beaconRaw,
        beacon_raw_sha256: sha256Hex(Buffer.from(response.beaconRaw, 'utf8'))
      }))
    },
    chain: {
      hash: profile.chainHash,
      public_key: profile.publicKey,
      scheme_id: profile.schemeID,
      genesis_time: profile.genesisTime,
      period_seconds: profile.periodSeconds
    },
    round: profile.round,
    round_closes_at_utc: profile.roundClosesAtUtc,
    beacon,
    beacon_canonical_sha256: sha256Hex(Buffer.from(canonicalJson(beacon), 'utf8')),
    randomness: beacon.randomness,
    randomness_sha256: sha256Hex(Buffer.from(beacon.randomness, 'ascii')),
    signature_sha256: sha256Hex(Buffer.from(beacon.signature, 'hex')),
    verification: {
      c0_contract: true,
      future_round: true,
      exact_round: true,
      official_relay_equality: true,
      frozen_chain_info: true,
      bls_signature: true,
      randomness_equals_sha256_signature: true,
      drand_client_version: '1.4.2'
    }
  }
}

async function fetchText (url) {
  const response = await fetch(url, {
    headers: { accept: 'application/json' },
    redirect: 'error',
    signal: AbortSignal.timeout(30000)
  })
  if (!response.ok) throw new Error(`${url} returned HTTP ${response.status}`)
  return response.text()
}

function parseObject (raw, where) {
  try {
    const value = JSON.parse(raw)
    if (value === null || typeof value !== 'object' || Array.isArray(value)) throw new Error('not an object')
    return value
  } catch (error) {
    throw new Error(`${where} returned invalid JSON: ${error.message}`)
  }
}

export async function fetchOfficialResponses (profile, fetcher = fetchText, now = new Date()) {
  assertUnlocked(profile, now)
  return Promise.all(profile.relays.map(async url => {
    const base = `${url}/${profile.chainHash}`
    const [infoRaw, beaconRaw] = await Promise.all([
      fetcher(`${base}/info`),
      fetcher(`${base}/public/${profile.round}`)
    ])
    return {
      url,
      infoRaw,
      beaconRaw,
      info: parseObject(infoRaw, `${url}/info`),
      beacon: parseObject(beaconRaw, `${url}/public/${profile.round}`)
    }
  }))
}

function argumentsFrom (argv) {
  const values = {}
  for (let index = 0; index < argv.length; index += 2) {
    const key = argv[index]
    if (!['--c0-contract', '--c0-validation-receipt', '--output'].includes(key) || argv[index + 1] === undefined) throw new Error('usage: fetch-and-verify-v12.mjs --c0-contract FILE --c0-validation-receipt FILE --output FILE')
    values[key] = argv[index + 1]
  }
  if (!values['--c0-contract'] || !values['--c0-validation-receipt'] || !values['--output']) throw new Error('usage: fetch-and-verify-v12.mjs --c0-contract FILE --c0-validation-receipt FILE --output FILE')
  return values
}

export async function writeExclusiveArtifact (output, artifact) {
  const resolved = path.resolve(output)
  await fs.mkdir(path.dirname(resolved), { recursive: true })
  await fs.writeFile(resolved, `${JSON.stringify(artifact, null, 2)}\n`, { flag: 'wx' })
  return resolved
}

async function main () {
  const args = argumentsFrom(process.argv.slice(2))
  const c0Raw = await fs.readFile(args['--c0-contract'], 'utf8')
  const c0 = parseObject(c0Raw, 'C0 contract')
  const receipt = parseObject(await fs.readFile(args['--c0-validation-receipt'], 'utf8'), 'C0 validation receipt')
  // All contract checks and the time lock run before the first network call.
  const profile = profileFromC0(c0, receipt, c0Raw)
  assertUnlocked(profile)
  const responses = await fetchOfficialResponses(profile)
  const artifact = await verifyRelayPair(responses, profile)
  const output = await writeExclusiveArtifact(args['--output'], artifact)
  process.stdout.write(`${artifact.randomness}\n`)
  process.stderr.write(`verified v1.2 artifact written exclusively to ${output}\n`)
}

const invoked = process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)
if (invoked) {
  main().catch(error => {
    process.stderr.write(`v1.2 drand retrieval rejected: ${error.message}\n`)
    process.exitCode = 1
  })
}
