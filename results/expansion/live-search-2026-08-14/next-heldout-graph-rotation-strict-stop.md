# Next held-out GRAPH rotation: strict stop

**Audit date:** 2026-08-14 UTC  
**Disposition:** `STRICT_STOP_EMPTY_QUALIFIED_SET`  
**qualified_target_count:** `0`

This was a read-only source/status scout followed by this report only. It did
not select or evaluate a target, freeze or dispatch a workflow, produce a
candidate, or authorize a release or upstream action.

## Authoritative pins and scope correction

- `google-deepmind/formal-conjectures` `main`:
  `2411d22e1bd550d050d0eac6c1fb379a76a3e7c5`.
- `teorth/erdosproblems` `main`:
  `3cbe2cffad0267952de3523089549009ea6fe5dc`.
- The DeepMind tree contains `FormalConjectures/WrittenOnTheWallII/` but no
  `FormalConjectures/WrittenOnTheWallI/` directory. Written on the Wall I is
  therefore not a DeepMind target source and was neither inspected nor ranked.

The current method ledger already records that all then-open WOWII modules
were evaluated and that the held-out graph queue was empty pending a new
upstream-manifest addition. The only subsequent graph-module addition is
Bondy longest cycles, which is already exposed and frozen as DEVELOPMENT.

## Rejected near-targets

These are diagnostic near-targets, not a fallback ranking.

### 1. Bondy longest cycles

- Exact target:
  `FormalConjectures/Arxiv/2606.03696/BondyLongestCycles.lean`, declaration
  `Arxiv.«2606.03696».bondy_conjecture`; upstream remains `research open`.
- Wall coordinate:
  `W = (k+1)delta - n - k(k-1)`. The sharp family
  `K_k join ((k+1)K_t)` has `W=-1`; at `k=t=4`, `(n,delta)=(24,7)` while the
  rounded premise requires degree `8`.
- Prospective transfer already frozen locally: balanced delete/add port
  surgery on `H=5K4`, followed by `K4 join H`, with the required obstruction
  `q_4(H) <= |H|-4` for four-path coverage.
- Rejection: locally selected, exposed, and contract-frozen. Its activation
  attempts have failed before target evaluation, but it is nonetheless an
  existing DEVELOPMENT lane, not an unclaimed held-out target.
- Strict stops include source/import drift, an exact-path upstream race,
  theorem-covered regimes (`k<=3`, `n>=5k^2+7k`, or claw-free output), pure
  edge addition, and failure of the target-free degree or crossing-reachability
  checks.

### 2. Kotzig/Ringel tree decompositions

- Exact targets:
  `FormalConjectures/Paper/KotzigConjecture.lean::KotzigConjecture.kotzig_conjecture`
  and
  `FormalConjectures/Paper/RingelConjecture.lean::RingelConjecture.ringel_conjecture`;
  both remain `research open`.
- Obstruction coordinate: a cyclic/rho labeling must realize every required
  nonzero near-distance exactly once. The previous `P3` seed realizes
  differences `{1,2}`.
- Rejection: the locally frozen end-edge subdivision stays within paths, an
  established graceful/Kotzig/Ringel domain, and ended
  `KNOWN_PROOF_DOMAIN`. The cluster has already been inspected and its only
  frozen transfer lane exhausted.
- A future lane would first need a sourced non-path tight seed and a
  role-preserving branch transfer outside every established small-order and
  sufficiently-large proof domain. Without target-free evidence that a
  transformed tree can reach a missing/colliding difference certificate,
  crossing reachability fails and evaluation must not begin.

### 3. Sidorenko homomorphism density

- Exact target:
  `FormalConjectures/Wikipedia/SidorenkoConjecture.lean::SidorenkoConjecture.sidorenko_conjecture`;
  upstream remains `research open`.
- Exact residual:
  `R_H(G)=M*N^(2e)-D^e*N^h`, where `M=homCount(H,G)`,
  `D=homCount(K2,G)`, `h=|V(H)|`, `e=|E(H)|`, and `N=|V(G)|`.
- Rejection: for the certified open pattern `H=K_{5,5}-C10`, no
  nondegenerate exact finite-host equality or near-wall is available.
  Zero-edge hosts are degenerate, proved pattern classes are closed, and
  balanced host blow-ups preserve all densities and hence the residual sign.
- A two-block host perturbation is only a conditional family idea. Until an
  independently sourced nondegenerate wall and target-free strict-integer
  crossing certificate exist, the lane remains
  `STRICT_STOP_NO_NONDEGENERATE_OPEN_DOMAIN_WALL`.

## Terminal status and next trigger

```text
qualified_target_count = 0
selected_target         = null
target_instances_read   = 0
candidate               = null
workflow_dispatched     = false
release_authorized      = false
upstream_action         = false
```

The next held-out GRAPH rotation may reopen only after a genuinely new
upstream graph declaration appears, or after a new source-certified,
nondegenerate wall outside every prior local lane passes the resolution-shape,
source/database/duplicate, theorem-domain, and crossing-reachability gates.
