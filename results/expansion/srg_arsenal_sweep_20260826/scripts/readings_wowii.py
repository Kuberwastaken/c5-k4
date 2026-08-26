"""Readings for every open WOWII entry against the arsenal.

Each builder: (X) -> list of dicts
  {"interp","lhs","rhs"[,"premise"][,"conclusion"][,"confidence"]}
lhs/rhs return scalars (exact) or tuples ("lb"/"ub", value).
Any function may raise xctx.Undef -> reading unusable on that graph.
"""
from fractions import Fraction

import networkx as nx

import helpers as H
from xctx import Undef, ex_ceil, ex_floor


def R(interp, lhs=None, rhs=None, premise=None, conclusion=None,
      confidence="high"):
    return {"interp": interp, "lhs": lhs, "rhs": rhs, "premise": premise,
            "conclusion": conclusion, "confidence": confidence}


def _avg_ecc_within_set_members(X, members):
    vals = [X.c["ecc"][v] for v in members]
    if not vals:
        raise Undef("empty")
    return Fraction(sum(vals), len(vals))


# ---------------------------------------------------------------- f/tree

def build_02(X):
    lam = X.lambda_stats()
    a = lam["avg"]
    mx = lam["max"]
    out = [
        R("L_s >= 2*(lambda_avg - 1)",
          lambda X=X: X.L_s_lb(), lambda X=X: 2 * (a - 1)),
        R("alt precedence: L_s >= 2*lambda_avg - 1",
          lambda X=X: X.L_s_lb(), lambda X=X: 2 * a - 1),
        R("glossary 'maximum' variant: L_s >= 2*(lambda_max - 1)",
          lambda X=X: X.L_s_lb(), lambda X=X: 2 * (mx - 1)),
    ]
    return out


def build_19(X):
    ea = X.ecc_avg_G()
    lm = X.lambda_stats()["max"]
    return [
        R("b >= floor(ecc_avg + lambda_max)",
          lambda: X.b(), lambda: ex_floor(ea + lm)),
        R("alt grouping: b >= floor(ecc_avg) + lambda_max",
          lambda: X.b(), lambda: ex_floor(ea) + lm),
    ]


def _p_path_cover(X):
    return X.p_cov()


def build_40(X):
    return [R("f >= ceil((p_cov + b + 1)/2)",
              lambda: X.f(),
              lambda: ex_ceil(Fraction(_p_path_cover(X) + X.b() + 1, 2)))]


def build_59(X):
    return [R("f >= ceil(sqrt(residue*b))",
              lambda: X.f(),
              lambda: ex_ceil(__import__("sympy").sqrt(X.residue() * X.b())))]


def build_61(X):
    return [R("f >= residue + ceil(diam/3)",
              lambda: X.f(), lambda: X.residue() + ex_ceil(Fraction(X.diam, 3)))]


def build_63(X):
    de_min = X.dist_even("min")
    return [R("f >= ceil((min dist_even + b + 1)/3)  [KILLED 2026-07-23]",
              lambda: X.f(),
              lambda: ex_ceil(Fraction(de_min + X.b() + 1, 3)))]


def build_64(X):
    return [R("f >= ceil(sqrt(alpha*(1 + n mod Delta)))  [KILLED 2026-07-26]",
              lambda: X.f(),
              lambda: ex_ceil(__import__("sympy").sqrt(
                  X.alpha() * (1 + X.n % X.Delta))))]


def build_65(X):
    return [R("f >= dist_min(A) + ceil(dist_min(M)/3)",
              lambda: X.f(),
              lambda: X.c["dist_min_A"] + ex_ceil(Fraction(X.c["dist_min_M"], 3)))]


def build_66(X):
    em = X.even_mode_min(of_complement=True)
    da = X.deg_avg
    return [R("f >= 2*ceil(even_mode_min(bar)/deg_avg_G)",
              lambda: X.f(), lambda: 2 * ex_ceil(Fraction(em, 1) / da))]


def build_72(X):
    ea = X.ecc_avg_G()
    lm = X.lambda_stats()["max"]
    return [
        R("tree >= ceil((ecc_avg + lambda_max)/3)",
          lambda: X.tree_lb(), lambda: ex_ceil((ea + lm) / 3)),
        R("alt grouping: tree >= ceil(ecc_avg + lambda_max/3)",
          lambda: X.tree_lb(), lambda: ex_ceil(ea + Fraction(lm, 3))),
    ]


def build_76(X):
    fm = X.freq_T_max()
    da = X.deg_avg
    return [R("tree >= freq[T_max]/floor(deg_avg)",
              lambda: X.tree_lb(),
              lambda: Fraction(fm, 1) / ex_floor(da))]


def build_84(X):
    return [R("tree >= 2*rad/delta",
              lambda: X.tree_lb(), lambda: Fraction(2 * X.rad, X.delta))]


def build_85(X):
    de_min = X.dist_even("min")
    return [R("tree >= ceil(sqrt(1 + 2*min dist_even))  [KILLED 2026-07-23]",
              lambda: X.tree_lb(),
              lambda: ex_ceil(__import__("sympy").sqrt(1 + 2 * de_min)))]


def build_96(X):
    de_min = X.dist_even("min")
    lm = X.lambda_stats()["max"]
    return [R("alpha <= 1 + min dist_even*(lambda_max - 1)",
              lambda: X.alpha(), lambda: 1 + de_min * (lm - 1))]


def build_100(X):
    lm = X.lambda_stats()["max"]
    import sympy
    lenbar = sympy.sqrt(sum(d * d for _, d in nx.complement(X.G).degree()))
    return [R("alpha <= ceil((lambda_max + 0.5*length(bar))/2)",
              lambda: X.alpha(),
              lambda: ex_ceil((lm + sympy.Rational(1, 2) * lenbar) / 2))]


def build_103(X):
    import sympy
    ea = X.ecc_avg_G()
    return [R("alpha <= floor(b - ln(ecc_avg))  [externally refuted 2026-07-20]",
              lambda: X.alpha(),
              lambda: ex_floor(X.b() - sympy.log(ea)))]


def build_108(X):
    de_max = X.dist_even("max")
    ac = X.alphacore()
    return [R("alpha <= max dist_even + 2*floor(alphacore/3)",
              lambda: X.alpha(), lambda: de_max + 2 * ex_floor(Fraction(ac, 3)))]


def build_111(X):
    Hc = nx.complement(X.G)
    dd = dict(Hc.degree())
    mx = max(dd.values())
    Sm = [v for v in dd if dd[v] == mx]
    NS = H.N_of(Hc, Sm)
    NSc = H.Nclosed_of(Hc, Sm)
    lam = X.lambda_stats()

    def lam_bar_avg():
        lb = X.lambda_per_vertex_bar()
        from fractions import Fraction as Fr
        return Fr(sum(lb.values()), len(lb))
    return [
        R("reading A: alpha <= ceil(1 + |N_comp(S_comp)|*(lambda_avg_G-1))",
          lambda: X.alpha(),
          lambda: ex_ceil(1 + len(NS) * (lam["avg"] - 1))),
        R("reading B: closed neighborhood in complement",
          lambda: X.alpha(),
          lambda: ex_ceil(1 + len(NSc) * (lam["avg"] - 1))),
        R("reading C: open N_comp(S_comp), lambda_avg of COMPLEMENT",
          lambda: X.alpha(),
          lambda: ex_ceil(1 + len(NS) * (lam_bar_avg() - 1))),
        R("reading D: closed N_comp[S_comp], lambda_avg of COMPLEMENT",
          lambda: X.alpha(),
          lambda: ex_ceil(1 + len(NSc) * (lam_bar_avg() - 1)))]


def build_133(X):
    r = X.rad
    lam = X.lambda_stats()["avg"]
    chi = X.chi_C4free()
    rhs_val = lam if chi == 1 else 1
    return [R("path >= rad + [lambda_avg]^chi_C4 (exponent)",
              lambda: X.path_induced(), lambda: r + rhs_val)]


def build_141(X):
    return [R("tree >= girth/2 - 1 + lambda_max  [resolved T 2026-08-04]",
              lambda: X.tree_lb(),
              lambda: Fraction(X.girth, 2) - 1 + X.lambda_stats()["max"])]


def _eccB_readings(X):
    return [("ecc(B) = member max (=diam)", X.Bset()[0] and X.diam),
            None]


def build_142(X):
    return [
        R("tree >= (2/3)girth + ecc(B), ecc(B)=diam (members all diametral)",
          lambda: X.tree_lb(), lambda: Fraction(2 * X.girth, 3) + X.diam),
        R("tree >= (2/3)girth + ecc_def52(B)",
          lambda: X.tree_lb(),
          lambda: Fraction(2 * X.girth, 3) + H.ecc_set(X.G, X.Bset())),
    ]


