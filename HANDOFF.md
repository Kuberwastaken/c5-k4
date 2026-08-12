# Handoff — C₅[K₄] counterexample campaign (for Codex on ai-vps)

Paste the block below into Codex. Everything referenced is on this box.

---

You are picking up a graph-theory counterexample campaign mid-flight. The
previous agent (Claude) hit a usage limit; three evaluation subagents died
before writing output. Your job: finish the expansion sweep, verify, and
keep committing.

## What this is

The graph **C₅[K₄]** (lexicographic product: 5 blobs of K₄ on a 5-cycle,
complete join between adjacent blobs; n=20, m=110, 11-regular,
vertex-transitive, diameter 2) is a counterexample carrier that has killed
multiple automated-conjecture-generator conjectures. Repo:
`/Users/kuber.mehta/Projects/c5-k4` (GitHub `Kuberwastaken/c5-k4`, public,
main branch, everything pushed). Read its `README.md` first — it is the
current state of knowledge.

Build the graph:
```python
import networkx as nx
G = nx.Graph(); G.add_nodes_from(range(20))
blob = lambda v: v//4
for u in range(20):
    for v in range(u+1, 20):
        if blob(u)==blob(v) or (blob(u)-blob(v))%5 in (1,4):
            G.add_edge(u,v)
```
Python env with networkx+pulp+matplotlib: `/home/ec2-user/.venvs/wowii/bin/python`.
Certified invariant profile (trusted, verified analytically + by assertion):
`/Users/kuber.mehta/Projects/c5-k4/data/profile.json`.

## Status: DONE (do not redo)

