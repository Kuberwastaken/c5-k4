"""Evaluation context wrapping an arsenal graph + certified battery.

Methods return ints/Fractions/sympy exprs, or raise Undef when the value is
not EXACTLY certified (bracketed). Lower-bound variants (*_lb) return the
search incumbent together with kind tag for one-sided HOLDS decisions.
"""
from fractions import Fraction
from pathlib import Path

import networkx as nx
import sympy

import helpers as H
import invlib as iv

META_PATH = Path(__file__).resolve().parent.parent / "cache" / "arsenal_meta.json"

FRAC_KEYS = ("deg_avg", "CW", "disp_avg", "median_median", "avg")


def revive(v):
    """JSON round-trip: Fraction -> 'n/d' string."""
    if isinstance(v, str):
        if "/" in v:
            a, b = v.split("/")
            try:
                return Fraction(int(a), int(b))
            except ValueError:
                return v
        try:
            return Fraction(int(v))
        except ValueError:
            return v
    return v


class Undef(Exception):
    pass


def S(x):
    if isinstance(x, Fraction):
        return sympy.Rational(x.numerator, x.denominator)
    return sympy.sympify(x)


def ex_floor(x):
    return int(sympy.floor(sympy.N(S(x), 60)))


def ex_ceil(x):
    return int(sympy.ceiling(sympy.N(S(x), 60)))


