#!/usr/bin/env python3
"""Frozen internal K(1,r) orbit surgery on the WOWII 40 K(2,c) wall."""

import importlib.util
import json
import math
import signal
import time
from pathlib import Path

import networkx as nx


ROOT=Path(__file__).resolve().parents[1]
RECORDS=ROOT/'results/expansion/prospective_wowii40_internal_star_records.jsonl'


def load(filename,name):
    path=Path(__file__).with_name(filename);spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


def persist(row):
    with RECORDS.open('a',encoding='utf-8') as output:
        output.write(json.dumps(row,sort_keys=True)+'\n');output.flush()
    return row


def star_graph(c,r):
    graph=nx.complete_bipartite_graph(2,c);center=2;arms=[]
    for vertex in range(3,3+r):graph.add_edge(center,vertex);arms.append(vertex)
    return graph,center,arms


def exact_row(exact,path_module,c,r,event):
    graph,center,arms=star_graph(c,r);n=len(graph);start=time.monotonic()
    adjacency=[0]*n
    for u,v in graph.edges():adjacency[u]|=1<<v;adjacency[v]|=1<<u
    forest,fw,fc=exact.largest_induced(adjacency,exact.is_forest_mask)
    bip,bw,bc=exact.largest_induced(adjacency,exact.is_bipartite_mask)
    path_cover,paths,cuts,linear_edges=path_module.exact_path_cover_milp(graph)
    remainder=set(graph)-{0,1};components=list(nx.connected_components(graph.subgraph(remainder)))
    rhs=math.ceil((path_cover+bip+1)/2)
    return persist({'event':event,'name':f'internal_star_c{c}_r{r}','c':c,'r':r,
        'center':center,'arms':arms,'hubs':[0,1],'n':n,'m':graph.number_of_edges(),
        'graph6':nx.to_graph6_bytes(graph,header=False).strip().decode(),
        'edges':sorted([u,v] for u,v in graph.edges()),
        'separator_components':[sorted(component) for component in components],
        'separator_component_count':len(components),'separator_path_lower':len(components)-2,
        'forest':forest,'forest_witness':fw,'bipartite':bip,'bipartite_witness':bw,
        'path_cover':path_cover,'path_cover_paths':paths,
        'path_cover_method':'exact_milp_linear_forest_with_cycle_cuts',
        'path_cover_cycle_cuts':cuts,'linear_forest_edges':linear_edges,
        'rhs':rhs,'slack':forest-rhs,'crossing':forest<rhs,
        'residual_R':(n-path_cover)+(n-bip)-2*(n-forest),
        'search_counts':{'forest_subsets':fc,'bipartite_subsets':bc},
        'seconds':round(time.monotonic()-start,6)})


def main():
    exact=load('prospective_wowii40_block_surgery.py','wowii40_exact')
    path_module=load('prospective_wowii40_bouquet_trial.py','wowii40_path_milp')
    for c in range(7,16):
        row=exact_row(exact,path_module,c,1,'starting_wall_reverified')
        expected=(c,c+1,c-3)
        actual=(row['forest'],row['bipartite'],row['path_cover'])
        if actual!=expected:raise AssertionError((c,actual,expected))
    rows=[exact_row(exact,path_module,c,r,'internal_star_evaluated')
          for c in range(7,16) for r in (2,3,4)]
    print(json.dumps({'summary':{'starting_walls':9,'evaluated':len(rows),
        'crossings':sum(row['crossing'] for row in rows),'timeouts':0,
        'slacks':{str(value):sum(row['slack']==value for row in rows)
        for value in sorted({row['slack'] for row in rows})}}}))
    for row in rows:print(json.dumps(row))


if __name__=='__main__':
    signal.alarm(60);main()
