"""Graffiti-style expression templates, their exact evaluator, and their renderer.

An emitted conjecture is a *relation* over the invariant vocabulary:

    {"rel": "<=" | ">=", "lhs": <expr>, "rhs": <expr>}

with `<expr>` drawn from this grammar (all nodes are plain JSON dicts, so the
population file is self-describing and every arm can evaluate a target
mechanically without parsing English):

    {"inv": name}                            an invariant
    {"const": c}                             an integer constant
    {"op": "add",        "args": [a, b, ..]}
    {"op": "sub",        "args": [a, b]}
    {"op": "mul",        "c": k, "arg": a}   k * a, k a small integer
    {"op": "ceil_div",   "arg": a, "d": k}   ceil(a / k), k a small integer
    {"op": "floor_div",  "arg": a, "d": k}   floor(a / k)
    {"op": "ceil_ratio", "num": a, "den": b} ceil(a / b), b an invariant expr
    {"op": "floor_ratio","num": a, "den": b} floor(a / b)

`evaluate` uses `fractions.Fraction` throughout: exact, never floating point.
`ceil_ratio`/`floor_ratio` are only ever built over denominators that are
provably `>= 1` on every connected graph with `n >= 2` (`POSITIVE_DENOMINATORS`),
so no emitted statement can be undefined anywhere in its own universe of
quantification.

The templates are the shapes Graffiti and its descendants actually emit: small
integer coefficients, sums and differences of two invariants, and — the point of
the exercise — ceilings and floors of halves, thirds and ratios, which is where
the discretisation lives.
"""
from __future__ import annotations

import math
from fractions import Fraction
from typing import Dict, List, Tuple

import numpy as np

from invariants import DISPLAY

# Invariants provably >= 1 for every connected graph on n >= 2 vertices, hence
# admissible as a denominator.  Excluded: f1, cutv, tri and every 0/1
# characteristic function, each of which vanishes on some connected graph.
POSITIVE_DENOMINATORS = frozenset([
    "n", "m", "Delta", "delta", "sigma2", "Sigma2", "dd",
    "res", "annih", "SW", "diam", "rad", "girth",
    "dist_even_min", "dist_even_max", "Tdist_min", "Tdist_max",
    "kappa", "disp_max", "disp_min", "spec_floor", "spec_ceil",
    "alpha", "omega", "chi", "mu", "lam_max", "lam_min",
    "gamma", "gamma_t", "gamma_2", "gamma_i", "f", "b",
    "deg_avg", "ecc_avg", "dist_avg", "CW", "lam_avg", "disp_avg",
])


# --------------------------------------------------------------------------
# exact evaluation (Fraction arithmetic)
# --------------------------------------------------------------------------
def evaluate(expr, vals: Dict[str, object]) -> Fraction:
    if "inv" in expr:
        return Fraction(vals[expr["inv"]])
    if "const" in expr:
        return Fraction(expr["const"])
    op = expr["op"]
    if op == "add":
        return sum((evaluate(a, vals) for a in expr["args"]), Fraction(0))
    if op == "sub":
        a, b = expr["args"]
        return evaluate(a, vals) - evaluate(b, vals)
    if op == "mul":
        return Fraction(expr["c"]) * evaluate(expr["arg"], vals)
    if op == "ceil_div":
        return Fraction(math.ceil(evaluate(expr["arg"], vals) / Fraction(expr["d"])))
    if op == "floor_div":
        return Fraction(math.floor(evaluate(expr["arg"], vals) / Fraction(expr["d"])))
    if op == "ceil_ratio":
        den = evaluate(expr["den"], vals)
        if den <= 0:
            raise ZeroDivisionError("non-positive denominator")
        return Fraction(math.ceil(evaluate(expr["num"], vals) / den))
    if op == "floor_ratio":
        den = evaluate(expr["den"], vals)
        if den <= 0:
            raise ZeroDivisionError("non-positive denominator")
        return Fraction(math.floor(evaluate(expr["num"], vals) / den))
    raise ValueError(op)


def check(relation, vals: Dict[str, object]) -> bool:
    """True iff the relation holds on the invariant values `vals`."""
    lhs = evaluate(relation["lhs"], vals)
    rhs = evaluate(relation["rhs"], vals)
    return lhs <= rhs if relation["rel"] == "<=" else lhs >= rhs


def slack(relation, vals: Dict[str, object]) -> Fraction:
    """Non-negative iff the relation holds; 0 exactly at tightness."""
    lhs = evaluate(relation["lhs"], vals)
    rhs = evaluate(relation["rhs"], vals)
    return rhs - lhs if relation["rel"] == "<=" else lhs - rhs


