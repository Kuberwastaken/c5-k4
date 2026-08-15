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

## 3 — Coordinates recovered

### 3.1 Fishburn–Reeds 20-gon — **exact published table recovered**

**Provenance.** Not obtainable from ScienceDirect (`092577219290026O`, HTTP 403
to this box). Recovered instead from
`github.com/davidiach/erdos97`, file `scripts/fr_cut_homotopy.py`, whose header
comment reads *"Fishburn–Reeds Table 1 (published as 1000·x_i, 1000·y_i).
A_i=(−x_i,y_i), B_i=(x_i,y_i)."* That repository is an AI-assisted research log
on Erdős **97** and elsewhere disclaims holding exact FR coordinates, so the
transcription was treated as unverified and **checked numerically before use**.

| i | 1000·x_i | 1000·y_i |
|---|---|---|
| 1 | 469.633821777 | −92.982777730 |
| 2 | 471.414237018 | −89.969229800 |
| 3 | 473.126180256 | −87.048665472 |
| 4 | **520.0** | **30.0** |
| 5 | 520.996246864 | **33.0** |
| 6 | **522.0** | **36.1** |
| 7 | 429.872125856 | 342.595442083 |
| 8 | 429.224646090 | 344.599064292 |
| 9 | 428.539574537 | 346.658610393 |
| 10 | 390.440922261 | 417.185267785 |

Vertices `A_i = (−x_i, y_i)`, `B_i = (x_i, y_i)`, `i = 1..10`; 20 points,
mirror-symmetric about the `y`-axis, no vertex on the axis.

Unit-distance pairs (`|A_i B_j| = |A_j B_i| = 1`), 15 undirected / 30 directed:
`(1,6) (1,9) (1,10) (2,5) (2,8) (2,10) (3,4) (3,7) (3,10) (4,8) (4,9) (5,7)
(5,9) (6,7) (6,8)` — a **3-regular bipartite** unit-distance graph between the
`A` side and the `B` side.

**The transcription is authentic.** All 30 unit distances hold to
`max |d² − 1| = 3.94e-12` as published. A fabricated table cannot satisfy 15
independent nonlinear equations to 12 digits. Newton-polishing at 60 decimal
digits (holding the five evidently hand-chosen round values `x₄, x₆, y₄, y₅, y₆`
fixed) drives the residual to `1.0e-59` and moves the coordinates by only
`6.3e-9`. The five round entries are exactly the free parameters: the incidence
structure gives **15** independent equations in **20** unknowns, so FR's family
is 5-dimensional and they fixed 5 coordinates. Everything is self-consistent.

Verified properties: **strictly convex** (monotone-chain hull with strict turns
returns all 20 vertices); **every vertex at distance exactly 1 from exactly 3
others** (min degree = max degree = 3), as advertised on erdosproblems.com/97.

Shape note (not in the citations): the polygon is highly clustered. `A₁A₂A₃`,
`A₄A₅A₆`, `A₇A₈A₉` are triples of near-coincident points — e.g.
`d²(A₁,A₂) = 1.225e-5`, i.e. distance `0.0035` against a diameter of `≈1.1`.
FR buy their unit distances by packing points into tiny arcs.

### 3.2 Danzer 9-gon — **reconstruction, not the original coordinates**

