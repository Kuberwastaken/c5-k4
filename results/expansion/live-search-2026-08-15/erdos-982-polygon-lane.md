# Erdős 982 — targeted counterexample lane via known equidistant convex polygons

**Lane opened:** 2026-08-15 UTC. **Method:** `METHOD_V1_6.md` (§A2 pre-flight,
§A3 G3-lite, §A5 durability, §A6 four-coordinate status).

**Predecessor:** `erdos-depth-frontier.md` §F3 (`HOLD_BOUNDED`, faithfulness
clean, exhaustive integer search to `n∈{6,7}` in `[0,30]×[−30,30]` and
`n∈{8,9}` in `[0,9]×[−9,9]`, zero counterexamples) and §F9 ("the live lead on
982"): a counterexample must have ≥3 other vertices equidistant from **every**
vertex, and the literature has exactly two such convex polygons — Danzer's
9-gon [Er87b] and the Fishburn–Reeds 20-gon [FiRe92]. Their coordinates were
never fetched. This lane fetches and tests them.

---

## HANDOFF STATE

| item | value |
|---|---|
| **Verdict** | **`STRICT_STOP_G3_WRONG_SIGN`** — both constructions move the target quantity the wrong way, by a provable margin; no crossing, no hold change |
| 982 status after this lane | unchanged: `HOLD_BOUNDED` (F3 bracket stands, now widened structurally — see §5) |
| Upstream action taken | **none** (read-only lane, as instructed) |
| Coordinates recovered | Fishburn–Reeds Table 1 (20-gon) — verified to 2e-12; a C3-symmetric Danzer-type 9-gon — re-solved here to 50 digits |
| Danzer *original* coordinates | not printed in any source reached; the 9-gon used here is a **reconstruction** from the stated combinatorial structure, so labelled throughout |
| Key number | both constructions have **per-vertex excess = 2**; EP 982's negation needs excess ≥ `⌈n/2⌉` (5 at n=9, 10 at n=20) |
| Scripts | `verify_erdos982_polygon_lane.py` (this directory) |

---

## 1 — Pre-flight P0 (METHOD §A2)

**1. Blob pinned.** Upstream commit `2411d22e1bd550d050d0eac6c1fb379a76a3e7c5`.
`git show upstream/main:FormalConjectures/ErdosProblems/982.lean` →
blob `33971c07d094160f9b54fc40433c2b0df155ad11`. **Unchanged** from the value
recorded by the predecessor in §F3. Declaration verbatim:

```lean
@[category research open, AMS 52]
theorem erdos_982 (n : ℕ) (hn : 3 ≤ n) (p : Fin n → ℝ²) (hp : Function.Injective p)
    (hp' : EuclideanGeometry.IsConvexPolygon p) :
    ∃ (i : Fin n), { d : ℝ | ∃ j : Fin n, j ≠ i ∧ d = dist (p i) (p j) }.ncard ≥ n / 2 := by
  sorry
```

Faithfulness is **not** re-litigated here; the predecessor's audit (ℕ-division
`n / 2 = ⌊n/2⌋`, `≥`, `ncard` = distinct-distance count, `Function.Injective` =
distinct points, `IsConvexPolygon` = strict convexity) is accepted. §A6: a
counterexample would therefore be a claim about **the mathematics**, not about
the formalization.

**2. Duplicate surface.**
`gh search issues --repo google-deepmind/formal-conjectures 982 --include-prs`:

| ref | state | content |
|---|---|---|
| issue #1053 | closed | original "add Erdős Problem 982" request |
| PR #1203 | merged | added the file |
| PR #2981 | closed | duplicate-file attempt at `variants.known_result` |
| issue #4691 | **open** | "add the solved concyclic variant and Lean proof" (arex1337, 2026-08-02) |
| PR #4694 | **open** | "feat(Erdős 982): add the concyclic solved variant" (2026-08-08) |
| issue #982 | closed | unrelated (it is *Erdős Problem 857*) |

#4691/#4694 add `erdos_982.variants.concyclic` — the statement that concyclic
point sets satisfy the bound. That is exactly the predecessor's "obstruction
identity", and it is already upstream. **Nothing on the upstream surface
concerns Danzer / Fishburn–Reeds or any counterexample attempt**, so this
lane's scope (test two named convex polygons against the declaration) is not a
duplicate. No hit ⇒ no stop.

