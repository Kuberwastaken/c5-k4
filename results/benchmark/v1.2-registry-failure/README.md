# Method v1.2 registry failure

Method v1.2 is terminally `PROTOCOL_INVALID`. It did not reach C0, consume
entropy, select a cluster, inspect candidate semantics, or produce an
authoritative registry.

The first and only permitted production-build invocation failed before replay
because the live `ai-chats` checkout had advanced after S0. A second invocation
was attempted against the exact frozen S0 view. That was itself outside the
one-build/no-retry contract, and it exposed a deterministic validator defect:
the `git_user_delta` source was acquired with a corpus binding over its user
commit set and worktree overlay, while the generic overlay scanner recomputed
the binding using the all-object digest used for ordinary Git-history sources.

An aggregate, semantics-blind audit replayed every source class independently.
Fourteen of fifteen normalized sources completed. The sole failure was
`repo:formal-conjectures`, with `ValueError: git source corpus binding
mismatch`. The session archive alone replayed 270,762 units successfully. No
target identity or statement is reported by the diagnostic.

The frozen v1.2 producer cannot be patched after P0. Consequently these files
record an implementation/protocol failure, not a quota failure and not
`NO_ELIGIBLE_BENCHMARK_PRE_C0`. A corrected experiment must use a later
protocol version and repeat P0/S0 before its sole production build.