No source reached prints Danzer's coordinates. `erdosproblems.com/97` carries an
image asset `97-Danzer` (a picture, referenced by the page's `addImageBox` JS),
and the construction is attributed to an explanation in [Er87b]; the site is
Cloudflare-gated and the underlying figure was not retrieved. **Stated plainly:
what is tested below is a reconstruction from the combinatorial structure, not
Danzer's published nonagon.**

The reconstruction is the natural one, and appears independently in the
`erdos97` repo (`src/erdos97/danzer18_doubling.py`) as a "Danzer-type" nonagon:
`C3` rotational symmetry, three orbits of three. Writing vertices as complex
numbers with `ω = e^{2πi/3}`, orbit `m` is `{z_m, ω z_m, ω² z_m}`. Each vertex
is automatically equidistant from its **two orbit mates**, at
`|z_m − ω z_m| = √3·|z_m|`; one tuned cross-orbit witness per orbit closes the
`k = 3` property. With the gauge `z₀ = 1` and the cross map
`0 ↦ (2,1), 1 ↦ (0,0), 2 ↦ (1,0)` the three conditions reduce **exactly**, with
no trigonometry, to a system over `ℚ(√3)`:

```
a₂² + b₂² + a₂ + √3·b₂        = 2
a₁² + b₁² + a₁                = 1/2
2(a₂²+b₂²) + 2(a₁a₂+b₁b₂) − (a₁²+b₁²) = 0        where z₁=a₁+ib₁, z₂=a₂+ib₂
```

Three equations in four unknowns ⇒ a **1-parameter family** (matching the
repo's Jacobian-rank-3 finding). Note `a₁²+b₁²+a₁ = 1/2` is the circle
`|z₁ + 1/2| = √3/2`, which has **no rational points** (`X²+Y²=3` is
insolvable in ℚ), so no member of this family has rational coordinates — the
predecessor's integer-grid search could never have seen it. That is exactly the
gap this lane was opened to cover.

Member tested (Newton at 60 digits, system residual `3.5e-56`):
`z₁ = −0.544100000000000 + 0.864901838360863 i`,
`z₂ = 0.802055422961524 + 0.276188094444543 i`, `z₀ = 1`.
Verified: **strictly convex** 9-gon, **every vertex has ≥3 equidistant others**.
Cross-checked against the repo's own 50-digit polar constants
(`r₁ = 1.02327653622861512…, φ₁ = 2.13488993490095944…,
r₂ = 0.84430467659553225…, φ₂ = 0.34318985719866858…`), which land on the same
family and give identical distance profiles.

---

## 4 — Test results against the declaration

Everything below is at 60 decimal digits with coordinates solved to `≤1e-56`;
two squared distances are called equal only if they agree to `1e-30` absolute
(and the robustness of that call is reported separately). Runtime: 0.9 s total,
against a 60 s cap. No timeouts, so no brackets.

### 4.1 Fishburn–Reeds 20-gon — `n = 20`, `⌊n/2⌋ = 10`

| quantity | value |
|---|---|
| strictly convex | **yes**, hull = all 20 |
| unit-degree per vertex | 3 (min = max) |
| distinct distances `c_i` | **17 at every one of the 20 vertices** |
| multiplicity profile at every vertex | `[3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]` |
| excess `E_i` | **2** at every vertex (need `≥ 10`) |
| **residual `R = min_i c_i − ⌊n/2⌋`** | **`+7`** (counterexample iff `≤ −1`) |

Robustness: the count `c_i = 17` is stable for any relative merge tolerance from
`1e-12` up to `1e-6`. It degrades only when the tolerance is coarse enough to
merge genuinely distinct distances inside FR's tight clusters (`1e-4 → 16`,
`1e-2 → 9`). Those are **tolerance artefacts, not coincidences**: the tightest
adjacent pair at any vertex is `d² = 4.4337e-6` vs `4.7111e-6` (absolute gap
`2.773e-7`, **relative gap 5.9 %**). Per the guard-band rule, none of these is a
crossing. The exact answer at full precision is `17`.

### 4.2 Danzer-type 9-gon — `n = 9`, `⌊n/2⌋ = 4`

| quantity | value |
|---|---|
| strictly convex | **yes**, hull = all 9 |
| `k = 3` property | holds at every vertex |
| distinct distances `c_i` | **6 at every one of the 9 vertices** |
| multiplicity profile at every vertex | `[3, 1, 1, 1, 1, 1]` |
| excess `E_i` | **2** at every vertex (need `≥ 5`) |
| **residual `R`** | **`+2`** |

Sorted squared distances from `v₀`:
`0.002220, 0.122710, 2.015841, 2.997780, 3.000000, 3.000000, 3.000000,
3.141285`. Stable for every merge tolerance from `1e-12` to `1e-3`.

The `2.997780` entry is a near-miss against the mate class `3.000000` (relative
gap `7.4e-4`) — the same near-coincidence `d²(v₀,v₄) ≈ 2.99778` the `erdos97`
repo records while hunting a `k = 4` example for Erdős **97**. Even if it closed
exactly it would give `c_i = 5`, i.e. `R = +1`. **Erdős 97 and Erdős 982 do not
meet here.**

### 4.3 Sweep of the whole 1-parameter Danzer family

852 admissible members sampled over `a₁ ∈ [−1.60, 0.60]` (1500 steps × 2
branches), each Newton-solved to `1e-50` and screened by three guards:
strict convexity, `min pairwise distance / diameter ≥ 1e-3`, and
`min exterior turn ≥ 1e-3` rad.

* best (smallest) `min_i c_i` anywhere in the family: **6** → `R = +2`.
* smallest relative gap between distinct classes among admissible members:
  `1.06e-6`; closing that single extra coincidence exactly would still leave
  `min_i c_i ≥ 5`, `R ≥ +1`.
* **53 members were rejected by the guards, and this mattered.** An earlier
  unguarded pass reported `min_i c_i = 2`, `R = −2` — an apparent crossing — at
  `a₁ = −0.5 + 1.2e-51`. At `a₁ = −1/2` the first equation forces
  `b₁ = ±√3/2`, i.e. `z₁ = ω`, so orbit 1 **collapses onto orbit 0**: the
  "9-gon" is 3 points each tripled, pairwise distances `~1e-25`, violating
  `Function.Injective p`. This is recorded because it is exactly the failure the
  guard-band rule exists to catch: **a sub-`1e-6` gap was not a crossing.**

### 4.4 Subset lattices (exhaustive)

Every subset of a strictly convex point set is strictly convex, so each of the
`2^9` and `2^20` subsets is a legitimate candidate at its own `n`. Both lattices
were exhausted by DFS over every target size `4 ≤ m ≤ n`, pruning on the
hereditary condition `c_i(T) ≤ ⌊m/2⌋ − 1` for all `i ∈ T`:

| point set | DFS nodes | subsets satisfying the negation |
|---|---|---|
| Danzer-type 9-gon | 644 | **0** |
| Fishburn–Reeds 20-gon | 234,316 | **0** |

This is forced, and the one-line reason generalises: with `max_t m_t = 3` at
every vertex and every other class a singleton, `c_i(S) ≥ |S| − 3` for any
subset `S`, so the negation `c_i(S) ≤ ⌊|S|/2⌋ − 1` requires `⌈|S|/2⌉ ≤ 2`, i.e.
`|S| ≤ 4`; and `|S| = 4` requires 4 mutually equidistant points in `ℝ²`.

### 4.5 Independent recomputation (METHOD Phase 7)

Path B is a structurally different program: float64/numpy, polar-trigonometric
parametrisation, seeded from the `erdos97` repo's own 50-digit constants rather
than from this lane's complex-algebraic Newton solve, with the FR table used
**unpolished** exactly as published. It reproduces every headline number:
FR-20 `min_i c_i = 17`, `R = +7`; Danzer-9 `min_i c_i = 6`, `R = +2`; both
strictly convex; both `k = 3`. Agreement across the whole tolerance sweep
`1e-12 … 1e-6`.

---

## 5 — Why the attack fails, and what that closes

The two constructions were built to refute **Erdős 97** (the `k`-equidistant
question), which constrains **one** distance class per vertex. EP 982 constrains
the **entire multiset**. Quantitatively:

> **Proposition.** Suppose a strictly convex `n`-gon has, at every vertex,
> one distance class of multiplicity `k` and all other classes singletons.
> Then `c_i = n − k` and `R = n − k − ⌊n/2⌋`. Hence `R ≤ −1` **iff**
> `k ≥ ⌈n/2⌉ + 1`.

Both literature constructions have `k = 3`:

| construction | `n` | `k` | `k` needed for `R ≤ −1` | deficit |
|---|---|---|---|---|
| Danzer-type 9-gon | 9 | 3 | 5 | **2** |
| Fishburn–Reeds 20-gon | 20 | 3 | 11 | **8** |

Equivalently, in mean multiplicity `(n−1)/c_i`: the negation of EP 982 requires
`(n−1)/c_i ≥ (n−1)/(⌊n/2⌋−1) > 2` at **every** vertex, while these constructions
deliver `(n−1)/(n−3) → 1`. The constructions therefore get **monotonically
worse** as `n` grows — which is precisely the observed `R = +2` at `n = 9`
versus `R = +7` at `n = 20`. This is the G3-lite sign, confirmed exactly.

Three consequences worth recording:

1. **The F9 lead is closed, structurally rather than just negatively.** The
   whole "≥ `k` equidistant at every vertex" branch of the literature can only
   yield an EP 982 counterexample once `k ≥ ⌈n/2⌉ + 1` — a vertex-centred circle
   through more than half the remaining vertices, at every vertex. Nothing in
   the unit-distance literature is remotely that.
2. **Even solving Erdős 97 would not touch EP 982.** A hypothetical `k = 4`
   convex `n`-gon (the open case, `$100`) satisfies `R ≤ −1` only for
   `n ≤ 2(k−1) = 6`; `n = 6` was already exhausted by the predecessor and
   `n ≤ 5` is unconditionally impossible. So Erdős 97 and Erdős 982, though they
   share the phrase "equidistant vertices", are disjoint as attack surfaces.
3. **The dimension counts are hopeless, not merely unlucky.** The Danzer family
   is 1-dimensional and needs 3 further coincidences per vertex class
   (over-determined by 2). The FR family is 5-dimensional (15 equations, 20
   unknowns) and needs 8 further coincidences at each of 10 mirror classes,
   i.e. ~80 equations on 5 parameters (over-determined by ~75).

**What is *not* closed.** The predecessor's `HOLD_BOUNDED` bracket is unchanged
in substance: integer/rational configurations exhausted for `n ∈ {6,7}` in
`[0,30]×[−30,30]` and `n ∈ {8,9}` in `[0,9]×[−9,9]`; `n ≥ 10` untouched; the
irrational regime untouched except for the two named algebraic families handled
here. This lane adds: the two named irrational-coordinate constructions in the
literature, their full 1- and 5-parameter families in the case of Danzer, and
both of their complete subset lattices. It does **not** bear on the underlying
conjecture, which remains open (best known `f(n) ≥ (13/36 + 1/22701)n − O(1)`,
Nivasch–Pach–Pinchasi–Zerbib).

### Verdict

**`STRICT_STOP_G3_WRONG_SIGN`** (METHOD §A3). No crossing. `erdos_982` status is
unchanged at `HOLD_BOUNDED`; blob `33971c07d094160f9b54fc40433c2b0df155ad11`
re-checked at the end of the lane and unchanged. Nothing was opened, commented,
or pushed upstream. §A6 coordinates: (1) the underlying question stays open;
(2) no formal solution; (3) the declaration is faithful; (4) no counterexample
to what it literally asserts was found.

### Script

`verify_erdos982_polygon_lane.py` (this directory) — runs the whole lane end to
end in under a second:

```
python3 verify_erdos982_polygon_lane.py
```

