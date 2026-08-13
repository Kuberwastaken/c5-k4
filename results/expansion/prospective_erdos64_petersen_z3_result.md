# Erdős 64 Petersen cyclic `Z3` lift result

Date: **2026-08-13 UTC**

Verdict: **HOLD_BOUNDED**

No public action was taken.

## Pre-freeze status gate

The live DeepMind source remains tagged `research open`; no matching open PR
or issue was found.  The live Erdős Problems page also marks problem 64 open.
The prior-art audit found no theorem covering every cyclic three-cover of
Petersen.  Markström's exhaustive cubic search stops below this 30-vertex
domain, and newer broad results cover restricted families rather than these
arbitrary nonbipartite covers.

The mechanism prediction was corrected before freeze: only a base cycle with
nonzero **total** `Z3` voltage is forced to triple in length.  A globally
nonzero voltage assignment need not make every Petersen 8-cycle nonzero.

## Frozen family and gate

The complete connected gauge-fixed family has `3^6-1 = 728` assignments:
tree-edge voltages are zero and the six cotree voltages range over every
nonzero member of `Z3^6`.  Every lift has 30 vertices and 45 edges.

Before constructing a lift, the gate:

- exactly recovered the frozen Petersen edge list;
- verified simplicity, connectedness, cubic degrees, and the explicit
  8-cycle `0-1-2-3-4-9-7-5-0`;
- compared the primary simple-cycle DFS against an independent
  subset/degree-two oracle on all 992 applicable connected Graph Atlas
  graph/length pairs through order seven.

Gate outcome: `PASS`, with zero mismatch or timeout.

## Exact family result

All 728 assignments were evaluated in approximately 1.4 seconds.  Every
constructed graph was simple, connected, cubic, and had minimum degree three.
For every candidate the exact searches returned the same presence profile:

```text
length 4:  absent in 728 / 728
length 8:  present in 728 / 728
length 16: present in 728 / 728
```

Each presence result has an explicit simple-cycle witness in the append-only
ledger.  Thus every lift satisfies Erdős 64 already through an 8-cycle (and
also through a 16-cycle).  There were no construction failures, crossings, or
timeouts.

The family is structurally useful despite the negative result: cyclic
three-covers eliminate all 4-cycles throughout this gauge-fixed Petersen
family, but they cannot simultaneously eliminate the inherited/recombined
8-cycle coordinate.  The trial therefore stops at `HOLD_BOUNDED`; no
crossing-triggered independent reconstruction or second novelty audit was
required.

## Artifacts

- `results/expansion/prospective_erdos64_petersen_z3_source_audit.md`;
- `results/expansion/prospective_erdos64_petersen_z3_contract.md`;
- `results/expansion/prospective_erdos64_petersen_z3_ledger.jsonl`;
- `scripts/prospective_erdos64_petersen_z3.py`.

