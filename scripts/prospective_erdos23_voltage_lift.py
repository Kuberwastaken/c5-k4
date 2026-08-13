#!/usr/bin/env python3
"""Frozen connected voltage 2-lift trial for current Erdős Problem 23."""

import argparse
import importlib.util
import itertools
import json
import subprocess
import time
from pathlib import Path

import networkx as nx


ROOT=Path(__file__).resolve().parents[1]
RECORDS=ROOT/'results/expansion/prospective_erdos23_voltage_lift_records.jsonl'
LABELG=Path('/Users/kuber.mehta/Projects/breakthroughmaxxing/07-marlin/total-coloring-n12-d6-m25-minimal/nauty2_8_9/labelg')


def maxcut_module():
    path=Path(__file__).with_name('prospective_erdos23_c5_surgery.py')
    spec=importlib.util.spec_from_file_location('erdos23_base',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def persist(row):
    with RECORDS.open('a',encoding='utf-8') as output:
        output.write(json.dumps(row)+'\n');output.flush()
    return row


def canonical_graph6(graph):
    encoded=nx.to_graph6_bytes(graph,header=False).decode()
    result=subprocess.run([str(LABELG),'-q'],input=encoded,text=True,
                          capture_output=True,check=True,timeout=10)
    return result.stdout.strip()


def canonical_masks():
    def orbit(bits):
        values=[]
        for reverse in (False,True):
            row=tuple(reversed(bits)) if reverse else tuple(bits)
            values.extend(row[i:]+row[:i] for i in range(5))
        return min(values)
    return sorted({orbit(bits) for bits in itertools.product((0,1),repeat=5) if any(bits)})


def voltage(template,active,m,a,b):
    if not active:return 0
    if template in ('diagonal','circulant0'):return int(a==b)
    if template=='bilinear':return (a%2)*(b%2)
    if template=='circulant01':return int((a-b)%m in (0,1))
    if template=='uniform':return 1
    raise ValueError(template)


def lift_graph(m,template,mask):
    graph=nx.Graph(); graph.add_nodes_from(range(10*m))
    vertex=lambda i,a,s:2*(i*m+a)+s
    voltage_table=[]
    for i in range(5):
        for a in range(m):
            for b in range(m):
                value=voltage(template,bool(mask[i]),m,a,b)
                voltage_table.append([i,a,b,value])
                for sheet in (0,1):
                    graph.add_edge(vertex(i,a,sheet),vertex((i+1)%5,b,sheet^value))
    return graph,voltage_table


def exact_record(module,name,graph,meta,stage):
    start=time.monotonic(); graph=nx.convert_node_labels_to_integers(graph)
    triangles=sum(nx.triangles(graph).values())//3
    maxcut,side,method=module.exact_maxcut_milp(graph)
    kept=sorted([u,v] for u,v in graph.edges() if (u in side)!=(v in side))
    deleted=sorted([u,v] for u,v in graph.edges() if (u in side)==(v in side))
    witness=nx.Graph();witness.add_nodes_from(graph);witness.add_edges_from(kept)
    assert triangles==0 and nx.is_bipartite(witness) and len(graph)%5==0
    bound=(len(graph)//5)**2
    return persist({'event':'voltage_graph_evaluated','stage':stage,'name':name,'meta':meta,
        'n':len(graph),'m':graph.number_of_edges(),'connected':nx.is_connected(graph),
        'components':nx.number_connected_components(graph),'triangle_count':triangles,
        'graph6':nx.to_graph6_bytes(graph,header=False).strip().decode(),
        'maxcut':maxcut,'cut_side':sorted(side),'cut_other_side':sorted(set(graph)-side),
        'kept_cut_edges':kept,'deleted_edges':deleted,'edge_bipartization':len(deleted),
        'bound':bound,'slack':bound-len(deleted),'crossing':len(deleted)>bound,
        'maxcut_method':method,'witness_replay':True,'seconds':round(time.monotonic()-start,6)})


def controls(module):
    outputs=[]
    for m in (2,3,4):
        zero,table=lift_graph(m,'uniform',(0,0,0,0,0))
        outputs.append(exact_record(module,f'zero_voltage_m{m}',zero,
            {'m':m,'template':'uniform','mask':[0]*5,'voltage_table':table},'lift_gate'))
        odd,table=lift_graph(m,'uniform',(1,0,0,0,0))
        outputs.append(exact_record(module,f'uniform_odd_voltage_m{m}',odd,
            {'m':m,'template':'uniform','mask':[1,0,0,0,0],'voltage_table':table},'lift_gate'))
    return outputs


def development(module,max_new):
    candidates=[];rejections=[]
    templates=('diagonal','bilinear','circulant0','circulant01')
    for m in (2,3,4):
        for template in templates:
            for mask in canonical_masks():
                graph,table=lift_graph(m,template,mask)
                if not nx.is_connected(graph):
                    rejections.append({'m':m,'template':template,'mask':mask,'reason':'disconnected'})
                    continue
                fingerprint=canonical_graph6(graph)
                duplicate=any(fingerprint==oldfp for _,_,oldfp,_,_,_ in candidates)
                if not duplicate:candidates.append((f'{template}_m{m}_mask{"".join(map(str,mask))}',graph,fingerprint,m,template,(mask,table)))
                if len(candidates)>=100:break
    existing=set()
    for line in RECORDS.read_text(encoding='utf-8').splitlines():
        try:row=json.loads(line)
        except json.JSONDecodeError:continue
        if row.get('stage')=='development' or row.get('event')=='voltage_timeout':
            existing.add(row.get('name'))
    outputs=[];timeouts=[];attempted=0
    for name,graph,_,m,template,(mask,table) in candidates:
        if name in existing:continue
        meta={'m':m,'template':template,'mask':mask,'voltage_table':table}
        try:outputs.append(exact_record(module,name,graph,meta,'development'))
        except TimeoutError:
            timeouts.append(persist({'event':'voltage_timeout','stage':'development','name':name,
                'n':len(graph),'meta':meta,'solve_cap_seconds':10}))
        attempted+=1
        if attempted>=max_new:break
    return outputs,rejections,timeouts


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--lane',choices=('controls','development'),required=True)
    parser.add_argument('--max-new',type=int,default=5);args=parser.parse_args()
    module=maxcut_module();start=time.monotonic()
    if args.lane=='controls':outputs=controls(module);rejections=[];timeouts=[]
    else:outputs,rejections,timeouts=development(module,args.max_new)
    print(json.dumps({'summary':{'lane':args.lane,'evaluated':len(outputs),'rejections':len(rejections),
        'crossings':sum(r['crossing'] for r in outputs),'timeouts':len(timeouts),'seconds':round(time.monotonic()-start,6)}}))
    for rejection in rejections:print(json.dumps({'event':'lift_rejected',**rejection}))
    for output in outputs:print(json.dumps(output))


if __name__=='__main__':main()