**WOWII (DeLaViña, Written on the Wall II) — exhausted.** All 522
transcribed conjectures evaluated against C₅[K₄]:
- 4 open-conjecture kills: **63, 85** (Kuber's, 2026-07-23, in
  formal-conjectures PR #4592 — merged-ready, CI green) and **64, 309**
  (Gebendorfer, Zenodo, July 2026 — both explicitly ride Kuber's carrier).
- 1 spawned kill: **181**, via the triangular graph **T(7)=L(K₇)**
  (SRG(21,10,5,4)): L_s+b = 22 < 23 = α+deg_avg(B(G²)); infinite family
  T(n), n≥7. Reading-dependent (deg_avg measured in G²). **Unclaimed** in
  formal-conjectures and absent from the literature — Kuber may want to
  stake it.
- 8 retro-kills (already-refuted-by-others conjectures this graph also
  kills): 24, 25, 46, 49, 52, 54, 55, 56 (+77 under one reading).
- ~40 exact-tightness (zero-slack) witnesses across open/proved/refuted.
- Corrupt-as-published entries exposed: **401b, 412f, 448b** (each
  violated by graphs inside Graffiti.pc's own database — stars, K₃, C₄ —
  so the published wording cannot be what was tested); plus proved
  theorem **97** has a sign typo (published `α ≤ λ_max − δ(Ḡ)` is false on
  C₅, P₄, Petersen; correct is `+`).
- Family sweeps (30+ members: C₅[K_m] m=2..8, C₇/C₉ blowups, non-uniform
  blobs B(...), complements) found no further kills — the family sits at
  *exact equality* on the remaining walls (window-argument proofs in
  `results/family_domination.md`).
- Transcription audit vs DeLaViña's live page (page itself updated
  2026-08-06): 3 open conjectures were missing from the community JSON
  (**136, 137, 138**) — recovered, evaluated, no violations (137 is tight).

**TxGraffiti/Optimist — done.** `results/expansion/txgraffiti.md` holds the
complete verdict table: all open conjectures HOLD on the arsenal. The one
"violation" (2306.12917 Conjecture 3, Z ≤ (3/2)γ_t) is a printed-statement
erratum refuted by K₃,₃ itself, not new math; one raw Optimist session
output is trivially false. Nothing to claim.

## Status: YOUR WORK (three lanes, none started)

Corpora are already acquired and normalized in
`/Users/kuber.mehta/Projects/c5-k4/corpora/` (provenance in
`ACQUISITION.md`):

1. **`graffiti_wow.json`** — Fajtlowicz's original *Written on the Wall*
   (WoW I), 587 entries, OCR-derived (confidence medium; garbled entries
   exist). Evaluate entries with status `open` or `unannotated`. Split as
   you like (previous plan: ids <450 and ids ≥450 as two workers).
2. **`autographix.json`** — AutoGraphiX (Aouchiche–Hansen) 259 entries;
   evaluate the ~70 with status `open`. Spectral/distance bounds (λ₁,
   average distance, proximity, remoteness, energy, Randić, algebraic
   connectivity).

### Arsenal (evaluate every conjecture against all of these)
- C₅[K₄] (the carrier) and C₅[K_m] for m ∈ {2,3,5,6,8}; C₇[K₃]; C₉[K₃].
- **T(n) = L(K_n)** for n ∈ {7,8,9} (`nx.line_graph(nx.complete_graph(n))`)
  — strongly regular, α=⌊n/2⌋, diam 2, spectrum {2(n−2), n−4, −2}. This is
  the lever that killed 181: it achieves **α > λ_max**, which blow-ups
  cannot.
- Complement of C₅[K₄] (8-regular, triangle-free, diam 2).
- For AGX also: Petersen, Paley(13/17/29) if cheap.
- Closed-form spectrum of C₅[K_m]: eigenvalues are `m·μ + (m−1)` for each
  C₅ eigenvalue μ ∈ {2, 2cos72° (×2), 2cos144° (×2)}, plus `−1` with
  multiplicity 5(m−1). Use it instead of numerics where possible.

### Non-negotiable protocol (this is what makes results trustworthy)
1. **DB-SANITY GATE.** Every candidate violation must be re-tested under
   the same reading on: all connected graphs n ≤ 7 (`nx.graph_atlas_g()`,
   ~995), plus C₅–C₉, P₇, Petersen, K₃,₃, K₇, stars, complete bipartite.
   These were inside the generators' own verification databases. **A
   reading that any of them violates is a mis-transcription, not a kill —
   discard it.** This rule already caught 4 corrupt WOWII entries; expect
   more in OCR'd WoW I.
2. **All plausible readings.** Terse statements are ambiguous (operator
   precedence, set vs member eccentricity, which graph an invariant
   applies to). Evaluate every reading; report per reading.
3. **Independent recomputation** of every gate-surviving violation by a
   second method (different code path, not the same helper).
4. **Novelty check** before claiming: WoW I is 20–40 years old and heavily
   studied — web-search the conjecture number + statement; AGX has known
   2021–2023 refutations (Wagner; Vito–Stefanus).
5. **Numerics:** exact `Fraction` for distance/degree invariants; for
   spectral quantities use a 1e-6 guard band — treat smaller gaps as ties,
   never as kills.
6. **Skip** unusable OCR garble with verdict `SKIP_OCR` and quote the
   garble (don't guess at the intended statement).

### Output discipline (learned the hard way — an agent lost an hour of work)
Write results **incrementally**, appending after every ~15–20 conjectures,
to `/Users/kuber.mehta/Projects/c5-k4/results/expansion/`:
`wow1_part1.md`, `wow1_part2.md`, `agx.md`. Never buffer everything for a
final write. Cap any ILP/CBC solve at 60s (`PULP_CBC_CMD(msg=0,
timeLimit=60)`) and record a bracket if it times out; an unbounded solve
already wedged one agent for 55 minutes.

## Infrastructure running right now
A shell loop `.../scratchpad/wowii309/autocommit2.sh` (started 10:27Z, runs
6h, i.e. until ~16:27Z) commits and pushes the repo every 2 minutes:
it syncs agent reports, commits all worktrees on all branches, merges every
branch into main, pushes main, and appends a heartbeat to
`.../scratchpad/wowii309/autocommit.log`. **Check it is alive**
(`ps -ef | grep autocommit2`); if it has expired, either restart it or just
commit/push yourself — sequential commits with clear messages, pushing as
you go, is the standing rule for this repo. Never force-push or rewrite
history.

Git identity for commits: `Kuber Mehta <kuberhob@gmail.com>`. Do **not**
add Claude/Anthropic co-author trailers.

## When the three lanes finish
1. Update `README.md`: fold results into the kill table / "where this
   weapon points next" section; keep the first-person voice (these are
   Kuber's disproofs — write "I found", not "the author found").
2. If any new kill survives all four protocol steps, tell Kuber
   explicitly and prepare (a) a certificate repo in the style of
   `github.com/Kuberwastaken/wowii-63-85-counterexample` and (b) a
   formal-conjectures PR in the house style. `lean/` currently holds
   `GraphConjecture63.lean` and `GraphConjecture85.lean` (final, building
   in PR #4592) plus draft formulations `GraphConjecture64.lean` and
   `GraphConjecture309.lean` (not yet built against the repo). A 181 file
   would need to be written fresh.
3. Open question worth an hour if lanes come back dry: recover
   DeLaViña's original wording for **401b, 412f, 448b** from Wayback
   snapshots of `cms.dt.uh.edu/faculty/delavinae/research/wowII/` — if the
   real statements differ from the corrupt published ones, they become
   huntable again.

Ask Kuber before anything outward-facing (posting PR comments, creating
repos, contacting authors).
