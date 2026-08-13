#!/usr/bin/env python3
"""Frozen two-hub equality-seed fusion trial for current WOWII 40."""

import importlib.util
import json
import math
import signal
import time
from pathlib import Path

import networkx as nx


ROOT=Path(__file__).resolve().parents[1]
RECORDS=ROOT/'results/expansion/prospective_wowii40_cutpair_fusion_records.jsonl'
SEEDS=[('c4_wall','C]',(4,3,4,1)),('k23_wall','Ds[',(5,4,5,1))]


def load_module(filename,name):
    path=Path(__file__).with_name(filename);spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


def persist(row):
    with RECORDS.open('a',encoding='utf-8') as output:
        output.write(json.dumps(row,sort_keys=True)+'\n');output.flush()
    return row


def seed_checks(exact):
    rows=[]
    for name,graph6,expected in SEEDS:
        graph=nx.from_graph6_bytes(graph6.encode())
        row=exact.exact_record(name,'cutpair_seed_gate',graph)
        actual=(row['n'],row['forest'],row['bipartite'],row['path_cover'])
        if actual!=expected:raise AssertionError((name,actual,expected))
        coloring=nx.bipartite.color(graph)
        sides=[sorted(v for v,color in coloring.items() if color==bit) for bit in (0,1)]
        size_two=min(side for side in sides if len(side)==2)
        rows.append(persist({'event':'seed_reverified','name':name,'graph6':graph6,
            'coordinates':{'n':actual[0],'forest':actual[1],'bipartite':actual[2],'path_cover':actual[3]},
            'canonical_hub_pair':size_two,'exact_witnesses':{'forest':row['forest_witness'],
            'bipartite':row['bipartite_witness'],'path_cover':row['path_cover_paths']}}))
    return rows


def parameters():
    return [(a,b) for total in range(2,6) for a in range(total+1) for b in [total-a]]


def fused_graph(c):
    # Canonical realization of the two identified hubs and c petal remainders.
    graph=nx.complete_bipartite_graph(2,c)
    return nx.convert_node_labels_to_integers(graph),0,1


def exact_record(exact,path_module,c,aliases):
    graph,hub_x,hub_y=fused_graph(c);n=len(graph);start=time.monotonic()
    adjacency=[0]*n
    for u,v in graph.edges():adjacency[u]|=1<<v;adjacency[v]|=1<<u
    forest,fw,fc=exact.largest_induced(adjacency,exact.is_forest_mask)
    bip,bw,bc=exact.largest_induced(adjacency,exact.is_bipartite_mask)
    path_cover,paths,cuts,linear_edges=path_module.exact_path_cover_milp(graph)
    components=list(nx.connected_components(nx.subgraph_view(graph,filter_node=lambda v:v not in {hub_x,hub_y})))
    component_count=len(components);certificate_lower=component_count-2
    if component_count!=c or path_cover<certificate_lower:raise AssertionError('separator certificate failed')
    rhs=math.ceil((path_cover+bip+1)/2)
    row={'event':'cutpair_fusion_evaluated','name':f'cutpair_fusion_c{c}','aliases':aliases,
        'n':n,'m':graph.number_of_edges(),'graph6':nx.to_graph6_bytes(graph,header=False).strip().decode(),
        'hubs':[hub_x,hub_y],'separator_components':component_count,
        'separator_component_vertices':[sorted(component) for component in components],
        'path_cover_lower_certificate':certificate_lower,'forest':forest,'forest_witness':fw,
        'bipartite':bip,'bipartite_witness':bw,'path_cover':path_cover,'path_cover_paths':paths,
        'path_cover_method':'exact_milp_linear_forest_with_cycle_cuts','path_cover_cycle_cuts':cuts,
        'linear_forest_edges':linear_edges,'rhs':rhs,'slack':forest-rhs,'crossing':forest<rhs,
        'residual_R':(n-path_cover)+(n-bip)-2*(n-forest),
        'search_counts':{'forest_subsets':fc,'bipartite_subsets':bc},
        'seconds':round(time.monotonic()-start,6)}
    return persist(row)


def main():
    exact=load_module('prospective_wowii40_block_surgery.py','wowii40_exact')
    path_module=load_module('prospective_wowii40_bouquet_trial.py','wowii40_path_milp')
    seed_checks(exact)
    provenance={}
    for a,b in parameters():provenance.setdefault(2*a+3*b,[]).append({'c4_copies':a,'k23_copies':b})
    rows=[exact_record(exact,path_module,c,aliases) for c,aliases in sorted(provenance.items())]
    print(json.dumps({'summary':{'raw_parameter_pairs':len(parameters()),'distinct_graphs':len(rows),
        'orders':[row['n'] for row in rows],'crossings':sum(row['crossing'] for row in rows),
        'timeouts':0,'slacks':{str(value):sum(row['slack']==value for row in rows)
        for value in sorted({row['slack'] for row in rows})}}}))
    for row in rows:print(json.dumps(row))


if __name__=='__main__':
    signal.alarm(60);main()