def invariants_of(expr, acc=None):
    acc = set() if acc is None else acc
    if "inv" in expr:
        acc.add(expr["inv"])
    elif "const" in expr:
        pass
    else:
        for key in ("args",):
            for a in expr.get(key, []):
                invariants_of(a, acc)
        for key in ("arg", "num", "den"):
            if key in expr:
                invariants_of(expr[key], acc)
    return acc


# --------------------------------------------------------------------------
# rendering
# --------------------------------------------------------------------------
def render(expr) -> str:
    if "inv" in expr:
        return DISPLAY[expr["inv"]]
    if "const" in expr:
        return str(expr["const"])
    op = expr["op"]
    if op == "add":
        parts = []
        for a in expr["args"]:
            s = render(a)
            if s.startswith("-"):
                parts.append(s)
            else:
                parts.append("+ " + s if parts else s)
        return " ".join(parts)
    if op == "sub":
        a, b = expr["args"]
        return "%s - %s" % (render(a), _paren(b))
    if op == "mul":
        return "%d*%s" % (expr["c"], _paren(expr["arg"]))
    if op == "ceil_div":
        return "ceil((%s)/%d)" % (render(expr["arg"]), expr["d"])
    if op == "floor_div":
        return "floor((%s)/%d)" % (render(expr["arg"]), expr["d"])
    if op == "ceil_ratio":
        return "ceil((%s)/(%s))" % (render(expr["num"]), render(expr["den"]))
    if op == "floor_ratio":
        return "floor((%s)/(%s))" % (render(expr["num"]), render(expr["den"]))
    raise ValueError(op)


def _paren(expr) -> str:
    s = render(expr)
    if "inv" in expr or "const" in expr or expr.get("op", "").startswith(("ceil", "floor")):
        return s
    return "(%s)" % s


def render_relation(relation) -> str:
    return "%s %s %s" % (render(relation["lhs"]), relation["rel"], render(relation["rhs"]))


# --------------------------------------------------------------------------
# scaled-integer template enumeration (generation-time fast path)
# --------------------------------------------------------------------------
# Every invariant on a graph with n <= 8 has a denominator dividing
# SCALE = lcm(1..8) * (something dividing it); see generate.py, which asserts it.
SCALE = 840


