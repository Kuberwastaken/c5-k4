#!/usr/bin/env python3
"""Erdos 274 / herzog_schonheim, upstream 274.lean.

  theorem herzog_schonheim {G} [Group G] (hG : 1 < ENat.card G) {i} [Fintype i]
      (hi : 1 < Fintype.card i) (P : Group.ExactCovering G i) :
      exists i j, i != j /\ (P.parts i).index = (P.parts j).index

Negation certificate for the finite case = one finite group G with an exact
partition of G into k > 1 cosets g_i H_i whose indices [G:H_i] are pairwise
distinct.  That is a finite, replayable object, so the triage label is right.

This script does the bounded finite search over a declared family of groups,
using permutation representations and full subgroup enumeration.
"""
import sys
import time
from itertools import permutations
from fractions import Fraction


# ---------- group plumbing ----------
def perm_group(gens, deg):
    """Closure of a set of permutations (tuples) under composition."""
    ident = tuple(range(deg))
    elts = {ident}
    frontier = [ident]
    while frontier:
        a = frontier.pop()
        for g in gens:
            b = tuple(g[a[i]] for i in range(deg))
            if b not in elts:
                elts.add(b)
                frontier.append(b)
    return sorted(elts)


def table(elts, deg):
    idx = {e: i for i, e in enumerate(elts)}
    m = len(elts)
    mul = [[0] * m for _ in range(m)]
    for i, a in enumerate(elts):
        for j, b in enumerate(elts):
            mul[i][j] = idx[tuple(a[b[k]] for k in range(deg))]
    ident = idx[tuple(range(deg))]
    return mul, ident


def subgroups(mul, ident):
    """All subgroups, as frozensets of element indices."""
    m = len(mul)
    def gen(seed):
        S = {ident} | set(seed)
        ch = True
        while ch:
            ch = False
            cur = list(S)
            for a in cur:
                for b in cur:
                    c = mul[a][b]
                    if c not in S:
                        S.add(c)
                        ch = True
        return frozenset(S)
    subs = {frozenset({ident})}
    frontier = [frozenset({ident})]
    while frontier:
        H = frontier.pop()
        for g in range(m):
            if g in H:
                continue
            K = gen(set(H) | {g})
            if K not in subs:
                subs.add(K)
                frontier.append(K)
    return sorted(subs, key=len)


def cosets(mul, H, m):
    seen = set()
    out = []
    for g in range(m):
        c = frozenset(mul[g][h] for h in H)
        if c not in seen:
            seen.add(c)
            out.append(c)
    return out


# ---------- the search ----------
def index_sets(divs, m):
    """All subsets S of `divs` (possible indices), |S| >= 2, pairwise distinct,
    with sum 1/n = 1.  Cosets of index n have size m/n."""
    res = []
    ds = sorted(divs)
    def rec(i, cur, tot):
        if tot == 1 and len(cur) >= 2:
            res.append(list(cur))
            return
        if tot > 1 or i == len(ds):
            return
        # optimistic bound: remaining largest possible additions
        rem = sum(Fraction(1, d) for d in ds[i:])
        if tot + rem < 1:
            return
        for j in range(i, len(ds)):
            rec(j + 1, cur + [ds[j]], tot + Fraction(1, ds[j]))
    rec(0, [], Fraction(0))
    return res


def hs_search(mul, ident, name, deadline):
    m = len(mul)
    subs = subgroups(mul, ident)
    by_index = {}
    for H in subs:
        idx = m // len(H)
        if idx == 1:
            continue
        by_index.setdefault(idx, []).extend(cosets(mul, H, m))
    hits = []
    for iset in index_sets(set(by_index), m):
        # DFS: cover the least uncovered element
        order = sorted(iset)          # small index = big coset first
        def rec(covered, remaining, chosen):
            if time.time() > deadline:
                raise TimeoutError
            if not remaining:
                return len(covered) == m
            e = next(x for x in range(m) if x not in covered)
            for n in list(remaining):
                for c in by_index[n]:
                    if e in c and not (c & covered):
                        if rec(covered | c, remaining - {n}, chosen + [(n, c)]):
                            hits.append(list(chosen + [(n, c)]))
                            return True
            return False
        if rec(frozenset(), set(iset), []):
            return dict(group=name, order=m, subgroups=len(subs),
                        COUNTEREXAMPLE=hits[-1])
    return dict(group=name, order=m, subgroups=len(subs),
                index_sets=len(index_sets(set(by_index), m)), ok=True)


def cyclic(n):
    return [tuple((i + 1) % n for i in range(n))], n


def dihedral(n):
    r = tuple((i + 1) % n for i in range(n))
    s = tuple((-i) % n for i in range(n))
    return [r, s], n


def sym(n):
    g1 = tuple([1, 0] + list(range(2, n)))
    g2 = tuple(list(range(1, n)) + [0])
    return [g1, g2], n


def main(budget):
    t0 = time.time()
    deadline = t0 + budget
    out = []
    fam = []
    # all subgroups of S5 (as abstract groups) -- covers C1..C6, C2^2, S3, D4,
    # D5, D6, A4, S4, F20, A5, ...
    elts5 = perm_group(sym(5)[0], 5)
    mul5, id5 = table(elts5, 5)
    subs5 = subgroups(mul5, id5)
    seen_orders = {}
    for H in subs5:
        if len(H) < 6:
            continue
        key = (len(H), tuple(sorted(len(frozenset(mul5[g][h] for h in H))
                                    for g in [0])))
        lst = sorted(H)
        pos = {e: i for i, e in enumerate(lst)}
        sub_mul = [[pos[mul5[a][b]] for b in lst] for a in lst]
        sub_id = pos[id5]
        fam.append((f"S5-subgroup(order {len(H)}) #{len(fam)}", sub_mul, sub_id))
    # cyclic and dihedral up to order 60
    for n in range(6, 61, 6):
        e = perm_group(*cyclic(n)); mu, i0 = table(e, n)
        fam.append((f"C{n}", mu, i0))
    for n in range(3, 31):
        if (2 * n) % 6:
            continue
        e = perm_group(dihedral(n)[0], n); mu, i0 = table(e, n)
        fam.append((f"D{n} (order {2*n})", mu, i0))
    for name, mu, i0 in fam:
        if time.time() > deadline:
            out.append(dict(status="TIMEOUT", after=name))
            break
        try:
            out.append(hs_search(mu, i0, name, deadline))
        except TimeoutError:
            out.append(dict(status="TIMEOUT", during=name))
            break
    return out, round(time.time() - t0, 1)


if __name__ == "__main__":
    res, secs = main(float(sys.argv[1]))
    bad = [r for r in res if "COUNTEREXAMPLE" in r]
    tested = [r for r in res if r.get("ok")]
    print("secs", secs, "groups tested", len(tested),
          "orders", sorted({r["order"] for r in tested}))
    print("total distinct-index index-sets explored",
          sum(r.get("index_sets", 0) for r in tested))
    print("COUNTEREXAMPLES:", bad)
    for r in res:
        if "status" in r:
            print(r)
