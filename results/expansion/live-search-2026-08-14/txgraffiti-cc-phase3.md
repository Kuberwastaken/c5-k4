# TxGraffiti C-C phase three: stratified `t=2` pairing freeze

Date: **2026-08-14 UTC**

Evidence split: **DEVELOPMENT**. This is not held-out Method v1.5 evidence.

This contract is the minimal correction required by
[`txgraffiti-cc-phase2-result.md`](txgraffiti-cc-phase2-result.md). It reuses
the phase-zero statement, source/status and database gate, and the phase-two
matched-core/independent-reservoir construction, exact four-second `i(G)`
MILP, structural proof `mu*(G)=3t`, crossing replay, nauty authority, durable
runtime, 60-second process cap, and 54-second internal stop.

No phase-three target was evaluated before freeze. Only syntax, import,
finite-domain construction, pairing-orbit counts, and structural-certificate
checks are permitted before the arms run.

## Correction and prior-use disclosure

Phase two mixed `t=3,4,5` inside one beam and used raw `i(G)` as a global
tie-break. This favored larger graphs and spent 42 of 48 wall evaluations at
`t=5`, even though all observed equality occurred at smaller coordinates.
Phase three removes cross-order ranking completely: every arm searches only
`t=2`, so every exact residual is `6-i(G)` on a 20-vertex cubic graph.

The construction and coordinates `t=2,3,4` were explored in disclosed scratch
scouting before phase two. Phase two also evaluated the cube with two fixed
pairings. Phase three is therefore development reuse, not a fresh benchmark.
It does not copy a scratch witness or phase-two ledger row; it freezes the
complete finite pairing domain modulo base automorphisms and lets nauty remove
any remaining graph isomorphisms.

## Finite domain

There are exactly five connected nonisomorphic cubic graphs on eight vertices.
Their frozen canonical graph6 strings are

```text
Gs@ipo  GsOiho  GtPHOk  Gv?IXW  GtP@Ww
```

For each base, enumerate all `11!! = 10,395` perfect matchings of its twelve
subdivision vertices. Quotient by the induced action of the base
automorphism group, retaining the lexicographically least matching in each
orbit. Constructor-only enumeration gives respectively

```text
278, 697, 2658, 768, 919
```

pairing orbits, for 5,320 construction states before final-graph nauty
deduplication. Each state is connected cubic on 20 vertices and carries the
same exact certificate `mu*(G)=6`. The only optimized quantity is the child's
exact independent domination number.

## Three disjoint deterministic arms

The Method v1.5 arm labels are used as three shards, not as adaptive search
strategies. Every constructed graph is canonicalized once with frozen nauty
`labelg`; its exact canonical SHA-256 is assigned by

```text
int(canonical_sha256, 16) mod 3
```

to `CATALOGUE=0`, `GENERIC=1`, or `WALL_NAVIGATION=2`. Thus a canonical graph
class can enter exactly one arm. Within every worker, construction states are
ordered by SHA-256 of `(base graph6, pairing representative)`, preventing a
base-order prefix from consuming the budget. Each arm scans that common
deterministic order, ignores classes assigned elsewhere, evaluates its own
classes exactly, and stops at the common 54-second internal deadline.

There is no parent witness score, beam, cross-coordinate comparison,
replacement, or adaptive backfill. A hard timeout is only a durable exact
prefix; completion of all three streams would exhaust the canonical image of
the 5,320-state quotient domain.

Any negative residual receives the phase-two independent CaDiCaL
at-most-six UNSAT replay and structural matching replay before a crossing
checkpoint. Zero crossings remain a bounded development result, never a
proof or publication authorization.

Frozen artifacts:

- [`txgraffiti-cc-phase3-manifest.json`](txgraffiti-cc-phase3-manifest.json)
- [`../../../scripts/search_txgraffiti_cc_phase3.py`](../../../scripts/search_txgraffiti_cc_phase3.py)
