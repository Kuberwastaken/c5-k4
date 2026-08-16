"""Path A for the catalogue arm: the campaign's own invariant code.

Everything comes from ``scripts/gen/invariants.py`` (the code that built the
frozen population's database `D`):

  * the whole polynomial block via ``invariants._poly_part``;
  * alpha / omega / lambda(v) via ``invariants._max_independent_bb``;
  * gamma / gamma_t / gamma_2 / gamma_i via ``invariants._min_dominating``;
  * mu, kappa, cutv, tri, the distance block, the exact spectral bracket and the
    characteristic functions all inside ``_poly_part``.

The single substitution is the chromatic number: ``invariants._chromatic_brute``
does not terminate on the larger catalogue members, so ``arm_catalogue_chi``
computes the same invariant by saturation-ordered branch and bound.  ``f`` and
``b`` are never computed: no target in the frozen population names them.

Returns per-block wall-clock alongside the values, so the driver can charge each
target only for the blocks it actually needs.
"""
from __future__ import annotations

import os
import sys
import time

_GEN = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "gen")
if _GEN not in sys.path:
    sys.path.insert(0, _GEN)

import invariants as INV                                   # noqa: E402  campaign code

from arm_catalogue_chi import chromatic_dsatur             # noqa: E402
from arm_catalogue_spec import spectral_bracket            # noqa: E402

BLOCKS = ["poly", "alpha", "omega", "chi", "lam", "gamma", "gamma_t", "gamma_2", "gamma_i"]

# which block supplies which invariant
BLOCK_OF = {
    "alpha": "alpha", "omega": "omega", "chi": "chi",
    "lam_max": "lam", "lam_min": "lam", "lam_avg": "lam",
    "gamma": "gamma", "gamma_t": "gamma_t", "gamma_2": "gamma_2", "gamma_i": "gamma_i",
}


def invariants(G, chi_deadline=None, candidate_colourings=()):
    """(values, per-block seconds, extras).  `extras` carries the chi certificate."""
    base = INV._base(G)
    adj, n = base["adj"], base["n"]
    full = (1 << n) - 1
    t = {}
    out = {}

    t0 = time.monotonic()
    out.update(INV._poly_part(G, adj, n))
    # ceil(lambda_1) recomputed exactly; see arm_catalogue_spec for why the
    # campaign's own bracket is wrong on 19 members of D (floor is unaffected).
    gen_fl, gen_ce = out["spec_floor"], out["spec_ceil"]
    fl, ce = spectral_bracket(adj, n)
    out["spec_floor"], out["spec_ceil"] = fl, ce
    t["poly"] = time.monotonic() - t0

    t0 = time.monotonic()
    out["alpha"] = INV._max_independent_bb(adj, full, n)
    t["alpha"] = time.monotonic() - t0

    t0 = time.monotonic()
    comp = [full & ~(adj[v] | (1 << v)) for v in range(n)]
    out["omega"] = INV._max_independent_bb(comp, full, n)
    t["omega"] = time.monotonic() - t0

    t0 = time.monotonic()
    lam = [INV._max_independent_bb(adj, adj[v], n) for v in range(n)]
    from fractions import Fraction
    out["lam_max"] = max(lam)
    out["lam_min"] = min(lam)
    out["lam_avg"] = Fraction(sum(lam), n)
    t["lam"] = time.monotonic() - t0

    t0 = time.monotonic()
    chi_timeout = False
    from_cert = False
    try:
        chi, lb, ub, col, from_cert = chromatic_dsatur(
            adj, n, clique_size=out["omega"], alpha=out["alpha"],
            deadline=chi_deadline, candidate_colourings=candidate_colourings)
    except TimeoutError:
        chi, lb, ub, col, chi_timeout = None, None, None, None, True
    out["chi"] = chi
    t["chi"] = time.monotonic() - t0

    for kind in ("gamma", "gamma_t", "gamma_2", "gamma_i"):
        t0 = time.monotonic()
        out[kind] = INV._min_dominating(adj, n, kind)
        t[kind] = time.monotonic() - t0

    extras = {"chi_lb": lb, "chi_ub": ub, "chi_colouring": col, "n": n, "adj": adj,
              "chi_timeout": chi_timeout, "chi_from_certificate": from_cert,
              "gen_spec_floor": gen_fl, "gen_spec_ceil": gen_ce}
    return out, t, extras
