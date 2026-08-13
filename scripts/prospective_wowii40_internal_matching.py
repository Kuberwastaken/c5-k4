#!/usr/bin/env python3
"""Frozen internal-side matching orbit surgery on the WOWII 40 K(2,c) wall."""

import importlib.util
import json
import math
import signal
import time
from pathlib import Path

import networkx as nx


ROOT=Path(__file__).resolve().parents[1]
RECORDS=ROOT/'results/expansion/prospective_wowii40_internal_matching_records.jsonl'


def load(filename,name):
    path=Path(__file__).with_name(filename);spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


def persist(row):
    with RECORDS.open('a',encoding='utf-8') as output:
        output.write(json.dumps(row,sort_keys=True)+'\n');output.flush()
    return row


def graph_for(c,k):
    graph=nx.complete_bipartite_graph(2,c)
    leaves=list(range(2,c+2));matching=[]
    for i in range(k):
        edge=(leaves[2*i],leaves[2*i+1]);graph.add_edge(*edge);matching.append(edge)
    return graph,matching


def coordinates(exact,path_module,name,graph,meta,event):
    graph=nx.convert_node_labels_to_integers(graph);n=len(graph);start=time.monotonic()
    adjacency=[0]*n
    for u,v in graph.edges():adjacency[u]|=1<<v;adjacency[v]|=1<<u
    forest,fw,fc=exact.largest_induced(adjacency,exact.is_forest_mask)
    bip,bw,bc=exact.largest_induced(adjacency,exact.is_bipartite_mask)
    path_cover,paths,cuts,linear_edges=path_module.exact_path_cover_milp(graph)
    rhs=math.ceil((path_cover+bip+1)/2)
    row={'event':event,'name':name,'meta':meta,'n':n,'m':graph.number_of_edges(),
        'graph6':nx.to_graph6_bytes(graph,header=False).strip().decode(),
        'edges':sorted([u,v] for u,v in graph.edges()),'forest':forest,'forest_witness':fw,
        'bipartite':bip,'bipartite_witness':bw,'path_cover':path_cover,'path_cover_paths':paths,
        'path_cover_method':'exact_milp_linear_forest_with_cycle_cuts','path_cover_cycle_cuts':cuts,
        'linear_forest_edges':linear_edges,'rhs':rhs,'slack':forest-rhs,'crossing':forest<rhs,
        'residual_R':(n-path_cover)+(n-bip)-2*(n-forest),
        'search_counts':{'forest_subsets':fc,'bipartite_subsets':bc},
        'seconds':round(time.monotonic()-start,6)}
    return persist(row)


def main():
    exact=load('prospective_wowii40_block_surgery.py','wowii40_exact')
    path_module=load('prospective_wowii40_bouquet_trial.py','wowii40_path_milp')
    for c in range(6,16):
        graph,_=graph_for(c,0)
        row=coordinates(exact,path_module,f'K2_{c}_wall',graph,{'c':c,'k':0},'wall_reverified')
        expected=(c+1,c+2,c-2)
        actual=(row['forest'],row['bipartite'],row['path_cover'])
        if actual!=expected:raise AssertionError((c,actual,expected))
    persist({'event':'structural_rejection','c':6,'k':3,
        'reason':'G-{X,Y} has c-k=3 components, giving only p>=1, below required p>=2'})
    rows=[]
    for c in range(6,16):
        for k in (1,2,3):
            if (c,k)==(6,3):continue
            graph,matching=graph_for(c,k)
            remainder=set(graph)-{0,1}
            components=list(nx.connected_components(graph.subgraph(remainder)))
            lower=len(components)-2
            if lower<2:raise AssertionError((c,k,lower))
            rows.append(coordinates(exact,path_module,f'internal_matching_c{c}_k{k}',graph,
                {'c':c,'k':k,'matching':matching,'hubs':[0,1],
                 'separator_components':[sorted(component) for component in components],
                 'path_cover_lower_certificate':lower},'internal_matching_evaluated'))
    print(json.dumps({'summary':{'evaluated':len(rows),'structural_rejections':1,
        'crossings':sum(row['crossing'] for row in rows),'timeouts':0,
        'slacks':{str(value):sum(row['slack']==value for row in rows)
        for value in sorted({row['slack'] for row in rows})}}}))
    for row in rows:print(json.dumps(row))


if __name__=='__main__':
    signal.alarm(60);main()