def build_144(X):
    return [
        R("tree >= girth - 1 + ecc(C) members (=radius)",
          lambda: X.tree_lb(), lambda: X.girth - 1 + X.rad),
        R("tree >= girth - 1 + ecc_def52(C)",
          lambda: X.tree_lb(),
          lambda: X.girth - 1 + H.ecc_set(X.G, X.Cset())),
    ]


def build_145(X):
    lmin_bar = min(X.lambda_per_vertex_bar().values())
    if lmin_bar == 0:
        raise Undef("lambda_min(bar) = 0 (complement has isolated vertex); "
                    "division undefined")
    return [
        R("tree >= 2*ecc(B)/lambda_min(bar), ecc(B)=diam",
          lambda: X.tree_lb(), lambda: Fraction(2 * X.diam, 1) / lmin_bar),
        R("tree >= 2*ecc_def52(B)/lambda_min(bar)",
          lambda: X.tree_lb(),
          lambda: Fraction(2 * H.ecc_set(X.G, X.Bset()), 1) / lmin_bar),
    ]


def build_146(X):
    gr2, _ = X.G2_rad_diam()
    return [
        R("tree >= 2*ecc(B)/rad(G^2), ecc(B)=diam",
          lambda: X.tree_lb(), lambda: Fraction(2 * X.diam, 1) / gr2),
        R("tree >= 2*ecc_def52(B)/rad(G^2)",
          lambda: X.tree_lb(),
          lambda: Fraction(2 * H.ecc_set(X.G, X.Bset()), 1) / gr2),
    ]


# ------------------------------------------------------------------ L_s

def build_154(X):
    orders = X.radial_orders()
    if not orders:
        raise Undef("no radial circles at radius>=1")
    return [R("L_s >= (1 + max order of radial circles)/min order",
              lambda: X.L_s_lb(),
              lambda: Fraction(1 + max(orders), min(orders)))]


def build_155(X):
    orders = X.radial_orders()
    return [R("L_s >= 1 + number of distinct radial-circle orders",
              lambda: X.L_s_lb(), lambda: 1 + len(set(orders)))]


def build_157(X):
    f1 = X.c["f1_deg1_freq"]
    emax = X.radial_ring_edges_max()
    return [R("L_s >= f_1 + sqrt(2*max |E(R(v))| over centers)",
              lambda: X.L_s_lb(),
              lambda: f1 + ex_floor(__import__("sympy").sqrt(2 * emax)))]


def build_160(X):
    return [R("L_s >= lambda_max + T_max*chi_C4free",
              lambda: X.L_s_lb(),
              lambda: X.lambda_stats()["max"] +
              X.T_max() * X.chi_C4free())]


def build_161(X):
    lmbar = max(X.lambda_per_vertex_bar().values())
    return [R("L_s >= lambda_max(bar)",
              lambda: X.L_s_lb(), lambda: lmbar)]


def build_162(X):
    lamv = X.lambda_per_vertex()
    mn = min(lamv.values())
    freq = list(lamv.values()).count(mn)
    fl = ex_floor(Fraction(1, X.delta))
    return [R("L_s >= freq(lambda_min)*floor(1/delta)",
              lambda: X.L_s_lb(), lambda: freq * fl)]


def build_165(X):
    k = X.card_NM_minus_M()
    return [R("L_s >= ceil(sqrt(2*|N(M)-M|))",
              lambda: X.L_s_lb(),
              lambda: ex_ceil(__import__("sympy").sqrt(2 * k)))]


def build_166(X):
    k = X.card_NM_minus_M()
    return [R("L_s >= |N(M)-M|/sqrt(rad)",
              lambda: X.L_s_lb(),
              lambda: Fraction(k, 1) / __import__("sympy").sqrt(X.rad))]


def build_169(X):
    return [R("L_s >= 1 + max dist_even - min dist_even",
              lambda: X.L_s_lb(),
              lambda: 1 + X.dist_even("max") - X.dist_even("min"))]


def build_171(X):
    dab = H.dist_avg_within(X.G, X.Bset())
    return [R("L_s >= (-1 + max dist_even)/dist_avg(B within)",
              lambda: X.L_s_lb(),
              lambda: Fraction(X.dist_even("max") - 1, 1) / dab)]


def build_172(X):
    db = X.diam  # Delta(B) members = diam; alt below
    dm2 = X.G2_dist_min_M()
    return [
        R("L_s >= -1 + Delta(B) + dist_min(M(G^2)), Delta(B)=diam "
          "[KILLED family 2026-08]",
          lambda: X.L_s_lb(), lambda: -1 + db + dm2),
        R("alt: Delta_def52(B) + dist_min(M(G^2))",
          lambda: X.L_s_lb(),
          lambda: -1 + H.induced_max_degree(X.G, X.Bset()) + dm2),
    ]


def build_174(X):
    return [R("L_s + b >= n + lambda_max - 1 [externally refuted 2026-07-23]",
              lambda: ("lb", X._incumbent("L_s") + X._incumbent("b")),
              lambda: X.n + X.lambda_stats()["max"] - 1)]


def build_176(X):
    return [R("L_s + b >= n + dist_min(M(G^2))  [KILLED 2026-08]",
              lambda: ("lb", X._incumbent("L_s") + X._incumbent("b")),
              lambda: X.n + X.G2_dist_min_M())]


def build_177(X):
    return [R("L_s + b >= 2*alpha + sigma",
              lambda: ("lb", X._incumbent("L_s") + X._incumbent("b")),
              lambda: 2 * X.alpha() + X.sigma)]


def build_178(X):
    return [R("L_s + b >= lambda_max + max|N(e)| [resolved T 2026-07-23]",
              lambda: ("lb", X._incumbent("L_s") + X._incumbent("b")),
              lambda: X.lambda_stats()["max"] + X.N_edge("max"))]


def build_179(X):
    return [R("L_s + b >= Delta + domination + lambda_max",
              lambda: ("lb", X._incumbent("L_s") + X._incumbent("b")),
              lambda: X.Delta + X.gamma_() + X.lambda_stats()["max"])]


def build_180(X):
    return [R("L_s + b >= 1 + alpha + max dist_even",
              lambda: ("lb", X._incumbent("L_s") + X._incumbent("b")),
              lambda: 1 + X.alpha() + X.dist_even("max"))]


def build_181(X):
    def rhs():
        B2 = X.Bset()
        dd2 = dict(X.G2.degree())
        vals = [dd2[v] for v in B2]
        return Fraction(sum(vals), len(vals))
    return [R("L_s + b >= alpha + deg_avg(B(G^2)) [KILLED via T(7) 2026-08]",
              lambda: ("lb", X._incumbent("L_s") + X._incumbent("b")),
              rhs)]


def build_182(X):
    B2 = X.Bset()
    d2max = max(dict(X.G2.degree())[v] for v in B2)
    return [R("L_s + b >= Delta(B(G^2)) + diam",
              lambda: ("lb", X._incumbent("L_s") + X._incumbent("b")),
              lambda: d2max + X.diam)]


def build_183(X):
    r2, _ = X.G2_rad_diam()
    return [R("L_s + b >= Delta(G^2) + 2*rad(G^2)",
              lambda: ("lb", X._incumbent("L_s") + X._incumbent("b")),
              lambda: X.G2_Delta() + 2 * r2)]


def build_184(X):
    B2 = X.Bset()

    def rhs():
        dd2 = X.dm  # distances measured in G^2 needed!
        H2 = X.G2
        dm2 = dict(nx.all_pairs_shortest_path_length(H2))
        tot = cnt = 0
        for s in B2:
            for v in H2.nodes():
                d = dm2[s][v]
                if d > 0:
                    tot += d
                    cnt += 1
        return X.G2_Delta() + 2 * Fraction(tot, cnt)
    return [R("L_s + b >= Delta(G^2) + 2*dist_avg(B(G^2),V(G^2)) [pairs avg]",
              lambda: ("lb", X._incumbent("L_s") + X._incumbent("b")), rhs),
            R("alt per-vertex avg: 2*avg_v dist_{G2}(v, B(G2))",
              lambda: ("lb", X._incumbent("L_s") + X._incumbent("b")),
              lambda: X.G2_Delta() + 2 *
              H.dist_avg_V_from_S(X.G2, B2))]


def build_185(X):
    return [R("L_s + b >= Delta(G^2) + 2*dist_avg(G^2)",
              lambda: ("lb", X._incumbent("L_s") + X._incumbent("b")),
              lambda: X.G2_Delta() + 2 * X.G2_dist_avg_within())]


def build_186(X):
    H2 = X.G2
    ecc2 = dict(nx.eccentricity(H2))
    c2 = [v for v in ecc2 if ecc2[v] == min(ecc2.values())]
    NC2 = H.N_of(H2, c2)

    def e_cc():
        return H.ecc_set(H2, c2)
    return [R("L_s + b >= |N(C(G^2))| + 2*ecc_def52(C(G^2))",
              lambda: ("lb", X._incumbent("L_s") + X._incumbent("b")),
              lambda: len(NC2) + 2 * e_cc()),
            R("alt member reading: ecc(C(G2)) = radius(G2)",
              lambda: ("lb", X._incumbent("L_s") + X._incumbent("b")),
              lambda: len(NC2) + 2 * min(ecc2.values()))]


