# V2 cap correction

The design scout's earlier multi-minute possibility is superseded. The standing
project rule is controlling: every solver or process stage has a 54-second
internal deadline inside a 60-second external process-group cap, with six
seconds allowed after `TERM` before `KILL`. V2 obtains separate allowances by
using a fixed staged matrix; it never lengthens a process and never builds a
dynamic matrix. Short CP-SAT slices are capped at 12 seconds.

The v1 least-positive representative correction remains exact and unchanged:
for a periodic residue `r mod m_q`, evaluate at `r` when positive and at `m_q`
when zero. `x=0` is excluded. No v2 optimization may alter this rule, the 55
primes, the six assignment cells, the source locks, or the gate scope.

Audit correction: every stage writes an explicit terminal even when an input
artifact or gate is absent. A duplicate assignment is skippable only when its
original assignment artifact and exact-adversary receipt are both hash-bound;
otherwise construction fails closed. Final artifact verification independently
replays the candidate binding, CRT, complete-cover status, and verified gate.
Artifact checksums alone are not success receipts. Each downstream stage also
requires the frozen predecessor verifier to accept exact matrix identity, zero
prerequisite and artifact-verifier codes, a faithful job/stage code pair, and
an allowed checksum-bound terminal. Honest caps, deadlines, and `NOT_RUN` are
preserved without treating worker or prerequisite failure as usable input.