def _cd(a: np.ndarray, d: int) -> np.ndarray:
    """ceil(a/d) in SCALE units, for `a` in SCALE units."""
    q = SCALE * d
    return SCALE * (-((-a) // q))


def _fd(a: np.ndarray, d: int) -> np.ndarray:
    q = SCALE * d
    return SCALE * (a // q)


def _cr(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """ceil(a/b) in SCALE units; scales cancel.  Requires b > 0."""
    return SCALE * (-((-a) // b))


def _fr(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return SCALE * (a // b)


def _K(c: int) -> int:
    return c * SCALE


def _plus(ast, c: int):
    if c == 0:
        return ast
    if c > 0:
        return {"op": "add", "args": [ast, {"const": c}]}
    return {"op": "sub", "args": [ast, {"const": -c}]}


# Each template is (tid, np_fn, ast_fn).  `np_fn` takes SCALE-unit int64 arrays
# and returns one; `ast_fn` takes the operand ASTs and returns the JSON AST.
# The tables are built once at import time, so the generation sweep allocates no
# closures and no dicts per candidate: ASTs are materialised only for survivors.

UNARY = []
for _c in (-3, -2, -1, 0, 1, 2, 3):
    UNARY.append(("x%+d" % _c,
                  (lambda c: lambda X: X + _K(c))(_c),
                  (lambda c: lambda X: _plus(X, c))(_c)))
for _k in (2, 3):
    for _c in (-2, -1, 0, 1):
        UNARY.append(("%dx%+d" % (_k, _c),
                      (lambda k, c: lambda X: k * X + _K(c))(_k, _c),
                      (lambda k, c: lambda X: _plus({"op": "mul", "c": k, "arg": X}, c))(_k, _c)))
for _d in (2, 3):
    for _c in (-1, 0, 1, 2):
        UNARY.append(("ceil(x/%d)%+d" % (_d, _c),
                      (lambda d, c: lambda X: _cd(X, d) + _K(c))(_d, _c),
                      (lambda d, c: lambda X: _plus({"op": "ceil_div", "arg": X, "d": d}, c))(_d, _c)))
        UNARY.append(("floor(x/%d)%+d" % (_d, _c),
                      (lambda d, c: lambda X: _fd(X, d) + _K(c))(_d, _c),
                      (lambda d, c: lambda X: _plus({"op": "floor_div", "arg": X, "d": d}, c))(_d, _c)))

BINARY_SYM = []
for _c in (-2, -1, 0):
    BINARY_SYM.append(("x+y%+d" % _c,
                       (lambda c: lambda X, Y: X + Y + _K(c))(_c),
                       (lambda c: lambda X, Y: _plus({"op": "add", "args": [X, Y]}, c))(_c)))
for _c in (0, 1):
    BINARY_SYM.append(("ceil((x+y)/2)%+d" % _c,
                       (lambda c: lambda X, Y: _cd(X + Y, 2) + _K(c))(_c),
                       (lambda c: lambda X, Y: _plus(
                           {"op": "ceil_div", "arg": {"op": "add", "args": [X, Y]}, "d": 2}, c))(_c)))
    BINARY_SYM.append(("floor((x+y)/2)%+d" % _c,
                       (lambda c: lambda X, Y: _fd(X + Y, 2) + _K(c))(_c),
                       (lambda c: lambda X, Y: _plus(
                           {"op": "floor_div", "arg": {"op": "add", "args": [X, Y]}, "d": 2}, c))(_c)))

# (tid, np_fn, ast_fn, requires_positive_denominator)
BINARY_ASYM = []
for _c in (0, 1, 2):
    BINARY_ASYM.append(("x-y%+d" % _c,
                        (lambda c: lambda X, Y: X - Y + _K(c))(_c),
                        (lambda c: lambda X, Y: _plus({"op": "sub", "args": [X, Y]}, c))(_c), False))
for _c in (0, 1):
    BINARY_ASYM.append(("ceil((x-y)/2)%+d" % _c,
                        (lambda c: lambda X, Y: _cd(X - Y, 2) + _K(c))(_c),
                        (lambda c: lambda X, Y: _plus(
                            {"op": "ceil_div", "arg": {"op": "sub", "args": [X, Y]}, "d": 2}, c))(_c), False))
    BINARY_ASYM.append(("floor((x-y)/2)%+d" % _c,
                        (lambda c: lambda X, Y: _fd(X - Y, 2) + _K(c))(_c),
                        (lambda c: lambda X, Y: _plus(
                            {"op": "floor_div", "arg": {"op": "sub", "args": [X, Y]}, "d": 2}, c))(_c), False))
    BINARY_ASYM.append(("2x-y%+d" % _c,
                        (lambda c: lambda X, Y: 2 * X - Y + _K(c))(_c),
                        (lambda c: lambda X, Y: _plus(
                            {"op": "sub", "args": [{"op": "mul", "c": 2, "arg": X}, Y]}, c))(_c), False))
BINARY_ASYM.append(("ceil(x/2)+y",
                    lambda X, Y: _cd(X, 2) + Y,
                    lambda X, Y: {"op": "add", "args": [{"op": "ceil_div", "arg": X, "d": 2}, Y]}, False))
BINARY_ASYM.append(("floor(x/2)+y",
                    lambda X, Y: _fd(X, 2) + Y,
                    lambda X, Y: {"op": "add", "args": [{"op": "floor_div", "arg": X, "d": 2}, Y]}, False))
BINARY_ASYM.append(("ceil(x/y)",
                    lambda X, Y: _cr(X, Y),
                    lambda X, Y: {"op": "ceil_ratio", "num": X, "den": Y}, True))
BINARY_ASYM.append(("floor(x/y)",
                    lambda X, Y: _fr(X, Y),
                    lambda X, Y: {"op": "floor_ratio", "num": X, "den": Y}, True))

TEMPLATE_COUNTS = {
    "unary": len(UNARY),
    "binary_symmetric": len(BINARY_SYM),
    "binary_asymmetric": len(BINARY_ASYM),
    "binary_asymmetric_ratio_only": sum(1 for t in BINARY_ASYM if t[3]),
}


# tid -> (arity, np_fn, ast_fn); lets the driver rebuild any right-hand side from
# its (template id, operands) descriptor without keeping arrays alive.
BY_TID = {}
for _t, _f, _a in UNARY:
    BY_TID[_t] = (1, _f, _a)
for _t, _f, _a in BINARY_SYM:
    BY_TID[_t] = (2, _f, _a)
for _t, _f, _a, _p in BINARY_ASYM:
    BY_TID[_t] = (2, _f, _a)
assert len(BY_TID) == len(UNARY) + len(BINARY_SYM) + len(BINARY_ASYM), "template id collision"