# ------------------------------------------------- Hamiltonian path claims

def _ham(interp, premise):
    return R(interp + " ==> G has a Hamiltonian path", premise=premise,
             conclusion="ham")


def build_189(X):
    return [_ham("max dist_even <= 1 + sigma",
                 lambda: X.dist_even("max") <= 1 + X.sigma)]


def build_190(X):
    return [_ham("0.5*(L_s+1) <= sigma",
                 lambda: Fraction(X._incumbent("L_s") + 1, 2) <= X.sigma)]


def build_194(X):
    return [_ham("alpha <= 1 + lambda_avg",
                 lambda: X.alpha() <= 1 + X.lambda_stats()["avg"])]


def build_198a(X):
    return [_ham("b <= 2 + ecc_avg(M)",
                 lambda: X.b() <= 2 + _avg_ecc_within_set_members(
                     X, X.M()))]


def build_199(X):
    return [_ham("tree - 2 <= kappa",
                 lambda: X.tree_() - 2 <= X.kappa())]


def build_200(X):
    return [_ham("tree == ceil(1 + lambda_avg) [externally refuted]",
                 lambda: X.tree_() == ex_ceil(1 + X.lambda_stats()["avg"]))]


def build_209(X):
    return [_ham("(1/6)*(1 + 2*|E(bar)|) <= freq(lambda_max(G)) "
                 "[externally refuted]",
                 lambda: Fraction(1 + 2 * len(list(
                     nx.complement(X.G).edges())), 6)
                 <= X.freq_lambda_max_G())]


def build_213(X):
    return [_ham("2 + lower median of bar degree seq <= gamma_2(bar)",
                 lambda: 2 + X.median_lower_bar() <= X.gamma2_bar())]


def build_217(X):
    chi2 = 1 if X.residue() == 2 else 0
    return [_ham("L(G) (#pendants) <= 4*chi_residue=2(G) + 2",
                 lambda chi2=chi2: X.c["f1_deg1_freq"] <= 4 * chi2 + 2)]


# ------------------------------------------------------------ gamma_t bounds

def build_232(X):
    return [
        R("gamma_t >= 0.5*(radius + ecc(B)), ecc(B)=diam",
          lambda: ("ub", X._incumbent("gamma_t")),
          lambda: Fraction(X.rad + X.diam, 2)),
        R("gamma_t >= 0.5*(radius + ecc_def52(B))",
          lambda: ("ub", X._incumbent("gamma_t")),
          lambda: Fraction(X.rad, 1) + Fraction(H.ecc_set(X.G, X.Bset()), 2)),
    ]


def build_233(X):
    return [
        R("gamma_t >= (2/3)*(1 + ecc(B)=diam)",
          lambda: ("ub", X._incumbent("gamma_t")),
          lambda: Fraction(2 * (1 + X.diam), 3)),
        R("gamma_t >= (2/3)*(1 + ecc_def52(B))",
          lambda: ("ub", X._incumbent("gamma_t")),
          lambda: Fraction(2 * (1 + H.ecc_set(X.G, X.Bset())), 3)),
    ]


def build_235(X):
    return [
        R("gamma_t >= (2/3)*ecc(B)=diam + chi_bipartite",
          lambda: ("ub", X._incumbent("gamma_t")),
          lambda: Fraction(2 * X.diam, 3) + X.bipartite_char()),
        R("gamma_t >= (2/3)*ecc_def52(B) + chi_bipartite",
          lambda: ("ub", X._incumbent("gamma_t")),
          lambda: Fraction(2 * H.ecc_set(X.G, X.Bset()), 3)
          + X.bipartite_char()),
    ]


def _comp_Nclosed_D2(X):
    S = X.D2set()
    return H.Nclosed_of(X.G, S)


def build_241(X):
    Sub = X.G.subgraph(H.Nclosed_of(X.G, X.D2set()))
    ncomp = nx.number_connected_components(Sub)
    dac = H.dist_avg_within(X.G, X.Cset())
    return [R("gamma_t >= floor[components(<N[S_deg2]>) + dist_avg(C within)]",
              lambda: ("ub", X._incumbent("gamma_t")),
              lambda: ex_floor(ncomp + dac))]


def build_242(X):
    Sub = X.G.subgraph(H.Nclosed_of(X.G, X.D2set()))
    ncomp = nx.number_connected_components(Sub)
    return [R("gamma_t >= (1/2)[components(<N[S_deg2]>) + ecc_avg(G)]",
              lambda: ("ub", X._incumbent("gamma_t")),
              lambda: Fraction(ncomp + _sum_ecc(X), 2))]


def _sum_ecc(X):
    ecc = X.c["ecc"]
    return Fraction(sum(ecc.values()), X.n)


def build_247(X):
    return [R("gamma_t >= 2*p_cov(G)",
              lambda: ("ub", X._incumbent("gamma_t")),
              lambda: 2 * X.p_cov())]


def build_252(X):
    return [R("gamma_t >= mode_min",
              lambda: ("ub", X._incumbent("gamma_t")),
              lambda: X.mode_min(),
              premise=lambda X=X: X.chi_C4free() == 1)]


def build_253(X):
    return [R("gamma_t >= 1 + mode_min",
              lambda: ("ub", X._incumbent("gamma_t")),
              lambda: 1 + X.mode_min(),
              premise=lambda X=X: X.girth >= 5)]


def build_255(X):
    ne = X.N_edge("max")
    return [R("gamma_t >= 2*|C|/max|N(e)|",
              lambda: ("ub", X._incumbent("gamma_t")),
              lambda: Fraction(2 * len(X.Cset()), ne))]


def build_256(X):
    ne = X.N_edge("max")
    return [R("gamma_t >= 2*|N(A)|/max|N(e)|",
              lambda: ("ub", X._incumbent("gamma_t")),
              lambda: Fraction(2 * X.card_N_A(), ne))]


def build_258(X):
    emax = X.dist_even("max")
    L = X.c["f1_deg1_freq"]
    if L == 0:
        raise Undef("no leaves: L=0 division")
    return [R("gamma_t >= 2*even_max/L(G)",
              lambda: ("ub", X._incumbent("gamma_t")),
              lambda: Fraction(2 * emax, L))]


def _gt_frac_named(X, setfn):
    L = X.c["f1_deg1_freq"]
    if L == 0:
        raise Undef("no leaves")
    S = setfn()
    NS = H.N_of(X.G, S)
    k = len(NS - set(S))
    return Fraction(2 * k, L)


def build_259(X):
    return [R("gamma_t >= 2*|N(M)-M|/L(G)",
              lambda: ("ub", X._incumbent("gamma_t")),
              lambda: _gt_frac_named(X, X.M))]


def build_260(X):
    return [R("gamma_t >= 2*|N(B)-B|/L(G)",
              lambda: ("ub", X._incumbent("gamma_t")),
              lambda: _gt_frac_named(X, X.Bset))]


def build_261(X):
    return [R("gamma_t >= 2*|N(S_deg2)-S_deg2|/L(G)",
              lambda: ("ub", X._incumbent("gamma_t")),
              lambda: _gt_frac_named(X, X.D2set))]


def build_267(X):
    A = X.A()

    def pairs():
        dm = X.dm
        tot = cnt = 0
        for s in A:
            for v in X.G.nodes():
                d = dm[s][v]
                if d > 0:
                    tot += d
                    cnt += 1
        return Fraction(tot, cnt)

    def per_v():
        dm = X.dm
        vals = []
        for v in X.G.nodes():
            d = min(dm[v][s] for s in A)
            if d > 0:
                vals.append(d)
        if not vals:
            raise Undef("per-vertex dist_avg(A,V): all distances zero")
        return Fraction(sum(vals), len(vals))
    return [
        R("gamma_t >= ceil[dist_avg(A,V)] pairs-average",
          lambda: ("ub", X._incumbent("gamma_t")), lambda: ex_ceil(pairs())),
        R("alt per-vertex average",
          lambda: ("ub", X._incumbent("gamma_t")), lambda: ex_ceil(per_v()))]


def build_268(X):
    dc = H.dist_avg_within(X.G, X.Cset())
    return [R("gamma_t >= floor[1 + dist_avg(C within)]",
              lambda: ("ub", X._incumbent("gamma_t")),
              lambda: ex_floor(1 + dc))]


def build_269(X):
    dc = H.dist_avg_within(X.G, X.Cset())
    return [R("gamma_t >= ceil[1 + dist_avg(C within)]",
              lambda: ("ub", X._incumbent("gamma_t")),
              lambda: ex_ceil(1 + dc),
              premise=lambda X=X: X.chi_C4free() == 1)]


