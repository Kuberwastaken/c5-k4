#!/usr/bin/env node

/** Fail-closed retrieval and verification for the Method v1.1 C1 beacon. */

import crypto from 'node:crypto'
import fs from 'node:fs/promises'
import path from 'node:path'
import process from 'node:process'
import { fileURLToPath } from 'node:url'
import { fetchBeacon } from 'drand-client'

export const PROFILE = Object.freeze({
  source: 'League of Entropy drand legacy mainnet',
  chainHash: '8990e7a9aaed2ffed73dbd7092123d6f289930540d7651336225dc172e51b2ce',
  publicKey: '868f005eb8e6e4ca0a47c8a77ceaa5309a47978a7c71bc5cce96366b5d7a569937c529eeda66c7293784a9402801af31',
  schemeID: 'pedersen-bls-chained',
  genesisTime: 1595431050,
  periodSeconds: 30,
  round: 6373886,
  roundClosesAtUtc: '2026-08-13T19:00:00Z',
  relays: ['https://api.drand.sh', 'https://api2.drand.sh']
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

export function assertUnlocked (profile = PROFILE, now = new Date()) {
  const unlock = Date.parse(profile.roundClosesAtUtc)
  if (!Number.isFinite(unlock)) throw new Error('invalid frozen round close time')
  if (now.getTime() < unlock) {
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
    if (info[key] !== value) throw new Error(`${where} info.${key} disagrees with the frozen chain`)
  }
}

function validateBeaconShape (beacon, profile, where) {
  if (beacon === null || typeof beacon !== 'object' || Array.isArray(beacon)) throw new Error(`${where} beacon is not an object`)
  if (beacon.round !== profile.round) throw new Error(`${where} returned round ${beacon.round}, expected ${profile.round}`)
  exactHex(beacon.randomness, 64, `${where} randomness`)
  exactHex(beacon.signature, 192, `${where} signature`)
  // Round one chains from the 32-byte group hash; later rounds chain from a
  // 96-byte BLS signature. The frozen prospective round is necessarily later.
  exactHex(beacon.previous_signature, beacon.round === 1 ? 64 : 192, `${where} previous_signature`)
  const recomputed = sha256Hex(Buffer.from(beacon.signature, 'hex'))
  if (beacon.randomness !== recomputed) throw new Error(`${where} randomness is not SHA256(signature)`)
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

export async function verifyRelayPair (responses, profile = PROFILE) {
  if (!Array.isArray(responses) || responses.length !== 2) throw new Error('exactly two relay responses are required')
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
  const artifact = {
    schema_version: 'c5k4-drand-randomness-artifact-1',
    retrieval: {
      source: profile.source,
      retrieved_at_utc: new Date().toISOString(),
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
      exact_round: true,
      official_relay_equality: true,
      frozen_chain_info: true,
      bls_signature: true,
      randomness_equals_sha256_signature: true,
      drand_client_version: '1.4.2'
    }
  }
  return artifact
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

export async function fetchOfficialResponses (profile = PROFILE, fetcher = fetchText) {
  assertUnlocked(profile)
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

async function main () {
  // This guard deliberately executes before the first call that can perform I/O.
  assertUnlocked(PROFILE)
  const responses = await fetchOfficialResponses(PROFILE)
  const artifact = await verifyRelayPair(responses, PROFILE)
  const here = path.dirname(fileURLToPath(import.meta.url))
  const output = process.argv[2] ?? path.resolve(here, '../../results/benchmark/c1/drand-round-6373886.json')
  await fs.mkdir(path.dirname(output), { recursive: true })
  await fs.writeFile(output, `${JSON.stringify(artifact, null, 2)}\n`, { flag: 'wx' })
  process.stdout.write(`${artifact.randomness}\n`)
  process.stderr.write(`verified artifact written to ${output}\n`)
}

const invoked = process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)
if (invoked) {
  main().catch(error => {
    process.stderr.write(`drand retrieval rejected: ${error.message}\n`)
    process.exitCode = 1
  })
}