class X:
    def __init__(self, name, G, cert):
        self.name = name
        self.G = G
        self.c = cert
        self.n = cert["n"]
        self._vt = None
        self._lamv = None
        self._lamv_bar = None
        self._G2 = None
        self._dm = None

    # ------------------------------------------------ infrastructure
    @property
    def vt_full(self):
        if self._vt is None:
            import json
            meta = json.load(open(META_PATH))
            w = meta[self.name]["vt"]
            self._vt = bool(w.get("orbit_full")) and bool(w.get("perms_valid"))
        return self._vt

    @property
    def dm(self):
        if self._dm is None:
            self._dm = dict(nx.all_pairs_shortest_path_length(self.G))
        return self._dm

    @property
    def G2(self):
        if self._G2 is None:
            self._G2 = H.square_graph(self.G)
        return self._G2

    def _cert_scalar(self, key):
        r = self.c[key]
        if isinstance(r, dict):
            if r.get("certified") and "value" in r:
                return r["value"]
            raise Undef(f"{key} not exactly certified ({r})")
        return r

    def _incumbent(self, key):
        r = self.c[key]
        if isinstance(r, dict) and r.get("value") is not None:
            return r["value"]
        if isinstance(r, (int, float)):
            return r
        raise Undef(f"{key} no incumbent")

    # ------------------------------------------------ basics
    @property
    def m_edges(self):
        return self.c["m_edges"]

    @property
    def delta(self):
        return self.c["delta"]

    @property
    def Delta(self):
        return self.c["Delta"]

    @property
    def sigma(self):
        return self.c["sigma_2nd_smallest"]

    @property
    def Sigma_deg(self):
        return self.c["Sigma_2nd_largest"]

    @property
    def deg_avg(self):
        return revive(self.c["deg_avg"])

    @property
    def dd(self):
        return self.c["dd"]

    @property
    def girth(self):
        g = self.c.get("_girth")
        if g is None:
            g = H.girth_safe(self.G)
            self.c["_girth"] = g
        if g is None:
            raise Undef("acyclic")
        return g

    @property
    def diam(self):
        return self.c["diam"]

    @property
    def rad(self):
        return self.c["rad"]

    def ecc_avg_G(self):
        ecc = self.c["ecc"]
        return Fraction(sum(ecc.values()), self.n)

    def ecc_avg_set(self, members):
        vals = [self.c["ecc"][v] for v in members]
        return Fraction(sum(vals), len(vals)) if vals else Undef("empty set")

    # distance-stat bundles
    def _fr(self, key):
        v = self.c[key]
        return revive(v)

    def dist_even(self, kind, subset=None):
        return self.stat("dist_even", kind, subset)

    def dist_odd(self, kind, subset=None):
        return self.stat("dist_odd", kind, subset)

    def Tdist(self, kind, subset=None):
        return self.stat("Tdist", kind, subset)

    def even_horizontal(self, kind, subset=None):
        return self.stat("even_horizontal", kind, subset)

    def odd_horizontal(self, kind, subset=None):
        return self.stat("odd_horizontal", kind, subset)

    def stat(self, key, kind, subset=None):
        d = self.c[key]
        vals = [d[v] for v in subset] if subset is not None else list(d.values())
        if not vals:
            raise Undef(f"empty subset for {key}")
        if kind == "min":
            return min(vals)
        if kind == "max":
            return max(vals)
        return Fraction(sum(vals), len(vals))

    # sets
    def M(self):
        return [v for v in self.G.nodes() if self.G.degree(v) == self.Delta]

    def A(self):
        return [v for v in self.G.nodes() if self.G.degree(v) == self.delta]

    def Bset(self):
        dm = self.diam
        return [v for v in self.G.nodes() if self.c["ecc"][v] == dm]

    def Cset(self):
        dr = self.rad
        return [v for v in self.G.nodes() if self.c["ecc"][v] == dr]

    def D2set(self):
        return H.degree_class(self.G, lambda d: d == 2)

    def Ppend(self):
        return H.degree_class(self.G, lambda d: d == 1)

    def Supp(self):
        return [v for v in self.G.nodes()
                if any(self.G.degree(u) == 1 for u in self.G[v])]

    def ModeMinSet(self):
        mm = self.c["mode_mode_min"]
        return [v for v in self.G.nodes() if self.G.degree(v) == mm]

    def A3(self):
        return H.degree_class(self.G, lambda d: d >= 3)

    def H3(self):
        return H.degree_class(self.G, lambda d: d >= 3)

    def H2(self):
        return H.degree_class(self.G, lambda d: d <= 2)

    def Deven(self):
        return H.degree_class(self.G, lambda d: d % 2 == 0)

    def M4set(self):
        kv = self.c["K4_v"]
        mx = max(kv.values())
        return [v for v in kv if kv[v] == mx]

    def A1set(self):
        """vertices adjacent to exactly one non-minimum-degree vertex"""
        amin = set(self.A())
        out = []
        for v in self.G.nodes():
            k = sum(1 for u in self.G[v] if u not in amin)
            if k == 1:
                out.append(v)
        return out

    def DminTotal(self):
        tr = self.c["Tdist"]
        mn = min(tr.values())
        return [v for v in tr if tr[v] == mn]

    def Xlambdamax_set(self):
        lamv = self.lambda_per_vertex()
        mx = max(lamv.values())
        return [v for v in lamv if lamv[v] == mx]

    def _lambda_of_vertex(self, H, v, cap):
        nb = list(H[v])
        if not nb:
            return 0
        val, _w, proved = iv.independence_number(H.subgraph(nb), cap)
        if not proved:
            raise Undef(f"lambda({v}) not exactly certified")
        return val

    def lambda_per_vertex(self):
        if self._lamv is None:
            if self.vt_full:
                val = self._lambda_of_vertex(self.G,
                                             next(iter(self.G.nodes())), 20.0)
                self._lamv = {v: val for v in self.G.nodes()}
            else:
                self._lamv = {v: self._lambda_of_vertex(self.G, v, 20.0)
                              for v in self.G.nodes()}
        return self._lamv

    def lambda_stats(self):
        ls = dict(self.c["lambda_stats"])
        if not ls.get("certified"):
            raise Undef("lambda_stats bracketed")
        ls["avg"] = revive(ls["avg"])
        return ls

    def lambda_per_vertex_bar(self):
        """local independence of the COMPLEMENT, per vertex."""
        if self._lamv_bar is not None:
            return self._lamv_bar
        Hc = nx.complement(self.G)
        if self.vt_full:
            val = self._lambda_of_vertex(Hc, next(iter(Hc.nodes())), 12.0)
            self._lamv_bar = {v: val for v in Hc.nodes()}
            return self._lamv_bar
        out = {}
        for v in Hc.nodes():
            out[v] = self._lambda_of_vertex(Hc, v, 12.0)
        self._lamv_bar = out
        return out

    def lambda_bar_freq(self, which):
        lamv = self.lambda_per_vertex_bar()
        vals = list(lamv.values())
        t = min(vals) if which == "min" else max(vals)
        return vals.count(t)

    def freq_lambda_max_G(self):
        lamv = self.lambda_per_vertex()
        vals = list(lamv.values())
        return vals.count(max(vals))

    # named-set cards (precomputed)
    def card_NM_minus_M(self):
        return self.c["card_NM_minus_M"]

    def card_N_M(self):
        return self.c["card_N_M"]

    def card_N_A(self):
        return self.c["card_N_A"]

    def card_NA_minus_A(self):
        return self.c["card_NA_minus_A"]

    def card_NB_minus_B(self):
        return self.c["card_NB_minus_B"]

    def N_edge(self, kind):
        return self.c["N_edge_max"] if kind == "max" else self.c["N_edge_min"]

    def Nbar_edge(self, kind):
        v = self.c["Nbar_edge_max" if kind == "max" else "Nbar_edge_min"]
        if v is None:
            raise Undef("complement edgeless")
        return v

    def radial_orders(self):
        out = []
        for c, orders in self.c["radial_circle_orders_at_center"].items():
            out.extend(orders)
        return out

    def radial_ring_edges_max(self):
        """max |E(R(c))| over centers c (edges within the radial circle)."""
        best = 0
        for c in self.Cset():
            seen, _lay = iv.bfs_layers(self.G, c)
            r = self.rad
            ring = [v for v, dd in seen.items() if dd == r]
            e = self.G.subgraph(ring).number_of_edges() if ring else 0
            best = max(best, e)
        return best

    def comp_of_named(self, setname):
        """induced subgraph helper targets used by several readings"""
        mapping = {
            "A": self.A, "M": self.M, "B": self.Bset, "C": self.Cset,
            "D2": self.D2set, "P": self.Ppend, "S": self.Supp,
            "Mmode": self.ModeMinSet,
        }
        return mapping[setname]()

    # scalar invariants
    def alpha(self):
        return self._cert_scalar("alpha")

    def alpha_lb(self):
        return ("lb", self._incumbent("alpha"))

    def f(self):
        return self._cert_scalar("f")

    def f_lb(self):
        return ("lb", self._incumbent("f"))

    def tree_(self):
        return self._cert_scalar("tree")

    def tree_lb(self):
        return ("lb", self._incumbent("tree"))

    def b(self):
        return self._cert_scalar("b")

    def b_lb(self):
        return ("lb", self._incumbent("b"))

    def path_induced(self):
        return self._cert_scalar("path_induced")

    def p_cov(self):
        return self._cert_scalar("p_cov")

    def ham(self):
        return bool(self.c.get("ham_path"))

    def traceable_char(self):
        return 1 if self.ham() else None

    def L_s(self):
        return self._cert_scalar("L_s")

    def L_s_lb(self):
        return ("lb", self._incumbent("L_s"))

    def mu(self):
        return self.c["mu"]

    def omega(self):
        r = self.c["omega"]
        if isinstance(r, dict):
            if r.get("certified"):
                return r["value"]
            raise Undef("omega bracketed")
        return int(r)

    def gamma_(self):
        return self._cert_scalar("gamma")

    def gamma_t(self):
        return self._cert_scalar("gamma_t")

    def gamma_t_ub(self):
        return ("ub", self._incumbent("gamma_t"))

    def gamma_2(self):
        return self._cert_scalar("gamma_2")

    def i_(self):
        return self._cert_scalar("i")

    def i_ub(self):
        return ("ub", self._incumbent("i"))

    def residue(self):
        return self.c["residue"]

    def HH_k(self):
        return self.c["HH_steps"]

    def annihilation(self):
        return self.c["annihilation"]

    def CW(self):
        return revive(self.c["CW"])

    def maxine(self):
        return self.c["maxine"]

    def WP_bar(self):
        return self.c["WP_complement"]

    def SW_G(self):
        return self.c["SW_G"]

    def SW_comp(self):
        return self.c["SW_comp"]

    def v_cover(self):
        return self.n - self.alpha()

    def length(self):
        return sympy.sqrt(self.c["length_sq"])

    def alphacore(self):
        if self.vt_full and self.alpha() < self.n:
            return 0
        raise Undef("alphacore structural argument unavailable")

    def A_core(self):
        """intersection of all maximum independent sets (as vertex list)"""
        if self.vt_full and self.alpha() < self.n:
            return []
        raise Undef("core unavailable")

    def u_char(self):
        if self.vt_full and self.alpha() < self.n:
            return 0
        raise Undef("u char unavailable")

    # triangles / K4 / disparity
    def T_max(self):
        return self.c["T_max"]

    def T_min(self):
        return self.c["T_min"]

    def freq_T_max(self):
        return self.c["freq_T_max"]

    def t_total(self):
        return self.c["triangles_total"]

    def K4_freqmax(self):
        return self.c["freq_K4_max"]

    def K4_max(self):
        return self.c["K4_max"]

    def dd_K4seq(self):
        return self.c["dd_K4_seq"]

    def chi_C4free(self):
        return self.c["chi_C4free"]

    def bipartite_char(self):
        return self.c["bipartite"]

    def disp_stat(self, kind):
        dv = sorted(self.c["disp"].values())
        if kind == "min":
            return dv[0]
        if kind == "max":
            return dv[-1]
        return Fraction(sum(dv), len(dv))

    # connectivity-ish
    def kappa(self):
        return self.c["kappa_vertex"]

    def kappa_v_count(self):
        return self.c["cut_vertices"]

    def components(self):
        return self.c["components"]

    def isolates(self):
        return self.c["isolates"]

    def dp_pairs(self):
        return self.c["dp_diametral_pairs"]

    def two_B_pairs(self):
        return self.c["two_B_pairs"]

    # medians / quartiles / modes
    def median(self, which="median"):
        return revive(self.c["median_" + which])

    def q1(self, reading="ceil"):
        return self.c["q1_" + reading]

    def mode_min(self):
        return self.c["mode_mode_min"]

    def mode_max(self):
        return self.c["mode_mode_max"]

    def dd_mode(self):
        return self.c["mode_dd_mode"]

    def even_mode_min(self, of_complement=False):
        v = self.c["mode_even_mode_min"]
        if of_complement:
            v = H_mode_stats(nx.complement(self.G))["even_mode_min"]
        if v is None:
            raise Undef("no even modes")
        return v

    def even_mode_max(self, of_complement=False):
        v = self.c["mode_even_mode_max"]
        if of_complement:
            v = H_mode_stats(nx.complement(self.G))["even_mode_max"]
        if v is None:
            raise Undef("no even modes")
        return v

    # ---- square graph quantities
    def G2_Delta(self):
        return max(dict(self.G2.degree()).values())

    def G2_M(self):
        dd = dict(self.G2.degree())
        mx = max(dd.values())
        return [v for v in dd if dd[v] == mx]

    def G2_rad_diam(self):
        H2 = self.G2
        ecc = dict(nx.eccentricity(H2))
        return min(ecc.values()), max(ecc.values())

    def G2_dist_min_M(self):
        Msq = self.G2_M()
        d = [self.dm[a][b] for i, a in enumerate(Msq)
             for b in Msq[i + 1:]]
        return min(d) if d else 0

    def G2_dist_avg_within(self):
        return H.dist_avg_within(self.G2, list(self.G2.nodes()))

    # ---- critical independent sets / H
    def crit_info(self):
        ci = self.c["alpha_crit"]
        if not isinstance(ci, dict) or not ci.get("certified"):
            raise Undef("alpha_crit not certified")
        return ci["D"], ci["aprime"]

    def H_union_maxcrit(self, enum_cap=25):
        """H = union of maximum critical independent sets."""
        D, aprime = self.crit_info()
        if aprime == 0:
            # check whether any NONEMPTY critical set exists
            import pulp
            vs = list(self.G.nodes())
            prob = pulp.LpProblem("critfeas", pulp.LpMaximize)
            x = {v: pulp.LpVariable(f"x_{i}", cat="Binary")
                 for i, v in enumerate(vs)}
            y = {v: pulp.LpVariable(f"y_{i}", 0, 1) for i, v in enumerate(vs)}
            for u, v in self.G.edges():
                prob += x[u] + x[v] <= 1
            for v in vs:
                for u in self.G[v]:
                    prob += y[v] >= x[u]
            prob += pulp.lpSum(x.values())
            prob += pulp.lpSum(x.values()) - pulp.lpSum(y.values()) >= D
            prob += pulp.lpSum(x.values()) >= 1
            prob.solve(pulp.PULP_CBC_CMD(msg=0, timeLimit=20))
            if pulp.LpStatus[prob.status] in ("Infeasible",):
                return []
            if pulp.LpStatus[prob.status] != "Optimal":
                raise Undef("critical-set feasibility undecided")
            raise Undef("nonempty critical sets exist; enumeration needed")
        raise Undef("aprime > 0; enumeration needed")

    # ---- spectral (closed forms handled by family table; numeric fallbacks)
    def lambda1_numeric(self):
        return self.c["lambda1_numeric"]

    def algebraic_connectivity_numeric(self):
        return self.c["algebraic_connectivity_numeric"]

    def proximity(self):
        return self.c["proximity"]

    def remoteness(self):
        return self.c["remoteness"]

    def avg_distance(self):
        return self.c["avg_distance"]

    def randic(self):
        return self.c["randic_index"]

    def mu_bar(self):
        Hc = nx.complement(self.G)
        return len(nx.max_weight_matching(Hc, maxcardinality=True))

    def gamma2_bar(self):
        r = iv.gamma_2(nx.complement(self.G), 40.0)
        if r["certified"]:
            return r["value"]
        raise Undef("gamma_2(bar) bracketed")

    def median_lower_bar(self):
        ds = sorted(d for _, d in nx.complement(self.G).degree())
        nn = len(ds)
        if nn % 2 == 1:
            return ds[(nn + 1) // 2 - 1]
        return ds[nn // 2 - 1]  # lower median

    def edge_connectivity(self):
        return self.c["kappa_edge"]


def H_mode_stats(G):
    from collections import Counter
    cnt = Counter(d for _, d in G.degree())
    mx = max(cnt.values())
    modes = sorted(k for k, v in cnt.items() if v == mx)
    ev = sorted(k for k in modes if k % 2 == 0)
    return {"mode_min": modes[0], "mode_max": modes[-1],
            "dd_mode": len(modes),
            "even_mode_min": ev[0] if ev else None,
            "even_mode_max": ev[-1] if ev else None}