def build_271(X):
    dMM = X.c["dist_max_M"]
    return [R("gamma_t >= ceil[sqrt(2*dist_max(M))]",
              lambda: ("ub", X._incumbent("gamma_t")),
              lambda: ex_ceil(__import__("sympy").sqrt(2 * dMM)))]


def build_281(X):
    return [R("gamma_t <= freq(lambda_min(bar)) + mu(G)",
              lambda: X.gamma_t_ub(),
              lambda: X.lambda_bar_freq("min") + X.mu())]


def build_287(X):
    return [R("gamma_t <= HH_k + mu(bar(G))",
              lambda: X.gamma_t_ub(),
              lambda: X.HH_k() + X.mu_bar())]


def build_290(X):
    return [R("gamma_t <= HH_k * Delta",
              lambda: X.gamma_t_ub(), lambda: X.HH_k() * X.Delta)]


def build_291(X):
    tmin = X.T_min()
    tv = X.c["T_v"]
    freqmin = list(tv.values()).count(tmin)
    return [
        R("gamma_t <= HH_k + freq(T_min) [externally refuted 2026-07-24]",
          lambda: X.gamma_t_ub(), lambda: X.HH_k() + freqmin),
        R("alt: HH_k + T_min",
          lambda: X.gamma_t_ub(), lambda: X.HH_k() + tmin),
    ]


def build_298(X):
    return [R("gamma_t <= annihilation + chi_C4free",
              lambda: X.gamma_t_ub(),
              lambda: X.annihilation() + X.chi_C4free())]


def build_299(X):
    return [R("gamma_t <= annihilation + |S_deg2|",
              lambda: X.gamma_t_ub(),
              lambda: X.annihilation() + len(X.D2set()))]


def build_300(X):
    return [R("gamma_t <= (n + freq(lambda_min(bar)))/2 "
              "[externally refuted 2026-07-26]",
              lambda: X.gamma_t_ub(),
              lambda: Fraction(X.n + X.lambda_bar_freq("min"), 2))]


def build_302(X):
    return [R("gamma_t <= min dist_even + freq(lambda_max(bar))",
              lambda: X.gamma_t_ub(),
              lambda: X.dist_even("min") + X.lambda_bar_freq("max"))]


def build_304(X):
    return [R("gamma_t <= (freq(lambda_max(bar)) + max|N_bar(e)|)/2",
              lambda: X.gamma_t_ub(),
              lambda: Fraction(X.lambda_bar_freq("max") +
                               X.Nbar_edge("max"), 2))]


def build_305(X):
    return [R("gamma_t <= ceil[(2/3)*max|N_bar(e)|]",
              lambda: X.gamma_t_ub(),
              lambda: ex_ceil(Fraction(2 * X.Nbar_edge("max"), 3)))]


def build_308(X):
    return [R("gamma_t <= (maxine + min|N_bar(e)|)/2",
              lambda: X.gamma_t_ub(),
              lambda: Fraction(X.maxine() + X.Nbar_edge("min"), 2))]


def build_309(X):
    mx = max(X.c["dist_even"][v] - X.c["even_horizontal"][v]
             for v in X.G.nodes())
    return [R("gamma_t <= (1/2)[max(dist_even - even_horizontal) + "
              "min|N_bar(e)|]  [KILLED 2026-07-25]",
              lambda: X.gamma_t_ub(),
              lambda: Fraction(mx + X.Nbar_edge("min"), 2))]


def build_310(X):
    tdmin = min(X.c["Tdist"].values())
    return [R("gamma_t <= ceil[1 + Tdist_min/3]",
              lambda: X.gamma_t_ub(),
              lambda: ex_ceil(1 + Fraction(tdmin, 3)))]


# ------------------------------------------------- wtd conditionals (314-328)

def _wtd(interp, premise):
    return R(interp + " ==> G is well total dominated", premise=premise,
             conclusion="wtd")


def build_314(X):
    return [_wtd("triangle-free and path_number <= 4",
                 lambda: X.t_total() == 0 and X.path_induced() <= 4)]


def build_316(X):
    return [_wtd("|P| >= deg_avg(bar)",
                 lambda: len(X.Ppend()) >= _deg_avg_of(nx.complement(X.G)))]


def _deg_avg_of(Gg):
    return Fraction(2 * Gg.number_of_edges(), Gg.number_of_nodes())


def build_317(X):
    return [_wtd("tree_number >= |E(bar)|",
                 lambda: X.tree_() >= len(list(nx.complement(X.G).edges())))]


def build_318(X):
    return [_wtd("max dist_even >= |E(bar)|",
                 lambda: X.dist_even("max") >=
                 len(list(nx.complement(X.G).edges())))]


def build_319(X):
    return [_wtd("max dist_even == gamma(G)",
                 lambda: X.dist_even("max") == X.gamma_())]


def build_320(X):
    return [_wtd("max dist_even == Tdist_min",
                 lambda: X.dist_even("max") == min(X.c["Tdist"].values()))]


def build_321(X):
    return [_wtd("ecc_avg(G) >= (1/3)*Tdist_max",
                 lambda: _sum_ecc(X) >= Fraction(
                     max(X.c["Tdist"].values()), 3))]


def build_322(X):
    return [_wtd("lambda_max(bar) <= 1 (n>=5)",
                 lambda: max(X.lambda_per_vertex_bar().values()) <= 1)]


def build_323(X):
    mx = max(X.Nbar_edge("max"), 0)

    def prem():
        mo = max(X.c["dist_odd"][v] - X.c["odd_horizontal"][v]
                 for v in X.G.nodes())
        return mx <= 1 + mo
    return [_wtd("max|N_bar(e)| <= 1 + max(dist_odd - odd_horizontal)",
                 prem)]


def build_324(X):
    return [_wtd("min?/max? |N_bar(e)| <= 1 + residue: reading max",
                 lambda: X.Nbar_edge("max") <= 1 + X.residue()),
            _wtd("alt reading min: min|N_bar(e)| <= 1 + residue",
                 lambda: X.Nbar_edge("min") <= 1 + X.residue())]


def build_325(X):
    Sub = X.G.subgraph(H.Nclosed_of(X.G, X.D2set()))
    ncomp = nx.number_connected_components(Sub)
    return [_wtd("min|N_bar(e)| <= 1 + components(<N[S_deg2]>)",
                 lambda: X.Nbar_edge("min") <= 1 + ncomp)]


def build_326(X):
    S2 = X.D2set()

    def prem():
        return bool(S2) and 3 * X.mu() <= H.induced_edges(X.G, S2)
    return [_wtd("3*mu(G) <= |E(S_deg2)|", prem)]


def build_328(X):
    kv = X.c["K4_v"]
    mx = max(kv.values())
    freqmax = list(kv.values()).count(mx)

    def prem():
        if mx == 0:
            return False
        return 4 * X.mu_bar() <= freqmax
    return [_wtd("4*mu(bar) <= freq(max K4 count)", prem)]


# ------------------------------------------------------- tree section 340-381

def build_tree_section(X):
    # every builder for the tree-hypothesis section shares one premise:
    # hypothesis "T is a tree" is FALSE on every arsenal graph.
    def prem_false():
        return False
    return [R("hypothesis 'T is a tree' — false on all arsenal graphs "
              "(premise gate)", premise=prem_false)]


TREE_IDS = [340, 341, 342, 343, 344, 348, 351, 352, 353, 354, 356, 358, 359,
            360, 361, 362, 363, 364, 365, 367, 369, 372, 373, 374, 375, 376,
            377, 378, 379, 380, 381]


# ------------------------------------------------------------- 382+ cluster

def build_382b(X):
    a1 = X.A1set()
    return [R("gamma_2 <= -1 + alpha*(delta + |A_1|)",
              lambda: ("ub", X._incumbent("gamma_2")),
              lambda: -1 + X.alpha() * (X.delta + len(a1)))]


def build_382c(X):
    ea = _avg_ecc_within_set_members(X, X.A())
    return [R("gamma_2 <= (alpha*ecc_avg(A) + |B|)/2",
              lambda: ("ub", X._incumbent("gamma_2")),
              lambda: Fraction(X.alpha() * ea + len(X.Bset()), 2))]


def build_382d(X):
    Xm = X.Xlambdamax_set()
    return [R("gamma_2 <= diam*(alpha + |X_lambda_max|)/2",
              lambda: ("ub", X._incumbent("gamma_2")),
              lambda: Fraction(X.diam * (X.alpha() + len(Xm)), 2))]


def build_382e(X):
    return [R("gamma_2 <= maxine + domination",
              lambda: ("ub", X._incumbent("gamma_2")),
              lambda: X.maxine() + X.gamma_())]


def build_384b(X):
    tv = set(X.c["T_v"].values())
    return [R("gamma_2 <= floor(n - |{distinct triangle counts}|/2)",
              lambda: ("ub", X._incumbent("gamma_2")),
              lambda: ex_floor(X.n - Fraction(len(tv), 2)))]


