import assert from 'node:assert/strict'
import crypto from 'node:crypto'
import fs from 'node:fs/promises'
import path from 'node:path'
import test from 'node:test'
import { fileURLToPath } from 'node:url'

import { LEGACY_CHAIN, canonicalJson, verifyRelayPair } from '../fetch-and-verify-v14.mjs'
import { replayV15Artifact } from '../verify-v15-artifact.mjs'

const here = path.dirname(fileURLToPath(import.meta.url))
const infoRaw = await fs.readFile(path.join(here, 'fixtures/legacy-round-1-info.json'), 'utf8')
const beaconRaw = await fs.readFile(path.join(here, 'fixtures/legacy-round-1-beacon.json'), 'utf8')
const c0a = { artifact_kind: 'C0A', pass_pool: { frozen: true } }
const c0aSha = crypto.createHash('sha256').update(`${canonicalJson(c0a)}\n`).digest('hex')
const c0tCommit = '4'.repeat(40)
const c0t = {
  c0a: { path: "results/benchmark/v1.5-protocol/C0A.json", sha256: c0aSha }, c0a_commit: '3'.repeat(40),
  randomness_contract: { source: LEGACY_CHAIN.source, chain_hash: LEGACY_CHAIN.chainHash, round: 1, round_closes_at_utc: '2020-07-22T15:17:30Z', value: null, entropy_used: false, selection_performed: false },
  publication_observation: { github_run: { completed_at_utc: '2020-07-22T15:10:00Z' } }
}
const profile = { ...LEGACY_CHAIN, round: 1, roundClosesAtUtc: '2020-07-22T15:17:30Z', c0PublishedAtUtc: '2020-07-22T15:10:00Z', c0ArtifactCommit: c0t.c0a_commit, c0AttestationCommit: c0tCommit }
const responses = LEGACY_CHAIN.relays.map(url => ({ url, infoRaw, beaconRaw, info: JSON.parse(infoRaw), beacon: JSON.parse(beaconRaw) }))
const artifact = await verifyRelayPair(responses, profile, new Date('2020-07-22T15:17:31Z'))

function bundle () { return structuredClone({ artifact, c0a, c0t, c0t_commit: c0tCommit }) }

test('replays exact raw relay bytes and real BLS offline', async () => {
  const receipt = await replayV15Artifact(bundle())
  assert.match(receipt, /^[0-9a-f]{64}$/)
})

test('rejects self-asserted verification flags, raw-byte drift, and relay swaps', async () => {
  const flag = bundle(); flag.artifact.verification.bls_signature = true; flag.artifact.beacon.signature = '00'.repeat(96)
  await assert.rejects(replayV15Artifact(flag), /(BLS|differs|randomness)/)
  const raw = bundle(); raw.artifact.retrieval.relays[0].beacon_raw += ' '
  await assert.rejects(replayV15Artifact(raw), /raw digest/)
  const swap = bundle(); swap.artifact.retrieval.relays.reverse()
  await assert.rejects(replayV15Artifact(swap), /order or URL/)
})
