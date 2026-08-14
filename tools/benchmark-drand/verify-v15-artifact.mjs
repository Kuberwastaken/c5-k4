#!/usr/bin/env node

/** Offline BLS replay for a Method v1.5 C0T-bound drand artifact.
 *
 * Reads one JSON bundle from stdin.  It performs no network I/O and delegates
 * the cryptographic relay verification to the exact inherited v1.4 verifier.
 */

import crypto from 'node:crypto'
import process from 'node:process'

import { LEGACY_CHAIN, canonicalJson, verifyRelayPair } from './fetch-and-verify-v14.mjs'

function fail (message) { throw new Error(message) }
function sha256 (bytes) { return crypto.createHash('sha256').update(bytes).digest('hex') }
function exactHex (value, length, label) {
  if (typeof value !== 'string' || value.length !== length || !/^[0-9a-f]+$/.test(value)) fail(`${label} malformed`)
}
function exactObject (value, label) {
  if (value === null || typeof value !== 'object' || Array.isArray(value)) fail(`${label} must be an object`)
  return value
}

export async function replayV15Artifact (bundle) {
  exactObject(bundle, 'bundle')
  if (canonicalJson(Object.keys(bundle).sort()) !== canonicalJson(['artifact', 'c0a', 'c0t', 'c0t_commit'])) fail('bundle shape invalid')
  const c0a = exactObject(bundle.c0a, 'C0A')
  const c0t = exactObject(bundle.c0t, 'C0T')
  const artifact = exactObject(bundle.artifact, 'randomness artifact')
  exactHex(bundle.c0t_commit, 40, 'C0T commit')
  exactHex(c0t.c0a_commit, 40, 'C0A commit')
  if (c0t.c0a?.sha256 !== sha256(Buffer.from(canonicalJson(c0a) + '\n'))) fail('C0T does not bind canonical C0A bytes')
  const contract = exactObject(c0t.randomness_contract, 'randomness contract')
  if (contract.source !== LEGACY_CHAIN.source || contract.chain_hash !== LEGACY_CHAIN.chainHash || contract.value !== null || contract.entropy_used !== false || contract.selection_performed !== false) fail('C0T randomness contract invalid')
  const completed = c0t.publication_observation?.github_run?.completed_at_utc
  if (typeof completed !== 'string' || Date.parse(completed) >= Date.parse(contract.round_closes_at_utc)) fail('C0 publication did not precede drand close')
  if (artifact.c0_binding?.artifact_commit !== c0t.c0a_commit || artifact.c0_binding?.attestation_commit !== bundle.c0t_commit || artifact.c0_binding?.published_at_utc !== completed) fail('artifact C0 binding invalid')
  if (artifact.round !== contract.round || artifact.round_closes_at_utc !== contract.round_closes_at_utc) fail('artifact round binding invalid')
  const captured = artifact.retrieval?.relays
  if (!Array.isArray(captured) || captured.length !== 2) fail('exactly two captured relays required')
  const responses = captured.map((row, index) => {
    if (row.url !== LEGACY_CHAIN.relays[index]) fail(`relay ${index + 1} order or URL invalid`)
    if (typeof row.info_raw !== 'string' || typeof row.beacon_raw !== 'string') fail(`relay ${index + 1} raw bytes absent`)
    if (sha256(Buffer.from(row.info_raw, 'utf8')) !== row.info_raw_sha256 || sha256(Buffer.from(row.beacon_raw, 'utf8')) !== row.beacon_raw_sha256) fail(`relay ${index + 1} raw digest mismatch`)
    let info, beacon
    try { info = JSON.parse(row.info_raw); beacon = JSON.parse(row.beacon_raw) } catch { fail(`relay ${index + 1} raw JSON invalid`) }
    return { url: row.url, infoRaw: row.info_raw, beaconRaw: row.beacon_raw, info, beacon }
  })
  const profile = {
    ...LEGACY_CHAIN, round: contract.round, roundClosesAtUtc: contract.round_closes_at_utc,
    c0PublishedAtUtc: completed, c0ArtifactCommit: c0t.c0a_commit, c0AttestationCommit: bundle.c0t_commit
  }
  const replayed = await verifyRelayPair(responses, profile, new Date(artifact.retrieval.retrieved_at_utc))
  if (canonicalJson(replayed) !== canonicalJson(artifact)) fail('artifact differs from exact offline cryptographic replay')
  return sha256(Buffer.from(canonicalJson(replayed), 'utf8'))
}

async function main () {
  const chunks = []
  for await (const chunk of process.stdin) chunks.push(chunk)
  const raw = Buffer.concat(chunks).toString('utf8')
  const value = JSON.parse(raw)
  process.stdout.write(`${await replayV15Artifact(value)}\n`)
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch(error => { process.stderr.write(`v1.5 offline drand replay rejected: ${error.message}\n`); process.exitCode = 1 })
}
