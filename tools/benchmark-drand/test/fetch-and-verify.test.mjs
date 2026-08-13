import assert from 'node:assert/strict'
import crypto from 'node:crypto'
import fs from 'node:fs/promises'
import test from 'node:test'
import { fileURLToPath } from 'node:url'
import path from 'node:path'

import { PROFILE, assertUnlocked, verifyRelayPair } from '../fetch-and-verify.mjs'

const here = path.dirname(fileURLToPath(import.meta.url))
const infoRaw = await fs.readFile(path.join(here, 'fixtures/legacy-round-1-info.json'), 'utf8')
const beaconRaw = await fs.readFile(path.join(here, 'fixtures/legacy-round-1-beacon.json'), 'utf8')
const info = JSON.parse(infoRaw)
const beacon = JSON.parse(beaconRaw)
const historical = { ...PROFILE, round: 1, roundClosesAtUtc: '2020-07-18T10:50:50Z' }

function pair () {
  return PROFILE.relays.map(url => ({ url, infoRaw, beaconRaw, info: structuredClone(info), beacon: structuredClone(beacon) }))
}

test('refuses before the frozen unlock time', () => {
  assert.throws(() => assertUnlocked(PROFILE, new Date('2026-08-13T18:59:59.999Z')), /network disabled/)
  assert.doesNotThrow(() => assertUnlocked(PROFILE, new Date('2026-08-13T19:00:00.000Z')))
})

test('accepts an offline historical two-relay fixture with BLS verification', async () => {
  const artifact = await verifyRelayPair(pair(), historical)
  assert.equal(artifact.randomness, beacon.randomness)
  assert.equal(artifact.verification.bls_signature, true)
  assert.equal(artifact.signature_sha256, beacon.randomness)
})

test('rejects wrong round', async () => {
  const responses = pair()
  responses[0].beacon.round = 2
  await assert.rejects(verifyRelayPair(responses, historical), /returned round/)
})

test('rejects a randomness hash that is not SHA256(signature)', async () => {
  const responses = pair()
  responses[0].beacon.randomness = '00'.repeat(32)
  await assert.rejects(verifyRelayPair(responses, historical), /SHA256\(signature\)/)
})

test('rejects a cryptographically invalid signature even with matching hash', async () => {
  const responses = pair()
  responses[0].beacon.signature = `${responses[0].beacon.signature.slice(0, -2)}00`
  responses[0].beacon.randomness = crypto.createHash('sha256').update(Buffer.from(responses[0].beacon.signature, 'hex')).digest('hex')
  await assert.rejects(verifyRelayPair(responses, historical), /BLS verification failed/)
})

test('rejects disagreement between official relays', async () => {
  const responses = pair()
  responses[1].beaconRaw = `${beaconRaw} `
  responses[1].beacon = { ...responses[1].beacon, previous_signature: `00${responses[1].beacon.previous_signature.slice(2)}` }
  await assert.rejects(verifyRelayPair(responses, historical), /(BLS verification failed|relay beacon mismatch)/)
})

test('rejects any substituted relay URL', async () => {
  const responses = pair()
  responses[1].url = 'https://example.invalid'
  await assert.rejects(verifyRelayPair(responses, historical), /URL is not the frozen official relay/)
})