def build_387(X):
    um = X.c["median_upper"]
    return [R("gamma_2 <= n - upper_median + 1",
              lambda: ("ub", X._incumbent("gamma_2")),
              lambda: X.n - um + 1),
            R("alt lower median",
              lambda: ("ub", X._incumbent("gamma_2")),
              lambda: X.n - X.c["median_lower"] + 1)]


def build_389a(X):
    Mm = X.ModeMinSet()
    q = X.q1("ceil")
    return [R("gamma_2 <= |M_mode_min|*(q1 + |A_deg2|) - 1",
              lambda: ("ub", X._incumbent("gamma_2")),
              lambda: len(Mm) * (q + len(X.D2set())) - 1),
            R("alt q1 floor reading",
              lambda: ("ub", X._incumbent("gamma_2")),
              lambda: len(Mm) * (X.q1("floor") + len(X.D2set())) - 1)]


def build_391(X):
    T2 = X.D2set()

    def rhs():
        mu_T = H.induced_mu(X.G, T2)
        e_A3 = H.induced_edges(X.G, X.A3())
        return X.p_cov() + 1 + mu_T + e_A3
    return [R("gamma_2 <= p + 1 + mu(G[T_deg2]) + |E(G[A_ge3])| "
              "[externally refuted 2026-07-24]",
              lambda: ("ub", X._incumbent("gamma_2")), rhs)]


def build_392b(X):
    Ad = X.A()

    def cnt():
        A2s = set(X.D2set())
        dm = X.dm
        c = 0
        for v in X.G.nodes():
            k = sum(1 for u in X.G[v] if u in A2s)
            if k == 1:
                c += 1
        return c
    return [R("gamma_2 <= mu(G[V-A_delta]) + |A_delta| + "
              "|{v:|N(v) cap A_2|=1}|",
              lambda: ("ub", X._incumbent("gamma_2")),
              lambda: H.induced_mu(X.G, [v for v in X.G.nodes()
                                         if v not in set(Ad)])
              + len(Ad) + cnt())]


def build_392c(X):
    Ad = X.A()
    return [R("gamma_2 <= mu(G[V-A_delta]) + |A_delta| + kappa_v",
              lambda: ("ub", X._incumbent("gamma_2")),
              lambda: H.induced_mu(X.G, [v for v in X.G.nodes()
                                         if v not in set(Ad)])
              + len(Ad) + X.kappa_v_count())]


def _NN_P(X):
    P = set(X.Ppend())
    NP = H.N_of(X.G, P)
    return H.N_of(X.G, NP)


def build_392d(X):
    Ad = len(X.A())
    W = _NN_P(X)
    rest = [v for v in X.G.nodes() if v not in W]
    return [R("gamma_2 <= mu(G) + mu(G[V-N(N(P))]) + |A_delta|",
              lambda: ("ub", X._incumbent("gamma_2")),
              lambda: X.mu() + H.induced_mu(X.G, rest) + Ad)]


def build_392e_f(X):
    Ad = len(X.A())
    A2s = set(X.D2set())
    NA2 = H.N_of(X.G, A2s)

    def cntf():
        c = 0
        for v in X.G.nodes():
            k = sum(1 for u in X.G[v] if u in NA2)
            if k == 1:
                c += 1
        return c
    out = [R("392e: gamma_2 <= mu + mu(G[N(A_2)]) + |A_delta|",
             lambda: ("ub", X._incumbent("gamma_2")),
             lambda: X.mu() + H.induced_mu(X.G, list(NA2)) + Ad)]
    # 392f: Nu(A)=N(A) min-degree neighborhood
    NA = H.N_of(X.G, set(X.A()))

    def cntg():
        c = 0
        for v in X.G.nodes():
            k = sum(1 for u in X.G[v] if u in NA)
            if k == 1:
                c += 1
        return c
    out.append(R("392f: gamma_2 <= mu + mu(G[N(A_2)]) + "
                 "|{v:|N(v) cap N(A_min)|=1}|",
                 lambda: ("ub", X._incumbent("gamma_2")),
                 lambda: X.mu() + H.induced_mu(X.G, list(NA2)) + cntg()))
    return out


def build_393a(X):
    P = len(X.Ppend())
    W = _NN_P(X)
    inside = [v for v in X.G.nodes() if v in W]
    outside = [v for v in X.G.nodes() if v not in W]
    return [R("gamma_2 <= |V-N(N(P))| + mu(G[N(N(P))]) + |P|",
              lambda: ("ub", X._incumbent("gamma_2")),
              lambda: len(outside) + H.induced_mu(X.G, inside) + P)]


def build_393b_c(X):
    P = set(X.Ppend())
    NP = H.N_of(X.G, P)
    W = H.N_of(X.G, NP)
    outside = [v for v in X.G.nodes() if v not in W]

    def e_NP():
        return H.induced_edges(X.G, NP)

    def cnt_open():
        c = 0
        for v in X.G.nodes():
            k = sum(1 for u in X.G[v] if u in NP)
            if k == 1:
                c += 1
        return c

    def cnt_closed():
        NPc = NP | P
        c = 0
        for v in X.G.nodes():
            k = sum(1 for u in X.G[v] if u in NPc)
            if k == 1:
                c += 1
        return c

    def cardNP():
        return len(NP)
    return [
        R("393b: |V-NN(P)| + |E(G[N(P)])| + |{v:|N(v) cap N(P)|=1}|",
          lambda: ("ub", X._incumbent("gamma_2")),
          lambda: len(outside) + e_NP() + cnt_open()),
        R("393c: |V-NN(P)| + |N(P)| + |{v:|N(v) cap N[P]|=1}|",
          lambda: ("ub", X._incumbent("gamma_2")),
          lambda: len(outside) + cardNP() + cnt_closed()),
    ]


def build_393d(X):
    P = set(X.Ppend())
    Mmax = set(X.M())
    NP = H.N_of(X.G, P)
    W = H.N_of(X.G, NP)
    insideW = [v for v in X.G.nodes() if v in W]
    minusM = [v for v in X.G.nodes() if v not in Mmax]
    M4 = X.M4set()
    return [R("393d: mu(G[V-NN(P)]) + alpha(G[V-M]) + |M_4|",
              lambda: ("ub", X._incumbent("gamma_2")),
              lambda: H.induced_mu(X.G, [v for v in X.G.nodes()
                                         if v not in W])
              + H.induced_alpha(X.G, minusM) + len(M4))]


def build_394(X):
    lamv = X.lambda_per_vertex()
    mn = min(lamv.values())
    Mmin = [v for v in lamv if lamv[v] == mn]
    A2s = X.D2set()
    return [R("394: gamma_2 <= mu + |E(G[A_2])| + |M_minlambda|",
              lambda: ("ub", X._incumbent("gamma_2")),
              lambda: X.mu() + H.induced_edges(X.G, A2s) + len(Mmin))]


def build_395a_b(X):
    Mm = X.ModeMinSet()
    Ad = X.A()
    VmAd = [v for v in X.G.nodes() if v not in set(Ad)]
    A2s = set(X.D2set())
    NA2 = H.N_of(X.G, A2s)
    out = [R("395a: |M_mode| + mu(G[V-A_delta]) + mu(G[N(A_2)])",
             lambda: ("ub", X._incumbent("gamma_2")),
             lambda: len(Mm) + H.induced_mu(X.G, VmAd)
             + H.induced_mu(X.G, list(NA2)))]
    # 395b: delta(G[V-A]) members min degree of induced subgraph; empty->0?
    def del_():
        subV = VmAd
        if not subV:
            raise Undef("empty induced")
        return H.induced_min_degree(X.G, subV)
    out.append(R("395b: |M_mode| + delta(G[V-A]) + |V-A_3|",
                 lambda: ("ub", X._incumbent("gamma_2")),
                 lambda: len(Mm) + del_() + (X.n - len(X.A3()))))
    return out


def build_396(X):
    Mm = X.ModeMinSet()
    A3 = set(X.A3())

    def cross():
        c = 0
        for u, v in X.G.edges():
            if (u in A3) != (v in A3):
                c += 1
        return c
    return [R("396: dd_mode + |M_mode| + |E(A_3, V-A_3)|",
              lambda: ("ub", X._incumbent("gamma_2")),
              lambda: X.dd_mode() + len(Mm) + cross())]


def build_397c(X):
    P = set(X.Ppend())
    NP = H.N_of(X.G, P)
    outside = [v for v in X.G.nodes() if v not in NP]
    import invlib as iv
    r = iv.gamma(H.square_graph(X.G), 40.0)
    if not r["certified"]:
        raise Undef("gamma(G^2) bracketed")
    g2 = r["value"]
    return [R("397c: gamma_2 <= |V-N(P)| + gamma(G^2)",
              lambda: ("ub", X._incumbent("gamma_2")),
              lambda: len(outside) + g2)]


