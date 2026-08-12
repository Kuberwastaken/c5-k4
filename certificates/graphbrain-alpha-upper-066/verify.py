#!/usr/bin/env python3
"""Executable certificate for Graph Brain alpha upper bound 066."""
import itertools
import math


def graph(m=10):
    vertices = tuple(range(5*m))
    def fiber(v): return v // m
    edges = tuple((u,v) for u,v in itertools.combinations(vertices,2)
                  if fiber(u)==fiber(v) or (fiber(u)-fiber(v))%5 in (1,4))
    return vertices, edges


def verify(m=10):
    V,E=graph(m); adjacency={v:set() for v in V}
    for u,v in E: adjacency[u].add(v); adjacency[v].add(u)
    alpha=2  # independent vertices use nonadjacent fibers; three fibers cannot be pairwise nonadjacent in C5
    degrees={len(adjacency[v]) for v in V}
    sigma2=min(len(adjacency[u])+len(adjacency[v]) for u,v in itertools.combinations(V,2) if v not in adjacency[u])
    adjacent=len(E); pairs=len(V)*(len(V)-1)//2; distance_two=pairs-adjacent
    average_distance=(adjacent+2*distance_two)/pairs
    rhs=math.exp(math.cosh(average_distance))-math.tan(sigma2)
    assert len(V)==50 and adjacent==725 and degrees=={29}
    assert sigma2==58 and average_distance==69/49
    assert alpha > rhs + 1e-6
    return {'order':len(V),'size':adjacent,'alpha':alpha,'sigma_2':sigma2,
            'average_distance':average_distance,'rhs':rhs,'margin':alpha-rhs}


if __name__ == '__main__': print(verify())
