# Method v1.3 pre-build failure

Method v1.3 is terminally `PROTOCOL_INVALID`. It published P0 and a complete
S0, but did not invoke its one allowed production registry build.

The exact two-call preflight successfully authenticated public P0T and resolved
the current upstream `formal-conjectures` main commit. That newly resolved
commit was absent from every local Git object store. The frozen contract used
`git ls-remote` for resolution, allowed no retry or third network command, and
forbade network during the production build. Fetching the missing object would
therefore have violated the preregistration.

This is an execution-envelope defect, not a quota result. No authoritative
registry, C0/C1, entropy, selection, target identity, or candidate-semantic
inspection was produced. A successor must combine exact resolution and object
materialization in its single allowed upstream network operation, then repeat
P0 and S0 before its sole build.