def build_398(X):
    P = set(X.Ppend())
    NP = H.N_of(X.G, P)
    W = H.N_of(X.G, NP)
    insideW = [v for v in X.G.nodes() if v in W]
    e_in = H.induced_edges(X.G, insideW)

    def cnt():
        c = 0
        for v in X.G.nodes():
            k = sum(1 for u in X.G[v] if u not in P)
            if k == 1:
                c += 1
        return c

    def e_cross():
        c = 0
        for u, v in X.G.edges():
            if (u in P) != (v in P):
                c += 1
        return c
    return [R("398: |E(G[V-NN(P)])| + |{v:|N(v) cap [V-N(P)]|=1}| + "
              "|E(P,V-P)|",
              lambda: ("ub", X._incumbent("gamma_2")),
              lambda: e_in + cnt() + e_cross())]


def build_399a_b_c(X):
    wp = X.WP_bar()
    Cc = X.Cset()
    A3 = X.A3()
    lamv = X.lambda_per_vertex()
    mn = min(lamv.values())
    Mmin = [v for v in lamv if lamv[v] == mn]
    out = [R("399a: WP(bar) + floor(alpha(G[C])/2)",
             lambda: ("ub", X._incumbent("gamma_2")),
             lambda: wp + ex_floor(Fraction(
                 H.induced_alpha(X.G, Cc), 2))),
           R("399b: WP(bar) + floor(3/alpha(G[A_3]))",
             lambda: ("ub", X._incumbent("gamma_2")),
             lambda: wp + ex_floor(Fraction(3,
                                            max(1, H.induced_alpha(X.G, A3))))),
           R("399c: (2/3)WP(bar) + 2|M_minlambda|",
             lambda: ("ub", X._incumbent("gamma_2")),
             lambda: Fraction(2 * wp, 3) + 2 * len(Mmin))]
    return out


def build_400c(X):
    dmn = X.disp_stat("min")
    return [R("400c: gamma_2 <= floor(3*A/disp_min)",
              lambda: ("ub", X._incumbent("gamma_2")),
              lambda: ex_floor(Fraction(3 * X.annihilation(), dmn)))]


def build_401a_b(X):
    tdmax = max(X.c["Tdist"].values())
    davg = X.disp_stat("avg")
    fm = X.freq_T_max()
    return [R("401a: gamma_2 <= 1 + floor(Tdist_max/disp_avg)",
              lambda: ("ub", X._incumbent("gamma_2")),
              lambda: 1 + ex_floor(Fraction(tdmax, 1) / davg)),
            R("401b: floor(3*Tdist_max/freq[T_max]) "
              "[KNOWN CORRUPT per README]",
              lambda: ("ub", X._incumbent("gamma_2")),
              lambda: ex_floor(Fraction(3 * tdmax, fm)))]


def build_402(X):
    Ad = set(X.A())
    AD = set(X.M())

    def cnt():
        c = 0
        for v in X.G.nodes():
            k = sum(1 for u in X.G[v] if u in AD)
            if k == 1:
                c += 1
        return c
    return [R("402: gamma_2 <= 2[isolates(G[A_delta]) + "
              "|{v:|N(v)cap A_Delta|=1}| + gamma_t]",
              lambda: ("ub", X._incumbent("gamma_2")),
              lambda: 2 * (H.induced_isolates(X.G, Ad) + cnt()
                           + X.gamma_t()))]


# ---------------------------------------------------------------- H entries

def _peN_H(X):
    Hu = X.H_union_maxcrit()
    return H.private_external_neighbors(X.G, set(Hu))


def build_404_407(X):
    Supp = X.Supp()
    # hypothesis: G is a tree on n > 2 vertices (statement premise)
    import networkx as _nx
    is_tree = (_nx.is_tree(X.G) if X.G.number_of_nodes() > 0 else False)

    def r404():
        return 2 * (len(Supp) - 1)

    def peNH():
        return _peN_H(X)
    VmL = [v for v in X.G.nodes() if v not in set(X.Ppend())]
    out = [
        R("404: peN(H) <= 2(|S_support|-1)",
          lambda: ("ub" if False else "exact", peNH()), lambda: r404(),
          premise=lambda: is_tree),
        R("405: peN(H) <= 2*alpha(G[V-L])",
          lambda: ("exact", peNH()),
          lambda: 2 * H.induced_alpha(X.G, VmL),
          premise=lambda: is_tree),
        R("406: peN(H) <= peN(V-L) - 2",
          lambda: ("exact", peNH()),
          lambda: H.private_external_neighbors(
              X.G, set(VmL)) - 2,
          premise=lambda: is_tree),
        R("407: peN(H) <= 2*p_cov",
          lambda: ("exact", peNH()), lambda: 2 * X.p_cov(),
          premise=lambda: is_tree),
    ]
    return out


def build_410a_b(X):
    Amin = set(X.A())
    Mmax = set(X.M())
    De = X.Deven()
    return [R("410a/b: |H| <= |V-A| + |V-M| + |E(G[D_even])|",
              lambda: ("exact", len(X.H_union_maxcrit())),
              lambda: (X.n - len(Amin)) + (X.n - len(Mmax))
              + H.induced_edges(X.G, De))]


def build_412a_b_d_e_f(X):
    P = set(X.Ppend())
    NP = H.N_of(X.G, P)
    NNP = H.N_of(X.G, NP)
    A2 = X.D2set()
    NA2 = H.N_of(X.G, set(A2))

    def cL_np():
        return H.induced_largest_component_order(X.G, NP)

    def cL_a2():
        return H.induced_largest_component_order(X.G, A2)

    def d_NNP():
        return H.induced_max_degree(X.G, NNP)

    out = [
        R("412a: |H| >= c_L(G[N(P)])",
          lambda: ("lb", len(X.H_union_maxcrit())), lambda: cL_np()),
        R("412b: |H| >= c_L(G[A_2])",
          lambda: ("lb", len(X.H_union_maxcrit())), lambda: cL_a2()),
        R("412d: |H| >= gamma_t",
          lambda: ("lb", len(X.H_union_maxcrit())), lambda: X.gamma_t()),
        R("412e: |H| >= 1 + Delta(G[N(N(P))])",
          lambda: ("lb", len(X.H_union_maxcrit())), lambda: 1 + d_NNP()),
        R("412f: |H| >= mu(G[V-N(P)]) [KNOWN CORRUPT per README]",
          lambda: ("lb", len(X.H_union_maxcrit())),
          lambda: H.induced_mu(X.G, [v for v in X.G.nodes()
                                     if v not in NP])),
    ]
    return out


def build_413a_b(X):
    P = set(X.Ppend())
    NNP = H.N_of(X.G, H.N_of(X.G, P))
    A2 = set(X.D2set())
    NA2mA2 = H.N_of(X.G, A2) - A2

    def r_a():
        return X.kappa() * H.induced_alpha(
            X.G, [v for v in X.G.nodes() if v not in set(X.A())]) \
            + H.induced_mu(X.G, NNP)
    out = [R("413a: |H| >= kappa*alpha(G[V-A]) + mu(G[N(N(P))])",
             lambda: ("lb", len(X.H_union_maxcrit())), lambda: r_a())]

    def r_b():
        npend = len(X.Ppend())
        cl = H.induced_largest_component_order(X.G, list(NA2mA2))
        return X.kappa() * cl + npend
    out.append(R("413b: |H| >= kappa*c_L(G[N(A_2)]-A_2) + #pendants",
                 lambda: ("lb", len(X.H_union_maxcrit())), lambda: r_b()))
    return out


def build_415a_b_c(X):
    A2 = set(X.D2set())
    NA2 = H.N_of(X.G, A2)

    def a_term():
        epn = H.private_external_neighbors(X.G, A2)
        iso = H.induced_isolates(X.G, NA2)
        return (epn - 1) * iso
    # B_2 low-confidence reading: vertices of degree at most two? use H2
    B2lc = set(X.H2())

    def b_term():
        epn = H.private_external_neighbors(X.G, B2lc)
        iso = H.induced_isolates(X.G, B2lc)
        return (epn - 1) * iso
    return [
        R("415a: |H| >= (peN(A_2)-1)*isolates(<N(A_2)>)",
          lambda: ("lb", len(X.H_union_maxcrit())), lambda: a_term(),
          confidence="high"),
        R("415b: |H| >= (peN(B_2)-1)*isolates(B_2), B_2 := deg<=2 "
          "(low-confidence set identity)",
          lambda: ("lb", len(X.H_union_maxcrit())), lambda: b_term(),
          confidence="low"),
        R("415c: |H| >= (peN(B_2)-1)*isolates(B_2), same low-confidence",
          lambda: ("lb", len(X.H_union_maxcrit())), lambda: b_term(),
          confidence="low"),
    ]