**3. Source reachability.**
* `erdosproblems.com/982` and `/97` are behind Cloudflare for plain `curl`
  (`Enable JavaScript and cookies to continue`) and return **HTTP 403** to
  `WebFetch`. The problem-97 text was nevertheless recovered verbatim through
  the SearXNG index of `erdosproblems.com/latex/97`:
  > "Erdős originally conjectured this (in [Er46b]) with no 3 vertices
  > equidistant, but Danzer found a {IMAGE=97-Danzer, convex polygon} on 9
  > points such that every vertex has three vertices equidistant from it (but
  > this distance is different for different vertices) […] [FiRe92] have found
  > a convex polygon on 20 points such that every vertex has three vertices
  > equidistant from it (and this distance is the same for all vertices)."

  Cross-checked against the mirror at `mathbounty.com/problems/97` and against
  the upstream Lean file `FormalConjectures/ErdosProblems/97.lean`, which
  carries the same sentence in its docstring. **Reachable** — the two target
  constructions are confirmed to exist and their defining properties are
  pinned. Note the parenthetical: Danzer's radii **vary by vertex**;
  Fishburn–Reeds' radius is **global** (unit).
* `Comput. Geom. 2 (1992) 81–91` (ScienceDirect `092577219290026O`) is
  paywalled/403 to this box.

**4. Budget.** Hard cap 60 s per computation, per §A2.4. All computations in
this lane finished in well under 1 s; no timeout brackets were incurred.

---

## 2 — What a counterexample actually needs (the quantity G3-lite tracks)

Fix a vertex `i` of a strictly convex `n`-gon. Let the `n−1` distances from `i`
to the other vertices fall into `c_i` classes with multiplicities
`m_1,…,m_{c_i}`, `Σ m_t = n−1`. Define the **excess**

> `E_i := (n−1) − c_i = Σ_t (m_t − 1)`

i.e. the total number of "extra" vertices beyond one per distance class. The
declaration's negation is `c_i ≤ ⌊n/2⌋ − 1` for **every** `i`, equivalently

> **`E_i ≥ (n−1) − (⌊n/2⌋ − 1) = n − ⌊n/2⌋ = ⌈n/2⌉` for every vertex `i`.**

The residual tracked below is `R := min_i c_i − ⌊n/2⌋`; a counterexample is
`R ≤ −1`. Equivalently `min_i E_i ≥ ⌈n/2⌉`.

**This is the whole lane in one line.** The property that Danzer and
Fishburn–Reeds establish — "every vertex has three others equidistant from it"
— is the statement `max_t m_t ≥ 3` at every vertex, which contributes
`E_i ≥ 2`. EP 982's negation needs `E_i ≥ ⌈n/2⌉`. The two are the same only
at `n = 4`. Erdős problem 97 (the `k`-equidistant question) constrains **one**
distance class; EP 982 constrains the **whole multiset**. The literature
constructions are calibrated for the former.

Regular `n`-gon reference point: `E_i = ⌈n/2⌉ − 1` at every vertex (each
non-diameter distance doubles), i.e. exactly one short of the requirement, and
`R = 0`. **The regular polygon is already the best known configuration**, and
any candidate must beat it at every vertex simultaneously.

### G3-lite (METHOD §A3) — sign written before any trial

Family A, C3-symmetric `3k`-gon with one tuned cross-witness per orbit
(the Danzer shape). From a vertex of orbit `m`: two orbit mates at
`√3·r_m` (one class, multiplicity 2), plus `3(k−1)` cross-orbit vertices,
generically all distinct, of which the construction forces exactly **one** into
the mate class. So `c_i = 1 + 3(k−1) − 1 = 3k − 3` and `E_i = 2`, independent
of `k`.

| member | `n = 3k` | `c_i` | `⌊n/2⌋` | `R = c_i − ⌊n/2⌋` |
|---|---|---|---|---|
| `k = 2` (smallest) | 6 | 3 | 3 | **0** |
| `k = 3` (Danzer) | 9 | 6 | 4 | **+2** |
| `k = 4` | 12 | 9 | 6 | **+3** |

Family B, mirror-symmetric bipartite unit-distance `2k`-gon
`A_i = (−x_i,y_i)`, `B_i = (x_i,y_i)`, each `A` at unit distance to three `B`
(the Fishburn–Reeds shape). The mirror maps `A ↔ B` and fixes **no** vertex
(all `x_i > 0`), so it induces no distance coincidence at any single vertex.
From `B_j`: one class of multiplicity 3 (its unit neighbours), everything else
generically singleton. So `c_i = (2k−1) − 2` and `E_i = 2`, again independent
of `k`.

| member | `n = 2k` | `c_i` | `⌊n/2⌋` | `R` |
|---|---|---|---|---|
| `k = 2` (smallest) | 4 | 1 | 2 | −1 (vacuous: needs 4 mutually equidistant points in ℝ², impossible) |
| `k = 5` | 10 | 7 | 5 | **+2** |
| `k = 10` (Fishburn–Reeds) | 20 | 17 | 10 | **+7** |

**Sign: positive and growing in `n` for both families.** Per §A3 this is a stop
before the trial. The trials were run anyway only because they cost
milliseconds and the lane's remit is to record exact numbers; the prediction
above was frozen first.

---

*(sections 3–5 appended after the runs)*
