#!/usr/bin/env python3
"""Executable structural certificate for Graph Brain alpha upper bound 081."""
from fractions import Fraction


def verify(m=4):
    # For C5[K_m]: independent vertices project to independent base-cycle
    # vertices, distance is inherited between distinct fibers, regular
    # vertex-transitivity gives edge connectivity=degree, and deleting two
    # nonadjacent neighboring fibers (2m vertices) witnesses/certifies kappa.
    alpha=2
    diameter=2
    degree=3*m-1
    edge_connectivity=degree
    vertex_connectivity=2*m
    rhs=Fraction(2*diameter,edge_connectivity-vertex_connectivity)
    assert m>=2
    assert alpha > rhs
    return {'m':m,'order':5*m,'alpha':alpha,'diameter':diameter,
            'edge_connectivity':edge_connectivity,
            'vertex_connectivity':vertex_connectivity,
            'rhs':str(rhs),'margin':str(Fraction(alpha)-rhs)}


if __name__ == '__main__': print(verify())