def build_416(X):
    P = set(X.Ppend())
    NNP = H.N_of(X.G, H.N_of(X.G, P))
    return [R("416: |H| >= isolates(<N(N(P))>) - 2",
              lambda: ("lb", len(X.H_union_maxcrit())),
              lambda: H.induced_isolates(X.G, NNP) - 2)]


# ---------------------------------------------------------------- i entries

def build_418b_c(X):
    Amin = set(X.A())
    VmA = [v for v in X.G.nodes() if v not in Amin]
    NA = H.N_of(X.G, Amin)
    e_NA = H.induced_edges(X.G, NA)
    def _pcov():
        return X.p_cov()
    out = [R("418b: i <= alpha(G[V-A]) + |E(G[N(A)])|*p_cov",
             lambda: X.i_ub(),
             lambda: H.induced_alpha(X.G, VmA) + e_NA * _pcov())]
    def _icore_len():
        return len(Amin & set(X.A_core()))
    out.append(R("418c: i <= alpha(G[V-A]) + |E(G[N(A)])| + |A cap I_core|",
                 lambda: X.i_ub(),
                 lambda: H.induced_alpha(X.G, VmA) + e_NA +
                 _icore_len()))
    return out


def build_420b_c(X):
    Ssup = set(X.Supp())
    NS = H.N_of(X.G, Ssup)
    VmNS = [v for v in X.G.nodes() if v not in NS]
    NA = H.Nclosed_of(X.G, set(X.A()))

    def t_min():
        return X.T_min()
    out = [R("420b: i <= alpha(G[V-N(S_support)]) + 4(|E(G[N[A]]|-1)",
             lambda: X.i_ub(),
             lambda: H.induced_alpha(X.G, VmNS)
             + 4 * (H.induced_edges(X.G, NA) - 1)),
            R("420c: i <= alpha(G[V-N(S_support)]) + 4(|T_min|-1)",
              lambda: X.i_ub(),
              lambda: H.induced_alpha(X.G, VmNS) + 4 * (t_min() - 1))]
    return out


def build_421b_c(X):
    g = X.gamma_()
    nmaxe = X.N_edge("max")
    lamv = X.lambda_per_vertex()
    mn = min(lamv.values())
    Mlam = [v for v in lamv if lamv[v] == mn]
    NMlam = H.Nclosed_of(X.G, Mlam)
    out = [R("421b: i <= gamma*floor(0.5*max|N(e)| - 1)",
             lambda: X.i_ub(),
             lambda: g * ex_floor(Fraction(nmaxe, 2) - 1))]
    out.append(R("421c: i <= gamma*(|N[M_minlambda]| - 3)",
                 lambda: X.i_ub(), lambda: g * (len(NMlam) - 3)))
    return out


def build_422a_d(X):
    Mm = set(X.M())
    VmM = [v for v in X.G.nodes() if v not in Mm]
    Amin = set(X.A())
    VmA = [v for v in X.G.nodes() if v not in Amin]
    D2 = X.D2set()
    out = [R("422a: i <= alpha(G[V-M]) + 2*floor(E(G[M])/3)",
             lambda: X.i_ub(),
             lambda: H.induced_alpha(X.G, VmM)
             + 2 * ex_floor(Fraction(H.induced_edges(X.G, Mm), 3))),
           R("422b: i <= alpha(G[M]) + gamma(G[V-M])^2",
             lambda: X.i_ub(),
             lambda: H.induced_alpha(X.G, list(Mm))
             + H.induced_gamma(X.G, VmM) ** 2),
           R("422c: i <= alpha(G[A]) + 2*floor(Delta(G[V-A])/3)",
             lambda: X.i_ub(),
             lambda: H.induced_alpha(X.G, list(Amin))
             + 2 * ex_floor(Fraction(H.induced_max_degree(X.G, VmA), 3))),
           R("422d: i <= alpha(G[V-D2]) + floor((|E(G[D2])|+1)/3), D:=D2 "
             "(low-confidence set id)",
             lambda: X.i_ub(),
             lambda: H.induced_alpha(X.G, [v for v in X.G.nodes()
                                           if v not in set(D2)])
             + ex_floor(Fraction(H.induced_edges(X.G, D2) + 1, 3)),
             confidence="low")]
    return out


def build_423(X):
    Mm = set(X.M())
    Em = H.induced_edges(X.G, Mm)
    NAm = H.Nclosed_of(X.G, set(X.A()))
    VmA = [v for v in X.G.nodes() if v not in Mm]
    return [R("423: i <= |E(G[M])| + alpha(G[N[A]])*alpha(G[V-A])",
              lambda: X.i_ub(),
              lambda: Em + H.induced_alpha(X.G, NAm)
              * H.induced_alpha(X.G, VmA))]


def build_425d_e(X):
    P = set(X.Ppend())
    NP = H.N_of(X.G, P)
    VmNP = [v for v in X.G.nodes() if v not in NP]
    D2 = X.D2set()
    ksum = sum(X.c["K4_v"].values())
    return [R("425d: i <= T_min + sum K_4(v) + gamma(G[V-N(P)])",
              lambda: X.i_ub(),
              lambda: X.T_min() + ksum + H.induced_gamma(X.G, VmNP)),
            R("425e: i <= 4*T_min + |E(G[D2])| (D:=D2 low-conf)",
              lambda: X.i_ub(),
              lambda: 4 * X.T_min() + H.induced_edges(X.G, D2),
              confidence="low")]


def build_426(X):
    Mm = X.M()
    NM = H.N_of(X.G, Mm)
    import invlib as iv
    r = iv.gamma(X.G.subgraph(NM).copy(), 30.0)
    if not r["certified"]:
        raise Undef("gamma(G[N(M)]) bracketed")
    return [R("426: i <= n - gamma(G[N(M)])",
              lambda: X.i_ub(), lambda: X.n - r["value"])]


def build_427(X):
    Cc = set(X.Cset())

    def e_cross():
        c = 0
        for u, v in X.G.edges():
            if (u in Cc) != (v in Cc):
                c += 1
        return c

    def rhs():
        P = set(X.Ppend())
        NP = H.N_of(X.G, P)
        inside = [v for v in X.G.nodes() if v in NP]
        return e_cross() + ex_floor(Fraction(
            2 * H.induced_edges(X.G, inside), 3))
    return [R("427: i <= |E(C,V-C)| + floor[(2/3)|E(G[V-N(P)])|]",
              lambda: X.i_ub(), lambda: rhs())]


def build_430a_c(X):
    out = []
    lam_max = X.lambda_stats()["max"]

    def r430c():
        r2g = X.residue()  # residue(G^2)=residue of square degree seq?
        sq = H.square_graph(X.G)
        seq = sorted((d for _, d in sq.degree()), reverse=True)
        rr = iv_residue_seq(seq)
        dm = max(dict(X.G.degree())[v] for v in X.M())
        return lam_max * rr + dm
    out.append(R("430c: i <= lambda_max*residue(G^2) + Delta(G[M])",
                 lambda: X.i_ub(), lambda: r430c()))
    return out


def iv_residue_seq(seq_desc):
    seq = sorted(seq_desc, reverse=True)
    while seq and seq[0] > 0:
        d = seq.pop(0)
        for i in range(min(d, len(seq))):
            seq[i] -= 1
        seq = sorted(seq, reverse=True)
    return len(seq)


def build_431a_b_c(X):
    res = X.residue()
    Dom = set(H.neighbor_dominators(X.G))
    ND = H.N_of(X.G, Dom)
    tv = X.c["T_v"]
    tmin = X.T_min()
    tmax = X.T_max()
    ddv = X.dd
    out = [R("431a: residue + peN(N(D_dominators)) + T_min "
             "(D:=neighbor dominators, low-conf)",
             lambda: X.i_ub(),
             lambda: res + H.private_external_neighbors(X.G, ND) + tmin,
             confidence="low"),
           R("431b: residue + gamma(G[N[A]])*peN(N(D)) + dp_pairs_at_diam "
             "(dp alt: pairs at distance 2 on periphery)",
             lambda: X.i_ub(),
             lambda: res + H.induced_gamma(X.G, H.Nclosed_of(X.G, ND))
             * H.private_external_neighbors(X.G, ND) + X.dp_pairs()),
           R("431c: residue*T_max + dd",
             lambda: X.i_ub(), lambda: res * tmax + ddv)]
    return out


def build_432a_b(X):
    ann = X.annihilation()
    mn = min(X.c["dist_even"][v] - X.c["dist_odd"][v] for v in X.G.nodes())
    P = set(X.Ppend())
    NP = H.N_of(X.G, P)
    outside = [v for v in X.G.nodes() if v not in NP]
    return [R("432a: annihilation + min(dist_even - dist_odd)",
              lambda: X.i_ub(), lambda: ann + mn),
            R("432b: |V-N(P)| + min(diff)*chi_bipartite",
              lambda: X.i_ub(),
              lambda: len(outside) + mn * X.bipartite_char())]


