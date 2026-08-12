#!/usr/bin/env python3
"""Executable structural certificate for Graph Brain alpha upper bound 081."""
from fractions import Fraction
import json
from pathlib import Path

import networkx as nx


def verify(m=4):
    # For C5[K_m]: independent vertices project to independent base-cycle
    # vertices, distance is inherited between distinct fibers, regular
    # vertex-transitivity gives edge connectivity=degree; deleting the two
    # fibers neighboring one surviving fiber (2m vertices) witnesses kappa.
    alpha=2
    diameter=2
    degree=3*m-1
    edge_connectivity=degree
    vertex_connectivity=2*m
    rhs=Fraction(2*diameter,edge_connectivity-vertex_connectivity)
    assert m>=4
    assert alpha > rhs
    return {'m':m,'order':5*m,'alpha':alpha,'diameter':diameter,
            'edge_connectivity':edge_connectivity,
            'vertex_connectivity':vertex_connectivity,
            'rhs':str(rhs),'margin':str(Fraction(alpha)-rhs)}


def simple_witness():
    # Two K5s sharing one cut vertex: n=9, alpha=2, diameter=2, lambda=4,
    # kappa=1, so the same exact RHS is 4/3.
    rhs=Fraction(4,3)
    return {'graph':'two K5s sharing a cut vertex','graph6':'H~}CKMF','order':9,
            'alpha':2,'diameter':2,'edge_connectivity':4,
            'vertex_connectivity':1,'rhs':str(rhs),'margin':str(Fraction(2)-rhs)}


def windmill(s=5,t=2):
    """W_{s,t}: t copies of K_s sharing exactly one hub."""
    assert s>=4 and t>=2 and Fraction(t)>Fraction(4,s-2)
    alpha=t; diameter=2; edge_connectivity=s-1; vertex_connectivity=1
    rhs=Fraction(4,s-2)
    assert alpha>rhs
    return {'s':s,'t':t,'order':1+t*(s-1),'alpha':alpha,'diameter':diameter,
            'edge_connectivity':edge_connectivity,'vertex_connectivity':vertex_connectivity,
            'rhs':str(rhs),'margin':str(Fraction(alpha)-rhs)}


def independence_number(g):
    return max(map(len, nx.find_cliques(nx.complement(g))))


def violates(g):
    edge_connectivity = nx.edge_connectivity(g)
    vertex_connectivity = nx.node_connectivity(g)
    denominator = edge_connectivity - vertex_connectivity
    if denominator == 0:
        return False  # The author evaluator returns +Infinity here.
    rhs = Fraction(2 * nx.diameter(g), denominator)
    return Fraction(independence_number(g)) > rhs


def named_gate():
    graphs = [nx.cycle_graph(n) for n in range(5, 10)]
    graphs += [nx.path_graph(7), nx.petersen_graph(),
               nx.complete_bipartite_graph(3, 3), nx.complete_graph(7)]
    graphs += [nx.star_graph(n) for n in range(3, 9)]
    graphs += [nx.complete_bipartite_graph(2, n) for n in range(2, 8)]
    graphs += [nx.cubical_graph(), nx.heawood_graph()]
    return graphs


def database_gate():
    atlas = [g for g in nx.graph_atlas_g() if len(g) > 1 and nx.is_connected(g)]
    assert len(atlas) == 995
    positive = [
        g for g in atlas if nx.edge_connectivity(g) > nx.node_connectivity(g)
    ]
    violations = sum(violates(g) for g in atlas)
    named = named_gate()
    named_violations = sum(violates(g) for g in named)
    assert len(positive) == 58 and violations == 0 and named_violations == 0
    return {'connected_atlas_orders':'2..7','connected_atlas_total':len(atlas),
            'applicable_nonzero_denominator':len(positive),
            'zero_denominator_vacuous_holds':len(atlas)-len(positive),
            'violations':violations,'named_tested':len(named),
            'named_violations':named_violations}


if __name__ == '__main__':
    actual={'source_id':'graphbrain-alpha-upper-081','simple_witness':simple_witness(),
            'campaign_witness':verify(4),'windmill_family_example':windmill(),
            'division_by_zero_semantics':'author Sage evaluator maps to +Infinity (vacuous hold)',
            'gate':database_gate()}
    expected=json.loads(Path(__file__).with_name('certificate.json').read_text())
    assert actual==expected
    print(json.dumps(actual,indent=2))
