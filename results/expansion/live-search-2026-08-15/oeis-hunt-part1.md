# OEIS open-declaration counterexample hunt — part 1 (ids < 130000)

**Campaign:** finite counterexamples to `@[category research open]` / `answer(sorry)`
declarations in `google-deepmind/formal-conjectures`, OEIS corpus.

**Upstream pin:** `google-deepmind/formal-conjectures` @ `2411d22e1bd550d050d0eac6c1fb379a76a3e7c5`
(`upstream/main`, "Disprove WOWII 59 (#4574)"). All Lean text read via
`git show upstream/main:FormalConjectures/OEIS/<id>.lean` in
`/Users/kuber.mehta/Projects/formal-conjectures`.

**Target list:** `results/expansion/open_targets_oeis_erdos_20260815.json`, entries with
`corpus=="OEIS"`, `id < 130000`, `previously_touched == false` — 61 files, sorted ascending.
(12 in-range files with `previously_touched==true` are skipped: 103151, 105565, 105720,
108081, 108211, 108569, 109074, 109908, 109909, 111291, 113019, 115257.)

**Protocol:** `METHOD.md` v1.0 (Phase 0A certificate-shape gate first; 60 s hard cap per
computation; exact integer arithmetic; second independent code path for every candidate;
no upstream write of any kind).

**Compute:** `/home/ec2-user/.venvs/wowii/bin/python` (3.9.25, numpy 2.0.2, no sympy —
Miller-Rabin/sieve helpers in `scripts/nt.py`).

**OEIS source:** `https://oeis.org/search?q=id:A<id>&fmt=json` (browser UA required;
plain curl is Cloudflare-challenged) plus `https://oeis.org/A<id>/b<id>.txt` where used.

---

## Running summary

| # | A-number | open decls | verdict | refuting witness |
|---|---|---|---|---|

*(populated incrementally below; one section per target)*

---