def build_433(X):
    NM = H.N_of(X.G, set(X.M()))
    G2 = X.G2
    s = sum(Fraction(1, d) for _, d in G2.degree() if d > 0)
    return [R("433: i <= 0.5*|N(M)|*floor(2*sum(1/deg of G^2))",
              lambda: X.i_ub(),
              lambda: Fraction(len(NM), 2) * ex_floor(2 * s))]


def build_434a_e(X):
    sw = X.SW_comp()
    Mm = X.M()
    Bp = X.Bset()
    NBc = H.Nclosed_of(X.G, Bp)
    eccC52 = H.ecc_set(X.G, X.Cset())
    delta_M = H.induced_min_degree(X.G, Mm)
    VmM = [v for v in X.G.nodes() if v not in set(Mm)]
    delta_VmM = H.induced_min_degree(X.G, VmM)
    out = [
        R("434a: i <= |M| + 2*floor(0.5*SW(comp))",
          lambda: X.i_ub(), lambda: len(Mm) + 2 * ex_floor(Fraction(sw, 2))),
        R("434b: i <= delta(G[M]) + 1 + SW(comp)  (diam>2 clause unused; "
          "all arsenal diam<=2 except noted)",
          lambda: X.i_ub(), lambda: delta_M + 1 + sw),
        R("434c: i <= delta(G[V-M]) + 1 + SW(comp)",
          lambda: X.i_ub(), lambda: delta_VmM + 1 + sw),
        R("434d: i <= SW(comp) - components(G[N[B]]) + 2",
          lambda: X.i_ub(),
          lambda: sw - nx.number_connected_components(
              X.G.subgraph(NBc)) + 2),
        R("434e: i <= SW(comp) - ecc_def52(C) + 2",
          lambda: X.i_ub(), lambda: sw - eccC52 + 2),
        R("434e-alt member: SW(comp) - radius + 2",
          lambda: X.i_ub(), lambda: sw - X.rad + 2),
    ]
    return out


def build_435(X):
    sw = X.SW_comp()
    G2 = X.G2
    dg2 = dict(G2.degree())
    mn = min(dg2.values())
    Ag2 = [v for v in dg2 if dg2[v] == mn]
    e_in = H.induced_edges(G2, Ag2)
    return [R("435: alpha_2 <= SW(bar) + ceil[(1+E((G^2)[A_{G^2}]))/3]",
              lambda: ("ub", X._incumbent("alpha_2")),
              lambda: sw + ex_ceil(Fraction(1 + e_in, 3)))]


def build_436c(X):
    wp = X.WP_bar()
    Dom = set(H.neighbor_dominators(X.G))
    dd = H.induced_max_degree(X.G, Dom)
    return [R("436c: alpha_2 <= HH_k*WP(bar) + Delta(G[D_dominators])",
              lambda: ("ub", X._incumbent("alpha_2")),
              lambda: X.HH_k() * wp + dd)]


def build_438a_b(X):
    Amin = X.A()
    H2 = X.H2()

    def a_ind(Ssub):
        sub = X.G.subgraph(Ssub)
        return iv_ann(sub)

    out = [R("438a: alpha_2 <= a(G) + a(G[V-A]) + |E(G[A])|",
             lambda: ("ub", X._incumbent("alpha_2")),
             lambda: X.annihilation()
             + a_ind([v for v in X.G.nodes() if v not in set(Amin)])
             + H.induced_edges(X.G, set(Amin)))]
    out.append(R("438b: alpha_2 <= a(G) + a(G[V-H_2]) + |E(G[H_2])| "
                 "[proved upstream #4916]",
                lambda: ("ub", X._incumbent("alpha_2")),
                lambda: X.annihilation()
                + a_ind([v for v in X.G.nodes() if v not in set(H2)])
                + H.induced_edges(X.G, set(H2))))
    return out


def iv_ann(Gsub):
    ds = sorted(d for _, d in Gsub.degree())
    m = Gsub.number_of_edges()
    s = k = 0
    for d in ds:
        if s + d <= m:
            s += d
            k += 1
        else:
            break
    return k


def build_439(X):
    NM = len(H.N_of(X.G, set(X.M())))
    cw = X.CW()

    def rhs():
        from xctx import ex_floor as ef
        return NM + ef(2 * (cw - 1))
    return [R("439: alpha_2 <= |N(M)| + floor[2(CW-1)]",
              lambda: ("ub", X._incumbent("alpha_2")), lambda: rhs())]


def build_442(X):
    H3 = X.H3()

    def rhs():
        pth = H_ind_path(X.G.subgraph(H3))
        from xctx import ex_ceil as ec
        return X.n - ec(Fraction(pth, 2))
    return [R("442: alpha_2 <= n - ceil[path(G[H_3])/2]",
              lambda: ("ub", X._incumbent("alpha_2")), lambda: rhs())]


def H_ind_path(Gsub):
    import invlib as iv
    v, proved = iv.largest_induced_path(Gsub, 20.0)
    return v


def build_443(X):
    disp_sum = sum(X.c["disp"].values())
    Nac = len(H.N_of(X.G, set(X.A_core())))
    return [R("443: alpha_2 <= sum(disparities) - |N(A_core)| - 2",
              lambda: ("ub", X._incumbent("alpha_2")),
              lambda: disp_sum - Nac - 2)]


def build_444(X):
    dd_k = X.dd_K4seq()
    from xctx import ex_floor as ef
    return [R("444: alpha_2 <= n - floor[dd(K4(v) sequence)/2]",
              lambda: ("ub", X._incumbent("alpha_2")),
              lambda: X.n - ef(Fraction(dd_k, 2)))]


def build_446(X):
    NA = H.N_of(X.G, set(X.A()))
    radNA = None

    def rho_read():
        r = H.induced_radius(X.G, NA)
        if r is None:
            raise Undef("N(A) induced disconnected: radius undefined")
        return r

    def p_read():
        import invlib as iv
        sub = X.G.subgraph(NA)
        r = iv.ham_path_search(sub, restarts=60, backtrack_budget=30000)
        return 1 if r == 1 else Undef("path cover >1 or unknown")
    Ss = X.Supp()
    return [R("446: alpha_2 <= rho(<N(A)> radius reading) + |V-S_support|",
              lambda: ("ub", X._incumbent("alpha_2")),
              lambda: rho_read() + (X.n - len(Ss)), confidence="low")]


def build_448a_b(X):
    Hn2 = [v for v in X.G.nodes() if X.G.degree(v) > X.n / 2]
    e_rest = H.induced_edges(X.G, [v for v in X.G.nodes()
                                   if v not in set(Hn2)])
    Amin = set(X.A())
    Ssup = set(X.Supp())
    NSs = H.N_of(X.G, Ssup)
    out = [R("448a: alpha_2 <= |H_{n/2}| + |E(G[V-H_{n/2}])| + radius",
             lambda: ("ub", X._incumbent("alpha_2")),
             lambda: len(Hn2) + e_rest + X.rad)]
    out.append(R("448a-alt: ... + residue",
                 lambda: ("ub", X._incumbent("alpha_2")),
                 lambda: len(Hn2) + e_rest + X.residue()))
    out.append(R("448b: alpha_2 <= |V-A| + |E(G[N(S_support)])| + radius "
                 "[KNOWN CORRUPT per README]",
                 lambda: ("ub", X._incumbent("alpha_2")),
                 lambda: (X.n - len(Amin)) + H.induced_edges(X.G, NSs)
                 + X.rad))
    return out


def build_449_450(X):
    H3 = set(X.H3())
    e_H3 = H.induced_edges(X.G, H3)
    A2 = set(X.D2set())
    NA2 = H.N_of(X.G, A2)
    Ss = X.Supp()
    Vh3 = [v for v in X.G.nodes() if v not in H3]
    out = [R("449: alpha_2 <= |V\\H_3| + ceil[(|E(G[H_3])|-1)/2]",
             lambda: ("ub", X._incumbent("alpha_2")),
             lambda: len(Vh3) + ex_ceil(Fraction(e_H3 - 1, 2)))]

    def rho1():
        r = H.induced_radius(X.G, NA2)
        if r is None:
            raise Undef("<N(A_2)> disconnected")
        return r
    VH3 = [v for v in X.G.nodes() if v not in H3]
    NH3 = H.N_of(X.G, VH3)

    def rho2():
        r = H.induced_radius(X.G, NH3)
        if r is None:
            raise Undef("<N(V-H_3)> disconnected")
        return r
    out.append(R("450: alpha_2 <= rho(<N(A_2)>) + |V\\S_support| + "
                 "rho(<N(V\\H_3)>) [rho:=radius readings, low-conf]",
                 lambda: ("ub", X._incumbent("alpha_2")),
                 lambda: rho1() + (X.n - len(Ss)) + rho2(),
                 confidence="low"))
    return out
